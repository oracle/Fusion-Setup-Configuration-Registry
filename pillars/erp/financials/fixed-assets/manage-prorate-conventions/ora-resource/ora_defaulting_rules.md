# Manage Prorate Conventions: Defaulting and Prorate-Date Generation

## Standard Defaults

For creation, use supplied business values first and default only missing
values. Source new values from these skill rules and declared live reference
checks; never copy or derive them from exported CSV data rows.

| Field | Internal | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|---|
| Reference Data Set | No | Enterprise Set | Omitted during create preparation; preserve the existing selection on updates | No; keep an explicit selection | validate_reference_data_set_name |
| Description | No | Human-readable sentence-case form of Prorate Convention Name | Description is omitted for a new definition | No; keep a supplied Description | |
| Prorate day position | No | First day | Monthly or Following month has neither a supplied prorate date nor a day qualifier | No; supplied values take priority | |
| Depreciate when placed in service | No | No for create and update; do not derive it from the BOSS Boolean | The business flag is omitted | No; keep supplied Yes/No or Y/N | |
| Business date format | Yes | YYYY/MM/DD for business date fields; preview dates remain MM/DD/YYYY | Preparing business date cells; never infer format from exported values | No; format the date without changing it | |
| Depreciate when placed in service format | Yes | Yes/Y maps to YES. No/N maps to NO. Preserve these uppercase values in DeprWhenAcquiredFlag. | Serializing the business flag | No | |
| Fiscal-year boundary dates | Yes | Leave blank when omitted and preserve supplied values; omit columns absent from the current template | Preparing the parent row; no separate import-acceptance check or customer question is required | No | |
| Unspecified Convention Info DFF columns | No | Blank for a create; preserve each current value returned by resolve_existing_prorate_parent for an update | Convention Info is absent or omits an export column during create or update preparation | No; never copy values from a different convention | resolve_existing_prorate_parent |

Apply the Enterprise Set default before required-input validation; do not ask the
customer to supply a Reference Data Set when this default applies. Verify its
exact dropdown name and resolve SetCode through the existing lookup. Show the
resolved set in the preview; never hardcode its code or substitute another set
if Enterprise Set cannot be verified.

## Audit-Field Defaults

| Situation | What Happens |
|---|---|
| Scope | During create/update preparation, apply this policy only to CreatedBy, CreationDate, LastUpdatedBy, LastUpdateDate, and LastUpdateLogin when present in the parent or detail export header. These are system-managed fields, not business inputs. |
| New parent or detail row, including a new detail during update | Serialize a true empty CSV field: a zero-length value, not whitespace, null, None, or a date placeholder. Never source it from user input, the configured/authenticated username, current time, a login/session identifier, or another row. |
| Existing row in an explicit update | Preserve the exact audit text from that same row using resolve_existing_prorate_parent. Do not regenerate or reformat it. A missing or ambiguous existing-row match does not permit copying another row or blanking an existing row. |
| Unchanged baseline rows | Preserve their audit text when retained by the approved package scope. |
| Contract evidence | Populated audit samples and absent nullability annotations do not override this default. An explicit same-task import constraint contradicting this policy is a technical mapping gap. |
| Existing immutable ZIP | Not applicable; follow Immutable artifact in Design Rules. |

Pass this policy with the task mapping to the parent. Integrity and header
fidelity checks belong to [Design Rules](ora_design_enforcement.md#design-rules).

## Generation Contract

Consume the variant from [Prorate Basis Resolution](ora_input_validation.md#prorate-basis-resolution)
without reinterpreting business input. Output supplies prorate_date_rows.

| Topic | Behavior |
|---|---|
| Supplied schedule | Preserve supplied starting dates and generate exactly the requested positive whole number of months using actual month lengths and leap years. A first period end date supplies the first EndDate; a first prorate date supplies the first ProrateDate. Derive a missing first StartDate from the source month within verified fiscal-year coverage. Default only missing values; never extend a supplied count automatically. |
| Input | Consume normalizedFiscalYearRows from resolve_prorate_fiscal_year_range. Process each returned year separately in its supplied order using its own startDate, endDate, and nullable midyearStartDate. Apply Fiscal-year setup preservation in [Design Rules](ora_design_enforcement.md#design-rules). |
| Monthly and Following month ranges | Enumerate each year's intersecting calendar months in ascending order. StartDate is the later of the fiscal-year start and the month's first day; EndDate is the earlier of the fiscal-year end and the month's last day. Preserve separate clipped rows at a fiscal-year boundary within a month. |
| Monthly and Following month target | Monthly uses the source row's calendar month; Following month uses the next calendar month, including December-to-January rollover. |
| Day position | For those two families, First day is day 1, Mid-month is day 15, and Last day is the actual final day of the target month. |
| Half-year | Emit exactly one full-year tuple per returned fiscal-year interval: StartDate and EndDate are that year's exact boundaries; ProrateDate is its non-null midyearStartDate, otherwise the fallback below. |
| Half-year null-midpoint fallback | Only when that row's midyearStartDate is null, calculate inclusiveMonthCount as the calendar-month difference between start and end plus one. Add floor(inclusiveMonthCount divided by two) calendar months to that year's startDate, clamping the day only when the target month requires it. |
| Calendar arithmetic | Use date-only calendar arithmetic and advance from the original anchors. Preserve month-end dates: January 31 becomes February 28/29 and then March 31; otherwise clamp the original day only when needed. Never use fixed-day increments. For Monthly and Following month, do not clip ProrateDate to the generated range: it may precede a clipped StartDate or exceed the fiscal-year end. Half-year's in-range requirement is enforced in Design Rules. |
| Existing-ZIP basis resolution | Preserve the original archive. Compare retained supplied schedule requirements directly when available; otherwise match the supported basis candidates over the archive's requested scope, not unrelated available years. Require a unique match or an explicit basis hint; report ambiguity without rebuilding the ZIP. Apply Design Rules. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PRC.GENERATE_DATES | step | 20 | apply_default | generated->PRC.ENFORCE_DESIGN;generation_failed->PRC.HANDLE_GENERATION | PRC.LOOKUP_CONTEXT | stop | Apply Standard Defaults and Generation Contract to the resolved context, including immutable-archive candidate matching when applicable. Apply Audit-Field Defaults only to proposed create/update rows, without creating a ZIP. Pass any audit mapping conflict forward as a technical package gap. |
