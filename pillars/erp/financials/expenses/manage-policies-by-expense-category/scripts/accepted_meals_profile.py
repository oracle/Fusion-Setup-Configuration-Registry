"""Reusable admission for the accepted SINGLE Meals profile, with no test IDs.

Admission validates business settings and resulting rows. It never authorizes
upload: native Run Book, Task Hook and Data Loader approval remain mandatory.
"""
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import json
import hashlib
from pathlib import Path

P = 'ORA_EXM_MEALS_POLICY'
R = P + '_LINE'
PROFILE = 'meals-single-currency-v2'
ROOT = Path(__file__).resolve().parents[1]


def definition():
    return json.loads((ROOT/'references/accepted-meals-profile.json').read_text())


def validate_context(contract, context, provenance, validation_date, receipt_path):
    profile = definition()
    if contract.get('executable_profile') != PROFILE:
        raise ValueError('Unknown executable Meals profile')
    proof = contract.get('sources',{}).get('LIVE-ACCEPTED-MEALS-PROFILE',{})
    if proof.get('sha256') != hashlib.sha256((ROOT/'references/accepted-meals-profile.json').read_bytes()).hexdigest():
        raise ValueError('Accepted profile evidence changed; regenerate and review its runtime contract')
    # Compatibility is checked against the actual task schema in read_package;
    # retain release provenance without imposing a version allowlist.
    release = context.get('ProcessRelease')
    if not isinstance(release, str) or not release.strip():
        raise ValueError('Meals profile requires baseline ProcessRelease provenance')
    if (not provenance or not context.get('ProcessEnv')
            or context['ProcessEnv'] != provenance.get('environment')):
        raise ValueError('Meals profile requires verified baseline environment provenance')
    from currency_receipt import origin
    origin(provenance.get('origin'))
    today = datetime.now(timezone.utc).date()
    if validation_date != today.isoformat() or receipt_path is None:
        raise ValueError('Meals profile requires today\'s explicit UTC validation date and baseline receipt')
    receipt = json.loads(Path(receipt_path).read_text())
    try:
        observed = datetime.fromisoformat(receipt['observed_at_utc'].replace('Z', '+00:00'))
    except (KeyError, ValueError, TypeError):
        raise ValueError('Meals profile baseline needs an actual observation timestamp') from None
    now = datetime.now(timezone.utc)
    if observed.tzinfo is None or observed.astimezone(timezone.utc).date() != today or observed > now:
        raise ValueError('Meals profile baseline observation is stale or in the future; refresh through the approved export route')
    observation = profile['observation_target']
    # Public evidence deliberately omits private historical target identity.
    # Missing identity never grants historical/live qualification to any target.
    observed_target = (bool(observation.get('environment'))
        and bool(observation.get('origin'))
        and context['ProcessEnv'] == observation['environment']
        and context['ProcessRelease'] == observation['release']
        and origin(provenance['origin']) == origin(observation['origin']))
    return {'historically_observed_target': observed_target,
            'requires_live_qualification': not observed_target,
            'release': context['ProcessRelease']}


