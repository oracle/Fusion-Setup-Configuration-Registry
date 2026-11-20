---
skill_id: "erp.financials.expenses.manage-corporate-card-programs"
name: "Manage Corporate Card Programs Setup Task Guidance"
description: "Guides CREATE of a Corporate Card Program through shared FSM export, local package preparation, core Data Loader validation and approved submission, with separately requested status and setup verification."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Expenses"
functional_area_code: "FIN_EXPENSES_DEPLOYED"
task_code: "EXM_MANAGE_CORPORATE_CARD_PROGRAMS"
task_name: "Manage Corporate Card Programs"
parent_skill_id: "erp.financials.expenses"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "orchestration"
execution_mode: "hybrid"
owner_team: "ERP financials pillar team"
version: "0.2.4"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "fusion_environment_context"
  - "template_and_current_baseline_or_authorized_acquisition"
  - "normalized_create_design_json"
  - "expected_process_environment"
outputs:
  - "setup_task_plan"
  - "offline_fsm_package"
  - "offline_preparation_report"
  - "data_load_execution_result"
  - "setup_verification_result"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.setup-export.task-level-export"
  - "core.data-loader"
uses_core:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "core.data-loader"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/expenses/manage-corporate-card-programs/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/expenses/manage-corporate-card-programs/current/"
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
  - "Writes a new local FSM ZIP only when --output is supplied without --dry-run; refuses overwrite."
  - "Creates approved FSM export jobs through shared task-level export."
  - "Reads target references through the core REST client."
  - "Uploads and initiates an approved CREATE through core Data Loader."
required_privileges:
  - "Target access to the task, reference data and FSM CSV exports."
  - "UCM upload and Data Loader initiation privileges for the selected task."
---

# Manage Corporate Card Programs

## Purpose

Create one new Travel corporate card program, optionally with one company
account and one upload rule, using existing issuer/site references. Supported
company payment choices are COMPANY and BOTH. The bounded field and operation
contract is [CREATE contract](references/create-contract.md).

For a request to create the program **in Fusion**, follow the
[live setup workflow](references/live-setup-workflow.md). It selects shared
export, core REST and Data Loader services explicitly. For a package-only
request, run only the local preparation steps below. Neither a ready rule plan
nor a prepared ZIP constitutes import approval or proof of successful setup.

## Authentication and supervised execution

Use the existing core authentication service with fresh login for every live
session. The export adapter always passes `force_login=True`, including when
`--force-login` is omitted; it exposes no cached-token or explicit-token mode.
Use the same fresh-login requirement for the selected REST-client and Data
Loader handoffs. A service that cannot honor it blocks that live step.

The task preserves the selected configuration and never retries an export POST.
Only read-only 401/403 failures may obtain one new core-authenticated token and
repeat the read. Core owns OAuth, secure cache writes and transport; this task
never reads, copies, decodes or manages tokens. Core may write its normal cache,
but no live route in this task may reuse it across sessions.

The intended account is confirmed by the human during each fresh sign-in, under
[the supervised execution contract](references/live-setup-workflow.md). Record
that as manual evidence, not automated subject verification. This skill supports
supervised setup and QA; unattended or multi-user execution is outside scope.
This restriction avoids the inherited cache-reuse identity gap for this task;
it does not repair core authentication or qualify other skills' cached routes.

## Inputs and scope

Use the active project selected by `router.implementation-router`. Bind the
user-selected environment through core authentication configuration; never copy
a host, account, release or test fixture from a previous run. Collect the business
values from [the customer workbook](references/workbook-intake.md) using
`scripts/workbook_intake.py`, or accept the same reviewed CREATE JSON. Resolve
applicable target references and review the normalized business choices. Preserve
cell provenance, literal text and leading zeros. Unknown headers or ambiguous
business mappings block; do not infer a different Data Loader business object.

