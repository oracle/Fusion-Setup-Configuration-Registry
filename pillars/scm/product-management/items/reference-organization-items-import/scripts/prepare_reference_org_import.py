#!/usr/bin/env python3
"""Prepare or validate a reference-org source ZIP for the standard Core loader."""
from __future__ import annotations
import argparse
import csv
import io
import json
import os
from pathlib import Path
import re
import sys
from typing import NamedTuple
from xml.etree import ElementTree as ET
import zipfile

REPO = next((p for p in Path(__file__).resolve().parents
             if (p / 'pillars').is_dir() and (p / 'schemas').is_dir()), None)


class PreparationError(ValueError):
    """A local reference-org schema/input error, independent of Core transport."""

    def __init__(self, stage, message):
        self.stage = stage
        super().__init__(stage + ': ' + message)


class Member(NamedTuple):
    name: str
    content: bytes

# Supported domain mapping, checked against supplied template/control files.
SHEETS = {
    'EGP_IMPORT_REF_ORG_ITEMS_INT': ('EgpImportRefOrgItemsInt', ('BATCH_ID', 'ITEM_NUMBER'), ('Batch ID', 'Item Number')),
    'EGP_IMPORT_REF_ORG_ORGS_INT': ('EgpImportRefOrgOrgsInt', ('BATCH_ID', 'DEF_ORG_CODE', 'REF_ORG_CODE'), ('Batch ID', 'Definition Organization Code', 'Reference Organization Code')),
    'EGP_IMPORT_REF_ORG_STRUCT_INT': ('EgpImportRefOrgStructInt', ('BATCH_ID', 'ITEM_NUMBER', 'STRUCTURE_NAME'), ('Batch ID', 'Item Number', 'Structure Name')),
}
MODES = ('assign', 'structures', 'both')
IMPORT_MODES = {
    'assign': 'ORA_REF_ORG_ASSIGN_ONLY',
    'structures': 'ORA_REF_ORG_BOM_COMMON_ONLY',
    'both': 'ORA_REF_ORG_ASSGN_BOM_COMMON',
}
DEFAULT_IMPORT_MODE = IMPORT_MODES['both']
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
MAX_INPUT = 16 * 1024 * 1024


def fail(message):
    raise PreparationError('input-validation', message)


def capture_schema(path, suffix):
    """Capture a template/control file, not a loader payload source."""
    if path.suffix.lower() != suffix or not path.is_file():
        fail('Supply a readable ' + suffix + ' schema file.')
    if path.stat().st_size > 64 * 1024 * 1024:
        fail('Schema file exceeds the supported size.')
    content = path.read_bytes()
    if not content or len(content) > 64 * 1024 * 1024:
        fail('Schema file is empty or exceeds the supported size.')
    return content


def resolve_import_mode(request):
    """Default only an omitted mode; preserve explicit supported lookup choices."""
    def resolve(value):
        if not isinstance(value, str) or not value.strip():
            fail('Explicit Import Mode cannot be blank or null.')
        value = value.strip()
        for alias, code in IMPORT_MODES.items():
            if value.casefold() in (code.casefold(), alias):
                return alias, code
        fail('Unsupported explicit Import Mode; resolve its lookup code before loading. It was not replaced by the default.')
    provided = [resolve(request[key]) for key in ('mode', 'import_mode') if key in request]
    if provided and any(value != provided[0] for value in provided[1:]):
        fail('mode and import_mode specify conflicting operations.')
    return provided[0] if provided else ('both', DEFAULT_IMPORT_MODE)


def parse_input(content):
    try:
        request = json.loads(content)
    except (ValueError, UnicodeDecodeError):
        fail('Mapped input must be valid JSON.')
    if not isinstance(request, dict) or set(request) - {'batch_id', 'mode', 'import_mode', 'items', 'organizations', 'structures'}:
        fail('Mapped input contains unsupported request fields.')
    missing = [key for key in ('batch_id', 'organizations') if key not in request]
    if missing:
        fail('Missing required fields: ' + ', '.join(missing))
    batch = request['batch_id']
    if isinstance(batch, bool) or not isinstance(batch, (str, int)) or not re.fullmatch(r'[0-9]{1,18}', str(batch)):
        fail('batch_id must be an integer of at most 18 digits, without floating-point conversion.')
    request['mode'], request['import_mode'] = resolve_import_mode(request)
    for field in ('items', 'organizations', 'structures'):
        rows = request.get(field, [])
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            fail(field + ' must be an array of mapped objects.')
    if not request['organizations']:
        fail('Missing organizations.')
    if request['mode'] in ('assign', 'both') and not request.get('items'):
        fail('Missing items for assignment.')
    if request['mode'] == 'structures' and not request.get('structures'):
        fail('Missing structures for the selected mode.')
    if request['mode'] == 'assign' and request.get('structures'):
        fail('Assignment-only mode cannot silently discard supplied structures.')
    return request


