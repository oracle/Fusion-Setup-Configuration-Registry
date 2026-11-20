"""Per Diem's own existing-row, no-determinant state and value ownership.

UI synchronization is not an import side effect. Existing percentage values
are explicit candidate updates; missing rows/keys/deletions never acquire IDs.
"""
from decimal import Decimal, InvalidOperation
from pathlib import Path
import hashlib

from accepted_meals_profile import rate_date
from per_diem_intake import MEAL_FIELDS, DEDUCTIONS, COMPONENT_RATES, MEAL_TIMES, ACCOM_TIMES

ROOT = Path(__file__).resolve().parents[1]
P = 'ORA_EXM_PERDIEM_POLICY'
R = P + '_LINE'
V = 'ORA_EXM_PER_DIEM_POLICY_VALUE'
ENTITIES = {P, R, V}
SOURCE = 'PER-DIEM-SOURCE-CONTRACT'
REF = P + '.PolicyName'
IDENTITY = [REF, 'AccommodationTypeCode', 'CurrencyCode', 'EndDate', 'GeoLocName',
    'LineHours', 'LineMinutes', 'RoleThreshold', 'RoleThresholdCode', 'SeasonEndDay',
    'SeasonEndMonth', 'SeasonStartDay', 'SeasonStartMonth', 'StartDate', 'TripExceedDays',
    'TypeOfLineCode', 'ZoneCode']
VALUE_IDENTITY = [REF, 'DeterminantCode', 'DeterminantValue', 'LineHours', 'LineMinutes', 'TypeOfLineCode']
DETERMINANTS = {'EnabledLocationFlag', 'EnabledSeasonRateFlag', 'EnabledAccomTypeFlag',
    'EnabledRoleFlag', 'EnabledLongTermFlag', 'EnabledWeekendHolidFlag', 'SpecificFirstLastDayFlag'}
INCLUDES = {'RateIncludeMealsFlag', 'RateIncludeAccomFlag', 'RateIncludeOtherFlag'}
FLAGS = INCLUDES | {'MealDeductionFlag', 'AccomDeductionFlag', 'AllowRateConversionFlag',
    'WithinEmployeeCityFlag', 'MealInclIncidentalFlag', 'MinTripDuratFlag', 'AccomFreeOnlyFlag',
    'AccomReqMealsEligibFlag', 'AccomMinTripDuratFlag', 'TimeAllowSameDayFlag'}
AMOUNTS = DEDUCTIONS | COMPONENT_RATES | {'BaseRate', 'AccommodationDeduction'}
MEAL_CODES = {'DAILY': ('DAILY',), 'TYPE': ('BREAKFAST', 'LUNCH', 'DINNER'),
    'NUMBER': ('ONE_MEAL', 'TWO_MEALS', 'THREE_MEALS')}
MEAL_RATES = {'DAILY': ('BaseRate',),
    'TYPE': ('MealsBreakfastRate', 'MealsLunchRate', 'MealsDinnerRate'),
    'NUMBER': ('MealsOneMealRate', 'MealsTwoMealsRate', 'MealsThreeMealsRate')}
LINE_EMPTY = {'AccommodationTypeCode', 'CurrencyCode', 'GeoLocName', 'RoleThreshold',
    'RoleThresholdCode', 'SeasonEndDay', 'SeasonEndMonth', 'SeasonStartDay', 'SeasonStartMonth',
    'TripExceedDays', 'ZoneCode', 'RawCity', 'RawCountry', 'RawCounty', 'RawState',
    'LowerRoleThreshold', 'LowerTripExceedDays', 'InvalidCode'}
STRUCTURAL = {'PolicyName', 'Status', 'RateFormulaMethodCode', 'CurrencyCode', 'CurrencyOptionCode'}


