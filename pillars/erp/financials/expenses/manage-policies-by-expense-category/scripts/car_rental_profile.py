"""Car Rental resulting-state rules from its own service/entity contract.

Source-qualified SINGLE create preparation and existing updates remain subject
to target lookups, immutable native validation and later exact import approval.
"""
import hashlib
from pathlib import Path
from datetime import date
from accepted_meals_profile import decimal_value, rate_date

ROOT=Path(__file__).resolve().parents[1]
P='ORA_EXM_CARRENTAL_POLICY'
R=P+'_LINE'
SOURCE='CAR-RENTAL-SOURCE-CONTRACT'
CONTROLS=('PolicyViolationFlag','DispWarningToUserFlag','PreventSubmissionFlag')
PARENT_INPUTS={'PolicyName','Description','CurrencyCode','PolicyEnforcementCode',
    *CONTROLS,'WarningTolerance','ErrorTolerance'}
UPDATES=PARENT_INPUTS-{'PolicyName','CurrencyCode'}
IDENTITY=[P+'.PolicyName','CurrencyCode','EndDate','GeoLocName','RoleName',
    'StartDate','TypeOfRateCode','ZoneCode']
RATE_EMPTY=('CurrencyCode','GeoLocName','RoleName','TypeOfRateCode','ZoneCode',
    'InvalidCode','RawCity','RawCountry','RawCounty','RawState','RoleCode')


def validate_evidence(contract):
    proof=ROOT/'references/car-rental-source-contract.json'
    if contract.get('sources',{}).get(SOURCE,{}).get('sha256')!=hashlib.sha256(proof.read_bytes()).hexdigest():
        raise ValueError('Car Rental source contract changed; regenerate and review the runtime contract')
    shared=ROOT/'references/shared-fsm-create-serialization.json'
    if contract.get('sources',{}).get('SHARED-FSM-CREATE-SERIALIZATION',{}).get('sha256')!=hashlib.sha256(shared.read_bytes()).hexdigest():
        raise ValueError('Shared Car Rental create serialization changed; regenerate and review the runtime contract')


def validate_parent(row):
    if row.get('Status') not in {'DRAFT','VALID'}:
        raise ValueError('Car Rental policy status transition is outside the initial profile')
    if row.get('CurrencyOptionCode')!='SINGLE' or not row.get('CurrencyCode'):
        raise ValueError('Car Rental requires a resolved SINGLE parent currency')
    for field in ('EnabledRoleFlag','EnabledLocationFlag'):
        if row.get(field)!='N':
            raise ValueError('Car Rental requires resolved No for determinant '+field)
    for field in ('PolicyRoleCode','LocationTypeCode','ZoneTypeCode'):
        if row.get(field)!='':
            raise ValueError('Car Rental determinant setting is outside the initial profile: '+field)
    if row.get('PolicyEnforcementCode') not in {'UPPER','VIOLATION'}:
        raise ValueError('Supply an explicit Car Rental Policy Enforcement choice')
    if any(row.get(f) not in {'Y','N'} for f in CONTROLS):
        raise ValueError('Car Rental warning controls require resolved Yes/No values')
    if row['DispWarningToUserFlag']=='Y' and row['PolicyViolationFlag']!='Y':
        raise ValueError('Display Warning to User requires Policy Violation Warning = Yes')
    if row['PolicyEnforcementCode']=='UPPER' and any(row[f]!='N' for f in CONTROLS):
        raise ValueError('Reimburse upper limit requires warning, display and prevention controls = No')
    numbers={f:decimal_value(row.get(f,''),f) for f in ('WarningTolerance','ErrorTolerance')}
    for field,control in [('WarningTolerance','PolicyViolationFlag'),('ErrorTolerance','PreventSubmissionFlag')]:
        if row[control]=='Y' and numbers[field] is None:
            raise ValueError(field+' is required when '+control+' = Yes')
    # The EO predicates do not depend on the UI control values.
    if all(v is not None for v in numbers.values()) and numbers['WarningTolerance']>=numbers['ErrorTolerance']:
        raise ValueError('Car Rental Warning Tolerance must be strictly less than Error Tolerance')
    if not row.get('PolicyName','').strip() or len(row['PolicyName'])>60 or len(row.get('Description',''))>240:
        raise ValueError('Car Rental Policy Name allows 60 characters and Description 240')


