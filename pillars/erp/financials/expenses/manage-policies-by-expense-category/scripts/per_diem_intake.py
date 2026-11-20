"""Supplied-value checks for ordinary Per Diem deduction/eligibility inputs.

UI range and branch rules do not establish FSM serialization or generated value
row ownership. Omitted update cells never disable or reset retained settings.
"""
from decimal import Decimal, InvalidOperation

P='ORA_EXM_PERDIEM_POLICY'
R=P+'_LINE'
MEAL_FIELDS={
    'DAILY':('MealsDailyDeduction',),
    'TYPE':('MealsBreakfastDeduction','MealsLunchDeduction','MealsDinnerDeduction'),
    'NUMBER':('MealsOneMealDeduction','MealsTwoMealsDeduction','MealsThreeMealsDeduction'),
}
DEDUCTIONS={f for values in MEAL_FIELDS.values() for f in values}
COMPONENT_RATES={'Meals'+part+'Rate' for part in ('Breakfast','Lunch','Dinner','OneMeal','TwoMeals','ThreeMeals')}|{'AccomNightRate','OthersStandardRate'}
MEAL_TIMES={meal+'Elig'+edge+unit for meal in ('Breakfast','Lunch','Dinner')
    for edge in ('Start','End') for unit in ('Hour','Minute')}
ACCOM_TIMES={'AccomEligib'+edge+unit for edge in ('Start','End') for unit in ('Hour','Minute')}


def supplied_issues(entity,values,parent,error):
    if entity not in {P,R}: return
    if entity==P:
        for deduction,include in [('MealDeductionFlag','RateIncludeMealsFlag'),('AccomDeductionFlag','RateIncludeAccomFlag')]:
            if values.get(deduction)=='Yes' and values.get(include)=='No':
                error(deduction,deduction+' requires '+include+' = Yes')
        for control,fields in {
            'MealDeductionFlag':{'MealsDeductionCode','MealsDeductCalcMethCode'},
            'AccomDeductionFlag':{'AccomDeductCalcMethCode'},
            'MinTripDuratFlag':{'MinDurationHours','MinDurationMinutes'},
            'AccomMinTripDuratFlag':{'AccomMinDurationHours','AccomMinDurationMinutes'},
            'TimeAllowSameDayFlag':{'TimeSameDayRuleCode'},
        }.items():
            if values.get(control)=='No':
                for field in sorted(fields & values.keys()):
                    error(field,field+' is not enterable when '+control+' = No; omitted updates preserve baseline values')
        for field in (MEAL_TIMES|ACCOM_TIMES)&values.keys():
            limit=24 if field.endswith('Hour') else 60
            try:
                value=int(values[field])
                if not 0<=value<=limit: raise ValueError()
            except (ValueError,TypeError):
                error(field,field+' must be an integer from 0 through '+str(limit)+' under the captured UI range')
        for field,maximum in [('AccomMinNightHoursStay',Decimal(24)),('MinimumReimbursement',None)]:
            if field not in values: continue
            try:
                number=Decimal(values[field])
                if not number.is_finite() or number<0 or maximum is not None and number>maximum:
                    raise ValueError()
            except (InvalidOperation,ValueError):
                error(field,field+' must be finite and nonnegative'+(' and no greater than 24' if maximum else ''))
        eligibility=values.get('OthersEligibCriteriaCode')
        for code,includes in {'MEALS':('RateIncludeMealsFlag',),
                'ACCOM':('RateIncludeAccomFlag',),'MEALS_ACCOM':('RateIncludeMealsFlag','RateIncludeAccomFlag')}.items():
            if eligibility==code:
                for field in includes:
                    if values.get(field)=='No': error('OthersEligibCriteriaCode',code+' eligibility requires '+field+' enabled')
        if values.get('MealInclIncidentalFlag')=='Yes' and values.get('RateIncludeOtherFlag')=='Yes':
            error('RateIncludeOtherFlag','Other cannot be selected while Meals Include Incidentals is Yes')
        return
    for field in (DEDUCTIONS|{'AccommodationDeduction'}|COMPONENT_RATES)&values.keys():
        try:
            amount=Decimal(values[field])
            if not amount.is_finite() or amount<0: raise ValueError()
        except (InvalidOperation,ValueError):
            error(field,field+' must be a finite nonnegative amount or percentage')
        control=('RateIncludeAccomFlag' if field=='AccomNightRate' else
                 'RateIncludeOtherFlag' if field=='OthersStandardRate' else
                 'RateIncludeMealsFlag' if field in COMPONENT_RATES else
                 'AccomDeductionFlag' if field=='AccommodationDeduction' else 'MealDeductionFlag')
        if parent.get(control)=='No':
            error(field,field+' requires the parent '+control+' enabled')
    mode=parent.get('MealsDeductionCode')
    if mode in MEAL_FIELDS:
        for field in (DEDUCTIONS-set(MEAL_FIELDS[mode]))&values.keys():
            error(field,field+' does not belong to the selected '+mode+' meals deduction type')
    for field,limit in [('LineHours',24),('LineMinutes',60)]:
        if field not in values: continue
        try:
            value=int(values[field])
            if field=='LineHours' and value==999: continue
            if not 0<=value<=limit: raise ValueError()
        except (ValueError,TypeError):
            error(field,field+' must be 0 through '+str(limit)+(' or 999 for the upper-limit range' if field=='LineHours' else ''))
