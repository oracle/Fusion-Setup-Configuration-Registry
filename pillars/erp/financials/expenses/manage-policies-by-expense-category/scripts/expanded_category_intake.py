"""Source-backed intake checks for categories awaiting FSM qualification.

Intake acceptance is not target lookup eligibility or import approval. The
existing runtime remains unavailable for these entities until its field-level
operation and resolver contracts are qualified.
"""
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT_BY_RATE = {
    'ORA_EXM_AIRFARE_POLICY_LINE': 'ORA_EXM_AIRFARE_POLICY',
    'ORA_EXM_CARRENTAL_POLICY_LINE': 'ORA_EXM_CARRENTAL_POLICY',
    'ORA_EXM_MILEAGE_LINE': 'ORA_EXM_MILEAGE_POLICY',
    'ORA_EXM_MISCELLANEOUS_POLICY_LINE': 'ORA_EXM_MISCELLANEOUS_POLICY',
    'ORA_EXM_PERDIEM_POLICY_LINE': 'ORA_EXM_PERDIEM_POLICY',
}
ENTITIES = frozenset(PARENT_BY_RATE) | frozenset(PARENT_BY_RATE.values())


def allowed_input(entity, field):
    catalog = json.loads((ROOT / 'references/intake-fields.json').read_text())
    return any(s['entity'] == entity and any(c.get('csv_field') == field
               and not c.get('workbook_only') for c in s['columns']) for s in catalog['sheets'])


def issues(records):
    """Check inputs, including the explicit UPPER mode's derived No/empty reset."""
    result = []
    parents = {(r['entity'], r['policy_name']): r['values'] for r in records if r['kind'] == 'policy'}
    for r in records:
        if r['entity'] not in ENTITIES:
            continue
        v = r['values']
        source = (r.get('sources') or [{}])[0]
        def error(field, message):
            result.append({'sheet': source.get('sheet', ''),
                           'cell': source.get('fields', {}).get(field, str(source.get('row', ''))),
                           'message': message})
        from per_diem_intake import supplied_issues
        supplied_issues(r['entity'],v,parents.get((PARENT_BY_RATE.get(r['entity']),r['policy_name']),{}),error)
        if 'PolicyName' in v and len(v['PolicyName']) > 60:
            error('PolicyName', 'Policy Name must not exceed the source-declared precision of 60 characters')
        if len(v.get('Description', '')) > 240:
            error('Description', 'Description must not exceed 240 characters')
        for field in ('DailyLimit', 'SingleInstanceLimit', 'MonthlyLimit', 'YearlyLimit', 'LifetimeLimit',
                      'Rate', 'BaseRate', 'ReimbursementPercentage', 'EligibilityDistance', 'MileageDeduction',
                      'WarningTolerance', 'ErrorTolerance', 'EligibilityDays', 'MaximumPassengers'):
            if field in v:
                if (field in {'WarningTolerance','ErrorTolerance'}
                        and v.get('PolicyEnforcementCode')=='UPPER' and v[field]==''):
                    continue  # Exact UI-disabled consequence, not a numeric input.
                try:
                    number = Decimal(v[field])
                    if not number.is_finite() or number < 0:
                        raise ValueError()
                except (InvalidOperation, ValueError):
                    error(field, field + ' must be a finite nonnegative number')
        if r['entity'] == 'ORA_EXM_AIRFARE_POLICY_LINE' and v.get('FlightClassCode') == 'FIRST':
            error('FlightClassCode', 'First is excluded by the flight-class lookup')
        if r['entity'] == 'ORA_EXM_CARRENTAL_POLICY' and all(f in v for f in ('WarningTolerance','ErrorTolerance')):
            try:
                warning, failure = Decimal(v['WarningTolerance']), Decimal(v['ErrorTolerance'])
                if warning.is_finite() and failure.is_finite() and warning >= failure:
                    error('ErrorTolerance', 'Car Rental Warning Tolerance must be strictly less than Error Tolerance whenever both are set, including when enforcement switches are No')
            except InvalidOperation:
                pass  # The numeric validation above reports malformed input.
        if r['entity'] == 'ORA_EXM_MILEAGE_POLICY':
            for control, fields in {
                'EnabledStdDeductionFlag': ('MileageDeduction',),
                'EnabledEligibilityFlag': ('EligibilityDistance',),
                'EnabledDeductCommuteFlag': ('CommuteDistanceRequiredFlag',),
                'EnabledMaxPassFlag': ('MaximumPassengers',),
                'EnabledAdditnlRatesFlag': ('AdditionalRatesListCode',),
                'EnabledPassengerFlag': ('PassengerRuleCode', 'CapturePassNamesFlag', 'CalcPassRateByDistFlag', 'EnabledMaxPassFlag', 'MaximumPassengers'),
            }.items():
                if v.get(control) == 'No':
                    for field in fields:
                        if field in v and v[field] != 'No':
                            error(field, field + ' is not enterable when ' + control + ' is No; blank updates preserve stored values')
        if r['entity'] == 'ORA_EXM_MISCELLANEOUS_POLICY':
            if v.get('EnabledEligibilityFlag') == 'No' and any(f in v for f in ('EligibilityDays', 'DaysBasedItemParentFlag')):
                error('EligibilityDays', 'Eligibility settings require Minimum Number of Days enabled')
            if v.get('YearlyLimitFlag') == 'No' and any(f in v for f in ('PeriodMonth', 'PeriodDay')):
                error('PeriodMonth', 'Annual reset fields require Yearly Limit enabled')
            if 'PeriodDay' in v and 'PeriodMonth' in v:
                import calendar
                try:
                    month, day = int(v['PeriodMonth']), int(v['PeriodDay'])
                    if not 1 <= month <= 12 or not 1 <= day <= calendar.monthrange(2001, month)[1]:
                        raise ValueError()
                except (ValueError, OverflowError):
                    error('PeriodDay', 'Supply a valid annual reset month/day (February 1–28)')
        if r['entity'] == 'ORA_EXM_MISCELLANEOUS_POLICY_LINE':
            p = parents.get((PARENT_BY_RATE[r['entity']], r['policy_name']), {})
            for amount in ('SingleInstanceLimit', 'DailyLimit', 'MonthlyLimit', 'YearlyLimit', 'LifetimeLimit'):
                if amount in v and p.get(amount + 'Flag') == 'No':
                    error(amount, amount + ' is not applicable because the parent limit is No')
            if p.get('RateTypeCode') == 'LIMIT' and 'ReimbursementPercentage' in v:
                error('ReimbursementPercentage', 'Rate limit mode does not accept Reimbursement Percentage')
        if r['entity'] == 'ORA_EXM_MILEAGE_LINE':
            p=parents.get((PARENT_BY_RATE[r['entity']],r['policy_name']),{})
            kind=v.get('TypeOfRateCode')
            if kind=='PASSENGER' and p.get('EnabledPassengerFlag')=='No':
                error('TypeOfRateCode','Passenger rates require the parent passenger rate option enabled')
            if kind=='ADDITIONAL' and p.get('EnabledAdditnlRatesFlag')=='No':
                error('TypeOfRateCode','Company-specific rates require the parent company-specific rate option enabled')
            if kind in {'MILEAGE','ADDITIONAL'} and 'PassengerThreshold' in v:
                error('PassengerThreshold','Passenger range applies only to passenger rate rows')
            if kind in {'MILEAGE','PASSENGER'} and 'AdditionalRateCode' in v:
                error('AdditionalRateCode','Company-specific code applies only to company-specific rate rows')
            if 'PassengerThreshold' in v:
                try:
                    threshold=int(v['PassengerThreshold'])
                    if threshold!=-1 and not 1<=threshold<=999:
                        raise ValueError()
                except ValueError:
                    error('PassengerThreshold','Passenger range upper limit must be positive and at most 999, or -1 for the source-defined upper-limit row')
    return result


