# Manage Fiscal Years: Reference Lookups

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_oldest_in_service_date_from_system_controls | Before determining coverage | First reuse a recently resolved, traceable Oldest DPIS for the exact same target environment and enterprise. If none is available, primary: `GET /api/boss/data/objects/ora/erpCore/fixedAssetsSetup/v1/assetSystemControlsView` through `core.fusion-api.rest-api-client`; fallback when the BOSS endpoint is unavailable, nonexistent, incomplete, or returns an authorization or other error: a current same-target Manage System Controls export | Require one exact enterprise result and read `oldestDatePlacedInService`. Treat BOSS data as evidence and BOSS no data as absence; do not export after either result. | Oldest DPIS and its year | If BOSS returns an error, automatically reuse a current same-target export or start the prescribed Manage System Controls data export through `shared.setup-export.task-level-export`. Poll a known export process instead of starting a duplicate. This fallback does not authorize any configuration import. If BOSS returns no data, or the selected source has no clear Oldest DPIS, do not determine coverage. |
| resolve_fiscal_year_export_metadata | Before package preparation | Current target FSM export for `FA_MANAGE_FISCAL_YEAR` | Exact task and target only; inspect headers and metadata XML, not data rows. | CSV members, headers, column order, and metadata XML contract | Do not prepare a package. |

## Live Lookups

| Resolver | Runs When | Request | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_fiscal_year_dff_segments | After create-new defaults/annual-row generation, or when verifying supplied reuse criteria | One batch-current DFF definition export through core.fusion-api.apps-common.descriptive-flexfields, supplied per-row values, and exact target evidence for reuse | Execute Fiscal Year DFF Resolution in create or reuse-criteria mode | Per-row required-field maps, validated values, conversions, and evidence references | Missing required input, invalid values, ambiguous mappings, incomplete evidence, or unsupported checks blocks the applicable operation |
| resolve_existing_fiscal_year | Before create or update | BOSS `assetFiscalYearDatesView` through `core.fusion-api.rest-api-client` | One exact Fiscal Year Name; compare every requested date row. | Existing definition and differences | BOSS data is existing-state evidence; BOSS no data permits create; only a BOSS error requires the FSM export fallback. Multiple matches block. |
| resolve_ledger_periods | Ledger-derived setup | Standard Fusion REST `/fscmRestApi/resources/11.13.18.05/ledgersLOV` and `/fscmRestApi/resources/11.13.18.05/accountingPeriodsLOV`; when the target supports an equivalent BOSS resource, use it only after its resource contract is verified. | One exact ledger; retain only exact period-set and period-type matches. | Ledger, calendar, regular and adjustment period rows | When neither live route is available, use `resolve_ledger_periods_export_fallback`. |
| resolve_ledger_periods_export_fallback | Standard Fusion REST and the verified BOSS alternative are unavailable, incomplete, or unauthorized | A current same-target General Ledger setup-data export containing the requested ledger and its accounting-period rows, obtained through `shared.setup-export.task-level-export`. | One exact ledger, period set, and period type; complete regular and adjustment-period coverage. | Ledger, calendar, regular and adjustment period rows. | Missing, incomplete, ambiguous, cross-target, or stale export blocks. |
| resolve_active_translation_languages | Before creating translations | `GET /api/boss/data/objects/ora/commonAppsInfra/objects/v1/languages/$views/activeLanguage?$limit=500` through `core.fusion-api.rest-api-client` | Page completely and retain every active result. | Every active `languageCode`, `languageTag`, and language description. | Stop if the result is missing, incomplete, or empty. Do not ask the user to select languages. |

## Fiscal Year DFF Resolution

Obtain one completed same-environment
FA_MANAGE_FIXED_ASSETS_DESCRIPTIVE_FLEXFILEDS setup-data export per immutable
batch through core.fusion-api.apps-common.descriptive-flexfields.
Use Financials / Fixed Assets; resolve task sequence and eligibility through
the authoritative catalog and shared export workflow.
Retain ProcessId, ZIP reference, outcome, environment, and batch identity.

Reuse that definition export for every annual row in the unchanged batch.
Do not export per Fiscal Year Name or annual year. Export again for a new
batch or changed batch/environment. This lifecycle takes precedence over
the reusable existing-state Export Fallback Selection Protocol.

1. Confirm ApplicationId=140 and DescriptiveFlexfieldCode=FA_FISCAL_YEAR
   from current metadata, including its mapping to annual date rows.
   Attribute columns alone do not establish another DFF identity. Require
   explicit metadata-to-object mapping for any supplied or contract-required
   header attributes; report an unresolved mapping instead of guessing.
