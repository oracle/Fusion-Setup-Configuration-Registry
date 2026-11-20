# Manage Common Options for Payables and Procurement Error Handling

For inaccessible additional REST validation, follow the availability policy
in ora_reference_lookups.md: retain the sanitized failure class and status,
preserve values, emit UNVERIFIED_API_UNAVAILABLE and continue preparation and
preview. This is a non-blocking warning, not a passed lookup or automatic
approval. The missing-evidence and auth failure stops below still apply to
BU/ledger identity, SOAP account validation and checks without this exception.
Completed negative or ambiguous reference results still require correction.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Template, header, node, or row-field-count mismatch | Stop, retain a sanitized package-shape finding, and recreate the candidate from the exact same-task template |
| A product-validated field lacks its required resolver evidence | Stop before preview unless the supplemental REST availability policy applies; record the specific attribute and missing resolver category |
| A transport-sanity-only field lacks a business-domain validator | Do not block a structurally valid candidate. Record the limitation so Fusion import/reconciliation remains the final acceptance check. |
| A direct LOV resolver has no exact eligible match, or a target/context resolver is ambiguous | Stop the local candidate and ask for corrected input or evidence. Do not fuzzy-match, select the first value, or reuse an export value. Report `AP:::AP_ATTR_NOT_EXISTS_TARGET_INS` only if the Fusion import actually returns it. |
| EnterpriseId is unresolved after applying the defaulting precedence | Ask for the affected row's EnterpriseId. Explicit input is allowed even when the export is empty, all blank, or has multiple distinct IDs. A singleton nonblank export value needs no confirmation. |
| The ERP Financials BU or ledger receipt does not prove one exact BU and its matching primary ledger | Stop before candidate construction. A user-entered EnterpriseId is allowed but does not replace BU/ledger evidence. Do not substitute a cross-pillar endpoint, user-entered SOBName, first returned row, or unrelated ledger. |
| HCM bill-to name resolution returns an authentication, authorization, transport, service, or endpoint-access error | Stop name resolution and ask for InternalLocationCode only if missing; never guess it or treat the error as no match. With an explicitly supplied code, use the declared FSCM fallback. Inaccessible supplemental checks may continue with a warning under the availability policy. |
| `SOBName` cannot resolve to exactly one ledger | Reject the row because `SetOfBooksId` is mandatory in the underlying entity |
| Read-only account preflight returns Invalid | Explain the outcome and offer the account-validation recovery choices below before returning the blocking issue. Invalid alone proves neither absence nor creation eligibility. |
| An account-segment field reaches governed import execution | If GL returns an invalid-combination result, preserve the redacted error and stop without retry. If it returns a newly created CCID, treat it as a verified side effect of the approved artifact and reconcile it through the Data Loader route |
| An approved direct account-combination SOAP creation receives a timeout, transport failure, HTTP 401, HTTP 403, or SOAP fault | Do not replay the mutating request. Preserve sanitized request identity and failure evidence, then run read-only `DynamicInsertion=No` reconciliation for the exact ledger and full string before considering any further action |
| An approved direct account-combination SOAP creation returns `Invalid` | Preserve the sanitized receipt and Invalid result; the receipt does not retain the detailed GL rejection reason. Do not create segment values, modify the request, or retry. Investigate the underlying ledger, segment-value, cross-validation, or dynamic-insertion condition before requesting new approval |
| An approved direct account-combination SOAP creation returns `Valid` but the no-create follow-up does not return Valid with the same CCID | Classify as uncertain write, preserve both receipts, and stop. Do not repeat creation; resolve through a read-only GL investigation. The receipt does not separately prove an enabled flag |
| Data Loader validation, Task Hook, preview, or approval is missing/stale | Stop before mutation; changed input requires a new validation and approval cycle |
| Fusion process, authentication, transport, or verification fails in a later governed execution | Preserve redacted process/status evidence and do not replay an import automatically |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Package contract gap | Header, row count, metadata node, or archive contract differs | Refresh/rebuild the exact package |
| Product-validation evidence gap | A changed field with an import-hook/entity/GL resolver lacks its required evidence | Obtain the named task-specific evidence |
| Transport-sanity disclosure | A changed field has no source-backed business domain beyond CSV shape | Preserve the type/length/precision/date result and disclose that field-level semantic acceptance is deferred to Fusion |
| Technical lookup gap | A required resolver outside the supplemental REST availability exception is unavailable, returns null, has no exact eligible match, or yields an ambiguous target/context | Stop the local candidate; correct the input or obtain the named evidence. Keep any later Fusion error separate from this local classification. |
| UNVERIFIED_API_UNAVAILABLE | A supplemental REST read reports a bound API availability failure | Preserve supplied values and continue with a warning under ora_reference_lookups.md; never report the check as passed. |
| Target-context default gap | No explicit EnterpriseId or usable export-derived value, or the two ERP responses are not exact/matching | Ask for missing EnterpriseId; separately obtain valid ERP BU/ledger receipts. The ERP endpoint does not validate EnterpriseId. |
| Approval blocker | Immutable preview or current contextual approval is absent/stale | Revalidate and obtain a later approval through Data Loader |
| Auth or authz | Required privilege is unavailable | Use core's permitted read-only authentication handling; supplemental REST failures continue with a warning, while required identity and execution failures stop. |
| HCM location-route access gap | HCM name resolution remains unavailable after the permitted read-only authentication handling | Ask for InternalLocationCode only if missing; with supplied CSV inputs, follow the declared fallback and supplemental availability policy. |
| Transport or environment | Network or target service fails before side effects | Retry only bounded idempotent reads in the selected workflow |
| Fusion API or process failed | Later governed submission/process fails | Persist redacted log/status and do not replay |
| Process timeout | Status remains nonterminal | Do not resubmit; preserve the process identity and provide the next-check path |

