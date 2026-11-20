"""Offline CREATE package preparation; no network, approval or import authority."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import zipfile
import xml.etree.ElementTree as ET

TASK = 'EXM_MANAGE_CORPORATE_CARD_PROGRAMS'
META = 'ASM_SETUP_CSV_METADATA.xml'
ROOT = 'EXM_CARD_PROGRAM.csv'
COMPANY = 'EXM_CC_COMPANY_ACCOUNT.csv'
UPLOAD = 'EXM_CARD_UPLOAD_RULE.csv'
HEADERS = json.loads((Path(__file__).resolve().parents[1] / 'references/package-headers.json').read_text())
PARENT = ['CardProgramName', 'CardTypeLookupCode', 'CardBrandLookupCode']
FORMATS = {'AmericanExpress': 'FILE_FMT_AMEX_GL1025', 'MasterCard': 'FILE_FMT_MSTRCARD_CDF3',
           'Visa': 'FILE_FMT_VISA', 'Diners': 'FILE_FMT_DINERS'}
ALLOWED = {
    ROOT: set(PARENT + ['Description', 'EnableCcTokenFlag']),
    COMPANY: {'CompanyAccountName', 'CompanyNumber', 'BuName', 'PayablesBUName',
              'CardIssuerName', 'CardIssuerSiteName', 'PartyNumber', 'PaymentTermName',
              'PaymentCurrencyCode', 'PaymentDueFromCode', 'ExpenseCcidSegments', 'Name',
              'Address1', 'Address2', 'Address3', 'Address4', 'City', 'Country', 'State',
              'Province', 'PostalCode'},
    UPLOAD: {'FileFormatCode', 'CardEmpMatchingRule', 'CcExpTypSumSourceCol', 'MapTypeCode',
             'CcExpTypDtlSourceCol', 'MapTypeCode1', 'MatchEmployeeAcrossBu', 'DetailWaitingDuration'},
}
MAX_MEMBER = 10 * 1024 * 1024


def inspect_package(path, environment):
    """Validate exact inventory, metadata and every physical CSV row without extraction."""
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != {*HEADERS, META}:
            raise ValueError('Package must contain exactly six unique CSVs and task metadata')
        if any(PurePosixPath(n).name != n or '\\' in n for n in names):
            raise ValueError('Unsafe archive member')
        if any(i.file_size > MAX_MEMBER or i.flag_bits & 1 for i in infos):
            raise ValueError('Oversized or encrypted archive member')
        members = {n: archive.read(n) for n in names}
    if b'<!DOCTYPE' in members[META].upper() or b'<!ENTITY' in members[META].upper():
        raise ValueError('XML declarations are unsupported')
    xml = ET.fromstring(members[META])
    def one(tag):
        found = xml.findall('./MigrationProcessCSVMetadataVORow/' + tag)
        if len(found) != 1 or not found[0].text:
            raise ValueError('Missing or ambiguous metadata ' + tag)
        return found[0].text
    if one('ObjectShortName') != TASK or one('ObjectType') != 'TASK':
        raise ValueError('Wrong task identity')
    if one('ProcessEnv') != environment or one('ProcessStatus') != 'COMPLETED':
        raise ValueError('Wrong environment or incomplete source export')
    release = one('ProcessRelease')
    rows = {}
    for name, header in HEADERS.items():
        parsed = list(csv.reader(io.StringIO(members[name].decode('utf-8-sig'), newline=''), strict=True))
        if not parsed or parsed[0] != header:
            raise ValueError('Header mismatch: ' + name)
        if any(len(row) != len(header) for row in parsed[1:]):
            raise ValueError('Row width mismatch: ' + name)
        rows[name] = [dict(zip(header, row)) for row in parsed[1:]]
    return members, rows, release


def normalize_design(design):
    if not isinstance(design, dict) or set(design) != {'operation', 'rows'} or design['operation'] != 'CREATE':
        raise ValueError('Expected CREATE and rows only')
    supplied = design['rows']
    if not isinstance(supplied, dict) or ROOT not in supplied or set(supplied) - ALLOWED.keys():
        raise ValueError('Unsupported entity scope; existing issuer/site references only')
    rows, skipped = {}, []
    for name, values in supplied.items():
        if not isinstance(values, dict) or set(values) - ALLOWED[name]:
            raise ValueError('Unsupported fields: ' + name)
        clean = {}
        for key, value in values.items():
            if value is not None and not isinstance(value, str):
                raise ValueError('Values must be text or null: ' + key)
            if value is None or not value.strip():
                skipped.append(name + '.' + key)
            else:
                if any(ord(c) < 32 for c in value):
                    raise ValueError('Control characters are unsupported: ' + key)
                clean[key] = value
        rows[name] = clean
    def require(name, fields):
        absent = [field for field in fields if not rows[name].get(field)]
        if absent:
            raise ValueError('Missing required fields in ' + name + ': ' + ', '.join(absent))
    require(ROOT, PARENT)
    root = rows[ROOT]
    if root['CardTypeLookupCode'] != 'TRAVEL' or root['CardBrandLookupCode'] not in FORMATS:
        raise ValueError('Resolve exact type and brand codes before preparation')
    for name, field, maximum in [(ROOT, 'CardProgramName', 80), (ROOT, 'Description', 240),
                                  (COMPANY, 'CompanyAccountName', 80), (COMPANY, 'CompanyNumber', 30)]:
        if len(rows.get(name, {}).get(field, '')) > maximum:
            raise ValueError('Field exceeds source length: ' + field)
    if root.get('EnableCcTokenFlag') not in {None, 'Y', 'M'}:
        raise ValueError('Invalid token code')
    derived = []
    if COMPANY in rows:
        require(COMPANY, ['CompanyAccountName', 'CompanyNumber', 'BuName', 'CardIssuerName',
                         'CardIssuerSiteName', 'PartyNumber', 'Address1', 'Country'])
        company = rows[COMPANY]
        if root['CardTypeLookupCode'] != 'PROCUREMENT':
            require(COMPANY, ['PaymentTermName', 'PaymentCurrencyCode', 'PaymentDueFromCode'])
            if company['PaymentDueFromCode'] not in {'COMPANY', 'BOTH'}:
                raise ValueError('This reviewed company-account path supports COMPANY or BOTH; other options need their source-backed contract')
            if company['PaymentDueFromCode'] in {'COMPANY', 'BOTH'}:
                require(COMPANY, ['ExpenseCcidSegments', 'Name'])
        if 'ExpenseCcidSegments' in company:
            value = company['ExpenseCcidSegments']
            parts = value.split('-')
            if len(parts) > 30 or any(not p or p != p.strip() for p in parts) or any(c in value for c in '.,/|;'):
                raise ValueError('Invalid account segment encoding')
        if company.get('PayablesBUName') and company['PayablesBUName'] != company['BuName']:
            raise ValueError('Conflicting business units')
    if UPLOAD in rows:
        upload = rows[UPLOAD]
        if not upload.get('FileFormatCode'):
            upload['FileFormatCode'] = FORMATS[root['CardBrandLookupCode']]
            derived.append(UPLOAD + '.FileFormatCode')
        for mapping, source in [('MapTypeCode', 'CcExpTypSumSourceCol'), ('MapTypeCode1', 'CcExpTypDtlSourceCol')]:
            if bool(upload.get(mapping)) != bool(upload.get(source)):
                raise ValueError('Mapping and source column must be supplied together')
            if len(upload.get(mapping, '')) > 30:
                raise ValueError('Mapping code exceeds 30 characters')
        if upload.get('MatchEmployeeAcrossBu') not in {None, 'Y', 'N'}:
            raise ValueError('Invalid cross-business-unit code')
        days = upload.get('DetailWaitingDuration')
        if days is not None and (not days.isascii() or not days.isdigit() or int(days) > 999999999):
            raise ValueError('Invalid waiting duration')
    parent = {'EXM_CARD_PROGRAM.' + key: root[key] for key in PARENT}
    for name in (COMPANY, UPLOAD):
        if name in rows:
            rows[name].update(parent)
    return rows, sorted(skipped), derived


def build_package(template, baseline, design, environment):
    members, template_rows, release = inspect_package(template, environment)
    if any(template_rows.values()):
        raise ValueError('Template must have no data rows')
    _, current, baseline_release = inspect_package(baseline, environment)
    if release != baseline_release:
        raise ValueError('Template and baseline releases differ')
    rows, skipped, derived = normalize_design(design)
    requested = rows[ROOT]['CardProgramName'].strip().casefold()
    if any(row['CardProgramName'].strip().casefold() == requested for row in current[ROOT]):
        raise ValueError('CREATE conflicts with an existing program')
    for name, header in HEADERS.items():
        stream = io.StringIO(newline='')
        writer = csv.writer(stream, lineterminator='\r\n')
        writer.writerow(header)
        if name in rows:
            writer.writerow([rows[name].get(field, '') for field in header])
        members[name] = stream.getvalue().encode('utf-8')
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, members[name])
    payload = output.getvalue()
    inspect_package(io.BytesIO(payload), environment)
    return payload, {'status': 'prepared_offline', 'taskCode': TASK,
        'sha256': hashlib.sha256(payload).hexdigest(),
        'rowCounts': {n: int(n in rows) for n in HEADERS},
        'skippedEmptyFields': skipped, 'derivedFields': derived,
        'importReady': False, 'importAuthorized': False,
        'remainingGates': ['Current target references and baseline provenance',
                           'Data Loader and Task Hook validation', 'Exact artifact approval']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--environment', required=True, help='Exact FSM ProcessEnv, not the OAuth profile name')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        def unique_pairs(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError('Duplicate JSON key: ' + key)
                result[key] = value
            return result
        design = json.loads(args.input.read_text(), object_pairs_hook=unique_pairs)
        payload, report = build_package(args.template, args.baseline, design, args.environment)
        if not args.dry_run:
            if args.output is None:
                raise ValueError('--output is required unless --dry-run is used')
            with args.output.open('xb') as target:
                target.write(payload)
        print(json.dumps(report, indent=2))
        return 0
    except (ValueError, OSError, zipfile.BadZipFile, ET.ParseError, csv.Error) as exc:
        print(json.dumps({'status': 'blocked', 'message': str(exc), 'importReady': False}))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
