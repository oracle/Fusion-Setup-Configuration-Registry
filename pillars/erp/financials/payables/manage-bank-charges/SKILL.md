---
skill_id: "erp.financials.payables.manage-bank-charges"
name: "Manage Bank Charges Setup Task Guidance"
description: "Prepares Bank Charges create and snapshot-bound update ZIPs, validates complete charge groups, and routes imports through Data Loader."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payables"
functional_area_code: "FIN_PAYABLES_DEPLOYED"
task_code: "ORA_AP_MANAGE_BANK_CHARGES"
task_name: "Manage Bank Charges"
parent_skill_id: "erp.financials.payables"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "hybrid"
owner_team: "ERP financials pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "snapshot_bound_update_request"
  - "post_import_export_observation"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "update_review"
  - "update_package"
  - "persistence_verification"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.setup-export.fsm-csv-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
  - "core.fusion-api.rest-api-client"
  - "core.auth.fusion-oauth-authentication"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-bank-charges/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-bank-charges/current/"
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
  - "Writes local preparation, comparison and export-observation artifacts."
  - "Approved post-import verification queries Core import status and starts/downloads a fresh task data export through Shared."
required_privileges:
  - "Fusion privileges and OAuth scope for task data export and Core Data Loader status retrieval."
---

# Manage Bank Charges Setup Task Guidance

## Purpose

Use this skill to prepare and validate Bank Charges setup changes and route
approved imports through the project Run Book. Use the parent
`erp.financials.payables` skill for functional-area scope and sequencing.

## Source-Backed Task Behavior

- The task adapter supports create and a snapshot-bound update route for one existing charge line. Its `update` command implements the procedure below to prepare and validate an update ZIP and review the complete expected state within the documented field and group limits. Generic keyed update commands remain unavailable because this task has no configured local row-index fields.
- Prepare an update from the selected records in a fresh export. Preserve the requested changes, original values, unspecified fields and untouched rows; do not turn the request into a create or apply create defaults. Knowledge of Oracle's internal record-matching algorithm is not a preparation or validation prerequisite.
- A bank-charge definition contains a header and charge lines. Validate and reconcile the complete group, including the CSV parent references.

## Workflow

Use the stages relevant to the request; local input assessment does not require
a live export.

1. Capture the requested operation, business values, target environment and project
   in the Run Book. Preserve the resolved dates when resuming existing intake.
2. Read the validation resources below and check the task-local registry and
   source rules using the execution checks below. Registry readiness is not a
   passed validation or import approval.
3. Obtain fresh exact-task state through `shared.setup-export.task-level-export`.
   Creation requires an absent-group assessment; an existing or ambiguous group
   requires an operation decision or further evidence.
4. For updates, use the update-preparation procedure below. For creates, use
   `scripts/fsm_task_adapter.py assess-intake` for local input checks.
   `scripts/prepare_charge_group_create.py` prepares create source or compares
   complete groups; it accepts successful reference evidence for every applicable
   lookup, recorded unavailable additional REST checks, or the existing explicit
   reference-verification waiver for offline intake. Record outcomes using the
   `reference_check_results` contract in `ora_reference_lookups.md`.
   `scripts/inspect_bank_charge_group.py` compares
   only All legal entities, banks and branches with one open-ended range and
   adapter-declared node sequences. Use each script's `--help` for arguments.
   Do not invent a waiver or infer identifiers from an unavailable API.
5. Use `shared.validation.setup-data-validator` and
   `shared.validation.reference-data-validator` for validation, then
   `core.data-loader` and its Task Hook for preview, approval of the exact
   candidate and import. Follow that contract for explicit check overrides.
6. Reconcile the complete requested group and preservation of baseline rows against
   a fresh export before declaring completion. Record the approved artifact,
   process identity, results and remaining blockers in the project workspace
   using the manifest's run and token-usage policies.
   Follow [post-import verification](references/readback-verification.md):
   matching file contents alone report `PENDING`; declare saved values verified
   only when `persistenceVerified` is true and the observation matches the current
   target, import request and exact files.

