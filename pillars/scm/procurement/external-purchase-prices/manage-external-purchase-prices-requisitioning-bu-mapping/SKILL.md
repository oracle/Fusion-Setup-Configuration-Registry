---
skill_id: "scm.procurement.external-purchase-prices.manage-external-purchase-prices-requisitioning-bu-mapping"
name: "Manage External Purchase Prices Requisitioning BU Mapping Setup Task Guidance"
description: "Retrieves External Purchase Prices BU Mappings through direct read-only REST and routes parent/child maintenance exclusively through Data Loader."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "External Purchase Prices"
functional_area_code: "ORA_EXTERNAL_PURCHASE_PRICES"
task_code: "ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_REQBU_MAPPING"
task_name: "Manage External Purchase Prices Requisitioning BU Mapping"
parent_skill_id: "scm.procurement.external-purchase-prices"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "REST"
businessObject: "externalPurchasePricesBusinessUnits"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM procurement pillar team"
version: "0.2.2"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "mapping_query"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "mapping_read_result"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/external-purchase-prices/manage-external-purchase-prices-requisitioning-bu-mapping/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/external-purchase-prices/manage-external-purchase-prices-requisitioning-bu-mapping/current/"
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
  - "Delegates read-only Fusion metadata and mapping lookups to the declared core services after the selected workflow's preflight."
  - "Creates local sample workbooks and persists sanitized planning, validation, skill-run, and token-usage artifacts through the declared core/shared services."
  - "Delegates requested exports and imports to their declared workflows; uploads, load initiation, and Fusion mutations require core.data-loader's exact-artifact approval and are never performed directly by this planning skill."
required_privileges:
  - "Offline planning requires no Fusion privilege; local artifact generation requires write access to the selected safe output directory."
  - "Live metadata or mapping reads require the selected environment's read privileges and confirmed visibility across all BUs relevant to the requested lookup."
  - "Mapping maintenance requires Purchase Pricing Manager-equivalent privileges; export/import permissions and mutation approval are checked by the selected shared/core workflow."
---

# Manage External Purchase Prices Requisitioning BU Mapping Setup Task Guidance

## Purpose

Provides task-specific record retrieval, setup planning, routing, export, import, and validation guidance for `Manage External Purchase Prices Requisitioning BU Mapping` under `External Purchase Prices`.

## Setup Task Skill Contract

- task_code: `ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_REQBU_MAPPING`
- task_name: `Manage External Purchase Prices Requisitioning BU Mapping`
- parent_skill_id: `scm.procurement.external-purchase-prices`
- pillar: `SCM`
- offering: `Procurement`
- functional_area: `External Purchase Prices`
- functional_area_code: `ORA_EXTERNAL_PURCHASE_PRICES`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `REST`
- businessObject: `externalPurchasePricesBusinessUnits`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when retrieving mappings, planning, sequencing, exporting, importing, or validating setup data for `Manage External Purchase Prices Requisitioning BU Mapping` under `External Purchase Prices`.

