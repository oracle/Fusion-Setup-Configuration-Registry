"""Inspect an EBS expense-category CSV locally; never call Fusion or approve an import.

The output contains source data. Persist it only in the untracked project workspace.
Blank source cells are unspecified, not Optional; retain EBS audit data as provenance.
"""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys

DIRECT = {
    'END_DATE_FIELD': 'EndDateField', 'MERCHANT_FIELD': 'MerchantField',
    'TICKET_CLASS_FIELD': 'TicketClassField', 'TICKET_NUMBER_FIELD': 'TicketNumberField',
    'LOCATION_TO_FIELD': 'LocationToField', 'LOCATION_FROM_FIELD': 'LocationFromField',
    'LICENSE_PLATE_FIELD': 'LicensePlateField',
}
UNMAPPED = {'DISTANCE_UOM', 'DISTANCE_FIELD', 'DESTINATION_FIELD',
            'ATTENDEES_FIELD', 'ATTENDEES_NUMBER_FIELD'}
AUDIT = {'CREATION_DATE', 'CREATED_BY', 'LAST_UPDATE_LOGIN', 'LAST_UPDATE_DATE', 'LAST_UPDATED_BY'}
KEYS = {'CATEGORY_OPTION_ID', 'CATEGORY_CODE', 'ORG_ID'}
HEADERS = KEYS | AUDIT | set(DIRECT) | UNMAPPED
CATEGORIES = {'ACCOMMODATIONS', 'AIRFARE', 'CAR_RENTAL', 'ENTERTAINMENT', 'MEALS', 'MILEAGE', 'MISC'}
# EBS source semantics supplied by the migration owner. Fusion-native ENABLED
# still means Optional; translate through intent, never copy source codes.
EBS_DISPLAY_LABELS = {'ENABLED': 'Required', 'DISABLED': 'Hidden', 'REQUIRED': 'Required'}
SOURCE_TYPE = 'ebs-category-csv'


