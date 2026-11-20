---
skill_id: "erp.financials.payments.manage-payment-methods"
name: "Manage Payment Methods Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Payment Methods under the Payments functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payments"
functional_area_code: "ORA_FIN_PAYMENTS"
task_code: "IBY_MANAGE_PAYMENT_METHODS"
task_name: "Manage Payment Methods"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payments/manage-payment-methods/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payments/manage-payment-methods/current/"
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

# Manage Payment Methods Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Payment Methods` under `Payments`.

## Setup Task Skill Contract

- task_code: `IBY_MANAGE_PAYMENT_METHODS`
- task_name: `Manage Payment Methods`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Payment Methods` under `Payments`.

## Setup Task Metadata

- Task name: `Manage Payment Methods`
- Task code: `IBY_MANAGE_PAYMENT_METHODS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## CSV Export, Import, and Validation Workflow

Apply [the core Data Loader execution contract](../../../../../core/data-loader/SKILL.md).
Create or modify this task's setup data only through its declared FSM workflow
using `core.data-loader`. UI inspection remains read-only. Missing route, catalog
support, payload contract, privileges or approvals is a visible blocker; do not
substitute direct REST, SQL or UI writes. Follow Data Loader's approval workflow
without requesting duplicate approval. Local adapter promotion is not live import
authorization.

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Financials`
- Functional area / Setup Object: `Payments`
- Setup task name: `Manage Payment Methods`
- Setup task code: `IBY_MANAGE_PAYMENT_METHODS`




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
<!-- fscr-create-fields: ORA_IBY_FD_PARENT_PAY_MET::AnticipatedFloat, ORA_IBY_FD_PARENT_PAY_MET::BankChargeBearerAplFlag, ORA_IBY_FD_PARENT_PAY_MET::DeliveryChannelAplFlag, ORA_IBY_FD_PARENT_PAY_MET::Description, ORA_IBY_FD_PARENT_PAY_MET::DocumentCategoryCode, ORA_IBY_FD_PARENT_PAY_MET::DueDayOfMonth, ORA_IBY_FD_PARENT_PAY_MET::DueMonthsForward, ORA_IBY_FD_PARENT_PAY_MET::EndDate, ORA_IBY_FD_PARENT_PAY_MET::ExclusivePmtAplFlag, ORA_IBY_FD_PARENT_PAY_MET::ExternalBankAcctAplFlag, ORA_IBY_FD_PARENT_PAY_MET::MaturityDateOffsetDays, ORA_IBY_FD_PARENT_PAY_MET::PaymentFormatAplFlag, ORA_IBY_FD_PARENT_PAY_MET::PaymentMethodCode, ORA_IBY_FD_PARENT_PAY_MET::PaymentMethodName, ORA_IBY_FD_PARENT_PAY_MET::PaymentModeCode, ORA_IBY_FD_PARENT_PAY_MET::PaymentReasonAplFlag, ORA_IBY_FD_PARENT_PAY_MET::PaymentReasonComntAplFlag, ORA_IBY_FD_PARENT_PAY_MET::PmtEnableAp, ORA_IBY_FD_PARENT_PAY_MET::PmtEnableAr, ORA_IBY_FD_PARENT_PAY_MET::PmtEnableCe, ORA_IBY_FD_PARENT_PAY_MET::RemittanceMessage1AplFlag, ORA_IBY_FD_PARENT_PAY_MET::RemittanceMessage2AplFlag, ORA_IBY_FD_PARENT_PAY_MET::RemittanceMessage3AplFlag, ORA_IBY_FD_PARENT_PAY_MET::SettlementPriorityAplFlag, ORA_IBY_FD_PARENT_PAY_MET::StartDate, ORA_IBY_FD_PARENT_PAY_MET::SupportBillsPayableFlag, ORA_IBY_FD_PARENT_PAY_MET::UniqueRemittanceIdAplFlag, ORA_IBY_FD_PARENT_PAY_MET::UriCheckDigitAplFlag, ORA_IBY_FD_PARENT_PAY_MET::FormatValue, IBY_FD_PAYMENT_METHOD::ApplicableTypeCode, IBY_FD_PAYMENT_METHOD::ApplicableValueFrom, IBY_FD_PAYMENT_METHOD::ApplicableValueTo, IBY_FD_PAYMENT_METHOD::ApplicationShortName, IBY_FD_PAYMENT_METHOD::BuName, IBY_FD_PAYMENT_METHOD::ExcludeFromApplicFlag, IBY_FD_PAYMENT_METHOD::LEName, IBY_FD_PAYMENT_METHOD::PaymentFlow, IBY_FD_PAYMENT_METHOD::PaymentMethodCode, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::AssignmentEntityId, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::EndDate, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::FieldNameCode, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::PaymentMethodCode, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::StartDate, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::TerritoryCode, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::ValAssignmentEntityType, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::ValidationSetCode, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::EndDateDisp, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::Description, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::Language, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::PaymentMethodCode, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::PaymentMethodName, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::SourceLang, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValParamDateValue, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValParamNumberValue, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValParamVarchar2Value, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValidationParameterCode, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValidationSetCode -->
<!-- fscr-update-fields: ORA_IBY_FD_PARENT_PAY_MET::AnticipatedFloat, ORA_IBY_FD_PARENT_PAY_MET::BankChargeBearerAplFlag, ORA_IBY_FD_PARENT_PAY_MET::DeliveryChannelAplFlag, ORA_IBY_FD_PARENT_PAY_MET::Description, ORA_IBY_FD_PARENT_PAY_MET::DocumentCategoryCode, ORA_IBY_FD_PARENT_PAY_MET::DueDayOfMonth, ORA_IBY_FD_PARENT_PAY_MET::DueMonthsForward, ORA_IBY_FD_PARENT_PAY_MET::EndDate, ORA_IBY_FD_PARENT_PAY_MET::ExclusivePmtAplFlag, ORA_IBY_FD_PARENT_PAY_MET::ExternalBankAcctAplFlag, ORA_IBY_FD_PARENT_PAY_MET::MaturityDateOffsetDays, ORA_IBY_FD_PARENT_PAY_MET::PaymentFormatAplFlag, ORA_IBY_FD_PARENT_PAY_MET::PaymentMethodName, ORA_IBY_FD_PARENT_PAY_MET::PaymentReasonAplFlag, ORA_IBY_FD_PARENT_PAY_MET::PaymentReasonComntAplFlag, ORA_IBY_FD_PARENT_PAY_MET::PmtEnableAp, ORA_IBY_FD_PARENT_PAY_MET::PmtEnableAr, ORA_IBY_FD_PARENT_PAY_MET::PmtEnableCe, ORA_IBY_FD_PARENT_PAY_MET::RemittanceMessage1AplFlag, ORA_IBY_FD_PARENT_PAY_MET::RemittanceMessage2AplFlag, ORA_IBY_FD_PARENT_PAY_MET::RemittanceMessage3AplFlag, ORA_IBY_FD_PARENT_PAY_MET::SettlementPriorityAplFlag, ORA_IBY_FD_PARENT_PAY_MET::StartDate, ORA_IBY_FD_PARENT_PAY_MET::SupportBillsPayableFlag, ORA_IBY_FD_PARENT_PAY_MET::UniqueRemittanceIdAplFlag, ORA_IBY_FD_PARENT_PAY_MET::UriCheckDigitAplFlag, ORA_IBY_FD_PARENT_PAY_MET::FormatValue, IBY_FD_PAYMENT_METHOD::BuName, IBY_FD_PAYMENT_METHOD::ExcludeFromApplicFlag, IBY_FD_PAYMENT_METHOD::LEName, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::EndDate, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::PaymentMethodCode, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::StartDate, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::TerritoryCode, ORA_PMT_METHOD_VALIDATION_ASSIGNMENT::EndDateDisp, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::Description, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::PaymentMethodName, ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION::SourceLang, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValParamDateValue, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValParamNumberValue, ORA_PAYMENT_METHOD_VALIDATION_VALUE::ValParamVarchar2Value -->

## Task-specific evidence boundary

Use the six task-local `ora-resource/` files and compiled `ora_rule_registry.json` for validation, dependency, reference, default, error and design rules. The source-backed field dispositions come from the project Attributes Workbook and the same-task export/template; they are candidate contracts pending controlled import verification. Use the exact template metadata `ObjectShortName` for FSM identity, never this task code as a Data Loader business object.

## Source-Backed Task Behavior

- Scope this task to Financials / Payments and the exact `IBY_MANAGE_PAYMENT_METHODS` FSM package. Its graph contains a payment-method parent, usage/applicability rows, language translations, validation assignments and validation parameter values. Preserve the exact template metadata, CSV members, column order and ancestor-qualified addressing. Sources: SRC-CATALOG-TASKS, SRC-FSM-PACKAGE, SRC-CODE-IBY-TASK-BO-SEED, SRC-CODE-IBY-BO-SEED; [input validation](ora-resource/ora_input_validation.md).
- Support source-backed create and update operations only for the entity-qualified fields declared in the lifecycle markers above and the matching input/design resources. Do not infer deletion or a field's update support from its presence in an export or from UI editability. Deletion remains unresolved. Sources: SRC-CODE-IBY-SVC-AM-IMPL, SRC-CODE-IBY-SVC-PARENT-VO, SRC-CODE-IBY-VALIDATION-EOS; [design enforcement](ora-resource/ora_design_enforcement.md).
- Address the parent by `PaymentMethodCode`; take the method code, name and requested effective dates from the implementor. The service parent code is required and insert-only. Updates preserve other non-audit values and unspecified records; a blank observed in an example is not an instruction to erase an existing value. Sources: SRC-CODE-IBY-SVC-PARENT-VO, SRC-FSM-PACKAGE; [defaulting boundaries](ora-resource/ora_defaulting_rules.md).
- Usage/applicability identity uses `PaymentMethodCode`, `ApplicableTypeCode`, `PaymentFlow`, `ApplicationShortName` and `ApplicableValueTo`. The source resolver maps ApplicationShortName to the internal application identity. Nullable scope is permitted only by the reviewed contract; CROSS_BORDER_FLAG and FOREIGN_CURRENCY_FLAG match independently of that scope value. Other reviewed types retain it, and unknown types remain blocked. Sources: SRC-CODE-IBY-USAGE-EO, SRC-CODE-IBY-SVC-AM-IMPL.
- Translation identity is `PaymentMethodCode` plus `Language`. SourceLang and PaymentMethodName follow their source-backed required contracts. Confirm requested language coverage; do not create additional languages merely because they occur in an example export. Sources: SRC-CODE-IBY-SVC-TL-VO, SRC-CODE-IBY-TL-EO; [input validation](ora-resource/ora_input_validation.md), [defaulting boundaries](ora-resource/ora_defaulting_rules.md).
- Validation-assignment identity uses `AssignmentEntityId`, nullable `FieldNameCode`, `ValAssignmentEntityType` and `ValidationSetCode`. The exported assignment reference is interpreted through its source mapping, not assumed portable from its column name; do not substitute the database-generated ValidationAssignmentId. Sources: SRC-CODE-IBY-VALIDATION-EOS, SRC-CODE-IBY-SVC-ASSIGN-VO.
- Validation-value identity combines the complete resolved assignment identity with the value row's own ValidationSetCode and ValidationParameterCode. Resolve the four ancestor-qualified CSV references within payment-method scope against exactly one assignment, recovering the omitted FieldNameCode only from that match. Missing, ambiguous, duplicate or incomplete parent context is a blocker. Sources: SRC-FSM-PACKAGE, SRC-CODE-IBY-VALIDATION-EOS, SRC-CODE-IBY-SVC-VALUE-VO.
- Keep all portable keys and ancestor addressing immutable on update; only the source-backed non-key fields may change. Validation parameter values must match the declared scalar/date type and configured validation-set/parameter context. Do not synthesize validation children when none are requested. Sources: SRC-CODE-IBY-SVC-ASSIGN-VO, SRC-CODE-IBY-SVC-VALUE-VO, SRC-CODE-IBY-VALIDATION-EOS; [input validation](ora-resource/ora_input_validation.md), [dependency readiness](ora-resource/ora_dependency_readiness.md).
- Exclude system-managed audit fields and unsupported export/display fields from implementor writes. Alias (FormatValue) has a source-backed create/update contract; other evidence-unresolved fields remain visible and cannot be relabeled as accepted. Any declared governed application-validation choice remains field/operation-specific and subject to its existing execution gates. Sources: SRC-CODE-IBY-SVC-PARENT-VO, SRC-CODE-IBY-SVC-TL-VO, SRC-CODE-IBY-SVC-VALUE-VO; [input validation](ora-resource/ora_input_validation.md), [design enforcement](ora-resource/ora_design_enforcement.md).
- Treat screenshot-selected and exported defaults as editable design evidence. Preserve explicit implementor choices and requested effective dates. EO defaults or a UI-created example do not prove FSM omission behavior and do not authorize automatic serialization of unconfirmed values, unrestricted children or translations. Sources: SRC-FSM-PACKAGE, SRC-CODE-IBY-PMT-EO-XML, SRC-CODE-IBY-PMT-EO-IMPL; [defaulting rules](ora-resource/ora_defaulting_rules.md).
- Resolve applicable payment-method, business-unit and legal-entity identifier references (CSV LEName contains LegalEntityIdentifier, not display Name) through the declared supported read-only preflights. Require an exact context-appropriate match; zero and multiple matches are data blockers. Keep endpoint unavailability separate from value validity and retain each unconfirmed reference/import contract. Sources: SRC-CODE-IBY-SVC-AM-IMPL, SRC-ORACLE-PMT-METHOD-LOV-26C, SRC-ORACLE-FIN-BU-LOV-26C, SRC-ORACLE-LEGAL-ENTITY-LOV-26C; [reference lookups](ora-resource/ora_reference_lookups.md), [dependency readiness](ora-resource/ora_dependency_readiness.md).
- Create or modify setup data only through the declared FSM workflow using core/data-loader. UI inspection is read-only. Exact task/package validation, applicable references and privileges, immutable preview and Data Loader's approval must pass before submission; no direct UI, REST or SQL write may replace that route. Sources: [core Data Loader execution contract](../../../../../core/data-loader/SKILL.md), [design enforcement](ora-resource/ora_design_enforcement.md).

- Evaluate source-proven import side effects against the fresh baseline before build/validation. A serialized AP/AR/CE flag N can delete existing application usage rows, and blank all-BU scope can remove specific-BU rows. Stop preserved-row create/update when either effect applies; reject seeded-parent edits that the hook suppresses and a known all-N application selection. These are conditional request blockers, not a global skill disable. Sources: SRC-DEBUG-IMPORT 325-330, 332-408, 587-619; SRC-REVIEW-PARENT-IMPL 2296-2307; [design enforcement](ora-resource/ora_design_enforcement.md).

- Select the exact evidenced87-column or historical89-column package variant before construction. Preserve historical field support, current metadata, strict calendar dates and ancestor-qualified child addressing; block mixed/unknown variants or fields absent from that export. This offline compatibility rule does not repair or qualify a deployed Fusion alternate-key definition. See [input validation](ora-resource/ora_input_validation.md) and [design enforcement](ora-resource/ora_design_enforcement.md); evidence: reviewed same-task export and offline package-variant qualification.

The parent payment method, applicability, translation, validation assignment and validation value entities are modeled as one parent service graph. A child is not an independent FSM import root. Every business operation must pass the entity-specific field allowlist and source-cited operation-ownership matrix in the current builder run state. Keep audit columns out of implementor input and preserve all unrequested exported values.

Before candidate construction, use the current environment for any applicable confirmed read-only payment-method, business-unit and legal-entity preflight. A successful one-match preflight proves only reference existence. Apply the individual source and qualification boundaries in the task resources. Alias is source-backed and payment mode is insert-only. Configured values, default serialization and remaining import behavior are evaluated for the selected request, not as a blanket task blocker. Report an unresolved update field as `evidence_unresolved`, not as a product rejection; offer the governed exact-field application-validation choice only under the adapter and Data Loader contract.

Run Book owns the implementation conversation and approval choreography. `core.data-loader` owns immutable preview, exact candidate approval, FSM import, process monitoring and fresh-export reconciliation. Task-local resources and the offline adapter have no Fusion write route. A successful process is not completion until persisted state is reconciled. Do not resubmit on timeout or unknown outcome.

The task-owned `e2e-adapter.json` is the offline customer contract. The test catalog and private test controls reside under the owning Payments functional area at `noship/tests/manage-payment-methods/`. A `blocked` capability means the skill remains a static prototype; do not present it as approved for live import or campaign execution. Test fixtures and retained-state policy are downstream E2E controls, not ordinary implementation limits.

Use FormatValue for Alias without a format-identity lookup. Preserve omitted Alias and unrelated values. Normalize assignment display dates through canonical EndDate. Include explicit Usage for application enablement and ALL/SPECIFY intent; parent flags do not create applicability through FSM. Reject source-proven ignored Usage edits and unsafe identity replacements. Fusion source supports a distinct flag-type update branch, but the current task contract cannot update ApplicableValueTo for CROSS_BORDER_FLAG or FOREIGN_CURRENCY_FLAG because it remains protected by the public key declaration. Report this existing task limitation and preserve the requested intent; do not bypass key protection or substitute create. Qualified Usage creates remain available. See field behavior and Usage correctness in the task resources. Data Loader continues to own live approval, execution and reconciliation.

For a Data Loader integration that selects memory-resident preparation, `build_candidate_bytes` prepares source-validated ZIP bytes in memory using the same serializer and exact-package validator as the offline CLI. Follow the selected checkout's Data Loader contract for its persisted-preflight or interactive-session handoff; this optional interface does not select or replace that workflow. Keep its candidate, blueprint and requirements in the native session; a no-op returns no payload. This preparation interface grants no upload/import authority and does not replace core approval or status workflows.

A create may contain an empty non-key `values` object when its complete source-backed business data is in `targetKey` (for example Usage). All required fields, exact-key, parent, domain and prerequisite checks still apply. An empty update remains invalid.
