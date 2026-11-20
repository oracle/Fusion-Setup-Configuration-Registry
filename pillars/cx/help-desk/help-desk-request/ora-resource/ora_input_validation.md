# Help Desk Category Input Validation

## Required Groups

| Task Code | Task Name | Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Requested operation | List, search, view children, create top-level category, create child category, update, activate, deactivate, export, or import verification | Stop before any Fusion operation | Ask for the intended operation | Every request |  |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Top-level category | Category Name, unique Category Code, Business Unit, and active choice | Stop before package preparation | Collect the missing values | Create top-level category |  |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Child category | Resolved parent, Category Name, unique Category Code, and active choice | Stop before package preparation | Collect the missing values and resolve the parent | Create child category | resolve_help_desk_parent_category |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Existing category | Exact category identity and requested change | Stop on an ambiguous target | Resolve exactly one category in the requested scope | Update, activation, deactivation, or verification | find_help_desk_categories |

## Field Validation

| Task Code | Task Name | Check | What Happens | Applies When | Resolver |
|---|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Category code uniqueness | Do not proceed when the requested Category Code already exists; Oracle documents that it must be unique across business units and application stripes. | Create top-level or child category | find_help_desk_categories |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Parent identity | Require one selected top-level category before creating a child. | Create child category | resolve_help_desk_parent_category |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Approved update scope | Change only the approved name, description, or active state while retaining exported identity and parent linkage. | Update, activate, or deactivate |  |

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | HRHDCAT.INPUT | step | 10 | validate_input | passed->HRHDCAT.DEFAULTS;issues->HRHDCAT.ERROR | none | stop | Validate the requested category operation and its applicable inputs. |
