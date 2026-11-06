---
skill_id: "erp.financials.payables.manage-payables-calendars"
name: "Manage Payables Calendars Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Payables Calendars under the Payables functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payables"
functional_area_code: "FIN_PAYABLES_DEPLOYED"
task_code: "AP_MANAGE_PAYABLES_CALENDARS"
task_name: "Manage Payables Calendars"
parent_skill_id: "erp.financials.payables"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.1.0"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-payables-calendars/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-payables-calendars/current/"
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

# Manage Payables Calendars Setup Task Guidance

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_OTHER_PERIOD_TYPE::CalendarName, AP_OTHER_PERIOD_TYPE::CalendarType, AP_OTHER_PERIOD_TYPE::Description, AP_OTHER_PERIOD_TYPE::AttributeCategory, AP_OTHER_PERIOD_TYPE::Attribute1, AP_OTHER_PERIOD_TYPE::Attribute2, AP_OTHER_PERIOD_TYPE::Attribute3, AP_OTHER_PERIOD_TYPE::Attribute4, AP_OTHER_PERIOD_TYPE::Attribute5, AP_OTHER_PERIOD_TYPE::Attribute6, AP_OTHER_PERIOD_TYPE::Attribute7, AP_OTHER_PERIOD_TYPE::Attribute8, AP_OTHER_PERIOD_TYPE::Attribute9, AP_OTHER_PERIOD_TYPE::Attribute10, AP_OTHER_PERIOD_TYPE::Attribute11, AP_OTHER_PERIOD_TYPE::Attribute12, AP_OTHER_PERIOD_TYPE::Attribute13, AP_OTHER_PERIOD_TYPE::Attribute14, AP_OTHER_PERIOD_TYPE::Attribute15, AP_OTHER_PERIOD_TYPE::EffectiveFrom, AP_OTHER_PERIOD_TYPE::EffectiveTo, AP_OTHER_PERIOD_TYPE::PeriodFrequency, AP_OTHER_PERIOD_TYPE::PeriodNameFormat, AP_OTHER_PERIOD_TYPE::PeriodsPerYear, AP_OTHER_PERIOD_TYPE::StartDate, AP_OTHER_PERIOD_PERIOD::AP_OTHER_PERIOD_TYPE.CalendarName, AP_OTHER_PERIOD_PERIOD::AP_OTHER_PERIOD_TYPE.CalendarType, AP_OTHER_PERIOD_PERIOD::ApplicationId, AP_OTHER_PERIOD_PERIOD::CalendarName, AP_OTHER_PERIOD_PERIOD::CalendarType, AP_OTHER_PERIOD_PERIOD::Description, AP_OTHER_PERIOD_PERIOD::AttributeCategory, AP_OTHER_PERIOD_PERIOD::Attribute1, AP_OTHER_PERIOD_PERIOD::Attribute2, AP_OTHER_PERIOD_PERIOD::Attribute3, AP_OTHER_PERIOD_PERIOD::Attribute4, AP_OTHER_PERIOD_PERIOD::Attribute5, AP_OTHER_PERIOD_PERIOD::Attribute6, AP_OTHER_PERIOD_PERIOD::Attribute7, AP_OTHER_PERIOD_PERIOD::Attribute8, AP_OTHER_PERIOD_PERIOD::Attribute9, AP_OTHER_PERIOD_PERIOD::Attribute10, AP_OTHER_PERIOD_PERIOD::Attribute11, AP_OTHER_PERIOD_PERIOD::Attribute12, AP_OTHER_PERIOD_PERIOD::Attribute13, AP_OTHER_PERIOD_PERIOD::Attribute14, AP_OTHER_PERIOD_PERIOD::Attribute15, AP_OTHER_PERIOD_PERIOD::DueDate, AP_OTHER_PERIOD_PERIOD::EndDate, AP_OTHER_PERIOD_PERIOD::EnteredPeriodName, AP_OTHER_PERIOD_PERIOD::PeriodName, AP_OTHER_PERIOD_PERIOD::PeriodNum, AP_OTHER_PERIOD_PERIOD::PeriodYear, AP_OTHER_PERIOD_PERIOD::StartDate -->
<!-- fscr-update-fields: AP_OTHER_PERIOD_TYPE::Description, AP_OTHER_PERIOD_TYPE::AttributeCategory, AP_OTHER_PERIOD_TYPE::Attribute1, AP_OTHER_PERIOD_TYPE::Attribute2, AP_OTHER_PERIOD_TYPE::Attribute3, AP_OTHER_PERIOD_TYPE::Attribute4, AP_OTHER_PERIOD_TYPE::Attribute5, AP_OTHER_PERIOD_TYPE::Attribute6, AP_OTHER_PERIOD_TYPE::Attribute7, AP_OTHER_PERIOD_TYPE::Attribute8, AP_OTHER_PERIOD_TYPE::Attribute9, AP_OTHER_PERIOD_TYPE::Attribute10, AP_OTHER_PERIOD_TYPE::Attribute11, AP_OTHER_PERIOD_TYPE::Attribute12, AP_OTHER_PERIOD_TYPE::Attribute13, AP_OTHER_PERIOD_TYPE::Attribute14, AP_OTHER_PERIOD_TYPE::Attribute15, AP_OTHER_PERIOD_TYPE::EffectiveTo, AP_OTHER_PERIOD_PERIOD::AP_OTHER_PERIOD_TYPE.CalendarName, AP_OTHER_PERIOD_PERIOD::AP_OTHER_PERIOD_TYPE.CalendarType, AP_OTHER_PERIOD_PERIOD::Description, AP_OTHER_PERIOD_PERIOD::AttributeCategory, AP_OTHER_PERIOD_PERIOD::Attribute1, AP_OTHER_PERIOD_PERIOD::Attribute2, AP_OTHER_PERIOD_PERIOD::Attribute3, AP_OTHER_PERIOD_PERIOD::Attribute4, AP_OTHER_PERIOD_PERIOD::Attribute5, AP_OTHER_PERIOD_PERIOD::Attribute6, AP_OTHER_PERIOD_PERIOD::Attribute7, AP_OTHER_PERIOD_PERIOD::Attribute8, AP_OTHER_PERIOD_PERIOD::Attribute9, AP_OTHER_PERIOD_PERIOD::Attribute10, AP_OTHER_PERIOD_PERIOD::Attribute11, AP_OTHER_PERIOD_PERIOD::Attribute12, AP_OTHER_PERIOD_PERIOD::Attribute13, AP_OTHER_PERIOD_PERIOD::Attribute14, AP_OTHER_PERIOD_PERIOD::Attribute15, AP_OTHER_PERIOD_PERIOD::DueDate, AP_OTHER_PERIOD_PERIOD::EndDate, AP_OTHER_PERIOD_PERIOD::PeriodNum, AP_OTHER_PERIOD_PERIOD::StartDate -->

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Payables Calendars` under `Payables`.

## Supported Operations

This task supports creating calendar and period setup records and making the bounded updates documented in [Input Validation](ora-resource/ora_input_validation.md) and [Design Enforcement](ora-resource/ora_design_enforcement.md). It does not support delete or end-date operations; all fields outside the documented create and update boundaries remain blocked.

## Task Behavior

Use this task to create and maintain Payables calendar types and their period
schedules. Calendar definitions and period rows are handled together, so a
requested update preserves unrelated calendar and period values while applying
only the permitted change.

- Build every candidate from the exact Manage Payables Calendars package. Keep
  both calendar and period CSV members, their ordered headers, metadata paths,
  full-width rows, and parent-child keys unchanged from the task template.
- A period row must name the same parent Calendar Name and Calendar Type as its
  calendar row. For every period create or update, include that matching parent
  calendar header row in the same FSM archive. Do not create or update a period
  independently of that parent context.
- A period `DueDate` is required for a `PAYMENT TERMS` calendar and optional for
  a `GENERAL` calendar. When supplied, it must be on or after `EndDate`.
- For an update, change only the documented calendar or period fields and
  preserve every other value and row from the fresh baseline. Calendar and
  period date ranges must remain ordered, periods must not overlap, and period
  number/year pairs must remain unique.
- Use the supported Calendar Type package codes. Preserve supplied period
  frequency and period-name-format codes without inventing a substitute or a
  default; Fusion validates customer-configured values during import.
- When the requester asks to generate the initial year's periods, set
  `generatePeriods: true` on its `AP_OTHER_PERIOD_TYPE` create operation. Supply
  `StartDate`, `PeriodFrequency`, the matching `PeriodsPerYear` (12 for monthly
  and 4-4-5 patterns, 4 for quarterly, 52 for weekly), and `PeriodNameFormat`
  (`MM` or `MMM` for monthly and 4-4-5 patterns, `QUARTER` or `WEEK` for the
  corresponding frequency). The adapter expands these into dated child rows
  in the preview and candidate. `OTHER` periods are manually defined. Do not
  combine generated and manual period rows for the same calendar.
- Fresh exports can represent dates as `YYYY/MM/DD`, but candidate import rows
  must serialize every nonblank date as `YYYY-MM-DD`. Normalize retained
  baseline dates as well as requester-supplied dates before import.
- Route every import through `core.data-loader` in FSM mode. A candidate still
  requires an immutable preview and explicit approval before submission.

## Setup Task Skill Contract

- task_code: `AP_MANAGE_PAYABLES_CALENDARS`
- task_name: `Manage Payables Calendars`
- parent_skill_id: `erp.financials.payables`
- pillar: `ERP`
- offering: `Financials`
- functional_area: `Payables`
- functional_area_code: `FIN_PAYABLES_DEPLOYED`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Payables Calendars` under `Payables`.

