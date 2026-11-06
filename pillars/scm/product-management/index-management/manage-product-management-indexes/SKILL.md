---
skill_id: "scm.product-management.index-management.manage-product-management-indexes"
name: "Manage Product Management Indexes Setup Task Guidance"
description: "Resolves attribute names, codes, or mixed selectors for additions and removals in one Product Management index, validates captured Data Loader rows, and reconciles approved loads and separately approved rebuilds."
layer: "pillar"
pillar: "SCM"
offering: "Product Management"
functional_area: "Index Management"
functional_area_code: "CUSTOM_INDEX_MANAGEMENT"
task_code: "CUSTOM_EGP_MANAGE_PM_INDEXES"
task_name: "Manage Product Management Indexes"
parent_skill_id: "scm.product-management.index-management"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "REST"
businessObject: "productManagementESIndexedAttributes"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "import"
execution_mode: "hybrid"
owner_team: "SCM product management pillar team"
version: "0.7.3"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "canonical_index_name"
  - "single_index_request"
  - "attributes_to_add"
  - "attributes_to_remove"
  - "index_rebuild_requested"
  - "index_rebuild_skip_confirmation"
  - "ess_execution_options"
  - "data_loader_status_check_requested"
  - "failed_load_rebuild_choice"
  - "reconciliation_evidence"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "seeded_indexed_attributes"
  - "index_attribute_delta"
  - "resolved_attribute_identity"
  - "resolved_requested_removals"
  - "index_create_contract"
  - "index_scope_validation_result"
  - "index_rebuild_ess_payload"
  - "ess_delegation_contract"
  - "index_rebuild_decision"
  - "failed_load_rebuild_decision"
  - "index_rebuild_ess_submission_result"
  - "data_loader_submission_followup"
  - "data_loader_status_result"
  - "index_execution_state"
  - "skill_run_record"
  - "token_usage_record"
uses_core:
  - "core.runbook"
  - "core.fusion-api.rest-api-client"
  - "core.fusion-api.apps-common.lookups"
  - "core.data-loader"
  - "core.data-loader.task-hook"
  - "core.fusion-api.ess-job-submitter"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/product-management/index-management/manage-product-management-indexes/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/product-management/index-management/manage-product-management-indexes/current/"
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
  - "Persists the selected single-index request and validation evidence under the project workspace; does not create or advance a batch plan."
  - "Persists index-specific checkpoints locally through its bundled helper; validates continuation and evidence without authorizing execution."
  - "Imports approved productManagementESIndexedAttributes rows only through the live core.data-loader preflight, Task Hook preview and approval workflow."
  - "Submits one index rebuild through core.fusion-api.ess-job-submitter only after fresh explicit approval of the exact payload and verified load/readback or the explicit confirmed-failure rebuild choice."
required_privileges:
  - "Target-environment OAuth access and privileges to view productManagementESIndexedAttributes metadata and Data Loader data-set status, as preflighted by core.data-loader."
  - "Privileges to upload approved Data Loader content to UCM and initiate the selected productManagementESIndexedAttributes Data Loader operation, as preflighted by core.data-loader."
  - "Fusion privileges appropriate to submit and check the requested Product Management Index Maintenance ESS operation, as preflighted by core.fusion-api.ess-job-submitter."
depends_on:
  - "core.data-loader"
  - "core.data-loader.task-hook"
  - "core.fusion-api.ess-job-submitter"
  - "core.project-mgmt.project-state-manager"
---

# Manage Product Management Indexes Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Product Management Indexes` under `Index Management`.

## Setup Task Skill Contract

