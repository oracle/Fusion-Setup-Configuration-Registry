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
  - "erp.financials.financial-reporting-structures.manage-chart-of-accounts-structure-instances"
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
side_effects:
  - "Read-only account and COA lookups, and setup-data exports for classification."
  - "Separately approved GL account-combination creation through the declared approval adapter; never from ordinary validation."
  - "Eligible missing accounts may be deferred to creation during the separately approved Invoice Options FSM import."
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

## Income Tax Reporting request labels

Handle Income Tax Reporting requests in this skill using the following visible
field labels. These controls appear on Manage Tax Reporting and Withholding Tax
Options and map to columns already supported by this task's shared
`AP_SYSTEM_PARAMETER` package.

| Customer field label | Package field |
|---|---|
| Use combined filing program | `CombinedFilingFlag` |
| Use supplier tax region | `IncomeTaxRegionFlag` |
| Income Tax Region | `IncomeTaxRegion` |
| Include withholding distributions in income tax reports | `Enable1099OnAwtFlag` |

For example, “For Income Tax Reporting, enable Use combined filing program for
`<business unit>`” requests `CombinedFilingFlag=Y`. An explicit disable requests
`N`. Apply the same enable/disable interpretation to the other two checkbox
labels. Keep canonical package field names in the normalized design and preview.

A label alone, or a table containing “Use combined filing program” with an empty
value cell, does not specify Yes or No. Ask for the intended setting and any
missing business unit. Do not treat an empty cell as No, a default, or an explicit
clear. Omitted fields retain their exported values, including existing blanks,
except for the combined-filing dependent flag reset described below.

When preparing a request that changes these settings, consider the resulting
combined-filing and supplier-region choices together:

- Setting Use combined filing program to No also sets Use supplier tax region
  to No. Explain this dependent effect before import and show it in the effective
  preview values. A fresh export with both flags set to No is the expected result.
  If the request explicitly combines No with supplier tax region = Yes, explain
  the conflict and ask for corrected choices before creating a candidate.
  Income Tax Region must be blank; if an existing region is populated, ask for
  an explicit clear or a different combined-filing choice.
- With Use combined filing program enabled and Use supplier tax region disabled,
  Income Tax Region is enabled and required. Reuse a populated existing region
  when it is unchanged; otherwise ask for the intended LOV value.
- With both options enabled, Income Tax Region is disabled because the supplier
  tax region is used. Do not require a separate region or silently clear a
  previously exported value. Reject a requested region change or clear unless
  the same request switches Use supplier tax region to No and supplies a region.

Check these dependencies against the fresh exported values plus the requested
changes. A missing or whitespace-only required region, an explicit clear of a
required region, or a change to a disabled region stops before candidate
creation. A populated unchanged region can be reused. Changes unrelated to these
three controls retain their existing values.

Income Tax Region is LOV-based. Preserve the selected package value; Fusion
validates it during the governed FSM import. Do not hardcode values or infer
the complete LOV from an export. Do not claim a separate local LOV
validation or automatic clearing of a populated region. Verify the documented
supplier-flag reset separately from unrelated preservation checks. Include withholding
distributions in income tax reports is a separate explicit checkbox choice;
do not infer it from either combined-filing setting.

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
CCID with `DynamicInsertion=No`, the narrow approved SOAP-rejection/FSM
deferral, or the explicit account business-validation override described below.
Account business errors block the candidate by default. The user may explicitly
approve submitting that exact account unchanged after seeing its error; retain
the bound waiver and warning without claiming the account is valid. Service or
context failures and uncertain results must be resolved before continuing.
Preserve receipt bindings to operation, BU, ledger, ordered segments
and baseline. Never create a GL combination from validation. Use the separately approved creation flow below for confirmed missing accounts. Keep the builder's JSON report
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

For Interest Expense Distribution, read
[account validation decisions and test cases](references/interest-account-validation.md)
when resolving a rejected account, discussing creation, or testing this flow.
Keep `DynamicInsertion=No` for validation of existing accounts. Require HTTP success, `Status=Valid`
and one positive CCID; an existing ID alone is insufficient. Show the bounded
Fusion error codes and message when rejected. `CcId=-1` means this validation
did not return a usable account; it does not prove absence. Disabled,
end-dated, future-dated and posting-restricted accounts must not receive a
creation offer. FSM completion alone does not establish account eligibility or
retention. Missing-account classification and separately approved creation use the flow below. Never turn the ordinary validation call into a creating call.

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

## Missing Interest Account: Check, Ask, Create Only After Approval

For account changes, first obtain a fresh setup-data export for
`GL_MANAGE_CHARTS_OF_ACCOUNTS_STRUCTURE_INSTANCES` through Task Level Export.
Use the account batch review below with `--coa-configuration <export.zip>` to
check exact combination existence before SOAP validation. Existing accounts
are validated with No; missing accounts follow the configuration/approval flow.
Reuse a matching export no older than 24 hours. This export supplies the actual
`DynamicCombinationCreationAllowed` value and the physical segment mapping;
`chartOfAccountsLOV` alone does not expose this setting. The export and Invoice
Options baseline must match the independently selected environment and release.
The resolver uses managed read-only ledger, COA and complete account LOV lookups.

Read the returned `accountResolution` and show its message to the user:

