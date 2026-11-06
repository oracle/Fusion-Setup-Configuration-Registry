# Input Validation

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_OTHER_PERIOD_TYPE::CalendarName, AP_OTHER_PERIOD_TYPE::CalendarType, AP_OTHER_PERIOD_TYPE::Description, AP_OTHER_PERIOD_TYPE::AttributeCategory, AP_OTHER_PERIOD_TYPE::Attribute1, AP_OTHER_PERIOD_TYPE::Attribute2, AP_OTHER_PERIOD_TYPE::Attribute3, AP_OTHER_PERIOD_TYPE::Attribute4, AP_OTHER_PERIOD_TYPE::Attribute5, AP_OTHER_PERIOD_TYPE::Attribute6, AP_OTHER_PERIOD_TYPE::Attribute7, AP_OTHER_PERIOD_TYPE::Attribute8, AP_OTHER_PERIOD_TYPE::Attribute9, AP_OTHER_PERIOD_TYPE::Attribute10, AP_OTHER_PERIOD_TYPE::Attribute11, AP_OTHER_PERIOD_TYPE::Attribute12, AP_OTHER_PERIOD_TYPE::Attribute13, AP_OTHER_PERIOD_TYPE::Attribute14, AP_OTHER_PERIOD_TYPE::Attribute15, AP_OTHER_PERIOD_TYPE::EffectiveFrom, AP_OTHER_PERIOD_TYPE::EffectiveTo, AP_OTHER_PERIOD_TYPE::PeriodFrequency, AP_OTHER_PERIOD_TYPE::PeriodNameFormat, AP_OTHER_PERIOD_TYPE::PeriodsPerYear, AP_OTHER_PERIOD_TYPE::StartDate, AP_OTHER_PERIOD_PERIOD::AP_OTHER_PERIOD_TYPE.CalendarName, AP_OTHER_PERIOD_PERIOD::AP_OTHER_PERIOD_TYPE.CalendarType, AP_OTHER_PERIOD_PERIOD::ApplicationId, AP_OTHER_PERIOD_PERIOD::CalendarName, AP_OTHER_PERIOD_PERIOD::CalendarType, AP_OTHER_PERIOD_PERIOD::Description, AP_OTHER_PERIOD_PERIOD::AttributeCategory, AP_OTHER_PERIOD_PERIOD::Attribute1, AP_OTHER_PERIOD_PERIOD::Attribute2, AP_OTHER_PERIOD_PERIOD::Attribute3, AP_OTHER_PERIOD_PERIOD::Attribute4, AP_OTHER_PERIOD_PERIOD::Attribute5, AP_OTHER_PERIOD_PERIOD::Attribute6, AP_OTHER_PERIOD_PERIOD::Attribute7, AP_OTHER_PERIOD_PERIOD::Attribute8, AP_OTHER_PERIOD_PERIOD::Attribute9, AP_OTHER_PERIOD_PERIOD::Attribute10, AP_OTHER_PERIOD_PERIOD::Attribute11, AP_OTHER_PERIOD_PERIOD::Attribute12, AP_OTHER_PERIOD_PERIOD::Attribute13, AP_OTHER_PERIOD_PERIOD::Attribute14, AP_OTHER_PERIOD_PERIOD::Attribute15, AP_OTHER_PERIOD_PERIOD::DueDate, AP_OTHER_PERIOD_PERIOD::EndDate, AP_OTHER_PERIOD_PERIOD::EnteredPeriodName, AP_OTHER_PERIOD_PERIOD::PeriodName, AP_OTHER_PERIOD_PERIOD::PeriodNum, AP_OTHER_PERIOD_PERIOD::PeriodYear, AP_OTHER_PERIOD_PERIOD::StartDate -->
<!-- fscr-update-fields: AP_OTHER_PERIOD_TYPE::Description, AP_OTHER_PERIOD_TYPE::AttributeCategory, AP_OTHER_PERIOD_TYPE::Attribute1, AP_OTHER_PERIOD_TYPE::Attribute2, AP_OTHER_PERIOD_TYPE::Attribute3, AP_OTHER_PERIOD_TYPE::Attribute4, AP_OTHER_PERIOD_TYPE::Attribute5, AP_OTHER_PERIOD_TYPE::Attribute6, AP_OTHER_PERIOD_TYPE::Attribute7, AP_OTHER_PERIOD_TYPE::Attribute8, AP_OTHER_PERIOD_TYPE::Attribute9, AP_OTHER_PERIOD_TYPE::Attribute10, AP_OTHER_PERIOD_TYPE::Attribute11, AP_OTHER_PERIOD_TYPE::Attribute12, AP_OTHER_PERIOD_TYPE::Attribute13, AP_OTHER_PERIOD_TYPE::Attribute14, AP_OTHER_PERIOD_TYPE::Attribute15, AP_OTHER_PERIOD_TYPE::EffectiveTo, AP_OTHER_PERIOD_PERIOD::AP_OTHER_PERIOD_TYPE.CalendarName, AP_OTHER_PERIOD_PERIOD::AP_OTHER_PERIOD_TYPE.CalendarType, AP_OTHER_PERIOD_PERIOD::Description, AP_OTHER_PERIOD_PERIOD::AttributeCategory, AP_OTHER_PERIOD_PERIOD::Attribute1, AP_OTHER_PERIOD_PERIOD::Attribute2, AP_OTHER_PERIOD_PERIOD::Attribute3, AP_OTHER_PERIOD_PERIOD::Attribute4, AP_OTHER_PERIOD_PERIOD::Attribute5, AP_OTHER_PERIOD_PERIOD::Attribute6, AP_OTHER_PERIOD_PERIOD::Attribute7, AP_OTHER_PERIOD_PERIOD::Attribute8, AP_OTHER_PERIOD_PERIOD::Attribute9, AP_OTHER_PERIOD_PERIOD::Attribute10, AP_OTHER_PERIOD_PERIOD::Attribute11, AP_OTHER_PERIOD_PERIOD::Attribute12, AP_OTHER_PERIOD_PERIOD::Attribute13, AP_OTHER_PERIOD_PERIOD::Attribute14, AP_OTHER_PERIOD_PERIOD::Attribute15, AP_OTHER_PERIOD_PERIOD::DueDate, AP_OTHER_PERIOD_PERIOD::EndDate, AP_OTHER_PERIOD_PERIOD::PeriodNum, AP_OTHER_PERIOD_PERIOD::StartDate -->

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Exact FSM package contract | AP_OTHER_PERIOD_TYPE.csv, AP_OTHER_PERIOD_PERIOD.csv, ASM_SETUP_CSV_METADATA.xml, and task identity AP_MANAGE_PAYABLES_CALENDARS | Block preview | Use the exact same-task template and current-data export package | Always | |
| Parent calendar identity | AP_OTHER_PERIOD_TYPE CalendarName and CalendarType | Block preview | Supply the parent identity using the exact package headers | When a calendar candidate is requested | |
| Child period parent linkage | AP_OTHER_PERIOD_PERIOD AP_OTHER_PERIOD_TYPE.CalendarName and AP_OTHER_PERIOD_TYPE.CalendarType matching one supplied parent calendar identity, with that parent header row included in the same FSM archive | Block preview | Add the matching parent header row and correct the child-to-parent key values before candidate preparation | When a period candidate is requested | |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Package members, header order, node paths, or parent-child keys differ from the exact template | Blocked | Do not build a candidate; restore exact same-task package fidelity | |
| A child period lacks the parent calendar identity or differs from its parent row | Blocked | Correct the parent-child linkage before preview | |
| Package structure and supplied identities pass the documented checks | Supported create/update boundary | Permit only the explicitly supported create fields and bounded update fields; keep every other default, value constraint, and update field unresolved | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Entity and header fidelity | Preserve the exact ordered headers for AP_OTHER_PERIOD_TYPE and AP_OTHER_PERIOD_PERIOD from the same-task template; reject renamed, reordered, added, or omitted fields | Always | |
| CSV row width | Require every nonempty row to contain its entity's exact header count and serialize trailing blank cells explicitly | Always | |
| Date serialization | Parse `YYYY/MM/DD` when retained from a fresh export, then serialize every nonblank candidate date as `YYYY-MM-DD` | Before candidate import | |
| Parent-child hierarchy | Preserve the metadata hierarchy and require each AP_OTHER_PERIOD_PERIOD parent-key pair to be explicitly serialized and match its AP_OTHER_PERIOD_TYPE parent identity | When a child row is supplied | |
| Audit fields | Do not accept CreatedBy, CreationDate, LastUpdatedBy, LastUpdateDate, or LastUpdateLogin as requester-authored create values | When those package columns are present | |
| Supported create fields | Permit the documented task field contract, including AttributeCategory and Attribute1 through Attribute15 on both calendar and period rows | Before candidate preparation | |
| Period DueDate | Require DueDate for PAYMENT TERMS calendar periods; permit a blank DueDate for GENERAL calendar periods. Validate every supplied DueDate as on or after EndDate | Before candidate preparation | |
| Bounded parent update fields | Permit AP_OTHER_PERIOD_TYPE.Description, EffectiveTo, AttributeCategory, and Attribute1 through Attribute15 for an exact existing CalendarName and CalendarType target when all other target values and unspecified rows are preserved; EffectiveTo must be on or after the retained EffectiveFrom | Before candidate preparation | |
| Bounded period update fields | Permit AP_OTHER_PERIOD_PERIOD.Description, StartDate, EndDate, PeriodNum, DueDate, AttributeCategory, and Attribute1 through Attribute15 for an exact existing CalendarName, CalendarType, and PeriodName target when all other target values and unspecified rows are preserved. AP_OTHER_PERIOD_TYPE.CalendarName and AP_OTHER_PERIOD_TYPE.CalendarType are required immutable parent-reference context, not mutable child business fields; enforce EndDate >= StartDate, DueDate >= EndDate when DueDate is supplied, require DueDate for PAYMENT TERMS calendars, prevent overlap with retained ranges, and keep (PeriodYear, PeriodNum) unique | Before candidate preparation | |
| Unproven field behavior | Do not infer defaults, value constraints, direct-write endpoints, or update support for any other package attribute | Before candidate preparation | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CALENDAR.VALIDATE_INPUT | step | 10 | validate_input | valid->CALENDAR.CHECK_LOCAL_VALUES;invalid->CALENDAR.INPUT_BLOCKED | none | stop | Always |

## Supporting Parent Validation

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
Validate all uploaded rows together so overlapping period creates and duplicate
year/period-number pairs are rejected when the header is unchanged, updated, or
newly created. For both user requests and uploaded ZIPs, compare requested
periods with each other and with retained baseline periods. Within the same
Calendar Name and Calendar Type, two periods cannot use the same year and
period number, even when their dates do not overlap.

## Explicit Clears and Final Period Dates

For an existing record, a populated description changed to blank is a requested
clear. Apply the same validation to NLP input and uploaded ZIPs. Blank optional
cells on new records remain omitted; required-field checks still apply.

Apply all requested period creates and updates to the fresh baseline before
checking for overlapping dates. Compare the final periods within the same
Calendar Name and Calendar Type, including periods left unchanged. Reject an
overlap involving a requested period, even when periods have different years.
A shared start/end date counts as an overlap. Use the final dates when another
period moves in the same batch. Existing overlaps between two unchanged periods
do not block an unrelated change.
