# Manage Conversion Rates and Policies Dependency Readiness

The task belongs to Financials Expenses. Business-unit and General Ledger conversion-type references must be resolved in the destination context before a candidate can be considered. A currency-specific exception additionally needs a destination currency. These are dependency preflights, not proof of FSM import acceptance.

## Sources

- `SRC-CODE-EXM-AMIMPL`, `SRC-CODE-BU-PVO`, `SRC-CODE-GL-PVO`, `SRC-CODE-EXM-CURRENCY-LOV`.
- `SRC-ORACLE-26C-REST-BU`, `SRC-ORACLE-26C-REST-TYPE`, `SRC-ORACLE-26C-REST-CURRENCY`.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Business unit | Resolve the exact destination business-unit name in its enterprise context; keep the import hook's BuName to OrgId mapping distinct from a public REST response |
| 2 | Conversion rate type | Resolve the exact destination UserConversionType and its stored ConversionType mapping |
| 3 | Currency | For each exception row, verify the exact CurrencyCode and enabled state in the destination |
| 4 | FSM import contract | Exact C1 parent create and U1 WarningTolerance 5 to 6 to 5 update/reversal observed (`SRC-FSM-EXM-C1-20261001`, `SRC-FSM-EXM-U1-20261001`); later parent/child field operations are observed; runtime reference verification, source-required fields and nullable-value-contract.md gate each Data Loader handoff; defaults and unsupported lifecycle actions are excluded |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| EXMCR.BU | Destination business unit | Yes | Parent policy | Lookup | Implementor-supplied BuName in destination enterprise | resolve_business_unit_by_name | Import hook maps BuName to OrgId using BusinessUnitP and BuAltKeyByName | Confirm exact destination name; stop on zero or ambiguous matches | BuName and resolved BusinessUnitId | SRC-CODE-EXM-AMIMPL, SRC-CODE-BU-PVO |
| EXMCR.TYPE | Destination conversion type | Yes | Parent policy | Lookup | Implementor-supplied UserConversionType | resolve_conversion_type_by_name | Import hook maps user-facing type to stored ExchangeRateType | Confirm exact destination type; stop on zero or ambiguous matches | UserConversionType and resolved ConversionType | SRC-CODE-EXM-AMIMPL, SRC-CODE-GL-PVO |
| EXMCR.CURRENCY | Destination currency | Conditional | Child exception | Lookup | Implementor-supplied CurrencyCode | resolve_currency_by_code | Require an enabled active destination currency before import, independently of server-side validation | Confirm the exact code and enabled state | CurrencyCode and enabled-state evidence | SRC-CODE-EXM-UI-CHILD, SRC-CODE-EXM-CURRENCY-LOV |
| EXMCR.IMPORT | Supported FSM operation | Yes | Any live handoff | Verify | Controlled same-task import and fresh export | | Parent/child create and field-update cycles observed; enforce exact identities, source-required fields, nullable percentages, blank audits and child carry-forward | Block clearing, rekeying, deletion, unknown fields and default-dependent creates; preserve optional blanks under nullable-value-contract.md | Supported operation, eligible fields, ProcessId, reconciliation | Lifecycle evidence matrix; nullable-value-contract.md; SRC-FSM-EXM-C1-20261001; SRC-FSM-EXM-U1-20261001 |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Lookup | An exact destination reference needs read-only verification | Lookup only after the active workflow authorizes the read; never create a reference from this task |
| Blocked | A requested operation lies outside creates with source-required fields or supported explicit-merge updates preserving nullable values | No Fusion import or dependent setup creation |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| EXMCR.CHECK_DEPENDENCIES | step | 2 | resolve_dependency | satisfied->EXMCR.LOOKUP_BU;unresolved->EXMCR.BLOCKED | EXMCR.VALIDATE_INPUT | stop | Every candidate; require source-backed create/update ownership and complete same-target evidence |