## Setup Task Metadata

- Task name: `Manage Payables Calendars`
- Task code: `AP_MANAGE_PAYABLES_CALENDARS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Financials`
- Functional area / Setup Object: `Payables`
- Setup task name: `Manage Payables Calendars`
- Setup task code: `AP_MANAGE_PAYABLES_CALENDARS`




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

Use the parent functional-area skill `erp.financials.payables` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Supporting Parent Headers

For every period create or update, include its matching calendar header once
in the same FSM archive. Match both CalendarName and CalendarType.

- Existing calendar, no requested header change: copy its header from the fresh
  current-data baseline without changing any business value.
- Existing calendar, requested header change: use that baseline header and apply
  only the permitted changes the user requested.
- New calendar: include the explicitly requested calendar create row with the
  required values. Do not invent a calendar to satisfy a period request.
- Calendar absent from the baseline and no explicit calendar create: stop and
  ask the user to identify an existing calendar or request a new calendar.

Leave audit fields blank in all import rows. Preserve calendar dates when
converting the export date format to the import date format. Reject missing
parents, unrequested changes to supporting headers, and populated audit fields.
Other existing periods do not need to be copied into the candidate. For an
uploaded ZIP, require the header inside that ZIP; validation does not add it.
Validate all uploaded rows together so overlapping period creates and duplicate
year/period-number pairs are rejected when the header is unchanged, updated, or
newly created. For both user requests and uploaded ZIPs, compare requested
periods with each other and with retained baseline periods. Within the same
Calendar Name and Calendar Type, two periods cannot use the same year and
period number, even when their dates do not overlap.

