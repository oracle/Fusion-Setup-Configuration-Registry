# Manage Reporting Currencies Design Enforcement

The gate enforces one closed non-EMU create baseline for Balance, Journal, or Subledger. There is no open functional TBD in that supported baseline. Pending execution or verification evidence is an operational state, not a missing functional rule.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Confirm business intent | Show source, target name, level, currency, behavior flags, rules, advisories, initialization intent, and explicit user confirmations. |
| 2 | Resolve ledger REST identity | Resolve the actual source and its owning primary separately through resolve_source_ledger; retain the owning-primary numeric LedgerId for PRIMARY_LEDGER_ID scope. |
| 3 | Acquire exact scoped export | Serialize the approved GL_MANAGE_REPORTING_CURRENCIES request root in the exact order TaskCode, SetupTaskCSVExportCriteria, SetupTaskCSVExportProcess; verify that order before submitting once through core.fusion-api.rest-api-client, then poll and download only by its ProcessId through shared.setup-export.fsm-csv-export. |
| 4 | Freeze scoped template | Require exact task and numeric PRIMARY_LEDGER_ID metadata scope, then preserve the eleven-member contract, exact headers, exact source roots, and metadata XML from the returned current-environment package. |
| 5 | Confirm level semantics | Balance is relationship-only; Journal and Subledger have one physical ALC target in both aliases; Subledger uses a method-ready primary source. |
| 6 | Resolve references and derived period | Every former UI LOV has one exact eligible match or authoritative same-release scoped evidence; Journal and Subledger derive FirstLedgerPeriodName from the scoped source row and validate it against the complete exact accounting-period scope. |
| 7 | Build minimum graph | Keep only required source-root context and add only the one new target graph. |
| 8 | Enforce population allowlists | Apply exact user values, documented derivations, explicit constants, inherited source values, and intentional blanks by header name. |
| 9 | Validate identifiers and rules | Leave both independent short names for service generation and emit only explicitly supported journal rules. |
| 10 | Validate package shape | Reopen CSV, verify widths and multiline values, compare metadata bytes, calculate hashes, and produce a semantic diff. |
| 11 | Apply safety boundary | Exclude review/submit, period opening, disable, deletion, and every other lifecycle operation. |
| 12 | Handoff and verify | Let core.data-loader own preview and approval; after process completion require a same-scope re-export comparison. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Any create | Error | resolve_source_ledger | Source is missing, ambiguous, outside scoped export, or category-ineligible | Select exactly one supported source and re-export its primary-ledger scope | No automatic fix |
| Primary-source scoped export acquisition | Error | inspect_scoped_reporting_currency_export | The create was submitted before exact ledger resolution; serialized root keys are not exactly TaskCode, SetupTaskCSVExportCriteria, SetupTaskCSVExportProcess in that order; root TaskCode or either child TaskCode is not GL_MANAGE_REPORTING_CURRENCIES; criteria and process are not sibling root arrays; criterion is not GL_PRIMARY_LEDGER, Set1, PRIMARY_LEDGER_ID, and the validated numeric LedgerId; ledger Name was used as AttributeValue; more than one create was submitted; or polling did not use only the returned ProcessId | Stop before POST when the serialization is wrong. If a process-first POST already occurred, reconcile its ProcessId and require explicit approval before one fresh criteria-first request through the declared route | Only through the declared export route and its approval gate |
| Returned scoped package | Error | inspect_scoped_reporting_currency_export | Metadata task is not GL_MANAGE_REPORTING_CURRENCIES, numeric PRIMARY_LEDGER_ID scope differs from the approved request, either root member does not contain exactly the selected source root, the eleven-member contract is incomplete, or the package has the observed process-first broad signature containing only ORA_GL_PRIMARY_LEDGER_CONFIG.csv, GL_PRIMARY_LEDGER.csv, and ASM_SETUP_CSV_METADATA.xml | Stop, quarantine the package, and reconcile the create request and ProcessId; never relabel or splice package evidence, and obtain explicit approval before a fresh criteria-first POST | No guessed fix |
| Subledger | Error | verify_subledger_source_readiness | Source is secondary or method readiness is absent or contradictory | Use a method-ready primary source | No automatic fix |
| Any create | Error | check_reporting_currency_name_availability | Name is blank, over 30 characters, or collides in the wider namespace | Supply a new exact name | No automatic fix |
| Target currency equals source currency | Warning | resolve_monetary_currency | User has not acknowledged the limited business value | Confirm the same-currency representation is intentional | User confirmation only |
| Journal or Subledger is selected | Warning |  | The need for converted journal or full subledger detail has not been stated | Prefer Balance for translated financial statements without detailed alternate-currency journals; confirm the added processing, reconciliation, and period-ordering cost | User confirmation only |
| Balance | Error | derive_minimum_target_graph | Either physical alias contains a new ALC target row | Remove both target rows; Balance is relationship-only | Yes before package freeze |
| Journal or Subledger | Error | read_source_physical_template | Either physical alias lacks the one new target, contains multiple targets, or differs semantically | Rebuild both target rows from the same exact source map | Yes before package freeze |
| Any create | Error | derive_minimum_target_graph | Either root member lacks its one owning-primary root, or either physical alias lacks the required primary or actual source context | Retain the owning-primary root and both required physical identities, once when source equals primary | Yes before package freeze |
| Any create | Error | derive_minimum_target_graph | Relationship count is not one; any of Name, Name1, Name2, Name3 is blank, unresolved, or mapped to the wrong role; or any rule-parent key differs | Apply the Relationship Row Population Contract and resolve every ledger reference before import | Yes before package freeze |
| Any create | Error | inspect_scoped_reporting_currency_export | Package member, header, order, width, or metadata differs from the current scoped template | Obtain or restore exact current package evidence | No guessed fix |
| FIND_RATE | Error |  | AlcMaxDaysRollRate is absent or is not an integer from 1 through 999 | Request an explicit valid day count | No automatic default |
| REPORT_ERROR | Error |  | AlcMaxDaysRollRate is nonblank | Clear the field and show the correction | Yes before package freeze |
| Initialization is enabled | Error | resolve_balance_initialization_period | Any atomic member is missing, period is ineligible, AlcInitDate is not period start, rate date is invalid, or rate type is unresolved | Complete the non-EMU atomic group from exact period evidence | Only deterministic date derivation |
| Initialization is disabled | Error |  | Any initialization field is nonblank | Clear the entire group | Yes before package freeze |
| Journal or Subledger | Error | resolve_first_opened_period | FirstLedgerPeriodName was requested as mandatory user intake, guessed, chosen from response order, copied from another ledger, left blank, or populated without one exact non-adjustment PeriodNameId match in the exported PeriodSetName and AccountedPeriodType scope | Derive it from the exact scoped source physical row, validate it through the complete accountingPeriodsLOV result, and show the evidence in preview | Deterministic derivation only |
| Derived FirstLedgerPeriodName or a supplied FirstOpenedPeriod is used as initialization evidence | Error | resolve_first_opened_period | The distinct balance-initialization predicate was not evaluated | Resolve each period under its own eligibility predicate | No automatic substitution |
| Current Balance, Journal, or Subledger baseline rules | Error | resolve_journal_category | The Other and Other and Y and Y row is absent, duplicated, unconfirmed, or joined to the wrong parent | Emit one exact confirmed baseline row | Yes before package freeze |
| Broad Other and Other and Y and Y policy | Warning | resolve_journal_category | The user has not accepted conversion of every unmatched GL journal | Explain the catch-all effect and require an explicit design decision | User confirmation only |
| Any rule set | Error | resolve_journal_category | Closing Journal and Other and N was authored only because the UI displayed it | Remove it; require an emitted same-release row before authoring | Yes before package freeze |
| Selective rule design | Error | resolve_journal_source | User intent, exact keys, include flags, or same-release evidence is incomplete | Treat as out-of-baseline until every row is explicitly designed and resolved | No inferred fix |
| Physical segment fields | Error | derive_source_coa_qualifiers | SEGMENT columns were guessed by ordinal or conflict with source qualifiers | Derive them from the exact source COA qualifier evidence | Yes only from authoritative evidence |
| BingoOps physical target | Error | derive_source_coa_qualifiers | Balancing tuple is not A and SEGMENT1 or management tuple is not A and SEGMENT2 | Restore the exact proven source tuples | Yes from exact evidence |
| BalSegValueOptionCode is A | Error | derive_minimum_target_graph | GL_LEDGER_SEG_VAL_ASSIGNMENT.csv contains a data row | Keep the member header-only | Yes before package freeze |
| Generated identifiers | Error |  | Physical ShortName or relationship TargetLedgerShortName is fabricated, copied, equalized, or interchanged | Leave each create field blank and verify both returned values independently | Yes before package freeze |
| Existing source role | Error | inspect_scoped_reporting_currency_export | A Journal or Subledger target requires a source-role transition but AlcLedgerTypeCode was left NONE or blank, or any source field other than the proven role transition changed | Preserve SOURCE when present; otherwise preview only the exact NONE or blank to SOURCE change proved for the same release | Yes only from authoritative evidence |
| New-row audit or process fields | Error |  | A source or historical identity was copied into a new row | Clear the new-row service-owned fields | Yes before package freeze |
| EMU fixed-rate initialization | Error |  | Baseline authoring is attempted without explicit intent and same-release evidence | Stop and create a separately reviewed out-of-baseline design | No baseline fix |
| Custom sequencing | Error |  | Sequence fields are inferred from source or display defaults | Stop until exact user intent and same-release field behavior are proved | No baseline fix |
| Partial account-filter initialization | Error |  | Assignment or BSV conversion rows are invented without exact scope and evidence | Stop; baseline remains all-values with header-only members | No baseline fix |
| Lifecycle operation | Error |  | Package or plan attempts Review and Submit, period opening, conversion disablement, deletion, or another lifecycle mutation | Remove the operation and route it as a separately authorized workflow if supported | No action in this task |
| Package preview | Error | verify_authored_package_shape | Hash, row counts, exact headers, semantic diff, intended blanks, or exclusion statement is absent | Regenerate the preview before approval handoff | Yes locally |
| Post-import verification | Error | verify_same_scope_reexport | Process submission or status is treated as configuration proof without same-scope re-export | Re-export and compare the exact target graph | No inferred success |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_source_ledger | Every create | Canonical source identity, category, currency, COA, calendar, method facts | ora_reference_lookups.md |
| check_reporting_currency_name_availability | Every create | Name availability and collision evidence | ora_reference_lookups.md |
| inspect_scoped_reporting_currency_export | Every create | Exact package contract, roots, headers, metadata XML | ora_reference_lookups.md |
| read_source_physical_template | Journal or Subledger | Exact 133-column source maps in both aliases | ora_reference_lookups.md |
| verify_subledger_source_readiness | Subledger | Primary category and exact method-ready tuple | ora_reference_lookups.md |
| resolve_monetary_currency | Every create | Eligible monetary currency | ora_reference_lookups.md |
| resolve_conversion_rate_type | Each applicable rate field | Exact active rate-type values | ora_reference_lookups.md |
| resolve_first_opened_period | Journal or Subledger | Exported FirstLedgerPeriodName, PeriodSetName, and AccountedPeriodType plus one exact non-adjustment accountingPeriodsLOV match and dates | ora_reference_lookups.md |
| resolve_balance_initialization_period | Initialization enabled | Initialization period and deterministic dates under its distinct predicate | ora_reference_lookups.md |
| resolve_rounding_account | Journal or Subledger | Exact valid source-COA account | ora_reference_lookups.md |
| resolve_journal_source | Selective rule requested | Exact source keys and names | ora_reference_lookups.md |
| resolve_journal_category | Any rule is authored | Exact category keys and names; baseline Other evidence | ora_reference_lookups.md |
| derive_source_coa_qualifiers | Physical target required | Exact balancing and management segment columns | ora_reference_lookups.md |
| derive_minimum_target_graph | Every create | Exact kept, added, removed, and header-only member rows | ora_reference_lookups.md |
| verify_authored_package_shape | Candidate built | Serialization, member, header, width, checksum, and metadata results | ora_reference_lookups.md |
| verify_same_scope_reexport | Import completed | Expected target graph, generated identifiers, and unexpected deltas | ora_reference_lookups.md |

