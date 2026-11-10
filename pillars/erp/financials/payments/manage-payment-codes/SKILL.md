---
skill_id: "erp.financials.payments.manage-payment-codes"
name: "Manage Payment Codes Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Payment Codes under the Payments functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payments"
functional_area_code: "ORA_FIN_PAYMENTS"
task_code: "IBY_MANAGE_PAYMENT_CODES"
task_name: "Manage Payment Codes"
parent_skill_id: "erp.financials.payments"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
uses_core:
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
persists_project_state: true
token_usage_tracking:
  enabled: true
  granularity: "per_skill_run"
  artifact_type: "token_usage_record"
  default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
  estimation_method: "chars/4 estimate unless exact tokenizer or API accounting is available"
  required_fields:
    - "activity_start_time"
    - "skill_id"
    - "task"
    - "trigger"
    - "artifacts_written"
    - "files_read"
    - "estimated_input_tokens"
    - "estimated_output_tokens"
    - "estimated_total_tokens"
    - "estimation_method"
    - "notes"
state_updates:
  - "setup_task_sequence"
  - "configuration_blueprints"
  - "validation_results"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payments/manage-payment-codes/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payments/manage-payment-codes/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects: []
required_privileges: []
---

# Manage Payment Codes Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Payment Codes` under `Payments`.

## Setup Task Skill Contract

- task_code: `IBY_MANAGE_PAYMENT_CODES`
- task_name: `Manage Payment Codes`
- parent_skill_id: `erp.financials.payments`
- pillar: `ERP`
- offering: `Financials`
- functional_area: `Payments`
- functional_area_code: `ORA_FIN_PAYMENTS`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Payment Codes` under `Payments`.

## Setup Task Metadata

- Task name: `Manage Payment Codes`
- Task code: `IBY_MANAGE_PAYMENT_CODES`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Financials`
- Functional area / Setup Object: `Payments`
- Setup task name: `Manage Payment Codes`
- Setup task code: `IBY_MANAGE_PAYMENT_CODES`




## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `erp.financials.payments` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Task Resource Contract

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: IBY_PAYMENT_CODE::PaymentCodeType, IBY_PAYMENT_CODE::PaymentCode, IBY_PAYMENT_CODE::TerritoryCode, IBY_PAYMENT_CODE::FormatValue, IBY_PAYMENT_CODE::Meaning, IBY_PAYMENT_CODE::StartDate, IBY_PAYMENT_CODE::Description, IBY_PAYMENT_CODE::EndDate, IBY_PAYMENT_CODE::EndDateDsp, IBY_PAYMENT_CODE::Code -->
<!-- fscr-update-fields: IBY_PAYMENT_CODE::TerritoryCode, IBY_PAYMENT_CODE::FormatValue, IBY_PAYMENT_CODE::Meaning, IBY_PAYMENT_CODE::StartDate, IBY_PAYMENT_CODE::Description, IBY_PAYMENT_CODE::EndDate, IBY_PAYMENT_CODE::EndDateDsp -->

Root create and same-key customer update are source-supported model behavior. Code pairing applies only to create; existing-row updates preserve its exported cell because its setter writes the insert-only key. EndDateDsp is derived from EndDate: blank for the no-end-date sentinel and equal for a finite date. Translation parent integrity remains required. Non-updateable audit/SeededFlag columns use the documented readXML ignore boundary; current-record baseline facts require a validated fresh full-task current-data export. Country verification is a required preview preflight. Direct translation operations remain unqualified and excluded. Root create requires complete installed-language inventory and qualified framework child effects. Before preview, root Meaning/Description updates require exact expected session-language effects and a qualified reconciliation contract, otherwise stop. Verify actual effects from the fresh post-import export afterward. Neither lifecycle markers nor a complete registry authorizes execution or supplies dynamic facts.

Read the governing [Task Rule Registry Execution](../../../../../core/data-loader/references/task-rule-registry-execution.md) contract, this task manifest, the exact-task registry and the planner result before interpreting any task node. Confirm exact task identity, require a successful planned result with ready reachable nodes, and read each reachable source anchor before evaluating its declared action and transition. Stop on missing or inconsistent artifacts; never infer a readiness override. Data Loader owns immutable preview and mutation approval.

Read these owning resources in order:

