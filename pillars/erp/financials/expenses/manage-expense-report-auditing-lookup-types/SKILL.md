---
skill_id: "erp.financials.expenses.manage-expense-report-auditing-lookup-types"
name: "Manage Expense Report Auditing Lookup Types Setup Task Guidance"
description: "Read implementor Excel workbooks, validate auditing lookup types, codes and sets, and prepare selected type/code FSM candidates through Run Book and Data Loader."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Expenses"
functional_area_code: "FIN_EXPENSES_DEPLOYED"
task_code: "EXM_MANAGE_AUDIT_LOOKUP_TYPES"
task_name: "Manage Expense Report Auditing Lookup Types"
parent_skill_id: "erp.financials.expenses"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "hybrid"
owner_team: "ERP financials pillar team"
version: "0.4.3"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "intake_workbook"
  - "destination_lookup_snapshot"
  - "target_environment"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/expenses/manage-expense-report-auditing-lookup-types/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/expenses/manage-expense-report-auditing-lookup-types/current/"
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
  - "Writes local parsed workbooks, reference evidence and offline FSM candidates in the selected project."
  - "Selects approved FSM export jobs and read-only reference GETs through shared/core clients."
  - "Hands reviewed candidates to core.data-loader; only its separately approved execution can change Fusion lookup types/codes."
required_privileges:
  - "Task-specific Functional Setup Manager export and lookup-read privileges."
  - "Export Import Functional Setups User and applicable Data Loader privileges at the execution gate."
---

# Manage Expense Report Auditing Lookup Types

## Purpose

Owner: ERP financials pillar team. Reviewers: responsible Financials pillar lead and functional SME.

Maintain existing Expenses lookup-type Meaning/Description and their codes for EXM_MANAGE_AUDIT_LOOKUP_TYPES.
Creating lookup types, changing module/view/configuration level, deleting codes,
DFF edits and independent translation authoring are outside this workbook contract.
Create and update are resolved from the target, never selected by a worksheet Operation column.

Refresh customer references before generating the implementor workbook. The
[portable workbook](assets/ManageExpenseReportAuditingLookupTypes_Input.xlsx) is
an unverified offline starter, not a customer inventory.
The revised workbook has optional Lookup Types rows for parent text edits and guided inputs and dropdowns for environment lookup
types, reference data sets and Yes/No. Its Reference Lists sheet explains the
choices; it is never evidence that a value exists or is editable in a target.
The shipped workbook has no environment-specific choices. Always populate lookup
types and reference sets from the selected customer environment before delivery. Existing row-4 workbooks remain supported.
Use [UI parity and language](references/ui-parity.md) for verified editability and remaining parity gaps,
[workbook intake](references/workbook-intake.md) for exact field semantics and
corrections, [destination reference contract](references/destination-reference-contract.md)
for lookup preflight and [evidence](references/evidence.md) for source boundaries.
The parser, preflight and package preparer are offline helpers, not Fusion clients.
Their parsed JSON, candidate ZIP and adapter reports use the task-local artifact
publisher: reject traversal, linked/replaced parent directories and existing
destinations; publish complete private files and roll back only outputs owned by
the failed publication. This also applies when the exact-task export is empty.

1. Under the active implementation router, resolve the project, task, environment,
   privileges and Run Book state. New implementation projects retain the router's
   run-or-skip prevalidation checkpoint. This task does not create a Run Book.
2. Read the workbook using scripts/intake_workbook.py read. Return every issue with
   cell/row context. Offer a corrected workbook or chat corrections. Revalidate the
   full model; retain source_issues until a corrected workbook is reparsed.
3. After local intake passes, select shared.setup-export.task-level-export for exact
   current-data and template exports. Apply its approval gates before creating jobs.
   Store ZIPs only in the selected project's exports directory. Validate metadata,
   task identity, four CSV headers, record widths and process completion.
4. Run scripts/refresh_customer_references.py under the read-only reference step
   declared in ora_reference_lookups.md, through core.fusion-api.rest-api-client.
   It derives module IDs from the approved exact-task exports or, when no mapping
   is exported, resolves the exact EXM/APPLICATION node through the Core BOSS
   taxonomy GET with boss_scope. Pass --properties for the trusted enrolled private
   profile; no credential copy into the repository is required. It reads current types
   and reference sets, follows selected code/DFF children for full identities, and
   writes destination.json, workbook-lovs.json, existing-input.json and preflight.json.
   Generate customer workbooks with this catalog and explicit --environment; use
   existing-input.json to prepopulate existing values, or the validated implementor
   model to preserve requested changes. Never replace implementor edits with a refresh.
   Check lookup types AND codes AND reference
   data sets, including seeded codes omitted by customer-modified exports. Normalize
   to the destination reference contract and run scripts/intake_workbook.py preflight.
   Never assume a missing exported code is new, use a prefix as proof of module
   ownership, ignore pagination, or fill in an unverified set/view identity.
5. Present the resulting create/update design and all remaining limitations. Type-only
   edits do not require unrelated code/set checks, but require existing type/view/module,
   retained parent row and verified session/export/import language with complete translation
   preservation evidence. Blank optional cells preserve current values. New code
   Meaning is required; existing blanks preserve. Use scripts/build_import_candidate.py
   --dry-run before writing an offline candidate. It supports selected-type text updates and selected-code creation
   and updates with complete baseline rows. Seeded updates missing from the export
   and language-sensitive text updates remain explicit preparation blockers until
   schema-complete/language evidence is supplied. Do not hide these as successful builds.
