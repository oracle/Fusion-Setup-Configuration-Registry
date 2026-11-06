# Input Validation

## Required Inputs

| Input group | Required values | Validation rule | Failure handling | Applies when | Notes |
|---|---|---|---|---|---|
| FSM action | `operation` | Must be `export_template`, `export_baseline`, `validate_package`, or `import_package` | Stop and request one supported operation | Always | |
| Task identity | `task_code`, `task_name` | Must match `POR_CONFIGURE_REQUISITIONING_BUSINESS_FUNCTION` and `Configure Requisitioning Business Function` | Stop before package preparation or import | Always | |
| Environment context | `fusion_environment_context` | Must identify the target Fusion environment and contain the privileges needed for the requested FSM export or import action | Stop before execution | Export or import | |
| Import package | `setup_data_zip` | Must be a prepared FSM setup-data ZIP created from the exported package structure | Stop before upload | Import | |
| Organization source | `OrganizationCode` | Must be supplied explicitly by the user or source data; do not infer it from deliver-to, procurement, or business-unit display values | Stop before CSV packaging or upload | Import | |

## Dependency-Aware Validation

| Dependency | Validation | Timing | Notes |
|---|---|---|---|
| Exported template or baseline package | The source package must preserve the task-level file names, task identity, CSV headers, and package layout from FSM export | Before CSV preparation | |
| Setup data validator | Prepared CSV data must pass `shared.validation.setup-data-validator` | Before approval preview | |
| Reference data validator | Referenced setup values must pass `shared.validation.reference-data-validator` | Before approval preview | |
| Data Loader approval preview | The immutable validated archive must be routed to `core.data-loader` as an FSM task-routed import and produce an approval preview tied to the same ZIP SHA-256 | Before import | |
| User approval | Approval must include target environment, package path, ZIP SHA-256, validation results, Data Loader approval preview, and intended operation | Before import | |

## Field Validation

| Field or rule | Validation | Timing | Notes |
|---|---|---|---|
| CSV headers | Headers must match the exported FSM template for this task | Before packaging | |
| OrganizationCode | Must be user-supplied or source-supplied as a CSV-ready code | Before packaging | Do not copy from deliver-to, procurement, or display-name values |
| ReqimportGroupByCode | Must be nonblank after defaulting | Before packaging | Default: `ITEM` |
| ReapprovalRequiredFlag | Must be nonblank after defaulting | Before packaging | Default: `N` |
| CreateOrdersFlag | Must be nonblank after defaulting | Before packaging | Default: `Y` |
| CancelBackingReqCode | Must be nonblank after defaulting | Before packaging | Default: `OPTIONALLY` |
| MultipleLegalEntities | Must be nonblank after defaulting | Before packaging | Default: `ERROR` |
| Optional CSV values | `LineType` and `ShipToLocation` are omitted unless CSV-ready values are directly supplied | Before packaging | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| POR.VALIDATE_FSM_PACKAGE | step | 1 | validate_input | export->POR.READY_FOR_FSM_EXPORT;import->POR.APPLY_FSM_DEFAULTS;invalid->POR.BLOCKED | none | stop | All task operations |
