# Manage Conversion Rates and Policies Input Validation

Before new-child requiredness checks, omit a new currency row when all four
setting inputs are blank. No exception is requested; this is currency-neutral
and never a USD-only validation error. Report omitted_empty_exceptions.
Existing child blanks retain fresh-export values. Remaining creates require
their source-required fields; optional percentages and parent Display flag
may be blank. No defaults or clearing are inferred. See
[nullable-value-contract.md](../references/nullable-value-contract.md).

This file validates task identity and source-backed package fields. A controlled FSM import accepted and persisted one parent create with BuName=Vision Interc Poland, UserConversionType=Corporate, flags Y/Y, tolerances 5/10 and no child row (`SRC-FSM-EXM-C1-20261001`). These are exact-case observations: C1 proved one parent create, and U1 proved WarningTolerance 5 to 6 to 5 for the same parent with no child row (`SRC-FSM-EXM-U1-20261001`). The later parent/child create and field-update cycles are observed (SRC-FSM-EXM-PARENT-20261014; SRC-FSM-EXM-CHILD-20261014). The supported workflow requires source-required fields on creates and explicit-merge updates preserving optional values, with fresh destination lookups. Unknown defaults, clearing, rekeying and deletion remain outside that contract; unknown Oracle error wording is not a preflight prerequisite.

## Sources

- Same-task FSM template and current-export inventories in the builder Source Register.
- `SRC-CODE-EXM-AMIMPL`, `SRC-CODE-EXM-ROOT-VO`, `SRC-CODE-EXM-CHILD-VO`, `SRC-CODE-EXM-ROOT-EO`, `SRC-CODE-EXM-CHILD-EO`.
- `SRC-CODE-EXM-UI-PAGE`, `SRC-CODE-EXM-UI-ROW`, `SRC-UI-EXM-DETAIL-20260930`.
- `SRC-CODE-EXM-UI-RULES-20261001` (parent/child page listeners, bean handlers, entity comparisons, and child currency check).

The finite/nonnegative numeric restriction is an explicit conservative
local preparation policy (`SRC-LOCAL-COMPLETE-ROW-POLICY-20261014`), implemented
by `scripts/build_fsm_from_workbook.py::_merge`. It does not assert a universal
Oracle numeric range or new import observations.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver | Evidence |
|---|---|---|---|---|---|---|
| Exact task package | ASM_SETUP_CSV_METADATA.xml and the two task CSV members with template-derived headers and node paths | Block candidate preparation | Obtain a fresh template and current export for EXM_MANAGE_CONVERSION_RATES_AND_POLICIES; validate task and member identity | Every candidate | | Same-task package inventory |
| Parent identity | BuName and UserConversionType for the intended business-unit policy | Block if the exact identity or conversion reference is missing or ambiguous | Supply exact destination values and complete governed operation evidence | Parent policy request | resolve_business_unit_by_name | SRC-CODE-EXM-AMIMPL, SRC-CODE-EXM-ROOT-EO |
| Currency exception identity | CurrencyCode for each requested child exception | Block if the child identity is missing or ambiguous | Supply destination code and verify it against the documented read-only path | Currency-specific exception request | resolve_currency_by_code | SRC-CODE-EXM-UI-CHILD, SRC-CODE-EXM-CHILD-EO |
| Operation contract | Exact create or update operation and field-level disposition | Require an entity-qualified create or update; new rows supply source-required fields and existing rows merge blanks from one fresh exact baseline match, preserving nullable values. Block unsupported operations | Parent and child creates and field updates observed; optionality follows nullable-value-contract.md; rekey, raw clearing and FSM deletion are outside workbook intake | Any create or update request | | Lifecycle evidence matrix; nullable-value-contract.md; SRC-FSM-EXM-C1-20261001; SRC-FSM-EXM-U1-20261001 |

## Field Validation

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: EXM_EXCHANGE_RATE_OPTION::BuName, EXM_EXCHANGE_RATE_OPTION::DfltExchangeRateFlag, EXM_EXCHANGE_RATE_OPTION::DispWarningToUser, EXM_EXCHANGE_RATE_OPTION::ErrorTolerance, EXM_EXCHANGE_RATE_OPTION::UserConversionType, EXM_EXCHANGE_RATE_OPTION::WarningTolerance, EXM_EXCH_RATE_TOLERANCE::CurrencyCode, EXM_EXCH_RATE_TOLERANCE::DfltExchangeRateFlag, EXM_EXCH_RATE_TOLERANCE::DispWarningToUser, EXM_EXCH_RATE_TOLERANCE::EXM_EXCHANGE_RATE_OPTION.BuName, EXM_EXCH_RATE_TOLERANCE::ErrorTolerance, EXM_EXCH_RATE_TOLERANCE::WarningTolerance -->
<!-- fscr-update-fields: EXM_EXCHANGE_RATE_OPTION::DfltExchangeRateFlag, EXM_EXCHANGE_RATE_OPTION::DispWarningToUser, EXM_EXCHANGE_RATE_OPTION::ErrorTolerance, EXM_EXCHANGE_RATE_OPTION::UserConversionType, EXM_EXCHANGE_RATE_OPTION::WarningTolerance, EXM_EXCH_RATE_TOLERANCE::DfltExchangeRateFlag, EXM_EXCH_RATE_TOLERANCE::DispWarningToUser, EXM_EXCH_RATE_TOLERANCE::ErrorTolerance, EXM_EXCH_RATE_TOLERANCE::WarningTolerance -->

