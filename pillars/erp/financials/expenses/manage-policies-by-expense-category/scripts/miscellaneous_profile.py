"""Miscellaneous's own no-determinant create and update state contract.

UI enterability is kept separate from the AM's ordinary/catch-all missing-rate
predicate. Explicit managed/empty recipes supply no import authority.
"""
import calendar
import hashlib
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from accepted_meals_profile import decimal_value, rate_date

ROOT = Path(__file__).resolve().parents[1]
P = 'ORA_EXM_MISCELLANEOUS_POLICY'
R = P + '_LINE'
SOURCE = 'MISCELLANEOUS-SOURCE-CONTRACT'
LIMITS = ('SingleInstanceLimit', 'DailyLimit', 'MonthlyLimit', 'YearlyLimit', 'LifetimeLimit')
CONTROLS = ('PolicyViolationFlag', 'DispWarningToUserFlag', 'PreventSubmissionFlag')
PARENT_UPDATES = {'Description', 'RateTypeCode', 'EnabledEligibilityFlag',
    'EligibilityDays', 'DaysBasedItemParentFlag', 'PeriodMonth', 'PeriodDay',
    'PolicyEnforcementCode', 'WarningTolerance', 'ErrorTolerance', *CONTROLS,
    *(f+'Flag' for f in LIMITS)}
RATE_UPDATES = {*LIMITS, 'ReimbursementPercentage'}
# Package names are the service's exported proxies for parent/role/geography IDs.
IDENTITY = [P+'.PolicyName', 'CurrencyCode', 'EndDate', 'GeoLocName', 'RoleName',
    'StartDate', 'TypeOfRateCode', 'ZoneCode', 'GenderCode']
DETERMINANTS = ('GeoLocName', 'RoleName', 'RoleCode', 'GradeCode', 'ZoneCode',
    'GenderCode', 'RawCountry', 'RawState', 'RawCounty', 'RawCity')


def validate_evidence(contract):
    proof = ROOT/'references/miscellaneous-source-contract.json'
    if contract.get('sources', {}).get(SOURCE, {}).get('sha256') != hashlib.sha256(proof.read_bytes()).hexdigest():
        raise ValueError('Miscellaneous source contract changed; regenerate and review the runtime contract')
    path=ROOT/'references/miscellaneous-create-serialization.json'
    if contract.get('sources',{}).get('SHARED-FSM-MISC-CREATE-SERIALIZATION',{}).get('sha256')!=hashlib.sha256(path.read_bytes()).hexdigest():
        raise ValueError('Miscellaneous create serialization changed; regenerate and review the runtime contract')


def enabled(row, field):
    """Y alone is true; preserve actual blank/N false serialization unchanged."""
    if field not in row or row[field] not in {'', 'N', 'Y'}:
        raise ValueError('Miscellaneous '+field+' requires its retained blank/N or explicit Y/N encoding')
    return row[field] == 'Y'


def integer(value, field, maximum):
    try:
        number = Decimal(value)
        if not number.is_finite() or number != number.to_integral_value() or not 1 <= number <= maximum:
            raise ValueError()
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError('Miscellaneous '+field+' must be a positive integer at most '+str(maximum)) from None
    return int(number)


