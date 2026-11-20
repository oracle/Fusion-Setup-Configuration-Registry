# Input Validation

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_INTEREST_PERIOD::StartDate, AP_INTEREST_PERIOD::EndDate, AP_INTEREST_PERIOD::AnnualInterestRate -->
<!-- fscr-update-fields: AP_INTEREST_PERIOD::EndDate, AP_INTEREST_PERIOD::AnnualInterestRate -->

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Exact task package | ASM_SETUP_CSV_METADATA.xml identifies AP_MANAGE_INTEREST_RATES and AP_INTEREST_PERIOD.csv matches the eight-column template header exactly | Block candidate preview | Re-export the exact task template and current state | Every operation | |
| New interest period | Explicit StartDate, EndDate, AnnualInterestRate | Block candidate preview | Supply all three business values | Create | |
| Matched update identity | StartDate from a unique same-task current export row, plus at least one supported changed field | Block candidate preview | Select the exact existing period; preserve StartDate | Update | |

For this task's FSM import, `AP_INTEREST_PERIOD.StartDate` (UI From Date) is the unique `AltKey` used to match an incoming row to an existing period. The entity defines that key and the task import implementation resolves primary keys through `AltKey` before reading the row. Match by calendar date, not CSV row position, To Date, or Rate (%). An update with no unique From Date match is blocked; a different From Date is a different identity and must not be presented as a change to the existing period. This contract is specific to Manage Interest Rates, not all FSM tasks.

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Exact package, target identity, or required business field is missing | Blocked | Correct request or obtain fresh same-task export | |
| Exact package and business values are complete | Ready for task design checks | Continue to date/rate and overlap checks | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Header and row width | Require exact template header order and eight RFC CSV fields per AP_INTEREST_PERIOD logical record, including trailing empty fields | Every candidate | |
| Required business fields | Reject blank StartDate, EndDate, or AnnualInterestRate for a new period; blank Rate (%) is visibly rejected in UI | Create | |
| Rate numeric range | Require a numeric AnnualInterestRate from 0 through 100 inclusive; UI reports AP-810443 outside range | Create or rate update | |
| Date shape | Use the exact package date type and reject malformed or ambiguous dates; UI display format is not a CSV format contract | Create or end-date update | |
| Date order | Require From Date (`StartDate`) on or before To Date (`EndDate`); accept equal dates as a one-day period and reject From Date after To Date | Create or end-date update | |
| Update field boundary | Keep StartDate as the import alternate key. Allow EndDate and AnnualInterestRate as supported update fields; do not treat audit fields or StartDate as editable update fields | Update | |
| Update target match | Normalize valid `YYYY-MM-DD` and `YYYY/MM/DD` StartDate values to the same calendar day; require exactly one match in the fresh current export. Reject missing or duplicate matches and duplicate requested StartDates before candidate generation. | Update | |
| Audit fields | CreatedBy, CreationDate, LastUpdatedBy, LastUpdateDate, and LastUpdateLogin appear in the exact export but are read-only in the service VO. Require blank audit cells and reject user-entered audit values; revalidate if the task template or release changes. | Every candidate | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| IRATE.VALIDATE_INPUT | step | 10 | validate_input | valid->IRATE.CHECK_DEPENDENCIES;invalid->IRATE.INPUT_BLOCKED | none | stop | Always |