The field markers describe observed caller-field roles and writability. They do not waive unresolved validation or approve a live operation. Identities select existing records; audits remain empty system-owned cells.

The optional Excel intake is a local input representation, not an FSM import package. Its exact two-tab, row-4 header contract is parsed by `scripts/build_fsm_from_workbook.py`. For an existing row, an empty field value cell retains the corresponding business value from one exact matching row in the fresh current export, including a blank value. Blank cells never request nulling. New rows require identities, parent conversion type, Default flag and child Display flag; optional percentages and parent Display flag may be blank. Duplicate parent business units and duplicate child business-unit/currency pairs block candidate generation. The generated ZIP remains review-only until core preflight, all Task Hook rules and exact-artifact approval pass. Validate every merged row, including carried siblings, using the source-backed nullable-value contract.

| Check | What Happens | Applies When | Resolver | Evidence |
|---|---|---|---|---|
| Exact CSV shape | Use the current same-task template for member names and ordered headers; reject short or long records and preserve explicit trailing blanks | Any candidate ZIP | | Same-task template inventory |
| Root references | Preserve the exact requested BuName and UserConversionType; do not substitute display labels for stored codes without the task import mapping | Parent row | resolve_business_unit_by_name | SRC-CODE-EXM-AMIMPL, SRC-CODE-GL-PVO |
| Child currency | Preserve CurrencyCode as a code and check destination availability; UI required marker is not proof of FSM import requiredness | Child row | resolve_currency_by_code | SRC-CODE-EXM-UI-CHILD, SRC-CODE-EXM-CURRENCY-LOV |
| Policy flags | Normalize literal Yes/No to Y/N; require Default on both entities and Display on the child. Parent Display may be blank. Reject populated codes other than Y/N. Do not predict the server diagnostic | DfltExchangeRateFlag or DispWarningToUser on either entity | | nullable-value-contract.md; SRC-CODE-EXM-UI-PAGE, SRC-CODE-EXM-UI-ROW |
| Warning checkbox dependency | In the parent or child UI, clearing WarningTolerance clears the corresponding Display Warning checkbox and disables it while warning is empty; flag a contradictory proposed combination for review rather than silently changing a CSV value | WarningTolerance is empty and DispWarningToUser is Y | | SRC-CODE-EXM-UI-RULES-20261001 |
| Percentage ordering | For parent and child rows with both values present, the entity validators require ErrorTolerance strictly greater than WarningTolerance; equality fails. Preserve the supplied values; do not infer the exact FSM import error or null-side behavior | Both policy thresholds supplied | | SRC-CODE-EXM-UI-RULES-20261001 |
| Percentage tolerances | Allow blank optional percentages. Validate populated values as finite, nonnegative decimals and compare ErrorTolerance greater than WarningTolerance only when both are populated. No Oracle upper limit or universal acceptance is claimed; failed imports use actual ProcessLog diagnostics | Policy threshold supplied or preserved | | nullable-value-contract.md; SRC-CODE-EXM-ROOT-EO, SRC-CODE-EXM-CHILD-EO |
| Audit fields | Keep all five audit headers and serialize blank cells; Fusion populated create audits and maintained update audits in the observed parent/child imports | Either entity | | SRC-CODE-EXM-ROOT-EO, SRC-CODE-EXM-CHILD-EO |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| EXMCR.VALIDATE_INPUT | step | 1 | validate_input | valid->EXMCR.CHECK_DEPENDENCIES;incomplete->EXMCR.BLOCKED | none | stop | Every create with required fields or explicit-merge update preserving nullable values; reject unsupported lifecycle requests |

<!-- E2E-DISCOVERY:DISC-EXM-U2-ERROR-TOLERANCE-20261002 -->
## Observed U2 parent ErrorTolerance input boundary

`SRC-FSM-EXM-U2-20261002` confirms exact one-row parent imports with ErrorTolerance 10 to 11 and a separately approved reversal from 11 to 10 for Vision Interc Poland / Corporate, flags Y/Y, WarningTolerance 5 and no child row. Both candidates left audit inputs blank. The result does not establish caller requiredness, defaults, accepted numeric range, other parent fields, child behavior or a general update contract.
