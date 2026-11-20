# Manage Receivables System Options Input Validation

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AR_SYSTEM_OPTIONS::AccountingMethod, AR_SYSTEM_OPTIONS::AccrueInterest, AR_SYSTEM_OPTIONS::AiLogFileMessageLevel, AR_SYSTEM_OPTIONS::AiMaxMemoryInBytes, AR_SYSTEM_OPTIONS::AutoRecInvoicesPerCommit, AR_SYSTEM_OPTIONS::AutoRecReceiptsPerCommit, AR_SYSTEM_OPTIONS::AutoSiteNumbering, AR_SYSTEM_OPTIONS::BUName, AR_SYSTEM_OPTIONS::CalcDiscountOnLinesFlag, AR_SYSTEM_OPTIONS::CerDsoDays, AR_SYSTEM_OPTIONS::CerSplitAmount, AR_SYSTEM_OPTIONS::ChangePrintedInvoiceFlag, AR_SYSTEM_OPTIONS::CodeCombinationIdGainSegments, AR_SYSTEM_OPTIONS::CodeCombinationIdLossSegments, AR_SYSTEM_OPTIONS::CodeCombinationIdRoundSegments, AR_SYSTEM_OPTIONS::CreateDetailedDist, AR_SYSTEM_OPTIONS::CreateReciprocalFlag, AR_SYSTEM_OPTIONS::DefaultCbDueDate, AR_SYSTEM_OPTIONS::DocumentSeqGenLevel, AR_SYSTEM_OPTIONS::GenerateCustomerNumber, AR_SYSTEM_OPTIONS::GroupingRuleName, AR_SYSTEM_OPTIONS::InvoiceDeletionFlag, AR_SYSTEM_OPTIONS::LedgerCurrency, AR_SYSTEM_OPTIONS::LedgerName, AR_SYSTEM_OPTIONS::LocationTaxAccountSegments, AR_SYSTEM_OPTIONS::PartialDiscountFlag, AR_SYSTEM_OPTIONS::PayUnrelatedInvoicesFlag, AR_SYSTEM_OPTIONS::PopulateGlSegmentsFlag, AR_SYSTEM_OPTIONS::PostingDaysPerCycle, AR_SYSTEM_OPTIONS::PrintHomeCountryFlag, AR_SYSTEM_OPTIONS::PrintRemitTo, AR_SYSTEM_OPTIONS::RuleSetName, AR_SYSTEM_OPTIONS::RunGlJournalImportFlag, AR_SYSTEM_OPTIONS::SalesrepRequiredFlag, AR_SYSTEM_OPTIONS::ServicedByAnyBuFlag, AR_SYSTEM_OPTIONS::SiteRequiredFlag, AR_SYSTEM_OPTIONS::TaxInvoicePrint, AR_SYSTEM_OPTIONS::TrxHeaderLevelRounding, AR_SYSTEM_OPTIONS::UnearnedDiscount -->
<!-- fscr-update-fields: AR_SYSTEM_OPTIONS::AccountingMethod, AR_SYSTEM_OPTIONS::AccrueInterest, AR_SYSTEM_OPTIONS::AiLogFileMessageLevel, AR_SYSTEM_OPTIONS::AiMaxMemoryInBytes, AR_SYSTEM_OPTIONS::AutoRecInvoicesPerCommit, AR_SYSTEM_OPTIONS::AutoRecReceiptsPerCommit, AR_SYSTEM_OPTIONS::AutoSiteNumbering, AR_SYSTEM_OPTIONS::CalcDiscountOnLinesFlag, AR_SYSTEM_OPTIONS::CerDsoDays, AR_SYSTEM_OPTIONS::CerSplitAmount, AR_SYSTEM_OPTIONS::ChangePrintedInvoiceFlag, AR_SYSTEM_OPTIONS::CodeCombinationIdGainSegments, AR_SYSTEM_OPTIONS::CodeCombinationIdLossSegments, AR_SYSTEM_OPTIONS::CodeCombinationIdRoundSegments, AR_SYSTEM_OPTIONS::CreateDetailedDist, AR_SYSTEM_OPTIONS::CreateReciprocalFlag, AR_SYSTEM_OPTIONS::DefaultCbDueDate, AR_SYSTEM_OPTIONS::DocumentSeqGenLevel, AR_SYSTEM_OPTIONS::GenerateCustomerNumber, AR_SYSTEM_OPTIONS::GroupingRuleName, AR_SYSTEM_OPTIONS::InvoiceDeletionFlag, AR_SYSTEM_OPTIONS::LedgerName, AR_SYSTEM_OPTIONS::LocationTaxAccountSegments, AR_SYSTEM_OPTIONS::PartialDiscountFlag, AR_SYSTEM_OPTIONS::PayUnrelatedInvoicesFlag, AR_SYSTEM_OPTIONS::PopulateGlSegmentsFlag, AR_SYSTEM_OPTIONS::PostingDaysPerCycle, AR_SYSTEM_OPTIONS::PrintHomeCountryFlag, AR_SYSTEM_OPTIONS::PrintRemitTo, AR_SYSTEM_OPTIONS::RuleSetName, AR_SYSTEM_OPTIONS::RunGlJournalImportFlag, AR_SYSTEM_OPTIONS::SalesrepRequiredFlag, AR_SYSTEM_OPTIONS::ServicedByAnyBuFlag, AR_SYSTEM_OPTIONS::SiteRequiredFlag, AR_SYSTEM_OPTIONS::TaxInvoicePrint, AR_SYSTEM_OPTIONS::TrxHeaderLevelRounding, AR_SYSTEM_OPTIONS::UnearnedDiscount -->

