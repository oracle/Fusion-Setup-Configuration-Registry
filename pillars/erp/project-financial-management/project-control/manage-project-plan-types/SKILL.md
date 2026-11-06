---
skill_id: "erp.project-financial-management.project-control.manage-project-plan-types"
name: "Manage Project Plan Types"
description: "Create, update, rename or duplicate project plan types from consultant business requirements in Codex, including defaults, sets, calendar, task dates, currencies, rates, progress and budget generation, using validated FSM packages and the Data Loader approval workflow."
layer: "pillar"
pillar: "ERP"
offering: "Project Financial Management"
functional_area: "Project Control"
functional_area_code: "PJF_PJO_DEPLOYED"
task_code: "PJO_MANAGE_PROJECT_PLAN_TYPES"
task_name: "Manage Project Plan Types"
parent_skill_id: "erp.project-financial-management.project-control"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP project financial management pillar team"
version: "0.3.8"
inputs:
  - "project_id"
  - "customer_project_plan_type_request"
  - "current_target_fsm_export"
  - "reference_acquisition_context"
outputs:
  - "setup_task_plan"
  - "immutable_fsm_preview"
  - "validation_checkpoints"
  - "execution_receipt_record"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
  - "core.data-loader.task-hook"
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
uses_core:
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"

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
persists_project_state: true
state_updates:
  - "setup_task_sequence"
  - "configuration_blueprints"
  - "validation_results"
  - "reports"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/erp/project-financial-management/project-control/manage-project-plan-types/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/project-financial-management/project-control/manage-project-plan-types/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "report"
    default_location: "project/{project_id}/artifacts/pillars/erp/project-financial-management/project-control/manage-project-plan-types/current/"
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
  - "Writes task plans, validation/preview evidence, execution receipts and redacted diagnostics to the selected project workspace through core project services."
  - "Creates setup export processes through the declared task-export service and submits approved setup imports through core.data-loader; never writes setup through the UI."
required_privileges:
  - "Authorized access to Manage Project Plan Types and its FSM task export/import operations in the selected Fusion environment."
---

# Manage Project Plan Types

## Purpose

Create, update, rename or duplicate project plan types through the supported FSM task package.
Consultants describe their requirements in Codex; Codex resolves business labels,
prepares the package, presents the effective choices and executes the approved
Data Loader route. Consultants do not need to maintain the Fusion UI or edit CSV
codes. UI inspection and ADE research are authoring activities, never runtime
prerequisites or fallback execution routes.

## REST Request Preflight

Before any workflow-selected REST request, apply the offering's
[REST version and query compatibility preflight](../../references/rest-query-compatibility.md).
Determine the effective framework version from the selected core client or
workflow, construct compatible query parameters, and verify that the outgoing
header agrees. Do not hardcode a separate pillar version. Existing route,
validation, classification/matching, persistence and approval gates still apply.

## Consultant Interaction

1. Use the implementation router and selected project context. Reuse known
   environment, business requirements and retained configuration. If no project
   exists, use the project workspace initializer under the router before durable
   setup work; do not ask consultants to build a workspace manually.
2. Establish create or update, name and effective dates. Accept UI labels such
   as From Date and To Date. For updates identify the exact existing row and
   requested changes; preserve its other values. A request to duplicate a type
   needs an identified source and a new name, and must not copy unrelated sets,
   business-unit rows or translations without the consultant's intent.
   An ordinary Duplicate request copies its source configuration, sets, BU rates
   and currencies. Resolve any requested exclusions; translated names require
   explicit new-name intent. Rename uses the existing translation child in the
   verified application language; never change the parent identity column to
   the new name. Re-export after rename before further maintenance.