Use only the owning workflow's declared external routes. Stop on an uncertain
import outcome before retrying; follow the error-handling resource.
Before observing persistence, preflight the candidate hash, Core preflight and
initiation evidence, configured target and unused output paths. Redact execution
diagnostics: retain process identities, artifact hashes and the sanitized failure
stage; never record credentials, tokens or raw sensitive responses.

Use new, distinct paths for reports and generated artifacts; outputs must not
overwrite inputs or existing files. Package metadata must use an exact terminal
success status: `COMPLETE`, `COMPLETED`, `SUCCESS`, or `SUCCEEDED`
(case-insensitive). A package manifest's environment must match `ProcessEnv`,
and its base URL must be a valid HTTPS origin without a path, query, credentials,
or fragment.

## Additional REST Validation Availability

Use `core.fusion-api.rest-api-client` for the declared legal entity, currency,
bank, country and branch GET checks. Access failures, missing endpoints, timeouts
and service outages are `UNVERIFIED_API_UNAVAILABLE` warnings: preserve supplied
references and continue preparation and preview without a separate waiver.
The Run Book converts the core client's successful checks or sanitized failures into
`reference_check_results` using `ora_reference_lookups.md`. Supply this optional
array in create intake or the snapshot-bound update request; the offline scripts
do not call REST themselves. Warnings remain in the preparation review and must
be disclosed in shared validation and Data Loader review, without becoming an
additional-reference blocker or a claim that the reference passed.

Required CSV values, local choices, option/name consistency, amounts, dates,
complete-group checks, exact snapshot identity, Data Loader validation and
approval still apply. Completed lookups with no match, ambiguity or conflicting
values still require correction. Unavailable APIs cannot supply missing names,
codes or identifiers. No mutation or automatic submission is authorized here.

## Prepare an Update

Use [fsm_task_adapter.py](scripts/fsm_task_adapter.py) with its `update` command
to prepare changes to one existing charge line. It supports standard and
negotiated charges, start/end dates and payment amount endpoints within a
same-period, contiguous group. Header and flexfield changes need additional
preparation support.

Write request JSON containing `task.code`, `environment.name`,
`snapshot_sha256`, `target.header` and `target.line` (complete raw rows from
that export), and `changes` (only the requested fields). The script requires
exactly one matching parent and child. Omitted values remain unchanged;
`null` or `""` explicitly requests clearing only `EndDate` or `TransAmountTo`.
Explicit clears are written as blank CSV cells and checked during reconciliation.
Supply decimal amounts as JSON strings to preserve precision; integers are
also accepted, but floating-point JSON numbers are rejected.

Run `python3 scripts/fsm_task_adapter.py update --request request.json
--snapshot export.zip --package update.zip --output update-review.json` from this
task folder. The ZIP contains the selected
header and all its charge lines, preserves the export metadata and column order,
and changes only the requested values. Other groups are excluded from the ZIP.
The adapter reopens and validates the ZIP before publishing it; existing output
files and requests with no effective changes are rejected. The review records
the ZIP hash, original/proposed values and the complete expected saved state.

Omit `--package` for a review only. Use `--validate-package update.zip` to recheck
an existing package, or `--after later-export.zip` to compare the complete saved
state; missing, additional or unrelated changed rows fail comparison.

Use the ZIP and its `sha256` for Data Loader's source and Task Hook
`finalData.archiveSha256`. Complete the workflow's reference/rule checks, preview
and artifact approval before import. Refresh the export and repeat preparation
when current-state evidence is stale; the file hash does not establish freshness.

## Validation Resources

Before executing task rules, complete the Task-Local Execution Checks below
and read these task resources in order. These resources own the detailed business rules:

1. [Input validation](ora-resource/ora_input_validation.md): package shape, required fields, scalar checks and native flexfield type checks.
2. [Reference lookups](ora-resource/ora_reference_lookups.md): eligible legal entities, currencies, banks and branches.
3. [Dependency readiness](ora-resource/ora_dependency_readiness.md): prerequisites and unresolved evidence.
4. [Defaulting](ora-resource/ora_defaulting_rules.md): create defaults and preservation of explicit values.
5. [Design enforcement](ora-resource/ora_design_enforcement.md): lifecycle limits, parent assembly and charge ranges.
6. [Error handling](ora-resource/ora_error_handling.md): failures, approval, recovery and reconciliation requirements.
7. [Rule registry](ora-resource/ora_rule_registry.json): executable task-node ordering and readiness.

### Task-Local Execution Checks

Select the registry entry for `ORA_AP_MANAGE_BANK_CHARGES` / `Manage Bank Charges`.
Require task and reachable-node readiness `ready`, and verify the start node,
supported actions, prerequisite and transition targets, source headings and named
resolver definitions against the resources above. Stop on missing, `TBD` or
inconsistent contracts; do not repair the graph during a run. A readiness override
requires explicit user acceptance and a recorded warning under the owning workflow;
it cannot waive required inputs, safety checks or approval.

Start at `start_node`. Complete every declared prerequisite using its permitted
outcome, including the documented unavailable-REST warning path. Perform only the
node's declared action and route, record sanitized evidence, and follow its
declared transition. Stop if no outcome matches; finish only at a terminal node.
Lookups remain read-only, and defaults follow their documented conditions.

Mutation remains through `core.data-loader` after validation, immutable preview
and contextual approval of the exact environment, operation and artifact. A
material change requires renewed approval. Never automatically replay an uncertain
import; reconcile first. On resume, refresh stale evidence and approval. Record
task identity, request fingerprint, current Rule ID, completed outcomes, warnings,
blockers, verified side effects and the safe next step in the project run record.

