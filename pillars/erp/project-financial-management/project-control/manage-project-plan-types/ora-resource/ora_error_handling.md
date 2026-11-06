# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Authentication fails or times out before an export `ProcessId` is returned | Record that Fusion initiation did not occur, refresh authentication, and create the first export. Do not label it indeterminate or require recovery of a nonexistent process. |
| An export `ProcessId` was returned but polling or download was interrupted | Resume the exact recorded process; do not create another export automatically. |
| The invoking shell or agent reports no stdout, ProcessId, or artifact | Before retrying, inspect the configured export directory for a newly completed task-coded ZIP, validate its metadata and timestamp, and recover its ProcessId from the filename. Empty stdout is not evidence that the asynchronous export failed. |
| Export output is absent, empty, corrupt, premature, or missing target metadata | Do not treat it as a zero-row baseline. Wait for the recorded process to complete or report the exact artifact failure. A completed valid ZIP with header-only members is a valid zero-row baseline. |
| A lookup page or selective query fails | Record endpoint, query shape, status and failure class without configured row values. A failed query is not no-match evidence. Use only the verified complete-fetch or query strategy in the lookup owner; incomplete later pages block validation. |
| Required input is missing or a bound UI validator rejects a value | Disclose the missing or invalid field and stop before retry. |
| Serialized child fields are missing | Return all supported findings together, including member, row, attribute and missing/blank state. Revalidate the whole corrected archive; do not repair only the first server error or only the parent row. |
| A required value has no proven default | Return blocking UNRESOLVED_REQUIRED_INPUT and request the exact missing business choice or source evidence. Never substitute blank or blanket N; this differs from unsupported reference membership. |
| Input wording resolves to zero or multiple canonical members | Identify the scoped CSV column and plausible meanings; request only the missing disambiguator. Do not demand English, an exact label, or a known code. |
| Dynamic reference or feature validation route is unsupported | Record REFERENCE_UNRESOLVED with blocking=false and continue. Preserve proven supplied representation, disclose skipped checks, and never mark the value validated. Known incompatibility, ambiguous input and failures of supported reads remain separate errors. |
| A UI LOV has no exported CSV mapping, or an exported reference has no applicable task control | Preserve the mismatch as a research blocker for requested changes. Do not invent a header, reuse an unrelated flag, or skip validation. |
| A protected attached or seed-data control is selected | Explain that the source renders the control read-only and stop. |
| The current task export cannot represent the requested change or the import reports an error | State the package-schema or import result and stop that unsupported option; do not make the skill dependent on UI maintenance or invent a direct API or different file contract. |
| The UI displays the source warning dialog for a default plan type or currency condition | Preserve the warning context, require user/product-owner resolution, and do not auto-confirm it. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| INPUT_ISSUES | Input validation fails | Return the exact missing or invalid fields. |
| SOURCE_INTENT_INVALID / SOURCE_INTENT_MISMATCH | The shared-conversion source control is invalid, contradicts the canonical action, or its persistent destinations differ | Reconcile the original request through preparation and rebuild the preview; do not drop intent or patch approved bytes. |
| UNMATERIALIZED_DEFAULT | Submitted synchronized options have an empty buffer in the final ZIP | Reprepare through the task helper to apply the 0-day save default and rebuild the preview. Do not request extra business input or patch approved bytes. |
| INACTIVE_OPTION | A requested activation is incompatible with the effective control state | Explain the prerequisite choice; do not change it silently. |
| CONFLICTING_CONVERSION_ATTRIBUTES | Shared conversion copy disagrees with an explicitly supplied destination | Resolve the conflicting business choice before preparation. |
| DESTRUCTIVE_CURRENCY_RESET_EXCLUDED | Disabling multicurrency would delete retained currency rows | Preserve the current setting; deletion is excluded even when implicit in another action. |
| INSERT_IDENTITY_EXISTS | An insert identity exists or is duplicated in the request | Use retained-row update intent or correct the duplicate; do not silently upsert. |
| RENAME_LANGUAGE_UNRESOLVED | Selected language lacks a unique complete retained translation | Acquire the fresh translation row through the same task export; never invent its SourceLang. |
| RENAME_IDENTITY_CONFLICT | The requested new name conflicts with another retained identity | Resolve the name; never create a replacement parent or delete the old one. |
| DUPLICATE_SOURCE_UNRESOLVED | Copy source parent/options are absent or ambiguous | Identify one source from a fresh task baseline before copying. |
| UNMAPPED_COPY_CONTEXT | Copy would omit budgetary-control children absent from the task package | Report the exact boundary; do not claim a complete copy or select another execution route. |
| UNSUPPORTED_PLANNING_CODE | Separate planning code has no verified standard mapping | Resolve the requirement before acquisition; do not reuse PlanTypeCode or request a validation waiver. |
| REFERENCE_MISSING | Complete authorized acquisition has no matching visible identity | Reconcile wording and visibility; do not claim global absence. |
| REFERENCE_AMBIGUOUS | Multiple eligible identities remain | Request a distinguishing code, profile ID or calendar context. |
| REFERENCE_INACCESSIBLE | Declared REST authorization/transport fails | Check the selected identity, connection and read privileges; never treat failure as no match. |
| REFERENCE_INCOMPATIBLE | A profile exists but not for the selected calendar, or a profile is requested for N/A | Correct the calendar/profile requirement; never silently substitute a profile. |
| REFERENCE_CONTEXT | Evidence belongs to another environment, identity, language or run, or target mapping is absent | Reacquire through the declared route with verified scope. |
| REFERENCE_INCOMPLETE | Required fields, page completeness or unique source identities are absent | Complete a fresh acquisition before resolving; preserve the failed stage. |
| REFERENCE_UNRESOLVED | Reference membership, eligibility or feature validation has no supported route | Warning, blocking=false; continue supported checks and normal preview/approval, listing affected fields and skipped checks. No routine waiver or manual research evidence is required |
| ROUTE_ISSUES | Readiness is missing | Obtain the current task export and prepare the task-level FSM validation and approval route. |
| DESIGN_ISSUES | A design gate blocks the request | Correct the scope or select an eligible plan type. |
| PREVIEW_READY | All supported applicable reference, design and exact-package checks pass for preview-only; unresolved/nonblocking warnings are disclosed | Present the immutable ZIP and SHA-256; stop without setup mutation or import approval. |
| ALL_GOOD | The task-level FSM submission gate is satisfied | Submit only through the approved Data Loader route; a successful preview does not establish approval. |

