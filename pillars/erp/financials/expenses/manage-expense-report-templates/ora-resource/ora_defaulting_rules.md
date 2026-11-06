# Manage Expense Report Templates Defaulting Rules

## Workbook-First Defaults

Do not propose archetypes or seed input. Required blanks remain issues;
optional blanks for new records mean no value. Blanks for existing records preserve the target value.
Only the explicitly defined cash-only assumptions below are automatic.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| Supplied workbook or correction value | Retain the validated implementor value | Initial workbook or either correction mode | No | |
| Business Unit, name, start date | Leave unknown values blank; retain supplied values | Generating intake | No | |
| Target-resolved existing blank or omitted field | Preserve the fresh-baseline value | Partial update | No | |
| Field-behavior `Blank` | Treat as an unentered field-behavior value | Any intake mode | No | |
| Explicit Clear | Null, only if nullable and supported | Implementor clears an existing-record field | No | |
| Optional target-resolved new-record blank | No value, as disclosed in intake instructions | Completed create intake | No | |
| New template card mapping and receipt flags | N; related threshold/default type null | Cash-only create | No | |
| New type card receipt flag | N; threshold/program null | Cash-only create | No | |
| Selected card-enabled template/type | Outside cash-only scope; block without changing card configuration | Edit baseline conflicts with cash-only assumptions | No | |
| Policy | No assignment on Create; preserve existing association on Edit | Policy is outside captured scope | No | |
| Itemization display | Disabled, Enabled, Required | Intake presentation | No | |
| Legacy itemization labels | Not required becomes Disabled; Optional becomes Enabled | Reading older seed labels | No | |
| Account | Blank Create is unset; blank Edit preserves; supplied account number resolves the BU primary ledger and maps to Segment1 | Every v1.5 imported expense type | No guessed ledger or account | Destination BU/ledger REST evidence |
| Tax and Projects | Tax values null; Projects Disabled; project receipt No; default expenditure type null | Every v1.5 imported expense type | Yes, fixed scope default | Builder |
| Internal IDs, WHO and optimistic-lock data | Generated/resolved or preserved by authorized importer/Fusion | Save/verification | No | |
