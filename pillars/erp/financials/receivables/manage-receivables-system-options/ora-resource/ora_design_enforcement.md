# Manage Receivables System Options Design Enforcement

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AR_SYSTEM_OPTIONS::AccountingMethod, AR_SYSTEM_OPTIONS::AccrueInterest, AR_SYSTEM_OPTIONS::AiLogFileMessageLevel, AR_SYSTEM_OPTIONS::AiMaxMemoryInBytes, AR_SYSTEM_OPTIONS::AutoRecInvoicesPerCommit, AR_SYSTEM_OPTIONS::AutoRecReceiptsPerCommit, AR_SYSTEM_OPTIONS::AutoSiteNumbering, AR_SYSTEM_OPTIONS::BUName, AR_SYSTEM_OPTIONS::CalcDiscountOnLinesFlag, AR_SYSTEM_OPTIONS::CerDsoDays, AR_SYSTEM_OPTIONS::CerSplitAmount, AR_SYSTEM_OPTIONS::ChangePrintedInvoiceFlag, AR_SYSTEM_OPTIONS::CodeCombinationIdGainSegments, AR_SYSTEM_OPTIONS::CodeCombinationIdLossSegments, AR_SYSTEM_OPTIONS::CodeCombinationIdRoundSegments, AR_SYSTEM_OPTIONS::CreateDetailedDist, AR_SYSTEM_OPTIONS::CreateReciprocalFlag, AR_SYSTEM_OPTIONS::DefaultCbDueDate, AR_SYSTEM_OPTIONS::DocumentSeqGenLevel, AR_SYSTEM_OPTIONS::GenerateCustomerNumber, AR_SYSTEM_OPTIONS::GroupingRuleName, AR_SYSTEM_OPTIONS::InvoiceDeletionFlag, AR_SYSTEM_OPTIONS::LedgerCurrency, AR_SYSTEM_OPTIONS::LedgerName, AR_SYSTEM_OPTIONS::LocationTaxAccountSegments, AR_SYSTEM_OPTIONS::PartialDiscountFlag, AR_SYSTEM_OPTIONS::PayUnrelatedInvoicesFlag, AR_SYSTEM_OPTIONS::PopulateGlSegmentsFlag, AR_SYSTEM_OPTIONS::PostingDaysPerCycle, AR_SYSTEM_OPTIONS::PrintHomeCountryFlag, AR_SYSTEM_OPTIONS::PrintRemitTo, AR_SYSTEM_OPTIONS::RuleSetName, AR_SYSTEM_OPTIONS::RunGlJournalImportFlag, AR_SYSTEM_OPTIONS::SalesrepRequiredFlag, AR_SYSTEM_OPTIONS::ServicedByAnyBuFlag, AR_SYSTEM_OPTIONS::SiteRequiredFlag, AR_SYSTEM_OPTIONS::TaxInvoicePrint, AR_SYSTEM_OPTIONS::TrxHeaderLevelRounding, AR_SYSTEM_OPTIONS::UnearnedDiscount -->
<!-- fscr-update-fields: AR_SYSTEM_OPTIONS::AccountingMethod, AR_SYSTEM_OPTIONS::AccrueInterest, AR_SYSTEM_OPTIONS::AiLogFileMessageLevel, AR_SYSTEM_OPTIONS::AiMaxMemoryInBytes, AR_SYSTEM_OPTIONS::AutoRecInvoicesPerCommit, AR_SYSTEM_OPTIONS::AutoRecReceiptsPerCommit, AR_SYSTEM_OPTIONS::AutoSiteNumbering, AR_SYSTEM_OPTIONS::CalcDiscountOnLinesFlag, AR_SYSTEM_OPTIONS::CerDsoDays, AR_SYSTEM_OPTIONS::CerSplitAmount, AR_SYSTEM_OPTIONS::ChangePrintedInvoiceFlag, AR_SYSTEM_OPTIONS::CodeCombinationIdGainSegments, AR_SYSTEM_OPTIONS::CodeCombinationIdLossSegments, AR_SYSTEM_OPTIONS::CodeCombinationIdRoundSegments, AR_SYSTEM_OPTIONS::CreateDetailedDist, AR_SYSTEM_OPTIONS::CreateReciprocalFlag, AR_SYSTEM_OPTIONS::DefaultCbDueDate, AR_SYSTEM_OPTIONS::DocumentSeqGenLevel, AR_SYSTEM_OPTIONS::GenerateCustomerNumber, AR_SYSTEM_OPTIONS::GroupingRuleName, AR_SYSTEM_OPTIONS::InvoiceDeletionFlag, AR_SYSTEM_OPTIONS::LedgerName, AR_SYSTEM_OPTIONS::LocationTaxAccountSegments, AR_SYSTEM_OPTIONS::PartialDiscountFlag, AR_SYSTEM_OPTIONS::PayUnrelatedInvoicesFlag, AR_SYSTEM_OPTIONS::PopulateGlSegmentsFlag, AR_SYSTEM_OPTIONS::PostingDaysPerCycle, AR_SYSTEM_OPTIONS::PrintHomeCountryFlag, AR_SYSTEM_OPTIONS::PrintRemitTo, AR_SYSTEM_OPTIONS::RuleSetName, AR_SYSTEM_OPTIONS::RunGlJournalImportFlag, AR_SYSTEM_OPTIONS::SalesrepRequiredFlag, AR_SYSTEM_OPTIONS::ServicedByAnyBuFlag, AR_SYSTEM_OPTIONS::SiteRequiredFlag, AR_SYSTEM_OPTIONS::TaxInvoicePrint, AR_SYSTEM_OPTIONS::TrxHeaderLevelRounding, AR_SYSTEM_OPTIONS::UnearnedDiscount -->