def validate_evidence(contract):
    path = ROOT/'references/per-diem-source-contract.json'
    if contract.get('sources', {}).get(SOURCE, {}).get('sha256') != hashlib.sha256(path.read_bytes()).hexdigest():
        raise ValueError('Per Diem source contract changed; regenerate the runtime contract')
    path=ROOT/'references/per-diem-create-serialization.json'
    if contract.get('sources',{}).get('PER-DIEM-CREATE-SERIALIZATION',{}).get('sha256')!=hashlib.sha256(path.read_bytes()).hexdigest():
        raise ValueError('Per Diem create serialization changed; regenerate and review the runtime contract')


def key(row, fields):
    return tuple(row.get(f, '') for f in fields)


def number(value, field, required=False):
    if value in ('', None):
        if required:
            raise ValueError('Per Diem '+field+' is required in the selected calculation branch')
        return None
    try:
        result = Decimal(value)
        if not result.is_finite() or result < 0:
            raise ValueError()
        return result
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError('Per Diem '+field+' must be finite and nonnegative') from None


def integer(value, field, maximum=None, required=False):
    result = number(value, field, required)
    if result is not None and (result != result.to_integral_value() or maximum is not None and result > maximum):
        raise ValueError('Per Diem '+field+' requires an integer'+(' no greater than '+str(maximum) if maximum is not None else ''))
    return int(result) if result is not None else None


def require_choice(row, field, allowed):
    if row.get(field) not in allowed:
        raise ValueError('Per Diem '+field+' requires an explicit supported choice: '+', '.join(sorted(allowed)))


