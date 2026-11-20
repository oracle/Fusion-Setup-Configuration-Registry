# Help Desk Category Defaults

## Standard Defaults

| Task Code | Task Name | Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Category list filter | StripeCd = 'ORA_SVC_HCM' and EnabledFlag = true and ParentCategoryId is null | Default category-list view | Yes; remove only the relevant active or root restriction for an explicit inactive or child-category lookup |  |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Child business unit | Business unit inherited from the selected root category | Create child category | No | resolve_help_desk_parent_category |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Existing category values | Retain exported keys, relationships, and unchanged values | FSM update, activation, or deactivation | No |  |

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | HRHDCAT.DEFAULTS | step | 20 | apply_default | passed->HRHDCAT.LOOKUPS;issues->HRHDCAT.ERROR | HRHDCAT.INPUT | stop | Apply only operation-appropriate defaults; a list-only filter never scopes a mutation or verification. |
