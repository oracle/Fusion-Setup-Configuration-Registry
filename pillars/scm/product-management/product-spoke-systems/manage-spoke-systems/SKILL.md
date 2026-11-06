---
skill_id: "scm.product-management.product-spoke-systems.manage-spoke-systems"
name: "Manage Spoke Systems Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Spoke Systems under the Product Spoke Systems functional area."
layer: "pillar"
pillar: "SCM"
offering: "Product Management"
functional_area: "Product Spoke Systems"
functional_area_code: "EGI_PRODUCT_SOURCE_SYSTEMS"
task_code: "EGI_MANAGE_SOURCE_SYSTEMS"
task_name: "Manage Spoke Systems"
parent_skill_id: "scm.product-management.product-spoke-systems"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "REST"
businessObjects:
  - "spokeSystemImportOptions"
  - "spokeSystemPublicationOptions"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM product management pillar team"
version: "0.1.1"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/product-management/product-spoke-systems/manage-spoke-systems/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/product-management/product-spoke-systems/manage-spoke-systems/current/"
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

# Manage Spoke Systems Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Spoke Systems` under `Product Spoke Systems`.

## Setup Task Skill Contract

- task_code: `EGI_MANAGE_SOURCE_SYSTEMS`
- task_name: `Manage Spoke Systems`
- parent_skill_id: `scm.product-management.product-spoke-systems`
- pillar: `SCM`
- offering: `Product Management`
- functional_area: `Product Spoke Systems`
- functional_area_code: `EGI_PRODUCT_SOURCE_SYSTEMS`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `REST`
- businessObjects: `spokeSystemImportOptions`, `spokeSystemPublicationOptions`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Spoke Systems` under `Product Spoke Systems`.

## Live Metadata Mapping

For requests to configure or change spoke-system options, use the
`spokeSystemImportOptions` and `spokeSystemPublicationOptions` business objects
available in the selected environment for metadata mapping through
`core.data-loader`'s live registered-business-object and schema workflows.
Select the owning business object and map the requested settings, values, and
identity keys from its live metadata. Do not require the user to repeat this
instruction or supply technical field names or a pre-existing sample workbook.
Do not hardcode setting-specific mappings or enum values.

A missing static task-specific mapping is not itself an incomplete contract:
first attempt the declared live metadata mapping. If the live contract remains
missing or ambiguous, report the exact unresolved field or identity requirement
and stop. Continue through the existing Data Loader validation and approval
workflow only after mapping succeeds; metadata discovery does not authorize a
write or establish that a requested setting was saved.

## Setup Task Metadata

- Task name: `Manage Spoke Systems`
- Task code: `EGI_MANAGE_SOURCE_SYSTEMS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `REST`
- Business Objects: `spokeSystemImportOptions, spokeSystemPublicationOptions`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader` using spokeSystemImportOptions, spokeSystemPublicationOptions as the Business Objects.

Use this task metadata when invoking those skills:

- Offering: `Product Management`
- Functional area / Setup Object: `Product Spoke Systems`
- Setup task name: `Manage Spoke Systems`
- Setup task code: `EGI_MANAGE_SOURCE_SYSTEMS`


## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business objects.

1. Confirm that `spokeSystemImportOptions`, `spokeSystemPublicationOptions` are the exact registered Data Loader business objects.
2. Generate the default editable XLSX samples through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "spokeSystemImportOptions" \
     "spokeSystemPublicationOptions" \
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

Use the parent functional-area skill `scm.product-management.product-spoke-systems` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Review and Task Rules

Required reviewers: responsible SCM Pillar Development Lead or SME and an FSCR A-Team/core reviewer.

Task-local validation is defined in `ora-resource/ora_input_validation.md` and `ora-resource/ora_error_handling.md`, with the compiled graph in `ora-resource/ora_rule_registry.json`. These rules require `spokeSystemCode`; they validate input presence only. Data Loader retains its metadata, identity, payload validation, and approval gates.
