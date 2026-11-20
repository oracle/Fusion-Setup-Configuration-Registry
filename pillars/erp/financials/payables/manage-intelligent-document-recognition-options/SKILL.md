---
skill_id: "erp.financials.payables.manage-intelligent-document-recognition-options"
name: "Manage Intelligent Document Recognition Options Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Intelligent Document Recognition Options under the Payables functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payables"
functional_area_code: "FIN_PAYABLES_DEPLOYED"
task_code: "ORA_MANAGE_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS"
task_name: "Manage Intelligent Document Recognition Options"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-intelligent-document-recognition-options/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-intelligent-document-recognition-options/current/"
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

# Manage Intelligent Document Recognition Options Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Intelligent Document Recognition Options` under `Payables`.

## Setup Task Skill Contract

- task_code: `ORA_MANAGE_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS`
- task_name: `Manage Intelligent Document Recognition Options`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Intelligent Document Recognition Options` under `Payables`.

## Setup Task Metadata

- Task name: `Manage Intelligent Document Recognition Options`
- Task code: `ORA_MANAGE_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS`
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
- Setup task name: `Manage Intelligent Document Recognition Options`
- Setup task code: `ORA_MANAGE_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS`




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

Use the parent functional-area skill `erp.financials.payables` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.


<!-- fscr-supported-operations: update -->
<!-- fscr-update-fields: ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::BuDerivationBasisCode, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::CalcTaxDuringImportFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::EnforceIncompleteStatusFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ImportFreightAmountFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ImportLinesMatchedFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ImportLinesUnmatchedFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ImportPairedLinesOnlyFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::SingleLineAmountPoFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::SingleLineUtilityInvFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::UseTaxAmountAsControlFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::RequesterEmailDomain, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ValidatePoLeFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ConvertEmailIntoAttachFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTION_EXTENSIONS::EnabledFlag -->
**Normal update fields:** the annotation above lists normal allowlist support only. **Governed mapping update:** `ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::Mappings` is additionally available through its exact-field serialized-XML validation path. It is not included in the normal allowlist.


## IDR update contract

This setup task updates an existing Intelligent Document Recognition configuration. Create is unsupported for both the options row and extension rows. Resolve the existing target record before preparing any update. Route approved FSM imports through core.data-loader; this skill and its resources own validation, defaults and design checks.

Require a completed, exact-task export from the target environment immediately before an options update. Its `ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS.csv` must contain exactly one data row. Treat that row as the existing singleton and preserve its unrelated fields. Zero or multiple rows block the update; do not create a row or arbitrarily choose one. The task-local adapter enforces this row-count rule and reconciles the singleton.

For extension changes, accept only the existing row with OptionCode AP_PRORATE_FREIGHT_MISC. Reject other codes, including ORA_AP_IMAGES and ORA_POLICY_DETAILS. Update only EnabledFlag on that selected row. Never create a missing row or rewrite its OptionCode.

Apply no business defaults on update. Preserve every unrequested non-audit value on targeted rows. Generated update rows leave the declared audit cells blank, as required by the package contract; this is not permission to change a business field. When the requester explicitly leaves Override Default Business Unit unselected, use code `N`.

## Requested field update policy

This task prohibits changes to `ProcessDocAttachmentFlag`, `ProcessDocxAttachmentFlag`, `ProcessPdfAttachmentFlag`, `ProcessTiffAttachmentFlag`, `ProcessPngAttachmentFlag`, and `ProcessJpegAttachmentFlag`. Reject an actual change to any of these fields. Interpret supported labels only to compare the request with the fresh target baseline; do not rewrite the exported image-format values. When the interpreted request exactly matches the baseline, accept it as a no-op; an image-only no-op writes no candidate ZIP, and an unchanged image value does not block another valid field update. Missing baseline evidence blocks this exception. No application-validation override may authorize a changed image-format value. Preserve their current exported values in generated candidates and reject prepared ZIPs that change them.

The intended UI scope contains 15 settings: 13 options fields with normal update support, the governed `Mappings` field, and the extension `EnabledFlag`. Allow normal updates to these 13 options fields: `BuDerivationBasisCode`, `UseTaxAmountAsControlFlag`, `ImportFreightAmountFlag`, `ImportLinesMatchedFlag`, `ImportLinesUnmatchedFlag`, `ValidatePoLeFlag`, `ConvertEmailIntoAttachFlag`, `RequesterEmailDomain`, `CalcTaxDuringImportFlag`, `EnforceIncompleteStatusFlag`, `SingleLineAmountPoFlag`, `SingleLineUtilityInvFlag`, and `ImportPairedLinesOnlyFlag`. `IdrActivationStatus` (Status) is display-only both before and after activation. Reject an explicit Status update even when it repeats the current value; the image-format no-op exception does not apply to Status. Reject Status, IDR email, other internal mappings, reference keys, flexfield attributes and every other non-UI field, including through overrides. `Mappings` is the UI mapping-dialog exception described below. Preserve their exported values on targeted rows and verify retained target state. For extensions, select only the existing `OptionCode=AP_PRORATE_FREIGHT_MISC` row and update only `EnabledFlag` (Y/N). Reject changes to every other extension field, including through an override; preserve all unrequested fields and rows and never rewrite the key. Apply declared types, limits and value contracts; use Y/N for supported on/off fields and retain the special email-flag and business-unit blank rules. Apply no defaults.

The normal update allowlist contains 14 fields across both entities; `Mappings` is the additional, conditionally governed setting. The `fscr-update-fields` comments list normal support only. Normal target validation, candidate approval, Fusion validation and fresh readback remain required.

## Source-Backed Task Behavior

- Update existing IDR options and extension rows only; create is unsupported. Require exactly one options data row in the fresh target export and treat it as the singleton; block zero or multiple rows.
- Select the existing extension row by `OptionCode=AP_PRORATE_FREIGHT_MISC`, update only `EnabledFlag`, and reject every other extension code.
- Map Override Default Business Unit selections to `RA`, `SE`, or `RE`. A deliberately empty selection maps to `N`; omission preserves the existing value.

## UI wording to persisted and package fields

The UI labels below map to the database columns and FSM CSV attributes. `DOC`, `DOCX`, `PDF`, `TIFF`, `PNG` and `JPEG` appear under **Image Attachment Formats**. Preserve these six fields; an explicitly unchanged value requires comparison with the fresh baseline. The update scope contains the 13 normal options fields, Email to Business Unit Mapping through its governed path, and extension `EnabledFlag`. Status is display-only. If a phrase is ambiguous, ask which field is intended.

| UI wording supplied | Database column | FSM CSV attribute |
|---|---|---|
| Override Default Business Unit | AP_IDR_OPTIONS.BU_DERIVATION_BASIS_CODE | BuDerivationBasisCode |
| Email to Business Unit Mapping dialog | AP_IDR_OPTIONS.BU_EMAIL_MAPPING | Mappings |
| Recognize tax amount | AP_IDR_OPTIONS.USE_TAX_AMOUNT_AS_CONTROL_FLAG | UseTaxAmountAsControlFlag |
| Recognize freight amount | AP_IDR_OPTIONS.IMPORT_FREIGHT_AMOUNT_FLAG | ImportFreightAmountFlag |
| Always create invoices in incomplete status | AP_IDR_OPTIONS.ENFORCE_INCOMPLETE_STATUS_FLAG | EnforceIncompleteStatusFlag |
| Calculate tax during import | AP_IDR_OPTIONS.CALC_TAX_DURING_IMPORT_FLAG | CalcTaxDuringImportFlag |
| Import only paired lines for matched invoices | AP_IDR_OPTIONS.IMPORT_PAIRED_LINES_ONLY_FLAG | ImportPairedLinesOnlyFlag |
| Recognize lines for matched invoices | AP_IDR_OPTIONS.IMPORT_LINES_MATCHED_FLAG | ImportLinesMatchedFlag |
| Recognize lines for unmatched invoices | AP_IDR_OPTIONS.IMPORT_LINES_UNMATCHED_FLAG | ImportLinesUnmatchedFlag |
| Create single invoice line for service orders | AP_IDR_OPTIONS.SINGLE_LINE_AMOUNT_PO_FLAG | SingleLineAmountPoFlag |
| Create single invoice line for utility suppliers | AP_IDR_OPTIONS.SINGLE_LINE_UTILITY_INV_FLAG | SingleLineUtilityInvFlag |
| DOC | AP_IDR_OPTIONS.PROCESS_DOC_ATTACHMENT_FLAG | ProcessDocAttachmentFlag |
| DOCX | AP_IDR_OPTIONS.PROCESS_DOCX_ATTACHMENT_FLAG | ProcessDocxAttachmentFlag |
| PDF | AP_IDR_OPTIONS.PROCESS_PDF_ATTACHMENT_FLAG | ProcessPdfAttachmentFlag |
| TIFF | AP_IDR_OPTIONS.PROCESS_TIFF_ATTACHMENT_FLAG | ProcessTiffAttachmentFlag |
| PNG | AP_IDR_OPTIONS.PROCESS_PNG_ATTACHMENT_FLAG | ProcessPngAttachmentFlag |
| JPEG | AP_IDR_OPTIONS.PROCESS_JPEG_ATTACHMENT_FLAG | ProcessJpegAttachmentFlag |
| Requester Email Domain Name | AP_IDR_OPTIONS.REQUESTER_EMAIL_DOMAIN | RequesterEmailDomain |
| Validate the legal entity identified for matched invoices | AP_IDR_OPTIONS.VALIDATE_PO_LE_FLAG | ValidatePoLeFlag |
| Convert email into attachment | AP_IDR_OPTIONS.CONVERT_EMAIL_INTO_ATTACH_FLAG | ConvertEmailIntoAttachFlag |
| Status | AP_IDR_OPTIONS.IDR_ACTIVATION_STATUS | IdrActivationStatus |
| Prorate freight and miscellaneous lines | AP_IDR_OPTION_EXTENSIONS.ENABLED_FLAG with OptionCode=AP_PRORATE_FREIGHT_MISC | EnabledFlag |

## Email to Business Unit Mapping

Update the Email to Business Unit Mapping setting through `Mappings`. Specify the email addresses, existing business-unit names and the intended additions, assignment changes, removals or clearing operation. Preserve the mapping when it is omitted from the request.

Provide `Mappings` as the complete intended list of rows, each with exactly `email` and `businessUnit` strings, or as serialized mapping XML. The adapter converts row lists to escaped XML and checks the supported XML shape, email inputs, explicit BU names and duplicate email rows. An empty list clears the collection. Retain every unrequested assignment. BU existence and application-specific reference validity are validated by Fusion during the approved import; local validation does not claim a successful BU lookup. Use the governed exact-field application-validation path, obtain the required informed acceptance, approve the exact import ZIP and verify saved rows after import.

Preserve the internal `BuEmailMapping` and `MappingUpdated` fields; neither may be directly updated. Technical mapping requirements are defined in `ora-resource/ora_input_validation.md`, `ora-resource/ora_reference_lookups.md` and `ora-resource/ora_dependency_readiness.md`.

### Preparing a mapping restore

Prepare restoration only when explicitly requested. The `rollback` command calculates values from the original and fresh current exports. For a governed mapping restore, supply `--governed-design` with exactly `operations` and `evidenceUnresolvedUpdateOverrides`. The operations must match the calculated restoration IDs, target, original values and preservation flags exactly; the override must bind to those restore operations with fresh informed acceptance. Forward approval is not reused. The command only builds local artifacts; a separate approval is required before importing the restore ZIP. Do not restore when the requester has chosen to retain the saved state.

## Override Default Business Unit choices

| UI choice | BuDerivationBasisCode |
|---|---|
| Email Routing Attribute | RA |
| Sender's Email Address | SE |
| Recipient Email Address | RE |
| No selection (empty field) | N |

Trim surrounding whitespace and accept a case-insensitive exact named choice or code. An explicitly supplied empty value means `N`; an omitted field means no change. Reject unknown values before candidate authoring.

## Task-local resources

Read ora-resource/ora_input_validation.md for request shape and supported fields, ora-resource/ora_reference_lookups.md for lookup contracts, ora-resource/ora_dependency_readiness.md for prerequisites, ora-resource/ora_defaulting_rules.md for the no-default update rule, ora-resource/ora_design_enforcement.md for mandatory gates, and ora-resource/ora_error_handling.md for refusal and retry behavior. The compiled ora-resource/ora_rule_registry.json describes local workflow nodes. The adapter's conditional and unresolved field contracts enforce target evidence and mapping-specific gates; a ready workflow node does not qualify every field for normal updates.

## Source boundary

The task identity and routing come from the effective FSM catalog. CSV field names and hierarchy come from exact-task setup metadata. The label-to-field mapping, update-only rule, extension allowlist, and business-unit choices are part of the reviewed task contract.

Do not treat a row from another environment as a target record or a source of product defaults. Do not place source ZIPs, email addresses, environment names, credentials or generated candidate data in this task skill.

## Prepared ZIP validation parity

Apply the same task business rules to NLP requests and prepared/uploaded ZIPs before approval: operation and field ownership, create/update matching, parent and required-child rules, lookup outcomes, allowed codes, required values, dates, limits, audit rules and preservation. ZIP structure validation alone is insufficient. Use a fresh exact-task baseline and an explicit operation design; unresolved intent or missing evidence blocks validation rather than assuming an upsert or inferring parent creation. The task-local `validate` command requires the template, baseline, blueprint and requirements and checks actual package values against that validated design. Do not substitute `manifest` inspection for business validation.

Treat the uploaded archive as immutable input. Report member, record key, field and rule for identified problems; never default, normalize labels, clear audit cells, add parents/children, remove rows or rebuild the ZIP during validation. Report files must be distinct from every input and must not overwrite existing files. A correction requires an explicit revised request or artifact, a separate candidate, renewed validation and the normal artifact-bound approval. A hash or completed import job alone does not establish business validity.

## Final-state batch validation

Before import, start from a fresh, sufficiently complete exact-task baseline and overlay all explicitly requested updates in memory; reject creates. Preserve omitted fields and retained records; omission is not deletion. Validate the resulting affected state as one batch, comparing changed/new records with one another and with retained records. Row-by-row success is insufficient. Evaluate final values rather than transient operation order, and reject duplicate target operations rather than choosing a last writer. Missing baseline coverage or an unresolved applicable rule blocks the affected batch; do not fabricate prerequisite records or remove conflicting rows to make it pass.

Retain the required existing options singleton and untargeted extension rows in target state. The import ZIP is an update delta: include only explicitly targeted rows, with their unrequested non-audit fields preserved; leave untargeted rows out of the ZIP. Their omission is not a delete request. Verify their preservation against a full post-import export. Apply all requested updates to that baseline together, preserve the extension allowlist and field-choice contracts, and reject duplicate operations on one target. Create remains unsupported; do not infer additional cross-field restrictions without evidence. Both NLP and prepared-ZIP paths must pass this gate before approval/import. For ZIPs, compare against the proposed final state without changing the upload; identify the conflicting record keys and applicable rule in diagnostics. Do not require unrelated baseline defects to be repaired unless the requested change depends on them.

## Input, target and evidence boundaries

- Keep source ZIPs, baselines, requests, contracts and existing artifacts immutable. Resolve output paths and check symlink/hardlink aliases before writing; exclusively create every output, including failure reports. Reject collisions among all outputs before starting an action. A late file appearing after preflight must not be overwritten.
- Use the independently selected Fusion environment and credential-free HTTPS origin as the target. The authentication profile is a separate input; do not derive an environment by stripping authentication labels. Match `ProcessEnv` to the selected environment, and match template/baseline environment and release. A matching ZIP hash cannot establish its own trusted target or reference evidence.
- Use the active export service's documented successful statuses (`COMPLETED` and `COMPLETED_WARNINGS` in the reviewed service); retain warnings for review. A downloadable ZIP, completed request or substring such as `INCOMPLETE` or `COMPLETED_ERRORS` is not process success. Validate real boolean template flags and reject a template-only label on populated CSV data; an empty current-data export is still possible.
- A URL must be an HTTPS origin without credentials, path, query or fragment. Do not accept a malformed host or use an evidence-supplied origin as the trusted target. Check package identity, member/header/type/path contracts and the supported release compatibility policy independently of labels.
- Preserve every unrequested business field and retained row on updates. `preserveOtherValues` and `preserveUnspecifiedRows` cannot disable this rule. Only explicitly requested, allowed changes may differ; this task declares no dependent clears or defaults. Validate uploaded ZIPs against that same effective design without rewriting the upload.
- At the live workflow gate, parse timezone-aware reference/import/readback timestamps, apply that workflow's actual freshness policy and require the verification export to follow the completed import. Reject malformed, timezone-free, stale, future or out-of-order evidence. File comparison alone does not confirm saved Fusion values; require target-bound import and fresh-export evidence from the supported workflow. Do not invent a time-to-live or persist evidence prohibited by the active Data Loader contract.
- Validate generated node sequences according to a reviewed sequencing policy; keep business identity, XML grouping, headers, types and relationships authoritative. Do not renumber exports or guess XML-file groups to bypass a compatibility gap.

The task-local offline adapter enforces exclusive output creation, exact export statuses, selected-environment manifest checks, strict origin/template labels, template/baseline compatibility and mandatory update preservation. Its reconciliation result remains `PENDING` with `persistenceVerified=false`; a matching comparison is separate from live verification. The adapter does not execute live reference calls or submit imports. Existing source-backed operation, field and default contracts remain binding.

## Selected Fusion target and authentication profile

Before preparing exports or task data, retain the independently confirmed Fusion
environment name and credential-free HTTPS origin in the project target context.
Retain the selected OAuth `environment` value separately as the authentication
profile. The names may be unrelated (for example, profile `DEV` and Fusion
environment `example-fusion`). Reuse a previously confirmed target; ask for its
actual identity only when it is missing or ambiguous. Never derive it by removing
a profile suffix or guessing from a hostname, ZIP or reference receipt.

Pass the actual selected Fusion name to task manifest/target-validation inputs,
and require it to match export `ProcessEnv`. Require the selected origin to match
the authenticated configured origin. Compare the login profile only with the
profile bound to the Data Loader preflight; do not compare it with `ProcessEnv`.
Keep task, release/schema, Run Book, archive-integrity and approval checks intact.
If a workflow accepts `referenceContext`, supply the separately selected target
there; do not invent that CLI option for adapters that do not declare it. This
identity handling grants no additional execution or import capability.


## Export Metadata Identity

Identify the options and extensions objects by their exact business object names
and XML paths. Accept positive export-local sequence numbers rather than requiring
a fixed 1/2 assignment. Reject same-level sequence collisions and preserve
Oracle metadata unchanged. The two XML roots are not a parent/child relationship.
See ora-resource/ora_design_enforcement.md, Metadata Object Identity.