Validate create and update values only within these source-backed entity-qualified allowlists. Treat an unlisted field as evidence-unresolved for that operation rather than declaring it invalid or unsupported; require supported evidence or the task's governed runtime-validation decision before use.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver | Source IDs |
|---|---|---|---|---|---|---|
| Business-unit identity | `BUName` | Block before package preview | Resolve exactly one business unit in the import enterprise context | Always | resolve_business_unit | SRC-FSM-PACKAGE; SRC-CODE-AM-IMPL; SRC-EDM-AR-SYSTEM-PARAMETERS-26C |
| Ledger identity | `LedgerName`; package `LedgerCurrency` must agree with the selected ledger | Block before package preview | Resolve exactly one ledger and retain its chart-of-accounts receipt | Always | resolve_ledger | SRC-FSM-PACKAGE; SRC-UI-RSO-FORM; SRC-CODE-AM-IMPL |
| Create application rule set | RuleSetName | Block before package preview and candidate ZIP generation | Require an explicit nonblank name; never default or copy it from another business unit; let the confirmed FSM import resolver map it to RuleSetId | Create operation | resolve_receivables_rules | SRC-CODE-AM-IMPL; SRC-CODE-AM-DEF; SRC-CODE-RESOLVER-APP-RULE-SET-VO; SRC-CODE-RESOLVER-APP-RULE-SET-EO; SRC-E2E-RSO-CREATE-RULESET-20260904 |
| Billing and revenue conditional set | Source-package fields corresponding to rule set, split amount, DSO days, discount-on-lines, salesperson requirement, posting days, tax-invoice printing, printed-transaction changes, grouping rule, unearned discount, reciprocal creation, AutoInvoice memory/log level, partial-payment discount, and gain/loss/rounding accounts | Block the row when the billing/revenue usage is enabled or an existing setup row requires the set | Complete every applicable field from the task-owned field contract, apply the confirmed business-label mappings below, and resolve references through the registered resolvers; ask one bounded business-language clarification for a genuinely unmapped term | Billing and Revenue section applies |  | SRC-CODE-EO-IMPL; SRC-FSM-PACKAGE; SRC-E2E-RSO-BUSINESS-LABEL-MAPPING-20260904 |
| Cash-processing conditional set | Source-package fields corresponding to site requirement, AutoRec invoices/receipts per commit, gain/loss/rounding accounts, unrelated-invoice payment, and default chargeback due date | Block the row when cash processing is enabled or an existing setup row requires the set | Complete every applicable field from the task-owned field contract, apply the confirmed business-label mappings below, and resolve references through the registered resolvers; ask one bounded business-language clarification for a genuinely unmapped term | Cash Processing section applies |  | SRC-CODE-EO-IMPL; SRC-FSM-PACKAGE; SRC-E2E-RSO-BUSINESS-LABEL-MAPPING-20260904 |
| Package contract | `ASM_SETUP_CSV_METADATA.xml` plus exactly one `AR_SYSTEM_OPTIONS.csv` using the current 202-column header contract | Block before preview | Refresh a same-task export/template from the target and rebuild through Data Loader | Any import candidate | verify_rso_package_baseline | SRC-FSM-PACKAGE; SRC-CODE-TASK-BO; SRC-CODE-SETUP-BO |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver | Source IDs |
|---|---|---|---|---|
| `BUName` or any activity business-unit name is populated | Continue only when each name resolves to exactly one business unit | Fill only the corresponding internal organization identifier in the import runtime | resolve_business_unit | SRC-CODE-AM-IMPL |
| `ItemValidBUName` is populated | Continue only when the organization name resolves once | Fill `ItemValidationOrgId` in the import runtime | resolve_item_validation_org | SRC-CODE-AM-IMPL |
| A hierarchy, automatch rule, grouping rule, application rule set, exception rule, or Receivables activity is populated | Continue when its Confirmed FSM import resolver contract is bound; public preflight is optional and unavailable for these fields | Preserve the user-facing package value and require the immutable Data Loader preview to resolve the documented business/context key to the mapped internal value |  | SRC-CODE-AM-IMPL; SRC-CODE-AM-DEF; SRC-CODE-RESOLVER-AUTOCASH-VO; SRC-CODE-RESOLVER-AUTOCASH-EO; SRC-CODE-RESOLVER-AUTOMATCH-VO; SRC-CODE-RESOLVER-AUTOMATCH-EO; SRC-CODE-RESOLVER-GROUPING-RULE-VO; SRC-CODE-RESOLVER-GROUPING-RULE-EO; SRC-CODE-RESOLVER-APP-RULE-SET-VO; SRC-CODE-RESOLVER-APP-RULE-SET-EO; SRC-CODE-RESOLVER-EXCEPTION-RULE-VO; SRC-CODE-RESOLVER-EXCEPTION-RULE-EO; SRC-CODE-RESOLVER-RECEIVABLE-ACTIVITY-VO; SRC-CODE-RESOLVER-RECEIVABLE-ACTIVITY-EO |
| A receipt method, reference-data set, batch source, transaction type, remittance account, ledger, or other public-preflight-backed reference is populated | Continue only after its exact supported read-only preflight returns the required single match | Preserve the user-facing package value; pass the resolved internal value only to the supported FSM import path |  | SRC-CODE-AM-IMPL |
| `AiAcctFlexKeyLeftPrompt` is populated | Continue when the ledger-derived chart of accounts is available and the Confirmed FSM import existence-validation contract is bound | Preserve the supplied prompt; require the immutable Data Loader preview to find an enabled GL# segment whose exact segment name matches the prompt | validate_accounting_flexfield_prompt | SRC-CODE-AM-IMPL; SRC-CODE-AM-DEF; SRC-CODE-RESOLVER-ACCOUNTING-FLEXFIELD-VVO |
| An account-combination segment field is populated | Continue only when the ledger-derived chart of accounts is known and the combination resolves and validates | Preserve the concatenated segment value and record the validation receipt | resolve_and_validate_account_combination | SRC-CODE-AM-IMPL; SRC-CODE-GL-BULK-COMBINATIONS; SRC-CODE-ARPT-SQL-FUNC |
| An FSM import alternate-key or existence check returns null | The task import records the field-specific dependency token, emits recoverable `AR:::AR_ATTR_NOT_EXISTS_TARGET_INS` with `ATTRIBUTE_NAME_LIST` and alternate-key values, and removes the invalid `AR_SYSTEM_OPTIONS` XML element | Stop and return the exact field, input, resolver, business/context keys, and surfaced message; never retry or invent a value |  | SRC-CODE-AM-IMPL; SRC-CODE-AM-DEF |
| Accounting-flexfield prompt validation returns no row | The surfaced dependency text includes `AiAcctFlexKeyLeftPrompt <value> does not exist`; the common recoverable error and invalid-element removal behavior apply | Stop the affected row and preserve the exact ledger/chart-of-accounts context without exposing physical IDs | validate_accounting_flexfield_prompt | SRC-CODE-AM-IMPL; SRC-CODE-AM-DEF; SRC-CODE-RESOLVER-ACCOUNTING-FLEXFIELD-VVO |
| A public preflight reference fails or is ambiguous | The task records an invalid dependency for the affected field and must not choose a candidate | Stop and return the exact field, input, resolver, and cardinality; never choose the first match |  | SRC-CODE-AM-IMPL |

