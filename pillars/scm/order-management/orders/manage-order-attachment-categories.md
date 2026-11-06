---
task_code: "DOO_MANAGE_ORCHESTRATION_ATTACHMENT_CATEGORIES"
task_name: "Manage Order Attachment Categories"
parent_skill_id: "scm.order-management.orders"
pillar: "SCM"
offering: "Order Management"
functional_area: "Orders"
functional_area_code: "ORA_DOO_ORDER_FULLFILLMENT"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
---

# Manage Order Attachment Categories

## Setup Task Metadata

- Task name: `Manage Order Attachment Categories`
- Task code: `DOO_MANAGE_ORCHESTRATION_ATTACHMENT_CATEGORIES`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## Attachment Categories Core Route

Route requests for this attachment-category task to
`core.fusion-api.apps-common`. The core skill must select its
`core.fusion-api.apps-common.attachments` route for attachment-category setup
data and follow that skill's preflight, export, and approved FSM CSV import
workflow.

Provide this functional context with the core-skill request:

- Module key: `DOO`
- Entities: `DOO_FULFILL_LINES_ALL`, `DOO_HEADERS_ALL`,
  `DOO_PROCESS_DEFINITIONS_VL`
- Setup task code: `DOO_MANAGE_ORCHESTRATION_ATTACHMENT_CATEGORIES`
- Offering: `Order Management`
- Functional area: `Orders`

Do not select a direct REST endpoint or database operation from this task
metadata. The routed core skill owns feature selection and any declared
external-operation workflow.

## Entity Display Names

Use this mapping when preparing or validating attachment-category entity
associations:

| Entity Name | Display Name |
|---|---|
| `DOO_FULFILL_LINES_ALL` | Fulfillment Line |
| `DOO_HEADERS_ALL` | Orchestration Order Header |
| `DOO_PROCESS_DEFINITIONS_VL` | Orchestration Process Definition |

## Attachment Category Input Defaults

When creating a new attachment category, require both of these values before
packaging or submission:

- `CategoryName` (Category Name)
- `UserName` (Category User Name)

Include `UserName` in the `FND_APP_ATTACHMENT_CATEGORY.csv` row. Do not
default either required value to blank; stop validation and request the missing
input instead.

For a new category and every entity association, use ModuleId
`47110F64AC7E08E2E040449823C60DB6` for the selected `DOO` module. Populate
this value in both `FND_APP_ATTACHMENT_CATEGORY.csv` and
`ORA_FND_APP_ATTACHMENT_CATEGORY.csv`. Do not leave `ModuleId` blank.

For `DOO_MANAGE_ORCHESTRATION_ATTACHMENT_CATEGORIES`, default an omitted
`ApplicationId` to `1` when preparing a new attachment-category FSM CSV
package for module key `DOO`. Before packaging or submission, confirm this
default against a fresh, complete setup-data baseline for the same task. If
the baseline does not contain `ApplicationId` `1`, stop with
`catalog_mismatch` and require an explicit replacement value.

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task. Route attachment-category
setup data work through `core.fusion-api.apps-common`, which selects the
attachments workflow and uses the relevant shared skills:

1. Export task setup data with `shared.setup-export.task-level-export`.
2. Validate exported or prepared task setup data with `shared.validation.setup-data-validator`.
3. Import setup task data with `core.data-loader`.

## Removal Boundary

Removal of an attachment category or an entity association is manual-only.
Do not represent a removal by omitting a row from an FSM CSV package, and do
not submit a deletion through this CSV import workflow. Before a manual
removal, verify the current category and associations, obtain explicit
destructive-action approval, and record the target, approval, and outcome in
the project audit evidence.

Use this task metadata when invoking those skills:

- Offering: `Order Management`
- Functional area / Setup Object: `Orders`
- Setup task name: `Manage Order Attachment Categories`
- Setup task code: `DOO_MANAGE_ORCHESTRATION_ATTACHMENT_CATEGORIES`




## Usage

Use this metadata file when planning, sequencing, exporting, importing, or validating setup data for `Manage Order Attachment Categories` under `Orders`.
