---
skill_id: "erp.financials.payments.manage-transmission-configurations"
name: "Manage Transmission Configurations Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Transmission Configurations under the Payments functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payments"
functional_area_code: "ORA_FIN_PAYMENTS"
task_code: "IBY_MANAGE_TRANSMISSION_CONFIGURATIONS"
task_name: "Manage Transmission Configurations"
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
version: "0.2.0"
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
  - "core.auth.fusion-oauth-authentication"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payments/manage-transmission-configurations/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payments/manage-transmission-configurations/current/"
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
side_effects:
  - "Downloads an already-authorized MTC export through the shared export engine and writes only sanitized local artifacts."
required_privileges: []
---

# Manage Transmission Configurations Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Transmission Configurations` under `Payments`.

## Setup Task Skill Contract

- task_code: `IBY_MANAGE_TRANSMISSION_CONFIGURATIONS`
- task_name: `Manage Transmission Configurations`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Transmission Configurations` under `Payments`.

## Setup Task Metadata

- Task name: `Manage Transmission Configurations`
- Task code: `IBY_MANAGE_TRANSMISSION_CONFIGURATIONS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Use `shared.setup-export.task-level-export` for governed export creation. Before download/persistence, apply the task-owned [sensitive-field policy](ora-resource/ora_sensitive_fields.md) and `scripts/sanitize_export.py`; do not save raw MTC data or process logs to the project.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Financials`
- Functional area / Setup Object: `Payments`
- Setup task name: `Manage Transmission Configurations`
- Setup task code: `IBY_MANAGE_TRANSMISSION_CONFIGURATIONS`




## Sensitive-field boundary

Read [Sensitive setup: manual completion policy](ora-resource/ora_sensitive_fields.md)
before collecting inputs, exporting, normalizing or importing this task. Warn
users to enter passwords, secrets and keys in Payments UI. Omit supplied
sensitive fields without repeating values and show the generated `manualSteps`
both before approval and after import. Only a newly created `SECURE_FTP_GET` or
`SECURE_FTP_PUT` configuration receives the explicit `USERNAME=changeit`
placeholder. Never overwrite an existing username/credential with it.

The task-owned policy and runtime enforce this boundary; neither customer input
nor approval can override it. Revalidate the final ZIP, including supplied ZIPs,
before Run Book / Data Loader submission. Manual credential completion remains
outstanding after a successful non-sensitive import.

## Source-Backed Task Behavior



- Create and update user transmission configurations, their parameter values, and configuration translations. Protocol/parameter definitions and their translations are preserved dependencies, not implementor edit targets in this task. Use exact exported business keys. Do not rename/reparent keys, convert an existing configuration's protocol, or delete records through this adapter.
- Resolve the exact existing target protocol and its parameters from the governed task export. Seed protocol codes include `HTTP_GET`, `HTTP_POST`, and `OAUTH_2_0`; transport descriptions such as HTTPS do not establish a different protocol code. Preserve inherited parent columns and derive new child context from the exact owning configuration and protocol.
- Require an explicit start date and end date for configuration creation. The reviewed EO uses current database date and the open-ended sentinel `4712-12-31`; do not guess a business start date offline. Keep `EndDateDsp` blank for the sentinel and equal to a finite end date. Source: SRC-CODE-CONFIG-DATES, SRC-CODE-EO-CONFIG.
- Populate only the value column selected by the target parameter type: `VARCHAR2`, `NUMBER`, or `DATE`. Enforce reviewed required/secured metadata and the sensitive-field policy, preserve dynamic metadata, and reject masked text in an import candidate. Preserve the target-specific `HTTP_MPART.NO_ACK` row unchanged pending metadata qualification. Source: SRC-CODE-PARAM-TYPES and reviewed protocol seed evidence.
- The OAuth protocol is seeded; OAuth configurations are user created. `HTTP_GET`/`HTTP_POST` parameter `OAUTH_TRANSMIT_CONFIG` stores the selected OAuth configuration ID in `TransmitNumberValue`. The current export omits the referenced OAuth name/ID mapping, and the reviewed import helper does not remap this scalar. Preserve an unchanged same-target reference; block new or changed assignment with `MTC-OAUTH-01`. Name-based export/import resolution is an accepted open product enhancement, not implemented functionality.
- Resolve requested tunnel names against target configuration context and retain FSM import-time validation. Do not call the deprecated, discoverable-but-unsupported transmission SOAP service as a runtime lookup. An unavailable optional public preflight does not replace or remove the governed FSM validation path.
- Review all crypto references on every touched configuration, including unchanged ones. Configuration DML checks credential type/name and can register a missing key from a Payments UCM file, with conditional file consumption and side effects not guaranteed to roll back with database changes. Existing type/name evidence does not prove password, subtype, expiry, or connectivity. Physical exported credential paths are not portable aliases. Source: SRC-CODE-CONFIG-DML, SRC-CODE-CREDENTIAL-UTIL.
- Retain exact configuration, parameter, credential type, sanitized target baseline hash, and non-secret UI evidence in the governed prerequisite record. Do not retain withheld aliases or credential values. Intentional UCM registration requires manual Payments UI completion. Neither the task nor its offline adapter authenticates, registers keys, imports, or transmits files automatically.
- Use the compiled [rule registry](ora-resource/ora_rule_registry.json) and its six authored resources for task planning and validation. Normalize the governed design, then validate any generated or supplied candidate with [the task adapter](scripts/fsm_task_adapter.py) before Data Loader submission. Preserve unspecified non-sensitive fields, unrelated rows and target metadata. Credential values are withheld from baseline artifacts and excluded from candidates; reports never treat masked equality as proof of credential preservation.
- Route live changes through the Run Book and `core.data-loader`, with normal environment authorization, immutable preview, candidate-specific approval, one submission, diagnostics, and fresh-export reconciliation. Offline tests and simulated persisted exports do not establish live behavior or grant import, transmission, commit, or push authority.

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

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: IBY_TRANSMISSION_CONFIGURATION::TransmitProtocolCode, IBY_TRANSMISSION_CONFIGURATION::TransmitProtocolName, IBY_TRANSMISSION_CONFIGURATION::TransmitConfigurationName, IBY_TRANSMISSION_CONFIGURATION::StartDate, IBY_TRANSMISSION_CONFIGURATION::EndDate, IBY_TRANSMISSION_CONFIGURATION::InactiveDate, IBY_TRANSMISSION_CONFIGURATION::TunnelTransmitConfigurationName, IBY_TRANSMISSION_CONFIGURATION::EndDateDsp, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::Language, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::SourceLang, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::TransmitConfigurationName, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitParameterCode, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitVarchar2Value, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitNumberValue, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitDateValue, IBY_TRANSMISSION_CONFIGURATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolCode, IBY_TRANSMISSION_CONFIGURATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolName, IBY_TRANSMISSION_CONFIGURATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitCodeLanguage, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolCode, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolName, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitCodeLanguage, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::IBY_TRANSMISSION_CONFIGURATION.TransmitConfigurationName, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolCode, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolName, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitCodeLanguage, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::IBY_TRANSMISSION_CONFIGURATION.TransmitConfigurationName -->
<!-- fscr-update-fields: IBY_TRANSMISSION_CONFIGURATION::StartDate, IBY_TRANSMISSION_CONFIGURATION::EndDate, IBY_TRANSMISSION_CONFIGURATION::InactiveDate, IBY_TRANSMISSION_CONFIGURATION::TunnelTransmitConfigurationName, IBY_TRANSMISSION_CONFIGURATION::EndDateDsp, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::SourceLang, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::TransmitConfigurationName, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitVarchar2Value, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitNumberValue, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitDateValue -->