1. [Input validation](ora-resource/ora_input_validation.md): complete 27-attribute create/update dispositions and string bounds.
2. [Dependency readiness](ora-resource/ora_dependency_readiness.md): identity, baseline and translation-parent requirements.
3. [Reference lookups](ora-resource/ora_reference_lookups.md): seeded Type domain, complete-export identity verifier and published Country/language public-preflight contracts. Fresh successful environment reads remain required; a published contract alone supplies no current values or read privilege proof.
4. [Defaulting](ora-resource/ora_defaulting_rules.md): explicit date/Code serialization, non-updateable audit/flag boundary and framework-owned, session-dependent language effects.
5. [Design enforcement](ora-resource/ora_design_enforcement.md): identity, namespace and seeded-field restrictions.
6. [Error handling](ora-resource/ora_error_handling.md): source error identifiers, disclosure and stop-before-retry gates.
7. [Compiled rule registry](ora-resource/ora_rule_registry.json): generated task-local graph and exact readiness blockers.

The import root is PaymentCodeVO; the observed package entities are IBY_PAYMENT_CODE and IBY_PAYMENT_CODE_TRANSLATION. Root identity is PaymentCodeType + PaymentCode; translation identity adds Language. The VL root entity overlays IBY_PAYMENT_CODES_B, and the translation entity maps IBY_PAYMENT_CODES_TL. Parent/child linkage uses both root keys. Both observed entity NodeSequence values are 1; these are entity-bound metadata, not a package-wide ordinal. Sources: SRC-FSM-PACKAGE, SRC-CS-EO, SRC-CS-TLEO, SRC-CS-TLLINK, SRC-CS-TLASSOC.

Use `core.data-loader` in FSM mode with empty manifest businessObject; resolve exact task import identity from same-task ASM_SETUP_CSV_METADATA.xml ObjectShortName. Task resources own validation facts, not package assembly or direct writes. The owning Run Book/Data Loader workflow must produce an immutable preview and obtain its separate exact approval before submission, monitor the original attempt and verify persisted state. Do not replay an uncertain load. End dating is an update; no CSV physical-delete/cascade/rollback mechanism is proven.

SRC-FSM-PACKAGE denotes the reviewed same-task template/current exports and metadata; raw rows remain outside reusable task source. SRC-UI-CREATE denotes the 2026-10-05 unsaved create dialog: required Name/Code/Type/From Date, observed From Date 10/5/26 and blank To Date, five Type labels, cancellation verified without Save. No durable screenshot or persisted-state proof is claimed. The generation-review artifact in the implementation project preserves exact artifact paths, provenance and gaps.

## Source-Backed Task Behavior

- Root identity is PaymentCodeType + PaymentCode; both keys are insert-only, and the transient Code setter changes PaymentCode. An existing identity cannot be renamed through update. Sources: SRC-CS-EO, SRC-CS-VO, SRC-CS-EOJAVA.
- Type uses the five seeded IBY_PAYMENT_CODE_TYPE codes, with business-label normalization and no serialization of UI indices. The user-declared reviewed task tables own static evaluation; FSM ListValidationBean remains the application validator. Sources: SRC-CS-TYPESEED, SRC-CS-UIVO, SRC-CS-EO.
- The effective PaymentCodeType ceiling is 30 characters in the public entity and task Input Validation; retain the closed five-code domain. The EO's broader model precision does not permit arbitrary Type values. Sources: SRC-CS-PC-PEO, SRC-CS-EO.
- SeededFlag Y prevents changes to TerritoryCode, Meaning and Description. Audit fields and SeededFlag remain service read-only: retain empty structural cells on create and preserve exported cells on update without accepting caller changes. The documented readXML ignore boundary does not authorize audit writes. Sources: SRC-CS-EOJAVA, SRC-CS-VO, SRC-CS-TLVO, SRC-INTERNAL-FSM-FAQ.
- Root StartDate defaults to current database date and EndDate to 4712-12-31 in the EO. CSV preparation uses an explicit business StartDate and EndDate, with EndDateDsp blank exactly for EndDate 4712/12/31 and equal to a finite EndDate otherwise. Code is paired with PaymentCode only on create; an update preserves its exported cell instead of invoking the key-writing setter. These scoped accessor contracts do not establish generic blank preserve-existing/default behavior. Sources: SRC-CS-EOJAVA, SRC-CS-EO, SRC-CS-VO, SRC-CS-FSM-MIGRATOR, SRC-CS-FSCORE-CSVXML, SRC-CS-FSCORE-XMLCONSTANTS.
- Translation identity adds Language, and SourceLang is required. Parent/root/child key pairs must agree and existing child inputs remain preserved. Framework root create produces one child for every installed I/B language, with SourceLang from the execution session; never assume US or filter installed languages by activation. Root Meaning/Description updates can propagate to children whose Language or SourceLang matches the applicable language, changing SourceLang. Before preview qualify exact expected effects and the reconciliation contract or stop; verify actual effects from the fresh post-import export afterward. Direct translation operation ownership remains unqualified and excluded. Sources: SRC-CS-TLEO, SRC-CS-TLLINK, SRC-CS-TLASSOC, SRC-PUBLIC-COMMON-OPENAPI-26D, SRC-CS-APPLCORE-TL-CREATE, SRC-CS-APPLCORE-TL-UPDATE, SRC-CS-APPLCORE-LANGUAGES.
- Country displays TerritoryShortName and stores TerritoryCode through TerritoryPEO. The owning reference resource defines exact published territoriesLOV code/name preflight; require a successful current-environment read. This public-preflight-only contract does not establish the exact FSM missing-reference error. Sources: SRC-CS-UIVO, SRC-CS-TERRVO, SRC-CS-TERRASSOC, SRC-PUBLIC-COMMON-OPENAPI-26D.
- Root/TL string bounds are entity-specific; customer PaymentCode cannot use the reserved ORA_ prefix. End dating is an update and does not establish CSV physical deletion or new-row rollback. Sources: SRC-CS-EO, SRC-CS-TLEO, SRC-CS-EOJAVA, SRC-CS-AM.

