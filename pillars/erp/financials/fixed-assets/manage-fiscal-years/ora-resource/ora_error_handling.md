# Manage Fiscal Years: Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Transport/API failure during an authorized read-only lookup | Record sanitized diagnostics. When the reference-lookup procedure declares a current same-target FSM export fallback, first search completed local export artifacts and validate the newest candidate's target, task, completion, ZIP integrity, and required business field. Compare recent same-target candidates when available. Poll an identified matching process before starting another export. Start a new data export only when no valid completed artifact or identified process provides complete, unambiguous evidence. The fallback does not authorize a configuration import or any other Fusion change. |
| One ledger in a multi-ledger request already exists or differs | Report the exact ledger, fiscal year, and comparison result. Isolate that track as already complete or awaiting an update-or-new decision; continue validation for unaffected tracks. |
| Bulk input has invalid rows | Return a row-level exception report and exclude only the invalid rows from package preparation. Preserve their input keys and validation failures. |
| A bulk batch fails or times out | Preserve the batch manifest, immutable archive identity, and process details. Do not resubmit the failed batch or submit dependent calendar batches until a recovery decision is approved. |
| Authentication 401 during an authorized read-only lookup | Refresh the cached token once, then repeat only that read-only lookup. If it still fails, use the task-declared current same-target FSM export fallback when available; otherwise record sanitized diagnostics and stop. |
| Authorization 403 during an authorized read-only lookup | Record sanitized diagnostics and use the task-declared current same-target FSM export fallback when available. Do not request additional read access solely to replace an adequate export; stop only if the fallback is unavailable, incomplete, or ambiguous. |
| OAuth token expired or login callback did not complete | Record only environment, expiry/callback outcome, and next sign-in action; refresh authentication before polling an existing process, and do not submit a duplicate export without an identified process. |
| Package/member/header/metadata mismatch | Classify as artifact persistence or catalog mismatch; stop before preview. |
| FSM CSV parser rejects a row or its field count differs from the header | Classify as artifact persistence. Stop before preview; report the member, row, expected and actual field counts, then rebuild the affected rows from the exported header. |
| Import timeout or failure | Report task, environment, process/request ID, last status, elapsed time, and safe next-check path; retain sanitized diagnostics. |
| Import accepted or related job succeeded but the requested fiscal year is not visible | Classify as a target-state verification failure. Capture the Data Loader request ID, completed FSM process log, and exact requested fiscal-year name; do not retry automatically. |
| Terminal-successful FSM process but requested fiscal-year fields remain unchanged | Classify as a target-state verification failure. Preserve the immutable archive fingerprint, completed FSM process log, and pre/post evidence; do not retry or report the fiscal year as created. |
| Data Loader/wrapper and setup-task statuses disagree | Treat the import as unresolved rather than succeeded or failed solely from either status. Preserve both statuses, stop before automatic resubmission, and escalate the request-ID/status correlation to the owning Data Loader/FSM team. |
| Post-import FSM process result is pending or times out | Record its process ID, last status, elapsed wait, and target environment. Do not submit a duplicate import or infer that the import failed. |

## Approved Import Execution and Handoff

Before requesting import approval, render a Final ZIP Preview for the exact immutable Fiscal Years package. Show ZIP filename, SHA-256 hash, target, requested fiscal-year scope, member names, and parent, translation, and date-row counts. Approval applies only to that displayed package and target.

After the one execution approval for that immutable Fiscal Years package, submit it immediately. Submit without requesting any further user response before submission.

After Fusion accepts initiation, report the request as `accepted — pending parent verification` and hand off its archive identity, target, request ID, and fiscal-year verification criteria to the Fixed Assets parent. The parent routes terminal-status and ProcessLog retrieval through `core.data-loader`, applies fresh target-state verification, shows the Post-Execution Verification Preview, and controls dependent-task progression. This task does not poll automatically or report the fiscal year as created.

After the parent reports verified completion, any dependent task reuses the exact verified Fiscal Year Name and date-row coverage as context. It must not create, infer, or substitute fiscal-year context from an accepted-but-unverified request.
## Failure Classes

