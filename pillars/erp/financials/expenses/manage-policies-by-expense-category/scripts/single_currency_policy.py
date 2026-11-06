"""User-authorized SINGLE policy mode; not inferred from blank workbook cells.

This scope restriction does not qualify CSV acceptance or derive child currency.
"""
MEALS = 'ORA_EXM_MEALS_POLICY'
MODE = 'SINGLE'


def require_existing_single_currency(parent):
    if parent.get('CurrencyOptionCode') != MODE:
        raise ValueError('Only existing Single currency / SINGLE Meals policies are supported; currency-mode conversion is not supported')


def policy_constants(entity, operation, before):
    if entity != MEALS:
        return {}
    if operation == 'update':
        require_existing_single_currency(before)
    elif operation != 'create':
        raise ValueError('Single-currency policy requires create or update')
    return {'CurrencyOptionCode': MODE}
