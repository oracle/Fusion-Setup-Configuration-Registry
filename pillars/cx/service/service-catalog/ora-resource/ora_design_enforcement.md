# Manage Product Groups Design Enforcement

## Enforcement Order

| Task Code | Task Name | Sequence | Step | What Must Happen |
|---|---|---|---|---|
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | 1 | Confirm FSM import support | Obtain an Oracle source that explicitly defines FSM import support, artifact shape, target, and mapping for product groups before an FSM import preview |

## Design Rules

| Task Code | Task Name | Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|---|---|
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | FSM import is requested | Error |  | The effective setup-task catalog marks export/import unsupported and the supplied API documentation does not define an FSM artifact or import contract | Stop with the import-support blocker. The named REST create has a separate Product Groups-specific command lifecycle and is not an import fallback. Update this rule only when an authoritative FSM contract and catalog support are available. | No |

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | MPG.GATE_FSM_IMPORT | decision | 3 | design_enforcement | fsm_contract_missing->MPG.FSM_IMPORT_BLOCKED | MPG.VALIDATE_REQUEST | stop | FSM import is requested |
