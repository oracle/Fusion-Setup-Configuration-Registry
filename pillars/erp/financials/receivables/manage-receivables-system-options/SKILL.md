---
skill_id: "erp.financials.receivables.manage-receivables-system-options"
name: "Manage Receivables System Options Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Receivables System Options under the Receivables functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Receivables"
functional_area_code: "FIN_RECEIVABLES_DEPLOYED"
task_code: "AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS"
task_name: "Manage Receivables System Options"
parent_skill_id: "erp.financials.receivables"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/receivables/manage-receivables-system-options/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/receivables/manage-receivables-system-options/current/"
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

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AR_SYSTEM_OPTIONS::AccountingMethod, AR_SYSTEM_OPTIONS::AccrueInterest, AR_SYSTEM_OPTIONS::AiLogFileMessageLevel, AR_SYSTEM_OPTIONS::AiMaxMemoryInBytes, AR_SYSTEM_OPTIONS::AutoRecInvoicesPerCommit, AR_SYSTEM_OPTIONS::AutoRecReceiptsPerCommit, AR_SYSTEM_OPTIONS::AutoSiteNumbering, AR_SYSTEM_OPTIONS::BUName, AR_SYSTEM_OPTIONS::CalcDiscountOnLinesFlag, AR_SYSTEM_OPTIONS::CerDsoDays, AR_SYSTEM_OPTIONS::CerSplitAmount, AR_SYSTEM_OPTIONS::ChangePrintedInvoiceFlag, AR_SYSTEM_OPTIONS::CodeCombinationIdGainSegments, AR_SYSTEM_OPTIONS::CodeCombinationIdLossSegments, AR_SYSTEM_OPTIONS::CodeCombinationIdRoundSegments, AR_SYSTEM_OPTIONS::CreateDetailedDist, AR_SYSTEM_OPTIONS::CreateReciprocalFlag, AR_SYSTEM_OPTIONS::DefaultCbDueDate, AR_SYSTEM_OPTIONS::DocumentSeqGenLevel, AR_SYSTEM_OPTIONS::GenerateCustomerNumber, AR_SYSTEM_OPTIONS::GroupingRuleName, AR_SYSTEM_OPTIONS::InvoiceDeletionFlag, AR_SYSTEM_OPTIONS::LedgerCurrency, AR_SYSTEM_OPTIONS::LedgerName, AR_SYSTEM_OPTIONS::LocationTaxAccountSegments, AR_SYSTEM_OPTIONS::PartialDiscountFlag, AR_SYSTEM_OPTIONS::PayUnrelatedInvoicesFlag, AR_SYSTEM_OPTIONS::PopulateGlSegmentsFlag, AR_SYSTEM_OPTIONS::PostingDaysPerCycle, AR_SYSTEM_OPTIONS::PrintHomeCountryFlag, AR_SYSTEM_OPTIONS::PrintRemitTo, AR_SYSTEM_OPTIONS::RuleSetName, AR_SYSTEM_OPTIONS::RunGlJournalImportFlag, AR_SYSTEM_OPTIONS::SalesrepRequiredFlag, AR_SYSTEM_OPTIONS::ServicedByAnyBuFlag, AR_SYSTEM_OPTIONS::SiteRequiredFlag, AR_SYSTEM_OPTIONS::TaxInvoicePrint, AR_SYSTEM_OPTIONS::TrxHeaderLevelRounding, AR_SYSTEM_OPTIONS::UnearnedDiscount -->
<!-- fscr-update-fields: AR_SYSTEM_OPTIONS::AccountingMethod, AR_SYSTEM_OPTIONS::AccrueInterest, AR_SYSTEM_OPTIONS::AiLogFileMessageLevel, AR_SYSTEM_OPTIONS::AiMaxMemoryInBytes, AR_SYSTEM_OPTIONS::AutoRecInvoicesPerCommit, AR_SYSTEM_OPTIONS::AutoRecReceiptsPerCommit, AR_SYSTEM_OPTIONS::AutoSiteNumbering, AR_SYSTEM_OPTIONS::CalcDiscountOnLinesFlag, AR_SYSTEM_OPTIONS::CerDsoDays, AR_SYSTEM_OPTIONS::CerSplitAmount, AR_SYSTEM_OPTIONS::ChangePrintedInvoiceFlag, AR_SYSTEM_OPTIONS::CodeCombinationIdGainSegments, AR_SYSTEM_OPTIONS::CodeCombinationIdLossSegments, AR_SYSTEM_OPTIONS::CodeCombinationIdRoundSegments, AR_SYSTEM_OPTIONS::CreateDetailedDist, AR_SYSTEM_OPTIONS::CreateReciprocalFlag, AR_SYSTEM_OPTIONS::DefaultCbDueDate, AR_SYSTEM_OPTIONS::DocumentSeqGenLevel, AR_SYSTEM_OPTIONS::GenerateCustomerNumber, AR_SYSTEM_OPTIONS::GroupingRuleName, AR_SYSTEM_OPTIONS::InvoiceDeletionFlag, AR_SYSTEM_OPTIONS::LedgerName, AR_SYSTEM_OPTIONS::LocationTaxAccountSegments, AR_SYSTEM_OPTIONS::PartialDiscountFlag, AR_SYSTEM_OPTIONS::PayUnrelatedInvoicesFlag, AR_SYSTEM_OPTIONS::PopulateGlSegmentsFlag, AR_SYSTEM_OPTIONS::PostingDaysPerCycle, AR_SYSTEM_OPTIONS::PrintHomeCountryFlag, AR_SYSTEM_OPTIONS::PrintRemitTo, AR_SYSTEM_OPTIONS::RuleSetName, AR_SYSTEM_OPTIONS::RunGlJournalImportFlag, AR_SYSTEM_OPTIONS::SalesrepRequiredFlag, AR_SYSTEM_OPTIONS::ServicedByAnyBuFlag, AR_SYSTEM_OPTIONS::SiteRequiredFlag, AR_SYSTEM_OPTIONS::TaxInvoicePrint, AR_SYSTEM_OPTIONS::TrxHeaderLevelRounding, AR_SYSTEM_OPTIONS::UnearnedDiscount -->