- task_code: `CUSTOM_EGP_MANAGE_PM_INDEXES`
- task_name: `Manage Product Management Indexes`
- parent_skill_id: `scm.product-management.index-management`
- pillar: `SCM`
- offering: `Product Management`
- functional_area: `Index Management`
- functional_area_code: `CUSTOM_INDEX_MANAGEMENT`
- available_flag: `Y`
- export_import_supported_flag: `N`
- csv_export_import_supported_flag: `N`
- dataloader_import_mode: `REST`
- businessObject: `productManagementESIndexedAttributes`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Product Management Indexes` under `Index Management`.

## Setup Task Metadata

- Task name: `Manage Product Management Indexes`
- Task code: `CUSTOM_EGP_MANAGE_PM_INDEXES`
- Available: `Y`
- Export/import supported: `N`
- CSV export/import supported: `N`
- CSV export/import routing: `not supported`
- Data Loader import mode: `REST`
- Business Object: `productManagementESIndexedAttributes`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `N`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

Do not route CSV export work to `shared.setup-export.task-level-export` or CSV import work to `core.data-loader` unless live Fusion metadata or Oracle guidance confirms support. Use `shared.validation.setup-data-validator` only when a setup data artifact is available for review. Use `shared.validation.reference-data-validator` when the task depends on cross-pillar reference data.

## REST Data Loader Import Workflow

`dataloader_import_mode: "REST"` identifies the registered Fusion Data Loader business-object contract; it does not authorize direct mutating REST calls. Route all setup-data mutations for `productManagementESIndexedAttributes` through `core.data-loader`.

1. Verify the registered business object and canonical index. Resolve user-supplied
   attribute, group, and object names or codes from existing identities first,
   then available metadata for unsatisfied requests using the rules below. Read seeded
   and existing identities and calculate the addition/removal delta, including
   missing seeded attributes for rebuild-only requests.
2. For any prospective POST, read the live create contract through
   `resolve_indexed_attribute_create_contract`. Populate required create codes
   from the uniquely resolved available-attribute record; names are not substitutes.
3. Use `core.data-loader` to generate the editable XLSX source after the delta is
   validated. Every POST includes `IndexName`, `AttributeCode`, `GroupCode`, and
   `ObjectCode`; `AttributeId` is blank or omitted. Validate prospective rows
   against the live create contract before Core preflight.
4. Follow Core's existing CLI preflight and Task Hook workflow described below.
   Core owns conversion, source/schema validation, the immutable ZIP and internal
   preflight envelope. Validate that exact ZIP against the delta and live create
   contract before building the Task Hook preview or presenting approval.
5. After explicit approval, use the unchanged Core preflight and Task Hook
   envelopes to submit the exact saved ZIP. Do not re-open the workbook or
   repeat validation after approval. An accepted import must include the
   Submitted Data Loader Status Continuation below in the same reply.
6. If the live metadata or template cannot represent the row, stop with a
   catalog-metadata mismatch. Never substitute a direct REST mutation.

### Core Preflight and Task Hook Handoff

There is no persistent Data Loader session or session event in this workflow.
Use the installed Core interfaces without importing Core Python implementation
code or constructing approval envelopes in the pillar.

1. In `core/data-loader`, run its declared preflight command without submission
   approval:

   ```text
   python3 scripts/upload_and_initiate.py <source.xlsx> --task-routed --preflight-envelope-output <internal-preflight.json>
   ```

   Require completed source/schema validation, `mappingComplete: true`,
   `taskRouted: true`, and Core's immutable artifact path and `archiveSha256`.
   An approval-stage preflight result means validation finished without upload;
   another failure, incomplete mapping or missing envelope blocks continuation.
   Core owns parsing/verifying its envelope. The host supplies only Core's
   returned artifact path and digest to the task guard, never an inferred path
   or a digest calculated from the source workbook.
2. Invoke Task Hook's `data-load` route with the existing project task context,
   exact task name and its persisted sequence. Read its execution guide and
   rule resources, then evaluate the applicable nodes. Reuse the active seeded,
   available and describe evidence. Validate the prepared ZIP through the
   archive guard below and retain its matching digest in the ordered results.
3. Call `build-data-load-preview` with the existing task context, ordered
   `ruleResults` and `finalData` bound to Core's same `archiveSha256`. Only after
   all checks pass, render Core's approval report and request approval of the
   exact environment, index and calculated change rows. Never
   treat the initial Core preflight report alone as a completed task preview.
4. After user approval, call Task Hook's `approve-data-load-preview`, then
   `verify-approved-data-load-archive` against that same ZIP. Persist and pass
   its returned `taskValidationEnvelope` unchanged, following Core's policy.
5. In `core/data-loader`, use its approved-preflight command:

   ```text
   python3 scripts/upload_and_initiate.py --approved-preflight-envelope <internal-preflight.json> --task-validation-envelope <task-envelope.json> --approve-upload
   ```

   Do not supply source paths, mapping edits, routing overrides or
   `--task-routed` on this approved invocation. Core checks the saved artifact,
   environment and Run Book binding before dispatch. A changed/missing
   artifact or context invalidates approval and requires fresh preflight and
   Task Hook validation. No automatic status polling or submission retry follows.

## Name-or-Code Inputs for Additions and Removals

Optional `ObjectSubTypeName` / `ObjectSubTypeCode` (or their snake_case
aliases) constrain the same Fusion metadata match. After resolving exactly one
available-attribute record, always retain its nonblank `ObjectSubTypeCode` in
the resolved identity, delta, and POST, even when the user omitted subtype.
Retain the returned subtype name as resolution evidence. Copy the code exactly;
never infer it from an attribute or group name. Multiple matching records require
disambiguation. Explicit subtype selectors must agree with the resolved record.
Block missing codes for explicit selectors, malformed codes, a resolved subtype
that is not writable in the live create contract, or any downstream omission or
change of the resolved code. Only a resolved record with no subtype uses a POST
without `ObjectSubTypeCode`.

Users may supply names, codes, or any combination for either operation.
Each addition and removal accepts `attribute`, `group`, and
`object` as a name or code, or explicit `attribute_name` / `attribute_code`,
`group_name` / `group_code`, and `object_name` / `object_code` fields (PascalCase
aliases are also accepted). At least an attribute selector is required. Explicit
name and code fields are AND constraints: both must identify the same record.
Apply the same rule to generic selectors, aliases, and optional subtype selectors.
Names/codes need not both be supplied; resolve missing values from metadata.
Never treat code-only or mixed input as a missing-name blocker. Preserve the
original request selectors and fingerprint; store resolved evidence separately.

Delegate retrieval of the standard lookup `ORA_EGP_PM_ES_INDEXES` to
`core.fusion-api.apps-common.lookups`. Require the complete result set, then
resolve the index within this pillar by trimmed, case-insensitive exact lookup
code or display meaning. Resolve requested additions against the complete
existing indexed-attribute response first. One unique complete match satisfies
the request without a POST. Only unsatisfied requests resolve from
`indexAvailableAttributes` for that canonical index, with trimmed,
case-insensitive exact comparisons. Generic
selectors match either name or code; explicit selectors match their named field.
Do not use fuzzy matches or derive codes from names. Multiple existing matches
block; a zero existing match proceeds to available metadata. Zero or multiple
available matches block prospective POST preparation. If a group or object selector was omitted, present
one unique candidate for scope confirmation before preparation; full uniquely
matching scope needs no extra confirmation.

`scripts/index_attribute_contract.py` implements this offline resolution and
POST validation. Its `--stdin` envelope contains `request` (one addition),
`canonical_index_name`, `existing_attributes` (complete live response), optional
`available_attributes` (complete live response), optional `create_contract`
(live describe response), and optional `scope_confirmed`. An exact existing
match returns `already_indexed` with its identity and subtype evidence and no
`post_row`; it requires neither available metadata nor a create contract.
An unsatisfied request returns a confirmation candidate or a verified `post_row`
from available metadata; every verified POST requires `create_contract`.
Omitting `existing_attributes` retains the prospective-POST interface for
missing seeded repairs. It makes no Fusion calls and writes no files. Pass its
input envelope through stdin. Run it for every requested addition and missing
seeded repair.

For example, synthetic input `attribute: Example Attribute`, `group: Example
Group`, `object: Example Object` can resolve to:

```json
{
  "RestAction": "POST",
  "IndexName": "fa-fscm-example",
  "AttributeCode": "EXAMPLE_ATTRIBUTE",
  "GroupCode": "EXAMPLE_GROUP",
  "ObjectCode": "EXAMPLE_OBJECT",
  "AttributeName": "Example Attribute",
  "GroupName": "Example Group",
  "ObjectName": "Example Object"
}
```

Copy the returned codes exactly, preserving case. The `/describe` contract
identifies required create inputs; `indexAvailableAttributes` supplies their
values. Do not ask users to repeat codes that can be resolved from metadata.

### Removal resolution

For removals, use the complete exact-index `productManagementESIndexedAttributes`
response, including names, codes, subtype fields and backend IDs. Never use
`indexAvailableAttributes` to select a DELETE target. Resolve trimmed,
case-insensitive exact selectors against that response; preserve returned case
in resolved values. All supplied names, codes and aliases must agree on one
record. A supplied `attribute_id` / `AttributeId` is an additional exact
constraint, never a replacement for an attribute selector. It may disambiguate
records whose supplied names/codes otherwise match; conflicting ID aliases block.
A unique candidate with omitted group or object requires scope confirmation,
using the same rule as additions. Full, unique scope needs no extra confirmation.
No match, multiple matches, incomplete metadata or a mismatched ID blocks row
preparation with actionable selector guidance; do not ask for names when codes
already identify the record.

Run `index_attribute_contract.py --stdin` with `operation: "remove"`, the original
`request`, `canonical_index_name`, complete `existing_attributes`, and optional
`scope_confirmed`. The default operation remains `add` for existing callers.
Removal returns `removal_resolved`, `candidate`, and `delete_row`, or
`candidate_confirmation_required` without a row. It never requires available
metadata or a create contract and performs no network calls. The DELETE row
retains the exact returned names/codes, subtype evidence and backend AttributeId.

For example, either operation accepts a synthetic selector such as
`{"attribute_code":"EXAMPLE_ATTRIBUTE","group":"Example Group","object_code":"EXAMPLE_OBJECT"}`.
The resolver fills the remaining names and codes from one live metadata record.

## Single-Index Scope Guard

The existing Run Book contains its catalog-resolved `Manage Product Management
Indexes` task. Do not change Run Book creation or use task Notes as execution
instructions. Start this task only after the active Run Book dashboard has been
delivered.

This skill handles exactly one requested index per invocation. Several
attributes for that index are allowed. If the user supplies two or more indexes,
stop with `input_validation` before any index-specific Fusion lookup, sample,
Task Hook, Data Loader, or ESS action. Ask the user to select one index and its
own attributes for this invocation. Do not choose the first index, split the
request into queued items, maintain batch status, or automatically start another
index after this one finishes. A later index requires a separate user request
and its own validation and approval gates.

Persist and register `single-index-request.json` under this skill's project
artifact directory. Its minimum non-sensitive contract is `schema_version:
"1.0"`, `environment`, one scalar `requested_index_name`,
`canonical_index_name` (null until the exact lookup resolves it), arrays of
`attributes_to_add` and `attributes_to_remove` whose rows inherit that index,
and boolean `index_rebuild_requested`. Record the request artifact, validation
summary, Data Loader Request ID and last status, readback summary, ESS payload and
request ID and rebuild approval decision in the existing project artifact/run
services. Data Loader failure material follows the persistence boundary below;
do not copy it into a project run record. Do not use chat history as the only checkpoint.

Persist `index-execution-state.json` beside the request artifact. It records
exactly one of `data_load_submitted`, `data_load_pending`,
`data_load_succeeded`, `data_load_failed`, `readback_verified`, `ess_approval_pending`, `ess_submitting`,
`ess_submitted`, `ess_skipped`, or `blocked`, together with the canonical index, the accepted
Data Loader Request ID when present, and non-sensitive artifact references.
Use the local helper to validate and persist task checkpoints; do not infer a continuation
from chat history.

The helper also retains `ess_dispatch_status` (`not_attempted`, `submitting`,
`submitted`, or `unknown`), `ess_request_id`, and
`data_loader_dispatch_uncertain`. These fields survive ordinary continuation
transitions; an uncertain dispatch must not be relabeled as never attempted.

A normal business review is not a failure: do not persist `blocked` merely
because the user requested a proposal or the delta is empty. After validating
an empty delta, prepare the exact ESS payload and persist `ess_approval_pending`
before stopping for review; this state records preparation, never submission
approval. Keep fresh exact-payload ESS approval mandatory.

The current state belongs to one invocation. Its canonical index and accepted
Data Loader Request ID are immutable after the first transition. For a later,
separately requested index in the same project, use the helper's `--start-new`
option with that new invocation's initial event. It archives the prior state
under `current/history/` by writing a snapshot, then atomically replaces the
current state. The prior current file remains readable if either write fails.
The helper refuses to replace a pending state. Preserve the archived state and prior run record; do
not transfer approvals or external IDs to the new invocation.

For a new user execution request after a terminal `blocked` invocation with
no Data Loader Request ID and no ESS submission or uncertain dispatch evidence,
`--start-new` may also restart the same index. Archive the prior pillar state and authorized evidence references, repeat the declared validation, and obtain fresh approvals.
Do not carry approvals or external IDs into the restarted invocation.
Do not use this recovery for pending, submitted, or uncertain external actions.
A request to edit this skill does not authorize restarting a project invocation.

The helper rejects a blocked restart before archiving or writing when a Data
Loader Request ID exists, `data_loader_dispatch_uncertain` is true, an ESS
Request ID exists, or `ess_dispatch_status` is not `not_attempted`. Legacy
blocked states missing dispatch fields also fail closed: reconcile their authorized saved evidence or a fresh user-requested core status result instead of inventing a no-dispatch marker or
discarding an existing request. Request status or resolve the external outcome
through the declared core workflow; do not restart the invocation to bypass it.
For a Data Loader upload/initiation outcome that is uncertain without an accepted
Request ID, record `blocked --data-loader-dispatch-uncertain` with a permitted pillar request/delta reference or an explicitly requested diagnostic file. A confirmed failure before any external dispatch uses
ordinary `blocked`. An empty delta still skips Data Loader and enters
`ess_approval_pending` directly; this restart guard does not restrict that path.

Run the local, read-only guard before an index-specific Fusion lookup:

```text
python3 pillars/scm/product-management/index-management/manage-product-management-indexes/scripts/index_work_item_guard.py --request <single-index-request.json>
```

After canonical lookup, rerun the request guard with `--mutation-ready` before
Data Loader or ESS approval. For live Data Loader work, validate Core's
immutable ZIP through the digest-bound archive gate below before Task Hook preview.
Delegate source-file validation, serialization, ZIP generation and approval
binding to core.data-loader. The pillar compares the rows in Core's prepared
ZIP against the calculated delta before preview. Inspect only Core's prepared
immutable ZIP at the declared task-validation gate; never re-open the original
workbook or regenerate a ZIP. Core owns technical source and archive validation.

## Metadata Evidence at Task Hook

Complete the declared read-semantic metadata POST lookups through
core.fusion-api.rest-api-client in the active preflight before Task Hook.
Keep complete responses in host memory bound to environment, canonical index
and unchanged request fingerprint. Task Hook consumes that same evidence;
it does not issue these POSTs through its GET lookup route. Do not reconstruct
metadata from chat or an earlier invocation. Missing/incomplete evidence or a
changed request/environment blocks preview and requires fresh preflight and
Task Hook validation. After approval, follow Core's retained-artifact contract;
do not re-query metadata or repeat task checks for an intact approved artifact.

## Checkpoint Ownership and Reconciliation

### Data Loader Persistence Boundary

Core Data Loader's persistence contract is authoritative. Render its complete
failure/status report in the current response and retain its diagnostics and
counts only in active host memory. Do not save core failure reports, diagnostics,
logs, summaries, dashboards or failure run records unless the user explicitly
requests a specific file. Applicable logs produced by core's user-requested
status workflow follow that workflow's separate policy; reference those authorized
logs without copying them into a new project failure report.

The pillar checkpoint stores only invocation identity, accepted external IDs,
continuation/dispatch markers, terminal outcome flags, user rebuild decisions and
references to permitted pillar artifacts or separately authorized files. It must
not contain core failure messages, error rows, counts, payloads or report copies.
This routing checkpoint is not a substitute for current core status evidence.
Use the existing request/delta artifact reference for a blocked loader dispatch
marker; no diagnostic file is required. Saving a failure file is optional and
must not become an extra prerequisite for the failed-load rebuild choice.

When a later turn needs load status, counts or failure details without an
authorized saved report, wait for the user to request a fresh core status check
for the same accepted Request ID in the same environment. Normalize its confirmed
result in memory and apply the reconciliation contract below. Never reconstruct
failure details from chat or a checkpoint, query automatically, or resubmit.
Without an accepted ID or immutable invocation bindings, remain blocked through
the existing reconciliation path. ESS and local checkpoint-write diagnostics
follow their own declared persistence policies.

The active routed Run Book/host workflow owns invocation, approval, waiting and
resume decisions. The allowed ora-resource Task Nodes own only this task's
index-specific preconditions and outcome rules. The local state helper validates
index checkpoint evidence; it is not an execution engine and never authorizes a
Fusion call, imports data, obtains approval, or advances another task.
The bundled `scripts/index_execution_state.py` helper performs safe JSON
read/write and history archival for this task inside the project workspace.
It uses Python standard-library modules and requires no new core adapter.
The host must also invoke the declared artifact registry/version services, record
the durable run and token usage, and follow core.data-loader's persistence limits.
A saved checkpoint never replaces current validation or explicit approval.

Every initial checkpoint requires the verified environment with --environment
and the original single-index request fingerprint with --request-sha256; missing
or malformed bindings fail before persistence. Continuations inherit these
immutable bindings. Missing legacy bindings cannot be backfilled by CLI arguments.
At ess_submitting, --approved-payload-sha256 must supply the exact original
approved payload fingerprint unless it is already recorded. These are local
checkpoint bindings, never a saved Core approval replay.

After a blocked status check or readback, the user may request reconciliation
through the already declared core Data Loader status and exact-index readback
routes. Reconciliation performs only those selected reads, never submission.
Normalize the confirmed core result into an in-memory evidence object and pass
it to the helper with --reconcile-stdin and the corresponding --event:

- Common fields: confirmed=true, environment, canonical_index_name,
  request_sha256 and outcome equal to the requested checkpoint event.
- Load evidence: the original accepted data_loader_request_id. A confirmed
  pending status permits data_load_pending; terminal success permits
  data_load_succeeded, followed by the ordinary readback gate. A corrected
  exact-index readback permits readback_verified only with load_succeeded=true
  and the original submitted delta, never a recalculated delta. A fresh confirmed
  terminal failure permits data_load_failed with --data-loader-terminal-status
  Failed. When no authorized report reference is supplied, require
  user_requested_status_check=true from the current user-requested core check.
  This boolean records the selected read route; it is not submission approval.
- ESS evidence: ess_request_id and approved_payload_sha256 matching the
  original approved payload. A blocked attempted ESS dispatch may become
  ess_submitted only after core evidence confirms acceptance for that payload,
  index and environment. Do not infer this from a similar job or timestamp.

Supply --artifact-ref only for permitted pillar artifacts or authorized evidence
files. Load reconciliation can omit it when the fresh user-requested in-memory
evidence meets the bindings above; ESS reconciliation still requires its
authorized artifact reference. Do not create a failure file merely to satisfy
the helper. The helper preserves
prior artifacts and a reconciliation_history entry, including previous dispatch
uncertainty. It rejects a changed environment, request fingerprint, index, ID,
conflicting terminal failure or absent evidence. A reconciled pending/successful
load clears only its current loader uncertainty flag while retaining history.
Never use --start-new to evade an outstanding or uncertain external operation.

Legacy checkpoints without environment/request bindings, unknown Data Loader
dispatch without an accepted ID, or ESS attempts without the original payload
fingerprint remain blocked. Reconcile their original registered artifacts and
core evidence through the active workflow; do not manufacture missing bindings,
reset the file or relabel the attempt. If core cannot establish the exact
identity, record an approval_blocker with the next evidence needed and stop.

## Submitted Data Loader Status Continuation

After `core.data-loader` accepts an indexed-attribute import and returns a
positive Request ID, emit the local helper's output as **commentary before the
final initiation report**. The commentary states the accepted Request ID,
that status has not been checked, and asks exactly:
`Would you like me to check the status of this Data Loader request now?`
Do not query status unless the user asks.

The final answer must contain only Core's complete, unchanged
`## Data Load In Progress` report, including its tables. Do not prepend or
append the helper output, the status question, a summary, or any other pillar
content to that final report. If pre-report commentary is unavailable, return
Core's unchanged report and defer the invitation to a later interaction;
never change the final-report contract to include it.

