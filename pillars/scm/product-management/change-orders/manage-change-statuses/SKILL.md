---
skill_id: "scm.product-management.change-orders.manage-change-statuses"
name: "Manage Change Statuses Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Change Statuses under the Change Orders functional area."
layer: "pillar"
pillar: "SCM"
offering: "Product Management"
functional_area: "Change Orders"
functional_area_code: "EGO_CHANGE_ORDERS"
task_code: "EGO_MANAGE_CHANGE_STATUSES"
task_name: "Manage Change Statuses"
parent_skill_id: "scm.product-management.change-orders"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM product management pillar team"
version: "0.1.0"
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
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
uses_core:
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
    default_location: "project/{project_id}/artifacts/pillars/scm/product-management/change-orders/manage-change-statuses/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/product-management/change-orders/manage-change-statuses/current/"
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
side_effects: []
required_privileges: []
---

# Manage Change Statuses Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Change Statuses` under `Change Orders`.

## Setup Task Skill Contract

- task_code: `EGO_MANAGE_CHANGE_STATUSES`
- task_name: `Manage Change Statuses`
- parent_skill_id: `scm.product-management.change-orders`
- pillar: `SCM`
- offering: `Product Management`
- functional_area: `Change Orders`
- functional_area_code: `EGO_CHANGE_ORDERS`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Change Statuses` under `Change Orders`.

## Setup Task Metadata

- Task name: `Manage Change Statuses`
- Task code: `EGO_MANAGE_CHANGE_STATUSES`
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

- Offering: `Product Management`
- Functional area / Setup Object: `Change Orders`
- Setup task name: `Manage Change Statuses`
- Setup task code: `EGO_MANAGE_CHANGE_STATUSES`




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

Use the parent functional-area skill `scm.product-management.change-orders` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Business Controls

Before creating or changing a change status, apply the task-specific controls in the [ORA resources](ora-resource/). This skill supports Create and Update only; reject Delete. Every Create and Update must begin with a fresh populated target export. For Create, use that export to resolve a supplied internal name or derive an omitted one from the Status Name by replacing whitespace runs with `_`, then reject whitespace-bearing or duplicate internal names and duplicate status names before ZIP preparation. Every Update must use a valid selector combination—Existing Internal Name; Existing Status; Existing Status with Existing Status Type; or Internal Name with either or both additional checks—to resolve the current row from that export. Existing Internal Name is a selector only; it never permits a template-only or partial-row import. Copy the complete selected exported row into the import ZIP and change only the requested StatusName, Description, or StatusType field. This preserves StatusInternalName, StatusName, StatusType, ObjectName, SeededFlag, and every other exported carrier. When the user provides End Date, show: "Warning: Change Status End Date is not supported by the import/export process and will be skipped." Omit End Date and continue with other supported requested changes. If no supported change remains, do not prepare an import artifact. Before showing approval, verify each update ZIP row against its selected export row: every non-requested field must be present and unchanged. If the check fails, regenerate the ZIP from the export; never preview or submit a partial update row. Existing Status alone proceeds when it resolves one row; when it resolves multiple rows, show every match and obtain explicit scope approval before preparing its ZIP. Otherwise, do not ask for confirmation during validation or ZIP preparation. Show the prepared ZIP contents and obtain explicit approval before import.
