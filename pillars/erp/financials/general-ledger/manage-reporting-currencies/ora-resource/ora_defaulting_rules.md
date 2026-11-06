# Manage Reporting Currencies Defaulting Rules

Defaults are conditional population rules, not substitutes for required user confirmation. Existing exported rows are preserved exactly. New rows use current same-release, same-task, same-role evidence; a baseline value is shown to the user before packaging whenever it represents business behavior. FirstLedgerPeriodName is a deterministic source-derived value for Journal or Subledger, not a guessed default or mandatory user input.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| Description | Blank | Journal or Subledger and the optional description is omitted | No |  |
| TargetLedgerCategoryCode | ALC | New relationship | Yes, reject any conflicting input |  |
| RelationshipTypeCode | BALANCE, JOURNAL, or SUBLEDGER from ConversionLevel | New relationship | Yes, derive from the validated level |  |
| Relationship ledger aliases and parent keys | Derive from the level-specific Relationship Row Population Contract in ora_input_validation.md | Every new relationship and its rule rows | Yes; no blank Name2 or substitution of the primary for a secondary source | derive_minimum_target_graph |
| ApplicationShortName | GL | New relationship and same-release template agrees | Yes, reject any other baseline value | inspect_scoped_reporting_currency_export |
| OrgIdTrans | -99 | New relationship and same-release template agrees | Yes, reject any other baseline value | inspect_scoped_reporting_currency_export |
| RelationshipEnabledFlag | Y | New baseline relationship | No; disclose and require confirmation |  |
| InheritCreationUserFlag | Y | New baseline relationship | No; disclose and require confirmation |  |
| AutomaticPostFlag | Y | New baseline relationship | No; disclose and require confirmation |  |
| StatusCode | CONFIRMED under the current scoped minimal-import contract | New baseline relationship and current same-role evidence agrees | Yes, reject fabricated lifecycle status and block on conflicting current evidence | inspect_scoped_reporting_currency_export |
| AlcInheritConversionType | N | Current supported non-EMU baseline; for Journal or Subledger this maps the Retain Transaction Rate Type default to No | No; disclose the default and require explicit supported intent and same-role evidence to change it | inspect_scoped_reporting_currency_export |
| AlcNoRateActionCode | REPORT_ERROR | Optional Missing Conversion Rate policy is omitted | No; disclose the current UI and service default | inspect_scoped_reporting_currency_export |
| AlcMaxDaysRollRate | Blank | AlcNoRateActionCode is REPORT_ERROR | Yes, require blank |  |
| AlcMaxDaysRollRate | No default | AlcNoRateActionCode is FIND_RATE | No; require explicit integer 1 through 999 |  |
| RevExpXlationRuleCode | PTD | Current Journal or Subledger new-row baseline | Yes, use the service-derived value; Balance remains explicit user intake | inspect_scoped_reporting_currency_export |
| OwnerEquityXlationRuleCode | PTD | Current Journal or Subledger new-row baseline | Yes, use the service-derived value; Balance remains explicit user intake | inspect_scoped_reporting_currency_export |
| AlcPeriodAverageRateTypeTrans | No default | Balance | No; require exact user-confirmed rate type | resolve_conversion_rate_type |
| AlcPeriodEndRateTypeTrans | No default | Balance | No; require exact user-confirmed rate type | resolve_conversion_rate_type |
| AlcDefaultConvRateTypeTrans | No default | Journal or Subledger | No; require exact user-confirmed rate type | resolve_conversion_rate_type |
| FirstLedgerPeriodName | Exact FirstLedgerPeriodName from the scoped source physical row after one exact non-adjustment accountingPeriodsLOV PeriodNameId match in the exported PeriodSetName and AccountedPeriodType scope | Journal or Subledger | No for the supported baseline; a different user value requires authoritative same-release eligibility evidence and revalidation, never LOV membership alone | resolve_first_opened_period |
| AlcInitConvOptionCode | Blank | Initialization is not requested | Yes, keep the whole initialization group blank |  |
| AlcInitConvOptionCode | I | Non-EMU Journal or Subledger initialization is explicitly requested | Yes, reject partial or conflicting values | resolve_balance_initialization_period |
| AlcInitPeriod | Exact eligible Balance Initialization Period | Initialization is requested | No; require user period intent and validation | resolve_balance_initialization_period |
| AlcInitDate | Start date of AlcInitPeriod | Initialization is requested | Yes, derive from exact resolved period | resolve_balance_initialization_period |
| AlcInitializingRateDate | Prior-period end or day before AlcInitDate | Initialization is requested and the user supplies no earlier valid override | No; allow an explicitly validated earlier date | resolve_balance_initialization_period |
| AlcInitializingRateTypeTrans | No default | Initialization is requested | No; require exact user-confirmed enabled rate type | resolve_conversion_rate_type |
| Journal rule | JeSourceKey Other, JeCategoryKey Other, JeSourceName Other, JeCategoryName Other, UserUpdatableFlag Y, IncludeFlag Y | Current Balance, Journal, or Subledger baseline after explicit broad-rule confirmation | No; selective rules require explicit intent and exact resolver evidence | resolve_journal_category |
| Closing Journal display line | Do not emit | Always unless a same-release scoped export proves the requested row | Yes, remove any row inferred only from UI display state |  |
| Physical Name and Name1 | ReportingCurrencyName | Journal or Subledger physical target | Yes, exact target business key |  |
| Physical LedgerCategoryCode | ALC | Journal or Subledger physical target | Yes, reject any other value |  |
| Physical AlcLedgerTypeCode | TARGET | Journal or Subledger physical target | Yes, reject any other value |  |
| Physical CurrencyCode | Validated CurrencyCode | Journal or Subledger physical target | Yes, exact resolved code | resolve_monetary_currency |
| Physical RoundingCcidSegments | Exact source value | Journal or Subledger and no optional override is supplied | No; validate any override through the source COA | resolve_rounding_account |
| Physical RevalFromPriLgrCurr | N | Current Journal or Subledger Revaluation Basis default is Entered currency | No; a Primary ledger currency override requires explicit supported intent | inspect_scoped_reporting_currency_export |
| Physical EnableJeApprovalFlag | N | Current Journal or Subledger default is unchecked | No; an enabled value requires explicit user opt-in | inspect_scoped_reporting_currency_export |
| Physical CreateJeFlag | Y | Current Journal or Subledger target baseline | Yes, require exact same-role evidence | inspect_scoped_reporting_currency_export |
| Physical SlaSequencingFlag and sequencing fields | Preserve current no-sequencing source or template values | Current baseline | Yes, custom sequencing is out-of-baseline | read_source_physical_template |
| Physical AlcTrans | Alc | Journal or Subledger physical target | Yes, exact current target marker | inspect_scoped_reporting_currency_export |
| Physical DataConversionLevelTrans | Blank | Journal or Subledger physical target | Yes, never copy secondary-ledger conversion values | inspect_scoped_reporting_currency_export |
| Physical ShortName | Blank | New physical target | Yes, service-generated only |  |
| TargetLedgerShortName | Blank | New relationship | Yes, service-generated only and independent of physical ShortName |  |
| Physical structural and calendar fields | Copy exact source value by header name | Journal or Subledger physical target, except explicitly transformed fields | Yes, block user attempts to alter inherited structure in this task | read_source_physical_template |
| Physical SLA method tuple | Copy exact source values | Journal or Subledger; Subledger requires method readiness | Yes, inherit from the actual source; do not apply the secondary-ledger Journal blank-method policy or default to Standard Accrual | read_source_physical_template |
| Physical option and account fields | Copy exact source values unless a supported task option is explicitly chosen and mapped | Journal or Subledger | No; every supported difference must be disclosed | read_source_physical_template |
| BalSegValueOptionCode and BalSegColumnName | Exact source qualifier values | Journal or Subledger | Yes, derive rather than guess | derive_source_coa_qualifiers |
| MgtSegValueOptionCode and MgtSegColumnName | Exact source qualifier values | Journal or Subledger | Yes, derive rather than guess | derive_source_coa_qualifiers |
| BingoOps balancing tuple | A and SEGMENT1 | The exact current BingoOps source is selected | Yes, require exact source evidence | derive_source_coa_qualifiers |
| BingoOps management tuple | A and SEGMENT2 | The exact current BingoOps source is selected | Yes, require exact source evidence | derive_source_coa_qualifiers |
| GL_LEDGER_SEG_VAL_ASSIGNMENT.csv rows | None | BalSegValueOptionCode is A | Yes, keep header-only |  |
| New-row audit, login, creation, update, process, and service fields | Blank | All new rows | Yes, never copy or fabricate |  |
| New-row descriptive flexfields | Blank | Baseline create | No; populate only with explicit supported intent and same-release evidence |  |
| Header-only members | Preserve exact header and zero data rows | No explicitly requested supported feature requires a row | Yes, remove unrelated carried rows | derive_minimum_target_graph |
| ASM_SETUP_CSV_METADATA.xml | Exact bytes from the current scoped export | Always | Yes, never hand-edit or regenerate | inspect_scoped_reporting_currency_export |

