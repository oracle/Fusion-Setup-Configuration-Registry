# Manage Secondary Ledgers Dependency Readiness

Dependency checks protect the structural create from stale or cross-environment evidence. They do not authorize creation of missing setup and do not complete the later mapping or ledger-options tasks.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Environment and task scope | Confirm target environment, release, Financials offering, General Ledger functional area, exact source primary, and Manage Secondary Ledgers task scope. |
| 2 | Source package | Acquire a validated project package, otherwise a fresh direct task export, otherwise a signed-in UI download; block when no authoritative package is available. |
| 3 | Source primary | Resolve one PRIMARY ledger and reconcile its rows in both 133-column aliases. |
| 4 | Primary options import gate | For a newly FSCR-created primary, require successful primary creation plus completed and verified primary Specify Ledger Options before any live secondary import. Secondary package preparation may overlap, but import may not. |
| 5 | Reference setup | Resolve enabled COA identity, derive segment roles from a current populated COA task export, and resolve enabled accounting calendar, period attributes, and active monetary currency. |
| 6 | Conversion dependencies | Enforce Adjustment Only equality, apply the conversion-level method policy, require source-primary method readiness for Subledger, and record later mapping or rate-policy dependencies. |
| 7 | Package closure | Preserve all required members, headers, ordering, manifest, header-only files, unrelated rows, and dependency closure. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| task_package | Exact FSM task package | Yes | Always | Verify | Validated project package, fresh direct export, or signed-in UI download in that order | inspect_task_package | The package carries the current release schema and business-object closure | Provide or acquire an authoritative Manage Secondary Ledgers package; do not use a hand-built ZIP | Package release, task scope, headers, aliases, manifest, baseline rows |
| source_primary | Source primary ledger | Yes | Always | Lookup | Exact current primary export plus authorized ledger LOV | resolve_source_primary_ledger | The secondary must belong to one primary and inherit exact policy | Supply a precise primary name or ID | SourcePrimaryLedgerId, SourcePrimaryLedgerName, source aliases |
| source_primary_export | Source primary physical row | Yes | Always | Verify | Both ledger aliases in the validated scoped export | read_source_primary_export | Compatibility and inherited flags require the exact source row | Re-export if the two aliases disagree or the source row is absent | Source COA, calendar, period set, period type, currency, inherited flags |
| source_primary_options_complete | Verified primary-ledger options | Yes | Source primary was newly created through FSCR | Verify | Successful primary create receipt plus primary-context GL_SPECIFY_LEDGER_OPTIONS terminal-success receipt and filtered identical-scope re-export | verify_source_primary_options_complete | Fusion rejects a secondary when its source primary options are incomplete; retained earnings and the assigned-method language must be valid first | Package preparation may continue, but do not preview for approval or import the secondary until the exact primary options are verified. Then regenerate the preview because readiness changed | Primary create/options receipts; retained-earnings, Standard Accrual, English language, triggered-option and alias-parity readiness |
| coa_structure | Accounting chart structure | Yes | Always | Lookup | Enabled chartOfAccountsLOV identity plus current populated GL_MANAGE_CHARTS_OF_ACCOUNTS_STRUCTURE_INSTANCES or GL_MANAGE_CHARTS_OF_ACCOUNTS task export for every semantic role; trigger a task-level export when no usable existing package contains the selected COA | resolve_coa_structure_roles | Segment columns and value sets are owned by the COA export contract, not constants and not REST-describe outputs | Provide an eligible COA; FSCR reuses a current matching export or triggers the named task export and reports exact member/key defects | ChartOfAccountsName, StructureInstanceId, StructureInstanceNumber, StructureInstanceCode, StructureCode, KeyFlexfieldCode, ApplicationId, balancing and management metadata; export receipt |
| calendar | Accounting calendar and physical period identity | Yes | Always | Lookup | accountingCalendarsLOV queried by UserPeriodSetName plus accountingPeriodsLOV queried by PeriodSetNameId and filtered locally by PeriodType | resolve_accounting_calendar | Calendar identity determines user period-set display, period set/type, and exact physical FirstLedgerPeriodName; the calendar LOV has no enabled flag | Provide an exact ACCOUNTING calendar and explicit physical FirstLedgerPeriodName or independently authoritative same-role evidence; do not use response order | UserPeriodSetName, CalendarId, PeriodSetName, AccountedPeriodType, FirstLedgerPeriodName |
| currency | Monetary currency | Yes | Always | Lookup | Enabled monetary currency LOV | resolve_monetary_currency | Ledger currency is a mandatory business choice | Provide an active monetary currency | CurrencyCode |
| accounting_method | Conversion-level Accounting Method | Yes | Always for a new secondary | Verify | Validated conversion level and exact method evidence; Standard Accrual default only when applicable and omitted | resolve_accounting_method_evidence | Balance/Journal reject a populated method; Subledger requires one; Adjustment Only uses the agreed FSCR default policy | Supply an optional applicable method name; an explicit choice must resolve before create | SlaAccountingMethodCode, SlaAccountingMethodType, blank SlaDescriptionLanguage, applicable effective method name |
| adjustment_compatibility | Equality to source primary | Conditional | Conversion level is Adjustment Only or ADJUST | Verify | Resolved user choices compared with exact source-primary export | read_source_primary_export | Product validation rejects incompatible adjustment-only designs | Choose the same COA, calendar, period set, period type, and currency as the primary | Compatibility result |
| coa_mapping_later | Primary-to-secondary COA mapping | Conditional | Secondary COA differs from primary COA | Blocked for later review, not silently created here | Exact selected COAs and later mapping-task export | read_source_primary_export | A different COA requires an approved mapping before review | Complete the dedicated mapping task after the shell is created | Mapping-required flag and source-target COA identities |
| rate_policy_later | Default conversion rate policy | Conditional | Secondary currency differs from primary currency | Blocked for later review, not silently defaulted here | Exact selected currencies and later mapping task | read_source_primary_export | Different currencies require a user-selected rate type | Complete the dedicated mapping task and select an exact rate type | Rate-policy-required flag |