# Manage Receivables System Options Setup Task Guidance

## Purpose

Provide source-bounded setup planning, task-level FSM package routing, validation, dependency, defaulting, error-handling, and design guidance for `Manage Receivables System Options` under `Receivables`.

Create and update are supported only for the entity-qualified fields in the markers above and remain subject to the field-specific rules and evidence in this task. A package field omitted from an operation marker is evidence-unresolved for that operation, not automatically product-unsupported. Physical deletion has no source-backed contract in this task; do not infer it from reverse-update cleanup, approved retained state, status, end date, inactivation, or another retirement mechanism.

## Setup Task Skill Contract

- task_code: `AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS`
- task_name: `Manage Receivables System Options`
- parent_skill_id: `erp.financials.receivables`
- pillar / offering / functional area: `ERP / Financials / Receivables`
- functional_area_code: `FIN_RECEIVABLES_DEPLOYED`
- export/import supported: `Y`
- CSV export/import supported: `Y`
- Data Loader import mode: `FSM`
- businessObject: empty by contract; use `ASM_SETUP_CSV_METADATA.xml` object short name `AR_SYSTEM_OPTIONS` as FSM archive identity
- source catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## When to Use

Use this skill for the exact FSM task when planning or validating a Receivables System Options change, reviewing a same-task export/template, producing an FSM package candidate, or routing a separately approved import through Data Loader.

Do not use it for another Receivables task, direct database changes, direct invocation of internal ADF implementation classes, or unsupported REST writes.

## Read Order

Read the governed resources in this order before producing a package preview:

1. `ora-resource/ora_input_validation.md`
2. `ora-resource/ora_reference_lookups.md`
3. `ora-resource/ora_dependency_readiness.md`
4. `ora-resource/ora_defaulting_rules.md`
5. `ora-resource/ora_design_enforcement.md`
6. `ora-resource/ora_error_handling.md`
7. `ora-resource/ora_rule_registry.json`

The compiled registry is incomplete while any applicable resolver contract remains unconfirmed, partial, or `TBD`. A missing optional public preflight path is not a readiness blocker when a complete source-proven FSM import resolution or validation contract exists. The execution planner must fail closed on every remaining contract blocker; do not use a readiness override unless the user explicitly authorizes it after reviewing every blocker.

## Evidence Boundary

