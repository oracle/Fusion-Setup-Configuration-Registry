---
skill_id: "erp.financials.payables.manage-payment-terms"
name: "Manage Payment Terms Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Payment Terms under the Payables functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payables"
functional_area_code: "FIN_PAYABLES_DEPLOYED"
task_code: "AP_MANAGE_PAYMENT_TERMS"
task_name: "Manage Payment Terms"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-payment-terms/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-payment-terms/current/"
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

# Manage Payment Terms Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Payment Terms` under `Payables`.

## Supported Operations

This task supports creating and updating Payment Terms setup records. It does not support delete or end-date operations. Only the operation-specific fields documented in [Input Validation](ora-resource/ora_input_validation.md) and [Design Enforcement](ora-resource/ora_design_enforcement.md) are permitted; all other fields remain blocked.

## Task Behavior

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_TERM_HEADER::Name, AP_TERM_HEADER::EnabledFlag, AP_TERM_HEADER::DueCutoffDay, AP_TERM_HEADER::Type, AP_TERM_HEADER::StartDateActive, AP_TERM_HEADER::EndDateActive, AP_TERM_HEADER::Rank, AP_TERM_HEADER::AttributeCategory, AP_TERM_HEADER::Attribute1, AP_TERM_HEADER::Attribute2, AP_TERM_HEADER::Attribute3, AP_TERM_HEADER::Attribute4, AP_TERM_HEADER::Attribute5, AP_TERM_HEADER::Attribute6, AP_TERM_HEADER::Attribute7, AP_TERM_HEADER::Attribute8, AP_TERM_HEADER::Attribute9, AP_TERM_HEADER::Attribute10, AP_TERM_HEADER::Attribute11, AP_TERM_HEADER::Attribute12, AP_TERM_HEADER::Attribute13, AP_TERM_HEADER::Attribute14, AP_TERM_HEADER::Attribute15, AP_TERM_HEADER::Description, AP_TERM_HEADER::GlobalAttributeCategory, AP_TERM_HEADER::GlobalAttribute1, AP_TERM_HEADER::GlobalAttribute2, AP_TERM_HEADER::GlobalAttribute3, AP_TERM_HEADER::GlobalAttribute4, AP_TERM_HEADER::GlobalAttribute5, AP_TERM_HEADER::GlobalAttribute6, AP_TERM_HEADER::GlobalAttribute7, AP_TERM_HEADER::GlobalAttribute8, AP_TERM_HEADER::GlobalAttribute9, AP_TERM_HEADER::GlobalAttribute10, AP_TERM_HEADER::GlobalAttribute11, AP_TERM_HEADER::GlobalAttribute12, AP_TERM_HEADER::GlobalAttribute13, AP_TERM_HEADER::GlobalAttribute14, AP_TERM_HEADER::GlobalAttribute15, AP_TERM_HEADER::GlobalAttribute16, AP_TERM_HEADER::GlobalAttribute17, AP_TERM_HEADER::GlobalAttribute18, AP_TERM_HEADER::GlobalAttribute19, AP_TERM_HEADER::GlobalAttribute20, AP_TERM_HEADER::GlobalAttributeDate1, AP_TERM_HEADER::GlobalAttributeDate2, AP_TERM_HEADER::GlobalAttributeDate3, AP_TERM_HEADER::GlobalAttributeDate4, AP_TERM_HEADER::GlobalAttributeDate5, AP_TERM_HEADER::GlobalAttributeNumber1, AP_TERM_HEADER::GlobalAttributeNumber2, AP_TERM_HEADER::GlobalAttributeNumber3, AP_TERM_HEADER::GlobalAttributeNumber4, AP_TERM_HEADER::GlobalAttributeNumber5, AP_TERM_LINE::AP_TERM_HEADER.Name, AP_TERM_LINE::SequenceNum, AP_TERM_LINE::DuePercent, AP_TERM_LINE::DueAmount, AP_TERM_LINE::DueDays, AP_TERM_LINE::DueDayOfMonth, AP_TERM_LINE::DueMonthsForward, AP_TERM_LINE::DiscountPercent, AP_TERM_LINE::DiscountDays, AP_TERM_LINE::DiscountDayOfMonth, AP_TERM_LINE::DiscountMonthsForward, AP_TERM_LINE::DiscountPercent2, AP_TERM_LINE::DiscountDays2, AP_TERM_LINE::DiscountDayOfMonth2, AP_TERM_LINE::DiscountMonthsForward2, AP_TERM_LINE::DiscountPercent3, AP_TERM_LINE::DiscountDays3, AP_TERM_LINE::DiscountDayOfMonth3, AP_TERM_LINE::DiscountMonthsForward3, AP_TERM_LINE::AttributeCategory, AP_TERM_LINE::Attribute1, AP_TERM_LINE::Attribute2, AP_TERM_LINE::Attribute3, AP_TERM_LINE::Attribute4, AP_TERM_LINE::Attribute5, AP_TERM_LINE::Attribute6, AP_TERM_LINE::Attribute7, AP_TERM_LINE::Attribute8, AP_TERM_LINE::Attribute9, AP_TERM_LINE::Attribute10, AP_TERM_LINE::Attribute11, AP_TERM_LINE::Attribute12, AP_TERM_LINE::Attribute13, AP_TERM_LINE::Attribute14, AP_TERM_LINE::Attribute15, AP_TERM_LINE::FixedDate, AP_TERM_LINE::Calendar, AP_TERM_SUBSCRIPTION::AP_TERM_HEADER.Name, AP_TERM_SUBSCRIPTION::SetCode, AP_TERM_HEADER_TRANSLATION::AP_TERM_HEADER.Name, AP_TERM_HEADER_TRANSLATION::Name, AP_TERM_HEADER_TRANSLATION::Description, AP_TERM_HEADER_TRANSLATION::Language, AP_TERM_HEADER_TRANSLATION::SourceLang -->
<!-- fscr-update-fields: AP_TERM_HEADER::EnabledFlag, AP_TERM_HEADER::DueCutoffDay, AP_TERM_HEADER::Type, AP_TERM_HEADER::StartDateActive, AP_TERM_HEADER::EndDateActive, AP_TERM_HEADER::Rank, AP_TERM_HEADER::AttributeCategory, AP_TERM_HEADER::Attribute1, AP_TERM_HEADER::Attribute2, AP_TERM_HEADER::Attribute3, AP_TERM_HEADER::Attribute4, AP_TERM_HEADER::Attribute5, AP_TERM_HEADER::Attribute6, AP_TERM_HEADER::Attribute7, AP_TERM_HEADER::Attribute8, AP_TERM_HEADER::Attribute9, AP_TERM_HEADER::Attribute10, AP_TERM_HEADER::Attribute11, AP_TERM_HEADER::Attribute12, AP_TERM_HEADER::Attribute13, AP_TERM_HEADER::Attribute14, AP_TERM_HEADER::Attribute15, AP_TERM_HEADER::Description, AP_TERM_HEADER::GlobalAttributeCategory, AP_TERM_HEADER::GlobalAttribute1, AP_TERM_HEADER::GlobalAttribute2, AP_TERM_HEADER::GlobalAttribute3, AP_TERM_HEADER::GlobalAttribute4, AP_TERM_HEADER::GlobalAttribute5, AP_TERM_HEADER::GlobalAttribute6, AP_TERM_HEADER::GlobalAttribute7, AP_TERM_HEADER::GlobalAttribute8, AP_TERM_HEADER::GlobalAttribute9, AP_TERM_HEADER::GlobalAttribute10, AP_TERM_HEADER::GlobalAttribute11, AP_TERM_HEADER::GlobalAttribute12, AP_TERM_HEADER::GlobalAttribute13, AP_TERM_HEADER::GlobalAttribute14, AP_TERM_HEADER::GlobalAttribute15, AP_TERM_HEADER::GlobalAttribute16, AP_TERM_HEADER::GlobalAttribute17, AP_TERM_HEADER::GlobalAttribute18, AP_TERM_HEADER::GlobalAttribute19, AP_TERM_HEADER::GlobalAttribute20, AP_TERM_HEADER::GlobalAttributeDate1, AP_TERM_HEADER::GlobalAttributeDate2, AP_TERM_HEADER::GlobalAttributeDate3, AP_TERM_HEADER::GlobalAttributeDate4, AP_TERM_HEADER::GlobalAttributeDate5, AP_TERM_HEADER::GlobalAttributeNumber1, AP_TERM_HEADER::GlobalAttributeNumber2, AP_TERM_HEADER::GlobalAttributeNumber3, AP_TERM_HEADER::GlobalAttributeNumber4, AP_TERM_HEADER::GlobalAttributeNumber5, AP_TERM_LINE::DuePercent, AP_TERM_LINE::DueAmount, AP_TERM_LINE::DueDays, AP_TERM_LINE::DueDayOfMonth, AP_TERM_LINE::DueMonthsForward, AP_TERM_LINE::DiscountPercent, AP_TERM_LINE::DiscountDays, AP_TERM_LINE::DiscountDayOfMonth, AP_TERM_LINE::DiscountMonthsForward, AP_TERM_LINE::DiscountPercent2, AP_TERM_LINE::DiscountDays2, AP_TERM_LINE::DiscountDayOfMonth2, AP_TERM_LINE::DiscountMonthsForward2, AP_TERM_LINE::DiscountPercent3, AP_TERM_LINE::DiscountDays3, AP_TERM_LINE::DiscountDayOfMonth3, AP_TERM_LINE::DiscountMonthsForward3, AP_TERM_LINE::AttributeCategory, AP_TERM_LINE::Attribute1, AP_TERM_LINE::Attribute2, AP_TERM_LINE::Attribute3, AP_TERM_LINE::Attribute4, AP_TERM_LINE::Attribute5, AP_TERM_LINE::Attribute6, AP_TERM_LINE::Attribute7, AP_TERM_LINE::Attribute8, AP_TERM_LINE::Attribute9, AP_TERM_LINE::Attribute10, AP_TERM_LINE::Attribute11, AP_TERM_LINE::Attribute12, AP_TERM_LINE::Attribute13, AP_TERM_LINE::Attribute14, AP_TERM_LINE::Attribute15, AP_TERM_LINE::FixedDate, AP_TERM_LINE::Calendar, AP_TERM_HEADER_TRANSLATION::Name, AP_TERM_HEADER_TRANSLATION::Description, AP_TERM_HEADER_TRANSLATION::SourceLang -->

