# Design Enforcement

## Enforcement Order

| Task Code | Task Name | Sequence | Step | What Must Happen |
|---|---|---|---|---|
| ORA_SVC_MANAGE_SEARCH_OPTIONS | Manage Global Search Profile Options | 1 | Separate configured current and intended target values | Validate the configured Site identity, Site flags and requested stored Y or N before preview; verify the changed value only after the owning workflow reports success |
| ORA_SVC_MANAGE_SEARCH_OPTIONS | Manage Global Search Profile Options | 2 | Refresh user session | Users must sign out and sign back in before checking Global Search visibility |

## Design Rules

| Task Code | Task Name | Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_SEARCH_OPTIONS | Manage Global Search Profile Options | A Global Search change is being prepared for preview | Error | resolve_global_search_profile_value | Requested target is not Y for enable or N for disable, the configured Site identity is unresolved, or the verified Site definition does not permit the selected change | Validate the intended stored value and Site flags before preview; current N with requested Y is a valid enable change, not a blocker | No |
| ORA_SVC_MANAGE_SEARCH_OPTIONS | Manage Global Search Profile Options | Global Search visibility is being validated after a profile update | Error |  | The user session has not been refreshed | Sign out and sign back in before checking whether Global Search is visible | Yes |

## Design Lookup Requirements

| Task Code | Task Name | Resolver | When Required | Values Needed | Source File |
|---|---|---|---|---|---|
| ORA_SVC_MANAGE_SEARCH_OPTIONS | Manage Global Search Profile Options | resolve_global_search_profile_value | Before preparing a Global Search change | Current configured Site value and identity; verified Site-enabled/updatable definition; requested target remains separate | ora_reference_lookups.md |

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_SEARCH_OPTIONS | Manage Global Search Profile Options | GSEARCH.DESIGN | step | 40 | design_enforcement | passed->GSEARCH.DONE;issues->RETURN_ISSUES | GSEARCH.DEFAULT | stop | Global Search is being enabled or validated |
