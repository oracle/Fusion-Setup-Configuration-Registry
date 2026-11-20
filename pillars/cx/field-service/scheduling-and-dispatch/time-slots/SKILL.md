---
skill_id: "cx.field-service.scheduling-and-dispatch.time-slots"
name: "Time Slots Setup Task Guidance"
description: "Provides task-specific setup guidance for Time Slots under the Scheduling and Dispatch functional area."
layer: "pillar"
pillar: "CX"
offering: "Field Service"
functional_area: "Scheduling and Dispatch"
functional_area_code: "ORA_FFS_FA_SCHEDULING_AND_DISPATCH"
task_code: "ORA_FFS_TS_TIME_SLOTS"
task_name: "Time Slots"
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
  - "execution_direction"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
uses_core:
  - "core.data-loader.task-rest"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/field-service/scheduling-and-dispatch/time-slots/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/field-service/scheduling-and-dispatch/time-slots/current/"
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
  - "When execution_direction=ora_rest_execution is explicitly selected, performs Time Slots PUT operations only after read-only preflight, a describe-backed immutable preview, and explicit approval."
required_privileges:
  - "Environment-approved Field Service Time Slots collection and item read access for preview and verification"
  - "Environment-approved Field Service Time Slots create/update permission for the exact approved PUT operation"
---

# Time Slots Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Time Slots` under `Scheduling and Dispatch`.

## Setup Task Skill Contract

- task_code: `ORA_FFS_TS_TIME_SLOTS`
- task_name: `Time Slots`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Time Slots` under `Scheduling and Dispatch`.

## Execution Direction

`execution_direction` is optional and defaults to `core.data-loader.task-rest`.
That Core route may execute only the operation methods it supports after its
own task-validation gate. It must reject the Time Slots `PUT` operation rather
than silently changing route or method.

Set `execution_direction=ora_rest_execution` only when explicitly selecting
the task-owned Time Slots REST workflow. That route requires read-only
preflight, describe-backed payload mapping, an immutable preview, and approval
bound to that preview immediately before the `PUT`. A failed or unsupported
default route is not permission to fall back automatically to direct REST.

The contract in `ora-resource/ora_rest_execution.md` is the source of truth for
route selection, supported operations, endpoint paths, refusal behavior, and
verification. It does not authorize a live call by itself.

## Time Slots REST Execution Contract

| Requested direction | Result | Constraint |
|---|---|---|
| Omitted or `core.data-loader.task-rest` | Use the Core Task REST executor | It permits GET, POST, and PATCH only. It must reject the Time Slots `PUT` and must not substitute a route. |
| `ora_rest_execution` | Use the pillar-owned direct REST workflow | This is the only selected route for a Time Slots `PUT`; it is not a fallback. |
| Data Loader archive/import | Block | CSV support is `UNKNOWN`; a configuration workbook is not a Data Loader artifact. |

The direct workflow uses the implementation API: search with
`GET /api/field-service/configuration/v1/timeSlots/`, read with
`GET /api/field-service/configuration/v1/timeSlots/{itemId}`, and create or
update with `PUT /api/field-service/configuration/v1/timeSlots/{itemId}`. The
public `GET /rest/ofscMetadata/v1/timeSlots` endpoint is discovery-only.
A `404` item read is a create candidate and a `200` item read is an update
candidate; both use the same implementation item PUT. Reject POST, PATCH,
DELETE, metadata-item write paths, and endpoint substitution. Every PUT uses
`FS-IDENTIFY-BY: label` always. Send `If-None-Match: {label}` only for a 404
create candidate; omit it for a 200 update candidate, otherwise the API
returns a create-only `409 Conflict`.

The writable body maps Label, Name, Status, Start Time, and End Time to
`label`, `name`, `active`, `timeStart`, and `timeEnd`. `isAllDay` appears only
in the documented response and is not written; all-day rows are therefore
rejected as unsupported by this direct contract. Activity Types and Capacity
Categories are not execution payload fields. The association APIs are never called.
Warehouse Visits has no mapped writable field and is rejected.

For an executable direct operation:

1. Validate the workbook and construct candidate payloads locally before any
   Fusion request. Confirm environment identity and Time Slots read access,
   then list/read the current state. For execution, require environment-owner
   evidence that the selected principal has Time Slots create/update permission;
   successful GET access alone does not establish write permission. Stop if
   authorization is missing or uncertain. No role or privilege-code name is
   assumed by this contract.
2. Resolve a 404 only as a create candidate; treat a 200 as an update, enable,
   or disable candidate. Stop on any other read result.
3. Produce an immutable preview containing environment identity, method, path,
   current-state summary, mapped body, field-level diff, and SHA-256 digest.
4. Obtain explicit approval bound to that exact digest immediately before PUT.
   Do not retry, roll back, or substitute a write method. If an independent
   slot write fails, retain its diagnostic and continue the remaining approved
   independent slots; return `partial_failed`, never `completed`.
5. Read the same item with GET after a successful PUT and compare saved fields
   with the approved request. Persist only redacted diagnostics and artifact
   references.

## Error Handling

Apply the task-local failure contract in
`ora-resource/ora_error_handling.md` before preview and execution. Preflight,
workbook validation, design-enforcement, dependency, lookup, and payload
mapping failures block the preview and no write is attempted. Do not retry a
PUT automatically, substitute an endpoint or execution route, or make a write
without approval bound to the immutable preview. Persist only sanitized,
redacted diagnostics. When an approved independent slot PUT fails, retain its
failure diagnostic, continue only the remaining approved independent slots,
and return `partial_failed`; verify each successful PUT with a same-item GET.

## Setup Task Metadata

- Task name: `Time Slots`
- Task code: `ORA_FFS_TS_TIME_SLOTS`
- Available: `Y`
- Export/import supported: `UNKNOWN`
- CSV export/import supported: `UNKNOWN`
- CSV export/import routing: `not supported`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `UNKNOWN`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

Do not route CSV export work to `shared.setup-export.task-level-export` or CSV import work to `core.data-loader` unless live Fusion metadata or Oracle guidance confirms support. Use `shared.validation.setup-data-validator` only when a setup data artifact is available for review. Use `shared.validation.reference-data-validator` when the task depends on cross-pillar reference data.


## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`
- `execution_direction` — optional; defaults to `core.data-loader.task-rest`.
  Set to `ora_rest_execution` only with an explicit task-owned REST selection.

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `cx.field-service.scheduling-and-dispatch` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Caller-Only Exact Preview

Use the task runner with `--mode preview --include-exact-preview` to return
`exactPreview` (including the exact requests and checksum) to the active caller
for approval. The option is rejected in execute mode before workflow calls.
Default output and durable evidence remain redacted. Keep captured caller output
in private OS-temporary storage; never copy request bodies or current-state
baselines into project evidence. Review the exact target, methods, paths, headers
and bodies before granting checksum-bound execution approval.