- Take every `AP_TERM_*` CSV header and its order from the exact FSM template
  for this task. Reject short or long rows, and keep explicit trailing blank
  fields. See `ora-resource/ora_input_validation.md` and
  `ora-resource/ora_rule_registry.json`.
- Build the package with these keys:
  `AP_TERM_HEADER.Name`; `AP_TERM_LINE.AP_TERM_HEADER.Name + SequenceNum`;
  `AP_TERM_SUBSCRIPTION.AP_TERM_HEADER.Name + SetCode`; and
  `AP_TERM_HEADER_TRANSLATION.AP_TERM_HEADER.Name + Language`. Fusion resolves
  the root alternate key and derives internal parent keys. Never put an
  internal ID in the CSV. See `ora-resource/ora_design_enforcement.md`.
- For every create or update of an `AP_TERM_LINE`, `AP_TERM_SUBSCRIPTION`,
  or `AP_TERM_HEADER_TRANSLATION` row, include the matching `AP_TERM_HEADER`
  row in the same FSM archive. Unless an explicit header operation supplies
  it, copy the parent unchanged from the fresh current-data export and blank
  all audit fields. Include each parent only once. Block generation if the
  parent is absent from both the explicit operations and the fresh baseline;
  validation must reject missing or changed supporting parents.
  Fusion can mark a child-only archive as successfully imported while skipping
  its update. The non-production `AP_TERM_LINE` test proved this behavior:
  a child-only `DueDays` change remained unpersisted after a successful import.