def validate_parent(row):
    if not row.get('PolicyName', '').strip() or len(row['PolicyName']) > 60 or len(row.get('Description', '')) > 240:
        raise ValueError('Per Diem Policy Name allows 60 characters and Description 240')
    require_choice(row, 'Status', {'DRAFT', 'VALID'})
    if row.get('PerdiemPolicyType') != 'GENERIC':
        raise ValueError('Per Diem initial profile requires its existing GENERIC policy type')
    if row.get('CurrencyOptionCode') != 'SINGLE' or not row.get('CurrencyCode'):
        raise ValueError('Per Diem initial profile requires resolved SINGLE parent currency')
    for field in DETERMINANTS:
        if row.get(field) != 'N':
            raise ValueError('Per Diem requires resolved No for excluded determinant '+field)
    formula = row.get('RateFormulaMethodCode')
    require_choice(row, 'RateFormulaMethodCode', {'SINGLE', 'SUMUP', 'TIME_SINGLE', 'TIME_SUMUP'})
    if row.get('TimeBasedRateModelFlag') != ('Y' if formula.startswith('TIME') else 'N'):
        raise ValueError('Per Diem TimeBasedRateModelFlag must agree with the source-derived formula')
    for field in FLAGS:
        # Inactive controls can be null in the exported existing state. No is
        # never inferred from that null; active branches require exact flags.
        if row.get(field, '') not in {'', 'Y', 'N'}:
            raise ValueError('Invalid Per Diem Yes/No control '+field)
    if row.get('MealInclIncidentalFlag') == 'Y' and row.get('RateIncludeOtherFlag') == 'Y':
        raise ValueError('Per Diem Other cannot be selected with Meals Include Incidentals')
    if formula == 'SINGLE':
        require_choice(row, 'RateMultiplierCode', {'DAYS', 'NIGHTS'})
        # Single.jsff95-109 renders this selector unconditionally in SINGLE.
        # Bean MCMS0/2 exclude percentage/spreadsheet for !isAdfDi and firstlastN.
        require_choice(row, 'MealsCalcMethodCode', {'RATE'})
    if formula in {'SUMUP', 'TIME_SUMUP'} and row.get('RateIncludeMealsFlag') == 'Y':
        require_choice(row, 'MealRateTypeCode', set(MEAL_RATES))
    if (formula == 'SUMUP' and row.get('RateIncludeMealsFlag') == 'Y'
            and row.get('MealRateTypeCode') in {'TYPE', 'NUMBER'}):
        require_choice(row, 'MealsCalcMethodCode', {'RATE'})
    if formula.startswith('TIME'):
        require_choice(row, 'TimePeriodCode', {'MIDNIGHT', 'START'})
        # Bean getLovTCM0/2 requires isAdfDi; RATE is its only non-ADFDi choice.
        require_choice(row, 'TimeCalcMethodCode', {'RATE'})
        if row.get('TimeAllowSameDayFlag') == 'Y':
            require_choice(row, 'TimeSameDayRuleCode', {'LESS', 'NOOVERNIGHT'})
    if row.get('MealDeductionFlag') == 'Y':
        if row.get('RateIncludeMealsFlag') != 'Y':
            raise ValueError('Per Diem meal deduction requires Meals included')
        require_choice(row, 'MealsDeductionCode', set(MEAL_FIELDS))
        require_choice(row, 'MealsDeductCalcMethCode', {'PERCENTAGE', 'RATE'})
        if row.get('MealsDeductCalcMethCode') == 'RATE' and row.get('RoleCalcMethod') == 'RATE':
            raise ValueError('Per Diem actual meal deduction is filtered out by retained RoleCalcMethod RATE')
        if formula == 'SUMUP' and row.get('MealRateTypeCode') not in {'', 'DAILY'}:
            raise ValueError('Per Diem SUMUP meal deductions require the DAILY meals branch')
    if row.get('AccomDeductionFlag') == 'Y':
        if row.get('RateIncludeAccomFlag') != 'Y' or formula not in {'SINGLE', 'TIME_SINGLE'}:
            raise ValueError('Per Diem accommodation deduction requires a single formula with Accommodations included')
        require_choice(row, 'AccomDeductCalcMethCode', {'PERCENTAGE', 'RATE'})
        if row.get('AccomDeductCalcMethCode') == 'RATE' and row.get('RoleCalcMethod') == 'RATE':
            raise ValueError('Per Diem actual accommodation deduction is filtered out by retained RoleCalcMethod RATE')
    for field in MEAL_TIMES | ACCOM_TIMES:
        integer(row.get(field), field, 24 if field.endswith('Hour') else 60)
    for prefix in ('BreakfastElig', 'LunchElig', 'DinnerElig', 'AccomEligib'):
        fields = [prefix+edge+unit for edge in ('Start', 'End') for unit in ('Hour', 'Minute')]
        if any(row.get(f, '') != '' for f in fields):
            start = tuple(int(row.get(prefix+'Start'+u) or 0) for u in ('Hour', 'Minute'))
            end = tuple(int(row.get(prefix+'End'+u) or 0) for u in ('Hour', 'Minute'))
            # EO validateMealsEligibility/validateAccomEligibility applies
            # whenever any coordinate exists, including inactive controls.
            if end <= start:
                raise ValueError('Per Diem '+prefix+' eligibility end must be strictly after start')
    from per_diem_applicability import validate_durations
    validate_durations(row, integer)
    night = number(row.get('AccomMinNightHoursStay'), 'AccomMinNightHoursStay')
    if night is not None and night > 24:
        raise ValueError('Per Diem accommodation minimum-night hours must not exceed 24')
    number(row.get('MinimumReimbursement'), 'MinimumReimbursement')
    if row.get('RateIncludeOtherFlag') == 'Y' and formula in {'SUMUP', 'TIME_SUMUP'}:
        if formula == 'TIME_SUMUP':
            require_choice(row, 'OthersCalcMethodCode', {'RATE'})
        require_choice(row, 'OthersEligibCriteriaCode', {'NONE', 'MEALS', 'ACCOM', 'MEALS_ACCOM'})
        needed = {'MEALS': ('RateIncludeMealsFlag',), 'ACCOM': ('RateIncludeAccomFlag',),
            'MEALS_ACCOM': ('RateIncludeMealsFlag', 'RateIncludeAccomFlag')}.get(row['OthersEligibCriteriaCode'], ())
        if any(row.get(f) != 'Y' for f in needed):
            raise ValueError('Per Diem Other eligibility depends on selected components')