def validate_parent(row):
    if row.get('Status') not in {'DRAFT', 'VALID'}:
        raise ValueError('Miscellaneous status transitions require a separate qualified operation')
    if not row.get('PolicyName', '').strip() or len(row['PolicyName']) > 60 or len(row.get('Description', '')) > 240:
        raise ValueError('Miscellaneous Policy Name allows 60 characters and Description 240')
    for field in ('EnabledRoleFlag', 'EnabledLocationFlag', 'EnabledGenderFlag'):
        if enabled(row, field):
            raise ValueError('Miscellaneous determinants remain excluded: '+field)
    if any(row.get(f, '') != '' for f in ('PolicyRoleCode', 'LocationTypeCode', 'ZoneTypeCode')):
        raise ValueError('Miscellaneous retained determinant settings are outside the no-determinant profile')
    mode = row.get('RateTypeCode')
    if mode not in {'LIMIT', 'PERCENT', 'BOTH'}:
        raise ValueError('Miscellaneous Rate Type must be LIMIT, PERCENT or BOTH')
    selected = {f: enabled(row, f+'Flag') for f in LIMITS}
    if mode == 'PERCENT':
        if any(selected.values()):
            raise ValueError('Miscellaneous percentage-only mode cannot enable monetary limit flags')
        if any(row.get(f) != '' for f in ('CurrencyOptionCode', 'CurrencyCode')):
            raise ValueError('Miscellaneous percentage-only mode requires blank currency context; conversion is not inferred')
    else:
        if not any(selected.values()):
            raise ValueError('Miscellaneous LIMIT/BOTH requires at least one of the five limits enabled')
        if row.get('CurrencyOptionCode') != 'SINGLE' or not row.get('CurrencyCode', '').strip():
            raise ValueError('Miscellaneous monetary limits require a resolved SINGLE parent currency')
    eligibility = enabled(row, 'EnabledEligibilityFlag')
    enabled(row, 'DaysBasedItemParentFlag')
    if eligibility and not row.get('EligibilityDays'):
        raise ValueError('Miscellaneous EligibilityDays is required when minimum days is enabled')
    if row.get('EligibilityDays'):
        integer(row['EligibilityDays'], 'EligibilityDays', 999999999)
    month, day = row.get('PeriodMonth', ''), row.get('PeriodDay', '')
    if selected['YearlyLimit'] and (not month or not day):
        raise ValueError('Miscellaneous Yearly Limit requires PeriodMonth and PeriodDay')
    if bool(month) != bool(day):
        raise ValueError('Miscellaneous annual reset requires both month and day')
    if month:
        if month not in {f'{m:02}' for m in range(1, 13)}:
            raise ValueError('Miscellaneous PeriodMonth must use the retained MONTH code 01 through 12')
        integer(day, 'PeriodDay', calendar.monthrange(2001, int(month))[1])
    flags = {f: enabled(row, f) for f in CONTROLS}
    enforcement = row.get('PolicyEnforcementCode')
    if enforcement not in {'UPPER', 'VIOLATION'}:
        raise ValueError('Miscellaneous Policy Enforcement requires UPPER or VIOLATION')
    if mode == 'LIMIT' and enforcement != 'VIOLATION' or mode != 'LIMIT' and enforcement != 'UPPER':
        raise ValueError('Miscellaneous LIMIT uses VIOLATION; PERCENT/BOTH uses UPPER percentage reimbursement')
    if flags['DispWarningToUserFlag'] and not flags['PolicyViolationFlag']:
        raise ValueError('Miscellaneous Display Warning requires Policy Violation Warning enabled')
    if enforcement == 'UPPER' and any(flags.values()):
        raise ValueError('Miscellaneous percentage reimbursement cannot enable warning/prevention controls')
    if enforcement == 'VIOLATION' and not (flags['PolicyViolationFlag'] or flags['PreventSubmissionFlag']):
        raise ValueError('Miscellaneous VIOLATION requires warning and/or prevent submission enabled')
    numbers = {f: decimal_value(row.get(f, ''), f) for f in ('WarningTolerance', 'ErrorTolerance')}
    for field, control in [('WarningTolerance', 'PolicyViolationFlag'), ('ErrorTolerance', 'PreventSubmissionFlag')]:
        if flags[control] and numbers[field] is None:
            raise ValueError('Miscellaneous '+field+' is required when '+control+' is enabled')
    # EO predicates are unconditional, including when switches are false.
    if all(n is not None for n in numbers.values()) and numbers['WarningTolerance'] >= numbers['ErrorTolerance']:
        raise ValueError('Miscellaneous WarningTolerance must be strictly less than ErrorTolerance')


