# Manage Transaction Types Dependency Readiness


## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Parent identity | Resolve exact SetCode and Name before any child or related-object resolution |
| 2 | Parent reference domains | Validate reference set, legal entity, application rule set, payment term, and related transaction type when applicable |
| 3 | Child accounting context | Resolve exact BuName and LedgerName before interpreting any segment combination |
| 4 | Environment-verified choices | Verify Partial lookup-backed values before serializing them |
| 5 | Data Loader boundary | Hand only a validated immutable FSM ZIP to core.data-loader |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| reference_set | Reference data set | Yes | Every parent create and every related set-qualified reference | Satisfied | Exact SetCode supplied by the implementor; FSM alternate-key validation is authoritative |  | SetCode scopes the parent identity and related references | Supply the exact reference-data-set code | SetCode |
| legal_entity | Legal entity | Conditional | LegalEntityIdentifier is supplied | Satisfied | Exact identifier supplied by the implementor; FSM alternate-key validation is authoritative |  | The legal entity is optional but must resolve exactly when present | Supply the exact legal-entity identifier or omit the optional field | LegalEntityIdentifier |
| application_rule_set | Receivables application rule set | Conditional | RuleSetName is supplied | Satisfied | Exact name supplied by the implementor; FSM alternate-key validation is authoritative |  | The named rule set must resolve uniquely | Supply the exact application rule-set name | RuleSetName |
| payment_term | Default payment term | Conditional | DefaultTermName or DefaultTermSetCode is supplied | Satisfied | Exact name and set code supplied together; FSM two-stage validation is authoritative |  | A term name without its set can cross scope | Supply both DefaultTermName and DefaultTermSetCode | DefaultTermName, DefaultTermSetCode |
| related_transaction_type | Related transaction type | Conditional | SubsequentTrxTypeName or CreditMemoTypeName is supplied | Satisfied | Exact related name and companion set code; FSM two-stage validation is authoritative |  | Related types must resolve within the intended set | Supply each related type with its matching SetCode | Related Name and SetCode |
| reference_account_context | Business unit and ledger | Conditional | A reference-account child row is emitted | Satisfied | Exact BuName and LedgerName supplied by the implementor; FSM validation is authoritative |  | Child accounting values are environment-specific | Supply exact business-unit and ledger names | BuName, LedgerName |
| environment_choice_codes | Creation sign, default transaction status, usage category, and transaction subclass | Conditional | Any listed field is requested | Blocked | RESOLVER-ENVIRONMENT-CHOICES |  | Exact current-environment codes remain unverified | Verify the exact code in the selected nonproduction environment or omit an optional field | CreationSign, DefaultStatus, UsageCategoryCode, TrxSubclassCode |
| account_combination | Ledger-specific account segments | Conditional | Any of ClearingSegments, DepositOffsetSegments, RevSegments, TaxSegments, UnbilledSegments, UnearnedSegments, DistSetSegments, DrcSegments, FreightSegments, RecSegments, BrUnpaidSegments, BrRemitSegments, or BrFactorSegments is supplied | Blocked | RESOLVER-ACCOUNT-COMBINATION |  | The authoritative FSM path may create a valid combination and is not read-only | Require explicit nonproduction runtime authorization; never synthesize or reorder segments | Exact ordered segment strings |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Exact supplied value and complete source-backed FSM validation contract exist | FSM validation may run only through the governed Data Loader flow |
| Blocked | Environment value, programmatic combination, or required pair is unresolved | No; stop before candidate handoff |
| Not applicable | Conditional field or child row is omitted | No lookup or creation is needed |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTT.CHECK_DEPENDENCIES | decision | 20 | resolve_dependency | ready->MTT.APPLY_DEFAULTS;blocked->RETURN_ISSUES | MTT.VALIDATE_INPUT | stop | Input validation succeeds |
