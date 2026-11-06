# Manage Fiscal Years: Defaulting Rules

## Defaults

| Field | Internal | Resolved value | Applies When | User Override | Resolver |
|---|---|---|---|---|---|
| Start fiscal year | No | When the selected start basis is Oldest DPIS, including a user-defined request without a supplied start year, identify the fiscal-year cycle row whose inclusive range contains Oldest DPIS (`Start Date <= Oldest DPIS <= End Date`) and use it as the first fiscal year. For a ledger-derived request, retain the earliest complete ledger fiscal year unless the user explicitly requests Oldest-DPIS-based creation. | Oldest-DPIS-based setup, including user-defined creation without a supplied start year | Yes | resolve_oldest_in_service_date_from_system_controls |
| End fiscal year | No | Fiscal year that starts in the next calendar year | Initial setup without supplied end coverage | Yes |  |
| Description | No | Human-readable sentence-case form of Fiscal Year Name | User leaves it blank for a new definition | Yes | |
| Midyear Start | No | Blank | No approved group-asset half-year rule and export does not require it | Yes | resolve_fiscal_year_export_metadata |
| System-managed WHO columns (`CreatedBy`, `CreationDate`, `LastUpdatedBy`, `LastUpdateDate`, `LastUpdateLogin`) | Yes | Do not populate, derive, copy, or modify the fields. Preserve the export header and use its prescribed blank or system-managed representation. | Before package generation, for every parent, translation, and fiscal-year-date CSV row. | No | resolve_fiscal_year_export_metadata |
| CSV file names, columns, and metadata XML | Yes | Exact package structure from a current FSM export of this task. Never source field values, technical IDs, or supported business values from export data rows. | Before package generation | No | resolve_fiscal_year_export_metadata |
| Unknown technical value | Yes | No default | A required code, ID, column, or package member is unknown | No | resolve_fiscal_year_export_metadata |

For a blank Description on a new definition, replace separators with spaces,
split camel-case words, retain recognized uppercase acronyms such as `FY`, and
lowercase ordinary words after the first word. For example, `APRIL_FISCAL_YEAR`
becomes `April fiscal year`. Use the resolved description in the fiscal-year
type and every active-language translation. Preserve a user-supplied description.

## Fiscal-Year Interval Display

For a ledger-derived request that has two start-date candidates, show this
table before asking the user to select one:

| Fiscal-year interval | Derived from | Reason |
|---|---|---|
| `<start> to <end>` | `System Controls Oldest DPIS` | `Fiscal-year interval containing Oldest DPIS.` |


## Default Disclosure

After user inputs are collected and before ZIP preparation, list every applied
default and resolved value in the user-facing proposal. A user may override a
default only where the table permits it; validate the supplied replacement
before use.

## Fiscal-Year Design Preview

For every create-new request, render a Design Preview after the equivalent-year decision, exact-name check, defaults, and design rules pass, but before ZIP creation. Show the target, fiscal-year type name, supplied or defaulted human-readable sentence-case description, ledger or user-defined cycle basis, Oldest DPIS, coverage through the fiscal year beginning next calendar year, active translation languages, disclosed defaults, and generated annual rows. Do not create a ZIP, upload, or import until the Design Preview is accepted.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FY.APPLY_DEFAULTS | step | 60 | apply_default | applied->FY.ENFORCE_DESIGN;blocked->FY.HANDLE_DEPENDENCY | FY.VALIDATE_DPIS_CONTAINMENT | stop | User selected create-new and the exact selected name is confirmed absent. Reuse a current pre-decision name check only for the same unchanged name and target; otherwise complete the selected-name check after the decision before applying defaults. |


