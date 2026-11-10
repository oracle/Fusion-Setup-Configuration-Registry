# Manage Data Access for Users Error Handling

## Common Section

### Task-Specific Failures

The identity, membership, context, and conflicting-intent rows below apply to mutations. Customer REST reads use their own read-scope resolver and outcomes.

| Situation | Classification | Required Result |
|---|---|---|
| Action, user, role, context, or required context value is missing | Input validation | Ask only for the missing business value; a missing-context decision must follow resolve_mutation_context_label |
| Zero eligible users remain | Identity not found | Stop without substituting another user |
| Multiple distinct eligible users remain | Ambiguous identity | Present `Username`, `UserId`, and `GUID`; require an exact identifier choice |
| Zero eligible active non-data roles remain | Role not found | Stop without selecting an inactive, data, or inexact role |
| Multiple distinct eligible roles remain | Ambiguous role | Present `RoleName`, `RoleCode`, and `RoleId`; require an exact identifier choice |
| Exact selected role is not assigned to the user | Missing prerequisite | Stop; MDA does not provision the role |
| Mutation context resolution returns missing, unknown, or conflicting | Input validation | Ask only for the unresolved context; preserve the supplied value and do not propose a different context inferred from that value |
| Mutation context resolution returns invalid_catalog | Catalog mismatch | Use failed->RETURN_ISSUES; report the mapping-source problem and repair action without asking the user to restate the context |
| MDA.VALIDATE_CONTEXT_VALUES lacks its resolved intake context or the explicit label/matched mapping row changed | Input validation (workflow-state failure) | Use failed->RETURN_ISSUES for this pre-execution validation pass; retain the supplied context and rebuild local evidence on the next permitted validation pass; do not invent a backward graph transition or restart an external operation |
| Conflicting Grant/Revoke intents target one complete identity | Conflicting request | Stop and require one desired state |
| User, role, or membership pagination is incomplete | Incomplete validation | Stop; do not infer a result from the first page or raw count |
| Read-only lookup receives 401 or 403 after the core client refreshes authentication once | Authorization or privilege | Stop and report the required read access; do not attempt a mutation |

These new failed transitions belong only to MDA.VALIDATE_INPUT and
MDA.VALIDATE_CONTEXT_VALUES. Other nodes retain their declared outcomes.
For submitted, pending, or uncertain external operations, the existing FSM
export/Data Loader resume and REST reconciliation/recovery contracts take
precedence over rebuilding local label evidence. Preserve recorded operation
identity and FSM date state; a missing context_resolution record does not
authorize a new export, import, or REST mutation.

### Cardinality and Context Values

Apply the applicable eligibility and exact-match rules before counting; deduplicate canonical identities and identical membership pairs. Never choose the first ambiguous result.

Current context values are not prevalidated. If Fusion rejects a value, report its sanitized error; do not invent a replacement, switch methods, or retry. A corrected request must pass fresh checks and applicable approval. Future declared validators must distinguish invalid, ambiguous, unsupported, and unavailable outcomes; absence of validation evidence is not proof of an invalid value.

### Reporting

Classify failures as input validation, catalog mismatch, auth/authz, transport/environment, Fusion API, process timeout, process failed, artifact persistence, or approval blocker, retaining the task-specific reason. Preserve per-row errors and a non-success aggregate status for incomplete work.

Show only needed business scope and sanitized errors. Never expose credentials, tokens, token caches, Authorization headers, or unrelated assignment rows. Do not report an uncertain write as “no access was changed.” Persistence failure never authorizes replay.

#### User-Facing Outcome Rules

Lead with the business outcome and identify the affected assignment
or requested read/export scope using permitted business values.

