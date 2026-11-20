"""Entertainment authoring checks from reviewed UI/model evidence.

CSV acceptance and persistence remain live-pending. No activation, determinant
changes, implicit clearing, currency conversion or rate deletion is authorized.
"""
import hashlib
from pathlib import Path
from datetime import date
from accepted_meals_profile import decimal_value, rate_date

P = 'ORA_EXM_ENTERTAINMENT_POLICY'
R = P + '_LINE'
ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'ENTERTAINMENT-AUTHORING'
IDENTITY = [P+'.PolicyName','CurrencyCode','EndDate','StartDate',
            'TypeOfAttendeCode','TypeOfRateCode','RoleName']
LIMITS = {'SingleInstanceLimit':'SingleInstanceLimitFlag','DailyLimit':'DailyLimitFlag',
          'YearlyLimit':'YearlyLimitFlag'}
CONTROLS = ('PolicyViolationFlag','DispWarningToUserFlag','PreventSubmissionFlag')
BEHAVIORS = {'DISABLED','ENABLED','REQUIRED'}
INPUTS = {'PolicyName','Description','NumOfAttendeesFlag','NumOfAttendeesAmount',
    'NumOfAttendeesCurrCode','EmployeeAttendeeInfoFlag','EmpAttendeeAmtCode',
    'EmplReqAsAttendeeFlag','NonEmplAttendeeInfoFlag','NonempAttendeeTypeCode',
    'NonempAttendeeAmtCode','NonempJobTitleCode','NonempCreationFlag',
    'NonempRequiredAttendeeFlag','EnabledRateLimitFlag',*LIMITS.values(),
    'PeriodMonth','PeriodDay','CurrencyCode','PolicyEnforcementCode',*CONTROLS,
    'WarningTolerance','ErrorTolerance'}


def validate_evidence(contract):
    proof = ROOT/'references/entertainment-profile.json'
    if contract.get('sources',{}).get(SOURCE,{}).get('sha256') != hashlib.sha256(proof.read_bytes()).hexdigest():
        raise ValueError('Entertainment authoring evidence changed; regenerate and review the contract')


def yesno(row, field):
    if row.get(field) not in {'Y','N'}:
        raise ValueError(field+': supply an explicit or resolved Yes/No choice')
    return row[field] == 'Y'


def absent(row, fields, reason):
    if any(row.get(f) not in (('',None,'N') if f.endswith('Flag') else ('',None)) for f in fields):
        raise ValueError(reason+'; clearing stored values is not supported by blank cells')


def validate_parent(row):
    if row.get('Status') not in {'DRAFT','VALID'}:
        raise ValueError('Entertainment authoring covers editable Draft/Valid policies; activation is outside this profile')
    if not row.get('PolicyName','').strip() or len(row['PolicyName']) > 80 or len(row.get('Description','')) > 240:
        raise ValueError('Supply Policy Name up to 80 and Description up to 240 characters')
    absent(row, ('AttendeeTypesFlag','EmpRateDeterminantFlag','NonempRateDeterminantFlag','EnabledRoleFlag'),
           'Entertainment Rate Determinants are excluded')
    count = yesno(row,'NumOfAttendeesFlag')
    rate = yesno(row,'EnabledRateLimitFlag')
    emp = yesno(row,'EmployeeAttendeeInfoFlag')
    nonemp = yesno(row,'NonEmplAttendeeInfoFlag')
    if count:
        if rate or emp or nonemp:
            raise ValueError('Capture number of attendees disables attendee information and rate limits')
        if decimal_value(row.get('NumOfAttendeesAmount',''),'Attendee Count Threshold') is None or not row.get('NumOfAttendeesCurrCode'):
            raise ValueError('Attendee count mode requires threshold amount and currency')
    else:
        absent(row,('NumOfAttendeesAmount','NumOfAttendeesCurrCode'),'Threshold fields apply only to attendee count mode')
    for enabled, behaviors, flags in [
        (emp,('EmpAttendeeAmtCode',),('EmplReqAsAttendeeFlag',)),
        (nonemp,('NonempAttendeeTypeCode','NonempAttendeeAmtCode','NonempJobTitleCode'),
         ('NonempCreationFlag','NonempRequiredAttendeeFlag'))]:
        if enabled:
            for field in behaviors:
                if row.get(field) not in BEHAVIORS:
                    raise ValueError(field+': choose Hidden, Optional or Required')
            for field in flags:
                yesno(row,field)
        else:
            absent(row,behaviors+flags,'Dependent attendee controls require their display checkbox')
    if not rate:
        absent(row,(*LIMITS.values(),'PeriodMonth','PeriodDay','CurrencyCode',
                    'PolicyEnforcementCode',*CONTROLS,'WarningTolerance','ErrorTolerance'),
               'Rate definition and enforcement require Enable Rate Limit = Yes')
        return
    enabled = [yesno(row,field) for field in LIMITS.values()]
    if not any(enabled):
        raise ValueError('Enable at least one Entertainment rate limit')
    if row.get('CurrencyOptionCode') != 'SINGLE' or not row.get('CurrencyCode'):
        raise ValueError('Entertainment rates require Single currency and an explicit Currency Code')
    if row['YearlyLimitFlag'] == 'Y':
        month = row.get('PeriodMonth','')
        if month not in {f'{m:02d}' for m in range(1,13)}:
            raise ValueError('Select an annual Period Start Month (January through December)')
        day = row.get('PeriodDay','')
        maximum = (31,28,31,30,31,30,31,31,30,31,30,31)[int(month)-1]
        if not isinstance(day,str) or not day.isdigit() or not 1 <= int(day) <= maximum:
            raise ValueError('Period Start Day is invalid for the selected month; February permits 1–28')
    else:
        absent(row,('PeriodMonth','PeriodDay'),'Yearly reset period requires Yearly Limit = Yes')
    enforcement = row.get('PolicyEnforcementCode')
    if enforcement not in {'UPPER','VIOLATION'}:
        raise ValueError('Supply an explicit Entertainment Policy Enforcement choice')
    flags = {f:yesno(row,f) for f in CONTROLS}
    if enforcement == 'UPPER' and any(flags.values()):
        raise ValueError('Reimburse upper limit requires warning, display and prevention controls = No')
    if enforcement == 'VIOLATION' and not (flags['PolicyViolationFlag'] or flags['PreventSubmissionFlag']):
        raise ValueError('Violation enforcement requires Policy Violation Warning or Prevent Report Submission = Yes')
    if flags['DispWarningToUserFlag'] and not flags['PolicyViolationFlag']:
        raise ValueError('Display Warning to User requires Policy Violation Warning = Yes')
    for amount, control in [('WarningTolerance','PolicyViolationFlag'),('ErrorTolerance','PreventSubmissionFlag')]:
        value = decimal_value(row.get(amount,''),amount)
        if flags[control] and value is None:
            raise ValueError(amount+' is required by '+control)
    if row.get('WarningTolerance') and row.get('ErrorTolerance'):
        if decimal_value(row['WarningTolerance'],'WarningTolerance') >= decimal_value(row['ErrorTolerance'],'ErrorTolerance'):
            raise ValueError('Warning Tolerance must be less than Error Tolerance')


