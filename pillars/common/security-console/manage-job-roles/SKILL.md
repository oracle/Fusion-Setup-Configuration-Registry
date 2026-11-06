---
skill_id: "common.security-console.manage-job-roles"
name: "Manage Job Roles"
description: "Prepare individual custom-role creation, updates, redesign and deletion requests, and route supported role changes through validated FSM CSV packages and approval-gated Data Loader execution. Also export, migrate or restore Manage Job Roles setup data."
layer: "pillar"
pillar: "Common"
type: "orchestration"
task_code: "ASXS_MANAGE_JOB_ROLES"
task_name: "Manage Job Roles"
parent_skill_id: "common.security-console"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
execution_mode: "hybrid"
owner_team: "FSCR Security team"
version: "0.3.0"
inputs:
  - "project_id"
  - "source_environment"
  - "target_environment"
  - "requested_operation"
  - "job_role_scope"
  - "setup_archive"
  - "user_input_file"
  - "execution_approval"
  - "role_definition_or_change_request"
  - "security_checkup_choice"
  - "proposed_role_and_privilege_evidence"
outputs:
  - "manage-job-roles-export"
  - "import-template-export"
  - "input-file-conformance-result"
  - "corrected-input-file"
  - "archive-validation-result"
  - "import-approval-preview"
  - "data-load-execution-result"
  - "diagnostics"
  - "skill_run_record"
  - "token_usage_record"
  - "role_change_plan"
  - "operation_support_result"
  - "security_checkup_decision"
  - "security_checkup_result_reference"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.common.security.risk-and-security-checkup"
  - "core.data-loader"
uses_core:
  - "core.data-loader"
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
  - "scope"
  - "exports"
  - "validation_results"
  - "design_decisions"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/common/security-console/manage-job-roles/"
    versioning_policy: "append-only"
  - artifact_type: "configuration_export"
    default_location: "project/{project_id}/exports/common/security-console/manage-job-roles/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/common/security-console/manage-job-roles/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
oracle_supplied_guidance_files:
  - purpose: "FSM archive and task identity validation"
    location: "ora-resource/ora_input_validation.md"
  - purpose: "Import dependency and same-environment restore checks"
    location: "ora-resource/ora_dependency_readiness.md"
  - purpose: "Immutable preview and Data Loader route enforcement"
    location: "ora-resource/ora_design_enforcement.md"
  - purpose: "Approval, retry, and diagnostic controls"
    location: "ora-resource/ora_error_handling.md"
oracle_supplied_guidance_status: "Repository-authored task validation guidance; current Oracle documentation and the active Fusion contract remain authoritative."
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "Only when the user opts in, delegates read-only risk metadata retrieval and assessment artifacts to the shared Risk and Security Checkup workflow."
  - "May route an approved task-level export to the shared export skill."
  - "May route an approved immutable FSM archive to core.data-loader for upload and import."
required_privileges:
  - "When the optional checkup is selected, BOSS read privileges required by shared.common.security.risk-and-security-checkup in the selected target environment."
  - "Verified Functional Setup Manager privileges to export the Manage Job Roles setup task."
  - "Verified target-environment privileges to upload and initiate the approved FSM archive through Data Loader."
---

# Manage Job Roles

## Purpose

Provide a controlled, cross-pillar method to create, update, redesign and
process deletion requests for individual custom roles, and to export, validate
and approval-gate the import of the **Manage Job Roles** FSM setup task. Delegate
transport and live import execution to the declared shared and core
dependencies. Prepare user-specified role values only against a verified FSM
CSV template, retaining its headers, metadata and supported operations.

Export and move the FSM setup task **Manage Job Roles** only through the
declared dependency workflows. The catalog identity is task code
`ASXS_MANAGE_JOB_ROLES`; require a current catalog or live-task lookup to
confirm that its export/import flags remain supported before execution.

## Scope and boundaries

- Accept creation, update, redesign and deletion requests for individual custom
  roles. Prepare only operations supported by the current FSM CSV contract;
  execute supported changes through `core.data-loader`.
- Support task-level FSM CSV export and import of an exported, supplied or
  template-conformant candidate archive.
- Honor the user's role design and explicit changes in this skill. Preserve
  unrelated fields and memberships; do not substitute another skill's missing
  execution classification for this declared FSM/Data Loader route.
- Do not call Fusion, OAuth, UCM, REST, FSM, or loader commands directly.
  `shared.setup-export.task-level-export` owns export; `core.data-loader`
  owns every import preflight, upload, initiation, and monitoring route.
- Treat a changed archive, source scope, target environment, or validation
  result as a new request that must pass all gates again.

## Required preflight

1. Resolve the project workspace, requested operation, source and target
   environments, and the exact job-role scope. Require source and target to be
   distinct for a migration request; require explicit confirmation for a
   same-environment restore.
2. Confirm the exact task name and code with
   `shared.setup-export.task-level-export` and verify its current
   `CSVExportImportSupportedFlag` is `Y`. If the task is ambiguous, unavailable,
   or unsupported, record a catalog-mismatch diagnostic and stop.
