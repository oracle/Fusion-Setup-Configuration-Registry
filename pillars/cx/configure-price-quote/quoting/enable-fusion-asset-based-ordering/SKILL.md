---
skill_id: "cx.configure-price-quote.quoting.enable-fusion-asset-based-ordering"
name: "Enable Fusion Asset-Based Ordering Setup Task Guidance"
description: "Provides staged explicit approvals for the CPQ Settings import, Adaptive Search selective publish, and conditional Unified Asset Read Model Sync."
layer: "pillar"
pillar: "CX"
offering: "Configure Price Quote"
functional_area: "Quoting"
functional_area_code: "CUSTOM_QUOTING"
task_code: "CUSTOM_ENABLE_FUSION_ASSET_BASED_ORDERING"
task_name: "Enable Fusion Asset-Based Ordering"
parent_skill_id: "cx.configure-price-quote.quoting"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "REST"
businessObjects:
  - "CpqCommerceSettings"
  - "publish"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "orchestration"
execution_mode: "hybrid"
owner_team: "CX configure price quote pillar team"
version: "2.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "fusion_environment_context"
  - "cpq_environment_context"
  - "fusion_abo_process_variable_name"
  - "fusion_optin_choice_short_name"
  - "prerequisite_update_approval"
  - "prerequisite_update_approval_fingerprint"
  - "cpq_preparation_approval"
  - "cpq_preparation_sha256"
  - "cpq_data_loader_approval"
  - "cpq_data_loader_preview_sha256"
  - "adaptive_search_preparation_approval"
  - "adaptive_preparation_sha256"
  - "adaptive_initialization_preparation_approval"
  - "initialization_preparation_sha256"
  - "explicit_adaptive_initialization_status_request"
  - "adaptive_search_publish_approval"
  - "adaptive_data_loader_preview_sha256"
  - "ess_submission_approval"
  - "ess_payload_sha256"
  - "cpq_write_result_artifact"
  - "ess_sync_submission_artifact"
  - "ess_sync_monitor_artifact"
  - "adaptive_search_publish_submission"
  - "adaptive_search_publish_status"
  - "abo_delta_action_library_function_recovery_approval"
  - "workflow_id"
  - "explicit_data_loader_status_request"
  - "adaptive_publish_monitoring_choice"
  - "explicit_adaptive_publish_status_request"
  - "execution_options"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "prerequisite_optin_handoff"
  - "authoritative_feature_state_evidence"
  - "prerequisite_update_preview"
  - "prerequisite_optin_verification"
  - "read_only_preflight_plan"
  - "cpq_preparation_proposal"
  - "cpq_data_loader_preview"
  - "generated_workbook_access"
  - "adaptive_preparation_proposal"
  - "adaptive_initialization_blocker"
  - "adaptive_initialization_preparation_proposal"
  - "adaptive_initialization_status"
  - "adaptive_search_publish_preview"
  - "ess_submission_preview"
  - "adaptive_search_publish_preparation"
  - "workflow_execution_result"
  - "cpq_settings_write_execution_result"
  - "cpq_settings_write_reconciliation"
  - "ess_sync_submission"
  - "ess_sync_monitoring"
  - "adaptive_search_publish_request"
  - "adaptive_search_status_request"
  - "adaptive_search_publish_completion"
  - "abo_delta_action_library_function_readback"
  - "abo_delta_action_library_function_recovery_preview"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.implementation-planning.fsm-set-optin.fsm-set-optin"
  - "shared.implementation-planning.fsm-set-optin.fsm-set-optin-features"
  - "cx.sales.sales-foundation.configure-adaptive-search"