3. Work through relevant groups: sets; cost/revenue and calendar; task dates;
   currency conversion; rates per business unit; progress/forecast; budget
   generation; configured additional information. Ask only for missing business
   choices that affect the requested configuration. Read
   [defaulting rules](ora-resource/ora_defaulting_rules.md) before preparation,
   [input validation](ora-resource/ora_input_validation.md) for field mappings,
   and [reference lookups](ora-resource/ora_reference_lookups.md) for LOV sources
   and eligibility. Read the dependency, design and error resources through the
   compiled rule plan before preview.
   For a new plan type, automatic forecast generation defaults to disabled
   (`ProgAutoGenFcstVer=N`); do not ask the user to confirm that default.
   The legacy source value `Prog_Sett_Automatically_generate_fo="Remaining plan"`
   repeats an ETC method, not an instruction to enable forecasts. Retain an
   independently supplied ETC selection, disclose this misplaced legacy value,
   and apply the create default without asking an enable/disable question.
   Require a forecast financial plan type only when generation is explicitly
   enabled. Explicit supported checkbox choices win; updates and duplicates
   preserve their existing/source value when no forecast change is requested.
4. Distinguish defaults, explicit choices and retained values in the preview.
   For submitted create/update Task Settings, enabling synchronization with an
   empty effective Date Adjustment Buffer in Days applies 0. An explicit integer
   overrides the retained buffer; an omitted nonempty retained buffer is preserved.
   Keep inactive buffers unchanged and disclose any applied zero in the preview.
   Explain disabled/dependent choices in business terms. In particular, planning
   amounts COST_ONLY does not itself enable tracking project costs. Calendar
   affects available rate dates and profiles; rate mode belongs to each business
   unit; forecast and budget generation select different financial plan types.
5. Account for every requested change as applied, retained, blocked or unverified.
   Never present a partially represented request as complete. For a package
   boundary, explain the unsupported option and continue independent supported
   work; do not direct the consultant to perform UI maintenance.
   Retain the supplied business-input object as `sourceInput` in the canonical
   preparation request and `finalData.sourceInput` in the preview input. Keep
   explicit later corrections in that effective input with their provenance.
   In particular, `Curr_Set_Use_Conversion=true` selects the shared-conversion
   action; preparation translates it and preview checks its persistent result.
   Canonical-only requests remain supported when no source-form input exists.
6. Deletion is excluded from this skill, including deletion of child assignments.
   Do not research deletion eligibility or offer an alternate deletion route.
   Disabling multicurrency with retained currency rows is also excluded because
   the importer deletes those rows. Shared-conversion intent uses the explicit
   field-copy mapping in Design Enforcement, with derived changes in preview.

## UI Coverage and Acceptance

The acceptance target is every applicable non-delete Manage Project Plan Types
UI operation. A schema-valid package or a passing offline suite alone does not
establish that target. Use the task's [coverage record](noship/tests/ui-coverage.md)
to distinguish supported preparation, target acceptance evidence and open gaps.
Never report full UI parity while a required operation is blocked or unverified.
The broad financial-plan editor's hidden controls are outside this task unless
task-specific evidence establishes their applicability.

Example: "Create a project plan type called Implementation Delivery, effective
1 January 2027, in the Common set. Track costs, use the accounting calendar,
calculate progress by effort, and use remaining-plan ETC. Prepare a preview."
Resolve those labels and dependencies without asking the consultant for CSV
headers, branch codes or IDs. Missing rate schedules are not a reason to invent
business-unit rate rows.

## Setup Task Skill Contract

- task_code: `PJO_MANAGE_PROJECT_PLAN_TYPES`
- task_name: `Manage Project Plan Types`
- parent_skill_id: `erp.project-financial-management.project-control`
- pillar: `ERP`
- offering: `Project Financial Management`
- functional_area: `Project Control`
- functional_area_code: `PJF_PJO_DEPLOYED`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Customer Inputs

- Project plan type name, description, start date, and optional end date.
- Project-plan branch and planning amount scope, including cost-only intent when applicable.
- Set assignment and any business-unit-specific planning-rate schedules.
- Calendar, period profile, rate derivation date, estimate-to-complete method, and physical-percent-complete choices.
- The current target-environment FSM export. If it is not yet available, authenticate and export it before package generation.

For creates, materialize only the scoped evidence-backed defaults. A header-only
export contains no configuration defaults. For updates, omitted options preserve
the selected record through retained baseline evidence, subject to importer
semantics. Never copy defaults from another exported type or infer an exact
member, header, code, or relationship from a different pod or older package.