```text
python3 pillars/scm/product-management/index-management/manage-product-management-indexes/scripts/data_loader_submission_followup.py --request-id <accepted-request-id>
```

This helper is offline and does not authorize or perform a status query. If
core reports acceptance without a positive Request ID, do not invent one or
claim a checkable submission; preserve the initiation diagnostics, classify
the outcome as uncertain, and block ESS preparation pending reconciliation.
Wait for the user to request a status check before invoking the core Data
Loader status workflow with the accepted Request ID in the same target
environment.

After each requested check, present the complete core status report. If the
result is pending or the data set is not yet available, offer the same status
choice again, using the same Request ID. Each subsequent check requires a new
user request; do not schedule, poll, or infer consent from an earlier check.
Keep the accepted request and last observed status available in the project
task run record so a later turn can resume without uploading or initiating the
artifact again.

When the result is terminal, stop offering the pending-load status choice. A
successful result still requires verification of every requested change for
the exact canonical `IndexName` before the separate ESS preparation and
approval gate. For a confirmed terminal failed result, preserve the complete core diagnostics
and follow the Failed Data Loader Rebuild Choice below. An uncertain result
keeps ESS preparation blocked. Do not resubmit the load as a status retry.

For a successful status result, this continuation is mandatory in the same
user-facing reply after the complete core status report:

