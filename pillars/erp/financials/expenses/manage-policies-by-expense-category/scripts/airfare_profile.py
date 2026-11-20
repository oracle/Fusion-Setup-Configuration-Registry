"""Airfare's own no-determinant resulting-state and operation boundaries.

Flight classes are checked against fresh target lookup evidence separately.
New-row preparation joins pinned serialization evidence; live create is pending.
"""
import hashlib
from datetime import date
from pathlib import Path
from accepted_meals_profile import rate_date

ROOT = Path(__file__).resolve().parents[1]
P = 'ORA_EXM_AIRFARE_POLICY'
R = P + '_LINE'
SOURCE = 'AIRFARE-SOURCE-CONTRACT'
IDENTITY = [P+'.PolicyName', 'EndDate', 'FlightDurationThreshold', 'RoleName',
            'StartDate', 'TypeOfRateCode']
UPDATES = {'Description', 'PolicyEnforcementCode', 'DispWarningToUserFlag'}


def validate_evidence(contract):
    proof = ROOT/'references/airfare-source-contract.json'
    if contract.get('sources', {}).get(SOURCE, {}).get('sha256') != hashlib.sha256(proof.read_bytes()).hexdigest():
        raise ValueError('Airfare source contract changed; regenerate and review the runtime contract')
    path=ROOT/'references/airfare-create-serialization.json'
    if contract.get('sources',{}).get('SHARED-FSM-AIRFARE-CREATE-SERIALIZATION',{}).get('sha256')!=hashlib.sha256(path.read_bytes()).hexdigest():
        raise ValueError('Airfare create serialization changed; regenerate and review the runtime contract')


def validate_parent(row):
    if row.get('Status') not in {'DRAFT', 'VALID'}:
        raise ValueError('Airfare status transition requires a separate qualified operation')
    if not row.get('PolicyName', '').strip() or len(row['PolicyName']) > 60 or len(row.get('Description', '')) > 240:
        raise ValueError('Airfare Policy Name allows 60 characters and Description 240')
    for field in ('EnabledRoleFlag', 'EnabledFlightTypeFlag', 'EnabledFlightDurationFlag'):
        if row.get(field) != 'N':
            raise ValueError('Airfare requires resolved No for determinant '+field)
    if any(row.get(f) != '' for f in ('PolicyRoleCode', 'FlightDurationCode')):
        raise ValueError('Airfare determinant settings are outside the initial profile')
    enforcement = row.get('PolicyEnforcementCode')
    warning = row.get('DispWarningToUserFlag')
    if enforcement not in {'PREVENT', 'VIOLATION'}:
        raise ValueError('Supply an explicit Airfare Policy Enforcement choice')
    if enforcement == 'VIOLATION' and warning not in {'Y', 'N'}:
        raise ValueError('Airfare warning enforcement requires resolved Display Warning to User Yes/No')
    if enforcement == 'PREVENT' and warning not in {'', 'N'}:
        raise ValueError('Airfare Display Warning to User is not enabled for Prevent report submission')


def validate_rate(row):
    if row.get('Status') not in {'DRAFT', 'VALID'}:
        raise ValueError('Airfare rate status is outside the initial profile')
    # Own UI doCreateSingleRate creates this catch-all even with no determinants.
    if row.get('TypeOfRateCode') != 'CATCH_ALL':
        raise ValueError('Airfare no-determinant rates require the explicit CATCH_ALL key')
    if any(row.get(f) != '' for f in ('FlightDurationThreshold', 'RoleName', 'RoleCode',
            'FlightClassCodeDomestic', 'FlightClassCodeInternat', 'InvalidCode')):
        raise ValueError('Airfare determinant or split domestic/international rates are outside the initial profile')
    if row.get('FlightClassCode') not in {'ANY', 'BUSINESS', 'COACH'}:
        raise ValueError('Airfare Flight Class requires an explicit supported choice and target lookup validation')
    start = rate_date(row.get('StartDate', ''), 'StartDate')
    if row.get('EndDate') and rate_date(row['EndDate'], 'EndDate') < start:
        raise ValueError('Airfare EndDate must be on or after StartDate')


