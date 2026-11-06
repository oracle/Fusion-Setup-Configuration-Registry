---
skill_id: "cx.sales.sales-foundation.configure-adaptive-search"
name: "Configure Adaptive Search Setup Task Guidance"
description: "Plans, previews, and submits an approved Adaptive Search publish for requested CX Sales objects through the registered Data Loader REST business object publish, honoring explicit full-publish requests and using a full-publish fallback for a new environment whose entity catalog is unavailable, null, or empty."
layer: "pillar"
pillar: "CX"
offering: "Sales"
functional_area: "Sales Foundation"
functional_area_code: "ORA_ZBS_SALES_FOUNDATION"
task_code: "ORA_CONFIGURE_ELASTIC_SEARCHES"
task_name: "Configure Adaptive Search"
parent_skill_id: "cx.sales.sales-foundation"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "REST"
businessObject: "publish"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "hybrid"
owner_team: "CX sales pillar team"
version: "0.4.0"
inputs:
  - "abo_initialization_request"
  - "abo_initialization_preparation_permission"
  - "project_id"
  - "environment"
  - "entities"
  - "authentication_reference"
  - "execution_mode"
outputs:
  - "abo_generated_workbook_access"
  - "abo_initialization_submission"
  - "abo_initialization_status"
  - "publish_plan"
  - "current_active_entities"
  - "confirmed_requested_entities"
  - "mapped_request_artifact"
  - "payload_mapping_report"
  - "publish_submission"
  - "publish_status"
  - "validation_result"
  - "diagnostic_report"
  - "skill_run_record"
  - "token_usage_record"
uses_core:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "core.fusion-api.api-error-handler"
  - "core.data-loader"
  - "core.runbook"
  - "core.diagnostics.environment-health-check"
  - "core.diagnostics.role-access-check"
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
  - "reports"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/sales/sales-foundation/configure-adaptive-search/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/sales/sales-foundation/configure-adaptive-search/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "report"
    default_location: "project/{project_id}/artifacts/pillars/cx/sales/sales-foundation/configure-adaptive-search/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
oracle_supplied_guidance_files:
  - purpose: "Input collection and credential-safe handling"
    location: "ora-resource/ora_input_intake.md"
  - purpose: "Input and preflight validation"
    location: "ora-resource/ora_input_validation.md"
  - purpose: "Environment, privilege, concurrency, sandbox, and contract readiness"
    location: "ora-resource/ora_dependency_readiness.md"
  - purpose: "Publish-status lookup behavior"
    location: "ora-resource/ora_reference_lookups.md"
  - purpose: "Execution defaults"
    location: "ora-resource/ora_defaulting_rules.md"
  - purpose: "Object-list bulk intake rules"
    location: "ora-resource/ora_bulk_intake.md"
  - purpose: "Preview and Data Loader publish workflow"
    location: "ora-resource/ora_rest_execution.md"
  - purpose: "Product and support-boundary guidance"
    location: "ora-resource/ora_design_advisory.md"
  - purpose: "Failure classification, disclosure, redaction, and retry safety"
    location: "ora-resource/ora_error_handling.md"
  - purpose: "Mandatory pre-publish design gates"
    location: "ora-resource/ora_design_enforcement.md"
  - purpose: "Administrator-facing tables, wording, and technical-detail suppression"
    location: "ora-resource/ora_user_presentation.md"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release after internal API contract validation"
side_effects:
  - "The ABO-only initial Full Publish companion uses a separately approved fixed nine-object scope and distinct receipt. It never changes standalone approval behavior or authorizes ESS."
  - "Enables the approved Adaptive Search business objects together with Fusion-mandated internal objects."
  - "Creates or updates a sandbox metamodel version when required by Fusion."
  - "Submits an ESS-backed full Adaptive Search publish and can temporarily block conflicting search-configuration changes."
required_privileges:
  - "Authenticated access to the target Oracle Fusion environment."
  - "Adaptive Search configuration and publish authorization."
---

# Configure Adaptive Search Setup Task Guidance

## Purpose