1. Transition `index-execution-state.json` to `data_load_succeeded`.
2. Read back `productManagementESIndexedAttributes` for the exact canonical
   `IndexName` and verify every submitted POST and DELETE result with
   `index_delta_guard.py --stdin --readback`. Supply the original validated
   request and submitted delta plus the complete core-retrieved response as
   `readback`; do not recalculate the delta after import. A POST with a subtype
   requires that exact subtype; a POST without one uses the original triplet
   match. Verify DELETE by its submitted backend AttributeId so an alternate
   subtype record does not imply failure. Missing required evidence, a retained
   DELETE ID, or a wrong-index row transitions to `blocked` and blocks ESS.
3. Transition the state to `readback_verified`, prepare the immutable ESS
   payload, then transition it to `ess_approval_pending`.
4. Append the target environment, affected index, rebuild impact, exact ESS
   payload, and a fresh explicit approval question. The complete core status
   report must remain unchanged; it is not a terminal response for the wider
   index-management workflow.

Use the helper for each state transition:

```text
python3 pillars/scm/product-management/index-management/manage-product-management-indexes/scripts/index_execution_state.py \
  --project-root project/<project_id> --event <event>
```

The helper derives the only permitted state path from `--project-root`:
`artifacts/pillars/scm/product-management/index-management/manage-product-management-indexes/current/index-execution-state.json`.
It rejects paths outside this repository's `project/{project_id}` workspace,
including symlinked artifact-path escapes, and reports local write failures as
`artifact_persistence` without exposing a path or state contents.