| Failure class | Safe next action |
|---|---|
| Input validation | Return to [ora_input_validation.md](ora_input_validation.md), identify every missing or invalid business value together, and revalidate. |
| Lookup evidence | Return to [ora_reference_lookups.md](ora_reference_lookups.md), retain sanitized diagnostics, and stop until complete target evidence is available. |
| Dependency | Return to [ora_dependency_readiness.md](ora_dependency_readiness.md) and resolve the blocking prerequisite or missing user decision. |
| Design enforcement | Return to [ora_design_enforcement.md](ora_design_enforcement.md) and correct the rejected design or obtain the required approval. |
| Approval | Keep the immutable archive in review state until explicit approval is received. |
| Import process | Report the task, target, process or request ID, last status, elapsed time, and safe next-check path. |
| Transport/environment | Authorized read-only lookup fails for a reason other than authentication; record sanitized diagnostics and stop. |
| Authentication | Authorized read-only lookup returns 401; refresh the cached token once and repeat only that lookup, then use the task-declared export fallback or stop. |
| Authorization | Authorized read-only lookup returns 403; use the task-declared current same-target FSM export fallback. Stop only when that evidence is unavailable, incomplete, or ambiguous. |
| Artifact persistence | Package member, header, or metadata shape is invalid; reacquire the validated export and rebuild the smallest delta. |
| Catalog mismatch | CSV code differs from export metadata; correct to the supported code. |
| Target-state verification failure | The completed FSM process log reports relevant errors, or the dependent calendar verification cannot find the exact requested fiscal year or expected material fields; preserve import/process-log evidence and do not claim creation or automatically resubmit. |
| Conflicting process status | Wrapper/Data Loader and setup-task process results disagree; preserve both statuses, escalate the request-ID/status correlation to the owning Data Loader/FSM team, and require target-state verification before any retry decision. |

## Disclosure Rules

| Situation | What must be shown |
|---|---|
| Pre-import block | Failure class, concise business explanation, owner resource, and next safe action. |
| Existing-state difference | The requested and existing business definitions, plus the update-or-new choice. |
| Import result | Archive identity, target, process or request ID, terminal status, and submitted, created, skipped, warned, or failed counts when available. |
| Lookup failure | Environment, read-only purpose, failure class, sanitized message, and next action. |
| Post-import handoff | Owner: Fixed Assets parent; state: `accepted — pending parent verification`; immutable archive fingerprint, target, requested fiscal-year name and scope, and request ID. |

## Refusal Rules

| Situation | What must not happen |
|---|---|
| Unresolved validation, lookup, dependency, or design rule | Do not prepare or submit an import. |
| Missing approval | Do not submit a live import. |
| Failed, pending, or timed-out import | Do not alter defaults by trial and error or automatically resubmit. |
| Terminal import result | Do not perform fresh-export or post-import BOSS verification in this skill. |
| Submitted import without target-state evidence | Do not report the fiscal year as created solely because an archive was accepted or a related job succeeded. |
| Conflicting or pending process states | Do not cancel, resume, or resubmit until the exact target-state result or an approved recovery decision is available. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FY.IMPORT_GATE | decision | 80 | execution_gate | approved->FY.HANDED_OFF_TO_PARENT;approval_missing->FY.HANDLE_APPROVAL | FY.ENFORCE_DESIGN | stop | The Final ZIP Preview identifies one validated immutable package for live import. |
| FY.HANDLE_INPUT | step | 90 | error_handler | handled->FY.ISSUES | FY.VALIDATE_INPUT | stop | Input is invalid. |
| FY.HANDLE_DEPENDENCY | step | 100 | error_handler | handled->FY.ISSUES | FY.RESOLVE_DEPENDENCIES | stop | A prerequisite or required decision is unresolved. |
| FY.HANDLE_LOOKUP | step | 110 | error_handler | handled->FY.ISSUES | FY.LOOKUP_EXISTING | stop | Lookup evidence is missing, different, or ambiguous. |
| FY.HANDLE_DESIGN | step | 120 | error_handler | handled->FY.ISSUES | FY.ENFORCE_DESIGN | stop | A design rule blocks the request. |
| FY.HANDLE_APPROVAL | step | 130 | error_handler | handled->FY.ISSUES | FY.IMPORT_GATE | stop | Import approval is missing. |
| FY.HANDED_OFF_TO_PARENT | terminal | 170 | terminal | none | FY.IMPORT_GATE | continue | Fiscal Years import is accepted — pending parent verification. |
| FY.DONE_EXISTS | terminal | 180 | terminal | none | FY.RESOLVE_DEPENDENCIES | continue | Matching fiscal year already exists or user selected verified reuse. |
| FY.ISSUES | terminal | 190 | terminal | none | none | continue | Any validation, lookup, dependency, design, or approval issue. |
