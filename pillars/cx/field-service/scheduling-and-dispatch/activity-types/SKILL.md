---
skill_id: "cx.field-service.scheduling-and-dispatch.activity-types"
name: "Activity Types Setup Task Guidance"
description: "Provides task-specific setup guidance for Activity Types under the Scheduling and Dispatch functional area."
layer: "pillar"
pillar: "CX"
offering: "Field Service"
functional_area: "Scheduling and Dispatch"
functional_area_code: "ORA_FFS_FA_SCHEDULING_AND_DISPATCH"
task_code: "ORA_FFS_TS_ACTIVITY_TYPES"
task_name: "Activity Types"
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
  - "project_id"
  - "execution_direction"
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
depends_on:
  - "cx.field-service"
  - "cx.field-service.scheduling-and-dispatch"
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
  - "skill_path"
  - "reports"
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
  - "Performs OFSC Metadata PUT operations only after read-only preflight, immutable preview, and explicit approval."
required_privileges:
  - "Environment-approved Oracle Field Service metadata read and Activity Type update permission"
---

# Activity Types Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Activity Types` under `Scheduling and Dispatch`.

## Setup Task Skill Contract

- task_code: `ORA_FFS_TS_ACTIVITY_TYPES`
- task_name: `Activity Types`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Activity Types` under `Scheduling and Dispatch`.

## Free-Format Workbook Intake

Accept a user-supplied `.xlsx` workbook as input even when it does not use the
FSCR Activity Types implementation template. Inspect only worksheets that
describe Activity Types, extract the available values, and build a per-record
intake summary before asking for anything else.

Map clear workbook labels to the task contract without requiring a template:

| Workbook label or equivalent | Task field | Handling |
|---|---|---|
| Activity Type Label | Activity Type Label | Required stable identifier |
| Activity Type Name, English Name, or Name | English Display Name | Required display name |
| Group or Activity Type Group | Group Label | Require confirmation when the workbook does not establish that it is the stable group label rather than a display name |
| Status, Active, or Enabled | Active | Normalize an unambiguous boolean value |
| Default Duration, Default Duration (minutes), or Duration | Default Duration | Require an integer from 1 through 1440 |
| Translation language/name columns | Translations | Accept only after the target-environment active-language lookup confirms the language |
| Optional-feature labels | Optional capabilities | Treat as proposed decisions; do not infer their business rationale or omitted flags |

After extraction, return one concise missing-details request that lists only
unresolved fields by Activity Type. Ask for the following only when absent or
ambiguous in the workbook:

1. Stable group label and whether each proposed record is new or a replacement.
2. Any required identity, active, duration, or English display-name value.
3. The business decision and rationale for each enabled optional capability, including time slots, segmentation, duration statistics, mobility, buckets, inventory, notifications, and tracking where applicable.
4. Any requested lookup selection or current-state result. Use the task-local documented read-only endpoints; do not ask the user to supply endpoint paths.
5. A preview record and a separate approval for every live PUT.

Treat every optional capability as disabled by default in the proposed
configuration. This default applies only to optional capabilities; never
default or change the required Activity Type Label, English Display Name, Group
Label, Active, or Default Duration fields. Do not silently rewrite the
workbook or execute a change from this default.

For every optional capability found in the workbook, render a per-Activity-Type
decision checklist. Show the extracted workbook value as evidence, preselect
`Keep disabled`, and ask the user to correct only the rows that must be
enabled. A capability is enabled only after an explicit user selection and a
short business reason:

| Capability | Current workbook value | Default decision | User correction when enablement is needed |
|---|---|---|---|
| Time slots and operating windows | extracted value | Keep disabled | Enable with appointment-window or quota-management need |
| Resource mobility, buckets, rescheduling, not-ordered, and non-scheduled work | extracted value | Keep disabled | Enable with dispatch or assignment need |
| Work zones, work skills, preferred resources, and links | extracted value | Keep disabled | Enable with eligibility, service-area, continuity, or related-record need |
| Inventory and required inventory | extracted value | Keep disabled | Enable with material requirement and routing impact |
| Travel and duration statistics | extracted value | Keep disabled and use manual duration | Enable with reliable history for statistics, or state why manual duration is unsafe |
| Segmentation, extended duration, mass activities, teamwork, and repeating activities | extracted value | Keep disabled | Enable with multi-day, interruptible, internal-work, or team-work need |
| Search and incoming-interface creation | extracted value | Keep disabled | Enable with user or authorized-integration need |
| Message triggers, delivery windows, and customer time zones | extracted value | Keep disabled | Enable with recipient, timing, service-window, or cross-time-zone need |
| Resource tracking and color convention | extracted value | Keep disabled | Enable with dispatch-display convention or privacy-policy need |

`TBD` is a blocking selection: retain it in the intake summary and stop before
preview. A selected `Enable` decision needs only the short business reason
requested in the final column; do not ask the user to restate the technical
flag name or reproduce workbook values.

Resolve the target environment from the selected FSCR environment profile in
`core/auth/fusionEnv.properties`; use its configured `environment` and
`restBaseUrl` for authorized preflight checks and, on the default executable
REST route, the approved OFSC Metadata PUT operations. Do not ask the user
to paste a base URL or credentials. The project workspace records only safe
environment identity and artifact references, not connection configuration. If
no usable profile is selected or more than one profile is in scope, stop with a
`transport_or_environment` prerequisite and ask the user to select or configure
an FSCR environment profile.

Do not ask the user to reformat the workbook, duplicate values already
extracted from it, or fill a template solely to proceed. Do not treat a blank
cell as permission to apply a default, disable a feature, invent a lookup path,
or create a replacement payload. Keep customer values out of reusable skill
files and project artifacts; persist only redacted validation outcomes when a
project workspace is in scope.

Use this intake prompt after extraction:

```text
I extracted the available Activity Types from your workbook. Please provide or
confirm only these unresolved items: {per-record missing fields, ambiguous
group labels, and corrections to the capability checklist preselected as
disabled}. Add a short reason only for capabilities you want enabled. I will
resolve the selected FSCR environment profile
separately. I will not modify the workbook or execute a PUT until they are
resolved and an exact preview is approved.
```

## Exact Create Preview

Build the request body only after the documented language, group, and
current-state lookups have passed. The workbook's `Customer` value is a
display name; resolve and use the target environment's canonical group label
in the request body.

For the user-selected default-capability policy, use the deterministic
preview-only builder:

```bash
python3 scripts/build_activity_types_preview.py \
  --workbook <free-format-activity-types.xlsx> \
  --group-label <canonical-environment-group-label> \
  --output <temporary-preview-data.json>