def records_digest(headers, rows):
    return hashlib.sha256(json.dumps({'headers': headers, 'rows': rows},
                                    sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def parse_csv(raw):
    if not raw or len(raw) > 10 * 1024 * 1024 or b'\x00' in raw:
        raise ValueError('Empty, oversized or binary CSV')
    reader = csv.reader(io.StringIO(raw.decode('utf-8-sig'), newline=''), strict=True)
    headers = next(reader)
    if len(headers) != len(set(headers)) or set(headers) - HEADERS or not KEYS <= set(headers):
        raise ValueError('Unknown, duplicate or missing key headers')
    rows = []
    for cells in reader:
        if len(cells) != len(headers):
            raise ValueError('CSV row width mismatch')
        rows.append(dict(zip(headers, cells)))
    if not rows:
        raise ValueError('No source records')
    return {'type': SOURCE_TYPE, 'version': 1, 'sha256': hashlib.sha256(raw).hexdigest(),
            'headers': headers, 'rows': rows, 'recordsSha256': records_digest(headers, rows),
            'businessUnitMappings': {}}


def cross_skill_routes(rows):
    """Advisory ownership for validated rows; never execution or semantic approval.

    Keep one route record for every nonblank business setting. Refer to existing
    task builders without inventing missing policy values or assigning policies.
    """
    prefix = 'erp.financials.expenses.'
    routes = []
    for number, row in enumerate(rows, 1):
        for field in sorted(set(DIRECT) | UNMAPPED):
            if not row.get(field, '').strip():
                continue
            route = {'record': number, 'sourceOrgId': row['ORG_ID'].strip(),
                     'category': row['CATEGORY_CODE'].strip(), 'sourceField': field,
                     'required': True, 'executionReady': False}
            if field in DIRECT:
                route.update(ownerSkill=prefix+'manage-expense-fields-by-category',
                             targetField=DIRECT[field], status='requires_category_contract_and_baseline',
                             dependencies=[])
            elif field in {'ATTENDEES_FIELD', 'ATTENDEES_NUMBER_FIELD'}:
                route.update(ownerSkill=prefix+'manage-policies-by-expense-category',
                             profile='Entertainment', status='semantic_conversion_and_assignment_gap',
                             dependencies=[prefix+'manage-expense-report-templates'],
                             missingInputs=['exact attendee capture behavior', 'policy identity',
                                            'count threshold/currency if count mode',
                                            'target expense types and assignment dates'],
                             implementationBoundary='Policy builder exists; template policy assignment is unsupported. Count and detail modes cannot be combined by this profile.')
            elif field == 'DISTANCE_UOM':
                route.update(ownerSkill=prefix+'manage-policies-by-expense-category',
                             profile='Mileage', targetField='UnitOfMeasureCode',
                             status='requires_policy_context_and_unit_mapping',
                             dependencies=[prefix+'manage-expense-report-templates'],
                             missingInputs=['policy identity and source rates/currency/dates or verified existing policy',
                                            'applicable expense types and assignment scope'],
                             implementationBoundary='Mileage policy builder exists; category unit does not define a complete policy. No automatic policy assignment.')
            else:
                route.update(ownerSkill=None, status='semantic_mapping_unverified', dependencies=[],
                             implementationBoundary='Do not infer Oracle Maps setup, odometer settings or a separate-task exclusion from this EBS flag.')
            routes.append(route)
    return routes


def normalize(source):
    """Regenerate requests and issues from retained source; caller must check live BU evidence.

    Same-named target columns are mapping candidates, subject to the planner's
    category-specific writable contract. No unsupported category is qualified here.
    """
    if not isinstance(source, dict) or source.get('type') != SOURCE_TYPE or source.get('version') != 1:
        raise ValueError('Invalid EBS intake envelope')
    if not re.fullmatch(r'[a-f0-9]{64}', str(source.get('sha256', ''))):
        raise ValueError('Source checksum required')
    headers, rows = source.get('headers'), source.get('rows')
    if (not isinstance(headers, list) or not all(isinstance(h, str) for h in headers)
            or len(headers) != len(set(headers)) or set(headers) - HEADERS
            or not KEYS <= set(headers) or not isinstance(rows, list) or not rows):
        raise ValueError('Invalid retained source schema')
    if source.get('recordsSha256') != records_digest(headers, rows):
        raise ValueError('Retained source records changed; rerun CSV intake')
    mappings = source.get('businessUnitMappings', {})
    if not isinstance(mappings, dict):
        raise ValueError('Explicit org-to-BU mappings required')
    requests, issues, seen, seen_ids = [], [], set(), set()
    for number, row in enumerate(rows, 1):
        if not isinstance(row, dict) or set(row) != set(headers) or not all(isinstance(v, str) for v in row.values()):
            raise ValueError('Invalid retained source record')
        org, category, identity = (row[k].strip() for k in ('ORG_ID', 'CATEGORY_CODE', 'CATEGORY_OPTION_ID'))
        if not re.fullmatch(r'[1-9][0-9]*', org) or not re.fullmatch(r'[1-9][0-9]*', identity) or category not in CATEGORIES:
            raise ValueError('Invalid source identity or category')
        if (org, category) in seen or identity in seen_ids:
            raise ValueError('Duplicate source identity or org/category')
        seen.add((org, category))
        seen_ids.add(identity)
        def issue(code, field=None):
            issues.append({'record': number, 'category': category, 'sourceOrgId': org,
                           'field': field, 'code': code})
        fields = {}
        for source_field, target_field in DIRECT.items():
            value = row.get(source_field, '').strip()
            if not value:
                continue
            if value not in EBS_DISPLAY_LABELS:
                issue('unknown_display_code', source_field)
            else:
                fields[target_field] = EBS_DISPLAY_LABELS[value]
        for field in sorted(UNMAPPED):
            if row.get(field, '').strip():
                issue('fusion_equivalent_unverified', field)
        mapping = mappings.get(org)
        name = None
        if mapping is None:
            issue('business_unit_mapping_required')
        elif (not isinstance(mapping, dict) or set(mapping) != {'BuName', 'BusinessUnitId', 'decisionRef'}
              or not isinstance(mapping['BuName'], str) or not mapping['BuName'].strip()
              or type(mapping['BusinessUnitId']) is not int or not 0 < mapping['BusinessUnitId'] <= 9223372036854775807
              or not isinstance(mapping['decisionRef'], str) or not mapping['decisionRef'].strip()):
            raise ValueError('Invalid approved business-unit mapping')
        else:
            name = mapping['BuName'].strip()
        if not fields:
            issue('no_mapped_field_decisions')
        requests.append({'businessUnit': name, 'category': category, 'enabled': 'Y', 'fields': fields,
                         'source': {'type': SOURCE_TYPE, 'record': number, 'sourceOrgId': org,
                                    'categoryOptionId': identity, 'sha256': source['sha256']}})
    if set(mappings) - {org for org, _ in seen}:
        raise ValueError('Mapping outside source scope')
    targets = [(r['businessUnit'], r['category']) for r in requests if r['businessUnit']]
    if len(targets) != len(set(targets)):
        raise ValueError('Multiple source orgs map to one target BU/category')
    return {'input_status': 'passed', 'mapping_status': 'blocked' if issues else 'mapped_candidates',
            'execution_status': 'blocked' if issues else 'awaiting_target_validation',
            'source_record_count': len(rows), 'requests': requests, 'issues': issues,
            'ebsSource': source, 'crossSkillRoutes': cross_skill_routes(rows), 'submission_allowed': False}


def validate_binding(data):
    """Fail closed when source issues or dropped/edited requests reach the planner."""
    source = data.get('ebsSource')
    marked = any(isinstance(r, dict) and isinstance(r.get('source'), dict)
                 and r['source'].get('type') == SOURCE_TYPE for r in data.get('requests', []))
    if source is None:
        if marked:
            raise ValueError('Retained EBS source review required')
        return []
    review = normalize(source)
    if data.get('requests') != review['requests']:
        raise ValueError('EBS requests differ from the retained source mapping; regenerate intake')
    resolved = data.get('resolvedBusinessUnits', [])
    for mapping in source['businessUnitMappings'].values():
        if not any(b.get('BuName') == mapping['BuName'].strip()
                   and b.get('BusinessUnitId') == mapping['BusinessUnitId']
                   and b.get('ActiveFlag') is True for b in resolved):
            raise ValueError('Approved EBS mapping differs from live BU evidence')
    return review['issues']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--business-unit-mappings', type=Path, help='JSON org ID -> BuName, BusinessUnitId, decisionRef')
    parser.add_argument('--output', type=Path, help='New private JSON file; never overwritten')
    parser.add_argument('--dry-run', action='store_true', help='Validate and print counts only; write nothing')
    args = parser.parse_args()
    if not args.dry_run and args.output is None:
        parser.error('--output required unless --dry-run')
    try:
        source = parse_csv(args.source.read_bytes())
        if args.business_unit_mappings:
            source['businessUnitMappings'] = json.loads(args.business_unit_mappings.read_text())
        result = normalize(source)
        if not args.dry_run:
            fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                json.dump(result, stream, indent=2)
                stream.write('\n')
        print(json.dumps({k: result[k] for k in ('input_status', 'mapping_status', 'execution_status',
                                               'source_record_count', 'issues', 'submission_allowed')}))
        return 1 if result['issues'] else 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError, StopIteration, csv.Error):
        print(json.dumps({'input_status': 'blocked', 'execution_status': 'blocked',
                          'failure_class': 'input_validation',
                          'message': 'Check CSV structure, identities, mappings and a new writable output path; no Fusion call made.'}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
