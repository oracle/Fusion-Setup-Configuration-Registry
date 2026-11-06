# Manage Reporting Currencies Input Validation

This resource validates creation of one reporting currency for one explicitly selected source ledger. A reporting currency is an additional currency representation of a primary or secondary ledger. Balance creates a translation relationship only; Journal converts eligible General Ledger journals and creates a physical ALC target; Subledger creates a physical ALC target with subledger-accounting representation and is supported only for a method-ready primary source.

The supported baseline is create-only and non-EMU. It does not review or submit Accounting Configuration, open periods, disable conversion, delete setup, or perform another reporting-currency lifecycle operation. Every business field that the Oracle task UI requires must be supplied by the user or shown back and explicitly confirmed, except First Opened Period for Journal or Subledger: FDoS derives that value from the exact scoped source physical row, validates it against the complete matching accounting-period LOV scope, and shows the derivation in preview. A resolver validates a free-text FDoS value; it never silently chooses a LOV value.

## Task and UI Flow

| Sequence | UI or FDoS Stage | Required Outcome |
|---|---|---|
| 1 | Select ledger scope | Resolve exactly one eligible primary or secondary source ledger; for a primary source retain its numeric LedgerId as the primary-ledger export scope and preserve the exact selected primary root for every source. |
| 2 | Add reporting currency | Capture name, description when used, conversion level, currency, and every displayed required value. |
| 3 | Enter conversion options | Capture level-specific rate types, translation rules, missing-rate behavior, accounts, flags, and optional initialization intent; for Journal or Subledger derive First Opened Period from the scoped source row and validate it against accountingPeriodsLOV. |
| 4 | Define conversion rules | Confirm the broad Other and Other and Yes baseline or collect each requested selective source/category rule; do not infer a displayed row. |
| 5 | Validate and preview | Resolve all former LOVs, derive only documented values, build the minimum target graph, and show an exact semantic and row-count diff. |
| 6 | Import handoff | Hand the immutable package to core.data-loader for its preview, approval, import, process, and diagnostic workflow. |
| 7 | Verify | Require a same-task, same-primary-ledger-scope re-export before declaring the setup verified. |
| 8 | Interpret task status | An observed Active reporting-currency status is informational; it does not authorize Review and Submit or another accounting-configuration lifecycle action. |

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Source ledger identity | SourceLedgerName and, when available, SourceLedgerId; SourcePrimaryLedgerName when the owning primary of a secondary source is not already evidenced | Stop and request the exact source ledger | Require one exact eligible source, resolve its owning primary separately, and reconcile both identities and source membership with the scoped task export | Always | resolve_source_ledger |
| Reporting currency identity | ReportingCurrencyName, Description | Stop when the name is absent; Description is optional and applies only to a physical Journal or Subledger target | Trim the name, require 1 through 30 characters, verify zero exact-name matches, and preserve exact optional description text | Always | check_reporting_currency_name_availability |
| Conversion design | ConversionLevel | Stop and request Balance, Journal, or Subledger | Map the exact user selection to BALANCE, JOURNAL, or SUBLEDGER; reject any other value | Always |  |
| Target currency | CurrencyCode | Stop and request the currency | Require one exact active enabled monetary-currency match; same-currency is allowed only after the advisory is acknowledged | Always | resolve_monetary_currency |
| Balance translation tuple | PeriodAverageRateType, PeriodEndRateType, RevenueExpenseTranslationRule, OwnerEquityTranslationRule | Stop and request or confirm every member | Resolve both rate types and accept only PTD or YTD for each translation rule | ConversionLevel is Balance | resolve_conversion_rate_type |
| Journal or Subledger conversion tuple | DefaultConversionRateType plus derived FirstLedgerPeriodName | Stop when the rate type is absent or when the scoped source period cannot be derived and validated | Resolve the exact enabled rate type; derive FirstLedgerPeriodName from the exact scoped source physical row and validate one non-adjustment match in the complete PeriodSetNameId and PeriodType LOV scope | ConversionLevel is Journal or Subledger | resolve_first_opened_period |
| Missing-rate policy | MissingRateAction, AlcMaxDaysRollRate | Use the disclosed REPORT_ERROR baseline with blank days when the optional policy is omitted; stop if a supplied override is incomplete | Accept REPORT_ERROR with blank days, or FIND_RATE with an explicit integer from 1 through 999 | Always |  |
| Non-EMU initialization | InitializeConversion, BalanceInitializationPeriod, AlcInitDate, AlcInitializingRateDate, AlcInitializingRateTypeTrans | Stop if intent is unknown or any enabled member is absent or invalid | If omitted, keep the entire group blank; if enabled, validate the distinct initialization-period predicate and derive only the documented dates | ConversionLevel is Journal or Subledger | resolve_balance_initialization_period |
| Journal conversion rules | JournalRuleIntent, JournalSource, JournalCategory, IncludeFlag, UserUpdatableFlag | Use the disclosed current baseline only after the user accepts its broad catch-all behavior; stop when a supplied selective set is incomplete | Confirm the current baseline Other and Other and Y and Y row, or resolve every selective row independently | Always | resolve_journal_source |
| Current package evidence | ScopedTaskExport, PackageEnvironment, PackageRelease, SourceLedgerScope | Stop; do not synthesize a package | Require a current same-task, same-environment export scoped to the selected primary-ledger root | Always | inspect_scoped_reporting_currency_export |
| Source physical template | Source rows from GL_PRIMARY_LEDGER.csv and GL_SECONDARY_LEDGER.csv | Stop; do not hand-build 133-column rows | Require the exact physical source row in both aliases and verify field-for-field equivalence | ConversionLevel is Journal or Subledger | read_source_physical_template |

