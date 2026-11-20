# Manage Payment Methods design enforcement

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: ORA_IBY_FD_PARENT_PAY_MET::AnticipatedFloat, ORA_IBY_FD_PARENT_PAY_MET::BankChargeBearerAplFlag, ORA_IBY_FD_PARENT_PAY_MET::DeliveryChannelAplFlag, ORA_IBY_FD_PARENT_PAY_MET::Description, ORA_IBY_FD_PARENT_PAY_MET::DocumentCategoryCode, ORA_IBY_FD_PARENT_PAY_MET::DueDayOfMonth, ORA_IBY_FD_PARENT_PAY_MET::DueMonthsForward, ORA_IBY_FD_PARENT_PAY_MET::EndDate, ORA_IBY_FD_PARENT_PAY_MET::ExclusivePmtAplFlag, ORA_IBY_FD_PARENT_PAY_MET::ExternalBankAcctAplFlag, ORA_IBY_FD_PARENT_PAY_MET::MaturityDateOffsetDays, ORA_IBY_FD_PARENT_PAY_MET::PaymentFormatAplFlag, ORA_IBY_FD_PARENT_PAY_MET::PaymentMethodCode, ORA_IBY_FD_PARENT_PAY_MET::PaymentMethodName, ORA_IBY_FD_PARENT_PAY_MET::PaymentModeCode, ORA_IBY_FD_PARENT_PAY_MET::PaymentReasonAplFlag, ORA_IBY_FD_PARENT_PAY_MET::PaymentReasonComntAplFlag, ORA_IBY_FD_PARENT_PAY_MET::PmtEnableAp, ORA_IBY_FD_PARENT_PAY_MET::PmtEnableAr, ORA_IBY_FD_PARENT_PAY_MET::PmtEnableCe, ORA_IBY_FD_PARENT_PAY_MET::RemittanceMessage1AplFlag, ORA_IBY_FD_PARENT_PAY_MET::RemittanceMessage2AplFlag, ORA_IBY_FD_PARENT_PAY_MET::RemittanceMessage3AplFlag, ORA_IBY_FD_PARENT_PAY_MET::SettlementPriorityAplFlag, ORA_IBY_FD_PARENT_PAY_MET::StartDate, ORA_IBY_FD_PARENT_PAY_MET::SupportBillsPayableFlag, ORA_IBY_FD_PARENT_PAY_MET::UniqueRemittanceIdAplFlag, ORA_IBY_FD_PARENT_PAY_MET::UriCheckDigitAplFlag, ORA_IBY_FD_PARENT_PAY_MET::FormatValue, IBY_FD_PAYMENT_METHOD::ApplicableTypeCode, IBY_FD_PAYMENT_METHOD::ApplicableValueFrom, IBY_FD_PAYMENT_METHOD::ApplicableValueTo, IBY_FD_PAYMENT_METHOD::ApplicationShortName, IBY_FD_PAYMENT_METHOD::BuName, IBY_FD_PAYMENT_METHOD::ExcludeFromApplicFlag, IBY_FD_PAYMENT_METHOD::LEName, IBY_FD_PAYMENT_METHOD::PaymentFlow, IBY_FD_PAYMENT_METHOD::PaymentMethodCode, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::AssignmentEntityId, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::EndDate, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::FieldNameCode, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::PaymentMethodCode, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::StartDate, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::TerritoryCode, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::ValAssignmentEntityType, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::ValidationSetCode, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::EndDateDisp, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::Description, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::Language, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::PaymentMethodCode, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::PaymentMethodName, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::SourceLang, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValParamDateValue, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValParamNumberValue, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValParamVarchar2Value, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValidationParameterCode, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValidationSetCode -->
<!-- fscr-update-fields: ORA_IBY_FD_PARENT_PAY_MET::AnticipatedFloat, ORA_IBY_FD_PARENT_PAY_MET::BankChargeBearerAplFlag, ORA_IBY_FD_PARENT_PAY_MET::DeliveryChannelAplFlag, ORA_IBY_FD_PARENT_PAY_MET::Description, ORA_IBY_FD_PARENT_PAY_MET::DocumentCategoryCode, ORA_IBY_FD_PARENT_PAY_MET::DueDayOfMonth, ORA_IBY_FD_PARENT_PAY_MET::DueMonthsForward, ORA_IBY_FD_PARENT_PAY_MET::EndDate, ORA_IBY_FD_PARENT_PAY_MET::ExclusivePmtAplFlag, ORA_IBY_FD_PARENT_PAY_MET::ExternalBankAcctAplFlag, ORA_IBY_FD_PARENT_PAY_MET::MaturityDateOffsetDays, ORA_IBY_FD_PARENT_PAY_MET::PaymentFormatAplFlag, ORA_IBY_FD_PARENT_PAY_MET::PaymentMethodName, ORA_IBY_FD_PARENT_PAY_MET::PaymentReasonAplFlag, ORA_IBY_FD_PARENT_PAY_MET::PaymentReasonComntAplFlag, ORA_IBY_FD_PARENT_PAY_MET::PmtEnableAp, ORA_IBY_FD_PARENT_PAY_MET::PmtEnableAr, ORA_IBY_FD_PARENT_PAY_MET::PmtEnableCe, ORA_IBY_FD_PARENT_PAY_MET::RemittanceMessage1AplFlag, ORA_IBY_FD_PARENT_PAY_MET::RemittanceMessage2AplFlag, ORA_IBY_FD_PARENT_PAY_MET::RemittanceMessage3AplFlag, ORA_IBY_FD_PARENT_PAY_MET::SettlementPriorityAplFlag, ORA_IBY_FD_PARENT_PAY_MET::StartDate, ORA_IBY_FD_PARENT_PAY_MET::SupportBillsPayableFlag, ORA_IBY_FD_PARENT_PAY_MET::UniqueRemittanceIdAplFlag, ORA_IBY_FD_PARENT_PAY_MET::UriCheckDigitAplFlag, ORA_IBY_FD_PARENT_PAY_MET::FormatValue, IBY_FD_PAYMENT_METHOD::BuName, IBY_FD_PAYMENT_METHOD::ExcludeFromApplicFlag, IBY_FD_PAYMENT_METHOD::LEName, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::EndDate, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::PaymentMethodCode, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::StartDate, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::TerritoryCode, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::EndDateDisp, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::Description, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::PaymentMethodName, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::SourceLang, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValParamDateValue, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValParamNumberValue, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValParamVarchar2Value -->

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Scope | Use exact Financials/Payments task and five-entity package; SRC-CATALOG-TASKS, SRC-FSM-PACKAGE |
| 2 | Field contracts | Exclude audit and unsupported fields; retain unresolved fields as blocked; Attributes Workbook |
| 3 | References | Run applicable supported preflights; retain partial FSM resolver gates |
| 4 | Execution handoff | Run Book and Data Loader own preview, approval, import and reconciliation |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Every candidate | Blocker |  | Exact task/package identity or header/type contract mismatches | Correct the task-matched candidate; SRC-FSM-PACKAGE | Yes, with new preview |
| Unresolved update field | Blocker |  | No field-level update evidence or governed application-validation choice | Keep disposition unresolved; do not claim product rejection | Only via governed choice |
| Any partial reference contract | Blocker |  | Candidate requires an unconfirmed resolver or configured value | Resolve the exact contract and revalidate | Yes, after evidence |
| Mutation handoff | Blocker |  | No immutable preview, separate approval, or current environment authorization | Use Run Book and Data Loader gates | No task-local write |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PM.DESIGN | step | 50 | design_enforcement | ok->PM.GATE;blocked->PM.RETURN_ISSUES | PM.DEFAULTS | stop | Every candidate |

