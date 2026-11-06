# Manage Reporting Currencies Dependency Readiness

Dependencies must be resolved in order because every package row is anchored to the exact source ledger, source configuration graph, and current environment template. A valid name match alone does not prove import readiness.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Project and environment identity | Select the FDOS project and exact nonproduction Fusion environment; record release and task identity without storing credentials. |
| 2 | Source ledger REST gate | Resolve the exact source and its owning primary through resolve_source_ledger before export; retain separate source and primary identities and use only the owning-primary numeric LedgerId for PRIMARY_LEDGER_ID. |
| 3 | Scoped export acquisition | After the REST gate passes, use core.fusion-api.rest-api-client for exactly one GL_MANAGE_REPORTING_CURRENCIES create request. Serialize the root keys in this exact order: TaskCode, SetupTaskCSVExportCriteria, SetupTaskCSVExportProcess. Keep the criteria and process arrays as root siblings, set PRIMARY_LEDGER_ID to the validated primary-root LedgerId, and give only the returned ProcessId to shared.setup-export.fsm-csv-export for polling and download. |
| 4 | Current task package proof | Require the returned package metadata to declare GL_MANAGE_REPORTING_CURRENCIES and the exact numeric PRIMARY_LEDGER_ID scope; preserve its exact members, headers, source root, and metadata XML. |
| 5 | Source physical template | For Journal or Subledger, prove the exact source row exists and agrees in both physical aliases; extract FirstLedgerPeriodName, PeriodSetName, and AccountedPeriodType from that row. |
| 6 | First opened period | For Journal or Subledger, query the complete accountingPeriodsLOV scope with PeriodSetNameId equal to exported PeriodSetName and PeriodType equal to exported AccountedPeriodType, then validate the exported FirstLedgerPeriodName as one non-adjustment PeriodNameId match. |
| 7 | Level readiness | Prove Balance, Journal, or Subledger eligibility; Subledger requires a method-ready primary source. |
| 8 | Other reference data | Resolve currency, applicable rate types, account, and any requested journal source and category. |
| 9 | Design atomicity | Complete missing-rate, initialization, translation, and rule groups without partial values. |
| 10 | Minimum target graph | Prove exact member, header, row, metadata, generated-value, and header-only expectations before packaging. |
| 11 | Import workflow | Route the immutable candidate to core.data-loader; its own preview and approval workflow is authoritative. |
| 12 | Post-import evidence | Obtain and compare a same-task, same-primary-ledger-scope re-export and the final process diagnostics. |

The create request body must have this exact nesting and wire-level root-key order. `TaskCode` must be serialized first, `SetupTaskCSVExportCriteria` second, and `SetupTaskCSVExportProcess` third. The criteria and process arrays are siblings at the request root. Substitute only the validated numeric primary-root LedgerId as the string value of `AttributeValue`:

```json
{
  "TaskCode": "GL_MANAGE_REPORTING_CURRENCIES",
  "SetupTaskCSVExportCriteria": [{"TaskCode": "GL_MANAGE_REPORTING_CURRENCIES", "BusinessObjectCode": "GL_PRIMARY_LEDGER", "AttributeSet": "Set1", "AttributeName": "PRIMARY_LEDGER_ID", "AttributeValue": "<resolved LedgerId>"}],
  "SetupTaskCSVExportProcess": [{"TaskCode": "GL_MANAGE_REPORTING_CURRENCIES"}]
}
```

Before POST, inspect the serialized request and require the exact root-key sequence shown above. The generic REST client preserves caller insertion order for both `--body` and `--body-file`; therefore construct the object or JSON file in that sequence and do not apply generic key sorting or any transformation that moves the process array ahead of the criteria array. Fusion has been observed to treat this endpoint as order-sensitive: a process-first request can start a broad export before the criterion is applied and return only `ORA_GL_PRIMARY_LEDGER_CONFIG.csv`, `GL_PRIMARY_LEDGER.csv`, and `ASM_SETUP_CSV_METADATA.xml`. That three-member result is invalid evidence for this task even if the POST and process report success.