3. Confirm the operator has Functional Setup Manager export access in the
   source and Data Loader import privileges in the target. Do not request or
   expose credentials, access tokens, or tenant secrets.
4. Record the source/target identities, task code, scope, and a redacted
   execution plan in the project workspace before any side effect.

## Individual custom-role operations

| Requested operation | Preparation and execution boundary |
| --- | --- |
| Create | Prepare a custom-role definition and explicit hierarchy or privilege membership rows using the verified template. |
| Update | Identify the existing custom role by exact code; change only the requested supported definition fields or memberships. |
| Redesign | Prepare an explicit before/after plan for the requested role, hierarchy and direct privilege changes. Use ADD for additions and REMOVE for requested membership removals. |
| Delete a hierarchy or privilege membership | Retain a row identifying the parent and member and set the documented membership action to REMOVE. Removing a CSV row is not a deletion operation. |
| Delete an individual role | Accept and scope the request, then confirm an explicit whole-role deletion operation in current Oracle guidance and the target's FSM import contract. Execute only if that operation is supported by Data Loader's selected FSM route. The existing role-definition template has no deletion-action column; do not invent DELETE, treat membership REMOVE as role deletion, or silently switch to browser, REST, SCIM or HDL. If no supported operation is established, record the operation-support gap and required next action. |

Creation, updates and redesign are intentional changes in the selected target;
they are not automatically same-environment restores. Preserve source metadata
and construct a new candidate before validation. Once validated, leave the
archive unchanged through the Data Loader approval and execution steps.

Do not edit or delete Oracle-seeded roles as if they were custom roles. Role
code changes, user provisioning and data-security-policy changes require an
explicit supported contract; this CSV route does not add or remove direct
data-security policies. Inherited data access can change when memberships change.

For deletion or removal, identify the exact affected role and memberships and
show the intended removal in the operation plan before Data Loader's approval
preview. Do not infer deletion from an omitted row, a blank value or a redesign
request. Keep template-export auto-authorization separate from actual role
mutations; Core Data Loader remains the authoritative import approval gate.

## Export Manage Job Roles

1. Route the export to `shared.setup-export.task-level-export` with task name
   `Manage Job Roles`, task code `ASXS_MANAGE_JOB_ROLES`, the source environment,
   and project ID.
2. Let that skill perform the task lookup, support-flag validation, export
   process creation, polling, download, and project export persistence. Do not
   substitute a template export for a data export.
3. Preserve the returned ZIP unchanged. Register its path, SHA-256, process ID,
   task identity, source environment, and export timestamp as the export record.
4. On an export timeout or failure, preserve the task code, process ID, last
   status, process log reference, elapsed wait, and next-check path. Do not
   start another export process automatically.

## Template-first import preparation

Read [FSM input preparation](../references/fsm-input-preparation.md) when the user needs help with the
template. Accept plain-language requirements, safely extract the package,
explain the columns and prepare the candidate; do not require the user to
understand or populate the CSV before work can start.


For user-specified custom role data, use the target environment's task-level
CSV template/spec package through `shared.setup-export.task-level-export`.
Template acquisition is not a migration or a same-environment restore.
Automatically authorize and execute the template/spec export needed to prepare
a user-requested role import; do not ask for a separate template-export approval.
This user-authorized exception applies only to `setupTaskCSVTemplateExports`
for the selected task and environment. It does not authorize populated data
exports, uploads, role imports, or retries after an uncertain POST outcome.
Retain identity, privilege, catalog, payload and audit checks, and leave actual
import approval to `core.data-loader`. Verify the template
supports every requested field and hierarchy reference; do not invent values,
columns, category codes or an IP-access encoding.

