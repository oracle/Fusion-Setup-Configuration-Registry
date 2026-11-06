# Adaptive Search Administrator Presentation

## Presentation Contract

- Use plain functional language for every normal interaction.
- Prefer compact tables for object validation, selection confirmation, publish preview, submission response, and errors.
- Use object display names from `localizedName` in administrator-facing output. Hide internal `entityName` values by default, but show them in parentheses when the user asks or when duplicate display names require disambiguation.
- Keep contract-validation details, contract IDs, internal artifact paths, rule-node IDs, and binding metadata out of user-facing output. The ABO companion's generated XLSX link is the sole workbook-access exception; it does not expose other internal artifacts.
- Continue calculating and persisting technical binding metadata internally.
- Show technical details only when the user explicitly asks for diagnostics or repository implementation information.
- In all administrator-facing output, including progress updates and success messages, use `Partial Publish`; never use the technical term `selective`. The technical value `publishType: selective` remains internal unless diagnostics are requested.
- Do not describe a prepared operation as a redundant, no-op, enabled-only, or technical publish. In particular, never render the phrase `A selective publish is prepared` or any equivalent phrase containing the technical publish mode.

## Progress Messages

### Standalone

| Situation | Administrator-facing response |
|---|---|
| Preparing or submitting a Partial Publish | `Preparing the approved Partial Publish for the specified environment. I’ll record the returned job details and won’t poll automatically.` |
| Submitting a Full Publish | `Submitting the approved Full Publish now. I’ll record the returned job details and won’t poll automatically.` |
| Preflight finds the latest publish has status SUCCEEDED | `Preflight passed: the latest publish completed successfully.` Never use `is terminal` in administrator-facing text. |

### Fusion ABO dependent invocation

For initialization, show the real missing/null/empty catalog blocker and the
parent's full ABO initialization preparation proposal. Core then supplies its
unchanged load preview for independent approval. After submission show:
"Full Publish can take 10 minutes or longer. Please wait about 8–10 minutes,
then request 'Check the Full Publish initialization status and continue' again."
Pending/failed
initialization cannot reoffer selective approval. Verified initialization
returns a fresh Partial Publish preparation template, not ESS. See
[ora_abo_initialization.md](ora_abo_initialization.md).

| Situation | Parent-visible progress response |
|---|---|
| Preparing the fixed publish before approval | `Preparing the fixed Adaptive Search publish for the Fusion ABO workflow.` |
| After CPQ approval | `Fusion ABO is applying the approved CPQ changes. Adaptive Search publish will require its own preview and approval after CPQ verification.` |
| Adaptive Search load submitted | `Completion is not verified. Say: Check the Adaptive Search load status and continue.` |
| Adaptive Search succeeds | `Fusion ABO verified Adaptive Search and will present the existing synchronization payload for separate approval.` |
| Workflow completes or stops | Return one final `COMPLETED`, `FAILED`, `TIMED_OUT`, `BLOCKED`, or `INDETERMINATE` outcome. Do not ask the consultant to request status or approve another step. |

## New Request Opening

| Situation | Administrator-facing response |
|---|---|
| Object display names were supplied | Begin object validation without mentioning prior jobs or historical project state |
| Object display names are missing | Ask: `Which business objects do you want to publish? Provide the object display names.` |
| Project state contains a previous submission | Keep it internal; do not show it in the opening response |
| Fresh status GET later returns WAIT, READY, RUNNING, or PAUSED | Show the blocking job ID and current status in a compact table |
| Fresh status GET later returns a terminal status | Continue silently; do not add historical-job wording to the preview |
| All requested objects are already enabled | Show them in Current Active Objects and continue to the Combined Publish Confirmation Table; do not suppress the requested publish |

Never open a new flow with wording such as `A prior Adaptive Search full publish is already submitted` based only on a persisted run record or its initial status.

When a standalone user later requests status, present the returned job ID and
current status as technical execution evidence. Do not present a new approval
prompt or imply that another publish will occur. In the Fusion ABO dependent
path, the user explicitly requests the load-status check. After verified load
success, the parent checks the same Adaptive Search job once and offers an
explicit choice before any repeated monitoring.

## Object Validation Table

| Field | Show to Administrator |
|---|---|
| Requested object | Yes, using localizedName |
| Object display name | Yes |
| Valid document object | Yes |
| Currently enabled | Yes |
| Validation result | Yes |

For invalid input, state which requested values are invalid and show up to three nearest display-name suggestions for each one. Ask whether a suggestion is the required entity and collect a corrected complete list. Do not show the full document-object catalog. Normally hide internal names. If display names are duplicated, render each duplicate as `Display Name (internalName)` and require an exact choice. The user may also ask to show internal names for all suggestions. Once the corrected list is valid, render it using the Selection Confirmation Table and ask the selection-confirmation prompt once; acceptance is final for object selection and must not be followed by another selection review.

## Combined Publish Confirmation Table

| Field | Show to Administrator |
|---|---|
| Current active objects | Yes |
| Additional Objects Added | Yes; show the final publish-selection objects that are not currently active, or `None` |
| Final publish selection | Yes |
| Environment name or hostname | Yes |
| Publish type | Partial Adaptive Search publish by default; Full Adaptive Search publish when explicitly requested or when the entity catalog is null or empty |
| Object list | Yes, using validated display names for Partial or explicit Full Publish; show `Accounts, Contacts, Leads, Opportunities, Revenue Lines, Activities, Assets, Items, Product Group` for the new-environment fallback |
| Object count | Yes for Partial or explicit Full Publish; state unavailable only for the OOTB fallback before its entity mapping is displayed |
| Action | Submit publish |
| Expected response | Data Loader acceptance. A publish job ID is available only after a later successful Data Loader status check. |
| Data Loader approval | This confirmation approves the exact validated immutable Data Loader source; do not show a second approval prompt |

