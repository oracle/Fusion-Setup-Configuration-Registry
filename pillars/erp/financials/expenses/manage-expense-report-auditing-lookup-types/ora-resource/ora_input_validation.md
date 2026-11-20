# Auditing lookup workbook validation

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Type text identity | Lookup Type on optional Lookup Types sheet | Stop | Supply an existing type, never a new definition | Every populated type row | |
| Code identity | Lookup Type; Lookup Code; Reference Data Set Code | Stop with row/cell issue | Correct workbook or chat, then revalidate | Every populated row | |
| Code meaning | Meaning | Stop | Supply a meaning, at most 80 model characters | Target identity is new | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Workbook schema | Lookup Codes and optional Lookup Types sheets; row 8 headers/row 9 onward data, or legacy row 4/5; optional Reference Lists is guidance only. Formulas, unknown/duplicate/missing columns, macros, external relationships and other sheets block | Workbook intake | |
| Text and lengths | Preserve leading zeros; type/code at most 30, meaning 80, description 240, tag 150. Database byte semantics remain application validation | Supplied fields | |
| Dates and integers | Real ISO date or native Excel date; no time; integer sequence up to 18 digits; resulting start must not follow end | Populated fields and retained target values | |
| Duplicate identity | Reject repeated type/code/set tuples; resolve ambiguous view context before normalization | Multiple rows | |
| FSM required system value | Reject blank or non-single-character ChangeSinceLastRefresh in every populated candidate CSV member; preserve existing exported values. Header-only members are allowed | Candidate packaging and native ZIP validation | |
| Corrections | Keep source issues until a corrected workbook is reparsed; never silently drop a column or formula | Chat corrections | |

Sources: references/evidence.md, EO-CODE and UI. Offline implementation: scripts/intake_workbook.py.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AUDLK_INPUT | step | 1 | validate_input | success->AUDLK_DEP | none | stop | Always |