def validate_rate(row):
    if row.get('Status') not in {'DRAFT','VALID'}:
        raise ValueError('Car Rental rate status is outside the initial profile')
    if any(row.get(f)!='' for f in RATE_EMPTY):
        raise ValueError('Car Rental reduced rates require blank determinant and child-currency coordinates')
    if decimal_value(row.get('DailyLimit',''),'DailyLimit') is None:
        raise ValueError('Car Rental Daily Limit is required by the input profile; Daily Limit must remain Yes')
    start=rate_date(row.get('StartDate',''),'StartDate')
    if row.get('EndDate') and rate_date(row['EndDate'],'EndDate')<start:
        raise ValueError('Car Rental EndDate must be on or after StartDate')


def validate_schedule(rates):
    if not rates:
        raise ValueError('Each selected Car Rental policy requires at least one compatible rate')
    periods=[]; keys=set()
    for row in rates:
        validate_rate(row)
        key=tuple(row.get(f,'') for f in IDENTITY if f!='StartDate')
        if key in keys:
            raise ValueError('Duplicate Car Rental alternate key excluding StartDate')
        keys.add(key)
        periods.append((rate_date(row['StartDate'],'StartDate'),
            rate_date(row['EndDate'],'EndDate') if row.get('EndDate') else date.max))
    periods.sort()
    if any(right[0]<=left[1] for left,right in zip(periods,periods[1:])):
        raise ValueError('Car Rental effective periods overlap; end dates are inclusive')


def validate_selection(records,rows):
    for name in {r['policy_name'] for r in records}:
        parents=[r for r in rows[P] if r['PolicyName'].casefold()==name.casefold()]
        rates=[r for r in rows[R] if r[P+'.PolicyName'].casefold()==name.casefold()]
        if len(parents)>1 or parents and parents[0]['PolicyName']!=name or any(r[P+'.PolicyName']!=name for r in rates):
            raise ValueError('Car Rental requires an exact unambiguous policy association')
        if parents:
            validate_parent(parents[0])
            for row in rates: validate_rate(row)
        elif rates:
            raise ValueError('Orphan Car Rental baseline rate')
        elif {r['entity'] for r in records if r['policy_name']==name}!={P,R}:
            raise ValueError('Create requires a Car Rental parent and at least one rate')


def validate_change(entity,operation,before,after,baseline_rows):
    (validate_parent if entity==P else validate_rate)(after)
    if operation=='update':
        allowed=UPDATES if entity==P else {'DailyLimit'}
        if {f for f in after if after[f]!=before[f]}-allowed:
            raise ValueError('Car Rental key, currency, dates, status and determinant changes require a separate qualified operation')
    if entity==P:
        for field,control in [('WarningTolerance','PolicyViolationFlag'),('ErrorTolerance','PreventSubmissionFlag')]:
            if after.get(field) and (operation=='create' or before.get(field)!=after[field]) and after[control]!='Y':
                raise ValueError(field+' is not enterable while '+control+' = No; omitted updates preserve baseline values')


def verify_result(submitted,original_rows):
    parents={r['PolicyName']:r for r in original_rows[P]}
    rates={tuple(r.get(f,'') for f in IDENTITY):r for r in original_rows[R]}
    for record in submitted:
        row=record['values']
        if record['entity']==P:
            validate_parent(row); parents[row['PolicyName']]=row
        else:
            validate_rate(row); rates[tuple(row.get(f,'') for f in IDENTITY)]=row
    names={r['values'].get('PolicyName',r['values'].get(P+'.PolicyName')) for r in submitted}
    for name in names:
        if name not in parents: raise ValueError('Car Rental rate requires an exact parent')
        validate_schedule([r for r in rates.values() if r[P+'.PolicyName']==name])
    return {'profile':'car-rental-single-currency-source-v1',
        'requires_live_qualification':True,'qualification':'source_qualified_create_preparation_live_pending_existing_updates_scoped',
        'import_approved':False}
