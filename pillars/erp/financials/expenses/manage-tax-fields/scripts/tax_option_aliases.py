"""Local ENABLE_TAX alias qualification checks; never calls or certifies Fusion.

The active runbook owns target/schema/provenance checks and core Data Loader
owns approval and submission. Normal preparation is limited to the maintained
live-qualified create-Y and combined N-to-Y update profiles. New switches plus
new rules may use sequential switch-only and rule-only stages. Other switch
operations require explicit qualification. Local checks never certify an import.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

SETUP = 'EXM_SETUP_OPTION.csv'
CASH = 'EXM_CASH_ADV_SETUP_AND_POLICY.csv'
VAT = 'EXM_VAT_FIELD.csv'
META = 'ASM_SETUP_CSV_METADATA.xml'
AUDIT = {'CreationDate', 'CreatedBy', 'LastUpdateDate', 'LastUpdatedBy', 'LastUpdateLogin'}
OPTION_HEADER = {'BuName', 'OptionCode', 'ValueCode', 'OtherOrgId'} | AUDIT
BEHAVIORS = {'EnableMerchantNameCode', 'EnableMerchantReceiptCode', 'EnableMerchantTaxRegCode',
             'EnableMerchantReferenceCode', 'EnableMerchantTaxpayerCode', 'EnableTaxClassificationCode'}
HEADERS = {SETUP: OPTION_HEADER, CASH: OPTION_HEADER,
           VAT: {'BuName', 'TerritoryCode', 'EnabledFlag'} | BEHAVIORS | AUDIT}
STRATEGY = 'enable-tax-identical-minimal-aliases-v1'
PROFILE_PATH = Path(__file__).resolve().parents[1] / 'references/qualified-option-alias-profile.json'


class AliasError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AliasError(message)


def read_package(content):
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            infos = archive.infolist()
            require(len(infos) == 4 and {x.filename for x in infos} == {*HEADERS, META},
                    'catalog mismatch: unexpected or duplicate package members')
            require(all(not x.flag_bits & 1 and x.file_size <= 10 * 1024 * 1024 for x in infos),
                    'input validation: encrypted or oversized package member')
            members = {x.filename: archive.read(x) for x in infos}
        headers, rows = {}, {}
        for name, expected in HEADERS.items():
            records = list(csv.reader(io.StringIO(members[name].decode('utf-8-sig'), newline=''), strict=True))
            require(records and len(records[0]) == len(expected) and set(records[0]) == expected,
                    'catalog mismatch: unexpected CSV header')
            require(all(len(row) == len(records[0]) for row in records[1:]),
                    'input validation: CSV row width mismatch')
            headers[name] = records[0]
            rows[name] = [dict(zip(records[0], row)) for row in records[1:]]
        return members, headers, rows
    except (zipfile.BadZipFile, UnicodeError, csv.Error, RuntimeError) as error:
        raise AliasError('input validation: unreadable package') from error


def index(rows, name, *, candidate=False):
    result = {}
    for row in rows:
        key = (row['BuName'], row['TerritoryCode' if name == VAT else 'OptionCode'])
        # Other option codes/global rows are retained as opaque baseline facts.
        require(key[1].strip() and key not in result, 'input validation: missing or duplicate identity')
        if candidate:
            require(key[0].strip(), 'input validation: a verified named BU is required')
            require(all(not row[field] for field in AUDIT), 'input validation: populated audit field')
            if name == VAT:
                require(row['EnabledFlag'] in {'Y', 'N'} and
                        all(row[field] in {'ENABLED', 'DISABLED', 'REQUIRED'} for field in BEHAVIORS),
                        'input validation: invalid tax-rule field')
            else:
                require(row['OptionCode'] == 'ENABLE_TAX' and row['ValueCode'] in {'Y', 'N'},
                        'input validation: only ENABLE_TAX Y/N is permitted')
        result[key] = {field: value for field, value in row.items() if field not in AUDIT}
    return result


def baseline_options(rows):
    first = index(rows[SETUP], SETUP)
    require(first == index(rows[CASH], CASH),
            'catalog mismatch: complete baseline option aliases disagree')
    return first


def schema_fingerprint(content):
    """Ignore run-specific XML values; bind the reviewed routing and schema."""
    members, headers, _ = read_package(content)
    try:
        text = members[META].decode('utf-8-sig')
    except UnicodeError as error:
        raise AliasError('catalog mismatch: invalid metadata encoding') from error
    require('<!DOCTYPE' not in text.upper() and '<!ENTITY' not in text.upper(),
            'catalog mismatch: XML DTD/entities are unsupported')
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        raise AliasError('catalog mismatch: invalid metadata XML') from error
    local = lambda element: element.tag.rsplit('}', 1)[-1]
    def one(name):
        values = [e.text or '' for e in root.iter() if local(e) == name]
        require(len(values) == 1 and values[0], 'catalog mismatch: ambiguous metadata identity')
        return values[0]
    mappings, migration_objects = {}, []
    for element in root.iter():
        values = {local(e): e.text or '' for e in element}
        if local(element) == 'MigrationProcessBusinessObjectCSVMetadataVORow':
            name = values.get('BusinessObjectShortName', '') + '.csv'
            require(name in HEADERS and name not in mappings, 'catalog mismatch: unexpected XML object')
            keys = ('XmlAttributeList', 'XmlAttributeTypeList', 'XmlNodePath', 'NodeSequence', 'BatchName')
            require(all(key in values for key in keys), 'catalog mismatch: incomplete XML mapping')
            mappings[name] = {key: values[key] for key in keys}
        elif local(element) == 'MigrationProcessMigrationObjectCSVMetadataVORow':
            keys = ('BusinessObjectShortName', 'MigrateFlag', 'IncludeExternalDataFlag', 'ServiceType')
            require(all(key in values for key in keys), 'catalog mismatch: incomplete migration object')
            migration_objects.append({key: values[key] for key in keys})
    require(set(mappings) == set(HEADERS), 'catalog mismatch: missing XML mapping')
    descriptor = {'task_code': one('ObjectShortName'), 'object_type': one('ObjectType'),
                  'release': one('ProcessRelease'), 'headers': headers, 'csv_mappings': mappings,
                  'migration_objects': sorted(migration_objects, key=lambda row: row['BusinessObjectShortName'])}
    return hashlib.sha256(json.dumps(descriptor, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def prepare_qualification(baseline, candidate, *, qualification_run=False):
    require(qualification_run, 'approval blocker: Tax alias qualification must be explicitly selected')
    base_members, base_headers, base_rows = read_package(baseline)
    members, headers, rows = read_package(candidate)
    require(members[META] == base_members[META] and headers == base_headers,
            'catalog mismatch: candidate metadata or ordered headers changed')
    before = baseline_options(base_rows)
    requested = index(rows[SETUP], SETUP, candidate=True)
    require(requested, 'input validation: no ENABLE_TAX change to qualify')
    # Accept a legacy header-only companion or an already-identical candidate.
    require(not rows[CASH] or index(rows[CASH], CASH, candidate=True) == requested,
            'input validation: candidate aliases diverge')
    for key, row in requested.items():
        require(row['OtherOrgId'] == (before[key]['OtherOrgId'] if key in before else ''),
                'input validation: transport identity must be baseline-owned')
    require(any(key not in before or row['ValueCode'] != before[key]['ValueCode']
                for key, row in requested.items()),
            'input validation: already-satisfied switch values do not qualify an import')
    index(rows[VAT], VAT, candidate=True)
    # Preserve VAT and metadata bytes; change only the alias needing replication.
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, content in members.items():
            if name == CASH:
                text = io.StringIO(newline='')
                writer = csv.DictWriter(text, fieldnames=headers[CASH], lineterminator='\r\n')
                writer.writeheader()
                writer.writerows(rows[SETUP])
                content = text.getvalue().encode('utf-8')
            archive.writestr(name, content)
    content = output.getvalue()
    return content, {'status': 'qualification_candidate', 'strategy': STRATEGY,
                     'requested_option_count': len(requested),
                     'candidate_sha256': hashlib.sha256(content).hexdigest(),
                     'baseline_sha256': hashlib.sha256(baseline).hexdigest(),
                     'live_import_verified': False}


def replace_members(content, replacements):
    members = read_package(content)[0]
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, value in members.items():
            archive.writestr(name, replacements.get(name, value))
    return output.getvalue()


def header_only(content):
    # Validated task headers contain no multiline column names.
    return content.splitlines(keepends=True)[0]


def prepare_switch_create_stage(baseline, candidate):
    """Split a combined create without promoting untested combined imports."""
    normalized, _ = prepare_qualification(baseline, candidate, qualification_run=True)
    original = read_package(baseline)[2]
    members, _, requested = read_package(normalized)
    switches = index(requested[SETUP], SETUP, candidate=True)
    before = baseline_options(original)
    require(all(key not in before and row['ValueCode'] == 'Y'
                for key, row in switches.items()),
            'input validation: staged create requires absent named-BU ENABLE_TAX=Y rows')
    rules = index(requested[VAT], VAT, candidate=True)
    existing_rules = index(original[VAT], VAT)
    require(rules and all(key not in existing_rules and (row['BuName'], 'ENABLE_TAX') in switches
                          for key, row in rules.items()),
            'input validation: staged create requires new tax rules for the selected switch BUs')
    switch_only = replace_members(normalized, {VAT: header_only(members[VAT])})
    content, report = prepare_qualified(baseline, switch_only)
    report.update(stage='switch-create', deferred_tax_rule_count=len(rules),
                  original_candidate_sha256=hashlib.sha256(candidate).hexdigest(),
                  next_action='After core approval, terminal success and fresh-export reconciliation, prepare the tax-rules stage from the original request.')
    return content, report


def prepare_tax_rules_stage(original_baseline, candidate, switch_candidate, fresh_baseline):
    """Require full switch-stage readback before preparing the deferred rules."""
    # Live process/provenance checks remain owned by the active workflow.
    expected_switch, _ = prepare_switch_create_stage(original_baseline, candidate)
    expected_members, _, expected = read_package(expected_switch)
    switch_members, _, submitted = read_package(switch_candidate)
    require(expected == submitted and expected_members[META] == switch_members[META],
            'input validation: switch-stage candidate differs from the original request')
    verify_readback(original_baseline, switch_candidate, fresh_baseline)
    require(schema_fingerprint(original_baseline) == schema_fingerprint(fresh_baseline),
            'catalog mismatch: schema/release changed between create stages')
    original_members, original_headers, original_rows = read_package(candidate)
    fresh_members, fresh_headers, fresh_rows = read_package(fresh_baseline)
    require(original_headers == fresh_headers,
            'catalog mismatch: ordered headers changed between create stages')
    rules = index(original_rows[VAT], VAT, candidate=True)
    existing_rules = index(fresh_rows[VAT], VAT)
    require(not (rules.keys() & existing_rules.keys()),
            'input validation: deferred rule create now matches an existing identity')
    content = replace_members(fresh_baseline, {
        SETUP: header_only(fresh_members[SETUP]), CASH: header_only(fresh_members[CASH]),
        VAT: original_members[VAT]})
    return content, {'status': 'rule_only_candidate', 'stage': 'tax-rules',
                     'requested_tax_rule_count': len(rules), 'requested_option_count': 0,
                     'candidate_sha256': hashlib.sha256(content).hexdigest(),
                     'baseline_sha256': hashlib.sha256(fresh_baseline).hexdigest(),
                     'original_candidate_sha256': hashlib.sha256(candidate).hexdigest(),
                     'switch_candidate_sha256': hashlib.sha256(switch_candidate).hexdigest(),
                     'switch_readback_matched': True, 'live_import_verified': False,
                     'next_action': 'Run normal rule-only validation and a new immutable core preview/approval; reconcile rules and protected switch values after import.'}


def prepare_qualified(baseline, candidate):
    """Match a maintained operation profile without expanding its evidence scope."""
    try:
        profile = json.loads(PROFILE_PATH.read_text())
    except (OSError, ValueError) as error:
        raise AliasError('catalog mismatch: maintained Tax alias profile is unavailable') from error
    require(isinstance(profile, dict), 'catalog mismatch: invalid Tax alias profile')
    require(profile.get('schema_version') == '1.1' and profile.get('strategy') == STRATEGY
            and profile.get('qualified_operations') == ['create']
            and profile.get('qualified_values') == ['Y'] and profile.get('scope') == 'named_business_unit'
            and profile.get('switch_only') is True,
            'catalog mismatch: unsupported Tax alias profile')
    additional = profile.get('additional_qualified_schemas', [])
    require(isinstance(additional, list) and all(
        isinstance(item, dict) and isinstance(item.get('release'), str) and item['release'].strip()
        and isinstance(item.get('schema_sha256'), str) and len(item['schema_sha256']) == 64
        and all(c in '0123456789abcdef' for c in item['schema_sha256']) for item in additional),
        'catalog mismatch: invalid additional Tax alias schemas')
    fingerprint = schema_fingerprint(baseline)
    allowed = [profile.get('schema_sha256'), *(item['schema_sha256'] for item in additional)]
    require(fingerprint in allowed,
            'catalog mismatch: fresh Tax schema/release is outside the qualified profile')
    content, report = prepare_qualification(baseline, candidate, qualification_run=True)
    original, requested = read_package(baseline)[2], read_package(candidate)[2]
    before = baseline_options(original)
    changes = index(requested[SETUP], SETUP, candidate=True)
    create_y = all(key not in before and row['ValueCode'] == 'Y'
                   for key, row in changes.items())
    if create_y:
        require(not requested[VAT],
                'catalog mismatch: create-Y profile is switch-only; use --stage switch-create for combined creates')
        operation_profile = 'create-y-switch-only'
    else:
        update = profile.get('qualified_update')
        require(isinstance(update, dict) and update.get('scope') == 'named_business_unit'
                and update.get('option_count') == 1 and update.get('before_value') == 'N'
                and update.get('value') == 'Y',
                'catalog mismatch: unsupported Tax update profile')
        rule = update.get('companion_rule')
        require(isinstance(rule, dict) and rule.get('operation') == 'create'
                and rule.get('same_business_unit') is True and rule.get('count') == 1
                and isinstance(rule.get('values'), dict)
                and set(rule['values']) == {'TerritoryCode', 'EnabledFlag'} | BEHAVIORS,
                'catalog mismatch: unsupported Tax update companion-rule profile')
        require(fingerprint == update.get('schema_sha256'),
                'catalog mismatch: Tax update schema/release is outside the qualified profile')
        require(len(changes) == update['option_count'] and all(
            key in before and before[key]['ValueCode'] == update['before_value']
            and row['ValueCode'] == update['value'] for key, row in changes.items()),
            'catalog mismatch: only named-BU create-Y or the maintained N-to-Y update is qualified')
        rules = index(requested[VAT], VAT, candidate=True)
        existing_rules = index(original[VAT], VAT)
        require(len(rules) == rule['count'] and all(
            key not in existing_rules and (row['BuName'], 'ENABLE_TAX') in changes
            and all(row[field] == value for field, value in rule['values'].items())
            for key, row in rules.items()),
            'catalog mismatch: qualified N-to-Y update requires its same-BU US rule create and tested field values')
        operation_profile = 'update-n-to-y-with-us-rule-create'
    report.update(status='qualified_candidate', profile_qualification_verified=True,
                  qualified_schema_sha256=fingerprint, operation_profile=operation_profile)
    return content, report


def verify_readback(baseline, candidate, readback):
    base_members, base_headers, original = read_package(baseline)
    members, headers, requested = read_package(candidate)
    if requested[SETUP]:
        # Also revalidate the exact switch candidate and its baseline binding.
        prepare_qualification(baseline, candidate, qualification_run=True)
    else:
        require(not requested[CASH] and requested[VAT],
                'input validation: rule-only readback requires empty option aliases and requested rules')
        require(members[META] == base_members[META] and headers == base_headers,
                'catalog mismatch: candidate metadata or ordered headers changed')
        index(requested[VAT], VAT, candidate=True)
    _, _, actual = read_package(readback)
    options = baseline_options(original)
    expected = dict(options)
    changes = index(requested[SETUP], SETUP, candidate=True)
    require(index(requested[CASH], CASH, candidate=True) == changes,
            'input validation: readback requires the final identical-alias candidate')
    expected.update(changes)
    observed = baseline_options(actual)
    # Inserted OtherOrgId may be assigned by the target. Existing transport
    # context and every unrequested option remain protected.
    for key in changes.keys() - options.keys():
        if key in observed:
            expected[key] = dict(expected[key], OtherOrgId=observed[key]['OtherOrgId'])
    require(expected == observed, 'Fusion API: switch readback or protected options differ')
    rules = index(original[VAT], VAT)
    rules.update(index(requested[VAT], VAT, candidate=True))
    require(rules == index(actual[VAT], VAT), 'Fusion API: tax rules or protected fields differ')
    return {'status': 'readback_matched', 'strategy': STRATEGY,
            'requested_option_count': len(changes), 'verified_tax_rule_count': len(rules),
            'export_provenance_verified': False, 'process_result_verified': False,
            'live_import_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', required=True, type=Path)
    parser.add_argument('--baseline-zip', required=True, type=Path)
    parser.add_argument('--candidate-zip', required=True, type=Path)
    parser.add_argument('--qualify-option-aliases', action='store_true',
                        help='Explicit nonproduction maintainer test outside the maintained qualified boundary.')
    parser.add_argument('--readback-zip', type=Path)
    parser.add_argument('--output-zip', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--stage', choices=('switch-create', 'tax-rules'),
                        help='Prepare staged switch/rule creates using the maintained switch-only route.')
    parser.add_argument('--original-baseline-zip', type=Path,
                        help='Pre-switch baseline, required for the tax-rules stage.')
    parser.add_argument('--switch-candidate-zip', type=Path,
                        help='Exact submitted switch-stage candidate, required for the tax-rules stage.')
    args = parser.parse_args()
    try:
        project = args.project_root.resolve()
        state = json.loads((project / 'state/project-state.json').read_text())
        require(isinstance(state, dict), 'input validation: invalid project state')
        require(project.name != '_template' and state.get('project_id') == project.name,
                'input validation: initialized project identity is required')
        for path, area in ((args.baseline_zip, 'exports'), (args.readback_zip, 'exports'),
                           (args.candidate_zip, 'artifacts'), (args.output_zip, 'artifacts'),
                           (args.original_baseline_zip, 'exports'), (args.switch_candidate_zip, 'artifacts')):
            if path is not None:
                require(path.suffix == '.zip' and path.resolve().is_relative_to(project / area),
                        'input validation: ZIP path is outside its selected project area')
        baseline, candidate = args.baseline_zip.read_bytes(), args.candidate_zip.read_bytes()
        require(not args.stage or not (args.qualify_option_aliases or args.readback_zip),
                'input validation: staged creates cannot select qualification or readback mode')
        require((args.stage == 'tax-rules') == bool(args.original_baseline_zip and args.switch_candidate_zip)
                and (args.stage == 'tax-rules' or not (args.original_baseline_zip or args.switch_candidate_zip)),
                'input validation: tax-rules stage requires both original baseline and switch candidate; other modes accept neither')
        if args.readback_zip:
            require(not args.output_zip and not args.dry_run, 'input validation: readback is read-only')
            report = verify_readback(baseline, candidate, args.readback_zip.read_bytes())
        else:
            require(args.dry_run != bool(args.output_zip), 'input validation: select dry-run or output ZIP')
            if args.stage == 'switch-create':
                content, report = prepare_switch_create_stage(baseline, candidate)
            elif args.stage == 'tax-rules':
                content, report = prepare_tax_rules_stage(args.original_baseline_zip.read_bytes(), candidate,
                                                         args.switch_candidate_zip.read_bytes(), baseline)
            elif args.qualify_option_aliases:
                content, report = prepare_qualification(baseline, candidate, qualification_run=True)
            else:
                content, report = prepare_qualified(baseline, candidate)
            if args.output_zip:
                with args.output_zip.open('xb') as output:
                    output.write(content)
        print(json.dumps(report, indent=2))
    except (AliasError, OSError, json.JSONDecodeError) as error:
        # Never print paths, raw payloads, or values from CSVs.
        message = str(error) if isinstance(error, AliasError) else 'artifact persistence: file access failed'
        failure_class = {'input validation': 'input_validation', 'catalog mismatch': 'catalog_or_metadata_mismatch',
                         'approval blocker': 'approval_blocker', 'Fusion API': 'fusion_api_error'}.get(
                             message.split(':')[0], 'artifact_persistence')
        print(json.dumps({'status': 'failed', 'failure_class': failure_class,
                          'message': message, 'live_import_verified': False}))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
