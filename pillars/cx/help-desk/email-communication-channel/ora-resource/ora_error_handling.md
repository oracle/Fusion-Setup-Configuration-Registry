# Error Handling

## Error Situations

| Task Code | Task Name | Situation | What Should Happen |
|---|---|---|---|
| ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS | Manage Email Templates for HR Help Desk | The requested profile option is outside the HR Help Desk email-template allow-list, the target profile level is absent, or the profile-value lookup has no exact match or multiple matches | Stop, disclose the missing or ambiguous input, and do not infer a profile level or value |
| ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS | Manage Email Templates for HR Help Desk | An update is requested through the REST lookup | Stop. The selected configured-profile lookup contract is read-only. For an FSM update, follow the task Use Cases and core.data-loader gates; the read registry does not authorize mutation. |

## Refusal Rules

| Task Code | Task Name | Situation | What Must Not Happen |
|---|---|---|---|
| ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS | Manage Email Templates for HR Help Desk | A request names another profile option or the profile value is not uniquely resolved | Do not read or update another profile option and do not select an ambiguous record |
| ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS | Manage Email Templates for HR Help Desk | An update is requested | Do not update a profile value through the configured-profile lookup. |

## Common Outbound Refusal

Common Outbound imports are unsupported until a separately reviewed task-owned
profile/level contract and supported execution workflow exist. Preserve the
selected context and diagnostics with catalog_or_metadata_mismatch. Record
blocked ruleResults; no passed, not_applicable or overridden import result is
permitted by this plan. A registry readiness waiver cannot enable an unsupported
operation. Do not preview, approve, upload, retry or substitute HR template rules,
REST or a browser. The selected shared export/package-inspection workflow is
separate and remains available.

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS | Manage Email Templates for HR Help Desk | HRHDEMAILTEMPLATE.READ_READY | terminal | 30 | terminal | none | HRHDEMAILTEMPLATE.LOOKUP | stop | The requested allow-listed profile value was read successfully |
| ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS | Manage Email Templates for HR Help Desk | RETURN_ISSUES | terminal | 99 | terminal | none | none | stop | Any HR Help Desk email-template profile-value gate produces issues |
| ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS | Manage Email Templates for HR Help Desk | HRHDEMAILTEMPLATE.UPDATE_HANDOFF_GATE | decision | 35 | execution_gate | ready->HRHDEMAILTEMPLATE.UPDATE_READY;blocked->RETURN_ISSUES | HRHDEMAILTEMPLATE.UPDATE_PREFLIGHT | stop | Require matching active Run Book/core.data-loader preflight for this task, FSM update operation, Help Desk context and immutable source. Return evidence only; missing or changed binding/source blocks. Request no duplicate load approval |
| ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS | Manage Email Templates for HR Help Desk | HRHDEMAILTEMPLATE.UPDATE_READY | terminal | 36 | terminal | none | HRHDEMAILTEMPLATE.UPDATE_HANDOFF_GATE | stop | Return validated update intent and evidence to the owning Data Loader workflow, which owns package mapping, exact preview, approval, execution and verification. No configured-profile REST write, direct import or automatic retry is permitted |
| ORA_SVC_MANAGE_COMMON_OUTBOUND_EMAIL_PROFILE_OPTIONS | Manage Common Outbound Email Profile Options | COMMONOUTBOUNDEMAIL.BLOCKED | terminal | 20 | terminal | none | COMMONOUTBOUNDEMAIL.REFUSE_IMPORT | stop | Return blocked import status, original task context and sanitized missing-contract evidence. Always record this refusal in ordered blocked ruleResults; it grants no import preview or write and defines no successful or overridden mutation outcome. |