Oracle documents role code, name, description, category and all-IP-address
access in Functional Security Custom Roles, plus parent/member codes and
ADD/REMOVE operations in the hierarchy file. Direct data-security policies are
not included in this CSV route. Consult
[the Oracle CSV role contract](https://docs.oracle.com/en/cloud/saas/sales/oscus/export-and-import-of-custom-roles-role-hierarchies-and-role-to.html)
and [CSV package editing guidance](https://docs.oracle.com/en/cloud/saas/human-resources/ochus/manage-role-definitions-using-csv-file-packages.html).
The target's template and import validations remain authoritative for a new
role; catalog flags alone do not prove the complete supplied request is valid.
This workflow uses `core.data-loader` for execution, never browser creation.

1. Unless the user explicitly overrides this sequence, export the task first
   and provide that export as the import template before asking for import
   content. Explain that the template establishes the supported archive and
   file structure; it is not approval to import.
2. When the user provides an input file, compare it with the export template
   for file names, headers, column order, encoding, required values, and
   task-specific references. Help correct structural defects in a separate
   candidate file; preserve the supplied original and do not silently alter
   business values.
3. Give the user a concise change summary and identify any unresolved values
   or references. Use the corrected file only after it conforms to the export
   structure and has been assembled into a new candidate archive using the
   supported archive shape. That candidate is a new artifact and must pass the
   validation and approval gates below.
4. The user may override the export-first sequence, template choice, or
   proposed file corrections at any time. Honor that direction, while retaining
   the required task-identity, validation, and immediate import-approval gates.

## Validate the archive for import

1. Require the supplied archive to be a non-empty ZIP and bind its SHA-256 to
   task code `ASXS_MANAGE_JOB_ROLES`, source environment, and target environment.
2. Route setup-data validation to `shared.validation.setup-data-validator` and
   preserve the resulting validation evidence. Fail closed on archive-shape,
   task-identity, scope, catalog, environment, or privilege mismatch.
3. Do not alter, unpack-and-repack, merge, or otherwise transform the archive
   after validation. Any change invalidates the evidence and approval preview.

## Optional Risk and Security Checkup

After archive validation and before the Data Loader handoff, resolve the user's
choice for this candidate and target. This is part of `MJR.DESIGN_GATE`. The
checkup dependency and its BOSS privileges are conditional on opting in; they
must not block the declined path. Export-only and template-only requests do
not enter this import checkpoint.

Unless the user has already explicitly chosen for this candidate and target, ask:

> Would you like to run Risk and Security Checkup on the proposed role access before importing? It checks for sensitive access and toxic privilege combinations.

Wait for an explicit yes or no. Silence, an import request, or import approval
is not consent to this assessment. Reuse an existing explicit choice for the
unchanged candidate and target without asking again.

- **Yes:** Route to
  [Risk and Security Checkup](../../../../shared/common/security/risk-and-security-checkup/SKILL.md)
  (`shared.common.security.risk-and-security-checkup`) under the active project
  workflow, using the selected target environment. That skill owns input
  normalization, Core-delegated fresh BOSS metadata reads, assessment delivery,
  artifacts, diagnostics and token accounting. Complete its preflight before
  external reads; do not start direct HTTP, OAuth or hierarchy lookups here.
- **No:** Record `declined` and present **Security checkup: Not performed**.
  Continue to the normal Data Loader validation and approval workflow without
  executing the checkup, authenticating for it, or implying the roles are safe.

Assess the proposed resulting role access rather than treating change rows as
a complete final role. Apply the checkup's
[input contract](../../../../shared/common/security/risk-and-security-checkup/references/input-validation.md):
its job-role ZIP normalizer excludes hierarchy expansion and cannot establish
final membership from REMOVE rows without a baseline. For a delta or redesign,
require baseline and proposed resulting privilege evidence, including resolved
inherited access where relevant, supplied or obtained through an already
supported routed workflow. Do not invent effective access or add a live lookup
route. Preserve the checkup's supplied-input coverage limitations. Evaluate
roles independently unless explicit user/persona grouping is supplied.

Present completed findings and coverage gaps before the import preview. Keep
risk acceptance with the user; findings do not authorize automatic role changes
or create a second import-approval gate. If the selected assessment fails or
required evidence is unavailable, record `blocked` or `failed` with its
classified diagnostic and stop this handoff. The user may resolve the blocker
or explicitly decline the optional assessment and proceed with **Security
checkup: Not performed**; never silently skip it or report a clean result.

Persist an append-only `security_checkup_decision` in the declared project
decision location and register/update project state through the existing Core
services. Record task, candidate artifact reference, target, explicit choice,
status (`declined`, `completed`, `blocked`, or `failed`), input coverage, and
assessment/diagnostic artifact references when available. Keep Data Loader
session captures, hashes, previews and approval objects in its live process
according to its contract; do not serialize them into the decision record.

If remediation changes the archive, repeat archive validation and this choice
checkpoint for the new candidate; do not reuse the old assessment. A changed
target or assessment input likewise invalidates prior assessment evidence.
Choosing the checkup never approves an import. Core Data Loader retains its
single authoritative final preview and execution-approval workflow. Present
the checkup outcome separately before that preview without altering the
loader's required preview output.

## Import the validated archive

1. Complete the optional checkup checkpoint above: require an explicit decline
   or a completed assessment presented to the user for the unchanged candidate
   and target. Route the immutable validated archive to `core.data-loader` as an FSM,
   task-routed import. Provide the task context, target environment, archive
   SHA-256, and validation evidence.
2. Let `core.data-loader` complete its required source and API validation and
   produce its immutable approval preview. This skill must not bypass or replace
   the Data Loader route with a direct FSM API, UCM upload, REST call, CSV
   utility, or browser action.
3. Present the exact target environment, task code, archive name and SHA-256,
   validation result, and expected import impact. Stop before the first POST.
4. Proceed only after the user gives a separate, immediate approval for that
   immutable preview. `core.data-loader` revalidates the archive and owns the
   upload, initiation, process monitoring, and diagnostics.
5. Do not retry an upload, initiation, import, overwrite, or replacement
   process without a fresh approval. Preserve returned request IDs, process-log
   references, and redacted diagnostics in the project workspace.

## Failure handling

Classify failures as input validation, catalog mismatch, authorization,
transport/environment, Fusion API, process timeout, process failed, artifact
persistence, or approval blocker. Redact credentials, tokens, customer data,
and sensitive role configuration. For any ambiguity or unsafe path, record the
blocker and recommended next action, then stop.

## Setup Tasks

No setup tasks were supplied when this skill was generated.