## Setup Task Metadata

- Task name: `Manage Project Plan Types`
- Task code: `PJO_MANAGE_PROJECT_PLAN_TYPES`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

Before authentication, export or reference acquisition, normalize business intent
and apply the initial input contract in `ora_input_validation.md`. A separate planning code
has no verified standard mapping and returns `UNSUPPORTED_PLANNING_CODE`.
`PlanTypeCode` identifies the `PROJECT_PLAN` branch. Never silently discard the
separate requirement, overload another column, or assume an unconfigured DFF.

1. Authenticate before creating an export. Designate the task-local export receipt/output directory first, create the export with the receipt-producing operation, and persist its `ProcessId`, task code, target, and last status there before polling or downloading. Do not rely on console output as the only export receipt.
2. If authentication fails or times out before a `ProcessId` is returned, classify the attempt as **not initiated in Fusion**. Reauthenticate and create the first export; this is not a retry of an accepted request. If a `ProcessId` exists, never create another export automatically: resume polling that exact process.
3. Accept an export only after the process reports completion and the downloaded file is a valid ZIP containing `ASM_SETUP_CSV_METADATA.xml` and the target-declared task members. A valid header-only member is a zero-row baseline; absent, empty, corrupt, or premature output is not.
4. Execute `ora-resource/ora_rule_registry.json` in sequence. Reconcile requested business values to codes and members proven by this target export. Exact CSV mapping is resolved from the current target-pod template before import.
   For reference sets, the workflow selects the shared OAuth REST GET client and
   the `resolve_set` acquisition and resolution contract. Period profiles resolve
   locally through `resolve_period_profile` and its Period Profile Evidence
   Boundary. Retain the historical SB4 tables for source traceability; they do
   not establish selected-target identity or a blocking calendar mismatch.
   No runtime database or REST lookup is added. Without current target-bound
   evidence, preserve supplied names with a nonblocking `REFERENCE_UNRESOLVED`
   warning; never claim target membership from the historical snapshot. Continue
   supported checks for other references as declared in the lookup resource.
   Supported reference reads change no Fusion setup. Their results do not establish plan-type
   editability, application privileges or eligibility beyond the listed checks.
5. Modify only the requested plan-type rows. For a target-proven cost-only project-plan request, use the target-exported `PROJECT_PLAN`, `COST_ONLY`, planning option, set-assignment, and business-unit rate-setting contracts.
   Use `scripts/prepare_import.py` with the completed target template, fresh data
   baseline, exact selected Fusion origin and normalized canonical request. Run
   `--dry-run` first. It prepares one named PROJECT_PLAN/BUDGET/COST_ONLY create
   with scoped defaults, or updates uniquely identified retained rows without
   create defaults. It preserves metadata and current header order, rejects
   cross-target exports and overwrite conflicts, and validates its result.
   For a copy use create with `duplicateFrom`; for rename use update with the
   language-scoped `rename` action. For new sets, BU rates, currencies or
   translations on an existing type use explicit `insertRows`, separately from
   retained-row patches. The source-backed contracts and limitations are in
   [preparation commands](scripts/README.md) and Design Enforcement.
   Other create branches and removal of children are outside this helper's
   scope. Deletion is excluded.
   For another missing non-delete operation, record a precise capability gap
   and stop that operation until this task's declared FSM preparation contract
   supports it. Do not bypass the helper or select a different execution route.
   Consultants
   supply business requirements; Codex prepares this internal canonical request.
   See [preparation commands](scripts/README.md). A dry-run never approves or
   initiates a load.