uses_core:
  - "core.project-mgmt.project-workspace-initializer"
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
  - "core.fusion-api.rest-api-client"
  - "core.data-loader"
  - "core.runbook"
  - "core.fusion-api.ess-job-submitter"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/quoting/enable-fusion-asset-based-ordering/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/quoting/enable-fusion-asset-based-ordering/current/"
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
  - "Delegates project initialization and initial Run Book creation to the existing shared planning and core workflows before ABO preflight or load preparation."
  - "May offer initial Adaptive Search Full Publish only for the exact missing-metamodel/null/empty catalog blocker, after separate preparation and independent Core approvals. Requires exact initialization load/job/catalog proof before a fresh Partial Publish proposal; initialization cannot authorize ESS."
  - "May invoke the existing shared FSM Set Optin Features workflow for one selected false Fusion prerequisite after a target-bound, current approval."
  - "Requires a separate ABO preparation-only approval before generating the CPQ workbook or starting its Core preflight. This approval does not authorize upload, submission, Adaptive Search or ESS."
  - "May submit exactly one fixed CPQ Commerce Settings Data Loader import through the registered CpqCommerceSettings business object after fresh target-bound preflight and separate explicit approval of its exact Task Hook preview; normal enablement imports the selected process, Fusion ABO enablement, and required ABO delta-action Library Function together, while function-only recovery imports only the fixed Library Function setting."
  - "After verified CPQ completion, requires separate ABO preparation-only approval before invoking the Adaptive Search companion's workbook generation and Core preflight. Only that skill through core.data-loader may submit the registered `publish` business object after its independent Core load approval; this task never sends the Adaptive Search POST; its companion retains private publish Data Loader identifiers."
  - "Pauses after each Data Loader submission until an explicit user status request. After verified loader success, offers a choice of bounded 15-second Adaptive Search job monitoring or checking later. Repeated job reads require the current explicit monitoring choice. May submit the fixed Unified Asset Read Model Sync ESS job exactly once only after final success, both entities enabled, and separate exact-payload ESS approval."
required_privileges:
  - "Run Book creation or selection privileges when the delegated core Run Book workflow is needed."
  - "Fusion privileges to read feature states and, only after explicit approval, update the required feature opt-in selections."
  - "Approved CPQ OAuth client and CPQ administrator permission for Commerce Settings reads, process validation, and the approved Fusion ABO Settings update."
  - "ORA_CPQ_ADMINISTRATOR_JOB permission to submit and monitor the Unified Asset Read Model Sync ESS job."
  - "Generic Configure Adaptive Search privileges to validate entity metadata, execute the registered Data Loader `publish` business object, read exact-job status, and return final entity evidence for the fixed selective publish."
---

# Enable Fusion Asset-Based Ordering Setup Task Guidance

## Customer-Facing Presentation

Render user-facing ABO results through
`scripts/abo_presentation.py` using the `render-presentation` command. Keep the
structured JSON result as the internal orchestration contract. The renderer is
the authoritative presentation boundary and validates its task-local contract
inside that Python module; no repository-level schema is required. Every public
coordinator command must attach the rendered `customer_presentation` after its
workflow result, payloads, and approval fingerprints are complete. The
presentation for `requires_process_selection` shows only the
short process-selection or invalid-process correction prompt, without the full
status template. For a verified invalid selection, state that no ABO
configuration changes were made. Do not infer that a Run Book was created;
report creation separately only when confirmed by its workflow result. This
exception changes presentation only, not Run Book ordering or approval gates.
For ABO workflow status and preparation outcomes, the presentation must show the complete workflow, all four required Fusion opt-ins,
every currently known false opt-in, why a later opt-in was not checked, and only
the approval for the one current eligible operation. Relay that presentation
without reconstructing it from internal JSON. Keep workflow progress separate from Core's load approval. Display Core's preview
Markdown verbatim without rebuilding a scope table or adding another question.
For accepted load submissions, return the coordinator's `customer_presentation`:
Core's receipt stays verbatim, followed by the coordinator's `next_action` under
`Next Action`. This tells the user to check the CPQ or Adaptive Search load
status and continue, or to wait before checking Full Publish initialization.
For status commands, return the full rendered ABO `customer_presentation`,
including Core's status Markdown when present. Do not return only the receipt
or append a duplicate next-action message. Submission acceptance does not verify
load completion and does not start automatic polling.
Immediately before a successful Core approval preview, relay the separate
`workbook_access` event's Markdown once. It links only the generated XLSX input
for optional viewing, not an editable approval payload or a new approval gate.
Do not merge it into Core's table, reread workbook contents, or add a review question.
The pending load uses its validated immutable archive even if the Excel file is edited.
Core previews and integrity values remain in their prescribed internal artifacts.
Preserve ESS's existing payload review. The ABO preparation template is a
business-plan approval, not a Core load approval. Never ask for Adaptive Search
load approval or ESS approval while its separate preview or payload is still
being prepared.

