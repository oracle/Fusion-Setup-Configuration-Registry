"""Serialize explicitly reviewed consumer-owned create fields, never user cells.

Recipes remain disabled unless the selected runtime contract supplies ownership,
values and registered evidence. This module supplies no runtime qualification.
"""
P='ORA_EXM_MEALS_POLICY'
ALLOWED={P:{'Status':'DRAFT','EnabledRoleFlag':'N','EnabledLocationFlag':'N'},
         P+'_LINE':{'Status':'DRAFT'},
         'ORA_EXM_ACCOM_POLICY':{'Status':'DRAFT','EnabledRoleFlag':'N','EnabledLocationFlag':'N',
             'EnabledSeasonRateFlag':'N','EnabledGenderFlag':'N'},
         'ORA_EXM_ACCOM_POLICY_LINE':{'Status':'DRAFT'}}
ALLOWED['ORA_EXM_ENTERTAINMENT_POLICY'] = {'Status':'DRAFT','AttendeeTypesFlag':'N',
    'EmpRateDeterminantFlag':'N','NonempRateDeterminantFlag':'N','EnabledRoleFlag':'N',
    'RateLimitTypeCode':'ATTENDEE'}
ALLOWED['ORA_EXM_ENTERTAINMENT_POLICY_LINE'] = {'Status':'DRAFT'}
ALLOWED['ORA_EXM_CARRENTAL_POLICY'] = {'Status':'DRAFT','EnabledRoleFlag':'N','EnabledLocationFlag':'N'}
ALLOWED['ORA_EXM_CARRENTAL_POLICY_LINE'] = {'Status':'DRAFT'}
ALLOWED['ORA_EXM_AIRFARE_POLICY'] = {'Status':'DRAFT','EnabledRoleFlag':'N',
    'EnabledFlightTypeFlag':'N','EnabledFlightDurationFlag':'N'}
ALLOWED['ORA_EXM_AIRFARE_POLICY_LINE'] = {'Status':'DRAFT','TypeOfRateCode':'CATCH_ALL'}
ALLOWED['ORA_EXM_MISCELLANEOUS_POLICY'] = {'Status':'DRAFT','EnabledRoleFlag':'N',
    'EnabledLocationFlag':'N','EnabledGenderFlag':'N'}
ALLOWED['ORA_EXM_MISCELLANEOUS_POLICY_LINE'] = {'Status':'DRAFT','CurrencyCode':'',
    'GeoLocName':'','RoleName':'','TypeOfRateCode':'','ZoneCode':'','GenderCode':''}
ALLOWED['ORA_EXM_MILEAGE_POLICY'] = {'Status':'DRAFT','EnabledRoleFlag':'N','EnabledLocationFlag':'N',
    'DistanceThresholdFlag':'N','EnabledVehCategoryFlag':'N','EnabledVehTypeFlag':'N',
    'EnabledFuelTypeFlag':'N','EnabledGenderFlag':'N'}
ALLOWED['ORA_EXM_MILEAGE_LINE'] = {'Status':'DRAFT'}
ALLOWED['ORA_EXM_PERDIEM_POLICY']={'Status':'DRAFT','PerdiemPolicyType':'GENERIC','CurrencyOptionCode':'SINGLE',
    **{f:'N' for f in ['EnabledLocationFlag','EnabledSeasonRateFlag','EnabledAccomTypeFlag',
        'EnabledRoleFlag','EnabledLongTermFlag','EnabledWeekendHolidFlag','SpecificFirstLastDayFlag']}}


def managed_create_values(entity, operation, current, contract, input_fields):
    if operation!='create':
        return {},[]
    recipes=current.get('create_managed_fields',{})
    if not isinstance(recipes,dict):raise ValueError('Invalid managed-create recipe inventory')
    sources=contract.get('sources',{})
    if not isinstance(sources,dict):sources={}
    result={};review=[]
    for field,recipe in recipes.items():
        if field in input_fields or field not in ALLOWED.get(entity,{}):
            raise ValueError('Managed create field is outside the protected policy scope: '+field)
        if not isinstance(recipe,dict) or recipe.get('value')!=ALLOWED[entity][field]:
            raise ValueError('Managed create value is outside the reviewed policy scope: '+field)
        rule=current.get('fields',{}).get(field,{})
        if rule.get('create')!='consumer-managed':
            raise ValueError(field+': explicit consumer-managed create ownership required')
        for ids in [recipe.get('source_ids'),rule.get('source_ids')]:
            if not isinstance(ids,list) or not ids or any(not isinstance(i,str) or not sources.get(i) for i in ids):
                raise ValueError(field+': managed create value and ownership need registered evidence')
        result[field]=recipe['value']
        review.append({'field':field,'value':recipe['value'],'source_ids':recipe['source_ids'],
                       'ownership':'consumer-managed; not an inferred Fusion default'})
    return result,review
