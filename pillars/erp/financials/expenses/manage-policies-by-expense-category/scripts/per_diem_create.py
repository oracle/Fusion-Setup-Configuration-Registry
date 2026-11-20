"""Source-qualified new Per Diem groups; explicit task-owned derived effects.

No user-controlled value-row target, inferred Fusion default or import side effect.
Existing policies keep the independently reviewed update-only effect path.
"""
from per_diem_profile import (P,R,V,REF,SOURCE,IDENTITY,VALUE_IDENTITY,DETERMINANTS,
    validate_parent,validate_rate,validate_value,validate_policy,expected_inline_values,
    integer,key,policy_rows)

CREATE_SOURCE='PER-DIEM-CREATE-SERIALIZATION'
IDS=[SOURCE,CREATE_SOURCE]


def check_recipe(contract):
    from per_diem_profile import validate_evidence
    validate_evidence(contract)
    rule=contract['entities'][P].get('create_derived_fields',{})
    if rule!={'TimeBasedRateModelFlag':{'derivation':'formula_time_prefix','source_ids':IDS}}:
        raise ValueError('Per Diem formula-derived create ownership differs from the reviewed contract')
    rule=contract['entities'][R].get('create_derived_fields',{})
    if rule!={'Status':{'derivation':'anchor_valid_other_draft','source_ids':IDS},
            'LowerLineHours':{'derivation':'same_kind_preceding_upper','source_ids':IDS},
            'LowerLineMinutes':{'derivation':'same_kind_preceding_upper','source_ids':IDS}}:
        raise ValueError('Per Diem range/status create ownership differs from the reviewed contract')


def explicit_kind(raw):
    from workbook_intake import load_catalog
    spec=next(c for sh in load_catalog()['sheets']if sh['entity']==R
        for c in sh['columns']if c.get('csv_field')=='TypeOfLineCode')
    return spec.get('display_values',{}).get(raw,raw)


def derive_create_fields(entity,values,records,original_rows,contract):
    """Derive only named non-input fields for a wholly new exact policy group."""
    if entity not in {P,R}:return {},[]
    check_recipe(contract)
    name=values.get('PolicyName'if entity==P else REF)
    if policy_rows(original_rows,name,P):
        raise ValueError('Per Diem new child/range creation for an existing policy requires separate existing-range synchronization qualification')
    if entity==P:
        formula=values.get('RateFormulaMethodCode')
        if formula not in {'SINGLE','SUMUP','TIME_SINGLE','TIME_SUMUP'}:
            raise ValueError('Per Diem create requires an explicit supported RateFormulaMethodCode')
        derived={'TimeBasedRateModelFlag':'Y'if formula.startswith('TIME')else'N'}
    else:
        kind=values.get('TypeOfLineCode')
        if kind not in {'ANCHOR','STANDARD','SAME','OTHER_STANDARD'}:
            raise ValueError('Per Diem create requires an explicit supported Rate Component; no ANCHOR default is inferred')
        if kind=='OTHER_STANDARD':
            raise ValueError('Per Diem OTHER_STANDARD creation lower-threshold ownership is source-pending; existing rows may use the separately reviewed update profile')
        own=[r['values']for r in records if r['entity']==R and r['policy_name']==name]
        heads=[r for r in own if explicit_kind(r.get('TypeOfLineCode'))=='ANCHOR']
        if len(heads)!=1:raise ValueError('Per Diem create requires exactly one explicit ANCHOR rate')
        head=heads[0]
        from datetime import datetime
        def csv_date(raw):return datetime.fromisoformat(raw).strftime('%Y/%m/%d')if raw else''
        if any(values.get(f,'')!=csv_date(head.get(f,''))for f in ['StartDate','EndDate']):
            raise ValueError('Per Diem new range dates must match the explicitly supplied ANCHOR dates')
        derived={'Status':'VALID'if kind=='ANCHOR'else'DRAFT'}
        if kind!='ANCHOR':
            own=[r for r in own if explicit_kind(r.get('TypeOfLineCode'))==kind]
            coordinates=[]
            for row in own:
                hour=integer(row.get('LineHours'),'LineHours',999,True)
                minute=integer(row.get('LineMinutes'),'LineMinutes',60)or 0
                if hour>24 and hour!=999:raise ValueError('Per Diem create range hours must be 0..24 or explicit 999')
                coordinates.append((hour,minute))
            if len({h for h,m in coordinates})!=len(coordinates):
                raise ValueError('Per Diem equal-hour minute range ordering is not source-qualified for creation; supply distinct hours or resolve that ordering')
            coordinates.sort()
            own_coordinate=(integer(values.get('LineHours'),'LineHours',999,True),
                integer(values.get('LineMinutes'),'LineMinutes',60)or 0)
            index=coordinates.index(own_coordinate)
            lower=(0,0)if index==0 else coordinates[index-1]
            if own_coordinate<=lower:raise ValueError('Per Diem create range upper bound must exceed its source-derived lower bound')
            derived.update(LowerLineHours=str(lower[0]),LowerLineMinutes=str(lower[1]))
    for field in derived:
        if contract['entities'][entity]['fields'].get(field,{}).get('create')!='consumer-managed':
            raise ValueError('Per Diem derived create field lacks reviewed consumer ownership: '+field)
    return derived,[{'field':field,'value':value,'source_ids':IDS,
        'ownership':'consumer-managed explicit source derivation; not a Fusion default'}for field,value in derived.items()]


