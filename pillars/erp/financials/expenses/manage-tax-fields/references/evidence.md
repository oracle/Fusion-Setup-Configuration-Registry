# Reviewed evidence

## Contract follow-up — 2026-10-05

### DOC-REST-BU

[Oracle Financials 26C: Get all business units](https://docs.oracle.com/en/cloud/saas/financials/26c/farfa/op-finbusinessunitslov-get.html) documents finBusinessUnitsLOV, queryable BusinessUnitName and response BusinessUnitId/BusinessUnitName/ActiveFlag. This supports an exact-name, active-BU preflight contract. It does not prove privileges, availability or enterprise equivalence on the target; the returned ID must not replace FSM's own enterprise-scoped name resolution.

### DOC-REST-TERRITORY

[Oracle Common Features 26C: Get all territories](https://docs.oracle.com/en/cloud/saas/applications-common/26c/farca/op-servername-fscmrestapi-resources-11.13.18.05-territorieslov-get.html) documents territoriesLOV and PrimaryKey finder with TerritoryCode. This supplies the country existence request contract. Literal OTHER remains the source-established exception, not an ISO territory lookup.

### SRC-CS-LOOKUP-PVO

`fusionapps/fin/components/payables/exm/lookups/pubicView/src/oracle/apps/financials/expenses/lookups/publicView/ExmLookupPVO.xml` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`), retrieved through authenticated external Chrome on 2026-10-05: lines 7-15 select lookup fields from EXM_LOOKUP_VALUES; ByLookupType and ByLookupCode criteria appear at 62-112, active-date criteria at 113-165, enabled criterion begins at 166. Do not substitute standardLookups solely because its attribute names resemble this view; equivalence still needs verification.

### SRC-CS-LOOKUP-VIEW

`fusionapps/fin/components/payables/exm/shared/lookups/dbSchema/database/fusionDB/FUSION/EXM_LOOKUP_VALUES.view` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`), retrieved 2026-10-05: lines 69-88 join FND_LOOKUP_VALUES_B/TL to FND_LOOKUP_TYPES; filter module 47110F64AC0608E2E040449823C60DB6 and view application IDs 0 or 10016. Generic REST lookup equivalence requires checking this context, not only the lookup type text. A standardLookups URI is therefore a discovery candidate, not yet the confirmed task resolver.

### DOC-FSM-PACKAGE

[Oracle FSM: Export and Import CSV File Packages](https://docs.oracle.com/en/cloud/saas/applications-common/26a/oafsm/export-and-import-csv-file-packages.html), latest accessible HTML found for this topic after 26B/26C URLs failed: retain every CSV member; a member without intended data may retain only its header. Preserve exported value formats. These generic rules do not establish how this task processes two members mapped to the same setup-option XML, nor create-time audit serialization.

[Oracle FSM 26C: Compare Task Setup Data](https://docs.oracle.com/en/cloud/saas/applications-common/26c/oafsm/compare-task-setup-data.html) states that CSV import does not delete destination records. This supports distinguishing absence from deletion, but does not establish blank-as-clear semantics.

### Framework source search

Authenticated CodeSearch searches for MigratorHelper.java and then MigratorHelper returned no matching files in FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64 on 2026-10-05 (index 2026-10-05). The collected task services delegate key reconciliation and XML reading to that helper. Its create/audit handling remains unverified; missing source is not evidence of a default.

Source branch: FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64, indexed 2026-10-02. Source behavior is not proof of successful import on another build. No setup mutation or import test was performed during that source-review phase; subsequent execution coverage is summarized below.

## SRC-CS-TASK

`fusionapps/fin/fun/db/data/FinFunShared/SetupTaskSD.xml#11469` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`)

Task EXM_MANAGE_TAX_FIELDS is enabled, named Manage Tax Fields, and routes to /WEB-INF/oracle/apps/financials/expenses/policy/taxfields/ui/flow/FinExmPolicyTaxFieldsMaster.xml#FinExmPolicyTaxFieldsMaster. Lines 11469-11488.

## SRC-CS-TASK-BO

`fusionapps/fin/fun/db/data/FinFunShared/SetupTaskBusinessObjectSD.xml#2729` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`)

Lines 2729-2743: task owns enabled EXM_SETUP_OPTION and EXM_VAT_FIELD mappings, each ImportSequence 0. Extra cash advance CSV membership still requires explanation.

## SRC-CS-UI-AM

`fusionapps/fin/components/payables/exm/policy/taxfields/model/src/oracle/apps/financials/expenses/policy/taxfields/uiModel/applicationModule/FinExmPolicyTaxFieldsAMImpl.java` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`)

Lines 84-109: doEnableTax creates or updates setup option using ENABLE_TAX constant and Y/N. Lines 225-235 create country row. Lines 259-284 create missing OTHER row on BU navigation. Lines 306-329 behavior lookup EXM_FIELD_BEHAVIOUR. UI behavior only; do not infer import defaults.

## SRC-CS-UI-AM-XML

`fusionapps/fin/components/payables/exm/policy/taxfields/model/src/oracle/apps/financials/expenses/policy/taxfields/uiModel/applicationModule/FinExmPolicyTaxFieldsAM.xml` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`)

Lines 17-40 bind VatFieldsVO, VatFieldsOtherVO, SetupOptionsVO, BehaviorsVO, BusinessUnitVO, TaxFieldsVO, TerritoryLOVVO. Lines 41-52 BU view links.

## SRC-CS-UI-VO

`fusionapps/fin/components/payables/exm/policy/taxfields/model/src/oracle/apps/financials/expenses/policy/taxfields/uiModel/view/VatFieldsVO.xml` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`)

EXM_VAT_FIELDS joined to FND_TERRITORIES_VL. Lines 111-112 shared VatFieldEO and read-only TerritoryPEO. UI defaults lines 126-167: ENABLED for merchant name and tax classification, DISABLED for other four. Not import-default evidence.

## SRC-CS-EO

`fusionapps/fin/components/payables/exm/policy/shared/model/src/oracle/apps/financials/expenses/policy/shared/model/entity/VatFieldEO.xml` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`)

Lines 23-30 EXM_VAT_FIELDS and VatFieldEOImpl. BU validation uses active BusinessUnitPVO; behavior resolver EXM_FIELD_BEHAVIOUR enabled Y. Territory validated except literal OTHER. Six controls validate DISABLED, ENABLED, REQUIRED. EnabledFlag validates Y/N. Primary key VatSetupId; unique alternate key OrgId+TerritoryCode at lines 562-593. Audit fields have history metadata.

## SRC-CS-FSM-AM

`fusionapps/fin/components/payables/exm/policy/shared/model/src/oracle/apps/financials/expenses/policy/shared/expenseVatFieldService/applicationModule/ExpenseVatFieldServiceAMImpl.java` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`)

Export excludes VatSetupId, OrgId, BusinessUnitId, ObjectVersionNumber (78-81). Import resolves BuName with tenant enterprise ID through BusinessUnitP/BuAltKeyByName (120-164), writes OrgId when found, updates PK using AltKey (168-171), then readXML (175-177). Exceptions become processing errors (183-188). Missing/multiple resolution semantics require helper review; do not assert successful import behavior.

## SRC-CS-FSM-VO

`fusionapps/fin/components/payables/exm/policy/shared/model/src/oracle/apps/financials/expenses/policy/shared/expenseVatFieldService/view/VatFieldVO.xml` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`)