def validate_rate(row, parent=None):
    if row.get('Status') not in {'DRAFT','VALID'}:
        raise ValueError('Entertainment authoring covers Draft/Valid rates only')
    absent(row,('CurrencyCode','TypeOfAttendeCode','TypeOfRateCode','RoleName','InvalidCode'),
           'Entertainment child currency and Rate Determinants are excluded')
    start = rate_date(row.get('StartDate',''),'StartDate')
    if row.get('EndDate') and rate_date(row['EndDate'],'EndDate') < start:
        raise ValueError('EndDate must be on or after StartDate')
    for amount,control in LIMITS.items():
        value = decimal_value(row.get(amount,''),amount)
        if parent is not None:
            if parent.get('EnabledRateLimitFlag') != 'Y':
                raise ValueError('Entertainment rate requires Enable Rate Limit = Yes')
            enabled = yesno(parent,control)
            if enabled != (value is not None):
                raise ValueError(amount+(' is required by the enabled parent limit' if enabled else ' must be blank when the parent limit is disabled'))


def validate_selection(records, rows):
    for name in {r['policy_name'] for r in records}:
        parents = [r for r in rows[P] if r['PolicyName'].casefold() == name.casefold()]
        rates = [r for r in rows[R] if r[P+'.PolicyName'].casefold() == name.casefold()]
        if len(parents) > 1 or any(r['PolicyName'] != name for r in parents) or any(r[P+'.PolicyName'] != name for r in rates):
            raise ValueError('Use one exact, unambiguous Entertainment Policy Name')
        if parents:
            validate_parent(parents[0])
            for row in rates: validate_rate(row,parents[0])
        elif rates:
            raise ValueError('Orphan Entertainment rate association')
        elif not any(r['entity'] == P and r['policy_name'] == name for r in records):
            raise ValueError('New Entertainment rates require their parent policy row')


def validate_change(entity, operation, before, after, baseline_rows):
    (validate_parent if entity == P else validate_rate)(after)
    allowed = INPUTS-{'PolicyName','CurrencyCode','NumOfAttendeesCurrCode'} if entity == P else set(LIMITS)
    if operation == 'update' and {f for f in after if before[f] != after[f]} - allowed:
        raise ValueError('Entertainment updates preserve identity, currency, dates, status and hidden fields')
    if entity == P:
        for amount,control in [('WarningTolerance','PolicyViolationFlag'),('ErrorTolerance','PreventSubmissionFlag')]:
            if after.get(amount) and (operation == 'create' or before.get(amount) != after[amount]) and after.get(control) != 'Y':
                raise ValueError(amount+' is not enterable while '+control+' = No')


def verify_result(submitted, original_rows):
    parents = {r['PolicyName']:r for r in original_rows[P]}
    rates = {tuple(r.get(f,'') for f in IDENTITY):r for r in original_rows[R]}
    for record in submitted:
        row = record['values']
        if record['entity'] == P: parents[row['PolicyName']] = row
        else: rates[tuple(row.get(f,'') for f in IDENTITY)] = row
    for name in {r['values'].get('PolicyName',r['values'].get(P+'.PolicyName')) for r in submitted}:
        if name not in parents: raise ValueError('Entertainment rate requires an exact parent')
        parent = parents[name]; validate_parent(parent)
        selected = [r for r in rates.values() if r[P+'.PolicyName'] == name]
        if parent['EnabledRateLimitFlag'] == 'Y' and not selected:
            raise ValueError('Entertainment rate limits require at least one compatible rate')
        periods = []
        for row in selected:
            validate_rate(row,parent)
            periods.append((rate_date(row['StartDate'],'StartDate'),rate_date(row['EndDate'],'EndDate') if row.get('EndDate') else date.max))
        periods.sort()
        if any(b[0] <= a[1] for a,b in zip(periods,periods[1:])):
            raise ValueError('Entertainment rate periods overlap; end dates are inclusive')
    return {'profile':'entertainment-no-determinants-v1','qualification':'authoring_extension_live_pending',
            'requires_live_qualification':True,'import_approved':False}