- A new `AP_TERM_HEADER` must include at least one explicitly requested
  `AP_TERM_LINE` installment for that same header in the package. This applies
  to enabled and disabled new terms. A set assignment or translation does not
  replace an installment. Stop before preview or ZIP generation with
  `AP_AT_LEAST_ONE_CHILD` and ask for installment details; never invent a line.
  For an existing term, a header update or child create/update does not require
  adding another installment. Keep its existing installments unchanged unless
  the user requests a change.
- For a create with `AP_TERM_HEADER_TRANSLATION` rows, use the header key
  as the logical target. Fusion may display and export the explicit US
  translation name instead of that key. Derive this alias only from the
  candidate's US translation row, use it for reconciliation and UI proof, and
  record the header-key-to-display-name mapping. A KO row is translation
  evidence, not another payment-term header.
- For a new payment-term header, default an omitted or blank `EnabledFlag` to `Y`, `Type` to `STD`, and `StartDateActive` to the package-builder system date in `YYYY/MM/DD`; record each applied value as an explicit default and serialize it into the CSV. A supplied `Type` must be exactly `STD`; reject every other Type before package generation. Other explicit request values override their corresponding defaults. See `ora-resource/ora_defaulting_rules.md`.
- When preparing an import ZIP, use the date format shown in the fresh export for new or changed dates. Keep unchanged dates exactly as exported.
- Validate header dates and Rank before package generation. Dates must use the supported calendar-date format, and `EndDateActive` cannot precede `StartDateActive`. Rank is compared globally across Payment Terms, must be a whole numeric value of at most 18 digits, and must not duplicate another header's numeric Rank; do not invent a positive or minimum Rank rule. See `ora-resource/ora_input_validation.md`.
- Validate every effective payment-term line before package generation. Require exactly one due basis (`DuePercent` or `DueAmount`) and exactly one complete due-date method (`DueDays`, `DueDayOfMonth` with `DueMonthsForward`, `FixedDate`, or `Calendar`). Percentage lines for a term must total exactly 100; amount lines must include a zero-amount line; and one term cannot mix percentage and amount bases. Enforce the documented day/month ranges, nonnegative due values, complete discount pairs, and ordered discount dates and percentages. See `ora-resource/ora_input_validation.md` and `ora-resource/ora_design_enforcement.md`.
- Accept a set code, a set name, or an unspecified "set" in the user's request.
  Keep an explicit code unchanged. For a name, look up `SetName` and get its
  `SetCode`. For an unspecified set, search both fields and count distinct
  SetCodes. One distinct code allows processing; multiple codes require the
  user to choose; no matches stop ZIP/import. Never guess a code, change its
  case, or substitute a different set. Show any name-to-code mapping in the
  preview. See [Reference Lookups](ora-resource/ora_reference_lookups.md).
