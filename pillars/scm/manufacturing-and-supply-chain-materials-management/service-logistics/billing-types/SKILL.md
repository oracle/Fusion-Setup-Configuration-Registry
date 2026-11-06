---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.service-logistics.billing-types"
name: "Billing Types Setup Task Guidance"
description: "Provides Billing Types setup planning and task-specific validation for new mappings and EnabledFlag changes under Service Logistics."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Service Logistics"
functional_area_code: "ORA_RCL"
task_code: "ORA_RCL_BILLING_TYPES"
task_name: "Billing Types"
parent_skill_id: "scm.manufacturing-and-supply-chain-materials-management.service-logistics"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "REST"
businessObject: "billingTypes"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "hybrid"
owner_team: "SCM manufacturing and supply chain materials management pillar team"
version: "0.1.4"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "requested_operation"
  - "fusion_environment_context"
  - "current_billing_type_identity"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
  - "billing_type_operation_result"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
uses_core:
  - "core.data-loader"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/service-logistics/billing-types/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/service-logistics/billing-types/current/"
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
  - "Reads registered Billing Types metadata and records through core services."
  - "Delegates approved single-record POST creates and EnabledFlag PATCH updates to core.data-loader after operation-specific metadata and task-rule validation."
required_privileges:
  - "Access to the selected Fusion environment, Billing Types metadata and records, and the operation-specific Data Loader privileges; verify these before execution."
---

# Billing Types Setup Task Guidance

## Purpose

Provides task-specific setup planning and business validation for `Billing Types` under `Service Logistics`.

## Setup Task Skill Contract

- task_code: `ORA_RCL_BILLING_TYPES`
- task_name: `Billing Types`
- parent_skill_id: `scm.manufacturing-and-supply-chain-materials-management.service-logistics`
- pillar: `SCM`
- offering: `Manufacturing and Supply Chain Materials Management`
- functional_area: `Service Logistics`
- functional_area_code: `ORA_RCL`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `REST`
- businessObject: `billingTypes`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Billing Types` under `Service Logistics`.

## Setup Task Metadata

- Task name: `Billing Types`
- Task code: `ORA_RCL_BILLING_TYPES`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `REST`
- Business Object: `billingTypes`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Delegate imports to [core.data-loader](../../../../../core/data-loader/SKILL.md).

Use this task metadata when invoking those skills:

- Offering: `Manufacturing and Supply Chain Materials Management`
- Functional area / Setup Object: `Service Logistics`
- Setup task name: `Billing Types`
- Setup task code: `ORA_RCL_BILLING_TYPES`

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

Use the parent functional-area skill `scm.manufacturing-and-supply-chain-materials-management.service-logistics` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

Task preflight, failure handling and redaction requirements are defined in `ora-resource/ora_error_handling.md` and `ora-resource/ora_reference_lookups.md`; technical execution controls remain with the delegated core skills.

## Billing Types Business Rules

The business-object display name is **Billing Types** and the catalog discriminator is `billingTypes`. The configured discriminator does not establish live registration or operation support.

| Requested action | Task scope |
|---|---|
| Read | Current Billing Types records and their enabled state |
| POST | One new category and billing-type mapping with an explicitly selected EnabledFlag |
| PATCH | EnabledFlag on one uniquely identified existing mapping |
| DELETE | Unsupported by the current task contract |

### New Mapping

- Require explicit category, billing type and EnabledFlag inputs.
- Category and type must each resolve to one authoritative lookup value.
- An existing exact BillingTypeCode blocks creation across all categories, including disabled mappings. Creation does not imply an upsert.
- BillingTypeId is server-generated. Audit and display fields are not business inputs.

### EnabledFlag Change

- Resolve an exact BillingTypeCode or BillingTypeId to one current mapping. A display meaning must resolve uniquely before it can identify a target.
- Require an explicitly requested Boolean flag. If the current state already matches, no change is needed.
- Limit the change to EnabledFlag and preserve omitted business fields.
- Changes to an existing category/code, null clearing and bulk mutations are outside this task contract.
