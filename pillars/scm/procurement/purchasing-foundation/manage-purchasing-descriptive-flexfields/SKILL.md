---
skill_id: "scm.procurement.purchasing-foundation.manage-purchasing-descriptive-flexfields"
name: "Manage Purchasing Descriptive Flexfields Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Purchasing Descriptive Flexfields under the Purchasing Foundation functional area."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "Purchasing Foundation"
functional_area_code: "ORA_PO_PURCHASING_FOUNDATION"
task_code: "PO_MANAGE_PURCHASING_DESCRIPTIVE_FLEXFIELDS"
task_name: "Manage Purchasing Descriptive Flexfields"
parent_skill_id: "scm.procurement.purchasing-foundation"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM procurement pillar team"
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
  - "core.fusion-api.apps-common.descriptive-flexfields"
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
uses_core:
  - "core.fusion-api.apps-common.descriptive-flexfields"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/purchasing-foundation/manage-purchasing-descriptive-flexfields/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/purchasing-foundation/manage-purchasing-descriptive-flexfields/current/"
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

# Manage Purchasing Descriptive Flexfields Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Purchasing Descriptive Flexfields` under `Purchasing Foundation`.

## Setup Task Skill Contract

- task_code: `PO_MANAGE_PURCHASING_DESCRIPTIVE_FLEXFIELDS`
- task_name: `Manage Purchasing Descriptive Flexfields`
- parent_skill_id: `scm.procurement.purchasing-foundation`
- pillar: `SCM`
- offering: `Procurement`
- functional_area: `Purchasing Foundation`
- functional_area_code: `ORA_PO_PURCHASING_FOUNDATION`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Purchasing Descriptive Flexfields` under `Purchasing Foundation`.

## Setup Task Metadata

- Task name: `Manage Purchasing Descriptive Flexfields`
- Task code: `PO_MANAGE_PURCHASING_DESCRIPTIVE_FLEXFIELDS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## Descriptive Flexfield Routing

Route Purchasing DFF setup-data work through
`core.fusion-api.apps-common.descriptive-flexfields`. It validates the exact
task context and catalog eligibility, uses task-level export for CSV export,
uses `core.data-loader` only for an approved FSM CSV import, and governs
approval-gated DFF deployment status workflows. Do not use direct REST
transport or submit an FSM archive outside that workflow.

Confirm the intended Purchasing flexfield definition and context from current
Fusion metadata before preparing an export or import artifact; do not infer it
from a similar definition name.

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. For DFF setup-data import, use the Descriptive Flexfield Routing section;
   it delegates an approved immutable FSM CSV archive to `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Procurement`
- Functional area / Setup Object: `Purchasing Foundation`
- Setup task name: `Manage Purchasing Descriptive Flexfields`
- Setup task code: `PO_MANAGE_PURCHASING_DESCRIPTIVE_FLEXFIELDS`




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

Use the parent functional-area skill `scm.procurement.purchasing-foundation` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
