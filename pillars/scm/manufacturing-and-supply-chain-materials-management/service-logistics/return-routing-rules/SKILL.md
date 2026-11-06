---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.service-logistics.return-routing-rules"
name: "Return Routing Rules Setup Task Guidance"
description: "Provides Business Object setup-data routing and validation guidance for Return Routing Rules under Service Logistics."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Service Logistics"
functional_area_code: "ORA_RCL"
task_code: "ORA_RCL_RETURN_ROUTING_RULES"
task_name: "Return Routing Rules"
parent_skill_id: "scm.manufacturing-and-supply-chain-materials-management.service-logistics"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "REST"
businessObject: "returnRoutingRules"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM manufacturing and supply chain materials management pillar team"
version: "0.3.3"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "requested_operation"
  - "rule_values"
  - "existing_rule_key"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "business_object_plan"
  - "business_object_readiness"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "scm.manufacturing-and-supply-chain-materials-management.service-logistics"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/service-logistics/return-routing-rules/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/service-logistics/return-routing-rules/current/"
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

# Return Routing Rules Setup Task Guidance

## Purpose

Provides task-specific setup planning, Business Object routing, export, import, and validation guidance for `Return Routing Rules` under `Service Logistics`.

## Setup Task Skill Contract

- task_code: `ORA_RCL_RETURN_ROUTING_RULES`
- task_name: `Return Routing Rules`
- parent_skill_id: `scm.manufacturing-and-supply-chain-materials-management.service-logistics`
- pillar: `SCM`
- offering: `Manufacturing and Supply Chain Materials Management`
- functional_area: `Service Logistics`
- functional_area_code: `ORA_RCL`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `REST`
- businessObject: `returnRoutingRules`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating `Return Routing Rules` setup data under `Service Logistics`.

## Setup Task Metadata

- Task name: `Return Routing Rules`
- Task code: `ORA_RCL_RETURN_ROUTING_RULES`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `REST`
- BO for REST: `returnRoutingRules` (Return Routing Rules; also referred to as `ReturnRoutingRules`)

## Return Routing Rules Business Object

Use **Return Routing Rules** as the setup task. Select the `REST` setup-data import adapter and its BO for REST, `returnRoutingRules`. The user-supplied spelling `ReturnRoutingRules` is an alias to resolve against the registered object; the registration evidence identifies the top Business Object and resource discriminator as case-sensitive `returnRoutingRules`. Confirm that the selected environment exposes that exact object and its REST import contract before preparing a load. Route the REST-backed setup-data import through `core.data-loader`; a direct rule-resource POST is a different operation and does not satisfy this import workflow.

1. Identify the target environment, requested create, update, or delete operation, and source values. For an existing rule, confirm its operation-specific key from the live Data Loader key-fields metadata or a validated task export. Do not invent a key.
2. Route sample generation and live attribute/key discovery through `core.data-loader`. Use the generated editable sample, attribute-details workbook, and key-fields workbook to establish the exact import field contract. Resolve the status field and required fields for the selected operation before preview.
3. Apply the task-specific input, dependency, local reference, and error checks in `ora-resource/`. Validate supplied item, zone, organization, subinventory, and other reference values against the reviewed, environment-bound ephemeral reference bundle defined in `ora-resource/ora_reference_lookups.md`. Stop on missing or stale evidence, Business Object registration, unresolved fields or keys, or ambiguous reference values. The Return Routing Rules task export confirms existing rule identity; it does not replace the reference bundle.
4. Route source validation, immutable artifact preparation, preview, approval, upload, REST-backed import, monitoring, and diagnostics through `core.data-loader` and its own authorization workflow. Use the confirmed BO for REST in the prepared import artifact. A sample request produces a local artifact only. Do not submit a load from this pillar skill.
5. For reading existing setup data, use the task-level setup export workflow below and validate any rule identity against its returned data. A Business Object name by itself does not provide an item-read route.

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader` using import mode `REST` and the confirmed BO for REST `returnRoutingRules`. Do not substitute a direct business-resource POST for the setup-data import.

Use this task metadata when invoking those skills:

- Offering: `Manufacturing and Supply Chain Materials Management`
- Functional area / Setup Object: `Service Logistics`
- Setup task name: `Return Routing Rules`
- Setup task code: `ORA_RCL_RETURN_ROUTING_RULES`


## Download Fusion Data Loader Sample

Use this workflow when a Fusion Data Loader sample is needed for the task's Business Object. The catalog's `REST` import mode remains a Data Loader classification.

1. Confirm that `returnRoutingRules` is the exact registered Data Loader Business Object in the selected environment.
2. Generate the default editable XLSX sample through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "returnRoutingRules" \
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
- `requested_operation`
- `rule_values`
- `existing_rule_key`

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `business_object_plan`
- `business_object_readiness`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `scm.manufacturing-and-supply-chain-materials-management.service-logistics` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Reference Evidence Persistence

Keep reference bundles, customer rows and actual source/export bytes in memory or private local ignored staging outside project/ and tracked files. Follow the task lookup evidence contract for safe paths, exact hashes, review and environment binding. Persist only redacted validation summaries in the declared project artifact locations. Missing ephemeral evidence after resume blocks handoff; a saved validation summary is not reference authority.