def existing_identity_context(values, rows, *, create_allowed=False):
    """Resolve the hidden key through the selected reviewed operation.

    Updates retain one exact existing rate. Explicit create admission uses the
    owning no-determinant CATCH_ALL value; it cannot repair an ambiguous key.
    Public callers must first validate the runtime's operation/source binding.
    """
    if not values.get(P+'.PolicyName') or not values.get('StartDate'):
        raise ValueError('Airfare rate requires explicit Policy Name and Start Date')
    fields = [f for f in IDENTITY if f != 'TypeOfRateCode']
    matches = [row for row in rows if all(row.get(f, '') == values.get(f, '') for f in fields)]
    if not matches and create_allowed:
        # Own UI creates the no-determinant catch-all. Runtime ownership and
        # source binding are checked before this explicit identity is used.
        return {'TypeOfRateCode':'CATCH_ALL'}
    if len(matches) != 1:
        raise ValueError('Airfare rate requires one exact existing full-key context unless its reviewed create route is selected')
    validate_rate(matches[0])
    return {'TypeOfRateCode': matches[0]['TypeOfRateCode']}


def validate_schedule(rates):
    if not rates:
        raise ValueError('Each selected Airfare policy requires at least one compatible rate')
    keys, periods = set(), []
    for row in rates:
        validate_rate(row)
        key = tuple(row.get(f, '') for f in IDENTITY if f != 'StartDate')
        if key in keys:
            raise ValueError('Duplicate Airfare alternate key excluding StartDate')
        keys.add(key)
        periods.append((rate_date(row['StartDate'], 'StartDate'),
            rate_date(row['EndDate'], 'EndDate') if row.get('EndDate') else date.max))
    periods.sort()
    if any(right[0] <= left[1] for left, right in zip(periods, periods[1:])):
        raise ValueError('Airfare effective periods overlap; end dates are inclusive')


def validate_selection(records, rows):
    for name in {r['policy_name'] for r in records}:
        parents = [r for r in rows[P] if r['PolicyName'].casefold() == name.casefold()]
        rates = [r for r in rows[R] if r[P+'.PolicyName'].casefold() == name.casefold()]
        if len(parents)>1 or parents and parents[0]['PolicyName']!=name or any(r[P+'.PolicyName']!=name for r in rates):
            raise ValueError('Airfare requires an exact unambiguous policy association')
        if parents:
            validate_parent(parents[0])
            for row in rates:validate_rate(row)
        elif rates:
            raise ValueError('Orphan Airfare baseline rate')
        elif {r['entity']for r in records if r['policy_name']==name}!={P,R}:
            raise ValueError('Create requires an Airfare parent and at least one rate')


def validate_change(entity, operation, before, after, baseline_rows):
    if operation not in {'create','update'}:
        raise ValueError('Airfare requires a reviewed create or update operation')
    (validate_parent if entity == P else validate_rate)(after)
    allowed = UPDATES if entity == P else {'FlightClassCode'}
    if operation=='create' and after.get('Status')!='DRAFT':
        raise ValueError('Airfare create requires consumer-owned DRAFT status')
    if operation=='update' and {f for f in after if after[f] != before[f]} - allowed:
        raise ValueError('Airfare keys, dates, status and determinant changes require a separate qualified operation')
    if entity == P and before.get('PolicyEnforcementCode') == 'PREVENT' and after.get('PolicyEnforcementCode') == 'VIOLATION' and after.get('DispWarningToUserFlag') not in {'Y', 'N'}:
        raise ValueError('Changing to Airfare warning enforcement requires an explicit Display Warning to User choice')


def verify_result(submitted, original_rows):
    parents = {r['PolicyName']: r for r in original_rows[P]}
    rates = {tuple(r.get(f, '') for f in IDENTITY): r for r in original_rows[R]}
    for record in submitted:
        row = record['values']
        if record['entity'] == P:
            validate_parent(row)
            parents[row['PolicyName']] = row
        else:
            validate_rate(row)
            rates[tuple(row.get(f, '') for f in IDENTITY)] = row
    names = {r['values'].get('PolicyName', r['values'].get(P+'.PolicyName')) for r in submitted}
    for name in names:
        if name not in parents:
            raise ValueError('Airfare rate requires an exact parent')
        validate_parent(parents[name])
        validate_schedule([r for r in rates.values() if r[P+'.PolicyName'] == name])
    return {'profile': 'airfare-no-determinants-source-v1', 'requires_live_qualification': True,
        'qualification': 'source_qualified_create_preparation_live_pending_existing_updates_scoped',
        'import_approved': False}