| Outcome | Required reporting |
|---|---|
| Grant already active | State that the exact assignment is already active and no changes were made |
| Revoke already inactive | State that the exact assignment is already inactive and no changes were made |
| Revoke finds no exact assignment | State that no matching assignment was found and no changes were made |
| Preparation or validation complete | State that preparation or validation completed; do not claim submission |
| Submission accepted | Return the authoritative Data Loader in-progress report |
| Processing completed | Report processing outcome; distinguish it from assignment verification |
| Assignment verified | State the observed assignment state for the verified scope |
| Export downloaded and validated | Link the ready export file; report extraction separately |
| Extraction failed | State that extraction failed and whether the downloaded file remains available |
| Read complete with no matches | State that no matches were found only when completeness is established |
| Read partial or limited | Show permitted results and explain what remains incomplete or outside the requested window |
| Count returned | Label it exact, estimated, or partial according to the evidence |
| Mixed outcomes | Separate completed, unchanged, failed, pending, unverified, and unattempted rows |

No-op messages require complete reconciliation under the existing
lifecycle rules. Do not apply REST no-op semantics to FSM operations.

#### User-Facing Failure Rules

For every failure or blocker, explain:

1. What could not be completed.
2. Which requested scope is affected.
3. Whether submission occurred and what outcome is known.
4. The evidence-supported next action.

| Failure class | Required explanation |
|---|---|
| Missing or invalid input | Name only the missing or invalid business values |
| Missing prerequisite | Explain the prerequisite that is not satisfied |
| Ambiguous identity or assignment | Explain the ambiguity and request the exact selection needed |
| Catalog or schema mismatch | Explain that the supported configuration or load definition could not be established |
| Authentication or authorization | State the evidenced access problem without exposing authentication internals |
| Package or artifact validation | Explain which requested content could not be validated; state that submission was blocked |
| Transport failure or timeout | Explain the interrupted operation and whether its outcome is known |
| Processing failed or partially completed | Preserve known row outcomes and actionable Fusion diagnostics |
| Verification failed or mismatched | Distinguish processing outcome from the unverified or differing assignment state |
| Persistence failure | Explain which required file or evidence could not be saved and preserve known execution outcomes |
| Approval blocker | Follow the existing executor approval contract without adding another gate |
| Unexpected failure | State the affected operation, known submission state, uncertainty, and safe next action; retain sanitized diagnostics |

Never infer an authorization problem, invalid value, or corrective action
without supporting evidence.

Say "No changes were made" only when the evidence establishes that no
mutation occurred. An uncertain submission must be reported as
unconfirmed, not failed, successful, or unchanged.

Do not expose raw API responses, stack traces, commands, credentials,
internal workflow identifiers, or unrelated records in the final response.
Preserve actionable sanitized Fusion diagnostics, required approval
details, deliverable links, and necessary recovery references.

These reporting rules never authorize retry, replay, rollback, method
switching, reduced-scope submission, or additional external calls.

## FSM Method

### Common for Grant and Revoke

| Situation | Classification | Required Result |
|---|---|---|
| FSM Available Role/Object Mappings table is missing, malformed, contains a blank key, a nonnumeric Application ID, or a duplicate full key | Mapping-reference mismatch | Stop before package construction and correct the existing table |
| FSM package is data-bearing, was produced by setupTaskCSVExports, was not extracted, or has the wrong task, members, metadata, or headers | Package contract failure | Stop and download, extract, and validate a fresh exact-task Template Only package |
| A generated assignment or mapping row has blank or non-`USER_DEFINED` `RecordTypeCode` | Package contract failure | Stop and rebuild the generated row with `RecordTypeCode=USER_DEFINED` |
| A mapping row is generated for a listed pair, a Revoke/deactivation, or more than once for the same unlisted pair | Unsupported package scope | Stop and rebuild the conditional mapping set |
| Either provisioning-rule CSV contains generated data rows | Unsupported package scope | Stop; preserve both provisioning-rule files as header-only |
| FSM Revoke date lookup finds no active matching assignment | Revoke start-date resolution | Report no active matching access; stop without preparing a mutation package |
| FSM Revoke date lookup finds multiple active matching assignments | Revoke start-date resolution | Present safe candidate details and require exact selection; do not choose the first row |
| FSM supplied or exported Revoke StartDateActive is missing, malformed, or later than a supplied EndDateActive | FSM Revoke start-date resolution | Report the date error and stop; never substitute today's date |
| FSM Revoke lookup does not return a ProcessId | Revoke export creation unconfirmed | Preserve sanitized evidence; do not assume no process was created or automatically repeat the export |
| FSM Revoke lookup returns a ProcessId but is still pending after the shared exporter's configured wait window expires | Revoke export pending | Follow the shared timeout policy; save ProcessId and observed status; on user-requested retry resume polling the same process, not a new export |
| FSM Revoke lookup reports a terminal failure | Revoke export failed | Preserve status and available sanitized process log; stop without automatically creating another export |
| FSM Revoke lookup completed but its data ZIP is not downloaded | Revoke export download failure | Preserve the existing ProcessId; resume its download on retry |
| FSM Revoke receipt or downloaded artifact cannot be persisted | Revoke artifact persistence failure | Stop before deriving a date or building a package; report the persistence blocker without launching another export |
| Fusion rejects a submitted FSM Revoke row because StartDateActive is required | Fusion import failure | Do not retry automatically; return to Revoke date resolution and require a corrected date |
| FSM import rejects a supplied context/value | Fusion import failure | Return the sanitized Fusion response; do not retry, resolve, or choose a replacement value |
| Mapping batch succeeds but the assignment batch processes zero rows | Fusion import failure | Report the RoleCode/ObjectName availability decision, mapping-row decision, canonical assignment identity, and sanitized process log; do not retry automatically |