## Purpose

Provides task-specific setup planning, prerequisite routing, and validation guidance for `Enable Fusion Asset-Based Ordering` under `Quoting`.

## Setup Task Skill Contract

- task_code: `CUSTOM_ENABLE_FUSION_ASSET_BASED_ORDERING`
- task_name: `Enable Fusion Asset-Based Ordering`
- parent_skill_id: `cx.configure-price-quote.quoting`
- pillar: `CX`
- offering: `Configure Price Quote`
- functional_area: `Quoting`
- functional_area_code: `CUSTOM_QUOTING`
- available_flag: `Y`
- export_import_supported_flag: `N`
- csv_export_import_supported_flag: `N`
- dataloader_import_mode: `REST`
- businessObjects: `CpqCommerceSettings`, `publish`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, validating prerequisites, or preparing
a governed change for `Enable Fusion Asset-Based Ordering` under `Quoting`.

## Setup Task Metadata

- Task name: `Enable Fusion Asset-Based Ordering`
- Task code: `CUSTOM_ENABLE_FUSION_ASSET_BASED_ORDERING`
- Available: `Y`
- Export/import supported: `N`
- CSV export/import supported: `N`
- CSV export/import routing: `not supported`
- Data Loader import mode: `REST`
- Business Objects: `CpqCommerceSettings`, `publish`

## Run Book Handoff

For a normal request such as "Enable Fusion ABO" or "Enable Fusion Asset-Based
Ordering", start with `router.implementation-router` and select the project
and this exact task. Reuse an existing active Run Book and its exact sequenced
task; do not create a duplicate on resume. A missing project or task binding
requires the delegated planning and core workflows below before ABO preflight
or load preparation. Retain the selected CPQ process through that handoff; a
process selection is not evidence that the process has been verified.

For a new project, have the routed
`shared.implementation-planning.task-dependency-resolver` persist the ordered
`setup_task_sequence`, then have
`shared.implementation-planning.offering-task-map-builder` produce the mapping
for `CUSTOM_ENABLE_FUSION_ASSET_BASED_ORDERING` in the matching Configure Price
Quote / Quoting context. This valid custom catalog task has no
`DisplaySequence`. Missing catalog sequence metadata alone must not cause a
request for a user-authored plan or workbook. Use the shared resolver's
documented `functional_area_tail` sequence and retain its diagnostic when that
fallback applies; this pillar must not assign a sequence itself.

An HTTP 204/empty FSM discovery result is an empty catalog-discovery outcome,
not by itself a transport or authentication failure. Preserve the request
context and diagnostic and let the shared resolver validate and sequence the
selected custom task against the effective catalog. Do not discard a valid
custom task solely because FSM returned no tasks. If discovery actually fails,
follow the shared workflow's prescribed fallback approval path. If no matching
sequence can be persisted, report the resolver blocker and stop before ABO
execution; do not bypass the task-map gate.

Once the valid sequenced mapping is available, delegate to
`core.project-mgmt.project-workspace-initializer` to create the canonical local
Run Book plan and task context, then let `core.runbook` create the initial Run
Book under its own authorization rules. Deliver the returned Run Book dashboard
before ABO preflight and use the canonical task context and positive sequence.
Missing membership or an unbound, failed, or unknown Run Book must be resolved
through the declared upstream workflow before continuing. A deferred creation
is handled by that workflow. This pillar delegates these operations; it does
not construct Run Book payloads or mutate Run Book control state. Run Book
creation or activation never approves CPQ, Adaptive Search, or ESS changes.

## Fusion Prerequisite Opt-in Handoff

Use the existing shared skill
`shared.implementation-planning.fsm-set-optin.fsm-set-optin-features` for all
required Fusion prerequisites. This task must never update `featureStates` directly.

1. Read the CPQ/ABO feature states first through the task's authoritative
   `featureStates` GET lookup. That lookup reuses
   the task-local `feature_states_reader.py` read-only adapter and
   requires exactly these two `COMBO` records:
   - `ORA_FOM_ASSET_BASED_ORDERING`
   - `ORA_ENABLE_UNIFIED_ORACLE_CPQ_IN_FUSION`
2. If either CPQ/ABO value is false, prepare one independent update preview
   for one false feature at a time. Do not read Subscription/Coverage states,
   combine features in one change, or continue to CPQ.