FSM view joins EXM_VAT_FIELDS to FUN_ORGANIZATIONS_V and reuses VatFieldEO. AltKey maps VatFieldEOAltKey (lines 180-186). Six controls and EnabledFlag have no explicit DefaultValue. Audit attributes IsUpdateable=false. Shared framework behavior still requires validation; do not infer omitted-field behavior.

## SRC-CS-EO-IMPL

`fusionapps/fin/components/payables/exm/policy/shared/model/src/oracle/apps/financials/expenses/policy/shared/model/entity/VatFieldEOImpl.java` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`)

Entity class extends OAEntityImpl; inspected generated getters/setters and complete source; no local create override or explicit business-field default assignment. This does not establish base-class defaults.

## SRC-CS-CASH-BO

`fusionapps/fin/fun/db/data/FinFunShared/SetupBusinessObjectSD.xml#13711` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`)

Visually verified lines 13711-13735: EXM_CASH_ADV_SETUP_AND_POLICY uses oracle.apps.financials.expenses.setup.shared.expenseSetupOptionService.ExpenseSetupOptionService, XmlFileName EXM_SETUP_OPTION.xml, XmlNodePath /SetupOptionVO/SetupOptionVORow. MigrationModeFlag Y. This proves shared service/XML routing, not permission to change cash-advance options.

