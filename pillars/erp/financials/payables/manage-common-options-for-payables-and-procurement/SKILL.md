---
skill_id: "erp.financials.payables.manage-common-options-for-payables-and-procurement"
name: "Manage Common Options for Payables and Procurement Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Common Options for Payables and Procurement under the Payables functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payables"
functional_area_code: "FIN_PAYABLES_DEPLOYED"
task_code: "AP_MANAGE_COMMON_OPTIONS_FOR_PAYABLES_AND_PROCUREMENT"
task_name: "Manage Common Options for Payables and Procurement"
parent_skill_id: "erp.financials.payables"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "hybrid"
owner_team: "ERP financials pillar team"
version: "0.2.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "post_import_export_observation"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "persistence_verification"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.setup-export.fsm-csv-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.ucm-rest-client"
  - "core.fusion-api.rest-api-client"
uses_core:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.ucm-rest-client"
  - "core.fusion-api.rest-api-client"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-common-options-for-payables-and-procurement/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-common-options-for-payables-and-procurement/current/"
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
  - "Writes local preparation artifacts, validation receipts and execution evidence."
  - "Selected read-only GL validation sends one SOAP request using installed core OAuth and byte transport."
  - "Selected GL creation can create one account combination after context-specific workflow approval using installed core OAuth and byte transport."
  - "Approved post-import verification queries Core import status and starts/downloads a fresh task data export through Shared, recording local evidence."
required_privileges:
  - "Fusion privileges and OAuth scope authorizing the selected GL AccountCombinationService operation and ledger."
  - "Separately qualified setup export/import privileges for workflows delegated to shared export and core.data-loader."
---

# Manage Common Options for Payables and Procurement Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Common Options for Payables and Procurement` under `Payables`.

## Setup Task Skill Contract

