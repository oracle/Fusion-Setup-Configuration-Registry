"""Offline category-field operation planner; no Fusion calls or import approval.

Consumes normalized workbook requests and a complete workflow-verified baseline.
Keep customer inputs and outputs in the untracked active project workspace.
"""
import argparse
from collections import Counter
import json
import sys

AUDIT = ('CreationDate', 'CreatedBy', 'LastUpdateLogin', 'LastUpdateDate', 'LastUpdatedBy')
FIELDS = ('EndDateField', 'MerchantField', 'TicketClassField', 'TicketNumberField',
          'TicketTypeField', 'LocationToField', 'LocationFromField', 'StartingOdometerField',
          'EndingOdometerField', 'LicensePlateField', 'AgencyField', 'PassengerNameField')
HEADERS = {'CategoryCode', 'BuName', *AUDIT, *FIELDS}
CATEGORIES = {'ACCOMMODATIONS', 'AIRFARE', 'CAR_RENTAL', 'ENTERTAINMENT', 'MEALS', 'MILEAGE', 'MISC'}
# Narrow, source-reviewed writable mapping. Other aliases stay contract-gated.
REVIEWED = {'ACCOMMODATIONS': {'MerchantField', 'EndDateField'},
            'ENTERTAINMENT': {'MerchantField'}, 'MEALS': {'MerchantField'}}
LABELS = {'required': 'REQUIRED', 'optional': 'ENABLED', 'hidden': 'DISABLED'}


