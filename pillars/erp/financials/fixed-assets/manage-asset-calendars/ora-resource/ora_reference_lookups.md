# Manage Asset Calendars: Reference Lookups

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| derive_periods_from_fiscal_year_cycle | After exact fiscal-year validation and period-count validation | Complete selected fiscal-year rows already validated in this task, requested periods per year, and an explicitly supplied generation pattern when needed | Apply Generated periods in ora_input_validation.md to the validated task evidence; this is a local calculation with no new lookup. | Complete generated calendar period rows, names, numbers, and dates | Missing validated rows or a required generation pattern blocks generation; do not guess. |

## Live Lookups

| Resolver | Runs When | Request | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_existing_asset_calendar_by_name | An explicit reuse request names one calendar | BOSS `assetCalendarsView` and `assetCalendarPeriodsView` through `core.fusion-api.rest-api-client` | Page both views completely. Match the exact Calendar Name and retain its linked Fiscal Year and all period rows. | Exact calendar identity, linked Fiscal Year, and complete period rows. | No exact name, duplicate name, incomplete paging, or incomplete period rows blocks reuse. Do not request a Fiscal Year or offer create/update. |
| resolve_existing_asset_calendar | Before create and immediately before import | BOSS `assetCalendarsView` and `assetCalendarPeriodsView` through `core.fusion-api.rest-api-client`, or the validated same-target data export under Complete Lookup Source Selection | Compare complete parent and period sets. Match exact Calendar Name, Fiscal Year Name, and requested periods. Use the governed export fallback when BOSS returns 403 or the first page hasMore=true. | Existing definition and differences, or validated empty Calendar setup | Complete BOSS no-data or a validated zero-row data export permits new-calendar preparation. One exact match permits verified reuse. One complete different definition requires the customer to choose update or create new. Multiple matches or unresolved source completeness block. |
| resolve_qualifying_fiscal_years_for_calendar | Fiscal Year Name is omitted after the Input Preview | `assetFiscalYearDatesView` through `core.fusion-api.rest-api-client` | Page all rows. Group rows by exact `fiscalYearName`; retain only names with complete, contiguous date rows that can satisfy the supplied calendar cycle, Start Fiscal Year, and period count. | Every qualifying exact Fiscal Year Name and its complete coverage. | No qualifying name requires Fiscal Year creation or extension details through `FA_MANAGE_FISCAL_YEAR`. Incomplete paging, unavailable data, or ambiguous coverage blocks; do not select a name. |
| resolve_calendar_date_basis_from_fiscal_year | Before deriving calendar period rows from a selected fiscal year | `assetFiscalYearDatesView` and the selected Start Fiscal Year | Page complete fiscal-year rows; match `fiscalYearName` and `assetFiscalYear` exactly and case-sensitively. Retain the selected row and later contiguous rows only. | Calendar Start Basis, Calendar End Basis, selected Start Fiscal Year, and retained fiscal-year rows. | Missing or ambiguous fiscal-year rows, an unavailable selected Start Fiscal Year row, or noncontiguous retained rows block. |
| resolve_fiscal_year_for_calendar | Before create or update | [Verified BOSS Request Contract](#verified-boss-request-contract) | Apply its exact-name and full-date-row comparison. | Existence and date-row comparison | Apply [BOSS Verification and Lookup Outcomes](#boss-verification-and-lookup-outcomes). |
| resolve_asset_calendar_export_metadata | Before package generation | Current same-target `FA_MANAGE_CALENDAR` export | Exact task and target only | Package members, columns, codes, date format, reserved fields | Do not prepare a package. |
| resolve_ledger_periods | Ledger-derived setup | Standard Fusion REST `ledgersLOV` and `accountingPeriodsLOV` through `core.fusion-api.rest-api-client`; an owning General Ledger export only when the REST contract is unavailable, incomplete, or ambiguous | One exact ledger; retain only exact period-set and period-type matches. | Ledger, calendar, regular and adjustment period rows | No exact match, multiple matches, or incomplete paging blocks. |
| resolve_equivalent_fiscal_years_for_ledger | Immediately after a ledger-derived lookup | `assetFiscalYearDatesView` through `core.fusion-api.rest-api-client` | Compare complete existing Fixed Assets fiscal-year date rows with each complete regular GL fiscal-year date range. | Equivalent Fixed Assets fiscal-year name(s), date rows, and unmatched ledger fiscal years. | Unavailable, partial, or ambiguous results are unresolved; do not select or create a fiscal year. |
| resolve_equivalent_asset_calendars_for_ledger | After equivalent fiscal-year lookup | BOSS `assetCalendarsView` and `assetCalendarPeriodsView` through `core.fusion-api.rest-api-client` | Compare each existing calendar linked to an equivalent fiscal year with the complete regular GL period rows. | Equivalent Fixed Assets calendar name(s), linked fiscal year, periods, and unmatched ledger fiscal years. | Unavailable, partial, or ambiguous results are unresolved; do not select or create a calendar. |

## Complete Lookup Source Selection

Start each BOSS collection with `$limit=1000`. When its first response has
`hasMore: false`, use that complete BOSS result. When it has `hasMore: true`,
stop BOSS pagination and obtain the current, same-target FSM data export
as the complete lookup source. Do not request a second BOSS page for that
collection. This is a bulk-read optimization, not a partial-result shortcut.
When either Calendar BOSS view returns 403, use this same governed export
fallback after the permitted authentication recovery. Access denial alone does
not block preparation when the fallback validates successfully.

Use an FSM snapshot only after all of the following pass:

1. The export completed successfully for the same target environment and was
   requested for the current validation or pre-import recheck. It must be an
   unfiltered setup-data export, not a template-only or specification export.
2. The `FA_MANAGE_CALENDAR` export contains `FA_CALENDAR.csv` and
   `ORA_FA_CALENDAR_PERIOD.csv`; their headers, parent/period relationships,
   and row shapes parse successfully.
3. For fiscal-year validation, the `FA_MANAGE_FISCAL_YEAR` export contains the
   fiscal-year date member needed to prove the exact fiscal-year rows. Do not
   use the Calendar export as a fiscal-year substitute.
4. The selected export members establish the complete in-scope parent and
   period sets. Missing members, unparseable rows, ambiguous duplicate keys, or
   incomplete scope block the lookup; they do not permit use of the first BOSS
   page as if it were complete.

When both validated members have headers and zero data rows, classify the
result as **empty Calendar setup** and satisfy the existing-calendar check.
With fiscal-year validation passed, continue to the Calendar Design Preview
through the existing defaulting and design checks. Do not introduce a
seeded-data blocker or require a waiver solely because this data export is
empty. This establishes the Calendar create path, not that all setup in the
environment is empty. Zero parents with nonzero periods, missing members,
filtered scope, failed export, or malformed/inconsistent data remain blockers.

After selecting the required snapshot path, compare all matching calendar
parents and their complete period rows from the export. Do not merge a partial
BOSS page with export rows. Persist the selected source, export process identifiers,
archive fingerprints, member counts, and comparison result. For the
immediately-before-import recheck, obtain a new complete source snapshot after
the immutable archive is finalized.

## BOSS Verification and Lookup Outcomes

## Existing Calendar Lookup Outcomes

After comparing the complete existing calendar and period rows, keep these
outcomes separate:

| Result | Required handling |
|---|---|
| Complete no-data result, including a validated unfiltered data export with zero parent and period rows | Classify as empty Calendar setup and continue with the proposed new calendar; no seeded-data waiver is required. |
| One exact matching definition | Report verified reuse; do not create or update. |
| One complete different definition | Show the exact differences and ask the customer to choose **update the existing calendar** or **create a new calendar**. Do not select either path automatically. |
| Multiple candidates, incomplete paging, unavailable source, or incomplete period rows | Treat as unresolved lookup evidence and stop. Do not offer update or create-new until the exact existing state is known. |

Before calendar preparation, apply the [Verified BOSS Request Contract](#verified-boss-request-contract)
and handle its result using the table below. For a newly created fiscal year,
repeat that availability check after import before proceeding to its calendar.

| Result | Required handling |
|---|---|
| Exact fiscal year with all required date rows | The calendar dependency is ready. |
| Exact fiscal year with an unavailable requested Start Fiscal Year | Stop and ask the customer to select an available Start Fiscal Year row or extend the fiscal year. Do not substitute a nearest row. |
| Fiscal year absent, partial, or different | Stop before calendar package preparation. |
| BOSS endpoint failure, incomplete result, or first response with `hasMore: true` | Require a current same-target `FA_MANAGE_FISCAL_YEAR` FSM export and apply the same exact-name and full-date-row comparison. For `hasMore: true`, the export is an allowed bulk-read selection under [Complete Lookup Source Selection](#complete-lookup-source-selection), not evidence that the first BOSS page is complete. Stop when that export is unavailable, incomplete, or ambiguous. |

## Configuration-Equivalent Asset Calendar Check

After the fiscal year and proposed periods are resolved, but before the Design
Preview or any package creation, use the complete BOSS result or the validated
FSM bulk snapshot selected under [Complete Lookup Source
Selection](#complete-lookup-source-selection). For each existing calendar whose
`FiscalYearName` exactly matches the proposed fiscal year and whose
`NumberPerFiscalYear` equals the proposed count, compare its complete period
set to the proposed set.

An existing calendar is configuration-equivalent only when it has the same
linked fiscal year, periods-per-year, and exactly one matching period for every
proposed period number, name, start date, and end date, with no extra or
missing periods. Calendar name and description are not comparison keys. Do not
treat a shared fiscal year, matching period count, partial coverage, or similar
name as equivalence.

Show every configuration-equivalent calendar in the Reference Validation
Preview. If one or more are found, stop before ZIP creation and ask the user to
reuse one exact named calendar or explicitly create a duplicate with the
requested name. Record that decision in the project artifact. Recheck both the
exact-name and configuration-equivalence outcomes immediately before import
using a new complete BOSS result or validated FSM bulk snapshot; if either
changes, invalidate the reviewed artifact and restart the review.

## Calendar Date Basis From Selected Fiscal Year

For a user-selected existing fiscal year, use the complete exact-name fiscal
year date rows as the authority for calendar coverage. The selected Start
Fiscal Year must match one exact `assetFiscalYear` row. Set the Calendar Start
Basis to that row's `startDate`, retain that row and later contiguous rows, and
set the Calendar End Basis to the latest retained `endDate`. This resolver does
not create, extend, or modify the fiscal year.

When an explicit ledger-derived start exception is approved, retain the
resolved end basis and replace only the start basis with the approved regular
GL period start. Record the fiscal-year rows and the exception in the project
artifact before generating period rows.

### Verified BOSS Request Contract

Use the BOSS client through `core.fusion-api.rest-api-client` with this
read-only resource:

```text
GET /api/boss/data/objects/ora/erpCore/fixedAssetsSetup/v1/assetFiscalYearDatesView
```

Request `$limit=500` and page with `$offset` until `hasMore` is `false`.
Validate `fiscalYearName` as an exact, case-sensitive match and compare
`assetFiscalYear`, `startDate`, `endDate`, and `midyearStartDate` to the
calendar's required fiscal-year rows. Use the current date only with a row's
inclusive `startDate` and `endDate` range; do not infer a fiscal year or period
from response order or a partial result set.

## Ledger Period Lookup Rules

Apply the [Standard Fusion REST Ledger-Period Contract](#standard-fusion-rest-ledger-period-contract).
Return the exact regular and adjustment rows as lookup evidence. Do not infer
frequency from a ledger label or opaque period-type code.

### Standard Fusion REST Ledger-Period Contract

For ledger-derived calendar scope, resolve the ledger and its periods through
this REST contract before requesting an export. Use the owning General Ledger
export route only when the contract is unavailable, incomplete, or ambiguous.

Use `core.fusion-api.rest-api-client/scripts/fusion_rest_client.py`, not the
BOSS client, for ledger-derived calendar evidence.

1. Query the supplied ledger name without changing case, punctuation, or
   whitespace:

   ```text
   GET /fscmRestApi/resources/11.13.18.05/ledgersLOV
     ?q=Name='{encoded Name}'
     &fields=LedgerId,Name,PeriodSetName,AccountedPeriodType
     &onlyData=true&totalResults=true&limit=500&offset={offset}
   ```

   Page until `hasMore` is `false`, then require exactly one exact `Name`
   match with nonblank `PeriodSetName` and `AccountedPeriodType`.

2. Query periods only for that resolved period set:

   ```text
   GET /fscmRestApi/resources/11.13.18.05/accountingPeriodsLOV
     ?q=PeriodSetNameId='{encoded PeriodSetName}'
     &fields=PeriodNameId,EnteredPeriodName,PeriodSetNameId,PeriodType,StartDate,EndDate,PeriodYear,PeriodNumber,AdjustmentPeriodFlag
     &onlyData=true&totalResults=true&limit=500&offset={offset}
   ```

   Page until `hasMore` is `false`. Retain rows whose `PeriodSetNameId` and
   `PeriodType` exactly match the resolved ledger values. Preserve both regular
   and adjustment rows as evidence; use only non-adjustment rows for
   ledger-equivalence comparisons.

3. When either REST endpoint is unavailable, returns an incomplete collection,
   or cannot resolve one exact ledger/period-set result, do not probe an
   unverified alternate endpoint. Route to a current, same-target export owned
   by the applicable General Ledger setup task. Do not substitute a Fixed
   Assets export for ledger period rows.

## Equivalent Fixed Assets Fiscal-Year Lookup

After `resolve_ledger_periods` succeeds, page
`assetFiscalYearDatesView` with `$limit=500` and `$offset` until `hasMore` is
false. Group the results by exact, case-sensitive `fiscalYearName` and retain
the associated `assetFiscalYear`, `startDate`, `endDate`, and
`midyearStartDate` values.

For each complete GL fiscal year, use only its regular (non-adjustment) ledger
periods. Its comparison range begins on the earliest regular `StartDate` and
ends on the latest regular `EndDate`; require the regular periods to be
continuous before treating the ledger-year range as usable evidence. An
existing Fixed Assets fiscal year is equivalent only when its complete date-row
set has the same fiscal-year start and end dates as that ledger-year range and
passes the existing exact-name/date-row validation contract. Do not treat a
similar name, matching period count, partial date range, or adjustment-period
date as an equivalent fiscal year.

Return one evidence row for every complete ledger fiscal year:

| Ledger fiscal year | GL regular-period range | Existing equivalent Fixed Assets fiscal year | Result |
| --- | --- | --- | --- |
| `<ledger PeriodYear>` | `<start> to <end>` | `<exact fiscalYearName>` or `None` | `equivalent` / `none` / `unresolved` |

When the user supplies a fiscal year, validate it as an exact existing fiscal
year that satisfies the calendar requirement; reuse that selection unchanged.
When no fiscal year is supplied, show each qualifying exact Fiscal Year Name
and its complete coverage, including a sole candidate, then require the
customer to select one or provide another exact Fiscal Year Name. Do not apply
a tie-break or select a fiscal year automatically. When no equivalent exists, route to
`FA_MANAGE_FISCAL_YEAR` to create or extend the fiscal year, then repeat this
availability lookup before preparing the asset calendar.

## Equivalent Fixed Assets Calendar Lookup

After the equivalent fiscal-year comparison, page both BOSS views used by
`resolve_existing_asset_calendar` until each returns `hasMore: false`. For each
existing calendar linked to an equivalent Fixed Assets fiscal year, compare its
complete period set to the corresponding ledger fiscal year's regular GL periods.

An existing Fixed Assets calendar is equivalent only when it has the same
exact linked fiscal-year name and every period has the same `PeriodName`,
`StartDate`, and `EndDate` as one regular GL period, with no extra, missing, or
adjustment-derived period. Do not accept matching dates with different period
names, a similar calendar name, or a partial period set.

Return one evidence row for every complete ledger fiscal year:

| Ledger fiscal year | Existing equivalent Fixed Assets fiscal year | Existing equivalent Fixed Assets calendar | Result |
| --- | --- | --- | --- |
| `<ledger PeriodYear>` | `<exact fiscalYearName>` or `None` | `<exact calendar name>` or `None` | `equivalent` / `none` / `unresolved` |

Show every exact equivalent result but do not silently select an asset calendar.
When more than one calendar is equivalent, mark the result ambiguous and
require the user to select the exact calendar name. When none exists, retain
the required user choice to create a new calendar.

### No-Match Retry and Multi-Ledger Gate

When the exact-name query returns zero rows, retry before treating the ledger
as unresolved: perform one fully paginated `ledgersLOV` read with the same
fields and filter the returned rows locally for the exact supplied `Name`.
This protects against a server-side query parsing or encoding issue; it does
not authorize selecting a partial or similar name.

For a multi-ledger request, complete this retry for every supplied ledger
before presenting a partial configuration proposal or requesting configuration
inputs for any ledger. If a ledger remains unresolved, report its exact-name
result and request only a corrected ledger name. Do not request fiscal-year
or asset-calendar names for the resolved tracks until every
ledger is either resolved or explicitly removed from scope.

## Ledger-Driven Response Structure

After the ledger-period, equivalent-fiscal-year, and equivalent-calendar lookup gates above pass, use the single
[Ledger-Derived Decision Prompt](ora_input_validation.md#ledger-derived-decision-prompt).
Pass the resolved ledger evidence to that template; do not render a second
evidence table or request names separately from this file.

## Bulk Lookup Matching

Page all required source results and create one exact lookup result per
supplied Ledger Name, Fiscal Year Name, and Calendar Name: exact match, no
match, multiple match, or lookup failure. Do not reuse partial matches, a
prior row's result, or failed lookup evidence for another calendar.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CAL.LOOKUP_EXISTING_REUSE | decision | 2 | reference_lookup | match->CAL.DONE_REUSE;absent_or_incomplete->CAL.HANDLE_LOOKUP | CAL.CLASSIFY_REQUEST | stop | An explicit reuse request names one Calendar |
| CAL.DISCOVER_FISCAL_YEARS | decision | 8 | reference_lookup | candidates_found->CAL.CONFIRM_FISCAL_YEAR;no_qualifying_candidate->CAL.HANDLE_INPUT;unresolved->CAL.HANDLE_LOOKUP | CAL.ROUTE_FISCAL_YEAR | stop | Fiscal Year Name is missing after the Input Preview |
| CAL.VALIDATE_FISCAL_YEAR | decision | 10 | reference_lookup | valid->CAL.VALIDATE_INPUT;start_year_unavailable->CAL.HANDLE_DEPENDENCY;invalid_or_unresolved->CAL.HANDLE_DEPENDENCY | CAL.ROUTE_FISCAL_YEAR | stop | Use resolve_fiscal_year_for_calendar and resolve_calendar_date_basis_from_fiscal_year to validate the supplied or customer-selected exact fiscal year and Start Fiscal Year. If the start row is unavailable, stop and request an exact available row or fiscal-year extension; never substitute a nearest year. |
| CAL.LOOKUP_EXISTING | decision | 30 | reference_lookup | absent->CAL.APPLY_DEFAULTS;match->CAL.DONE_EXISTS;different->CAL.DECIDE_UPDATE_OR_NEW;unresolved->CAL.HANDLE_LOOKUP | CAL.RESOLVE_DEPENDENCIES | stop | Dependencies are ready |
| CAL.DECIDE_UPDATE_OR_NEW | decision | 35 | evaluate_result | update_selected->CAL.APPLY_DEFAULTS;create_new_selected->CAL.NEW_INPUT_REQUIRED;unresolved->CAL.HANDLE_INPUT | CAL.LOOKUP_EXISTING | stop | Complete existing-state evidence differs from the proposal; evaluate the customer update-or-create-new choice. Update continues; create-new returns for exact new Calendar Name collection and fresh validation; an unanswered choice is missing input, not a lookup failure. |
