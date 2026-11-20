"""User-authorized SINGLE policy mode; not inferred from blank workbook cells.

This scope restriction does not qualify CSV acceptance or derive child currency.
"""
MEALS = 'ORA_EXM_MEALS_POLICY'
MODE = 'SINGLE'


def require_existing_single_currency(parent):
    if parent.get('CurrencyOptionCode') != MODE:
        raise ValueError('Only existing Single currency / SINGLE Meals or Accommodations policies are supported; currency-mode conversion is not supported')


def policy_constants(entity, operation, before, supplied=None):
    if entity=='ORA_EXM_MISCELLANEOUS_POLICY':
        # The reviewed create profile clears the EO SINGLE default in PERCENT
        # mode and explicitly supplies SINGLE only for monetary modes. Existing
        # updates retain their original immutable currency context unchanged.
        if operation=='create' and (supplied or {}).get('RateTypeCode')in {'LIMIT','BOTH'}:
            return {'CurrencyOptionCode':MODE}
        return {}
    if entity == 'ORA_EXM_ENTERTAINMENT_POLICY':
        if (supplied or {}).get('EnabledRateLimitFlag', before.get('EnabledRateLimitFlag')) != 'Y':
            return {}
        if operation == 'update':
            require_existing_single_currency(before)
        return {'CurrencyOptionCode':MODE}
    if entity=='ORA_EXM_MILEAGE_POLICY':
        if operation=='create':return {'CurrencyOptionCode':MODE}
        if operation=='update':return {}  # Preserve existing Mileage update values/review.
        raise ValueError('Single-currency policy requires create or update')
    if entity not in {MEALS, 'ORA_EXM_ACCOM_POLICY', 'ORA_EXM_CARRENTAL_POLICY'}:
        return {}
    if operation == 'update':
        require_existing_single_currency(before)
    elif operation != 'create':
        raise ValueError('Single-currency policy requires create or update')
    return {'CurrencyOptionCode': MODE}