3. Only after both CPQ/ABO values are true, read the Subscription/Coverage
   `COMBO` records:
   - `ORA_FOM_OSS_INTEGRATION_SUBSCRIPTIONS` — Integrate Order Management with
     Subscription Management to Process Subscriptions
   - `ORA_FOM_OSS_INTEGRATION_COVERAGES` — Integrate Order Management with
     Subscription Management to Process Coverages
4. If either Subscription/Coverage value is false, prepare one independent
   update preview for one false feature at a time. Do not continue to CPQ.
5. Only when all four `StatusFlag` values are true, continue without invoking
   the shared writer.
6. Use the shared skill's `--feature-code` and `--action set-choices` flow.
   It must resolve and validate one exact feature-choice short name before an
   update. Do not use the generic `opt-in` inference for this task, hard-code
   `Enabled`, or use a fallback choice.
7. A shared-skill `--dry-run` may help resolve a choice and create a plan, but
   it is never evidence that an opt-in is already enabled. Only the fresh,
   exact `featureStates` GET response is authoritative for `StatusFlag`.
8. Present the target, exact false feature code, resolved exact choice, and
   planned effect. Obtain explicit, current approval bound to that preview
   immediately before the one live shared-workflow update.
9. After the shared update returns, reread the approved stage through the
   authoritative GET lookup, then rerun the full ordered preflight. If any
   feature remains false, the response is
   incomplete, or the update fails, stop. Do not retry, roll back, or proceed
   to CPQ automatically.
10. Resume this task only from a fresh ordered read-only preflight after all statuses
   are verified true.

`ABO.REQUIRES_PREREQUISITE_UPDATE` is a controlled handoff point. The task
delegates the actual opt-in mutation to the existing shared skill and preserves
its approval and project-audit controls; it does not construct its own Fusion
PATCH request.

## Read-Only Preflight Orchestration

After the active FDOS workflow selects the declared read routes, use the
task coordinator to combine, in this order:

1. the approved CPQ read of Commerce settings;
2. the approved CPQ exact-setting read of
   `defineFieldsForModifyActionFunction`;
3. the approved CPQ read/verification of the selected or CPQ-defaulted
   Standard Process; and
4. the exact, fresh CPQ/ABO two-record evidence followed by the
   Subscription/Coverage two-record evidence obtained through the task-local
   `featureStates` reader.

The combined preflight never calls a Fusion opt-in update and never calls a
CPQ write. It has only these terminal classifications:

- `blocked`: input, CPQ state, or process validation is unsafe;
- `requires_prerequisite_update`: return one approval-required shared-workflow
  handoff for one false Fusion opt-in at a time;
- `already_configured`: all required opt-ins, the existing CPQ setting, and the fixed
  ABO delta-action Library Function are verified;
- `requires_abo_delta_action_library_function_recovery`: Fusion ABO is already
  enabled for the exact selected process, but the fixed Library Function is
  blank, missing, or different; create a narrow function-only recovery preview;
- `ready_for_cpq_write_route`: all reads pass and the task may create an
  approval preview for the fixed CPQ Settings sequence.

The final classification is deliberately **not** `ready_for_execution`. A
fresh, target-bound CPQ Settings preview and explicit current approval are
still required before the core executor can submit any CPQ Settings Data Loader import.

## CPQ Settings, Adaptive Search, and Conditional ESS

The task coordinator owns the governed CPQ workflow; it never accepts a raw
CPQ URL, HTTP method, payload, bearer token, or transport from a caller.

### Staged preparation, validation and load approval for 26.10

This branch uses the existing Core persisted-preflight and Task Hook protocol.
Read `core/data-loader/SKILL.md`, its Task Hook skill, and the returned execution
guide. The host does not retain a running process between turns.

1. Run `preview-cpq-preparation` after routed project initialization and fresh
   preflight. Present the complete ABO plan and obtain preparation-only approval.
   No workbook or load exists yet. `cancel-cpq-preparation` declines this proposal.
