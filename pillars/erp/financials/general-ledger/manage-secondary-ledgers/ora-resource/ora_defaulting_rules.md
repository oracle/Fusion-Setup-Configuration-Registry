# Manage Secondary Ledgers Defaulting Rules

Apply the documented conversion-specific defaults after validating the current task package and source-primary values. An existing secondary under the selected primary is not a prerequisite. Defaults do not replace required business inputs or authorize unsupported designs.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| LedgerCategoryCode | SECONDARY | New physical secondary row | No |  |
| AlcLedgerTypeCode | NONE | New physical secondary row | No |  |
| SecondaryLedgerTrans | Secondary | New physical secondary row | No |  |
| DataConversionLevelTrans | BALANCE, JOURNAL, SUBLEDGER, or ADJUST mapped from the validated user choice | New physical secondary row | No |  |
| ChartOfAccountsName, StructureInstanceId, StructureInstanceNumber, StructureInstanceCode, and structure identity | Exact enabled chartOfAccountsLOV row plus matching structure instance from the current populated COA task export | New physical secondary row | No; map ChartOfAccountsName from returned Name and never substitute StructureInstanceId for StructureInstanceNumber | resolve_coa_structure_roles |
| UserPeriodSetName, PeriodSetName, AccountedPeriodType | Exact enabled accounting-calendar record | New physical secondary row | No | resolve_accounting_calendar |
| FirstLedgerPeriodName | Exact explicit physical first-period input or independently authoritative same-role export evidence validated against PeriodNameId and PeriodType | New physical secondary row after complete period lookup | No; response order and label sorting are not authority, and this create value does not replace mandatory user confirmation in the secondary-options task | resolve_secondary_first_ledger_period |
| Secondary-options First Opened Period handoff | No create-package value | A user already supplied the later options-task period | No; retain for Specify Ledger Options only and never substitute it for the resolver-derived physical FirstLedgerPeriodName |  |
| CurrencyCode | Exact active monetary currency selected by the user | New physical secondary row | No | resolve_monetary_currency |
| SequencingModeCode | Exact source-primary value, or N only when that source value is null | New secondary row | No | read_source_primary_export |
| SingleCurrencyJournalFlag | Exact source-primary value | New secondary row | No | read_source_primary_export |
| BalanceMjeByCurrencyFlag | Exact source-primary value | New secondary row | No | read_source_primary_export |
| SlaAccountingMethodCode | Blank for BALANCE/JOURNAL; resolved user method code for SUBLEDGER/ADJUST, or STANDARD_ACCRUAL when omitted | New physical secondary row | Preserve the applicable resolved user choice | resolve_accounting_method_evidence |
| SlaAccountingMethodType | Blank for BALANCE/JOURNAL; resolved method type for SUBLEDGER/ADJUST, with S for the Standard Accrual default | New physical secondary row | Preserve the resolved method type | resolve_accounting_method_evidence |
| SlaDescriptionLanguage | Intentional blank | New physical secondary row at structural create | No for creation | resolve_accounting_method_evidence |
| ObjectTypeCode, LeLedgerTypeCode, LedgerAttributes, KeyFlexfieldCode, ApplicationShortName | L, L, L, GL#, GL | A same-release controlled normal physical-secondary role proves the constants | No | resolve_coa_structure_roles |
| BalSegValueOptionCode and MgtSegValueOptionCode | A and A | New same-release controlled all-values secondary design | No; explicit supported assignment design uses its own rows | resolve_coa_structure_roles |
| BalSegColumnName, BalSegValueSetCode, MgtSegColumnName, MgtSegValueSetCode | Exact role metadata from the documented joins within the selected COA task export | New secondary row | No | resolve_coa_structure_roles |
| FutureEnterablePeriodsLimit | 1 | New same-release matching controlled secondary role only; ledger options later require user confirmation | Yes at Specify Ledger Options, never silently in that task |  |
| NumberOfProcessors and ProcessingUnitSize | 1 and 5000 | New same-release matching controlled physical-secondary role | No |  |
| ProjectsImplementedTrans, CreateJeFlag, AutorevAfterOpenPrdFlag | false, Y, Y | New same-release matching controlled physical-secondary role | No for structural create |  |
| SuspenseAllowedFlag, AllowIntercompanyPostFlag, TrackRoundingImbalanceFlag, EnableAverageBalancesFlag, EnableBudgetaryControlFlag, RequireBudgetJournalsFlag, EnableJeApprovalFlag, EnableAutomaticTaxFlag | N for each field | New matching controlled secondary and the user did not request the optional family | No in this task |  |
| ConsolidationLedgerFlag, TranslateEodFlag, TranslateQatdFlag, TranslateYatdFlag, AutomaticallyCreatedFlag, SlaBalByLedgerCurrFlag, EnableReconciliationFlag, SlaLedgerCashBasisFlag, UssglOptionCode | N for each field | New matching controlled secondary and the user did not request the optional family | No in this task |  |
| ValidateJournalRefDate, JrnlsGroupByDateFlag, PriorPrdNotificationFlag, PopUpStatAccountFlag, NetClosingBalFlag, IncomeStmtAdbStatusCode, PostingCutoffFlag | N for each field | New matching controlled secondary and the user did not request the optional family | No in this task |  |
| RetEarnCcidSegments | Intentional blank | Controlled new Journal or Subledger secondary shell; retained earnings is completed in Specify Ledger Options | No |  |
| CumTransCcidSegments, ResEncumCcidSegments, NetIncomeCcidSegments, RoundingCcidSegments, SlaEntCurBalSusSegments, SlaLedgerCurBalSusSegments, IntercoGainLossSegments, CrossLgrClrAccSegments, SuspenseAccountCcidSegments | Intentional blank or exact role-inherited value only where proven | New physical secondary role and corresponding option family is not explicitly requested | No; never borrow another ledger's account and do not blanket-copy retained earnings | read_source_primary_export |
| EnfSeqDateCorrelationCode | Intentional blank | Controlled new physical secondary role | No; do not copy the primary N |  |
| ShortName, LedgerId, physical identifiers, audit fields, process fields | Intentional blank for create where generation is supported | New row | No; service owns generation |  |
| Attribute1 through Attribute15 and AttributeCategory | Intentional blank | DFF context is not deployed and explicitly requested | No; author only with exact deployed-context evidence plus explicit user intent |  |
| TargetLedgerCategoryCode and RelationshipTypeCode | SECONDARY and the validated conversion code | New source-primary to target-secondary relationship | No |  |
| Relationship Name, Name2, and Name3 | Exact SourcePrimaryLedgerName | BALANCE, JOURNAL, SUBLEDGER, and ADJUST | No; source, SLA, and owning-primary roles all refer to the primary | read_source_primary_export |
| Relationship Name1 | Exact SecondaryLedgerName | BALANCE, JOURNAL, SUBLEDGER, and ADJUST | No; must resolve to the target SECONDARY physical row |  |
| SourceLedgerName, SourceLedgerCategoryCode, TargetLedgerName, TargetCurrencyCode, ApplicationShortName | Exact primary name, PRIMARY, exact secondary name, exact selected currency, GL | New source-primary to target-secondary relationship | No; names/currency are user/resolver values and role/application codes require exact matching-role evidence | read_source_primary_export |
| OrgIdTrans, RelationshipEnabledFlag, InheritCreationUserFlag, AutomaticPostFlag | -99, N, Y, N | Controlled new in-process secondary relationship | No |  |
| AlcNoRateActionCode and AlcInheritConversionType | REPORT_ERROR and Y | Controlled new in-process secondary relationship | No |  |
| Name4 and AlcDefaultConvRateTypeTrans | Intentional blank | New relationship before the dedicated mapping task resolves any different-COA mapping or different-currency rate choice | No; never guess a mapping or Corporate |  |
| RevalFromPriLgrCurr, initialization, disable-date, other translation/rate, BSV tree/replication, and relationship DFF fields | Intentional blank or preserve exact export | Optional design was not explicitly requested and no exact same-role contract owns the field | No; use the mapping/UI handoff when requested |  |
| TargetLedgerShortName | Intentional blank on create; service derives it from the target resolved by Name1 | New relationship | No; never invent it or leave Name1 unresolved |  |
| JeSourceKey, JeSourceName, JeCategoryKey, JeCategoryName, UserUpdatableFlag, IncludeFlag | Other, Other, Other, Other, Y, Y | New BALANCE, JOURNAL, or SUBLEDGER secondary baseline in the current simplified task package | No; apply only to the new relationship and preserve existing rules |  |
| Seeded Closing Journal and Revaluation inclusion rules | Service generated during simplified import | New JOURNAL or SUBLEDGER secondary baseline | No; do not author duplicate seeded rows or a conversion-set identifier |  |

