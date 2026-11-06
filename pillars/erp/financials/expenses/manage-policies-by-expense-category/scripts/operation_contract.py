"""Audit selected operation contracts without inventing field acceptance."""

FACTS = ('ownership', 'identity', 'required_fields', 'operations', 'cross_field')


def resolve_policy_operation_contract(entity, current, contract):
    """Return exact missing evidence; this is a local check, never a lookup."""
    findings = []
    def fail(code, message):
        findings.append({'code': code, 'entity': entity, 'message': message,
                         'failure_class': 'catalog_mismatch'})
    admitted = isinstance(current,dict) and current.get('ready') is True
    if not admitted:
        fail('operation_unqualified', entity + ': operation/entity ownership contract is incomplete')
        return findings
    sources = contract.get('sources', {})
    if not isinstance(sources, dict):
        sources = {}
    for fact in FACTS:
        ids = current.get(fact + '_source_ids')
        if not isinstance(ids, list) or not ids or any(not isinstance(i, str) or i not in sources or not sources[i] for i in ids):
            fail('missing_' + fact + '_evidence', entity + ' ' + fact + ' needs registered evidence')
    operations = current.get('operations')
    if (not isinstance(operations, list) or not operations or any(not isinstance(op, str) for op in operations)
            or len(operations) != len(set(operations)) or any(op not in {'create', 'update'} for op in operations)):
        fail('invalid_operation_allowlist', entity + ': reviewed create/update operation allowlist is invalid')
    if not isinstance(current.get('cross_field_rules'), list):
        fail('missing_cross_field_rules', entity + ': explicit resulting-state rule inventory required')
    return findings


def field_qualification(catalog, contract):
    """Inventory every workbook occurrence, including still unresolved inputs."""
    rows = []
    for sheet in catalog['sheets']:
        entity = sheet['entity']
        entry = contract.get('entities', {}).get(entity, {})
        for spec in sheet['columns']:
            if spec.get('workbook_only'):
                continue
            field = spec['csv_field']
            rule = entry.get('fields', {}).get(field, {})
            rows.append({'sheet': sheet['name'], 'entity': entity, 'field': field,
                         'create': rule.get('create', 'unresolved'),
                         'update': rule.get('update', 'unresolved'),
                         'entity_ready': entry.get('ready') is True,
                         'source_ids': rule.get('source_ids', [])})
    return rows