def validate_parent(row, *, creating=False):
    profile = definition()
    for field, expected in profile['parent_settings'].items():
        if row.get(field) != expected:
            raise ValueError(field+': supported Meals profile requires '+repr(expected))
    for field, domain in profile['parent_domains'].items():
        if row.get(field) not in domain:
            raise ValueError(field+': supply one of '+repr(domain))
    if not row.get('CurrencyCode','').strip():
        raise ValueError('Supply a parent Currency Code eligible in the target environment')
    if row['SingleInstanceLimitFlag'] == row['DailyLimitFlag'] == 'N':
        raise ValueError('Enable Single Instance Limit and/or Daily Sum Limit')
    if row['DispWarningToUserFlag']=='Y' and row['PolicyViolationFlag']!='Y':
        raise ValueError('Display Warning to User requires Policy Violation Warning = Yes')
    if row['PolicyEnforcementCode']=='UPPER' and any(row[f]!='N' for f in
            ('PolicyViolationFlag','DispWarningToUserFlag','PreventSubmissionFlag')):
        raise ValueError('Reimburse upper limit requires warning, display and prevention controls = No')
    for field, control in [('WarningTolerance','PolicyViolationFlag'),('ErrorTolerance','PreventSubmissionFlag')]:
        number = decimal_value(row.get(field,''),field)
        if row[control]=='Y' and number is None:
            raise ValueError(field+' is required when '+control+' = Yes')
    if row.get('WarningTolerance') and row.get('ErrorTolerance'):
        if Decimal(row['WarningTolerance']) >= Decimal(row['ErrorTolerance']):
            raise ValueError('Warning Tolerance must be less than Error Tolerance when both are present')
    for field in profile['parent_empty_fields']:
        if row.get(field) != '':
            raise ValueError(field+': outside the supported Meals profile; leave blank or preserve a compatible baseline')
    for field in ('RateIncludeMealsFlag','RateIncludeOtherFlag'):
        if row.get(field) != ('' if creating else 'N'):
            raise ValueError(field+': incompatible hidden Meals profile value')
    name = row.get('PolicyName', '')
    if not name.strip():
        raise ValueError('PolicyName is required')
    if len(name) > 80 or len(row.get('Description', '')) > 240:
        raise ValueError('Meals profile allows Policy Name up to80 and Description up to240 characters')


def decimal_value(value, field):
    if value == '':
        return None
    try:
        amount = Decimal(value)
    except (InvalidOperation,ValueError,TypeError):
        raise ValueError(field+' must be a finite nonnegative number') from None
    if not amount.is_finite() or amount < 0:
        raise ValueError(field+' must be a finite nonnegative number')
    return amount


def validate_rate(row, parent=None):
    if row.get('Status') != 'DRAFT':
        raise ValueError('Meals profile supports DRAFT rates only')
    for field in definition()['rate_empty_fields']:
        if row.get(field) != '':
            raise ValueError(field+': outside the supported single-currency Meals rate profile')
    for field in ('SingleInstanceLimit','DailyLimit'):
        decimal_value(row.get(field,''),field)
    if parent is not None:
        from reduced_rate_profile import validate_resulting_rate
        validate_resulting_rate(R,row,parent)
    start = rate_date(row.get('StartDate', ''), 'StartDate')
    if row.get('EndDate') and rate_date(row['EndDate'], 'EndDate') < start:
        raise ValueError('EndDate must be on or after StartDate')


def rate_date(value, field):
    try:
        date = datetime.strptime(value, '%Y/%m/%d').date()
    except (ValueError, TypeError):
        raise ValueError(field+': supply a valid date; CSV uses YYYY/MM/DD') from None
    if date.strftime('%Y/%m/%d') != value:
        raise ValueError(field+' must use YYYY/MM/DD representation')
    return date


def validate_schedule(rates, parent):
    """Check all resulting rates, including retained rows absent from input.

    With no role/location/type determinants, effective periods must not overlap.
    End dates are inclusive; a blank end date represents an open-ended period.
    This is a conservative authoring rule, not a claim about server defaulting.
    """
    if not rates:
        raise ValueError('Each selected Meals policy requires at least one compatible rate')
    periods = []
    no_start_keys = set()
    for row in rates:
        validate_rate(row, parent)
        key = tuple(row.get(f, '') for f in ('CurrencyCode','EndDate','GeoLocName','RoleName','TypeOfRateCode','ZoneCode'))
        if key in no_start_keys:
            raise ValueError('Duplicate rate alternate key excluding StartDate; supply distinct nonoverlapping periods')
        no_start_keys.add(key)
        periods.append((rate_date(row['StartDate'], 'StartDate'),
            rate_date(row['EndDate'], 'EndDate') if row.get('EndDate') else datetime.max.date()))
    periods.sort()
    if any(right[0] <= left[1] for left, right in zip(periods, periods[1:])):
        raise ValueError('Meals rate effective periods overlap; end dates are inclusive')


