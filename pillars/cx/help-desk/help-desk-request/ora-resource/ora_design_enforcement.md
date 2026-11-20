# Help Desk Category Design Enforcement

## Enforcement Order

| Task Code | Task Name | Sequence | Step | What Must Happen |
|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | 1 | Resolve identity | Confirm the selected category or parent unambiguously. |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | 2 | Preserve FSM integrity | Use complete same-task export evidence and validate the resulting package. |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | 3 | Approve import | Present the exact package through the Data Loader preview and approval workflow. |

## Design Rules

| Task Code | Task Name | Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Create top-level or child category | Error | find_help_desk_categories | The requested Category Code is not unique across business units and application stripes. | Select an approved unique code; do not synthesize a suffix. | Yes, provide a different approved code. |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Create child category | Error | resolve_help_desk_parent_category | Parent identity or root business-unit inheritance is unresolved. | Resolve the parent and retain its root business unit. | No guessed relationship. |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | FSM mutation | Error |  | Package is missing required same-task metadata, members, headers, relationships, or validation evidence. | Preserve complete package integrity and submit only through the approved Data Loader workflow. | No reduced CSV or REST-payload substitute. |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Delete category | Error |  | Deletion is not supported by the rerouted category workflow. | Use deactivation when appropriate. | No |

## Design Lookup Requirements

| Task Code | Task Name | Resolver | When Required | Values Needed | Source File |
|---|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | find_help_desk_categories | Create or existing-category selection | Category-code matches and candidate records | ora_reference_lookups.md |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | resolve_help_desk_parent_category | Create child category | Parent identity and root business unit | ora_reference_lookups.md |

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | HRHDCAT.POLICY | step | 50 | design_enforcement | passed->HRHDCAT.VALIDATED;issues->HRHDCAT.ERROR | HRHDCAT.DEPENDENCIES | stop | Enforce category hierarchy and FSM package-integrity rules before handing off to the routed workflow. |
