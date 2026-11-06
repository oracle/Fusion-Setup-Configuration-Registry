# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 10 | Parent calendar type | Establish the AP_OTHER_PERIOD_TYPE calendar identity before supplying related AP_OTHER_PERIOD_PERIOD rows |
| 20 | Child period rows | Bind AP_OTHER_PERIOD_PERIOD parent-key columns to the exact parent calendar identity |
| 30 | Create lifecycle semantics | Use the task-specific bounded create allowlist. For period rows, StartDate, EndDate, and PeriodNum are required. DueDate is required for PAYMENT TERMS calendars and optional for GENERAL calendars; when supplied it must be on or after EndDate. The parent Description is optional. |
| 40 | Update lifecycle semantics | Allow bounded exact-key updates, including AttributeCategory and Attribute1 through Attribute15 on both calendar and period rows. Preserve every other value; child parent-reference context remains immutable. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| parent_calendar_type | AP_OTHER_PERIOD_TYPE parent calendar | Yes | A period row is supplied | Satisfied when exact parent identity is supplied | Exact same-task package metadata and CSV headers | | Child rows carry AP_OTHER_PERIOD_TYPE.CalendarName and AP_OTHER_PERIOD_TYPE.CalendarType as parent keys | Supply a matching parent calendar identity before submitting period rows | AP_OTHER_PERIOD_PERIOD.AP_OTHER_PERIOD_TYPE.CalendarName; AP_OTHER_PERIOD_PERIOD.AP_OTHER_PERIOD_TYPE.CalendarType |
| field_lifecycle_contract | Field-level create/update semantics | Yes | Any create or update candidate is requested | Ready for the bounded create/update allowlists, including AttributeCategory and Attribute1 through Attribute15 on calendar and period rows | SRC-CODE-CALENDAR-SERVICE, SRC-IMPLEMENTOR-CONFIRMED-DFF-LIFECYCLE | | Preserve values outside the documented allowlists | Block any other update outside the bounded create/update allowlists | Payables |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Exact parent identity and package linkage are supplied | No lookup is implied |
| Blocked | Package linkage or field lifecycle semantics are missing | No; stop before preview |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CALENDAR.CHECK_DEPENDENCIES | step | 17 | resolve_dependency | ready->CALENDAR.ENFORCE_DESIGN;blocked->CALENDAR.INPUT_BLOCKED | CALENDAR.CHECK_LOCAL_VALUES | stop | Always; verify applicable parent linkage and bounded field lifecycle contracts before design enforcement |
