# Auditing lookup dependencies

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| audit_lookup_scope | Target lookup, complete code population and set | Yes | Every row | Verify | Fresh supported read-only evidence | resolve_auditing_lookup_references | Export omits unmodified seeded codes | Resolve exact view/set/module and retain source evidence | Type, view, set, code existence |

Existing Expenses lookup types and reference data sets are prerequisites. This task
never creates them as a fallback. Oracle Run Book, identity and Data Loader privilege
checks remain with the owning core workflows. Reference evidence is refreshed before
packaging and cannot authorize execution. See references/destination-reference-contract.md.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AUDLK_DEP | step | 2 | resolve_dependency | success->AUDLK_LOOKUP | AUDLK_INPUT | stop | Always |
