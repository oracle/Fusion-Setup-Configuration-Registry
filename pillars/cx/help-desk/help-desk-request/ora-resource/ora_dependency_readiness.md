# Help Desk Category Dependencies

## Required Dependency Order

| Task Code | Task Name | Sequence | Dependency | What Must Happen |
|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | 1 | Category identity | Resolve the applicable category or parent before a single-record action. |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | 2 | Same-task FSM evidence | Export the same setup task and confirm package structure before a category mutation. |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | 3 | Validation and approval | Validate the package and use the Data Loader preview and approval workflow before import. |

## Dependency Rules

| Task Code | Task Name | Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | HRHDCAT.PARENT | Parent category | Conditional | Create child category or view children | Verify | Categories collection | resolve_help_desk_parent_category | Oracle assigns a child category the business unit of its root category. | Select one parent category before proceeding. | Parent identity and root business unit |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | HRHDCAT.FSM | Same-task FSM package | Yes | Create, update, activate, or deactivate | Satisfied | Same-task export metadata |  | Package structure, headers, object names, node order, and relationships must come from the selected setup task. | Export first; do not substitute a reduced CSV or REST JSON payload. | Export provenance and validated package |

## Dependency Classification

| Task Code | Task Name | Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Verify | Parent identity is needed | Yes, read-only lookup only |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Blocked | Same-task FSM evidence is missing or invalid | No |

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | HRHDCAT.DEPENDENCIES | step | 40 | resolve_dependency | passed->HRHDCAT.POLICY;issues->HRHDCAT.ERROR | HRHDCAT.LOOKUPS | stop | Confirm dependencies applicable to the selected operation. |