6. Route the exact candidate through core.data-loader under the active core.runbook.
   Read the selected core contract at handoff: its immutable preview and separate
   approval are authoritative. Never POST a task package directly, persist interactive
   session captures/approval objects, double-ask for the same Data Loader action, or
   treat this workbook as import approval. Return accepted initiation immediately.
7. On a later authorized status/readback request, retain external IDs, job outcome,
   row warnings and verified persisted values separately. Use fresh exact-key readback
   or export to reconcile changed values and unchanged selected fields. Inspect
   translation and DFF preservation. A completed process alone is not verified setup.
   Let the implementor decide completion/retry. No automatic live mutation retry.

## Local commands

Run from this skill's root directory or use absolute script paths. All outputs
belong under project/{project_id}/artifacts or exports, never in the skill folder.

```bash
python3 scripts/intake_workbook.py read --input implementor.xlsx --output parsed.json
python3 scripts/refresh_customer_references.py --repo-root <repository> --project-root <project> --input parsed.json --template template.zip --baseline current.zip --environment <selected-environment> --output-dir <project>/artifacts/<new-reference-folder> --read-dir <project>/exports/<new-read-folder> --dry-run
python3 scripts/intake_workbook.py preflight --input parsed.json --snapshot destination.json --environment <selected-environment> --output checked.json
python3 scripts/build_import_candidate.py --input parsed.json --snapshot destination.json --environment <selected-environment> --template template.zip --baseline current.zip --output candidate.zip --dry-run
```

Remove --dry-run only to prepare the local candidate after checks pass. It does not
submit. Use the installed spreadsheet skill and bundled artifact-tool runtime to run
scripts/create_workbook.mjs for a blank or corrected workbook; --input accepts the
same normalized model. The shipped workbook has two input tables with 200 rows each and a Reference Lists sheet.
Use --live instead of --dry-run on the reference collector only at the declared
read step. Generate with --lov-catalog <reference-folder>/workbook-lovs.json
--environment <selected-environment> and optionally --input <reference-folder>/existing-input.json.
The generator rejects catalogs older than one hour or from another environment.
Only offline template authoring may use --offline-starter. Fixed task identity,
schema and Yes/No choices are portable; module IDs, set IDs, customer labels,
configuration levels and existing codes are always collected from the destination.
The verified scope is export- or taxonomy-confirmed application modules, not inferred
descendant modules. Any existing destination reference set can be selected, including
one without existing codes for this type. Empty modified-only exports select the
declared taxonomy GET; missing/ambiguous nodes, undocumented identities and ambiguous
views block preparation. No guessed defaults are used. A dry-run validates local
inputs and identifies the required resolution route; it does not verify live references.
Use --properties /absolute/private/profile.properties on the collector for a selected
private profile. The same retained profile supplies scope and, only on the taxonomy
route, boss_scope. Its environment must match --environment and both routes use its
single HTTPS restBaseUrl origin. Profile changes stop collection.

## Resource workflow

Read ora-resource/ora_input_validation.md, ora_dependency_readiness.md,
ora_reference_lookups.md, ora_defaulting_rules.md, ora_design_enforcement.md and
ora_error_handling.md, then the compiled ora_rule_registry.json and validated
build_rule_execution_plan.py result. Their graph stops at a design handoff and
contains no direct Fusion write. Structural readiness does not prove live import
qualification or satisfy Data Loader's own validation.

## Failure, error_redaction and persistence

Classify failures as input validation, catalog mismatch, auth/authz, transport or
environment, Fusion API, process timeout, process failed, artifact persistence or
approval blocker. Stop dependent work on ambiguity, stale/missing references,
malformed ZIPs or source conflicts. Only the core auth route may refresh a rejected
cached token once. Never retry an import automatically. On timeout retain environment,
TaskCode, ProcessId, last status and elapsed wait; use the declared status check after
a user decision. Retrieve ProcessLog when available and preserve row warnings and
partial success. Recovery uses fresh evidence and a new reviewed candidate.

Persist sanitized diagnostics, artifact references, skill runs and token estimates
in the current project, following manifest workspace paths. Keep customer values,
exports and screenshots untracked. Never store credentials, tokens, private keys,
Authorization headers or protected Data Loader interactive-session material here.

## Qualification

The package contract was observed on an internal 11.13.27.04.0 environment; the
latest public documentation located during authoring was 26D. Recheck release
compatibility on each target. Offline behavior and read-only UI/REST evidence are
separate from live import qualification. The initial live create test failed because ChangeSinceLastRefresh was blank.
The generator now supplies its source-declared N default for new codes and validates
required retained values across populated candidate members; The corrected create and subsequent code-update imports were verified in the
authoring environment. Detailed results and failure/recovery evidence remain
in the project workspace. This does not qualify parent-text changes, independent
translations, deletion, or a new environment. The generic E2E tester still needs
a task-owned compatible adapter and test bundle; offline tests do not satisfy
that prerequisite.
