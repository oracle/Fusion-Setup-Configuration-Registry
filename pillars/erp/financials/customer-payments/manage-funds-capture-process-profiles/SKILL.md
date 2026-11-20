---
skill_id: "erp.financials.customer-payments.manage-funds-capture-process-profiles"
name: "Manage Funds Capture Process Profiles Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Funds Capture Process Profiles under the Customer Payments functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Customer Payments"
functional_area_code: "ORA_FIN_CUSTOMER_PAYMENTS"
task_code: "IBY_MANAGE_FUNDS_CAPTURE_PROCESS_PROFILES"
task_name: "Manage Funds Capture Process Profiles"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/customer-payments/manage-funds-capture-process-profiles/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/customer-payments/manage-funds-capture-process-profiles/current/"
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

# Manage Funds Capture Process Profiles Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Funds Capture Process Profiles` under `Customer Payments`.

## Setup Task Skill Contract

- task_code: `IBY_MANAGE_FUNDS_CAPTURE_PROCESS_PROFILES`
- task_name: `Manage Funds Capture Process Profiles`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Funds Capture Process Profiles` under `Customer Payments`.

## Setup Task Metadata

- Task name: `Manage Funds Capture Process Profiles`
- Task code: `IBY_MANAGE_FUNDS_CAPTURE_PROCESS_PROFILES`
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
- Functional area / Setup Object: `Customer Payments`
- Setup task name: `Manage Funds Capture Process Profiles`
- Setup task code: `IBY_MANAGE_FUNDS_CAPTURE_PROCESS_PROFILES`




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

## Task workflow and boundaries


<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: IBY_FC_PROCESS_PROFILE::AutomaticPnSubmitFlag, IBY_FC_PROCESS_PROFILE::Description, IBY_FC_PROCESS_PROFILE::EndDate, IBY_FC_PROCESS_PROFILE::EndDateDisp, IBY_FC_PROCESS_PROFILE::ExternalSettlementFlag, IBY_FC_PROCESS_PROFILE::GroupByIntBankAccount, IBY_FC_PROCESS_PROFILE::GroupByLegalEntity, IBY_FC_PROCESS_PROFILE::GroupByOrg, IBY_FC_PROCESS_PROFILE::GroupBySettlementCurr, IBY_FC_PROCESS_PROFILE::GroupBySettlementDate, IBY_FC_PROCESS_PROFILE::InactiveDate, IBY_FC_PROCESS_PROFILE::LimitByAmtCurr, IBY_FC_PROCESS_PROFILE::LimitByExchRateType, IBY_FC_PROCESS_PROFILE::LimitBySettlementNum, IBY_FC_PROCESS_PROFILE::LimitByTotalAmt, IBY_FC_PROCESS_PROFILE::OnlineAuthAckRdrCode, IBY_FC_PROCESS_PROFILE::OnlineAuthFormatCode, IBY_FC_PROCESS_PROFILE::OnlineAuthTransPrtclCode, IBY_FC_PROCESS_PROFILE::OverridePayerDeliveryFlag, IBY_FC_PROCESS_PROFILE::PayerNotificationCondition, IBY_FC_PROCESS_PROFILE::PayerNotificationDelMethod, IBY_FC_PROCESS_PROFILE::PayerNotificationFormat, IBY_FC_PROCESS_PROFILE::PayerNotifyInvoicesCount, IBY_FC_PROCESS_PROFILE::QueryAckRdrCode, IBY_FC_PROCESS_PROFILE::QueryFormatCode, IBY_FC_PROCESS_PROFILE::QueryTransPrtclCode, IBY_FC_PROCESS_PROFILE::SettlementAckRdrCode, IBY_FC_PROCESS_PROFILE::SettlementCompletePoint, IBY_FC_PROCESS_PROFILE::SettlementFileDirectory, IBY_FC_PROCESS_PROFILE::SettlementFileExtension, IBY_FC_PROCESS_PROFILE::SettlementFilePrefix, IBY_FC_PROCESS_PROFILE::SettlementFormatCode, IBY_FC_PROCESS_PROFILE::SettlementTransPrtclCode, IBY_FC_PROCESS_PROFILE::StartDate, IBY_FC_PROCESS_PROFILE::Suffix, IBY_FC_PROCESS_PROFILE::SysCcProfileCode, IBY_FC_PROCESS_PROFILE::SysCcProfileName, ORA_IBY_FC_CREDIT_CARD_PROFILE::EndDate, ORA_IBY_FC_CREDIT_CARD_PROFILE::InactiveDate, ORA_IBY_FC_CREDIT_CARD_PROFILE::Key1, ORA_IBY_FC_CREDIT_CARD_PROFILE::StartDate, ORA_IBY_FC_CREDIT_CARD_PROFILE::Suffix, ORA_IBY_FC_CREDIT_CARD_PROFILE::SysCcProfileCode, ORA_IBY_FC_CREDIT_CARD_PROFILE::TransmitConfigurationName, ORA_IBY_FC_CREDIT_CARD_PROFILE::TransmitConfigurationName1, ORA_IBY_FC_CREDIT_CARD_PROFILE::TransmitConfigurationName2, ORA_IBY_FC_CREDIT_CARD_PROFILE::UserCcProfileCode, ORA_IBY_FC_CREDIT_CARD_PROFILE::UserCcProfileName, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::AutomaticPnSubmitFlag, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::Description, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::EndDate, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::EndDateDisp, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::ExternalSettlementFlag, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::GroupByIntBankAccount, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::GroupByLegalEntity, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::GroupByOrg, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::GroupBySettlementCurr, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::GroupBySettlementDate, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::InactiveDate, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::LimitByAmtCurr, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::LimitByExchRateType, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::LimitBySettlementNum, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::LimitByTotalAmt, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::OnlineDebAckRdrCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::OnlineDebFormatCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::OnlineDebTransPrtclCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::OverridePayerDeliveryFlag, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::PayerNotificationCondition, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::PayerNotificationDelMethod, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::PayerNotificationFormat, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::PayerNotifyInvoicesCount, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::QueryAckRdrCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::QueryFormatCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::QueryTransPrtclCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementAckRdrCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementCompletePoint, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementFileDirectory, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementFileExtension, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementFilePrefix, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementFormatCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementReqFlag, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementTransPrtclCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::StartDate, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::Suffix, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SysDcProfileCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SysDcProfileName, ORA_IBY_FC_SYS_EFT_PROFILE::AccompanyLetterFormat, ORA_IBY_FC_SYS_EFT_PROFILE::AutomaticPnSubmitFlag, ORA_IBY_FC_SYS_EFT_PROFILE::BatchBookingFlag, ORA_IBY_FC_SYS_EFT_PROFILE::Description, ORA_IBY_FC_SYS_EFT_PROFILE::EndDate, ORA_IBY_FC_SYS_EFT_PROFILE::EndDateDisp, ORA_IBY_FC_SYS_EFT_PROFILE::ExternalSettlementFlag, ORA_IBY_FC_SYS_EFT_PROFILE::FundsXferAckRdrCode, ORA_IBY_FC_SYS_EFT_PROFILE::FundsXferFormatCode, ORA_IBY_FC_SYS_EFT_PROFILE::FundsXferTransPrtclCode, ORA_IBY_FC_SYS_EFT_PROFILE::GroupByIntBankAccount, ORA_IBY_FC_SYS_EFT_PROFILE::GroupByLegalEntity, ORA_IBY_FC_SYS_EFT_PROFILE::GroupByOrg, ORA_IBY_FC_SYS_EFT_PROFILE::GroupBySettlementCurr, ORA_IBY_FC_SYS_EFT_PROFILE::GroupBySettlementDate, ORA_IBY_FC_SYS_EFT_PROFILE::InactiveDate, ORA_IBY_FC_SYS_EFT_PROFILE::LimitByAmtCurr, ORA_IBY_FC_SYS_EFT_PROFILE::LimitByExchRateType, ORA_IBY_FC_SYS_EFT_PROFILE::LimitBySettlementNum, ORA_IBY_FC_SYS_EFT_PROFILE::LimitByTotalAmt, ORA_IBY_FC_SYS_EFT_PROFILE::Localinstr, ORA_IBY_FC_SYS_EFT_PROFILE::LogicalGroupingMode, ORA_IBY_FC_SYS_EFT_PROFILE::OverridePayerDeliveryFlag, ORA_IBY_FC_SYS_EFT_PROFILE::PayerNotificationCondition, ORA_IBY_FC_SYS_EFT_PROFILE::PayerNotificationDelMethod, ORA_IBY_FC_SYS_EFT_PROFILE::PayerNotificationFormat, ORA_IBY_FC_SYS_EFT_PROFILE::PayerNotifyInvoicesCount, ORA_IBY_FC_SYS_EFT_PROFILE::PurposeCode, ORA_IBY_FC_SYS_EFT_PROFILE::QueryAckRdrCode, ORA_IBY_FC_SYS_EFT_PROFILE::QueryFormatCode, ORA_IBY_FC_SYS_EFT_PROFILE::QueryTransPrtclCode, ORA_IBY_FC_SYS_EFT_PROFILE::ServiceLevel, ORA_IBY_FC_SYS_EFT_PROFILE::SettleRequireVrfyFlag, ORA_IBY_FC_SYS_EFT_PROFILE::SettlementCompletePoint, ORA_IBY_FC_SYS_EFT_PROFILE::SettlementFileDirectory, ORA_IBY_FC_SYS_EFT_PROFILE::SettlementFileExtension, ORA_IBY_FC_SYS_EFT_PROFILE::SettlementFilePrefix, ORA_IBY_FC_SYS_EFT_PROFILE::StartDate, ORA_IBY_FC_SYS_EFT_PROFILE::Suffix, ORA_IBY_FC_SYS_EFT_PROFILE::SysEftProfileCode, ORA_IBY_FC_SYS_EFT_PROFILE::SysEftProfileName, ORA_IBY_FC_SYS_EFT_PROFILE::VerifyAckRdrCode, ORA_IBY_FC_SYS_EFT_PROFILE::VerifyFormatCode, ORA_IBY_FC_SYS_EFT_PROFILE::VerifyTransPrtclCode, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::EndDate, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::InactiveDate, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::Key1, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::StartDate, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::Suffix, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::SysDcProfileCode, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::TransmitConfigurationName, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::TransmitConfigurationName1, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::TransmitConfigurationName2, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::UserDcProfileCode, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::UserDcProfileName, ORA_IBY_FC_USER_EFT_PROFILE::EndDate, ORA_IBY_FC_USER_EFT_PROFILE::InactiveDate, ORA_IBY_FC_USER_EFT_PROFILE::Key1, ORA_IBY_FC_USER_EFT_PROFILE::StartDate, ORA_IBY_FC_USER_EFT_PROFILE::Suffix, ORA_IBY_FC_USER_EFT_PROFILE::SysEftProfileCode, ORA_IBY_FC_USER_EFT_PROFILE::TransmitConfigurationName, ORA_IBY_FC_USER_EFT_PROFILE::TransmitConfigurationName1, ORA_IBY_FC_USER_EFT_PROFILE::TransmitConfigurationName2, ORA_IBY_FC_USER_EFT_PROFILE::UserEftProfileCode, ORA_IBY_FC_USER_EFT_PROFILE::UserEftProfileName -->
<!-- fscr-update-fields: IBY_FC_PROCESS_PROFILE::AutomaticPnSubmitFlag, IBY_FC_PROCESS_PROFILE::Description, IBY_FC_PROCESS_PROFILE::EndDate, IBY_FC_PROCESS_PROFILE::EndDateDisp, IBY_FC_PROCESS_PROFILE::ExternalSettlementFlag, IBY_FC_PROCESS_PROFILE::GroupByIntBankAccount, IBY_FC_PROCESS_PROFILE::GroupByLegalEntity, IBY_FC_PROCESS_PROFILE::GroupByOrg, IBY_FC_PROCESS_PROFILE::GroupBySettlementCurr, IBY_FC_PROCESS_PROFILE::GroupBySettlementDate, IBY_FC_PROCESS_PROFILE::InactiveDate, IBY_FC_PROCESS_PROFILE::LimitByAmtCurr, IBY_FC_PROCESS_PROFILE::LimitByExchRateType, IBY_FC_PROCESS_PROFILE::LimitBySettlementNum, IBY_FC_PROCESS_PROFILE::LimitByTotalAmt, IBY_FC_PROCESS_PROFILE::OnlineAuthAckRdrCode, IBY_FC_PROCESS_PROFILE::OnlineAuthFormatCode, IBY_FC_PROCESS_PROFILE::OnlineAuthTransPrtclCode, IBY_FC_PROCESS_PROFILE::OverridePayerDeliveryFlag, IBY_FC_PROCESS_PROFILE::PayerNotificationCondition, IBY_FC_PROCESS_PROFILE::PayerNotificationDelMethod, IBY_FC_PROCESS_PROFILE::PayerNotificationFormat, IBY_FC_PROCESS_PROFILE::PayerNotifyInvoicesCount, IBY_FC_PROCESS_PROFILE::QueryAckRdrCode, IBY_FC_PROCESS_PROFILE::QueryFormatCode, IBY_FC_PROCESS_PROFILE::QueryTransPrtclCode, IBY_FC_PROCESS_PROFILE::SettlementAckRdrCode, IBY_FC_PROCESS_PROFILE::SettlementCompletePoint, IBY_FC_PROCESS_PROFILE::SettlementFileDirectory, IBY_FC_PROCESS_PROFILE::SettlementFileExtension, IBY_FC_PROCESS_PROFILE::SettlementFilePrefix, IBY_FC_PROCESS_PROFILE::SettlementFormatCode, IBY_FC_PROCESS_PROFILE::SettlementTransPrtclCode, IBY_FC_PROCESS_PROFILE::StartDate, IBY_FC_PROCESS_PROFILE::Suffix, IBY_FC_PROCESS_PROFILE::SysCcProfileName, ORA_IBY_FC_CREDIT_CARD_PROFILE::EndDate, ORA_IBY_FC_CREDIT_CARD_PROFILE::InactiveDate, ORA_IBY_FC_CREDIT_CARD_PROFILE::Key1, ORA_IBY_FC_CREDIT_CARD_PROFILE::StartDate, ORA_IBY_FC_CREDIT_CARD_PROFILE::Suffix, ORA_IBY_FC_CREDIT_CARD_PROFILE::SysCcProfileCode, ORA_IBY_FC_CREDIT_CARD_PROFILE::TransmitConfigurationName, ORA_IBY_FC_CREDIT_CARD_PROFILE::TransmitConfigurationName1, ORA_IBY_FC_CREDIT_CARD_PROFILE::TransmitConfigurationName2, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::AutomaticPnSubmitFlag, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::Description, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::EndDate, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::EndDateDisp, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::ExternalSettlementFlag, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::GroupByIntBankAccount, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::GroupByLegalEntity, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::GroupByOrg, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::GroupBySettlementCurr, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::GroupBySettlementDate, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::InactiveDate, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::LimitByAmtCurr, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::LimitByExchRateType, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::LimitBySettlementNum, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::LimitByTotalAmt, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::OnlineDebAckRdrCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::OnlineDebFormatCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::OnlineDebTransPrtclCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::OverridePayerDeliveryFlag, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::PayerNotificationCondition, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::PayerNotificationDelMethod, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::PayerNotificationFormat, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::PayerNotifyInvoicesCount, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::QueryAckRdrCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::QueryFormatCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::QueryTransPrtclCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementAckRdrCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementCompletePoint, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementFileDirectory, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementFileExtension, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementFilePrefix, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementFormatCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementReqFlag, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SettlementTransPrtclCode, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::StartDate, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::Suffix, ORA_IBY_FC_SYS_DEBIT_CARD_PROFILE::SysDcProfileName, ORA_IBY_FC_SYS_EFT_PROFILE::AccompanyLetterFormat, ORA_IBY_FC_SYS_EFT_PROFILE::AutomaticPnSubmitFlag, ORA_IBY_FC_SYS_EFT_PROFILE::BatchBookingFlag, ORA_IBY_FC_SYS_EFT_PROFILE::Description, ORA_IBY_FC_SYS_EFT_PROFILE::EndDate, ORA_IBY_FC_SYS_EFT_PROFILE::EndDateDisp, ORA_IBY_FC_SYS_EFT_PROFILE::ExternalSettlementFlag, ORA_IBY_FC_SYS_EFT_PROFILE::FundsXferAckRdrCode, ORA_IBY_FC_SYS_EFT_PROFILE::FundsXferFormatCode, ORA_IBY_FC_SYS_EFT_PROFILE::FundsXferTransPrtclCode, ORA_IBY_FC_SYS_EFT_PROFILE::GroupByIntBankAccount, ORA_IBY_FC_SYS_EFT_PROFILE::GroupByLegalEntity, ORA_IBY_FC_SYS_EFT_PROFILE::GroupByOrg, ORA_IBY_FC_SYS_EFT_PROFILE::GroupBySettlementCurr, ORA_IBY_FC_SYS_EFT_PROFILE::GroupBySettlementDate, ORA_IBY_FC_SYS_EFT_PROFILE::InactiveDate, ORA_IBY_FC_SYS_EFT_PROFILE::LimitByAmtCurr, ORA_IBY_FC_SYS_EFT_PROFILE::LimitByExchRateType, ORA_IBY_FC_SYS_EFT_PROFILE::LimitBySettlementNum, ORA_IBY_FC_SYS_EFT_PROFILE::LimitByTotalAmt, ORA_IBY_FC_SYS_EFT_PROFILE::Localinstr, ORA_IBY_FC_SYS_EFT_PROFILE::LogicalGroupingMode, ORA_IBY_FC_SYS_EFT_PROFILE::OverridePayerDeliveryFlag, ORA_IBY_FC_SYS_EFT_PROFILE::PayerNotificationCondition, ORA_IBY_FC_SYS_EFT_PROFILE::PayerNotificationDelMethod, ORA_IBY_FC_SYS_EFT_PROFILE::PayerNotificationFormat, ORA_IBY_FC_SYS_EFT_PROFILE::PayerNotifyInvoicesCount, ORA_IBY_FC_SYS_EFT_PROFILE::PurposeCode, ORA_IBY_FC_SYS_EFT_PROFILE::QueryAckRdrCode, ORA_IBY_FC_SYS_EFT_PROFILE::QueryFormatCode, ORA_IBY_FC_SYS_EFT_PROFILE::QueryTransPrtclCode, ORA_IBY_FC_SYS_EFT_PROFILE::ServiceLevel, ORA_IBY_FC_SYS_EFT_PROFILE::SettleRequireVrfyFlag, ORA_IBY_FC_SYS_EFT_PROFILE::SettlementCompletePoint, ORA_IBY_FC_SYS_EFT_PROFILE::SettlementFileDirectory, ORA_IBY_FC_SYS_EFT_PROFILE::SettlementFileExtension, ORA_IBY_FC_SYS_EFT_PROFILE::SettlementFilePrefix, ORA_IBY_FC_SYS_EFT_PROFILE::StartDate, ORA_IBY_FC_SYS_EFT_PROFILE::Suffix, ORA_IBY_FC_SYS_EFT_PROFILE::SysEftProfileName, ORA_IBY_FC_SYS_EFT_PROFILE::VerifyAckRdrCode, ORA_IBY_FC_SYS_EFT_PROFILE::VerifyFormatCode, ORA_IBY_FC_SYS_EFT_PROFILE::VerifyTransPrtclCode, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::EndDate, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::InactiveDate, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::Key1, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::StartDate, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::Suffix, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::SysDcProfileCode, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::TransmitConfigurationName, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::TransmitConfigurationName1, ORA_IBY_FC_USER_DEBIT_CARD_PROFILE::TransmitConfigurationName2, ORA_IBY_FC_USER_EFT_PROFILE::EndDate, ORA_IBY_FC_USER_EFT_PROFILE::InactiveDate, ORA_IBY_FC_USER_EFT_PROFILE::Key1, ORA_IBY_FC_USER_EFT_PROFILE::StartDate, ORA_IBY_FC_USER_EFT_PROFILE::Suffix, ORA_IBY_FC_USER_EFT_PROFILE::SysEftProfileCode, ORA_IBY_FC_USER_EFT_PROFILE::TransmitConfigurationName, ORA_IBY_FC_USER_EFT_PROFILE::TransmitConfigurationName1, ORA_IBY_FC_USER_EFT_PROFILE::TransmitConfigurationName2 -->

This task owns credit-card, debit-card and bank-account funds capture process profiles and their account children. Financials → Customer Payments is the canonical owner; cross-listing under Student Management and Public Sector does not create another implementation. Shared payment systems, accounts, protocols, formats and transmission configurations are prerequisites, not mutation targets.

Create and update are supported with separate field contracts. End-date changes are updates. Physical deletion is unqualified. Primary keys and three FSM alternate user-profile names cannot be renamed. Translations remain package/reconciliation dependencies. Do not reduce ordinary update support to the easiest test field.

Read ora-resource/ora_input_validation.md, ora_dependency_readiness.md, ora_reference_lookups.md, ora_defaulting_rules.md, ora_design_enforcement.md and ora_error_handling.md. The compiled ora_rule_registry.json defines the local validation graph. Detailed field contracts and stable requirement references are in references/field-contracts.json, references/resolver-contracts.json and references/source-register.json.

Use core.runbook for input orchestration and invoke core.data-loader through the active checkout's documented interface for preparation, preview, approval and submission. Design confirmation is separate from import approval. The task's offline runtime does not authorize a mutation. Missing approval, changed candidate, uncertain prior submission, or unavailable supported route stops submission. No direct browser import, SQL, invented endpoint or automatic retry is permitted.

An unresolved business field is evidence_unresolved, not proven invalid. Apply every known deterministic rule first. For an eligible unresolved field, disclose the exact gap and expected FSM diagnostic surface and obtain explicit acceptance for that exact candidate before normal preview and import approval. This never bypasses package integrity, target identity, parent ownership, key/audit protection, a proven-invalid rule, an explicitly unsupported operation/field, environment authorization or candidate-specific submission approval. Stop after rejection; no automatic retry.

For updates obtain a fresh same-task export and prove exactly one existing primary-key match before building. Preserve unrelated rows and unchanged cells; mapped blanks serialize explicit nulls. An absent target can create a row; import matching is not an update-only guard. Require explicit root and child Suffix and child Key1, and verify their payment-system coherence. Preserve exact template headers, trailing empty fields, metadata and hierarchy. The three import roots have nested processing branches and separate family processing; no package-wide atomicity is promised.

After approved application execution, reconcile exact requested persisted values against a fresh export and verify preservation. Do not require transient display-only values to persist. Report application errors honestly and return for a new business decision after rejection. End-date retirement is not physical deletion or baseline restoration for a created record.


## Functional task requirements

- Three processing families use distinct root/user nodes and portable key mappings; preserve explicit Suffix and child Key1 relationships.
- XML target matching uses owning keys and rejects multiple rows; no match can create a row, so an update must first prove exact target existence.
- Blank mapped CSV fields become XML nulls; preserve baseline values for untouched fields. The task runtime permits explicit clearing of optional credit-card PayerNotificationDelMethod only; other nullable-field behavior remains field-specific.
- Three user-profile names are non-updatable FSM alternate keys; translation rows are retained package dependencies, not independently exposed operation targets.
- DFF storage metadata does not establish deployed contexts or value sets; resolve requested DFF meaning from current configuration before applying changes.
- Separate family processing do not establish all-or-nothing import; physical-delete signaling is unqualified and end-dating must not be presented as deletion.
- Node sequence numbers are export-local; preserve metadata from the actual baseline and validate exact XML ownership.


## Active Data Loader interface

Resolve the selected checkout's core.data-loader SKILL.md at each live handoff and follow its documented interface; do not import its Python modules, call private helpers, or infer compatibility from function names. Task identity, FSM routing, local rule results and requested business changes are the task contract. The loader owns transport, approval representation, session lifetime, permitted retention and status handling.

Keep task design review separate from the Data Loader approval preview. Display the active loader's approval Markdown exactly as returned, without adding task details or a task-specific approval keyword. Present business design and evidence during the preceding design review.

The task runtime's file-based normalize/build/validate/reconcile/rollback commands are offline authoring tools, not a Data Loader session bridge. A live interactive session must evaluate this task's rules from the captured records/native sources exposed by the documented protocol; never reopen source files or persist session data to feed the offline CLI. Submit ordered rule results through the active public protocol. A required rule that cannot be evaluated from permitted inputs blocks that handoff.

If the active loader requires an interactive session, retain that process and its connection, honor memory-only retention, and obtain fresh validation and approval after session loss or expiry. Never substitute saved envelopes, replay prior approvals, or fall back to a legacy submission command. If the active checkout instead documents file-based approval, follow only that interface. Unsupported host/tester interfaces block live execution without changing business-operation support. Offline artifacts are not live approval records. Return initiation as required by the active loader; later authorized status and reconciliation use the original accepted identity.
