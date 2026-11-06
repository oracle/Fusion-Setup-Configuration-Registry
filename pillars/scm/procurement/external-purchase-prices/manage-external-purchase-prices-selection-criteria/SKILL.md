---
skill_id: "scm.procurement.external-purchase-prices.manage-external-purchase-prices-selection-criteria"
name: "Manage External Purchase Prices Selection Criteria Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage External Purchase Prices Selection Criteria under the External Purchase Prices functional area."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "External Purchase Prices"
functional_area_code: "ORA_EXTERNAL_PURCHASE_PRICES"
task_code: "ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_SELECTION_CRITERIA"
task_name: "Manage External Purchase Prices Selection Criteria"
parent_skill_id: "scm.procurement.external-purchase-prices"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "REST"
businessObject: "externalPurchasePricesSelectionCriteria"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM procurement pillar team"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/external-purchase-prices/manage-external-purchase-prices-selection-criteria/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/external-purchase-prices/manage-external-purchase-prices-selection-criteria/current/"
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
  - "An explicitly selected task-local review may issue read-only Fusion GET requests and persist sanitized review evidence in the project workspace."
required_privileges:
  - "View External Purchase Prices Selection Criteria privilege (or an equivalent grant) and access to the intended requisitioning business unit for a live review."
---

# Manage External Purchase Prices Selection Criteria Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage External Purchase Prices Selection Criteria` under `External Purchase Prices`.

## Setup Task Skill Contract

- task_code: `ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_SELECTION_CRITERIA`
- task_name: `Manage External Purchase Prices Selection Criteria`
- parent_skill_id: `scm.procurement.external-purchase-prices`
- pillar: `SCM`
- offering: `Procurement`
- functional_area: `External Purchase Prices`
- functional_area_code: `ORA_EXTERNAL_PURCHASE_PRICES`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `REST`
- businessObject: `externalPurchasePricesSelectionCriteria`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage External Purchase Prices Selection Criteria` under `External Purchase Prices`.

## Setup Task Metadata

- Task name: `Manage External Purchase Prices Selection Criteria`
- Task code: `ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_SELECTION_CRITERIA`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `REST`
- Business Object: `externalPurchasePricesSelectionCriteria`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Apply the documented task-local selection rules before `shared.validation.setup-data-validator`; run the read-only review route below when an existing criterion must be verified.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader` using `externalPurchasePricesSelectionCriteria` as the BusinessObject.

Use this task metadata when invoking those skills:

- Offering: `Procurement`
- Functional area / Setup Object: `External Purchase Prices`
- Setup task name: `Manage External Purchase Prices Selection Criteria`
- Setup task code: `ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_SELECTION_CRITERIA`

## Task-Local Selection Criteria Review

Use this read-only route when the selected project workflow calls for verification of an existing selection criterion. Before any Fusion GET, confirm the project and target environment and a positive decimal `SelectionId` or an exact requisitioning BU name (or both for a consistency check). The manifest names the required view privilege, but this route does not independently inspect role grants or BU-access assignments; the declared GET supplies the access outcome. When both identities are supplied, read by `SelectionId` and require the returned BU name to match exactly. For an offline plan or when the project workflow has not selected an external read, review only supplied planning evidence and record the live lookup as pending. A resource file or endpoint reference alone does not authorize a live call.

1. Load this task `SKILL.md` and `ora-resource/ora_rule_registry.json`. Select the single entry matching this exact task code and name; require readiness `ready` with no blocking reasons. Verify that its start node, transition targets, prerequisites, and source file/heading for every reachable node exist and agree with the task-local rules. Stop on a missing, ambiguous, incomplete, or inconsistent graph and request a maintainer correction; do not repair it at runtime. Begin at `EPPSEL.VALIDATE_INPUT` and follow only declared outcomes after their prerequisites succeed, ending at the selected terminal node. The registry does not authorize an external call by itself.
2. Load the source file and heading for each reachable node. Apply input, dependency, defaulting, design, and error rules from this task's `ora-resource/` files. The only live lookup in that plan is the documented GET in `ora_reference_lookups.md`, executed through `core.fusion-api.rest-api-client`; names with apostrophes, semicolons, or backslashes use its documented unfiltered, paginated collection route. Do not substitute direct REST calls or a different integration.
3. For a live collection read, require one exact match after complete pagination; for an item read, require the returned ID and any supplied BU name to match. Stop on ambiguous identity, a GET authentication or authorization failure, incomplete results, or a Fusion error. Persist only sanitized task identity, environment, validated facts, outcome, evidence references, and diagnostics under the selected `project/{project_id}` workspace and record the skill run and token usage. Never persist credentials, tokens, raw response bodies, or protected identifiers.
4. After a completed live read, return the criterion or state that no exact criterion was visible in the completed collection read, with the documented source-type, party-type, and lowest-price precedence, plus the validation outcome and one safe next action. Do not claim that a zero-result read independently proves BU access or global absence. For an offline plan, state that no current criterion was verified. This route does not create, update, delete, export, or import setup data. Use the declared shared export/validation and `core.data-loader` routes for those separate actions and their own gates.

The task-local review has no write approval gate because it makes no Fusion mutation. Any later import or other mutation follows its selected workflow and approval contract.

## Oracle Sources

- [Oracle Procurement 26C: Selection Criteria for External Purchase Prices](https://docs.oracle.com/en/cloud/saas/procurement/26c/oaprc/selection-criteria-for-external-purchase-prices.html) — BU scope, choices, precedence, and latest-line tie break.
- [Oracle Procurement 26D: REST endpoints](https://docs.oracle.com/en/cloud/saas/procurement/26d/fapra/rest-endpoints.html) — supported selection-criteria collection and item GET paths.
- [Oracle Procurement security reference: Purchase Pricing Manager](https://docs.oracle.com/en/cloud/saas/procurement/26b/oapcm/Purchase_Pricing_Manager_job_roles.html) — names the view privilege; this read route does not independently inspect grant assignments.


## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business object.

1. Confirm that `externalPurchasePricesSelectionCriteria` is the exact registered Data Loader business object.
2. Generate the default editable XLSX sample through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "externalPurchasePricesSelectionCriteria" \
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

Use the parent functional-area skill `scm.procurement.external-purchase-prices` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
