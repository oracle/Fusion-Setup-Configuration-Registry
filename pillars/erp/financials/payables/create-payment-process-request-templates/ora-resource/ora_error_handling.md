# Error Handling

Apply the field mappings and resolver rules in [Reference Lookups](ora_reference_lookups.md).

This resource returns task-rule results and preserves the active Run Book/Data Loader execution boundary. Source error identifiers below are implementation evidence, not a claim that their rendered text or every path was observed in a live import.

For post-import acceptance, follow [persistence verification](../references/persistence-verification.md).
An unexpected or missing selection member in an affected template is a
comparison failure even when all requested scalar values match. Preserve the
observed state and diagnose it before any separately approved recovery. A
missing internal framework label alone does not invalidate supported input or
prevent ordinary create/update preparation.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Input shape, type, required identity or field-operation check fails | Return the affected record/field, failed contract and safe correction before package preparation. |
| An offline adapter command fails | Return nonzero with failure_class, stage naming the failed command, and recommended_action both at the report top level and on the affected errors row. Classify OSError as artifact_persistence, unsafe output paths or overwrite conflicts as approval_blocker, and invalid inputs as input_validation. Preserve a sanitized diagnostic and safe correction. |
| TemplateName is blank or violates exact identity uniqueness | Preserve FND_CMN_REQ_ATTRIB_API_SERV or FND_CMN_RCRD_VAL when returned under its actual condition; do not invent rendered text. |
| AddlPayThruDays is negative | Preserve FND_CMN_POSITIVE_OR_ZERO for this proven bound. Do not apply that message name as a minimum rule for other day fields. |
| From/Hi payment priority exceeds To/Low | Preserve AP_PAY_ENTER_HIGHER_PRIORITY and disclose the two mapped fields. |
| InactiveDate violates the source current-date expression | Preserve FND_CMN_END_DTE_ERLY_EQ_TDAY under newValue >= currentDate. |
| An applicable selected currency/BU group is missing a child | Preserve AP_PAY_SPECIFY_PMT_CURRENCIES / AP_PAY_SPECIFY_OPERATING_UNITS under their actual option conditions. Do not generalize source-group EXCLUDE semantics. |
| Cross-currency conversion type source list validation fails | Retain FND_CMN_INVALID_ATTRB_API_SERV when emitted for the evidenced nonnull XCurrRateType validation; do not imply a complete captured rate-label domain. |
| Method LE/BU applicability fails | Retain IBY_AP_VLDT_METHOD_LE / IBY_AP_VLDT_METHOD_ORG with the selected context and safe correction. Missing-code generic-exception wording remains unqualified. |
| Profile bank/BU/currency/method applicability fails | Retain IBY_AP_VLDT_PROF_ACC / IBY_AP_VLDT_PROF_ORG / IBY_AP_VLDT_PROF_CURR / IBY_AP_VLDT_PROF_METHOD only for the corresponding source validation. Profile-currency count failure is not universal currency-master rejection. |
| Printed profile/default-document or explicit-document context fails | Preserve IBY_APSUB_NO_DEFAULT_PMT_DOC / IBY_BUILD_MISS_PMT_DOC_REL_PAR only under their source conditions; do not make a payment document universally required. |
| Import resolver has no first row or more than one possible match | Use its exact source-specific boundary. Source first-row selection is not a duplicate-rejection guarantee; the BU null-return mapping explicitly clears its derived OrgId. Do not invent a uniform no-match exception. |
| FSM import catches an exception | Retain the sanitized localized message in the governed process diagnostic. Do not infer all rows rolled back or replay a partial/uncertain write. |
| A source/evidence gap is essential to the requested candidate | Return evidence_unresolved with exact field, operation, unanswered question and expected FSM failure surface. Offer eligible unresolved business UPDATE application validation after explicit exact-field/exact-candidate acceptance; preserve warning/override in blueprint and immutable preview, normal environment authorization, Data Loader approval, one submit, diagnostics and fresh-export reconciliation. Protected keys/audit/identity, proven-invalid, malformed or unsupported behavior remain blocked. |
| An authorized later import fails or times out | Use the active core status/diagnostic workflow for that same attempt; preserve request/process identity and known partial successes. Stop before another write, corrected candidate preview and separate approval. |
| Fusion succeeds but persisted-state or Run Book outcome is incomplete | Keep Fusion execution, persisted-state verification and Run Book synchronization separate; do not resubmit a successful import to repair tracking. Human completion/disposition remains required. |
| A proposed readback reuses baseline/candidate path or digest, mismatches environment/release, or has a blank/reused ESS request identity | Reject the readback input. A different archive and metadata identity are necessary comparison checks, not proof of independent fresh acquisition. Obtain readback through the owning export workflow and retain its process/status, digest and context. |
| An offline readback comparison completes | Report status COMPARISON_ONLY with comparisonStatus PASS when values match, or status FAIL with comparisonStatus FAIL when they do not; persistenceVerified=false in both cases. The owning Run Book/export workflow must establish successful independent post-import acquisition and reconcile the result before claiming persistence; archive metadata or matching rows alone do not supply that proof. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input validation | Missing/invalid business inputs, types, row widths or fixed package codes | Correct affected inputs and regenerate candidate preview |
| catalog mismatch | Task identity, members, headers or metadata paths do not match the exact package | Restore same-task scope and shape; no alternate task substitution |
| evidence unresolved | Requested field transformation, eligibility or child synchronization relies on an unclosed source contract | Close/disposition that exact question; do not invent product behavior |
| auth/authz | Workflow-selected supported reference or execution step cannot establish access | Follow owning authentication/privilege workflow; no credential persistence |
| transport/environment or Fusion API | Declared external step fails before definitive business outcome | Retain sanitized diagnostics; respect owning client's retry/idempotency rules |
| process timeout or process failed | Accepted later import has terminal failure or incomplete monitoring | Use same-attempt status/ProcessLog workflow; do not submit a replacement write automatically |
| artifact persistence or approval blocker | Immutable preview/artifact binding, retention or current approval fails | Stop before mutation and restore the active core contract prerequisites |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Task-rule result | Exact task identity, requested operation, evaluated path, affected fields, applicable source IDs, missing/invalid facts and one safe correction or handoff action. |
| Before Data Loader preparation | Candidate business effect, known alias/default/setter effects and unresolved/deferred validations; no temporary roles, reference values or test fixtures enter portable source. |
| Before any later mutation | The selected core revision's immutable preview/artifact binding and current contextual approval; changed intent/default/reference context invalidates prior approval. Task rules do not impose a new keyword. |
| After any later attempt | Fusion process outcome, offline comparison, workflow-established fresh persisted-state verification and Run Book progress separately; process success or a COMPARISON_ONLY PASS is not completed business setup. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Task rule reaches handoff | Do not issue REST/FSM writes, internal ADF calls, OAuth shortcuts or a browser import fallback. Run Book/Data Loader owns package processing, preview, approval and submission. |
| A supporting public preflight was not qualified | Do not invent one or disable a source-confirmed authoritative FSM contract solely for that reason. |
| A write failed, timed out or has uncertain status | Do not automatically retry or replace it; reconcile the accepted attempt and obtain a newly approved corrected preview when required. |
| A proposed cleanup/delete/rollback is requested | Do not infer physical deletion, child replacement or rollback from InactiveDate, omission, test cleanup policy or helper booleans. |
| Sensitive material is encountered | Do not persist credentials, tokens, Authorization headers, raw environment/customer setup rows or private opaque runtime material in portable source. |
| A registry is compiled or offline tests pass | Do not claim live environment qualification, persisted success, journey acceptance, merge readiness or permission to commit/push. |
| A readback comparison passes without independent acquisition evidence | Do not promote comparisonStatus PASS to persistenceVerified=true or a persisted-business-result claim. Obtain and reconcile successful fresh acquisition evidence through the owning workflow. |