- Run `scripts/resolve_reference_prerequisites.py` before normalization. It
  accepts `setReference` input and fills the subscription's `SetCode` only
  after a complete, clear lookup. A supplied code or Calendar is checked by a
  read-only GET: a readable result allows processing, no rows stop it, and
  malformed responses stop it. The calendar query joins its name and type
  filters with `and`.
- For an uploaded ZIP containing set assignments or installment Calendars, run the same reference helper
  with `--package` before `validate-upload`. Pass its saved results using
  `--reference-evidence`. These results must cover every SetCode and nonblank installment Calendar
  in that exact ZIP. Missing results, no matches, or malformed responses stop validation.
  An unavailable API follows the supplied-value warning rule below.
- If a check for an explicit code or Calendar is unavailable, record
  `validation_skipped` and keep the supplied value for the separately approved
  import. HTTP 400 also records a `resolver_contract_issue` for maintenance.
  If a name or unspecified set cannot be fully looked up, stop and ask for the
  Set Code; do not use the skipped-check rule to invent a required value.
- Keep template-required audit columns as technical package behavior. Do not ask an implementation user to invent audit values; preserve non-requested values and rows from the fresh current export. See `ora-resource/ora_defaulting_rules.md` and `ora-resource/ora_input_validation.md`.
- Keep all adapter package construction and validation offline. Live export, preview, import, monitoring, persisted-state verification, commit, push, merge, and publication require their separate approvals. See `e2e-adapter.json` and `ora-resource/ora_design_enforcement.md`.

