---
skill_id: "scm.procurement.purchasing-foundation.manage-approved-supplier-list-statuses"
name: "Manage Approved Supplier List Statuses Setup Task Guidance"
description: "Provides setup guidance, explicit read-only fetching and search, and local import validation for Manage Approved Supplier List Statuses under Purchasing Foundation."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "Purchasing Foundation"
functional_area_code: "ORA_PO_PURCHASING_FOUNDATION"
task_code: "PO_MANAGE_APPROVED_SUPPLIER_LIST_STATUSES"
task_name: "Manage Approved Supplier List Statuses"
parent_skill_id: "scm.procurement.purchasing-foundation"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "REST"
businessObject: "purchasingApprovedSupplierListStatuses"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM procurement pillar team"
version: "0.1.6"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "operation_context"
  - "source_format"
  - "fetch_criteria"
  - "fusion_environment_context"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "validation_result"
  - "fetch_result"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/purchasing-foundation/manage-approved-supplier-list-statuses/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/purchasing-foundation/manage-approved-supplier-list-statuses/current/"
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
  - "Explicit fetch requests read Fusion through the shared REST client; it may refresh its private OAuth cache. Local import validation performs no external calls."
required_privileges:
  - "Only for explicit fetching, access to the selected Fusion environment and permission to read purchasingApprovedSupplierListStatuses. Local import validation needs no Fusion privilege."
---

# Manage Approved Supplier List Statuses Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, fetching, export, import, and validation guidance for `Manage Approved Supplier List Statuses` under `Purchasing Foundation`.

## Setup Task Skill Contract

- task_code: `PO_MANAGE_APPROVED_SUPPLIER_LIST_STATUSES`
- task_name: `Manage Approved Supplier List Statuses`
- parent_skill_id: `scm.procurement.purchasing-foundation`
- pillar: `SCM`
- offering: `Procurement`
- functional_area: `Purchasing Foundation`
- functional_area_code: `ORA_PO_PURCHASING_FOUNDATION`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `REST`
- businessObject: `purchasingApprovedSupplierListStatuses`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, fetching, exporting, importing, or validating setup data for `Manage Approved Supplier List Statuses` under `Purchasing Foundation`.

## Setup Task Metadata

- Task name: `Manage Approved Supplier List Statuses`
- Task code: `PO_MANAGE_APPROVED_SUPPLIER_LIST_STATUSES`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `REST`
- Business Object: `purchasingApprovedSupplierListStatuses`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Apply the local ASL Status resource contract below; it requires no external reference-data lookup.
4. Import setup task data with `core.data-loader` using purchasingApprovedSupplierListStatuses as the BusinessObject.

Use this task metadata when invoking those skills:

- Offering: `Procurement`
- Functional area / Setup Object: `Purchasing Foundation`
- Setup task name: `Manage Approved Supplier List Statuses`
- Setup task code: `PO_MANAGE_APPROVED_SUPPLIER_LIST_STATUSES`


## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business object.

1. Confirm that `purchasingApprovedSupplierListStatuses` is the exact registered Data Loader business object.
2. Generate the default editable XLSX sample through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "purchasingApprovedSupplierListStatuses" \
     --output-dir "<project-artifact-directory>"
   ```

3. Keep the generated workbooks together:
   - editable sample
   - attribute-details workbook
   - key-fields workbook
4. Review the generated headers and key fields before preparing source data. The operation uses read-only Fusion metadata and does not upload or import data.
5. Use the generated editable workbook as the starting point for the later Data Loader preparation and approval workflow.



## Query Live ASL Statuses

For an explicit get/list/fetch/search request, select read_fetch through
[operation routing and fetch-criteria validation](ora-resource/ora_input_validation.md#operation-routing).
Follow [fetch_asl_statuses](ora-resource/ora_reference_lookups.md) through
[the shared REST client](../../../../../core/fusion-api/rest-api-client/SKILL.md)
and return the [fetch result and diagnostics](ora-resource/ora_error_handling.md#fetch-results-and-failures).
Create/update/delete validation selects the separate local data_load branch.
Never use fetching as an import-validation prerequisite, identity resolver, or
mutation fallback; never select it merely because a status name or ID is supplied.

## Source Fidelity and InactiveDate

Use [input validation](ora-resource/ora_input_validation.md) for field contracts,
[defaulting](ora-resource/ora_defaulting_rules.md) for source preparation,
[design enforcement](ora-resource/ora_design_enforcement.md) for clearing consent,
and [handoff gates](ora-resource/ora_error_handling.md#representation-and-handoff-gates)
for representation blockers. Direct PATCH acceptance does not establish loader
clearing support. No REST fallback is permitted.

Prepare each compatible field-set/operation/date-intent group as a separate
single-source Data Loader validation cycle, retaining original row references. Do not
assume multiple ASL CSVs or duplicate business-object sections can be combined.
Each load requires its own final-preview-bound approval; no automatic submission.
Validate the actual captured headers/rows using an untouched capture and a
separate typed view. Corrections follow the error resource's cancellation and
fresh-validation recovery, never edits to the prepared artifact.

## Delete ASL Statuses

For an explicit delete request, follow [Delete Validation](ora-resource/ora_input_validation.md#delete-validation),
[delete source preparation](ora-resource/ora_defaulting_rules.md#delete-source-preparation),
and [delete handoff safeguards](ora-resource/ora_error_handling.md#delete-handoff).
Delegate execution to core.data-loader through the ASL resource contract below.

## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`
- `operation_context`: optional intent (create, update, delete, undetermined) and explicit rename/clearing request, separate from business attributes
- `source_format`: JSON, CSV, or XLSX provenance for date-cell presence handling
- `fetch_criteria`: explicit fetch mode and optional attribute filters
- `fusion_environment_context`: selected environment for explicit reads

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `validation_result`
- `fetch_result`: records, criteria, completeness, and read diagnostics
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `scm.procurement.purchasing-foundation` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.


