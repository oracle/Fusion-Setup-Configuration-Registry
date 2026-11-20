---
task_code: "QSC_MANAGE_PRODUCT_GROUPS"
task_name: "Manage Product Groups"
parent_skill_id: "cx.service.service-catalog"
pillar: "CX"
offering: "Service"
functional_area: "Service Catalog"
functional_area_code: "ORA_SVC_SERVICE_CATALOG"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
---

# Manage Product Groups

## Setup Task Metadata

- Task name: `Manage Product Groups`
- Task code: `QSC_MANAGE_PRODUCT_GROUPS`
- Available: `Y`
- Export/import supported: `N`
- CSV export/import supported: `N`
- CSV export/import routing: `not supported`
- Data Loader import mode: not selected (catalog import unsupported)
- Business Object: ``

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `N`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

Do not route CSV export work to `shared.setup-export.task-level-export` or CSV import work to `core.data-loader` unless live Fusion metadata or Oracle guidance confirms support. Use `shared.validation.setup-data-validator` only when a setup data artifact is available for review.

## Usage

For an explicit product-group create, use the enabled `create-product-group`
[REST contract](ora-resource/ora_rest_documentation.md) through the task-only
[Product Groups command](scripts/product_group_rest.py). This selected workflow
implements its complete preview, approval verification and create lifecycle
locally and delegates HTTP/authentication to core.fusion-api.rest-api-client.
Require the exact Service task context, active environment-bound Run Book and
reviewed read/create privileges before Describe and duplicate checks. Present
the immutable preview for exact immediate approval, submit one POST and verify
the returned ID, names and supplied flags through a fresh GET. Never replay an
attempt or substitute an ad hoc REST call. Core Task Hook does not supply these
REST commands. Catalog N/N flags and unselected import mode remain unchanged;
this named create enables no CSV/FSM import or other mutation.

Use this metadata file when planning, sequencing, exporting, importing, or validating setup data for `Manage Product Groups` under `Service Catalog`.