## Field Validation

| Check | What Happens | Applies When | Resolver | Source IDs |
|---|---|---|---|---|
| Supported package field | Accept only headers present in the current same-task `AR_SYSTEM_OPTIONS.csv` contract; use the task-owned 202-column field inventory internally | Always | verify_rso_package_baseline | SRC-FSM-PACKAGE |
| Business-unit key | Require one row per business unit; `ORG_ID` is the persisted primary/alternate identity and must not be supplied as an unevidenced physical ID | Always | resolve_business_unit | SRC-EDM-AR-SYSTEM-PARAMETERS-26C; SRC-CODE-EO |
| One-character string maximum | Reject before candidate ZIP generation when any of these AR_SYSTEM_OPTIONS fields exceeds 1 character: AccrueInterest, AutoSiteNumbering, CalcDiscountOnLinesFlag, ChangePrintedInvoiceFlag, CreateReciprocalFlag, GenerateCustomerNumber, InvoiceDeletionFlag, PartialDiscountFlag, PayUnrelatedInvoicesFlag, PopulateGlSegmentsFlag, PrintHomeCountryFlag, PrintRemitTo, RunGlJournalImportFlag, SalesrepRequiredFlag, ServicedByAnyBuFlag, SiteRequiredFlag, TrxHeaderLevelRounding, UnearnedDiscount. Report entity, field, actual length, maximum, and characters; request a shorter business value and require a new preview. Never truncate. | A listed field is supplied as a target key or operation value |  | SRC-FSM-PACKAGE; SRC-CODE-EO; SRC-EDM-AR-SYSTEM-PARAMETERS-26C |
| Thirty-character string maximum | Reject before candidate ZIP generation when any of these AR_SYSTEM_OPTIONS fields exceeds 30 characters: AccountingMethod, DefaultCbDueDate, TaxInvoicePrint, CreateDetailedDist. Report entity, field, actual length, maximum, and characters; request a shorter business value and require a new preview. Never truncate. | A listed field is supplied as a target key or operation value |  | SRC-FSM-PACKAGE; SRC-CODE-EO; SRC-EDM-AR-SYSTEM-PARAMETERS-26C |
| Eighty-character string maximum | Reject before candidate ZIP generation when AR_SYSTEM_OPTIONS.DocumentSeqGenLevel exceeds 80 characters. Report entity, field, actual length, maximum, and characters; request a shorter business value and require a new preview. Never truncate. | DocumentSeqGenLevel is supplied as a target key or operation value |  | SRC-FSM-PACKAGE; SRC-CODE-EO; SRC-EDM-AR-SYSTEM-PARAMETERS-26C |
| Create application rule set | Reject before ZIP generation when RuleSetName is missing or blank; do not infer a default or copy another business unit's value | Create operation | resolve_receivables_rules | SRC-CODE-AM-IMPL; SRC-CODE-AM-DEF; SRC-CODE-RESOLVER-APP-RULE-SET-VO; SRC-CODE-RESOLVER-APP-RULE-SET-EO; SRC-E2E-RSO-CREATE-RULESET-20260904 |
| Boolean flags | Accept only values documented by the current package contract and confirmed source rules; do not infer UI labels or coerce unknown values | Flag supplied |  | SRC-FSM-PACKAGE; SRC-CODE-EO |
| Header-level rounding account | When `TrxHeaderLevelRounding` is enabled, require a valid `TrxHeaderRoundCCIDSegments` value | Header-level rounding enabled | resolve_and_validate_account_combination | SRC-HELP-RSO-26C; SRC-CODE-EO-IMPL |
| Salesperson requirement | When salesperson is required, require an approved sales-credit percent limit; a blank limit means no enforced limit | Salesperson required |  | SRC-HELP-RSO-26C |
| Account combinations | Resolve concatenated segments only under the ledger-derived chart of accounts and require successful combination validation | Any account segment field populated | resolve_and_validate_account_combination | SRC-CODE-AM-IMPL; SRC-CODE-GL-BULK-COMBINATIONS; SRC-CODE-ARPT-SQL-FUNC |
| Unknown semantics | Preserve a structurally valid but unsupported business interpretation as `evidence_unresolved`; ask one bounded business-language clarification or record an eligible explicit nonproduction runtime-validation override, but never request developer authoring artifacts | Task-owned semantic evidence is Open, TBD, or Blocked |  | SRC-FSM-PACKAGE |
| System-owned values | Do not invent internal IDs, audit values, object versions, ESS values, or database-only columns | Always |  | SRC-EDM-AR-SYSTEM-PARAMETERS-26C; SRC-CODE-EO |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RSO.VALIDATE_INPUT | step | 10 | validate_input | valid->RSO.RESOLVE_REFERENCES;invalid->RSO.HANDLE_ERROR | none | stop | Before any lookup or package preview |

