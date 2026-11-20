---
skill_id: "cx.field-service.scheduling-and-dispatch.work-skills"
name: "Work Skills Setup Task Guidance"
description: "Provides task-specific setup guidance for Work Skills under the Scheduling and Dispatch functional area."
layer: "pillar"
pillar: "CX"
offering: "Field Service"
functional_area: "Scheduling and Dispatch"
functional_area_code: "ORA_FFS_FA_SCHEDULING_AND_DISPATCH"
task_code: "ORA_FFS_TS_WORK_SKILLS"
task_name: "Work Skills"
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
  - "task_skill_id"
  - "execution_direction"
outputs:
  - "skill_run_record"
  - "token_usage_record"
uses_core:
  - "core.auth.fusion-oauth-authentication"
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
  - "token_usage_records"
workspace_outputs:
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
  - "Delegates default Task REST requests without fallback and performs explicit REST PUTs only after immutable preview and checksum-bound approval."
required_privileges:
  - "Access to the target Oracle Field Service environment and required OAuth scope."
  - "Permission to read Work Skill metadata for preflight and GET verification."
  - "Permission to create or update Work Skill metadata for an explicitly approved REST PUT."
---

# Work Skills Setup Task Guidance

## Purpose

Provides task-specific Work Skills orchestration under `Scheduling and Dispatch`.

## Setup Task Skill Contract

- task_code: `ORA_FFS_TS_WORK_SKILLS`
- task_name: `Work Skills`
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

Use the Field Service offering skill as the starting point. This nested skill is
the only Work Skills task entry point and delegates shared workflow behavior to
`pillars/cx/field-service/scripts/task_orchestration.py`.

## Setup Task Metadata

- Task name: `Work Skills`
- Task code: `ORA_FFS_TS_WORK_SKILLS`
- Available: `Y`
- Export/import supported: `UNKNOWN`
- CSV export/import supported: `UNKNOWN`
- CSV export/import routing: `not supported`

## Execution Directions

- Default: `core.data-loader.task-rest`. The shared task runner delegates to
  that Core-owned route only; if it rejects PUT, it blocks and requires an
  explicit `ora_rest_execution` request.
- Explicit live-write route: `ora_rest_execution`. It uses the task-local
  adapter, shared OAuth/Core REST client, immutable preview, exact-checksum
  approval, ordered Work Skill then Work Skill Group upsert PUTs, and GET
  verification.
- No automatic fallback occurs between these directions.

Run Work Skills only through:

```text
scripts/run_work_skills.py
```

The runner accepts free-format `.xlsx` field/value worksheets. Its task-local
adapter owns Work Skills workbook validation, OFSC Metadata paths, payload
mapping, and verification. The shared runner owns route selection, transport,
preview/approval binding, no-retry behavior, and safe write sequencing.

This runner handles Work Skill and Work Skill Group resource payloads. Group
members must reference a Work Skill included in the workbook or an existing
target Work Skill; optional group capabilities default to `false`. If the
workbook also contains Work Skill Conditions, it blocks: those are separate API
resources with their own `POST`/`PUT` identity contract and must not be silently
dropped.

## Preflight and Approval

Before any live upsert, the runner validates the workbook and its required
fields, executes every registered Work Skills design rule using qualification,
routing/optimization, and onboarding/dispatcher evidence, and blocks configured
Work Skill Conditions until their separately approved API payload is implemented.
It validates group members and capacity rationale, resolves the requested execution direction, confirms an
active English language in the target environment, and retrieves an
object-or-absent baseline for every label. It then writes an immutable preview
containing the environment, PUT paths, request bodies, baselines, and SHA-256
checksum. A live `PUT` proceeds only when the caller explicitly selects
`ora_rest_execution` and supplies that fresh checksum as approval.

## Failure Handling

Input and workbook failures stop before preview; route, baseline, language,
approval, and verification failures stop before the next side effect. The
runner does not automatically retry live `PUT` requests. It records redacted
run evidence under `project/{project_id}/state/runs/`, classifying failures as
`input_validation`, `approval_or_workflow_blocker`, or
`unexpected_runner_error`; it never records tokens, credentials, or request
bodies in durable project evidence.

## Customer Input Template

Start customer data collection from
[`assets/Work_Skills_End_User_Input_Template.xlsx`](assets/Work_Skills_End_User_Input_Template.xlsx).
The `Work Skills`, `Work Skill Groups`, and `Work Skill Group Members` sheets
are executable input. Groups run only after their member Work Skills and retain
the declared member ratios. The `Work Skill Conditions` sheet is for design
capture only and remains blocked from execution until its separate API identity
contract is implemented.

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `UNKNOWN`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

Do not route CSV export work to `shared.setup-export.task-level-export` or CSV import work to `core.data-loader` unless live Fusion metadata or Oracle guidance confirms support. Use `shared.validation.setup-data-validator` only when a setup data artifact is available for review. Use `shared.validation.reference-data-validator` when the task depends on cross-pillar reference data.


## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`

## Outputs

- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `cx.field-service.scheduling-and-dispatch`
for scope decisions. Persist only redacted run evidence under
`project/{project_id}`; never persist tokens, credentials, or customer payloads.

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

Use `--mode preview --include-exact-preview` to return the full `exactPreview`
for checksum-bound approval. Default caller output remains the implementation
summary, and durable evidence remains redacted. The option is rejected in
execute mode. Completed and no-change runs do not require a preview to report
their terminal result. Keep captured exact output in private OS-temporary storage.
