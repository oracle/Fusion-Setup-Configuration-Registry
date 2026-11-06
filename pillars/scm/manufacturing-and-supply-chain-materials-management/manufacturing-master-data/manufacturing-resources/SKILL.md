---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.manufacturing-master-data.manufacturing-resources"
name: "Manufacturing Resources Setup Task Guidance"
description: "Provides task-specific setup guidance for Manufacturing Resources under the Manufacturing Master Data functional area."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Manufacturing Master Data"
functional_area_code: "ORA_WIS_COMMON_MFG_WORK_SETUP"
task_code: "ORA_REDWOOD_MANUFACTURING_RESOURCES"
task_name: "Manufacturing Resources"
parent_skill_id: "scm.manufacturing-and-supply-chain-materials-management.manufacturing-master-data"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: "productionResources"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/manufacturing-master-data/manufacturing-resources/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/manufacturing-master-data/manufacturing-resources/current/"
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

# Manufacturing Resources Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manufacturing Resources` under `Manufacturing Master Data`.

## Setup Task Skill Contract

- task_code: `ORA_REDWOOD_MANUFACTURING_RESOURCES`
- task_name: `Manufacturing Resources`
- parent_skill_id: `scm.manufacturing-and-supply-chain-materials-management.manufacturing-master-data`
- pillar: `SCM`
- offering: `Manufacturing and Supply Chain Materials Management`
- functional_area: `Manufacturing Master Data`
- functional_area_code: `ORA_WIS_COMMON_MFG_WORK_SETUP`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: use the manifest frontmatter value.
- businessObject: `productionResources`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manufacturing Resources` under `Manufacturing Master Data`.

## Setup Task Metadata

- Task name: `Manufacturing Resources`
- Task code: `ORA_REDWOOD_MANUFACTURING_RESOURCES`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: follow `dataloader_import_mode` in frontmatter.
- Business Object: `productionResources`

## Import Mode Selection

Use the manifest's `dataloader_import_mode` as the default unless the active
workflow records an explicit supported mode override. Both modes use `core.data-loader` validation, immutable-artifact approval,
and execution; selecting FSM does not bypass the central workflow.

- For `FSM`, use the selected task's target-exported CSV package and
  `ASM_SETUP_CSV_METADATA.xml`. Preserve required members, exported column names,
  parent-child keys, and native Y/N flags. Keep unrequested child CSVs header-only
  and exclude unrelated baseline records. Validate mappings before preparation;
  do not convert native FSM CSVs to a REST DAT or require REST BO registration.
- For `REST` (the HCM Data Loader route), retain `productionResources` as the
  `businessObject`, require its corrected live registration, and use the existing
  sample, metadata, operation, and task rules. REST field encodings and child
  contracts still apply; native FSM exceptions do not apply to REST sources.
- To restore the REST default after the BO configuration is fixed, update
  `dataloader_import_mode` to `REST`,
  retaining the declared business object. Revalidate new sources through the
  selected route; never reuse an approval for a different mode or artifact.
- FSM selection alone does not authorize deletion. Stop on a requested operation
  unsupported by the selected route; never turn a delete into a merge or silently
  switch routes after a failed or uncertain write.

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader` using the selected `dataloader_import_mode` and its matching artifact contract.

Use this task metadata when invoking those skills:

- Offering: `Manufacturing and Supply Chain Materials Management`
- Functional area / Setup Object: `Manufacturing Master Data`
- Setup task name: `Manufacturing Resources`
- Setup task code: `ORA_REDWOOD_MANUFACTURING_RESOURCES`


## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business object.

1. Confirm that `productionResources` is the exact registered Data Loader business object.
2. Generate the default editable XLSX sample through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "productionResources" \
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