The operation markers are the source-backed field boundary for create and update. Physical deletion remains a separate unresolved lifecycle contract; reverse-update cleanup, approved retained state, status, end date, inactivation, and other retirement behavior must not be represented as delete.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Identity and baseline | Prove one target business unit, one ledger, and the current same-task package contract |
| 2 | Reference and conditional rules | Resolve every populated reference and complete the applicable Billing and Revenue/Cash Processing set |
| 3 | Irreversible and cross-row behavior | Disclose header-rounding, Bills Receivable, MFAR, detailed-distribution, and claim-management effects before preview |
| 4 | Data Loader gate | Produce an immutable FSM preview and require separate exact approval; this resource layer never writes directly |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? | Source IDs |
|---|---|---|---|---|---|---|
| Every candidate | Error | verify_rso_package_baseline | Package identity, target/release, 202-column header contract, task result, or unrelated-row preservation is unproven | Refresh a same-task export/template and rebuild | Yes | SRC-FSM-PACKAGE |
| Any listed source-backed string field is supplied | Error |  | The candidate has not passed the exact character-length validation in ora_input_validation.md, or any listed value exceeds its recorded maximum | Shorten the affected business value, rerun validation, and generate a new immutable preview; never truncate or bypass the boundary | Yes | SRC-FSM-PACKAGE; SRC-CODE-EO; SRC-EDM-AR-SYSTEM-PARAMETERS-26C |
| Every candidate | Error | resolve_business_unit | Business unit is zero/many/unresolved | Correct the exact business-unit name or target reference data | Yes | SRC-CODE-AM-IMPL; SRC-UI-RSO-FORM |
| Every candidate | Error | resolve_ledger | Ledger is zero/many/unresolved, or package ledger currency conflicts | Correct the exact ledger name, currency, or target reference data | Yes | SRC-CODE-AM-IMPL; SRC-UI-RSO-FORM |
| Create operation | Error | resolve_receivables_rules | RuleSetName is missing, blank, or not accepted by the confirmed FSM import resolver | Supply an explicit application rule-set name; never infer or copy one from another business unit | Yes | SRC-CODE-AM-IMPL; SRC-CODE-AM-DEF; SRC-CODE-RESOLVER-APP-RULE-SET-VO; SRC-CODE-RESOLVER-APP-RULE-SET-EO; SRC-E2E-RSO-CREATE-RULESET-20260904 |
| Header-level rounding enabled | Error | resolve_and_validate_account_combination | Rounding account is blank or invalid | Supply a valid rounding account before preview | Yes | SRC-HELP-RSO-26C; SRC-CODE-EO-IMPL |
| Existing row has header-level rounding enabled | Error |  | Candidate attempts to disable it | Preserve enabled state; Oracle Help documents it as not reversible after save | No | SRC-HELP-RSO-26C |
| Salesperson required | Error |  | Approved sales-credit percent limit decision is absent | Supply an explicit limit or explicitly accept no limit when blank | Yes | SRC-HELP-RSO-26C |
| Printed-transaction changes or discount options change | Warning |  | Business owner has not reviewed downstream printed-transaction or discount behavior | Review the exact preview with Receivables owner | Yes | SRC-HELP-RSO-26C |
| Bills Receivable is disabled | Error |  | Dependent Bills Receivable records exist or absence is unproven | Keep enabled or prove no dependency | Yes | SRC-CODE-EO-IMPL |
| `CreateDetailedDist`/MFAR is enabled or changed | Error |  | Same-ledger propagation and existing-document impact are not disclosed and reviewed | Show every same-ledger BU potentially affected and block if document-history validation fails | Yes | SRC-CODE-EO-IMPL; SRC-CODE-ARP-DISTRIBUTIONS |
| Claim-management behavior changes | Error |  | Potential Claim Investigation payment-schedule sentinel creation is not disclosed | Include the potential side effect in preview and verification | Yes | SRC-CODE-EO-IMPL; SRC-CODE-ARP-PAY-SCHED |
| A populated reference has neither a supported public preflight contract nor a complete Confirmed FSM import resolution/validation contract | Error |  | The affected field would rely on a Partial, To collect, unsupported, or `TBD` resolver contract | Obtain the missing contract evidence or remove the field from the change | Yes | SRC-REST; SRC-CODE-AM-IMPL |
| A populated receipt-rule, exception-rule, Receivables-activity, or accounting-flexfield-prompt field uses its Confirmed FSM import-only contract | Error |  | The confirmed import contract or required input/context is missing before preview, or FSM import later surfaces an invalid dependency | Correct only the affected business/context key; do not invent a REST preflight or call internal components directly | Yes | SRC-CODE-AM-IMPL; SRC-CODE-AM-DEF; SRC-CODE-RESOLVER-AUTOCASH-VO; SRC-CODE-RESOLVER-AUTOMATCH-VO; SRC-CODE-RESOLVER-GROUPING-RULE-VO; SRC-CODE-RESOLVER-APP-RULE-SET-VO; SRC-CODE-RESOLVER-EXCEPTION-RULE-VO; SRC-CODE-RESOLVER-RECEIVABLE-ACTIVITY-VO; SRC-CODE-RESOLVER-ACCOUNTING-FLEXFIELD-VVO |
| Any attribute semantics remain unproved | Error |  | Candidate relies on task-owned authoring evidence marked Open, TBD, or Blocked for behavioral meaning | Ask one bounded business-language clarification; when the value is structurally valid but evidence remains unresolved, allow only an explicit nonproduction runtime-validation override followed by immutable preview and separate approval. Never ask the implementation user for developer authoring artifacts | Yes | SRC-FSM-PACKAGE |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_business_unit | Every candidate | Runtime organization identity and exact-match receipt | ora_reference_lookups.md |
| resolve_ledger | Every candidate | Ledger identity and chart-of-accounts receipt | ora_reference_lookups.md |
| resolve_receivables_rules | Every create and whenever a rule or hierarchy name is populated | Confirmed import contract and explicit rule names before preview; successful FSM import resolution before claiming completion | ora_reference_lookups.md |
| resolve_and_validate_account_combination | Any account segment populated | Ledger/COA and explicit segment provenance before preview; successful import validation before claiming completion | ora_reference_lookups.md |
| verify_rso_package_baseline | Every preview | Task/package/target/release/header/fingerprint receipt | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RSO.ENFORCE_DESIGN | decision | 50 | design_enforcement | passed->RSO.EXECUTION_GATE;blocked->RSO.HANDLE_ERROR | RSO.APPLY_DEFAULTS | stop | Before Data Loader preview |

