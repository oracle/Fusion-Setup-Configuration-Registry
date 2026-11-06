# Manage Asset Calendars: Input Validation

## Fiscal-Year-First Gate

An explicit request to reuse one exact existing Calendar Name is an exception
to this create-path gate. First read that calendar and its complete period rows;
do not render a Fiscal Year Name as required or ask for one. Report verified
reuse only when the exact named calendar and its linked Fiscal Year and period
rows are complete; otherwise report the lookup result and stop without a
create, update, package, or import.

For a user-defined create or update request, `CAL.CLASSIFY_REQUEST` must
transition to `CAL.CHECK_REQUIRED_INPUT` before any live lookup. Render the
complete `Input Preview` in the active Manage Asset Calendars chat, then check
the required inputs for this collection stage: exact Calendar Name, Start
Fiscal Year, and Periods per Year. Require an exact Fiscal Year Name when the
user selected one; when it is omitted, require enough fiscal-year cycle and
coverage detail to use the documented candidate-discovery path. Mark each
missing value **Required**, ask only for those values, and stop before Fiscal
Year or Calendar lookup, export, period generation, ZIP preparation, or import.
Description and Period Suffix may use their documented defaults. An initial
ledger-derived request follows its separate Ledger Name and Setup Scope gate;
an exact-name reuse request follows the reuse lookup path. A saved artifact,
link, or progress summary is not the chat preview. Only after this preflight
passes may the create or update path enter `CAL.VALIDATE_FISCAL_YEAR`.

After required-input preflight passes, validate a supplied Fiscal Year Name
exactly and case-sensitively against complete `assetFiscalYearDatesView` rows
before any other calendar
lookup, defaulting, period-row collection, or package preparation. A missing,
partial, or ambiguous fiscal year is a dependency blocker: report it and stop.
Do not accept a user assumption that the fiscal year exists as lookup evidence.

When the fiscal year exists but its requested Start Fiscal Year row is absent,
stop before period generation, ZIP creation, or import. Ask the user to select
an available exact `assetFiscalYear` row or extend the fiscal year; do not
substitute a nearest year automatically.

## Input Preview and Fiscal Year Selection

Before any live Fiscal Year lookup or missing-input stop, render the shared
`Input Preview` in the active Manage Asset Calendars chat. Show every supplied
business value and mark missing inputs required at the current collection
stage as **Required**. If Fiscal Year Name is omitted but candidate discovery
is supported by supplied cycle and coverage, show it as pending selection.
Do not ask for an arbitrary end year before checking existing Fiscal Years.

After the lookup, show every qualifying Fiscal Year with its exact name and
complete coverage. Require the customer to select one even when there is only
one qualifying Fiscal Year; the customer may instead provide another exact
Fiscal Year Name. If no qualifying Fiscal Year exists, request the Fiscal Year
details required to create or extend it through `FA_MANAGE_FISCAL_YEAR`.

## Required Groups

