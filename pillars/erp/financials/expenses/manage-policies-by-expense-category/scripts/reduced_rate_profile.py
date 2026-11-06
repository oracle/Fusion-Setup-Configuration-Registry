"""Validate reduced rate input against explicit or baseline parent settings.

No values are generated. Missing workbook parent flags are deferred to the
baseline operation stage, so omitted update controls are not interpreted as No.
"""

MEALS = 'ORA_EXM_MEALS_POLICY'
LIMIT_FLAGS = {'SingleInstanceLimit': 'SingleInstanceLimitFlag', 'DailyLimit': 'DailyLimitFlag'}


def flag(value):
    if value in ('Yes', 'Y', True):
        return True
    if value in ('No', 'N', False):
        return False
    return None


def workbook_limit_issues(records):
    parents = {(r['entity'], r['policy_name']): r['values'] for r in records if r['kind']=='policy'}
    issues = []
    for record in records:
        if not record['entity'].endswith('_LINE'):
            continue
        parent = parents.get((record['entity'][:-5],record['policy_name']), {})
        source = record['sources'][0] if record['sources'] else {}
        for control in ('EnabledRoleFlag','EnabledLocationFlag'):
            if flag(parent.get(control)) is True:
                issues.append({'sheet':source.get('sheet',''),'cell':str(source.get('row','')),
                    'message':'Reduced rate sheets cannot supply determinants for parent '+control+' = Yes'})
        if parent.get('CurrencyOptionCode') not in (None,'SINGLE'):
            issues.append({'sheet':source.get('sheet',''),'cell':str(source.get('row','')),
                'message':'Reduced rate sheets require parent Rate Currency = Single currency; currency is specified on the parent'})
        if record['entity'] != MEALS+'_LINE':
            continue
        for field, control in LIMIT_FLAGS.items():
            if field in record['values'] and flag(parent.get(control)) is False:
                source = next((s for s in record['sources'] if field in s['fields']), {})
                issues.append({'sheet':source.get('sheet','Meals Rates'),
                    'cell':source.get('fields',{}).get(field,''),
                    'message':field+' is not applicable because parent '+control+' is No'})
    return issues


def validate_resulting_rate(entity, row, parent):
    """Operation-stage validation after exact baseline and parent resolution."""
    if entity != MEALS+'_LINE':
        return
    states = {amount:flag(parent.get(control)) for amount,control in LIMIT_FLAGS.items()}
    if any(state is None for state in states.values()):
        raise ValueError('Meals limit applicability requires both resolved parent limit flags')
    if not any(states.values()):
        raise ValueError('Meals parent must enable at least one limit for a rate')
    for amount, enabled in states.items():
        supplied = row.get(amount) not in ('', None)
        if supplied and not enabled:
            raise ValueError(amount+' is not applicable to the resolved parent')
        if enabled and not supplied:
            raise ValueError(amount+' is required by the resolved parent limit flag')


def validate_reduced_parent(parent):
    """No child determinant/currency columns exist in this workbook revision."""
    from single_currency_policy import require_existing_single_currency
    require_existing_single_currency(parent)
    for field in ('EnabledRoleFlag','EnabledLocationFlag'):
        if flag(parent.get(field)) is not False:
            raise ValueError('Reduced rates require explicit/resolved No for parent '+field)
    for field in ('EnabledRoleFlag','EnabledLocationFlag','EnabledSeasonRateFlag','EnabledGenderFlag'):
        value = parent.get(field)
        if value not in ('',None) and flag(value) is not False:
            raise ValueError('Reduced rates do not support enabled parent determinant '+field)
    if parent.get('CurrencyOptionCode') != 'SINGLE' or not parent.get('CurrencyCode'):
        raise ValueError('Reduced rates require a single-currency parent with explicit Currency Code; child currency derivation remains separately qualified')