MDA.HANDOFF_GATE returns ready only when every FSM mutation row and its Template-derived package pass the input, dependency, and design contracts. It returns blocked otherwise. The gate makes no import call and collects no additional task-local approval; core.data-loader owns import preview/approval after MDA.HANDOFF_READY.

### Grant

A missing or invalid package, mapping decision, or Grant date blocks handoff. Do not resolve a Grant failure by invoking the Revoke original-date resolver or switching to REST.

### Revoke

### Revoke Lookup Disclosure

For FSM Revoke date-lookup failures before mutation, retain each affected row's unknown_confirmed
state and do not ask for the date again. Only after the shared wait window
expires with the process still pending, say:
“The access-details lookup is still running. No access was changed.”
For a failed or unavailable lookup, say:
“I couldn't retrieve the existing access details. No access was changed.”
Keep ProcessId, ZIP paths, and process logs in sanitized diagnostics, not the
user message. Do not suggest a permissions fix unless the returned evidence
identifies an authorization problem. A later explicit retry resumes the
recorded safe stage.


### Export/List

MDA.FSM_EXPORT_READY means that the declared shared exporter can receive the validated read scope. It is not evidence that export creation, polling, download, or persistence has completed. Follow the exporter's recovery stage; do not automatically create another process after an uncertain submission.

## REST Method

### Common for Grant and Revoke

