---
skill_id: "cx.field-service.scheduling-and-dispatch.work-zones"
name: "Work Zones Setup Task Guidance"
description: "Provides task-specific setup guidance for Work Zones under the Scheduling and Dispatch functional area."
layer: "pillar"
pillar: "CX"
offering: "Field Service"
functional_area: "Scheduling and Dispatch"
functional_area_code: "ORA_FFS_FA_SCHEDULING_AND_DISPATCH"
task_code: "ORA_FFS_TS_WORK_ZONES"
task_name: "Work Zones"
parent_skill_id: "cx.field-service.scheduling-and-dispatch"
available_flag: "Y"
export_import_supported_flag: "UNKNOWN"
csv_export_import_supported_flag: "UNKNOWN"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "orchestration"
execution_mode: "hybrid"
owner_team: "CX field service pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "work_zones_workbook"
  - "execution_direction"
  - "setup_data_artifacts"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
uses_core:
  - "core.auth.fusion-oauth-authentication"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/field-service/scheduling-and-dispatch/work-zones/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/field-service/scheduling-and-dispatch/work-zones/current/"
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
  - "Performs approval-bound Work Zone POST creates or PUT replacements through the Field Service shared workflow."
required_privileges:
  - "Access to the selected Oracle Field Service environment and required OAuth scope"
  - "Environment-approved Work Zone metadata read access for preview and verification"
  - "Environment-approved Work Zone create or replace permission for the exact approved POST or PUT operation"
---

# Work Zones Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Work Zones` under `Scheduling and Dispatch`.

## Setup Task Skill Contract

- task_code: `ORA_FFS_TS_WORK_ZONES`
- task_name: `Work Zones`
- parent_skill_id: `cx.field-service.scheduling-and-dispatch`
- pillar: `CX`
- offering: `Field Service`
- functional_area: `Scheduling and Dispatch`
- functional_area_code: `ORA_FFS_FA_SCHEDULING_AND_DISPATCH`
- available_flag: `Y`
- export_import_supported_flag: `UNKNOWN`
- csv_export_import_supported_flag: `UNKNOWN`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Work Zones` under `Scheduling and Dispatch`.

## Authorization Preconditions

Before execution, require environment-owner evidence that the selected principal
has Work Zone create or replace permission for the exact approved operation.
Successful GET access and preview approval do not establish write authorization.
Stop when authorization is missing or uncertain. These are capability prerequisites,
not assumed Oracle role or privilege-code names. No write probe is permitted to
establish authorization. Keep the selected environment and Field Service OAuth
scope checks in the existing routed authentication and execution services.

## Setup Task Metadata

- Task name: `Work Zones`
- Task code: `ORA_FFS_TS_WORK_ZONES`
- Available: `Y`
- Export/import supported: `UNKNOWN`
- CSV export/import supported: `UNKNOWN`
- CSV export/import routing: `not supported`

## Execution Directions

- Default: `ora_rest_execution`. Use only the documented Work Zones REST contract through `scripts/run_work_zone.py`.
- Data Loader is not an execution direction for this task. CSV package import remains unsupported by the effective catalog.
- Do not fall back automatically between directions. Data Loader and other endpoint families are unsupported.

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `UNKNOWN`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

Do not route CSV export work to `shared.setup-export.task-level-export` or CSV import work to `core.data-loader` unless live Fusion metadata or Oracle guidance confirms support. Use `shared.validation.setup-data-validator` only when a setup data artifact is available for review. Use `shared.validation.reference-data-validator` when the task depends on cross-pillar reference data.


## Shared Field Service Orchestration

Start from `pillars/cx/field-service/SKILL.md`. The reusable lifecycle—route selection, current-state reads, immutable preview/checksum, approval binding, ordered write, redacted evidence, and GET verification—is owned only by `pillars/cx/field-service/scripts/task_orchestration.py`.

`scripts/task_adapter.py` owns Work Zones workbook mapping, Work Zone validation, OFSC Metadata paths, request payloads, and verification rules. `scripts/run_work_zone.py` is the only task entry point. Do not invoke the adapter or Core REST client directly.



## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `work_zones_workbook`: a readable `.xlsx` workbook containing the `Work Zones` worksheet and the required yellow design-evidence columns
- `assets/Work_Zones_Input_Template.xlsx`: task-local end-user input template; blue columns map to the REST request and yellow columns are design evidence only
- `execution_direction`: omit or specify `ora_rest_execution` for the documented Work Zones create-or-replace route
- `project_id`: an existing durable FSCR project workspace; required by `scripts/run_work_zone.py`
- `setup_data_artifacts`

## Execution Safety

### Preflight

Before a preview or write, the runner validates the selected environment identity, the Work Zones workbook, required API fields, active/inactive status, unique case-insensitive keys, and the 50-character key limit. It then executes `WZ.ENFORCE_DESIGN` against the required yellow design-evidence columns before any current-state GET. This is an evidence-completeness gate: it does not falsely claim to prove live geography, assignment, or routing outcomes. `travelArea` is deprecated by OFSC and omitted from the workbook mapping and REST payload. The runner obtains a current-state GET baseline for every label; HTTP 404 selects collection POST creation, while an existing baseline selects singular PUT replacement. It then creates an immutable, redacted preview bound to the target environment and checksum.

### Failure and Retry Behavior

Classify malformed workbook data as input validation, incomplete design evidence as a design-enforcement blocker, unsupported direction or contract gaps as catalog or metadata mismatch, request failures as Fusion API or transport failures, and unmatched approval as an approval blocker. Do not retry a live POST or PUT automatically. Stop on the first write or verification failure, retain only redacted evidence and an append-only run record under the selected project workspace, including only an allowlisted HTTP status, Fusion error code, or field when available, and require a fresh preview and explicit approval before another attempt. See `ora-resource/ora_error_handling.md` for the task-local disclosure and refusal rules.

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `cx.field-service.scheduling-and-dispatch` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Runner service selection

The task runner accepts `--service field-service`, which is also its default
and only supported service. Task REST preflight, approved writes, and read-back
use `fs_restBaseUrl` and `fs_scope`. The route metadata and runner result identify
`service: field-service`; the runner does not perform BOSS catalog discovery.

New-project prevalidation and Run Book binding are separate project workflow
steps. This service option does not skip those gates or authorize setup writes.

## Workbook Intake Service

Workbook adapters use the local guarded XLSX primitive in
`pillars/cx/field-service/scripts/guarded_xlsx.py` for bounded ZIP/XML parsing.
Task-specific field mapping and business rules remain in this package.
The reader performs no external calls and does not select an execution route
or grant load approval.

## Caller-Only Exact Preview

Use the task runner with `--mode preview --include-exact-preview` to return
`exactPreview` (including the exact requests and checksum) to the active caller
for approval. The option is rejected in execute mode before workflow calls.
Default output and durable evidence remain redacted. Keep captured caller output
in private OS-temporary storage; never copy request bodies or current-state
baselines into project evidence. Review the exact target, methods, paths, headers
and bodies before granting checksum-bound execution approval.