def validate_rate_scope(row, parent=None):
    """Hard existing line scope only; writable amounts are merged later."""
    if row.get('Status') not in {'DRAFT', 'VALID'} or row.get('InvalidCode', '') != '':
        raise ValueError('Miscellaneous rates require an existing DRAFT/VALID row without InvalidCode')
    if any(row.get(f, '') != '' for f in DETERMINANTS):
        raise ValueError('Miscellaneous rate determinants remain excluded and cannot be discarded from identity')
    if row.get('TypeOfRateCode') not in {'', 'MISC', 'CATCH_ALL'}:
        raise ValueError('Miscellaneous requires its retained blank/MISC/CATCH_ALL rate type, never a generated default')
    start = rate_date(row.get('StartDate', ''), 'StartDate')
    if row.get('EndDate') and rate_date(row['EndDate'], 'EndDate') < start:
        raise ValueError('Miscellaneous EndDate must be on or after StartDate')
    if parent is not None:
        if row.get(P+'.PolicyName') != parent['PolicyName']:
            raise ValueError('Miscellaneous rate requires its exact owning policy')
        if row.get('CurrencyCode') not in {'', parent.get('CurrencyCode', '')}:
            raise ValueError('Miscellaneous child currency differs from its single/percentage parent context')


def validate_rate(row, parent=None):
    validate_rate_scope(row, parent)
    numbers = {f: decimal_value(row.get(f, ''), f) for f in RATE_UPDATES}
    if parent is None:
        return
    validate_parent(parent)
    selected = [f for f in LIMITS if enabled(parent, f+'Flag')]
    percent = parent['RateTypeCode'] in {'PERCENT', 'BOTH'}
    value = numbers['ReimbursementPercentage']
    if row['TypeOfRateCode'] == 'CATCH_ALL':
        missing = [f for f in selected if numbers[f] is None]
        if percent and value is None:
            missing.append('ReimbursementPercentage')
    else:
        # Exact own AM ordinary-row predicate; BOTH is not an invented AND.
        missing = [f for f in selected if numbers[f] is None and value is None]
        if percent and value is None and all(numbers[f] is None for f in LIMITS):
            missing.append('ReimbursementPercentage or a monetary amount')
    if missing:
        raise ValueError('Miscellaneous missing applicable rate: '+', '.join(missing))


def existing_identity_context(values, rows, *, create_allowed=False):
    """Retain an existing key or source-owned empty ordinary create context."""
    visible = [P+'.PolicyName', 'StartDate', 'EndDate']
    if not values.get(visible[0]) or not values.get('StartDate'):
        raise ValueError('Miscellaneous rate requires explicit Policy Name and Start Date')
    matches = [row for row in rows if all(row.get(f, '') == values.get(f, '') for f in visible)]
    if not matches and create_allowed:
        # Own non-ADFDI single-rate creation leaves type/currency/determinants
        # unset. The service import path retains these nulls; no sentinel.
        return {f:''for f in IDENTITY if f not in values}
    if len(matches) != 1:
        raise ValueError('Miscellaneous rate requires one exact existing full-key context unless the reviewed create route is selected')
    validate_rate_scope(matches[0])
    if any(f in values and values[f] != matches[0].get(f, '') for f in IDENTITY):
        raise ValueError('Miscellaneous full-key context cannot rename a hidden identity coordinate')
    return {f: matches[0].get(f, '') for f in IDENTITY if f not in values}


def validate_schedule(rates, parent):
    if not rates:
        raise ValueError('Each selected Miscellaneous policy requires at least one compatible existing rate')
    keys, periods = set(), []
    for row in rates:
        validate_rate(row, parent)
        key = tuple(row.get(f, '') for f in IDENTITY if f != 'StartDate')
        if key in keys:
            raise ValueError('Duplicate Miscellaneous alternate key excluding StartDate (including GenderCode and EndDate)')
        keys.add(key)
        periods.append((rate_date(row['StartDate'], 'StartDate'),
            rate_date(row['EndDate'], 'EndDate') if row.get('EndDate') else date.max))
    periods.sort()
    if any(right[0] <= left[1] for left, right in zip(periods, periods[1:])):
        raise ValueError('Miscellaneous effective periods overlap; end dates are inclusive')


