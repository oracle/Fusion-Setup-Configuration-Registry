# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Transport/API failure during an authorized read-only lookup | Record sanitized diagnostics and stop before retry. |
| Existing definition matches but requested values are unverified, ambiguous or incompatible | Handle VSET.CHECK_VALUE_SCOPE blocked; preserve the definition, report affected values/parents and stop. Definition existence alone cannot complete a Manage Values request. |
| Authentication 401/403 during an authorized read-only lookup | Refresh the cached token once, then repeat only that read-only lookup. If it still fails, record sanitized diagnostics and stop. |
| OAuth token expired or login callback did not complete | Record only environment, expiry/callback outcome, and next sign-in action; refresh authentication before polling an existing process, and do not submit a duplicate export without an identified process. |
| Package/member/header/metadata mismatch, including a values-only or metadata-plus-values partial ZIP | Classify as artifact persistence or catalog mismatch; stop before the parent approval workflow. Rebuild against the current same-task export contract; a valid header-only export is sufficient for a first-time definition. An existing-definition amendment needs a populated export or a validated template/spec package with reference-parent evidence in `ora_reference_lookups.md`. Retain every required member, especially `FND_APP_FLEX_VALUE_SET.csv`. |
| Reference-parent evidence has an unresolved, conflicting, defaulted, or guessed parent field | Classify as catalog mismatch or input validation. Stop before ZIP creation; obtain an authoritative field source or use a supported populated export. Never substitute a similarly named REST field or an inferred default. |
| FSM process log says a value row was skipped because its FND_APP_FLEX_VALUE_SET.csv parent row is missing | Classify as process failed with warnings. Verify the requested value through a fresh complete REST check, do not continue a dependent parent request, and rebuild a new exact package that includes one approved definition parent row for each value-row ValueSetCode. |
| FSM CSV parser rejects a row or its field count differs from the header | Classify as artifact persistence. Stop before preview; report the member, row, expected and actual field counts, then rebuild the affected rows from the exported header. |
| Import timeout or failure | Report task, environment, process/request ID, last status, elapsed time, and safe next-check path; retain sanitized diagnostics. |
| An approved default changes | Invalidate the prior approval and return to the parent approval workflow with the revised resolved values and readiness evidence. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Request field is incomplete or incompatible | Correct inputs and validate again. |
| Conditional definition mismatch | Fields do not match the selected ValidationType and ValueDataType | Correct the selected-combination fields, then regenerate the preview. |
| Validation source gap | Selected validation type has no target-supported Definition mapping | Obtain same-task export or active supported metadata; do not infer an FSM label-to-CSV contract. |
| Catalog mismatch | CSV code differs from export metadata | Correct to supported code. |
| Approval blocker | Live import approval is absent | Request approval for target, package, and operation. |
| Transport/environment | Authorized read-only lookup fails for a reason other than authentication | Record sanitized diagnostics and stop; do not retry automatically. |
| Authentication | Authorized read-only lookup returns 401/403 | Refresh the cached token once and repeat only that lookup; otherwise stop. |
| Artifact persistence | Package member/header/metadata shape is invalid | Reacquire validated export and rebuild smallest delta. |
| Input/design scope gap | Export inventory and approved business scope differ | Obtain approved values or scope confirmation; keep the baseline unchanged. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Import readiness | required files/columns, derived values and sources, unresolved gaps, readiness status, approval state |
| Lookup failure | environment, read-only purpose, failure class, sanitized message, next action |
| Post-import handoff | Owner: Fixed Assets parent; state: `accepted — pending parent verification`; immutable archive fingerprint, target, requested ValueSetCode and scope, and request ID. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Missing parent or package-source evidence | Do not generate a child value or guessed default. A template package is usable only with validated reference-parent evidence. |
| Live import | Do not execute without explicit approval immediately before the operation. |
| Failed import | Do not change defaults by trial-and-error or automatically resubmit the package. |
| Accepted import | Do not report the value set as created. The Fixed Assets parent applies fresh target-state verification and controls continuation; `core.data-loader` retrieves terminal status and ProcessLog. |

## Approved Import Execution and Handoff

After the approved immutable Value Sets package is accepted, report it as
`accepted — pending parent verification` and hand off its archive identity,
target, request ID, and definition/value verification criteria to the Fixed
Assets parent. The parent routes status and ProcessLog retrieval through
`core.data-loader`, applies fresh target-state verification, shows the
Post-Execution Verification Preview, and controls dependent-task progression.
This task does not perform post-import verification. A dependent task may reuse only the parent-verified
ValueSetCode and approved value scope; it must not create or infer context from
an accepted-but-unverified request.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| VSET.IMPORT_GATE | decision | 60 | execution_gate | approved->VSET.HANDED_OFF_TO_PARENT;approval_missing->VSET.HANDLE_APPROVAL | VSET.ENFORCE_DESIGN | stop | A validated package is proposed for live import; reaching the approved transition confirms only the approved submission gate, not target-state creation |
| VSET.HANDLE_INPUT | step | 70 | error_handler | handled->VSET.ISSUES | VSET.VALIDATE_INPUT | stop | Input is invalid |
| VSET.HANDLE_DEPENDENCY | step | 80 | error_handler | handled->VSET.ISSUES | VSET.RESOLVE_DEPENDENCIES | stop | Dependency is blocked |
| VSET.HANDLE_LOOKUP | step | 90 | error_handler | handled->VSET.ISSUES | VSET.LOOKUP_EXISTING | stop | Lookup is blocked |
| VSET.HANDLE_VALUES | step | 95 | error_handler | handled->VSET.ISSUES | VSET.CHECK_VALUE_SCOPE | stop | Requested value scope cannot be verified or safely added to the existing definition |
| VSET.HANDLE_DESIGN | step | 100 | error_handler | handled->VSET.ISSUES | VSET.ENFORCE_DESIGN | stop | Design rule blocks the package |
| VSET.HANDLE_APPROVAL | step | 110 | error_handler | handled->VSET.ISSUES | VSET.IMPORT_GATE | stop | Approval is absent |
| VSET.HANDED_OFF_TO_PARENT | terminal | 120 | terminal | none | VSET.IMPORT_GATE | continue | Accepted — pending parent verification. The Fixed Assets parent applies fresh target-state verification and controls dependent-task progression; core.data-loader retrieves terminal status and ProcessLog. |
| VSET.DONE_MATCH | terminal | 125 | terminal | none | VSET.CHECK_VALUE_SCOPE | stop | Existing definition matches and the request is definition-only; no import is needed |
| VSET.DONE_VALUES | terminal | 126 | terminal | none | VSET.CHECK_VALUE_SCOPE | stop | Existing definition and every requested value/parent/material field already match current verified state; no import is needed |
| VSET.ISSUES | terminal | 130 | terminal | none | none | stop | A blocker is handled |