## User Intake and Requiredness

| Field | Requiredness | Accepted Value or Confirmation | Notes |
|---|---|---|---|
| SourceLedgerName | Definitely required | Exact free-text ledger name | Source may be primary or secondary for Balance and Journal; Subledger requires primary. |
| ReportingCurrencyName | Definitely required | Trimmed nonblank name of at most 30 characters | Must be unique in the wider ledger/reporting-currency namespace; GL-781171 is a blocking collision. |
| ConversionLevel | Definitely required | Balance, Journal, or Subledger | The level changes the physical graph and required fields. |
| CurrencyCode | Definitely required | Exact enabled monetary currency code | Same as source currency is technically accepted but normally adds no currency diversification. |
| Description | Optional | Exact user text or blank | Applies only to physical Journal or Subledger targets; never synthesize marketing or business-purpose text. |
| PeriodAverageRateType and PeriodEndRateType | Conditionally mandatory | Exact enabled rate-type display names | Required for Balance; GL-781333 applies when translation details are incomplete. |
| RevenueExpenseTranslationRule and OwnerEquityTranslationRule | Conditionally mandatory | PTD or YTD | Required for Balance and separately confirmed. |
| FirstOpenedPeriod | Not mandatory user intake; optional evidenced override | Normally omitted because FDoS derives the exact source FirstLedgerPeriodName. A different supplied period requires exact same-release UI or scoped-export eligibility evidence in addition to LOV validation. | For Journal and Subledger, derive the value from the selected source row and show the period, period-set/type tuple, non-adjustment result, and dates in preview. GL-781342 still blocks an absent or invalid authored FirstLedgerPeriodName. |
| DefaultConversionRateType | Conditionally mandatory | Exact enabled rate-type display name | Required for Journal and Subledger. |
| MissingRateAction | Optional/defaulted | REPORT_ERROR or FIND_RATE | Omission uses the disclosed current REPORT_ERROR baseline; FIND_RATE is an explicit override. |
| AlcMaxDaysRollRate | Conditionally mandatory | Integer 1 through 999 | Required only with FIND_RATE and forbidden with REPORT_ERROR. |
| RoundingAccount | Optional/inherited | Exact valid source-COA account when overridden | Journal and Subledger inherit the exact source candidate; validate it and ask only for an override. |
| InitializeConversion | Optional but explicit | Yes or No | Yes activates the entire non-EMU initialization group. |
| BalanceInitializationPeriod and initialization rate type | Conditionally mandatory | Exact eligible period and exact enabled rate type | Required when initialization is Yes. |
| RevaluationBasis, JournalApproval, RetainTransactionRate, RetainJournalCreator | Optional | Exact supported value or explicit acceptance of a disclosed baseline | Do not infer intent from an export alone. |
| Custom sequencing | Optional out-of-baseline | Exact design plus same-release proof | No default is invented. |
| Partial account-filter initialization | Optional out-of-baseline | Exact account-filter design plus same-release proof | No assignment or filter row is authored in the baseline. |
| Selective journal rules | Optional out-of-baseline | Exact source/category/include policy plus same-release proof | Manual and Adjustment and N is a proven persistence example, not a default or permission to infer another combination. |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Source ledger is absent, ambiguous, outside the scoped export, or an ineligible category | Blocked | Return the candidate identities and request an exact supported source | resolve_source_ledger |
| Subledger is selected for a secondary source or a source without method-ready evidence | Blocked | Choose a method-ready primary source or move the design outside this baseline | verify_subledger_source_readiness |
| Any free-text LOV value has zero or multiple eligible matches | Blocked | Preserve the user text and ask for a precise supported value; never select the first result |  |
| The scoped export is stale, cross-environment, broad, missing metadata, or missing an exact source root | Blocked | Obtain a fresh primary-ledger-scoped Manage Reporting Currencies export | inspect_scoped_reporting_currency_export |
| Journal or Subledger source physical aliases disagree | Blocked | Re-export and reconcile the package before authoring | read_source_physical_template |
| All validation and reference facts are exact | Ready | Continue to dependency readiness |  |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Name syntax and uniqueness | Trim outer whitespace; require 1 through 30 characters; reject any exact collision and preserve the original input in the error | Always | check_reporting_currency_name_availability |
| Conversion enumeration | Map Balance to BALANCE, Journal to JOURNAL, and Subledger to SUBLEDGER; reject every other label or code | Always |  |
| Source eligibility | Require PRIMARY or SECONDARY for Balance and Journal; require PRIMARY and accounting-method readiness for Subledger | Always | resolve_source_ledger |
| Currency membership | Require one exact active enabled monetary currency; disclose but do not block a same-currency design after user confirmation | Always | resolve_monetary_currency |
| Translation completeness | Require both rate types and both independent PTD or YTD choices | ConversionLevel is Balance | resolve_conversion_rate_type |
| First opened period derivation and eligibility | Read FirstLedgerPeriodName, PeriodSetName, and AccountedPeriodType from the exact scoped source physical row; query the complete accountingPeriodsLOV scope using PeriodSetNameId and PeriodType; require exactly one row whose PeriodNameId equals the exported FirstLedgerPeriodName and whose AdjustmentPeriodFlag is false. Do not sort labels, choose the first response row, infer status fields the endpoint does not return, or reuse initialization eligibility. | ConversionLevel is Journal or Subledger | resolve_first_opened_period |
| Initialization period eligibility | Require the first future-enterable period or first never-opened period using the balance-initialization predicate; do not reuse FirstOpenedPeriod merely because its name exists | InitializeConversion is Yes | resolve_balance_initialization_period |
| Non-EMU initialization atomicity | Require AlcInitConvOptionCode I, eligible AlcInitPeriod, AlcInitDate equal to period start, AlcInitializingRateDate defaulting to prior-period end or the day before period start, and exact AlcInitializingRateTypeTrans; otherwise block | InitializeConversion is Yes | resolve_balance_initialization_period |
| Initialization omission | Require all five initialization fields blank; reject a partial group | InitializeConversion is No |  |
| Missing rate action | Apply the disclosed REPORT_ERROR baseline when omitted; accept only explicit FIND_RATE or REPORT_ERROR when supplied | Always |  |
| Missing rate days | Require a base-10 integer from 1 through 999 for FIND_RATE; require blank for REPORT_ERROR; zero, negative, decimal, text, and greater than 999 block | Always |  |
| Rate type membership | Require one exact enabled UserConversionType for every applicable rate field | A rate-type field is required or supplied | resolve_conversion_rate_type |
| Rounding account | Validate the inherited source candidate; when the user overrides it, require one exact enabled combination in the source COA with the intended rounding purpose | ConversionLevel is Journal or Subledger | resolve_rounding_account |
| Journal rule completeness | Require source, category, IncludeFlag, and UserUpdatableFlag as an atomic row; empty UI-added rows are not rules | A custom or baseline rule is to be authored | resolve_journal_category |
| Baseline journal rule | Require exactly Other and Other and Y and Y unless the user explicitly requests and proves a selective design | Current Balance, Journal, or Subledger baseline is selected | resolve_journal_category |
| Display-only Closing Journal line | Do not author Closing Journal and Other and N from UI display state; it was not emitted by the same-release Journal or Subledger export | Any rule preview contains that line without exported evidence |  |
| Physical target necessity | Require zero target rows for Balance and exactly one new ALC and TARGET row in each physical alias for Journal or Subledger | Always | derive_minimum_target_graph |
| Physical alias parity | Compare all 133 headers and values after substituting only the alias-specific parent header; any other difference blocks | ConversionLevel is Journal or Subledger | read_source_physical_template |
| Existing source role | Preserve SOURCE when already emitted; when a source with no physical ALC is proven to require the role transition, allow only AlcLedgerTypeCode from NONE or blank to SOURCE and show it as a separate existing-row change | ConversionLevel is Journal or Subledger | inspect_scoped_reporting_currency_export |
| Generated identifiers | Require physical ShortName and relationship TargetLedgerShortName blank on create where supported; never fabricate, copy, or interchange them | Always |  |
| Segment qualifier fields | Derive column names from exact source COA qualifiers, never segment ordinals; for the proven BingoOps source require A and SEGMENT1 plus A and SEGMENT2 | ConversionLevel is Journal or Subledger | derive_source_coa_qualifiers |
| All-values assignment | Require GL_LEDGER_SEG_VAL_ASSIGNMENT.csv header-only when BalSegValueOptionCode is A; rows require explicit nonbaseline account-filter intent and same-release evidence | Always |  |
| Source-root closure | Require exactly one owning-primary root in GL_LEDGER.csv and ORA_GL_PRIMARY_LEDGER_CONFIG.csv. Retain that primary and the actual source in both physical aliases, once when they are the same; exclude unrelated existing rows | Always | derive_minimum_target_graph |
| Relationship cardinality | Require exactly one new ORA_GL_LEDGER_RELATIONSHIP.csv row for the target design | Always | derive_minimum_target_graph |
| Relationship ledger aliases | Require nonblank, resolvable Name, Name1, Name2, and Name3 under the level-specific Relationship Row Population Contract; validate every repeated rule-parent key against the relationship | Always | derive_minimum_target_graph |
| Rule cardinality | Require only the new target rules; the baseline has one Other and Other and Y and Y row | Always | derive_minimum_target_graph |
| Header integrity | Preserve every exact member name, exact header text, header order, and column count from the current scoped package | Always | inspect_scoped_reporting_currency_export |
| CSV serialization | Use RFC-compatible quoting, preserve embedded newlines in account-segment fields, reopen every generated CSV, and require each row width to equal its header width | Always | verify_authored_package_shape |
| Metadata integrity | Preserve ASM_SETUP_CSV_METADATA.xml from the same-task, same-environment scoped export without editing | Always | inspect_scoped_reporting_currency_export |
| Unknown fields | Reject undocumented fields, aliases, or guessed identifiers and name the unsupported input | User supplies a field outside this contract |  |