<!-- E2E-DISCOVERY:RSO-E2E-DISC-004 -->
## Complete create contract

Every create requires nonblank `LedgerName`, `RuleSetName`, `CerSplitAmount`, `CerDsoDays`, `CalcDiscountOnLinesFlag`, `LocationTaxAccountSegments`, `CodeCombinationIdRoundSegments`, `CodeCombinationIdGainSegments`, `CodeCombinationIdLossSegments`, `PostingDaysPerCycle`, `TaxInvoicePrint`, `DocumentSeqGenLevel`, `GroupingRuleName`, `AiMaxMemoryInBytes`, `AiLogFileMessageLevel`, `DefaultCbDueDate`, `AutoRecInvoicesPerCommit`, and `AutoRecReceiptsPerCommit`, in addition to the `BUName` key. Source-backed create defaults may satisfy their named fields. `LedgerCurrency` is ledger-derived transient context: validate agreement when supplied, but do not require it to persist in a fresh export.

<!-- E2E-DISCOVERY:RSO-E2E-DISC-005 -->
## Business-label normalization

Normalize supported implementation-language values before validating package types. The mapping is task-owned and must not be generalized to other setup tasks.

| Business field | Accepted implementation-language values | Exact package value | Behavior | Source IDs |
|---|---|---|---|---|
| Tax invoice printing | Show total tax only; Total tax only; TOTAL ONLY | TOTAL ONLY | Match case-insensitively after trimming; preserve the exact package value when already supplied. | SRC-E2E-RSO-BUSINESS-LABEL-MAPPING-20260904 |
| Document sequence assignment | Assign when transaction is completed; When transaction is completed; When completed; WHEN_TRX_COMPLETED | WHEN_TRX_COMPLETED | Match case-insensitively after trimming; preserve the exact package value when already supplied. | SRC-E2E-RSO-BUSINESS-LABEL-MAPPING-20260904 |
| Chargeback due date | Due date of open invoice; Open invoice due date; DUE_DATE | DUE_DATE | Match case-insensitively after trimming; preserve the exact package value when already supplied. | SRC-E2E-RSO-BUSINESS-LABEL-MAPPING-20260904 |
| AutoInvoice maximum memory | Positive whole-number MB such as 5 MB, or an exact nonnegative byte integer | AiMaxMemoryInBytes decimal integer | Convert MB to bytes using value x 1048576; 5 MB becomes 5242880. Preserve an explicit byte integer without reconversion. | SRC-E2E-RSO-BUSINESS-LABEL-MAPPING-20260904 |

