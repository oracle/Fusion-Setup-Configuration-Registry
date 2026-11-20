# Defaulting Rules

## Standard Defaults

| Task Code | Task Name | Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_SEARCH_OPTIONS | Manage Global Search Profile Options | FUSION_APPS_SEARCH_ENABLED | Y | Explicit enable intent with no supplied requested value; Yes is the UI display label for stored Y; disable requires supplied N | No |  |
| ORA_SVC_MANAGE_TAGS | Manage Tags | AdministratorCreatedFlag business intent | true only for an explicitly requested new administrator tag; otherwise false for generic create when omitted | Create only and no supplied flag; never apply to updates or rewrite an explicit true/false value. FSM Y/N is a separate export-confirmed encoding, not a boolean default | No |  |

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_SEARCH_OPTIONS | Manage Global Search Profile Options | GSEARCH.DEFAULT | step | 30 | apply_default | applied->GSEARCH.DESIGN;issues->RETURN_ISSUES | GSEARCH.LOOKUP | stop | Every Global Search request; apply the conditional enable default or preserve the supplied Y or N unchanged |
| ORA_SVC_MANAGE_TAGS | Manage Tags | TAG.CREATE_DEFAULTS | step | 15 | apply_default | applied->TAG.CREATE_PREFLIGHT;issues->RETURN_ISSUES | TAG.VALIDATE | stop | Apply only a missing AdministratorCreatedFlag business-intent default from Standard Defaults; retain explicit true/false. If a supplied FSM flag needs normalization, require the selected export/XML to confirm its representation; unresolved encoding returns issues. Do not serialize an FSM row here. |