## Failed Data Loader Rebuild Choice

A confirmed terminal `Failed` Data Loader result gives the user a choice to
rebuild the current index despite the load failure. This also applies to partial
success. Present the complete core status report and retain error details and
successful/failed counts in active memory under the Data Loader Persistence
Boundary. Retain the Request ID and canonical index in the pillar checkpoint;
never relabel the load successful
or imply that a rebuild retries or repairs failed rows.

1. Persist `data_load_failed` using the state helper with
   `--data-loader-terminal-status Failed`. If no authorized report reference
   exists, pass --reconcile-stdin with the fresh confirmed in-memory load evidence,
   outcome=data_load_failed and user_requested_status_check=true. Do not save a
   report just to produce --artifact-ref. For an older blocked invocation, obtain
   a fresh user-requested status check bound to its original environment, request
   fingerprint, Request ID and canonical index before offering the choice.
2. After the unchanged core report, state that a rebuild uses the current index
   configuration, including partial successes, and does not fix failed rows.
   Ask: `Would you like to proceed with the index rebuild despite this failed
   Data Loader request?` Pending, timed-out, uncertain, or missing-ID outcomes
   do not offer this choice.
3. Wait for the user's choice. On decline, persist the decision and transition
   to `blocked` with `--failed-load-rebuild-choice decline`; do not prepare or
   submit ESS. On proceed, persist the explicit choice bound to the environment,
   canonical index and failed Request ID; keep detailed failure evidence in
   active memory or an authorized file. A request to proceed
   with the rebuild after the reported failure counts as this choice.
