---
skill_id: "erp.financials.payables.manage-interest-rates"
name: "Manage Interest Rates Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Interest Rates under the Payables functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payables"
functional_area_code: "FIN_PAYABLES_DEPLOYED"
task_code: "AP_MANAGE_INTEREST_RATES"
task_name: "Manage Interest Rates"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-interest-rates/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-interest-rates/current/"
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

# Manage Interest Rates Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Interest Rates` under `Payables`.

## Supported Operations

This task supports creating an interest-rate period and updating an existing period's To Date (`EndDate`) or Rate (%) (`AnnualInterestRate`) through an exact-task FSM CSV import. `StartDate` (UI From Date) identifies the period and is preserved on update. Physical deletion, a separate end-date operation, and changing `StartDate` as an update are not supported by this skill. See [Input Validation](ora-resource/ora_input_validation.md) and [Design Enforcement](ora-resource/ora_design_enforcement.md) for the operation-specific gates.

## Task Behavior

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_INTEREST_PERIOD::StartDate, AP_INTEREST_PERIOD::EndDate, AP_INTEREST_PERIOD::AnnualInterestRate -->
<!-- fscr-update-fields: AP_INTEREST_PERIOD::EndDate, AP_INTEREST_PERIOD::AnnualInterestRate -->

- Build from the exact `AP_MANAGE_INTEREST_RATES` template with `AP_INTEREST_PERIOD.csv` and `ASM_SETUP_CSV_METADATA.xml`. Keep the eight ordered CSV columns and full row width; reject another task's metadata or malformed rows.
- For this task, `AP_INTEREST_PERIOD.StartDate` is the unique import alternate key, shown as From Date in the UI. The entity declares `AltKey` on `StartDate`, and the task import resolves rows through `AltKey`. Match exactly one row in a fresh same-task export by calendar date, not by row position, To Date, or Rate (%). Keep `StartDate` unchanged for an update.
- A create requires explicit From Date, To Date, and Rate (%). An update changes only a requested `EndDate` or `AnnualInterestRate`; retain other values on that period and every unspecified period. An omitted CSV row is not a delete request. A new From Date is a different identity and must be designed separately.
- Require From Date (`StartDate`) to be on or before To Date (`EndDate`), including a one-day period when they are equal. Reject a period when From Date is after To Date or when its dates overlap another period. Rate (%) must be numeric and between 0 and 100 inclusive. The UI has shown AP-810412 for an overlap, a required-value error for blank Rate, and AP-810443 for an out-of-range Rate.
- Keep the five exported audit columns blank in import candidates; they are read-only system fields. Revalidate this serialization if the release or template changes.
- Route immutable preview, candidate-specific approval, import, monitoring, and fresh-export reconciliation through `core.data-loader`. A ZIP, UI screenshot, or successful process status alone does not prove the intended persisted values (task catalog and core.data-loader contract).

## Rule enforcement

| Rule group | Enforcing step |
|---|---|
| Exact task ZIP, metadata, headers, row width, source release and schema | `scripts/fsm_task_adapter.py` package reader, source-pair check, and blueprint validation. A changed release blocks normalization until the audit-cell import behavior is revalidated and the task evidence release is updated. |
| Create values, numeric Rate (%) 0–100, calendar dates, date order, inclusive overlap, StartDate identity, supported fields, audit-cell prohibition, and preservation | `scripts/fsm_task_adapter.py` normalization and candidate validation. The private tests in `noship/tests/manage-interest-rates` exercise the rejection and boundary cases. |
| Fresh same-task export, immutable candidate review, import approval, uncertain submission handling, and post-import fresh-export reconciliation | The selected `shared.setup-export.task-level-export`, `core.data-loader`, and `test-fsm-task-e2e-noship` workflows. These require live workflow evidence and cannot be established from an offline ZIP alone. |

`ora-resource/ora_rule_registry.json` describes the task workflow; it does not execute validation by itself. Stop if the applicable enforcing step has not run or its evidence is missing.

## UI wording to persisted and package fields

| UI wording | FSM CSV attribute | Use |
|---|---|---|
| From Date | `StartDate` | Required on create; unique match key preserved on update. |
| To Date | `EndDate` | Required on create; supported update field. |
| Rate (%) | `AnnualInterestRate` | Required on create; supported update field, 0 through 100 inclusive. |

`CreatedBy`, `CreationDate`, `LastUpdatedBy`, `LastUpdateDate`, and `LastUpdateLogin` are package audit columns, not user-editable values.

## Setup Task Skill Contract