## Boolean Input Preparation

Use [scripts/normalize_booleans.py](scripts/normalize_booleans.py) according to
[permitted normalization](ora-resource/ora_defaulting_rules.md#permitted-boolean-normalization).
`normalize_record` returns independent raw_record, typed record, changes, and
issues; helper success is distinct from complete ASL validation. Before archive
preparation, use `prepare_loader_record` and block preparation on helper issues.
Use the declared loader source writer; do not invent a JSON import route.

```bash
python3 pillars/scm/procurement/purchasing-foundation/manage-approved-supplier-list-statuses/scripts/normalize_booleans.py --mode normalize --dry-run
```

During artifact validation, derive business records from captured headers/rows,
excluding declared controls, and call `verify_captured_record`. Preserve the
capture and use its separate validation view; follow error handling for needed
corrections. Preparation evidence accompanies normal task-rule review and does
not authorize submission.

Natural-language labels such as “description” may identify StatusDescription
while preparing a request; literal business attribute names follow the exact
input allowlist, with no aliases.

## ASL Status Resource Contract

Read [the registry](ora-resource/ora_rule_registry.json), then its source anchors:
[input validation](ora-resource/ora_input_validation.md),
[preservation rules](ora-resource/ora_defaulting_rules.md),
[design enforcement](ora-resource/ora_design_enforcement.md), and
[error handling and handoff](ora-resource/ora_error_handling.md).
Delegate import preparation, Task Hook validation, preview, approval, and submission
to [core Data Loader](../../../../../core/data-loader/SKILL.md).
Apply the ASL resource rules to the final prepared artifact using the
[captured-source contract](ora-resource/ora_input_validation.md#record-and-captured-source-validation)
and [prepared artifact gates](ora-resource/ora_error_handling.md#prepared-artifact-gate).

Preflight the exact task, complete graph, source integrity, and input fidelity.
Start at ASL.CLASSIFY_OPERATION and follow only the selected branch. For
create/update/delete preparation or Data Loader validation, select data_load;
start the existing local rules at ASL.NORMALIZE_INPUT and stop at ASL.READY or
ASL.RETURN_ISSUES. That branch performs no REST calls, authentication, metadata
retrieval, or existence checks. The explicit read_fetch branch alone can reach
ASL.FETCH_STATUSES. Sample generation and setup export remain separate requested
core/shared workflows, never task-validation prerequisites.

Normalize only the three declared boolean attributes with the task-local helper before strict field validation. Retain raw input and conversion evidence; reject unsupported flag values without coercion. Accept only the exact business attributes declared by input validation.
Description is rejected as unknown. Intent affects required fields but never
selects a REST action. A supplied valid StatusId supports partial update
validation; record existence remains Data Loader's responsibility.

Return a machine-readable validation_result conforming to schemas/validation-result.schema.json: status is passed, warning, or failed; findings contain severity and message plus optional artifact and recommended_action. Put row indexes, field names, issue codes, and sanitized evidence in findings messages; do not add schema-unknown keys. Keep the task terminal and completed path in the separate task-rule validation result. Local graph success is READY_FOR_DATALOADER_REVIEW;
it does not establish Fusion acceptance. Batch failure blocks approval and retains
all per-row results. Use core project services and the manifest workspace policy
for durable validation evidence, skill runs, and token records.

Local data_load preparation needs no Fusion privilege and creates no Fusion side effects.
It performs a finite pass over captured rows and does not poll or retry. Stop on
interruption or graph failure and rerun against corrected, freshly captured input.
Data Loader owns environment identity, live BO registration/metadata, privileges,
source validation, operation selection, preview, approval, submission, and status
handling. Do not call REST directly if its contract cannot handle the request.
For failures load the task-local error guidance: correct local input before
retrying; never automatically replay a write; delegate timeout/status recovery to
Data Loader. Redact credentials and sensitive payloads from diagnostics.

Required human reviewers are the Procurement Pillar Development Lead or SME and
an FSCR A-Team/core reviewer. Package readiness does not replace merge approval.
