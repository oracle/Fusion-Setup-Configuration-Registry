# Manage Asset Calendars: Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Validate definition | Apply [Input Validation](ora_input_validation.md#field-validation). |
| 2 | Check existing state | Use resolve_existing_asset_calendar from [Reference Lookups](ora_reference_lookups.md#local-lookups). |
| 3 | Enforce import readiness | Block preview or import until every technical value has source evidence. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Any provided calendar field | Recommendation | | A value is valid but differs from available product guidance or established setup conventions | Explain the recommendation, rationale, and impact; retain the user's explicit value | Yes |
| Source GL calendar is monthly and has an adjustment period | Error | resolve_ledger_periods | The proposed FA depreciation or prorate calendar includes the GL adjustment-period row | Exclude only the GL adjustment-period row; preserve the source's regular monthly periods. Handle FA corrections in the applicable open FA period and post to GL's adjustment period if required. | Yes |
| Calendar will support a ledger-posting asset book | Blocker | resolve_ledger_periods | A proposed FA period name does not exactly equal the matching regular GL `EnteredPeriodName`, or its dates differ | Build the FA calendar from the ledger's regular GL period names and dates; exclude adjustment periods. Do not rely on date equivalence alone (for example, `Jan-2020` versus `Jan-20`). | Yes |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_ledger_periods | Ledger-derived calendar design | Regular and adjustment GL period rows | ora_reference_lookups.md |

## GL Adjustment-Period Handling

Apply the monthly-calendar rule in [Design Rules](#design-rules) without
changing the General Ledger accounting design. Fixed Assets has no matching
adjustment flag; copying the row can make it a depreciation period. For
nonmonthly calendars, do not apply that monthly-calendar rule automatically;
use the requested design and task-specific validation.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CAL.ENFORCE_DESIGN | decision | 50 | design_enforcement | pass->CAL.IMPORT_GATE;blocked->CAL.HANDLE_DESIGN | CAL.APPLY_DEFAULTS | stop | Defaults and lookup results are available |
