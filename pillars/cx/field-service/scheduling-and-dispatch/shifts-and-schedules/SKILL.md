---
skill_id: "cx.field-service.scheduling-and-dispatch.shifts-and-schedules"
name: "Shifts and Schedules Setup Task Guidance"
description: "Provides task-specific setup guidance for Shifts and Schedules under the Scheduling and Dispatch functional area."
layer: "pillar"
pillar: "CX"
offering: "Field Service"
functional_area: "Scheduling and Dispatch"
functional_area_code: "ORA_FFS_FA_SCHEDULING_AND_DISPATCH"
task_code: "ORA_FFS_TS_SHIFTS_AND_SCHEDULES"
task_name: "Shifts and Schedules"
parent_skill_id: "cx.field-service.scheduling-and-dispatch"
available_flag: "Y"
export_import_supported_flag: "UNKNOWN"
csv_export_import_supported_flag: "UNKNOWN"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "hybrid"
owner_team: "CX field service pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "filled_workbook_template"
  - "execution_direction"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
  - "execution_route"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/field-service/scheduling-and-dispatch/shifts-and-schedules/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/field-service/scheduling-and-dispatch/shifts-and-schedules/current/"
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
  - "Writes individual Shift Item records only after an immutable preview and explicit approval"
required_privileges:
  - "Field Service configuration read access for baseline and verification GETs"
  - "Field Service configuration write access for explicitly approved Shift Item operations"
---

# Shifts and Schedules Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Shifts and Schedules` under `Scheduling and Dispatch`.

## Setup Task Skill Contract

- task_code: `ORA_FFS_TS_SHIFTS_AND_SCHEDULES`
- task_name: `Shifts and Schedules`
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

Use this skill when planning, validating, previewing, or importing `Shifts and Schedules` setup data from a workbook template completed by the end user.

## Filled Workbook Template Intake

The end user supplies one filled XLSX configuration workbook. The `Work Schedules` worksheet is authoritative for this task; the workbook filename is not.

The worksheet contains the `Work Schedules` table and the `Shifts` table. Preserve each workbook value exactly until validation. Do not infer a REST payload from a display name, a workbook row number, or an empty cell.

| Workbook section | Required end-user fields | REST use | Refusal condition |
|---|---|---|---|
| Work Schedules | Name, Label, Active | Creates or resolves the parent work schedule by label before any item request | The label, name, or active state is missing |
| Shifts | Work Schedule Label, Name, Label, Active, Type, Start time, End time, Points, Decoration | Creates or resolves the parent shift by label before any schedule-item request | The shift label, referenced schedule, or required shift fields are missing |
| Work-schedule item payload | `work_schedule_label`, `itemId`, `type`, `shiftLabel` or `nonWorkingReasonLabel`, `startDate`, `endDate` when applicable, and repeat fields | Maps the completed workbook row to the documented OFSC item body only after its schedule and shift are planned | Required workbook fields are absent |

The current `Work Schedules` worksheet does not by itself provide every Shift Item payload field. The end user must provide the missing payload fields in the filled template or as a clearly associated workbook table. Do not fabricate `record_type`, dates, recurrence, `shift_id`, `non_working_reason_id`, or internal IDs.

## Preflight Checks

Before any current-state lookup, preview, or write, the runner validates the filled workbook, required REST fields, task design rules, execution direction, and target configuration. It uses each parent-label GET as the current-state baseline; a missing parent is created from the corresponding `Work Schedules` or `Shifts` workbook row through a conditional PUT. It then verifies the requested operation is preview or has an immutable-preview checksum with explicit approval for the target environment. A failed preflight stops the route before any REST call; it does not fall back to Data Loader, PATCH, or inferred payload values.

## REST Parent and Item Contract

Source: Configuration API contract (public source verification pending), Work Schedules and Shifts v1 sections. The REST client uses the documented Configuration API paths below.

Use the documented metadata API in this mandatory dependency order:

| Operation | Method and path | Identity | Result |
|---|---|---|---|
| Create or resolve work schedule | PUT `/api/field-service/configuration/v1/workSchedules/{label}` | Work schedule label | Parent schedule read-back |
| Create or resolve shift | PUT `/api/field-service/configuration/v1/shifts/{label}` | Shift label | Parent shift read-back |
| Read items | GET `/api/field-service/configuration/v1/workSchedules/{label}/items` | Work schedule label | Work-schedule item collection |
| Create item | POST `/api/field-service/configuration/v1/workSchedules/{label}/items` | Work schedule label plus validated payload | Created item |
| Update item | PUT `/api/field-service/configuration/v1/workSchedules/{label}/items/{itemId}` | Work schedule label and positive workbook `itemId` | Updated item |
| Delete item | DELETE `/api/field-service/configuration/v1/workSchedules/{label}/items/{itemId}` | Work schedule label and positive workbook `itemId` | No content |

For a `shift` POST, map the completed workbook row to the OFSC item body using this shape. `shiftLabel`, `repeatType`, and `repeatDays` are workbook fields; they are not emitted unchanged:

