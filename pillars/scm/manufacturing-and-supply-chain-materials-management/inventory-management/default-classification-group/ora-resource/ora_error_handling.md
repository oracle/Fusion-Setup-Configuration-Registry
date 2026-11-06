# Default Classification Group Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| A catalog, criteria entity, or criteria condition lookup has no exact result, multiple results, conflicting supplied representations, or incomplete pagination | Stop before Data Loader handoff and show the affected field, resolver name, and correction needed. |
| A literal criterion value is blank or has an unsupported shape | Stop before Data Loader handoff and request a nonblank text value. |
| A criteria entity lookup resolves to a disabled or ineffective value | Stop and require an enabled effective ORA_MSC_ROP_CRITERIA_TYPE value. |
| Required parent context, child operation, or child identity input is absent | Stop and request only the missing documented fields. |
| Data Loader metadata is unavailable or rejects prepared data | Preserve its sanitized diagnostic and classification. Do not create a task-local metadata preflight or direct REST write fallback. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | A documented required input, shape, or normalization rule fails | Correct the supplied task input and validate again. |
| Lookup readiness | A named resolver has no exact eligible row, multiple rows, or an inaccessible/incomplete response | Provide an exact identifier or display value and rerun the named resolver. |
| Data Loader availability | Classification Groups metadata cannot be read in the selected environment | Verify external BO registration and environment access before retrying. |
| Data Loader validation | Data Loader or Fusion rejects prepared data | Correct the source from its returned diagnostic. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Lookup failure | The affected field, supplied representation, resolver name, exact request path, match count when available, and correction needed. |
| Data Loader handoff | Task name, task code, business object, child operation, resolved parent context, canonical criteria entity and condition codes, and literal criteria values. |
| Data Loader failure | The Data Loader request or process identifier when available, failed row identity, sanitized message, stage, and recommended next action. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| A display value or code is ambiguous | Do not fuzzy-match, contains-match, or select the first row. |
| A lookup route or BO metadata is unavailable | Do not route to direct REST POST, PATCH, DELETE, or a task-local metadata preflight. |
| A Data Loader outcome is uncertain | Do not resubmit until read-only status verification clarifies the result. |
| A child source contains a manually constructed REST composite address | Do not use it as a surrogate identifier. Preserve the BO-declared parent and child user keys and let the registered BO construct the REST address. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DCG.DATA_LOADER_HANDOFF | decision | 60 | execution_gate | ready->DCG.DONE;blocked->DCG.HANDLE_ERROR;failure->DCG.HANDLE_ERROR | DCG.RESOLVE_EXISTING_GROUP | stop | Before handing normalized group-header or child operations to core.data-loader |
| DCG.HANDLE_ERROR | step | 70 | error_handler | handled->DCG.RETURN_ISSUES | none | stop | Any local validation, lookup, or Data Loader issue |
| DCG.RETURN_ISSUES | terminal | 80 | terminal | none | none | stop | A blocking issue was classified and disclosed |
| DCG.DONE | terminal | 90 | terminal | none | DCG.DATA_LOADER_HANDOFF | stop | Local task rules passed and Data Loader owns final validation and execution |