## Setup Task Skill Contract

- task_code: `AP_MANAGE_PAYMENT_TERMS`
- task_name: `Manage Payment Terms`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Payment Terms` under `Payables`.

## Setup Task Metadata

- Task name: `Manage Payment Terms`
- Task code: `AP_MANAGE_PAYMENT_TERMS`
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
- Setup task name: `Manage Payment Terms`
- Setup task code: `AP_MANAGE_PAYMENT_TERMS`




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

## Verifying Changes After Import

`reconcile` can report `PASS` only after the workflow has observed a successful
import and a later completed export from the same task and environment. Supply
`--verification-evidence <observations.json> --environment <selected-environment>
--base-url <selected-https-origin> --import-request-id <completed-import-request>`
along with the baseline, approved candidate, blueprint, requirements and export.
Missing, stale or mismatched evidence leaves verification `PENDING`; say that
saved changes have not yet been verified.

For an offline file comparison, use `reconcile --compare-only`. Its result is
`MATCH` or `DIFFERENT`, with `persistenceVerification=NOT_PERFORMED`. A file match
does not prove that an import occurred. Package building and import approval
are unchanged. See [Error Handling](ora-resource/ora_error_handling.md#reconciliation-evidence)
for the required observations.


## Reference Lookup Evidence

When a design or uploaded ZIP uses lookup receipts, follow
[Reference evidence provenance](references/reference-evidence-provenance.md).
Keep the selected target separate from evidence, require matching environment
and HTTPS origin, and rerun preflight for missing, malformed, future, or
more-than-24-hour-old observations. The same provenance checks apply to
unavailable lookup warnings. An offline receipt does not authorize a live call
or prove that Fusion imported the ZIP.


## Uploaded Package Compatibility

Before reporting an uploaded ZIP as valid, supply `validate-upload` with
`--target-context <selected-target.json>` from the independently selected
workflow target. Both baseline and uploaded metadata must match its environment
and release. Read [Uploaded package compatibility](references/uploaded-package-compatibility.md)
for the contract and migration boundary. Matching schemas alone do not establish
source/target compatibility.


## Source Manifest Labels and Origins

When producing a source manifest or verifying post-import observations, follow
[Manifest labels and HTTPS origins](references/manifest-labels-and-origins.md).
A source manifest's environment must match its ZIP metadata; keep migration
destination information separate. Use a credential-free HTTPS origin without
an API path, query or fragment. A template-only label requires an empty package.

## EBS Migration to Fusion

Use this section for user-declared EBS / E-Business Suite / R12 payment-term
migration. These names are synonymous for this workflow; XML view names and
minimum API/patch metadata do not prove a particular EBS release. Treat the XML
as source data, keep it unchanged, and build a separate target-format candidate.

### Review and map EBS payment terms to Fusion

An `APTermsTLVO` XML record can combine header settings, translated text and
nested `APTermsLinesVO` installments. Its view-object name does not mean every
field must load into Fusion `AP_TERMS_TL`. The 22 header settings absent from
Fusion TL have exact-name locations in Fusion B; these are stored values, not
derived replacements. Use the following business mapping through FSM entities,
not direct table writes:

| Source content | Fusion storage / FSM destination | Handling |
| --- | --- | --- |
| `EnabledFlag`, `DueCutoffDay`, `Type`, `StartDateActive`, `EndDateActive`, `Rank`, `AttributeCategory`, `Attribute1`…`Attribute15` on the EBS header/TL representation | `AP_TERMS_B` / `AP_TERM_HEADER.csv` | Map the 22 settings to their same-named FSM header fields; do not discard them as missing from TL. Validate their target meaning and values, including `Type=STD` and supported enabled flags, even if an EBS schema description labels a source field unused. |
| `Name`, `Description`, `Language`, `SourceLang` | `AP_TERMS_TL` / `AP_TERM_HEADER_TRANSLATION.csv`, with `Name` also the logical header key and `Description` represented on `AP_TERM_HEADER.csv` | Preserve source-language text and translation identity. Keep header/translation names and descriptions consistent with the approved language mapping and existing US-alias behavior. Do not move language columns into B. |
| Nested `APTermsLinesVO` installment fields | `AP_TERMS_LINES` / `AP_TERM_LINE.csv` | Preserve `SequenceNum`, due basis/method, discount tiers, attributes, `FixedDate` and `Calendar`; bind each line to `AP_TERM_HEADER.Name`. |
| Selected Fusion reference-data set assignments | `AP_TERMS_ST` / `AP_TERM_SUBSCRIPTION.csv` | Obtain the user's intended sets and resolve their SetCodes under the existing reference rules. Do not invent a set assignment when the XML supplies none. |

Where multiple language records represent one term, consolidate only the shared
header identity, keeping each requested translation and installment relationship.
Compare repeated header and line values before consolidation. Disclose identical
duplicates and conflicts and obtain a user decision before merging, excluding or
changing source records; never choose first/last silently. A destination name
match is not permission to overwrite an existing term.

### Fields outside this extract and supporting references

Check each actual source for `DISCOUNT_AMOUNT`, `DISCOUNT_AMOUNT_2`,
`DISCOUNT_AMOUNT_3`, `DISCOUNT_CRITERIA`, `DISCOUNT_CRITERIA_2` and
`DISCOUNT_CRITERIA_3`, including normalized XML spellings. These EBS setup fields
have no verified Fusion setup-level replacement. When absent, they require no
payload exclusion or invented values for that file. Their absence does not prove
they are unused across EBS. If present, disclose the fields and values and stop
the affected mapping for a user decision; do not silently drop them, convert
amounts to percentages or map them to `DueAmount`.

### XML to CSV, validation, approval and reconciliation

1. Inventory source headers, language rows, installments and populated fields.
   Record every source-to-target mapping and any user decisions; preserve dates,
   blanks, zeros and names without cleanup. All fields having a destination is
   a mapping result, not an import-validity claim.
2. Obtain the selected target's fresh exact-task current export and template.
   Resolve creates, updates and already-matching records against that baseline;
   show conflicts and obtain the intended outcome before changing target values.
   Use the existing reference helper for set assignments and nonblank Calendars.
   Validate populated flexfields against the intended target configuration.
3. Prepare the separate FSM CSVs using the template's exact headers, hierarchy,
   metadata and target date format. Include the required parent header for every
   child operation and at least one explicitly mapped installment for every new
   term. Preserve unrequested baseline values and rows. Show any applicable
   create defaults; absence in XML does not authorize clearing existing values.
   Do not relabel an EBS XML or cross-environment ZIP as a compatible Fusion
   export; retain source provenance separately and apply the existing target and
   package compatibility rules.
4. Run existing header, global Rank, due-basis totals, due-date method, discount
   completeness/order, translation, reference and final-batch rules. Disclose
   unsupported fields, duplicate resolutions and every proposed transformation.
   Use the active Run Book, core Data Loader and Task Hook workflow; submit only
   after approval of the exact validated immutable candidate. Scope/mapping
   approval alone is not upload approval.
5. After import, check the actual job outcome and obtain a fresh same-target
   export. Compare requested, submitted and saved header, installment,
   translation and set-assignment values, including preservation checks. Use the
   existing verification-evidence contract; a successful job or offline match
   alone does not establish saved-state verification.
