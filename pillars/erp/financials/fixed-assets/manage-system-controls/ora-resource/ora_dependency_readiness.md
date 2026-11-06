# Manage System Controls: Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---:|---|---|
| 1 | Category, Location, and Asset Key Flexfield Structures | Configure and validate the structures before system controls. |
| 2 | System Controls | Select the validated structures and set the oldest date placed in service. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| FA_SYSTEM_CONTROLS.FLEXFIELDS | Category, Location, and Asset Key Flexfield Structures | Yes | Confirmed create path | Lookup | Approved target configuration or supported read-only metadata | resolve_assets_flexfield_structures | System controls require one usable structure instance of each type for asset transactions. | For each type, provide one exact enabled structure and one matching enabled `StructureInstanceCode`; select the instance explicitly when more than one is enabled. When the structure was newly deployed, require parent-verified target context before System Controls package creation. | Category, Location, and Asset Key selected enabled `StructureInstanceCode` values |
| FA_SYSTEM_CONTROLS.EXPORT_METADATA | Current FSM export | Yes | FSM CSV package preparation | Lookup | Current target-environment export | resolve_system_controls_export_metadata | The export supplies the task-specific package contract and technical defaults. | Export this exact task from the target environment. | CSV files, metadata XML, headers, IDs, codes, defaults |
| FA_SYSTEM_CONTROLS.EXISTING_STATE | Existing system controls | Yes | Before a create decision | Lookup | Exact Enterprise Name BOSS lookup first; current same-target `FA_MANAGE_SYSTEM_CONTROL` FSM export only when BOSS is unavailable, fails, or has no exact row | resolve_existing_system_controls | System controls are single-row system-wide controls. Once set, they are read-only and must not be changed through this skill. | Verify the exact enterprise row through BOSS first. Use a successful FSM export with the expected header and zero data rows only as the fallback create-path evidence. | Existing read-only definition, or confirmed absence |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Ready | All required dependency values are resolved, including confirmed System Controls absence when the selected path is create. | Yes |
| Technical lookup gap | An export, read-only contract, code, or identifier is unresolved. | No |
| Existing System Controls set | An exact existing Enterprise Name row is found. Show it as read-only; no create or update path is available. | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| SYS.RESOLVE_DEPENDENCIES | decision | 38 | resolve_dependency | ready->SYS.PRESENT_REFERENCE_PREVIEW;blocked->SYS.HANDLE_DEPENDENCY | SYS.COLLECT_CREATE_INPUTS | stop | Existing System Controls absence is confirmed and creation inputs are valid |
