#!/usr/bin/env python3
"""Offline source preparation for one charge group and contiguous amount ranges.

Produces source bytes only: Data Loader, Task Hook, fresh-state assessment and
candidate-bound approval remain mandatory. Never calls Fusion or creates IDs.
"""
from __future__ import annotations

import argparse
import copy
from collections import Counter
from decimal import Decimal
import json
from pathlib import Path
import re
import zipfile
from xml.etree import ElementTree

from fsm_task_adapter import (
    AdapterError, _default_contract_path, _load_contract, _read_package,
    _validate_parent_assembly, _write_candidate, assess_business_intake, _metadata_object_contracts,
    _bind_readback, _validate_new_outputs,
)
from inspect_bank_charge_group import _row


def read_group_package(path, contract):
    """Bind each source package's node sequences without changing its metadata.

    Validate hierarchy by node paths and CSV parent context, not an earlier
    export's sequence values. The shared reader checks archive and field shape.
    """
    try:
        with zipfile.ZipFile(path) as archive:
            info = archive.getinfo(contract['package']['metadataMember'])
            if info.file_size > 2_000_000:
                raise AdapterError('Metadata exceeds the charge-group size limit.')
            objects = _metadata_object_contracts(ElementTree.fromstring(archive.read(info)))
        bound = copy.deepcopy(contract)
        sequences = set()
        for entity in bound['package']['entities']:
            item = objects.get(entity['name'])
            if item is None or item['nodePath'] != entity['nodePath']:
                raise AdapterError('Source metadata has a missing or changed charge-group hierarchy path.')
            sequence = str(item['nodeSequence']).strip()
            if not re.fullmatch(r'[1-9][0-9]*', sequence) or sequence in sequences:
                raise AdapterError('Source metadata sequences must be unique positive integers.')
            sequences.add(sequence)
            entity['nodeSequence'] = sequence
        return _read_package(path, bound)
    except (OSError, KeyError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        raise AdapterError(f'Invalid charge-group source metadata: {exc}') from exc


def assemble(contract, intake):
    checked = assess_business_intake(contract, intake)
    header, child = contract['package']['entities']
    fields = checked['normalized_header']
    identifier = fields.get('LegalEntityIdentifier')
    if fields['LegalEntityName'] == 'All':
        if identifier is not None and (not isinstance(identifier, str) or identifier.strip()):
            raise AdapterError('All legal entities requires a blank LegalEntityIdentifier.')
        fields['LegalEntityIdentifier'] = ''
        scope_check = 'all_entity_blank_identifier'
    else:
        if not isinstance(identifier, str) or not identifier.strip():
            raise AdapterError('LegalEntityIdentifier is required for a named legal entity; the importer does not resolve a name-only key.')
        scope_check = 'named_entity_identifier'
    policy = intake.get('reference_verification_policy')
    deferred = checked['reference_validation_warnings']
    verified = checked['reference_validation_verified']
    if (not verified and not deferred and
            (not isinstance(policy, dict) or policy.get('mode') != 'user_supplied_no_environment_lookup')):
        raise AdapterError('Supply verified evidence for every applicable reference, recorded unavailable checks, or the explicit user-supplied reference policy.')
    lines = intake['draft_charge_lines']
    periods = {(line['StartDate'], line.get('EndDate') or '') for line in lines}
    if len(periods) != 1:
        raise AdapterError('This route requires the same effective period on all ranges.')
    ordered = sorted(lines, key=lambda line: Decimal(str(line['TransAmountFrom'])))
    if Decimal(str(ordered[0]['TransAmountFrom'])) != 0:
        raise AdapterError('The first range must start at zero.')
    for index, line in enumerate(ordered):
        start = Decimal(str(line['TransAmountFrom']))
        end = line.get('TransAmountTo')
        if index == len(ordered) - 1:
            if end not in (None, ''):
                raise AdapterError('The final range must have an open upper amount.')
        else:
            if end in (None, ''):
                raise AdapterError('Only the final range may have an open upper amount.')
            if Decimal(str(end)) <= start:
                raise AdapterError('Each finite range must have positive width.')
            if Decimal(str(end)) != Decimal(str(ordered[index + 1]['TransAmountFrom'])):
                raise AdapterError('Adjacent ranges must share exactly the same boundary; gaps and overlaps are rejected.')
    parent = {field: '' if fields.get(field) is None else str(fields[field]) for field in header['headers']}
    prefix = header['name'] + '.'
    children = []
    for values in ordered:
        children.append({field: parent[field[len(prefix):]] if field.startswith(prefix)
                         else '' if values.get(field) is None else str(values[field])
                         for field in child['headers']})
    rows = {header['name']: [parent], child['name']: children}
    for entity in (header, child):
        for row in rows[entity['name']]:
            _row(entity, row)
    assembly = _validate_parent_assembly(contract, rows)
    return rows, {
        'status': 'LOCAL_SOURCE_CHECKS_PASS',
        'checks': checked['local_checks_passed'] + [scope_check, 'same_effective_period',
                  'zero_start', 'positive_finite_ranges', 'contiguous_ranges', 'open_final_range', 'csv_parent_assembly'],
        'parent_links': assembly['links'],
        'reference_validation': ('VERIFIED; recorded checks match this environment and supplied references'
                                 if verified else 'UNVERIFIED_API_UNAVAILABLE; supplied values preserved, no identifiers inferred'
                                 if deferred else 'waived_by_user; supplied values preserved, no identifiers inferred'),
        'reference_validation_warnings': deferred,
        'reference_validation_evidence': checked['reference_validation_evidence'],
        'threshold_boundary': 'Source-backed range validation requires equal adjacent endpoints; this is not proof of payment-time rate selection at the boundary.',
        'fusion_calls': 0, 'execution_ready': False,
    }


def inspect_charge_group(contract, intake, package):
    expected, checks = assemble(contract, intake)
    if package.metadata['ProcessEnv'] != intake['environment']['name']:
        raise AdapterError('Snapshot environment differs from the requested environment.')
    header, child = contract['package']['entities']
    links = _validate_parent_assembly(contract, package.rows)['links']
    wanted = expected[header['name']][0]
    # Discovery selector, not a persisted update key. Ignore optional enrichment
    # to avoid misreporting a populated country/number as a missing target.
    selector = ['LegalEntityName', 'LegalEntityIdentifier', 'CurrencyCode', 'SettlementPriorityDisplay',
                'TransferringBankOption', 'TransferringBankName', 'TransferringBranchOption', 'TransferringBranchName',
                'ReceivingBankOption', 'ReceivingBankName', 'ReceivingBranchOption', 'ReceivingBranchName']
    def match(row):
        # Broad case-insensitive comparison fails closed on possible duplicates;
        # exact supplied-value equality is still required for an EXACT result.
        return all(row[field].casefold() == wanted[field].casefold() for field in selector)
    matches = [i for i, row in enumerate(package.rows[header['name']]) if match(row)]
    status = 'ABSENT' if not matches else 'AMBIGUOUS' if len(matches) > 1 else 'DIFFERENT'
    if len(matches) == 1:
        actual = package.rows[header['name']][matches[0]]
        supplied = set(intake['draft_field_mapping'])
        # Unspecified bank reference metadata may be populated by Fusion.
        enriched = {field for field in header['headers'] if field not in supplied and
                    ('BankCountry' in field or 'BankNumber' in field or 'BranchNumber' in field)}
        normalized = dict(actual)
        for field in enriched:
            normalized[field] = ''
        prefix = header['name'] + '.'
        child_rows = []
        for link in links:
            if link['header_index'] == matches[0]:
                row = dict(package.rows[child['name']][link['line_index']])
                for field in enriched:
                    row[prefix + field] = ''
                child_rows.append(row)
        if (_row(header, normalized) == _row(header, wanted) and
            Counter(_row(child, row) for row in child_rows) == Counter(_row(child, row) for row in expected[child['name']])):
            status = 'EXACT'
    return {'status': status, 'header_match_count': len(matches), 'local_checks': checks,
            'persistenceVerified': False, 'comparisonOnly': True,
            'boundary': 'Complete group comparison, with unspecified reference enrichment ignored; no update key or execution authority.'}


def compare_charge_group_after(contract, intake, before, after, *, candidate_path=None,
                               readback_evidence_path=None, import_request_id=None, target_url=None):
    if inspect_charge_group(contract, intake, before)['status'] != 'ABSENT':
        raise AdapterError('Create reconciliation requires an absent target in the before snapshot.')
    if before.metadata['ProcessRelease'] != after.metadata['ProcessRelease']:
        raise AdapterError('Snapshot releases differ.')
    result = inspect_charge_group(contract, intake, after)
    preserved = {entity['name']: not bool(Counter(_row(entity, row) for row in before.rows[entity['name']]) -
                                         Counter(_row(entity, row) for row in after.rows[entity['name']]))
                 for entity in contract['package']['entities']}
    comparison = {'status': 'PASS' if result['status'] == 'EXACT' and all(preserved.values()) else 'FAIL',
                  'target': result, 'baseline_rows_preserved': preserved, 'fusion_calls': 0}
    candidate_error = None
    if candidate_path is not None and readback_evidence_path is not None:
        try:
            candidate = read_group_package(Path(candidate_path), contract)
            if (candidate.metadata['ProcessRelease'] != before.metadata['ProcessRelease'] or
                    inspect_charge_group(contract, intake, candidate)['status'] != 'EXACT'):
                raise AdapterError('Candidate release or requested charge group differs.')
        except (AdapterError, OSError, ValueError) as exc:
            candidate_error = f"Submitted candidate does not match this create: {exc}"
    return _bind_readback(
        comparison, contract, before, after, candidate_path,
        readback_evidence_path, import_request_id, target_url, candidate_error,
    )


def prepare(contract, intake, template, output):
    rows, checks = assemble(contract, intake)
    _validate_new_outputs([output], [template.path])
    if template.metadata['ProcessEnv'] != intake['environment']['name']:
        raise AdapterError('Source package environment differs from the requested environment.')
    if output.exists():
        raise AdapterError('Refusing to overwrite an existing source archive.')
    _write_candidate(template, template, contract, rows, output)
    generated = read_group_package(output, contract)
    if generated.rows != rows:
        raise AdapterError('Source archive round-trip differs from the intended rows.')
    if generated.member_bytes[contract['package']['metadataMember']] != template.member_bytes[contract['package']['metadataMember']]:
        raise AdapterError('Source-owned metadata changed.')
    return {**checks, 'status': 'SOURCE_PREPARED_NOT_APPROVED', 'source_path': str(output),
            'sha256': generated.archive_sha256, 'row_counts': {name: len(values) for name, values in rows.items()},
            'requires': ['current-state absence assessment', 'Data Loader and Task Hook validation', 'exact artifact import approval']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--intake', type=Path, required=True)
    parser.add_argument('--template', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--snapshot', type=Path)
    parser.add_argument('--before', type=Path)
    parser.add_argument('--candidate', type=Path)
    parser.add_argument('--readback-evidence', type=Path)
    parser.add_argument('--import-request-id')
    parser.add_argument('--target-url')
    args = parser.parse_args()
    try:
        if args.output:
            _validate_new_outputs([args.output], [_default_contract_path()] + [
                value for name, value in vars(args).items()
                if name != 'output' and isinstance(value, Path)
            ])
        if (args.candidate or args.readback_evidence or args.import_request_id or args.target_url) and not (args.snapshot and args.before):
            raise AdapterError('Read-back evidence options require snapshot and before.')
        contract = _load_contract(_default_contract_path())
        intake = json.loads(args.intake.read_text())
        if args.snapshot:
            current = read_group_package(args.snapshot, contract)
            result = compare_charge_group_after(
                contract, intake, read_group_package(args.before, contract), current,
                candidate_path=args.candidate, readback_evidence_path=args.readback_evidence,
                import_request_id=args.import_request_id, target_url=args.target_url,
            ) if args.before else inspect_charge_group(contract, intake, current)
        elif args.template and args.output:
            result = prepare(contract, intake, read_group_package(args.template, contract), args.output)
        elif args.template or args.output or args.before:
            raise AdapterError('Supply template and output together, or snapshot with optional before.')
        else:
            result = assemble(contract, intake)[1]
    except (AdapterError, ValueError, KeyError, OSError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'message': str(exc), 'fusion_calls': 0}))
        return 1
    print(json.dumps(result, indent=2))
    return int(result['status'] in {'FAIL', 'DIFFERENT', 'AMBIGUOUS', 'PENDING', 'BLOCKED'})


if __name__ == '__main__':
    raise SystemExit(main())
