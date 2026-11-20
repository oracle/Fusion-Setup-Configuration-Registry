"""Compare pod labels without changing evidence bytes or business identifiers."""


def environment_key(value):
    if (not isinstance(value, str) or not value or value.strip() != value
            or not value.isascii()):
        raise ValueError('Explicit ASCII target environment required')
    return value.lower()


def same_environment(left, right):
    try:
        return environment_key(left) == environment_key(right)
    except ValueError:
        return False


def same_binding(left, right):
    """Ignore only pod-label case; all other binding fields remain exact."""
    if not isinstance(left, dict) or not isinstance(right, dict):
        return False
    return (same_environment(left.get('environment'), right.get('environment'))
            and {k: v for k, v in left.items() if k != 'environment'}
            == {k: v for k, v in right.items() if k != 'environment'})