def validate_rate(row, *, business_complete=True):
    require_choice(row, 'Status', {'DRAFT', 'VALID'})
    if any(row.get(f, '') != '' for f in LINE_EMPTY):
        raise ValueError('Per Diem no-determinant line requires blank location, role, season, trip and child-currency coordinates')
    require_choice(row, 'TypeOfLineCode', {'ANCHOR', 'STANDARD', 'SAME', 'OTHER_STANDARD'})
    if business_complete:
        for field in AMOUNTS:
            number(row.get(field), field)
    start = rate_date(row.get('StartDate', ''), 'StartDate')
    if row.get('EndDate') and rate_date(row['EndDate'], 'EndDate') < start:
        raise ValueError('Per Diem EndDate must be on or after StartDate')
    if row['TypeOfLineCode'] == 'ANCHOR':
        if any(row.get(f, '') != '' for f in ('LineHours', 'LineMinutes', 'LowerLineHours', 'LowerLineMinutes')):
            raise ValueError('Per Diem ANCHOR is not a time-range line')
    else:
        hours = integer(row.get('LineHours'), 'LineHours', 999, True)
        if hours > 24 and hours != 999:
            raise ValueError('Per Diem range hours must be 0 through 24 or the existing 999 upper sentinel')
        integer(row.get('LineMinutes'), 'LineMinutes', 60)
        integer(row.get('LowerLineHours'), 'LowerLineHours', 999, True)
        integer(row.get('LowerLineMinutes'), 'LowerLineMinutes', 60)


def validate_value(row):
    require_choice(row, 'TypeOfLineCode', {'MEAL_DEDUCTION', 'ACCOM_DEDUCTION', 'MEALS', 'STANDARD', 'SAME', 'OTHER_STANDARD'})
    number(row.get('LineValue'), 'LineValue')
    if row['TypeOfLineCode'] in {'STANDARD', 'SAME', 'OTHER_STANDARD'}:
        if row.get('DeterminantCode', '') or row.get('DeterminantValue', ''):
            raise ValueError('Per Diem time values cannot acquire role/determinant coordinates')
        integer(row.get('LineHours'), 'LineHours', 999, True)
        integer(row.get('LineMinutes'), 'LineMinutes', 60)
        integer(row.get('LowerLineHours'), 'LowerLineHours', 999, True)
        integer(row.get('LowerLineMinutes'), 'LowerLineMinutes', 60)
    elif any(row.get(f, '') != '' for f in ('DeterminantValue', 'LineHours', 'LineMinutes',
            'LowerDeterminantValue', 'LowerLineHours', 'LowerLineMinutes')):
        raise ValueError('Per Diem component/deduction values require their exact code-only identity')


def existing_identity_context(values, rows, *, create_allowed=False):
    """Retain an exact existing subtype; never default STANDARD or ANCHOR."""
    if not values.get(REF) or not values.get('StartDate'):
        raise ValueError('Per Diem rate requires explicit Policy Name and Start Date')
    candidates = [r for r in rows if all(r.get(f, '') == values.get(f, '')
        for f in IDENTITY if f != 'TypeOfLineCode' or f in values)]
    if not candidates and create_allowed:
        if values.get('TypeOfLineCode')not in {'ANCHOR','STANDARD','SAME','OTHER_STANDARD'}:
            raise ValueError('Per Diem create requires explicit Rate Component; no ANCHOR/STANDARD default')
        return {'TypeOfLineCode':values['TypeOfLineCode']}
    if len(candidates) != 1:
        raise ValueError('Per Diem rate needs one exact existing full-key context; no subtype/default or new association is inferred')
    validate_rate(candidates[0], business_complete=False)
    return {'TypeOfLineCode': candidates[0]['TypeOfLineCode']}


def unique_rows(rows, fields, label):
    if len({key(r, fields) for r in rows}) != len(rows):
        raise ValueError('Ambiguous Per Diem '+label+' alternate key')