## Package Preview Contract

| Preview Section | Must Show |
|---|---|
| Target | Environment, Fusion release, task code GL_MANAGE_REPORTING_CURRENCIES, primary-ledger scope, source ledger, target name, level, and currency. |
| User intent | Required user fields, explicit confirmations, optional selections, derived First Opened Period when applicable, same-currency warning when applicable, and all out-of-baseline exclusions. |
| Source evidence | Ledger resolver identity, approved exact scoped-export request tuple, serialized root-key order TaskCode then SetupTaskCSVExportCriteria then SetupTaskCSVExportProcess, ProcessId, scoped export identity and checksum, exact task and numeric scope metadata, metadata checksum, exact eleven-member set, source physical parity result, and First Opened Period LOV evidence when applicable. |
| Row impact | Before and candidate data-row counts for all ten CSV members, with the exact kept source roots and exact new target keys. |
| Field impact | Every transformed relationship, physical, and rule field; all four resolved relationship ledger aliases and repeated rule parents; inherited families including the actual source accounting-method tuple; derived values; intentional blanks; independent generated identifiers. |
| Safety | No unrelated existing rows authored and no lifecycle action. Disclose that importing source context can invoke Oracle option propagation to existing Journal/Subledger RCs; preserve a before snapshot and report every resulting delta. |
| Artifact | Immutable candidate ZIP checksum and a machine-readable errors array, even when empty. |

