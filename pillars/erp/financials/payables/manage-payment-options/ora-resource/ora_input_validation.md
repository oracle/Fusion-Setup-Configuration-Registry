# Input Validation

A blank Resolver means the check runs locally against the documented task
contract, candidate package, or fresh baseline; it requires no reference lookup.

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_SYSTEM_PARAMETER::BuName, AP_SYSTEM_PARAMETER::EnterpriseId, AP_SYSTEM_PARAMETER::BankChargeBearer, AP_SYSTEM_PARAMETER::BankChargeDeductionTypeDes, AP_SYSTEM_PARAMETER::TermName -->
<!-- fscr-update-fields: AP_SYSTEM_PARAMETER::WhenToAccountPmt, AP_SYSTEM_PARAMETER::PostDatedPaymentsFlag, AP_SYSTEM_PARAMETER::AllowSupplierBankOverride, AP_SYSTEM_PARAMETER::PayDocCategoryOverride, AP_SYSTEM_PARAMETER::AllowPymtThirdPartyOvrd, AP_SYSTEM_PARAMETER::BankChargeBearer, AP_SYSTEM_PARAMETER::BankChargeDeductionTypeDes -->

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Exact FSM package contract | Matching AP_SYSTEM_PARAMETER.csv header, ASM_SETUP_CSV_METADATA.xml, and task identity AP_MANAGE_PAYMENT_OPTIONS | Block preview | Use the supplied current-data and template exports for this exact task | Always | |
| Target business-unit scope | Business unit identity from the requested change and one unique package row | Block preview | Provide an unambiguous target business unit and reconcile it to a fresh same-task export | Before any candidate is prepared | |
| Shared system-options contract | A compatible Manage Invoice Options AP_SYSTEM_PARAMETER adapter/runtime is available and accepts the complete candidate row | Block preview | Restore or refresh ../manage-invoice-options/e2e-adapter.json and ../manage-invoice-options/scripts/fsm_task_adapter.py; do not bypass the sibling task contract with a payment-only package | Every supported Payment operation | |
| Submitted optional Payment field | A value for each Payment Options control the requester chose to change | Block preview | Validate the submitted value against that field's exact task contract; preserve the baseline value for every omitted optional field | When a Payment Options value is supplied | |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Package identity, target scope, or field contract is incomplete | Blocked | Do not build a candidate; resolve the missing evidence | |
| Sibling Invoice Options shared-row contract rejects the complete proposed AP_SYSTEM_PARAMETER row | Blocked | Correct the reported shared field, prerequisite, lookup receipt, or default; then regenerate the Payment candidate | |
| Package, target scope, and requested payment-accounting evidence are complete | Ready for governed preview | Route preview and any import only through core.data-loader | |

## Field Validation

## Business-Control-to-Package Mapping