For task validation, use the [source anchors](ora-resource/ora_design_enforcement.md#source-anchors)
and [versioned read-only lookup contract](ora-resource/ora_reference_lookups.md#lookup-contract-v1)
with the registered task rules. A reference alone is not execution authority;
select the operation route below and complete its preflight before a Fusion call.

## Operation Routing

| Requested Outcome | Execution Route | Completion |
|---|---|---|
| Retrieve current parent and child records (GET) | This skill's read-only workflow below, using core.fusion-api.rest-api-client directly | Return current details or confirmed not-found; no Data Loader handoff |
| Create, update or delete a parent or child (POST, PATCH, DELETE) | core.data-loader, including its task validation and exact-artifact approval | Only the loader may upload, initiate or execute the mutation |
| Read existing state during mutation validation or authorized post-load verification | Direct GET through core.fusion-api.rest-api-client under the selected workflow's preflight | Return evidence to that workflow; a GET never becomes a write |
| Generate a loader template, check a loader job, or export setup data | The existing explicitly requested template, loader-status or shared export workflow | Do not classify these as a request to retrieve mapping records |

The core.data-loader dependency is conditional on loader work, not record GET.
Never route a pure record read through core.data-loader, its Task Hook or its
task-validator helper. Never use the direct REST client for POST, PATCH or DELETE
in this task, even though the shared client supports those methods.

## Read-Only Mapping Workflow

1. Select the implementation project and environment through the active project
   workflow. Accept `mapping_query` from the user's read request: exact
   `SourceOrganization` and `ProcurementBUName` or `ProcurementBUId`, plus any
   supplied parent/child IDs or child filters. A loader XLSX, Run Book mutation
   step, REST action column and mutation approval are not prerequisites for GET.
   Missing intent or keys require clarification; never infer a create operation.
2. Confirm exact task/catalog and environment identity, read privileges and
   visibility for the requested parent and relevant children, safe evidence
   destinations, and a finite read budget before any external call. Pure reads
   do not require Procurement/BPA maintenance readiness or write privileges.
3. Load this task's `ora-resource/ora_rule_registry.json` and select the
   single entry matching its exact task code and name. Require readiness
   `ready` with no blocking reasons. Check that the start node, transition
   targets, prerequisites, and source file/heading for every reachable node
   exist and agree with the task-local rules. Stop on a missing, ambiguous,
   incomplete, or inconsistent graph; request a maintainer correction rather
   than repairing it during a read. Do not use the loader's task-rule helper.
   The read path is
   `EPPBU.VALIDATE_INPUT` → `EPPBU.RESOLVE_REFERENCES` →
   `EPPBU.RETURN_READ_RESULT`. Classify and disclose failures through
   `EPPBU.HANDLE_ERROR` → `EPPBU.RETURN_ISSUES`.
4. Read the [Core REST API Client](../../../../../core/fusion-api/rest-api-client/SKILL.md)
   and follow the [lookup contract](ora-resource/ora_reference_lookups.md#lookup-contract-v1).
   That client owns authentication and GET transport. Resolve the exact parent
   and all requested child details with complete pagination; do not run the
   active-membership conflict scan solely for a record read.
5. Select `read_complete` only for a pure read with complete lookup evidence,
   including a confirmed not-found result. Return requested current values
   without defaults or modification. Partial, ambiguous or inaccessible results
   are issues, never not-found. Keep record values transient; persist only the
   sanitized receipt, skill-run and token-usage evidence under the project policy.
   Do not generate a sample, stage an artifact, request mutation approval, upload,
   initialize a load or fall back to Data Loader if GET fails.

For write validation, successful reference resolution selects `resolved`, not
`read_complete`, and continues through dependency, defaulting and design checks
to `EPPBU.READY_FOR_DATA_LOADER_REST`. Mixed read/write requests retain the
loader route for every requested mutation; lookup success never authorizes one.

## Setup Task Metadata

- Task name: `Manage External Purchase Prices Requisitioning BU Mapping`
- Task code: `ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_REQBU_MAPPING`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `REST`
- Business Object: `externalPurchasePricesBusinessUnits`

Use the technical BO name `externalPurchasePricesBusinessUnits` for Data Loader
metadata lookup, sample generation and import handoff. `External Purchase Prices
BU Mappings` is the display name only; do not pass it as `businessObject` or as
the Data Loader business-object argument.

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task. For explicitly requested setup export, import or loader-artifact validation (not record GET), use the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader` using externalPurchasePricesBusinessUnits as the Business Object.

Use this task metadata when invoking those skills:

- Offering: `Procurement`
- Functional area / Setup Object: `External Purchase Prices`
- Setup task name: `Manage External Purchase Prices Requisitioning BU Mapping`
- Setup task code: `ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_REQBU_MAPPING`


## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business object.

1. Confirm that `externalPurchasePricesBusinessUnits` is the exact registered Data Loader business object.
2. Generate the default editable XLSX sample through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "externalPurchasePricesBusinessUnits" \
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
- `mapping_query`: read-only request keys; required for record retrieval, not a loader artifact

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `mapping_read_result`: requested current parent/child details or confirmed not-found; read-only route only
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `scm.procurement.external-purchase-prices` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