## Population Classes

| Population Class | Meaning | Examples |
|---|---|---|
| User required | Exact value is requested or explicitly confirmed and then resolved | Name, level, currency, applicable UI-required rate types, translation rules |
| User conditional | Required only when a selected option activates the field group | FIND_RATE days, initialization period and rate type, selective rule keys |
| Derived | Deterministic from validated authoritative facts | FirstLedgerPeriodName from the scoped source row plus LOV proof, RelationshipTypeCode, AlcInitDate, default initializing-rate date, source COA segment columns |
| Inherited | Copied by exact header from the scoped source physical row | Calendar, COA structure, SLA method, account strings, unchanged option flags |
| Closed constant | Same-release task contract proves one non-negotiable technical value | ALC, TARGET, GL, -99, Alc |
| Service generated | Intentionally blank on create and verified only after re-export | Physical ShortName, TargetLedgerShortName, audit values |
| Intentional blank | Not applicable or explicitly omitted as an atomic group | Balance physical target, REPORT_ERROR max days, disabled initialization group |
| Out-of-baseline | No value is produced without a separately evidenced design | EMU fixed-rate initialization, custom sequencing, partial account filter, selective nonbaseline rules |

## Intentional Blanks

| Field or Member | Required Blank Condition | Reason |
|---|---|---|
| Physical target rows | ConversionLevel is Balance | Balance is a relationship-only reporting currency. |
| AlcMaxDaysRollRate | MissingRateAction is REPORT_ERROR | The day window applies only to FIND_RATE. |
| Entire initialization group | Initialization is not requested | Partial initialization is invalid. |
| Balance default conversion rate | ConversionLevel is Balance | Balance uses period average and period end rate types. |
| Balance physical identifiers | ConversionLevel is Balance | No physical target exists. |
| DataConversionLevelTrans | Current Journal or Subledger ALC target | Same-release reporting-currency target rows emit blank. |
| ShortName and TargetLedgerShortName | Create package | Oracle generates separate identifiers. |
| Audit and process fields | Any new row | Source identity and prior process metadata cannot be propagated. |
| BSV assignment member rows | BalSegValueOptionCode is A | All values need no explicit assignment row in the baseline. |

## Existing Row Preservation

| Situation | Rule |
|---|---|
| Source root is required for dependency closure | Copy the exact scoped source row, including its existing audit values; for a Journal or Subledger create, the only permitted semantic change is a separately previewed AlcLedgerTypeCode transition from NONE or blank to SOURCE when exact same-release evidence requires it. |
| Unrelated primary, secondary, reporting-currency, relationship, or rule row appears in the export | Do not carry it into the create package. |
| A source field is not listed in the physical transformation allowlist | Copy it by exact header name for the new physical target, subject to the explicit new-row audit and DFF blank rules. |
| Current same-role and historical evidence disagree | Use current same-release scoped evidence and the 2026-08-27 functional closure; record the historical fact only as chronology. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MRC-040-APPLY-DEFAULTS | step | 40 | apply_default | applied->MRC-050-ENFORCE-DESIGN;failed->MRC-070-HANDLE-ERROR | MRC-030-RESOLVE-DEPENDENCIES | stop | Always |