6. Validate the exact ZIP with `shared.validation.setup-data-validator` and `shared.validation.reference-data-validator`. Preserve `ASM_SETUP_CSV_METADATA.xml` unchanged and reject unrequested existing or translated rows.
   Run this task's `scripts/validate_import.py` against those same ZIP bytes
   with explicit create/update intent. Resolve every reported required parent
   and child value before preview; do not infer defaults from target frequency
   or stop correction at the first server error. This task's
   `scripts/import_preview.py` evaluates the executable contract and Task Hook
   route before recording approval. Its later `verify` handoff checks retained
   evidence/approval integrity and delegates exact-byte and current Run Book
   binding checks to the canonical core verifier. It must not rerun task
   validation, rule planning or preview construction after approval. Supply
   `finalData.archivePath`, `finalData.archiveSha256` and `finalData.operation`;
   narrative rule results do not replace the byte check. Report package integrity,
   task-contract validation, deferred checks and server validation separately.
   Use this task-local wrapper for the preview/approval handoff, then verify
   its envelope immediately before the existing Data Loader submission route.
   The wrapper retains task evidence separately from the core preview and
   delegates approval and verification to the authoritative Task Hook. Preserve
   its returned loader envelope unchanged. Missing approval bindings or a
   changed project, active Run Book or server require a fresh preview and
   approval; regenerate legacy local envelopes rather than patching them.
   Direct generic preview construction does not execute this task's field checks
   and is not a valid substitute for this task workflow.
   A preview-only request ends at `PJO.PPT.PREVIEW_READY` with the immutable ZIP
   and SHA-256 after every supported applicable check passes and unresolved warnings are disclosed. It requires no import approval
   and does not invoke Data Loader. Continue to step 7 only for submission.
7. Route the immutable ZIP and its SHA-256 to `core.data-loader`. A same-request `auto-approve`, `auto approve`, `approve without asking`, or `skip confirmation` instruction authorizes this one load after every validation gate passes; otherwise wait for later approval of the exact preview. Auto-approval never waives validation or authorizes a retry.
8. Before submission, preflight a safe writable task-local execution-receipt destination. After accepted initiation, register the returned UCM Content ID, Data Loader Request ID, approved archive reference/checksum, target, project, task and latest status through the declared core project services. Return the loader's complete In Progress report without automatic status checks, process logs, exports or readback. Acceptance means initiated, not completed or verified. If submission is uncertain or receipt persistence fails, preserve any known identifiers, record the failure and stop; repair only local evidence and never resubmit under the old approval.
   Retain a separate local copy of the task-approved envelope before handing
   the loader its disposable envelope. Capture the actual structured initiation
   result from the selected core adapter. Use `scripts/execution_receipt.py`
   to persist its allowlisted IDs and approved binding, then register that
   receipt through the existing project services. The helper performs local
   checks only; it does not submit, poll, or infer completion. Missing receipt
   persistence must never trigger another load.
9. Only on a later explicit status/results/verification request, validate the registered target, project, task, request ID and approved-archive binding before external calls. Missing or mismatched context blocks. Delegate status/count/error checks to `core.data-loader`; never repeat preparation, approval or submission. A status-only request returns that status without an export. An active status or bounded timeout returns In Progress and waits for another request; terminal failure stops. For requested setup verification, require terminal success before a fresh same-task export through `shared.setup-export.task-level-export`, then compare requested fields and preserved groups/children with the approved preview. Retain returned process diagnostics when available. Missing or mismatched readback prevents verified completion and does not authorize another write.

An indeterminate submission with no recoverable request ID requires a later
explicit recovery request. The active workflow selects supported read/status
reconciliation using the known request or UCM identifier, or a same-task export
when identity cannot be recovered. Recovery does not select preparation or
authorize resubmission; any genuinely new load requires fresh validation and
approval through the existing Data Loader route.

Do not make this skill dependent on UI maintenance. If the target package cannot represent a requested option, stop only that unsupported option and report the exact package boundary; do not invent a UI mutation, direct REST write, alternate member, or payload.

Use this task metadata when invoking those skills:

- Offering: `Project Financial Management`
- Functional area / Setup Object: `Project Control`
- Setup task name: `Manage Project Plan Types`
- Setup task code: `PJO_MANAGE_PROJECT_PLAN_TYPES`

## Validation Checkpoints

- The name is distinct for the selected plan-type branch, dates are ordered, and requested enumerations resolve in the target export.
- Set identity resolves exactly once in the authorized collection. Business-unit assignment eligibility, plan-type editability and import privileges remain separate checks; set lookup success does not prove them.
- Resolve every requested rate schedule for its business-unit row and that row's
  rate mode. Actual-rate mode permits applicable fallback schedules; planning-rate
  mode exposes the additional resource schedules. Do not drop fallback schedules
  merely because Use planning rates is off.
