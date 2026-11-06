# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Missing client-specific field, terms acceptance, or single source root | Classify as input validation; identify the missing field or row count without disclosing credential values. |
| Existing registration count or key is unknown or ambiguous | Stop before import preview; do not assume create or synthesize an update key. |
| Mail address uniqueness or feature opt-in is unconfirmed | Stop before import preview or credential validation and request target-pod evidence. |
| ORA_SCH_RECALL_INGEST_START_DATE has no Site-level value or has an invalid date | Ask the user to set or correct the Site-level profile value in yyyy-MM-dd format through core.fusion-api.apps-common.profile-options. Do not use an effective session value, product or user-level value, or a guessed fallback date. |
| Capture Recall Notices feature has EnabledFlag N | Route to shared.implementation-planning.fsm-set-optin.fsm-set-optin-features for the exact feature and offering. Its dry-run, approval, PATCH, refresh, and reread must complete before this task continues. Do not patch the feature from this task-rule graph. |
| validateCredentials REST contract is unavailable | Classify as catalog or contract mismatch; stop before a live call and record the missing path, method, or payload contract. |
| Authentication, authorization, transport, or Fusion API failure | Record a redacted failure classification and safe next action; do not retry a write or validation action with uncertain side effects. |
| Source data, target, mapping, or task rules need correction during a pending load | Cancel the live Data Loader session and start a fresh session with corrected inputs. Do not reread edited files into the existing preview, persist captured records or approval objects, or replay a prior approval. |
| Data Loader process handle is lost or the session expires | Start a fresh validation session and obtain its approval; a saved preview or approval cannot resume submission. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | A required source value, one-record shape check, Site-level profile value, or feature opt-in prerequisite fails | Correct the source or prerequisite through its owning skill; for a pending import cancel it and rerun validation in a fresh Data Loader session using its returned captured records/native sources. |
| Catalog mismatch | The requested BO or REST operation does not match this task or has no verified contract | Resolve the correct task-specific contract before execution. |
| Auth/authz | The selected identity lacks access to metadata, state, or validation | Obtain the documented privilege and retry only the read-only preflight. |
| Transport/environment | The selected pod or connection is unavailable or mismatched | Correct the selected environment and discard cross-pod evidence. |
| Fusion API | Fusion rejects an operation or payload | Preserve the redacted response and correct the contract or input before a new attempt. |
| Approval blocker | A mutating REST operation or Data Loader import lacks approval for its exact preview | Obtain the owning workflow's required approval immediately before execution. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Input or design blocker | Task identity, selected environment, failed check, redacted evidence, and one safe next action. |
| Credential validation result | Outcome and sanitized server message only; never show a client secret, refresh token, access token, or full credential payload. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RECALL.REGISTRATION.HANDLE-ISSUE | step | 30 | error_handler | handled->RECALL.REGISTRATION.RETURN-ISSUES | none | stop | Input or design validation is blocked |
| RECALL.REGISTRATION.DONE-IMPORT-PREFLIGHT | terminal | 40 | terminal | none | RECALL.REGISTRATION.ENFORCE-DESIGN | stop | Import checks passed; core.data-loader owns immutable preview, approval, and import |
| RECALL.REGISTRATION.DONE-VALIDATION-PREFLIGHT | terminal | 50 | terminal | none | RECALL.REGISTRATION.ENFORCE-DESIGN | stop | Credential-validation checks passed; only the declared REST operation may be executed |
| RECALL.REGISTRATION.RETURN-ISSUES | terminal | 60 | terminal | none | none | stop | Validation issues have been classified and disclosed |
