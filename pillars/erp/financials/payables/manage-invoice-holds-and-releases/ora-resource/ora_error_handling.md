# Manage Invoice Holds and Releases — Error Handling

No task node performs a setup write.
The active Run Book and core.data-loader own processing, immutable preview,
candidate-bound approval, submission and accepted-initiation reporting.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AP_HOLD.GATE | decision | 60 | execution_gate | success->AP_HOLD.DONE;failure->AP_HOLD.ERRORS | AP_HOLD.DESIGN | stop | All prior task rules completed; return validation result only |
| AP_HOLD.ERRORS | step | 70 | error_handler | reported->RETURN_ISSUES | none | stop | A previous node reports failure or missing evidence |
| AP_HOLD.DONE | terminal | 80 | terminal | none | AP_HOLD.GATE | stop | Return successful validation only; never claim import or saved-state success |
| RETURN_ISSUES | terminal | 90 | terminal | none | none | stop | Return recorded issues and safe resume stage |

## Error Situations

| Situation | What Should Happen |
|---|---|
| Rule plan is incomplete | Report exact file, field/column and missing contract; stop before processing or mutation. No readiness override was supplied |
| Inputs or candidate representation are invalid | Report the exact field and failed contract in ora_input_validation.md; correct the request before build. Defaults remain owned by ora_defaulting_rules.md. |
| Record identity fails | Report the exact key and resolver outcome from ora_reference_lookups.md; stop the affected operation rather than changing its lifecycle intent. |
| Invalid HoldType | Preserve FND_CMN_INVALID_ATTRB_API_SERV and the actual returned process diagnostics. Do not manufacture a live response |
| Negative notification/reminder days | Report the affected integer field and FND_CMN_POSITIVE; apply the accepted-range contract in ora_input_validation.md. |
| Routing/manual-release combination rejected | Surface AP_HOLD_RES_ROUTING_NO with affected fields and exception scope; no automatic correction |
| Requested update violates Update Restrictions | Stop before build. Use UPDATE_TYPE_RESTRICTED_FIELD for restricted-type accounting/manual-release changes, UPDATE_FIELD_REQUIRES_UPDATEABLE for accounting/manual-release, inactive-date or description updateability restrictions, UPDATE_ROUTING_RESTRICTED for routing restrictions, and UPDATE_ROUTING_DETAIL_RESTRICTED for notification days, reminder days or hold instructions when routing is N or blank after applying any eligible requested routing change, or baseline updateability is N. Report operation ID, exact AP_HOLD_CODE key, requested field, baseline type/flags, applicable routing value and the failed condition from ora_design_enforcement.md. Unsupported inputs retain their separate unsupported-update diagnostic. |
| Pre-import field combination conflicts | Stop before build with MANUAL_RELEASE_DEPENDENCY_CONFLICT for an incompatible supplied routing/instruction/day value when the manual-N rule applies, or RELEASE_TYPE_FLAG_CONFLICT for a forbidden create flag on one of the five release types. Report operation, exact key, triggering condition, field, supplied value and required value. These are task-policy diagnostics; do not claim a returned Fusion error or silently correct the request. |
| Routing is No with resolution options supplied | Require blank HoldInstruction, WaitBeforeNotifyDays and ReminderDays. After update eligibility checks, use ROUTING_DISABLED_DETAIL_CONFLICT for supplied nonblank values, including unchanged values or zero days. Derive omitted clears and disclose them in the preview; eligible explicit clears are valid. |
| Derived values or import processing are relevant | Show design-owned sourceDrivenEffects and supporting lookup maintenance separately from requests/defaults. Lookup maintenance remains nonblocking, including preserved or unchanged descriptions; accounting effects follow their own disclosure. Do not treat an incompatible supplied combination as merely a warning or claim the saved result without readback. |
| Persisted deletion requested | Report AP_NO_DELETE under the operation limits in ora_design_enforcement.md. Any requested inactivation requires its own eligible update, readback and candidate approval. |
| Supporting lookup or accounting database operation fails | Preserve FND_GENERIC_MESSAGE, sanitized cause and context; stop. |
| Accounting update fails or needs investigation | Preserve requested and available actual before/after flags and process/event diagnostics; apply Accounting Effects in ora_design_enforcement.md. This is conditional follow-up, not a prerequisite for accepting an eligible update. A reverse setup flag update does not guarantee restoration of prior accounting-event states. |
| Accounting event processing fails | Outer routine sets AP_DEBUG unless SQLCODE=-20001 then raises APP_EXCEPTION. Nested payment-time withholding block suppresses its local exception; not all nested failures propagate |
| Export/import process times out | Preserve environment, task code, ProcessId/requestId, last status, elapsed wait and next-check path under the project; do not resubmit |
| A request may have reached Fusion | Preserve the uncertain outcome and external ID. Follow the verification and retry limits below. |
| Partial success or failed process | Retrieve and persist process status/logs, then use the declared fresh-export route for reconciliation even on failure. Cleanup is best effort and does not guarantee that a commit was prevented; retain successes and errors with nonzero status. Never assume rollback or automatically retry. |
| Fresh export differs | Report every requested and collateral difference, raw values and evidence; distinguish disclosed setter effects from unexpected changes and verify every affected dependent field. Initiation or downloaded package is not saved-state success |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Shape, known domain, scalar type or required business value fails | Correct exact input and regenerate preview |
| Catalog mismatch | Wrong task, offering, CSV flag, metadata identity or package header | Stop and reacquire the correct task contract |
| Auth/authz | Selected client lacks valid identity or privilege | Follow its declared auth recovery; never expose credentials |
| Transport/environment | TLS/network/service unavailable | Preserve error; do not reinterpret as no-match or retry a mutation |
| Fusion API | API or task validation rejects submitted operation | Preserve sanitized diagnostics and results; no alternate-route fallback |
| Process timeout / process failed | Declared monitor reports timeout or terminal failure | Retain IDs/status/logs and stop; preserve partial outcomes |
| Artifact persistence | Expected package/evidence could not be safely written | Stop before claiming completion or submission |
| Approval blocker | Missing exact candidate approval or changed preview | Present a new immutable preview through core.data-loader at the declared gate |
| Required request evidence missing | Required input, package or task-key identity is missing | Identify the affected request field or artifact and safe next action; do not add proof-only prerequisites. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Preflight result | Exact task identity, supported operation boundaries, missing field/operation contracts, current node and safe next action |
| Preservation intent | Show exact requests, derived omitted sourceDrivenEffects, accountingEffects, baseline hash and raw/calendar date provenance. Apply the input/package and pre-import consistency contracts; disclose each affected dependent field for any requested reconciliation. |
| Create intent | Show exact new key, applied defaults under ora_defaulting_rules.md, derived omitted values, the complete non-audit row, optional blanks and separate lookup maintenance. Include the identity outcome from ora_reference_lookups.md. |
| Data Loader handoff | Require verified task capability, environment identity/privileges, fresh operation-specific task-key identity, valid accepted row/package values and an immutable candidate preview. Use the declared workflow and candidate-bound Data Loader/Task Hook approval. Validation readiness alone does not authorize mutation; the adapter remains offline. |
| Accepted initiation | Retain the Data Loader response and external IDs; report accepted initiation accurately. Do not automatically poll, export or reconcile after a successful initiation. Follow-up runs when requested or when a declared failure, uncertain-outcome or recovery procedure requires it. Do not claim completed processing or verified saved values from initiation alone. |
| Recovery | Reverse artifacts are not restored-state proof. Create cannot produce a reverse-delete package; retain created identity and actual state, and consider separately approved inactivation only if requested. Every reverse or recovery stage must satisfy Update Restrictions and Pre-import Consistency Rules against its qualified current baseline. A change from an exported PostableFlag X to Y or N cannot have an automatic reverse candidate that writes X, because X is not an accepted input. Disclose that limitation in the forward preview; preserving an omitted existing X does not authorize writing it during recovery. Stop with the applicable diagnostic for restricted recovery; never bypass the policy or introduce stages to evade it. If one reverse package cannot restore original values, return only a conditional staged plan requiring exact intermediate readback, another eligible candidate and its separate approval. A staged plan or matching readback does not establish restoration eligibility or guarantee. No physical delete, transaction reversal guarantee or hidden lookup rollback. InactiveDate clear/assignment is not a cleanup guarantee. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Catalog supports CSV but import semantics are unresolved | Do not infer create/update support solely from catalog flag Y. The declared offline contracts still require operation-specific input/build controls; reconciliation controls apply when reconciliation is selected. Live submission requires all live gates. |
| Internal resolver is incomplete | Do not call a database/package directly, invent a public service or create reference data |
| Input failure is silently corrected | Apply ora_input_validation.md; never truncate, rewrite, silently clear or replace a failed input with zero. |
| Plan or candidate approval is stale | Do not reuse it for a materially changed environment, payload, key, operation or executor |
| Prior write has uncertain outcome | Do not automatically retry POST/PATCH/DELETE, loader/import or ESS operations. Obtain declared read-only verification before any new separately approved attempt. |
| Sampled data or a test expectation is offered as proof | A sampled value does not replace the accepted domain. Do not report saved-value comparison or successful execution without retained run/readback evidence. An expected no-exception result is not an observed result. |

