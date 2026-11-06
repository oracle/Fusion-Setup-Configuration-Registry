#!/usr/bin/env python3
"""Inspect a complete All/All charge group in an exact-task exported snapshot.

This is an offline evidence check, not an importer or a readiness override.
It compares a whole child collection and does not invent a persisted line key.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re

from fsm_task_adapter import (
    AdapterError, _default_contract_path, _load_contract, _read_package,
    _validate_parent_assembly, assess_business_intake,
    _bind_readback,
)


def _cell(entity, field, value):
    """Exact typed comparison; blanks are distinct from numeric zero."""
    if not isinstance(value, str):
        raise AdapterError(f"Expected a CSV string for {field}.")
    kind = entity['types'].get(field, '').lower()
    if value == '':
        return ('blank', '')
    if kind == 'date':
        if not re.fullmatch(r'\d{4}([-\/])\d{2}\1\d{2}', value):
            raise AdapterError(f"Invalid calendar-date representation in {field}.")
        try:
            return ('date', date.fromisoformat(value.replace('/', '-')).isoformat())
        except ValueError as exc:
            raise AdapterError(f"Invalid calendar date in {field}.") from exc
    if kind == 'decimal':
        if not re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', value):
            raise AdapterError(f"Invalid decimal representation in {field}.")
        try:
            number = Decimal(value)
        except InvalidOperation as exc:
            raise AdapterError(f"Invalid decimal in {field}.") from exc
        if not number.is_finite():
            raise AdapterError(f"Nonfinite decimal in {field}.")
        return ('decimal', number)  # Decimal equality is exact; no rounding.
    return ('string', value)  # No trimming, case folding, or alias guessing.


def _row(entity, row):
    if set(row) != set(entity['headers']):
        raise AdapterError(f"Incomplete exported row for {entity['name']}.")
    return tuple(_cell(entity, field, row[field]) for field in entity['headers'])


def _expected(contract, intake):
    checked = assess_business_intake(contract, intake)
    if checked['csv_assembly_review'] is None:
        raise AdapterError('Group inspection requires All legal entities, All banks and All branches.')
    if len(intake['draft_charge_lines']) != 1:
        raise AdapterError('This business check currently supports one complete open-ended charge range.')
    expected = checked['csv_assembly_review']['rows']
    header, _ = contract['package']['entities']
    target = expected[header['name']][0]
    for field in header['headers'][:18]:
        if any(x in field for x in ('BankName', 'BankNumber', 'BankCountry', 'BranchName', 'BranchNumber')) or field == 'LegalEntityIdentifier':
            if target[field] != '':
                raise AdapterError('All-scope inspection requires blank specific reference context.')
    return checked, expected


def inspect_group(contract, intake, package):
    checked, expected = _expected(contract, intake)
    environment = intake.get('environment', {}).get('name')
    if not environment or package.metadata['ProcessEnv'] != environment:
        raise AdapterError('Export environment does not match the explicit business intake.')
    header, line = contract['package']['entities']
    links = _validate_parent_assembly(contract, package.rows)['links']
    # This broad selector locates candidate groups. It is not a general key.
    scope = ['LegalEntityName', 'CurrencyCode', 'SettlementPriorityDisplay',
             'TransferringBankOption', 'TransferringBranchOption',
             'ReceivingBankOption', 'ReceivingBranchOption']
    wanted = expected[header['name']][0]
    matches = [i for i, row in enumerate(package.rows[header['name']])
               if all(row[field] == wanted[field] for field in scope)]
    status = 'ABSENT' if not matches else 'AMBIGUOUS' if len(matches) != 1 else 'DIFFERENT'
    header_equal = False
    children_equal = False
    actual_children = []
    if len(matches) == 1:
        index = matches[0]
        actual = package.rows[header['name']][index]
        actual_children = [package.rows[line['name']][x['line_index']] for x in links if x['header_index'] == index]
        header_equal = _row(header, actual) == _row(header, wanted)
        children_equal = Counter(_row(line, row) for row in actual_children) == Counter(_row(line, row) for row in expected[line['name']])
        if header_equal and children_equal:
            status = 'EXACT'
    return {
        'status': status, 'task': intake['task'], 'environment': environment,
        'snapshot_sha256': package.archive_sha256,
        'snapshot_process_status': package.metadata['ProcessStatus'],
        'snapshot_release': package.metadata['ProcessRelease'],
        'header_match_count': len(matches), 'child_count': len(actual_children),
        'all_header_values_equal': header_equal, 'complete_child_collection_equal': children_equal,
        'row_counts': {e['name']: len(package.rows[e['name']]) for e in (header, line)},
        'local_input_checks_passed': checked['local_checks_passed'],
        'comparison': 'Full header and multiset of full child rows, using declared date/decimal types; no line key inferred.',
        'freshness': 'Caller must bind this file to a fresh authorized export result; a local path alone does not prove freshness.',
        'persistenceVerified': False, 'comparisonOnly': True,
        'execution_ready': False, 'candidate_generated': False, 'fusion_calls': 0,
    }


def compare_after(contract, intake, before, after, *, candidate_path=None,
                  readback_evidence_path=None, import_request_id=None, target_url=None):
    before_result = inspect_group(contract, intake, before)
    after_result = inspect_group(contract, intake, after)
    if before_result['status'] != 'ABSENT':
        raise AdapterError('Create comparison requires an absent target in the before snapshot.')
    if before.metadata['ProcessRelease'] != after.metadata['ProcessRelease']:
        raise AdapterError('Snapshot releases differ; re-establish a comparable baseline.')
    preservation = {}
    for entity in contract['package']['entities']:
        old = Counter(_row(entity, row) for row in before.rows[entity['name']])
        new = Counter(_row(entity, row) for row in after.rows[entity['name']])
        preservation[entity['name']] = not bool(old - new)
    passed = after_result['status'] == 'EXACT' and all(preservation.values())
    comparison = {
        'status': 'PASS' if passed else 'FAIL', 'before_sha256': before.archive_sha256,
        'after_sha256': after.archive_sha256, 'target': after_result,
        'baseline_rows_preserved': preservation,
        'concurrent_unrelated_additions': 'Allowed; removed or changed baseline rows fail.',
        'boundary': 'Snapshot comparison only. Does not prove which process caused a row, authorize an import, or establish update/retry identity.',
        'execution_ready': False, 'fusion_calls': 0,
    }
    candidate_error = None
    if candidate_path is not None and readback_evidence_path is not None:
        try:
            candidate = _read_package(Path(candidate_path), contract)
            if (candidate.metadata['ProcessRelease'] != before.metadata['ProcessRelease'] or
                    inspect_group(contract, intake, candidate)['status'] != 'EXACT'):
                raise AdapterError('Candidate release or requested charge group differs.')
        except (AdapterError, OSError, ValueError) as exc:
            candidate_error = f"Submitted candidate does not match this create: {exc}"
    return _bind_readback(
        comparison, contract, before, after, candidate_path,
        readback_evidence_path, import_request_id, target_url, candidate_error,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--intake', type=Path, required=True)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--before', type=Path)
    parser.add_argument('--candidate', type=Path)
    parser.add_argument('--readback-evidence', type=Path)
    parser.add_argument('--import-request-id')
    parser.add_argument('--target-url')
    args = parser.parse_args()
    try:
        if (args.candidate or args.readback_evidence or args.import_request_id or args.target_url) and not args.before:
            raise AdapterError('Read-back evidence options require before and snapshot.')
        contract = _load_contract(_default_contract_path())
        intake = json.loads(args.intake.read_text())
        current = _read_package(args.snapshot, contract)
        result = compare_after(
            contract, intake, _read_package(args.before, contract), current,
            candidate_path=args.candidate, readback_evidence_path=args.readback_evidence,
            import_request_id=args.import_request_id, target_url=args.target_url,
        ) if args.before else inspect_group(contract, intake, current)
    except (AdapterError, ValueError, OSError) as exc:
        print(json.dumps({'status': 'REJECTED', 'message': str(exc), 'execution_ready': False, 'fusion_calls': 0}))
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result['status'] in {'ABSENT', 'EXACT', 'PASS'} else 1


if __name__ == '__main__':
    raise SystemExit(main())
