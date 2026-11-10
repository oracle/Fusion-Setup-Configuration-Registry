# Customers Errors and Execution Gate


## Error Situations

| Situation | What Should Happen |
|---|---|
| Input/package validation fails | Return row/field codes without customer values; create no partial candidate |
| Loader rejects rows or returns PARTIAL | Retain errors and successful/partially persisted entities; failed process does not imply rollback |
| Lost response or process timeout | Preserve the same attempt and request IDs; status retrieval only, no automatic resubmission |
| Corrected input is proposed | New immutable preview and approval; never reuse previous acceptance |

## Pre-import Readiness

Task Hook evaluates this resource before the immutable preview and candidate
approval. Check that the execution and verification contracts are available;
do not require an import result, returned request ID or approval at this stage.
`ARCU.READY` means ready for central preview only. It neither authorizes a
submission nor marks the business task complete.

| Check | What Must Be Shown |
|---|---|
| Central FBDI handoff | Apply ../references/central-handoff.md to actual candidate evidence: registration/core/Run Book binding, actual OAuth principal and read-only preflight, explicit untested/verified/denied execution-access status, and approval covering the selected core bounded rejection recovery, with no task-level retries; failed required checks take blocked. Untested upload access is not a passed privilege check or a preview blocker |
| Verification plan | Apply ../references/verification-plan.md and ../references/business-outcome-reconciliation.md with the candidate-generated runtime scope; retain all 87 columns including DFFs, verify requested values and relevant effects, disclose unused hidden storage, and review partial persistence; actual after-results are not required before preview |
| Correlation plan | Confirm the central route retains distinct Data Loader request/dataset/run IDs, interface LOAD_REQUEST_ID, product UPLOAD_REQUEST_ID and BATCH_ID when returned; never manufacture these before submission |
| Argument contract | Application 222/interface 59; explicit batch name, null document ID, null batch ID, ESSCREATE, and a binding to the actual interface request ID when returned; reverify against runtime registration |
| Candidate binding | Exact archive hash, environment, registration, argument contract and operation intent are ready for central preview; disclose eligible loader-validation gaps |

## After Governed Submission

Run Book and core Data Loader own submission, monitoring and completion. This
phase is not part of Task Hook's pre-import rule plan. Preserve actual returned
correlation IDs, reconcile persisted entities, relationships and requested
values, and report Fusion outcome separately from Journey synchronization.
Follow the normal human completion or retry decision. A passed pre-import rule,
preview approval or successful process status cannot substitute for this phase.
See [the phase contract](../references/task-hook-handoff.md).

The compiled registry describes available evaluation instructions, not a passed
candidate. Use [the central handoff evaluation](../references/central-handoff.md)
and retain actual evidence/dispositions for every applicable check. Never emit a
passed resource result merely because its definition is complete.

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Known input rule or package contract fails | Correct the specific field or archive |
| Catalog mismatch | Task, BO or route differs | Resolve exact supported registration; do not guess |
| Auth/authz | Declared central access unavailable | Use approved authentication workflow; never request credentials in input files |
| Process failed or timeout | Actual load fails or status remains unknown | Retain last status and exact attempt; stop before retry |
| Partial persistence | Some requested entities/values exist and others fail | Disclose exact observed outcome and obtain a correction decision |
| Approval blocker | Acceptance is missing/stale or normal approval is absent | Bind a fresh explicit decision to the current preview |

## Task Results

| Result | Meaning |
|---|---|
| Offline preview | Layout and implemented checks passed; live gates remain open |
| RETURN_ISSUES | Report missing/failed contract with no successful import claim |
| READY_FOR_CENTRAL_PREVIEW | Pre-import checks passed; requires central preview and normal candidate approval before submission |
| Verified business outcome | Post-import persisted reconciliation and Journey synchronization have separate evidence; not a Task Hook pre-import result |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ARCU.EXECUTION_GATE | decision | 60 | execution_gate | ready->ARCU.READY;blocked->ARCU.ERROR | ARCU.DESIGN | stop | Before central preview: execution contract, candidate binding, before-state and verification plan are ready |
| ARCU.ERROR | step | 70 | error_handler | reported->RETURN_ISSUES | none | stop | Any blocked or failed step |
| ARCU.READY | terminal | 80 | terminal | none | ARCU.EXECUTION_GATE | stop | READY_FOR_CENTRAL_PREVIEW only; no approval, submission or persisted-outcome claim |
| RETURN_ISSUES | terminal | 90 | terminal | none | none | stop | Unresolved or failed outcome |