## Source Evidence

The following IDs resolve the implementation sources cited in the task resources. Task CodeSearch evidence uses FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64. An explicit user exception authorized read-only research of directly referenced framework branches: FSCORE_MAIN_GENERIC (series push September 24, 2026) and FSM_MAIN_GENERIC (series push October 1, 2026). These snapshots do not establish the deployed pod revision or a successful CSV import. Public task documentation was reviewed at 26D; historical ADF/ApplCore API references were reviewed as background and excluded from task runtime authority.

| Source ID | Evidence | Boundary |
|---|---|---|
| SRC-CS-APPLCORE-TL-CREATE | APPLCORE source archive fmwtools/BUILD_HOME/atgpf/plugins/jdeveloper/jdev/oaext/oracle.apps.fnd.applcore-src.zip; member oracle/apps/fnd/applcore/oaext/model/OAEntityImpl.java:2691-2788,3069-3084,4852-4912 | Reviewed ADE dependency source: one owned child per installed language; Language iterated, SourceLang session-derived. Not deployed-version parity or direct child operation proof. |
| SRC-CS-APPLCORE-TL-UPDATE | Same APPLCORE archive/member OAEntityImpl.java:3300-3303,3356-3455 | Root translated setters propagate by matching Language or SourceLang and set SourceLang. Exact session/effect qualification remains a pre-preview requirement. |
| SRC-CS-APPLCORE-LANGUAGES | Same archive; member oracle/apps/fnd/applcore/oaext/model/OAUtility.java:2037-2050 | Installed membership uses I/B; active membership is separate. Fresh environment values still require the declared resolver. |
| SRC-CS-PC-PEO | PaymentCodePEO.xml — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/iby/fundsDisbursementSetup/paymentCodes/publicEntity/src/oracle/apps/financials/payments/fundsDisbursementSetup/paymentCodes/publicEntity/PaymentCodePEO.xml#30` | PaymentCodeType precision 30; read-only mapping/precision evidence does not qualify importer null handling or deployed revision. |
| SRC-INTERNAL-FSM-FAQ | Setup Data Export-Import FAQ — `Setup Data Export-Import FAQ; page 1681235222; v37; 2025-08-01` | v37, updated 2025-08-01: readXML ignores non-updateable row attributes. Applied only to the exact task service VO audit/flag definitions; no successful import or translation business ownership inferred. |
| SRC-PUBLIC-COMMON-OPENAPI-26D | [Common Features 26D OpenAPI](https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/openapi.json) | Version 2026.09.28, updated October 2026: complete Country/language field schemas, paging and exact installed/active language finder contracts. Published read-only preflight only; no deployed values, CSV language default or translation ownership inferred. |
| SRC-FSM-CURRENT-20261006 | Fresh current-data export through shared.setup-export.task-level-export; exact-task receipt retained only in the implementation project | Completed exact-task/environment/submitted-user manifest and full-scope export without criteria. Baseline facts must be refreshed for each preview; exported child rows do not prove lifecycle ownership or allowed-language population. |
| SRC-FSM-TEMPLATE-20261006 | Fresh template-only export through shared.setup-export.task-level-export; exact-task receipt in the implementation project | Completed same-task/environment/user manifest and both ordered CSV headers; shape matches the current-data export. No record-existence or business-write proof. |
| SRC-CS-AMIMPL | PaymentCodeServiceAMImpl.java — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/iby/fundsDisbursementSetup/paymentCodes/model/src/oracle/apps/financials/payments/fundsDisbursementSetup/paymentCodes/paymentCodeService/applicationModule/PaymentCodeServiceAMImpl.java` | Imports IBY_PAYMENT_CODE.xml through MigratorHelper.readXML; exports both VOs excluding ObjectVersionNumber; localized exceptions become processing errors. No direct PL/SQL invocation observed. |
| SRC-CS-AM | PaymentCodeServiceAM.xml — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/iby/fundsDisbursementSetup/paymentCodes/model/src/oracle/apps/financials/payments/fundsDisbursementSetup/paymentCodes/paymentCodeService/applicationModule/PaymentCodeServiceAM.xml` | Wires PaymentCode and PaymentCodeTranslation service VOs; exposes service CRUD and merge. This does not establish CSV physical deletion. |
| SRC-CS-VO | PaymentCodeVO.xml — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/iby/fundsDisbursementSetup/paymentCodes/model/src/oracle/apps/financials/payments/fundsDisbursementSetup/paymentCodes/paymentCodeService/view/PaymentCodeVO.xml` | Root package fields use PaymentCodeEO; PaymentCode/PaymentCodeType while-insert; service audit and SeededFlag read-only; Code and EndDateDsp transient. |
| SRC-CS-EO | PaymentCodeEO.xml — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/iby/fundsDisbursementSetup/paymentCodes/model/src/oracle/apps/financials/payments/fundsDisbursementSetup/paymentCodes/model/entity/PaymentCodeEO.xml` | VL entity over IBY_PAYMENT_CODES_B; composite key; source lengths/defaults; date and ORA_ prefix validation; lookup type IBY_PAYMENT_CODE_TYPE. |
| SRC-CS-EOJAVA | PaymentCodeEOImpl.java — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/iby/fundsDisbursementSetup/paymentCodes/model/src/oracle/apps/financials/payments/fundsDisbursementSetup/paymentCodes/model/entity/PaymentCodeEOImpl.java` | Seeded Y restricts TerritoryCode/Meaning/Description; DB-current StartDate and 4712-12-31 EndDate defaults; transient setters affect persisted key/date. |
| SRC-CS-TLVO | PaymentCodeTranslationVO.xml — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/iby/fundsDisbursementSetup/paymentCodes/model/src/oracle/apps/financials/payments/fundsDisbursementSetup/paymentCodes/paymentCodeService/view/PaymentCodeTranslationVO.xml` | Translation package fields map to PaymentCodeTranslationEO; audit fields service read-only. |
| SRC-CS-TLEO | PaymentCodeTranslationEO.xml — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/iby/fundsDisbursementSetup/paymentCodes/model/src/oracle/apps/financials/payments/fundsDisbursementSetup/paymentCodes/model/entity/PaymentCodeTranslationEO.xml` | TL identity PaymentCode/PaymentCodeType/Language; SourceLang required; lengths; standard OAEntityImpl. |
| SRC-CS-UIVO | PaymentCodeVO.xml — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/iby/fundsDisbursementSetup/paymentCodes/model/src/oracle/apps/financials/payments/fundsDisbursementSetup/paymentCodes/model/view/PaymentCodeVO.xml` | UI and service share root EO. Type shows Meaning and returns LookupCode; country shows TerritoryShortName and returns TerritoryCode; Status derived and outside package. |
| SRC-CS-TLLINK | PaymentCodeVOToPaymentCodeTranslationVO.xml — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/iby/fundsDisbursementSetup/paymentCodes/model/src/oracle/apps/financials/payments/fundsDisbursementSetup/paymentCodes/paymentCodeService/view/link/PaymentCodeVOToPaymentCodeTranslationVO.xml` | 1-to-many link matches PaymentCode and PaymentCodeType. |
| SRC-CS-TLASSOC | PaymentCodeEOToTranslationEO.xml — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/iby/fundsDisbursementSetup/paymentCodes/model/src/oracle/apps/financials/payments/fundsDisbursementSetup/paymentCodes/model/entity/association/PaymentCodeEOToTranslationEO.xml` | Owned translation entities match root PaymentCode and PaymentCodeType; no CSV deletion instruction is established. |
| SRC-CS-TERRASSOC | TerritoryPEOToPaymentCodeEO.xml — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/iby/fundsDisbursementSetup/paymentCodes/model/src/oracle/apps/financials/payments/fundsDisbursementSetup/paymentCodes/model/entity/association/TerritoryPEOToPaymentCodeEO.xml` | Country references TerritoryPEO.TerritoryCode; exact missing-value error not specified in this association. |
| SRC-CS-TERRVO | TerritoryVVO.xml — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/components/payables/iby/fundsDisbursementSetup/paymentCodes/model/src/oracle/apps/financials/payments/fundsDisbursementSetup/paymentCodes/model/view/TerritoryVVO.xml` | Country resolver uses TerritoryPEO; code and short name fields, sorted by code. |
| SRC-CS-TYPESEED | Payment Code Type seed 26164-26262 — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/iby/db/data/StandardLookupTypeSD.xml#26164` | IBY_PAYMENT_CODE_TYPE, ViewApplicationId 0, CustomizationLevel S, SetId 0; five enabled canonical type codes and labels. |
| SRC-CS-BOSEED | Payment Code business object seed 22927-23012 — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/fun/db/data/FinFunShared/SetupBusinessObjectSD.xml#22927` | Exact service/XML/root path and alternate keys; UpdateEnabledFlag Y is not an override of EO while-insert restrictions. |
| SRC-CS-REFSEED | Payment Code reference attribute seed 5410-5429 — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/fun/db/data/FinFunShared/SetupBOReferenceAttributeSD.xml#5410` | PaymentCode and PaymentCodeType reference BO/attribute IDs are null; seed records do not define a separate foreign BO resolver. |
| SRC-CS-TASKSEED | Payment Codes task BO linkage 4958-4963 — `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64/fusionapps/fin/fun/db/data/FinFunShared/SetupTaskBusinessObjectSD.xml#4958` | IBY_MANAGE_PAYMENT_CODES binds IBY_PAYMENT_CODE, enabled Y, import sequence 0. |
| SRC-PUBLIC-26D | [Oracle Financials 26D APIs, Business Objects, and Schema](https://docs.oracle.com/en/cloud/saas/financials/26d/api.html) | Published 26D index reviewed; October 2026 REST guide update. Index is freshness evidence only. |
| SRC-PUBLIC-PAYMENT-LOV | [26D REST endpoint list: Payment Codes LOV](https://docs.oracle.com/en/cloud/saas/financials/26d/farfa/rest-endpoints.html) | Discovery of read-only collection/item paymentCodesLOV paths; exact operation/query/response limitations are recorded in Reference Lookups. |
| SRC-CS-FSM-MIGRATOR | MigratorAMHelper.java — `FSM_MAIN_GENERIC/fsm/components/setup/asm/model/src/oracle/apps/setup/migrator/model/applicationModule/MigratorAMHelper.java` | Live FSM CSV-to-XML path uses export/current metadata and calls XmlCSVAMImpl; does not prove independent child operation ownership. |
| SRC-CS-FSCORE-CSVAM | XmlCSVAMImpl.java — `FSCORE_MAIN_GENERIC/fscore/components/setupHub/remoteApp/publicModel/src/oracle/apps/setupHub/xml/model/applicationModule/XmlCSVAMImpl.java` | Orders declared node metadata, builds parent maps and invokes the converter. |
| SRC-CS-FSCORE-CSVXML | CSVXmlTransform.java — `FSCORE_MAIN_GENERIC/fscore/components/setupHub/remoteApp/publicModel/src/oracle/apps/setupHub/xml/transform/CSVXmlTransform.java` | Header/row/key/parent checks, typed date conversion and explicit-null XML output; no task audit suppression proved. |
| SRC-CS-FSCORE-MODELUTIL | ModelUtil.java — `FSCORE_MAIN_GENERIC/fscore/components/setupHub/remoteApp/publicModel/src/oracle/apps/setupHub/common/util/model/ModelUtil.java` | Sets XML_EXPLICIT_NULL; no task default or audit acceptance claim. |
| SRC-CS-FSCORE-XMLCONSTANTS | XmlConstants.java — `FSCORE_MAIN_GENERIC/fscore/components/setupHub/remoteApp/publicModel/src/oracle/apps/setupHub/xml/XmlConstants.java` | Declares yyyy/MM/dd to yyyy-MM-dd conversion; WHO constant list does not suppress history columns. |
| SRC-CS-FSCORE-MIGRATOR | MigratorHelper.java — `FSCORE_MAIN_GENERIC/fscore/components/setupHub/remoteApp/publicModel/src/oracle/apps/setupHub/remoteApp/publicModel/migrator/MigratorHelper.java` | Reads XML at the task-declared depth; records row failures/undo. Distinguish includeSeedData overloads before making export coverage claims. |
