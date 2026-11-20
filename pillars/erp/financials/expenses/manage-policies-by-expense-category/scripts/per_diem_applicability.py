"""Changed-field enterability from the captured Per Diem UI branch controls.

Compare with the final merged parent; never clear unchanged dormant values.
These task-input checks do not establish shared readXML field acceptance.
"""
from per_diem_intake import MEAL_FIELDS, DEDUCTIONS

P = 'ORA_EXM_PERDIEM_POLICY'
R = P + '_LINE'


def time_main_active(parent):
    formula = parent.get('RateFormulaMethodCode')
    return formula == 'TIME_SINGLE' or formula == 'TIME_SUMUP' and parent.get('RateIncludeMealsFlag') == 'Y'


def accommodation_components_active(parent):
    return parent.get('RateFormulaMethodCode') in {'SUMUP', 'TIME_SUMUP'} and parent.get('RateIncludeAccomFlag') == 'Y'


def meal_deduction_enabled(parent):
    single = parent.get('RateFormulaMethodCode') in {'SINGLE', 'TIME_SINGLE'}
    return parent.get('RateIncludeMealsFlag') == 'Y' and (single or parent.get('MealRateTypeCode') in {'', None, 'DAILY'})


def meal_deduction_active(parent):
    return meal_deduction_enabled(parent) and parent.get('MealDeductionFlag') == 'Y'


def accommodation_deduction_active(parent):
    return (parent.get('RateFormulaMethodCode') in {'SINGLE', 'TIME_SINGLE'}
        and parent.get('RateIncludeAccomFlag') == 'Y' and parent.get('AccomDeductionFlag') == 'Y')


def duration_branches(parent):
    # SUMUP's meals AND accommodation duration blocks are commented out
    # (Bug22894530). Time's
    # meals inputs are active; their showRequired is a task input indication,
    # not proof that commonCode's differently named bindings execute there.
    return (
        ('MinTripDuratFlag', 'MinDurationHours', 'MinDurationMinutes', time_main_active(parent)),
        ('AccomMinTripDuratFlag', 'AccomMinDurationHours', 'AccomMinDurationMinutes',
            parent.get('RateFormulaMethodCode') == 'TIME_SUMUP' and parent.get('RateIncludeAccomFlag') == 'Y'),
    )


def validate_durations(parent, integer):
    for flag, hours, minutes, active in duration_branches(parent):
        if not active or parent.get(flag) != 'Y':
            continue
        # Bounds belong to the active input fragment, including retained active
        # values. Inactive legacy values are preserved without this new cap.
        integer(parent.get(hours), hours, 24)
        integer(parent.get(minutes), minutes, 60)
        if all(parent.get(f, '') in {'', None} for f in (hours, minutes)):
            raise ValueError('Per Diem '+flag+' requires at least one explicit hours/minutes value in the active task input; zero counts as supplied')


def validate_changed_fields(entity, before, after, parent):
    changed = {f for f in after if after.get(f) != before.get(f)}
    formula = parent.get('RateFormulaMethodCode')
    if entity == P:
        checks = {
            'MealsDeductionCode': meal_deduction_active(parent),
            'MealsDeductCalcMethCode': meal_deduction_active(parent),
            'AccomDeductCalcMethCode': accommodation_deduction_active(parent),
            'MinimumReimbursement': meal_deduction_active(parent) or accommodation_deduction_active(parent),
        }
        if 'MealDeductionFlag' in changed and after.get('MealDeductionFlag') == 'Y':
            checks['MealDeductionFlag'] = meal_deduction_enabled(parent)
        if 'AccomDeductionFlag' in changed and after.get('AccomDeductionFlag') == 'Y':
            checks['AccomDeductionFlag'] = accommodation_deduction_active(parent)
        for flag, hours, minutes, active in duration_branches(parent):
            checks[hours] = checks[minutes] = active and parent.get(flag) == 'Y'
            if flag in changed and after.get(flag) == 'Y':
                checks[flag] = active
        for field in sorted(changed & checks.keys()):
            if not checks[field]:
                raise ValueError('Per Diem '+field+' is not enterable under the final parent controls; unchanged dormant values are preserved')
        return
    if entity != R:
        return
    kind = after.get('TypeOfLineCode')
    for field in changed:
        allowed = True
        if field == 'BaseRate':
            if kind == 'ANCHOR':
                allowed = (formula == 'SINGLE' and parent.get('RoleCalcMethod') != 'RATE'
                    or formula == 'SUMUP' and parent.get('RateIncludeMealsFlag') == 'Y'
                    and parent.get('MealRateTypeCode') in {'', None, 'DAILY'})
            elif kind in {'STANDARD', 'SAME'}:
                allowed = (time_main_active(parent) and parent.get('TimeCalcMethodCode') == 'RATE'
                    and (kind != 'SAME' or parent.get('TimeAllowSameDayFlag') == 'Y'))
            elif kind == 'OTHER_STANDARD':
                allowed = (formula == 'TIME_SUMUP' and parent.get('RateIncludeOtherFlag') == 'Y'
                    and parent.get('OthersCalcMethodCode') == 'RATE')
            else:
                allowed = False
        elif field in DEDUCTIONS:
            allowed = (kind == 'ANCHOR' and meal_deduction_active(parent)
                and field in MEAL_FIELDS.get(parent.get('MealsDeductionCode'), ()))
        elif field == 'AccommodationDeduction':
            allowed = kind == 'ANCHOR' and accommodation_deduction_active(parent)
        elif field in {'MealsBreakfastRate', 'MealsLunchRate', 'MealsDinnerRate'}:
            allowed = (kind == 'ANCHOR' and formula == 'SUMUP'
                and parent.get('RateIncludeMealsFlag') == 'Y' and parent.get('MealRateTypeCode') == 'TYPE')
        elif field in {'MealsOneMealRate', 'MealsTwoMealsRate', 'MealsThreeMealsRate'}:
            allowed = (kind == 'ANCHOR' and formula == 'SUMUP'
                and parent.get('RateIncludeMealsFlag') == 'Y' and parent.get('MealRateTypeCode') == 'NUMBER')
        elif field == 'AccomNightRate':
            allowed = kind == 'ANCHOR' and accommodation_components_active(parent)
        elif field == 'OthersStandardRate':
            allowed = kind == 'ANCHOR' and formula == 'SUMUP' and parent.get('RateIncludeOtherFlag') == 'Y'
        if not allowed:
            raise ValueError('Per Diem '+field+' is not enterable for this subtype and final parent include/deduction controls; unchanged dormant values are preserved')
