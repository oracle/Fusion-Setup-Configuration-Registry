# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Input validation fails | Persist field and rule identifiers, classify as input validation, and stop before artifact generation |
| Catalog identity differs | Classify as catalog mismatch and stop; do not use a close task match |
| Data Loader authentication or UCM authorization fails | Classify as auth or authz; refresh a cached-token 401 or 403 once, then stop without falling back to a direct FSM import endpoint |
| Template or transport is unavailable | Classify as transport or environment; do not substitute an older or guessed import contract |
| Existing mapping is identical | Report it and stop without creating a duplicate |
| Existing mapping differs | Persist field-level differences and request direction |
| Concurrent change is detected | Invalidate approval and regenerate comparison and readiness |
| FBDI validation fails | Correct locally and regenerate; do not submit to discover known defaults |
| FBDI is selected for a standard FSM-supported mapping | Reclassify the route as a Data Loader FSM package and continue from the current same-task export; do not request an XLSM. |
| Multiple-source rules are selected without a Data Loader-authorized FBDI adapter | Stop before package generation; do not submit directly through FBDI or FSM. |
| Import process times out | Persist environment, mapping, job, ProcessId or requestId, last status, elapsed wait, and next-check path |
| Import process fails | Retrieve and persist ProcessLog or status payload, affected mapping, artifact fingerprint, and row errors |
| Partial preparation succeeds | Preserve valid artifacts with status, stage, errors array, and nonzero outcome; do not submit |
| Approval is absent | Classify as approval blocker and stop |
| Source COA is missing, disabled, or ambiguous | Report the exact lookup result and stop before mapping-task or structure export |
| Target COA is missing, disabled, or ambiguous | Report the exact lookup result and stop before mapping-task or structure export |
| Duplicate mapping name | Report GL_DUP_COA_MAPPING_NAME and stop for distinct-name or approved-update direction |
| Target segment rule is duplicated | Stop and require update or conflict resolution; do not generate a second rule |
| Source or target segment is unresolved | Stop before export and resolve segment metadata for the exact COA |
| Value set is unresolved | Stop before rule generation; do not infer a value set from a label |
| Value-set definition has zero or multiple exact matches | Stop before value lookup; report the segment-derived ValueSetCode and match count |
| Value-set child values are unavailable or paging is incomplete | Stop before constant, copy, or rollup validation; do not conclude that values are absent or populations match |
| Referenced value is missing, disabled, or ineffective | Stop before package generation and report the value set, value, accounting date, and independent-value context when applicable |
| Mapping method is invalid | Stop and resolve a template- or VO-proved method code |
| Rollup range is invalid | Stop when bounds are incomplete, reversed, duplicate, or overlapping |
| Account rule is routed to FBDI | Stop FBDI package generation; use the export-derived FSM task-CSV package submitted through core.data-loader instead |
| FSM account-rule contract is missing or altered | Stop before Data Loader upload; re-export the task and regenerate ORA_GL_AFF_MAP_RULE.csv with matching ASM_SETUP_CSV_METADATA.xml |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Missing, malformed, overlength, invalid, or conflicting business input | Correct input and rerun |
| Catalog mismatch | Task, offering, or functional-area identity does not match the catalog | Correct routing |
| Auth or authz | Credentials, token, role, or privilege prevents access | Use existing authentication and access diagnostics |
| Transport or environment | Network, endpoint, template download, or environment identity is unavailable | Restore access and refresh evidence |
| Fusion API | Supported read-only lookup returns a Fusion error | Persist response metadata and diagnose |
| Process timeout | Import remains nonterminal beyond the approved wait | Stop polling and report next-check path |
| Process failed | Load or import ends in error or warning requiring correction | Persist logs and correct original artifacts |
| Artifact persistence | Required project artifact cannot be safely written | Stop before live action |
| Approval blocker | Required explicit approval is missing or stale | Obtain fresh exact-action approval |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Before retry | Failure class, environment, stage, mapping, request or process ID, status, log reference, artifact fingerprint, and corrective action |
| Before Replace | Complete-set proof, omitted existing rules, deletion impact, and explicit approval |
| Before update | Field-level differences and fresh concurrency comparison |
| Before account-rule action | Account-rule identity, source criteria, target combination, overlaps, effective precedence, FSM task-CSV contract evidence, and import mode |

## Invalid Mapping Rule Recovery

For GL_COA_MAPPING_INVALD_MAP_RULE / GL-781639, inspect the full ProcessLog and package contents. A successful CoaMapping detail with a failed parent does not prove transaction rollback: check current mapping state before reusing the name. A header with no child rules is not an acceptable create test. Resolve the complete enabled target-segment inventory and valid values, correct the design, and rerun local validation and Data Loader/Task Hook preflight. Do not infer a specific internal validation condition from the generic message or reuse a prior artifact approval for changed bytes.

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Technical code is unresolved | Do not submit a live import to discover it |
| Mutation failed without idempotency evidence | Do not retry automatically |
| Mapping or approval target is ambiguous | Do not create, update, replace, import, or delete |
| Account rule appears in an FBDI import artifact | Do not upload the FBDI package |
| Account rule appears in an FSM package without current export-derived ORA_GL_AFF_MAP_RULE.csv metadata | Do not upload the package |
| Replace package is incomplete | Do not allow Replace |
| Secrets appear in diagnostics | Do not persist them |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COAMAP.ERROR | step | 15 | error_handler | stop->COAMAP.STOPPED | COAMAP.EXECUTE | stop | Live execution or verification fails |
| COAMAP.DONE_LIVE | terminal | 16 | terminal | none | COAMAP.VERIFY | stop | Read-only verification passes |
| COAMAP.DONE_EXISTING | terminal | 17 | terminal | none | COAMAP.LOOKUP | stop | Existing definition is identical |
| COAMAP.NEEDS_DIRECTION | terminal | 18 | terminal | none | COAMAP.LOOKUP | stop | Existing definition differs without approved direction |
| COAMAP.STOPPED | terminal | 19 | terminal | none | none | stop | Approval is declined or an execution error requires stop |
| COAMAP.DONE_PREPARED | terminal | 20 | terminal | none | COAMAP.PREVIEW | stop | Local package prepared; current target mapping comparison pending; no submission approval or live mutation |
| COAMAP.DONE_SUBMITTED | terminal | 21 | terminal | none | COAMAP.EXECUTE | stop | Data Loader accepted initiation; return its response immediately without polling or claiming import completion |
| COAMAP.DONE_PENDING | terminal | 22 | terminal | none | COAMAP.VERIFY | stop | A user-requested result check is in progress or not available yet; return current status without automatic polling or resubmission |