## SRC-CS-SETUP-FSM-AM

`fusionapps/fin/components/payables/exm/setup/shared/model/src/oracle/apps/financials/expenses/setup/shared/expenseSetupOptionService/applicationModule/ExpenseSetupOptionServiceAMImpl.java` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`)

Export lines 64-89 filters by FUN_BUSINESS_UNIT, excludes OptionId/OrgId/BusinessUnitId/ObjectVersionNumber and emits EXM_SETUP_OPTION.xml. No task-specific OptionCode filter appears in this method. Import lines 143-177 resolves BuName plus enterprise via BuAltKeyByName, reports BU not found as processing message, maps missing-BU OtherOrgId=-1 to OrgId=-1 and other values to -999, then updates PK by AltKey and invokes readXML. This is shared service behavior, not authorization for global scope or unrelated setup-option changes.

## SRC-CS-TAX-SETUP-VO

`fusionapps/fin/components/payables/exm/policy/taxfields/model/src/oracle/apps/financials/expenses/policy/taxfields/uiModel/view/SetupOptionsVO.xml` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`)

Visually verified lines 28-43: filters ORG_ID=:BindOrgId AND OPTION_CODE=:bindEnableTax; bindEnableTax DefaultValue ENABLE_TAX. Combined with UI AM doEnableTax, task business values are Y/N for ENABLE_TAX.

## SRC-CS-SETUP-EO

`fusionapps/fin/components/payables/exm/setup/shared/model/src/oracle/apps/financials/expenses/setup/shared/model/entity/SetupOptionEO.xml` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`)

Entity OptionCode required, length 30, validated through enabled EXM_SETUP_OPTIONS lookup; ValueCode length 30 with no literal list in this XML. Alternate key OptionCode+OrgId (363-375). Shared entity is broader than tax task. EOImpl and import view remain to review for complete field contracts.

## FSM-EXPORT

Same-task current export and header-only template were completed for EXM_MANAGE_TAX_FIELDS on release 11.13.27.01.0. Package structure and headers agree. Current package SHA256: 468c98ead693f993e88ce1941c8af38f181634bc23eadcb5cf336b440d7f1864. Template SHA256: 2cf184724f49384f901eec7de4c7d9391915a370463226f0a798ccc5a415bc28. Raw data, credentials and environment-specific business values are intentionally excluded.

## FSM-DUPLICATE-CHECK

A direct byte comparison of EXM_SETUP_OPTION.csv and EXM_CASH_ADV_SETUP_AND_POLICY.csv in each collected ZIP returned identical for both current and template exports. This verifies duplicate contents in those exact artifacts; it does not establish whether a future export is identical or authorize removing a member. The shared XML/service mapping is corroborated by SRC-CS-CASH-BO and SRC-CS-SETUP-FSM-AM.


## SRC-CS-BEHAVIOR-BOOTSTRAP (historical corroboration only)

`fusionapps/fin/exm/noship/bootstrap/EXM_SEED_LOOKUP.sql#125` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`)

Visually reviewed lines 125-178 on 2026-10-05. The lookup type uses X_VIEW_APPSNAME=EXM and X_APPLICATION_SHORT_NAME=EXM. Value definitions map REQUIRED to Required, ENABLED to Optional and DISABLED to Hidden, each enabled Y. This file is under noship/bootstrap and last modified in 2009; it is historical corroboration, not proof of current shipped seeds or target configuration. EXM is a candidate application context to investigate for the generic lookup resolver, not an established callable contract.

## SRC-CS-MAPPING-MIGRATION (related implementation only)

`fusionapps/fin/components/ledger/xla/accountingMethodSetup/mappingSets/model/src/oracle/apps/financials/subledgerAccounting/accountingMethodSetup/mappingSetsService/model/applicationModule/MappingSetsServiceAMImpl.java#1698` (reviewed source: `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64`)

Definition search for updatePrimaryKeysInXML found six results in the selected Fusion project. Reviewed this local implementation: lines 1790-1802 convert absent/empty alternate-key values to NullValue; lines 1811-1849 find a row by alternate key, reuse its primary key, or generate a new sequence key if eligible and absent. This is a method on MappingSetsServiceAMImpl, not the MigratorHelper implementation invoked by Expenses. It does not resolve audit-column serialization or CSV-to-XML shared-member behavior and must not be used to close those contracts.

