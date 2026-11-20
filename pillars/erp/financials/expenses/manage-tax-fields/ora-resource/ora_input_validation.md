# Manage Tax Fields input validation

Evidence: FSM-EXPORT, SRC-CS-EO, SRC-CS-TAX-SETUP-VO, SRC-CS-UI-AM. See ../references/evidence.md.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Target and business intent | Environment, operation, BuName, requested field behaviors | Return issues | Request the missing scope; no global fallback | create or update | |
| Tax rule identity | BuName and TerritoryCode | Return issues | Country/territory or explicit OTHER | tax rule change | resolve_tax_territory |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Field behavior codes | Accept DISABLED, ENABLED, REQUIRED; reject other supplied codes | six Enable*Code attributes | resolve_tax_behaviors |
| EnabledFlag | Accept Y or N when supplied; no inferred default | flag supplied | |
| Tax switch | OptionCode must be ENABLE_TAX and ValueCode Y or N | setup option change | |
| EBS source binding | Recompute parent profile intake from unchanged CSV and source/environment-bound decisions; reject unresolved or conflicting records and unsupported mappings | EBS profile input | |
| Duplicate identities | Reject conflicting changes for the same BU/territory or BU/option | multiple requested rows | |
| Package shape | Preserve exact headers and metadata from same-task template | FSM preparation | |
| Business-field serialization | On create require every task business field explicitly; on update preserve unspecified business values from the fresh baseline. Do not support blank-as-clear or omission-as-default | create or update | |
| Audit serialization | Preserve audit headers and serialize empty cells for CreationDate, CreatedBy, LastUpdateDate, LastUpdatedBy and LastUpdateLogin using the builder adapter convention; never accept user audit values (BUILDER-AUDIT-CONTRACT) | candidate preparation | |
| Setup-option aliases | The normal route permits named-BU create-Y or the maintained combined N-to-Y update matching their respective operation and schema profiles in references/qualified-option-alias-profile.json through scripts/tax_option_aliases.py, without a separate qualification-choice prompt. New Y switches with new same-BU rules use the documented staged-create route: switch-only first, full readback, then rule-only. Other switch operations require explicit nonproduction qualification. Switch stages populate identical minimal requested rows in EXM_SETUP_OPTION.csv and EXM_CASH_ADV_SETUP_AND_POLICY.csv. Reject divergent, duplicate or unrelated rows; reconcile both complete baseline aliases first. Report and omit an already-satisfied Update; tax-rule-only changes leave both aliases header-only. Preserve every package member, exact header and metadata byte; follow references/option-alias-qualification.md | create or update | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| TAX.INPUT | step | 1 | validate_input | success->TAX.LOOKUPS;failure->TAX.ISSUES | none | stop | create or update |
