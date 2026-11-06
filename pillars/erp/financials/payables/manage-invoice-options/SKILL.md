---
skill_id: "erp.financials.payables.manage-invoice-options"
name: "Manage Invoice Options Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Invoice Options under the Payables functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payables"
functional_area_code: "FIN_PAYABLES_DEPLOYED"
task_code: "AP_MANAGE_INVOICE_OPTIONS"
task_name: "Manage Invoice Options"
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
  - "erp.financials.payables.manage-payment-options"
uses_core:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.ucm-rest-client"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-invoice-options/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-invoice-options/current/"
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

# Manage Invoice Options Setup Task Guidance

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_SYSTEM_PARAMETER::BuName, AP_SYSTEM_PARAMETER::InterestSegments, AP_SYSTEM_PARAMETER::BaseCurrencyCode, AP_SYSTEM_PARAMETER::InvoiceCurrencyCode, AP_SYSTEM_PARAMETER::PaymentCurrencyCode, AP_SYSTEM_PARAMETER::AlwaysTakeDiscFlag, AP_SYSTEM_PARAMETER::PayDateBasisLookupCode, AP_SYSTEM_PARAMETER::AddDaysSettlementDate, AP_SYSTEM_PARAMETER::DaysBetweenCheckCycles, AP_SYSTEM_PARAMETER::FederalIdentificationNum, AP_SYSTEM_PARAMETER::UpdatePaySiteFlag, AP_SYSTEM_PARAMETER::GlDateFromReceiptFlag, AP_SYSTEM_PARAMETER::DiscIsInvLessTaxFlag, AP_SYSTEM_PARAMETER::AccountingMethodOption, AP_SYSTEM_PARAMETER::OnlinePrintFlag, AP_SYSTEM_PARAMETER::EftUserNumber, AP_SYSTEM_PARAMETER::MaxOutlay, AP_SYSTEM_PARAMETER::VendorPayGroupLookupCode, AP_SYSTEM_PARAMETER::RequireTaxEntryFlag, AP_SYSTEM_PARAMETER::PostDatedPaymentsFlag, AP_SYSTEM_PARAMETER::SecondaryAccountingMethod, AP_SYSTEM_PARAMETER::InterestToleranceAmount, AP_SYSTEM_PARAMETER::TermsDateBasis, AP_SYSTEM_PARAMETER::LiabilityPostLookupCode, AP_SYSTEM_PARAMETER::DiscountDistributionMethod, AP_SYSTEM_PARAMETER::CombinedFilingFlag, AP_SYSTEM_PARAMETER::IncomeTaxRegion, AP_SYSTEM_PARAMETER::IncomeTaxRegionFlag, AP_SYSTEM_PARAMETER::AllowFinalMatchFlag, AP_SYSTEM_PARAMETER::AllowFlexOverrideFlag, AP_SYSTEM_PARAMETER::AllowPaidInvoiceAdjust, AP_SYSTEM_PARAMETER::UssglTransactionCode, AP_SYSTEM_PARAMETER::UssglTrxCodeContext, AP_SYSTEM_PARAMETER::InvDocCategoryOverride, AP_SYSTEM_PARAMETER::PayDocCategoryOverride, AP_SYSTEM_PARAMETER::VendorAutoIntDefault, AP_SYSTEM_PARAMETER::TransferDescFlexFlag, AP_SYSTEM_PARAMETER::AllowAwtFlag, AP_SYSTEM_PARAMETER::AllowAwtOverride, AP_SYSTEM_PARAMETER::CreateAwtDistsType, AP_SYSTEM_PARAMETER::CreateAwtInvoicesType, AP_SYSTEM_PARAMETER::AwtIncludeDiscountAmt, AP_SYSTEM_PARAMETER::AwtIncludeTaxAmt, AP_SYSTEM_PARAMETER::AutoCreateFreightFlag, AP_SYSTEM_PARAMETER::GlobalAttributeCategory, AP_SYSTEM_PARAMETER::GlobalAttribute1, AP_SYSTEM_PARAMETER::GlobalAttribute2, AP_SYSTEM_PARAMETER::GlobalAttribute3, AP_SYSTEM_PARAMETER::GlobalAttribute4, AP_SYSTEM_PARAMETER::GlobalAttribute5, AP_SYSTEM_PARAMETER::GlobalAttribute6, AP_SYSTEM_PARAMETER::GlobalAttribute7, AP_SYSTEM_PARAMETER::GlobalAttribute8, AP_SYSTEM_PARAMETER::GlobalAttribute9, AP_SYSTEM_PARAMETER::GlobalAttribute10, AP_SYSTEM_PARAMETER::GlobalAttribute11, AP_SYSTEM_PARAMETER::GlobalAttribute12, AP_SYSTEM_PARAMETER::GlobalAttribute13, AP_SYSTEM_PARAMETER::GlobalAttribute14, AP_SYSTEM_PARAMETER::GlobalAttribute15, AP_SYSTEM_PARAMETER::GlobalAttribute16, AP_SYSTEM_PARAMETER::GlobalAttribute17, AP_SYSTEM_PARAMETER::GlobalAttribute18, AP_SYSTEM_PARAMETER::GlobalAttribute19, AP_SYSTEM_PARAMETER::GlobalAttribute20, AP_SYSTEM_PARAMETER::AllowSupplierBankOverride, AP_SYSTEM_PARAMETER::UseBankChargeFlag, AP_SYSTEM_PARAMETER::BankChargeBearer, AP_SYSTEM_PARAMETER::MrcBaseCurrencyCode, AP_SYSTEM_PARAMETER::GainLossCalcLevel, AP_SYSTEM_PARAMETER::WhenToAccountPmt, AP_SYSTEM_PARAMETER::FutureDatedPmtLiabRelief, AP_SYSTEM_PARAMETER::GlTransferAllowOverride, AP_SYSTEM_PARAMETER::GlTransferMode, AP_SYSTEM_PARAMETER::GlTransferSubmitJournalImp, AP_SYSTEM_PARAMETER::IncludeReportingSob, AP_SYSTEM_PARAMETER::ApprovalWorkflowFlag, AP_SYSTEM_PARAMETER::AllowForceApprovalFlag, AP_SYSTEM_PARAMETER::ValidateBeforeApprovalFlag, AP_SYSTEM_PARAMETER::XmlPaymentsAutoConfirmFlag, AP_SYSTEM_PARAMETER::BuildPrepaymentAccountsFlag, AP_SYSTEM_PARAMETER::Enable1099OnAwtFlag, AP_SYSTEM_PARAMETER::ApprovalTiming, AP_SYSTEM_PARAMETER::ReceiptAcceptanceDays, AP_SYSTEM_PARAMETER::PaymentPriority, AP_SYSTEM_PARAMETER::ExcludeFreightFromDiscount, AP_SYSTEM_PARAMETER::AutoCalculateInterestFlag, AP_SYSTEM_PARAMETER::ProrateIntInvAcrossDists, AP_SYSTEM_PARAMETER::RequireInvoiceGroupFlag, AP_SYSTEM_PARAMETER::EmployeePaymentPriority, AP_SYSTEM_PARAMETER::EmployeePayGroupLookupCode, AP_SYSTEM_PARAMETER::SsInvoiceBackdatingFlag, AP_SYSTEM_PARAMETER::SsLimitToSinglePoFlag, AP_SYSTEM_PARAMETER::SsUpriceChangeForQtymatch, AP_SYSTEM_PARAMETER::SOBName, AP_SYSTEM_PARAMETER::TermName, AP_SYSTEM_PARAMETER::EmployeeTermName, AP_SYSTEM_PARAMETER::PrepaymentTermName, AP_SYSTEM_PARAMETER::ToleranceName, AP_SYSTEM_PARAMETER::ServicesToleranceName, AP_SYSTEM_PARAMETER::AwtName, AP_SYSTEM_PARAMETER::EnterpriseId, AP_SYSTEM_PARAMETER::PrepaymentAvailableMesgFlag, AP_SYSTEM_PARAMETER::RecalcPayScheduleFlag, AP_SYSTEM_PARAMETER::BudgetDateBasis, AP_SYSTEM_PARAMETER::OverrideMatchRejectionFlag, AP_SYSTEM_PARAMETER::RouteInterfaceRejectionFlag, AP_SYSTEM_PARAMETER::AllowInvThirdPartyOvrd, AP_SYSTEM_PARAMETER::AllowPymtThirdPartyOvrd, AP_SYSTEM_PARAMETER::RoutingFlag, AP_SYSTEM_PARAMETER::AttachmentMandatorySsFlag, AP_SYSTEM_PARAMETER::DisallowAttachmentDelFlag, AP_SYSTEM_PARAMETER::BankChargeDeductionTypeDes, AP_SYSTEM_PARAMETER::ReleaseDupInvoiceHoldFlag, AP_SYSTEM_PARAMETER::SsQtyMatchOverbillFlag, AP_SYSTEM_PARAMETER::SsAmtMatchOverbillFlag, AP_SYSTEM_PARAMETER::EscheatmentEligibilityPeriod, AP_SYSTEM_PARAMETER::AccountDefaultBasisCodeDes -->
<!-- fscr-update-fields: AP_SYSTEM_PARAMETER::InterestSegments, AP_SYSTEM_PARAMETER::BaseCurrencyCode, AP_SYSTEM_PARAMETER::InvoiceCurrencyCode, AP_SYSTEM_PARAMETER::PaymentCurrencyCode, AP_SYSTEM_PARAMETER::AlwaysTakeDiscFlag, AP_SYSTEM_PARAMETER::PayDateBasisLookupCode, AP_SYSTEM_PARAMETER::AddDaysSettlementDate, AP_SYSTEM_PARAMETER::DaysBetweenCheckCycles, AP_SYSTEM_PARAMETER::FederalIdentificationNum, AP_SYSTEM_PARAMETER::UpdatePaySiteFlag, AP_SYSTEM_PARAMETER::GlDateFromReceiptFlag, AP_SYSTEM_PARAMETER::DiscIsInvLessTaxFlag, AP_SYSTEM_PARAMETER::AccountingMethodOption, AP_SYSTEM_PARAMETER::OnlinePrintFlag, AP_SYSTEM_PARAMETER::EftUserNumber, AP_SYSTEM_PARAMETER::MaxOutlay, AP_SYSTEM_PARAMETER::VendorPayGroupLookupCode, AP_SYSTEM_PARAMETER::RequireTaxEntryFlag, AP_SYSTEM_PARAMETER::PostDatedPaymentsFlag, AP_SYSTEM_PARAMETER::SecondaryAccountingMethod, AP_SYSTEM_PARAMETER::InterestToleranceAmount, AP_SYSTEM_PARAMETER::TermsDateBasis, AP_SYSTEM_PARAMETER::LiabilityPostLookupCode, AP_SYSTEM_PARAMETER::DiscountDistributionMethod, AP_SYSTEM_PARAMETER::CombinedFilingFlag, AP_SYSTEM_PARAMETER::IncomeTaxRegion, AP_SYSTEM_PARAMETER::IncomeTaxRegionFlag, AP_SYSTEM_PARAMETER::AllowFinalMatchFlag, AP_SYSTEM_PARAMETER::AllowFlexOverrideFlag, AP_SYSTEM_PARAMETER::AllowPaidInvoiceAdjust, AP_SYSTEM_PARAMETER::UssglTransactionCode, AP_SYSTEM_PARAMETER::UssglTrxCodeContext, AP_SYSTEM_PARAMETER::InvDocCategoryOverride, AP_SYSTEM_PARAMETER::PayDocCategoryOverride, AP_SYSTEM_PARAMETER::VendorAutoIntDefault, AP_SYSTEM_PARAMETER::TransferDescFlexFlag, AP_SYSTEM_PARAMETER::AllowAwtFlag, AP_SYSTEM_PARAMETER::AllowAwtOverride, AP_SYSTEM_PARAMETER::CreateAwtDistsType, AP_SYSTEM_PARAMETER::CreateAwtInvoicesType, AP_SYSTEM_PARAMETER::AwtIncludeDiscountAmt, AP_SYSTEM_PARAMETER::AwtIncludeTaxAmt, AP_SYSTEM_PARAMETER::AutoCreateFreightFlag, AP_SYSTEM_PARAMETER::GlobalAttributeCategory, AP_SYSTEM_PARAMETER::GlobalAttribute1, AP_SYSTEM_PARAMETER::GlobalAttribute2, AP_SYSTEM_PARAMETER::GlobalAttribute3, AP_SYSTEM_PARAMETER::GlobalAttribute4, AP_SYSTEM_PARAMETER::GlobalAttribute5, AP_SYSTEM_PARAMETER::GlobalAttribute6, AP_SYSTEM_PARAMETER::GlobalAttribute7, AP_SYSTEM_PARAMETER::GlobalAttribute8, AP_SYSTEM_PARAMETER::GlobalAttribute9, AP_SYSTEM_PARAMETER::GlobalAttribute10, AP_SYSTEM_PARAMETER::GlobalAttribute11, AP_SYSTEM_PARAMETER::GlobalAttribute12, AP_SYSTEM_PARAMETER::GlobalAttribute13, AP_SYSTEM_PARAMETER::GlobalAttribute14, AP_SYSTEM_PARAMETER::GlobalAttribute15, AP_SYSTEM_PARAMETER::GlobalAttribute16, AP_SYSTEM_PARAMETER::GlobalAttribute17, AP_SYSTEM_PARAMETER::GlobalAttribute18, AP_SYSTEM_PARAMETER::GlobalAttribute19, AP_SYSTEM_PARAMETER::GlobalAttribute20, AP_SYSTEM_PARAMETER::AllowSupplierBankOverride, AP_SYSTEM_PARAMETER::UseBankChargeFlag, AP_SYSTEM_PARAMETER::BankChargeBearer, AP_SYSTEM_PARAMETER::MrcBaseCurrencyCode, AP_SYSTEM_PARAMETER::GainLossCalcLevel, AP_SYSTEM_PARAMETER::WhenToAccountPmt, AP_SYSTEM_PARAMETER::FutureDatedPmtLiabRelief, AP_SYSTEM_PARAMETER::GlTransferAllowOverride, AP_SYSTEM_PARAMETER::GlTransferMode, AP_SYSTEM_PARAMETER::GlTransferSubmitJournalImp, AP_SYSTEM_PARAMETER::IncludeReportingSob, AP_SYSTEM_PARAMETER::ApprovalWorkflowFlag, AP_SYSTEM_PARAMETER::AllowForceApprovalFlag, AP_SYSTEM_PARAMETER::ValidateBeforeApprovalFlag, AP_SYSTEM_PARAMETER::XmlPaymentsAutoConfirmFlag, AP_SYSTEM_PARAMETER::BuildPrepaymentAccountsFlag, AP_SYSTEM_PARAMETER::Enable1099OnAwtFlag, AP_SYSTEM_PARAMETER::ApprovalTiming, AP_SYSTEM_PARAMETER::ReceiptAcceptanceDays, AP_SYSTEM_PARAMETER::PaymentPriority, AP_SYSTEM_PARAMETER::ExcludeFreightFromDiscount, AP_SYSTEM_PARAMETER::AutoCalculateInterestFlag, AP_SYSTEM_PARAMETER::ProrateIntInvAcrossDists, AP_SYSTEM_PARAMETER::RequireInvoiceGroupFlag, AP_SYSTEM_PARAMETER::EmployeePaymentPriority, AP_SYSTEM_PARAMETER::EmployeePayGroupLookupCode, AP_SYSTEM_PARAMETER::SsInvoiceBackdatingFlag, AP_SYSTEM_PARAMETER::SsLimitToSinglePoFlag, AP_SYSTEM_PARAMETER::SsUpriceChangeForQtymatch, AP_SYSTEM_PARAMETER::SOBName, AP_SYSTEM_PARAMETER::TermName, AP_SYSTEM_PARAMETER::EmployeeTermName, AP_SYSTEM_PARAMETER::PrepaymentTermName, AP_SYSTEM_PARAMETER::ToleranceName, AP_SYSTEM_PARAMETER::ServicesToleranceName, AP_SYSTEM_PARAMETER::AwtName, AP_SYSTEM_PARAMETER::EnterpriseId, AP_SYSTEM_PARAMETER::PrepaymentAvailableMesgFlag, AP_SYSTEM_PARAMETER::RecalcPayScheduleFlag, AP_SYSTEM_PARAMETER::BudgetDateBasis, AP_SYSTEM_PARAMETER::OverrideMatchRejectionFlag, AP_SYSTEM_PARAMETER::RouteInterfaceRejectionFlag, AP_SYSTEM_PARAMETER::AllowInvThirdPartyOvrd, AP_SYSTEM_PARAMETER::AllowPymtThirdPartyOvrd, AP_SYSTEM_PARAMETER::RoutingFlag, AP_SYSTEM_PARAMETER::AttachmentMandatorySsFlag, AP_SYSTEM_PARAMETER::DisallowAttachmentDelFlag, AP_SYSTEM_PARAMETER::BankChargeDeductionTypeDes, AP_SYSTEM_PARAMETER::ReleaseDupInvoiceHoldFlag, AP_SYSTEM_PARAMETER::SsQtyMatchOverbillFlag, AP_SYSTEM_PARAMETER::SsAmtMatchOverbillFlag, AP_SYSTEM_PARAMETER::EscheatmentEligibilityPeriod, AP_SYSTEM_PARAMETER::AccountDefaultBasisCodeDes -->

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Invoice Options` under `Payables`.

## Supported Operations

This task supports creating a new Invoice Options setup row and updating an exact existing setup row. It does not support delete or end-date operations. Only the operation-specific fields documented in [Input Validation](ora-resource/ora_input_validation.md) and [Design Enforcement](ora-resource/ora_design_enforcement.md) are permitted; all other fields remain blocked.

## Task Behavior

- Use the exact `AP_SYSTEM_PARAMETER` package and CSV header contract. The
  supported create and update fields are defined by the local resources and
  adapter.

- Keep the exact `AP_SYSTEM_PARAMETER` package root
  (`/SystemOptionVO/SystemOptionVORow`) and the current template's header order
  and field count. Do not create a replacement schema. For a create, find the
  business unit in `finBusinessUnitsLOV`, use its `PrimaryLedgerId` to find the
  ledger in `ledgersLOV`, and write that ledger name to `SOBName`.
  For `EnterpriseId`, use (in order): the value explicitly requested for that
  row, the current-run default, or the fresh FSM export when it has exactly one
  nonblank value. Record this choice as `enterpriseIdResolution`. An update
  keeps the value from its uniquely matched export row. Fusion then resolves
  `BuName` and `EnterpriseId` to `OrgId`.
- The three payment-term fields are separate defaults. In the CSV, the Payment
  Request Payment Terms control is `EmployeeTermName`. Check each supplied name
  with the read-only `payablesPaymentTerms` service and keep the result as
  evidence only; do not choose an ID from multiple results. On import, Fusion
  resolves `TermName`, `PrepaymentTermName`, and `EmployeeTermName` to their
  corresponding IDs. A missing value is reported as an import dependency.
- Before normalization, run `scripts/resolve_lookup_prerequisites.py` for any
  populated page lookup fields. The adapter checks fixed system values locally.
  It preserves customer-controlled values and lets Fusion validate them during
  the separately approved import.
- Route every import through `core.data-loader` in FSM mode. A static artifact
  never authorizes an import: Data Loader still requires an immutable preview
  and approval for that candidate.

## Setup Task Skill Contract

- task_code: `AP_MANAGE_INVOICE_OPTIONS`
- task_name: `Manage Invoice Options`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Invoice Options` under `Payables`.