4. On proceed, prepare the immutable payload in the Index Rebuild ESS Workflow
   and transition to `ess_approval_pending` with
   `--failed-load-rebuild-choice proceed` and `--artifact-ref <decision>`.
   This branch does not require `data_load_succeeded` or full-delta readback.
   Retain the original submitted delta and terminal failure checkpoint flag; do not
   invent complete success or recalculate/resubmit the failed load.
5. If the host lost the current failure report or counts before this step,
   obtain a fresh user-requested core status check and confirm the same terminal
   failure before continuing. Present the exact target environment, index, impact, failed-load counts and
   payload, then require fresh explicit ESS submission approval. Choosing to
   proceed despite failure is not approval of a payload not yet presented.
   Use the same approved delegation contract and submit-only core ESS route.
   Retain terminal `Failed` status and the rebuild choice through subsequent
   states. Never transfer this choice to another load, index or environment.

## Index Attribute Delta Workflow

For every requested index change or explicit index rebuild, calculate the target
state before preparing a Data Loader row. Use the exact canonical `IndexName`
returned by `ORA_EGP_PM_ES_INDEXES`. Follow Core's existing preflight, persistence,
Task Hook preview and approval contract. Validate the exact prepared ZIP against the delta before preview.

1. POST `{"indexName":"<IndexName>"}` to the read-only
   `indexManagementMetadata` endpoint. Extract every value in
   `SeededIndexedAttributes`. Each value is an identity in the form
   `AttributeCode#GroupCode#ObjectCode`.
2. Resolve every user-requested addition by name or code against the complete
   existing indexed attributes first, applying all supplied selectors. A unique
   existing match retains its exact names, codes and subtype evidence and is
   already satisfied. Multiple matches or incomplete subtype evidence block.
   Resolve only unsatisfied requests through `indexAvailableAttributes`.
   Retain its three-part identity plus the exact nonblank ObjectSubTypeCode returned by the unique metadata
   record, even when the user omits subtype or supplies null/empty selectors. Keep
   seeded identities as three-part requirements. For rebuild-only requests,
   check all seeded identities even with no requested additions.
3. Retrieve all existing indexed attributes for the canonical index, including
   ObjectSubTypeCode and ObjectSubTypeName. A requested addition with a resolved subtype
   is already present only if all three codes AND the subtype code match.
   A different or explicitly blank/null existing subtype does not satisfy it.
   Missing subtype evidence on a matching triplet blocks scoped comparison;
   retrieve complete metadata rather than assuming absence. Only when the resolved metadata has no
   subtype, use triplet comparison without a subtype constraint. Seeded identities also use triplet comparison. Union the missing seeded
   and requested identities without duplicate POST rows. Preserve distinct existing
   subtype records; conflicting resolved subtypes for one triplet block rather
   than silently selecting one. Do not delete an existing alternate subtype.
4. Resolve every remaining addition identity, including a missing seeded
   identity found during a rebuild-only request, to one exact
   available-attribute record. Then prepare `RestAction: POST` rows with the exact returned
   `IndexName`, `AttributeCode`, `GroupCode`, and `ObjectCode`, plus validated names.
   Include every nonblank ObjectSubTypeCode returned by the resolved record,
   including for missing seeded repairs. Check the live create
   contract. `AttributeId` remains blank or omitted.
5. Resolve user-requested removals with `resolve_requested_removal` against
   the complete exact-index existing response, applying every original name,
   code, generic selector, subtype and supplied ID constraint. Record one ordered
   resolved identity and verified backend `AttributeId` per request before final
   delta validation. The resolver supplies exact names even for code-only input.
   Never use a seeded/default or available-attribute identity as a DELETE target.
   Before preparing any source, compare every resolved requested addition, including
   already-indexed matches, with every resolved removal. Matching code triplets
   overlap when the addition has no resolved subtype or both resolved subtype
   codes match. Stop with input_validation and ask the user to choose add or
   remove for the overlapping scope; never silently prefer deletion or infer a
   replacement operation. Distinct resolved subtype codes may proceed. Repeat
   this check against the unchanged request and delta before captured-row approval.
6. Prepare one Data Loader source containing the calculated POST
   rows followed by the requested DELETE rows; core captures it before approval. If both deltas are empty, skip
   only Data Loader and continue to the Index Rebuild ESS Workflow.

### Delta and Captured-Row Gates

Calculate and validate `index_attribute_delta` before sample/source
preparation. Retain the existing schema version `1.0` evidence: environment,
canonical index, request fingerprint, ordered resolved requested additions,
seeded and existing code identities, validated missing seeded additions, and
calculated POST/DELETE rows. Include `resolved_requested_removals` for all
removals (an empty array may be omitted when none are requested). Each entry
contains `request_index`, `attribute_id`, attribute/group/object names and codes,
returned subtype fields (including null/blank code evidence), and
`scope_confirmed: true` only after required partial-scope confirmation. DELETE
rows retain the same resolved fields plus `rest_action: DELETE`. Keep the original
request immutable. The guard independently re-resolves its selectors against
complete existing evidence and rejects conflicting selectors, duplicate DELETE
IDs, changed evidence or a different backend target. Legacy deltas with removals
but no resolution evidence require fresh preflight and validation; never infer
this evidence or replay old approvals. Previously submitted deltas still use
their original ID-based readback and continuation paths. Each resolved addition
preserves the original request index, all supplied selector constraints, and the returned subtype code
and name when present. Captured POST rows must retain every resolved subtype code. Each POST contains codes
and names from its unique source record; each DELETE contains its resolved ID.

Use `index_delta_guard.py --stdin` with an envelope of `request` and `delta`
for the initial check. Do not pass `--require-data-loader` at this stage. The
request fingerprint is computed by `_request_digest` and binds the delta to the
selected request. An invalid delta blocks continuation; a valid empty delta does
not. Inspect the validated `data_loader_required` result:

