# Design Enforcement

## FSM Execution Order

| Sequence | Activity | Enforcement |
|---:|---|---|
| 1 | Export task template or baseline package | Use `shared.setup-export.task-level-export` and retain the returned `ProcessId`, terminal status, ZIP, and process log artifacts |
| 2 | Prepare CSV package | Preserve the exported package structure, task identity, file names, and CSV headers |
| 3 | Validate setup and reference data | Run `shared.validation.setup-data-validator` and `shared.validation.reference-data-validator` before approval |
| 4 | Preview and approve | Show target environment, package path, validation results, and final CSV values before import |
| 5 | Build immutable Data Loader approval preview | Route only the immutable validated archive to `core.data-loader` as an FSM task-routed import with target environment, task context, SHA-256, and validation evidence |
| 6 | Import approved package | Data Loader owns upload, initiation, monitoring, and diagnostics; track the returned identifier to terminal status |

## Design Rules

| Scenario | Severity | Field | Condition | Required handling | Blocking |
|---|---|---|---|---|---|
| Any operation | Error | Task identity | Task code or task name does not match this setup task | Stop and correct the task routing | Yes |
| Export | Error | Export evidence | Export has no returned `ProcessId`, terminal status, ZIP, or process log artifact | Stop with a tracking-failure result | Yes |
| Import | Error | Package structure | ZIP was not prepared from the exported FSM package structure | Stop before upload | Yes |
| Import | Error | Validation results | Setup data or reference data validation has not passed | Stop before approval | Yes |
| Import | Error | Approval | User approval does not reference the exact package, SHA-256, target environment, validation results, Data Loader approval preview, and intended operation | Stop before upload | Yes |
| Import | Error | OrganizationCode | Value is missing or inferred from another field | Stop before packaging | Yes |
| Import | Error | Import evidence | Import initiation has no returned request or process identifier | Stop with a tracking-failure result | Yes |
| Import | Error | Execution owner | Upload, initiation, monitoring, or diagnostics are attempted outside `core.data-loader` | Stop and reroute to the Data Loader-owned FSM import workflow | Yes |
| Any operation | Error | Execution route | A mechanism other than FSM task-level setup-data export or import is selected | Stop and reroute to the supported FSM task-level setup-data workflow | Yes |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| POR.ENFORCE_FSM_IMPORT_RULES | step | 3 | design_enforcement | pass->POR.READY_FOR_APPROVED_FSM_IMPORT;fail->POR.BLOCKED | POR.APPLY_FSM_DEFAULTS | stop | All task operations |
