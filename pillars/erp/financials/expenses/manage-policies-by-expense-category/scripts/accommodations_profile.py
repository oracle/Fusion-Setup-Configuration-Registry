"""Accommodations authoring extension; target import reconciliation is pending.

Daily Limit is intrinsic to this category, not a parent CSV flag. Determinants
are excluded. Native approval, target evidence and reconciliation still apply.
"""
import hashlib
import json
from pathlib import Path

from accepted_meals_profile import decimal_value, rate_date
from reduced_rate_profile import validate_reduced_parent

P = 'ORA_EXM_ACCOM_POLICY'
R = P + '_LINE'
ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'ACCOMMODATIONS-AUTHORING'
IDENTITY = [P+'.PolicyName','CurrencyCode','EndDate','GeoLocName','RoleName',
    'SeasonEndDay','SeasonEndMonth','SeasonStartDay','SeasonStartMonth',
    'StartDate','TypeOfRateCode','ZoneCode','GenderCode']
CONTROLS = ('PolicyViolationFlag','DispWarningToUserFlag','PreventSubmissionFlag')
RATE_EMPTY = ('CurrencyCode','GeoLocName','RoleName','SeasonEndDay','SeasonEndMonth',
    'SeasonStartDay','SeasonStartMonth','TypeOfRateCode','ZoneCode','GenderCode',
    'InvalidCode','RawCity','RawCountry','RawCounty','RawState','RoleCode','GradeCode')


def validate_evidence(contract):
    source = contract.get('sources', {}).get(SOURCE, {})
    if source.get('sha256') != hashlib.sha256((ROOT/'references/accommodations-profile.json').read_bytes()).hexdigest():
        raise ValueError('Accommodations authoring evidence changed; regenerate and review its runtime contract')


def validate_parent(row):
    validate_reduced_parent(row)
    if row.get('Status') != 'DRAFT':
        raise ValueError('Accommodations supports DRAFT policies only')
    if row.get('PolicyEnforcementCode') not in {'UPPER','VIOLATION'}:
        raise ValueError('Supply an explicit Accommodations Policy Enforcement choice')
    if any(row.get(f) not in {'Y','N'} for f in CONTROLS):
        raise ValueError('Accommodations warning controls require resolved Yes/No values')
    if row['DispWarningToUserFlag'] == 'Y' and row['PolicyViolationFlag'] != 'Y':
        raise ValueError('Display Warning to User requires Policy Violation Warning = Yes')
    if row['PolicyEnforcementCode'] == 'UPPER' and any(row[f] != 'N' for f in CONTROLS):
        raise ValueError('Reimburse upper limit requires warning, display and prevention controls = No')
    for field, control in [('WarningTolerance','PolicyViolationFlag'),('ErrorTolerance','PreventSubmissionFlag')]:
        if decimal_value(row.get(field,''), field) is None and row[control] == 'Y':
            raise ValueError(field+' is required when '+control+' = Yes')
    if row.get('WarningTolerance') and row.get('ErrorTolerance'):
        if decimal_value(row['WarningTolerance'],'WarningTolerance') >= decimal_value(row['ErrorTolerance'],'ErrorTolerance'):
            raise ValueError('Warning Tolerance must be less than Error Tolerance when both are present')
    for field in ('RatesSourceCode','PolicyRoleCode','LocationTypeCode','ZoneTypeCode'):
        if row.get(field) != '':
            raise ValueError(field+': outside the supported Accommodations profile')
    if not row.get('PolicyName','').strip() or len(row['PolicyName']) > 80 or len(row.get('Description','')) > 240:
        raise ValueError('Supply Policy Name up to 80 and Description up to 240 characters')


