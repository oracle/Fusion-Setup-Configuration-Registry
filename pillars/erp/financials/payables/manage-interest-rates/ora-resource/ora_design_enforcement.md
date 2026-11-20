# Design Enforcement

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_INTEREST_PERIOD::StartDate, AP_INTEREST_PERIOD::EndDate, AP_INTEREST_PERIOD::AnnualInterestRate -->
<!-- fscr-update-fields: AP_INTEREST_PERIOD::EndDate, AP_INTEREST_PERIOD::AnnualInterestRate -->

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Validate period bounds | From Date (`StartDate`) must be on or before To Date (`EndDate`); equal dates make a valid one-day interval. |
| 2 | Check overlap | Proposed date interval must not overlap another configured period; UI shows AP-810412. |
| 3 | Preserve identity | Match each update to exactly one fresh-export period by StartDate (UI From Date), the task-specific alternate key. Preserve it; row order, EndDate, and AnnualInterestRate are not match keys. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Create or end-date update | Blocker | | From Date (`StartDate`) is after To Date (`EndDate`) | Set From Date on or before To Date before preview | Yes |
| Create or end-date update | Blocker | | Proposed interval overlaps an existing interval; Oracle UI reports AP-810412 | Choose a nonoverlapping interval and regenerate preview | Yes |
| Update | Blocker | | StartDate changes, is absent or ambiguous in the fresh same-task current export, or appears more than once among requested updates | Select exactly one existing period by From Date and retain its StartDate; use a separately designed operation for a different From Date | Yes |
| Any import | Blocker | | Candidate preview, separate approval, and Data Loader route are missing | Follow core.data-loader governance | Yes |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| IRATE.ENFORCE_DESIGN | step | 30 | design_enforcement | pass->IRATE.EXECUTION_GATE;blocked->IRATE.DESIGN_BLOCKED | IRATE.CHECK_DEPENDENCIES | stop | Always |