- task_code: `AP_MANAGE_COMMON_OPTIONS_FOR_PAYABLES_AND_PROCUREMENT`
- task_name: `Manage Common Options for Payables and Procurement`
- parent_skill_id: `erp.financials.payables`
- pillar: `ERP`
- offering: `Financials`
- functional_area: `Payables`
- functional_area_code: `FIN_PAYABLES_DEPLOYED`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Common Options for Payables and Procurement` under `Payables`.

## Setup Task Metadata

- Task name: `Manage Common Options for Payables and Procurement`
- Task code: `AP_MANAGE_COMMON_OPTIONS_FOR_PAYABLES_AND_PROCUREMENT`
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
- Functional area / Setup Object: `Payables`
- Setup task name: `Manage Common Options for Payables and Procurement`
- Setup task code: `AP_MANAGE_COMMON_OPTIONS_FOR_PAYABLES_AND_PROCUREMENT`

## Source-Backed Task Behavior

- For a user-provided Bill-to Location name, follow `ora-resource/ora_reference_lookups.md#bill-to-location-resolution`: use HCM `locationsLov` to resolve the name, then HCM `locationsV2` to verify the same record is active, bill-to enabled, and effective. If HCM is inaccessible and `InternalLocationCode` is missing, ask the user for that code. With an explicitly supplied code, use the declared FSCM fallback; inaccessible additional checks may continue under the availability policy below. Do not invent a code, set or effective date or treat an HCM error as an empty result.
- The same-task FSM package defines one CSV member, `AP_FINANCIAL_SYS_PARAM.csv`, with 81 headers and metadata node `/FinancialsOptionVO/FinancialsOptionVORow`; preserve its exact header order and explicit trailing blanks.
- CSV export/import is catalog-supported and the import mode is `FSM`; `businessObject` remains empty because the exact archive metadata identifies the FSM object.
- For normal candidate intake, request `BuName` as the target-context value and require a fresh exact-task export. Honor a nonblank explicit `EnterpriseId` for its row; otherwise use the uniquely matched update-row value, then the single distinct nonblank export value, without asking for confirmation. Ask for an ID only when none of those sources resolves it. An explicit row override never replaces or invalidates the export default. Keep that default only in the current design/preflight artifact; see `ora-resource/ora_defaulting_rules.md#enterprise-id-precedence`. The declared ERP resolver still uses `finBusinessUnitsLOV` for the exact BU's `PrimaryLedgerId` and `ledgersLOV/{PrimaryLedgerId}` for `SOBName`. These calls do not validate EnterpriseId; Fusion performs its applicable validation during import. Unavailable, ambiguous, or inconsistent BU/ledger evidence remains a blocker; a supplied EnterpriseId cannot substitute for it.
- A source pass establishes base-entity new-row requiredness: `OrgId`, `SetOfBooksId`, and seven account CCIDs are non-null. For the FSM CSV, derive the identity from `BuName` and use `SOBName` to resolve the ledger/chart of accounts; require and preflight `AcctsPaySegments`, `PrepaySegments`, `DiscTakenSegments`, `RateVarGainSegments`, `RateVarLossSegments`, `GainSegments`, and `LossSegments`. Do not rely on the UI’s reference-integration account defaulting because the FSM import service does not invoke it. All other base-entity fields are nullable unless the import path has a separately registered validator. See `ora_input_validation.md#required-candidate-context`.
- For a first-time UI setup of a selected BU, report the source-backed defaulting outcome before preparing an FSM candidate: fixed entity defaults are `GaplessInvNumFlag=N`, `ExpenseAccrualCode=RECEIPT`, `DefaultExchangeRateType=Corporate`, `LiabilityPostLookupCode=NONE`, `MakeRateMandatoryFlag=Y`, `DefaultPmtExchangeRateType=Corporate`, and `MakeRateMandatoryPmtFlag=Y`. The two `Corporate` values are internal entity attributes, not direct CSV headers; do not infer `UserConversionRateType` or `UserDefaultPmtExchangeRateType` from them. Also report the eight conditional Reference Integration account attempts, but never auto-populate their segment fields. The UI only makes those attempts after MOAC access, Payables Invoicing eligibility, and confirmation that no options row exists. The create preview must distinguish these UI defaults from the seven account-segment values that remain explicit, separately validated FSM inputs. See `ora-resource/ora_defaulting_rules.md#standard-defaults`.
- Source establishes the CSV transport identity: the importer uses `BuName` + `EnterpriseId` to derive the persisted primary key `OrgId`. A candidate still requires a fresh current-data export to prove that this derived target is absent for a create, or present exactly once for an update. Synthetic offline regression values exercise the preparation contract only; they are not proof of environment-valid values or persisted behavior.
- For an explicitly supplied account-segment string, use `scripts/account_combination_preflight.py` to validate one through 30 supplied segments in the selected ledger. Record its receipt as validation evidence only; it does not prove a portable key or authorize the FSM import. See [SOAP execution delegation](#soap-execution-delegation) for execution and approval requirements.
- Require a resolver receipt for each supplied import-path reference: `SetCode`, `InternalLocationCode`, the two user conversion-rate type fields, `VatCountryCode`, and every account-segment field. Each successful receipt binds the operation, field, exact requested value and the design's `referenceContext` (environment, HTTPS origin, current export SHA-256, run ID and start time), retaining the actual response's `observedAt`. Select context before lookup; current preparation requires a run started within 24 hours. Follow the [receipt binding contract](ora-resource/ora_reference_lookups.md#receipt-binding-contract); never refresh a timestamp or rebind old evidence to make it pass.
- Validate supplied `ExpenseAccrualCode` and `LiabilityPostLookupCode` against the user-approved fixed choices in `ora_reference_lookups.md#user-approved-fixed-choices`. Normalize a listed UI label or exact code to the CSV code; reject unlisted or blank inputs. These two fields require no live LOV/REST lookup or resolver receipt. Omission preserves the existing update value; first-time UI defaults remain report-only, not automatically inserted into the CSV.
- Keep `GaplessInvNumFlag` and `MakeRateMandatoryFlag` closed to `Y`/`N`. A nonblank `BuyingCompanyIdentifier` (maximum 10 characters) requires effective `GaplessInvNumFlag=Y`, confirmed by normalized requested values or the fresh current export; blank, missing, or unknown flags do not qualify. This user-required preparation guardrail must not silently enable gapless numbering; clearing the identifier remains allowed. Keep the explicit-clear requirement when switching gapless to `N` and the automatic-offset derived-field prohibition.
- Treat fields without a task-specific import validator as transport-sanity-only. For those values, enforce the declared CSV type, maximum length, numeric precision, and date syntax, but do not require a current LOV, normalize a label to an unproven code, assume a Boolean encoding, or block on missing DFF metadata. This includes payment method/currency fields, ordinary flags, vendor-number and date-basis fields, tax/bank/match fields, both transaction-effective dates, and Global Attribute Category plus Global Attributes 1–20. Retain the limitation in the preview/reconciliation record: Fusion remains authoritative for deployed DFF, database, and downstream rules.
- The server-side new-row procedure initializes `PaymentMethodLookupCode`, `UserDefinedVendorNumCode`, `VendorNumStartNum`, `FuturePeriodLimit`, `ManualVendorNumType`, `ReceiptAcceptanceDays`, and `TermsDateBasis` to `NULL`: on a create, omit a blank input from requested values and retain its empty CSV cell. An optional blank update is an explicit clear subject to the same transport-sanity treatment; it is not silently defaulted. Treat `AutomaticOffsetsFlag` and `AutomaticOffsetsChangeFlag` as entity-derived values, never direct CSV inputs. See `ora_input_validation.md#transport-sanity-only-fields`.
- When GL account-combination creation is separately requested, use `scripts/account_combination_create.py` with the preview and contextual approval described in [SOAP execution delegation](#soap-execution-delegation). Follow creation with the read-only preflight.
- Run Book and `core.data-loader` own immutable-artifact processing, Task Hook preview, contextual approval, and every Payables-and-Procurement-options import or update. The separately approved account-combination SOAP creation client does not authorize a direct import or a REST mutation of task options.
- The task-owned adapter is offline and non-mutating. It can normalize, build, and validate create and update candidates under the documented preparation contract; fields without product validation receive documented transport sanity only.
- A successful reference-set receipt must contain the resolved non-null, nonblank `SetId` from the same record as the exact `returnedSetCode`; zero is a valid supplied ID. When a supplemental REST check is inaccessible, use the availability handling below; never invent `SetId` or label the set verified.
- Package validation accepts only exact terminal success statuses: `COMPLETE`, `COMPLETED`, `SUCCESS`, or `SUCCEEDED` (case-insensitive). Unknown, incomplete, warning, or error statuses stop preparation. Reconciliation requires candidate and persisted export `ProcessEnv` and `ProcessRelease` to equal the baseline before comparing row values.
- Preserve unrequested values and rows in every update; `preserveOtherValues` and `preserveUnspecifiedRows` cannot be disabled. Supply each intended field change explicitly.
- Use new, distinct paths for reports and generated artifacts; outputs must not overwrite inputs or existing files. A package manifest's environment must match its `ProcessEnv`, and its base URL must be a valid HTTPS origin without a path, query, credentials, or fragment.
- Reconciliation without a governed export observation reports `PENDING`, even when `comparisonStatus` is `PASS`. Declare saved values verified only when `persistenceVerified` is true. Follow [post-import verification](references/readback-verification.md) to collect and bind the observation to the current target, import request and exact files.
- Offline rollback requires a separate `--prerequisites` JSON array and `--reference-context` JSON file for the fresh current run and export. Bind fresh receipts to `RB-OP-001` (and subsequent rollback operation IDs), each restored reference value, and the current export's BU/ledger context. Never reuse or automatically rebind the forward receipts. Historical checks of the original forward plan retain identity checks without the 24-hour preparation limit; new rollback preparation still requires fresh evidence. Stop if current values no longer match the forward requested change. A locally built rollback ZIP is not permission to submit it.

### Unavailable Additional REST Checks

Use `core.fusion-api.rest-api-client` for the declared read-only REST lookups.
Handle access failures, missing endpoints, timeouts and service outages for set,
bill-to location, conversion-rate type and VAT reference checks as
`UNVERIFIED_API_UNAVAILABLE` warnings. Preserve the supplied CSV values and
continue preparation and preview without a separate waiver. The Run Book must
convert the core client's sanitized failure into an `unavailable` prerequisite
using the contract in `ora_reference_lookups.md`; these offline adapters make no
REST calls themselves. Carry the warning into shared validation and Data Loader
review rather than turning it into a missing-reference blocker.

Missing required CSV inputs still require user input. A completed lookup that
finds an invalid, inactive, conflicting or ambiguous value still requires
correction. BU/ledger target identity, SOAP account validation, local field rules,
Data Loader validation and approval retain their requirements. A warning is
evidence that verification could not run, not evidence that the reference passed.




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

Use the parent functional-area skill `erp.financials.payables` for functional-area sequencing and scope decisions.

## Adapter lifecycle and input-field contract

### Payables adapter and core ownership

Use a task-specific Payables adapter over a generic core API client. This split
follows the Pillar and Core Skill Audit Rules in
`governance/skill-layer-responsibilities.md`.

| Responsibility | Owner |
|---|---|
| Select the account field, environment, resolved ledger and ordered segments; bind creation approval | Payables workflow |
| Build and check the GL SOAP request; interpret the response and persist task receipts | Payables adapter |
| Authenticate and send XML bytes using the installed client's HTTP/TLS/redirect behavior | Core API client and OAuth skill |
| Evaluate account validity against the selected ledger's deployed rules | Fusion AccountCombinationService |
| Preview, approve and execute Common Options FSM imports or updates | Run Book and core.data-loader |

### SOAP execution delegation

`scripts/account_combination_workflow.py` delegates authentication and XML
byte transport to the installed functions in
`core/fusion-api/ucm-rest-client/scripts/ucm_rest_client.py`:
`get_authorization_header` for OAuth and `request_bytes` for the SOAP body.
Keep generic authentication and transport implementations in core.

Select the environment, verify operation privileges and resolve the exact
ledger before execution. The actual XML must contain one declared operation
and row matching the ledger, ordered segments and execution mode; missing,
duplicate, extra or incorrectly namespaced fields fail before authentication.

- **Validation:** `scripts/account_combination_preflight.py --ledger-name <ledger> --segments <account-string>` sends `validateAndCreateAccounts` with `DynamicInsertion=No`. This read-only operation cannot create a code combination. Use `--output` to retain its sanitized validation receipt.
- **Creation:** `scripts/account_combination_create.py` uses `DynamicInsertion=Yes`. First use `--preview-output` to write the local request identity without authentication or network calls. After contextual workflow approval, use `--approval-file` and a new `--output` receipt. Approval must be a `fscr-soap-approval-v1` record with `approved: true`, a nonblank `approvalId` and the preview's exact `request` object, binding environment/base URL, endpoint, SOAPAction, operation, ledger, ordered segments, mode and XML SHA-256. Any change invalidates that approval.

For file receipts, require a new destination distinct from inputs, approval
and token-cache files; reject linked or existing destinations. Reserve it
before authentication and persist the dispatch checkpoint before calling core.

Both commands make one core byte-client call per invocation, without
`call_with_retry` or automatic authorization refresh after a 401/403.
HTTP, TLS and redirects follow installed core behavior, with certificate
verification enabled through runtime trust configuration. Core can issue
redirect requests internally; the receipt identifies the initial endpoint,
not a verified final destination.

On authentication, transport, SOAP or persistence failure, retain available
receipt checkpoints and request identity. Do not automatically replay creation;
reconcile uncertain outcomes through the read-only preflight and obtain fresh
contextual approval before another submission. Persist durable evidence in
the project paths above and follow `ora-resource/ora_error_handling.md`.

Offline tests use installed core with mocked OAuth/HTTP responses. Live
connectivity, privileges and saved outcomes require evidence from the selected
workflow.

### SOAP response validation and redaction

Require a SOAP 1.1 Envelope with one Body containing the namespaced
`validateAndCreateAccountsResponse` and one `result`. Interpret only direct
GL service `Status` and optional `CcId` fields in that result. Validity requires
one unambiguous `Valid` status, a 2xx HTTP response and no SOAP fault;
header-only status, unrelated XML, wrong namespaces and ambiguous results
cannot establish validity.

Retain only a recognized `Status` (`Valid` or `Invalid`) and an unambiguous
positive numeric `CcId` of at most 38 ASCII digits. Omit unexpected fields,
`ErrorCode`, free text, raw fault/error bodies, authentication exception details,
tokens and Authorization headers. SOAP faults produce a fixed message and an
empty result field map. Invalid XML, NUL-containing encodings, DTD/entity
declarations and responses over 1 MiB produce bounded diagnostics without
response excerpts. The ledger/segment request identity remains in the receipt.

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_FINANCIAL_SYS_PARAM::BuName, AP_FINANCIAL_SYS_PARAM::SOBName, AP_FINANCIAL_SYS_PARAM::AcctsPaySegments, AP_FINANCIAL_SYS_PARAM::PrepaySegments, AP_FINANCIAL_SYS_PARAM::FutureDatedPaymentSegments, AP_FINANCIAL_SYS_PARAM::RateVarGainSegments, AP_FINANCIAL_SYS_PARAM::RateVarLossSegments, AP_FINANCIAL_SYS_PARAM::DiscTakenSegments, AP_FINANCIAL_SYS_PARAM::MiscChargeSegments, AP_FINANCIAL_SYS_PARAM::FreightSegments, AP_FINANCIAL_SYS_PARAM::PrepayTaxDiffSegments, AP_FINANCIAL_SYS_PARAM::GainSegments, AP_FINANCIAL_SYS_PARAM::LossSegments, AP_FINANCIAL_SYS_PARAM::ExpenseAccrualSegments, AP_FINANCIAL_SYS_PARAM::PaymentMethodLookupCode, AP_FINANCIAL_SYS_PARAM::UserDefinedVendorNumCode, AP_FINANCIAL_SYS_PARAM::VendorNumStartNum, AP_FINANCIAL_SYS_PARAM::AlwaysTakeDiscFlag, AP_FINANCIAL_SYS_PARAM::PayDateBasisLookupCode, AP_FINANCIAL_SYS_PARAM::InvoiceCurrencyCode, AP_FINANCIAL_SYS_PARAM::PaymentCurrencyCode, AP_FINANCIAL_SYS_PARAM::FuturePeriodLimit, AP_FINANCIAL_SYS_PARAM::ReqEncumbranceFlag, AP_FINANCIAL_SYS_PARAM::PurchEncumbranceFlag, AP_FINANCIAL_SYS_PARAM::ManualVendorNumType, AP_FINANCIAL_SYS_PARAM::ReceiptAcceptanceDays, AP_FINANCIAL_SYS_PARAM::TermsDateBasis, AP_FINANCIAL_SYS_PARAM::HoldUnmatchedInvoicesFlag, AP_FINANCIAL_SYS_PARAM::ExclusivePaymentFlag, AP_FINANCIAL_SYS_PARAM::VatRegistrationNum, AP_FINANCIAL_SYS_PARAM::VatCountryCode, AP_FINANCIAL_SYS_PARAM::BankChargeBearer, AP_FINANCIAL_SYS_PARAM::MatchOption, AP_FINANCIAL_SYS_PARAM::GlobalAttributeCategory, AP_FINANCIAL_SYS_PARAM::GlobalAttribute1, AP_FINANCIAL_SYS_PARAM::GlobalAttribute2, AP_FINANCIAL_SYS_PARAM::GlobalAttribute3, AP_FINANCIAL_SYS_PARAM::GlobalAttribute4, AP_FINANCIAL_SYS_PARAM::GlobalAttribute5, AP_FINANCIAL_SYS_PARAM::GlobalAttribute6, AP_FINANCIAL_SYS_PARAM::GlobalAttribute7, AP_FINANCIAL_SYS_PARAM::GlobalAttribute8, AP_FINANCIAL_SYS_PARAM::GlobalAttribute9, AP_FINANCIAL_SYS_PARAM::GlobalAttribute10, AP_FINANCIAL_SYS_PARAM::GlobalAttribute11, AP_FINANCIAL_SYS_PARAM::GlobalAttribute12, AP_FINANCIAL_SYS_PARAM::GlobalAttribute13, AP_FINANCIAL_SYS_PARAM::GlobalAttribute14, AP_FINANCIAL_SYS_PARAM::GlobalAttribute15, AP_FINANCIAL_SYS_PARAM::GlobalAttribute16, AP_FINANCIAL_SYS_PARAM::GlobalAttribute17, AP_FINANCIAL_SYS_PARAM::GlobalAttribute18, AP_FINANCIAL_SYS_PARAM::GlobalAttribute19, AP_FINANCIAL_SYS_PARAM::GlobalAttribute20, AP_FINANCIAL_SYS_PARAM::NrTaxRounding, AP_FINANCIAL_SYS_PARAM::BuyingCompanyIdentifier, AP_FINANCIAL_SYS_PARAM::GaplessInvNumFlag, AP_FINANCIAL_SYS_PARAM::ExpenseAccrualCode, AP_FINANCIAL_SYS_PARAM::LiabilityPostLookupCode, AP_FINANCIAL_SYS_PARAM::TransEffectiveStartDate, AP_FINANCIAL_SYS_PARAM::TransEffectiveEndDate, AP_FINANCIAL_SYS_PARAM::MakeRateMandatoryFlag, AP_FINANCIAL_SYS_PARAM::EnterpriseId, AP_FINANCIAL_SYS_PARAM::EffectiveStartDate, AP_FINANCIAL_SYS_PARAM::EffectiveEndDate, AP_FINANCIAL_SYS_PARAM::SetCode, AP_FINANCIAL_SYS_PARAM::InternalLocationCode, AP_FINANCIAL_SYS_PARAM::MakeRateMandatoryPmtFlag, AP_FINANCIAL_SYS_PARAM::UserConversionRateType, AP_FINANCIAL_SYS_PARAM::UserDefaultPmtExchangeRateType, AP_FINANCIAL_SYS_PARAM::OneTimePayLiabSegments, AP_FINANCIAL_SYS_PARAM::OneTimePayExpenseSegments, AP_FINANCIAL_SYS_PARAM::RetainageSegments, AP_FINANCIAL_SYS_PARAM::UnclaimedFundsSegments -->
<!-- fscr-update-fields: AP_FINANCIAL_SYS_PARAM::SOBName, AP_FINANCIAL_SYS_PARAM::AcctsPaySegments, AP_FINANCIAL_SYS_PARAM::PrepaySegments, AP_FINANCIAL_SYS_PARAM::FutureDatedPaymentSegments, AP_FINANCIAL_SYS_PARAM::RateVarGainSegments, AP_FINANCIAL_SYS_PARAM::RateVarLossSegments, AP_FINANCIAL_SYS_PARAM::DiscTakenSegments, AP_FINANCIAL_SYS_PARAM::MiscChargeSegments, AP_FINANCIAL_SYS_PARAM::FreightSegments, AP_FINANCIAL_SYS_PARAM::PrepayTaxDiffSegments, AP_FINANCIAL_SYS_PARAM::GainSegments, AP_FINANCIAL_SYS_PARAM::LossSegments, AP_FINANCIAL_SYS_PARAM::ExpenseAccrualSegments, AP_FINANCIAL_SYS_PARAM::PaymentMethodLookupCode, AP_FINANCIAL_SYS_PARAM::UserDefinedVendorNumCode, AP_FINANCIAL_SYS_PARAM::VendorNumStartNum, AP_FINANCIAL_SYS_PARAM::AlwaysTakeDiscFlag, AP_FINANCIAL_SYS_PARAM::PayDateBasisLookupCode, AP_FINANCIAL_SYS_PARAM::InvoiceCurrencyCode, AP_FINANCIAL_SYS_PARAM::PaymentCurrencyCode, AP_FINANCIAL_SYS_PARAM::FuturePeriodLimit, AP_FINANCIAL_SYS_PARAM::ReqEncumbranceFlag, AP_FINANCIAL_SYS_PARAM::PurchEncumbranceFlag, AP_FINANCIAL_SYS_PARAM::ManualVendorNumType, AP_FINANCIAL_SYS_PARAM::ReceiptAcceptanceDays, AP_FINANCIAL_SYS_PARAM::TermsDateBasis, AP_FINANCIAL_SYS_PARAM::HoldUnmatchedInvoicesFlag, AP_FINANCIAL_SYS_PARAM::ExclusivePaymentFlag, AP_FINANCIAL_SYS_PARAM::VatRegistrationNum, AP_FINANCIAL_SYS_PARAM::VatCountryCode, AP_FINANCIAL_SYS_PARAM::BankChargeBearer, AP_FINANCIAL_SYS_PARAM::MatchOption, AP_FINANCIAL_SYS_PARAM::GlobalAttributeCategory, AP_FINANCIAL_SYS_PARAM::GlobalAttribute1, AP_FINANCIAL_SYS_PARAM::GlobalAttribute2, AP_FINANCIAL_SYS_PARAM::GlobalAttribute3, AP_FINANCIAL_SYS_PARAM::GlobalAttribute4, AP_FINANCIAL_SYS_PARAM::GlobalAttribute5, AP_FINANCIAL_SYS_PARAM::GlobalAttribute6, AP_FINANCIAL_SYS_PARAM::GlobalAttribute7, AP_FINANCIAL_SYS_PARAM::GlobalAttribute8, AP_FINANCIAL_SYS_PARAM::GlobalAttribute9, AP_FINANCIAL_SYS_PARAM::GlobalAttribute10, AP_FINANCIAL_SYS_PARAM::GlobalAttribute11, AP_FINANCIAL_SYS_PARAM::GlobalAttribute12, AP_FINANCIAL_SYS_PARAM::GlobalAttribute13, AP_FINANCIAL_SYS_PARAM::GlobalAttribute14, AP_FINANCIAL_SYS_PARAM::GlobalAttribute15, AP_FINANCIAL_SYS_PARAM::GlobalAttribute16, AP_FINANCIAL_SYS_PARAM::GlobalAttribute17, AP_FINANCIAL_SYS_PARAM::GlobalAttribute18, AP_FINANCIAL_SYS_PARAM::GlobalAttribute19, AP_FINANCIAL_SYS_PARAM::GlobalAttribute20, AP_FINANCIAL_SYS_PARAM::NrTaxRounding, AP_FINANCIAL_SYS_PARAM::BuyingCompanyIdentifier, AP_FINANCIAL_SYS_PARAM::GaplessInvNumFlag, AP_FINANCIAL_SYS_PARAM::ExpenseAccrualCode, AP_FINANCIAL_SYS_PARAM::LiabilityPostLookupCode, AP_FINANCIAL_SYS_PARAM::TransEffectiveStartDate, AP_FINANCIAL_SYS_PARAM::TransEffectiveEndDate, AP_FINANCIAL_SYS_PARAM::MakeRateMandatoryFlag, AP_FINANCIAL_SYS_PARAM::EffectiveStartDate, AP_FINANCIAL_SYS_PARAM::EffectiveEndDate, AP_FINANCIAL_SYS_PARAM::SetCode, AP_FINANCIAL_SYS_PARAM::InternalLocationCode, AP_FINANCIAL_SYS_PARAM::MakeRateMandatoryPmtFlag, AP_FINANCIAL_SYS_PARAM::UserConversionRateType, AP_FINANCIAL_SYS_PARAM::UserDefaultPmtExchangeRateType, AP_FINANCIAL_SYS_PARAM::OneTimePayLiabSegments, AP_FINANCIAL_SYS_PARAM::OneTimePayExpenseSegments, AP_FINANCIAL_SYS_PARAM::RetainageSegments, AP_FINANCIAL_SYS_PARAM::UnclaimedFundsSegments -->

The current offline preparation contract allows 74 create inputs (including two
selector keys through `targetKey`) and 72 update inputs. The five audit fields
and two derived automatic-offset flags are never caller inputs; update keys
remain immutable. `SOBName` is derived from ERP primary-ledger evidence, not a
ledger-reassignment option. Existing per-field checks and bound receipts still
apply. Fields governed by the approved sanity-only policy remain accepted after
those checks; no new LOV or uncertainty-approval gate is introduced. This is
preparation support, not proof that every accepted value persists in Fusion.
Unspecified update values remain unchanged; UI defaults remain report-only.

The structured create/update declarations in the authoring run state and the
current task resources govern regeneration. Do not restore obsolete unresolved
intake blockers or the former Procurement placement. Keep Financials / Payables
ownership.