- If false, persist the validated empty delta, record that Data Loader was
  intentionally skipped, prepare the immutable canonical-index ESS payload,
  and transition directly to `ess_approval_pending`. Follow
  `PMINDEX.PREPARE_ESS_REBUILD_EMPTY` to the separate fresh ESS approval decision.
  An empty delta must not transition to `blocked` or imply an ESS skip.
  Do not prepare a source or start Core preflight.
- If true, rerun `index_delta_guard.py --stdin --require-data-loader` before
  source preparation. After Core preflight, use the archive check below for
  every nonempty delta, including removal-only changes.

### Prepared-Archive Row Gate

Before Task Hook preview or approval, pass `request`, `delta` and the active
`create_contract` (required for POSTs) through stdin:

```text
python3 pillars/scm/product-management/index-management/manage-product-management-indexes/scripts/index_delta_guard.py --stdin --require-data-loader --archive <core-prepared.zip> --archive-sha256 <core-preflight-archiveSha256>
```

The guard reads the ZIP bytes once, verifies Core's digest, and inspects only
its root indexed-attributes DAT. It checks row order, index, operation, names,
codes, generated IDs, resolved removal IDs and every metadata-derived subtype
against the validated delta and live create contract. It rejects extra sections,
malformed headers, directive/RestAction disagreement and changed archive bytes.
Only Core-ignored MacOS sidecars are excluded from member selection. The returned
`archive_sha256` must equal Core's `archiveSha256` and Task Hook's
`finalData.archiveSha256`; a mismatch blocks preview. The guard performs no
Fusion calls, source conversion, preflight-envelope parsing or submission.

DELETE optional code fields may be blank when the registered template uses
names and ID; supplied code/subtype fields must agree. Names-only POSTs,
unrequested rows, missing POST create metadata and lost subtype codes block.
`--stdin --captured` remains an offline normalized-record validation interface
for tests and callers with explicit records; it is not a session protocol and
cannot substitute for the digest-bound archive check in this live workflow.

Follow Core's source correction, Task Hook preview, approval and retained-artifact
submission contract above. All nonempty deltas reach PMINDEX.DATA_LOADER_GATE.
A requested successful status plus exact readback, or an explicit failed-load
rebuild choice after confirmed terminal failure, permits ESS preparation.
A saved pillar artifact never substitutes for Core's validation or approval.

Pillar-owned preparation artifacts, including a calculated delta, may be retained
under the repository’s confidentiality and project-artifact rules. This does not
authorize persisting copies of Core preflight envelopes or approval artifacts contrary to
core.data-loader’s contract. Record project intent, validation counts, state,
accepted external IDs, and sanitized diagnostics under their applicable policies.
The separate ESS payload follows its own workflow.

## Preflight and Execution Safety

Before preparing a preview or performing any live Fusion activity, load and
apply `ora-resource/ora_error_handling.md`. Its task-specific classifications,
disclosure rules, and refusal rules are mandatory controls for Data Loader and
ESS preparation, approval, submission, status checks, and failure handling.
Do not proceed when that resource is unavailable or cannot be read; classify
the condition as `artifact_persistence` and stop before preview or live
execution.

Before any Fusion-changing action, confirm the target environment, Data Loader privileges, registered business object, exact index/attribute scope, seeded metadata, existing-attribute state, calculated addition/removal delta, and rows from Core's immutable prepared ZIP. Use `validate_index_available_attribute` to confirm that each POST identity resolves to exactly one available source attribute. Validate the source row against the current Data Loader metadata and obtain the Task Hook preview before `core.data-loader` evaluates approval and submits the import.

Classify durable failures as `input_validation`, `catalog_or_metadata_mismatch`, `auth_expired_or_invalid`, `authorization_or_privilege`, `transport_or_environment`, `fusion_api_error`, `process_timeout`, `process_failed`, `artifact_persistence`, or `approval_blocker`. Delegate authentication, token refresh, HTTP transport, and technical retry handling to the core skill executing the operation: `core.fusion-api.rest-api-client` for declared metadata/readback requests, `core.data-loader` for loads, and `core.fusion-api.ess-job-submitter` for rebuild submissions. Do not add a pillar-level retry around a failed core invocation. Preserve the returned failure stage, classification, and diagnostics, then apply the index-specific stop and continuation rules. Do not automatically resubmit failed or uncertain index changes; any subsequent attempt must satisfy the applicable workflow checks and approval requirements.

For a timeout or failed Data Loader import, render core's report and follow the
Data Loader Persistence Boundary: retain only permitted pillar checkpoint fields,
and save core failure material only for an explicit request for a specific file.
Use fresh user-requested status checks for recovery when no report is saved.
For ESS and local persistence failures, retain sanitized diagnostics under their
declared policies with stage, failure class, environment, artifact references,
external ID, last status and next action. Never print or persist credentials,
OAuth tokens, token-cache contents, private keys, tenant secrets or sensitive payloads.

## Index Rebuild ESS Workflow

Use this workflow after every requested index operation, including an operation
whose calculated attribute delta is empty, and after an explicit failed-load rebuild choice. It is required by default because a
rebuild can be needed even when the indexed-attribute data already matches the
requested state. Skip it only when the user explicitly confirms that ESS
submission is not required; absence of a skip confirmation means the workflow
must prepare the rebuild request.

1. When the calculated POST or DELETE delta is nonempty, including a missing
   seeded-attribute repair delta from a rebuild-only request, submit the
   indexed-attribute change through `core.data-loader`. After submission,
   use the Submitted Data Loader Status Continuation above and, once the load
   is complete and successful for the exact canonical `IndexName`, proceed
   with preparation of the Product Management index rebuild ESS job and obtain
   separate approval to submit that index rebuild job. For a confirmed terminal failed load, use the Failed Data Loader Rebuild
   Choice before preparing ESS. Do not prepare, preview, or submit ESS while
   the related load is pending, uncertain, or unverified. When the delta is empty, record that Data
   Loader was intentionally skipped and continue directly to the ESS decision
   and its separate approval gate.
