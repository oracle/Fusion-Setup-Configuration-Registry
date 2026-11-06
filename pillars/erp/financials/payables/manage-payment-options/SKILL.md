---
skill_id: "erp.financials.payables.manage-payment-options"
name: "Manage Payment Options Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Payment Options under the Payables functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payables"
functional_area_code: "FIN_PAYABLES_DEPLOYED"
task_code: "AP_MANAGE_PAYMENT_OPTIONS"
task_name: "Manage Payment Options"
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
  - "erp.financials.payables.manage-invoice-options"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-payment-options/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-payment-options/current/"
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

# Manage Payment Options Setup Task Guidance

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_SYSTEM_PARAMETER::BuName, AP_SYSTEM_PARAMETER::EnterpriseId, AP_SYSTEM_PARAMETER::BankChargeBearer, AP_SYSTEM_PARAMETER::BankChargeDeductionTypeDes, AP_SYSTEM_PARAMETER::TermName -->
<!-- fscr-update-fields: AP_SYSTEM_PARAMETER::WhenToAccountPmt, AP_SYSTEM_PARAMETER::PostDatedPaymentsFlag, AP_SYSTEM_PARAMETER::AllowSupplierBankOverride, AP_SYSTEM_PARAMETER::PayDocCategoryOverride, AP_SYSTEM_PARAMETER::AllowPymtThirdPartyOvrd, AP_SYSTEM_PARAMETER::BankChargeBearer, AP_SYSTEM_PARAMETER::BankChargeDeductionTypeDes -->

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Payment Options` under `Payables`.

## Supported Operations

This task supports creating a new Payment Options setup row and updating an exact existing setup row. It does not support delete or end-date operations. Only the operation-specific fields documented in [Input Validation](ora-resource/ora_input_validation.md) and [Design Enforcement](ora-resource/ora_design_enforcement.md) are permitted; all other fields remain blocked.

## Task Behavior

Use this task to configure Payment-owned values for the shared Payables system
options row, including payment accounting timing, post-dated payment policy,
bank-charge responsibility, rate requirements, and payment terms. An update
preserves unrelated Invoice Options values; do not use this task to change
Invoice-owned settings.

- Build every candidate from the exact Manage Payment Options package and a
  fresh, uniquely matched business-unit baseline. Preserve the package root,
  CSV headers and order, and all baseline values except the Payment-owned
  values explicitly requested for change.
- Validate the resulting complete shared row with the Invoice Options field
  contract before preview. This protects Invoice-owned prerequisites and
  preservation rules. For creates, include the documented shared-row create
  defaults from Invoice Options in the blueprint, preview, and actual CSV.
  This does not authorize other Invoice-owned changes. Invoke only the sibling validator, not the full
  Invoice Options skill, to avoid a recursive workflow. Apply the same checks
  to uploaded ZIP rows. Check creates as complete proposed rows; for updates,
  combine the supplied changes with baseline values before checking. Report
  missing required fields or shared-row rule failures against the affected row.
- For an uploaded create ZIP, use `validate-upload --validation-context` with
  the saved build report for that exact ZIP and baseline. The report carries
  the existing lookup results. Check `SOBName` and `BaseCurrencyCode` against
  the business unit's resolved primary ledger; these are required CSV context,
  not requested changes. Missing or mismatched lookup results stop validation.
  Require the shared create defaults in the actual uploaded CSV; reject blank
  or conflicting cells instead of filling them during validation. Keep the ZIP
  unchanged and continue to enforce the shared required fields.
- Do not infer a Payment Options value from an export. Validate supplied values
  only against their documented field contract; preserve an omitted optional
  field exactly as it appears in the baseline. Only creates receive the shared
  documented defaults; updates never receive them. Do not add a CSV column that is
  absent from the exact task template.
- Before normalization, run `scripts/resolve_lookup_prerequisites.py` for an
  applicable read-only preflight. For a new shared row, it delegates the supplied
  `TermName` to the Invoice Options-owned resolver and carries the resulting
  receipt into normalization. This does not authorize Invoice-owned term changes
  on Payment updates or require a separate Invoice Options workflow/export.
  If the API responds successfully but finds no
  matching record, stop preparation and ask the user to correct the value. If a
  supporting lookup cannot be checked, keep the supplied value, record why the
  check was skipped, and allow preparation to continue. A new row must still
  stop if required BU/ledger values cannot be obtained. Follow the detailed
  response rules in `ora-resource/ora_reference_lookups.md`; Fusion performs the
  final check during the approved import.
- For Bank Charge Deduction Type, write `Standard`, `Negotiated`, or `None`
  in `BankChargeDeductionTypeDes`. The CSV takes the name; database codes
  `S`, `N`, and `X` are not valid values for this CSV field.
- Route every import through `core.data-loader` in FSM mode. A candidate still
  requires an immutable preview and explicit approval before submission.

## Setup Task Skill Contract

- task_code: `AP_MANAGE_PAYMENT_OPTIONS`
- task_name: `Manage Payment Options`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Payment Options` under `Payables`.