## Out-of-Baseline Branches

| Branch | Required User Intent | Same-Release Evidence Required | Baseline Behavior |
|---|---|---|---|
| EMU fixed-rate initialization | Exact fixed-rate relationship intent and affected currencies | Current task UI and exported relationship proving applicability, option code, and which rate fields Oracle suppresses; do not infer EMU from currency names | Stop. Oracle guidance indicates only Period may apply and code D can suppress initializing rate date and type, but author nothing until the exact branch is proved. |
| Custom sequencing | Exact desired sequencing policy and business reason | Current exported physical fields and UI mapping for every sequencing field | Keep no sequencing and stop before any custom field is authored. |
| Partial account-filter initialization | Exact balancing-segment scope, inclusion policy, and initialization intent | Current rows and headers for GL_LEDGER_SEG_VAL_ASSIGNMENT.csv and ORA_PRIMARY_BALANCING_SEGMENT_VALUE_CONVERSION_RULES.csv plus source qualifier evidence | Keep BalSegValueOptionCode A and both members header-only. |
| Selective journal-source/category conversion | Exact broad-include or selective-include strategy and every source, category, IncludeFlag, and UserUpdatableFlag | Exact current UI or export key/display pairs and relationship-parent contract; Manual and Adjustment and N is only a proven example | Emit only the confirmed Other and Other and Y and Y baseline until the separate design is complete. |

