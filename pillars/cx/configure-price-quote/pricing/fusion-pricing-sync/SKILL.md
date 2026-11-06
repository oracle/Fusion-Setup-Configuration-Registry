---
skill_id: "cx.configure-price-quote.pricing.fusion-pricing-sync"
name: "Fusion Pricing Sync Setup Task Guidance"
description: "Routes Run Book preparation through core services, generates a POST trigger DAT for the no-business-payload CpqChargeSetSync operation, and submits through the approved immutable Data Loader archive."
layer: "pillar"
pillar: "CX"
offering: "Configure Price Quote"
functional_area: "Pricing"
functional_area_code: "CUSTOM_PRICING"
task_code: "CUSTOM_FUSION_PRICING_SYNC"
task_name: "Fusion Pricing Sync"
parent_skill_id: "cx.configure-price-quote.pricing"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "REST"
businessObject: "CpqChargeSetSync"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "import"
execution_mode: "hybrid"
owner_team: "CX configure price quote pillar team"
version: "0.3.6"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "sync_direction_from_prompt"
outputs:
  - "setup_task_plan"
  - "validated_dat_artifact"
  - "charge_set_load_result"
  - "diagnostics"
  - "skill_run_record"
  - "token_usage_record"
uses_core:
  - "core.project-mgmt.project-workspace-initializer"
  - "core.runbook"
  - "core.data-loader"
  - "core.data-loader.task-hook"
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
  - artifact_type: "other"
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/pricing/fusion-pricing-sync/runs/{run_id}/CpqChargeSetSync.dat"
    versioning_policy: "append-only"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/pricing/fusion-pricing-sync/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/pricing/fusion-pricing-sync/current/"
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
  - "Delegates initial project and Run Book preparation or creation to the existing core workflows before Data Loader steps."
  - "Generates a CpqChargeSetSync DAT through core.data-loader using live metadata."
  - "After Data Loader approval, uploads the immutable CpqChargeSetSync archive to UCM and initiates one standard IMPORT_AND_LOAD request."
required_privileges:
  - "Run Book creation or selection privileges when the delegated core Run Book workflow is needed."
  - "Fusion Data Loader access to resolve business-object metadata, upload approved archives to UCM, and initiate data loads."
---

# Fusion Pricing Sync Setup Task Guidance

## Purpose

After the Run Book is prepared and active, run the Fusion Data Loader workflow
for `CpqChargeSetSync` through an approved immutable archive for a supported
Fusion-to-CPQ request. A general business-outcome request selects this workflow; the user
does not need to request `Generate DAT` or `initiateDataLoad` separately.

`CpqChargeSetSync` is a trigger-only sync task. Never ask the
user for charge-set rows, mapping data, or a source DAT. The DAT/ZIP and the
`initiateDataLoad` request fields are internal workflow artifacts, not user
inputs. Use the generic core Data Loader DAT generator. The generated DAT is an
internal workflow artifact rather than a user-requested sample.
`core.data-loader` resolves the live template, validates and packages the DAT,
and owns approval, upload, and initiation. Task rules validate the POST trigger
contract against the immutable source. Do not define task-local exceptions
to core validation.

## Pricing Trigger Contract

The pillar developer confirms that pricing sync is a POST operation with no
business request payload. The registered Data Loader adapter executes that
operation from a trigger DAT; the DAT row and the generic `initiateDataLoad`
request are loader transport artifacts, not charge-set business data.
`dataloader_import_mode: REST` selects this registered REST-backed Data Loader
business object. It does not mean direct REST execution and does not conflict
with using DAT as the loader source. Keep this route; do not change it to HDL
or require an additional direct-REST execution document.

Use the generic generator's explicit `--operation create --format dat` path so
`RestAction`, when present in the live template, is `POST`, never `PATCH` or
`DELETE`. Do not use update-mode sample enrichment or look up existing charges.
`chargeId` is a non-mandatory integer surrogate field. If the generator includes
it, its metadata-valid integer placeholder is acceptable: the particular value
has no business meaning and needs no existence, uniqueness, or mapping lookup.
Its omission is also acceptable when the live source schema permits it. Do not
ask the user for it or reject a generated integer merely because it is a sample
value. This contract does not waive core schema or datatype checks.

If live metadata requires business inputs, contradicts the optional integer
contract, or cannot provide a usable registered template, report the exact
metadata mismatch. Do not invent a REST/DAT conflict or substitute a direct
POST. A failed lookup is a blocker; a successful metadata-backed loader route
does not need an independently callable business endpoint.

## Run Book Handoff

