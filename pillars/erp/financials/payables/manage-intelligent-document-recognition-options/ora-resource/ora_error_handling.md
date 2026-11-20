# IDR Error Handling

Stop before retry when an import or persistence outcome is unclear.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Image Attachment Formats value requested | Reject an actual change or missing baseline proof. Interpret supported labels only for comparison with the fresh baseline; accept exact equality as a no-op and preserve the exported value unchanged; image-only no-ops create no ZIP. Overrides cannot authorize changes, and prepared ZIPs must preserve all six values. |
| Create requested | Reject the operation; update an existing IDR setup only. |
| Extension OptionCode differs from AP_PRORATE_FREIGHT_MISC | Reject before package generation; do not target ORA_AP_IMAGES or ORA_POLICY_DETAILS. Leave untargeted rows out of the update ZIP and verify they remain unchanged in target state; do not copy extra rows from another source. |
| Target record or allowed extension row is absent | Block. No row creation or automatic repair. |
| Fusion import returns an error or uncertain state | Retain exact request and process identity, inspect returned diagnostics and a fresh export, and stop before retry or rollback decisions. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Unsupported request | Create or disallowed extension code | Ask for an update to an existing allowed record or a corrected code. |
| Dependency blocked | Existing options singleton or required extension row missing | Obtain a fresh target export; do not submit an import. |
| Product validation | Fusion rejects a controlled update | Preserve exact diagnostics and compare a fresh export before any retry. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Candidate preview | Existing target identity, requested fields, canonical choice codes, extension selector, unresolved blockers, and package diff. |
| Live import | Exact task, nonproduction environment, candidate digest, source export identity, and separate Data Loader approval record. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Fresh target CSV contains other extension rows | Their presence in the baseline is valid. Leave them out of the update ZIP, reject operations on them and additions/removals, and verify they remain unchanged in the post-import export. |
| User names a UI field but writeability is unresolved | Do not treat mapping alone as permission to mutate. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| IDR.DONE | terminal | 50 | terminal | none | IDR.DESIGN.ENFORCE | stop | All task-local validation gates pass; return readiness to Run Book and Data Loader without writing Fusion state. |
| IDR.ERROR.BLOCK | terminal | 60 | terminal | none | none | stop | A validation, dependency, or design gate fails. Return a specific blocker. |

## Import outcome and saved-state verification

Submission, job completion and saved-configuration verification are separate outcomes. An initiation response is in progress, not verified completion. Follow the active Run Book/Data Loader status/results workflow and its authorization and polling limits; these task rules do not introduce a direct client or automatic polling route.

When evaluating import results, obtain the exact request/process final status, total/loaded/failed object counts when supplied, and all applicable paginated error/warning diagnostics through the declared core service. Inspect diagnostics even when the status says success or failed counts are zero. Missing status, unavailable diagnostics, incomplete results or a polling timeout leave the outcome unverified; disclose the missing evidence and the supported next-check path. Never translate processed counts into proof that every requested row/value was saved.

Then obtain a fresh, sufficiently complete exact-task export from the same target environment through the supported workflow. Reconcile each requested update and supported explicit clear by its task identity and expected stored values, including source-backed service-derived values. Check preserved records/fields; this task declares no parent/child creation contract; allow only documented audit/service transformations. Treat the original approved artifact/design as immutable evidence. With valid evidence, a missing target, skipped child, unchanged requested value, partial persistence or unintended change is verification FAIL even if the job succeeded. Without that evidence, retain the DIFFERENT comparison and report verification PENDING.

Report job outcome and reconciliation outcome separately. Claim verified completion only when the job reached an accepted successful terminal state, failed objects are absent, diagnostics contain no unresolved actionable errors/warnings, and every requested saved value and applicable preservation check passes. If counts or diagnostics are unavailable, do not assume zero. Report failed or partial results with affected keys/fields and permitted diagnostics, retaining confirmed successes. Do not retry the import or perform rollback automatically; reconcile first and use the active workflow's retry/recovery and approval rules.

## Fresh post-import export evidence

