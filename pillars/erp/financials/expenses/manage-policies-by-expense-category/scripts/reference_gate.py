"""Keep unqualified target lookups out of candidate construction.

This gate does not perform a lookup or classify a supplied reference as invalid.
A permanent configuration flag cannot bind a result to an operation or target.
"""

LINE_IDENTITIES = frozenset({'RoleName', 'GeoLocName', 'RawCountry', 'RawState',
                             'RawCounty', 'RawCity', 'ZoneCode'})
LOOKUP_INPUTS = {
    'ORA_EXM_MEALS_POLICY': frozenset({'CurrencyCode'}),
    'ORA_EXM_MEALS_POLICY_LINE': LINE_IDENTITIES | {'CurrencyCode', 'GradeCode'},
    'ORA_EXM_ACCOM_POLICY': frozenset({'CurrencyCode'}),
    'ORA_EXM_ACCOM_POLICY_LINE': LINE_IDENTITIES | {'CurrencyCode', 'GradeCode'},
    'ORA_EXM_ENTERTAINMENT_POLICY': frozenset({'CurrencyCode','NumOfAttendeesCurrCode'}),
    'ORA_EXM_ENTERTAINMENT_POLICY_LINE': frozenset({'RoleName','CurrencyCode','TypeOfAttendeCode'}),
    'ORA_EXM_CARRENTAL_POLICY': frozenset({'CurrencyCode'}),
    'ORA_EXM_CARRENTAL_POLICY_LINE': LINE_IDENTITIES | {'CurrencyCode'},
    'ORA_EXM_MISCELLANEOUS_POLICY': frozenset({'CurrencyCode'}),
    'ORA_EXM_MISCELLANEOUS_POLICY_LINE': LINE_IDENTITIES | {'CurrencyCode','GenderCode','GradeCode'},
    'ORA_EXM_MILEAGE_POLICY': frozenset({'CurrencyCode'}),
    'ORA_EXM_PERDIEM_POLICY': frozenset({'CurrencyCode'}),
}


def require_qualified_reference_route(entity, supplied, entity_contract, *, currency_context=None, resulting_values=None):
    """Require operation-bound currency evidence; stop other unqualified inputs.

    Includes supplied unchanged values: eligibility can change independently of
    a policy's stored code. Omitted retained values need checking when the
    reviewed operation requires it. Never infer that requirement from a flag.
    The immutable task inventory prevents a caller dropping reference_fields
    from silently bypassing known reference inputs.
    """
    declared = entity_contract.get('reference_fields', [])
    retained = entity_contract.get('validate_retained_reference_fields', [])
    for label, fields in [('reference_fields', declared),
                          ('validate_retained_reference_fields', retained)]:
        if (not isinstance(fields, list)
                or any(not isinstance(field, str) or not field for field in fields)
                or len(fields) != len(set(fields))):
            raise ValueError(entity + ': malformed ' + label)
    required = ((LOOKUP_INPUTS.get(entity, frozenset()) | set(declared))
                & set(supplied)) | set(retained)
    if entity == 'ORA_EXM_ENTERTAINMENT_POLICY':
        if not isinstance(resulting_values,dict):
            raise ValueError('Entertainment: no operation-bound target reference route is qualified without the resolved resulting parent')
        required = required | {f for f in LOOKUP_INPUTS[entity] if resulting_values.get(f)}
    review = None
    if entity == 'ORA_EXM_MISCELLANEOUS_POLICY':
        if not isinstance(resulting_values, dict):
            raise ValueError('Miscellaneous reference checks require the resolved resulting parent')
        if resulting_values.get('RateTypeCode') in {'LIMIT', 'BOTH'}:
            required = required | {'CurrencyCode'}
            if currency_context is not None and currency_context.get('receipt') is None:
                raise ValueError('Miscellaneous monetary limits require an operation-bound currency receipt')
        elif resulting_values.get('RateTypeCode') == 'PERCENT' and not resulting_values.get('CurrencyCode'):
            required = required - {'CurrencyCode'}
    if 'CurrencyCode' in required and currency_context is not None and not currency_context.get('receipt'):
        raise ValueError(entity+': operation-bound currency receipt required')
    if entity == 'ORA_EXM_ENTERTAINMENT_POLICY' and currency_context is not None:
        from currency_receipt import verify
        reviews = []
        for field,key in [('CurrencyCode','resulting_currency'),('NumOfAttendeesCurrCode','resulting_threshold_currency')]:
            code = currency_context.get(key)
            if code:
                item = verify(currency_context['receipt'],currency_context['binding'],entity,
                    currency_context['policy_name'],currency_context['operation'],code)
                if field in supplied and supplied[field] != code:
                    raise ValueError('Currency receipt value differs from supplied '+field)
                item['field'] = field
                reviews.append(item)
                required = required - {field}
        if required:
            raise ValueError(entity+': unresolved operation-bound currency reference: '+','.join(sorted(required)))
        return {'fields':reviews,'boundary':'Eligibility only; no import authority'}
    if 'CurrencyCode' in required and currency_context is not None:
        if not currency_context.get('receipt'):
            raise ValueError(entity+'.CurrencyCode: operation-bound currency receipt required')
        from currency_receipt import verify
        review = verify(currency_context['receipt'], currency_context['binding'], entity,
                        currency_context['policy_name'], currency_context['operation'],
                        currency_context['resulting_currency'])
        if 'CurrencyCode' in supplied and supplied['CurrencyCode'] != review['value']:
            raise ValueError('Currency receipt value differs from supplied value')
        required = required - {'CurrencyCode'}
    if required:
        raise ValueError(entity + '.' + ','.join(sorted(required))
                         + ': no operation-bound target reference route is qualified; '
                         'static reference_verified flags and captured developer results '
                         'cannot authorize candidate construction')
    return review