| UI control | Exact task-package field | Customer validation behavior |
|---|---|---|
| Allow payment date before the system date | `PostDatedPaymentsFlag` (`Y`/`N`) | Validate `Y` or `N`; do not substitute `FutureDatedPmtLiabRelief`. |
| Allow override of supplier site bank account | `AllowSupplierBankOverride` | Validate `Y` or `N`. |
| Allow document category override | `PayDocCategoryOverride` | Validate `Y` or `N`. |
| Allow payee override for third-party payments | `AllowPymtThirdPartyOvrd` | Validate `Y` or `N`. |
| Account for Payment | `WhenToAccountPmt` | Use the observed package code: `PAYMENT ONLY` (At payment issue), `CLEARING ONLY` (At payment clearing), or `BOTH` (At payment issue and clearing). Oracle's [SystemOptionEO declaration](https://codesearch.oraclecorp.com/source/xref/FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/ap/sharedSetup/payablesSystemOptions/model/src/oracle/apps/financials/payables/sharedSetup/payablesSystemOptions/model/entity/SystemOptionEO.xml#2207) sets `Precision="30"` for this field, so reject values longer than 30 characters before preview. |
| Bank Charge Deduction Type | `BankChargeDeductionTypeDes` | Write `Standard`, `Negotiated`, or `None`. Do not write the database codes `S`, `N`, or `X`. |
| Minimum days to initiate escheatment | `EscheatmentEligibilityPeriod` | Require a nonnegative integer. |

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Archive identity | Accept only the exact AP_SYSTEM_PARAMETER setup archive whose metadata matches Manage Payment Options | Always | |
| Header and node fidelity | Preserve the exact template header order, XML node path, and CSV field count including trailing blanks | Always | |
| Shared-row integrity | Merge the approved Payment fields onto the exact baseline row, then validate that complete row through the Invoice Options AP_SYSTEM_PARAMETER contract. When Payment create is lifecycle-enabled from fresh task evidence, validate the complete proposed row and its Invoice-owned prerequisites/defaults through the same contract. | Every supported Payment operation, including uploaded ZIP rows | |
| Submitted Payment field | Serialize only a Payment Options field the requester explicitly supplies. Validate it against its own code/value contract and preserve the baseline value for every omitted optional field. | When any Payment Options field is edited | |
| Optional-field update evidence | Apply the same validation to every optional Payment field. If updateability for a requested field is not confirmed, require a governed application-validation override bound exactly to that field; do not treat another field's successful import evidence as exclusive support. | When an optional Payment field is edited | |
| Required create payment term | For a new shared AP_SYSTEM_PARAMETER row, obtain the supplied TermName receipt through the delegated owning resolver before normalization; do not fabricate a receipt or request an extra Invoice Options workflow. Payment updates retain their Invoice-owned term fields unchanged. | Create | resolve_payment_term_from_name |
| Payment-date override | Map **Allow payment date before the system date** to `PostDatedPaymentsFlag` (`Y`/`N`). Do not substitute `FutureDatedPmtLiabRelief`. | When supplied | |
| Supplier-bank override | Map **Allow override of supplier site bank account** to AllowSupplierBankOverride. Accept only Y or N when supplied; preserve the baseline value otherwise. | When supplied | |
| Payment document-category override | Map **Allow document category override** to PayDocCategoryOverride. Accept only Y or N when supplied; do not substitute the invoice-side InvDocCategoryOverride field. | When supplied | |
| Third-party payee override | Map **Allow payee override for third-party payments** to AllowPymtThirdPartyOvrd. Accept only Y or N when supplied. | When supplied | |
| Conversion-rate requirement | Map **require** or **enable** to Yes (`Y`) and **do not require** to No (`N`). Preserve the exported value when omitted. | When supplied | |
| Bank-charge deduction type | Write `Standard`, `Negotiated`, or `None` in `BankChargeDeductionTypeDes`. This CSV field takes the name, not the database code `S`, `N`, or `X`. | When supplied | |
| Escheatment minimum days | Map **Minimum days to initiate escheatment** to `EscheatmentEligibilityPeriod`. Require a nonnegative integer when supplied. | When supplied | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PAYOPT.VALIDATE_INPUT | step | 10 | validate_input | valid->PAYOPT.LOOKUP_PREFLIGHT;invalid->PAYOPT.INPUT_BLOCKED | none | stop | Always |

## Uploaded Create Context

Validate new uploaded rows with the same shared required-field rules as new
request rows. Treat the CSV's `SOBName` and `BaseCurrencyCode` as resolved
business-unit context and compare them with the saved BU/primary-ledger lookup
results for the exact ZIP and baseline. Reject missing context, another BU's
receipts, conflicting ledger/currency cells, missing required values, and
unsupported business-field changes. Keep audit fields blank and leave the ZIP
unchanged. Use `--validation-context` as described in
[Reference Lookups](ora_reference_lookups.md#uploaded-create-zips).

## Shared Create Defaults

For a new Payment Options row, reuse the Invoice Options documented create
defaults listed in [Defaulting Rules](ora_defaulting_rules.md). Include them in
the blueprint and preview, and physically write them in the CSV. Require them
when validating a saved blueprint or generated candidate. This covers the seven
required `N` flags and four date-basis values; it does not make other Invoice
Options fields editable through Payment Options.

An uploaded create must contain all these default values in its actual CSV.
Reject blank or conflicting cells even if request normalization could supply a
default. Do not change uploaded bytes. Existing updates keep their baseline
values and receive no create defaults. Use Invoice Options when the user asks
for different Invoice-owned settings.

## Clearing Optional Values in Uploaded ZIPs

For an existing row, compare business fields with the fresh baseline, including
blank cells. Clearing Bank Charge Bearer must pass the same checks in NLP input
and uploaded ZIPs. Keep required-field and shared Invoice Options checks in
place. Blank optional create cells remain omitted; uploaded creates must still
contain the required values, shared defaults, and resolved BU context.

## Update preservation

For updates, `preserveOtherValues` must be `true` or omitted (defaults to `true`). Explicit `false` and nonboolean values are rejected before candidate preparation or validation. Omitted fields retain their baseline values.