Provide a governed REST workflow for previewing, approving, and submitting a partial Adaptive Search publish for requested CX Sales objects. Honor an explicit Full Publish request; otherwise, use Full Publish when the Entities lookup establishes a new environment by returning HTTP 400 `Could not find active meta model`, a null result, or an empty result.

## Request Interpretation

Use this task skill when the request explicitly concerns Adaptive Search publish,
full publish, index rebuild, or enabling and publishing Adaptive Search objects.
Requests such as `search objects`, `full publish of objects`, or `index objects`
are ambiguous outside this task context. Ask whether the requester wants to
search Fusion records or configure, enable, index, or publish Adaptive Search
objects; do not select this workflow until Adaptive Search is confirmed.

## Setup Task Contract

- Task: `Configure Adaptive Search` (`ORA_CONFIGURE_ELASTIC_SEARCHES`)
- Parent: `cx.sales.sales-foundation`
- CSV export/import: not supported
- Execution mode: hybrid
- Publication status: internal-only

Use this skill for an immediate selected-object publish. A validated object list uses `publishType: selective`. A full publish is required when the user explicitly requests it, and is otherwise permitted when the Entities lookup returns HTTP 400 `Could not find active meta model`, a null response, a null `items` value, or an empty `items` array, which this workflow classifies as a new environment. An explicit Full Publish collects and validates the requested object list, asks whether to retain current active objects with it, then submits the selected mapped internal-entity array without `publishType`. For a new environment, confirmation of the OOTB list submits its internal-entity array without `publishType`; if that list is declined, validate the replacement list and submit its mapped internal-entity array without `publishType`. Scheduled publishing, cancellation, attribute-level configuration, and production execution are outside scope.

Do not present the custom publish action as a publicly supported Oracle REST contract. Validate it against the target Fusion release.

## Execution Adapter

Use `core.fusion-api.rest-api-client` only for the read-only document-entity
and publish-status GET operations. Submit the approved publish through
`core.data-loader` using the registered REST business object `publish`; its
Data Loader import is the sole submission route. The Fusion registration and
live metadata for `publish` are the execution contract; do not require, infer,
or block on a separate Adaptive Search-specific adapter. Both routes use
`core/auth/fusionEnv.properties`. Do not substitute a browser or an ad hoc HTTP
client.

## Companion Invocation and Return Contract

This skill has two deliberately different interaction modes.

### Standalone Adaptive Search

A direct request such as `Partially publish Consolidated Asset and Serialized
Asset` follows the normal entity lookup, immutable-source, Data Loader approval,
and submission flow. It displays its own single confirmation, returns the Data
Loader receipt, and performs a status lookup only when the user later asks for
it. Standalone behavior must remain unchanged: it does not automatically poll
or start ESS.

### Fusion ABO dependent invocation

The ABO-only initial Full Publish companion is separately governed by
`ora-resource/ora_abo_initialization.md`. Only exact missing-metamodel/null/empty
Entities conditions select this branch. Obtain separate parent preparation
permission and independent Core approval, verify its exact load/job/catalog,
then require fresh normal Partial Publish approvals. Initialization never
authorizes ESS and cannot use the normal selective operation identity.
The numbered flow below applies to normal Partial Publish.

The ABO companion handover is version 2.0. It accepts the fixed ordered pair
ConsolidatedAsset, SerializedAsset, exact project/target, verified CPQ predecessor
and non-executable parent workflow identity. Parent provenance is not approval.
Configure Adaptive Search owns canonical workbook values and private correlation.
Core Data Loader owns workbook generation, persisted preflight, Task Hook,
approval and submission on this 26.10 route.

1. After exact CPQ load success and fresh readbacks, obtain the parent's separate
   preparation permission. Only then invoke `prepare_publish_load` through
   `prepare-adaptive-load`. Validate target, pair, contract and concurrency.
2. Prepare the complete fixed row: `RestAction=POST`, canonical `entities`,
   `publishType=selective`, `Content-Type=application/json`,
   `REST-Framework-Version=9`, `Preference=transient`. Headers/operation are
   workbook columns, not extra REST-body fields. Return the versioned Core
   workbook handoff, accept its confirmed path, then follow the Core preflight
   handoff for that path and exact Run Book task. Core validates and freezes the
   archive through its existing route; no upload occurs.
