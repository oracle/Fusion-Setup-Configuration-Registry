# Manage Asset Calendars: Defaulting Rules

## Defaults

| Field | Internal | Resolved value | Applies When | User Override | Resolver |
|---|---|---|---|---|---|
| Calendar-period start basis | No | Start Date of the exact selected Start Fiscal Year row in the selected fiscal year | Initial setup | Yes | resolve_calendar_date_basis_from_fiscal_year |
| Calendar-period end basis | No | Latest End Date from the selected Start Fiscal Year row forward in the exact selected fiscal year's complete contiguous date rows | Initial setup without a user-supplied calendar end basis | Yes | resolve_calendar_date_basis_from_fiscal_year |
| Description | No | Human-readable sentence-case form of Calendar Name | User leaves it blank for a new definition | Yes | |
| Period Suffix | No | `FISCAL` (`PeriodSuffixType` import value) | User does not supply a suffix | Yes, if valid | resolve_asset_calendar_export_metadata |
| Calendar period rows | No | Read each complete selected fiscal-year date row, divide its whole-calendar-month cycle by the requested periods per year, and generate the resulting contiguous groups. When an equal monthly partition is not possible, apply the supplied period-generation pattern. Number each fiscal year's groups from 1 through the requested count, generate `Mon-YYYY` names, and display dates in previews as `DD-Mon-YYYY`. | Always after the fiscal-year date rows and periods per year are validated | Yes, by supplying a different valid period-generation pattern | derive_periods_from_fiscal_year_cycle |
| Technical identifiers, CSV files, column order, internal codes, date format, and future-use or reserved fields | Yes | Exact values from a current same-task FSM export; retain its values for future-use or reserved fields when present | Before package generation | No | resolve_asset_calendar_export_metadata |

For a blank Description on a new definition, replace separators with spaces,
split camel-case words, retain recognized uppercase acronyms such as `FA`, and
lowercase ordinary words after the first word. For example, `FA_MONTHLY_CAL`
becomes `FA monthly cal`. Preserve a user-supplied description and validate the
resolved value against the description length limit.

## Values That Must Stay User-Supplied

| Value | Rule |
|---|---|
| Calendar Name | Apply [Missing Fiscal Year and Calendar Names](ora_input_validation.md#missing-fiscal-year-and-calendar-names). |
| Description | Keep the supplied value; when omitted, apply [Defaults](#defaults). |
| Fiscal Year Name | Apply [Missing Fiscal Year and Calendar Names](ora_input_validation.md#missing-fiscal-year-and-calendar-names) and the [fiscal-year relationship check](ora_input_validation.md#calendar-consistency-rules). |
| Start Fiscal Year | Require an existing exact `assetFiscalYear` row in the selected fiscal year. It may be later than the fiscal year's earliest available row, but not earlier. |
| Periods per Year | Require the supplied design or derive it only from approved ledger evidence. |
| Period-generation pattern | Supply this only when the selected fiscal-year cycle cannot be evenly partitioned into whole-calendar-month groups. The skill generates all period rows; do not ask the user to enter them individually. |

## Fiscal-Year Resolution

For every calendar, a valid user-selected Fixed Assets fiscal year takes
precedence over automatic resolution. Validate that selection against the
calendar requirement and reuse it without substitution. When the user has not
selected a fiscal year, show every qualifying equivalent with its exact name
and coverage and require the customer to select one, including a sole
candidate; do not apply a tie-break. When no equivalent fiscal
year exists, route to `FA_MANAGE_FISCAL_YEAR` and do not prepare the calendar
until that workflow confirms the created fiscal year is available.

When the user does not supply a Period Suffix, write `FISCAL` to the
`PeriodSuffixType` field in the calendar package. Do not replace this default
with a display label or omit the field.

Use the selected fiscal-year coverage when generating the calendar. The
selected Start Fiscal Year must identify an exact fiscal-year date row in the
selected fiscal year. Use that row's Start Date as the Calendar Start Basis and
generate that row and later contiguous selected rows. Do not generate calendar
periods before the selected row. The latest retained End Date remains the
default end basis. An explicit
user-approved ledger-derived start exception may replace only the start basis
for that ledger-derived calendar.

For a ledger-derived calendar, an explicit user-approved start at the earliest
complete regular GL period overrides the fiscal-year start basis. Preserve the
exact GL period name and dates for that first period and exclude any GL
adjustment period. The selected fiscal year's latest End Date remains the
calendar end basis unless the user explicitly supplies a different end basis.

For generated periods, use the selected fiscal-year date rows as the source of
the cycle. For each row, derive equal whole-calendar-month groups from the
requested count and generate the entire resolved coverage. Generate the period
names; do not treat them as user-supplied. Validate generated rows with the
same contiguity, uniqueness, start-basis, and end-basis checks
used for every calendar. If a cycle is not month-aligned or its month count is
not divisible by the requested count, do not guess boundaries; request a
period-generation pattern and generate the rows from it.

For Input, Design, Final ZIP, and Post-Execution previews, render generated
period names as `Mon-YYYY` and dates as `DD-Mon-YYYY`, for example
`Jan-2026 | 01-Jan-2026 | 31-Jan-2026`. This is a presentation convention only:
serialize dates in the exact format established by the current same-task FSM
export.

## Default Disclosure

After user inputs are collected and before ZIP preparation, list every applied
default in the user-facing proposal, including its field and resolved value.
The user may provide an explicit value to override any default whose User
Override column is `Yes`; revalidate the replacement before use. Always show
the resolved fiscal-year start and end bases. Require the first and last
calendar periods to align to them unless an explicit approved exception is
recorded.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CAL.APPLY_DEFAULTS | step | 40 | apply_default | applied->CAL.ENFORCE_DESIGN;blocked->CAL.HANDLE_DEPENDENCY | CAL.LOOKUP_EXISTING | stop | No equal existing calendar was found |
