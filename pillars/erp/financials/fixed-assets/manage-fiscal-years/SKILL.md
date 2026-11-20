---
skill_id: "erp.financials.fixed-assets.manage-fiscal-years"
name: "Manage Fiscal Years Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Fiscal Years under the Fixed Assets functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Fixed Assets"
functional_area_code: "FIN_FIXED_ASSETS_DEPLOYED"
task_code: "FA_MANAGE_FISCAL_YEAR"
task_name: "Manage Fiscal Years"
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
version: "0.1.6"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/fixed-assets/manage-fiscal-years/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/fixed-assets/manage-fiscal-years/current/"
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

# Manage Fiscal Years Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation
guidance for `Manage Fiscal Years` under `Fixed Assets`.

## Setup Task Skill Contract

- task_code: `FA_MANAGE_FISCAL_YEAR`
- task_name: `Manage Fiscal Years`
- parent_skill_id: `erp.financials.fixed-assets`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`

## Usage

Use this skill when planning, creating, updating, importing, or validating
Fixed Assets fiscal years. Use the parent Fixed Assets skill for shared
approval, import-status, and project-state safeguards.

## Setup Task Metadata

- Offering: `Financials`
- Functional area / Setup Object: `Fixed Assets`
- Setup task name: `Manage Fiscal Years`
- Setup task code: `FA_MANAGE_FISCAL_YEAR`

## Resource Routing

| Need | Read |
|---|---|
| Required names, dates, and package cohesion | [ora_input_validation.md](ora-resource/ora_input_validation.md) |
| Ledger-derived facts and existing-state checks | [ora_reference_lookups.md](ora-resource/ora_reference_lookups.md) |
| Defaults | [ora_defaulting_rules.md](ora-resource/ora_defaulting_rules.md) |
| Dependencies and coverage | [ora_dependency_readiness.md](ora-resource/ora_dependency_readiness.md) |
| Design and production readiness | [ora_design_enforcement.md](ora-resource/ora_design_enforcement.md) |
| Failures and safe next actions | [ora_error_handling.md](ora-resource/ora_error_handling.md) |
| Task sequence | [ora_rule_registry.json](ora-resource/ora_rule_registry.json) |

## CSV Export, Import, and Validation Workflow

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Build a task-specific delta ZIP containing only the requested create or update rows; use the baseline export only for CSV members, headers, metadata, and supported values. Do not re-import baseline records.
5. Import the approved immutable package with `core.data-loader`.
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

Keep technical export and package metadata internal. Track token usage for
generated project artifacts and skill-run records using the manifest policy.