<!-- E2E-DISCOVERY:RSO-E2E-DISC-001 -->
## CreateDetailedDist persisted canonicalization

Treat CreateDetailedDist persistence as field- and context-scoped. SystemParameterEOImpl.prepareForDML first normalizes null/blank to N, then applies ORA_CREATE_MULTIFUND_ACCOUNTING and same-ledger logic using MFAREnabledSystemParametersVVO (SetOfBooksId plus BindFlag over AR_SYSTEM_PARAMETERS_ALL). Reconciliation may accept blank-to-N only when the selected run proves the N branch and must retain the raw difference plus source IDs. Never treat blank-to-Y as equivalent; Y can propagate to same-ledger business units and remains a functional change.

<!-- E2E-DISCOVERY:RSO-E2E-DISC-003 -->
## Create application rule-set enforcement

For every create operation, require an explicit nonblank `RuleSetName` before preview or candidate ZIP generation. Do not infer a default or copy a value from another business unit. Resolve the supplied name only through `resolve_receivables_rules`; public REST preflight remains unavailable, so FSM import is authoritative for the `RuleSetName` to `RuleSetId` mapping. A missing or blank value is a local validation failure and must never reach import.

<!-- E2E-DISCOVERY:RSO-E2E-DISC-004 -->
## Transient ledger-currency reconciliation

