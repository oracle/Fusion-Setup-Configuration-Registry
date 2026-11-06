"""Read the category workbook as inert data and map its values to exact FSM fields."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from zipfile import BadZipFile, ZipFile
from category_scope import ENTITIES, allowed_input, require_scoped_records

ROOT = Path(__file__).resolve().parents[1]
TASK = 'ORA_EXM_MANAGE_POLICIES_BY_EXPENSE_CATEGORY'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
INTEGER_TYPES = {'int', 'integer', 'long', 'short'}
NUMBER_TYPES = INTEGER_TYPES | {'decimal', 'double', 'float', 'number'}


class IntakeError(ValueError):
    pass


def load_catalog():
    return json.loads((ROOT / 'references/intake-fields.json').read_text())


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def present(value):
    return value is not None and (not isinstance(value, str) or bool(value.strip()))


def header(value):
    return re.sub(r'\s+', ' ', str(value or '')).strip().rstrip('*†‡').strip().casefold()


def column(index):
    text = ''
    while index:
        index, rem = divmod(index - 1, 26)
        text = chr(65 + rem) + text
    return text


def column_index(address):
    match = re.fullmatch(r'([A-Z]+)([1-9][0-9]*)', address or '')
    if not match:
        raise IntakeError('Invalid worksheet cell address')
    result = 0
    for char in match[1]:
        result = result * 26 + ord(char) - 64
    return result, int(match[2])


def xml(data):
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise IntakeError('DTD/entity XML is unsupported')
    return ET.fromstring(data)


def checked_zip(path):
    archive = ZipFile(path)
    names = archive.namelist()
    if len(names) != len(set(names)):
        archive.close()
        raise IntakeError('Duplicate archive members')
    if len(names) > 3000 or sum(x.file_size for x in archive.infolist()) > 128 * 1024 * 1024:
        archive.close()
        raise IntakeError('Archive exceeds intake limits')
    for name in names:
        if '\\' in name or name.startswith('/') or '..' in PurePosixPath(name).parts:
            archive.close()
            raise IntakeError('Unsafe archive member')
    return archive


def normalize(value, spec, date1904=False):
    if not present(value):
        return None
    if 'display_values' in spec:
        mapping = spec['display_values']
        if isinstance(value, str):
            for display, code in mapping.items():
                if value.strip().casefold() == display.casefold() or value == code:
                    return code
        raise IntakeError('Select '+ ' or '.join(mapping))
    if spec.get('boolean'):
        if isinstance(value, bool):
            return 'Yes' if value else 'No'
        if isinstance(value, str) and value.strip().casefold() in {'yes', 'no'}:
            return value.strip().capitalize()
        raise IntakeError('Enter Yes or No')
    kind = spec.get('type', 'string')
    if kind in {'date', 'dateTime'}:
        if isinstance(value, Decimal):
            # Excel 1900 serial 60 represents a nonexistent leap day.
            if not date1904 and Decimal(60) <= value < Decimal(61):
                raise IntakeError('Excel serial 60 is not a real date')
            epoch = datetime(1904, 1, 1) if date1904 else datetime(1899, 12, 31)
            serial = value if date1904 or value < 60 else value - 1
            try:
                parsed = epoch + timedelta(microseconds=int(serial * Decimal(86400000000)))
            except (OverflowError, ValueError):
                raise IntakeError('Date is outside the supported range') from None
        elif isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.strip())
            except ValueError:
                raise IntakeError('Enter a real Excel date or ISO YYYY-MM-DD date') from None
            if parsed.tzinfo is not None:
                raise IntakeError('Timezone-bearing dates require a verified field contract')
        else:
            raise IntakeError('Enter a real date')
        if kind == 'date':
            if parsed.time() != datetime.min.time():
                raise IntakeError('Date-only field cannot contain a time')
            return parsed.date().isoformat()
        return parsed.isoformat(timespec='microseconds' if parsed.microsecond else 'seconds')
    if kind in NUMBER_TYPES:
        if isinstance(value, bool):
            raise IntakeError('Enter a number, not a Boolean')
        try:
            result = Decimal(str(value).strip())
        except InvalidOperation:
            raise IntakeError('Enter a number without separators or currency symbols') from None
        if not result.is_finite():
            raise IntakeError('Number must be finite')
        if abs(result.adjusted()) > 1000 or abs(result.as_tuple().exponent) > 1000:
            raise IntakeError('Number exceeds the supported CSV serialization precision')
        if kind in INTEGER_TYPES and result != result.to_integral_value():
            raise IntakeError('Enter a whole number')
        return format(result, 'f')
    if not isinstance(value, str):
        raise IntakeError('Enter this name/code as text to preserve spelling and leading zeros')
    return value.strip() if spec.get('key') else value


def read_workbook(path, catalog=None):
    catalog = catalog or load_catalog()
    if any(s['entity'] not in ENTITIES or s.get('shared_entities') for s in catalog['sheets']):
        raise IntakeError('Intake catalog includes a category outside limited authoring scope')
    if any(not allowed_input(s['entity'], c['csv_field']) and not (
            s['entity'] in {'ORA_EXM_ACCOM_POLICY','ORA_EXM_CARRENTAL_POLICY'}
            and c.get('field') == '_DailyLimitEnabled' and c.get('csv_field') is None
            and c.get('fixed_value') == 'Yes' and c.get('workbook_only') is True)
            for s in catalog['sheets'] for c in s['columns']):
        raise IntakeError('Intake catalog includes a removed input field')
    result = {'schema_version': '1.0', 'task_code': TASK, 'workbook_sha256': sha256(Path(path).read_bytes()),
              'blocks': [], 'source_issues': [], 'issues': [], 'pending_checks': [], 'import_ready': False}

    def issue(sheet, cell, message, source=False):
        item = {'sheet': sheet, 'cell': cell, 'message': message}
        result['issues'].append(item)
        if source:
            result['source_issues'].append(item)

    with checked_zip(path) as archive:
        if any('vbaproject' in n.casefold() or n.startswith('xl/externalLinks/') for n in archive.namelist()):
            raise IntakeError('Macros and external workbook links are unsupported')
        workbook = xml(archive.read('xl/workbook.xml'))
        props = workbook.find('s:workbookPr', NS)
        date1904 = props is not None and props.get('date1904') in {'1', 'true'}
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            strings = [''.join(item.itertext()) for item in xml(archive.read('xl/sharedStrings.xml')).findall('s:si', NS)]
        relations = {r.get('Id'): r for r in xml(archive.read('xl/_rels/workbook.xml.rels'))}
        listed = list(workbook.find('s:sheets', NS))
        sheets = {s.get('name'): s for s in listed}
        if len(sheets) != len(listed):
            raise IntakeError('Duplicate worksheet names')
        expected = {s['name'] for s in catalog['sheets']}
        for name in sorted(set(sheets) - expected - set(catalog['optional_sheets'])):
            issue(name, '', 'Sheet outside limited authoring scope or unknown sheet; values cannot be mapped', True)
        for spec in catalog['sheets']:
            name = spec['name']
            if name not in sheets:
                issue(name, '', 'Missing required category sheet', True)
                continue
            relation = relations[sheets[name].get('{'+REL+'}id')]
            if relation.get('TargetMode') == 'External':
                raise IntakeError('External worksheet is unsupported')
            member = relation.get('Target', '')
            member = member.lstrip('/') if member.startswith('/') else posixpath.normpath('xl/' + member)
            if not member.startswith('xl/') or '..' in PurePosixPath(member).parts:
                raise IntakeError('Unsafe worksheet relationship')
            cells = {}
            for row in xml(archive.read(member)).findall('s:sheetData/s:row', NS):
                for cell in row.findall('s:c', NS):
                    address = cell.get('r')
                    ci, ri = column_index(address)
                    if ri < catalog['header_row']:
                        continue  # Instruction text is never executed or treated as task authority.
                    value_node = cell.find('s:v', NS)
                    value = value_node.text if value_node is not None else None
                    typ = cell.get('t')
                    formula = cell.find('s:f', NS) is not None
                    if formula:
                        issue(name, address, 'Formula cells are not accepted as input', True)
                    if typ == 'e':
                        issue(name, address, 'Excel error cell is not accepted', True)
                    elif typ == 's' and value is not None:
                        value = strings[int(value)]
                    elif typ == 'inlineStr':
                        inline = cell.find('s:is', NS)
                        value = ''.join(inline.itertext()) if inline is not None else ''
                    elif typ == 'b' and value is not None:
                        if value not in {'0', '1'}:
                            raise IntakeError('Invalid Excel Boolean')
                        value = value == '1'
                    elif typ not in {'str', 'd', 'e'} and value is not None:
                        try:
                            value = Decimal(value)
                        except InvalidOperation:
                            raise IntakeError('Malformed numeric Excel cell') from None
                    if (ri, ci) in cells:
                        raise IntakeError('Duplicate worksheet cell address')
                    cells[ri, ci] = (value, formula)
            expected_headers = {header(c['label']): c for c in spec['columns']}
            accepted_headers = {header(label): c for c in spec['columns']
                                for label in [c['label'], *c.get('aliases', [])]}
            columns = {}
            seen = set()
            for (ri, ci), (value, _) in cells.items():
                if ri != catalog['header_row'] or not present(value):
                    continue
                key = header(value)
                field = accepted_headers.get(key)
                if field is not None:
                    key = header(field['label'])
                if key in seen:
                    issue(name, column(ci)+'4', 'Duplicate header', True)
                seen.add(key)
                if field is None:
                    issue(name, column(ci)+'4', 'Unknown header', True)
                else:
                    columns[ci] = field
            for key in expected_headers.keys() - seen:
                if not expected_headers[key].get('optional_header'):
                    issue(name, '4', 'Missing header: '+expected_headers[key]['label'], True)
            block = {'sheet': name, 'entity': spec['entity'], 'kind': spec['kind'], 'rows': [], 'source_cells': []}
            populated_rows = {}
            for (ri, ci), (value, formula) in cells.items():
                if ri >= catalog['first_data_row'] and (present(value) or formula):
                    populated_rows.setdefault(ri, []).append((ci, value, formula))
            for ri, populated in sorted(populated_rows.items()):
                record, locations = {}, {}
                for ci, value, formula in populated:
                    if ci not in columns:
                        issue(name, column(ci)+str(ri), 'Populated cell has no supported header', True)
                        continue
                    field = columns[ci]
                    locations[field['field']] = column(ci)+str(ri)
                    if formula:
                        continue
                    try:
                        normalized = normalize(value, field, date1904)
                        if normalized is not None:
                            if field.get('fixed_value') and normalized != field['fixed_value']:
                                raise IntakeError(field['label']+' is fixed to '+field['fixed_value'])
                            record[field['field']] = normalized
                    except (IntakeError, ValueError, OverflowError) as exc:
                        issue(name, column(ci)+str(ri), str(exc))
                fixed = {c['field'] for c in spec['columns'] if c.get('fixed_value')}
                if record and not (record.keys() - fixed) and all(
                        record.get(c['field'], c['fixed_value']) == c['fixed_value']
                        for c in spec['columns'] if c.get('fixed_value')):
                    continue  # Template's fixed Yes indicators do not create records.
                for field in spec['columns']:
                    if field.get('key') and field['field'] not in record:
                        ci = next((i for i, c in columns.items() if c['field'] == field['field']), 1)
                        issue(name, column(ci)+str(ri), 'Required workbook association: '+field['label'])
                if 'StartDate' in record and 'EndDate' in record and record['EndDate'] < record['StartDate']:
                    issue(name, locations['EndDate'], 'End date precedes start date')
                block['rows'].append(record)
                block['source_cells'].append({'row': ri, 'fields': locations})
            result['blocks'].append(block)
    result['row_count'] = sum(len(b['rows']) for b in result['blocks'])
    # Validate split section identity and contradictions without inventing Fusion keys.
    seen = {}
    for block in result['blocks']:
        spec = next(s for s in catalog['sheets'] if s['name'] == block['sheet'])
        for row, source in zip(block['rows'], block['source_cells']):
            policy = row.get('PolicyName', row.get('_PolicyName'))
            ref = row.get('_Rate Reference', row.get('_Value Reference'))
            if spec['kind'] == 'rate':
                identity = (policy, row.get('StartDate', ''), row.get('EndDate', ''))
            else:
                identity = (policy, ref) if spec['kind'] in {'policy', 'value'} or ref else tuple(sorted(row.items()))
            key = (block['sheet'], identity)
            if key in seen:
                issue(block['sheet'], str(source['row']), 'Duplicate workbook row association')
            seen[key] = True
    try:
        result['records'] = merge_records(result, catalog)
    except IntakeError as exc:
        result['records'] = []
        issue('', '', str(exc))
    if result['records'] and not result['issues']:
        try:
            require_scoped_records(result['records'])
        except ValueError as error:
            issue('', '', str(error))
    result['status'] = 'needs_correction' if result['issues'] else 'local_shape_valid' if result['row_count'] else 'needs_input'
    if not result['row_count']:
        result['pending_checks'].append('No populated input rows; a blank workbook cannot produce a candidate')
    if result['row_count']:
        result['pending_checks'].append('Resolve target operations, required values, field domains, references and entity ownership before import')
    from reduced_rate_profile import workbook_limit_issues
    result['issues'].extend(workbook_limit_issues(result['records']))
    if result['issues']:
        result['status'] = 'needs_correction'
    return result


def merge_records(model, catalog):
    records = {}
    for block in model['blocks']:
        spec = next(s for s in catalog['sheets'] if s['name'] == block['sheet'])
        for row, source in zip(block['rows'], block['source_cells']):
            policy = row.get('PolicyName', row.get('_PolicyName'))
            if spec['kind'] == 'policy':
                identity = policy
            else:
                identity = (block['sheet'], source['row'])
            key = (spec['entity'], identity)
            record = records.setdefault(key, {'entity': spec['entity'], 'kind': spec['kind'], 'policy_name': policy,
                                            'workbook_reference': None, 'values': {}, 'unmapped_inputs': {}, 'sources': [],
                                            'shared_entities': spec.get('shared_entities', [])})
            record['sources'].append({'sheet': block['sheet'], **source})
            for field in spec['columns']:
                name = field['field']
                if name not in row or field.get('workbook_only'):
                    continue
                mapped = field['csv_field']
                if mapped is None:
                    record['unmapped_inputs'][name] = row[name]
                    continue
                if mapped in record['values'] and record['values'][mapped] != row[name]:
                    raise IntakeError('Conflicting split-section values for '+spec['entity']+'.'+mapped)
                record['values'][mapped] = row[name]
    return list(records.values())


def read_package(path, catalog):
    with checked_zip(path) as archive:
        names = archive.namelist()
        metadata = [n for n in names if PurePosixPath(n).name == 'ASM_SETUP_CSV_METADATA.xml']
        if len(metadata) != 1:
            raise IntakeError('Expected exactly one FSM metadata member')
        root = xml(archive.read(metadata[0]))
        identities = {x.text for x in root.iter() if x.tag.rsplit('}', 1)[-1] == 'ObjectShortName'}
        if identities != {TASK}:
            raise IntakeError('FSM task identity mismatch')
        csv_members = {PurePosixPath(n).name for n in names if PurePosixPath(n).suffix.casefold() == '.csv'}
        if csv_members != {e+'.csv' for e in catalog['entities']}:
            raise IntakeError('CSV entity inventory differs from the exact task contract')
        members, grids = {}, {}
        for entity, expected in catalog['entities'].items():
            matches = [n for n in names if PurePosixPath(n).name == entity+'.csv']
            if len(matches) != 1:
                raise IntakeError('Missing/ambiguous CSV member: '+entity)
            member = matches[0]
            rows = list(csv.reader(io.StringIO(archive.read(member).decode('utf-8-sig'))))
            if not rows or rows[0] != expected or len(set(rows[0])) != len(rows[0]):
                raise IntakeError('Exact header contract mismatch: '+entity)
            if any(len(r) != len(expected) for r in rows[1:]):
                raise IntakeError('Malformed CSV row width: '+entity)
            members[entity] = member
            grids[entity] = rows
        return members, grids


def csv_bytes(headers, records):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\r\n', quoting=csv.QUOTE_ALL)
    writer.writerow(headers)
    for record in records:
        writer.writerow([record.get(field, '') for field in headers])
    return stream.getvalue().encode('utf-8')


def artifact_output(destination, project_root):
    """Delegate new output-path admission to the core artifact service."""
    import importlib.util
    service = ROOT.parents[4]/'core/project-mgmt/artifact-registry-manager/scripts/project_artifact_paths.py'
    if not service.is_file():
        raise IntakeError('Core artifact path preflight is unavailable')
    spec = importlib.util.spec_from_file_location('fscr_project_artifact_paths', service)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        return module.validate_artifact_path(destination, project_root)
    except ValueError as error:
        raise IntakeError(str(error)) from error


def draft_projection(model, template_zip, output_dir, catalog=None, *, project_root=None):
    """Write review-only CSV grids; never a ZIP or import-ready candidate."""
    catalog = catalog or load_catalog()
    if model['status'] != 'local_shape_valid':
        raise IntakeError('Correct workbook issues or supply input before CSV projection')
    try:
        require_scoped_records(model['records'])
    except ValueError as error:
        raise IntakeError(str(error)) from error
    _, _ = read_package(template_zip, catalog)
    if any(r['unmapped_inputs'] for r in model['records']):
        raise IntakeError('Populated UI-only field has no established CSV mapping: Policy Start Date')
    if any(r['shared_entities'] for r in model['records']):
        raise IntakeError('Mileage Periods entity ownership is unresolved; do not emit both aliases')
    directory = artifact_output(output_dir, project_root)
    # Draft encodings are explicit review conventions, not approved field domains.
    booleans = {(s['entity'], c['csv_field']) for s in catalog['sheets'] for c in s['columns'] if c.get('boolean')}
    grouped = {}
    for record in model['records']:
        values = {k: ('Y' if v == 'Yes' else 'N') if (record['entity'], k) in booleans else v for k, v in record['values'].items()}
        from single_currency_policy import MEALS, MODE
        if record['entity'] == MEALS:
            values['CurrencyOptionCode'] = MODE
        grouped.setdefault(record['entity'], []).append(values)
    artifact_output(directory, project_root).mkdir(parents=True)
    manifest = {'schema_version':'1.0','task_code':TASK,'kind':'offline_csv_projection','import_ready':False,
                'workbook_sha256':model['workbook_sha256'],'template_sha256':sha256(Path(template_zip).read_bytes()),
                'encoding_boundary':'Yes/No -> Y/N and ISO dates are draft review conventions. Final serialization requires verified field rules.',
                'blank_boundary':'Empty CSV cells in this draft are omitted intake, not authorized clearing/defaulting; overlay a verified baseline before import.',
                'skill_constants':{'ORA_EXM_MEALS_POLICY':{'CurrencyOptionCode':'SINGLE'}},
                'members':[], 'pending_checks':model['pending_checks']}
    for entity, rows in grouped.items():
        data = csv_bytes(catalog['entities'][entity], rows)
        member = entity+'.csv'
        (directory / member).write_bytes(data)
        manifest['members'].append({'file':member,'rows':len(rows),'sha256':sha256(data)})
    (directory / 'projection-review.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def write_json_new(path, data, *, project_root=None):
    path = artifact_output(path, project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['read', 'project'])
    parser.add_argument('--workbook', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--template-zip', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        artifact_output(args.output, args.project_root)
        model = read_workbook(args.workbook)
        if args.command == 'read':
            if not args.dry_run:
                write_json_new(args.output, model, project_root=args.project_root)
            print(json.dumps({'status':model['status'],'row_count':model['row_count'],'issues':model['issues']}))
            return 0 if model['status']=='local_shape_valid' else 2
        if not args.template_zip:
            raise IntakeError('--template-zip is required')
        if args.dry_run:
            read_package(args.template_zip, load_catalog())
            print(json.dumps({'status':model['status'],'rows':model['row_count'],'import_ready':False}))
            return 0 if model['status']=='local_shape_valid' else 2
        review = draft_projection(model,args.template_zip,args.output,project_root=args.project_root)
        print(json.dumps({'status':'offline_csv_projection','import_ready':False,'members':len(review['members'])}))
        return 0
    except (IntakeError, OSError, ValueError, KeyError, IndexError, ET.ParseError, BadZipFile) as exc:
        print(json.dumps({'status':'blocked','failure_class':'input validation','message':str(exc)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