<!-- fscr-supported-operations: create, update -->
<!-- fscr-update-fields: ORA_AP_BANK_CHARGE_LINE::BankChargeStandard, ORA_AP_BANK_CHARGE_LINE::BankChargeNegotiated, ORA_AP_BANK_CHARGE_LINE::StartDate, ORA_AP_BANK_CHARGE_LINE::EndDate, ORA_AP_BANK_CHARGE_LINE::TransAmountFrom, ORA_AP_BANK_CHARGE_LINE::TransAmountTo -->
<!-- fscr-create-fields: ORA_AP_BANK_CHARGE::Attribute1, ORA_AP_BANK_CHARGE::Attribute10, ORA_AP_BANK_CHARGE::Attribute11, ORA_AP_BANK_CHARGE::Attribute12, ORA_AP_BANK_CHARGE::Attribute13, ORA_AP_BANK_CHARGE::Attribute14, ORA_AP_BANK_CHARGE::Attribute15, ORA_AP_BANK_CHARGE::Attribute2, ORA_AP_BANK_CHARGE::Attribute3, ORA_AP_BANK_CHARGE::Attribute4, ORA_AP_BANK_CHARGE::Attribute5, ORA_AP_BANK_CHARGE::Attribute6, ORA_AP_BANK_CHARGE::Attribute7, ORA_AP_BANK_CHARGE::Attribute8, ORA_AP_BANK_CHARGE::Attribute9, ORA_AP_BANK_CHARGE::AttributeCategory, ORA_AP_BANK_CHARGE::AttributeDate1, ORA_AP_BANK_CHARGE::AttributeDate2, ORA_AP_BANK_CHARGE::AttributeDate3, ORA_AP_BANK_CHARGE::AttributeDate4, ORA_AP_BANK_CHARGE::AttributeDate5, ORA_AP_BANK_CHARGE::AttributeNumber1, ORA_AP_BANK_CHARGE::AttributeNumber2, ORA_AP_BANK_CHARGE::AttributeNumber3, ORA_AP_BANK_CHARGE::AttributeNumber4, ORA_AP_BANK_CHARGE::AttributeNumber5, ORA_AP_BANK_CHARGE::CurrencyCode, ORA_AP_BANK_CHARGE::LegalEntityIdentifier, ORA_AP_BANK_CHARGE::LegalEntityName, ORA_AP_BANK_CHARGE::ReceivingBankCountry, ORA_AP_BANK_CHARGE::ReceivingBankName, ORA_AP_BANK_CHARGE::ReceivingBankNumber, ORA_AP_BANK_CHARGE::ReceivingBankOption, ORA_AP_BANK_CHARGE::ReceivingBranchName, ORA_AP_BANK_CHARGE::ReceivingBranchNumber, ORA_AP_BANK_CHARGE::ReceivingBranchOption, ORA_AP_BANK_CHARGE::SettlementPriorityDisplay, ORA_AP_BANK_CHARGE::TransferringBankCountry, ORA_AP_BANK_CHARGE::TransferringBankName, ORA_AP_BANK_CHARGE::TransferringBankNumber, ORA_AP_BANK_CHARGE::TransferringBankOption, ORA_AP_BANK_CHARGE::TransferringBranchName, ORA_AP_BANK_CHARGE::TransferringBranchNumber, ORA_AP_BANK_CHARGE::TransferringBranchOption, ORA_AP_BANK_CHARGE_LINE::Attribute1, ORA_AP_BANK_CHARGE_LINE::Attribute10, ORA_AP_BANK_CHARGE_LINE::Attribute11, ORA_AP_BANK_CHARGE_LINE::Attribute12, ORA_AP_BANK_CHARGE_LINE::Attribute13, ORA_AP_BANK_CHARGE_LINE::Attribute14, ORA_AP_BANK_CHARGE_LINE::Attribute15, ORA_AP_BANK_CHARGE_LINE::Attribute2, ORA_AP_BANK_CHARGE_LINE::Attribute3, ORA_AP_BANK_CHARGE_LINE::Attribute4, ORA_AP_BANK_CHARGE_LINE::Attribute5, ORA_AP_BANK_CHARGE_LINE::Attribute6, ORA_AP_BANK_CHARGE_LINE::Attribute7, ORA_AP_BANK_CHARGE_LINE::Attribute8, ORA_AP_BANK_CHARGE_LINE::Attribute9, ORA_AP_BANK_CHARGE_LINE::AttributeCategory, ORA_AP_BANK_CHARGE_LINE::AttributeDate1, ORA_AP_BANK_CHARGE_LINE::AttributeDate2, ORA_AP_BANK_CHARGE_LINE::AttributeDate3, ORA_AP_BANK_CHARGE_LINE::AttributeDate4, ORA_AP_BANK_CHARGE_LINE::AttributeDate5, ORA_AP_BANK_CHARGE_LINE::AttributeNumber1, ORA_AP_BANK_CHARGE_LINE::AttributeNumber2, ORA_AP_BANK_CHARGE_LINE::AttributeNumber3, ORA_AP_BANK_CHARGE_LINE::AttributeNumber4, ORA_AP_BANK_CHARGE_LINE::AttributeNumber5, ORA_AP_BANK_CHARGE_LINE::BankChargeNegotiated, ORA_AP_BANK_CHARGE_LINE::BankChargeStandard, ORA_AP_BANK_CHARGE_LINE::EndDate, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.CurrencyCode, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.LegalEntityIdentifier, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.LegalEntityName, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.ReceivingBankCountry, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.ReceivingBankName, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.ReceivingBankNumber, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.ReceivingBankOption, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.ReceivingBranchName, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.ReceivingBranchNumber, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.ReceivingBranchOption, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.SettlementPriorityDisplay, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.TransferringBankCountry, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.TransferringBankName, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.TransferringBankNumber, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.TransferringBankOption, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.TransferringBranchName, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.TransferringBranchNumber, ORA_AP_BANK_CHARGE_LINE::ORA_AP_BANK_CHARGE.TransferringBranchOption, ORA_AP_BANK_CHARGE_LINE::StartDate, ORA_AP_BANK_CHARGE_LINE::TransAmountFrom, ORA_AP_BANK_CHARGE_LINE::TransAmountTo -->