2. Read enabled global definitions from
   ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_GLOBAL_SEGMENT.csv, scoped to that
   exact application and DFF. Retain optional enabled segments too.
3. Resolve supplied contexts from
   ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv in the same export.
   Require one exact enabled ContextCode, otherwise one exact enabled Name.
4. Read enabled context-sensitive definitions from
   ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv for that exact application,
   DFF, and context. Blank context never waives global requirements.
5. In create mode, require nonblank values for every applicable RequiredFlag=Y
   segment, including hidden segments, on every proposed annual row.
   Map supplied values by unique current ColumnName, SegmentCode, or Prompt.
   Reject unknown, disabled, out-of-context, ambiguous, or conflicting input.
   Do not silently propagate one annual row's values to other years.
6. Delegate only read-only value-set verification through Manage Fixed Assets
   Flexfield Value Sets. Never create, enable, or modify sets or values.
   With no ValueSetCode, validate the supported column contract.
   Format Only requires applicable type/format/length/precision/scale/range
   checks, not enumerated membership. Independent requires exact eligible
   membership; Dependent also requires the exact eligible parent/value pair.
   Table membership is unsupported by the current delegated workflow:
   report it as unverified and stop. Unsupported types, incomplete coverage,
   unresolved visibility, and invalid values remain blockers.
7. Retain supplied values and documented canonical conversions separately.
   Show conversions in previews. Resolve actual import headers from the
   current task contract, never from assumed database column names.

In reuse-criteria mode, validate and compare only supplied DFF criteria
against complete exact-name/exact-year target evidence. Do not demand create
inputs, alter existing values, or turn a mismatch into an update.

The DFF definition export is metadata evidence, distinct from the Fiscal
Years template/spec package and existing-state exports. Its definition rows
may establish requirements but never supply proposed fiscal-year values.
A failed or incomplete export cannot prove that no segments are required.

## Export Fallback Selection Protocol

When a resolver permits an FSM export fallback, apply this sequence before
requesting a user decision, reporting a missing dependency, or creating a new
export process:

1. Search the active project workspace and other available project workspaces
   for completed exports of the exact setup task and target environment.
2. Order candidates by completion time, newest first. Validate the target from
   the artifact metadata or process record, the exact task code, successful
   completion, ZIP integrity, and the required CSV member and business field.
3. Use the newest candidate that provides one complete, unambiguous result.
   Compare the required business field with other recent same-target candidates
   when they are available; a disagreement is ambiguous and blocks the flow.
4. If a matching export process is already identified but unfinished, poll that
   process. Do not start a duplicate export.
5. Start a new same-target data export only when no valid completed artifact or
   identified process is available. For the System Controls fallback, invoke
   `shared/setup-export/task-level-export/scripts/export_setup_task_csv.py`
   with `--task-code FA_MANAGE_SYSTEM_CONTROL --data` and the selected project
   and target OAuth properties. Do not use its default template-only mode.
   The export is a read-only prerequisite and does not authorize a
   configuration import.

For the System Controls resolver, inspect `FA_SYSTEM_CONTROL.csv` in the
downloaded data ZIP and require exactly one applicable data row with a
nonblank `DatePlacedInService`. A successful export process or a header-only
CSV is not evidence of a configured Oldest DPIS; record the zero-row or
missing-field result and stop coverage defaulting. Do not rerun an identical
export to try to manufacture data. Extract only `DatePlacedInService`; do not
expose or use other System Controls fields for fiscal-year defaulting.

## Equivalent Fixed Assets Fiscal Year Lookup

For a ledger-derived request, after `resolve_ledger_periods`, page `assetFiscalYearDatesView` completely and group its rows by exact `fiscalYearName`. For each candidate fiscal year, compare its minimum `startDate`, maximum `endDate`, and ordered regular date coverage with one complete regular-year group from the resolved ledger. Exclude ledger adjustment periods from the comparison. For a user-defined request, always compare each candidate with the supplied fiscal-year cycle and resolved start coverage, even when a Fiscal Year Name was supplied. List each exact equivalent match with Fiscal Year Name, coverage, and regular-period count/frequency.

A zero-match result is valid availability evidence, not a lookup failure. Report the exact equivalent-match results, including no match, without selecting or creating a fiscal year automatically.