## Setup Task Metadata

- Task name: `Manage Invoice Options`
- Task code: `AP_MANAGE_INVOICE_OPTIONS`
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
- Setup task name: `Manage Invoice Options`
- Setup task code: `AP_MANAGE_INVOICE_OPTIONS`

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

`AP_SYSTEM_PARAMETER` is a shared row with separate Invoice and Payment
ownership rules. For an Invoice Options setup update, merge the requested change
with the baseline, then validate all resulting Payment-owned values with the
Manage Payment Options field contract. For a new Invoice Options setup row,
validate only supplied Payment-owned values and never invent optional ones.
Invoke only the sibling validator, not the full Payment Options skill, to avoid
a recursive workflow.

For one business unit, a single NLP request that includes both Invoice Options
and Payment Options changes is one shared-row transaction. Merge all requested
fields into one canonical `AP_SYSTEM_PARAMETER` row before candidate generation,
validate both field contracts against that row, and submit only this Invoice
Options package when any Invoice Options field is present. Do not create or
submit a second full-row package with a different baseline or values. A
Payment-only request remains a Manage Payment Options package.

Use the parent functional-area skill `erp.financials.payables` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

Account segment serialization and blank-position rules: see `ora-resource/ora_input_validation.md`, “Account segment package format”.

For account changes, ledger changes affecting an existing account, or enabling
interest invoices, run `scripts/resolve_lookup_prerequisites.py --baseline
<fresh-export.zip>` before normalization. It uses the task-owned
`scripts/interest_account_validation.py` and the unchanged core OAuth/HTTP client. Require a positive existing
CCID with `DynamicInsertion=No`; invalid or unavailable validation blocks the
candidate. Preserve receipt bindings to operation, BU, ledger, ordered segments
and baseline. Never create a GL combination. Keep the builder's JSON report
with a generated ZIP. For offline `validate-upload`, pass that report through
`--validation-context <build-report.json>`. It ties the original requests and
lookup results to the exact ZIP and baseline, including interest-account
checks. For a separately prepared upload, `--prerequisites` still accepts
upload-specific preflight receipts. Missing evidence blocks account changes.
Account serialization remains the native 30-slot LF vector.