## Account Validation Recovery

Read the preflight receipt's `recovery` outcome. `INVALID_COMBINATION` means GL
rejected this ledger/account; it does not identify the reason. Explain that the
combination may be missing or may fail another GL rule, then offer to correct or
use an existing account, review the separately approved creation path, or stop.
Do not require the user to know SOAP flags. Respect an explicit prohibition on
GL creation; explain that creation review requires a new user decision, and
continue only with correction or stop unless that restriction is changed.

If the user selects creation review, retain the exact ledger and ordered
segments and disclose that absence and creation eligibility are unverified.
Use the existing `account_combination_create.py --preview-output` workflow and
its exact request-bound approval before any `DynamicInsertion=Yes` call. A
choice to review creation is not execution approval. Never infer the chart of
accounts' Dynamic Insertion setting from the request flag or an Invalid result.

After successful approved creation, run `account_combination_preflight.py`
with `DynamicInsertion=No` for that same ledger/account. Require a valid result
and matching returned CCID before resuming the pending AP preparation. If
either CCID is absent or differs, retain both receipts and investigate instead
of recreating the account. Group repeated field requests by exact environment,
ledger and ordered segments; create an approved combination once and bind its
fresh verification evidence to each affected field. Preserve existing valid
combinations and completed verified creations. Uncertain outcomes retain the
no-replay rule above.

After correction or successful creation verification, finish recovery at
`APCO.RESUME_PREPARATION` and begin a new preparation pass at
`APCO.VALIDATE_INPUT` / `APCO.RESOLVE_REFERENCES` with the pending AP request and
current bound receipts. This resumes the user's task without replaying completed
GL creation; it does not bypass reference checks, Data Loader review or approval.

For `VALIDATED`, retain the bound receipt and resume AP preparation; an absent
optional CCID in ordinary validation is not proof that creation is needed.
For `SERVICE_FAILURE` or `INCONCLUSIVE_RESPONSE`, explain the service/access or
response failure and obtain valid read-only evidence before proceeding. Do not
offer creation as a remedy for those failures. Parser and transport exceptions
likewise remain failures, not missing-account evidence.

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Static blocker | Exact task code, resource rule, missing evidence, and safe next action |
| Future preview | Exact target, immutable artifact identity, package-shape receipt, unresolved blockers, and current approval state |
| Future failure | Failure class, environment, stage, redacted evidence, external IDs when available, and recommended action |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Unknown business behavior | Do not invent a default, requiredness rule, accepted value, lookup, or update behavior; apply only the declared transport sanity when no product-backed field contract exists |
| Incomplete resolver | Do not call an undocumented service, fuzzy-match, or select the first candidate |
| Missing Data Loader gate | Do not upload, invoke a task adapter, import, or otherwise change Fusion |
| Uncertain write | Do not replay until read-only reconciliation establishes side effects |
| Direct SOAP creation is requested without exact current approval | Do not set `DynamicInsertion=Yes`; obtain a new approval bound to the ledger, full segment string, endpoint, operation, and side effect |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| APCO.HANDLE_ERROR | step | 60 | error_handler | account_invalid->APCO.ACCOUNT_RECOVERY;handled->APCO.RETURN_ISSUES | none | stop | Classify any failure; route a completed Invalid no-create account result to recovery review |
| APCO.ACCOUNT_RECOVERY | decision | 65 | execution_gate | revalidated->APCO.RESUME_PREPARATION;stopped->APCO.RETURN_ISSUES | APCO.HANDLE_ERROR | stop | Local recovery review only; follow Account Validation Recovery for separately approved creation, no-create verification and resumption |
| APCO.RETURN_ISSUES | terminal | 70 | terminal | none | none | stop | A blocking issue was classified and disclosed |
| APCO.RESUME_PREPARATION | terminal | 75 | terminal | none | APCO.ACCOUNT_RECOVERY | stop | Recovery passed; start a new preparation pass for the pending AP request using current bound no-create evidence without replaying GL creation |
| APCO.DONE | terminal | 80 | terminal | none | APCO.ENFORCE_DESIGN | stop | Required checks passed and unavailable additional REST checks are disclosed as unverified |