2. With the exact project/workflow and proposal digest, run `prepare-cpq-load
   --approve-cpq-preparation --cpq-preparation-sha256 <digest>`. Recheck the
   target, process choice and prerequisites; consume the two-hour permission
   once. The coordinator writes the fixed values and returns a versioned
   `core.data-loader` workbook handoff. Follow that skill's sample-generation
   route, save its structured result, and return it through `accept-cpq-workbook
   --core-handoff-result <result.json>`. The coordinator then returns the
   versioned Core preflight handoff for that exact workbook and Run Book task.
3. Follow the Core persisted preflight with `--preflight-envelope-output` and
   its Task Hook. Evaluate ordered resources against the immutable archive,
   business scope and current-stage evidence; mark only genuinely deferred
   nodes not_applicable. Never blanket-pass checks or perform future mutations.
   Have Core build the bound Task Hook preview and return the preflight path,
   task validation, preview path and complete approval Markdown as one structured
   result. Pass it to `build-load-preview --load-stage cpq
   --core-handoff-result <result.json>`. The coordinator checks the archive,
   target, task context and preview before approval is offered.
4. Display the optional generated XLSX link once, then Core's complete approval
   Markdown verbatim. The link adds no review question. The validated archive
   is frozen: edits to Excel cannot update this load; revised input needs fresh
   preparation, validation and approval. The first permission is not load approval.
5. On a later contextual approval, run `submit-data-load --load-stage cpq
   --approve-load --load-preview-sha256 <current-preview-digest>`. Verify the
   exact project/target/scope, unchanged archive/preflight/Run Book context and
   current preview. This reserves intent and returns an exact Core submit
   handoff. Follow Core's `approve-data-load-preview` and
   `verify-approved-data-load-archive`; pass its envelope unchanged through
   `--task-validation-envelope`. Submit the saved archive through
   `--approved-preflight-envelope --approve-upload` once, with no source
   conversion or automatic retry. Return Core's structured receipt via
   `complete-data-load --load-stage cpq --core-handoff-result <result.json>`.
   Return its complete `customer_presentation` verbatim and pause. It preserves
   Core's accepted-load Markdown and tells the user to check the CPQ load status
   and continue. Do not poll automatically. An uncertain result requires
   reconciliation; never replay a reserved submission.
6. Only an explicit user request runs `check-cpq-load-status`. Follow its
   versioned Core status handoff, then return the structured status through
   `check-cpq-load-status --core-handoff-result <result.json>`. Pending stops.
   Require exact successful load status plus fresh process, enablement and
   Library Function readbacks before offering Adaptive Search preparation.
   Return the complete `customer_presentation`; after successful verification it
   shows CPQ completion and asks approval to prepare the Adaptive Search Partial
   Publish.
   Function-only recovery imports only its function and verifies all final values.
7. Obtain separate preparation-only approval for the fixed Partial Publish.
   Run `prepare-adaptive-load --approve-adaptive-preparation
   --adaptive-preparation-sha256 <digest>`, follow its workbook handoff, and
   return the result through `accept-adaptive-workbook --load-stage adaptive`.
   Follow Core's preflight/Task Hook handoff as above and return its result via
   `build-load-preview --load-stage adaptive --core-handoff-result <result.json>`.
   Show the generated Excel link and Core preview. A later independent load approval runs
   `submit-data-load --load-stage adaptive --approve-load
   --load-preview-sha256 <digest>`, follows the Core submit handoff and returns
   its receipt via `complete-data-load --load-stage adaptive`. Return the full
   `customer_presentation` verbatim; it preserves Core's accepted-load Markdown
   and tells the user to check the Adaptive Search load status and continue.
   Pause there; do not poll automatically. Preserve verified CPQ completion
   throughout.
8. The precise missing-metamodel/null/empty catalog conditions instead follow
   `ora_initial_full_publish.md`: separate Full preparation permission, fixed
   nine-object workbook with blank publishType, Core workbook/preflight
   handoffs and preview, then an independent load approval with
   `--load-stage initialization`. Initialization
   load/job/catalog proof permits a new Partial proposal; it never authorizes ESS.
9. Pause after every submission. Explicit loader checks follow the Core status
   handoff for the exact saved request once. After verified Partial load success,
   discover/pin its new job and check once. Return the complete
   `customer_presentation` with the actual publish status, then ask: “Would you
   like me to keep checking every 15 seconds, or would you prefer to check the
   status later?” Resume does not restart polling from an old choice. Require
   both entities enabled.
