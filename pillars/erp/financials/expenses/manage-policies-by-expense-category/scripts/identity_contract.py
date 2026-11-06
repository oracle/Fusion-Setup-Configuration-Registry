"""Fail closed on case-only portable-key collisions; never infer server matching."""
from workbook_intake import IntakeError


def select_identity(rows, values, fields, match_rule):
    if match_rule not in {'exact', 'casefold'}:
        raise IntakeError('Identity matching policy is unqualified')
    def key(row, fold=False):
        parts = tuple(row.get(field, '') for field in fields)
        if any(not isinstance(part, str) for part in parts):
            raise IntakeError('Portable identity values must be text')
        return tuple(part.casefold() for part in parts) if fold else parts
    wanted = key(values, match_rule == 'casefold')
    matches = [row for row in rows if key(row, match_rule == 'casefold') == wanted]
    if len(matches) > 1:
        raise IntakeError('Ambiguous baseline identity; no row may be selected arbitrarily')
    if match_rule == 'exact':
        folded = [row for row in rows if key(row, True) == key(values, True)]
        if len(folded) != len(matches):
            raise IntakeError('Case-only baseline identity collision; correct the exact key instead of inferring Fusion case matching')
    return matches
