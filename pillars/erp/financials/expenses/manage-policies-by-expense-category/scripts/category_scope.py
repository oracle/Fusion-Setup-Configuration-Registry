"""Authoring scope for this branch; exported out-of-scope data is preserved."""
from expanded_category_intake import ENTITIES as EXPANDED_ENTITIES, PARENT_BY_RATE

CATEGORIES = ('Meals', 'Accommodations', 'Entertainment', 'Airfare', 'Car Rental', 'Mileage', 'Miscellaneous', 'Per Diem')
PARENTS = ('ORA_EXM_MEALS_POLICY', 'ORA_EXM_ACCOM_POLICY', 'ORA_EXM_ENTERTAINMENT_POLICY', 'ORA_EXM_CARRENTAL_POLICY', 'ORA_EXM_MISCELLANEOUS_POLICY', 'ORA_EXM_MILEAGE_POLICY')
ENTITIES = frozenset({
    'ORA_EXM_MEALS_POLICY', 'ORA_EXM_MEALS_POLICY_LINE',
    'ORA_EXM_ACCOM_POLICY', 'ORA_EXM_ACCOM_POLICY_LINE',
    'ORA_EXM_ENTERTAINMENT_POLICY', 'ORA_EXM_ENTERTAINMENT_POLICY_LINE',
}) | EXPANDED_ENTITIES | {'ORA_EXM_PER_DIEM_POLICY_VALUE'}

REMOVED_PARENT_FIELDS = frozenset({'RatesSourceCode', 'MealsRateSourceCode',
    'RateIncludeMealsFlag', 'RateIncludeOtherFlag', 'LocationTypeCode', 'ZoneTypeCode',
    'GeoLocName', 'EnabledSeasonRateFlag', 'EnabledGenderFlag', 'Status',
    'EnabledRoleFlag', 'PolicyRoleCode', 'EnabledLocationFlag', 'CurrencyOptionCode'})
RATE_FIELDS = frozenset({'StartDate', 'EndDate', 'DailyLimit', 'SingleInstanceLimit'})


def owning_policy(entity):
    """Use the exported association, including Mileage's nonuniform name."""
    if entity not in ENTITIES:
        raise ValueError('Category outside limited authoring scope: ' + str(entity))
    if entity == 'ORA_EXM_PER_DIEM_POLICY_VALUE':
        return 'ORA_EXM_PERDIEM_POLICY'
    return PARENT_BY_RATE.get(entity, entity.removesuffix('_LINE'))


def input_identity_fields(entity):
    """Workbook coordinates only, not a substitute for the full FSM key."""
    if entity == 'ORA_EXM_PER_DIEM_POLICY_VALUE':
        from per_diem_profile import VALUE_IDENTITY
        return tuple(VALUE_IDENTITY)
    if not entity.endswith('_LINE'):
        owning_policy(entity)  # Reject unknown entities, even on parent rows.
        return ('PolicyName',)
    fields = (owning_policy(entity)+'.PolicyName', 'StartDate', 'EndDate')
    if entity == 'ORA_EXM_MILEAGE_LINE':
        fields += ('TypeOfRateCode', 'PassengerThreshold', 'AdditionalRateCode', 'CalculationMethodCode')
    if entity == 'ORA_EXM_PERDIEM_POLICY_LINE':
        fields += ('TypeOfLineCode', 'LineHours', 'LineMinutes')
    return fields


def submitted_identity_records(records):
    """Retain every workbook identity coordinate when checking serialized rows."""
    return [{'entity': r['entity'], 'values': {
        field: r['values'].get(field, '') for field in input_identity_fields(r['entity'])
    }, 'shared_entities': []} for r in records]