This lookup is mandatory for every user-defined fiscal-year/ledger-derived cycle and is not
an optimization that may be skipped when a name was supplied. Complete the
System Controls start-year default first when needed. When the requester
supplied a Fiscal Year Name, complete its exact-name existing-state check
before showing the equivalent list and requesting the reuse-or-create-new
decision. When no name was supplied, mark that exact-name check not
applicable. If the create-new decision supplies a name that was not checked or changes the candidate name, run resolve_existing_fiscal_year for that exact selected name after the decision and before defaults or preview. Require confirmed absence for create-new; an existing or ambiguous selected name blocks creation. Do not create a preview or begin package work before the decision.
## BOSS Verification and Expected Outcomes

Use `assetFiscalYearDatesView` as the authoritative pre-submission check.
Require an exact Fiscal Year Name and compare every requested date row. If the
fiscal year is absent, creation may proceed after the other checks pass; if only some rows match, include only missing rows; if a row differs, show the difference and obtain an update decision. Treat a BOSS data response as existing-state evidence and a BOSS no-data response as absence evidence. Only when BOSS returns an error, including an unavailable, incomplete, or authorization-error response after its permitted authentication retry, require a current same-target `FA_MANAGE_FISCAL_YEAR` FSM export as the existing-state fallback before package preparation. A fallback export may confirm existing state only; never copy its data-row values into proposed package fields or defaults. Do not treat it as evidence when it is incomplete or ambiguous.

| Result | Required handling |
|---|---|
| Equal fiscal year exists | Report it as existing; do not create a duplicate. |
| Existing fiscal year differs | Show the differences and require an update-or-new decision. |
| BOSS returns an error, including unavailable, incomplete, or authorization-error response | Require a current same-target `FA_MANAGE_FISCAL_YEAR` FSM export and apply the same exact-name and full-date-row comparison. Stop only when that fallback is unavailable, incomplete, or ambiguous. Do not request additional BOSS access solely for this preflight when the export is sufficient. |

### Verified BOSS Request Contract

Use the BOSS client through `core.fusion-api.rest-api-client` with this
read-only resource:

```text
GET /api/boss/data/objects/ora/erpCore/fixedAssetsSetup/v1/assetFiscalYearDatesView
```

Request `$limit=500`. When `hasMore` is `false`, treat that response as the
complete fiscal-year result. Only when `hasMore` is `true`, page with `$offset`
until `hasMore` is `false`.
For each item, use `fiscalYearName`, `assetFiscalYear`, `startDate`,
`endDate`, and `midyearStartDate`. Check an exact, case-sensitive
`fiscalYearName` match for existing-state validation. Do not use this endpoint to derive the End fiscal year default; calculate that default from the next calendar year instead.
Do not treat a response with `hasMore=true`, a partial page set, or a similarly
named fiscal year as evidence.

## Ledger Period Lookup Rules

1. Use the standard Fusion REST client to query
   `/fscmRestApi/resources/11.13.18.05/ledgersLOV` with
   `q=Name='<exact ledger name>'` and `limit=500`. Request `LedgerId`,
   `Name`, `PeriodSetName`, and `AccountedPeriodType`, and page with
   `offset` until `hasMore` is false. Do not use the BOSS client or a direct
   `Name` request parameter; those routes are not supported by every target.
2. Use the standard Fusion REST client to query
   `/fscmRestApi/resources/11.13.18.05/accountingPeriodsLOV` with
   `q=PeriodSetNameId='<resolved PeriodSetName>'` and `limit=500`. Request
   `EnteredPeriodName`, `PeriodSetNameId`, `PeriodType`, `StartDate`,
   `EndDate`, `PeriodYear`, `PeriodNumber`, and `AdjustmentPeriodFlag`, and
   page with `offset` until `hasMore` is false.
3. If either standard REST resource is unavailable, incomplete, or unauthorized,
   try an equivalent BOSS resource only when its exact resource path, fields,
   and pagination contract have been verified for the target. Do not substitute
   a similarly named BOSS resource.
4. If neither live route resolves complete evidence, reuse or start a current
   same-target General Ledger setup-data export through
   `shared.setup-export.task-level-export`. The export must contain the exact
   ledger, `PeriodSetNameId`, `PeriodType`, and every requested accounting-period
   row. Validate the export's target environment and completion status before
   use; retain regular and adjustment periods separately. Never copy export rows
   into a Fixed Assets import package or mix them with evidence from another
   target environment.
3. Separate regular from adjustment rows. For each regular-year group, derive
   its minimum start date, maximum end date, and regular-period count. Keep
   adjustment rows separate; they never extend the regular fiscal year.