10. Present the existing exact ESS payload for separate approval, submit once
    through its existing adapter and monitor its exact request within its bound.
    Relay the full completion template only after verified ESS success.

### Artifact lifecycle and recovery

Core-required archives, preflight and Task Hook envelopes are local internal
artifacts, never credentials or tokens. A Core load preview expires after
30 minutes. Preparation proposals have separate two-hour one-use permissions.
Changed artifacts, scope or context require fresh validation and approval.
A missing workbook link is optional; it cannot alter the frozen load or approve it.
Do not reread/convert original inputs after final approval. Use the exact verified
archive and Core envelope. Decline stops the load; cancel a pending preparation
locally and obtain a fresh proposal before attempting revised input.

`resume-live-workflow` restores pending rule evaluation or the current load
preview without generating another workbook. Accepted receipts are recovered
without another upload or an automatic status call. Possibly-submitted intents
permit only exact status/reconciliation. Never retry a live mutation because a
receipt or checkpoint is missing. Keep the separate preparation, upload,
monitoring and ESS permissions distinct.

## ABO Delta-Action Library Function Contract

Fusion ABO requires a fixed Commerce Library Function for ABO delta action-code
calculation. This task owns one immutable CPQ setting contract; it is not a
caller-provided function name:

```json
{
  "items": [
    {
      "type": "COMMERCE",
      "key": "defineFieldsForModifyActionFunction",
      "value": "_s_getAttributesForABODeltaActionCalculation"
    }
  ]
}
```

The CPQ Data Loader approval includes this exact setting. For new
enablement, the core CPQ executor must include it in the same immutable
three-item payload as the verified process and `enableFusionABO = Yes`. After
the one Data Loader import succeeds, it must verify the process and Fusion ABO
values and then perform the exact read:

```text
GET /rest/v19/settings/COMMERCE/defineFieldsForModifyActionFunction
```

Only an exact `COMMERCE` setting with the fixed key and fixed value permits the
Adaptive Search routing step. The task must never accept an alternate function name, raw
settings body, path, method, or caller override.

If Fusion ABO is already enabled for the exact selected Standard Process but
this setting is blank, missing, or different, classify the request as
`requires_abo_delta_action_library_function_recovery`. Create a fresh,
target-bound function-only preparation proposal that clearly shows the current
and required values. Obtain preparation-only approval, then the separate
current Core approval for only that CPQ recovery import. Adaptive
Search publish and ESS each retain their separate later approvals. Import only
`configure_abo_delta_action_library_function`; verify the existing process and enablement by GET,
then run `verify_abo_delta_action_library_function`, and then continue to the existing
Adaptive Search/ESS chain. It must not replay the process-save or
`enableFusionABO` Data Loader import. If the existing setting cannot be read safely, stop
instead of assuming it is missing.

## Unified Asset Read Model Sync Contract

The conditional ESS submission occurs only after the approval-bound Adaptive
Search publish operation has succeeded and final entity verification has passed;
callers cannot replace its job metadata or add request parameters:

```json
{
  "description": "FDOS Fusion ABO Unified Asset Read Model Sync | project=<project-id> | process=<verified-process-variable-name>",
  "jobDefinitionId": "JobDefinition://oracle/apps/ess/configPriceQuote/assets/UnifiedAssetReadModelSyncMasterJob",
  "application": "CrmEss",
  "product": "CPQ",
  "requestParameters": []
}
```

There is no CPQ-only ESS recovery command in this workflow. An ESS request can
be created only after Configure Adaptive Search returns `SUCCEEDED` for the
same opaque publish operation and both final entity records are enabled. Empty
`requestParameters` intentionally lets ESS choose the Number of Workers and
Commit Asset Batch Size from data volume. A failed or timed-out ESS job does
not roll back CPQ Fusion ABO or authorize a resubmission. Immediately before
the one ESS POST, the ABO controller persists a durable request record keyed by
the project and exact returned publish operation/job correlation. A submitted
or possibly-sent record blocks a duplicate POST; the same record permits
GET-only reconciliation. When a record is already `dispatch_started` but no
request ID was persisted, reconcile only through the task-local ESS adapter's
read-only recent-request lookup for the fixed job definition, exact
description, and application. Persist a request ID only when exactly one match
is found; zero or multiple matches remain blocked from automatic resubmission.
The task-local ESS adapter validates the approval and contract, then imports
the unchanged core ESS submit and status functions. It does not use the core
CLI's POST retry route. A `COMPLETED` status without definitive success or
failure evidence remains pending within the bounded GET poll; timeout preserves
the request ID for status-only reconciliation.

