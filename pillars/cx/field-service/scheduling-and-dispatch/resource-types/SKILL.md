---
skill_id: "cx.field-service.scheduling-and-dispatch.resource-types"
name: "Resource Types Setup Task Guidance"
description: "Provides task-specific setup guidance for Resource Types under the Scheduling and Dispatch functional area."
layer: "pillar"
pillar: "CX"
offering: "Field Service"
functional_area: "Scheduling and Dispatch"
functional_area_code: "ORA_FFS_FA_SCHEDULING_AND_DISPATCH"
task_code: "ORA_FFS_TS_RESOURCE_TYPES"
task_name: "Resource Types"
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
  - "setup_data_artifacts"
  - "resource_types_workbook"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
uses_core:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "core.data-loader.task-rest"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/field-service/scheduling-and-dispatch/resource-types/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/field-service/scheduling-and-dispatch/resource-types/current/"
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
  - "Delegates default Core Task REST work without fallback; performs explicit approved Resource Type PUTs only through ora_rest_execution."
required_privileges:
  - "Access to the target Oracle Field Service environment and required OAuth scope."
  - "Privilege to read Resource Type metadata for preflight and GET verification."
  - "Privilege to create or update Resource Type metadata when ora_rest_execution is explicitly approved."
---

# Resource Types Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Resource Types` under `Scheduling and Dispatch`.

## Setup Task Skill Contract

- task_code: `ORA_FFS_TS_RESOURCE_TYPES`
- task_name: `Resource Types`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Resource Types` under `Scheduling and Dispatch`.

## Setup Task Metadata

- Task name: `Resource Types`
- Task code: `ORA_FFS_TS_RESOURCE_TYPES`
- Available: `Y`
- Export/import supported: `UNKNOWN`
- CSV export/import supported: `UNKNOWN`
- CSV export/import routing: `not supported`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `UNKNOWN`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

Do not route CSV export work to `shared.setup-export.task-level-export` or CSV import work to `core.data-loader` unless live Fusion metadata or Oracle guidance confirms support. Use `shared.validation.setup-data-validator` only when a setup data artifact is available for review. Use `shared.validation.reference-data-validator` when the task depends on cross-pillar reference data.

## Workbook Intake

Use the `Resource Types` worksheet in the supplied configuration workbook as the task input. The workbook filename is not authoritative because it also contains unrelated worksheets, including `Time Slots` and `Work Skills`.

The customer-ready [Resource Types input template](assets/Resource_Types_Input_Template.xlsx) provides the accepted row layout and its companion `Resource Type Details` worksheet. It remains a free-format intake: equivalent customer workbooks are accepted when they supply the same information.

The intake must retain the worksheet's Resource Type labels, active flags, associated resource roles, feature flags, load thresholds, cost-of-time settings, travel settings, and statistic parameters. Before a preview, reject a workbook that has no `Resource Types` worksheet, duplicate Resource Type labels, an empty label, or contradictory mutually exclusive selections for the same Resource Type.

The workbook-derived records are a design input; they are not a REST payload and must not be sent unchanged to Fusion.

## Shared Field Service Task Orchestration

Start at the Field Service offering skill, then invoke only
`scripts/run_resource_types.py` for this task. The shared
`pillars/cx/field-service/scripts/task_orchestration.py` owns route selection,
immutable preview creation, checksum-bound approval, ordered writes, and GET
verification. `scripts/task_adapter.py` owns only Resource Types workbook
mapping, capability defaulting, metadata lookups, and business-field checks.

The default execution direction is `core.data-loader.task-rest`. It must not
fall back to `ora_rest_execution`. If the Core Task REST route does not permit
the declared `PUT`, block and request explicit `ora_rest_execution`.

For the explicit live-write route, use the complete contract in
[`ora-resource/ora_rest_execution.md`](ora-resource/ora_rest_execution.md):
free-format workbook validation, active English preflight, false-by-default
optional capabilities, OFSC Metadata GET baselines, immutable SHA-256 preview,
explicit checksum approval, ordered no-retry PUTs, and GET verification.

Persist only redacted diagnostic and run evidence under `project/{project_id}`.
Do not persist credentials, OAuth tokens, or customer payloads.

## Failure Handling and Recovery

Load [`ora-resource/ora_error_handling.md`](ora-resource/ora_error_handling.md)
before preview or live execution. The runner executes the compiled nested
`RT.*` validation and design-enforcement graph before REST preflight; any
applicable Error rule blocks preview and PUT. Classify failures as
`input_validation`, `design_enforcement`, `authorization_or_privilege`,
`fusion_api`, `artifact_persistence`, `approval_blocker`, or
`partial_execution`.

Retry only a cached-token `401` or `403` through the Core client once. Never
retry a PUT automatically. A PUT or read-back failure stops the displayed
sequence, sends no later PUT, and requires a fresh continuation preview after
read-back reconciliation. Persist redacted project evidence with status,
stage, failure class, safe message, recommended action, environment, checksum,
checks run, and a partial-failure errors array. It must never contain labels,
payloads, baselines, credentials, or tokens.


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