4. Use the earliest complete regular-year group as the ledger-derived first year. Record an initial partial group as partial rather than complete.

### Bulk Ledger and Period Collection

For a request with multiple ledgers, collect requested `ledgersLOV` rows through one fully paginated read or the smallest supported set of paginated reads. Build a working table of exact requested ledger name, ledger ID, period-set name, and accounted-period type. If neither live route is available, use one validated same-target export fallback per distinct ledger and period-set group.

Group the working rows by exact period-set name and accounted-period type. Query `accountingPeriodsLOV` once per distinct group, page every result set completely, and map that group's period rows back to every ledger in the group. Derive and validate the fiscal-year pattern separately for each ledger; shared retrieval never permits one ledger's period result to be used for a different period-set/type group.


### No-Match Retry and Multi-Ledger Gate

When the exact-name query returns zero rows, retry before treating the ledger
as unresolved: perform one fully paginated `ledgersLOV` read with the same
fields and filter the returned rows locally for the exact supplied `Name`.
This protects against a server-side query parsing or encoding issue; it does
not authorize selecting a partial or similar name.

For a multi-ledger request, complete this retry for every supplied ledger
before presenting a partial configuration proposal or requesting configuration
inputs for any ledger. If a ledger remains unresolved, report its exact-name
result and request only a corrected ledger name. Do not request start basis,
fiscal-year names for the resolved tracks until every
ledger is either resolved or explicitly removed from scope.

## Ledger-Driven Response Structure

When all supplied ledger names are resolved, present the live ledger evidence
before requesting a start basis or fiscal-year name. Use
the following response structure exactly. Do not merge the table headings,
omit their separator row, or place the recommendation before the table.

Start with this sentence:

```text
I verified the live ledger setup.
```

If the supplied name differs from the exact target display name, append one
short parenthetical correction to that sentence; otherwise, do not add one.

Then render one row per resolved ledger in this exact Markdown table:

| Ledger | GL calendar | Fiscal-year pattern | GL periods | Fixed Assets treatment |
|---|---|---|---|---|
| `<exact ledger display name>` | `<configured calendar display name>` | `<regular fiscal-year start>â€“<regular fiscal-year end>; first complete fiscal year <start>â€“<end>` | `<regular-period count> <frequency> periods + <adjustment-period count> adjustment period(s)` | `Create <regular-period count> Fixed Assets depreciation/prorate periods aligned to the regular GL periods; exclude the GL adjustment period.` |

After the ledger evidence table, continue with the equivalent-fiscal-year lookup result.
## Bulk Lookup Matching

Page all required source results and create one exact lookup result per
supplied ledger and Fiscal Year Name: exact match, no match, multiple match, or
lookup failure. Do not use partial matches, a prior row's result, or failed
lookup evidence for another row.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FY.LOOKUP_EXISTING | decision | 30 | reference_lookup | checked_or_not_applicable->FY.LOOKUP_EQUIVALENT;unresolved->FY.HANDLE_LOOKUP | FY.RESOLVE_DEPENDENCIES | stop | When a Fiscal Year Name was supplied, check its exact existing state after cycle and coverage resolution; otherwise record not applicable. |
| FY.LOOKUP_EQUIVALENT | decision | 35 | reference_lookup | resolved->FY.DECIDE_EQUIVALENT;blocked->FY.HANDLE_LOOKUP | FY.LOOKUP_EXISTING | stop | Identify equivalent existing Fixed Assets fiscal years after exact-name status is available and before the reuse-or-create decision, preview, or package preparation. |
| FY.VERIFY_REUSE_DFF | decision | 50 | reference_lookup | no_criteria->FY.DONE_EXISTS;match->FY.DONE_EXISTS;unresolved->FY.HANDLE_LOOKUP | FY.DECIDE_EQUIVALENT | stop | User selected an exact verified fiscal year for reuse. Without supplied DFF criteria, return no_criteria without a DFF export. Otherwise execute resolve_fiscal_year_dff_segments in reuse-criteria mode and require an exact match. |
| FY.RESOLVE_DFF | decision | 65 | reference_lookup | resolved->FY.ENFORCE_DESIGN;missing_or_invalid_input->FY.HANDLE_INPUT;unverified->FY.HANDLE_LOOKUP | FY.APPLY_DEFAULTS | stop | Create-new decision, selected-name checks, and annual-row generation are complete. Execute resolve_fiscal_year_dff_segments in create mode for every proposed annual row before Design Preview or package preparation. |