def validate_execution_mode(request):
    """The current loader route has no per-run ESS argument carrier."""
    if request['import_mode'] != DEFAULT_IMPORT_MODE:
        raise PreparationError('catalog-or-metadata-mismatch',
            'The current loader route cannot forward this Import Mode override to ESS. '
            'No load was started. Use a separately supported execution route or add '
            'a supported per-run parameter binding; the requested mode was not replaced.')


def workbook_contract(content):
    """Read schema metadata only; never execute macros or reuse example data."""
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            if sum(i.file_size for i in z.infolist()) > 128 * 1024 * 1024:
                fail('Template exceeds the supported uncompressed size.')
            strings = []
            if 'xl/sharedStrings.xml' in z.namelist():
                root = ET.fromstring(z.read('xl/sharedStrings.xml'))
                strings = [''.join(t.text or '' for t in s.findall('.//m:t', NS)) for s in root.findall('m:si', NS)]
            rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
            result = []
            for sheet in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet', NS):
                name = sheet.get('name')
                if name not in SHEETS:
                    if name.startswith('EGP_IMPORT_REF_ORG_'):
                        fail('Unsupported additional reference-org interface sheet; update the mapping contract.')
                    continue
                target = rels[sheet.get('{'+NS['r']+'}id')]
                path = target.lstrip('/') if target.startswith('/') else 'xl/' + target
                root = ET.fromstring(z.read(path))
                values = {}
                for cell in root.findall('m:sheetData/m:row/m:c', NS):
                    address = cell.get('r', '')
                    if not re.fullmatch(r'[A-Z]+[46]', address):
                        continue
                    if cell.find('m:f', NS) is not None:
                        fail('Formula-based schema metadata is unsupported; use the authoritative export contract.')
                    value = cell.find('m:v', NS)
                    text = value.text if value is not None and value.text else ''
                    if cell.get('t') == 's':
                        text = strings[int(text)]
                    elif cell.get('t') == 'inlineStr':
                        text = ''.join(t.text or '' for t in cell.findall('m:is//m:t', NS))
                    values[address] = text.strip().lstrip('*').strip()
                headers = [values.get(chr(66+i)+'4', '') for i in range(len(SHEETS[name][2]))]
                if values.get('A4') != 'Name' or tuple(headers) != SHEETS[name][2]:
                    fail('Template column drift on ' + name + '; update mapping before import.')
                expected = {chr(66+i)+'4' for i in range(len(headers))}
                if any(a.endswith('4') and a != 'A4' and a not in expected and v for a, v in values.items()):
                    fail('Unexpected export column on ' + name + '.')
                limits = []
                for i in range(len(headers)):
                    match = re.fullmatch(r'VARCHAR2\((\d+)\)', values.get(chr(66+i)+'6', ''), re.I)
                    limits.append(int(match.group(1)) if match else None)
                result.append((name, limits))
            if {name for name, _ in result} != set(SHEETS):
                fail('Template must contain all three reference-org schema sheets.')
            return result
    except (zipfile.BadZipFile, KeyError, ET.ParseError, ValueError, IndexError, RuntimeError):
        fail('Template workbook is malformed or has unsupported schema metadata.')


def control_limits(content, sheet):
    try:
        text = content.decode('utf-8-sig')
    except UnicodeDecodeError:
        fail('Control file must be UTF-8.')
    if not re.search(r'INTO\s+TABLE\s+' + sheet + r'\b', text, re.I):
        fail('Control file table mismatch for ' + sheet + '.')
    if not re.search(r'CHARACTERSET\s+UTF8\b', text, re.I) or not re.search(r'LENGTH\s+SEMANTICS\s+CHAR\b', text, re.I) or not re.search(r"FIELDS\s+TERMINATED\s+BY\s+','\s+OPTIONALLY\s+ENCLOSED\s+BY\s+'\"'\s+TRAILING\s+NULLCOLS", text, re.I):
        fail('Unsupported control-file CSV encoding/delimiter/null contract.')
    start = text.find('(BATCH_ID')
    if start < 0:
        fail('Unsupported control-file field layout.')
    fields = []
    for line in text[start:].splitlines():
        line = line.strip().lstrip('(').rstrip(',').strip()
        if not line or line == ')':
            continue
        match = re.match(r'^([A-Z_]+)\b(.*)$', line)
        if not match:
            fail('Unsupported control-file field declaration.')
        name, rest = match.groups()
        if re.search(r'\b(CONSTANT|EXPRESSION)\b', rest, re.I) or re.fullmatch(r'\s*"[^"]+"\s*', rest):
            continue
        length = re.fullmatch(r'\s*char\((\d+)\)\s*', rest, re.I)
        if rest.strip() and not length:
            fail('Unsupported input column type for ' + name + '.')
        fields.append((name, int(length.group(1)) if length else None))
    if tuple(name for name, _ in fields) != SHEETS[sheet][1]:
        fail('Control-file input columns drifted for ' + sheet + '.')
    return [length for _, length in fields]