Submit the validated criteria-first body once through `core.fusion-api.rest-api-client`. Never nest the criteria inside the process row, serialize `SetupTaskCSVExportProcess` before `SetupTaskCSVExportCriteria`, use the ledger name as `AttributeValue`, call an unscoped exporter, or issue another create request while the returned process outcome is known or reconcilable. Pass only the returned `ProcessId` to `shared.setup-export.fsm-csv-export` for polling and download. A process-first request or three-member broad result must be reconciled and requires explicit approval before any fresh POST; it must never be reused as the scoped template.

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| MRC-DEP-01 | Exact project and target environment identity | Yes | Always | Verify | Active project context and routed environment selection |  | Prevents cross-environment templates and accidental external effects | Select the project, environment name, release, and intended primary-ledger scope | ProjectId, Environment, FusionRelease |
| MRC-DEP-03 | Source ledger identity and category | Yes | Always | Lookup | Exact user source name and optional ID through ledgersLOV, reconciled to the returned scoped export | resolve_source_ledger | Every alias must distinguish the actual source from its owning primary; the owning-primary LedgerId supplies the export scope for either source category | Provide the exact source ledger; use a primary for Subledger. For a secondary source with no authoritative parent evidence, provide its owning primary name | SourceLedgerName, SourceLedgerId, SourceLedgerCategory, SourcePrimaryLedgerName, SourcePrimaryLedgerId, ExportPrimaryLedgerId |
| MRC-DEP-02 | Fresh exact-primary-root-scoped task export | Yes | After the source ledger REST gate and exact primary-root identity are satisfied | Acquire and verify | One criteria-first GL_MANAGE_REPORTING_CURRENCIES create request through core.fusion-api.rest-api-client, followed by shared.setup-export.fsm-csv-export polling and download using only the returned ProcessId | inspect_scoped_reporting_currency_export | Supplies authoritative package members, exact headers, source roots, metadata, calendar tuple, and current FirstLedgerPeriodName | Use the exact body above and verify the serialized root-key sequence TaskCode, SetupTaskCSVExportCriteria, SetupTaskCSVExportProcess before POST; keep GL_PRIMARY_LEDGER, Set1, PRIMARY_LEDGER_ID, and the validated numeric primary-root LedgerId unchanged | ProcessId, SerializedRootKeyOrder, SourcePackage, PackageChecksum, MetadataChecksum, exact task and scope receipt |
| MRC-DEP-04 | Source COA and calendar tuple | Yes | Always | Verify | Exact resolved source and exported physical row | read_source_physical_template | Periods, accounts, multiline segments, and target structure inherit from the source | Resolve any conflict before authoring | ChartOfAccountsId, PeriodSetName, AccountedPeriodType, CalendarName |
| MRC-DEP-05 | Source physical row parity | Yes | Journal or Subledger | Verify | GL_PRIMARY_LEDGER.csv and GL_SECONDARY_LEDGER.csv source rows | read_source_physical_template | Both aliases must receive an identical physical target graph | Re-export if either alias is absent or differs semantically | SourcePrimaryAliasRow, SourceSecondaryAliasRow |
| MRC-DEP-06 | Subledger accounting-method readiness | Yes | Subledger | Verify | Source category and exact SLA method tuple | verify_subledger_source_readiness | A secondary source or incomplete accounting method cannot support the baseline Subledger design | Choose a method-ready primary source or treat the request as out-of-baseline | SubledgerSourceReady, SlaAccountingMethodCode, SlaAccountingMethodType, SlaDescriptionLanguage |
| MRC-DEP-07 | Target currency | Yes | Always | Lookup | User CurrencyCode and currency catalog | resolve_monetary_currency | Prevents disabled, nonmonetary, or mistyped currencies | Provide the exact enabled currency code and confirm same-currency intent when applicable | CurrencyCode |
| MRC-DEP-08 | Balance rate and rule tuple | Yes | Balance | Lookup | User rate-type names and independent translation-rule choices | resolve_conversion_rate_type | All four values are UI-required and drive relationship fields | Provide or confirm average and end rate types plus both PTD or YTD choices | AlcPeriodAverageRateTypeTrans, AlcPeriodEndRateTypeTrans, RevExpXlationRuleCode, OwnerEquityXlationRuleCode |
| MRC-DEP-09 | Journal or Subledger default rate type | Yes | Journal or Subledger | Lookup | User rate-type name | resolve_conversion_rate_type | Required conversion behavior cannot be inferred from a display default | Provide or confirm one exact enabled rate type | AlcDefaultConvRateTypeTrans |
| MRC-DEP-10 | Derived first opened period | Yes | Journal or Subledger | Lookup | FirstLedgerPeriodName, PeriodSetName, and AccountedPeriodType from the exact scoped source physical row, validated against the complete matching accountingPeriodsLOV scope | resolve_first_opened_period | Determines the physical target FirstLedgerPeriodName without making a derivable UI field mandatory user intake; LOV membership alone must not replace the exported source authority | No period input is required for the baseline; review the derived period and evidence in preview. A different supplied period needs authoritative same-release eligibility evidence. | FirstLedgerPeriodName, FirstOpenedPeriodStartDate, FirstOpenedPeriodEndDate, FirstOpenedPeriodEvidence |
| MRC-DEP-11 | Rounding account | Yes | Journal or Subledger | Verify | Exact inherited source physical row or an explicit user override | resolve_rounding_account | The optional UI field must still be structurally valid when inherited or changed | Accept the validated inherited candidate or provide an exact enabled detail-postable override | RoundingCcidSegments |
| MRC-DEP-12 | Missing-rate policy | Yes | Always | Verify | Disclosed REPORT_ERROR baseline or explicit user override |  | FIND_RATE and REPORT_ERROR require mutually exclusive day handling | Accept REPORT_ERROR or choose FIND_RATE and supply 1 through 999 days | AlcNoRateActionCode, AlcMaxDaysRollRate |
| MRC-DEP-13 | Non-EMU initialization group | Yes | InitializeConversion is Yes | Lookup | User intent, source calendar, eligible period, rate type | resolve_balance_initialization_period | Initialization is atomic and uses eligibility distinct from FirstOpenedPeriod | Supply the eligible period and rate type; accept or override the disclosed rate date | AlcInitConvOptionCode, AlcInitPeriod, AlcInitDate, AlcInitializingRateDate, AlcInitializingRateTypeTrans |
| MRC-DEP-14 | Journal conversion rule catalog | Yes | Always | Lookup | Explicit baseline confirmation or selective design | resolve_journal_category | The current package emits target rules even for the proven Balance create, and rules must not come from unexported display state | Confirm Other and Other and Y and Y or supply exact selective rows | JournalRules |
| MRC-DEP-15 | Source COA qualifier mapping | Yes | Journal or Subledger | Verify | Source export and authoritative COA qualifier evidence | derive_source_coa_qualifiers | Segment column names cannot be ordinal guesses | Confirm the balancing and management qualifier mapping | BalSegValueOptionCode, BalSegColumnName, MgtSegValueOptionCode, MgtSegColumnName |
| MRC-DEP-16 | Exact minimum graph and serialization | Yes | Always | Verify | Candidate package and current template | verify_authored_package_shape | Prevents unresolved relationship ledger references, incorrect source/primary joins, unrelated authored rows, and malformed CSV | Review all member row counts, headers, blanks, and semantic additions | CandidatePackageChecksum, MemberRowCounts, ShapeValidation |
| MRC-DEP-17 | Data-loader approval and process controls | Yes | A live import is requested | Blocked until routed | Immutable reviewed package and core.data-loader workflow |  | Import side effects need the authoritative single approval workflow | Use core.data-loader preview and approval; do not request duplicate approval in this resource | ApprovalRecord, ProcessId |
| MRC-DEP-18 | Same-scope re-export verification | Yes | Import process completed | Verify | Approved package, process output, same-scope re-export | verify_same_scope_reexport | Process submission or success alone does not prove the exact configuration delta | Re-export the same task and primary-ledger scope and compare the new graph | VerificationResult, GeneratedPhysicalShortName, GeneratedRelationshipShortName |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Exact authoritative identity and same-release evidence agree | Read-only downstream lookups may run; no external mutation from this resource |
| Lookup | A complete supported business key exists and the active workflow permits its documented read-only resolver | Read-only lookup only |
| Acquire and verify | Exact ledger and primary-root scope passed the REST gate and the user approved the one immutable export request | Create one export process through core.fusion-api.rest-api-client with the exact serialized root-key order TaskCode, SetupTaskCSVExportCriteria, SetupTaskCSVExportProcess; use only its ProcessId with shared.setup-export.fsm-csv-export, then verify the returned task, numeric scope, eleven members, roots, and metadata |
| Verify | Local package or project evidence must be reconciled before the next node | Local validation only |
| Out-of-baseline | EMU fixed-rate initialization, custom sequencing, partial account-filter initialization, or nonbaseline selective source/category design is requested | No baseline create; require explicit intent and same-release evidence before a separate supported design path |
| Blocked | Required evidence is missing, ambiguous, unauthorized, stale, cross-environment, incompatible, or has failed validation | No |
| Import with Approval | The immutable package passed this resource and core.data-loader has reached its approval gate | Only core.data-loader may import; its approval workflow is authoritative |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MRC-030-RESOLVE-DEPENDENCIES | decision | 30 | resolve_dependency | ready->MRC-040-APPLY-DEFAULTS;blocked->MRC-070-HANDLE-ERROR | MRC-020-RESOLVE-REFERENCES | stop | Always |
