# Manage Receivables System Options Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Current task package | Bind successful same-task metadata/template evidence and the exact current header contract |
| 2 | Business unit and ledger | Resolve one active business unit with finBusinessUnitsLOV and one matching primary ledger; retain applicable function, legal-entity and chart-of-accounts receipts; use fresh RSO export for create/update existence checks |
| 3 | Reference-data sets and organizations | Resolve any set code, item-validation organization, and activity business units needed by populated fields |
| 4 | Rules, methods, sources, types, activities, and accounts | Resolve every applicable alternate key exactly once in dependency order |
| 5 | Conditional business rules | Prove the applicable Billing and Revenue/Cash Processing sets and source-backed design gates |
| 6 | FSM preview | Hand the complete package candidate to Data Loader for immutable preview; no mutation occurs in this resource layer |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| rso_package | Current `AR_SYSTEM_OPTIONS` package contract | Yes | Always | Verify | Fresh same-task export/template | verify_rso_package_baseline | Prevent stale headers, wrong object identity, and unrelated-row loss | Refresh from the target when any fingerprint or release differs | Shape and fingerprint receipt |
| business_unit | Business unit | Yes | Always | Lookup | finBusinessUnitsLOV plus fresh same-task export | resolve_business_unit | `ORG_ID` owns one system-options row per BU | Supply the exact business-unit name | Runtime organization ID |
| ledger | Ledger and chart of accounts | Yes | Always | Lookup | Approved Fusion read-only service | resolve_ledger | Ledger drives currency, accounting, and account-combination validation | Supply the exact ledger name and verify package currency | Ledger ID and chart-of-accounts receipt |
| item_validation_org | Item validation organization | Conditional | `ItemValidBUName` populated | Lookup | Approved Fusion read-only service | resolve_item_validation_org | Imported name must map to the internal organization | Supply the exact organization name | Item validation organization ID |
| receivables_rules | AutoCash hierarchy, automatch, grouping, and application rule set | Conditional | Corresponding name populated | Verify | Confirmed FSM import resolver; public preflight unavailable | resolve_receivables_rules | Import resolves each unique package name and stores the mapped internal identifier | Supply exact names and retain the immutable preview and require successful FSM import validation | AutocashHierarchyId, AutomatchRuleId, DefaultGroupingRuleId, RuleSetId |
| receipt_method | BA/CC receipt method | Conditional | Corresponding method name populated | Lookup | Approved Fusion read-only service | resolve_receipt_method | iReceivables receipt options depend on valid methods | Supply exact method names | Corresponding receipt-method IDs |
| reference_data_set | Reference-data set | Conditional | Set-code field populated | Lookup | Approved Fusion read-only service | resolve_reference_data_set | Exception rules, sources, and transaction types are set-scoped | Supply exact set code | Paired set ID |
| exception_rule | Exception rule | Conditional | Exception rule populated | Verify | Confirmed FSM import resolver after set-code resolution; public preflight unavailable | resolve_exception_rule | Unique rule identity depends on Name plus resolved SetId | Supply exact rule name and set code and retain the immutable preview and require successful FSM import validation | ExceptionRuleId |
| transaction_source | Transaction batch source | Conditional | Source name populated | Lookup | Approved Fusion read-only service | resolve_transaction_batch_source | Late-charge and BR source identity is set-scoped | Supply exact source and set | Source sequence ID |
| transaction_type | Invoice/debit-memo transaction type | Conditional | Type name populated | Lookup | Approved Fusion read-only service | resolve_transaction_type | Type identity is set-scoped | Supply exact type and set | Type sequence ID |
| receivables_activity | Receivables activity | Conditional | Activity name populated | Verify | Confirmed FSM import resolver after BU resolution; public preflight unavailable | resolve_receivables_activity | Unique activity identity is Name plus OrgId | Supply exact name and activity BU and retain the immutable preview and require successful FSM import validation | ExceptionAdjRecTrxId, ExceptionWrtoffRecTrxId, FinchrgReceivablesTrxId, or PenaltyRecTrxId |
| remittance_account | Remittance bank account | Conditional | BA/CC remittance account populated | Lookup | Approved Fusion read-only service | resolve_remittance_bank_account | Bank-account use is organization-scoped | Supply exact account name | Bank-account-use ID |
| flexfield_prompt | Accounting flexfield prompt | Conditional | `AiAcctFlexKeyLeftPrompt` populated | Verify | Confirmed FSM import existence validation; public preflight unavailable | validate_accounting_flexfield_prompt | Enabled GL# segment prompt must exist under the ledger-derived chart of accounts | Supply the exact prompt and retain the immutable preview and require successful FSM import validation | Existence validation receipt; no mapped value |
| account_combination | Accounting combinations | Conditional | Any account-segment field populated | Verify | Supported FSM import resolver | resolve_and_validate_account_combination | Reject proven invalid combinations; final resolver validation runs in FSM import | Supply valid concatenated segments | Ledger/COA and segment provenance; final import validation receipt |

## Dependency Classification

| Result Category | When Used | Can Continue? |
|---|---|---|
| Satisfied | Exact source-bounded value and receipt already exist | Yes |
| Lookup | An approved supported read-only Fusion lookup is required | Read-only only |
| Verify | Local package validation or a Confirmed FSM import resolution/validation contract is required | Local/supported import validation only |
| Blocked | Required value, package evidence, exact cardinality, applicable resolver contract, or semantic evidence is missing or fails | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RSO.CHECK_DEPENDENCIES | decision | 30 | resolve_dependency | ready->RSO.APPLY_DEFAULTS;blocked->RSO.HANDLE_ERROR | RSO.RESOLVE_REFERENCES | stop | After reference resolution and before defaults |