## Required Package Members

| Member | Population Policy |
|---|---|
| GL_LEDGER.csv | Preserve dependency-closure root rows unchanged. |
| ORA_GL_PRIMARY_LEDGER_CONFIG.csv | Preserve the duplicate root alias unchanged. |
| GL_PRIMARY_LEDGER.csv | Add exactly one SECONDARY physical row and keep it semantically identical to the row in GL_SECONDARY_LEDGER.csv. |
| GL_SECONDARY_LEDGER.csv | Add the duplicate SECONDARY physical row; never treat the alias as a different ledger. |
| ORA_GL_JOURNAL_CONFIG_DETAIL.csv | Preserve dependency closure; do not synthesize setup-step or status receipts. |
| ORA_LEGAL_ENTITY_BAL_SEG_VAL_DEF.csv | Preserve dependency closure unchanged. |
| GL_LEDGER_SEG_VAL_ASSIGNMENT.csv | Add rows only for an explicitly supported BSV assignment design; controlled all-values code A creates no assignment row. |
| ORA_GL_LEDGER_RELATIONSHIP.csv | Add one source-primary to target-secondary relationship row in disabled in-process state. |
| ORA_GL_JOUNAL_CONVERSION_RULES.csv | Apply the new-secondary conversion-rule baseline and parent-key contract from ora_defaulting_rules.md for BALANCE, JOURNAL, or SUBLEDGER; preserve existing rules. The product filename spelling is intentional. |
| ORA_PRIMARY_BALANCING_SEGMENT_VALUE_CONVERSION_RULES.csv | Preserve dependency closure; conversion or replication rows belong to the mapping design, not this baseline create. |
| ASM_SETUP_CSV_METADATA.xml | Preserve the export-generated manifest and business-object field contract; never hand-author process identity, status, request, release, or timestamp values. |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Exact authoritative identity and required export evidence agree | Read-only lookup only |
| Lookup | Alternate business key is present and one documented resolver can run | Read-only lookup only |
| Deferred mapping | Current shell is safe but different COA or currency requires the later mapping task | No create here; record the dependency |
| Blocked | Required evidence is missing, ambiguous, unauthorized, stale, cross-environment, or incompatible | No |
| Create with Approval | Never used by this resource for prerequisites | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MSL-030-RESOLVE-DEPENDENCIES | decision | 30 | resolve_dependency | ready->MSL-040-APPLY-DEFAULTS;blocked->MSL-070-HANDLE-ERROR | MSL-020-RESOLVE-REFERENCES | stop | Always |