For a normal request such as "Fusion Pricing Sync" or "Setup Fusion Pricing",
start with `router.implementation-router` and select the project and this exact
task. If a new project is needed, delegate to
`core.project-mgmt.project-workspace-initializer`: create the canonical local
Run Book plan and task context, then let `core.runbook` create the initial Run
Book under its own authorization rules. Deliver the returned Run Book dashboard
before DAT generation. Reuse an existing active Run Book and exact sequenced
task; do not create a duplicate on resume. Missing task membership or an
unbound, failed, or unknown Run Book requires the declared core workflow to
resolve it before proceeding. A deferred creation is handled by that workflow.

The intended flow is Run Book preparation, DAT generation and validation,
Data Loader approval, then upload and initiation. Run Book creation or
activation never approves the pricing upload. This skill delegates Run Book
operations; it does not construct Run Book payloads or mutate its control state.

For user-facing narration, say "syncing Fusion pricing reference data." Use
Fusion-to-CPQ wording only when direction needs to be confirmed or explained.
Keep charge-set terminology and the business-object name in the internal
workflow; preserve any verbatim approval or initiation report required by
`core.data-loader`.

## Preflight

Before the first live Data Loader step, infer the requested source and target
from the user's prompt and apply the direction rules in
`ora-resource/ora_input_validation.md`. Only Fusion as source and CPQ as target
may proceed. Then read and apply the task-local input
validation, dependency-readiness, reference-lookup, and error-handling
guidance. Require an exact live `CpqChargeSetSync` metadata match, a validated
immutable archive, completed Task Hook validation, and a current approval bound
to that exact archive. Delegate environment identity, privilege, artifact, and
approval-envelope checks to `core.data-loader` and `core.data-loader.task-hook`.
Stop before upload or `initiateDataLoad` when any preflight check fails,
is ambiguous, or no longer matches the approved archive.

## Required Workflow

Read the task-local `ora-resource/` files in this order: defaulting rules,
input validation, dependency readiness, reference lookups, error handling,
then the rule registry.

Complete the Run Book handoff above before the first Data Loader step. Use its
canonical task-context.json and the positive sequence for Fusion Pricing Sync.

1. Resolve `CpqChargeSetSync` from live `dataLoaderBusinessObjects` metadata
   and download its DAT template/schema through `core.data-loader`.
2. Generate an internal `CpqChargeSetSync` DAT through the generic core Data
   Loader generator, using a fresh artifact-directory ID and
   `--operation create --format dat`. Save it under
   `project/{project_id}/artifacts/pillars/cx/configure-price-quote/pricing/fusion-pricing-sync/runs/{run_id}`.
   Use only this one generated DAT as the source; its generated record is the
   sync trigger, not user-supplied charge-set data.
   Keep the Run Book's configured runID; the fresh artifact-directory ID must
   not replace it. Validate POST and the optional integer chargeId contract
   from ora-resource/ora_input_validation.md.
   Pass the DAT to `core.data-loader` for live source/schema validation,
   immutable ZIP preparation, preflight, and Task Hook validation. Reject any
   generated value that does not pass those core gates. Do not collect
   charge-set data from the user.
3. After the one Data Loader approval, upload only that approved archive to UCM
   and call `initiateDataLoad` with `IMPORT_AND_LOAD`. Do not retry either POST.

## Routing and Approval

`core.data-loader` owns live business-object metadata, DAT schema and source
validation, deterministic ZIP preparation, immutable-artifact checks, UCM
upload, and the fixed generic `initiateDataLoad` action. This skill must not
implement those Data Loader functions.

The one Data Loader initiation requires a current approval for the exact
immutable `CpqChargeSetSync` archive. An active Run Book is a prerequisite, not
a substitute for the Data Loader approval.

Ask the user only for an approval at the `core.data-loader` approval gate. Do
not expose internal workflow verbs as required user prompts.

## Recovery and Persistence

Persist redacted validation and failure diagnostics under the project workspace.
Do not persist credentials, tokens, authorization headers, or archive contents.
Do not retry a UCM upload or `initiateDataLoad` after dispatch without explicit
approval or idempotency evidence.

## Download Fusion Data Loader Sample

This generated sample-download section applies to a separate explicit workbook
sample request. The normal Fusion Pricing Sync workflow above generates DAT
with `--operation create --format dat`; it does not require a user-supplied
workbook or a second sample-generation prompt.

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business object.

1. Confirm that `CpqChargeSetSync` is the exact registered Data Loader business object.
2. Generate the default editable XLSX sample through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "CpqChargeSetSync" \
     --operation create \
     --output-dir "<project-artifact-directory>"
   ```

3. Keep the generated workbooks together:
   - editable sample
   - attribute-details workbook
   - key-fields workbook
4. Review the generated headers and key fields before preparing source data. The operation uses read-only Fusion metadata and does not upload or import data.
5. Use the generated editable workbook as the starting point for the later Data Loader preparation and approval workflow.