3. Evaluate returned Task Hook resources in order against the validated source
   and exact current-stage evidence. Missing/incorrect fields block approval.
   Core creates the exact bound preview. Return its structured preflight and
   Task Hook result through `build-load-preview --load-stage adaptive
   --core-handoff-result <result.json>`.
   Show the optional generated XLSX link once before Core's unchanged Markdown.
   Viewing is not approval; edits do not change the validated archive.
4. After independent contextual load approval, `submit-data-load --load-stage
   adaptive --approve-load --load-preview-sha256 <digest>` reserves intent and
   returns a Core submit handoff. Follow Core approval and archive verification,
   upload the saved bytes once and return its correlated result through
   `complete-data-load --load-stage adaptive`. No retained process is required.
5. Pause for an explicit load-status request. Follow the Core status handoff and
   return its bound result. Pending/failed/unknown stops.
   Store exact successful load evidence; subsequent job ticks never query the
   loader again. Discover/pin the new job and require matching job IDs.
6. The parent checks once, offers 15-second monitoring or check later if pending,
   and repeats only on current consent. Final readiness requires both enabled
   entities. The companion never submits ESS or repeats a possibly-sent load.


## Read Order

1. Read `ora-resource/ora_input_intake.md` and `ora_input_validation.md`.
2. Read `ora_dependency_readiness.md`, `ora_reference_lookups.md`, and `ora_defaulting_rules.md`.
3. Read `ora_design_advisory.md` and `ora_design_enforcement.md`.
4. Read `ora_publish_source_serialization.json` before preparing a Data Loader source. It is the sole approved conversion from the REST entities array to the registered string source field.
5. Read `ora_error_handling.md` before preview or a live call.
6. Read `ora_rest_execution.md` and use its compiled `ora_rule_registry.json` task graph.

## Standalone Workflow

