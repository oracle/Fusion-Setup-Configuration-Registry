---
skill_id: "scm.procurement.purchasing-foundation.manage-hazard-classes"
name: "Manage Hazard Classes Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Hazard Classes under the Purchasing Foundation functional area."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "Purchasing Foundation"
functional_area_code: "ORA_PO_PURCHASING_FOUNDATION"
task_code: "PO_MANAGE_HAZARD_CLASSES"
task_name: "Manage Hazard Classes"
parent_skill_id: "scm.procurement.purchasing-foundation"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "REST"
businessObject: "purchasingHazardClasses"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM procurement pillar team"
version: "0.3.1"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/purchasing-foundation/manage-hazard-classes/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/purchasing-foundation/manage-hazard-classes/current/"
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
required_privileges:
  - "Manage Purchasing Hazard Class (PO_MANAGE_PURCHASING_HAZARD_CLASS_PRIV) for the setup page; the selected Data Loader route must separately validate its access; local field validation requires no Fusion access."
---

# Manage Hazard Classes Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Hazard Classes` under `Purchasing Foundation`.

## Setup Task Skill Contract

- task_code: `PO_MANAGE_HAZARD_CLASSES`
- task_name: `Manage Hazard Classes`
- parent_skill_id: `scm.procurement.purchasing-foundation`
- pillar: `SCM`
- offering: `Procurement`
- functional_area: `Purchasing Foundation`
- functional_area_code: `ORA_PO_PURCHASING_FOUNDATION`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `REST`
- businessObject: `purchasingHazardClasses`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Hazard Classes` under `Purchasing Foundation`.

## Setup Task Metadata

- Task name: `Manage Hazard Classes`
- Task code: `PO_MANAGE_HAZARD_CLASSES`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `REST`
- Business Object: `purchasingHazardClasses`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Use `shared.validation.reference-data-validator` only for separately scoped reference-data work; this task’s local validation requires no reference lookup.
4. Import setup task data with `core.data-loader` using purchasingHazardClasses as the BusinessObject.

Use this task metadata when invoking those skills:

- Offering: `Procurement`
- Functional area / Setup Object: `Purchasing Foundation`
- Setup task name: `Manage Hazard Classes`
- Setup task code: `PO_MANAGE_HAZARD_CLASSES`


## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business object.

1. Confirm that `purchasingHazardClasses` is the exact registered Data Loader business object.
2. Generate the default editable XLSX sample through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "purchasingHazardClasses" \
     --output-dir "<project-artifact-directory>"
   ```

3. Keep the generated workbooks together:
   - editable sample
   - attribute-details workbook
   - key-fields workbook
4. Review the generated headers and key fields before preparing source data. The operation uses read-only Fusion metadata and does not upload or import data.
5. Use the generated editable workbook as the starting point for the later Data Loader preparation and approval workflow.



## Branch Data Loader Contract

This branch uses Data Loader's persisted immutable ZIP and Task Hook workflow.
It does not expose a captured-record session API. In this task, "captured"
records mean a read-only evaluation view derived from the exact prepared
artifact, after core mapping and conversion. Read DAT members from that ZIP,
honor their escaping and record directives, and keep business fields separate
from RestAction/control metadata. Do not evaluate mutable original CSV/XLSX
files in place of the artifact or write a replacement serializer in the pillar.
If the artifact cannot be decoded losslessly, stop with a representation blocker.

Prepare all permitted task transformations before core conversion. Preserve
original row references and scoped intent separately, and compare the resulting
artifact with that approved preparation. Keep blanks distinct from omitted
columns. Split incompatible field sets before preparation; never drop a blank
cell from an already prepared record. Explicit null requires a verified loader
encoding and otherwise blocks preparation rather than becoming an empty string.

Use core.data-loader's Task Hook data-load route after its normal preflights.
Return ordered ruleResults for the prepared artifact; use the existing
build-data-load-preview with finalData.archiveSha256, then the core workflow's
approve-data-load-preview and verify-approved-data-load-archive gates. The core
workflow owns approval and submission. Rule-result changes are evidence only.
Corrections require fresh preparation, validation and approval envelopes. After
approval, submit the unchanged approved ZIP through core.data-loader; do not
reopen original sources, reconvert or rerun reference lookups for submission.

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

## Hazard Class Resource Contract

Reviewer: SCM Procurement Pillar Development Lead. Existing field-rule baseline:
Oracle 26D REST documentation. The approved operation-neutral plan defines local
validation and delegates record identity and operation handling to Data Loader.

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
2. [Defaulting rules](ora-resource/ora_defaulting_rules.md).
3. [Design enforcement](ora-resource/ora_design_enforcement.md).
4. [Error handling and Data Loader handoff](ora-resource/ora_error_handling.md).

The retained [reference lookup](ora-resource/ora_reference_lookups.md) and
[dependency readiness](ora-resource/ora_dependency_readiness.md) resources state
that this local graph requires neither lookups nor external dependencies.

Every row requires both `HazardClass` and `HazardClassCode`. Description and
InactiveDate are optional and checked only when supplied. An empty CSV/XLSX
InactiveDate cell means not provided: omit the date attribute for that record.
Explicit JSON null remains null; a supplied nonempty date must be YYYY-MM-DD. `HazardClassId` is
optional; preserve any supplied value exactly without validation or normalization.
ID validity and identity handling belong to Data Loader. Operation, environment,
and loader control fields remain separate workflow context; no create/update
input is required for this pillar validation.

The single path is input validation, value preservation, design checks, and
Data Loader handoff. It makes no REST calls and does not authenticate, resolve
IDs, compare existing records, or select POST/PATCH. Supplied name and code are
business data, never reinterpreted as lookup-only context. Omitted optional
fields stay omitted, including empty CSV/XLSX InactiveDate cells; explicit nulls
and all supplied IDs remain unchanged.
No business defaults or replacement identities are generated.

The graph ends with `READY_FOR_DATALOADER_REVIEW`, not import success. Offline
validation can reach this terminal without leaving record verification pending.
Data Loader still owns metadata, source validation, serialization, preview,
approval, submission, and verification for the registered business object
`purchasingHazardClasses` in REST mode. Its preflights and blockers remain
authoritative. Resource nodes do not set `RestAction` or execute writes.

Automatic POST/PATCH selection and invalid-ID handling are delegated under the
approved working assumption; this package does not verify their implementation
or server behavior. Do not invent a fallback if the downstream contract cannot
process the supplied source. Local readiness does not prove ID validity,
record existence, uniqueness, authorization, or server acceptance.

The setup-page privilege remains Manage Purchasing Hazard Class
(`PO_MANAGE_PURCHASING_HAZARD_CLASS_PRIV`); Data Loader validates its own access.
The separate sample-generation workflow above may use loader metadata reads;
it is not part of this local validation graph.