The controller validates the exact delegation contract through the task-local
adapter before creating a dispatchable reservation. A legacy reservation
without a request ID is recoverable only for the known missing-HTTPS-scheme
defect: its persisted contract and payload hashes must match, the entire old
contract must equal the corrected contract except for the bare Fusion host and
an optional bare environment hostname, and
local validation must prove `dispatch_attempted: false`. The corrected contract
must then pass local validation and any new ESS POST must have its separate
current explicit approval.
Any other legacy contract, missing evidence, changed hash, or failure after
dispatch begins remains blocked from automatic resubmission.

## CPQ Process Selection

`fusion_abo_process_variable_name` is optional.

1. When the requester supplies a nonblank CPQ process variable name, preserve
   that exact value. This includes an explicit `oraclecpqo` value: it is not
   rejected merely because it is the CPQ Dev default.
2. When the requester omits the value or supplies only whitespace, ask for a
   process selection before preflight: "Please provide the CPQ Standard Process
   variable name. If you want to use the default, reply `use default` and I
   will use `oraclecpqo`." Do not make a CPQ or Fusion request until the
   requester either supplies a value or explicitly selects the default.
3. When the requester explicitly selects the default, disclose that CPQ Dev's
   default process variable name, `oraclecpqo`, has been selected. The
   disclosure must state that it will be used only if the target CPQ site
   verifies that it exists and is a Standard Process (`processType = 0`).
4. In both cases, use the approved read-only CPQ process lookup to require an
   exact variable-name match and `processType = 0` before any preview or later
   write can be prepared.
5. A display label such as `Oracle CPQ` is not a process variable name. Do not
   translate it into `oraclecpqo` or any other value without an explicit
   routing rule; ask for the exact variable name instead.

The default is a documented CPQ Dev behavior, not an unconditional fallback.
If `oraclecpqo` is absent or non-Standard on the selected site, stop and ask
for a valid Standard Process variable name.



## Inputs and Outputs

The manifest declares project, target, process choice and stage-specific inputs.
Preparation proposals bind business scope and expiry; they never approve a load.
Core's persisted Task Hook preview binds the exact immutable archive and context.
Load approval is supplied through the current preview digest after contextual
user consent; ESS retains its separate payload digest. Explicit status requests
are read-only permissions. Outputs include XLSX inputs, Core-required immutable
artifacts and validation envelopes, sanitized receipts/checkpoints, verified
readbacks, initialization readiness, final entity readiness and ESS results.

## Implementation Notes

Configure Adaptive Search remains owned by
[Configure Adaptive Search](../../../sales/sales-foundation/configure-adaptive-search/SKILL.md).
Only its introduced companion executors implement the ABO handover; standalone
Partial/Full Publish behavior is unchanged. Prepare the companion after verified
CPQ success, never before CPQ approval. Keep opaque operation IDs across the
boundary and publish Data Loader correlation private to the companion.

Use the original project's active Run Book and exact task-context sequence.
Historical completion is never fresh preflight evidence. Preserve normal and
function-only settings, prerequisite routing and ESS behavior. Save non-executable
checkpoints, register artifacts, append skill runs and token estimates.
Retain only Core-required validated artifacts and approval envelopes. Core stays unchanged; the existing persisted approval protocol remains authoritative.
A metadata HTTP 403 remains a separate authorization/API blocker; report the
approved failing stage safely, never guess a role or bypass the selected route.

## Safe Failure Presentation

For any CPQ setting (including the fixed Library Function), Fusion feature-state, ESS, or Adaptive Search failure, report the
task stage, failure class, verified side effects, and one safe next action. An
approved core adapter may add a bounded Oracle business message, provider code,
or correlation ID only when it supplies that value in an explicit structured
safe field. Never derive a message from raw exception text or expose a raw
response body, HTML, unfiltered header, token, password, client secret, cookie,
or customer payload. Persist only the same allowlisted structured details when
they are needed for reconciliation.
