# Manage Legal Addresses Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Country, layout, time-zone, or export resolver returns zero or many | Stop and show normalized inputs, request or filter, result counts, eligibility predicates, and candidates |
| Equivalent address exists | Return Existing Match and do not create a duplicate |
| Import completes with ValidatedFlag N and GeometryStatusCode DIRTY | Accept and disclose the unvalidated state; do not claim canonicalization |
| Import reports location, source-reference, or geography failure | Preserve package fingerprint and process evidence; do not retry with guessed values |
| Final package readiness fails | Stop before Data Loader preview; disclose the exact missing or changed archive evidence and rerun the selected task SKILL.md local FSM package-preparation workflow |
| Blank or incorrectly formatted LeFormattedAddress | Stop before preview; derive a nonblank value under ora_defaulting_rules.md, replace every comma with slash, and revalidate the final CSV and archive |
| Existing or unrelated upload rows | Stop before preview; rebuild a separate create archive containing only the reviewed new addresses and header-only companion CSVs; never replay the populated baseline |
| A broader export container is Completed with errors | Inspect the exact process log and archive. Accept evidence for this task only when every required object/member completed successfully with zero failed, warning, or partial rows and every failure is proven outside this task; otherwise block. |
| Import status is nonterminal beyond the approved wait | Stop with environment, operation, task code, ProcessId, last status, elapsed time, and next-check path |
| Data Loader status disagrees with FSM process/log evidence | Report each layer separately and the task outcome as pending or unverified until reconciled; do not infer address failure or resubmit |
| Required process log is missing, stale, incomplete, or unreadable | Report the observed status with the log limitation; do not quote a verified task-level success or failure or invent a root cause |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Required, conditional, length, type, or layout rule fails | Correct the exact field and rerun preview |
| Catalog mismatch | Target metadata, header, layout, or resolver evidence conflicts | Refresh authoritative evidence and re-author |
| Auth or authz | Required identity or privilege is unavailable | Refresh approved cached authentication once for a read, then stop |
| Transport or environment | Network or target service fails before side effect | Retry only a known idempotent read with bounded backoff |
| Fusion API or process failed | Fusion rejects or a process reaches failed terminal state | Persist redacted status/log evidence and do not replay automatically |
| Broader export contamination | A broader export failed outside this task while every required object/member has complete successful evidence | Scope strictly to this task, disclose the exception, and continue only after all baseline checks pass; otherwise classify as package evidence failure and block |
| Process timeout | Import remains nonterminal beyond the approved wait | Do not resubmit; provide next-check path |
| Re-export mismatch | Terminal success does not produce the expected semantic row | Show expected-versus-actual natural-key and field differences |
| Package readiness | Final archive identity, baseline, metadata/header preservation, new-row-only scope, nonblank normalized LeFormattedAddress, ZIP, hash, inventory, diff, receipt, or unchanged-source evidence fails | Rebuild locally through the selected task SKILL.md workflow and revalidate the complete graph |
| Status discrepancy or insufficient outcome evidence | Data Loader status conflicts with the underlying FSM process/log, or a required log/counter is unavailable | Preserve the observed statuses and evidence limits; reconcile the existing request read-only before declaring a task outcome or retrying |

## Log-Based Outcome Verification

These are task-specific interpretation rules for a user-requested status, result, error analysis, or verification. Keep central Data Loader monitoring/reporting unchanged: use its status/error/log helper first, preserve its report, and distinguish the returned Data Loader status from the legal-address outcome. Accepted initiation remains submission only; do not add automatic polling after initiation.

1. Correlate the target environment, submitted archive/request, task code and returned FSM migration process ID. Retrieve and read the current FSM ProcessLog through the existing monitoring workflow; also inspect the underlying process completion state when needed to resolve a discrepancy. Check dataSetErrors even when aggregate counters show zero errors. Never diagnose from the dataset status label alone or a log for a different run.
2. Read the relevant LegalLocation stage, final available object counters, diagnostic messages, terminal process state and overall outcome. Logs can contain repeated progress snapshots: use the latest applicable counters per object, never sum cumulative snapshots. Separate successful address work, skipped duplicate rows, other object errors, and process-level failure. Unexpected processing of existing legal entities or other companion objects is a scope discrepancy to investigate, not an expected part of a create-only load.
3. A Data Loader error while FSM reports incomplete or its log continues progressing is a status discrepancy. State the observed Data Loader error and FSM progress separately; keep the overall task outcome pending or unverified. A timeout or status-synchronization fault is only a hypothesis unless explicit evidence establishes it. Aggregate zero counts do not prove zero addresses were processed. Empty error results do not prove success or explain an error label.
4. Quote verified import success only when terminal FSM/log evidence supports success for the requested new address count with zero failed rows and any warnings explained. A success for a LegalLocation stage while the overall process is incomplete supports a stage-progress statement only. Before claiming exact address or field persistence, re-export current same-target data and match the reviewed components and new source references; report missing, ambiguous or mismatched rows explicitly. Compare authored LeFormattedAddress with the returned value and generated display fields separately; formatting differences alone do not prove creation failure.
5. Quote verified failure only when a correlated terminal FSM result/log or explicit fatal error supports it. Identify the failing stage and actionable diagnostic, distinguish any successful or persisted addresses, and do not attribute unrelated object errors or skipped rows to the new address. If a terminal failure has no diagnostic cause, report that the cause is unavailable; do not guess. Reconcile any partial write before a new submission.
6. If the log, completion evidence, or required counters are unavailable or conflicting, report what is known and what remains unverified, with the existing request/process and the next read-only check. Never turn missing evidence into success, failure, or permission to replay the import.