def range_rows(rows, field):
    if not rows:
        raise ValueError('Per Diem selected time calculation requires existing '+field+' range rows')
    ordered = sorted(rows, key=lambda r: (integer(r.get('LineHours'), 'LineHours', 999, True),
        integer(r.get('LineMinutes'), 'LineMinutes', 60) or 0))
    previous = (0, 0)
    for row in ordered:
        upper = (int(row['LineHours']), int(row.get('LineMinutes') or 0))
        lower = (int(row['LowerLineHours']), int(row.get('LowerLineMinutes') or 0))
        if lower != previous or upper <= lower:
            raise ValueError('Per Diem time ranges require exact source-synchronized increasing lower/upper thresholds')
        number(row.get(field), field, True)
        previous = upper


def expected_inline_values(parent, head):
    """Source UI synchronization relationships, not an FSM generated-row claim."""
    expected = {}
    if parent.get('MealDeductionFlag') == 'Y' and parent.get('MealsDeductCalcMethCode') == 'PERCENTAGE':
        mode = parent['MealsDeductionCode']
        expected.update({('MEAL_DEDUCTION', code): head.get(field, '')
            for code, field in zip(MEAL_CODES[mode], MEAL_FIELDS[mode])})
    if parent.get('AccomDeductionFlag') == 'Y' and parent.get('AccomDeductCalcMethCode') == 'PERCENTAGE':
        expected['ACCOM_DEDUCTION', 'ACCOM_DEDUCTION'] = head.get('AccommodationDeduction', '')
    # doSyncMeals explicitly removes MEALS values for non-ADFDi SUMUP.
    if (parent.get('RateIncludeMealsFlag') == 'Y' and parent.get('RateFormulaMethodCode') != 'SUMUP' and parent.get('MealRateTypeCode') in {'TYPE', 'NUMBER'}
            and parent.get('MealsCalcMethodCode') == 'PERCENTAGE'):
        mode = parent['MealRateTypeCode']
        expected.update({('MEALS', code): head.get(field, '')
            for code, field in zip(MEAL_CODES[mode], MEAL_RATES[mode])})
    return expected


def active_line_kinds(parent):
    kinds = {'ANCHOR'}
    formula = parent.get('RateFormulaMethodCode', '')
    if formula.startswith('TIME'):
        kinds.add('STANDARD')
        if parent.get('TimeAllowSameDayFlag') == 'Y':
            kinds.add('SAME')
        if formula == 'TIME_SUMUP' and parent.get('RateIncludeOtherFlag') == 'Y':
            kinds.add('OTHER_STANDARD')
    return kinds


