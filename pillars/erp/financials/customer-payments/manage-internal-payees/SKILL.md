---
skill_id: "erp.financials.customer-payments.manage-internal-payees"
name: "Manage Internal Payees Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Internal Payees under the Customer Payments functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Customer Payments"
functional_area_code: "ORA_FIN_CUSTOMER_PAYMENTS"
task_code: "IBY_MANAGE_INTERNAL_PAYEES"
task_name: "Manage Internal Payees"
parent_skill_id: "erp.financials.customer-payments"
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
  - "erp.financials.payments.manage-payment-systems"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/customer-payments/manage-internal-payees/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/customer-payments/manage-internal-payees/current/"
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

# Manage Internal Payees Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Internal Payees` under `Customer Payments`.

## Setup Task Skill Contract

- task_code: `IBY_MANAGE_INTERNAL_PAYEES`
- task_name: `Manage Internal Payees`
- parent_skill_id: `erp.financials.customer-payments`
- pillar: `ERP`
- offering: `Financials`
- functional_area: `Customer Payments`
- functional_area_code: `ORA_FIN_CUSTOMER_PAYMENTS`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Internal Payees` under `Customer Payments`.

## Setup Task Metadata

- Task name: `Manage Internal Payees`
- Task code: `IBY_MANAGE_INTERNAL_PAYEES`
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

For payee inactivation, establish whether the requested outcome concerns the stored Activestatus flag, date-based UI Status, or both. The search page calculates UI Status from StartDate/EndDate and the database date. A finite end date must remain consistent in EndDate and EndDateDsp because both fields represent the same effective end date. For condition reconciliation, an omitted PayerBankRoutingNumDisp can export as Value even for AMOUNT; consult the task's defaulting and design rules before treating a derived display as an unexpected business change.

For a new or changed payment-system/account tuple, use the read-only Manage Payment Systems dependency-export contract in the reference guide before import. A successful complete `IBY_MANAGE_PAYMENT_SYSTEMS` export can establish exact Suffix/Key1 membership or absence. Account ownership remains a separate check. This dependency authorizes evidence acquisition, with prerequisite creation handled only by its owning task under separate authority.

Use this task metadata when invoking those skills:

- Offering: `Financials`
- Functional area / Setup Object: `Customer Payments`
- Setup task name: `Manage Internal Payees`
- Setup task code: `IBY_MANAGE_INTERNAL_PAYEES`




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

Use the parent functional-area skill `erp.financials.customer-payments` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Source-backed operation scope

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: ORA_IBY_FC_DEFAULT_ROUTE::Instrtype, ORA_IBY_FC_DEFAULT_ROUTE::PaymentChannelCode, ORA_IBY_FC_DEFAULT_ROUTE::FndcptUserProfileCode, ORA_IBY_FC_DEFAULT_ROUTE::FndcptUserProfileName, ORA_IBY_FC_DEFAULT_ROUTE::Key1, ORA_IBY_FC_DEFAULT_ROUTE::Suffix, ORA_IBY_FC_INT_PAYEE_MAP::OrgType, ORA_IBY_FC_INT_PAYEE_MAP::BuName, ORA_IBY_FC_ROUTING_CONDITION::ParameterCode, ORA_IBY_FC_ROUTING_CONDITION::OperationCode, ORA_IBY_FC_ROUTING_CONDITION::Value, ORA_IBY_FC_ROUTING_CONDITION::EntrySequence, ORA_IBY_FC_ROUTING_CONDITION::PayerBankRoutingNumDisp, IBY_INTERNAL_PAYEE::Payeeid, IBY_INTERNAL_PAYEE::Name, IBY_INTERNAL_PAYEE::Ecappid, IBY_INTERNAL_PAYEE::Username, IBY_INTERNAL_PAYEE::Password, IBY_INTERNAL_PAYEE::Activestatus, IBY_INTERNAL_PAYEE::Supportedop, IBY_INTERNAL_PAYEE::Logo, IBY_INTERNAL_PAYEE::Threshold, IBY_INTERNAL_PAYEE::RiskEnabled, IBY_INTERNAL_PAYEE::MccCode, IBY_INTERNAL_PAYEE::DbaName, IBY_INTERNAL_PAYEE::DbaCity, IBY_INTERNAL_PAYEE::DbaStateProvince, IBY_INTERNAL_PAYEE::DbaCountry, IBY_INTERNAL_PAYEE::InactiveDate, IBY_INTERNAL_PAYEE::StartDate, IBY_INTERNAL_PAYEE::EndDate, IBY_INTERNAL_PAYEE::PayerNotifSendFrom, IBY_INTERNAL_PAYEE::PayerNotifEmailSubject, IBY_INTERNAL_PAYEE::EndDateDsp, ORA_IBY_FC_ACCNT_PAYMENT::Ecappid, ORA_IBY_FC_ACCNT_PAYMENT::Payeeid, ORA_IBY_FC_ACCNT_PAYMENT::Status, ORA_IBY_FC_ACCNT_PAYMENT::Accttype, ORA_IBY_FC_ACCNT_PAYMENT::Instrtype, IBY_FC_ROUTING_RULE::Payeeid, IBY_FC_ROUTING_RULE::Configured, IBY_FC_ROUTING_RULE::Priority, IBY_FC_ROUTING_RULE::Paymentmethodname, IBY_FC_ROUTING_RULE::InstrType, IBY_FC_ROUTING_RULE::InstrSubType, IBY_FC_ROUTING_RULE::Bepkey, IBY_FC_ROUTING_RULE::InactiveDate, IBY_FC_ROUTING_RULE::FndcptUserProfileCode, IBY_FC_ROUTING_RULE::FndcptUserProfileName, IBY_FC_ROUTING_RULE::PaymentChannelCode, IBY_FC_ROUTING_RULE::StartDate, IBY_FC_ROUTING_RULE::EndDate, IBY_FC_ROUTING_RULE::Suffix, IBY_FC_ROUTING_RULE::Key1, IBY_FC_ROUTING_RULE::EndDateDsp, IBY_FC_ROUTING_RULE::TokenizationRoutingFlag, IBY_FC_ROUTING_RULE::IBY_INTERNAL_PAYEE.Payeeid, ORA_IBY_FC_ACCNT_PAYMENT::IBY_INTERNAL_PAYEE.Payeeid, ORA_IBY_FC_DEFAULT_ROUTE::IBY_INTERNAL_PAYEE.Payeeid, ORA_IBY_FC_INT_PAYEE_MAP::IBY_INTERNAL_PAYEE.Payeeid, ORA_IBY_FC_ROUTING_CONDITION::IBY_INTERNAL_PAYEE.Payeeid, ORA_IBY_FC_ROUTING_CONDITION::IBY_FC_ROUTING_RULE.Paymentmethodname -->
<!-- fscr-update-fields: ORA_IBY_FC_DEFAULT_ROUTE::Instrtype, ORA_IBY_FC_DEFAULT_ROUTE::FndcptUserProfileCode, ORA_IBY_FC_DEFAULT_ROUTE::FndcptUserProfileName, ORA_IBY_FC_DEFAULT_ROUTE::Key1, ORA_IBY_FC_DEFAULT_ROUTE::Suffix, ORA_IBY_FC_ROUTING_CONDITION::ParameterCode, ORA_IBY_FC_ROUTING_CONDITION::OperationCode, ORA_IBY_FC_ROUTING_CONDITION::Value, ORA_IBY_FC_ROUTING_CONDITION::PayerBankRoutingNumDisp, IBY_INTERNAL_PAYEE::Name, IBY_INTERNAL_PAYEE::Ecappid, IBY_INTERNAL_PAYEE::Username, IBY_INTERNAL_PAYEE::Password, IBY_INTERNAL_PAYEE::Activestatus, IBY_INTERNAL_PAYEE::Supportedop, IBY_INTERNAL_PAYEE::Logo, IBY_INTERNAL_PAYEE::Threshold, IBY_INTERNAL_PAYEE::RiskEnabled, IBY_INTERNAL_PAYEE::MccCode, IBY_INTERNAL_PAYEE::DbaName, IBY_INTERNAL_PAYEE::DbaCity, IBY_INTERNAL_PAYEE::DbaStateProvince, IBY_INTERNAL_PAYEE::DbaCountry, IBY_INTERNAL_PAYEE::InactiveDate, IBY_INTERNAL_PAYEE::StartDate, IBY_INTERNAL_PAYEE::EndDate, IBY_INTERNAL_PAYEE::PayerNotifSendFrom, IBY_INTERNAL_PAYEE::PayerNotifEmailSubject, IBY_INTERNAL_PAYEE::EndDateDsp, ORA_IBY_FC_ACCNT_PAYMENT::Ecappid, ORA_IBY_FC_ACCNT_PAYMENT::Status, IBY_FC_ROUTING_RULE::Configured, IBY_FC_ROUTING_RULE::Priority, IBY_FC_ROUTING_RULE::InstrType, IBY_FC_ROUTING_RULE::InstrSubType, IBY_FC_ROUTING_RULE::Bepkey, IBY_FC_ROUTING_RULE::InactiveDate, IBY_FC_ROUTING_RULE::FndcptUserProfileCode, IBY_FC_ROUTING_RULE::FndcptUserProfileName, IBY_FC_ROUTING_RULE::PaymentChannelCode, IBY_FC_ROUTING_RULE::StartDate, IBY_FC_ROUTING_RULE::EndDate, IBY_FC_ROUTING_RULE::Suffix, IBY_FC_ROUTING_RULE::Key1, IBY_FC_ROUTING_RULE::EndDateDsp, IBY_FC_ROUTING_RULE::TokenizationRoutingFlag -->

Create and update are source-supported. Preserve exact alternate-key identities; end dating is an update, not physical deletion. Source support does not imply that every exported field is a business input. Read the per-field create/update dispositions before changing any field.

## Read Order

Read this task manifest and its six resource files. For task-routed imports, use the installed core.data-loader and Task Hook workflow. When Task Hook returns ready, read its returned executionGuide and rule plan, then evaluate the applicable task rules in the required order through their declared anchors. Registry readiness alone is not completed validation. Do not require a developer-only authoring planner or substitute an independently constructed validation result. Run Book owns inputs and orchestration; the active core owns preview, approval and imports.

## Reference and deployment boundaries

Use the current target's exact-task export and template. Reference availability and authorization must be checked in that target; documentation alone does not establish deployment equivalence. Preserve unchanged same-environment reference values. Stop only the affected new or changed selection when its required identity or eligibility evidence is unavailable.

SOURCEPROD uses the governed taxonomy applicationLOV route and its numeric alternativeId. PAYER resolution covers PERSON and ORGANIZATION through the declared hub endpoints, using exact PartyNumber and returning PartyId. Other requested party types require an additional qualified identity route. Receipt methods require both exact identity and the bank/class eligibility checks in the reference guide.

## Data Loader interface boundary

Invoke the installed core.data-loader skill through its declared inputs and outputs. Supply the selected task identity, FSM mode, empty businessObject, source artifacts and task rules. The installed core owns session mode, task validation, preview, approval, serialization, submission, monitoring and result reporting. This task must not call private loader Python functions, instantiate session internals, persist or reconstruct approval envelopes, or require a ZIP digest before approval. Respect the installed workflow: 26.10 may use its documented file-based handoff; main uses a live interactive session. Never mix the two protocols. The task adapter is an offline package/validation utility, not a loader replacement or submission interface.

## Payment account dependency and ownership

For a new or changed account, obtain a fresh complete Manage Payment Systems export. Match exact Suffix and ancestor-scoped Key1. This proves membership, not the owning payee. After first use, inspect the selected Internal Payee's payment-system account table and retain target-bound read-only evidence. Include any first-use ownership assignment in the approved preview. An execution surface without UI access must obtain that evidence from an authorized operator and disclose the assisted handoff.

## Mapping creation

For ORA_IBY_FC_INT_PAYEE_MAP creation, provide Payeeid, OrgType and BuName in targetKey. An empty values object is permitted only when all declared create fields are key fields and all required fields are keys. Duplicate, parent, dependency and ownership checks still apply. BusinessUnitId is not an established create input.

## Public reference documentation

These links describe public schemas and APIs. Follow the task rules for matching, eligibility and current-target verification; public API access alone does not establish eligibility.

| Documentation | Link |
|---|---|
| IBY_ACCPPMTMTHD | https://docs.oracle.com/en/cloud/saas/financials/26d/oedmf/ibyaccppmtmthd-12766.html#ibyaccppmtmthd-12766 |
| IBY_DEFAULT_BEP | https://docs.oracle.com/en/cloud/saas/financials/26d/oedmf/ibydefaultbep-12770.html#ibydefaultbep-12770 |
| IBY_FNDCPT_PAYEE_APPL | https://docs.oracle.com/en/cloud/saas/financials/26d/oedmf/ibyfndcptpayeeappl-12772.html#ibyfndcptpayeeappl-12772 |
| IBY_PAYEE | https://docs.oracle.com/en/cloud/saas/financials/26d/oedmf/ibypayee-12774.html#ibypayee-12774 |
| IBY_PMTMTHD_CONDITIONS | https://docs.oracle.com/en/cloud/saas/financials/26d/oedmf/ibypmtmthdconditions-12778.html#ibypmtmthdconditions-12778 |
| IBY_ROUTINGINFO | https://docs.oracle.com/en/cloud/saas/financials/26d/oedmf/ibyroutinginfo-12780.html#ibyroutinginfo-12780 |
| Get business units (26D) | https://docs.oracle.com/en/cloud/saas/financials/26d/farfa/op-finbusinessunitslov-get.html |
| REST API for Oracle Fusion Cloud Financials - Get all bank accounts | https://docs.oracle.com/en/cloud/saas/financials/26d/farfa/op-cashbankaccounts-get.html |
| REST API for Oracle Fusion Cloud Financials - Get all banks | https://docs.oracle.com/en/cloud/saas/financials/26d/farfa/op-cashbanks-get.html |
| Get standard lookup codes (26D) | https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/op-http-servername-fscmrestapi-resources-11.13.18.05-standardlookups-lookuptype-child-lookupcodes-get.html |
| REST API for Oracle Fusion Cloud Financials - Get all currencies | https://docs.oracle.com/en/cloud/saas/financials/26d/farfa/op-preferredcurrencieslov-get.html |
| REST API for Oracle Fusion Cloud Financials - Get all receipt method details | https://docs.oracle.com/en/cloud/saas/financials/26d/farfa/op-receiptmethods-get.html |
| REST API for Common Features in Oracle Fusion Cloud Applications - Get all territories | https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/op-servername-fscmrestapi-resources-11.13.18.05-territorieslov-get.html |