## Minimum Import Member Impact

| Member | Balance | Journal or Subledger | Baseline Rule |
|---|---|---|---|
| GL_LEDGER.csv | Exact owning-primary root only | Exact owning-primary root only | No target row. |
| ORA_GL_PRIMARY_LEDGER_CONFIG.csv | Exact owning-primary root only | Exact owning-primary root only | No target row. |
| GL_PRIMARY_LEDGER.csv | Owning primary and actual source, once when equal | Owning primary and actual source, once when equal, plus one new ALC and TARGET row | Both aliases represent the same physical target. |
| GL_SECONDARY_LEDGER.csv | Owning primary and actual source, once when equal | Owning primary and actual source, once when equal, plus one new ALC and TARGET row | Both aliases represent the same physical target. |
| ORA_GL_LEDGER_RELATIONSHIP.csv | One new relationship | One new relationship | No unrelated relationship is carried forward. |
| ORA_GL_JOUNAL_CONVERSION_RULES.csv | Only the new target rule rows | Only the new target rule rows | Current default is one Other and Other and Y and Y row. |
| ORA_GL_JOURNAL_CONFIG_DETAIL.csv | Header-only | Header-only | Populate only for an explicitly requested supported nonbaseline feature. |
| ORA_LEGAL_ENTITY_BAL_SEG_VAL_DEF.csv | Header-only | Header-only | Populate only for an explicitly requested supported feature. |
| GL_LEDGER_SEG_VAL_ASSIGNMENT.csv | Header-only | Header-only for BalSegValueOptionCode A | No baseline data row. |
| ORA_PRIMARY_BALANCING_SEGMENT_VALUE_CONVERSION_RULES.csv | Header-only | Header-only | Partial account-filter initialization is out-of-baseline. |
| ASM_SETUP_CSV_METADATA.xml | Preserve scoped metadata contract | Preserve scoped metadata contract | Never regenerate or edit by guess. |