def prepare_members(request_content, template_content, controls):
    request = parse_input(request_content)
    layout = workbook_contract(template_content)
    if set(controls) != set(SHEETS):
        fail('Supply one matching control file for each reference-org sheet.')
    batch = str(request['batch_id'])
    members = []
    for sheet, workbook_limits in layout:
        stem, fields, _ = SHEETS[sheet]
        lengths = control_limits(controls[sheet], sheet)
        kind = {'ITEMS': 'items', 'ORGS': 'organizations', 'STRUCT': 'structures'}[sheet.split('_')[-2]]
        rows = request.get(kind, [])
        if not rows:
            continue
        buf = io.StringIO(newline='')
        writer = csv.writer(buf, lineterminator='\n')
        for index, row in enumerate(rows, 1):
            if set(row) - set(fields):
                fail(f'{sheet} row {index}: unsupported mapped fields.')
            values = []
            for field, ctl_limit, wb_limit in zip(fields, lengths, workbook_limits):
                value = row.get(field, batch if field == 'BATCH_ID' else '')
                if not isinstance(value, (str, int)) or isinstance(value, bool):
                    fail(f'{sheet} row {index}: {field} must be text or an integer.')
                value = str(value)
                if any(ord(c) < 32 for c in value):
                    fail(f'{sheet} row {index}: {field} contains a control character.')
                if field == 'BATCH_ID' and value != batch:
                    fail(f'{sheet} row {index}: Batch ID mismatch.')
                limits = [n for n in (ctl_limit, wb_limit) if n is not None]
                if limits and len(value) > min(limits):
                    fail(f'{sheet} row {index}: {field} exceeds the template/control length.')
                values.append(value)
            if kind == 'items' and not values[1].strip():
                fail(f'{sheet} row {index}: missing ITEM_NUMBER.')
            if kind in ('organizations', 'structures') and not any(v.strip() for v in values[1:]):
                fail(f'{sheet} row {index}: missing organization or structure selectors.')
            if kind == 'structures' and not all(v.strip() for v in values[1:]) and not request.get('items'):
                fail('Partial structure selection requires the item list.')
            writer.writerow(values)
        content = buf.getvalue().encode('utf-8')
        if any(len(row) != len(fields) for row in csv.reader(io.StringIO(content.decode('utf-8')))):
            fail('CSV round-trip field-count validation failed.')
        members.append(Member(stem + '.csv', content=content))
    return tuple(members), request


def validate_native_archive(content, template_content, controls, *, batch_id, mode=None, import_mode=None):
    """Validate captured native bytes against this run's template; never repack."""
    request = {'batch_id': batch_id, 'items': [],
               'organizations': [], 'structures': []}
    if mode is not None:
        request['mode'] = mode
    if import_mode is not None:
        request['import_mode'] = import_mode
    layout = workbook_contract(template_content)
    contracts = {SHEETS[sheet][0] + '.csv': (sheet, SHEETS[sheet][1])
                 for sheet, _ in layout}
    kinds = {'ITEMS': 'items', 'ORGS': 'organizations', 'STRUCT': 'structures'}
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            infos = archive.infolist()
            if not infos or sum(info.file_size for info in infos) > 128 * 1024 * 1024:
                fail('Native archive is empty or exceeds the supported uncompressed size.')
            names = [info.filename for info in infos]
            if len({name.casefold() for name in names}) != len(names):
                fail('Native archive contains duplicate member names.')
            for info in infos:
                if info.is_dir() or info.filename not in contracts or info.flag_bits & 1:
                    fail('Native archive contains an unsafe, encrypted or unexpected member.')
                sheet, fields = contracts[info.filename]
                text = archive.read(info).decode('utf-8-sig')
                rows = list(csv.reader(io.StringIO(text), strict=True))
                if not rows:
                    fail('Native CSV member has no records: ' + info.filename)
                for index, row in enumerate(rows, 1):
                    if len(row) != len(fields):
                        fail(f'{info.filename} row {index}: field count does not match template.')
                    if tuple(row) in (fields, SHEETS[sheet][2]):
                        fail('Native CSV member must be headerless: ' + info.filename)
                    request[kinds[sheet.split('_')[-2]]].append(dict(zip(fields, row)))
            # Apply the same batch, selectors, mode and length checks as raw input.
            validated, request = prepare_members(json.dumps(request).encode('utf-8'),
                                                  template_content, controls)
            if names != [member.name for member in validated]:
                fail('Native archive members do not follow the current template order.')
            # Return captured original members, preserving quoting and line endings.
            return tuple(Member(info.filename, content=archive.read(info)) for info in infos), request
    except (zipfile.BadZipFile, UnicodeDecodeError, csv.Error, RuntimeError, OSError):
        fail('Native archive is malformed or has invalid CSV encoding.')


