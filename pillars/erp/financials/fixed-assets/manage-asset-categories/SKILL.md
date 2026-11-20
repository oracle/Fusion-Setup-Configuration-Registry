---
skill_id: "erp.financials.fixed-assets.manage-asset-categories"
name: "Manage Asset Categories Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Asset Categories under the Fixed Assets functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Fixed Assets"
functional_area_code: "FIN_FIXED_ASSETS_DEPLOYED"
task_code: "FA_MANAGE_ASSET_CATEGORY"
task_name: "Manage Asset Categories"
parent_skill_id: "erp.financials.fixed-assets"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.1.14"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "core.fusion-api.apps-common.descriptive-flexfields"
  - "erp.financials.fixed-assets.manage-fixed-assets-flexfield-value-sets"
  - "erp.financials.fixed-assets.manage-fixed-assets-key-flexfields"
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
uses_core:
  - "core.fusion-api.apps-common.descriptive-flexfields"
  - "core.fusion-api.rest-api-client"
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
persists_project_state: true
token_usage_tracking:
  enabled: true
  granularity: "per_skill_run"
  artifact_type: "token_usage_record"
  default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
  estimation_method: "chars/4 estimate unless exact tokenizer or API accounting is available"
  required_fields:
    - "activity_start_time"
    - "skill_id"
    - "task"
    - "trigger"
    - "artifacts_written"
    - "files_read"
    - "estimated_input_tokens"
    - "estimated_output_tokens"
    - "estimated_total_tokens"
    - "estimation_method"
    - "notes"
state_updates:
  - "setup_task_sequence"
  - "configuration_blueprints"
  - "validation_results"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/fixed-assets/manage-asset-categories/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/fixed-assets/manage-asset-categories/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "Reads current DFF definitions and value-set evidence through declared workflows; imports remain delegated to core.data-loader."
required_privileges:
  - "Read access to the selected DFF metadata export and applicable value-set scopes."
---

# Manage Asset Categories Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Asset Categories` under `Fixed Assets`.

## Setup Task Skill Contract

- task_code: `FA_MANAGE_ASSET_CATEGORY`
- task_name: `Manage Asset Categories`
- parent_skill_id: `erp.financials.fixed-assets`
- pillar: `ERP`
- offering: `Financials`
- functional_area: `Fixed Assets`
- functional_area_code: `FIN_FIXED_ASSETS_DEPLOYED`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Asset Categories` under `Fixed Assets`.

## Setup Task Metadata

- Task name: `Manage Asset Categories`
- Task code: `FA_MANAGE_ASSET_CATEGORY`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Financials`
- Functional area / Setup Object: `Fixed Assets`
- Setup task name: `Manage Asset Categories`
- Setup task code: `FA_MANAGE_ASSET_CATEGORY`




## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `erp.financials.fixed-assets` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