## Physical Row Population Contract

Author the physical ALC row by exact header-name mapping from the current source physical row, never by column position. The table is a transformation allowlist; every unlisted header is copied byte-for-byte from the source row unless the current same-role template proves a required blank.

| Field or Family | Population Rule | Validation |
|---|---|---|
| Alias parent | GL_PRIMARY_LEDGER uses ORA_GL_PRIMARY_LEDGER_CONFIG.Name; GL_SECONDARY_LEDGER uses GL_LEDGER.Name | Both equal SourcePrimaryLedgerName, including when the actual source is secondary. |
| Name and Name1 | ReportingCurrencyName | Both equal the validated target name. |
| Description | Exact optional user text or blank | No synthesized description; not applicable to Balance. |
| ShortName | Blank on create | Service-generated after successful import; never use TargetLedgerShortName. |
| LedgerCategoryCode and AlcLedgerTypeCode | ALC and TARGET | Exact closed values. |
| ObjectTypeCode and LeLedgerTypeCode | Preserve exact source values | No guessed constants. |
| CurrencyCode | Validated CurrencyCode | Exact resolved code. |
| PeriodSetName, AccountedPeriodType, CalendarName, UserPeriodSetName | Preserve exact source values | Must remain source compatible. |
| FirstLedgerPeriodName | Exact scoped source FirstLedgerPeriodName after resolve_first_opened_period validates the matching PeriodSetNameId, PeriodType, PeriodNameId, and non-adjustment row | Journal or Subledger baseline derives and previews this value; it is not mandatory user intake. |
| KeyFlexfieldCode, StructureInstanceCode, ApplicationShortName | Preserve exact source values | Must match the source COA structure. |
| BalSegValueOptionCode and BalSegColumnName | Preserve or derive from exact source qualifier evidence | BingoOps evidence is A and SEGMENT1. |
| MgtSegValueOptionCode and MgtSegColumnName | Preserve or derive from exact source qualifier evidence | BingoOps evidence is A and SEGMENT2. |
| SLA accounting-method tuple | Preserve exact source method code, type, and language | Subledger additionally requires method readiness. |
| Account segment families | Preserve exact multiline source strings | CSV quoting and embedded newline count must survive. |
| EnableJeApprovalFlag and other option flags | Preserve source unless the user explicitly selected a supported task option and same-role evidence defines the mapping | Every change appears in preview. |
| AlcTrans | Alc | Exact current physical-target marker. |
| DataConversionLevelTrans | Blank | Current reporting-currency ALC rows prove blank; do not reuse secondary-ledger conversion codes. |
| Audit, login, date, process, and service identifiers | Blank on the new row | Never copy source audit identity or fabricate service values. |
| Descriptive flexfields | Blank unless the user explicitly requested and same-release evidence supports them | No baseline DFF propagation. |
| Every remaining header | Copy the exact source value by header name | A missing, duplicate, or unexpected header blocks authoring. |

