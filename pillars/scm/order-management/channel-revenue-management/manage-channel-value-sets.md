---
task_code: "ORA_CJM_MANAGE_CHANNEL_VALUE_SETS"
task_name: "Manage Channel Value Sets"
parent_skill_id: "scm.order-management.channel-revenue-management"
pillar: "SCM"
offering: "Order Management"
functional_area: "Channel Revenue Management"
functional_area_code: "ORA_FOM_CHANNEL_REV_MGMT"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
---

# Manage Channel Value Sets

## Setup Task Metadata

- Task name: `Manage Channel Value Sets`
- Task code: `ORA_CJM_MANAGE_CHANNEL_VALUE_SETS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## Value Set Routing

Route requests for `Manage Channel Value Sets` first to
`core.fusion-api.apps-common`, which selects
`core.fusion-api.apps-common.value-sets`.

The selected Apps Common workflow owns the supported direct REST behavior:

1. Read a value-set definition and its validation-table metadata.
2. Read, create, update, or delete supported child value-set values, subject
   to its preflight and immediate approval gate for writes.
3. Do not treat a root value-set definition as writable through this route.

## Supported Create and Update Operations

Use the task-level FSM route for root value-set definitions and for a package
that changes a value set together with its values. The current Apps Common REST
route remains limited to reads and child-value operations.

| Target | Create | Update | Required route |
| --- | --- | --- | --- |
| Root value-set definition | Supported | Supported for template-supported mutable fields | Validated task-level FSM package through `core.data-loader` |
| Value-set values | Supported | Supported | Task-level FSM package, or Apps Common REST for a child-value-only request |

Use the rows scoped to `ORA_CJM_MANAGE_CHANNEL_VALUE_SETS` in the shared
`ora-resource/` files as the rule source. Read input validation, dependency
readiness, reference lookups, defaulting, and error handling, then consume the
compiled task graph using the resource-authoring execution guide. These
resources own create/update requirements, carrier prerequisites, serialization
and identity resolvers, preservation defaults, and failure diagnostics.

`dataloader_import_mode: FSM` is the catalog-derived route for root-definition
create or update and for combined parent-and-value changes. It requires the
normal immutable-archive validation and approval workflow. It must not be used
as an unverified fallback for a direct REST child-value request.

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export task setup data with `shared.setup-export.task-level-export`.
2. Validate exported or prepared task setup data with `shared.validation.setup-data-validator`.
3. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Order Management`
- Functional area / Setup Object: `Channel Revenue Management`
- Setup task name: `Manage Channel Value Sets`
- Setup task code: `ORA_CJM_MANAGE_CHANNEL_VALUE_SETS`




## Usage

Use this metadata file when planning, sequencing, exporting, importing, or validating setup data for `Manage Channel Value Sets` under `Channel Revenue Management`.