## Same-Scope Re-export Acceptance

| Check | Acceptance Rule |
|---|---|
| Target identity | Exactly one new relationship matches the actual source, owning primary, target name, level, currency, and all four resolved ledger aliases. |
| Balance shape | No new physical ALC row exists in either alias. |
| Journal or Subledger shape | Exactly one matching physical ALC and TARGET row exists in both aliases; the alias rows are semantically equal and preserve the actual source accounting-method code, type, and language. |
| Generated short names | Physical ShortName and relationship TargetLedgerShortName are captured separately and never required to be equal. |
| Rate policy | Missing-rate action, max days, rate types, translation rules, and initialization values equal the approved preview. |
| Source role | AlcLedgerTypeCode remains SOURCE or shows only the approved transition from NONE or blank to SOURCE when the physical target was created. |
| Rules | Only approved target rule rows exist, with exact relationship-parent keys; no display-only Closing Journal row appeared through authoring. |
| Scope integrity | Compare every existing row within the scope. Report source-option propagation separately, including its exact before/after values and evidence; unexplained or unapproved deltas keep verification unresolved. |
| Evidence | Process status and log, approved package checksum, re-export checksum, semantic diff, and validation result are persisted under the project workflow. |

## Functional Closure Register

| Branch | Status | Enforcement |
|---|---|---|
| Supported non-EMU Balance, Journal, and Subledger baseline | Closed; no functional TBD | Execute the rules in this resource. |
| FIND_RATE max-day handling | Closed | Explicit integer 1 through 999. |
| REPORT_ERROR max-day handling | Closed | Blank. |
| Non-EMU initialization | Closed | Atomic I plus eligible period, period start, prior-period-end default rate date, and required rate type. |
| First Opened versus Balance Initialization Period | Closed | Derive FirstLedgerPeriodName from the exact scoped source row, validate it against the complete exact accounting-period scope, and apply the separate initialization-period predicate only when initialization is enabled. |
| Current default journal rule | Closed | Other and Other and Y and Y only. |
| UI Closing Journal line | Closed for baseline | Do not author without emitted same-release evidence. |
| Independent short names | Closed | Leave blank on create and verify independently. |
| BingoOps segment qualifier values | Closed | A and SEGMENT1; A and SEGMENT2; no BSV assignment row. |
| EMU, custom sequencing, partial account filter, nonbaseline selective rules | Explicit out-of-baseline branches | Require user intent and same-release evidence; never invent defaults. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MRC-050-ENFORCE-DESIGN | decision | 50 | design_enforcement | ready->MRC-060-EXECUTION-GATE;blocked->MRC-070-HANDLE-ERROR | MRC-040-APPLY-DEFAULTS | stop | Always |
