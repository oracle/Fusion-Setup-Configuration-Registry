---
skill_id: "scm.supply-chain-planning.supply-chain-planning-configuration.configure-planning-analytics"
name: "Configure Planning Analytics Setup Task Guidance"
description: "Provides task-specific setup guidance for Configure Planning Analytics under the Supply Chain Planning Configuration functional area."
layer: "pillar"
pillar: "SCM"
offering: "Supply Chain Planning"
functional_area: "Supply Chain Planning Configuration"
functional_area_code: "ORA_MSC_VC_PLANNING_CONFIGURAT"
task_code: "ORA_MSC_CONFIGURE_PLANNING_ANALYTICS"
task_name: "Configure Planning Analytics"
parent_skill_id: "scm.supply-chain-planning.supply-chain-planning-configuration"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "REST"
businessObjects:
  - "dimensionCatalogs"
  - "planningMeasureCatalogs"
  - "planningLevels"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM supply chain planning pillar team"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/supply-chain-planning/supply-chain-planning-configuration/configure-planning-analytics/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/supply-chain-planning/supply-chain-planning-configuration/configure-planning-analytics/current/"
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

# Configure Planning Analytics Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Configure Planning Analytics` under `Supply Chain Planning Configuration`.

## Setup Task Skill Contract

- task_code: `ORA_MSC_CONFIGURE_PLANNING_ANALYTICS`
- task_name: `Configure Planning Analytics`
- parent_skill_id: `scm.supply-chain-planning.supply-chain-planning-configuration`
- pillar: `SCM`
- offering: `Supply Chain Planning`
- functional_area: `Supply Chain Planning Configuration`
- functional_area_code: `ORA_MSC_VC_PLANNING_CONFIGURAT`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `REST`
- businessObjects: `dimensionCatalogs`, `planningMeasureCatalogs`, `planningLevels`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Configure Planning Analytics` under `Supply Chain Planning Configuration`.

## Setup Task Metadata

- Task name: `Configure Planning Analytics`
- Task code: `ORA_MSC_CONFIGURE_PLANNING_ANALYTICS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `REST`
- Business Objects: `dimensionCatalogs, planningMeasureCatalogs, planningLevels`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader` using dimensionCatalogs, planningMeasureCatalogs, planningLevels as the Business Objects.

Use this task metadata when invoking those skills:

- Offering: `Supply Chain Planning`
- Functional area / Setup Object: `Supply Chain Planning Configuration`
- Setup task name: `Configure Planning Analytics`
- Setup task code: `ORA_MSC_CONFIGURE_PLANNING_ANALYTICS`


## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business objects.

1. Confirm that `dimensionCatalogs`, `planningMeasureCatalogs`, `planningLevels` are the exact registered Data Loader business objects.
2. Generate the default editable XLSX samples through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "dimensionCatalogs" \
     "planningMeasureCatalogs" \
     "planningLevels" \
     --output-dir "<project-artifact-directory>"
   ```

3. Keep each business object's generated workbook set together:
   - editable sample workbook
   - attribute-details workbook
   - key-fields workbook
4. Review the generated headers and key fields before preparing source data. The operation uses read-only Fusion metadata and does not upload or import data.
5. Use the generated editable workbooks as the starting point for the later Data Loader preparation and approval workflow.

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

Review recorded creation/deletion cases in [tests/golden-scenarios.md](tests/golden-scenarios.md); their fixtures are sanitized session evidence, not live execution authorization.

Use the parent functional-area skill `scm.supply-chain-planning.supply-chain-planning-configuration` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

Before task validation, load [Task Rule Registry Execution](../../../../../core/data-loader/references/task-rule-registry-execution.md), the selected registry/source rules, and `ora-resource/ora_error_handling.md`. Resolve the exact task through the invoking runbook or Data Loader workflow's `resolve-task-rules` gate; require a ready registry and consistent source anchors, prerequisites, and transitions before following `start_node`. Stop on missing or inconsistent rules rather than inventing a route. The invoking runbook or Data Loader workflow owns task inputs and write approval. Route declared live GETs through `core.fusion-api.rest-api-client`; its environment, privilege, authentication, timeout and redaction checks apply. Persist validation failures through the declared project services as specified in the error guidance.