## Narrow Post-Import Interest Verification

This check applies only when a nonblank Interest Expense Distribution was
requested and Create Interest Invoices (`AutoCalculateInterestFlag`) is `Y` in
the effective submitted row. Reject a nonblank requested account before building
a package when this flag is not `Y`; preserve the exported flag for an update
unless the requester changes it. Disabling interest invoices clears the account
and tolerance; do not expect account retention in that case.

After the approved import completes, inspect its status/errors through Data
Loader, obtain a fresh same-task setup-data export through Task Level Export,
then run the task-owned command:

```text
python3 scripts/fsm_task_adapter.py verify-interest --baseline <before.zip> --candidate <approved.zip> --blueprint <blueprint.json> --export <fresh-after.zip> --report <verification.json> --verification-evidence <observations.json> --environment <selected-environment> --base-url <selected-https-origin> --import-request-id <completed-import-request>
```

Use the environment, HTTPS origin and import request selected by the governed
workflow. The observation file must come from that workflow's actual Data Loader
status/error checks and completed Task Level Export, with file hashes and times.
Do not create success observations from matching CSV values or copied ZIP
metadata. See [Error Handling](ora-resource/ora_error_handling.md#post-import-readback-evidence)
for the observation fields and checks. Missing or mismatched proof leaves
verification `PENDING`; do not describe the account as saved.

The task workflow must complete this follow-up before claiming the requested
interest account was configured. `PASS` means the requested ordered account
segments persisted on the exact BU with interest enabled; a blank or different
account is `FAIL`. Missing/unreadable readback is `PENDING`: report "Import
completed; interest account verification pending." With no requested account,
this check is `NOT_APPLICABLE`. Compare leading zeros and blank segment positions
using the existing canonical multiline format. Do not compare unrelated fields
or BUs, audit values, defaults or derived fields. Full `reconcile` remains an
optional diagnostic. Do not retry imports or restore values automatically.

Data Loader's import result remains separate. `SUCCESS.DONE` in the pre-import
Task Hook registry means pre-import readiness, not persisted configuration.

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

Invoice Options imports the Payment Options descriptor and runtime to validate
Payment-owned fields in the shared AP_SYSTEM_PARAMETER row. It calls the Payment
field-contract entry point, never the full Payment Options workflow or blueprint
validator.

The sibling ID in `depends_on` is a required code/component dependency. Package
both skill folders, including their SKILL.md, e2e-adapter.json and script files,
under the same Payables parent directory. Preserve the sibling directory names
used by the loaders. The reciprocal declarations describe mutual runtime
requirements, not an execution order or a request to run both workflows.
Dependency collection should include each skill once. A missing sibling runtime
or descriptor blocks validation with an actionable error; do not replace it with
weaker local checks. Keep both components together when distributing this pair.