For create, `LedgerCurrency` may be serialized from the exact resolved ledger receipt to validate ledger consistency. `SystemParameterCreateUIVO` defines it as transient and the successful four-row exact-task export left it blank. Reconciliation may therefore accept only this named candidate-value-to-blank result under the descriptor's `nonPersistedFields` contract, while retaining the raw difference and source IDs. Any other field mismatch remains a failure.

<!-- E2E-DISCOVERY:RSO-E2E-DISC-005 -->
## Implementation-user abstraction boundary

Developer authoring artifacts are internal evidence, not implementation-user prerequisites. Evaluate them internally and present only the business decision, supported choices, uncertainty, and likely FSM validation behavior. Never require an implementation user to provide the Attributes Workbook, Source Register, CodeSearch evidence, or internal CSV encodings. Use one bounded clarification for an unmapped business term; preserve an eligible explicit nonproduction runtime-validation override as evidence_unresolved and continue only through immutable preview and separate approval.

<!-- E2E-DISCOVERY:RSO-E2E-DISC-010 -->
## Same-ledger detailed-distribution effective-state preview

Before a create preview, use the fresh exact-task export and resolved LedgerName to identify existing same-ledger Receivables System Options rows. When any same-ledger row has CreateDetailedDist=Y, show Y as the effective result for every new target on that ledger and require explicit business acceptance; do not promise N. If the user does not accept Y, remove the affected target from the candidate. Keep N-to-Y as a material raw reconciliation difference rather than a global canonicalization. Request 286042 proved this behavior for two Vision City-ledger targets while all unrelated rows were preserved. Source IDs: SRC-CODE-EO-IMPL, SRC-CODE-MFAR-COUNT-VVO, and SRC-E2E-RSO-MFAR-SAME-LEDGER-20260904.