def validate_selection(records, rows):
    for name in {r['policy_name'] for r in records}:
        parents = [r for r in rows[P] if r['PolicyName'].casefold() == name.casefold()]
        rates = [r for r in rows[R] if r[P+'.PolicyName'].casefold() == name.casefold()]
        if len(parents)>1 or parents and parents[0]['PolicyName']!=name or any(r[P+'.PolicyName']!=name for r in rates):
            raise ValueError('Miscellaneous update requires its exact unambiguous existing policy')
        if not parents:
            if rates:raise ValueError('Orphan Miscellaneous baseline rate')
            if {r['entity']for r in records if r['policy_name']==name}!={P,R}:
                raise ValueError('Create requires a Miscellaneous parent and at least one rate')
            continue
        validate_parent(parents[0])
        validate_schedule(rates, parents[0])


def validate_pre_edit_selection(records, rows):
    """Require hard old ownership/identity, not complete old business inputs."""
    for name in {r['policy_name'] for r in records}:
        parents = [r for r in rows[P] if r['PolicyName'].casefold() == name.casefold()]
        rates = [r for r in rows[R] if r[P+'.PolicyName'].casefold() == name.casefold()]
        if len(parents)>1 or parents and parents[0]['PolicyName']!=name or any(r[P+'.PolicyName']!=name for r in rates):
            raise ValueError('Miscellaneous update requires its exact unambiguous existing policy')
        if not parents:
            if rates:raise ValueError('Orphan Miscellaneous baseline rate')
            if {r['entity']for r in records if r['policy_name']==name}!={P,R}:
                raise ValueError('Create requires a Miscellaneous parent and at least one rate')
            continue
        parent = parents[0]
        if parent.get('Status') not in {'DRAFT', 'VALID'} or not name.strip() or len(name) > 60:
            raise ValueError('Miscellaneous pre-edit lifecycle or identity scope is unqualified')
        if any(enabled(parent, f) for f in ('EnabledRoleFlag', 'EnabledLocationFlag', 'EnabledGenderFlag')):
            raise ValueError('Miscellaneous pre-edit determinants remain excluded')
        if any(parent.get(f, '') != '' for f in ('PolicyRoleCode', 'LocationTypeCode', 'ZoneTypeCode')):
            raise ValueError('Miscellaneous pre-edit determinant context remains excluded')
        currency = (parent.get('CurrencyOptionCode', ''), parent.get('CurrencyCode', ''))
        if currency != ('', '') and not (currency[0] == 'SINGLE' and currency[1].strip()):
            raise ValueError('Miscellaneous pre-edit currency context cannot be changed or inferred')
        keys, no_start = set(), set()
        for row in rates:
            validate_rate_scope(row, parent)
            key = tuple(row.get(f, '') for f in IDENTITY)
            other = tuple(row.get(f, '') for f in IDENTITY if f != 'StartDate')
            if key in keys or other in no_start:
                raise ValueError('Ambiguous Miscellaneous full or no-Start alternate key')
            keys.add(key); no_start.add(other)