## Verifying Changes After Import

`reconcile` can report `PASS` only after the workflow has observed a successful
import and a later completed export from the same task and environment. Supply
`--verification-evidence <observations.json> --environment <selected-environment>
--base-url <selected-https-origin> --import-request-id <completed-import-request>`
along with the baseline, approved candidate, blueprint, requirements and export.
Missing, stale or mismatched evidence leaves verification `PENDING`; say that
saved changes have not yet been verified.

For an offline file comparison, use `reconcile --compare-only`. Its result is
`MATCH` or `DIFFERENT`, with `persistenceVerification=NOT_PERFORMED`. A file match
does not prove that an import occurred. Package building and import approval
are unchanged. See [Error Handling](ora-resource/ora_error_handling.md#reconciliation-evidence)
for the required observations.


## Uploaded Package Compatibility

Before reporting an uploaded ZIP as valid, supply `validate-upload` with
`--target-context <selected-target.json>` from the independently selected
workflow target. Both baseline and uploaded metadata must match its environment
and release. Read [Uploaded package compatibility](references/uploaded-package-compatibility.md)
for the contract and migration boundary. Matching schemas alone do not establish
source/target compatibility.


## Source Manifest Labels and Origins

When producing a source manifest or verifying post-import observations, follow
[Manifest labels and HTTPS origins](references/manifest-labels-and-origins.md).
A source manifest's environment must match its ZIP metadata; keep migration
destination information separate. Use a credential-free HTTPS origin without
an API path, query or fragment. A template-only label requires an empty package.
