"""Authoring scope for this branch; exported out-of-scope data is preserved."""
CATEGORIES = ('Meals',)
ENTITIES = frozenset({
    'ORA_EXM_MEALS_POLICY', 'ORA_EXM_MEALS_POLICY_LINE',
})

REMOVED_PARENT_FIELDS = frozenset({'RatesSourceCode', 'MealsRateSourceCode',
    'RateIncludeMealsFlag', 'RateIncludeOtherFlag', 'LocationTypeCode', 'ZoneTypeCode',
    'GeoLocName', 'EnabledSeasonRateFlag', 'EnabledGenderFlag', 'Status',
    'EnabledRoleFlag', 'PolicyRoleCode', 'EnabledLocationFlag', 'CurrencyOptionCode'})
RATE_FIELDS = frozenset({'StartDate', 'EndDate', 'DailyLimit', 'SingleInstanceLimit'})


def allowed_input(entity, field):
    if entity not in ENTITIES:
        return False
    if entity.endswith('_LINE'):
        return (field == entity[:-5]+'.PolicyName' or field in RATE_FIELDS
                and (field != 'SingleInstanceLimit' or entity == 'ORA_EXM_MEALS_POLICY_LINE'))
    return field not in REMOVED_PARENT_FIELDS


def require_scoped_records(records):
    for record in records:
        if record.get('entity') not in ENTITIES or record.get('shared_entities'):
            raise ValueError('Category outside limited authoring scope: ' + str(record.get('entity')))
        if any(not allowed_input(record['entity'], field) for field in record.get('values', {})):
            raise ValueError('Field outside reduced workbook input scope: '+record['entity'])
    names = {}
    identities = set()
    for record in records:
        values = record.get('values', {})
        rate = record['entity'].endswith('_LINE')
        field = 'ORA_EXM_MEALS_POLICY.PolicyName' if rate else 'PolicyName'
        name = values.get(field, record.get('policy_name'))
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Every selected row requires an exact Policy Name')
        if record.get('policy_name') is not None and record['policy_name'] != name:
            raise ValueError('Policy Name association differs from the supplied row')
        if names.setdefault(name.casefold(), name) != name:
            raise ValueError('Case-only Policy Name association collision; use exact names')
        key = (record['entity'], name.casefold())
        if rate:
            key += (values.get('StartDate', ''), values.get('EndDate', ''))
        if key in identities:
            raise ValueError('Duplicate workbook policy/rate identity')
        identities.add(key)


def require_target_rate_identities(records, rows):
    """Reject ambiguous keys for selected policies without limiting row counts."""
    require_scoped_records(records)
    names = {r.get('values', {}).get('PolicyName', r.get('values', {}).get('ORA_EXM_MEALS_POLICY.PolicyName', r.get('policy_name')))
             for r in records}
    selected = {name.casefold() for name in names}
    rates = rows.get('ORA_EXM_MEALS_POLICY_LINE', [])
    for name in selected:
        matches = [r for r in rates if r.get('ORA_EXM_MEALS_POLICY.PolicyName', '').casefold() == name]
        exact_names = {r['ORA_EXM_MEALS_POLICY.PolicyName'] for r in matches}
        if exact_names - names:
            raise ValueError('Case-only baseline rate association collision')
        keys = [tuple(r.get(f, '') for f in (
            'CurrencyCode','EndDate','GeoLocName','RoleName','StartDate','TypeOfRateCode','ZoneCode')) for r in matches]
        if len(keys) != len(set(keys)):
            raise ValueError('Ambiguous baseline rate identity for selected policy')