def validate_new_parent(parent):
    validate_parent(parent)
    if parent.get('Status')!='DRAFT':raise ValueError('New Per Diem parent requires explicit managed DRAFT')
    for field in ['AllowRateConversionFlag','RateIncludeMealsFlag','RateIncludeAccomFlag',
            'RateIncludeOtherFlag','MealDeductionFlag','AccomDeductionFlag']:
        if parent.get(field)not in {'Y','N'}:
            raise ValueError('Per Diem create requires explicit '+field+' Yes/No; no EO/UI default is inferred')
    if not any(parent.get(f)=='Y'for f in ['RateIncludeMealsFlag','RateIncludeAccomFlag','RateIncludeOtherFlag']):
        raise ValueError('Per Diem create requires at least one Rate Includes component, matching the UI last-component guard')
    if (parent.get('RateFormulaMethodCode','').startswith('TIME')
            and parent.get('MealsCalcMethodCode')=='PERCENTAGE'):
        raise ValueError('Per Diem dormant MEALS percentage component creation is not qualified for the active time-rate UI branch')


def owns_line_status(entity,after,managed_values,contract):
    if entity!=R:return False
    check_recipe(contract)
    expected='VALID'if after.get('TypeOfLineCode')=='ANCHOR'else'DRAFT'
    return (after.get('TypeOfLineCode')in {'ANCHOR','STANDARD','SAME','OTHER_STANDARD'}
        and after.get('Status')==managed_values.get('Status')==expected
        and contract['entities'][R]['fields']['Status']['create']=='consumer-managed')


def new_value_rows(parent,rates,contract):
    """Create only the exact code-based percentage companions of the new head."""
    check_recipe(contract);validate_new_parent(parent)
    heads=[r for r in rates if r.get('TypeOfLineCode')=='ANCHOR']
    if len(heads)!=1:raise ValueError('New Per Diem policy needs one exact ANCHOR before deriving value rows')
    expected=expected_inline_values(parent,heads[0])
    if any(kind not in {'MEAL_DEDUCTION','ACCOM_DEDUCTION'}for kind,code in expected):
        raise ValueError('Per Diem new internal value profile admits exact deduction companions only')
    headers=contract['entities'][V]['fields']
    rows=[]
    for (kind,code),amount in sorted(expected.items()):
        row=dict.fromkeys(headers,'')
        row.update({REF:parent['PolicyName'],'TypeOfLineCode':kind,'DeterminantCode':code,'LineValue':amount})
        validate_value(row);rows.append(row)
    return rows


def verify_new_values(parent,rates,values,contract):
    expected=new_value_rows(parent,rates,contract)
    if {key(r,VALUE_IDENTITY)for r in expected}!={key(r,VALUE_IDENTITY)for r in values}:
        raise ValueError('Per Diem new value rows must be exactly the source-derived code companions')
    for row in values:
        wanted=next(r for r in expected if key(r,VALUE_IDENTITY)==key(row,VALUE_IDENTITY))
        from per_diem_profile import number
        if number(row.get('LineValue'),'LineValue')!=number(wanted.get('LineValue'),'LineValue'):
            raise ValueError('Per Diem new value amount differs from its exact ANCHOR deduction')
    validate_policy(parent,rates,values)