## Local artifact protection

The task-local FSM package runtime checks CLI input, output and report paths before
processing. Stop on aliases, duplicate or nested destinations, existing outputs,
output symlinks or paths outside --workspace. Choose fresh paths; do not overwrite
inputs or evidence. A failed path check reports to stderr only. Subsequent file
write failures return artifact_persistence; any failure report uses exclusive
creation. Invalid CSV quoting, JSON encoding/integer limits and corrupt ZIP
compression return input_validation without an unhandled traceback. Candidate
ZIPs are staged and independently validated before publication; failed candidates
are not published. Publish the complete output set exclusively; if publication
fails, remove only outputs created by that attempt and preserve existing files.
Use new output paths on retry. These local operations do not submit or retry a
Fusion mutation and have no process-polling window.

Local CLI diagnostics include status, stage, failure class, errors and the
recommended action. Missing or malformed inputs and schema conflicts return
input_validation; unsafe overwrite returns approval_blocker; other filesystem
access or write failures return artifact_persistence. A preflighted --report
path retains the diagnostic. Exit status is 0 for declared success/no-op and 2
for classified failure. Never include credentials or token caches in inputs or
reports; local tests use synthetic archives and do not establish a Fusion result.

When reconciliation is requested, reject reuse of candidate or baseline paths,
bytes or export process IDs. Require a separate export with a positive process
ID and matching environment/release/schema. A value match returns COMPARISON_ONLY
with persistenceVerified=false. These local checks do not authenticate the
download or prove an import completed; the owning workflow supplies that evidence.
Comparison does not replace independent candidate validation.

Recovery preparation must satisfy the same field, clear and update-eligibility
contracts as the forward request. Validate the reverse values and resulting
effects before advertising automatic recovery; omit unchanged effect-only
fields. Forward-bound reference evidence or exceptions cannot validate or
authorize the reverse operation. Disclose when restoring a value needs fresh
reference evidence or when its original blank lacks an accepted clearing rule;
do not publish an automatic reverse candidate for that unsupported restoration.
