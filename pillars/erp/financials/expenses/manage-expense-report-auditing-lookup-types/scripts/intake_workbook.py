#!/usr/bin/env python3
"""Offline XLSX intake and destination lookup preflight. Never calls Fusion."""
import sys as _artifact_sys
from pathlib import Path as _ArtifactPath
_artifact_sys.path.insert(0, str(_ArtifactPath(__file__).resolve().parent))
from artifact_publication import publish_files, publish_json
import argparse
import datetime as dt
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / 'references/intake-fields.json').read_text())
TASK = 'EXM_MANAGE_AUDIT_LOOKUP_TYPES'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REL = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
MAP = {'meaning': 'Meaning', 'description': 'Description', 'enabled': 'EnabledFlag',
       'start_date': 'StartDateActive', 'end_date': 'EndDateActive',
       'display_sequence': 'DisplaySequence', 'tag': 'Tag'}
TYPE_MEMBER = 'ORA_FINANCIALS_GENERIC_LOOKUP_TYPE.csv'
TYPE_TL_MEMBER = 'ORA_FINANCIALS_GENERIC_LOOKUP_TYPE_TRANSLATION.csv'


def type_rows(model):
    return model.get('type_rows', [])


def validate_types(model):
    errors, seen = [], set()
    fields = CATALOG['type_sheet']['fields']
    for position, record in enumerate(type_rows(model)):
        locations = model.get('type_source_rows', [])
        row = locations[position] if position < len(locations) else position + 9
        def issue(field, message):
            errors.append({'sheet': 'Lookup Types', 'row': row, 'field': field, 'message': message})
        for key in set(record) - {f['key'] for f in fields}:
            issue(key, 'Unknown field. Correct and reparse the workbook.')
        for field in fields:
            key, value = field['key'], record.get(field['key'])
            if not present(value):
                if field['required_for'] == 'always':
                    issue(key, 'Existing lookup type is required.')
                continue
            if not isinstance(value, str) or len(str(value)) > field['maximum']:
                issue(key, 'Enter text within the model length limit of ' + str(field['maximum']) + '.')
            if value == 'Clear':
                issue(key, 'Clearing is not supported by the verified import contract; blank preserves.')
        if record.get('lookup_type') in seen:
            issue('lookup_type', 'Duplicate lookup type in this workbook.')
        seen.add(record.get('lookup_type'))
    return errors


def present(value):
    return value is not None and str(value).strip() != ''


def norm(value):
    return str(value or '').strip().rstrip('*†‡').strip().casefold()


def iso_date(value):
    # Only the intake date contract. Export date parsing belongs to the snapshot adapter.
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Use a real date as YYYY-MM-DD.')
    dt.date.fromisoformat(value)
    return value


def validate(model):
    errors = list(model.get('source_issues', [])) + validate_types(model)
    if model.get('task_code', TASK) != TASK:
        errors.append({'field': 'task_code', 'message': 'Task identity mismatch.'})
    seen = set()
    for position, record in enumerate(model.get('rows', [])):
        source_rows = model.get('source_rows', [])
        index = source_rows[position] if position < len(source_rows) else position + model.get('first_data_row', 5)
        def issue(field, message):
            errors.append({'row': index, 'field': field, 'message': message})
        for key in set(record) - {f['key'] for f in CATALOG['fields']}:
            issue(key, 'Unknown field. Correct and reparse the workbook.')
        for field in CATALOG['fields']:
            key, value = field['key'], record.get(field['key'])
            if not present(value):
                if field['required_for'] == 'always':
                    issue(key, 'Required identity is missing.')
                continue
            if value == 'Clear':
                if not field['nullable']:
                    issue(key, 'This field cannot be cleared.')
                continue
            if field['kind'] in {'text', 'choice'} and not isinstance(value, str):
                issue(key, 'Enter text. Preserve leading zeros in identifiers.')
            if field['maximum'] and len(str(value)) > field['maximum']:
                issue(key, 'Exceeds the model length limit of ' + str(field['maximum']) + '.')
            if field['kind'] == 'date':
                try:
                    iso_date(value)
                except (ValueError, TypeError):
                    issue(key, 'Use a real date as YYYY-MM-DD.')
            if key == 'enabled' and value not in {'Yes', 'No'}:
                issue(key, 'Select Yes or No.')
            if field['kind'] == 'integer':
                if isinstance(value, bool) or not re.fullmatch(r'-?\d+', str(value)) or abs(int(value)) >= 10**18:
                    issue(key, 'Enter a whole number with at most 18 digits.')
        identity = tuple(record.get(k) for k in ('lookup_type', 'lookup_code', 'set_code'))
        if identity in seen:
            issue('lookup_code', 'Duplicate identity in this workbook.')
        seen.add(identity)
    model['issues'] = errors
    model['status'] = 'invalid' if errors else ('needs_input' if not model.get('rows') and not type_rows(model) else 'pending_destination_checks')
    model['pending_checks'] = ['Fresh lookup type, complete code population, reference data set, meaning uniqueness, retained dates and operation checks.']
    return model


