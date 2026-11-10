# Customers Dependency Readiness


Before any runtime read or central handoff, apply
[governed read routes](../references/governed-read-routes.md). The task-only
revision selects task-owned customer read mapping and attempt evidence through
unchanged core clients, and unchanged core submission under its exact-candidate
approval/recovery contract. Missing actual evidence still blocks the applicable
check; never substitute SQL, invented facts or task-owned execution plumbing.

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Resolver | Value Source | Values to Fill | User Guidance |
|---|---|---|---|---|---|---|---|
| existing_customer_targets | Raw before-state evidence and proposed entity intent available for evaluation | Yes | Before ARCU.MATCH | resolve_customer_existing_targets | Supported candidate-bound API before collection and API target plan for existing targets, or detailed supplied identity/ownership/target-plan documents; reviewed provenance/completeness required | Evidence references for the following evaluator; not a predeclared passed match | Supply or refresh evidence through the assisted evidence contract; SQL is developer-only; retain ambiguity |
| configured_references | Profile classes, reference sets, geography, tax, receipt methods, DFF contexts/segments | Conditional | Corresponding fields supplied or product requires them |  | Reviewed setup or explicitly disclosed loader validation; no guessed setup | Preserve submitted values | These are dependencies; this task does not create missing reference setup |

## Dependency Order

| Order | Dependency | Reason |
|---|---|---|
| 1 | Input and parent consistency | Establish exact worksheet scope and user intent |
| 2 | Existing-target matching | Determine actual create/update/reuse effects before approval |
| 3 | Configured references | Verify through a documented path or explicitly accept eligible loader-validation gaps |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ARCU.DEPENDENCIES | step | 30 | resolve_dependency | ready->ARCU.MATCH;blocked->ARCU.ERROR | ARCU.DEFAULTS | stop | Before governed preview |