Never ask an implementation user for the Attributes Workbook, Source Register, source code, or an internal CSV encoding. If a requested business term is not mapped, ask one concise business-language clarification naming the field and supported choices. A structurally valid but still unproved value may proceed only through the documented explicit nonproduction runtime-validation override, immutable preview, and separate approval; a proven invalid value remains blocked.

<!-- E2E-DISCOVERY:RSO-E2E-DISC-007 -->
## Discount Basis lookup-backed enumeration

Treat `CalcDiscountOnLinesFlag` as the four-value Discount Basis enumeration even though its package name ends in `Flag`. Normalize implementation-language choices case-insensitively after trimming: `Invoice Amount` maps to `I`; `Lines Only` maps to `L`; `Lines, Freight Items, and Tax` maps to `T`; and `Lines and Tax, not Freight Items and Tax` maps to `F`. Preserve an exact supported code already supplied. On create the value is required and nonblank. Reject any other code or label, including Boolean-style `N` or `Y`, before candidate ZIP generation and ask one concise business-language clarification listing the four choices. Source IDs: `SRC-CODE-RSO-DISCOUNT-BASIS-LOOKUP`, `SRC-CODE-CREATE-UI-VO`, `SRC-BO-RSO-DISCOUNT-BASIS-26C`, and `SRC-E2E-RSO-BUSINESS-LABEL-MAPPING-20260904`.