def plan(data):
    if not isinstance(data, dict):
        raise ValueError('Expected an object')
    # Regenerate EBS intent before workbook defaults or package construction.
    if 'ebsSource' in data or any(isinstance(r, dict) and isinstance(r.get('source'), dict)
                                 and r['source'].get('type') == 'ebs-category-csv'
                                 for r in (data.get('requests') or [])):
        from ebs_intake import validate_binding
        issues = validate_binding(data)
        if issues:
            return {'input_status': 'passed', 'contract_status': 'blocked',
                    'execution_status': 'blocked', 'failure_class': 'catalog_mismatch',
                    'issues': issues, 'operations': [], 'counts': {}, 'submission_allowed': False,
                    'next_action': 'Resolve all EBS mappings before planning; do not import a partial source batch.'}
    # These assertions must come from the routed workflow, not workbook cells.
    evidence = data.get('baselineEvidence', {})
    environment = data.get('environment')
    if (not isinstance(environment, str) or not environment.strip()
            or evidence.get('environment') != environment
            or evidence.get('taskCode') != 'EXM_MANAGE_EXPENSE_FIELDS_BY_CATEGORY'
            or evidence.get('complete') is not True):
        raise ValueError('Complete same-target, same-task baseline evidence required')
    resolved = data.get('resolvedBusinessUnits')
    if not isinstance(resolved, list) or not resolved:
        raise ValueError('Resolved active BU evidence required')
    names, ids = set(), set()
    for bu in resolved:
        name, identity = bu.get('BuName'), bu.get('BusinessUnitId')
        if (not isinstance(name, str) or not name.strip() or name in names
                or type(identity) is not int or not 0 < identity <= 9223372036854775807
                or identity in ids or bu.get('ActiveFlag') is not True):
            raise ValueError('Ambiguous or invalid resolved BU evidence')
        names.add(name)
        ids.add(identity)
    baseline = data.get('baselineRows')
    if not isinstance(baseline, list):
        raise ValueError('Baseline rows required')
    existing = {}
    for row in baseline:
        if not isinstance(row, dict) or set(row) != HEADERS or any(not isinstance(v, str) for v in row.values()):
            raise ValueError('Baseline must contain exactly the 19 exported string cells')
        key = (row['BuName'], row['CategoryCode'])
        if not all(key) or key in existing:
            raise ValueError('Missing or duplicate baseline scope')
        existing[key] = row
    requests = data.get('requests')
    if not isinstance(requests, list) or not requests:
        raise ValueError('No requested rows')
    audit_policy = data.get('createAuditPolicy')
    if audit_policy not in (None, 'blank', 'pause'):
        raise ValueError('Create audit policy must be blank, pause or omitted')
    operations, seen = [], set()
    for request in requests:
        if not isinstance(request, dict) or set(request) - {'businessUnit', 'category', 'enabled', 'fields', 'source'}:
            raise ValueError('Unknown request properties')
        bu, category = request.get('businessUnit'), request.get('category')
        if not isinstance(bu, str) or bu.strip() not in names or category not in CATEGORIES:
            raise ValueError('Unresolved BU or category')
        bu = bu.strip()
        key = (bu, category)
        if key in seen:
            raise ValueError('Duplicate requested BU/category')
        seen.add(key)
        flag = request.get('enabled', '')
        if flag is None:
            flag = ''
        if not isinstance(flag, str) or flag.strip().upper() not in ('', 'Y', 'N'):
            raise ValueError('Enabled must be Y, N or blank')
        flag = flag.strip().upper() or 'N'
        fields = request.get('fields', {})
        if not isinstance(fields, dict) or set(fields) - set(FIELDS):
            raise ValueError('Unknown field attribute')
        values, defaults = {}, []
        for field, value in fields.items():
            if value is None:
                value = ''
            if not isinstance(value, str):
                raise ValueError('Field choice must be text')
            label = value.strip().lower()
            if flag == 'N':
                if label:
                    raise ValueError('Removal conflicts with explicit field decisions')
                continue
            if label and label not in LABELS:
                raise ValueError('Field choice must be Required, Optional or Hidden')
            values[field] = LABELS[label or 'optional']
            if not label:
                defaults.append(field)
        before = existing.get(key)
        op = {'BuName': bu, 'CategoryCode': category, 'source': request.get('source'),
              'defaults': defaults, 'changes': [], 'issues': []}
        if flag == 'N':
            op['operation'] = 'already_absent' if before is None else 'assisted_removal'
            op['contract_status'] = 'passed'
            op['execution_status'] = 'no_change' if before is None else 'awaiting_manual_execution'
        else:
            if not values:
                raise ValueError('Y requires at least one applicable field header')
            unsupported = set(values) - REVIEWED.get(category, set())
            op['operation'] = 'create' if before is None else 'update'
            op['changes'] = [{'field': f, 'before': None if before is None else before[f], 'after': v}
                             for f, v in values.items() if before is None or before[f] != v]
            if unsupported:
                op['issues'].append('field_contract_unverified')
            if before is None:
                if audit_policy is None:
                    op['issues'].append('create_audit_policy_required')
                elif audit_policy == 'pause':
                    op['issues'].append('create_paused_by_user')
                if category in REVIEWED and set(values) != REVIEWED[category]:
                    op['issues'].append('create_applicable_field_headers_missing')
                if not op['issues']:
                    # Qualified blank-audit create policy: start empty, never clone a BU.
                    candidate = {header: '' for header in HEADERS}
                    candidate.update(BuName=bu, CategoryCode=category, **values)
                    op['candidateRow'] = candidate
                    op['audit_policy'] = 'blank_framework_generated'

            elif not unsupported:
                if op['changes']:
                    op['candidateRow'] = dict(before, **values)
                else:
                    op['operation'] = 'unchanged'
            op['contract_status'] = 'blocked' if op['issues'] else 'passed'
            op['execution_status'] = ('blocked' if op['issues'] else
                                      'no_change' if not op['changes'] else 'awaiting_core_preflight')
        operations.append(op)
    blocked = any(op['contract_status'] == 'blocked' for op in operations)
    manual = any(op['operation'] == 'assisted_removal' for op in operations)
    mutations = any(op['operation'] in ('create', 'update') for op in operations)
    status = 'blocked' if blocked else 'split_workflow_required' if manual and mutations else 'awaiting_manual_execution' if manual else 'awaiting_core_preflight' if mutations else 'no_change'
    return {'input_status': 'passed', 'contract_status': 'blocked' if blocked else 'passed',
            'execution_status': status, 'counts': dict(Counter(op['operation'] for op in operations)),
            'operations': operations, 'submission_allowed': False,
            'next_action': 'Resolve each contract issue; select blank or pause for new-row audits when required. Never submit a partial plan.' if blocked else
                           'Use the existing Run Book and core.data-loader preview/approval for mutations; verify manual removals separately.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, help='Protected JSON; see ora_input_validation.md')
    args = parser.parse_args()
    try:
        with open(args.input, encoding='utf-8') as stream:
            result = plan(json.load(stream))
    except (OSError, ValueError, TypeError, AttributeError, KeyError):
        print(json.dumps({'input_status': 'blocked', 'contract_status': 'not_evaluated',
                          'execution_status': 'blocked', 'failure_class': 'input_validation',
                          'message': 'Invalid input or baseline evidence; validate scope, flags, labels, duplicates and complete same-target baseline.'}))
        return 1
    print(json.dumps(result, indent=2))
    return 1 if result['contract_status'] == 'blocked' else 0


if __name__ == '__main__':
    sys.exit(main())