1. Start every new publish request by collecting the target environment, requested publish mode, and object display names. Do not lead with, summarize, or reuse a prior submission record from project state. If objects are missing, ask exactly: `Which business objects do you want to publish? Provide the object display names.` Do not substitute another intake prompt. After inputs are available, compare the environment, endpoint, publish mode, normalized object selection, headers, and validated contract binding with any current mapped-request metadata and invalidate stale mappings internally without displaying historical job details.
2. Reject an empty list. Recognize these case-insensitive CPQ aliases before validation: `Quote`, `Quotes`, `Standard Quotes`, `Standard Quote Process`, `oraclecpqo`, `oraclecpqo_transaction`, and `oraclecpqo_transactionLine`. Each recognized alias resolves directly and atomically to both payload entities `oraclecpqo_transaction` and `oraclecpqo_transactionLine`; do not validate either entity against the Entities response. Only for the exact current Fusion ABO companion authorization, also recognize `Consolidated Asset`, `Consolidated Assets`, `ConsolidatedAsset`, `Serialized Asset`, `Serialized Assets`, and `SerializedAsset`; resolve them to the fixed `ConsolidatedAsset`, `SerializedAsset` pair after confirming those exact entity names are document entities in the current Entities response. These ABO aliases do not alter standalone alias handling. For explicit Full Publish, validate any remaining requested objects exactly as for Partial Publish, but construct the Full Publish payload without `publishType`.
3. Always call `/crmRestApi/searchResources/latest/entities?language=en&limit=-1&isDocument=true` once to detect a new environment. Use `isDocument=true` as the only object-validation filter; do not apply an `isEnabled` query filter. HTTP 400 `Could not find active meta model`, a null response, null `items`, or empty `items` selects the existing OOTB Full Publish path even for a CPQ-only request. When the response is nonempty, skip validation only for the direct CPQ entities and validate any remaining requested objects.
4. For Partial Publish, on HTTP 200 with a nonempty `items` array, build the internal valid-choice set from every nonempty `localizedName` in `items`, regardless of its `isEnabled` flag. Compare only the remaining requested object display names with that set using exact matching. Do not display the full document-object catalog. Combine their mapped `entityName` values with the two direct CPQ entities when a CPQ alias was supplied, deduplicate while preserving first-seen order, and add `publishType: selective`. For each direct CPQ entity, use a matching Entities item's `localizedName` and `isEnabled` only for presentation: show matching enabled names in Current active objects and show the remaining direct CPQ entity names in Additional Objects Added. If an entity is absent from the response, display its exact direct entity name in the final selection and Additional Objects Added; never display `Not inferred`. The final CPQ selection always contains both direct payload entities and has an object count of two. Hide internal names normally, except when needed to distinguish duplicate localized names or an entity absent from the response. For each invalid remaining requested label, show up to three nearest display-name matches and ask whether one is the required entity. For an explicit Full Publish with a nonempty response, show `Current active objects` and `Newly Requested Objects to enable`, then ask exactly: `Should the current enabled objects be retained and combined together with the requested objects for a new publish ?` This is a selection decision, not live approval. On Yes, deduplicate and preserve first-seen order with current active objects first, followed by the requested objects, and use that union as the final Full Publish selection. On No, use only the validated requested objects. A valid resolved list then proceeds to publish preflight. If the response itself is null, `items` is null, or `items` is empty, classify the environment as new and present the OOTB confirmation below. Do not validate the OOTB list. If the user declines it, collect a replacement full list, call Entities again for any non-CPQ aliases, and use Full Publish with its mapped and direct internal entities and no `publishType`.
5. If the user declines the single final approval confirmation, do not submit. For a partial publish, collect a revised nonempty list and repeat the object-review iteration. For an explicit Full Publish, retain the already chosen selection only if the user supplies a fresh final approval; otherwise collect a revised list or stop.
6. On Entities HTTP 400 `Could not find active meta model`, classify the target as a new environment and continue to the OOTB Full Publish confirmation. For any other status, return the status and redacted message and stop.
7. After validation and before the single final confirmation, perform a fresh latest-status GET through the shared REST client to block concurrent publishes. Never use a persisted submission's initial status as concurrency evidence. Treat HTTP 404 with exactly `{"Error":"Cannot parse null string"}` as an expected no-prior-publish result and continue; this applies in particular after the Entities HTTP 400 new-environment fallback. Show prior-job details only when this fresh response is `WAIT`, `RUNNING`, or `PAUSED` and therefore blocks the new publish. If the fresh response is terminal, continue silently. Any other status or malformed response is a redacted error and stops the workflow. Only the approved publish write is submitted through Data Loader.
8. Run `python3 scripts/validate_publish_contract.py --json` to validate `ora-resource/ora_publish_contract.json`, then generate a new mapped request and mapping report. Require its declared contract ID, POST method, publish path, JSON content type, `Preference: transient`, and both payload schemas. Map the approval-bound request into the registered `publish` Data Loader REST business object, with `RestAction: POST`, `Content-Type: application/json`, `REST-Framework-Version: 9`, and `Preference: transient`. Keep `publishType: selective` only for Partial Publish and omit it for Full Publish. Publish artifacts under executable `current` names only after binding the confirmed environment, endpoint, normalized entity list, headers, and validated contract fields.
9. Present administrator-facing object review, correction, preview, submission, and error tables using `ora-resource/ora_user_presentation.md`. Use display names and hide internal names by default. Keep hashes, contract IDs, artifact paths, and binding metadata internal unless the user explicitly asks for technical diagnostics.
   For every administrator-facing progress update, use `Partial Publish` rather than the technical payload mode. Do not describe an approved requested publish as redundant merely because objects are enabled or a previous job is terminal.
