---
skill_id: "erp.financials.fixed-assets.manage-prorate-conventions"
name: "Manage Prorate Conventions Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Prorate Conventions under the Fixed Assets functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Fixed Assets"
functional_area_code: "FIN_FIXED_ASSETS_DEPLOYED"
task_code: "FA_MANAGE_PRORATE_CONVENTION"
task_name: "Manage Prorate Conventions"
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
version: "0.12.1"
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
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
uses_core:
  - "core.fusion-api.apps-common.descriptive-flexfields"
  - "core.auth.fusion-oauth-authentication"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/fixed-assets/manage-prorate-conventions/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/fixed-assets/manage-prorate-conventions/current/"
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
  - "Reads current Convention Types DFF definitions and validates supplied or preserved values through declared read-only workflows."
  - "Performs read-only target lookups for Reference Data Set identity, SetCode, and fiscal-year dates."
  - "May refresh local gitignored OAuth token caches through the shared authentication capability."
  - "Routes validation FSM exports and approved import operations to shared and core skills."
required_privileges:
  - "Read access to the selected DFF metadata export and applicable value-set scopes."
  - "Fusion access for FA_MANAGE_PRORATE_CONVENTION export and import."
  - "Fusion BOSS read access to assetFiscalYearDatesView."
  - "Fusion BOSS read access to commonAppsInfra setIdSets."
---

# Manage Prorate Conventions Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation
guidance for `Manage Prorate Conventions` under `Fixed Assets`.

## Setup Task Skill Contract

- task_code: `FA_MANAGE_PRORATE_CONVENTION`
- task_name: `Manage Prorate Conventions`
- parent_skill_id: `erp.financials.fixed-assets`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`

## Usage

Use this skill when planning, creating, updating, importing, or validating
Fixed Assets prorate conventions. Use the parent Fixed Assets skill for shared
approval, immutable ZIP review, import-status handoff, post-import
verification, and project-state safeguards. This child skill validates the
requested convention, fiscal-year/date rows, reference data set, defaults, and
package readiness; it must not poll accepted imports or start dependent tasks.

## Setup Task Metadata

- Offering: `Financials`
- Functional area / Setup Object: `Fixed Assets`
- Setup task name: `Manage Prorate Conventions`
- Setup task code: `FA_MANAGE_PRORATE_CONVENTION`



## CSV Export, Import, and Validation Workflow

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Build a task-specific delta ZIP containing only the requested create or
   update rows; use the baseline export only for CSV members, headers,
   metadata, and supported values. Do not re-import baseline records.
5. Import the approved immutable package with `core.data-loader`; after
   accepted initiation, report `accepted — pending parent verification` and
   leave terminal status, ProcessLog review, and fresh target read-back to the
   parent Fixed Assets workflow.

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
