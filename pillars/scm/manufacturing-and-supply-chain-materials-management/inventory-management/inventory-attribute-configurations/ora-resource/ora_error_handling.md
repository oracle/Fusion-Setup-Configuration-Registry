# Inventory Attribute Configurations Error Handling

## Source Evidence

| Source | Used For |
|---|---|
| Live Data Loader metadata check | `inventoryAttributeSetups` was visible in the configured environment during authoring. |
| Redwood `striping-attributes` action chains | Approved controls use Boolean values; Applicability Level and Source Type use the declared lookups. |
| User-provided lookup type | Status uses `ORA_INV_ATTR_STATUS`. |
| Authoring boundary | `core.data-loader` owns execution and the central per-run metadata preflight. |

## Error Situations

| Situation | What Should Happen |
|---|---|
| Approved checkbox control has a non-Boolean value | Stop before Data Loader handoff and report the field and accepted Boolean representation. |
| Applicability Level lookup returns no match, multiple matches, or a code/meaning conflict | Stop before Data Loader handoff and report the supplied values and resolver outcome. |
| Source Type lookup returns no match, multiple matches, or a code/meaning conflict | Stop before Data Loader handoff and report the supplied values and resolver outcome. |
| Status lookup returns no match, multiple matches, or a code/meaning conflict | Stop before Data Loader handoff and report the supplied values and resolver outcome. |
| Data Loader metadata is unavailable in a future environment | Stop and report the registered BO `inventoryAttributeSetups` and failed central preflight. Do not add direct REST write guidance. |
| Data Loader or Fusion rejects prepared data | Preserve the sanitized status, row identity, failure class, and message. Correct the source through the Data Loader workflow. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | An approved Boolean control has an unsupported representation. | Correct the input and restart task validation. |
| Reference lookup | Applicability Level, Source Type, or Status has no exact match, is ambiguous, or has conflicting code and Meaning. | Correct the supplied representation and rerun the resolver. |
| Data Loader availability | The central Data Loader metadata preflight fails. | Verify BO registration and target-environment access through `core.data-loader`. |
| Data Loader or Fusion validation | A prepared record is rejected downstream. | Correct data using the reported diagnostic; do not infer a direct REST workaround. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Central Data Loader metadata preflight fails | Do not create a task-local preflight rule or direct REST fallback. |
| A lookup or control-normalization error occurs | Do not select an approximate lookup match or coerce an unsupported value. |
| A Data Loader operation has an uncertain outcome | Do not resubmit until the Data Loader status is reconciled. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| IAC.DATA_LOADER_HANDOFF | decision | 30 | execution_gate | ready->IAC.DONE;blocked->IAC.HANDLE_ERROR;failure->IAC.HANDLE_ERROR | IAC.RESOLVE_STATUS | stop | Local validation and optional approved lookups have passed; hand preparation to core.data-loader. |
| IAC.HANDLE_ERROR | step | 40 | error_handler | handled->IAC.RETURN_ISSUES | none | stop | Any local validation, lookup, or Data Loader handoff issue. |
| IAC.RETURN_ISSUES | terminal | 50 | terminal | none | IAC.HANDLE_ERROR | stop | A blocking issue was classified and disclosed. |
| IAC.DONE | terminal | 60 | terminal | none | IAC.DATA_LOADER_HANDOFF | stop | Local task rules passed and core.data-loader owns subsequent validation and execution. |