## Population Classes

| Population Class | Rule |
|---|---|
| Required user input | Preserve the exact raw business choice; only documented closed-enum mapping may produce a separate code. An all-whitespace value blocks as missing. |
| Conditional user input | Collect only when the documented trigger applies; a triggered blank blocks. |
| Optional method desired state | For SUBLEDGER/ADJUST, author the resolved user choice and default only when omitted; BALANCE/JOURNAL have no method tuple. |
| Resolver derived | Populate only from one exact eligible authoritative record. |
| Export derived or inherited | Copy only from the exact scoped source row or dependency export and show it in preview. |
| Controlled role default | Apply only the documented defaults for the validated conversion level and package contract; never copy another ledger's customizations. |
| Intentional blank | Emit blank exactly when the proven role contract requires it. |
| Service owned | Leave unpopulated for create when generation is supported, then verify the generated value by re-export. |
| Preserve existing | On edit or dependency closure, retain the export byte value unless an approved field delta owns the change. |

## CSV Field Population

| Package Member | Relevant Population Behavior |
|---|---|
| GL_PRIMARY_LEDGER.csv | Add the complete SECONDARY physical row with user, resolver, inherited, controlled-default, blank, and service-owned values classified above. |
| GL_SECONDARY_LEDGER.csv | Add the same logical and physical values under the second alias; any semantic difference blocks preview. |
| ORA_GL_LEDGER_RELATIONSHIP.csv | Add exactly one disabled in-process primary-to-secondary relationship with OrgIdTrans -99; do not activate or complete mapping. |
| ORA_GL_JOUNAL_CONVERSION_RULES.csv | For a new BALANCE, JOURNAL, or SUBLEDGER secondary, add exactly one baseline Other and Other Y and Y row. Set GL_LEDGER.Name and GL_SECONDARY_LEDGER.Name to the source primary; repeat the relationship's Name, Name1, Name3, TargetLedgerCategoryCode, RelationshipTypeCode, TargetCurrencyCode, ApplicationShortName, and OrgIdTrans under their exact exported parent columns. Keep audit and unrequested optional fields blank and preserve all existing rows. |
| GL_LEDGER_SEG_VAL_ASSIGNMENT.csv | Keep header-only for all-values code A; add rows only for explicitly reviewed assignment scope. |
| Remaining CSV members | Preserve dependency closure, row order, headers, aliases, header-only state, and unrelated rows unchanged. |
| ASM_SETUP_CSV_METADATA.xml | Preserve the export-generated manifest; do not populate service process or audit fields. |