def validate_policy(parent, rates, values, *, verify_inline=True):
    validate_parent(parent)
    unique_rows(rates, IDENTITY, 'line')
    unique_rows(rates, [f for f in IDENTITY if f != 'StartDate'], 'line excluding StartDate')
    unique_rows(values, VALUE_IDENTITY, 'value')
    # Retained inactive rows are preserved; they do not acquire write authority.
    # Source-dependent old rows are not deleted merely to simplify the profile.
    for row in rates:
        if row.get('TypeOfLineCode') in active_line_kinds(parent):
            validate_rate(row)
    heads = [r for r in rates if r['TypeOfLineCode'] == 'ANCHOR']
    if len(heads) != 1:
        raise ValueError('Per Diem requires one exact existing ANCHOR; creating/replacing head rows is unqualified')
    head = heads[0]
    formula = parent['RateFormulaMethodCode']
    if formula == 'SINGLE':
        number(head.get('BaseRate'), 'BaseRate', True)
    if formula == 'SUMUP':
        if parent.get('RateIncludeMealsFlag') == 'Y':
            fields = MEAL_RATES[parent['MealRateTypeCode']]
            if all(head.get(f, '') == '' for f in fields):
                raise ValueError('Per Diem selected meals component requires at least one amount, including zero')
        if parent.get('RateIncludeAccomFlag') == 'Y':
            number(head.get('AccomNightRate'), 'AccomNightRate', True)
        if parent.get('RateIncludeOtherFlag') == 'Y':
            number(head.get('OthersStandardRate'), 'OthersStandardRate', True)
    if formula.startswith('TIME'):
        percent = parent['TimeCalcMethodCode'] == 'PERCENTAGE'
        source, amount = (values, 'LineValue') if percent else (rates, 'BaseRate')
        range_rows([r for r in source if r['TypeOfLineCode'] == 'STANDARD'], amount)
        if formula == 'TIME_SUMUP' and parent.get('RateIncludeOtherFlag') == 'Y':
            source, amount = (values, 'LineValue') if parent.get('OthersCalcMethodCode') == 'PERCENTAGE' else (rates, 'BaseRate')
            other = [r for r in source if r['TypeOfLineCode'] == 'OTHER_STANDARD']
            # AM completeness only requires OtherStandard for START; retain the
            # precise predicate rather than strengthening MIDNIGHT behavior.
            if parent['TimePeriodCode'] == 'START' or other:
                range_rows(other, amount)
        if parent.get('TimeAllowSameDayFlag') == 'Y':
            source, amount = (values, 'LineValue') if percent else (rates, 'BaseRate')
            same = [r for r in source if r['TypeOfLineCode'] == 'SAME']
            if same:
                range_rows(same, amount)
        if formula == 'TIME_SUMUP' and parent.get('RateIncludeAccomFlag') == 'Y':
            number(head.get('AccomNightRate'), 'AccomNightRate', True)
    if parent.get('MealDeductionFlag') == 'Y':
        if all(head.get(f, '') == '' for f in MEAL_FIELDS[parent['MealsDeductionCode']]):
            raise ValueError('Per Diem meal deduction requires at least one amount in its selected type')
    if parent.get('AccomDeductionFlag') == 'Y':
        number(head.get('AccommodationDeduction'), 'AccommodationDeduction', True)
    expected = expected_inline_values(parent, head)
    active_value_kinds = {coordinate[0] for coordinate in expected}
    inline = [r for r in values if r.get('TypeOfLineCode') in active_value_kinds]
    for row in inline:
        validate_value(row)
    actual = {(r['TypeOfLineCode'], r.get('DeterminantCode', '')): r for r in inline}
    if len(actual) != len(inline) or set(actual) != set(expected):
        raise ValueError('Per Diem percentage value inventory requires existing exact rows; missing/new/deleted synchronization rows are unqualified')
    if verify_inline:
        for coordinate, value in expected.items():
            if number(actual[coordinate].get('LineValue'), 'LineValue') != number(value, 'inline amount'):
                raise ValueError('Per Diem percentage value must match its source ANCHOR amount')
    return expected, actual


def policy_rows(rows, name, entity):
    return [r for r in rows.get(entity, []) if r.get('PolicyName' if entity == P else REF, '').casefold() == name.casefold()]


def validate_selection(records, rows):
    for name in {r['policy_name'] for r in records}:
        parents = policy_rows(rows, name, P)
        if not parents:
            if policy_rows(rows,name,R)or policy_rows(rows,name,V):
                raise ValueError('Orphan Per Diem baseline lines/values cannot acquire a new parent')
            if not {P,R}<={r['entity']for r in records if r['policy_name']==name}:
                raise ValueError('Per Diem create requires a new parent and explicit ANCHOR/rate group')
            continue
        if len(parents) != 1 or parents[0]['PolicyName'] != name:
            raise ValueError('Per Diem update requires its exact unambiguous existing policy')
        rates, values = policy_rows(rows, name, R), policy_rows(rows, name, V)
        if any(r[REF] != name for r in rates + values):
            raise ValueError('Case-only Per Diem association collision')
        # Selection establishes ownership/identity, not business completeness.
        # An existing DRAFT with an empty amount may be completed by this very
        # workbook; all required values are checked after the merged changes.
        unique_rows(rates, IDENTITY, 'line')
        unique_rows(rates, [f for f in IDENTITY if f != 'StartDate'], 'line excluding StartDate')
        unique_rows(values, VALUE_IDENTITY, 'value')
        if len([r for r in rates if r.get('TypeOfLineCode') == 'ANCHOR']) != 1:
            raise ValueError('Per Diem requires one exact existing ANCHOR; creation is unqualified')


