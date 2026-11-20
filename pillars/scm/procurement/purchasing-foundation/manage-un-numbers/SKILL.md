---
skill_id: "scm.procurement.purchasing-foundation.manage-un-numbers"
name: "Manage UN Numbers Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage UN Numbers under the Purchasing Foundation functional area."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "Purchasing Foundation"
functional_area_code: "ORA_PO_PURCHASING_FOUNDATION"
task_code: "PO_MANAGE_UN_NUMBERS"
task_name: "Manage UN Numbers"
parent_skill_id: "scm.procurement.purchasing-foundation"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "REST"
businessObject: "purchasingUNNumbers"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM procurement pillar team"
version: "0.2.3"
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
  - "core.fusion-api.rest-api-client"
  - "core.auth.fusion-oauth-authentication"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/purchasing-foundation/manage-un-numbers/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/purchasing-foundation/manage-un-numbers/current/"
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
  - "Conditionally reads Hazard Class records through the shared authenticated Fusion REST client during preparation and captured-record validation."
required_privileges:
  - "Read access to purchasingHazardClasses in the selected environment when an association lookup is required; Data Loader separately checks write privileges."
---

# Manage UN Numbers Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage UN Numbers` under `Purchasing Foundation`.

## Setup Task Skill Contract

- task_code: `PO_MANAGE_UN_NUMBERS`
- task_name: `Manage UN Numbers`
- parent_skill_id: `scm.procurement.purchasing-foundation`
- pillar: `SCM`
- offering: `Procurement`
- functional_area: `Purchasing Foundation`
- functional_area_code: `ORA_PO_PURCHASING_FOUNDATION`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `REST`
- businessObject: `purchasingUNNumbers`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage UN Numbers` under `Purchasing Foundation`.

## Setup Task Metadata

- Task name: `Manage UN Numbers`
- Task code: `PO_MANAGE_UN_NUMBERS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `REST`
- Business Object: `purchasingUNNumbers`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Resolve or verify Hazard Class associations using the task reference lookup before loader archive preparation; shared reference validation remains available for separately scoped work.
4. Import setup task data with `core.data-loader` using purchasingUNNumbers as the BusinessObject.

Use this task metadata when invoking those skills:

- Offering: `Procurement`
- Functional area / Setup Object: `Purchasing Foundation`
- Setup task name: `Manage UN Numbers`
- Setup task code: `PO_MANAGE_UN_NUMBERS`


## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business object.

1. Confirm that `purchasingUNNumbers` is the exact registered Data Loader business object.
2. Generate the default editable XLSX sample through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "purchasingUNNumbers" \
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

Use the parent functional-area skill `scm.procurement.purchasing-foundation` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.


## UN Number Resource Contract

Use the same name/code business-field rules for create and update. UNNumberId
retains unchecked pass-through. Non-null HazardClassId must pass input shape
checks and a read-only existence lookup. Accept HazardClass (not HazardClassName
or HazardClassCode) as the exact display-name preparation input. Description
is required and nonblank for explicit create intent or an explicit prepared
RestAction=POST. It remains optional for update and neutral apply, but non-null
when supplied. Its maximum length is 240 characters in every case. Generic
apply/upsert POST transport alone does not establish explicit create intent.
Preserve scoped intent and its source in workflow context through captured-source
validation; do not add intent to business data or infer it from IDs. Delete requires explicit
DELETE and only a non-null, nonblank UNNumberId; reject association inputs.

Route imports through `core.data-loader` using this task's registered Business
Object and exact task context. Data Loader's Task Hook resolves the
[compiled task registry](ora-resource/ora_rule_registry.json) and supplies the
execution guide and applicable rule resources after its immutable archive
preparation workflow. Follow that guide and the declared graph transitions,
evaluate records from that prepared archive, and return the required rule results. Data
Loader owns preview, approval, submission, and verification.

If the registry or its source rules are missing, inconsistent, or incomplete,
stop and report an authoring issue. Registry compilation and development
planning belong to authoring and verification, not runtime preparation. Use
the published registry and read the owning resource sections for every reached
node:

1. [Input validation](ora-resource/ora_input_validation.md).
2. [Hazard Class resolution](ora-resource/ora_reference_lookups.md) and
   [conditional dependency](ora-resource/ora_dependency_readiness.md).
