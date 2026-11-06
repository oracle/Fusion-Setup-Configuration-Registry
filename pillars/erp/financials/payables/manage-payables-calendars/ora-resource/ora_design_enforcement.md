# Design Enforcement

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_OTHER_PERIOD_TYPE::CalendarName, AP_OTHER_PERIOD_TYPE::CalendarType, AP_OTHER_PERIOD_TYPE::Description, AP_OTHER_PERIOD_TYPE::AttributeCategory, AP_OTHER_PERIOD_TYPE::Attribute1, AP_OTHER_PERIOD_TYPE::Attribute2, AP_OTHER_PERIOD_TYPE::Attribute3, AP_OTHER_PERIOD_TYPE::Attribute4, AP_OTHER_PERIOD_TYPE::Attribute5, AP_OTHER_PERIOD_TYPE::Attribute6, AP_OTHER_PERIOD_TYPE::Attribute7, AP_OTHER_PERIOD_TYPE::Attribute8, AP_OTHER_PERIOD_TYPE::Attribute9, AP_OTHER_PERIOD_TYPE::Attribute10, AP_OTHER_PERIOD_TYPE::Attribute11, AP_OTHER_PERIOD_TYPE::Attribute12, AP_OTHER_PERIOD_TYPE::Attribute13, AP_OTHER_PERIOD_TYPE::Attribute14, AP_OTHER_PERIOD_TYPE::Attribute15, AP_OTHER_PERIOD_TYPE::EffectiveFrom, AP_OTHER_PERIOD_TYPE::EffectiveTo, AP_OTHER_PERIOD_TYPE::PeriodFrequency, AP_OTHER_PERIOD_TYPE::PeriodNameFormat, AP_OTHER_PERIOD_TYPE::PeriodsPerYear, AP_OTHER_PERIOD_TYPE::StartDate, AP_OTHER_PERIOD_PERIOD::AP_OTHER_PERIOD_TYPE.CalendarName, AP_OTHER_PERIOD_PERIOD::AP_OTHER_PERIOD_TYPE.CalendarType, AP_OTHER_PERIOD_PERIOD::ApplicationId, AP_OTHER_PERIOD_PERIOD::CalendarName, AP_OTHER_PERIOD_PERIOD::CalendarType, AP_OTHER_PERIOD_PERIOD::Description, AP_OTHER_PERIOD_PERIOD::AttributeCategory, AP_OTHER_PERIOD_PERIOD::Attribute1, AP_OTHER_PERIOD_PERIOD::Attribute2, AP_OTHER_PERIOD_PERIOD::Attribute3, AP_OTHER_PERIOD_PERIOD::Attribute4, AP_OTHER_PERIOD_PERIOD::Attribute5, AP_OTHER_PERIOD_PERIOD::Attribute6, AP_OTHER_PERIOD_PERIOD::Attribute7, AP_OTHER_PERIOD_PERIOD::Attribute8, AP_OTHER_PERIOD_PERIOD::Attribute9, AP_OTHER_PERIOD_PERIOD::Attribute10, AP_OTHER_PERIOD_PERIOD::Attribute11, AP_OTHER_PERIOD_PERIOD::Attribute12, AP_OTHER_PERIOD_PERIOD::Attribute13, AP_OTHER_PERIOD_PERIOD::Attribute14, AP_OTHER_PERIOD_PERIOD::Attribute15, AP_OTHER_PERIOD_PERIOD::DueDate, AP_OTHER_PERIOD_PERIOD::EndDate, AP_OTHER_PERIOD_PERIOD::EnteredPeriodName, AP_OTHER_PERIOD_PERIOD::PeriodName, AP_OTHER_PERIOD_PERIOD::PeriodNum, AP_OTHER_PERIOD_PERIOD::PeriodYear, AP_OTHER_PERIOD_PERIOD::StartDate -->
<!-- fscr-update-fields: AP_OTHER_PERIOD_TYPE::Description, AP_OTHER_PERIOD_TYPE::AttributeCategory, AP_OTHER_PERIOD_TYPE::Attribute1, AP_OTHER_PERIOD_TYPE::Attribute2, AP_OTHER_PERIOD_TYPE::Attribute3, AP_OTHER_PERIOD_TYPE::Attribute4, AP_OTHER_PERIOD_TYPE::Attribute5, AP_OTHER_PERIOD_TYPE::Attribute6, AP_OTHER_PERIOD_TYPE::Attribute7, AP_OTHER_PERIOD_TYPE::Attribute8, AP_OTHER_PERIOD_TYPE::Attribute9, AP_OTHER_PERIOD_TYPE::Attribute10, AP_OTHER_PERIOD_TYPE::Attribute11, AP_OTHER_PERIOD_TYPE::Attribute12, AP_OTHER_PERIOD_TYPE::Attribute13, AP_OTHER_PERIOD_TYPE::Attribute14, AP_OTHER_PERIOD_TYPE::Attribute15, AP_OTHER_PERIOD_TYPE::EffectiveTo, AP_OTHER_PERIOD_PERIOD::AP_OTHER_PERIOD_TYPE.CalendarName, AP_OTHER_PERIOD_PERIOD::AP_OTHER_PERIOD_TYPE.CalendarType, AP_OTHER_PERIOD_PERIOD::Description, AP_OTHER_PERIOD_PERIOD::AttributeCategory, AP_OTHER_PERIOD_PERIOD::Attribute1, AP_OTHER_PERIOD_PERIOD::Attribute2, AP_OTHER_PERIOD_PERIOD::Attribute3, AP_OTHER_PERIOD_PERIOD::Attribute4, AP_OTHER_PERIOD_PERIOD::Attribute5, AP_OTHER_PERIOD_PERIOD::Attribute6, AP_OTHER_PERIOD_PERIOD::Attribute7, AP_OTHER_PERIOD_PERIOD::Attribute8, AP_OTHER_PERIOD_PERIOD::Attribute9, AP_OTHER_PERIOD_PERIOD::Attribute10, AP_OTHER_PERIOD_PERIOD::Attribute11, AP_OTHER_PERIOD_PERIOD::Attribute12, AP_OTHER_PERIOD_PERIOD::Attribute13, AP_OTHER_PERIOD_PERIOD::Attribute14, AP_OTHER_PERIOD_PERIOD::Attribute15, AP_OTHER_PERIOD_PERIOD::DueDate, AP_OTHER_PERIOD_PERIOD::EndDate, AP_OTHER_PERIOD_PERIOD::PeriodNum, AP_OTHER_PERIOD_PERIOD::StartDate -->

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 10 | Package fidelity | Confirm exact CSV members, ordered headers, metadata node paths, and parent-child keys |
| 20 | Semantic readiness | Confirm documented field lifecycle contracts before candidate preparation |
| 30 | Governed execution | Require immutable preview and explicit approval before routing any import through core.data-loader |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Always | Error | | Package is not the exact same-task template/current-data contract | Re-export the exact task package and preserve every member, header, node path, and parent key | Yes, by replacing the package evidence |
| A create candidate contains a field outside the documented allowlist, or an update changes a field outside the bounded update allowlist | Error | | The field is outside the documented contract | Preserve exact keys and unrelated values. AttributeCategory and Attribute1 through Attribute15 are supported on calendar and period create/update rows; child parent references remain immutable, and date/period validations still apply | Yes, with documented lifecycle evidence |
| A live import is requested | Error | | Immutable preview, explicit candidate approval, and core.data-loader routing are absent | Create a governed preview and obtain approval before one submission | Yes, through the central workflow |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CALENDAR.ENFORCE_DESIGN | decision | 20 | design_enforcement | ready->CALENDAR.EXECUTION_GATE;blocked->CALENDAR.DESIGN_BLOCKED | CALENDAR.CHECK_DEPENDENCIES | stop | Always |