def validate_selection(records, rows):
    """Reject unsupported existing settings before any workbook overlay."""
    for name in {r['policy_name'] for r in records}:
        selected = [r for r in records if r['policy_name'] == name]
        parents = [r for r in rows[P] if r['PolicyName'].casefold() == name.casefold()]
        rates = [r for r in rows[R] if r[P+'.PolicyName'].casefold() == name.casefold()]
        if len(parents) > 1:
            raise ValueError('Meals profile requires an unambiguous parent identity')
        if parents:
            if parents[0]['PolicyName'] != name or any(r[P+'.PolicyName'] != name for r in rates):
                raise ValueError('Use the exact existing Policy Name; case aliases are unsupported')
            validate_parent(parents[0])
            for rate in rates:
                validate_rate(rate,parents[0])
        elif rates:
            raise ValueError('Orphan rate association in baseline')
        elif {r['entity'] for r in selected} != {P,R}:
            raise ValueError('Create requires a Meals policy row and at least one Meals Rates row per new policy')


def validate_change(entity, operation, before, after, baseline_rows):
    if entity == P:
        validate_parent(after, creating=operation == 'create')
    elif entity == R:
        validate_rate(after)
    else:
        raise ValueError('Only Meals policy/rate rows are executable')
    if operation == 'update':
        allowed = ({'Description','SingleInstanceLimitFlag','DailyLimitFlag','PolicyEnforcementCode',
            'PolicyViolationFlag','DispWarningToUserFlag','PreventSubmissionFlag','WarningTolerance','ErrorTolerance'}
            if entity == P else {'SingleInstanceLimit','DailyLimit'})
        changed = {field for field,value in after.items() if before[field] != value}
        if changed - allowed:
            raise ValueError('Meals updates cannot change identity, dates, currency, status or hidden fields')
    if entity == P:
        for field, control in [('WarningTolerance','PolicyViolationFlag'),('ErrorTolerance','PreventSubmissionFlag')]:
            changed = operation=='create' or before.get(field,'') != after.get(field,'')
            if after.get(field) and changed and after[control]!='Y':
                raise ValueError(field+' is not enterable while '+control+' = No; blank updates preserve stored tolerances')


def verify_result(submitted, original_rows):
    """Validate actual serialized rows, including automatically added context."""
    parents = {r['PolicyName']:r for r in original_rows[P]}
    def rate_key(row):
        return tuple(row.get(f, '') for f in (P+'.PolicyName','CurrencyCode','EndDate',
            'GeoLocName','RoleName','StartDate','TypeOfRateCode','ZoneCode'))
    rates = {rate_key(r):r for r in original_rows[R]}
    for record in submitted:
        row = record['values']
        if record['entity'] == P:
            creating = not any(r['PolicyName'] == row['PolicyName'] for r in original_rows[P])
            validate_parent(row, creating=creating)
            parents[row['PolicyName']] = row
        else:
            validate_rate(row)
            rates[rate_key(row)] = row
    selected = {r['values'].get('PolicyName',r['values'].get(P+'.PolicyName')) for r in submitted}
    for name in selected:
        if name not in parents:
            raise ValueError('Selected Meals rate requires an exact parent')
        validate_schedule([r for r in rates.values() if r[P+'.PolicyName'] == name],parents[name])
    original = {'CurrencyCode':'USD','SingleInstanceLimitFlag':'Y','DailyLimitFlag':'N',
        'PolicyEnforcementCode':'VIOLATION','PolicyViolationFlag':'N','DispWarningToUserFlag':'N','PreventSubmissionFlag':'N',
        'WarningTolerance':'','ErrorTolerance':''}
    old_parents = {r['PolicyName']:r for r in original_rows[P]}
    expanded = len(selected) > 1 or any(
        sum(r[P+'.PolicyName'] == n for r in rates.values()) > 1
        or any(r.get('EndDate') for r in rates.values() if r[P+'.PolicyName'] == n)
        or any(parents[n].get(f)!=v for f,v in original.items())
        or (n in old_parents and (
            any(old_parents[n].get(f)!=v for f,v in original.items())
            or any(old_parents[n].get(f)!=v for f,v in parents[n].items() if f!='Description')))
        for n in selected)
    return {'profile':PROFILE, 'qualification':'accepted_core_with_expanded_inputs' if expanded else 'accepted_create_and_update_profile',
            'requires_live_qualification':expanded,
            'parameterization':'Multiple Meals policies and nonoverlapping effective-dated rates; eligible single currencies, either/both limits, UPPER/VIOLATION and valid warning controls; dates/identity/currency immutable on update',
            'import_approved':False}