## Source-reviewed import side effects

Sources: SRC-DEBUG-IMPORT; SRC-REVIEW-PARENT-IMPL. These rules are source-confirmed; deployed behavior remains separately qualified.

- For a serialized payment-method parent, AP/AR/CE flag N can remove that application's existing usage rows, including a retained N flag on an unrelated parent edit. Inspect the fresh baseline and stop if this would violate preserved-row create/update. Do not treat the deletion as an implicit approved operation.
- Moving PAYER_ORG to blank all-BU scope can consolidate/remove existing specific-BU rows. Stop preserved-row create/update when those rows exist in the same method/application context.
- A seeded parent is removed from the import XML by the source hook; reject a request that would otherwise claim to update it.
- At least one of AP, AR or CE must remain enabled. Do not infer missing enablement flags or serialize defaults to satisfy this rule.
- Source-confirmed lookup mapping is distinct from environment identity/cardinality and live import qualification. A ready orchestration node means it can evaluate these conditional gates; it does not satisfy every resolver for every request.

## Exact package variants

The task-specific extension accepts the historical89-column parent and the exact observed87-column parent that omits only DueDayOfMonth and DueMonthsForward. The canonical descriptor retains all historical field/operation contracts. Current variant selection is immutable per operation and validates its full field/type/node fingerprint. Reject mixed/unknown variants and requests for absent fields; obtain a compatible export instead of fabricating columns.

For the observed87-column variant, declared calendar-date inputs remain strict ISO dates and serialize to the evidenced yyyy/MM/dd CSV representation. Reconciliation exposes raw format differences and compares only the same valid Gregorian date; strings, numbers, timestamps, unknown formats and changed days remain strict. Rollback converts only explicitly declared exported dates to strict input dates. Preserve every unrequested raw value.

Create usage/translation rows with their source-export ancestor-qualified PaymentMethodCode equal to the immutable portable code. This derives addressing, not another business input. Metadata remains byte-for-byte from the matching current source. No package variant or adapter key declaration can create a missing Fusion business-object definition.

## Usage and derived-field correctness

FSM discards matched incoming Usage rows of ordinary types. Reject actual scalar changes that the hook ignores; unchanged rows remain permitted. Fusion source gives CROSS_BORDER_FLAG and FOREIGN_CURRENCY_FLAG a distinct update branch. The current task contract nevertheless blocks their ApplicableValueTo changes under its fixed public key declaration; this is a task-contract limitation, not evidence that Fusion rejects the operation. Stop with that precise limitation and do not bypass key protections or recast the edit as create. Changing resolved BU/LE can change Usage identity and needs an explicit scope-change plan. Existing preserved-row and all-BU consolidation guards remain active. Source: SRC-CODE-IBY-SVC-AM-IMPL 556-638.

Do not omit requested Alias, application enablement or applicability to make a candidate pass. Report the field-specific issue and retain the business intent. Source-proven no-op, seed metadata and derived display constraints cannot be bypassed as evidence uncertainty. Eligible unresolved business fields retain governed application validation. Assignment source/display dates must agree; preservation verifies the derived relationship rather than ignoring the column.

<!-- E2E-DISCOVERY:DISC-PM-DATE-NOOP-001 -->
## Already-satisfied calendar dates

For an update whose requested values are already present, both memory and file package builders return no candidate. Compare declared calendar dates using the same strict ISO-input and source-export calendar equivalence used by reconciliation; different formatting of the same valid date is not a business change. Changed days and malformed formats remain changes or validation errors. Other scalar types retain exact comparison. Source: the qualified export date contract and existing reconciliation rules.