2. When more than one attribute is added or removed, require every requested
   change for that one index to be verified before preparing one rebuild job.
   A confirmed failed change may use the explicit failed-load rebuild choice;
   pending, uncertain, or different-index changes still block the job.
3. Build the following immutable request using the exact canonical `IndexName`
   already validated for the indexed-attribute operation. Substitute only the
   two marked values; preserve every other field and the one-element parameter
   order exactly:

   ```json
   {
     "description": "rebuildIndex-<index name>",
     "jobDefinitionId": "JobDefinition://oracle/apps/ess/scm/productCatalogManagement/common/PMESIndexMaintenanceJob",
     "application": "FscmEss",
     "requestType": "SINGLETON",
     "requestParameters": [
       {
         "name": "submit.argument1",
         "paramType": "STRING",
         "value": "<index name>"
       }
     ]
   }
   ```

4. Prompt the user with the target environment, the affected index, the
   rebuild impact, and this exact payload. Require a new explicit approval
   immediately before submission. The user may instead explicitly confirm that
   ESS submission is not required, which records a skip and ends the rebuild
   workflow. Approval of the Data Loader import, an earlier plan, or the
   combined attribute-and-rebuild request does not approve this ESS POST.
   On an explicit skip, transition the continuation state from
   `ess_approval_pending` to terminal `ess_skipped` and persist the skip
   decision; absence of approval is not a skip.
5. After explicit approval, construct an `ess_delegation_contract` with stage
   `approved_submission` and validate it against
   `schemas/ess-delegation-contract.schema.json` version `1.0`. Populate it as
   specified below and apply the ESS handoff validation rule in
   `ora-resource/ora_input_validation.md`. Delegate only the validated envelope
   to `core.fusion-api.ess-job-submitter`; core owns mapping its contents to the
   script-level submission interface. Preserve submit-only behavior: execution
   options do not authorize polling. Immediately before invoking core, persist
   `ess_submitting` with an artifact reference to the approved immutable payload.
   This checkpoint denotes an attempt in progress and is not restartable after
   a crash. On confirmed acceptance, persist `ess_submitted --ess-request-id
   <requestId>` with the core response artifact. Persist the returned positive `requestId`
   and approved payload fingerprint under the active project workspace. Do not
   call Scheduler REST directly from this task skill.
6. Do not automatically poll, retry, or submit a replacement request. When the
   user asks for job status, use the core ESS submitter's `--request-id` route.
   On a missing response, timeout, or transport ambiguity, retain the payload
   fingerprint and any returned ID, record `blocked --ess-dispatch-uncertain`
   with the core diagnostic artifact, reconcile with read-only evidence, and
   require new explicit approval before another submission.


### Approved ESS Delegation Envelope

Prepare the task, job, environment, and execution options alongside the rebuild
preview. Do not label the envelope approved or set approval to true until the
user approves that exact submission. A Data Loader approval cannot supply this
ESS approval.

| Contract field | Value |
|---|---|
| contract_version | 1.0 |
| stage | approved_submission, only after explicit ESS approval |
| task.task_name | Manage Product Management Indexes |
| task.task_code | CUSTOM_EGP_MANAGE_PM_INDEXES |
| fusion_environment_context | Verified target environment context used for the approved rebuild; exclude credentials and tokens |
| job_contract.job_definition_id | JobDefinition://oracle/apps/ess/scm/productCatalogManagement/common/PMESIndexMaintenanceJob |
| job_contract.application | FscmEss |
| request_payload | Exact approved rebuild payload from step 3, with the verified canonical IndexName |
| execution_options.wait_seconds | Positive integer from validated ess_execution_options or the current core default |
| execution_options.poll_interval_seconds | Positive integer from validated ess_execution_options or the current core default |
| approval.explicit_submission_approval | true only after fresh explicit approval |
| approval.approved_payload_sha256 | SHA-256 of the exact approved request_payload serialization |

Serialize the payload once as UTF-8 JSON for the approval fingerprint and retain
that representation through handoff. Verify the hash against the approved bytes;
do not recompute a new approval hash to authorize a changed payload. Preserve the
approved environment, job identity, and execution options with the payload.
Validate the complete envelope, including the schema's conditional requirements
for approved_submission, before delegation. Do not pass independent environment,
payload, or execution-option overrides beside the envelope. Core maps the
validated contract to its existing submission interface with submit-only behavior;
only a later user-requested status check may authorize tracking.


## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business object.

1. Confirm that `productManagementESIndexedAttributes` is the exact registered Data Loader business object.
2. Generate the default editable XLSX sample through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "productManagementESIndexedAttributes" \
     --output-dir "<project-artifact-directory>"
   ```

3. Keep the generated workbooks together:
   - editable sample
   - attribute-details workbook
   - key-fields workbook
4. Review the generated headers and key fields before preparing source data. The operation uses read-only Fusion metadata and does not upload or import data.
5. Use the generated editable workbook as the starting point for the later Data Loader preparation and approval workflow.

## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`
- `canonical_index_name`
- `single_index_request`
- `attributes_to_add`
- `attributes_to_remove`
- `index_rebuild_requested`
- `index_rebuild_skip_confirmation`
- `ess_execution_options`
- `data_loader_status_check_requested`
- `failed_load_rebuild_choice`
- `reconciliation_evidence`

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `seeded_indexed_attributes`
- `index_attribute_delta`
- `resolved_attribute_identity`
- `index_create_contract`
- `index_scope_validation_result`
- `index_rebuild_ess_payload`
- `ess_delegation_contract`
- `index_rebuild_decision`
- `failed_load_rebuild_decision`
- `index_rebuild_ess_submission_result`
- `data_loader_submission_followup`
- `data_loader_status_result`
- `index_execution_state`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Reviewer group: SCM Pillar Lead, A-Team/core, and QA.

Use the parent functional-area skill `scm.product-management.index-management` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
