# Help Desk Category Reference Lookups

Oracle documents the Categories collection as a read endpoint at `/crmRestApi/resources/11.13.18.05/categories`. These lookup definitions are read-only guidance; the active project workflow selects and authorizes any Fusion request.

## Live Lookups

| Task Code | Task Name | Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | find_help_desk_categories | List, search, duplicate check, or verification | Requested search values and applicable Help Desk scope | /crmRestApi/resources/11.13.18.05/categories | Category identity, name, code, description, active state, business unit, stripe, and parent relationship | Apply the default list filter only for the default view. For an explicit inactive or child lookup, remove only the relevant restriction. | Matching category records | An empty list is valid for a list or duplicate check. Multiple records are valid for a list but block a single-record change. |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | resolve_help_desk_parent_category | Create child category or view children | Selected parent category identity | /crmRestApi/resources/11.13.18.05/categories | Parent category identity and root business unit | Resolve exactly one selected top-level category before using it as the parent. | Parent identity and inherited business unit | Stop if the parent is absent or ambiguous. |

## Lookup Execution Rules

| Task Code | Task Name | Situation | What Happens |
|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Category selection | A category selected for change, deactivation, or child creation must resolve unambiguously; do not select the first returned row. |
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | Default filter | The Help Desk root-category default is list-only. Do not use its active or root restriction to conclude that an inactive or child category does not exist. |

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS | Manage Categories for HR Help Desk Requests | HRHDCAT.LOOKUPS | step | 30 | reference_lookup | passed->HRHDCAT.DEPENDENCIES;issues->HRHDCAT.ERROR | HRHDCAT.DEFAULTS | stop | Perform only the read lookup required by the selected operation. |