## Final Package Readiness Gate

| Check | Required Evidence |
|---|---|
| Target identity | Exact target environment and task identity for XLE_MANAGE_LEGAL_ADDRESSES |
| Baseline | Fresh same-target, same-release, successful same-task FSM export receipt |
| Package structure | Current ASM metadata and exact expected member hierarchy |
| CSV contract | Exact exported header bytes/order, encoding and member hierarchy; only reviewed new rows in XLE_LE_LEGAL_ADDRESS.csv; all companion CSVs header-only; required system blanks preserved |
| Semantic scope | Address data-row count and identities equal the reviewed unique new candidate set; zero existing data rows included across the archive; documented CreatedByModule, new collision-checked OrigSystemReference, validation-status semantics, and country style/layout |
| LeFormattedAddress | Every new row has a nonblank comma-free value exactly matching ora_defaulting_rules.md derivation and the preview; spaces preserved for complete-line comma replacement |
| Preservation | Baseline remains immutable; ASM metadata and exact CSV headers/encoding/hierarchy retained in the separate upload; existing baseline data rows deliberately excluded, not deleted in Fusion |
| Forbidden values | No unsupported, physical, audit, ESS, object-version, authority, function, or service-owned value is introduced except a carrier explicitly authorized by the task rules |
| Archive validity | Final immutable archive is a valid ZIP |
| Fingerprint | SHA-256 of the exact final archive |
| Review evidence | Final member inventory with baseline/upload data-row counts and semantic diff showing excluded existing rows, only reviewed new address rows included, and zero companion data rows |
| Receipt | Sanitized package-preparation receipt with no secrets or sensitive payload values |
| Freshness | No source, value, mapping, package, member, or hash changed after validation |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Preview | Exact new candidate identities and count, nonblank LeFormattedAddress and derivation, user components, resolved style, defaults, Generated/Null/System treatment, new source references, N/DIRTY meaning, zero existing rows included and zero companion data rows |
| Failure | Failure class, environment, task code, stage, safe redacted evidence, external IDs, and recommended action |
| Scoped export exception | Overall process state and ID, each failed object and detail from the exact process log, required-object states and row counters, archive fingerprint, and the task-scope decision |
| Verification | Correlated FSM process/log state and LegalLocation counters, exact re-exported new keys/components and source references, authored versus returned formatted fields, validation status, and proof no unrelated data rows were submitted; claim unrelated stored rows are unchanged only with separate supporting evidence |
| Conflicting or incomplete status | Exact observed Data Loader status and underlying FSM progress, checked log stage/counters and limitations; distinguish pending or unverified task outcome from a verified terminal success/failure |
| READY_FOR_DATA_LOADER_PREVIEW handoff | State that this is validation and handoff only; the central Data Loader preview has not been created or approved |
| Archive change | Identify the change and require complete graph revalidation, local package preparation, and a new central preview |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Missing or ambiguous evidence | Do not guess, fuzzy-match, select the first row, or use exported business values beyond the exact legal-address exception |
| Uncertain or failed write | Do not retry automatically or submit a second package before read-only reconciliation |
| Existing-row replay | Do not upload a populated baseline or any existing data row as part of this create-only workflow; do not broaden an address request into processing existing legal entities or registrations |
| Missing LeFormattedAddress | Do not leave it blank, treat it as a generated-display field, or pass a comma-containing value after normalization |
| Outcome claim without log verification | Do not claim a verified task-level success/failure from initiation, aggregate Data Loader status/counts, an incomplete stage log, or missing diagnostics alone |
| N/DIRTY result | Do not describe the address as geography-validated or canonicalized |
| Broader export ambiguity | Do not hide the overall error, ignore a failed object, or accept the archive when a required-object status/counter is failed, warning, partial, missing, or indeterminate |
| Package gate | Do not require, infer, record, or claim user approval; do not upload, initiate, or mutate Fusion |
| Approval-bound action | Only core.data-loader may create the later preview, obtain explicit approval, verify the exact archive hash, upload, and initiate |
| Final archive changed | Do not reuse the readiness result or a central preview; require complete revalidation and a new preview |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| LA.PACKAGE_PREVIEW_GATE | decision | 60 | execution_gate | ready->LA.READY_FOR_DATA_LOADER_PREVIEW;blocked->LA.HANDLE_ERROR;failure->LA.HANDLE_ERROR | LA.ENFORCE_DESIGN | stop | After the task SKILL.md local workflow has produced the exact final immutable FSM ZIP and immediately before core.data-loader builds its preview |
| LA.HANDLE_ERROR | step | 70 | error_handler | handled->LA.RETURN_ISSUES | none | stop | Any validation, lookup, dependency, default, enforcement, or package-readiness failure |
| LA.RETURN_ISSUES | terminal | 80 | terminal | none | none | stop | A blocking issue was classified and disclosed |
| LA.READY_FOR_DATA_LOADER_PREVIEW | terminal | 90 | terminal | none | LA.PACKAGE_PREVIEW_GATE | stop | All task rules and final-package readiness checks passed; the central Data Loader preview has not yet been created or approved |
