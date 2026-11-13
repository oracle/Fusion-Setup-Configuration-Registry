---
skill_id: "erp.financials.payments.manage-payment-systems"
name: "Manage Payment Systems Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Payment Systems under the Payments functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payments"
functional_area_code: "ORA_FIN_PAYMENTS"
task_code: "IBY_MANAGE_PAYMENT_SYSTEMS"
task_name: "Manage Payment Systems"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payments/manage-payment-systems/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payments/manage-payment-systems/current/"
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

# Manage Payment Systems Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Payment Systems` under `Payments`.

## Setup Task Skill Contract

- task_code: `IBY_MANAGE_PAYMENT_SYSTEMS`
- task_name: `Manage Payment Systems`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Payment Systems` under `Payments`.

## Setup Task Metadata

- Task name: `Manage Payment Systems`
- Task code: `IBY_MANAGE_PAYMENT_SYSTEMS`
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
- Setup task name: `Manage Payment Systems`
- Setup task code: `IBY_MANAGE_PAYMENT_SYSTEMS`




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

## Source-reviewed MPS implementation contract

Owner/reviewer: Oracle Fusion Payments / Payments SME and FSCR A-Team reviewers.

Support both create and update within the independent field contracts. Never infer create-only behavior from incomplete update-field evidence. Source-reviewed behavior is not live-qualified behavior. Read the current core task-node execution guide before the compiled registry, then the six owning resources.

1. Resolve the exact task and owning payment system/account from Run Book context.
2. Read references/sensitive-policy.json before processing any option value. Keep credentials out of all generated files, diagnostics and previews. Sensitive or unknown account options require manual UI completion; omit their whole value rows. Do not insert changeit or a blank substitute.
3. Apply references/field-contracts.json independently for create and update. Preserve all 133 evidence dispositions, including unresolved fields. Existing unchanged values are not requested mutations; preserve them only from a matching sanitized baseline when safe.
4. Apply references/entity-operation-contracts.json and retain unchanged parent identities. Account option codes are scoped to their owning system. Root Suffix and account Key1 are matching identities; no renaming or physical deletion.
5. Execute the compiled task rules and conditional lookups. references/reference-contracts.json distinguishes public GET, import resolution/validation and manual UI boundaries. Never invent a public resolver from a table or internal VO.
6. Let core.data-loader own payload processing, immutable preview, approval and submission through its active session contract. The task's offline helper is not an alternative upload path. Follow current memory-only retention requirements; no persisted approval envelope and no automatic retry.
7. For post-import verification, route to shared.setup-export.task-level-export for a fresh export of the exact IBY_MANAGE_PAYMENT_SYSTEMS task, then reconcile intended ordinary changes and unchanged siblings against the matching pre-import baseline. Select the current governed read/export workflow and its prerequisites before execution. Do not expose exported credential values. Imported success alone does not establish business completion; outstanding manual steps keep the task In Progress.

### Identity and preservation

The FSM metadata ObjectShortName owns archive identity; businessObject remains empty for FSM. Use the exact eight-entity package contract and preserve its relationship columns. BankName/HomeCountry reference an existing bank; they never authorize bank-master changes. BU_NAME is the specific name-resolving account option. Other option values use their documented canonical strings.

Blank mapped CSV cells can become explicit XML null. Never use blanks or missing headers to mean unchanged. A nonempty or uncertain root credential blocks the affected serialized root subtree. Omitted sensitive child rows are intended to preserve their existing values; runtime qualification must verify both plaintext and segment-backed cases. Root credential columns have lower research priority, but have not been proven obsolete.

### Scoped gaps

Unresolved fields and target DFF contexts remain visible in field-contracts.json. Eighteen account-choice machine resolvers remain manual. No automatic DATE-valued setting conversion is supported until its exact format is established. Qualification may expand these contracts after evidence review; do not label gaps permanently unsupported.

### Task-owned runtime policy

The runtime loads `references/sensitive-policy.json` and `references/lifecycle-policy.json`; their combined digest binds each normalized blueprint. Sensitive or unclassified account-setting operations become manual UI steps and contribute no CSV row. Manual-only requests produce no importable operation. Mixed requests retain eligible ordinary create/update operations. MPS has no placeholder exception.

Automatic account-setting handling is restricted to BU_NAME and the five documented public lookup options in the policy. Supply BU_NAME through BuName, not a database ID. Supply `optionResolutionEvidence` for each automatic setting operation: operationId, exact targetKey, resolverId, canonicalValue (BuName for BU_NAME), baselineSha256, matchCount=1 and evidenceRef. Public lookup receipts also require enabledAndEffective=true. Obtain the evidence through the selected supported read/UI workflow; this offline adapter does not call a resolver or authenticate. Missing, stale or ambiguous evidence stops the affected automated request. Other option rows remain manual even when their SecuredFlag is N.

An update that changes SecuredFlag/TopologyMgrCode, or root serialization that would remove an existing scheme, requires manual lifecycle handling. Ordinary updates to other eligible systems remain available. Reconciliation checks the ID-backed BuName projection and expected flag-created schemes. Rollback never restores credentials; a change requiring fresh option-resolution evidence must be prepared as a separately validated reverse request rather than reusing a stale receipt.

Evidence-unresolved update fields retain the current governed application-validation override. It cannot bypass known unsupported fields, sensitive-field policy, exact keys, audit restrictions or lifecycle checks. Static validation does not establish live import success or preservation of encrypted rows.

## Source-Backed Task Behavior

- Required create inputs and nonblank writes are enforced by `references/create-input-policy.json`, independently of the portable matching keys. Root name/dates, format dates, explicit account owner type, definition datatype/label/display order, translation label/source language/owning-definition context, and option-specific values must be complete. Only the previously documented new-definition SecuredFlag=N default is materialized; ordinary updates and complete key-only child creates remain supported. The policy digest binds normalization, candidate validation and reconciliation. Sources: SRC-MPS-ADE-003, SRC-MPS-ADE-004, SRC-MPS-META-005, SRC-MPS-META-006, SRC-MPS-META-008, SRC-MPS-META-009, SRC-MPS-META-011, SRC-MPS-META-012, SRC-MPS-META-020, SRC-MPS-META-023, SRC-MPS-META-024, SRC-MPS-ADE-001, SRC-MPS-FW-CSV.

- Create and update use the exact eight-entity package and declared portable composite keys; audit fields are not implementor inputs. Existing unchanged values require a matching safe baseline. Sources: SRC-FSM-PACKAGE, SRC-MPS-ADE-001, SRC-MPS-FW-HELPER.
- Sensitive and unclassified account settings are manual UI operations; omit the complete value row from automatic packages, including rollback. No MPS placeholder exception exists. Sources: SRC-MPS-POLICY, SRC-MPS-ADE-007, SRC-MPS-ADE-008, SRC-MPS-FW-CSV.
- Classify setting values by owning payment system plus option code, reviewed semantics, SecuredFlag, topology and prior sensitivity. SecuredFlag=N or null segment ID does not establish that a value is safe to import. Sources: SRC-MPS-OPTION-006, SRC-MPS-ADE-007, SRC-MPS-ADE-008.
- Any nonempty or uncertain root credential blocks serialization of that owning system's subtree. This is an FSCR preservation boundary, not evidence that the root fields are obsolete. Sources: SRC-MPS-POLICY, SRC-MPS-ADE-005, SRC-MPS-FW-CSV.
- BU_NAME uses BuName and the import service's BusinessUnitPVO resolution; source takes the first match, so obtain evidence of one exact match before packaging. Reconcile the ID-backed BuName projection. Sources: SRC-MPS-ADE-001, SRC-MPS-META-020.
- Five documented public lookup options may use exact canonical codes only with a bound, unique, enabled and date-effective resolution receipt. Other reference-valued settings remain manual until a supported resolver is qualified. Sources: SRC-MPS-META-022, SRC-MPS-DOC-LOOKUPS, SRC-MPS-RESOLVER-004.
- Bank name/country resolution and EO list validators run during governed import; their source declarations do not prove target values or successful execution. Sources: SRC-MPS-ADE-001, SRC-MPS-ADE-004, SRC-MPS-ADE-016.
- Root end date may equal start date; format end date must be later. The root no-end sentinel is 4712-12-31; a UI blank display is not equivalent to a blank CSV field. Sources: SRC-MPS-ADE-003, SRC-MPS-ADE-004, SRC-MPS-META-008, SRC-MPS-META-009.
- Instrument flags synchronize schemes: Y creates/retains, N can remove, and null does nothing. Automatic serialization that would remove an existing scheme stops for manual lifecycle handling; reconciliation checks expected Y-created schemes. Source: SRC-MPS-ADE-005.
- Root URL validation accepts HTTP/HTTPS with length greater than ten when nonblank. Citi character substitution requires Citi-Payables applicability and positional pairing. Sources: SRC-MPS-ADE-005, SRC-MPS-EDM-IBY-BEPINFO.
- Evidence-unresolved update fields retain the exact governed application-validation override; unknown create contracts remain unavailable. An override cannot bypass a known safety, unsupported-field or lifecycle restriction. Sources: references/field-contracts.json, current Data Loader and Builder contracts.
- Whole-row omission is the preservation design, supported by reviewed converter/readXML behavior and offline tests; encrypted/plaintext target preservation and actual create/update success still require separately authorized runtime qualification. Sources: SRC-MPS-FW-CSV, SRC-MPS-FW-READER, SRC-MPS-FW-HELPER.

### Read order

- references/sensitive-policy.json and references/field-contracts.json
- ora-resource/ora_design_enforcement.md
- ora-resource/ora_input_validation.md
- ora-resource/ora_reference_lookups.md
- ora-resource/ora_dependency_readiness.md
- ora-resource/ora_defaulting_rules.md
- ora-resource/ora_error_handling.md
- ora-resource/ora_rule_registry.json

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: IBY_PAYMENT_SYSTEM::Name, IBY_PAYMENT_SYSTEM::Baseurl, IBY_PAYMENT_SYSTEM::Suffix, IBY_PAYMENT_SYSTEM::BepType, IBY_PAYMENT_SYSTEM::OutboundInvalidChars, IBY_PAYMENT_SYSTEM::OutboundReplaceChars, IBY_PAYMENT_SYSTEM::NlsLanguage, IBY_PAYMENT_SYSTEM::StartDate, IBY_PAYMENT_SYSTEM::EndDate, IBY_PAYMENT_SYSTEM::B2BTradingPartnerName, IBY_PAYMENT_SYSTEM::CreditCardFlag, IBY_PAYMENT_SYSTEM::DebitCardFlag, IBY_PAYMENT_SYSTEM::FCBankTransferFlag, IBY_PAYMENT_SYSTEM::FDBankTransferFlag, IBY_PAYMENT_SYSTEM::BankName, IBY_PAYMENT_SYSTEM::HomeCountry, ORA_IBY_PAYMENT_SYSTEM_SCHEME::Pmtschemename, ORA_IBY_PAYMENT_SYSTEM_TRAN::TransmitProtocolCode, ORA_IBY_PAYMENT_SYSTEM_ACC_VAL::AccountOptionCode, ORA_IBY_PAYMENT_SYSTEM_ACC_VAL::AccountOptionValue, ORA_IBY_PAYMENT_SYSTEM_ACC_VAL::BuName, ORA_IBY_PAYMENT_SYSTEM_FORMAT::PaymentFormatCode, ORA_IBY_PAYMENT_SYSTEM_FORMAT::StartDate, ORA_IBY_PAYMENT_SYSTEM_FORMAT::EndDate, ORA_IBY_PAYMENT_SYSTEM_KEY::Ownertype, ORA_IBY_PAYMENT_SYSTEM_KEY::Key1, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::AccountOptionCode, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::AccountOptionDatatype, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::SecuredFlag, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::UniquePerBatchFlag, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::DisplayOrder, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::TokenProfileFlag, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::AccountOptionName, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::AccountOptionCode, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::Language, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::SourceLang, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::AccountOptionName, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::IBY_PAYMENT_SYSTEM.Suffix, ORA_IBY_PAYMENT_SYSTEM_FORMAT::IBY_PAYMENT_SYSTEM.Suffix, ORA_IBY_PAYMENT_SYSTEM_KEY::IBY_PAYMENT_SYSTEM.Suffix, ORA_IBY_PAYMENT_SYSTEM_SCHEME::IBY_PAYMENT_SYSTEM.Suffix, ORA_IBY_PAYMENT_SYSTEM_TRAN::IBY_PAYMENT_SYSTEM.Suffix, ORA_IBY_PAYMENT_SYSTEM_ACC_VAL::IBY_PAYMENT_SYSTEM.Suffix, ORA_IBY_PAYMENT_SYSTEM_ACC_VAL::ORA_IBY_PAYMENT_SYSTEM_KEY.Key1, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::IBY_PAYMENT_SYSTEM.Suffix, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::ORA_IBY_PAYMENT_SYSTEM_ACC_NAME.AccountOptionCode -->
<!-- fscr-update-fields: IBY_PAYMENT_SYSTEM::Name, IBY_PAYMENT_SYSTEM::Baseurl, IBY_PAYMENT_SYSTEM::BepType, IBY_PAYMENT_SYSTEM::OutboundInvalidChars, IBY_PAYMENT_SYSTEM::OutboundReplaceChars, IBY_PAYMENT_SYSTEM::NlsLanguage, IBY_PAYMENT_SYSTEM::StartDate, IBY_PAYMENT_SYSTEM::EndDate, IBY_PAYMENT_SYSTEM::B2BTradingPartnerName, IBY_PAYMENT_SYSTEM::CreditCardFlag, IBY_PAYMENT_SYSTEM::DebitCardFlag, IBY_PAYMENT_SYSTEM::FCBankTransferFlag, IBY_PAYMENT_SYSTEM::FDBankTransferFlag, IBY_PAYMENT_SYSTEM::BankName, IBY_PAYMENT_SYSTEM::HomeCountry, ORA_IBY_PAYMENT_SYSTEM_ACC_VAL::AccountOptionValue, ORA_IBY_PAYMENT_SYSTEM_ACC_VAL::BuName, ORA_IBY_PAYMENT_SYSTEM_FORMAT::StartDate, ORA_IBY_PAYMENT_SYSTEM_FORMAT::EndDate, ORA_IBY_PAYMENT_SYSTEM_KEY::Ownertype, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::SecuredFlag, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::UniquePerBatchFlag, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::DisplayOrder, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::TokenProfileFlag, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::AccountOptionName, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::SourceLang, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::AccountOptionName -->
