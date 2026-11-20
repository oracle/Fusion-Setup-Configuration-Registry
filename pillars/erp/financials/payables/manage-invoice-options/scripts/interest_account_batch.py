"""Review every Invoice Options record and apply an explicit batch disposition.

Review makes read-only calls; select is offline. Creation uses the existing
exact-request creation command; import remains owned by Data Loader.
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import sys

import fsm_task_adapter as adapter
import resolve_lookup_prerequisites as resolver
from interest_account_fsm_fallback import digest, RESOLVER
import interest_account_override as account_override


def review_batch(design, config, baseline):
    operations = design.get('operations')
    if not isinstance(operations, list) or not operations:
        raise ValueError('A nonempty operations array is required.')
    if not config.get('coaConfiguration'):
        raise ValueError('Batch account review requires a fresh COA configuration export.')
    ids = [op.get('id') for op in operations if isinstance(op, dict)]
    if len(ids) != len(operations) or any(not isinstance(x, str) or not x.strip() for x in ids) or len(set(ids)) != len(ids):
        raise ValueError('Every record must have a unique nonblank operation ID.')
    records = []
    merged = copy.deepcopy(design)
    merged['operations'] = []
    merged['prerequisites'] = []
    for op in operations:
        single = copy.deepcopy(design)
        single['operations'] = [copy.deepcopy(op)]
        try:
            resolved, _ = resolver.resolve_lookup_prerequisites(single, config, baseline)
            deferred = [r for r in resolved.get('prerequisites', []) if r.get('operationId') == op['id'] and r.get('resolver') == RESOLVER]
            context = adapter._interest_account_context(resolved, {'name': 'AP_SYSTEM_PARAMETER', 'keyFields': ['BuName']}, resolved['operations'][0], baseline)
            overridden = [r for r in resolved.get('prerequisites', []) if r.get('operationId') == op['id'] and r.get('resolver') == account_override.RESOLVER]
            records.append({'operationId': op['id'], 'targetKey': op.get('targetKey'),
                            'status': 'overridden' if overridden else 'fsm_pending' if deferred else 'ready',
                            'account': context[0] if context else None,
                            'ledger': context[1] if context else None,
                            'accountState': 'validation_overridden' if overridden else 'pending_creation' if deferred else 'existing_usable' if context else 'not_applicable'})
            merged['operations'] += resolved['operations']
            merged['prerequisites'] += [r for r in resolved.get('prerequisites', []) if r.get('operationId') in (None, op['id'])]
            merged['referenceContext'] = resolved.get('referenceContext')
            for warning in resolved.get('warnings', []):
                if warning not in merged.setdefault('warnings', []):
                    merged['warnings'].append(warning)
            for key, value in resolved.get('resolvedScope', {}).items():
                if isinstance(value, list):
                    merged.setdefault('resolvedScope', {}).setdefault(key, []).extend(
                        item for item in value if item not in merged.get('resolvedScope', {}).get(key, []))
        except resolver.AccountValidationError as exc:
            resolution = exc.account_resolution or {}
            context = adapter._interest_account_context(single, {'name': 'AP_SYSTEM_PARAMETER', 'keyFields': ['BuName']}, single['operations'][0], baseline)
            record = {'operationId': op['id'], 'targetKey': op.get('targetKey'),
                'status': 'creation_approval_required' if resolution.get('creationAllowed') is True else 'blocked',
                'message': resolution.get('message') or str(exc), 'accountResolution': resolution,
                'accountValidation': exc.account_validation,
                'accountValidationResult': exc.account_validation_result,
                'candidateDesign': copy.deepcopy(single),
                'account': context[0] if context else None, 'ledger': context[1] if context else None,
                'provenance': resolver._new_reference_provenance(single.get('referenceContext'), baseline)}
            # A completed approved creation rejection can be explicitly waived too.
            for rejected in config.get('creationRejections', []):
                if context and account_override.creation_rejection_matches(rejected, operation=op,
                        account=context[0], ledger=context[1], baseline_sha256=baseline.archive_sha256,
                        base_url=record['provenance']['baseUrl']):
                    failure = rejected['creationReceipt']['validationFailure']
                    record.update(status='blocked', accountValidationResult=rejected['creationReceipt'],
                        accountValidation=failure, message=failure.get('message') or 'Account creation was rejected.',
                        accountResolution={**resolution, 'classification': 'creation_rejected', 'creationAllowed': False})
            record['overrideEligible'] = account_override.eligible_record(record)
            if record['overrideEligible']:
                record['choices'] = ['correct', 'override', 'exclude', 'stop']
            records.append(record)
        except (ValueError, RuntimeError, resolver.LookupPreflightError, resolver.metadata.DataLoadError, OSError) as exc:
            records.append({'operationId': op['id'], 'targetKey': op.get('targetKey'),
                            'status': 'blocked', 'message': str(exc)})
    counts = {name: sum(r['status'] == name for r in records)
              for name in ('ready', 'fsm_pending', 'overridden', 'creation_approval_required', 'blocked')}
    return {'schemaVersion': 'invoice-account-batch-review-v1', 'designSha256': digest(design),
            'baselineSha256': baseline.archive_sha256, 'records': records, 'counts': counts,
            'resolvedDesign': merged,
            'choices': ['correct', *(['override'] if any(r.get('overrideEligible') for r in records) else []), 'exclude', 'stop'],
            'message': f"{counts['ready']} records ready; {counts['fsm_pending']} require account creation during import; "
                       f"{counts['creation_approval_required']} require creation approval; {counts['blocked']} blocked; {counts['overridden']} explicitly overridden. "
                       'Review all records before deciding. No records have been silently excluded.'}


def select_records(review, decision=None):
    if (not isinstance(review, dict) or review.get('schemaVersion') != 'invoice-account-batch-review-v1'
            or not isinstance(review.get('records'), list) or not isinstance(review.get('resolvedDesign'), dict)
            or any(not isinstance(row, dict) or not isinstance(row.get('operationId'), str)
                   or row.get('status') not in ('ready', 'fsm_pending', 'overridden', 'blocked', 'creation_approval_required')
                   for row in review.get('records', []))):
        raise ValueError('A complete current batch review is required.')
    blocked_ids = {r['operationId'] for r in review['records'] if r['status'] not in ('ready', 'fsm_pending', 'overridden')}
    if not blocked_ids and decision is None:
        choices = {}
    else:
        if (not isinstance(decision, dict)
                or decision.get('schemaVersion') != 'invoice-account-batch-decision-v1'
                or decision.get('approved') is not True or not decision.get('approvalId')):
            raise ValueError('A current explicit decision bound to the complete review is required.')
        source_review = decision.get('sourceReview')
        if decision.get('reviewSha256') != digest(review):
            # Creation outcomes can evolve without changing the user's requested
            # records. Preserve exact prior exclusions, not a generic consent.
            if (not isinstance(source_review, dict)
                    or decision.get('reviewSha256') != digest(source_review)
                    or source_review.get('schemaVersion') != review['schemaVersion']
                    or not review.get('designSha256') or not review.get('baselineSha256')
                    or source_review.get('designSha256') != review['designSha256']
                    or source_review.get('baselineSha256') != review['baselineSha256']
                    or {r['operationId'] for r in source_review.get('records', [])} !=
                       {r['operationId'] for r in review['records']}):
                raise ValueError('The exclusion decision is stale for the requested records or baseline.')
        choices = decision.get('records')
        if not isinstance(choices, dict):
            raise ValueError('Record decisions are required; no implicit exclusions are allowed.')
    records = review['records']
    ids = {r['operationId'] for r in records}
    blocked = {r['operationId'] for r in records if r['status'] not in ('ready', 'fsm_pending', 'overridden')}
    allowed = set(blocked)
    if isinstance(decision, dict) and isinstance(decision.get('sourceReview'), dict):
        allowed |= {r['operationId'] for r in decision['sourceReview']['records']
                    if r.get('status') not in ('ready', 'fsm_pending', 'overridden')}
    actions = {key: value.get('action') if isinstance(value, dict) else value for key, value in choices.items()}
    if not blocked <= set(choices) <= allowed or any(x not in ('exclude', 'stop', 'correct', 'override') for x in actions.values()):
        raise ValueError('Choose correct, explicit override with reason, exclude or stop for every blocked record.')
    if any(x in ('stop', 'correct') for x in actions.values()):
        raise ValueError('Stopped. Correct the requested records and rerun the complete review before preparation.')
    selected = copy.deepcopy(review['resolvedDesign'])
    overrides = []
    for record in records:
        if actions.get(record['operationId']) != 'override':
            continue
        if decision.get('reviewSha256') != digest(review):
            raise ValueError('An override requires approval of the current failure review.')
        item = account_override.make_override(record, decision, review)
        partial = record['candidateDesign']
        ops = [op for op in partial['operations'] if op['id'] == record['operationId']]
        if len(ops) != 1:
            raise ValueError('Override record must retain its exact requested operation.')
        selected['operations'] += copy.deepcopy(ops)
        selected['prerequisites'] += [copy.deepcopy(r) for r in partial.get('prerequisites', [])
            if not (r.get('operationId') == record['operationId'] and r.get('field') == 'InterestSegments')]
        selected['prerequisites'].append(item)
        for key, values in partial.get('resolvedScope', {}).items():
            if isinstance(values, list):
                selected.setdefault('resolvedScope', {}).setdefault(key, []).extend(
                    copy.deepcopy(v) for v in values if v not in selected.get('resolvedScope', {}).get(key, []))
        for message in [*partial.get('warnings', []), account_override.warning(item)]:
            if message not in selected.setdefault('warnings', []):
                selected['warnings'].append(message)
        overrides.append({'operationId': record['operationId'], 'targetKey': record['targetKey'],
            'reason': item['approval']['reason'], 'accountValidation': record['accountValidation']})
    excluded = {key for key, action in actions.items() if action == 'exclude'}
    included = ids - excluded
    selected['operations'] = [op for op in selected['operations'] if op['id'] in included]
    if not included:
        raise ValueError('No eligible records remain; nothing will be imported.')
    if {op['id'] for op in selected['operations']} != included:
        raise ValueError('Review operations do not match the eligible records.')
    selected['prerequisites'] = [r for r in selected.get('prerequisites', []) if r.get('operationId') in (None, *included)]
    disposition = {'included': sorted(included), 'excluded': [
        {'operationId': r['operationId'], 'targetKey': r.get('targetKey'), 'reason': r.get('message')}
        for r in records if r['operationId'] in excluded], 'overridden': overrides}
    selected.setdefault('warnings', []).append('Approved batch disposition: ' + json.dumps(disposition, sort_keys=True))
    selected['batchDisposition'] = disposition
    return selected


def verified_counts(readback, validations, expected):
    """Only observed saved rows AND usable same-context accounts can count as success."""
    counts = {'savedAndValidated': 0, 'failed': 0, 'pending': 0, 'notApplicable': 0}
    for check in readback.get('checks', []):
        state = check['status']
        if state == 'NOT_APPLICABLE':
            counts['notApplicable'] += 1
        elif state == 'FAIL':
            counts['failed'] += 1
        elif state != 'PASS':
            counts['pending'] += 1
        else:
            result = validations.get(check['operationId'])
            if result is None or (isinstance(result, dict) and
                    (result.get('validationFailure') or {}).get('classification') in
                    ('soap_fault', 'http_failure', 'incomplete_response')):
                counts['pending'] += 1
            elif usable_result(result, expected.get(check['operationId'])):
                counts['savedAndValidated'] += 1
            else:
                counts['failed'] += 1
    return counts



def usable_result(result, expected):
    import re
    if not isinstance(expected, dict) or not isinstance(result, dict):
        return False
    ids = result.get('responseFields', {}).get('CcId')
    request = result.get('request') or {}
    return (result.get('valid') is True and result.get('readOnly') is True
            and result.get('dynamicInsertion') == 'No' and not result.get('soapFault')
            and type(result.get('httpStatus')) is int and 200 <= result['httpStatus'] < 300
            and result.get('responseFields', {}).get('Status') == ['Valid']
            and isinstance(ids, list) and len(ids) == 1 and isinstance(ids[0], str)
            and re.fullmatch(r'[1-9][0-9]{0,37}', ids[0]) is not None
            and request.get('baseUrl') == expected['baseUrl']
            and request.get('readOnly') is True
            and request.get('businessContext') == {'ledgerName': expected['ledger'],
                'segments': expected['segments'], 'dynamicInsertion': 'No'})


def verify_batch(args):
    from interest_account_validation import parse_segments
    contract = adapter._load_contract(resolver.TASK_ROOT/'e2e-adapter.json')
    context = resolver._read_json(args.target_context)
    readback = adapter.verify_interest_distribution(contract, args.baseline, args.candidate,
        args.blueprint, args.export, resolver._read_json(args.verification_evidence), context)
    validations = {}; expected = {}
    if any(check['status'] == 'PASS' for check in readback['checks']):
        design = resolver._read_json(args.blueprint)
        config = resolver.metadata.read_config(args.properties, **resolver.metadata.oauth_kwargs(args))
        baseline = adapter._read_package(args.baseline, contract)
        resolver._configured_reference_target(config, context, baseline)
        for check in readback['checks']:
            if check['status'] != 'PASS':
                continue
            op = next(op for op in design['operations'] if op['id'] == check['operationId'])
            account, ledger = adapter._interest_account_context(design,
                {'name': 'AP_SYSTEM_PARAMETER', 'keyFields': ['BuName']}, op, baseline)
            expected[op['id']] = {'baseUrl': config['host'], 'ledger': ledger, 'segments': parse_segments(account)}
            try:
                validations[op['id']] = resolver._run_account_validation(config, ledger, account)
            except (ValueError, RuntimeError, resolver.LookupPreflightError, resolver.metadata.DataLoadError):
                # An unavailable check is pending, never an inferred success.
                pass
    return {'schemaVersion': 'invoice-account-batch-verification-v1', 'readback': readback,
            'accountValidation': validations, 'counts': verified_counts(readback, validations, expected)}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    review = sub.add_parser('review')
    review.add_argument('--design', type=Path, required=True)
    review.add_argument('--baseline', type=Path, required=True)
    review.add_argument('--coa-configuration', type=Path, required=True)
    review.add_argument('--creation-rejection', type=Path, action='append', default=[])
    review.add_argument('--fsm-deferral', type=Path, action='append', default=[])
    review.add_argument('--output', type=Path, required=True)
    resolver.metadata.add_oauth_arguments(review)
    select = sub.add_parser('select')
    select.add_argument('--review', type=Path, required=True)
    select.add_argument('--decision', type=Path, help='Required only when records need correction, exclusion or stop.')
    select.add_argument('--output', type=Path, required=True)
    verify = sub.add_parser('verify')
    for name in ('baseline', 'candidate', 'blueprint', 'export', 'verification-evidence', 'target-context', 'output'):
        verify.add_argument('--'+name, type=Path, required=True)
    resolver.metadata.add_oauth_arguments(verify)
    args = parser.parse_args(argv)
    try:
        protected = [p for key, p in vars(args).items() if key != 'output' and isinstance(p, Path)]
        adapter._validate_new_outputs([args.output], protected + getattr(args, 'fsm_deferral', []) + getattr(args, 'creation_rejection', []))
        if args.command == 'verify':
            value = verify_batch(args)
        elif args.command == 'select':
            value = select_records(resolver._read_json(args.review), resolver._read_json(args.decision) if args.decision else None)
        else:
            config = resolver.metadata.read_config(args.properties, **resolver.metadata.oauth_kwargs(args))
            config['coaConfiguration'] = args.coa_configuration
            config['fsmDeferrals'] = [resolver._read_json(p) for p in args.fsm_deferral]
            config['creationRejections'] = [resolver._read_json(p) for p in args.creation_rejection]
            baseline = adapter._read_package(args.baseline, adapter._load_contract(resolver.TASK_ROOT/'e2e-adapter.json'))
            value = review_batch(resolver._read_json(args.design), config, baseline)
        adapter._write_new_json(args.output, value)
        status = ('REVIEW_REQUIRED' if args.command == 'review' else 'SELECTED')
        if args.command == 'verify':
            status = ('VERIFICATION_FAILED' if value['counts']['failed'] else
                      'VERIFICATION_PENDING' if value['counts']['pending'] else 'VERIFIED')
        print(json.dumps({'status': status, 'output': str(args.output),
                          'message': value.get('message'), 'counts': value.get('counts')}))
        if args.command == 'verify' and (value['counts']['failed'] or value['counts']['pending']):
            return 2
        return 0
    except (ValueError, RuntimeError, OSError, resolver.LookupPreflightError, resolver.metadata.DataLoadError) as exc:
        print(json.dumps({'status': 'FAIL', 'error': str(exc)}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