- task_code: `AP_MANAGE_INTEREST_RATES`
- task_name: `Manage Interest Rates`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Interest Rates` under `Payables`.

## Setup Task Metadata

- Task name: `Manage Interest Rates`
- Task code: `AP_MANAGE_INTEREST_RATES`
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
- Setup task name: `Manage Interest Rates`
- Setup task code: `AP_MANAGE_INTEREST_RATES`




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

## Task-local resources

Read `ora-resource/ora_input_validation.md` for request fields and identity checks, `ora-resource/ora_dependency_readiness.md` for current-export prerequisites, `ora-resource/ora_defaulting_rules.md` for the absence of business defaults, `ora-resource/ora_design_enforcement.md` for date and key gates, and `ora-resource/ora_error_handling.md` for rejection and retry handling. The compiled `ora-resource/ora_rule_registry.json` is the task-node execution contract. `e2e-adapter.json` and `scripts/fsm_task_adapter.py` implement the customer-facing offline candidate and reconciliation path; private regression material is under the functional area's `noship/tests/manage-interest-rates` directory.

## Supported Data Handling

When updating Rate (%) (`AnnualInterestRate`), preserve From Date (`StartDate`), To Date (`EndDate`), and unrelated records unless a supported field change is explicitly requested. Leave system-managed audit cells blank. Revalidate serialization when the task template or release changes.

No external reference resolver or task-specific business default was found for the eight package fields. Do not invent a REST lookup or default value. Physical deletion and changing an existing period's From Date are outside the supported FSM import contract; the UI behavior for changing From Date has not been established here.

## Prepared ZIP validation parity

Apply the same task business rules to NLP requests and prepared/uploaded ZIPs before approval: operation and field ownership, create/update matching, parent and required-child rules, lookup outcomes, allowed codes, required values, dates, limits, audit rules and preservation. ZIP structure validation alone is insufficient. Use a fresh exact-task baseline and an explicit operation design; unresolved intent or missing evidence blocks validation rather than assuming an upsert or inferring parent creation. The task-local `validate` command requires the template, baseline, blueprint and requirements and checks actual package values against that validated design. Do not substitute `manifest` inspection for business validation.

Treat the uploaded archive as immutable input. Report member, record key, field and rule for identified problems; never default, normalize labels, clear audit cells, add parents/children, remove rows or rebuild the ZIP during validation. Report files must be distinct from every input and must not overwrite existing files. A correction requires an explicit revised request or artifact, a separate candidate, renewed validation and the normal artifact-bound approval. A hash or completed import job alone does not establish business validity.

## Final-state batch validation

Before import, start from a fresh, sufficiently complete exact-task baseline and overlay all explicitly requested creates and updates in memory. Preserve omitted fields and retained records; omission is not deletion. Validate the resulting affected state as one batch, comparing changed/new records with one another and with retained records. Row-by-row success is insufficient. Evaluate final values rather than transient operation order, and reject duplicate target operations rather than choosing a last writer. Missing baseline coverage or an unresolved applicable rule blocks the affected batch; do not fabricate prerequisite records or remove conflicting rows to make it pass.

Overlay every EndDate update and create before checking inclusive date-range intersections, including retained periods. A range shortened by another operation in the same batch is evaluated at its final dates, regardless of operation order. Rate-only changes do not create an unrelated historical repair requirement. Both NLP and prepared-ZIP paths must pass this gate before approval/import. For ZIPs, compare against the proposed final state without changing the upload; identify the conflicting record keys and applicable rule in diagnostics. Do not require unrelated baseline defects to be repaired unless the requested change depends on them.

## Input, target and evidence boundaries

- Keep source ZIPs, baselines, requests, contracts and existing artifacts immutable. Resolve output paths and check symlink/hardlink aliases before writing; exclusively create every output, including failure reports. Reject collisions among all outputs before starting an action. A late file appearing after preflight must not be overwritten.
- Use the independently selected Fusion environment and credential-free HTTPS origin as the target. The authentication profile is a separate input; do not derive an environment by stripping authentication labels. Match `ProcessEnv` to the selected environment, and match template/baseline environment and release. A matching ZIP hash cannot establish its own trusted target or reference evidence.
- Use the active export service's documented successful statuses (`COMPLETED` and `COMPLETED_WARNINGS` in the reviewed service); retain warnings for review. A downloadable ZIP, completed request or substring such as `INCOMPLETE` or `COMPLETED_ERRORS` is not process success. Validate real boolean template flags and reject a template-only label on populated CSV data; an empty current-data export is still possible.
- A URL must be an HTTPS origin without credentials, path, query or fragment. Do not accept a malformed host or use an evidence-supplied origin as the trusted target. Check package identity, member/header/type/path contracts and the supported release compatibility policy independently of labels.
- Preserve every unrequested business field and retained row on updates. `preserveOtherValues` and `preserveUnspecifiedRows` cannot disable this rule. Only explicitly requested changes and source-backed, previewed dependent clears/defaults may differ. Validate uploaded ZIPs against that same effective design without rewriting the upload.
- At the live workflow gate, parse timezone-aware reference/import/readback timestamps, apply that workflow's actual freshness policy and require the verification export to follow the completed import. Reject malformed, timezone-free, stale, future or out-of-order evidence. Offline file comparison and synthetic/captured readback do not prove live persistence; keep verification pending until the supported workflow supplies valid target-bound evidence. Do not invent a time-to-live or persist evidence prohibited by the active Data Loader contract.
- Validate generated node sequences according to a reviewed sequencing policy; keep business identity, XML grouping, headers, types and relationships authoritative. Do not renumber exports or guess XML-file groups to bypass a compatibility gap.

The task-local offline adapter enforces exclusive output creation, exact export statuses, selected-environment manifest checks, strict origin/template labels, template/baseline compatibility and mandatory update preservation. Its reconciliation result remains `PENDING` with `persistenceVerified=false`; a matching comparison is separate from live verification. The adapter does not execute live reference calls or submit imports. Existing source-backed operation, field and default contracts remain binding.

## Selected Fusion target and authentication profile

Before preparing exports or task data, retain the independently confirmed Fusion
environment name and credential-free HTTPS origin in the project target context.
Retain the selected OAuth `environment` value separately as the authentication
profile. The names may be unrelated (for example, profile `DEV` and Fusion
environment `example-fusion`). Reuse a previously confirmed target; ask for its
actual identity only when it is missing or ambiguous. Never derive it by removing
a profile suffix or guessing from a hostname, ZIP or reference receipt.

Pass the actual selected Fusion name to task manifest/target-validation inputs,
and require it to match export `ProcessEnv`. Require the selected origin to match
the authenticated configured origin. Compare the login profile only with the
profile bound to the Data Loader preflight; do not compare it with `ProcessEnv`.
Keep task, release/schema, Run Book, archive-integrity and approval checks intact.
If a workflow accepts `referenceContext`, supply the separately selected target
there; do not invent that CLI option for adapters that do not declare it. This
identity handling grants no additional execution or import capability.