def validate_change(entity, operation, before, after, baseline_rows):
    if operation not in {'create','update'}:
        raise ValueError('Miscellaneous requires a reviewed create or update operation')
    (validate_parent if entity == P else validate_rate)(after)
    allowed = PARENT_UPDATES if entity == P else RATE_UPDATES
    if operation=='create':
        if after.get('Status')!='DRAFT':raise ValueError('Miscellaneous create requires managed DRAFT status')
        if entity==P:
            if any(after.get(f)!='N'for f in ['EnabledRoleFlag','EnabledLocationFlag','EnabledGenderFlag']):
                raise ValueError('Miscellaneous create requires explicit managed No determinants')
            for field in ['EnabledEligibilityFlag',*CONTROLS,*(f+'Flag'for f in LIMITS)]:
                if after.get(field)not in {'Y','N'}:raise ValueError('Miscellaneous create requires explicit Yes/No for '+field)
            if after['EnabledEligibilityFlag']=='Y'and after.get('DaysBasedItemParentFlag')not in {'Y','N'}:
                raise ValueError('Miscellaneous create requires explicit DaysBasedItemParentFlag when eligibility is enabled')
        elif after.get('TypeOfRateCode')!=''or after.get('CurrencyCode')!='':
            raise ValueError('Miscellaneous ordinary create requires source-owned blank type and raw child currency')
    if operation=='update' and (set(before) != set(after) or {f for f in after if after[f] != before[f]} - allowed):
        raise ValueError('Miscellaneous keys, currency, dates, status and determinants require a separate qualified operation')
    if entity == P:
        controls = {'EligibilityDays': 'EnabledEligibilityFlag', 'DaysBasedItemParentFlag': 'EnabledEligibilityFlag',
            'PeriodMonth': 'YearlyLimitFlag', 'PeriodDay': 'YearlyLimitFlag',
            'WarningTolerance': 'PolicyViolationFlag', 'DispWarningToUserFlag': 'PolicyViolationFlag',
            'ErrorTolerance': 'PreventSubmissionFlag'}
        for field, control in controls.items():
            if after.get(field) != before.get(field) and after.get(field) not in {'', 'N'} and not enabled(after, control):
                raise ValueError('Miscellaneous '+field+' is not enterable while '+control+' is disabled; omitted updates preserve baseline values')


def verify_result(submitted, original_rows):
    """Overlay immutable-key patches, then validate every retained sibling rate."""
    names = {r['values'].get('PolicyName', r['values'].get(P+'.PolicyName')) for r in submitted}
    validate_pre_edit_selection([{'entity':r['entity'],'policy_name':r['values'].get('PolicyName',r['values'].get(P+'.PolicyName'))}for r in submitted], original_rows)
    parents = {r['PolicyName']: r for r in original_rows[P]}
    rates = {tuple(r.get(f, '') for f in IDENTITY): r for r in original_rows[R]}
    changed_rates = []
    seen = set()
    for record in submitted:
        row = record['values']
        parent = record['entity'] == P
        key = row['PolicyName'] if parent else tuple(row.get(f, '') for f in IDENTITY)
        target = parents if parent else rates
        if (record['entity'], key) in seen:
            raise ValueError('Miscellaneous resulting state requires one unambiguous immutable identity per submitted row')
        seen.add((record['entity'], key))
        exists=key in target
        before=target[key]if exists else dict.fromkeys(row,'')
        validate_change(record['entity'], 'update'if exists else'create', before, row, original_rows)
        if not parent:
            changed_rates.append((before, row))
        target[key] = row
    for before, row in changed_rates:
        parent = parents[row[P+'.PolicyName']]
        for field in LIMITS:
            if row.get(field) != before.get(field) and not enabled(parent, field+'Flag'):
                raise ValueError('Miscellaneous '+field+' is not enterable because its resulting parent limit is disabled')
        if row.get('ReimbursementPercentage') != before.get('ReimbursementPercentage') and parent['RateTypeCode'] == 'LIMIT':
            raise ValueError('Miscellaneous ReimbursementPercentage is not enterable in LIMIT mode')
    for name in names:
        validate_parent(parents[name])
        validate_schedule([r for r in rates.values() if r[P+'.PolicyName'] == name], parents[name])
    return {'profile': 'miscellaneous-no-determinants-source-v1', 'requires_live_qualification': True,
        'qualification': 'source_qualified_create_preparation_live_pending_existing_updates_scoped',
        'percentage_boundary': 'Finite nonnegative local input policy; no source-proven 100 percent cap or server acceptance claim',
        'import_approved': False}
