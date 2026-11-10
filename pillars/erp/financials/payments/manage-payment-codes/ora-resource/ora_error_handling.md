# Manage Payment Codes — Error Handling

Error identifiers are source-proven validations, not observed live CSV failures. The reviewed live FSM caller converts CSV metadata/values to XML before the task's readXML call. The converter marks explicit-null output; successful blank/default or audit-field acceptance remains unqualified. SRC-CS-AMIMPL 203–239 shows localized processing-error handling; no direct task PL/SQL call was observed. Framework sources: SRC-CS-FSM-MIGRATOR, SRC-CS-FSCORE-CSVXML, SRC-CS-FSCORE-MIGRATOR.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Invalid type | Local static mismatch: report the supplied type and request one reviewed canonical code or unique label before candidate generation. If Fusion validation returns FND:::FND_CMN_INVALID_ATTRB_API_SERV from PaymentCodeType_Rule_0, disclose that observed application error; do not label a local check as a live import result; SRC-CS-EO |
| Invalid date order | Disclose FND:::FND_CMN_FRM_ERLY_EQ_TO_DATE when EndDate < StartDate; SRC-CS-EO |
| Reserved prefix | Disclose IBY:::IBY_RESERVED_SEED_DATA_PREFIX for customer ORA_ codes; SRC-CS-EO |
| Overlength string | Report record/field, actual length, source maximum, characters and correction required; never truncate; SRC-CS-EO, SRC-CS-TLEO |
| Duplicate CSV header | Reject duplicate names after case normalization. If the converter returns ASK_CSV_DUPLICATE_COLUMN, preserve the observed diagnostic and identify the member/header; SRC-CS-FSCORE-CSVXML |
| CSV row width or parent mismatch | Reject short/extra fields and unmatched parent-key pairs before preview. The converter checks row width and emits ASK_CSV_MISSING_PARENT_ROW when the required parent row is absent; preserve actual errors separately from local validation; SRC-CS-FSCORE-CSVXML |
| Partial resolver/default/lifecycle | Return exact missing contract; do not infer authority, suppress field or call a substitute endpoint; approved prompt and resource-authoring contract |
| Import processing exception | Preserve localized processingError and available status/log under project diagnostics; SRC-CS-AMIMPL |
| Timeout/uncertain mutation | Stop; preserve original process identity and last status; reconcile before any fresh submission; Run Book/Data Loader governance |
| Fusion succeeded but Run Book sync failed | Record outcomes separately; keep recoverable In Progress state without erasing successful import; approved prompt and Run Book governance |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input validation | Invalid field, value, length, key or date | Request corrected business facts and generate new preview |
| catalog mismatch | Task/package identity or metadata mismatch | Stop; reconcile exact effective catalog/template |
| auth/authz | Missing identity/privileges or expired session | Use authorized authentication workflow; no credentials in diagnostics |
| transport/environment | Environment inaccessible | Preserve attempt and resume safe read/status check |
| Fusion API | Application validation or service error | Capture status/log; no automatic write retry |
| process timeout | Original request nonterminal at deadline | Report process/status/elapsed and next status-check path |
| process failed | Terminal failed import | Persist available ProcessLog and partial successes/errors |
| artifact persistence | Required immutable artifact missing/unreadable | Stop before submission and repair artifact path |
| approval blocker | Preview-specific approval missing or invalidated | Return immutable preview for the separate Data Loader approve gate |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Static readiness | Exact task, reached node/source, missing contracts; static compilation is not import proof |
| Preview handoff | Target environment, operation, exact keys and changes, immutable artifact/fingerprint, relevant warnings; Run Book/Data Loader owns package preview and approval |
| Completion | Import/process result, persisted-state verification and Run Book disposition separately; process success alone is insufficient |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Static-generation approval | No live save/import/delete, commit, push, merge or publication |
| Incomplete readiness | No readiness override inferred; no adapter generation before successful rule-plan gate |
| Uncertain load | No automatic resubmission; recheck original attempt and obtain required new preview/approval |
| Sensitive evidence | No credentials, access tokens, Authorization headers or raw environment export rows in reusable task files |
| Delete/rollback | No CSV delete/cascade/recovery inferred from service CanDelete, status or end date |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MPC_CREATE_GATE | step | 60 | execution_gate | ready->MPC_RETURN_CREATE;blocked->MPC_HANDLE_ISSUES | MPC_DESIGN | stop | Create; validation handoff only, no mutation |
| MPC_UPDATE_GATE | step | 70 | execution_gate | ready->MPC_RETURN_UPDATE;blocked->MPC_HANDLE_ISSUES | MPC_DESIGN | stop | Update; validation handoff only, no mutation |
| MPC_HANDLE_ISSUES | step | 80 | error_handler | disclosed->RETURN_ISSUES | none | stop | Any missing/invalid/unavailable contract or failed check |
| MPC_RETURN_CREATE | terminal | 90 | terminal | none | MPC_CREATE_GATE | stop | Create validation complete; return facts to workflow owner |
| MPC_RETURN_UPDATE | terminal | 100 | terminal | none | MPC_UPDATE_GATE | stop | Update validation complete; return facts to workflow owner |
| RETURN_ISSUES | terminal | 110 | terminal | none | none | stop | Return blockers and safe resume context |