def validate_pre_edit_selection(records, rows):
    """Hard existing identities/scope first; all business rules after overlay."""
    validate_selection(records, rows)
    for name in {r['policy_name'] for r in records}:
        parents=policy_rows(rows,name,P)
        if not parents:continue
        parent=parents[0]
        formula = parent.get('RateFormulaMethodCode', '')
        if (parent.get('Status') not in {'DRAFT', 'VALID'} or not name.strip() or len(name) > 60
                or parent.get('PerdiemPolicyType') != 'GENERIC'
                or parent.get('CurrencyOptionCode') != 'SINGLE' or not parent.get('CurrencyCode')
                or formula not in {'SINGLE', 'SUMUP', 'TIME_SINGLE', 'TIME_SUMUP'}
                or parent.get('TimeBasedRateModelFlag') != ('Y' if formula.startswith('TIME') else 'N')):
            raise ValueError('Per Diem pre-edit lifecycle, identity, formula or currency scope is unqualified')
        if any(parent.get(f) != 'N' for f in DETERMINANTS):
            raise ValueError('Per Diem pre-edit determinants remain excluded')
        for row in policy_rows(rows, name, R):
            if row.get('TypeOfLineCode') in active_line_kinds(parent):
                validate_rate(row, business_complete=False)


def validate_change(entity, operation, before, after, baseline_rows):
    if operation=='create':
        name=after.get('PolicyName'if entity==P else REF)
        if policy_rows(baseline_rows,name,P):
            raise ValueError('Per Diem cannot create-on-miss for an existing policy without separate existing-range/value synchronization qualification')
        if entity==P:
            from per_diem_create import validate_new_parent
            validate_new_parent(after)
            from per_diem_applicability import validate_changed_fields
            validate_changed_fields(P,before,after,after)
        elif entity==R:
            validate_rate(after)
            if after.get('Status')!=('VALID'if after.get('TypeOfLineCode')=='ANCHOR'else'DRAFT'):
                raise ValueError('Per Diem new line status must follow reviewed ANCHOR VALID/other DRAFT derivation')
        elif entity==V:
            validate_value(after)
            if after.get('TypeOfLineCode')not in {'MEAL_DEDUCTION','ACCOM_DEDUCTION'}:
                raise ValueError('Per Diem new value rows are exact deduction companions only')
        return
    if operation!='update':raise ValueError('Unsupported Per Diem operation')
    if entity == P:
        validate_parent(after)
        from per_diem_applicability import validate_changed_fields
        validate_changed_fields(P, before, after, after)
        if any(after.get(f) != before.get(f) for f in STRUCTURAL | DETERMINANTS):
            raise ValueError('Per Diem formula/currency/status/key/determinant transitions require separate qualified serialization')
        heads = [r for r in baseline_rows.get(R, []) if r.get(REF) == before['PolicyName'] and r.get('TypeOfLineCode') == 'ANCHOR']
        if len(heads) != 1:
            raise ValueError('Per Diem parent transition requires an exact existing ANCHOR')
        try:
            old_inventory = set(expected_inline_values(before, heads[0]))
        except (KeyError, ValueError):
            raise ValueError('Per Diem original percentage value ownership cannot be established; creating/rekeying missing synchronization rows is unqualified') from None
        if old_inventory != set(expected_inline_values(after, heads[0])):
            raise ValueError('Per Diem transition changes percentage value-row inventory; new/deleted synchronization rows require separate qualification')
    elif entity == R:
        validate_rate(after)
        if {f for f in after if after[f] != before[f]} - AMOUNTS:
            raise ValueError('Per Diem line keys, dates, status and range bounds are preserved; only business amounts may change')
    elif entity == V:
        validate_value(after)
        if {f for f in after if after[f] != before[f]} - {'LineValue'}:
            raise ValueError('Per Diem value keys and generated lower bounds cannot change')