- Fusion explicitly rejects a segment value: show that service error and ask for a corrected account. Do not offer combination creation to create or repair a segment value.
- Existing unusable account: explain the problem directly, for example “This account
  exists but is disabled. Please choose another account.” For date or posting
  restrictions, name that restriction. Do not preface the answer with “Fusion
  rejected it.” Keep the raw service code/message in diagnostic evidence and
  do not offer creation. If no specific reason was returned, say the existing
  account could not be validated for use.
- Confirmed missing, dynamic creation disabled: explain that creation is disabled.
- Confirmed missing, configuration unknown: explain what is unconfirmed and stop creation.
- Confirmed missing, configuration enabled: ask
  whether to create the exact combination, use an existing account, or stop.
  Explain that Fusion still validates cross-validation and other combination
  rules during creation. Do not promise that creation will succeed.

The resolver's creation question is a stop with no satisfied receipt or candidate.
A user choosing creation authorizes preparation of the exact preview, not a silent
write. Run `scripts/interest_account_creation.py --design <design.json> --baseline
<invoice-options.zip> --coa-configuration <coa.zip> --operation-id <operation-id>
--preview-output <new-preview.json> --token-cache auto`. This performs fresh
read-only checks and prepares a creation request (logical `DynamicInsertion=Yes`, serialized as the GL service flag `Y`); it does not
submit that request. Show the exact target, ledger, ordered segments and creation
effect and obtain explicit approval immediately before execution.

The approval JSON must be `fscr-soap-approval-v1`, with `approved: true`, a
nonblank `approvalId`, and the exact preview `request` and `taskContext` objects.
Do not manufacture approval from configuration or from a generic testing request.
Then invoke the same command with `--approval-file <approval.json> --output
<new-receipt.json>` instead of `--preview-output`. It rechecks absence and
configuration, submits once through its own `scripts/account_combination_workflow.py` adapter
and core OAuth/HTTP, records its receipt, and revalidates the returned positive
CCID with `DynamicInsertion=No`. Failed or uncertain creation never retries automatically. Only the specific
SOAP dynamic-insertion rejection may produce the separately documented FSM
deferral after fresh missing/configuration checks. Keep the receipt and reconcile before any separately approved retry.

On success rerun the ordinary resolver for a fresh baseline-bound account receipt,
then continue normal Invoice Options preparation and Data Loader approval. Account
creation does not save Invoice Options. Complete the existing post-import account
verification after a separately approved setup import. If the user declines, use
`--decline` or simply stop; no authentication, account creation or setup save occurs.

Account creation is self-contained in Invoice Options. Its local
`scripts/account_combination_workflow.py` binds the exact request approval, reserves
and records the execution receipt, and submits once through the unchanged core
OAuth/HTTP client. It does not load code from Common Options.
Preserve the user's ordered segment values and blank positions in both validation
and creation requests. Fusion decides requiredness, segment validity and combination
eligibility. Do not block a blank segment or a value merely because it has not
appeared in existing accounts. Existence/configuration checks and exact creation
approval remain required; they do not replace Fusion's business validation.


## Account batch review and FSM creation fallback

For account changes, follow [Account checks and batch review](references/interest-account-batch-flow.md).
Use `scripts/interest_account_batch.py review` with fresh COA evidence to check
the exact combination before SOAP validation, and report every record before
asking once about corrections, explicit account-business-validation overrides, exclusions or stopping. Prepare all
missing-account creation previews together; one explicit answer may approve
those exact requests, with separate bound execution records. Explain that any
created GL accounts remain if the later Invoice Options import is cancelled or fails.

Only an approved SOAP creation rejected solely with `GL_ASM_ACCOUNT_DYN_INSERT`
can be deferred to FSM after fresh absence and configuration checks. The returned
`deferred_to_fsm` receipt is not a positive CCID or an import approval. Other
account business errors and existing unusable accounts stay blocked by default;
the user may explicitly approve submitting the exact account unchanged through
the [account-validation override workflow](references/account-validation-overrides.md).
This waiver is separate from the automatic FSM creation fallback and does not
apply to service or context failures or uncertain execution. Include each attempted
account creation and the approved included/excluded record list in the normal
Data Loader preview. Do not silently skip rows, bypass Task Hook or submit automatically.
After import, use the batch verification command to check both persisted
Invoice Options and usable CCIDs; report verified counts, errors and pending checks.

## Fresh COA export evidence

Use `scripts/export_interest_account_configuration.py` with the ordinary Task
Level Export arguments `--task-code GL_MANAGE_CHARTS_OF_ACCOUNTS_STRUCTURE_INSTANCES
--data --project-id <project> --token-cache auto`. It delegates export mechanics
to the shared skill and records a `<export.zip>.observation.json` receipt beside
the unchanged ZIP. Keep both files together. Native Fusion metadata may omit a
timezone; in that case the account check uses the matching completed export
run's UTC observations and ZIP hash, never a guessed server timezone or file
modification time. Old, missing or mismatched observations remain blocked.

## Explicit account business-validation overrides

If the user explicitly wants to submit an account unchanged after seeing its
validation error, follow [account-validation-overrides.md](references/account-validation-overrides.md).
The batch selector supports a reasoned per-record override, and package checks
retain its bound failure receipt and warning. Do not report the account valid.
Show the waiver in the final preview and record affected Task Hook rules as
`overridden`; normal Data Loader approval is still required. FSM may accept or
reject the record, so verify the saved account and its usability afterward.
