"""Prepare a qualified Expense Fields FSM ZIP locally; never upload or approve.

Input is the normalized operation-planner JSON. Use a workflow-verified fresh
baseline ZIP and the user's selected createAuditPolicy. Customer data must stay
in the active untracked project workspace, outside reusable tracked source.
"""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

from plan_operations import HEADERS, plan

MEMBERS = {'EXM_CATEGORY_FIELD.csv', 'ASM_SETUP_CSV_METADATA.xml'}
TASK = 'EXM_MANAGE_EXPENSE_FIELDS_BY_CATEGORY'


def build_package(data, baseline_bytes):
    """Return archive bytes and sanitized counts; reject partial or empty loads."""
    with zipfile.ZipFile(io.BytesIO(baseline_bytes)) as archive:
        if len(archive.infolist()) != 2 or set(archive.namelist()) != MEMBERS:
            raise ValueError('Baseline must contain exactly the two task members')
        for item in archive.infolist():
            limit = 10 * 1024 * 1024 if item.filename.endswith('.csv') else 1024 * 1024
            if item.file_size > limit or item.flag_bits & 1:
                raise ValueError('Oversized or encrypted member')
        metadata = archive.read('ASM_SETUP_CSV_METADATA.xml')
        if b'<!DOCTYPE' in metadata.upper() or b'<!ENTITY' in metadata.upper():
            raise ValueError('Unexpected XML declaration')
        root = ET.fromstring(metadata)
        def values(name):
            return [e.text for e in root.iter() if e.tag.split('}')[-1] == name]
        required = {'ObjectShortName': TASK, 'ObjectType': 'TASK', 'ProcessStatus': 'COMPLETED',
                    'BusinessObjectShortName': 'EXM_CATEGORY_FIELD',
                    'XmlNodePath': '/CategoryFieldVO/CategoryFieldVORow'}
        for name, expected in required.items():
            found = values(name)
            if not found or any(value != expected for value in found):
                raise ValueError('Baseline metadata identity mismatch')
        reader = csv.reader(io.StringIO(archive.read('EXM_CATEGORY_FIELD.csv').decode('utf-8-sig')), strict=True)
        headers = next(reader)
        if len(headers) != 19 or set(headers) != HEADERS:
            raise ValueError('Unexpected baseline headers')
        attribute_lists, type_lists = values('XmlAttributeList'), values('XmlAttributeTypeList')
        if len(attribute_lists) != 1 or len(type_lists) != 1:
            raise ValueError('Ambiguous attribute definitions')
        attributes, types = attribute_lists[0].split(','), type_lists[0].split(',')
        if len(attributes) != 19 or set(attributes) != HEADERS or len(types) != 19:
            raise ValueError('Attribute definitions mismatch')
        if any(t != ('dateTime' if h in {'CreationDate', 'LastUpdateDate'} else 'string') for h, t in zip(attributes, types)):
            raise ValueError('Attribute type mismatch')
        rows = []
        for cells in reader:
            if len(cells) != len(headers):
                raise ValueError('Invalid CSV row width')
            rows.append(dict(zip(headers, cells)))
    if data.get('baselineRows') != rows:
        raise ValueError('Planner baseline must equal the validated ZIP rows')
    result = plan(data)
    if result['contract_status'] != 'passed' or result['execution_status'] != 'awaiting_core_preflight':
        raise ValueError('No complete runnable FSM batch; resolve issues or use the assisted split workflow')
    candidates = [op['candidateRow'] for op in result['operations'] if 'candidateRow' in op]
    if not candidates:
        raise ValueError('No changed rows; do not create an empty load')
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=headers, lineterminator='\r\n')
    writer.writeheader()
    writer.writerows(candidates)
    csv_bytes = stream.getvalue().encode('utf-8')
    if len(csv_bytes) > 10 * 1024 * 1024:
        raise ValueError('CSV exceeds package size contract')
    target = io.BytesIO()
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, content in [('EXM_CATEGORY_FIELD.csv', csv_bytes), ('ASM_SETUP_CSV_METADATA.xml', metadata)]:
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)
    return target.getvalue(), result['counts']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--baseline-zip', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if not args.dry_run and args.output is None:
        parser.error('--output is required unless --dry-run is supplied')
    try:
        payload, counts = build_package(json.loads(args.input.read_text()), args.baseline_zip.read_bytes())
        if not args.dry_run:
            if args.output.suffix.lower() != '.zip':
                raise ValueError('Output must be a ZIP')
            fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(payload)
                    os.fchmod(stream.fileno(), 0o400)
            except BaseException:
                args.output.unlink(missing_ok=True)
                raise
        print(json.dumps({'status': 'dry_run_passed' if args.dry_run else 'prepared',
                          'counts': counts, 'archiveSha256': hashlib.sha256(payload).hexdigest(),
                          'submission_allowed': False}))
        return 0
    except (OSError, ValueError, TypeError, AttributeError, KeyError, StopIteration, csv.Error, zipfile.BadZipFile, ET.ParseError):
        print(json.dumps({'status': 'blocked', 'message': 'Package preparation failed; check protected input, baseline identity/schema, operation plan and output path. No upload performed.'}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