def preflight_requirements(records):
    """Expose unresolved target checks per supplied row, never silently skip them."""
    catalog = json.loads((ROOT / 'references/intake-fields.json').read_text())
    checks = []
    for r in records:
        if r['entity'] not in ENTITIES:
            continue
        for sheet in catalog['sheets']:
            if sheet['entity'] != r['entity']:
                continue
            for field in sheet['columns']:
                name = field.get('csv_field')
                if name in r['values'] and field.get('lookup'):
                    if field['lookup'] == 'MONTH':
                        checks.append({'entity': r['entity'], 'policy_name': r['policy_name'],
                            'field': name, 'value': r['values'][name], 'lookup': 'MONTH',
                            'status': 'requires_local_calendar_validation',
                            'boundary': 'Validate the task numeric month domain and resulting month/day pair. This is not target lookup eligibility; observed serialized values do not prove all MONTH lookup codes or FSM writes.'})
                        continue
                    checks.append({'entity': r['entity'], 'policy_name': r['policy_name'],
                                   'field': name, 'value': r['values'][name], 'lookup': field['lookup'],
                                   'status': 'requires_target_verification',
                                   'boundary': 'Dropdown membership does not establish target eligibility. Context-qualified, operation-bound evidence required.'})
    return checks


def require_qualified_operations(records, contract=None):
    selected = sorted(entity for entity in {r['entity'] for r in records} & ENTITIES
        if not isinstance(contract,dict) or contract.get('entities',{}).get(entity,{}).get('ready') is not True)
    if selected:
        raise ValueError('FSM qualification pending for ' + ', '.join(selected)
                         + ': resolve field-level create/update and context-qualified lookup contracts before candidate construction; workbook intake is review-only')