## Relationship Row Population Contract

| Field or Family | Population Rule | Validation |
|---|---|---|
| GL_LEDGER.Name and GL_SECONDARY_LEDGER.Name | GL_LEDGER.Name = SourcePrimaryLedgerName; GL_SECONDARY_LEDGER.Name = SourceLedgerName | The owning primary and actual source are distinct roles; they coincide only for a primary source. |
| Name | SourceLedgerName for every conversion level | Resolve the actual source physical ledger, including a secondary source. |
| TargetLedgerCategoryCode | ALC | Exact constant. |
| RelationshipTypeCode | BALANCE, JOURNAL, or SUBLEDGER | Derived only from validated ConversionLevel. |
| Name1 | SourceLedgerName for Balance; ReportingCurrencyName for Journal or Subledger | Balance references the source physical ledger; Journal and Subledger reference the proposed physical ALC target. |
| Name2 | SourceLedgerName for Balance or Journal; ReportingCurrencyName for Subledger | Required SLA-ledger reference; resolve the existing source or proposed physical target. Never leave blank. |
| Name3 | SourcePrimaryLedgerName for every conversion level | Resolve the owning primary even when the actual source is secondary. |
| TargetCurrencyCode | Validated CurrencyCode | Exact resolved code. |
| ApplicationShortName and OrgIdTrans | GL and -99 | Require same-release same-task evidence. |
| TargetLedgerName | ReportingCurrencyName | Exact validated target name. |
| RelationshipEnabledFlag, InheritCreationUserFlag, AutomaticPostFlag, StatusCode | Use the exact current same-release, same-role create values; the current scoped minimal contract proves Y, Y, Y, CONFIRMED | Show all four in preview; preserve existing rows and perform no lifecycle operation. |
| AlcNoRateActionCode and AlcMaxDaysRollRate | Explicit policy pair | FIND_RATE requires 1 through 999; REPORT_ERROR requires blank. |
| AlcInheritConversionType | N for the current non-EMU baseline | Custom inheritance is out-of-baseline. |
| AlcInitConvOptionCode and initialization fields | Entire atomic group or all blank | Apply the non-EMU initialization contract exactly. |
| RevExpXlationRuleCode and OwnerEquityXlationRuleCode | User-confirmed PTD or YTD for Balance; service-derived PTD and PTD for the current Journal or Subledger new-row baseline | Journal and Subledger do not expose these as required intake; do not turn them into extra questions. |
| TargetLedgerShortName | Blank on create | Service-generated relationship identifier; never use physical ShortName. |
| AlcDefaultConvRateTypeTrans | Validated default rate type for Journal or Subledger; blank for Balance | Exact display value. |
| AlcInitializingRateTypeTrans | Exact initialization rate type when initialization is enabled; otherwise blank | Atomic with initialization group. |
| AlcPeriodAverageRateTypeTrans and AlcPeriodEndRateTypeTrans | Validated Balance rate types; blank for Journal or Subledger | Level-exclusive. |
| DisableConversionDate, BSV replication, tree, DFF, audit, and service fields | Blank in the baseline create row | Require explicit supported intent before any nonblank value. |

