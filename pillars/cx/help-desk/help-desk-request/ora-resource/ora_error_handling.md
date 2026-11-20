# Help Desk Category Error Handling

## Error Situations

| Task Code | Task Name | Situation | What Should Happen |
|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Missing required input, duplicate code, or ambiguous category | Report the missing or conflicting value and stop before mutation. |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Failed or incomplete read lookup | Retain sanitized diagnostic evidence and stop; do not report no matches. |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Failed, uncertain, or timed-out import | Retain request or process identifiers and diagnostics, report the last status and next-check path, and do not automatically reimport. |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Delete request | Return the documented unsupported result and offer deactivation when appropriate. |

## Disclosure Rules

| Task Code | Task Name | Gate | What Must Be Shown |
|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Validation or import failure | Exact task, failing stage, sanitized diagnostics, and the next safe action. |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Approval | Exact target and immutable package before Data Loader import. |

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | HRHDCAT.VALIDATED | terminal | 80 | terminal | none | HRHDCAT.POLICY | stop | Return validated facts to the routed workflow; no Fusion mutation has been performed by this rule graph. |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | HRHDCAT.ERROR | terminal | 90 | terminal | none | none | stop | Return a safe error or unsupported outcome without retrying or performing an external action. |
