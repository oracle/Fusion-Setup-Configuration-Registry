# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Configured REST host and active project Run Book host differ | Classify as transport/environment, stop before further external calls, invalidate cross-pod lookup evidence for this project, and request the correct environment selection through the owning workflow. |
| Required fields, singleton cardinality, unsupported organization-only or dual-dimension mapping, grouping value, or in-transit auto-close dependency is invalid | Stop before preview and identify the affected business object and row. |
| A read-only reconciliation or describe request fails | Classify as auth/authz, transport/environment, or Fusion API; retain sanitized diagnostics and stop before retry. |
| Current state is ambiguous | Do not choose a record or generate a PATCH path; request a precise reconciliation. |
| An approved organization name or coordinator name returns zero, multiple, inactive, noninventory, incomplete, or unpaged results | Stop the affected row before preview. Do not infer a code or worker ID; request a corrected name or unique source key and repeat the routed read-only lookup. |
| An existing singleton has no user-provided changed values or no returned ParameterValueId | Stop before preview. Ask the user for the exact values to update, then rerun the corresponding read-only Data Loader query to obtain ParameterValueId. |
| A design rule blocks the preview | Return the specific correction, including the selected-organization scope or the required owner/subinventory condition. |
| Preview approval is missing or stale | Do not import or authorize submission from this graph. Let core.data-loader apply its approval policy to the Task Hook preview for the validated immutable artifact. Missing or mismatched artifact, context or envelopes require fresh validation and approval. |
| Prepared artifact, target, mapping, task rules, or approval context changes | Stop submission and repeat preparation, task validation and approval for the corrected artifact and context. Never reconstruct an approval envelope. After approval, changes to the original source alone do not affect an intact approved artifact; submit only its persisted bytes without rereading the source. |
| Traceability default source rows are duplicated or scope is malformed | Return input validation with the affected rows; preserve -1 as the valid default marker and require positive IDs for exceptions. Do not request an organization name for the default. |
| Multiple existing traceability defaults or incomplete current-state evidence | Stop reconciliation; report the default count or unavailable evidence. Never select the first default or assume an inaccessible default does not exist. |
| Traceability plan would create a second default or leave none | Return a design blocker. Reconcile the one existing default as an update using its returned key, or plan one supported create if no default exists. Preserve other organization exceptions. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | A required request value or documented combination is missing or invalid | Correct the affected row; prepare a corrected immutable artifact and repeat validation before approval. |
| Catalog mismatch | A requested business object is not one of the six registered task business objects | Stop and correct the task routing. |
| Auth/authz or transport/environment or Fusion API | Describe or reconciliation cannot complete | Stop before retry; resolve the reported condition and preserve sanitized evidence. |
| Approval blocker | A live import lacks current explicit approval for its immutable preview | Delegate approval to core.data-loader under its current policy; Task Hook verifies the approved preview and archive but does not submit. |
| Design blocker | A required configuration semantic is not met | Correct the configuration; repeat artifact preparation and validation before preview. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Reconciliation or describe failure | Target environment, business object, read-only operation purpose, failure classification, sanitized message, and safe next action. |
| Preview approval | Present the core Data Loader approval report unchanged. Let Data Loader and Task Hook persist their prescribed internal preflight, preview, approval and validation-envelope artifacts. Keep this material out of task planning/checkpoint artifacts and never disclose credentials or source contents. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Uncertain singleton or item key | Do not manufacture ParameterValueId or submit an update. |
| Existing recallGlobalParams or recallItemValidationOrganizations row | Do not POST another singleton record. Do not use a user-provided ParameterValueId; pass only the value returned by the corresponding read-only business-object query to Data Loader. |
| Containment owner removal | Do not delete an existing mapping; use ActiveFlag false only through the approved supported update route. |
| Participating-organization scope change | Do not append selected organizations without reconciling the full desired scope. |
| Any live import | Do not bypass core.data-loader, preview, or the current explicit approval gate. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RECALL.PARAMETERS.HANDLE-INPUT-ERROR | step | 70 | error_handler | handled->RECALL.PARAMETERS.RETURN-ISSUES | none | stop | Input validation is invalid |
| RECALL.PARAMETERS.HANDLE-LOOKUP-ERROR | step | 80 | error_handler | handled->RECALL.PARAMETERS.RETURN-ISSUES | none | stop | A reconciliation, dependency, or describe lookup is blocked, ambiguous, unsupported, or failed |
| RECALL.PARAMETERS.HANDLE-DEPENDENCY-ERROR | step | 85 | error_handler | handled->RECALL.PARAMETERS.RETURN-ISSUES | none | stop | A required dependency is blocked |
| RECALL.PARAMETERS.HANDLE-DESCRIBE-ERROR | step | 90 | error_handler | handled->RECALL.PARAMETERS.RETURN-ISSUES | none | stop | Describe metadata is unsupported or incomplete |
| RECALL.PARAMETERS.HANDLE-DESIGN-BLOCKER | step | 100 | error_handler | handled->RECALL.PARAMETERS.RETURN-ISSUES | none | stop | A design rule blocks preview |
| RECALL.PARAMETERS.DONE-READY-FOR-PREVIEW | terminal | 120 | terminal | none | RECALL.PARAMETERS.ENFORCE-DESIGN | stop | Task rules passed; return ordered results to Task Hook for digest-bound preview, approval and archive verification before core.data-loader submission |
| RECALL.PARAMETERS.RETURN-ISSUES | terminal | 130 | terminal | none | none | stop | Validation, lookup, dependency, or design issues are handled |