## Setup Task Metadata

- Task name: `Manage Payment Options`
- Task code: `AP_MANAGE_PAYMENT_OPTIONS`
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
- Setup task name: `Manage Payment Options`
- Setup task code: `AP_MANAGE_PAYMENT_OPTIONS`




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

`AP_SYSTEM_PARAMETER` is a shared row, but Invoice Options and Payment Options
own different fields. Before normalization, run
`scripts/resolve_lookup_prerequisites.py`. It performs the relevant read-only
Invoice Options check, records advisory results, and never writes to Fusion.

For every Payment Options create or update, validate the complete resulting row
against the Invoice Options contract. This ensures an update cannot bypass an
Invoice-owned prerequisite, default, or preservation rule. Conversely, an
Invoice Options update validates its resulting Payment-owned values with this
contract. An Invoice Options create validates only Payment values supplied by
the requester; it never adds optional Payment values. This dependency does not
mean that either task should guess or populate fields from the other page.
Invoke only the sibling validator, not the full Invoice Options skill, to avoid
a recursive workflow.

For one business unit, a single NLP request that includes both Payment Options
and Invoice Options changes is one shared-row transaction. Merge all requested
fields into one canonical `AP_SYSTEM_PARAMETER` row before candidate generation
and validate both contracts against it. When any Invoice Options field is
present, the Invoice Options package is the sole writer; do not generate or
submit a second Payment Options full-row package. Use this Payment Options
package only for a payment-only request.

Use the parent functional-area skill `erp.financials.payables` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

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


## Reference Lookup Evidence

When a design or uploaded ZIP uses lookup receipts, follow
[Reference evidence provenance](references/reference-evidence-provenance.md).
Keep the selected target separate from evidence, require matching environment
and HTTPS origin, and rerun preflight for missing, malformed, future, or
more-than-24-hour-old observations. The same provenance checks apply to
unavailable lookup warnings. An offline receipt does not authorize a live call
or prove that Fusion imported the ZIP.


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


## Sibling Runtime Dependency

Payment Options imports the Invoice Options descriptor and runtime for shared
AP_SYSTEM_PARAMETER validation and delegates lookup preflight to its resolver.
Invoice Options may call back only into the Payment field contract; it must not
recursively invoke the full Payment Options workflow or blueprint validator.

The sibling ID in `depends_on` is a required code/component dependency. Package
both skill folders, including their SKILL.md, e2e-adapter.json and script files,
under the same Payables parent directory. Preserve the sibling directory names
used by the loaders. The reciprocal declarations describe mutual runtime
requirements, not an execution order or a request to run both workflows.
Dependency collection should include each skill once. A missing sibling runtime
or descriptor blocks validation with an actionable error; do not replace it with
weaker local checks. Keep both components together when distributing this pair.