11. Before presenting confirmation, prepare and validate the immutable Data Loader source from the mapped request using the live registered `publish` metadata. Present one combined confirmation table containing Current active objects, Additional Objects Added, Final publish selection, environment, publish type, object list, object count, action, expected response, and the fact that the confirmed source is the exact Data Loader source to be submitted. For a partial publish, ask exactly: `Please provide your confirmation to proceed with partial publish of the requested objects.` For an explicit Full Publish, ask exactly: `Please provide your confirmation to proceed with full publish of the requested objects.` For a null or empty Entities result, show `Accounts, Contacts, Leads, Opportunities, Revenue Lines, Activities, Assets, Items, Product Group` and ask exactly: `No Prior publish was performed, Please provide your confirmation to proceed with full publish of these OOTB objects`. Bind the response internally to the immutable Data Loader source, environment, endpoint, headers, entities, mapped payload, and validated contract binding. This is the one and only live approval confirmation; the earlier explicit-Full-Publish retain decision only selects the object list. Do not render a subsequent Data Loader approval prompt. A valid registered `publish` BO must proceed through `core.data-loader`; do not block on an additional adapter-registration check.
12. Submit exactly one approved Data Loader REST import. Never retry the live import automatically.
13. On accepted Data Loader initiation, display `Data Loader Content ID` and `Data Loader Request ID` using those exact labels. State that the Data Loader Request ID is not the Adaptive Search Publish Job ID and that no Adaptive Search job details are available yet. Do not infer, invent, or display a Publish Job ID at submission time, and do not automatically poll.
14. Only when the user explicitly asks for the current publish status, use the accepted Data Loader Request ID in a Core status handoff and apply its bound structured result. If the Data Loader status is successful, make one read-only latest-status GET to `/crmRestApi/searchResources/latest/publishStatus` and display its `jobId`, `publishSource`, `mmuuid`, and status as the Adaptive Search publish result. If the Data Loader status is not successful, display the Data Loader status and safe returned error details, do not call Adaptive Search publishStatus, and do not retry or poll automatically.
15. Persist a redacted submission result, validation result, report, skill run, and token-usage record.

## Golden Scenario

Input object display names are `Accounts` and `Contacts`. Entities GET returns HTTP 200 with items, maps them internally to `Account` and `Contact`, and provides a filtered current-active display. After the concurrency check and payload mapping, one combined confirmation table shows current active objects, Additional Objects Added, final publish selection, environment, publish type, object count, action, and expected response. The user confirms once. The payload includes `entities` and `publishType: selective`. Submission displays the Data Loader Content ID and Data Loader Request ID, clearly identifies them as Data Loader identifiers rather than an Adaptive Search Publish Job ID, and ends without polling. On an explicit later status request, a successful Data Loader status permits one latest Adaptive Search publish-status GET, which displays the returned jobId, mmuuid, status, and source.

In the Fusion ABO dependent path, a Core persisted preflight supplies the
separate approval preview only after CPQ verification. The accepted
publish_operation_id is not job completion. Data Loader content and request IDs
are internal to the companion checkpoint; Core's authoritative receipt is relayed
unchanged. Pause for the explicit user load-status request. After successful
Data Loader processing, discover/pin the new job and check it once; the parent
offers 15-second monitoring or checking later if pending. Repeated job-only
monitoring requires the current explicit choice; later status requests check once.
The final result includes final_entity_readiness for the fixed pair and returns
control to the primary's saved stage for its separate ESS approval.

In the new-environment fallback, the Entities response is null or has null or empty `items`. The single combined confirmation table displays `Accounts, Contacts, Leads, Opportunities, Revenue Lines, Activities, Assets, Items, Product Group`, then asks exactly: `No Prior publish was performed, Please provide your confirmation to proceed with full publish of these OOTB objects`. The preview states that the requested selection cannot be validated. A Yes submits `{"entities":["Account","Contact","Lead","Opportunity","Revenue","Activity","Asset","Product","CRMProductGroup"]}` without `publishType`; do not validate these OOTB objects. A No collects a replacement full list, calls Entities again for validation, and then submits the mapped internal-entity array without `publishType` after the final Full Publish confirmation.

For an explicit Full Publish with a nonempty entity catalog, suppose Current active objects are `Accounts, Leads, Activities, Contacts, Consolidated Assets` and the requested object is `Accounts`. Before preflight, show those current and newly requested lists and ask the retain question. A Yes produces that five-object final selection, `Additional Objects Added` as `None`, and the mapped entity array `Account, Lead, Activity, Contact, ConsolidatedAsset`; a No produces only `Accounts` as the final selection. In either case, then render the final Full Publish approval table and require the final approval prompt.

## Approval, Retry, and Security

