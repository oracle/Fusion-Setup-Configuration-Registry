---
skill_id: "scm.procurement.procurement-foundation.configure-requisitioning-business-function"
name: "Configure Requisitioning Business Function Setup Task Guidance"
description: "Prepares and imports requisitioning business-function setup data through FSM task-level CSV export and import for the Procurement Foundation functional area."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "Procurement Foundation"
functional_area_code: "ORA_PO_PROC_FOUNDATION_FA"
task_code: "POR_CONFIGURE_REQUISITIONING_BUSINESS_FUNCTION"
task_name: "Configure Requisitioning Business Function"
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
  - "operation"
  - "setup_data_zip"
  - "fusion_environment_context"
outputs:
  - "setup_task_plan"
  - "template_package"
  - "setup_data_validation_result"
  - "reference_data_validation_result"
  - "data_loader_approval_preview"
  - "setup_data_import_result"
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
  - "core.data-loader"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/procurement-foundation/configure-requisitioning-business-function/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/procurement-foundation/configure-requisitioning-business-function/current/"
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

# Configure Requisitioning Business Function Setup Task Guidance

## Purpose

Prepares, validates, and imports requisitioning business-function setup data through the FSM task-level CSV export and import route for `Procurement Foundation`.

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Configure Requisitioning Business Function` under `Procurement Foundation`.

## Setup Task Skill Contract

- task_code: `POR_CONFIGURE_REQUISITIONING_BUSINESS_FUNCTION`
- task_name: `Configure Requisitioning Business Function`
- parent_skill_id: `scm.procurement.procurement-foundation`
- pillar: `SCM`
- offering: `Procurement`
- functional_area: `Procurement Foundation`
- functional_area_code: `ORA_PO_PROC_FOUNDATION_FA`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Supported Route

Use the FSM task-level setup data route for every export, prepare, validate, and import activity for this task:

1. Export the task template or baseline package with `shared.setup-export.task-level-export`.
2. Prepare the task CSV files inside the exported package structure.
3. Validate the prepared setup data with `shared.validation.setup-data-validator`.
4. Validate referenced setup values with `shared.validation.reference-data-validator`.
5. Present the prepared package, validation results, target environment, and intended operation for explicit user approval.
6. Route the immutable validated archive to `core.data-loader` as an FSM task-routed import with target environment, task context, SHA-256, and validation evidence.
7. Let Data Loader create the immutable approval preview, then proceed only after separate immediate approval for that unchanged preview.
8. Data Loader owns upload, initiation, monitoring, and diagnostics. Track the returned import process identifier to a terminal state before reporting the result.

## Setup Task Metadata

- Task name: `Configure Requisitioning Business Function`
- Task code: `POR_CONFIGURE_REQUISITIONING_BUSINESS_FUNCTION`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`

## Resource-Authored Rules

Use the task-local `ora-resource` artifacts as the source of truth for executable setup guidance:

- `ora_input_validation.md` owns required inputs, CSV-package validation, task identity checks, validator gates, Data Loader approval-preview checks, and user approval requirements.
- `ora_defaulting_rules.md` owns CSV field defaults and defaulting guardrails.
- `ora_design_enforcement.md` owns route enforcement and Data Loader import ownership checks.
- `ora_error_handling.md` owns failure classification, disclosure, refusal rules, and terminal task nodes.

## FSM Evidence and Status Tracking

For an export, retain the export request, returned `ProcessId`, every poll result, terminal status, and the downloaded ZIP or process log artifact path.

For an import, retain the approved ZIP path, SHA-256, Data Loader approval preview, upload evidence, initiation response, returned request or process identifier, every poll result, terminal status, and process log artifact path. Report an import as initiated only after Fusion returns an accepted initiation response with an identifier that can be tracked.

When status is requested, use the exact captured process identifier. If an authoritative response or required identifier is missing, stop with a tracking-failure result; do not label execution successful, failed, or indeterminate, and do not reissue the import.

## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `operation`
- `setup_data_zip`
- `fusion_environment_context`

## Outputs

- `setup_task_plan`
- `template_package`
- `setup_data_validation_result`
- `reference_data_validation_result`
- `data_loader_approval_preview`
- `setup_data_import_result`
- `setup_data_routing`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `scm.procurement.procurement-foundation` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
