#!/usr/bin/env python3
"""Local ASL boolean preparation and captured-record verification; no I/O services."""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys

FIELDS = ('AllowPurchasingApprovalFlag', 'AllowSourcingFlag', 'AslDefaultFlag')
TRUE_TEXT = frozenset(('true', 'yes', 'y', '1'))
FALSE_TEXT = frozenset(('false', 'no', 'n', '0'))


def normalize_record(record):
    """Return independent raw/typed views, all boolean issues, and conversion evidence.

    Checks IDs and null encoding as well as flags; not complete ASL validation.
    Unknown fields and unrelated values are
    preserved for the task's subsequent required/field/design checks.
    """
    raw = copy.deepcopy(record)
    typed = copy.deepcopy(record)
    changes, issues = [], []
    if not isinstance(record, dict):
        return dict(raw_record=raw, record=typed, changes=changes, issues=[
            dict(field='record_shape', code='object_required')])
    if 'StatusId' in record:
        value = record['StatusId']
        valid = type(value) is int or (isinstance(value, str) and
                 re.fullmatch(r'-?[0-9]+', value, flags=re.ASCII) is not None)
        # Bound text length after stripping leading zeros before int conversion.
        digits = str(value).lstrip('-').lstrip('0') if valid else ''
        valid = valid and len(digits) <= 19
        if valid:
            key = int(('-' if str(value).startswith('-') else '') + (digits or '0'))
            valid = -(2**63) <= key <= 2**63 - 1
        if not valid:
            issues.append(dict(field='StatusId', code='int64_identifier_required'))
    for field, value in record.items():
        if value is None:
            issues.append(dict(field=field, code='unsupported_null_encoding'))
    for field in FIELDS:
        if field not in record:
            continue
        value = record[field]
        if type(value) is bool or (value is None and field != 'AslDefaultFlag'):
            continue
        if isinstance(value, str):
            token = value.strip().casefold()
            if token in TRUE_TEXT or token in FALSE_TEXT:
                converted = token in TRUE_TEXT
                typed[field] = converted
                changes.append(dict(field=field, path='/' + field, before=value, after=converted,
                                    reason='asl_boolean_text_normalization'))
                continue
        issues.append(dict(field=field, code='boolean_required' if field == 'AslDefaultFlag'
                           else 'nullable_boolean_required'))
    return dict(raw_record=raw, record=typed, changes=changes, issues=issues)


def prepare_loader_record(record):
    """Prepare canonical flag text BEFORE archive preparation; never rewrite a prepared artifact.

    Explicit null remains in the evidence but blocks source creation. A CSV blank
    is an empty string, never a null marker. IDs retain their representation.
    """
    result = normalize_record(record)
    wire = copy.deepcopy(result['record'])
    if isinstance(wire, dict):
        for field in FIELDS:
            if field in wire and type(wire[field]) is bool:
                wire[field] = 'true' if wire[field] else 'false'
    result['loader_record'] = wire
    return result


def verify_captured_record(record):
    """Type a canonical record derived from the prepared artifact without changing it.

    A noncanonical spelling requires preparation and fresh archive validation even if it
    could normalize successfully; validation must describe the submitted values.
    """
    result = normalize_record(record)
    if isinstance(record, dict):
        for field in FIELDS:
            if field not in record or not isinstance(record[field], str):
                continue
            if type(result['record'][field]) is bool and record[field] not in ('true', 'false'):
                result['issues'].append(dict(field=field, code='noncanonical_artifact_revalidate'))
    return result


def validate_delete_records(records, rest_actions, *, intent):
    """Local ID-only delete gate; controls/context are separate from business data.

    The caller passes untouched captured business records and their exact controls.
    No ID resolution, operation inference, source editing or execution occurs.
    """
    issues = []
    if intent != 'delete':
        issues.append(dict(field='intent', code='explicit_delete_required'))
    if not records or len(records) != len(rest_actions):
        issues.append(dict(field='records', code='delete_control_count_mismatch'))
    for index, record in enumerate(records):
        action = rest_actions[index] if index < len(rest_actions) else None
        if action != 'DELETE':
            issues.append(dict(row_index=index + 1, field='RestAction', code='exact_delete_required'))
        if not isinstance(record, dict):
            issues.append(dict(row_index=index + 1, field='record', code='object_required'))
            continue
        if 'StatusId' not in record:
            issues.append(dict(row_index=index + 1, field='StatusId', code='delete_id_required'))
        for field in record:
            if field != 'StatusId':
                issues.append(dict(row_index=index + 1, field=field, code='delete_id_only'))
        if 'StatusId' in record:
            for issue in normalize_record({'StatusId': record['StatusId']})['issues']:
                issues.append(dict(row_index=index + 1, **issue))
    return dict(records=copy.deepcopy(records), rest_actions=copy.deepcopy(rest_actions),
                issues=issues, status='failed' if issues else 'passed',
                complete_asl_validation=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('normalize', 'prepare', 'captured'), default='normalize')
    parser.add_argument('--dry-run', action='store_true', help='Local preview only (all modes are local and read-only).')
    args = parser.parse_args()
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, list):
            raise ValueError('Supply a JSON array of business records on stdin.')
        operation = {'normalize': normalize_record, 'prepare': prepare_loader_record,
                     'captured': verify_captured_record}[args.mode]
        rows = [dict(row_index=i, **operation(record)) for i, record in enumerate(payload, 1)]
        failed = any(row['issues'] for row in rows)
        json.dump(dict(status='failed' if failed else 'passed', mode=args.mode,
                       rows=rows, complete_asl_validation=False), sys.stdout, indent=2, allow_nan=False)
        print()
        return int(failed)
    except (ValueError, TypeError) as exc:
        print(json.dumps(dict(status='failed', failure_class='input_validation', message=str(exc))), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
