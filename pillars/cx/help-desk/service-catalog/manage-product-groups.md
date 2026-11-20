---
task_code: "QSC_MANAGE_PRODUCT_GROUPS"
task_name: "Manage Product Groups"
parent_skill_id: "cx.help-desk.service-catalog"
pillar: "CX"
offering: "Help Desk"
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

## Purpose

Review Help Desk Product Groups while preserving the catalog's unsupported CSV export/import status.

## Use Cases

### Review Help Desk Product Groups Source Status

Confirm the Help Desk Product Groups task is present while preserving the unsupported setup-data route.

1. Review the effective setup-task metadata and generated Help Desk task artifact.
2. Confirm that export/import and CSV export/import are not supported for QSC_MANAGE_PRODUCT_GROUPS.
3. Stop with a source-guidance blocker before any configuration package, Data Loader route, REST write route, or CX Service substitution is proposed.

### Request Help Desk Product Groups Source Guidance

Collect the missing Oracle source guidance required before Help Desk Product Groups can be configured.

1. Ask for Help Desk-specific Oracle guidance that defines supported objects, fields, validation, and execution contract.
2. Record that no catalog-supported CSV import/export route exists for this task.
3. Do not infer a contract from Manage Product Group Usage or any CX Service task.

## Guard Rails

1. Require an authenticated Fusion user context before any Fusion operation; use `core.auth.fusion-oauth-authentication`.
2. Do not use `core.fusion-api.rest-api-client` to create, update, or delete records.
3. Do not use `shared.setup-import.task-level-import` to create, update, or delete records.

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `N`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

Do not route CSV export work to `shared.setup-export.task-level-export` or CSV import work to `core.data-loader` unless live Fusion metadata or Oracle guidance confirms support. Use `shared.validation.setup-data-validator` only when a setup data artifact is available for review.



## Usage

Use this metadata file when planning, sequencing, exporting, importing, or validating setup data for `Manage Product Groups` under `Service Catalog`.
