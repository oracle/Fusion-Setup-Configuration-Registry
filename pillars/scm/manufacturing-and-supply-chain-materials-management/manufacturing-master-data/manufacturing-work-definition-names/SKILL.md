---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.manufacturing-master-data.manufacturing-work-definition-names"
name: "Manufacturing Work Definition Names Setup Task Guidance"
description: "Provides task-specific setup guidance for Manufacturing Work Definition Names under the Manufacturing Master Data functional area."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Manufacturing Master Data"
functional_area_code: "ORA_WIS_COMMON_MFG_WORK_SETUP"
task_code: "CUSTOM_MANUFACTURING_WD_NAME"
task_name: "Manufacturing Work Definition Names"
parent_skill_id: "scm.manufacturing-and-supply-chain-materials-management.manufacturing-master-data"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "REST"
businessObject: "workDefinitionNamesV2"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM manufacturing and supply chain materials management pillar team"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/manufacturing-master-data/manufacturing-work-definition-names/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/manufacturing-master-data/manufacturing-work-definition-names/current/"
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

# Manufacturing Work Definition Names Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manufacturing Work Definition Names` under `Manufacturing Master Data`.

## Setup Task Skill Contract

- task_code: `CUSTOM_MANUFACTURING_WD_NAME`
- task_name: `Manufacturing Work Definition Names`
- parent_skill_id: `scm.manufacturing-and-supply-chain-materials-management.manufacturing-master-data`
- pillar: `SCM`
- offering: `Manufacturing and Supply Chain Materials Management`
- functional_area: `Manufacturing Master Data`
- functional_area_code: `ORA_WIS_COMMON_MFG_WORK_SETUP`
- available_flag: `Y`
- export_import_supported_flag: `N`
- csv_export_import_supported_flag: `N`
- dataloader_import_mode: `REST`
- businessObject: `workDefinitionNamesV2`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manufacturing Work Definition Names` under `Manufacturing Master Data`.

## Setup Task Metadata

- Task name: `Manufacturing Work Definition Names`
- Task code: `CUSTOM_MANUFACTURING_WD_NAME`
- Available: `Y`
- Export/import supported: `N`
- CSV export/import supported: `N`
- CSV export/import routing: `not supported`
- Data Loader import mode: `REST`
- Business Object: `workDefinitionNamesV2`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `N`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

Do not route CSV export work to `shared.setup-export.task-level-export` or CSV import work to `core.data-loader` unless live Fusion metadata or Oracle guidance confirms support. Use `shared.validation.setup-data-validator` only when a setup data artifact is available for review. Use `shared.validation.reference-data-validator` when the task depends on cross-pillar reference data.


## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business object.

1. Confirm that `workDefinitionNamesV2` is the exact registered Data Loader business object.
2. Generate the default editable XLSX sample through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "workDefinitionNamesV2" \
     --output-dir "<project-artifact-directory>"
   ```

3. Keep the generated workbooks together:
   - editable sample
   - attribute-details workbook
   - key-fields workbook
4. Review the generated headers and key fields before preparing source data. The operation uses read-only Fusion metadata and does not upload or import data.
5. Use the generated editable workbook as the starting point for the later Data Loader preparation and approval workflow.



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

Use the parent functional-area skill `scm.manufacturing-and-supply-chain-materials-management.manufacturing-master-data` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
