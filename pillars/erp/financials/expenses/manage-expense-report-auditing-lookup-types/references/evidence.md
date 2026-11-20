# Evidence and authority boundaries

## Combined local publication qualification (2026-11-17)

The task retains the artifact-publication fixes from the equivalency maintenance
work alongside empty-baseline taxonomy resolution and private-profile selection.
Offline intake, candidate and adapter outputs use the co-shipped no-follow
publisher. Task-local synthetic regressions cover linked or replaced parents,
private permissions, complete writes, no overwrite and collision rollback that
preserves another writer's files. The empty-export regression also exercises the
actual candidate CLI and rejects an output parent linked outside the project.
These checks are local; no new live Fusion or generic readback qualification is
claimed. Export-omitted seeded updates and generic adapter module-enrichment
reconciliation still retain their documented evidence requirements.

## Empty-baseline reference resolution (2026-11-17)

Drop 3 exposed a local bootstrap gap: modified-only baseline exports can have no
module-bearing rows, while the collector required such a row before reading seeded
types. The collector now selects the Core BOSS taxonomy GET when no mapping exists.
The [Common documentation index](https://docs.oracle.com/en/cloud/saas/applications-common/)
resolved to 26D on this review date. Its [taxonomy collection contract](https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/op-servername-api-boss-data-objects-ora-commonappsinfra-objects-v1-taxonomynodes-get.html)
documents moduleId as the node identifier, moduleKey/moduleType and dollar-prefixed
filter/sort/paging parameters. Resolve the unique EXM/APPLICATION node independently
of lookup naming; never substitute alternativeId, an undocumented moduleGUID or an
environment-specific constant. Existing export-confirmed scope remains supported.

The collector also accepts a trusted --properties path and preserves the selected
profile/environment/origin across standard and BOSS requests, using Core scope
selection and separate tokens. Synthetic tests cover empty packages through one-code
candidate generation, failure gates, pagination and private profile binding. This
is local qualification, not a new QQY live-read or import qualification.

Public documentation was reviewed newest-first on 2026-10-30. The latest published
Financials/Common documentation located was 26D; the internal export reports
11.13.27.04.0. Source revision and environment evidence are separate.

| ID | Source | Reviewed claim |
|---|---|---|
| SRC-001 | [Oracle Financials latest documentation index](https://docs.oracle.com/en/cloud/saas/financials/26d/) | Release index verified 2026-10-30 |
| SRC-002 | [Audit list reasons](https://docs.oracle.com/en/cloud/saas/financials/26d/faiex/how-you-add-to-or-remove-employees-from-the-audit-list.html) | EXM_AUDIT_REASON purpose; not an import field contract |
| SRC-003 | [Expense Assistant setup](https://docs.oracle.com/en/cloud/saas/financials/26d/faiex/set-up-expense-assistant.html) | Task navigation and ORA_EXM_MATCH_MERCHANT_NAME; no blanket scope beyond task |
| SRC-004 | [Expense risk indicator](https://docs.oracle.com/en/cloud/saas/financials/26d/faiex/expense-report-risk-indicator-in-expense-audit.html) | Standard-lookup task boundary; do not conflate creating risk lookup types with this seeded-type code maintenance task |
| SRC-005 | Task seed; CodeSearch path SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/fun/db/data/FinFunShared/SetupTaskSD.xml#10211 | Task flow ManageGenericLookupTF; mode=search,moduleType=APPLICATION,moduleKey=EXM |
| SRC-006 | FSM service Java; CodeSearch path SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/financialCommon/fun/appsLookups/appsLookupsService/src/oracle/apps/financials/commonModules/appsLookups/appsLookupService/applicationModule/appsLookupServiceAMImpl.java | exportData lines 381-382 customer-modified filter; importData 412-553 type/code readXML; SetCode resolver and missing-set row warning |
| SRC-007 | FSM service module; CodeSearch path SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/financialCommon/fun/appsLookups/appsLookupsService/src/oracle/apps/financials/commonModules/appsLookups/appsLookupService/applicationModule/appsLookupServiceAM.xml | Primary LookupTypeGeneric1 and LookupGeneric1, SetIdLookupVO; translation view links |
| SRC-008 | UI task flow; CodeSearch path SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/financialCommon/fun/appsLookups/ui/public_html/WEB-INF/oracle/apps/financials/commonModules/appsLookups/ui/flow/ManageGenericLookupTF.xml | Frontend search/edit routing and mode/module/lookupType parameters |
| SRC-009 | Lookup-code primary VO; CodeSearch path SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/financialCommon/fun/appsLookups/appsLookupsService/src/oracle/apps/financials/commonModules/appsLookups/appsLookupService/view/LookupGenericVO.xml | Key: LookupCode,LookupType,SetId,ViewApplicationId; SetCode derived from FND_SETID_SETS_VL; customer-modified-only filter |
| SRC-010 | Lookup-code EO; CodeSearch path SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/financialCommon/fun/appsLookups/model/src/oracle/apps/financials/commonModules/appsLookups/model/entity/LookupGenericEO.xml | Required type/code 30, meaning 80; description 240; enabled Y/N default Y; tag 150; integer display sequence; dates start<=end; duplicate code and meaning validation |
| SRC-011 | Lookup-code entity Java; CodeSearch path SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/financialCommon/fun/appsLookups/model/src/oracle/apps/financials/commonModules/appsLookups/model/entity/LookupGenericEOImpl.java | validateSetId() returns true; overload has view set-enabled check. Start-date customization restrictions are skipped for appsLookupService AM by skipValidationFromJava, so UI editability is not proof of import restriction |
| REST-TYPES | [Generic lookups GET](https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/op-servername-fscmrestapi-resources-11.13.18.05-genericlookups-get.html) | Type/view/module, code fields and pagination; code response omits SetId |
| REST-SETS | [Set ID sets GET](https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/op-http-servername-fscmrestapi-resources-11.13.18.05-setidsets-get.html) | SetCodeFinder and SetCode/SetId/SetName |
| VO-SET | SetIdLookupVO.xml; CodeSearch path SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/financialCommon/fun/appsLookups/appsLookupsService/src/oracle/apps/financials/commonModules/appsLookups/appsLookupService/view/SetIdLookupVO.xml | SetCode criterion over FND_SETID_SETS_VL; AM maps result to SetId and warns/skips on no match |
| SEED-REF | SetupBOReferenceAttributeSD.xml; CodeSearch path SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/fun/db/data/FinFunShared/SetupBOReferenceAttributeSD.xml#4052 | LookupCode, SetCode, ViewApplicationId and lookupType reference-attribute registrations; null reference BO mappings do not establish value existence |

Aliases: AM-SERVICE = SRC-006; EO-CODE = SRC-010; UI = the read-only task search,
EXM_AUDIT_REASON code table and unsaved-create view recorded in the project evidence.
The unsaved row was cancelled; no configuration was saved.

## Capability limits

The workbook LOV redesign and historical auditing examples are documented in
[lookup-type-research.md](lookup-type-research.md), reviewed 2026-10-31. The UI
initializer's taxonomy-descendant scope is broader than a direct ModuleId GET;
neither a module inventory nor the six historical examples is the complete LOV
for every environment. The shipping workbook contains no customer lookup choices;
its runtime dropdowns must be populated from destination evidence.

Create/update code intent is supported by the AM importData readXML path and EO/VO fields.
The workbook excludes caller-supplied keys beyond business identity, audit/transient
fields, DFFs and independent translation authoring. This exclusion is intake scope, not
evidence that Oracle cannot update them. Enabled Y/N and default Y come from EO-CODE.
Start/end relation and code/meaning uniqueness come from its declarative validators.
UI seed editability is not an FSM restriction: entity Java skips certain customization
checks for the service AM. Physical delete is outside scope and not inferred from end dating.

Live code creation and updates were verified in the authoring environment after
correcting the required refresh flag described below. The project retains the
import outcomes, failure/recovery evidence and exact-key readback. This qualifies
only the exercised code scenarios; parent Meaning/Description changes, independent
translations, seeded updates without complete baseline rows and rollback still
require separate runtime/preservation evidence. Historical live results do not
constitute a campaign through the generic E2E tester.

## Current type edit extension

See ui-parity.md for the 2026-10-31 review of primary UI/EO/FSM VO, text lengths,
translation keys and runtime gaps. Version 0.3.0 adds existing type Meaning and
Description input, selected-parent offline packaging and UI-equivalent code
permission checks. Source configuration rules are separated from the service AM
validation bypass. Live language propagation and full UI parity remain unqualified.
The colleague workbook was inspected without modifying it.

## Customer-set correction (2026-11-03)

The implementor's historical-target-withheld screenshot shows a new EXM_AUDIT_REASON row with
customer reference sets in the LOV. CodeSearch reinspection of VO-SET confirms
its query reads SET_CODE/SET_ID from FND_SETID_SETS_VL, with only an exact SetCode
criterion, not a relationship to existing codes. SRC-009 confirms SetId belongs
to the code identity alongside type/code/view. The refresh adapter therefore
reads the unfiltered type code child and each DFF identity across all sets, then
qualifies the destination sets, including sets with no existing selected-type
codes. An available dropdown is not evidence of a completed import; live
acceptance and readback remain separate gates.

The 26D generic lookup item GET documents lookupsDFF identity fields including
LookupType, LookupCode, ViewApplicationId and SetId. Live read-only verification
returned those identities for all 25 selected-type codes without configured
DFF attributes. Customer identities are kept in project exports only.

## Required refresh flag (source checked 2026-11-03)

LookupGenericEO.xml lines 351–359 and LookupGenericTranslationEO.xml lines 200–208
in financialCommon/fun/appsLookups/model declare ChangeSinceLastRefresh
IsNotNull=true, Precision=1 and DefaultValue=N. New code candidates must serialize
N rather than an explicit blank. Existing type/code/translation rows retain their
exported value; missing retained values block packaging. This is a fixed product
default, not customer environment data or an administrator workbook field.
Exact-task current export evidence also contained N across all four CSV members.
The initial import failed with JBO-27014 on base and automatically generated
translation rows; empty translation CSVs must not be populated with guessed languages.

## Export-local node sequences

The paired exact-task template and current-data exports reviewed on 2026-11-03
have identical business-object names, XML paths, batch mappings and column
contracts, but different NodeSequence values (template 1/3, data 2/4). These
observations establish that this task cannot require the authoring-time sequence
numbers on every export, even within one environment and release.

Use the existing export-local policy: validate positive integers and reject
sequence collisions within the same XML-file/hierarchy level. The type and type
translation map to LookupTypeGeneric1; code and code translation map to
LookupGeneric1. These are task mappings, not destination record identifiers.
Continue checking exact paths, columns, types, task, environment and release
compatibility. Candidate metadata must remain byte-identical to the selected
template. Do not rewrite a baseline or infer permission to change lookup data
from sequence differences. Live success on arbitrary releases is not implied.

## Create readback module resolution

The 2026-11-03 create/readback test confirmed that the import service populated
ModuleId when the candidate supplied ModuleKey and ModuleType. The resulting ID
matched the pre-import exact lookup type/view/module association. Reconciliation
accepts this enrichment only for a new code with a blank candidate ModuleId and
one unambiguous nonblank module ID in matching pre-import type/code rows. It
rejects missing or conflicting evidence, unrelated IDs and module changes on
updates. No destination ID is embedded in the verifier. The report includes the
baseline, candidate and readback hashes to bind that evidence.
