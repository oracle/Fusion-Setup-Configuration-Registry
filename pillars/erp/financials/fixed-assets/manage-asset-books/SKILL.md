---
skill_id: "erp.financials.fixed-assets.manage-asset-books"
name: "Manage Asset Books Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Asset Books under the Fixed Assets functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Fixed Assets"
functional_area_code: "FIN_FIXED_ASSETS_DEPLOYED"
task_code: "FA_MANAGE_ASSET_BOOK"
task_name: "Manage Asset Books"
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
version: "0.1.9"
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
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
  - "core.fusion-api.rest-api-client"
uses_core:
  - "core.fusion-api.apps-common.descriptive-flexfields"
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
  - "core.fusion-api.rest-api-client"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/fixed-assets/manage-asset-books/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/fixed-assets/manage-asset-books/current/"
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

# Manage Asset Books Setup Task Guidance

## Purpose

Plan, export, import, or validate Fixed Assets book setup. An asset book must exist before assets can be added.

## Setup Task Skill Contract

- Task code: `FA_MANAGE_ASSET_BOOK`
- Task name: `Manage Asset Books`
- Parent skill: `erp.financials.fixed-assets`
- Pillar: `ERP`
- Offering: `Financials`
- Functional area: `Fixed Assets` (`FIN_FIXED_ASSETS_DEPLOYED`)
- Available/export/import/CSV support: `Y`
- Source catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Asset Books` under `Fixed Assets`.

## Setup Task Metadata

- Task name: `Manage Asset Books`
- Task code: `FA_MANAGE_ASSET_BOOK`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Catalog purpose: create books with accounting rules and accounts for fixed-assets reporting and tax accounting policies.

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

Use the parent `erp.financials.fixed-assets` skill for broader sequencing and scope. Track token usage for generated project artifacts and skill-run records using the manifest policy.