def allowed_input(entity, field):
    if entity == 'ORA_EXM_PER_DIEM_POLICY_VALUE':
        # Identity inspection only. There is no workbook value sheet; only the
        # builder's source-bound existing-value effect path can serialize it.
        return field in input_identity_fields(entity)
    if entity in EXPANDED_ENTITIES:
        from expanded_category_intake import allowed_input as expanded_allowed
        return expanded_allowed(entity, field)
    if entity not in ENTITIES:
        return False
    if entity == 'ORA_EXM_ENTERTAINMENT_POLICY':
        from entertainment_profile import INPUTS
        return field in INPUTS
    if entity == 'ORA_EXM_ENTERTAINMENT_POLICY_LINE':
        return field in {entity[:-5]+'.PolicyName','StartDate','EndDate','SingleInstanceLimit','DailyLimit','YearlyLimit'}
    if entity == 'ORA_EXM_ACCOM_POLICY' and field in {'SingleInstanceLimitFlag','DailyLimitFlag'}:
        return False  # Daily limit is intrinsic; there is no corresponding CSV flag.
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
        rate = record['entity'].endswith('_LINE') or record['entity'] == 'ORA_EXM_PER_DIEM_POLICY_VALUE'
        parent = owning_policy(record['entity'])
        field = parent+'.PolicyName' if rate else 'PolicyName'
        name = values.get(field, record.get('policy_name'))
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Every selected row requires an exact Policy Name')
        if record.get('policy_name') is not None and record['policy_name'] != name:
            raise ValueError('Policy Name association differs from the supplied row')
        if names.setdefault((parent, name.casefold()), name) != name:
            raise ValueError('Case-only Policy Name association collision; use exact names')
        key = (record['entity'], name.casefold())
        if rate:
            key += tuple(values.get(f, '') for f in input_identity_fields(record['entity'])[1:])
        if key in identities:
            raise ValueError('Duplicate workbook policy/rate identity')
        identities.add(key)


def require_target_rate_identities(records, rows):
    """Reject ambiguous keys for selected policies without limiting row counts."""
    require_scoped_records(records)
    from mileage_rate_profile import P as mileage_parent, R as mileage_rate, IDENTITY
    names = {r['values'].get('PolicyName',r['values'].get(mileage_parent+'.PolicyName',r.get('policy_name')))
        for r in records if r['entity'] in {mileage_parent,mileage_rate}}
    for name in names:
        matches=[r for r in rows.get(mileage_rate,[]) if r.get(mileage_parent+'.PolicyName','').casefold()==name.casefold()]
        if any(r.get(mileage_parent+'.PolicyName')!=name for r in matches):
            raise ValueError('Case-only baseline Mileage rate association collision')
        keys=[tuple(r.get(f,'') for f in IDENTITY) for r in matches]
        if len(keys)!=len(set(keys)):
            raise ValueError('Ambiguous baseline Mileage rate identity for selected policy')
        no_start=[tuple(r.get(f,'') for f in IDENTITY if f!='StartDate') for r in matches]
        if len(no_start)!=len(set(no_start)):
            raise ValueError('Mileage alternate key excluding StartDate is duplicated in the selected policy')
    for parent in PARENTS:
        if parent == mileage_parent:
            continue  # Full nonuniform Mileage association/16-part key checked above.
        names = {r.get('values', {}).get('PolicyName', r.get('values', {}).get(parent+'.PolicyName', r.get('policy_name')))
                 for r in records if r['entity'].removesuffix('_LINE') == parent}
        for name in {n.casefold() for n in names}:
            matches = [r for r in rows.get(parent+'_LINE', []) if r.get(parent+'.PolicyName', '').casefold() == name]
            if {r[parent+'.PolicyName'] for r in matches} - names:
                raise ValueError('Case-only baseline rate association collision')
            fields = ('CurrencyCode','EndDate','GeoLocName','RoleName','StartDate','TypeOfRateCode','ZoneCode')
            if parent == 'ORA_EXM_ENTERTAINMENT_POLICY':
                fields = ('CurrencyCode','EndDate','StartDate','TypeOfAttendeCode','TypeOfRateCode','RoleName')
            if parent == 'ORA_EXM_ACCOM_POLICY':
                fields += ('SeasonEndDay','SeasonEndMonth','SeasonStartDay','SeasonStartMonth','GenderCode')
            if parent == 'ORA_EXM_MISCELLANEOUS_POLICY':
                from miscellaneous_profile import IDENTITY
                fields = tuple(IDENTITY)
            keys = [tuple(r.get(f, '') for f in fields) for r in matches]
            if len(keys) != len(set(keys)):
                raise ValueError('Ambiguous baseline rate identity for selected policy')