## Journal Rule Population Contract

| Field or Family | Population Rule | Validation |
|---|---|---|
| Relationship parent fields | Repeat GL_LEDGER.Name, GL_SECONDARY_LEDGER.Name, and every exported ORA_GL_LEDGER_RELATIONSHIP business-key field through OrgIdTrans | Match the new relationship exactly, including its level-specific Name1 and owning-primary Name3; do not add an unexported Name2 rule header. |
| JeSourceKey and JeSourceName | Other for the current baseline | Resolve both for a selective design. |
| JeCategoryKey and JeCategoryName | Other for the current baseline | Resolve both for a selective design. |
| UserUpdatableFlag and IncludeFlag | Y and Y for the current baseline | The user confirms the broad include behavior. |
| Audit, login, date, DFF, inheritance, and rate-type fields | Blank on create unless same-release evidence requires a supported value | Never copy prior execution metadata. |

## Preview and Verification Requirements

| Checkpoint | Required Evidence |
|---|---|
| Intake summary | Exact environment, source ledger, name, level, currency, required user values, optional choices, advisories, explicit confirmations, and the derived First Opened Period evidence for Journal or Subledger. |
| Package diff | SHA-256 of source export and immutable candidate ZIP; exact member order; exact headers; before and after row counts; added, removed, and changed semantic rows. |
| Minimum graph | One owning-primary root; required primary and actual-source physical context; zero or one physical target by level; one relationship; only new target rules; all other CSV members header-only. |
| Blank and generated values | Explicit list of intended blanks, including both independent generated short-name fields and all new-row audit values. |
| Safety boundary | Statement that no Review and Submit, period opening, disable, deletion, or other lifecycle operation is included. |
| Re-export | Same environment, same task, same primary-ledger scope; match target name, level, currency, rate options, initialization, physical cardinality, rules, generated identifiers, and absence of unrelated changes. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MRC-010-VALIDATE-INPUT | decision | 10 | validate_input | valid->MRC-020-RESOLVE-REFERENCES;invalid->MRC-070-HANDLE-ERROR | none | stop | Always |
