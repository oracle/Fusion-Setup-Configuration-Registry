# Manage Fiscal Years: Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | Required Action |
|---:|---|---|
| 1 | Ledger and Fixed Assets start evidence | Resolve the earliest complete ledger fiscal year when a ledger is supplied, and obtain one clear Oldest DPIS value before applying the Start fiscal year defaulting rule. Retrieve System Controls once per target environment and reuse its Oldest DPIS value for all ledgers and subsequent requests; do not fetch it separately for each ledger. |
| 2 | Equivalent Fixed Assets fiscal year | After deriving ledger periods or validating the user-defined fiscal-year cycle and resolving the optional start year from System Controls, check a supplied candidate Fiscal Year Name read-only first (or mark it not applicable when omitted), then find matching existing Fixed Assets fiscal years and obtain the user reuse-or-create decision. The candidate check never replaces that decision. This gate is mandatory before preview or package preparation; a newly supplied or changed create-new name must pass exact-name checking after the decision. |
| 3 | Selected fiscal-year action | Reuse the exact user-selected equivalent fiscal year, or create the user-named new fiscal year, only after all technical values are known. |

## Required Checks

| Check | Required? | When | Source | Why | What to do if it is missing |
|---|---|---|---|---|---|
| `FA_SYSTEM_CONTROLS` | Yes | Every ledger-derived setup and every direct-input setup with a missing start | `resolve_oldest_in_service_date_from_system_controls` | Provide one clear Oldest DPIS value for the ordered start-evidence rule. | Resolve once per target environment and reuse the value for all ledgers and subsequent requests; do not fetch separately per ledger. When the BOSS lookup fails, first search and validate completed same-target Manage System Controls exports, newest first, then poll an identified matching process. Start a new export only if neither provides complete, unambiguous evidence. Stop only if the completed fallback cannot provide one clear Oldest DPIS value. |
| `GL_LEDGER_PERIODS` | Yes | Every ledger-derived setup | `resolve_ledger_periods` | Provide exact ledger fiscal-year coverage and regular-period pattern. | Try standard Fusion REST, then a verified BOSS equivalent. If neither live route is available, reuse or start a current same-target General Ledger setup-data export and validate its exact ledger, period set, period type, and complete period rows. Stop only if that export is missing, incomplete, ambiguous, cross-target, or stale. |
| `FA_FISCAL_YEAR_EXPORT` | Yes | Before building a package | One template/spec FSM export of this task from the target environment | The export supplies the package contract only: members, headers, column order, and metadata XML. | Obtain one template/spec export for exact headers and metadata. Do not inspect, learn, copy, or reuse data-row values or formatting from it; do not request a second populated export for this purpose. |
| `FA_FISCAL_YEAR_EXISTENCE` | Yes | Before create or update | `resolve_existing_fiscal_year` | Prevent duplicates and make updates safe. | Stop if existing-state evidence is unavailable, incomplete, or unclear. |
| `ACTIVE_TRANSLATION_LANGUAGES` | Yes | Before building a package for a create-new fiscal year | `resolve_active_translation_languages` | Generate complete translation coverage. | Page the active-language result completely and create one row per active language. Stop only if the result is missing, incomplete, or empty; do not ask the user to choose languages. |

## Result Types

| Result | Meaning | What you may do |
|---|---|---|
| Ready | All checks and technical defaults have proof | Run lookups only. A package still needs a preview and approval. |
| Business decision needed | A fiscal year exists but differs from the request | Do not create or update until the user chooses what to do. |
| Technical lookup missing | System Controls BOSS result, its error-only export fallback, fiscal-year export, or existing-state information is missing | Run lookups only. Do not build or submit a package. |

## Ledger-Derived Customer Decision Gate

For a ledger-derived request, do not request setup names or prepare a package
until the following decision gate is complete. It is a prerequisite because the
selected basis determines the fiscal-year coverage and the dependent calendar
coverage.

| Ledger | GL calendar | Fiscal-year pattern | GL periods | Fixed Assets treatment |
|---|---|---|---|---|
| `<exact ledger name>` | `<configured GL calendar>` | `<start> to <end>; first ledger fiscal year <start> to <end>` | `<regular count> regular periods + <adjustment count> adjustment period(s)` | `Create <regular count> Fixed Assets periods aligned to regular GL periods; exclude GL adjustment periods.` |

## Multi-Ledger Setup and Review Prerequisites

Treat every ledger as an independent track. A different existing-state result
for one ledger is a business decision for that track and does not block package
preparation for the other ready tracks.

Before building a combined fiscal-year ZIP, require all included tracks to
have the same target environment and current Manage Fiscal Years export
contract. A fiscal-year ZIP must not include asset-calendar objects.

Before requesting submission approval, show the exact ZIP review for every
fiscal year in scope:

### Create Fiscal Year — `<fiscal-year name>`

| Field | Value |
|---|---|
| *Name | `<fiscal-year name>` |
| *Description | `<resolved description>` |

| Fiscal Year | Start Date | End Date | Midyear Start Date |
|---|---|---|---|
| `<year>` | `<start>` | `<end>` | `<value or —>` |

Show the first 10 date rows and total row count when the table is longer.
State the ledger mapped to the fiscal year and the archive totals for parent,
translation, and fiscal-year-date rows. The ZIP is not ready until the review
matches the immutable archive and the separate creation and submission
approvals required by `core.data-loader` are present.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FY.RESOLVE_DEPENDENCIES | decision | 20 | resolve_dependency | ready->FY.LOOKUP_EXISTING;blocked->FY.HANDLE_DEPENDENCY | FY.VALIDATE_INPUT | stop | Valid input; resolve ledger evidence or validate the user-defined cycle, and obtain Oldest DPIS before applying defaults. |