```

The builder creates one immutable `PUT` request per Activity Types
worksheet. It maps only the required label, active status, group label,
default duration, and English translation, and explicitly sets every optional
feature to `false`. It omits time slots, segment settings, and colors because
they are not enabled by the default-capability policy. The temporary preview
data contains customer configuration and must not be persisted in
`project/{project_id}`.

Use the task-local immutable preview builder after current-state GETs:

```bash
python3 scripts/build_activity_types_execution_preview.py \
  --payload-preview <temporary-preview-data.json> \
  --execution-direction ora_rest_execution \
  --environment <selected-FSCR-environment-name> \
  --baseline <label>=<temporary-current-state.json> \
  --output <temporary-exact-preview.json>
```

Display the resulting exact preview and SHA-256 digest for review, then require
a separately recorded approval bound to that digest immediately before each live
PUT. `ora_rest_execution` is not read-only: after approval, it invokes
`core.fusion-api.rest-api-client` for the declared `PUT`, then the declared GET
verification. A changed workbook, group label, feature decision, route,
environment, path, body, or current-state result invalidates the preview.

Use `scripts/run_activity_types.py` as the only task entry point. Run it with
`--mode preview` first, then run `--mode execute --approve-checksum <checksum>`
only after explicit user approval for that exact checksum. Do not manually chain
the helper scripts or call the REST client directly.

## Failure Handling and Evidence

Read [ora-resource/ora_error_handling.md](ora-resource/ora_error_handling.md)
before returning a blocked, partial, or completed result. Classify failures as
`input_validation`, `catalog_mismatch`, `auth_or_authz`,
`transport_or_environment`, `fusion_api`, `artifact_persistence`, or
`approval_blocker`. Stop before a write for all preflight failures. A `401` or
`403` may use the Core client's one token refresh; no `PUT` is retried.

For every runner invocation, require an initialized `--project-id` and write
only a redacted run record and standard token-usage row. The exact preview,
payload, baseline, labels, and REST response must be written only to an
OS-temporary `--output` path and never to `project/` or another durable
workspace location. On a failed or uncertain `PUT`, stop the ordered sequence,
record a redacted `partial_execution` outcome, and require a fresh current-state
preview before any continuation.

## Setup Task Metadata

- Task name: `Activity Types`
- Task code: `ORA_FFS_TS_ACTIVITY_TYPES`
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
- `project_id` — required for the runner; must name an initialized FSCR project
  workspace so it can record redacted evidence and token usage.
- `execution_direction` — optional; defaults to `ora_rest_execution`, the only
  executable route for this task's declared `PUT`. `core.data-loader.task-rest`
  is accepted only as an explicit fail-closed selection because its Core-owned
  contract permits GET, POST, and PATCH, not PUT.

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
