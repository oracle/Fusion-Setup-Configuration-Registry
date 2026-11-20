# ASL Status Error Handling and Handoff

Apply [FSCR error handling](../../../../../../governance/error-handling-guidelines.md)
and the [Data Loader contract](../../../../../../core/data-loader/SKILL.md).
The data_load branch validates local input and never performs Fusion operations.
Only the explicit read_fetch branch may perform the GET declared by its lookup
resource. Import error/handoff rules below apply only to data_load; fetch-only
results and failures are handled separately.

## Normalization Evidence and Recovery

Include the raw value, typed boolean, attribute, and row for every permitted
conversion in local evidence and existing rule-result changes. Rule-result changes
are evidence, not payload edits. A captured-value violation of
[input validation](ora_input_validation.md#field-validation) requires canceling
the validation cycle, preparing a corrected source, and fresh validation/preview/approval.
Never rewrite an immutable prepared artifact or reread mutable source files to replace its
capture. Collect all issues, including those returned early by preparation helpers.

## Representation and Handoff Gates

These are source-representation safeguards, not additional business-field types.
Check them before reporting readiness, even if input and design checks pass.

| Situation | Blocking Condition | Diagnosis and Recovery |
|---|---|---|
| Explicit null in any supplied field | No supported loader null encoding established | Report unsupported_null_encoding with row and field; retain the supplied null as evidence and block file preparation. Never replace it with a blank or invented marker. Nullable permission/date fields can pass their business contract while failing this gate. |
| Any explicit date clearing | Selected Data Loader route has no verified clearing representation | Report loader_clearing_unverified and retain scoped intent. Direct PATCH acceptance is not loader verification. Block handoff; no live verification or REST fallback during validation. |
| Prepared-source fidelity | Value, type, name, precision, or field presence differs outside declared preparation rules | Report input-fidelity failure; restore original intent and rebuild the source using the permitted transformations in defaulting. |
| Captured-source fidelity | Values/headers have been rewritten, or submission would differ from the validated capture | Block handoff; cancel, prepare a corrected source, and create a fresh validation cycle. Do not apply reported changes to captured rows. |
| Incompatible source groups | One captured source represents differing supplied field sets or incompatible operation/date intent | Reprepare separate sources through skill routing, retaining original row references. A blank does not encode omission; keep-date instructions require a source without the date column. |
| Graph integrity | Required rules, source anchors, or transitions are stale, incomplete, or inconsistent | Repair and recompile the contract before resuming. |

## Error Situations

| Situation | What Should Happen |
|---|---|
| Required fields missing | List every missing row/field requirement from the intent matrix; request correction |
| Unknown field, including Description | Report the exact attribute as unsupported business input; do not alias or discard it |
| Invalid value or conflicting identity/intent | Preserve row/field issues and stop before handoff; never fall back to another identity rule |
| Mixed valid and invalid rows | Preserve each row result and all issues; block the batch from approval, with no silent partial load |
| Stale or incomplete resource graph | Report the source anchor and node; repair and recompile before resuming |
| Downstream loader rejects metadata, identity, privileges, or operation | Preserve its diagnosis and follow its documented recovery; local validation cannot override the rejection |
| Failed or uncertain write | Stop; never automatically replay a write. Reconciliation belongs to the selected Data Loader workflow |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input_validation | Missing, malformed, unsupported business attributes or contradictory intent | Correct records/context and rerun all local checks |
| catalog_or_metadata_mismatch | Wrong task or business object, unavailable registration, stale graph | Resolve metadata before approval |
| auth_expired_or_invalid / authorization_or_privilege | Downstream authentication or access rejection | Follow Data Loader recovery; perform no authentication during local validation |
| transport_or_environment | Downstream connection or environment failure | Resolve target/connectivity through the selected core workflow |
| fusion_api_error | Server rejects a record, including duplicate name or identity | Preserve sanitized error; let Data Loader resolve server requirements |
| process_timeout / process_failed | Downstream load times out or fails | Preserve known partial results and request ID; follow Data Loader status workflow only when requested |
| artifact_persistence | Required project result cannot be saved | Report failed destination and stop additional side effects |
| approval_blocker | Data Loader lacks approval bound to its final preview | Use its authoritative approval workflow |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Local success | Exact task code/name, terminal, completed path, per-row checks, recommendations, preservation effects, and READY_FOR_DATALOADER_REVIEW; verified Fusion side effects none |
| Local failure | Task identity, MISSING / UNSUPPORTED / FAILED, node, row index, attribute, issue code, failure class, and safe correction/resume step; collect all row issues |
| Downstream execution | Use Data Loader's prescribed user-facing result and approval format; never claim local readiness means import success |
| Durable results | Use active project validation/run/token records and existing core project services; redact secrets and sensitive values, and exclude credentials, opaque URLs, and protected IDs from task-node records |

## Data Loader Handoff

Only after all business checks and representation gates pass, return preserved
records, row references, scoped intent, and validation evidence for
purchasingApprovedSupplierListStatuses. Follow [skill routing](../SKILL.md#asl-status-resource-contract)
for the validation cycle, preview, approval, and execution workflow. Local field validity
establishes neither identity existence nor live operation support.

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Import client validation | No REST calls, token refresh, live lookup, metadata fetch, or Fusion mutation |
| Missing name/ID resolution | No direct REST fallback or invented matching contract |
| Local readiness | No claim of uniqueness, valid privileges, registered BO, record existence, server acceptance, or completed import |
| Error recovery | No silent attribute correction, alias, skipped row, default insertion, or automatic write retry |

## Date Action Review

Present **no initial date** for explicit create empty strings, **set** for valid
dates, **keep unchanged** only when the date column is absent, and **clear
requested** for scoped update clearing instructions. Display applicable input,
design, or representation issues beside the affected rows; null or unverified
clearing must not be presented as ready. Preserve source-row references across
groups. Mixed failures follow Error Situations; do not silently load valid rows.

## Delete Handoff

Retain user-request evidence and exact validated targets for the deletion preview.
Use [Delete Validation](ora_input_validation.md#delete-validation) for missing,
invalid, extra-field, and conflicting-control diagnostics. Unsupported deletion
metadata or server restrictions remain blockers after local success; preserve
the sanitized diagnosis. Never fall back to direct REST, MERGE, or automatic
retry of an uncertain delete. Execution and preview-bound approval follow
[skill routing](../SKILL.md#delete-asl-statuses).

## Prepared Artifact Gate

Evaluate the exact prepared ZIP through the existing
[core Data Loader workflow](../../../../../../core/data-loader/SKILL.md), using the
[captured-source contract](ora_input_validation.md#record-and-captured-source-validation).
The final artifact hash must be the one supplied to Task Hook.
Do not alter its bytes, headers, field presence, record directives or values
through ruleResults. Discard superseded preview/approval envelopes and prepare
a new artifact for corrections. Compare the artifact with the approved preparation,
retaining original row references and scoped operation intent for every affected
row, including mixed-operation work. Native DAT deletion inputs require the same
exact DELETE directive/control agreement as converted inputs. Local validation
does not establish metadata compatibility or live deletability.

| Situation | Blocking Condition | Recovery |
|---|---|---|
| CSV deletion | The final record has a MERGE directive even when its RestAction is DELETE | Block handoff. Use core Data Loader's delete XLSX preparation and validate a fresh artifact whose DELETE directive and control agree; never patch the CSV-derived DAT or submit it as a delete |
| Delete artifact | Record directive or explicit DELETE control is missing or conflicts with scoped user intent or the ID-only contract | Correct the approved source preparation and repeat core validation before preview |
| Artifact decoding | DAT values, escaping, operation controls or original row/intent association cannot be evaluated losslessly | Stop; obtain a supported prepared source/artifact through core rather than inventing a parser or execution route |

## Fetch Results and Failures

Apply only to read_fetch. These results never enter the Data Loader approval or
import handoff flow. ASL.RETURN_FETCH_INPUT_ISSUES returns status=failed,
complete=false, empty items, match_count=0 and pages_read=0 with applied criteria
and sanitized criteria diagnostics; no authentication or GET has occurred.

For ASL.RETURN_FETCH_RESULT, preserve the lookup's items, applied criteria,
observed match count and pages_read. Malformed responses or
HTTP/auth/access/transport failures stop the read with sanitized stage/diagnostics.
Partial results cannot establish not_found or ambiguous. Use failed for preflight
or first-request HTTP/transport failure before a valid page; malformed collection
data is incomplete even on page one. Otherwise use incomplete for unfinished
traversal. Page-limit exhaustion is incomplete; an early match cannot override it.
Never convert a failed read into an empty successful result or use a read error
as an import fallback. Follow only the shared core client's recovery policy.

Return fetch_result: status (found/not_found/ambiguous for completed exact-name
reads; complete for completed text/list reads, including zero matches; otherwise
incomplete/failed), complete, applied_criteria, items, match_count, pages_read,
and diagnostics. Show a compact seven-field table in requested field order,
explicit nulls, criteria, count, and completeness; partial counts are observed
matches only. Show ambiguous candidates without choosing one. Errors are not
empty-result claims, and results never authorize mutation. Keep results in memory
unless an artifact is requested through existing project services.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ASL.HANDOFF | decision | 40 | execution_gate | ready->ASL.READY;blocked->ASL.HANDLE_ISSUES | ASL.CHECK_DESIGN | stop | Evaluate every Representation and Handoff Gate and Prepared Artifact Gate; all rows must pass business rules and representation checks before Data Loader review; no execution authorization |
| ASL.READY | terminal | 50 | terminal | none | ASL.HANDOFF | stop | Return READY_FOR_DATALOADER_REVIEW with verified Fusion side effects none |
| ASL.RETURN_FETCH_RESULT | terminal | 60 | terminal | none | ASL.FETCH_STATUSES | stop | Explicit read_fetch only; return Fetch Results and Failures with existing fetch_result statuses and completeness, including partial observations; never enter Data Loader handoff |
| ASL.RETURN_FETCH_INPUT_ISSUES | terminal | 65 | terminal | none | ASL.VALIDATE_FETCH_CRITERIA | stop | Explicit read_fetch with invalid or unsupported criteria; return failed with complete=false, empty items, zero matches/pages and sanitized diagnostics without authentication or GET |
| ASL.HANDLE_ISSUES | step | 90 | error_handler | reported->ASL.RETURN_ISSUES | none | stop | Classify all reached local issues with row and field context |
| ASL.RETURN_ISSUES | terminal | 100 | terminal | none | ASL.HANDLE_ISSUES | stop | Return MISSING for missing inputs, UNSUPPORTED for unsupported intent, otherwise FAILED; mixed failures use FAILED and retain individual issue types |