- Before packaging, evaluate requested changes against the effective retained
  control state. `prepare_import.py` rejects requests to activate known disabled
  controls; inactive defaults and unchanged retained values remain preserved.
  The byte validator cannot reconstruct user intent, so deferred inactive-field
  checks still require the assisted design gate for packages prepared elsewhere.
- Calendar type, period profile, rate-date basis, ETC method, and percent-complete calculation/basis are serialized only through the exact target-exported columns and codes.
- The preview contains only the required parent and requested child rows, preserves target metadata, and has a recorded SHA-256.
- Include preparation's row counts, copy/rename intent and all default/derived
  changes in the Task Hook preview. Rename preserves parent identity and selected
  translation SourceLang; duplicate identifies its source and copied collections;
  insertRows must be absent identities in the fresh baseline. Never report server
  acceptance from local validation alone.
- Submission occurs once after checksum-bound approval and ends In Progress. Verified setup completion requires the later explicitly requested workflow, terminal success and independent target-state readback; initiation or preview alone cannot establish it.

## Route Boundaries

- Project Plan Type defaults can cascade to templates and projects. Keep project-plan and financial-plan options distinct, and respect restrictions on attached or predefined plan types.
- Only a fresh target export establishes the import member and header contract.
- The supported task-level FSM route remains export, exact-ZIP validation, immutable preview and approval, then Data Loader-authorized submission. Do not substitute direct writes or automated UI execution.

## Reference Validation Support

Reference sets use the documented read-only API for accessible identity.
Calendar and other fixed choices use the tables included in this skill.
Period-profile identity and calendar validation follow the resolver’s target
evidence boundary. Historical SB4 tables remain source references; they cannot
establish current identity or a blocking mismatch on the selected target. CSV
still uses names. Without matching current evidence, supplied names and other
unsupported lookup checks remain unresolved, nonblocking warnings; preserve
their proven CSV representation and continue without a waiver. Do not claim
unsupported checks passed.
Static immutable choices remain locally validated without REST. Known invalid
values, ambiguous input, unsupported CSV mappings and failed supported reads
retain their normal error handling.

A separate planning code also has no supported standard field mapping.
`PlanTypeCode` is the project-plan branch discriminator, not a business code.

## Runtime Readiness

At use time the customer must provide or freshly export the target-pod FSM package, have permission to export/import `PJO_MANAGE_PROJECT_PLAN_TYPES`, and supply the business values required by the package. Missing business input or representation gates the checkpoint that needs it; missing REST validation support alone does not gate package generation or submission.

Supported reference reads and their limits are declared in
`ora-resource/ora_reference_lookups.md`. Only available FSCR runtime services
may execute them; no external research environment or manually constructed
reference snapshot is a runtime prerequisite or validation substitute.

## Durable Artifacts and Review

Resolve `project_id` from the selected existing implementation project before preparation or execution; missing project identity is an input-validation blocker. Persist plans, validation results, immutable previews, approved package references, execution receipts and redacted failure diagnostics under `project/{project_id}/artifacts/pillars/erp/project-financial-management/project-control/manage-project-plan-types/current/`. Raw exports belong under `project/{project_id}/exports/project-financial-management/project-control/manage-project-plan-types/`. Never persist credentials or tokens there.

Use `core.project-mgmt.artifact-version-manager` for major new versions and confirmed minor updates, `core.project-mgmt.artifact-registry-manager` to register each durable artifact, and `core.project-mgmt.project-state-manager` to update only declared state fields and record the run under `project/{project_id}/state/runs/`. These pillar-owned services persist the returned receipt without extending the loader's initiation request. Append later requested statuses, verification and partial-failure evidence to that receipt. Reconcile uncertain writes only in the later explicitly requested recovery workflow above; do not resubmit automatically. Record token usage using the manifest policy.

Required reviewers: responsible ERP Pillar Development Lead or SME, FSCR A-Team/core reviewer, and QA for validation/execution changes. Package readiness does not replace merge approval.