Evidence: 11.13.27.04.0 SECONDARY/SUBLEDGER exports and reviewed 26.10 source for [secondary relationship defaults](https://codesearch.oraclecorp.com/source/xref/FUSIONAPPS_11.13.26.10.0_LINUX.X64/fusionapps/fin/components/ledger/gl/ledgers/ledgerDefinitions/model/src/oracle/apps/financials/generalLedger/ledgers/ledgerDefinitions/model/entity/LedgerEOImpl.java#4351), [Other/Other Y/Y](https://codesearch.oraclecorp.com/source/xref/FUSIONAPPS_11.13.26.10.0_LINUX.X64/fusionapps/fin/components/ledger/gl/ledgers/ledgerDefinitions/model/src/oracle/apps/financials/generalLedger/ledgers/ledgerDefinitions/model/entity/LedgerRelationshipEOImpl.java#3006), and [service-generated import rules](https://codesearch.oraclecorp.com/source/xref/FUSIONAPPS_11.13.26.10.0_LINUX.X64/fusionapps/fin/components/ledger/gl/ledgers/ledgerDefinitions/model/src/oracle/apps/financials/generalLedger/ledgers/ledgerDefinitions/model/entity/LedgerRelationshipEOImpl.java#3259).

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MSL-040-APPLY-DEFAULTS | step | 40 | apply_default | applied->MSL-050-ENFORCE-DESIGN;failed->MSL-070-HANDLE-ERROR | MSL-030-RESOLVE-DEPENDENCIES | stop | Always |