| Situation | Classification | Required Result |
|---|---|---|
| Explicit scheduled/date-limited intent | Input validation | Explain that REST cannot fulfill it; obtain method selection without dropping dates |
| Assignment pagination incomplete or nonprogressing | Fusion API | Block planning; no conclusions from partial results |
| Multiple distinct exact assignment IDs | Input validation | Block; do not pick the first assignment or silently narrow the target |
| Required tuple fields or boolean ActiveFlag missing/invalid | Fusion API | Block; do not infer absent or inactive |
| Finder value cannot be safely represented | Input validation | Stop before the call; do not concatenate unescaped values |
| Read remains unauthorized after one core refresh | Auth/authz | Report the required access; do not mutate |
| Registered MDA loader object is missing or ambiguous | Catalog mismatch | Block this REST mutation route; report candidates or missing registration without direct-write or FSM fallback |
| Current registration or schema does not match retained contract evidence | Catalog mismatch | Block; resolve current target metadata and restart preparation |
| The current registered schema lacks a field or key needed for the selected minimal source, or declares a conflicting type or encoding | Input validation: unsupported target contract | Block that operation and name the mismatch |
| The final archive contains an unrequested attribute, blank generated key, or mismatched operation/state | Input validation | Block Task Hook approval and rebuild the source from the request and current schema |
| Final archive/digest differs, or an executable PATCH has the wrong ID, RestAction, ActiveFlag value, or extra assignment attributes | Input validation | Block Task Hook approval and require corrected preparation |
| Sample rows, no-op rows, DELETE, or unrelated changes remain in the final artifact | Input validation | Block Task Hook approval and require corrected preparation |
| Task Hook lacks original method/context, workflow stage, current schema evidence, final archive digest, or ordered rule results | Input validation | Stop rather than reselecting the method, reconstructing intent, or invoking Data Loader recursively |
| Loader metadata/upload/initiation privileges are unavailable | Auth/authz | Report the evidenced missing access; successful assignment GET access is insufficient |
| Upload or initiation fails, times out, or has an uncertain response | Transport/environment or Fusion API | Follow core recovery with retained artifact/reference; no new upload or job by MDA |
| Loader job is pending or not yet available | Process timeout or current pending status | Return the core status and next-check reference; do not resubmit or claim completion |
| Loader job fails or partially completes | Process failed | Return core diagnostics and known row outcomes; no automatic semantic verification, rollback, or batch replay |
| Later readback fails or returns a different tuple/state after terminal success | Fusion API or transport/environment | Report processing success separately from mismatch/unverified assignment state; do not repair automatically |
| Required artifact or approved envelope is missing/modified | Artifact persistence or approval blocker | Core must block submission; require fresh preparation and approval |
| Exact Data Loader artifact approval is missing or only an old direct-REST receipt exists | Approval blocker | Complete the core artifact approval workflow; add no second task-local approval |

MDA.REST_HANDOFF_GATE runs only after MDA.REST_VALIDATE_ARTIFACT returns validated during workflow_stage=task_validation. Check every row's contract result, exact final archive digest/readback, original method-selection evidence, same task/environment, no-op accounting, and declared follow-up/recovery path. Return ready or blocked without executing writes or obtaining approval. MDA.REST_READY returns rule results to the existing Data Loader preview workflow; never invoke MDA preparation or another load from that terminal.

If contract or artifact preflight blocks a Revoke or reactivation, report that the assignment change was not submitted; do not describe it as a Fusion rejection. Apply these additional contract and artifact failure rules only to REST writes, never to FSM or REST read/status/no-op paths.

MDA.REST_NOOP_DONE returns completed no-op outcomes only when every requested row needs no write and reconciliation is complete. It bypasses loader registration, samples, archives, and approval. In a mixed batch, preserve no-op observations separately while including only required writes in the artifact.

### Grant

- One active exact assignment: “This data-access assignment is already active. No changes were made.”
- One inactive exact assignment requires a validated state-only activation record and Data Loader approval.
- No exact assignment after complete reconciliation requires a validated create record and Data Loader approval.
- A failed/uncertain submission must not be automatically repeated.

### Revoke

- One inactive exact assignment: “This data-access assignment is already inactive. No changes were made.”
- No exact assignment after complete reconciliation: “No matching data-access assignment was found. No changes were made.”
- One active exact assignment requires a validated state-only deactivation record and Data Loader approval.
- No original-date question, DELETE, or automatic alternate-method attempt.

### Retry and Resume

Core owns authentication and bounded retry behavior for its metadata, upload, initiation, and status operations. MDA does not invoke the shared REST client's POST/PATCH path or add an outer retry. Read-only assignment GETs retain the shared client's existing authentication handling.

After failed or uncertain execution, retain core's observed stage, artifact and available submission reference. On a later explicit request, check that same job through core before planning corrective work. Pending or ambiguous submissions are not permission to replay. A separately requested corrective load requires fresh current reconciliation, an explicitly selected remaining scope, and new artifact approval; never resubmit previously successful rows automatically. Ordinary assignment reads can establish observed state but cannot prove which job caused it.

Before approval, stale or changed reconciliation/contract evidence invalidates the proposed artifact. After approval, honor core's immutable submission contract: no new lookups or source edits. Known request/environment/artifact changes require a fresh cycle, not a silently modified approved load. Job queuing introduces a concurrency window; do not promise atomic or ordered execution.

A verified no-op requires no mutation approval. Do not label an uncertain write as a no-op merely because a later read sees the desired state.