| Requirement group | Accepted fields | When missing | How to resolve | Applies when | Resolver |
|---|---|---|---|---|---|
| Calendar identity | Calendar Name, Start Fiscal Year, Periods per Year, Fiscal Year Name or enough cycle and coverage detail for candidate discovery; optional Description and Period Suffix | Stop after Input Preview, before lookup or package work | Request only missing required inputs for this collection stage; apply Description and Period Suffix defaults from ora_defaulting_rules.md. | User-defined setup, or ledger-derived setup after the fiscal-year decision gate | |
| Ledger-derived setup | Ledger Name and Setup Scope | Stop before deriving configuration detail | Provide the ledger and select Fiscal Year, Asset Calendar, or Both. | Only when the user explicitly asks to create or derive the calendar from a ledger | |
| Fiscal-year relationship | Fiscal Year Name | Stop after Input Preview, before package work | Apply the fiscal-year existence and calendar-date-basis check in [Field Validation](#field-validation). | Always | resolve_calendar_date_basis_from_fiscal_year |
| Calendar periods | Periods per Year plus the selected fiscal year's complete date rows | Stop after Input Preview, before package work | Generate period rows from the selected fiscal-year cycle and requested count. When equal whole-calendar-month groups are not possible, require an explicit period-generation pattern; do not require manually entered period rows. | Always | derive_periods_from_fiscal_year_cycle |

## Missing Fiscal Year and Calendar Names

For an initial ledger-derived request, Ledger Name and Setup Scope are enough
to perform the source lookups. Use the [Ledger-Derived Decision Prompt](#ledger-derived-decision-prompt)
after the lookup gate; do not reject missing calendar identity values before
that input-collection stage.

Retain explicit answers already supplied for the active request, target, and
ledger. Ask once for only the missing required values at each collection stage;
ask again only to correct an invalid or ambiguous answer. Do not derive or
suggest the Calendar Name from a ledger, fiscal year, export, project
artifact, prior attempt, existing setup, or unrelated context. A valid
user-supplied Fiscal Year Name takes precedence; otherwise resolve the Fiscal
Year Name from the calendar requirement under [Equivalent Fixed Assets Fiscal
Year Lookup](ora_reference_lookups.md#equivalent-fixed-assets-fiscal-year-lookup).
The Calendar Name must be exact user-supplied before calendar preparation.

For multiple ledgers, retain each ledger-to-name mapping. A shared name is
allowed only when the user explicitly assigns it and the existing-state check
proves that the shared configuration is appropriate.

For a user-defined asset-calendar request, use this selection prompt before
collecting a period-generation specification or preparing a package. Omit supplied fields and apply
[Defaults](ora_defaulting_rules.md#defaults) where allowed; do not ask again
merely to confirm an optional description or an applicable default:

```text
To create <AssetCalendarName>, please provide:
- Fiscal-year cycle and required coverage
- Start Fiscal Year
- Periods per Year
- Period Suffix: None / Calendar / Fiscal
- Description (optional)
```

For a user-defined calendar, do not ask for a Ledger Name or offer ledger
derivation as an alternative to supplying the required calendar fields or
period-generation inputs. The skill generates the period rows. Use the
following prompt only when the user explicitly requests a ledger-derived
calendar:

```text
To derive setup from a ledger, please provide:
- Ledger Name
- Setup Scope: Fiscal Year / Asset Calendar / Both
```

## Ledger-Derived Decision Prompt

This section owns the single ledger-derived evidence and missing-input prompt.
Use it only after the [No-Match Retry and Multi-Ledger Gate](ora_reference_lookups.md#no-match-retry-and-multi-ledger-gate)
is complete. Render the evidence table, recommendation, and missing-input
request in that order; do not repeat this interaction from another resource.

Start with this sentence:

```text
I verified the live ledger setup.
```

If the supplied name differs from the exact target display name, append one
short parenthetical correction; otherwise, do not add one. Render one row per
resolved ledger, preserving the table headings and separator row:

| Ledger | GL calendar | Fiscal-year pattern | GL periods | Existing equivalent Fixed Assets fiscal year | Existing equivalent Fixed Assets calendar | Fixed Assets treatment |
|---|---|---|---|---|---|---|
| `<exact ledger display name>` | `<configured calendar display name>` | `<regular fiscal-year start> to <regular fiscal-year end>; first complete fiscal year <start> to <end>` | `<regular-period count> <frequency> periods + <adjustment-period count> adjustment period(s)` | `<exact fiscalYearName>` or `None` or `Ambiguous` | `<exact calendar name>` or `None` or `Ambiguous` | `<treatment validated under Design Rules>` |

Populate Fixed Assets treatment from [Design Rules](ora_design_enforcement.md#design-rules).
Do not use the response template to introduce another adjustment-period rule.
Then render the following recommendation and input request, with a blank line
before each heading:

```markdown
## Recommendation

The selected Fixed Assets fiscal year and Start Fiscal Year establish the calendar coverage. Use the selected Start Fiscal Year row and later contiguous rows. In previews, label this `Calendar coverage (from selected Start Fiscal Year)`; do not use the technical phrase `retained coverage`. <State the exact equivalent Fixed Assets fiscal year and calendar when they exist; otherwise state the required creation or selection action.>

## Please provide

- Fiscal year: select one listed qualifying `<exact fiscalYearName>` or provide another exact Fiscal Year Name / route to `FA_MANAGE_FISCAL_YEAR` when no equivalent exists
- Asset calendar: use existing `<exact calendar name>` / select one of the listed equivalent calendars / create new asset calendar
- For each create-new choice, the exact user-approved name; for a new asset calendar, its required period suffix and description when supplied
```

Apply [Missing Fiscal Year and Calendar Names](#missing-fiscal-year-and-calendar-names).
When a user supplies a fiscal year, validate that it exists and satisfies the
calendar requirement; reuse it unchanged when valid. Do not replace an
explicit user selection with an automatically resolved candidate. When no
fiscal year is supplied, show every qualifying exact Fiscal Year Name with
coverage and ask the customer to select one, including when there is only one
candidate. Do not apply a tie-break or select a candidate automatically. When
no equivalent exists,
route fiscal-year creation through `FA_MANAGE_FISCAL_YEAR` and stop calendar
package preparation until its fresh availability check passes.
For a fiscal-year-only scope, omit the Asset Calendar choice. For an
asset-calendar-only scope, the reused or newly created Fiscal Year Name must
identify an existing fiscal year before calendar preparation.
For multiple ledgers, collect the choices in one ledger-to-input table. For
bulk input, show its first 10 rows and link the complete confirmation table.
Continue only after the [customer decision gate](ora_dependency_readiness.md#ledger-derived-customer-decision-gate)
is satisfied.

## Bulk Input Set

For 100 or more calendars, accept a parent table and a period-row table.
Link them with the exact Calendar Name; include Ledger Name when a ledger
mapping is supplied.

| Table | Required fields |
|---|---|
| Calendar parent | Ledger Name when applicable, Calendar Name, Description, Fiscal Year Name, Start Fiscal Year, Periods per Year, Period Suffix |
| Calendar period | Calendar Name, Period Name, Period Number, Start Date, End Date |

Apply [Field Validation](#field-validation) and
[Calendar Consistency Rules](#calendar-consistency-rules) to every parent and
period row. Reject period rows without exactly one parent. A rejected calendar
and its period rows do not invalidate unrelated calendars. Return row number,
calendar name when present, failed check, and correction required; never
silently omit a row.

## Field Validation

Validate the [Required Groups](#required-groups) and apply the structural
constraints in [Calendar Consistency Rules](#calendar-consistency-rules), then
run these additional checks.

| Check | Validation | Applies when | Resolver |
|---|---|---|---|
| Fiscal year exists | Reject a calendar that cannot be linked to an existing fiscal year. | Always | resolve_fiscal_year_for_calendar |
| Calendar date basis | Resolve the exact selected Start Fiscal Year from the selected fiscal year's complete date rows. If it is unavailable, block and require an available row or fiscal-year extension. The selected row's Start Date is the calendar start basis; retain only that row and later fiscal-year rows for the generated calendar. | Always | resolve_calendar_date_basis_from_fiscal_year |
| Generated periods | For each complete selected fiscal-year date row, calculate the number of full calendar months in the cycle. When that count divides evenly by the requested periods per year, group the equal number of whole months into each period. Otherwise apply the user-supplied period-generation pattern. Number periods from 1 through the requested count within each fiscal year, and generate names based on the first month in each group using `Mon-YYYY`. Display every preview start and end date as `DD-Mon-YYYY`. | Always | derive_periods_from_fiscal_year_cycle |
| Periods are contiguous and do not overlap | Reject gaps and overlapping date ranges. | Always | |
| Initial period | Reject a first period whose start date differs from the resolved Calendar Start Basis, unless a ledger-derived calendar has an explicit user-approved start at the earliest complete regular GL period evidenced by resolve_ledger_periods. | Initial calendar setup | resolve_calendar_date_basis_from_fiscal_year |
| Final period | Reject a last period whose end date differs from the resolved Calendar End Basis, unless the user explicitly approves a different end basis. | Initial calendar setup | resolve_calendar_date_basis_from_fiscal_year |
| Period suffix | Accept None, Calendar, or Fiscal as user-facing values; normalize an omitted value to `FISCAL` and write that exact value to `PeriodSuffixType`. | Always | resolve_asset_calendar_export_metadata |
| Period-name year suffix | Reject a two-digit year suffix when the calendar range can create duplicate period names. Use a four-digit year suffix, such as `Jan-1850`. | Before FSM ZIP preparation | |

## Calendar Consistency Rules

Run these checks before every immutable ZIP preview. Do not rely on a later
import error to discover an invalid calendar definition.

| Setup object | Constraint | Enforced validation |
|---|---|---|
| Calendar | Name is required, unique, and no longer than 15 characters. Description is optional and no longer than 40 characters. | Reject blank, duplicate, or overlength values. |
| Fiscal-year relationship | Fiscal Year Name is no longer than 30 characters. | Reject overlength values; apply the existence check in [Field Validation](#field-validation). |
| Period count | The number of periods per year is required. | Reject invalid supplied period counts. Apply [GL Adjustment-Period Handling](ora_design_enforcement.md#gl-adjustment-period-handling) when deriving the count from a ledger. |
| Calendar period | Each period needs a name, number, start date, and end date. Calendar and period names are no longer than 15 characters. | Reject blank or overlength values and a start date after its end date. |
| Calendar relationship | Every period belongs to the proposed calendar. | Require the parent calendar in the same archive or confirm that it already exists in the target environment. |
| Period uniqueness | A calendar cannot repeat a period name, start date, or period-number/start-date combination. | Reject duplicate period identities before preview. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CAL.CLASSIFY_REQUEST | decision | 1 | evaluate_result | explicit_reuse->CAL.LOOKUP_EXISTING_REUSE;create_or_update->CAL.CHECK_REQUIRED_INPUT | none | stop | A Calendar request is received |
| CAL.CHECK_REQUIRED_INPUT | decision | 3 | validate_input | valid->CAL.ROUTE_FISCAL_YEAR;invalid->CAL.HANDLE_INPUT | CAL.CLASSIFY_REQUEST | stop | Before any live lookup for create/update, render Input Preview and apply the required-input checks for the current user-defined or ledger-derived collection stage. Missing required input stops the request; exact-name reuse follows its separate lookup path. |
| CAL.ROUTE_FISCAL_YEAR | decision | 5 | evaluate_result | supplied->CAL.VALIDATE_FISCAL_YEAR;not_supplied->CAL.DISCOVER_FISCAL_YEARS | CAL.CHECK_REQUIRED_INPUT | stop | Required-input preflight passed; classify whether an exact Fiscal Year Name was supplied. This node performs no live lookup. |
| CAL.CONFIRM_FISCAL_YEAR | decision | 9 | evaluate_result | candidate_selected->CAL.VALIDATE_FISCAL_YEAR;another_exact_name_supplied->CAL.VALIDATE_FISCAL_YEAR;fiscal_year_details_needed->CAL.HANDLE_INPUT;selection_pending->CAL.HANDLE_INPUT | CAL.DISCOVER_FISCAL_YEARS | stop | Evaluate the customer selection from the complete candidate list, including a sole candidate. A selected candidate or another exact supplied name must pass CAL.VALIDATE_FISCAL_YEAR; an unanswered selection returns missing input. |
| CAL.VALIDATE_INPUT | decision | 15 | validate_input | valid->CAL.RESOLVE_DEPENDENCIES;invalid->CAL.HANDLE_INPUT | CAL.VALIDATE_FISCAL_YEAR | stop | The exact selected fiscal year and Start Fiscal Year passed CAL.VALIDATE_FISCAL_YEAR; apply Field Validation and Calendar Consistency Rules. |