- Approval is mandatory and becomes invalid if environment, endpoint, headers, entities, mapped payload, or validated contract binding changes.
- A changed or unverified mapping input invalidates the prior mapped request immediately. Never leave its payload under an executable `current` filename or show its body as the current proposal. Preserve it only as a versioned historical artifact when supported, and leave a non-executable invalidation record containing safe fingerprints and the reason.
- There is one confirmation only. It is shown after validation, concurrency preflight, payload mapping, and immutable Data Loader source validation; it accepts the final object list and approves that exact source for submission.
- In the Fusion ABO dependent path, exact parent project/target/fixed-pair
  provenance and verified CPQ evidence are required. They are not approval.
  Obtain separate approval of Core's current persisted Task Hook preview;
  a saved preview, source digest or approval envelope alone does not authorize submission; require explicit approval of the current bound Core preview.
- Invalid object correction is not approval. Never continue with a partially valid list: show all invalid display names and up to three nearest matching display names for each invalid value, then collect and validate a complete corrected list. Do not restrict display-name validity by `isEnabled` or disclose the full catalog.
- Do not submit while the latest status is `WAIT`, `RUNNING`, or `PAUSED`. HTTP 404 with exactly `{"Error":"Cannot parse null string"}` is a no-prior-publish concurrency pass; any other status response fails closed.
- Do not retry POST after timeout, connection loss, or ambiguous submission. Perform only a safe status lookup and ask before another mutation.
- A submission status such as `WAIT` or `RUNNING` is reported as returned and is not treated as a reason to poll automatically.
- In the Fusion ABO dependent path, the user explicitly requests Data Loader
  status. After that check verifies success, the parent checks the pinned job
  once and offers monitoring or checking later. Repeated 15-second monitoring
  requires current explicit consent; no loader reads on those ticks.
- Keep administrator-facing responses functional and concise. Do not show contract-validation details, SHA-256 values, contract fingerprints, contract IDs, internal artifact paths, execution-node IDs, or binding metadata in normal flows. Persist those details internally for stale-payload detection, approval binding, audit, and diagnostics.
- Treat project run records as historical audit data, not opening-message content. Do not announce a prior job at the start of a new publish flow. Mention an earlier job only when a fresh concurrency lookup proves it is currently nonterminal and blocking.
- Never print or persist passwords, Authorization headers, OAuth tokens, cookies, or token-cache content.
- Treat Basic authentication as a secure runtime profile reference, never as a stored Base64 value.
- Use synthetic hosts, identifiers, timestamps, and users in examples and tests.

## Failure Handling

Apply `ora-resource/ora_error_handling.md` before preview or execution. Classify
input, catalog, authentication, authorization, transport, Fusion API, process,
artifact-persistence, and approval failures using the repository error-handling
taxonomy. Complete environment, privilege, input, mapping, contract, and
concurrency preflight before side effects. Do not retry a live publish POST
automatically; after an ambiguous outcome, make only the documented read-only
status check and require fresh approval before any new submission. The Fusion
ABO dependent path resumes only from its persisted exact-operation checkpoint
with GET-only status calls; it never recreates an operation or re-submits an
ambiguous publish. On timeout
or terminal failure, persist redacted diagnostics and the last known job status
under the project workspace, report the safe functional error and next action,
and never persist credentials, tokens, Authorization headers, or sensitive
payload values.

## Implementation Notes

Use the parent functional-area skill for sequencing. The object list can be accepted as JSON or a simple table; map display names to the internal REST `entities` field only after validation. This is not an FSM CSV export/import operation. Track token usage for all generated project artifacts and skill-run records.

## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business object.

1. Confirm that `publish` is the exact registered Data Loader business object.
2. Generate the default editable XLSX sample through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "publish" \
     --output-dir "<project-artifact-directory>"
   ```

3. Keep the generated workbooks together:
   - editable sample
   - attribute-details workbook
   - key-fields workbook
4. Review the generated headers and key fields before preparing source data. The operation uses read-only Fusion metadata and does not upload or import data.
5. Use the generated editable workbook as the starting point for the later Data Loader preparation and approval workflow.