Search limitation: the all-project definition search for MigratorHelper returned HTTP 502. The narrower full-text EXM_FIELD_BEHAVIOUR search succeeded; *seed* path filtering returned two historical noship SQL files. Literal seed path filtering returned no matches, so that result is not evidence of seed absence.


## REPO-AR-ADAPTER-REVIEW

Reviewed origin/lmallick_receivables_system_options at commit f6f74dc3d880b7ef7a00167ac15c68e3a9a06d6a, task folder pillars/erp/financials/receivables/manage-receivables-system-options. The e2e-adapter.json descriptor allows update only and has generation.readiness=blocked. Its runtime emits only requested rows, blanks audit cells, retains all members and uses current baseline metadata. It is a packaging precedent, not successful create evidence or evidence about Expenses' two members sharing one XML mapping. Do not copy its readiness or infer live validation.

## BUILDER-AUDIT-CONTRACT

The previously downloaded deliverable builder assets/fsm_task_adapter.py, SHA256 4921669d4b5f71f53c0084778a2df55c3d5c3a05ff5af9bd14a77b85368acd20, clears each entity audit field at lines 1119-1120 and rejects populated audit cells at 1190-1193. references/fsm-task-adapter-contract-v1.md permits standard Fusion who-column identification. Together with the task's non-updateable audit VO attributes, this establishes the candidate convention: keep headers, emit empty audit cells, retain baseline evidence separately. It does not establish blank business-field semantics or successful target execution.

## BUILDER-FSM-VALIDATION

The same builder contract's Builder readiness rules explicitly permit Confirmed fsm_import_resolved/fsm_import_validated references without a public GET when keys, validation and failure semantics are retained. SRC-CS-EO lines 46-59 binds ExmLookupPVO to EXM_FIELD_BEHAVIOUR and EnabledFlag=Y; each behavior's ListValidationBean validates LookupCode membership and reports FND_CMN_INVALID_ATTRB_API_SRV2. The reviewed import path uses the corresponding entity-backed VO. The resolver is therefore import-time validation; it does not pre-populate target values, select a first match or invent a REST endpoint.


## DOC-CSV-EMPTY-MEMBER