def write_source_archive(destination, members, request, template_content, controls):
    """Publish one validated transient source ZIP; this never authorizes a load."""
    validate_execution_mode(request)
    destination = destination.expanduser()
    if not destination.is_absolute() or destination.suffix.lower() != '.zip':
        fail('Select an absolute transient output path ending in .zip.')
    parent = destination.parent.resolve(strict=True)
    if REPO is None:
        fail('Cannot identify the FSCR workspace for safe source publication.')
    if parent == REPO or REPO in parent.parents:
        fail('Source ZIP must be outside the repository and project workspaces.')
    destination = parent / destination.name
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for member in members:
            archive.writestr(member.name, member.content)
    content = buf.getvalue()
    validate_native_archive(content, template_content, controls,
                            batch_id=request['batch_id'], import_mode=request['import_mode'])
    # Exclusive owner-only creation prevents overwrites and final-path symlinks.
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, 'wb') as output:
            output.write(content)
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--control-file', type=Path, action='append', required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--dry-run', action='store_true', help='Validate locally; no auth, ZIP creation or files.')
    action.add_argument('--output-zip', type=Path, help='Create a validated transient source ZIP for the separate Core loader.')
    action.add_argument('--handoff-check', action='store_true', help='Validate a supplied native ZIP and supported live mode without changing it.')
    parser.add_argument('--native-zip', type=Path, help='Validate and retain an existing template-exported ZIP unchanged.')
    options = parser.parse_args(argv)
    if options.handoff_check and not options.native_zip:
        parser.error('--handoff-check requires --native-zip')
    if options.output_zip and options.native_zip:
        parser.error('A native ZIP is preserved in place; use --handoff-check, not --output-zip')
    try:
        content = sys.stdin.buffer.readline(MAX_INPUT + 1)
        if len(content) > MAX_INPUT or not content.endswith(b'\n'):
            fail('Mapped input must be one bounded JSON line followed by a newline.')
        template = capture_schema(options.template, '.xlsm')
        controls = {}
        for path in options.control_file:
            matches = [sheet for sheet, (stem, _, _) in SHEETS.items() if path.name == stem + '.ctl']
            if len(matches) != 1 or matches[0] in controls:
                fail('Control files must have unique prescribed filenames.')
            controls[matches[0]] = capture_schema(path, '.ctl')
        native = None
        if options.native_zip:
            intent = json.loads(content)
            if not isinstance(intent, dict) or 'batch_id' not in intent or set(intent) - {'batch_id', 'mode', 'import_mode'}:
                fail('Native ZIP input requires batch_id and optional mode/import_mode; source rows come from the captured ZIP.')
            source_mode, import_mode = resolve_import_mode(intent)
            native = options.native_zip.absolute()
            if native.suffix.lower() != '.zip' or not native.is_file():
                fail('Native archive source must be a ZIP.')
            if native.stat().st_size > 128 * 1024 * 1024:
                fail('Native archive exceeds the supported size.')
            native_content = native.read_bytes()
            if len(native_content) > 128 * 1024 * 1024:
                fail('Native archive exceeds the supported size.')
            members, request = validate_native_archive(native_content, template, controls,
                batch_id=intent['batch_id'], mode=source_mode, import_mode=import_mode)
        else:
            members, request = prepare_members(content, template, controls)
        if options.dry_run:
            print(json.dumps({'status': 'validated', 'member_count': len(members), 'zip_created': False}))
            return 0
        validate_execution_mode(request)
        if options.output_zip:
            output = write_source_archive(options.output_zip, members, request, template, controls)
            print(json.dumps({'status': 'ready', 'source_zip': str(output), 'zip_created': True}))
        else:
            print(json.dumps({'status': 'ready', 'source_zip': str(native), 'zip_created': False}))
        return 0
    except (OSError, ValueError, MemoryError) as exc:
        # Domain errors contain field names, not customer values; never echo inputs.
        print(str(exc) if isinstance(exc, PreparationError) else 'Unable to read or validate preparation sources.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