Matching file contents establish only a comparison result. To claim saved-value verification, the active supported workflow must retain an evidence chain binding the intended target environment identity/base URL and exact task code to the approved baseline, operation design/requirements and immutable import ZIP hashes; the actual import request/process ID; its confirmed terminal status (success or failure) and completion time; and a separate exact-task data export request/process ID, start/completion times, downloaded artifact hash and receipt. Correlate request IDs to the core service's status/export records, not user-entered labels, file names, local modification times or copied candidate metadata. Redact credentials and sensitive payloads.

The verification export must be requested after confirmed import completion, finish successfully, contain the required data scope rather than a template, and come from the same intended environment and task. Record timezone-aware timestamps and establish the order import completed -> export requested -> export completed -> artifact retrieved. A baseline export, candidate ZIP, earlier export, unknown-time export or missing/mismatched request/file/environment/task binding cannot prove persistence even when every value matches. Missing or incomplete scope or provenance leaves verification PENDING; report the missing evidence and obtain a supported fresh export rather than inventing receipts. Do not infer export freshness from a different file hash alone.

Task-local reconciliation is an offline value comparison: `comparisonStatus` reports MATCH/DIFFERENT, while matching values alone return `status: PENDING` and `persistenceVerified: false`. Its report cannot certify the external evidence chain; only the active workflow may combine the comparison with independently obtained core-service import/export records to claim verified completion. An offline mismatch is DIFFERENT; saved-value verification remains PENDING until valid evidence supports PASS or FAIL. If that workflow cannot obtain or validate the required evidence, stop the completion claim and report the gap; this guidance adds no external execution route or automatic polling authorization.

## Every requested field must be compared

Reconcile every requested field, including explicit blank clears, using three values: the normalized requested stored value, the actual submitted ZIP cell and the fresh post-import export cell. Do not use the design as a substitute for inspecting submitted cells, or stop after the first saved field matches. Identify each result by operation, CSV member/entity, exact task record key and field. Show submitted and saved mismatches separately with expected/actual values, preserving any documented date/service transformation and its evidence. A missing record is distinct from an empty cell and cannot satisfy a clear request. Keep matching fields visible so partial persistence is explicit; retain safe values or redact sensitive values under the task policy. File comparison remains separate from the required import/export provenance chain and final job outcome.

## Verification result meanings and partial failure

| Result | Meaning |
|---|---|
| PASS | Valid import/export evidence confirms the requested values were saved. |
| FAIL | Valid evidence shows missing or different values. |
| PENDING | There is not enough valid evidence to confirm the saved result. |
| MATCH / DIFFERENT | Files were compared offline; this does not prove an import occurred. |

Apply these meanings to saved-value verification, separately from job status and pre-import validation. The offline adapter returns verification `status: PENDING`, `persistenceVerified: false`, and `comparisonStatus: MATCH` or `DIFFERENT`. It cannot promote a comparison to verification PASS/FAIL without an independently validated import/export evidence chain. Keep all mismatch details even when verification is PENDING. A malformed input or rejected pre-import validation may still report its own validation failure; that is not a saved-value verification FAIL.

An import failure can leave partial changes. Preserve exact request IDs, approved artifact references/hashes, failed-object counts and permitted diagnostics; report confirmed saved changes, confirmed mismatches and unresolved records separately. Do not assume atomic rollback, retry the import, undo changes or delete/recreate records automatically. Any later recovery requires a separately authorized, validated action through the supported workflow after inspecting saved state. Missing post-failure evidence leaves verification PENDING; a job's failure alone does not establish what was or was not saved.

## Regression and audit evidence boundaries

Use synthetic fixtures for builder-to-upload round trips and for creates, updates, child-only operations, explicit clears, missing dependencies, invalid values and batch conflicts where supported. Test the task's rejection rule when an operation is unsupported; do not invent a create/clear/child contract to make a case pass. Exercise candidate reuse, wrong-target export metadata, stale baseline reuse, missing evidence and changed files as offline verification-refusal cases. They establish PENDING safety boundaries, not proof that a live import or full receipt-verification path was tested.

Keep expected verification result, actual verification result and test result as separate report fields/columns. Show offline MATCH/DIFFERENT separately. Store environment-specific fixtures, job records and execution evidence in the project workspace; historical fixtures and prior approval receipts never authorize a later live run. Bind each test/audit record to the exact files and hashes examined. Refresh changed test bindings and rerun relevant tests and the final scope audit after later edits. A package audit is not proof of Oracle importer behavior or a later file revision.