def _read_sheet(path, catalog):
    model = {'schema_version': '3.0', 'task_code': TASK, 'rows': [], 'source_rows': [], 'source_cells': [], 'source_issues': [],
             'workbook_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    def issue(cell, message):
        model['source_issues'].append({'cell': cell, 'message': message})
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or sum(x.file_size for x in z.infolist()) > 25_000_000:
            raise ValueError('Unsafe or oversized workbook archive.')
        if any('vbaproject' in n.lower() or n.startswith('xl/externalLinks/') for n in names):
            raise ValueError('Macros and external workbook links are unsupported.')
        for n in names:
            if n.endswith('.rels'):
                for r in ET.fromstring(z.read(n)):
                    if r.get('TargetMode') == 'External':
                        issue(n, 'External relationships are unsupported. Remove links and reparse.')
        strings = []
        if 'xl/sharedStrings.xml' in names:
            strings = [''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', NS)]
        sheets = ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet', NS)
        allowed_sheets = {'Lookup Codes', 'Lookup Types', 'Reference Lists'}
        if any(s.get('name') not in allowed_sheets for s in sheets) or len(sheets) > 3:
            issue('workbook', 'Use Lookup Types, Lookup Codes and optional Reference Lists. Translation authoring sheets require a separate verified contract.')
        selected = [s for s in sheets if s.get('name') == catalog['sheet_name']]
        if len(selected) != 1:
            if len(selected) > 1:
                issue('workbook', 'Duplicate input sheet.')
            return model
        targets = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        # Reference lists are human guidance, never authoritative destination data.
        # Reject executable cell formulas there as well as on the input sheet.
        for reference in [s for s in sheets if s.get('name') == 'Reference Lists']:
            reference_target = targets[reference.get(REL)]
            reference_member = reference_target.lstrip('/') if reference_target.startswith('/') else 'xl/' + reference_target
            if '..' in Path(reference_member).parts:
                raise ValueError('Unsafe reference sheet path.')
            ref_tree = ET.fromstring(z.read(reference_member))
            for cell in ref_tree.findall('.//s:sheetData/s:row/s:c', NS):
                if cell.find('s:f', NS) is not None or cell.get('t') == 'e':
                    issue('Reference Lists!' + cell.get('r', '?'), 'Reference lists must contain literal values without formulas or errors.')
        target = targets[selected[0].get(REL)]
        member = target.lstrip('/') if target.startswith('/') else 'xl/' + target
        if '..' in Path(member).parts:
            raise ValueError('Unsafe sheet path.')
        tree = ET.fromstring(z.read(member))
        cells, types = {}, {}
        for c in tree.findall('.//s:sheetData/s:row/s:c', NS):
            address, kind = c.get('r'), c.get('t')
            if c.find('s:f', NS) is not None:
                issue(address, 'Formula found. Replace with a literal value and reparse.')
            if kind == 'inlineStr':
                value = ''.join(c.find('s:is', NS).itertext())
            else:
                value = c.findtext('s:v', '', NS)
                if kind == 's':
                    value = strings[int(value)]
                elif value and kind not in {'str', 'e', 'd'}:
                    value = float(value) if '.' in value else int(value)
            if kind == 'e':
                issue(address, 'Excel error value is unsupported.')
            cells[address] = value
            types[address] = kind
        expected = {norm(f['label']): f['key'] for f in catalog['fields']}
        candidates = []
        for possible in (4, 8):
            labels = {norm(v) for address, v in cells.items() if re.fullmatch(r'[A-Z]+' + str(possible), address) and present(v)}
            if set(expected) <= labels:
                candidates.append(possible)
        if len(candidates) > 1:
            issue('workbook', 'Multiple input headers found. Keep one input table.')
        header_row = candidates[0] if len(candidates) == 1 else catalog['header_row']
        first_data_row = header_row + 1
        model.update(header_row=header_row, first_data_row=first_data_row)
        headers = {}
        for address, value in cells.items():
            if re.fullmatch(r'[A-Z]+' + str(header_row), address) and present(value):
                key = expected.get(norm(value))
                col = re.match('[A-Z]+', address)[0]
                if key is None or key in headers.values():
                    issue(address, 'Unknown or duplicate header: ' + str(value))
                else:
                    headers[col] = key
        for key in expected.values():
            if key not in headers.values():
                issue('row ' + str(header_row), 'Missing header for ' + key)
        rows = sorted({int(re.search(r'\d+$', a)[0]) for a, v in cells.items() if present(v) and int(re.search(r'\d+$', a)[0]) >= first_data_row})
        for row in rows:
            record, locations = {}, {}
            for address, value in cells.items():
                if int(re.search(r'\d+$', address)[0]) != row or not present(value):
                    continue
                col = re.match('[A-Z]+', address)[0]
                key = headers.get(col)
                if key is None:
                    issue(address, 'Value is outside the supported table columns.')
                    continue
                field = next(f for f in catalog['fields'] if f['key'] == key)
                if types.get(address) == 'd':
                    if field['kind'] != 'date':
                        issue(address, 'Native Excel dates are only supported in date columns.')
                    else:
                        try:
                            # SpreadsheetML ISO dates may include midnight and UTC Z.
                            # Never truncate a real time or shift a date by a timezone.
                            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:T00:00:00(?:\.0+)?Z?)?', value):
                                raise ValueError()
                            value = iso_date(value[:10])
                        except (ValueError, TypeError):
                            issue(address, 'Use a real date without a time component or timezone offset.')
                if field['kind'] == 'date' and isinstance(value, (int, float)):
                    if value != int(value):
                        issue(address, 'Date includes a time component.')
                    # Both standard Excel date systems are supported.
                    prop = ET.fromstring(z.read('xl/workbook.xml')).find('s:workbookPr', NS)
                    epoch = dt.date(1904, 1, 1) if prop is not None and prop.get('date1904') in {'1', 'true'} else dt.date(1899, 12, 30)
                    value = (epoch + dt.timedelta(days=int(value))).isoformat()
                if field['kind'] == 'integer' and isinstance(value, float) and value.is_integer():
                    value = int(value)
                record[key], locations[key] = value, address
            if record:
                model['rows'].append(record)
                model['source_rows'].append(row)
                model['source_cells'].append(locations)
    return model


def read_workbook(path):
    model = _read_sheet(path, CATALOG)
    types = _read_sheet(path, CATALOG['type_sheet'])
    for key in ('rows', 'source_rows', 'source_cells', 'header_row', 'first_data_row'):
        if key in types:
            model['type_' + key] = types[key]
    for issue in types['source_issues']:
        located = dict(issue, sheet='Lookup Types')
        if located not in model['source_issues']:
            model['source_issues'].append(located)
    return validate(model)


def preflight(model, snapshot, environment, now=None):
    model = validate(model)
    errors = list(model['issues'])
    def error(row, field, message):
        errors.append({'row': row, 'field': field, 'message': message})
    if snapshot.get('task_code') != TASK or snapshot.get('environment') != environment:
        error(None, 'snapshot', 'Task or environment mismatch.')
    try:
        captured = dt.datetime.fromisoformat(snapshot['captured_at'].replace('Z', '+00:00'))
        age = ((now or dt.datetime.now(dt.timezone.utc)) - captured).total_seconds()
        if age < -60 or age > 3600:
            raise ValueError()
    except (KeyError, ValueError, TypeError):
        error(None, 'snapshot', 'Provide target evidence captured within the last hour.')
    if snapshot.get('complete') is not True or (model.get('rows') and
            (snapshot.get('codes_complete') is not True or snapshot.get('sets_complete') is not True)):
        error(None, 'snapshot', 'Lookup, code and set pagination must all be complete.')
    resolved_types = []
    for position, record in enumerate(type_rows(model)):
        locations = model.get('type_source_rows', [])
        index = locations[position] if position < len(locations) else position + 9
        def type_error(field, message):
            errors.append({'sheet': 'Lookup Types', 'row': index, 'field': field, 'message': message})
        matches = [t for t in snapshot.get('types', []) if t.get('LookupType') == record.get('lookup_type')]
        if len(matches) != 1:
            type_error('lookup_type', 'Resolve exactly one existing lookup type and view. This FSM page does not create lookup types.')
            continue
        t = matches[0]
        if t.get('ModuleId') not in snapshot.get('expenses_module_ids', []) or not re.fullmatch(r'\d+', str(t.get('ViewApplicationId'))):
            type_error('lookup_type', 'Verify the existing type in the Expenses module/descendant scope and its view.')
            continue
        if t.get('CustomizationLevel') not in {'S', 'E', 'U'}:
            type_error('lookup_type', 'Verify the target configuration level; never take it from an editable reference list.')
        changes = {}
        for field, target in [('meaning', 'Meaning'), ('description', 'Description')]:
            value = record.get(field)
            if present(value) and value != t.get(target):
                changes[target] = value
        if changes:
            context = snapshot.get('text_context', {})
            language = context.get('language')
            if not language or not context.get('source_ref') or context.get('export_language') != language or context.get('import_language') != language:
                type_error('snapshot', 'Verify matching destination session, export and import language before changing translated type text.')
            scopes = [r for r in snapshot.get('type_translation_scopes', []) if r.get('LookupType') == t['LookupType']
                      and str(r.get('ViewApplicationId')) == str(t['ViewApplicationId']) and r.get('complete') is True and r.get('source_ref')]
            if len(scopes) != 1:
                type_error('snapshot', 'Complete selected-type translation preservation evidence is required.')
        resolved_types.append({'source_sheet': 'Lookup Types', 'source_row': index, 'operation': 'update',
                               'identity': {k: t[k] for k in ('LookupType', 'ViewApplicationId')}, 'changes': changes})
    resolved, final_population = [], {}
    for r in snapshot.get('codes', []) if model.get('rows') else []:
        if any(r.get(k) is None for k in ('LookupType', 'ViewApplicationId', 'SetId', 'LookupCode')):
            error(None, 'snapshot', 'Code evidence lacks full type/view/set/code identity; do not infer set context from a generic REST response.')
            continue
        key = (r.get('LookupType'), str(r.get('ViewApplicationId')), str(r.get('SetId')), r.get('LookupCode'))
        if key in final_population:
            error(None, 'snapshot', 'Duplicate code identity in destination evidence.')
        final_population[key] = r.copy()
    for position, record in enumerate(model.get('rows', [])):
        source_rows = model.get('source_rows', [])
        index = source_rows[position] if position < len(source_rows) else position + model.get('first_data_row', 5)
        types = [t for t in snapshot.get('types', []) if t.get('LookupType') == record.get('lookup_type')]
        sets = [s for s in snapshot.get('sets', []) if s.get('SetCode') == record.get('set_code')]
        if len(types) != 1 or len(sets) != 1:
            error(index, 'lookup_type', 'Lookup type and reference data set must each resolve exactly once; clarify view context if ambiguous.')
            continue
        t, s = types[0], sets[0]
        if any(not re.fullmatch(r'\d+', str(v)) for v in (t.get('ViewApplicationId'), s.get('SetId'))):
            error(index, 'snapshot', 'Verified view and set IDs must be nonnegative integer identities.')
            continue
        module_ids = snapshot.get('expenses_module_ids', [])
        if not module_ids or t.get('ModuleId') not in module_ids:
            error(index, 'lookup_type', 'Lookup type is not verified in the Expenses APPLICATION module.')
            continue
        key = (record['lookup_type'], str(t.get('ViewApplicationId')), str(s.get('SetId')), record.get('lookup_code'))
        scopes = [v for v in snapshot.get('code_scopes', []) if v.get('LookupType') == key[0]
                  and str(v.get('ViewApplicationId')) == key[1] and str(v.get('SetId')) == key[2]
                  and v.get('complete') is True and v.get('source_ref')]
        if len(scopes) != 1:
            error(index, 'snapshot', 'Complete code evidence is required for this exact lookup type/view/set scope.')
            continue
        existing = final_population.get(key)
        operation = 'update' if existing else 'create'
        changes = {}
        if operation == 'create' and not present(record.get('meaning')):
            error(index, 'meaning', 'Meaning is required for a new code.')
        for k, target in MAP.items():
            value = record.get(k)
            if not present(value):
                continue
            if value == 'Clear':
                if operation == 'create':
                    error(index, k, 'Clear applies only to an existing code.')
                # Clearing requires explicit verified import null serialization.
                error(index, k, 'Explicit clearing requires a verified null import contract; blank preserves the value.')
                continue
            converted = ('Y' if value == 'Yes' else 'N') if k == 'enabled' else value
            if existing and str(converted) == str(existing.get(target)):
                continue
            changes[target] = converted
        if not existing:
            changes.setdefault('EnabledFlag', 'Y')
        level = t.get('CustomizationLevel')
        if level not in {'S', 'E', 'U'}:
            error(index, 'lookup_type', 'Verify the target configuration level before deriving UI permissions.')
        if operation == 'create' and level == 'S':
            error(index, 'lookup_code', 'System lookup types disable code creation for an ordinary admin.')
        restricted = {'EnabledFlag', 'StartDateActive', 'EndDateActive', 'Tag'} & changes.keys()
        if existing and restricted:
            allowed = level == 'U' or (level == 'E' and present(existing.get('CreatedBy')) and existing['CreatedBy'] != 'SEED_DATA_FROM_APPLICATION')
            for field in restricted:
                if str(changes[field]) != str(existing.get(field, '')) and not allowed:
                    error(index, field, 'The FSM UI disables this field for a System code or a seeded Extension code; verify CreatedBy for Extension codes.')
        result = dict(existing or {}, **changes)
        result.update(LookupType=key[0], ViewApplicationId=key[1], SetId=key[2], LookupCode=key[3])
        start, end = result.get('StartDateActive'), result.get('EndDateActive')
        if start and end:
            try:
                if iso_date(start) > iso_date(end):
                    error(index, 'end_date', 'End date precedes the resulting start date.')
            except ValueError:
                error(index, 'start_date', 'Destination date must be normalized unambiguously before comparison.')
        final_population[key] = result
        resolved.append({'source_row': index, 'operation': operation, 'identity': {'LookupType': key[0], 'LookupCode': key[3], 'ViewApplicationId': t.get('ViewApplicationId'), 'SetCode': s['SetCode']}, 'changes': changes})
    meanings = {}
    for key, value in final_population.items():
        meaning_key = key[:3] + (value.get('Meaning'),)
        if meaning_key in meanings and meanings[meaning_key] != key and present(value.get('Meaning')):
            error(None, 'meaning', 'Duplicate resulting meaning within lookup type, view and set.')
        meanings[meaning_key] = key
    return {'task_code': TASK, 'environment': environment, 'status': 'blocked' if errors or not (resolved or resolved_types) else 'ready_for_design_review',
            'issues': errors, 'resolved_rows': resolved, 'resolved_type_rows': resolved_types,
            'checks': ['lookup_type', 'lookup_code', 'reference_data_set', 'expenses_module', 'complete_pagination', 'freshness', 'meaning_uniqueness', 'retained_date_ranges', 'ui_permissions', 'type_text_language', 'type_translation_preservation'],
            'execution_authorized': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['read', 'validate', 'preflight'])
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--snapshot', type=Path)
    p.add_argument('--environment')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        p.error('Refusing to overwrite output.')
    model = read_workbook(args.input) if args.command == 'read' else validate(json.loads(args.input.read_text()))
    if args.command == 'preflight':
        if not args.snapshot or not args.environment:
            p.error('preflight requires --snapshot and --environment')
        model = preflight(model, json.loads(args.snapshot.read_text()), args.environment)
    publish_json(args.output, model, ensure_ascii=False)
    print(json.dumps({'status': model['status'], 'issues': len(model['issues'])}))
    return 1 if model['issues'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
