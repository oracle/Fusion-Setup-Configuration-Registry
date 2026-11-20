---
skill_id: "erp.financials.payables.create-payment-process-request-templates"
name: "Create Payment Process Request Templates Setup Task Guidance"
description: "Creates, updates, exports, and validates Payables payment process request template setup through governed FSM CSV workflows, preserving unrelated templates and reference master data."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payables"
functional_area_code: "FIN_PAYABLES_DEPLOYED"
task_code: "ORA_AP_MANAGE_PAYMENT_PROCESS_REQUEST_TEMPLATE"
task_name: "Create Payment Process Request Templates"
parent_skill_id: "erp.financials.payables"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "configuration_blueprint"
  - "offline_task_package"
  - "reconciliation_report"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
uses_core:
  - "core.runbook"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/create-payment-process-request-templates/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/create-payment-process-request-templates/current/"
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
  - "Writes local blueprints, previews, validated FSM candidates and reconciliation reports under the active project workspace."
  - "Delegates approved Fusion imports to the active Run Book and core.data-loader; the task runtime makes no network calls."
required_privileges: []
---

# Create Payment Process Request Templates Setup Task Guidance

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::AcceleratedInvoicesOption, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::AddlPayFromDays, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::AddlPayThruDays, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::AddlPaymentDays, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute1, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute10, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute11, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute12, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute13, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute14, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute15, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute2, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute3, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute4, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute5, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute6, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute7, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute8, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute9, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::AttributeCategory, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::BankAccountName, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::BankChargeBearerOverride, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::CreateInstrsFlag, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::CrossCurrencyRateType, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::CurrencyGroupOption, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Description, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::DocumentRejectionLevel, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::FirstApprover, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::FirstVoucherNumber, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::FundingCardAccount, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::HiPaymentPriority, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::InactiveDate, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::InvoiceConversionRateType, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::LeGroupOption, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::LowPaymentPriority, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::OuGroupOption, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PartyNumber, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PayGroupOption, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PayOnlyWhenDue, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PayablesReviewSettings, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentConversionRateType, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentDateOption, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentDocumentName, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentMethodCode, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentMode, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentProfileName, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentRejectionLevel, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentsReviewSettings, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PersonNumber, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::SettlementPriorityValue, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::SourceGroupOption, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::SupplierOrParty, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::SupplierType, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::TemplateName, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::TemplateTypeValue, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::TransactionCalendar, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::ZeroAmountsAllowed, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::ZeroInvAllowedFlag, ORA_PPR_BU_GROUP::Name, ORA_PPR_BU_GROUP::ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES.TemplateName, ORA_PPR_CURRENCY_GROUP::CurrencyCode, ORA_PPR_CURRENCY_GROUP::ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES.TemplateName, ORA_PPR_LE_GROUP::LegalEntityIdentifier, ORA_PPR_LE_GROUP::ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES.TemplateName, ORA_PPR_PAY_GROUP::ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES.TemplateName, ORA_PPR_PAY_GROUP::VendorPayGroupName, ORA_PPR_SOURCE_GROUP::InvoiceSourceName, ORA_PPR_SOURCE_GROUP::ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES.TemplateName -->
<!-- fscr-update-fields: ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::AcceleratedInvoicesOption, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::AddlPayFromDays, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::AddlPayThruDays, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::AddlPaymentDays, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute1, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute10, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute11, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute12, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute13, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute14, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute15, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute2, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute3, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute4, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute5, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute6, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute7, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute8, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Attribute9, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::AttributeCategory, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::BankAccountName, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::BankChargeBearerOverride, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::CreateInstrsFlag, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::CrossCurrencyRateType, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::CurrencyGroupOption, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::Description, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::DocumentRejectionLevel, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::FirstApprover, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::FirstVoucherNumber, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::FundingCardAccount, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::HiPaymentPriority, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::InactiveDate, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::InvoiceConversionRateType, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::LeGroupOption, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::LowPaymentPriority, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::OuGroupOption, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PartyNumber, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PayGroupOption, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PayOnlyWhenDue, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PayablesReviewSettings, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentConversionRateType, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentDateOption, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentDocumentName, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentMethodCode, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentMode, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentProfileName, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentRejectionLevel, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PaymentsReviewSettings, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::PersonNumber, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::SettlementPriorityValue, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::SourceGroupOption, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::SupplierOrParty, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::SupplierType, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::TemplateTypeValue, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::TransactionCalendar, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::ZeroAmountsAllowed, ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES::ZeroInvAllowedFlag -->

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Create Payment Process Request Templates` under `Payables`.

Reviewers: the Payables Pillar Development Lead or SME and an FSCR A-Team/core
reviewer, with functional, automation and QA review for behavior changes.

## Usage

Enter through `router/implementation-router` and the active project/Run Book.
Use the parent `erp.financials.payables` skill for sequencing. Delegate exact-task
exports, setup/reference validation and imports to the dependencies declared in
the manifest; the task adapter performs offline preparation and reconciliation.
Track durable artifacts and token usage under the active project.

## Task scope and identity

This task configures reusable payment process request templates. It does not
create a runtime payment process request or maintain payment process profiles.
The root CSV entity is ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES; match a template
by exact TemplateName. A requested rename changes identity and requires a
separate design decision. Never substitute an internal TemplateId.

The task owns five selection collections: business units, currencies, legal
entities, pay groups and invoice sources. Each child row carries the exact
parent TemplateName plus its source-backed reference key. Referenced business
units, currencies, legal entities, suppliers, bank accounts, documents, payment
methods, profiles, people, calendars and lookup definitions remain existing
dependencies. A child criterion belongs to its template transaction; this
contract does not expose standalone child or master-data operations.

Root create and update are supported. Every exposed field has its own create
and update disposition; operation support does not make all fields writable.
Knowledge of Oracle's internal record-matching algorithm, framework source or
consumed dependency labels is not an additional preparation or validation
prerequisite for these supported operations. Use the task's established CSV,
identity, field and reference contracts. Resolve an uncertain behavior through
applicable source evidence or a governed controlled test with independent
readback; scope that uncertainty to the affected field or operation.
Audit fields are protected, keys identify the target, and unspecified values
and records are preserved. Both `preserveOtherValues` and
`preserveUnspecifiedRows` must remain true for bounded task operations; neither
flag can waive preservation. Declared source effects remain the only derived
changes allowed beyond the requested values. InactiveDate is retirement/update, not physical
deletion. Child aggregate omission, replacement, removal and duplicate-helper
behavior are not fully established; disclose the exact affected action before
preparing a candidate and do not infer deletion from a missing CSV row.

A child membership create must serialize its owning parent in the same ZIP.
When that parent has no explicit root operation, include exactly one full row
from the current baseline, preserving every non-audit value and blank while
leaving audit cells empty. Show this retained parent context in the complete
preview; it is not a new root operation and receives no create defaults. If an
explicit root create or update already supplies the parent, use that reviewed
operation row instead. Reject missing, modified or unrelated context rows;
never synthesize a missing parent or copy unrequested child collections.
An implicit parent with a blank required Payment Conversion Rate Type needs an
explicit supported root correction; do not default or silently repair it.
The package rule does not establish import success or preservation: verify the
root, requested child and all retained selections through independent readback.
It does not enable child replacement, removal or master-data changes.

## Default acceptable input values

Before validating supplied dropdown, radio or checkbox input, read
[Acceptable input values](references/acceptable-input-values.md). Use its
listed acceptable names, codes and CSV mappings as the default validation
reference for every environment. Preserve these concrete default values
without attaching them to an environment name. Do not require a live lookup
solely because the environment differs. Resolve an unlisted configured value
or an explicit reference check through the active reference-validation route.

Normalize only an unambiguous listed label to its documented CSV value.
Meaning-alias fields retain the exact displayed label; browser option indexes
are never business codes. The guide's FSM CSV format column controls what is
serialized: `TemplateTypeValue` takes the displayed Meaning, whereas group
options, Y/N flags and `PaymentDateOption` take their documented codes. An
attribute name ending in Value or Type does not establish its representation.
Apply these checks only to supplied or changed
values and retain each field's blank, dependency and operation rules.
These lists define acceptable values. For omitted create fields, apply the
[UI create-default policy](ora-resource/ora_defaulting_rules.md); preserve explicit
values and blanks and show all applied defaults in the preview. Never apply
create defaults to updates.
Supplier Type uses listed names first. For an unlisted supplied name, execute
`resolve_supplier_type_rest` through the declared Core REST route and retain
its field/operation-bound evidence before preparing a candidate. One or more
exact Meaning matches pass, including duplicate matches. Preserve Meaning in
the CSV; API failures block validation rather than establish an invalid name.
Unchanged retained Supplier Types do not trigger this check.
Other searchable master-data LOVs continue to use their reference contracts.

For Transaction Calendar, First Approver, Funding Card Account and Bank
Conversion Rate Type, **use user inputs directly** when supplied. Take values
as-is without verification, validation, REST/LOV checks, normalization,
conversion, pairing checks or derived companion values. This explicit policy
takes precedence over general input/reference-verification instructions for
these four fields; no additional input-verification decision is needed.
Preserve omission. Keep the existing Transaction Calendar import-assignment
and Bank Conversion Rate Type CSV-mapping limits separate from input handling;
retain an unmapped supplied value in the blueprint/preview without inventing
an import field. See the guide's Direct user inputs section.

Before preparing a candidate, apply the guide's
[payment-mode and payment-document dependencies](references/acceptable-input-values.md#payment-mode-account-and-profile-rules)
to effective supplied plus retained values. Virtual card requires a funding
account/profile and empty bank/document; nonvirtual mode requires an empty
funding account. A document requires a selected bank. Require explicit clears
for conflicts, preserve unrelated updates, and do not validate funding-account
contents.

The descriptor declares exact effects of explicitly supplied setters: request
date clears its offset, each All selection clears only that template's related
selected rows, and the resolved Virtual card branch forces immediate payment
file creation. Include those derived values and affected selection groups in
the immutable preview. A supplied value that conflicts with a proven effect
needs correction. Keep all other fields and rows protected. The preview also
identifies recovery that cannot be automated from the reviewed source contract;
do not treat a blank optional date or an omitted selection row as proof of a
supported clearing or deletion operation.

## Rule-driven workflow

1. Enter through the Implementation Router and active project/Run Book; resolve
   this exact task and distinguish create, update, export, prepare, import,
   monitoring and verification intent. A mixed or ambiguous request needs a
   bounded clarification; preserve and report excluded work.
2. Obtain same-task template and current-data exports through the shared task
   exporter. Validate task identity, release, members, headers, record widths,
   portable keys and parent links before designing a change.
3. Consume this task's compiled registry through the active Run Book/Data
   Loader Task Hook workflow and follow its reached Task Nodes. The owning
   workflow selects and validates the registry; this skill does not invoke
   developer compilers or the loader's private validator directly.
   Read input validation, reference contracts,
   dependency readiness, defaulting, design enforcement and error handling in
   ora-resource. Their source evidence and unresolved boundaries control each
   requested field.
4. Interpret business labels only through their field's value contract. Keep
   display-Meaning aliases distinct from stored codes. Apply the direct-user-input
   exceptions above. For other references, confirm eligible configured values
   without creating prerequisite master data.
   A supported public read-only preflight can provide early evidence; when it
   is unavailable, a confirmed FSM resolver remains authoritative. Successful
   zero matches remain a data outcome, not a transport failure; multiple
   matching rows are accepted for REST reference validation.
   For every task REST reference check, apply the acceptance policy in
   `references/acceptable-input-values.md`: one or more matching returned rows
   pass, including multiple rows. Do not require uniqueness or block on an
   unproved import-time duplicate/enablement check after a REST match. Bind
   the retained response to its field prerequisite using `restResult` with
   `httpStatus` and `items`; this satisfies the adapter's conditional reference
   gate. Preserve the supplied portable CSV value rather than choosing an ID.
5. Preserve explicit business input. For creates, explicitly serialize the UI
   defaults for omitted fields, including Review proposed payments checked and
   both document/payment validation failures set to Stop process for review.
   Apply these task defaults without a contextual receipt or extra user prompt.
   Explicit values and blanks take precedence; updates preserve retained values.
   An omitted
   PaymentConversionRateType defaults to Corporate; an explicitly blank alias
   remains invalid. HiPaymentPriority is From, LowPaymentPriority is To;
   each is 1..99 and From must not exceed To.
6. Produce a blueprint and complete preview with exact changes, defaults,
   preserved values, prerequisites, warnings and evidence gaps. The offline
   task descriptor supplies the domain contract to the
   [task-local package preparation](ora-resource/ora_dependency_readiness.md#package-preparation)
   through the thin local entrypoint. That runtime performs package build, independent
   candidate validation, determinism, scoped update recovery and reconciliation.
   Preview includes declared setter effects and automatic rollback limitations;
   unproved typed clears and restoration of removed selections require separately
   reviewed recovery. These local components do not
   authenticate, submit imports or grant mutation authority.
7. For an explicitly unresolved eligible update field, explain the exact
   uncertainty and obtain the implementor's field/operation-specific decision
   before governed application validation. Carry that warning into the
   blueprint and preview. Invalid values, protected keys/audit, unsupported
   fields, identity ambiguity and missing authorization cannot use this choice.
8. Route every import through the active Run Book and core.data-loader with
   import mode FSM, empty businessObject and exact task/archive identity.
   Validate every CSV logical record against its exact header width, preserving
   trailing empty columns. Follow the selected loader's immutable preview and
   approval contract. Submit once; uncertain outcomes require status recovery,
   not resubmission.
9. Follow [persistence verification](references/persistence-verification.md).
   Retrieve available process diagnostics and independently acquire a fresh
   exact-task readback through the shared exporter. Use a readback with a
   different path and digest from the baseline and candidate, matching
   environment/release and a distinct nonblank ESS request identity. These
   archive checks do not establish acquisition freshness. The adapter reports
   status COMPARISON_ONLY with comparisonStatus PASS for matches, or FAIL
   with comparisonStatus FAIL for mismatches; persistenceVerified=false in both.
   The owning Run Book/export workflow must retain the successful independent
   acquisition process, status, digest and target context, establish that the
   readback follows the import, and reconcile every requirement and preservation
   assertion before claiming persisted business results. Check the exact portable
   membership set of each affected template's five selection collections,
   including expected empty groups, and reject unexpected additions as well as
   missing members. The candidate contains operation rows and any required
   unchanged parent context, not a copy of every retained child; omission from
   the candidate is not a deletion instruction.
   Record Fusion outcome,
   comparison, persistence verification and Run Book synchronization separately;
   process completion alone does not complete the business setup.

## Validation scope

Use the acceptable-input-values reference for fixed choices, REST fallback
validation, direct-user-input fields and CSV representations. One or more exact
REST matches pass; duplicate matches do not introduce a uniqueness gate.
Transaction Calendar, First Approver, Funding Card Account and Bank Conversion
Rate Type use the supplied values directly when mentioned.

Apply the [validation responsibility rules](ora-resource/ora_input_validation.md#validation-responsibility): run known local checks and declared reference checks,
then leave application-specific acceptance of supported mapped fields to Fusion.
Do not add proof of internal setter order, helper revision or future saved values
as a prerequisite for ordinary preparation. Only a genuinely unverified direct
write uses the existing field-specific update exception; normal import approval
still belongs to Core Data Loader.

Root create and update are supported. Preserve unrequested fields and rows.
Child selection keys identify membership; they are not master-data rename
requests. Child removal or aggregate replacement, technical identity changes,
configured DFF domains and recovery must follow their declared operation-specific
contracts. Do not infer those capabilities from scalar-field support.

No runtime payment request API, direct REST write, browser upload shortcut or
database write is an execution route for this task. Use the active Run Book and
Core Data Loader for approved imports, and the selected status/export workflows
for subsequent verification.
