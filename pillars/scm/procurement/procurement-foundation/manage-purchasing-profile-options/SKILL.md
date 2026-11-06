---
skill_id: "scm.procurement.procurement-foundation.manage-purchasing-profile-options"
name: "Manage Purchasing Profile Options Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Purchasing Profile Options under the Procurement Foundation functional area."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "Procurement Foundation"
functional_area_code: "ORA_PO_PROC_FOUNDATION_FA"
task_code: "PO_MANAGE_PURCHASING_PROFILE_OPTIONS"
task_name: "Manage Purchasing Profile Options"
parent_skill_id: "scm.procurement.procurement-foundation"
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
  - "core.fusion-api.apps-common.profile-options"
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
uses_core:
  - "core.fusion-api.apps-common.profile-options"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/procurement-foundation/manage-purchasing-profile-options/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/procurement-foundation/manage-purchasing-profile-options/current/"
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

# Manage Purchasing Profile Options Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Purchasing Profile Options` under `Procurement Foundation`.

## Setup Task Skill Contract

- task_code: `PO_MANAGE_PURCHASING_PROFILE_OPTIONS`
- task_name: `Manage Purchasing Profile Options`
- parent_skill_id: `scm.procurement.procurement-foundation`
- pillar: `SCM`
- offering: `Procurement`
- functional_area: `Procurement Foundation`
- functional_area_code: `ORA_PO_PROC_FOUNDATION_FA`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Purchasing Profile Options` under `Procurement Foundation`.

## Setup Task Metadata

- Task name: `Manage Purchasing Profile Options`
- Task code: `PO_MANAGE_PURCHASING_PROFILE_OPTIONS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## Profile Option Routing

Use `core.fusion-api.apps-common.profile-options` for FND profile-option
definition discovery and configured profile-option value changes. Provide the
profile option's internal code, requested action, configured level (`site`,
`product`, or `user`), intended value, and the scope target for product or
user level. The Apps Common workflow validates the definition, enabled and
updatable level, target identity, and current value before a write. It owns
approval, mutation, and diagnostics; do not call profile-option REST endpoints
directly from this task skill.

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. For a supplied FSM task-export artifact, import setup task data with
   `core.data-loader` after the Data Loader workflow validates the artifact.
5. For normal FND profile-option discovery or value changes, use the Profile
   Option Routing section above rather than Data Loader.

Use this task metadata when invoking those skills:

- Offering: `Procurement`
- Functional area / Setup Object: `Procurement Foundation`
- Setup task name: `Manage Purchasing Profile Options`
- Setup task code: `PO_MANAGE_PURCHASING_PROFILE_OPTIONS`




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

Use the parent functional-area skill `scm.procurement.procurement-foundation` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