def plan_existing_value_updates(records, rows, *, exclude_new_policies=()):
    """Return exact companion updates; never mutate inputs or create/delete rows."""
    result = []
    names = {r['policy_name'] for r in records if r['entity'] in {P, R}}
    for name in names:
        if name in exclude_new_policies:continue
        parents = policy_rows(rows, name, P)
        if len(parents) != 1:
            raise ValueError('Per Diem synchronization requires an exact parent')
        expected, actual = validate_policy(parents[0], policy_rows(rows, name, R),
            policy_rows(rows, name, V), verify_inline=False)
        for coordinate, value in expected.items():
            before = actual[coordinate]
            if number(before.get('LineValue'), 'LineValue') == number(value, 'inline amount'):
                continue
            if value == '':
                raise ValueError('Clearing an existing Per Diem value requires unqualified explicit-empty serialization')
            after = {**before, 'LineValue': value}
            validate_change(V, 'update', before, after, rows)
            result.append({'entity': V, 'policy_name': name, 'operation': 'update',
                'targetKey': {f: before.get(f, '') for f in VALUE_IDENTITY}, 'before': before,
                'after': after, 'source': SOURCE, 'reason': 'Explicit existing value synchronization from reviewed UI relationship; not an import side effect'})
    return result


def verify_result(submitted, original_rows):
    rows = {e: [dict(r) for r in original_rows.get(e, [])] for e in ENTITIES}
    names = set()
    changes = []
    for record in submitted:
        entity, row = record['entity'], record['values']
        names.add(row.get('PolicyName', row.get(REF)))
        fields = ['PolicyName'] if entity == P else IDENTITY if entity == R else VALUE_IDENTITY
        matches = [r for r in rows[entity] if key(r, fields) == key(row, fields)]
        if len(matches)>1:raise ValueError('Ambiguous Per Diem submitted alternate key')
        before=matches[0]if matches else dict.fromkeys(row,'')
        operation='update'if matches else'create'
        validate_change(entity,operation,before,row,original_rows)
        changes.append((entity,before,row))
        if matches:rows[entity][rows[entity].index(matches[0])]=row
        else:rows[entity].append(row)
    for name in names:
        parents = policy_rows(rows, name, P)
        if len(parents) != 1:
            raise ValueError('Per Diem result requires an exact parent')
        from per_diem_applicability import validate_changed_fields
        parent = parents[0]
        for entity, before, after in changes:
            if after.get('PolicyName', after.get(REF)) == name:
                validate_changed_fields(entity, before, after, parent)
                if entity == V and before != after:
                    heads = [r for r in policy_rows(rows, name, R) if r.get('TypeOfLineCode') == 'ANCHOR']
                    if len(heads) != 1:
                        raise ValueError('Per Diem value effect requires one exact resulting ANCHOR')
                    expected = expected_inline_values(parent, heads[0])
                    coordinate = after.get('TypeOfLineCode'), after.get('DeterminantCode')
                    if (coordinate not in expected
                            or number(after.get('LineValue'), 'LineValue') != number(expected[coordinate], 'inline amount')):
                        raise ValueError('Per Diem changed value row lacks its exact active resulting ANCHOR relationship')
        expected,actual=validate_policy(parents[0], policy_rows(rows, name, R), policy_rows(rows, name, V))
        if not policy_rows(original_rows,name,P):
            values=policy_rows(rows,name,V)
            if len(values)!=len(expected)or{(r['TypeOfLineCode'],r.get('DeterminantCode',''))for r in values}!=set(expected):
                raise ValueError('New Per Diem value inventory must be exact source-derived deduction companions')
            if any(r.get('TypeOfLineCode')not in active_line_kinds(parent)for r in policy_rows(rows,name,R)):
                raise ValueError('New Per Diem rates cannot create inactive line kinds')
    return {'profile': 'per-diem-no-determinants-existing-v1', 'requires_live_qualification': True,
        'qualification': 'source_qualified_new_policy_groups_live_pending_existing_updates_scoped',
        'import_approved': False}
