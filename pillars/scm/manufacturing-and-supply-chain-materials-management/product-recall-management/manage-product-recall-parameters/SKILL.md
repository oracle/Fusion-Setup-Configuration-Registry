---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.product-recall-management.manage-product-recall-parameters"
name: "Manage Product Recall Parameters Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Product Recall Parameters under the Product Recall Management functional area."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Product Recall Management"
functional_area_code: "ORA_ENQ_PRODUCT_RECALL_MANAGEMENT"
task_code: "ORA_MANAGE_PRODUCT_RECALL_PARAMETERS"
task_name: "Manage Product Recall Parameters"
parent_skill_id: "scm.manufacturing-and-supply-chain-materials-management.product-recall-management"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "REST"
businessObjects:
  - "recallGlobalParams"
  - "recallItemValidationOrganizations"
  - "recallInventoryOrganizations"
  - "recallContainmentTaskOwners"
  - "recallProductTraceabilityGroupings"
  - "recallSubinventories"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM manufacturing and supply chain materials management pillar team"
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
  - "scm.manufacturing-and-supply-chain-materials-management.product-recall-management"
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
uses_core:
  - "core.fusion-api.rest-api-client"
  - "core.data-loader.task-hook"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/product-recall-management/manage-product-recall-parameters/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/product-recall-management/manage-product-recall-parameters/current/"
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

# Manage Product Recall Parameters Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Product Recall Parameters` under `Product Recall Management`.

## Setup Task Skill Contract

- task_code: `ORA_MANAGE_PRODUCT_RECALL_PARAMETERS`
- task_name: `Manage Product Recall Parameters`
- parent_skill_id: `scm.manufacturing-and-supply-chain-materials-management.product-recall-management`
- pillar: `SCM`
- offering: `Manufacturing and Supply Chain Materials Management`
- functional_area: `Product Recall Management`
- functional_area_code: `ORA_ENQ_PRODUCT_RECALL_MANAGEMENT`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `REST`
- businessObjects: `recallGlobalParams`, `recallItemValidationOrganizations`, `recallInventoryOrganizations`, `recallContainmentTaskOwners`, `recallProductTraceabilityGroupings`, `recallSubinventories`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Product Recall Parameters` under `Product Recall Management`.

## Setup Task Metadata

- Task name: `Manage Product Recall Parameters`
- Task code: `ORA_MANAGE_PRODUCT_RECALL_PARAMETERS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `REST`
- Business Objects: `recallGlobalParams, recallItemValidationOrganizations, recallInventoryOrganizations, recallContainmentTaskOwners, recallProductTraceabilityGroupings, recallSubinventories`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader` using recallGlobalParams, recallItemValidationOrganizations, recallInventoryOrganizations, recallContainmentTaskOwners, recallProductTraceabilityGroupings, recallSubinventories as the Business Objects.

Use this task metadata when invoking those skills:

- Offering: `Manufacturing and Supply Chain Materials Management`
- Functional area / Setup Object: `Product Recall Management`
- Setup task name: `Manage Product Recall Parameters`
- Setup task code: `ORA_MANAGE_PRODUCT_RECALL_PARAMETERS`


## Task Preflight and Data Loader Handoff

Use the current `core.data-loader` immutable-artifact workflow for imports. Complete source review, mapping, Business Object/API validation, conversion and final upload artifact preparation before invoking `core.data-loader.task-hook` through its `data-load` route. Require Data Loader's verified persisted preflight, with task routing, completed mapping and a digest matching the final artifact. Read the Task Hook's returned execution guide and evaluate this task's graph against that exact artifact and current declared read-only lookup evidence. Do not invoke Task Validator directly.

`RECALL.PARAMETERS.DONE-READY-FOR-PREVIEW` means task rules passed; it does not approve or submit an import. Return ordered rule results to Task Hook and use its `build-data-load-preview` command with the final artifact digest. Core Data Loader owns the approval report and approval policy. After approval through that policy, use Task Hook's `approve-data-load-preview` and `verify-approved-data-load-archive` commands. Persist the returned `taskValidationEnvelope` unchanged and pass it to Data Loader with its approved preflight envelope. Never reconstruct previews, approvals, envelopes or digests.

Keep the prepared artifact immutable through validation and approval. A correction to the artifact, mapping, environment or task rules requires fresh preparation, validation and approval. After approval, submit the exact persisted bytes through the approved-preflight route; do not reopen or reconvert original sources or repeat live validation. An edit to an original source alone does not alter an intact approved artifact. Missing or changed artifacts or mismatched context/envelopes block submission and require fresh validation and approval.

Explicit sample deliverables use the separate sample workflow below. Task-authored durable plans and checkpoints contain sanitized summaries only, using the artifact contract. Core Data Loader and Task Hook retain their prescribed internal preflight, preview, approval and validation-envelope artifacts; do not copy that material into task planning artifacts. Task Hook owns its validation-result registration, run record and token-usage entry. Never persist credentials or worker identity details in task checkpoints.

## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business objects.

1. Confirm that `recallGlobalParams`, `recallItemValidationOrganizations`, `recallInventoryOrganizations`, `recallContainmentTaskOwners`, `recallProductTraceabilityGroupings`, `recallSubinventories` are the exact registered Data Loader business objects.
2. Generate the default editable XLSX samples through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "recallGlobalParams" \
     "recallItemValidationOrganizations" \
     "recallInventoryOrganizations" \
     "recallContainmentTaskOwners" \
     "recallProductTraceabilityGroupings" \
     "recallSubinventories" \
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

## Machine Readable Output Contract

Use [`ora-resource/ora_output_contract.json`](ora-resource/ora_output_contract.json) for the required JSON shapes of `setup_task_plan`, `setup_data_routing`, and `validation_checkpoints`. Persist those artifacts using the manifest's declared workspace output locations. The contract contains no customer values, environment identifiers, credentials, or executable payloads.

## Implementation Notes

Review the synthetic [golden scenarios](references/golden-scenarios.md) before changing task gates or graph transitions.

Use the parent functional-area skill `scm.manufacturing-and-supply-chain-materials-management.product-recall-management` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
