"""Serialize explicitly reviewed consumer-owned create fields, never user cells.

Recipes remain disabled unless the selected runtime contract supplies ownership,
values and registered evidence. This module supplies no runtime qualification.
"""
P='ORA_EXM_MEALS_POLICY'
ALLOWED={P:{'Status':'DRAFT','EnabledRoleFlag':'N','EnabledLocationFlag':'N'},
         P+'_LINE':{'Status':'DRAFT'}}


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
            raise ValueError('Managed create field is outside the protected Meals scope: '+field)
        if not isinstance(recipe,dict) or recipe.get('value')!=ALLOWED[entity][field]:
            raise ValueError('Managed create value is outside the reviewed Meals scope: '+field)
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