### Loader Follow-up Outcomes

MDA.LOADER_STATUS_READY authorizes only the declared core status/diagnostics handoff. Missing reference or environment is an input issue, not a reason to initiate another job. A status-only request never needs mutation eligibility or loader sample generation. Return the core report for pending, unavailable, failed, partial, or successful processing. Semantic verification is a separate results/verification step requiring terminal success, exact artifact/submission linkage, and submitted assignment scope. If those receipts are unavailable, report verification as unverified while retaining any valid job status.

The existing external MDA test coordinator's direct-REST preview receipt does not automatically cover a loader artifact. Do not treat test prompts or legacy receipts as same-request Data Loader auto-approval, and do not report live PASS from an accepted initiation. This skill does not edit or silently reinterpret that external test policy.

### Read Outcomes and Failures

| Situation | Required result |
|---|---|
| Complete finder-bound GET plan returns zero rows | Successful empty List after every required branch and page completes |
| Valid finder-free GET, with or without q, returns rows | Report observed matching rows with requested_scope_complete=false and collection_complete=false unless independent exhaustive evidence covers this exact scope |
| Valid finder-free GET, with or without q, returns zero rows | Report unverified absence/incomplete scope, never an empty complete List or exact zero; do not invent a finder or switch methods |
| Requested scope cannot be represented by a documented, validated GET expression | invalid_scope with unsupported_collection_scope; explain the query capability gap without inventing missing mutation inputs |
| One required finder-bound branch fails or remains unpaged | Incomplete overall scope; retain completed branch evidence and safe continuation, never report a complete union or exact count |
| Consistent repeated assignment ID | Collapse duplicates; report raw and distinct counts separately; advance offsets by raw rows |
| Same assignment ID has conflicting returned data | Incomplete result; preserve the conflict and do not report an exact count |
| Returned UserName or RoleNameCr is missing or conflicts with a finder-bound identity | Incomplete result; do not silently discard the row or claim that the matching collection is empty |
| Search returns multiple rows | Valid result; no exact-choice requirement |
| Requested window is satisfied and more rows exist | Successful window; collection_complete=false |
| Single-assignment GET returns 404 | Not found for that ID |
| Query field/operator/grouping is invalid | Explain the specific query issue |
| Query contains standalone unary NOT | Return invalid_scope with unsupported_query_operator before REST invocation; explain supported operator-specific exclusions without silently rewriting an explicit raw query |
| Requested framework is rejected | Report incompatibility; retain requested semantics |
| Requested output/sort attribute is unsupported | Report that option; do not silently discard it |
| Read options conflict with the selected mode | Clarify or return invalid_scope; never silently drop a window, projection, or condition |
| Retrieval fails before requested scope is satisfied | Incomplete result with permitted partial results and safe continuation information |
| Estimated count is unavailable | Report unavailable; never substitute zero |
| Exact-count retrieval is interrupted | Count incomplete; do not label a partial count exact |
| Authorization fails | Report required read access |
| Read timeout or transport failure | Report failed/incomplete scope; preserve supplied query |

MDA.REST_LIST_DONE reports the requested read scope after complete or window_complete; a successful window is not a failure merely because hasMore=true. MDA.REST_GET_DONE reports found/not_found, and MDA.REST_COUNT_DONE reports a completed count with its exact/estimated kind. These terminals return read outcomes only; none authorizes or executes a mutation.