def validate_rate(row):
    if row.get('Status') != 'DRAFT':
        raise ValueError('Accommodations supports DRAFT rates only')
    if any(row.get(f) != '' for f in RATE_EMPTY):
        raise ValueError('Accommodations rates do not support rate determinants or child currency inputs')
    if decimal_value(row.get('DailyLimit',''), 'DailyLimit') is None:
        raise ValueError('Accommodations Daily Limit is required')
    start = rate_date(row.get('StartDate',''), 'StartDate')
    if row.get('EndDate') and rate_date(row['EndDate'],'EndDate') < start:
        raise ValueError('EndDate must be on or after StartDate')


def validate_schedule(rates):
    if not rates:
        raise ValueError('Each selected Accommodations policy requires at least one compatible rate')
    periods, keys = [], set()
    from datetime import date
    for row in rates:
        validate_rate(row)
        key = tuple(row.get(f,'') for f in IDENTITY if f != 'StartDate')
        if key in keys:
            raise ValueError('Duplicate Accommodations rate alternate key excluding StartDate')
        keys.add(key)
        periods.append((rate_date(row['StartDate'],'StartDate'),
            rate_date(row['EndDate'],'EndDate') if row.get('EndDate') else date.max))
    periods.sort()
    if any(right[0] <= left[1] for left,right in zip(periods,periods[1:])):
        raise ValueError('Accommodations rate effective periods overlap; end dates are inclusive')


def validate_selection(records, rows):
    for name in {r['policy_name'] for r in records}:
        selected = [r for r in records if r['policy_name'] == name]
        parents = [r for r in rows[P] if r['PolicyName'].casefold() == name.casefold()]
        rates = [r for r in rows[R] if r[P+'.PolicyName'].casefold() == name.casefold()]
        if len(parents) > 1:
            raise ValueError('Accommodations requires an unambiguous parent identity')
        if parents:
            if parents[0]['PolicyName'] != name or any(r[P+'.PolicyName'] != name for r in rates):
                raise ValueError('Use the exact existing Accommodations Policy Name')
            validate_parent(parents[0])
            for rate in rates:
                validate_rate(rate)
        elif rates:
            raise ValueError('Orphan Accommodations rate association in baseline')
        elif {r['entity'] for r in selected} != {P,R}:
            raise ValueError('Create requires an Accommodations policy row and at least one Accommodations Rates row')


def validate_change(entity, operation, before, after, baseline_rows):
    (validate_parent if entity == P else validate_rate)(after)
    if operation == 'update':
        allowed = ({'Description','PolicyEnforcementCode',*CONTROLS,'WarningTolerance','ErrorTolerance'}
            if entity == P else {'DailyLimit'})
        if {f for f in after if before[f] != after[f]} - allowed:
            raise ValueError('Accommodations updates cannot change identity, dates, currency, status or hidden fields')
    if entity == P:
        for field,control in [('WarningTolerance','PolicyViolationFlag'),('ErrorTolerance','PreventSubmissionFlag')]:
            if after.get(field) and (operation == 'create' or before.get(field) != after[field]) and after[control] != 'Y':
                raise ValueError(field+' is not enterable while '+control+' = No; blank updates preserve stored tolerances')


def verify_result(submitted, original_rows):
    parents = {r['PolicyName']:r for r in original_rows[P]}
    rates = {tuple(r.get(f,'') for f in IDENTITY):r for r in original_rows[R]}
    for record in submitted:
        row = record['values']
        if record['entity'] == P:
            validate_parent(row)
            parents[row['PolicyName']] = row
        else:
            validate_rate(row)
            rates[tuple(row.get(f,'') for f in IDENTITY)] = row
    selected = {r['values'].get('PolicyName',r['values'].get(P+'.PolicyName')) for r in submitted}
    for name in selected:
        if name not in parents:
            raise ValueError('Selected Accommodations rate requires an exact parent')
        validate_schedule([r for r in rates.values() if r[P+'.PolicyName'] == name])
    return {'profile':'accommodations-single-currency-v1','qualification':'authoring_extension_live_pending',
        'requires_live_qualification':True,'import_approved':False}