[Oracle: Export and Import CSV File Packages](https://docs.oracle.com/en/cloud/saas/applications-common/26d/oafsm/export-and-import-csv-file-packages.html), Modify Setup Data, verified 2026-10-29 against current 26D documentation. Oracle instructs retaining every CSV member and using a heading-only file when its setup data is not to be included. This general exclusion rule does not establish which alias owns a shared XML node or whether a heading-only alias can mask a populated alias. It cannot qualify the former single-populated-alias Tax strategy.

## TAX-ALIAS-RECOVERY — 2026-10-29

The tester analysis supplied in the development request reports a successful
job with zero SetupOption rows and two VatField rows processed; US/OTHER rules
persisted while ENABLE_TAX=Y did not. A retained earlier Tax ProcessLog inspected
in this development session independently reports zero SetupOption rows and one
VatField row, with successful job status. That earlier artifact has not been
matched to the tester's two-row run. Its retained candidate and baseline pass
the new helper's local switch-only alias checks; historical artifacts are not
a fresh baseline or proof of a successful recovery import. The proposed
shared-alias mechanism remains unproven. The same analysis reports a successful related Auto
Submission identical-alias test; the checked-in Auto Submission
[qualification contract](../../manage-auto-submission-and-matching-options/references/option-alias-qualification.md)
still labels that strategy unqualified. Neither establishes Tax-specific success.

The [Tax qualification contract](option-alias-qualification.md) supersedes the
single-populated-member instruction for controlled nonproduction tests. Its
local helper checks minimal identical aliases and fresh-export comparisons of
switches, tax rules and protected settings. Offline passes do not promote the
strategy or change historical live results.

A subsequent controlled named-BU create-Y test in this session completed with
one SetupOption row processed and zero failures. Fresh same-target export
reconciliation confirmed the new ENABLE_TAX=Y value in both aliases, all 306
protected option facts unchanged, and all 44 tax rules unchanged. The process
release was `11.13.27.04.0`; the exact schema is bound in the maintained
[qualified profile](qualified-option-alias-profile.json). The human explicitly
requested retaining the new row. This supports only the
[documented create-Y boundary](option-alias-qualification.md#live-qualified-boundary--2026-10-29),
not existing-row updates, global scope, N creates, other releases or UI tests.
Target-specific IDs, exports, ProcessLog, hashes and the retention decision
remain in the untracked project evidence rather than this reusable summary.

A controlled repetition on the original tester deployment, process release
`11.13.26.10.0`, subsequently passed the same named-BU switch-only create-Y test.
One SetupOption row processed with zero failures; a fresh export confirmed Y in
both aliases, all 64 unrequested option facts unchanged, and all 3 existing tax
rules unchanged. Retention was explicitly authorized. The older retained failed
package had the same setup-option row and process release; its companion alias
was empty. The corrected package populated both aliases and excluded the
already-imported tax-rule delta. The second exact schema fingerprint is now
listed in the maintained profile. This supports the packaging correction on
both deployments, without proving the internal alias-selection mechanism or
claiming a same-session single-alias A/B comparison.


## TAX-ALIAS-UPDATE — 2026-11-02

The retained approved nonproduction implementation on `11.13.26.10.0` now
provides update evidence beyond the historical create-only boundary. One
existing named-BU ENABLE_TAX row changed from N to Y alongside creation of
the same BU's US rule (merchant reference REQUIRED, other five behaviors
ENABLED, EnabledFlag N). The immutable candidate used identical minimal
aliases and preserved the baseline OtherOrgId. Its SHA256 is
`5805c518f75c6a1a71870644aee4d4ec4f0b3784eba672d51da21ea8e72eb1b1`.

The retained Task Hook approval binds those bytes and target Run Book. The
submission/status history and terminal ProcessLog bind the import to one
SetupOption and one VatField row processed, zero failures and warnings. The
before/after task export records surround the import in time. Rechecking the
complete exports with `verify_readback` confirmed both aliases, the new rule,
all 64 protected options and all 3 existing rules. Baseline and readback SHA256
are respectively `d6c247e27e2dfa7c35e35e7904a37af79e5d809cd1020fe787582fbeb44694c9`
and `a128821e81d75e3ead616e860835e0bbd0a4571551310a641202bed149555bfe`.
The user approved retaining the implementation's final values. Raw artifacts,
target identities and external IDs remain in the untracked project evidence.

The [update profile](option-alias-qualification.md#live-qualified-update-boundary--2026-11-02)
promotes only that combined operation on its exact schema/release. Earlier
create-only statements above describe the evidence available on their dates.
No new Fusion mutation was performed to review or promote this retained run.

## STAGED-CREATE-PREPARATION — 2026-11-02

The local helper can now split a complete new-Y-switch/new-same-BU-rule request
into a qualified switch-only candidate and, after full switch readback, a
rule-only candidate. Its 48-test offline suite covers deferred-rule retention,
both aliases, inserted target-owned transport context, fresh stage-2 metadata,
protected values, original-request binding, lifecycle/schema mismatches,
intervening changes and CLI input/dry-run/no-overwrite behavior. The final
rule-only readback also verifies preservation of the newly created switches.

This is orchestration of the existing create-Y and rule-only routes, not new
evidence for a combined-create import. It performs no Fusion calls and grants
no approval. The host must separately validate references, environment and
export provenance, terminal process results, and core approval for each stage.
No live two-stage execution was performed as part of this source change.

## Validation coverage — 2026-10-07

The Manage Tax Fields Testing campaign (retained internal campaign; historical summary below) records selected nonproduction execution evidence separately from the source review above. Its snapshot at this date includes 57 live setup passes, covering selected creates, updates, all 18 field/value combinations and 30 directed transitions. BU and territory preflight, terminal import results and fresh-export reconciliation were exercised. UI01 (hidden) and UI02 (optional blank) passed; UI03 is partial because required-field validation was observed but supplied-value persistence was not verified. Remaining transition and setup cases are not certified.

The repository suite has 27 passing offline tests, including nine cleanup-lifecycle tests. These are reference-harness and mocked-core checks, not production-adapter or complete live E2E coverage. Live cleanup is not certified. The source references and package hashes above describe the original authoring artifacts, not every later run. Target identity, privileges, current references, candidate approval and fresh-export reconciliation remain mandatory for each execution. Tenant names, credentials, business-unit values and transaction identifiers are intentionally excluded from this reusable summary.
