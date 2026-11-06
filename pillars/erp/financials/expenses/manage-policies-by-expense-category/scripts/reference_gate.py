"""Keep unqualified target lookups out of candidate construction.

This gate does not perform a lookup or classify a supplied reference as invalid.
A permanent configuration flag cannot bind a result to an operation or target.
"""

LINE_IDENTITIES = frozenset({'RoleName', 'GeoLocName', 'RawCountry', 'RawState',
                             'RawCounty', 'RawCity', 'ZoneCode'})
LOOKUP_INPUTS = {
    'ORA_EXM_MEALS_POLICY': frozenset({'CurrencyCode'}),
    'ORA_EXM_MEALS_POLICY_LINE': LINE_IDENTITIES | {'CurrencyCode', 'GradeCode'},
}


def require_qualified_reference_route(entity, supplied, entity_contract, *, currency_context=None):
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
    review = None
    if 'CurrencyCode' in required and currency_context is not None:
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