- Same-task Fusion export/template evidence confirms `AR_SYSTEM_OPTIONS`, `AR_SYSTEM_OPTIONS.csv`, `ASM_SETUP_CSV_METADATA.xml`, and the current 202-column structural contract.
- Oracle Help 26C supports the documented salesperson, header-level rounding, printed-transaction, unearned-discount, and partial-payment-discount guidance.
- Oracle Financials EDM 26C supports `AR_SYSTEM_PARAMETERS_ALL`, `ORG_ID` identity, schema relationships, types, and nullability; it does not independently prove import behavior.
- Reviewed implementation evidence supports the FSM import resolvers, invalid-dependency behavior, conditional validation, account-combination handling, and documented cross-row/database side effects.
- Twelve resolver requirements are confirmed. Eight have supported public read-only preflight paths. Receipt rules, exception rules, Receivables activities, and the accounting-flexfield prompt have complete source-proven FSM import resolution or validation contracts but no supported standalone public GET; the four retained official-documentation `No match` dispositions limit optional preflight only.
- No supported public task-specific REST write resource was established. Internal ADF components prove the import contract but are not directly callable contracts; actual resolution or validation occurs only inside the separately governed FSM Data Loader preview/import path.
- Environment current-data exports can contain sensitive customer configuration. Never embed their values in examples, fixtures, documentation, tests, or source control.
- Treat the Attributes Workbook, Source Register, CodeSearch evidence, and package encodings as developer-only authoring inputs. Never ask an implementation user to supply them. Apply every confirmed task-owned mapping internally. For a genuinely unmapped business term, ask one concise business-language clarification; when the value is structurally valid but evidence remains unresolved, honor only the documented explicit nonproduction runtime-validation override and continue through immutable preview and separate approval. Proven invalid values remain blocked.

## Source-Backed Task Behavior

Before package generation, enforce these exact `AR_SYSTEM_OPTIONS` string maxima in characters: 1 character for `AccrueInterest`, `AutoSiteNumbering`, `CalcDiscountOnLinesFlag`, `ChangePrintedInvoiceFlag`, `CreateReciprocalFlag`, `GenerateCustomerNumber`, `InvoiceDeletionFlag`, `PartialDiscountFlag`, `PayUnrelatedInvoicesFlag`, `PopulateGlSegmentsFlag`, `PrintHomeCountryFlag`, `PrintRemitTo`, `RunGlJournalImportFlag`, `SalesrepRequiredFlag`, `ServicedByAnyBuFlag`, `SiteRequiredFlag`, `TrxHeaderLevelRounding`, `UnearnedDiscount`; 30 characters for `AccountingMethod`, `DefaultCbDueDate`, `TaxInvoicePrint`, `CreateDetailedDist`; and 80 characters for `DocumentSeqGenLevel`. The same-task package establishes the fields and string types, `SystemParameterEO.xml` establishes the ADF character precision, and Oracle Financials EDM 26C corroborates the owning table lengths. Validate target-key and operation values before candidate ZIP generation. On overflow, report the entity, field, actual length, maximum, and unit, ask for a shorter business value, and require a new preview; never truncate silently.

