"""Task-owned, in-memory FSM composition; no IO or submission.

Requires core's captured header-only template and normalized, baseline-compared
intent. The host still verifies environment, BU, timezone, rules and approval.
See references/fsm-transport-profile.md for evidence and capability boundaries.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
import csv
import io
import zipfile

from input_contract import InputError, TASK_CODE, normalize, split_verified_noops

PROFILE_ID = 'org-settings-schema-v1'
OPTION_CANDIDATE_ID = 'identical-option-aliases-schema-candidate-v1'
ORG = 'EXM_ORG_SETTING.csv'
OPTION_MEMBERS = ('EXM_SETUP_OPTION.csv', 'EXM_CASH_ADV_SETUP_AND_POLICY.csv')
ORG_HEADER = ('BuName', 'SettingCode', 'CreationDate', 'CreatedBy', 'LastUpdateDate',
              'LastUpdatedBy', 'LastUpdateLogin', 'SettingValue', 'SettingValueDecoded')
OPTION_HEADER = ('BuName', 'OptionCode', 'ValueCode', 'CreationDate', 'CreatedBy',
                 'LastUpdateLogin', 'LastUpdateDate', 'LastUpdatedBy', 'OtherOrgId')
ORG_ATTRIBUTES = 'CreationDate,CreatedBy,LastUpdateDate,LastUpdatedBy,LastUpdateLogin,SettingCode,SettingValue,BuName,SettingValueDecoded'
OPTION_ATTRIBUTES = 'OptionCode,ValueCode,CreationDate,CreatedBy,LastUpdateLogin,LastUpdateDate,LastUpdatedBy,BuName,OtherOrgId'
METADATA = 'ASM_SETUP_CSV_METADATA.xml'


def reconcile_option_baseline(alias_rows):
    """Compare workflow-resolved canonical facts from both fresh export aliases.

    The host resolves scope using the declared source contract and verifies
    completeness/provenance. Unrelated option values remain opaque data.
    """
    if not isinstance(alias_rows, dict) or set(alias_rows) != set(OPTION_MEMBERS):
        raise InputError('FSM_ALIAS_BASELINE_CONFLICT: both complete option aliases are required.')
    indexes = []
    for name in OPTION_MEMBERS:
        rows = alias_rows[name]
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            raise InputError('FSM_ALIAS_BASELINE_CONFLICT: expected canonical option facts.')
        split_verified_noops([], rows)  # Includes duplicate/invalid identity rejection.
        if any(row['entity'] != 'EXM_SETUP_OPTION' for row in rows):
            raise InputError('FSM_ALIAS_BASELINE_CONFLICT: option aliases contain another entity.')
        indexes.append({(row['code'], row['scope'], row['business_unit']): row['value'] for row in rows})
    if indexes[0] != indexes[1]:
        raise InputError('FSM_ALIAS_BASELINE_CONFLICT: option aliases disagree; never select by order or header.')
    return [{'entity': 'EXM_SETUP_OPTION', 'code': key[0], 'scope': key[1],
             'business_unit': key[2], 'value': value} for key, value in indexes[0].items()]


def verify_option_readback(changes, before_aliases, after_aliases):
    """Compare requested option results AND preservation of unrequested options.

    Returns offline comparison evidence, not proof of where/when exports ran.
    The qualification workflow separately requires successful Fusion process
    results, same-target export provenance and organization-setting preservation.
    """
    before = reconcile_option_baseline(before_aliases)
    after = reconcile_option_baseline(after_aliases)
    split_verified_noops(changes, [])
    key = lambda row: (row['code'], row['scope'], row['business_unit'])
    expected = {key(row): row['value'] for row in before}
    requested = set()
    for change in changes:
        if change['entity'] != 'EXM_SETUP_OPTION':
            continue
        canonical = normalize({'scope': change['scope'], 'business_unit': change['business_unit'],
                               'controls': {'auto_submission': change['value']}})['changes'][0]
        if canonical != change:
            raise InputError('FSM_READBACK_MISMATCH: unreviewed option change.')
        if key(change) in expected and expected[key(change)] == change['value']:
            raise InputError('FSM_READBACK_MISMATCH: an already-satisfied value does not qualify a setting change.')
        expected[key(change)] = change['value']
        requested.add(key(change))
    if not requested:
        raise InputError('FSM_READBACK_MISMATCH: no option change was tested.')
    if expected != {key(row): row['value'] for row in after}:
        raise InputError('FSM_READBACK_MISMATCH: requested values or unrequested option preservation differ.')
    return {'status': 'matched', 'requested_option_count': len(requested),
            'preserved_option_count': len(expected.keys() - requested),
            'export_provenance_verified': False}


def prepare_members(template_bytes, changes, *, qualification_run=False):
    """Return task CSV/metadata bytes for a candidate validated by core later.

    Accept only the exact header-only template, never an unfiltered data export.
    Metadata is retained byte-for-byte; no files are extracted or written.
    """
    expected = {METADATA, ORG, *OPTION_MEMBERS}
    try:
        with zipfile.ZipFile(io.BytesIO(template_bytes)) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if (len(names) != len(expected) or set(names) != expected
                    or any(info.flag_bits & 1 or info.file_size > 8 * 1024 * 1024 for info in infos)
                    or sum(info.file_size for info in infos) > 16 * 1024 * 1024):
                raise InputError('FSM_SCHEMA_MISMATCH: require exactly the four bounded template members.')
            members = {name: archive.read(name) for name in names}
        headers = {}
        for name, content in members.items():
            if name == METADATA:
                continue
            records = list(csv.reader(io.StringIO(content.decode('utf-8-sig'), newline=''), strict=True))
            if len(records) != 1:
                raise InputError('FSM_SCHEMA_MISMATCH: require header-only CSVs, not a data export.')
            headers[name] = tuple(records[0])
        rows = compose_changes(members[METADATA].decode('utf-8-sig'), headers, changes,
                               qualification_run=qualification_run)
        for name, header in headers.items():
            output = io.StringIO(newline='')
            writer = csv.writer(output, lineterminator='\r\n')
            writer.writerow(header)
            writer.writerows(rows[name])
            members[name] = output.getvalue().encode('utf-8')
        return tuple(members.items())
    except (zipfile.BadZipFile, UnicodeError, csv.Error, ET.ParseError, RuntimeError) as exc:
        raise InputError('FSM_SCHEMA_MISMATCH: invalid ZIP, UTF-8, CSV or XML template.') from exc


def qualify_template(metadata_xml, headers):
    """Match a reviewed schema, never certify live import results from metadata."""
    if '<!DOCTYPE' in metadata_xml.upper() or '<!ENTITY' in metadata_xml.upper():
        raise InputError('FSM_SCHEMA_MISMATCH: DTD/entities are forbidden.')
    root = ET.fromstring(metadata_xml)
    local = lambda element: element.tag.rsplit('}', 1)[-1]
    values = lambda name: [e.text or '' for e in root.iter() if local(e) == name]
    releases = values('ProcessRelease')
    if len(releases) != 1 or not releases[0].strip():
        raise InputError('FSM_SCHEMA_MISMATCH: ProcessRelease must have one nonempty diagnostic value.')
    release = releases[0]
    for tag, expected in [('ObjectShortName', TASK_CODE), ('ObjectType', 'TASK')]:
        if values(tag) != [expected]:
            raise InputError(f'FSM_SCHEMA_MISMATCH: {tag} needs a maintained transport-profile refresh.')
    expected_headers = {ORG: ORG_HEADER, **dict.fromkeys(OPTION_MEMBERS, OPTION_HEADER)}
    if set(headers) != set(expected_headers) or any(
            len(headers[name]) != len(expected_headers[name])
            or set(headers[name]) != set(expected_headers[name]) for name in headers):
        raise InputError('FSM_SCHEMA_MISMATCH: unexpected CSV member or ordered header.')
    found = set()
    for row in root.iter():
        if local(row) != 'MigrationProcessBusinessObjectCSVMetadataVORow':
            continue
        data = {local(e): e.text or '' for e in row}
        name = data.get('BusinessObjectShortName', '') + '.csv'
        if name not in expected_headers or name in found:
            raise InputError('FSM_SCHEMA_MISMATCH: unexpected or repeated metadata object.')
        found.add(name)
        org = name == ORG
        expected = {
            'XmlAttributeList': ORG_ATTRIBUTES if org else OPTION_ATTRIBUTES,
            'XmlAttributeTypeList': ('dateTime,string,dateTime,string,string,string,string,string,string'
                                     if org else 'string,string,dateTime,string,string,dateTime,string,string,long'),
            'XmlNodePath': '/OrgSettingVO/OrgSettingVORow' if org else '/SetupOptionVO/SetupOptionVORow',
            'NodeSequence': '1', 'BatchName': '',
        }
        if any(data.get(key, '') != value for key, value in expected.items()):
            raise InputError('FSM_SCHEMA_MISMATCH: XML mapping, type, sequence or batch changed.')
    if found != set(expected_headers):
        raise InputError('FSM_SCHEMA_MISMATCH: missing metadata object.')
    return {'profile': PROFILE_ID, 'option_candidate': OPTION_CANDIDATE_ID,
            'release': release, 'qualification': 'schema-compatible-live-import-unverified',
            'profile_live_import_verified': False, 'live_result_verified': False}


def compose_org_changes(metadata_xml, headers, changes):
    """Return only intended setting rows; untouched alias files stay header-only.

    No previous import ZIP or copied audit values are accepted by this function.
    It returns structured rows, not a CSV/ZIP. prepare_members encodes CSV;
    the preparation helper writes a candidate ZIP before core preflight.
    """
    return compose_changes(metadata_xml, headers, changes)


def compose_changes(metadata_xml, headers, changes, *, qualification_run=False):
    """Mirror only ENABLE_AUTO_SUB_DA_EXP for an explicit qualification run.

    This is executable candidate construction, not a live qualification claim.
    The ordinary customer route retains its gate until import/read-back evidence
    qualifies a maintained profile. Both aliases receive the same field/value
    map, serialized in their own target header order. No alias wins by name.
    """
    if not isinstance(qualification_run, bool):
        raise InputError('Qualification mode must be an explicit boolean.')
    qualify_template(metadata_xml, headers)
    if not isinstance(changes, list) or not changes:
        raise InputError('No remaining changes: do not submit an empty import.')
    # Also rejects duplicate or malformed logical identities.
    split_verified_noops(changes, [])
    rows = {name: [] for name in headers}
    for change in changes:
        if change['entity'] != 'EXM_ORG_SETTING' and not qualification_run:
            raise InputError('FSM_ALIAS_COLLISION: populated setup-option aliases need their own qualified strategy.')
        request = {'scope': change['scope'], 'business_unit': change['business_unit'],
                   'matching_scope': 'GLOBAL' if change['scope'] == 'GLOBAL' else None,
                   'controls': {change.get('input_control', ''): change['value']}}
        canonical = normalize(request)['changes'][0]
        if canonical != change:
            raise InputError('Mapped setting differs from canonical business intent.')
        if len(change['value']) > 255 or '\x00' in change['value']:
            raise InputError('Setting value exceeds the reviewed string contract.')
        if change['entity'] == 'EXM_SETUP_OPTION':
            fields = dict.fromkeys(OPTION_HEADER, '')
            fields.update(BuName=change['business_unit'] or '', OptionCode=change['code'],
                          ValueCode=change['value'], OtherOrgId='-1' if change['scope'] == 'GLOBAL' else '')
            for name in OPTION_MEMBERS:
                rows[name].append([fields[field] for field in headers[name]])
        else:
            fields = dict.fromkeys(ORG_HEADER, '')
            fields.update(BuName=change['business_unit'] or '', SettingCode=change['code'],
                          SettingValue=change['value'], SettingValueDecoded=change['value'])
            rows[ORG].append([fields[field] for field in headers[ORG]])
    return rows