```json
{
  "type": "shift",
  "label": "SH_EAST_DAY",
  "shiftType": "regular",
  "startDate": "2024-06-17",
  "endDate": "2024-12-31",
  "recurrence": {
    "type": "weekly",
    "every": 1,
    "startDate": "2024-06-17",
    "endDate": "2024-12-31",
    "weekdays": ["monday", "tuesday", "wednesday", "thursday", "friday"]
  }
}
```

The work schedule and shift PUTs are documented upserts. A new parent uses `If-None-Match: {label}`; an existing parent is read before preview and then explicitly represented in the immutable plan. An on-call shift requires `decoration` with one of `yellow`, `orange`, `red`, `blue`, `green`, or `purple`; decoration is not allowed for a regular shift. A workbook `shiftLabel` maps to OFSC item `label`, with its configured `shiftType`; a workbook `nonWorkingReasonLabel` maps to OFSC item `label`. If `endDate` is supplied, it must not precede `startDate`; weekly workbook repeats require `repeatDays`, which map to full weekday names in `recurrence.weekdays`.

This contract creates or resolves documented parent resources before it handles individual work-schedule items. It does not authorize an undocumented bulk import endpoint or a live mutation. Before a live POST, PUT, or DELETE, create an immutable preview from the exact filled workbook rows and obtain explicit approval for the target environment, operation, path, payload, and identity.

## Execution Direction

The filled workbook is validated before any route is selected. `execution_direction` is optional; when it is omitted, use the Data Loader-based direction. It is a route preference, not authorization to bypass source, preview, approval, or verification gates.

| execution_direction | Selection | Owner | Route behavior |
|---|---|---|---|
| `data_loader_execution` | Default | `core.data-loader` | Validate the workbook and use the Core Data Loader workflow only if its applicable source, metadata, immutable-preview, and approval gates confirm a supported import contract. `CSVExportImportSupportedFlag=UNKNOWN` is a hard stop for an assumed FSM CSV import. |
| `ora_rest_execution` | Explicit user selection | This pillar task plus `core.fusion-api.rest-api-client` | Resolve/create work schedules, resolve/create shifts, then read and mutate work-schedule items. Bind the full ordered plan to the immutable preview and approval, execute once, then verify with GET. |

The Core `task-rest` executor currently accepts only GET, POST, and PATCH. It cannot execute the documented Shift Item PUT contract. Do not substitute PATCH. For a requested PUT, the selected `ora_rest_execution` route uses the shared `core.fusion-api.rest-api-client` after all task gates pass; it remains subject to explicit approval and read-back verification. DELETE is never selected from a filled workbook unless the user explicitly requests deletion and approves the exact positive `internalId`.

## Executable REST Route

The `ora_rest_execution` contract is implemented rather than merely described:

```text
pillars/cx/field-service/scripts/task_orchestration.py
pillars/cx/field-service/scheduling-and-dispatch/shifts-and-schedules/scripts/task_adapter.py
pillars/cx/field-service/scheduling-and-dispatch/shifts-and-schedules/scripts/run_shifts_and_schedules.py
```

The runner accepts the filled workbook, produces an immutable JSON preview, and stops at approval by default. It delegates all HTTP calls to `core/fusion-api/rest-api-client`; task-specific workbook mapping, API paths, payload validation, deletion acknowledgement, and GET verification remain in the Shifts adapter.

```bash
python3 pillars/cx/field-service/scheduling-and-dispatch/shifts-and-schedules/scripts/run_shifts_and_schedules.py \
  --workbook <filled-workbook.xlsx> \
  --execution-direction ora_rest_execution \
  --mode preview \
  --output <preview.json>
```

## Failure Handling and Safety

- Validate the filled workbook and every required REST field before current-state lookup, preview, or write.
- Classify failures as input validation, approval blocker, auth/authz, transport/environment, Fusion API, verification mismatch, or artifact persistence. Return the stage and redacted evidence.
- A cached-token refresh may occur once inside the shared client for a rejected read. Do not retry POST, PUT, DELETE, import, or an uncertain write outcome.
- The immutable preview checksum binds the target environment, GET baselines, paths, methods, and request bodies. Any change requires a fresh preview and approval.
- Stop after the first write failure or failed GET verification. Do not substitute PATCH, roll back, or fall back to Data Loader.
- DELETE needs both approval of the exact checksum and the explicit runner `--allow-delete` acknowledgement.

## Setup Task Metadata

- Task name: `Shifts and Schedules`
- Task code: `ORA_FFS_TS_SHIFTS_AND_SCHEDULES`
- Available: `Y`
- Export/import supported: `UNKNOWN`
- CSV export/import supported: `UNKNOWN`
- CSV export/import routing: `not supported`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `UNKNOWN`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

Do not route CSV export or CSV import work to `shared.setup-export.task-level-export` or `shared.setup-import.task-level-import` unless live Fusion metadata or Oracle guidance confirms support. Use `shared.validation.setup-data-validator` only when a setup data artifact is available for review. Use `shared.validation.reference-data-validator` when the task depends on cross-pillar reference data.


## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `filled_workbook_template`
- `execution_direction` — optional; defaults to `data_loader_execution`; accepted alternate is `ora_rest_execution`

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`
- `execution_route`

## Implementation Notes

Use the parent functional-area skill `cx.field-service.scheduling-and-dispatch` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
