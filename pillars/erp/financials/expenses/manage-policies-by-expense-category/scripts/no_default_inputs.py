"""Enforce explicit authoring choices; never infer Fusion minimum inputs/defaults."""

FIELDS = {
    'ORA_EXM_MEALS_POLICY': ('PolicyEnforcementCode',),
}


def enforce_no_default_inputs(entity, operation, supplied, baseline):
    """Return evidence of explicit/retained values without changing either map.

    This is a skill input restriction, not an Oracle requiredness declaration.
    Write acceptance, code domains, target eligibility and empty serialization
    still belong to their independent reviewed operation contracts.
    """
    if operation not in {'create', 'update'}:
        raise ValueError('No-default input policy requires create or update')
    explicit, retained = [], []
    for field in FIELDS.get(entity, ()):
        if field in supplied:
            value = supplied[field]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(entity+'.'+field+': supply an explicit nonblank choice; no default or clearing is requested')
            explicit.append(field)
        elif operation == 'create':
            raise ValueError(entity+'.'+field+': supply an explicit create choice; this skill does not request Fusion defaults')
        else:
            value = baseline.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(entity+'.'+field+': omitted update choice has no nonblank baseline value to preserve; supply a reviewed explicit choice')
            retained.append(field)
    return {'policy': 'no_implicit_business_defaults', 'explicit_fields': explicit,
            'retained_baseline_fields': retained, 'values_generated': False}