For a partial publish, ask exactly: `Please provide your confirmation to proceed with partial publish of the requested objects.`

For an explicit Full Publish with a nonempty entity catalog, before preparing the final table, show a selection-decision table with `Current active objects` and `Newly Requested Objects to enable`, then ask exactly: `Should the current enabled objects be retained and combined together with the requested objects for a new publish ?` On Yes, the final selection is the ordered, deduplicated union of active objects followed by requested objects. On No, the final selection is the requested objects only. This question is not approval to submit.

For any Full Publish, ask exactly: `Please provide your confirmation to proceed with full publish of the requested objects.`

This is the only live-approval prompt in a standalone Adaptive Search run.
Render it only after the current publish-status check, payload mapping, and
immutable Data Loader source validation are complete. On Yes, submit the
already prepared source. In the Fusion ABO dependent path, display Core's persisted preview verbatim after
CPQ verification; obtain separate approval through the exact validated archive.
ABO must not bypass validation or replace the validated archive. Outside that exact
dependent route, the existing Data Loader confirmation remains required.

For a recognized CPQ alias with a nonempty Entities response, do not use catalog
membership as a validation gate. Instead, match the two direct entity names
(`oraclecpqo_transaction` and `oraclecpqo_transactionLine`) only to obtain
their `localizedName` and `isEnabled` values for the table. List enabled matches
under Current active objects and disabled matches under Additional Objects Added.
If either direct entity is absent, show its exact entity name under Additional
Objects Added and Final publish selection rather than `Not inferred`. The final
CPQ selection always has two objects.

## New-Environment Full-Publish Confirmation

When the Entities response is null, `items` is null, or `items` is empty, display only these OOTB objects: `Accounts`, `Contacts`, `Leads`, `Opportunities`, `Revenue Lines`, `Activities`, `Assets`, `Items`, and `Product Group`.

For a null or empty Entities response, ask exactly: `No Prior publish was performed, Please provide your confirmation to proceed with full publish of these OOTB objects`

On Yes, submit the OOTB internal-entity array without `publishType`. Do not validate the OOTB objects. On No, collect a replacement full list, validate it against a fresh Entities response, then show the Full Publish confirmation. Each path shows only its applicable final confirmation.

## Standalone Submission Result Table

For a successful submission, use exactly `Partial publish submitted successfully` when the mapped payload has `publishType: selective`. For every other successful submission, use exactly `Full pulish submitted successfully.` Do not include the environment name or technical publish type. The immediate submission result is a Data Loader initiation receipt, not an Adaptive Search job result.

| Field | Show to Administrator |
|---|---|
| Result | Submitted or failed |
| Data Loader Content ID | Yes; label it exactly and do not call it a Publish Job ID |
| Data Loader Request ID | Yes; label it exactly and state that it is not the Adaptive Search Publish Job ID |
| Adaptive Search Publish Job ID | `Not available until Data Loader processing completes. Ask for the current publish status to retrieve it.` |
| Automatic polling | State that it is not performed |

When the user explicitly asks for the current publish status, first show the
Data Loader status for the stored Data Loader Request ID. Only when that status
is successful, make one latest Adaptive Search publish-status lookup and show
its Publish Job ID, Initial Status, Publish Source, and Metamodel UUID. If the
Data Loader status is failed or otherwise not successful, show its safe error
details and do not perform the Adaptive Search status lookup.

## Fusion ABO Dependent Return Contract

Core's load preview Markdown and single approval question are displayed verbatim,
without reconstructing a parent source/digest approval or asking twice.
Keep the parent workflow progress separate from the Core preview/receipt.
At successful approval readiness, display the separate `workbook_access`
Markdown event once before Core's preview, without altering its table or
question. This is optional workbook viewing only, not an editing control,
mandatory review or extra approval. Edits do not update the retained load.
If the optional link is unavailable, retain its safe access message and Core's
unchanged preview; do not restart or modify the validated prepared load.

After acceptance say: "Adaptive Search load submitted. Completion has not yet
been verified. To check it and continue, say: Check the Adaptive Search load
status and continue." Pending load status returns this same next-check prompt
and stops. After verified load success, show the parent's full ABO template with
the actual publish status and ask: "Would you like me to keep checking every 15
seconds, or would you prefer to check the status later?" Keep-checking permits
bounded job-only monitoring. Check-later saves the checkpoint and stops; a later
status request checks once. Never describe a stopped monitor as still active.
The parent offers the existing exact ESS payload for separate approval only
after final publish/readiness verification on either path, then the full final
completion template after approved ESS success. Core previews remain unchanged.

Public companion results retain opaque publish_operation_id and normalized
status/readiness. Private correlation stays in its checkpoint; the authoritative
Core receipt is relayed unchanged. Core-required artifact hashes and Task Hook preview/approval envelopes are retained internally.

## Error Table

| Field | Show to Administrator |
|---|---|
| Stage | Functional stage name |
| Result | Failed or blocked |
| HTTP status | When available |
| Safe Fusion message | Yes |
| Recommended action | Yes |
| Stack traces, secrets, internal fingerprints, and diagnostic artifact paths | Never; generated XLSX access is shown only in its separate ABO workbook-access message |

## Internal-Only Metadata

Persist but do not normally display: normalized input binding, validated contract binding, payload binding, artifact bindings, approval bindings, invalidation details, and execution-node identifiers.
