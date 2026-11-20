# Transmission error handling



Task: IBY_MANAGE_TRANSMISSION_CONFIGURATIONS — Manage Transmission Configurations.

## Error Situations

| Situation | What Should Happen |
|---|---|
| FND_CMN_RCRD_VAL | Report duplicate configuration-name conflict; re-resolve exact target; do not retry as create |
| FND_CMN_FRM_ERLY_EQ_TO_DATE | Report invalid effective-date order; retain failed request for correction |
| FND_CMN_REQ_ATTRIB_API_SERV | Identify the affected field without values; inspect the failing stage because the message can arise from UI requiredness or private-key registration password validation |
| FND_CMN_FLE_ERR or IBY_INVALID_WALLET during key registration | Retain redacted error evidence; inspect UCM and credential-store state before any retry. Configuration rollback alone does not prove external state was restored |
| Missing or ambiguous target reference | Stop affected design; request exact target evidence |
| FSM process failed or outcome uncertain | Preserve redacted process/log evidence; acquire fresh export before any new decision |
| New field or source mismatch | Stop; refresh metadata and re-author rules rather than accepting arbitrary columns |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Design review | Exact task, operation, configuration identities, changed field names, redacted parameter values and unresolved prerequisites |
| Import approval | Immutable sanitized package fingerprint and intended target through active Data Loader contract; disclose create-only username placeholders and pending manual credential/key setup |
| Completion | Actual process result and fresh-export reconciliation; static success alone is insufficient |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Uncertain or failed import | Automatic retry, alternate endpoint, rollback import or transmission test |
| Requested secret disclosure | Print unsealed export data or embed it in tracked evidence |
| Missing source-backed rule | Guess requiredness, credential mappings or protocol defaults |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTC.GATE | step | 60 | execution_gate | success->RETURN_SUCCESS;failure->MTC.ERROR | MTC.DESIGN | stop | Always; returns validation only |
| RETURN_SUCCESS | terminal | 70 | terminal | none | MTC.GATE | stop | Validation completed; no mutation authorized |
| MTC.ERROR | step | 80 | error_handler | handled->MTC.STOP | none | stop | Any declared failure |
| MTC.STOP | terminal | 90 | terminal | none | none | stop | Failure handled |

## Evidence

- Entity validation messages (reviewed implementation evidence).
- UI missing-value error (reviewed implementation evidence).
- Current core.runbook and core.data-loader governance contracts; no direct write is authorized by this graph.

- Configuration DML and credential registration (reviewed implementation evidence) — existing-key check, UCM fetch, password/file checks and conditional deletion.
- Credential utility (reviewed implementation evidence) — type/name existence, materialization and legacy-path side effects.

## Sensitive setup boundary

Apply [the sensitive-field policy](ora_sensitive_fields.md) before these checks. Credential import and intentional key registration are manual; only the explicit SFTP create username placeholder is permitted.
