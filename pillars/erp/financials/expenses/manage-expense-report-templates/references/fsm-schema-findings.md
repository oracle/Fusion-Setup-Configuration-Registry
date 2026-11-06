# FSM schema findings

A schema-only export on 2026-09-24 returned release 11.13.26.10.0 and eleven
CSV members plus ASM_SETUP_CSV_METADATA.xml. This is authoring evidence, not
a reusable live baseline. Run `inspect_fsm_schema.py` on each fresh target
export before packaging. Preserve all unrelated CSV members, including card
and policy members, byte-for-byte. Their presence does not authorize edits.

Both child CSVs have these parent-reference columns:

```
EXM_EXPENSE_TEMPLATE.BuName
EXM_EXPENSE_TEMPLATE.Name
EXM_EXPENSE_TYPE.BuName
EXM_EXPENSE_TYPE.TemplateName
EXM_EXPENSE_TYPE.Name
```

`EXM_EXPENSE_TYPE_ITEMIZATION.csv` additionally contains BuName,
ExpTemplateName, Name and audit columns. Its XML node is
`/ExpenseTemplateVO/ExpenseTemplateVORow/ExpenseType/ExpenseTypeVORow/ExpenseTypeItemize/ExpenseTypeItemizeVORow`.
It has **no Include flag or mapping EndDate**. Include Yes describes an intended
relationship, not a literal CSV flag. Include No/removal and mapping end-dating
must remain blocked until supported import semantics are verified. Do not
silently ignore an entered end date or treat omission as deletion.

`EXM_PROJECT_EXP_TYPE_MAP.csv` additionally contains ClassificationCode,
ProjectUnitName, ExpenditureTypeName, EffectiveStartDate, EffectiveEndDate,
SysEffectiveDate, Name, ExpTemplateName, BuName and audit columns. Its XML node
is `/ExpenseTemplateVO/ExpenseTemplateVORow/ExpenseType/ExpenseTypeVORow/ProjectExpTypeMap/ProjectExpTypeMapVORow`.
Headers establish structure, not valid ClassificationCode values, date defaults,
or deletion semantics. The current adapter uses the complete expense-type,
Project Unit and expenditure-type relationship key and obtains the four technical
attributes from matching reference rows in the fresh export. Mapping Edit retains
the existing relationship; changing an identity requires a separate Create.

The expense-type CSV exposes ItemizationOnlyFlag, so the builder can handle
Itemization Only Type Yes/No. It also exposes Segment1. The current workbook
accepts Expense Type Account as account_number and derives LedgerName from the
BU primary ledger; omitted edit accounts preserve existing values.
The import VO and EO expose Segment1 and the import hook resolves LedgerName
to ChartOfAccountsId (see destination-reference-contract.md).
It also writes TaxClassificationCode and
TaxProductCategoryCode as blank/null because the current workbook does not
collect either tax value.

The template CSV has no default-template field. EXM_ORG_SETTING.csv includes
SettingCode, SettingValue and SettingValueDecoded, but their presence alone
does not establish how to change the default template. That operation remains
blocked. Virtual-card association is absent from the observed type CSV;
policy is represented by separate protected members. These remain outside
the cash-only intake and mutation scope.

The current builder supports child relationship additions and existing-row
preservation. See `child-mappings.md` for the exact supported contract and
project reference requirements. Removal and itemization end-dating remain
unsupported. Do not ask the implementor for technical keys or substitute an
undeclared UI/REST path when reference evidence is unavailable.