An item 404 during customer retrieval differs from an item 404 during post-write verification. Preserve verification uncertainty: a failed readback does not prove that the preceding write failed. Never broaden a rejected query or silently downgrade its framework. Missing mutation fields and multiple matches are not customer-read errors.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Applicable input, identity, membership, or method dependency is unresolved | Stop the selected branch and request only missing business facts or exact selection |
| FSM package/design invariant fails | Stop handoff; do not use current data as a mutation baseline |
| REST reconciliation, loader contract, or artifact invariant fails | Stop before core preview or submission |
| Fusion rejects a context value | Report the sanitized error; do not replace the value or switch methods |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| MISSING | Required input or exact selection absent | Request only missing business facts |
| FAILED | Validation, catalog, package, API, or design contract fails | Correct and replan |
| AUTHORIZATION_OR_PRIVILEGE | Required access is unavailable | Resolve the evidenced access problem |
| UNSUPPORTED | Requested scope is outside supported operations | Explain the supported scope |
| APPROVAL_BLOCKER | Selected executor's required exact approval is absent | Complete that executor's approval contract |
| TRANSPORT_OR_ENVIRONMENT | DNS, TLS, timeout, or environment failure | Preserve evidence; reconcile uncertain writes without replay |
| ARTIFACT_PERSISTENCE | Required sanitized evidence cannot be persisted | Stop further mutations and report the persistence blocker |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Blocked readiness | Selected scope, method, and actionable blocking condition |
| Preview | Exact selected-method payload/artifact and side effects required by its execution contract |
| Executor failure | Sanitized result, partial/uncertain outcomes, and safe next action |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| FSM import lacks required immutable artifact or Data Loader approval | Do not submit or add a duplicate task-local approval |
| REST load lacks current exact-artifact approval | Do not submit, invoke assignment POST/PATCH, or reuse an old direct-REST receipt |
| Loader follow-up is pending, failed, partial, or lacks scope linkage | Do not claim verified assignments, prepare a replacement artifact, or retry automatically |
| Selected-method preparation fails | Do not silently switch methods |
| Failed/uncertain write or partial batch | Do not automatically replay, roll back, or claim no change |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When | Resolver |
|---|---|---|---|---|---|---|---|---|
| MDA.LOADER_STATUS_READY | terminal | 3 | terminal | none | MDA.LOADER_STATUS_INPUT | stop | Return readiness to SKILL.md later Data Loader status and verification handoff |  |
| MDA.REST_PREPARE_READY | terminal | 185 | terminal | none | MDA.REST_VALIDATE_ARTIFACT | stop | Return planning readiness to SKILL.md registered REST loader preparation; not approval or execution |  |
| MDA.HANDOFF_GATE | step | 120 | execution_gate | ready->MDA.HANDOFF_READY;blocked->RETURN_ISSUES | MDA.ENFORCE_DESIGN | stop | Check aggregate FSM package readiness; Data Loader owns approval |  |
| MDA.HANDOFF_READY | terminal | 130 | terminal | none | MDA.HANDOFF_GATE | stop | Return FSM import readiness to the explicit SKILL.md Data Loader handoff |  |
| MDA.REST_HANDOFF_GATE | step | 190 | execution_gate | ready->MDA.REST_READY;blocked->RETURN_ISSUES | MDA.REST_VALIDATE_ARTIFACT | stop | Check validated immutable REST loader artifact and retained method/context; core owns approval and submission |  |
| MDA.REST_READY | terminal | 200 | terminal | none | MDA.REST_HANDOFF_GATE | stop | Return final-artifact validation to the calling Data Loader Task Hook; no recursive handoff or submission |  |
| MDA.REST_NOOP_DONE | terminal | 205 | terminal | none | MDA.REST_CLASSIFY_PLAN | stop | Return completed no-op outcomes from complete reconciliation; no mutation approval |  |
| MDA.FSM_EXPORT_READY | terminal | 220 | terminal | none | MDA.FSM_EXPORT_CHECK | stop | Return readiness to SKILL.md explicit shared-exporter handoff; export not yet executed |  |
| MDA.REST_LIST_DONE | terminal | 240 | terminal | none | MDA.REST_LIST | stop | Return completed List or window with separate requested-scope and collection completion evidence |  |
| MDA.REST_GET_DONE | terminal | 260 | terminal | none | MDA.REST_GET | stop | Return definitive found/not-found item read; no mutation |  |
| MDA.REST_COUNT_DONE | terminal | 280 | terminal | none | MDA.REST_COUNT | stop | Return completed assignment count labeled exact or estimated; no mutation |  |
| RETURN_ISSUES | terminal | 990 | terminal | none | none | stop | Return selected-branch blockers without handoff or mutation |  |