The task-node flow is **Input → Local value checks → Dependencies → Design → Execution gate**.
`CALENDAR.CHECK_LOCAL_VALUES` precedes `CALENDAR.CHECK_DEPENDENCIES`, followed by
`CALENDAR.ENFORCE_DESIGN`. This task has no defaulting node; the flow does not add
inferred defaults or live lookups. Each node is defined once in its owning resource
file; the generated registry connects them.

## Supporting Parent Preservation

For every period create or update, include its matching calendar header once
in the same FSM archive. Match both CalendarName and CalendarType.

- Existing calendar, no requested header change: copy its header from the fresh
  current-data baseline without changing any business value.
- Existing calendar, requested header change: use that baseline header and apply
  only the permitted changes the user requested.
- New calendar: include the explicitly requested calendar create row with the
  required values. Do not invent a calendar to satisfy a period request.
- Calendar absent from the baseline and no explicit calendar create: stop and
  ask the user to identify an existing calendar or request a new calendar.

Leave audit fields blank in all import rows. Preserve calendar dates when
converting the export date format to the import date format. Reject missing
parents, unrequested changes to supporting headers, and populated audit fields.
Other existing periods do not need to be copied into the candidate. For an
uploaded ZIP, require the header inside that ZIP; validation does not add it.
Validate all uploaded rows together. Apply period creates and updates to the
fresh baseline, then reject overlapping final dates involving a requested
period. Include periods left unchanged in this check. The check applies when
the header is unchanged, updated, or newly created.