## Disclosure Rules

The task preview adds field-specific unresolved-reference warnings for supplied
period profiles, budget targets and forecast targets. Preserve all three
groups in the consultant-facing preview; a passing ZIP check cannot establish
their target eligibility. Retain any independently acquired current evidence
separately and state exactly what it proves. Missing copy destinations for an
explicit shared-conversion source input return SOURCE_INTENT_MISMATCH before
preview or approval; they cannot be waived by narrative rule results.

| Gate | What Must Be Shown |
|---|---|
| Before a configuration mutation | Exact task code, selected branch, validated facts, each unresolved/nonblocking field and skipped check, route boundary, and the explicit approval requirement. |
| Preview with unresolved checks | State that the affected supplied values are unverified and may be rejected by Fusion; absence of REST alone does not prevent preview or normal approval. |
| Package integrity | Report ZIP/CSV structure, metadata identity and the digest of the actual bytes separately from field validation. A readable ZIP alone is not a valid task payload. |
| Task-contract validation | Report executable field and relationship findings independently of caller-supplied rule results. Blocking findings cannot be waived by narrative success or a registry-readiness override. |
| Deferred checks | List target membership, editability, environment-specific configuration and other checks that the local validator did not perform. Never describe them as passed. |
| Server-side validation | Report not run until Fusion actually validates a submitted package. Local success does not prove import success; retain the process result and independent readback separately. |
| On a blocked result | Blocking rule, source-backed reason, and one safe next action. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| No current task export or package-schema evidence is available | Do not create a payload, call an endpoint, or infer a file format. |
| A user approval is absent | Do not mutate task configuration. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PJO.PPT.EXECUTION_GATE | decision | 40 | execution_gate | preview-ready->PJO.PPT.PREVIEW_READY;approved-fsm-route->PJO.PPT.DONE;approval-or-route-missing->PJO.PPT.ROUTE_ISSUES | PJO.PPT.DESIGN_GATE | stop | After supported applicable rules and exact package validation, with unresolved warnings disclosed: preview-only may return without import approval; submission still requires checksum-bound approval |
| PJO.PPT.INPUT_ISSUES | terminal | 50 | terminal | none | none | stop | Input validation fails |
| PJO.PPT.ROUTE_ISSUES | terminal | 60 | terminal | none | none | stop | Readiness or approval is missing |
| PJO.PPT.DESIGN_ISSUES | terminal | 70 | terminal | none | none | stop | Design enforcement blocks the request |
| PJO.PPT.PREVIEW_READY | terminal | 75 | terminal | none | PJO.PPT.EXECUTION_GATE | stop | Validated immutable preview prepared; no setup mutation or import approval claimed |
| PJO.PPT.DONE | terminal | 80 | terminal | none | PJO.PPT.EXECUTION_GATE | stop | Approved FSM route is ready |