<!-- E2E-DISCOVERY:RSO-E2E-DISC-009 -->
## Controlled create-required transaction and receipt choices

Every create requires explicit nonblank values for ChangePrintedInvoiceFlag, PartialDiscountFlag, and SiteRequiredFlag. Ask for them in business language: whether printed transactions may be changed, whether partial payments can earn discounts, and whether receipts require a customer site. Do not expose package-field names unless needed for diagnostics, and do not invent a universal default. Reject an incomplete create before candidate ZIP generation and report all three missing choices together. Controlled FSM imports returned FND_CMN_REQ_ATTRIB_API_SERV for each omitted field; the corrected eight-row request succeeded. Source ID: SRC-E2E-RSO-CREATE-REQUIRED-ATTRIBUTES-20260904.

## Salesperson requirement on create

Require an explicit `SalesrepRequiredFlag` choice on create. A controlled nonproduction FSM import on release 27.01 rejected an omitted value with `FND_CMN_REQ_ATTRIB_API_SERV`; do not assume an import default. Ask whether a salesperson is required. If Yes, retain the existing sales-credit percent-limit decision gate. Source: SRC-E2E-RSO-CREATE-SALESREP-20261023.

## Source-audited required create fields

The supported complete billing/cash create profile must cover both lists in
`SystemParameterEOImpl.validateSystemParameterEO`, plus the non-null input
attributes in `SystemParameterEO.xml`. In addition to the fields above, require
`CreateReciprocalFlag` and `PayUnrelatedInvoicesFlag`: ask whether reciprocal
customer relationships should be created and whether payments may apply to
unrelated customers' invoices. Do not invent a default for either choice.

Also require nonblank `AccountingMethod`, `AccrueInterest`, `AutoSiteNumbering`,
`GenerateCustomerNumber`, `PopulateGlSegmentsFlag`, and `UnearnedDiscount` after
applying the existing source-backed create defaults. Omission uses the existing
default; an explicitly blank value is unresolved and must be reported, not silently
replaced. Collect all missing required choices in one clarification before preview.

These checks complete the skill's existing combined create profile; the application
itself makes Billing and Cash Processing requirements conditional on BU usage or
previously configured sections. Do not infer that every BU must enable both functions.
Do not copy another BU's flags merely to make a create pass. Existing optional flags
such as invoice deletion, journal import and printing remain optional.

Source: SRC-CODE-EO; SRC-CODE-EO-IMPL; SRC-CODE-CREATE-UI-VO.
Audit baseline: FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64_261019.2306.
The source label is not asserted to be identical to the deployed target release.

For updates, preserve omitted values. Reject an explicit blank/null for an entity
non-null field or for a required field in an already configured Billing or Cash
Processing section. Determine the posted section from the fresh baseline's
GroupingRuleName and SiteRequiredFlag respectively, mirroring the EO's
DefaultGroupingRuleId/SiteRequiredFlag checks. This local check does not replace
BU-function discovery or FSM's final validation for newly enabled sections.