## Local publication and recovery

Stage and validate the complete local output set before publishing it with
exclusive creation. If publication fails, remove only outputs created by that
attempt and preserve all pre-existing files. Classify malformed, missing or
schema-conflicting input as `input_validation`, unsafe overwrite attempts as
`approval_blocker`, and filesystem/publication failures as `artifact_persistence`.
Return status, stage, failure class, errors and a recommended action; write a
diagnostic through `--report` only after its output path passes preflight.
Local commands exit `0` for success or a valid no-op and `2` for a classified
failure. Correct inputs and choose fresh safe output paths before a local retry;
this does not authorize any live retry.

Preview `automaticRollbackSupported` and `rollbackLimitations`. Only declared
nullable fields may be cleared under their effective conditions; do not infer a
blank date or number can restore a prior value. Recreation of removed selections
requires a separately reviewed design. Validate each reverse operation and its
declared effects against the projected forward state, omitting unchanged fields
included only for a forward effect. Forward-operation evidence or accepted
exceptions do not validate the reverse operation: disclose any required fresh
reference evidence before presenting recovery as ready.

## Handoff Outcomes

| Outcome | Meaning | Evidence |
|---|---|---|
| PPR.READY_CREATE | Applicable task-rule checks completed for this bounded create; return to the invoking Run Book/Data Loader for its own preparation/approval gates. No Fusion write occurred. | Root operation and per-field contracts; evaluated task path |
| PPR.READY_UPDATE | Applicable task-rule checks completed for this exact-key bounded update; return to the invoking Run Book/Data Loader. No child-aggregate replacement or Fusion write is implied. | Root operation and per-field contracts; fresh retained context |
| RETURN_ISSUES | Return actionable invalid/unsupported/evidence-unresolved issues and safe resume action. No mutation is authorized. | Affected source contract and evaluated failure path |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PPR.HANDOFF_GATE | decision | 60 | execution_gate | create_ready->PPR.READY_CREATE;update_ready->PPR.READY_UPDATE;not_ready->PPR.HANDLE_ISSUES | PPR.ENFORCE_DESIGN | stop | Return only candidate-specific task-rule readiness to active Run Book/Data Loader; do not require a developer-test keyword or perform an import |
| PPR.READY_CREATE | terminal | 70 | terminal | none | PPR.HANDOFF_GATE | stop | Bounded create checks complete; handoff only, no business completion claim |
| PPR.READY_UPDATE | terminal | 80 | terminal | none | PPR.HANDOFF_GATE | stop | Exact-key bounded update checks complete; handoff only, no business completion claim |
| PPR.HANDLE_ISSUES | step | 900 | error_handler | returned->RETURN_ISSUES | none | stop | Any input/reference/dependency/default/design/handoff issue; classify and disclose without writes or retries |
| RETURN_ISSUES | terminal | 910 | terminal | none | none | stop | Return accumulated actionable issues and safe next action |