Use a blank template and completed unfiltered baseline for this exact task,
environment and release. The live workflow acquires them through the declared
shared service; package-only mode requires supplied artifacts and provenance.
Different headers fail closed. Release independence means no hardcoded target;
it does not imply compatibility with every future template.

## Preflight checks

Before local preparation or external execution, confirm the initialized active
project, selected environment and principal, requested CREATE scope, exact catalog
task and CSV support, required privileges, and all mandatory or conditional
workbook values. Resolve applicable references through the declared workflow;
require same-target template/baseline provenance, exact headers and no duplicate
program. Do not treat a failed lookup as an absent reference.

Before writing local inputs, candidates or reports, validate each new artifact
path through core.project-mgmt.artifact-registry-manager under the active project.
Reject traversal, symlinked paths and existing outputs; source files must be the
explicitly selected workbook/design/exports. The export adapter separately checks
its initialized project, receipt and exports-directory containment. Keep
credentials out of every artifact. Before live operations, apply the owning
export or Data Loader approval gate, artifact-integrity and Run Book checks in
[the live workflow](references/live-setup-workflow.md). A failed preflight stops
that operation and records its classified diagnostic without a mutation retry.

## Local package preparation

1. Apply [input validation](ora-resource/ora_input_validation.md),
   [defaulting](ora-resource/ora_defaulting_rules.md), and the CREATE contract.
   Derive an omitted upload format from the supported brand only when an upload
   row is requested. Preserve explicit values. Skip optional blanks while keeping
   the physical CSV columns; required and conditional blanks still block.
2. Run `scripts/prepare_fsm_package.py --template <template.zip> --baseline
   <baseline.zip> --input <design.json> --environment <expected-ProcessEnv>
   --dry-run`. Use the actual FSM ProcessEnv, not an assumed OAuth profile name.
3. On success, run the same arguments with `--output <new.zip>` in the active
   project's artifacts folder. The helper refuses overwrite and validates
   inventory, ordered headers, task/environment/release, parent links and baseline
   duplicate names. Its `prepared_offline`, `importReady=false` and
   `importAuthorized=false` correctly describe this intermediate artifact.
4. For live setup, continue to the selected core Data Loader workflow. The helper
   does not set approval or manufacture Task Hook evidence.

## Execution, approval and verification

Read [live setup workflow](references/live-setup-workflow.md) before any external
operation. It owns acquisition prerequisites, the supported service handoffs,
export approval boundaries, submission, separately requested status inspection,
and fresh-export read-back. Use the six ora-resource files as the task-specific
validation rules, including [reference lookups](ora-resource/ora_reference_lookups.md)
and [design enforcement](ora-resource/ora_design_enforcement.md). Their rule
registry is a validation plan; it never directly executes an import.

Core Data Loader owns exact-artifact validation and approval. Return its accepted
initiation report unchanged and stop; do not automatically poll. A later explicit
status/verification request selects the verification phase. Compare the requested
values and protected pre-existing rows with `scripts/verify_fsm_setup.py` after
acquiring a fresh same-target export. A passing comparison proves only the checked
values at that export time; record load outcome and comparison separately.

## Errors and persistence

Follow [export recovery](references/export-response-recovery.md) and
[blocker handling](references/blocker-resolution.md). Classify input validation,
catalog mismatch, auth/authz, transport/environment, Fusion API, process timeout,
process failed, artifact persistence and approval blockers. Never retry an
uncertain export or load POST automatically. Preserve known external IDs and
partial successes; a recording failure never authorizes resubmission.

Keep authorized setup exports in the active project's untracked exports folder
and redacted results in its artifacts folder. Core services own authentication,
secret handling and transport; never write credentials into project artifacts.
Record skill runs and token usage through the declared project services. Preserve
core Data Loader's authoritative report and internal-artifact retention contract.

Owner: ERP financials pillar team. Reviewers: Expenses SME/Pillar Development
Lead and FSCR A-Team/core reviewer. Local tests qualify local logic only. Live QA
must identify the tested revision, target, fixture, load outcome and read-back.
