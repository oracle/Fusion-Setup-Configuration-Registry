# Manage Conversion Rates and Policies Design Enforcement

Expense conversion-rate policy can use a business-unit rate type and currency exceptions. Warning and error percentages influence runtime expense behavior. Parent and child entity comparisons are source-backed; the exact import-side range and error behavior remain unresolved. These rules constrain candidate design and preserve the source boundary.

## Sources

- [26D Options for Configuring Expense Policies](https://docs.oracle.com/en/cloud/saas/financials/26d/faiex/options-for-configuring-expense-policies.html) (`SRC-ORACLE-26D-EXPENSE-POLICIES`, rechecked 2026-10-14).
- [nullable-value-contract.md](../references/nullable-value-contract.md): frontend/EO percentage optionality and conditional comparisons, rechecked 2026-10-21. The remaining finite/nonnegative numeric preparation policy is not an Oracle numeric-domain claim.
- `SRC-CODE-EXM-AMIMPL`, `SRC-CODE-EXM-UI-PAGE`, `SRC-CODE-EXM-UI-ROW`, `SRC-UI-EXM-DETAIL-20260930`.
- `SRC-CODE-EXM-UI-RULES-20261001` (UI checkbox dependency, parent/child EO tolerance comparison, child CurrencyCode check).

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Establish policy context | Identify the intended business unit, conversion type, and whether currency exceptions are requested |
| 2 | Verify references | Use the task's declared read-only resolvers only after the active workflow selects them |
| 3 | Review policy flags and tolerances | Preserve supplied Y/N policy choices and percentage thresholds; do not invent a default or numeric range |
| 4 | Confirm import contract | Exact C1 parent create and U1 `WarningTolerance` `5 → 6 → 5` update/reversal observed (`SRC-FSM-EXM-C1-20261001`, `SRC-FSM-EXM-U1-20261001`); later parent and child field operations are recorded in SRC-FSM-EXM-PARENT-20261014 and SRC-FSM-EXM-CHILD-20261014; handoff requires the bounded preparation contract, verified references and core Task Hook; unobserved defaults/clearing/rekey/deletion remain unsupported |

## Design Rules

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: EXM_EXCHANGE_RATE_OPTION::BuName, EXM_EXCHANGE_RATE_OPTION::DfltExchangeRateFlag, EXM_EXCHANGE_RATE_OPTION::DispWarningToUser, EXM_EXCHANGE_RATE_OPTION::ErrorTolerance, EXM_EXCHANGE_RATE_OPTION::UserConversionType, EXM_EXCHANGE_RATE_OPTION::WarningTolerance, EXM_EXCH_RATE_TOLERANCE::CurrencyCode, EXM_EXCH_RATE_TOLERANCE::DfltExchangeRateFlag, EXM_EXCH_RATE_TOLERANCE::DispWarningToUser, EXM_EXCH_RATE_TOLERANCE::EXM_EXCHANGE_RATE_OPTION.BuName, EXM_EXCH_RATE_TOLERANCE::ErrorTolerance, EXM_EXCH_RATE_TOLERANCE::WarningTolerance -->
<!-- fscr-update-fields: EXM_EXCHANGE_RATE_OPTION::DfltExchangeRateFlag, EXM_EXCHANGE_RATE_OPTION::DispWarningToUser, EXM_EXCHANGE_RATE_OPTION::ErrorTolerance, EXM_EXCHANGE_RATE_OPTION::UserConversionType, EXM_EXCHANGE_RATE_OPTION::WarningTolerance, EXM_EXCH_RATE_TOLERANCE::DfltExchangeRateFlag, EXM_EXCH_RATE_TOLERANCE::DispWarningToUser, EXM_EXCH_RATE_TOLERANCE::ErrorTolerance, EXM_EXCH_RATE_TOLERANCE::WarningTolerance -->

The field markers describe observed caller-field roles and writability. They do not waive unresolved validation or approve a live operation. Identities select existing records; audits remain empty system-owned cells.

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? | Evidence |
|---|---|---|---|---|---|---|
| A parent policy is proposed | Blocking | resolve_business_unit_by_name | Exact destination business unit is absent or ambiguous | Correct BuName and rerun the read-only preflight | Yes | SRC-CODE-EXM-AMIMPL, SRC-CODE-BU-PVO |
| A parent policy is proposed | Blocking | resolve_conversion_type_by_name | Exact destination UserConversionType is absent or ambiguous | Select a destination conversion type and preserve its user-facing name in the package | Yes | SRC-CODE-EXM-AMIMPL, SRC-CODE-GL-PVO |
| A currency exception is proposed | Blocking | resolve_currency_by_code | CurrencyCode is unknown or the destination currency is not enabled | Correct the code or destination setup and repeat the documented preflight; do not predict Oracle import errors | Yes | SRC-CODE-EXM-CURRENCY-LOV, SRC-CODE-EXM-UI-CHILD |
| Both warning and error percentages are supplied on a parent or child row | Blocking | | ErrorTolerance is less than or equal to WarningTolerance | Correct the proposed values so ErrorTolerance is strictly greater; exact FSM import rejection remains unproved | Yes | SRC-CODE-EXM-UI-RULES-20261001 |
| WarningTolerance is empty on a parent or child row | Blocking | | DispWarningToUser is proposed as Y despite the UI clearing and disabling the checkbox in this state | Resolve the conflicting intent; do not automatically alter the import package | Yes | SRC-CODE-EXM-UI-RULES-20261001 |
| Warning or error tolerance is supplied | Blocking | | A populated merged value is nonnumeric, nonfinite or negative, or both percentages are populated and error is not greater than warning | Allow nullable percentages and preserve blank baseline values; correct invalid populated values without claiming an Oracle upper bound or exact server error | Yes | nullable-value-contract.md; SRC-CODE-EXM-ROOT-EO |
| A requested operation or field lies outside the entity-qualified observed contracts | Blocking | | Rekey, FSM deletion, unknown default reliance or an unproved field operation is requested | Promote reviewed controlled evidence together across task artifacts | No | Lifecycle evidence matrix; SRC-FSM-EXM-C1-20261001; SRC-FSM-EXM-U1-20261001 |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_business_unit_by_name | Parent policy context | BuName and destination enterprise | ora_reference_lookups.md |
| resolve_conversion_type_by_name | Parent policy context | UserConversionType | ora_reference_lookups.md |
| resolve_currency_by_code | Currency exception context | CurrencyCode | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| EXMCR.CHECK_DESIGN | step | 6 | design_enforcement | passed->EXMCR.EXECUTION_GATE;blocked->EXMCR.BLOCKED | EXMCR.LOOKUP_CURRENCY | stop | Enforce source-required fields, nullable percentages, ordering when both populated, verified references and preservation |

<!-- E2E-DISCOVERY:DISC-EXM-C1-CREATE-20261001 -->
## Observed parent-create boundary

`SRC-FSM-EXM-C1-20261001` confirms that one exact parent create with Vision Interc Poland / Corporate, flags Y/Y, tolerances 5/10 and no child row was accepted and persisted. The full before/after export shows unchanged unrelated rows. Do not infer other values, requiredness, a tolerance range, child creation, update, deletion or resolver error behavior from that observation.

<!-- E2E-DISCOVERY:DISC-EXM-U1-WARNING-TOLERANCE-20261001 -->
## Observed parent-update boundary

`SRC-FSM-EXM-U1-20261001` confirms that one parent WarningTolerance change from 5 to 6 and a separately approved reversal from 6 to 5 were accepted and persisted for Vision Interc Poland / Corporate with no child row. The final export restored all business values; 22 unrelated parent rows and 6 child rows were unchanged as full CSV-row multisets. The target's LastUpdateLogin and LastUpdateDate audit fields changed. Do not infer a general update contract, tolerance range, other field or target behavior, child preservation during update, or resolver error behavior.

<!-- E2E-DISCOVERY:DISC-EXM-U2-ERROR-TOLERANCE-20261002 -->
## Observed parent ErrorTolerance update boundary

`SRC-FSM-EXM-U2-20261002` confirms one parent ErrorTolerance change from 10 to 11 and a separately approved reversal from 11 to 10 were accepted and persisted for Vision Interc Poland / Corporate with no child row. The final export restored all business values; 22 unrelated parent rows and 6 child rows were unchanged as full CSV-row multisets. The target's LastUpdateLogin and LastUpdateDate audit fields changed. Do not infer a general update contract, tolerance range, other field or target behavior, child preservation during update, requiredness/defaults or resolver error behavior.

<!-- E2E-DISCOVERY:DISC-EXM-CONTRACTS-20261014 -->
## Observed matching, child preservation and removal boundary

SRC-FSM-EXM-PARENT-20261014 and SRC-FSM-EXM-CHILD-20261014 establish observed updates of the same parent and child under exact BU and BU/currency matching; unchanged sibling and parent business values were reconciled. SRC-FSM-EXM-OMISSION-20261014 establishes preservation of existing child full rows, including audits, when the present child CSV contains headers and no rows during a parent update. Absence of the CSV member or XML node is unproved. Keep workbook child carry-forward as a conservative candidate policy. SRC-FSM-EXM-UI-20261014 establishes UI removal of individual exceptions while retaining the parent; it does not establish FSM deletion or workbook deletion. Shared MigratorHelper implementation remains unavailable.