- One persisted system-options row is owned by a business unit (`ORG_ID`). Resolve the package business-unit name exactly once in the enterprise context.
- Resolve ledger and chart of accounts before validating any account-combination segments.
- Resolve set-scoped rules, sources, and transaction types only after their reference-data set; resolve activities and remittance accounts only after their business-unit context.
- A missing or ambiguous public-preflight result, or a null FSM alternate-key/existence result, is an invalid dependency. Stop the row and never choose a candidate.
- For receipt rules, exception rules, and Receivables activities, FSM import resolves the documented business/context keys to internal identifiers. For `AiAcctFlexKeyLeftPrompt`, FSM import performs an enabled `GL#` segment existence check under the ledger-derived chart of accounts and does not replace the supplied prompt.
- Every create requires an explicit nonblank `RuleSetName`. Never infer or copy it from another business unit; validate it through the confirmed FSM-import application-rule-set resolver before accepting the import result.
- Every create also requires explicit nonblank business choices for whether printed transactions may be changed (`ChangePrintedInvoiceFlag`), partial payments may earn discounts (`PartialDiscountFlag`), and receipts require a customer site (`SiteRequiredFlag`). Ask for any omitted choice in one concise business-language clarification and reject the create before ZIP generation if any remains blank. Controlled FSM diagnostics prove requiredness but do not establish a universal default.
- Normalize the confirmed RSO business labels before package validation: `Show total tax only` or `Total tax only` maps to `TaxInvoicePrint=TOTAL ONLY`; `Assign when transaction is completed` or `When completed` maps to `DocumentSeqGenLevel=WHEN_TRX_COMPLETED`; `Due date of open invoice` or `Open invoice due date` maps to `DefaultCbDueDate=DUE_DATE`; and Discount Basis maps `Invoice Amount` to `CalcDiscountOnLinesFlag=I`, `Lines Only` to `L`, `Lines, Freight Items, and Tax` to `T`, and `Lines and Tax, not Freight Items and Tax` to `F`. Match case-insensitively after trimming and preserve an exact supported package value already supplied. Despite its package name, `CalcDiscountOnLinesFlag` is not Boolean; reject `N`, `Y`, and every value outside `I`, `L`, `T`, and `F` before ZIP generation.
- Normalize a positive whole-number AutoInvoice memory value expressed in MB to `AiMaxMemoryInBytes` using `MB x 1048576`; for example, `5 MB` becomes `5242880`. Preserve an explicit nonnegative byte integer without reconversion. Do not invent a default.
- An FSM import resolver/validation failure emits recoverable `AR:::AR_ATTR_NOT_EXISTS_TARGET_INS` with `ATTRIBUTE_NAME_LIST` and alternate-key values, records the field-specific dependency token, and removes the invalid `AR_SYSTEM_OPTIONS` XML element from further import processing. The prompt-specific failure includes `AiAcctFlexKeyLeftPrompt <value> does not exist`.
- When header-level rounding is enabled, require a valid rounding account. Once enabled and saved, Oracle Help documents that it cannot be disabled.
- When salesperson is required, require an explicit sales-credit percent limit decision; a blank limit means no enforced limit.
- Bills Receivable cannot be disabled while dependent Bills Receivable records exist.
- MFAR/detailed-distribution changes can affect other business-unit rows sharing the ledger; claim-management behavior can create a Claim Investigation payment-schedule sentinel. Before create preview, inspect the fresh export for an existing exact-ledger row. If that ledger already has detailed distributions enabled, show `Y` as the effective result and require explicit business acceptance instead of promising `N`; keep any persisted `N`-to-`Y` difference material and visible. Disclose and reconcile these effects.
- Confirmed new-entity defaults are `AccountingMethod=ACCRUAL`, `AccrueInterest=N`, and `UnearnedDiscount=N`. Never overwrite explicit input, and do not assume CSV blank/default timing without preview evidence.

## CSV Export, Import, and Validation Workflow

1. Export current task data with `shared.setup-export.task-level-export`.
2. Verify target/release, successful process state, `AR_SYSTEM_OPTIONS` metadata identity, the exact current headers, and archive fingerprint.
3. Validate task data with `shared.validation.setup-data-validator`.
4. Validate reference data with `shared.validation.reference-data-validator` and the task resources. Use a supported public preflight when documented; otherwise require a complete confirmed FSM import resolution/validation contract and defer the field-scoped check to the immutable Data Loader preview. Stop only when the applicable contract is missing, partial, or fails.
5. Preserve unrelated rows and current-data confidentiality while building a candidate package.
   If every requested update already exactly matches the fresh current-data baseline, complete source, field, target, prerequisite, and requirement validation and return `NO_OP` without an import ZIP. Retain input/design hashes and the business summary; `candidateSha256` is null and the member inventory is empty. Record the no-change outcome and do not hand it to Data Loader. This also applies to an already-restored update rollback. Do not treat approximate text or date-format differences as exact equality. A create or batch containing any real change follows the normal package, validation, preview, and approval workflow.
6. Route import only through `core.data-loader` with mode `FSM` and an empty `businessObject`.
7. Require Data Loader's immutable preview and separate exact approval before any live mutation.
8. After a terminal process result, reconcile the exact business-unit natural key, requested fields, side effects, and unrelated-row preservation. Never resubmit an uncertain write automatically.

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

Use the parent functional-area skill `erp.financials.receivables` for broader sequencing and scope decisions. Run Book owns task input/orchestration, Data Loader owns package processing/preview/approval/writes, and this task skill owns source-bounded task guidance. Track token usage for generated project artifacts and skill-run records using the manifest policy.
