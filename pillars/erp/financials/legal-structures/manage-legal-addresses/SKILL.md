---
skill_id: "erp.financials.legal-structures.manage-legal-addresses"
name: "Manage Legal Addresses Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Legal Addresses under the Legal Structures functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Legal Structures"
functional_area_code: "ORA_ASK_LEGAL_STRUCTURES"
task_code: "XLE_MANAGE_LEGAL_ADDRESSES"
task_name: "Manage Legal Addresses"
parent_skill_id: "erp.financials.legal-structures"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.2.0"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/legal-structures/manage-legal-addresses/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/legal-structures/manage-legal-addresses/current/"
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

# Manage Legal Addresses Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Legal Addresses` under `Legal Structures`.

## Setup Task Skill Contract

- task_code: `XLE_MANAGE_LEGAL_ADDRESSES`
- task_name: `Manage Legal Addresses`
- parent_skill_id: `erp.financials.legal-structures`
- pillar: `ERP`
- offering: `Financials`
- functional_area: `Legal Structures`
- functional_area_code: `ORA_ASK_LEGAL_STRUCTURES`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Legal Addresses` under `Legal Structures`.

## Setup Task Metadata

- Task name: `Manage Legal Addresses`
- Task code: `XLE_MANAGE_LEGAL_ADDRESSES`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Load the task-local `ora-resource/ora_rule_registry.json` and run its referenced input, lookup, dependency, defaulting, design, error-handling, and final-package-readiness checks. The ora-resource graph validates the candidate; it does not create a Fusion mutation.
5. Prepare the FSM archive locally using the contract below.
6. Hand the exact final archive to `core.data-loader` only after the local workflow returns `READY_FOR_DATA_LOADER_PREVIEW`.

Use this task metadata when invoking those skills:

- Offering: `Financials`
- Functional area / Setup Object: `Legal Structures`
- Setup task name: `Manage Legal Addresses`
- Setup task code: `XLE_MANAGE_LEGAL_ADDRESSES`

### Local-Only FSM Package Preparation

This assisted workflow prepares a package locally and stops before upload or any Fusion mutation.

1. Require a fresh, same-target, same-release, successful same-task FSM export as the immutable baseline. Bind the exact environment and task identity, current `ASM_SETUP_CSV_METADATA.xml`, exact CSV member hierarchy, exact header spelling and order, and the exported encoding.
2. Re-run the complete task ora-resource graph against the reviewed inputs and baseline. Fail closed with a task-specific package-contract gap if any source, mapping, value, member hierarchy, header, encoding, carrier, or system-blank rule is missing or ambiguous; do not invent a package contract.
3. Build a new-rows-only upload archive; the immutable export is reference evidence for metadata, headers, and duplicate checks, never the upload payload. Preserve `ASM_SETUP_CSV_METADATA.xml` byte-for-byte and retain the exact exported CSV member hierarchy, header bytes/order, and encoding. In `XLE_LE_LEGAL_ADDRESS.csv`, include only the reviewed new addresses that passed complete-scope duplicate checks. Keep every companion CSV header-only with zero data rows. Exclude every existing baseline row, including existing addresses, legal entities, establishments, registrations, and functions. Omitting rows from this create package does not request deletion in Fusion. Do not submit an unfiltered export or append new rows to a populated baseline for upload.
4. Every new address row must have nonblank `LeFormattedAddress`, `CreatedByModule` set to `XLE_CREATE_LE`, and a new collision-checked `OrigSystemReference`. Apply the deterministic formatting contract in `ora-resource/ora_defaulting_rules.md`: replace every comma in a supplied complete single-line address with `/`, preserving the other characters and spaces. For component-only input, derive a nonblank value from the reviewed components and resolved country layout; block if the source or mapping is ambiguous. Validate the final CSV value, not just the input or preview.
5. Do not copy physical IDs, audit fields, object-version fields, ESS fields, or service-owned values from the baseline or another row. Copy a value only when the task resources explicitly authorize it as a carrier. Keep Fusion-generated `FormattedAddress` and `FormattedMultilineAddress` blank; this blank treatment never applies to `LeFormattedAddress`.
6. Reparse every CSV in the final ZIP. Require its address data-row count and identities to equal exactly the reviewed unique new candidate set, all `LeFormattedAddress` values to be populated and normalized, existing data rows included to equal zero, and every companion data-row count to equal zero. Require at least one new row; if all requested addresses already exist, return Existing Match without submitting an empty import. Block a mismatch before Data Loader preview. Produce the immutable archive, SHA-256, per-member baseline/upload row counts, header/metadata fingerprints, and a semantic diff explicitly showing excluded baseline rows and newly authored rows. Record a sanitized package-preparation receipt.
7. Any source, mapping, value, package byte, member inventory, or hash change invalidates this preview state and requires the full validation and package-preparation workflow to run again.
8. On success, return `READY_FOR_DATA_LOADER_PREVIEW`. Do not claim `READY_FOR_IMPORT` or approval. Stop before upload or mutation and hand the exact immutable archive to `core.data-loader`, which owns Task Hook validation, preview, explicit approval, archive-hash verification, upload, and initiation. A standalone new-rows-only package is the normal contract for this task, not an exception requiring a baseline-preservation waiver.

### Outcome Reporting and Verification

Keep the central Data Loader approval, initiation, monitoring, and report contracts unchanged. Accepted initiation means submitted, not created; return its initiation report without automatic status polling. When the user requests status, results, errors, or verification, use the central monitoring workflow and apply `ora-resource/ora_error_handling.md` before making a task-level success or failure claim.

Inspect the current, correctly correlated FSM ProcessLog, underlying process completion state, and relevant object counters alongside Data Loader status/errors. A Data Loader error with a still-running FSM process is a status discrepancy, not proof that address creation failed. Missing or incomplete logs leave the task outcome unverified. Confirm exact new-row persistence through a fresh same-target export before claiming the address or a particular field value is present in Fusion. Distinguish the authored `LeFormattedAddress` from the returned value and Fusion-generated display fields; do not promise the submitted slash string will be displayed verbatim.


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

Use the parent functional-area skill `erp.financials.legal-structures` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