3. [Defaulting and preservation](ora-resource/ora_defaulting_rules.md).
4. [Design enforcement](ora-resource/ora_design_enforcement.md).
5. [Error handling and handoff](ora-resource/ora_error_handling.md).

## Hazard Class Preparation and Capture Boundary

1. Validate original input and scoped operation intent, including conditional
   Description requiredness, before any lookup. A supplied name must
   be a nonblank string up to 40 characters. A supplied non-null ID must be an
   integer or ASCII decimal string within 18-digit precision. Reject name plus
   explicit null ID. No association input or null ID without a name remains
   optional. Inactive-date eligibility is left to Fusion.
2. For applicable create/update rows, select the target environment, confirm
   authenticated core REST access and read privileges, then run resolve_hazard_class.
   Accept validated integer or ASCII decimal-string response IDs under the resolver contract; compare IDs losslessly. Exact case-sensitive name matching and supplied ID/name agreement are required;
   complete pagination before deciding uniqueness. Valid delete rows bypass reads.
3. Preserve original inputs and lookup provenance in preparation context. Build
   separate loader-ready data: populate an omitted HazardClassId from the unique
   result, preserve a supplied verified ID's representation, and keep HazardClass
   as context rather than a writable attribute. Preserve all other values except
   the existing create/update empty InactiveDate-cell omission. Do not overwrite
   originals or persist real payloads/IDs in reusable repository guidance.
4. Start Data Loader only with normalized source records. During Task Hook
   validation, read the immutable prepared artifact and reverify any non-null HazardClassId.
   Never use ruleResults/changes to patch captured data. If a correction is needed,
   block, cancel the pending validation cycle, prepare corrected input and validate afresh.
5. Preserve explicit DELETE and existing create/update controls. Data Loader owns
   preview, approval and writes; this graph authorizes only its declared reads.

The successful path is UN.VALIDATE_INPUT -> UN.RESOLVE_HAZARD_CLASS ->
UN.PRESERVE_VALUES -> UN.CHECK_DESIGN -> UN.HANDOFF -> UN.READY. The resolver
returns not_applicable without a read when no association is supplied or on
valid deletes. Failed lookups and validation errors lead to UN.HANDLE_ISSUES ->
UN.RETURN_ISSUES. READY_FOR_DATALOADER_REVIEW never implies import success.

Data Loader retains registered-object metadata, operation-specific requiredness,
ID acceptance, identity/reference checks, serialization, preview, approval,
submission, and server-error handling for purchasingUNNumbers in REST mode.
Its own preflights remain authoritative. Live registration, operation selection,
and server behavior are unverified; do not invent an alternative execution path
when its contract cannot process the source. The sample download workflow above
is a separate read-only metadata operation, not part of local field validation.

Field-rule review and graph checks provide different evidence. Graph checks
verify structure and failure isolation; they do not implement or execute a
standalone field validator.


## Delete Preparation

For an explicitly requested deletion, prepare the loader operation as
RestAction=DELETE with UNNumberId as the only business field. No name, code,
description, date, or hazard-class field is required or accepted for deletion.
Presence-only checking is intentional: ID type, format, range, and existence
remain Data Loader responsibilities. An ID alone never implies delete.

Oracle documents DELETE
/fscmRestApi/resources/11.13.18.05/purchasingUNNumbers/{UNNumberId} in the
[UN Numbers DELETE API](https://docs.oracle.com/en/cloud/saas/procurement/26d/fapra/op-purchasingunnumbers-unnumberid-delete.html).
This is reference documentation; the selected executor remains core.data-loader.

To request an editable delete sample through the existing metadata workflow:

```bash
python3 core/data-loader/scripts/generate_sample_dat.py \
  "purchasingUNNumbers" --operation delete \
  --output-dir "<project-artifact-directory>"
```

Keep the generated workbook set together and validate the live registered-object
contract. A generated sample or local readiness does not authorize submission.
Use Data Loader's immutable-archive preview and approval; unsupported deletion
metadata blocks execution. Do not bypass it with direct REST or automatically
retry a failed or uncertain deletion.
