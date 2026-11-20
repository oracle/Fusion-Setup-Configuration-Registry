# Manage Fiscal Years: Design Enforcement

## Design Principles

Review every provided fiscal-year field against the applicable task export,
table constraints, and documented Fixed Assets guidance. Treat invalid values
as blockers; present valid but suboptimal choices as recommendations and retain
the user's explicit choice.

- Align the Fixed Assets fiscal-year pattern and regular periods with the
  associated GL calendar when asset reporting and close periods must align.
  A different asset calendar requires approved business rationale and a
  documented reconciliation approach.
- Record the fiscal-year pattern, regular-period pattern, and readable period
  suffix. For uneven calendars, such as 4-4-5 or 13-period calendars, validate
  the date coverage and period sequence.

## Coverage and Update Controls

| When | Stop when | What to do |
|---|---|---|
| Update of a used fiscal year | The impact is unknown or target-environment approval is missing | Complete the impact check and obtain explicit approval. |
| First fiscal-year date row for an Oldest-DPIS-based creation | Its inclusive date range does not contain Oldest DPIS (`Start Date <= Oldest DPIS <= End Date`) | Reject it. This is mandatory validation after the reuse-or-create decision and before design preview; compare actual dates, not the fiscal-year label. |
| Fiscal-year coverage | The design does not include the fiscal year that starts in the next calendar year | Extend the planned fiscal years before related calendar work. |

## DFF Preview and Artifact Enforcement

Show applicable DFF business prompts and reviewed values with each annual
row. Include documented canonical conversions in the proposal.

Before execution approval, inspect every annual row in the immutable ZIP
against its required-field map, approved context/values, and current import
headers. Reject missing required values, cross-year copying, unsupported
header mappings, or serialization mismatches. Keep translations separate.

Retain all existing cycle, coverage, Oldest DPIS, translation, package-creation,
and execution-approval checks.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FY.ENFORCE_DESIGN | decision | 70 | design_enforcement | pass->FY.IMPORT_GATE;blocked->FY.HANDLE_DESIGN | FY.RESOLVE_DFF | stop | Defaults and lookup results are available; validate the design and render the required Design Preview. |
