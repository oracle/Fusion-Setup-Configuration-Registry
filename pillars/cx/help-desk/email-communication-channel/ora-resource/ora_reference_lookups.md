# Reference Lookups

## Live Lookups

| Task Code | Task Name | Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS | Manage Email Templates for HR Help Desk | resolve_hrhd_email_template_profile_value | A configured allow-listed HR email-template profile value must be read | Exact allow-listed ProfileOptionName; explicit Site, Product or User level; SITE, application short name or UserName key for that level | GET /fscmRestApi/resources/11.13.18.05/profileOptions/{ProfileOptionName}; then GET its child/siteProfileOptionValues/SITE, child/productProfileOptionValues/{LevelValue} or child/userProfileOptionValues/{UserName} through core.fusion-api.apps-common for the selected level | ProfileOptionName and selected configured child ProfileOptionValue with its documented level key | Require the exact allow-listed definition and exactly one value at the explicitly selected level/key. Retain raw value and returned identity. Session-effective profileValues is separate comparison evidence and never proves configured scope. | Verified allow-listed profile code, explicit level/key and current configured raw value | Stop on missing/ambiguous definition or value, unsupported level, missing scope key, non-allow-listed code or failed read. Never select the first match or infer Site scope. |

## Lookup Execution Rules

| Task Code | Task Name | Situation | What Happens |
|---|---|---|---|
| ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS | Manage Email Templates for HR Help Desk | An HR Help Desk email-template profile-value lookup is requested | Use only the declared definition and level-specific configured GETs through the approved core profile-options route. Preserve explicit scope, keys and raw values; do not write during lookup or treat session-effective values as configured-level verification. |

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS | Manage Email Templates for HR Help Desk | HRHDEMAILTEMPLATE.LOOKUP | step | 20 | reference_lookup | read_found->HRHDEMAILTEMPLATE.READ_READY;issues->RETURN_ISSUES | HRHDEMAILTEMPLATE.VALIDATE | stop | The allow-listed HR Help Desk email-template profile value must be resolved |

Configured-read contract source: the repository-retained Profiles CRUD service guidance in core/fusion-api/apps-common/profile-options/references/profile-options.md. The public profileValues API describes session-effective reads only. This task selects GETs only; its existing FSM workflow owns any later approved mutation.
