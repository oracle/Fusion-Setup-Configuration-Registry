---
skill_id: "erp.risk-and-security.assign-initial-users.assign-risk-power-user-role"
name: "Assign Risk Power User Role"
description: "Discovers current Risk process owners, prepares approved Risk Power User access requests, and verifies their outcome."
layer: "pillar"
pillar: "ERP"
offering: "Risk and Security"
functional_area: "Assign Initial Users"
functional_area_code: "ORA_GTG_RM_INITIAL_USERS"
task_code: "ORA_GTG_ASSIGN_RISK_POWER_USER_ROLE"
task_name: "Assign Risk Power User Role"
parent_skill_id: "erp.risk-and-security.assign-initial-users"
available_flag: "Y"
export_import_supported_flag: "UNKNOWN"
csv_export_import_supported_flag: "UNKNOWN"
dataloader_import_mode: "REST"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "orchestration"
execution_mode: "hybrid"
owner_team: "ERP Risk Management pillar team"
version: "1.1.9"
inputs: ["project_id", "fusion_environment_context", "poll_interval_seconds", "max_poll_wait_seconds"]
outputs: ["risk_power_user_receipt", "risk_power_user_exceptions", "runbook_lifecycle_result", "skill_run_record", "token_usage_record"]
depends_on: ["erp.risk-and-security.assign-initial-users", "core.auth.fusion-oauth-authentication", "core.fusion-api.rest-api-client", "core.project-mgmt.artifact-registry-manager"]
uses_core: ["core.auth.fusion-oauth-authentication", "core.fusion-api.rest-api-client", "core.project-mgmt.artifact-registry-manager"]
persists_project_state: true
token_usage_tracking:
  enabled: true
  granularity: "per_skill_run_and_artifact"
  artifact_type: "token_usage_record"
  default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
  estimation_method: "chars/4 estimate unless exact tokenizer or API accounting is available"
  required_fields: ["activity_start_time", "skill_id", "task", "trigger", "artifacts_written", "files_read", "estimated_input_tokens", "estimated_output_tokens", "estimated_total_tokens", "estimation_method", "notes"]
state_updates: ["validation_results", "reports", "token_usage_records"]
workspace_outputs:
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/risk-and-security/assign-initial-users/assign-risk-power-user-role/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "report"
    default_location: "project/{project_id}/artifacts/pillars/erp/risk-and-security/assign-initial-users/assign-risk-power-user-role/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
side_effects:
  - "Reads BOSS Risk Management process-owner configuration and Fusion SCIM users and roles."
  - "After fresh customer approval, submits one Advanced Access Request per eligible user who is not already assigned."
required_privileges:
  - "BOSS read access to Risk Management reference data and owner properties."
  - "Fusion SCIM read access and Advanced Access Request submit privilege for the OAuth identity."
---

# Assign Risk Power User Role

## Purpose

Assign the Risk Power User role to eligible current default `USER` owners
configured by **Assign Default Process Owners**. Do not infer owners and do not
modify process-owner properties.

## Consultant-facing behavior

Follow the offering [Consultant Interaction Contract](../../references/consultant-interaction-contract.md).
Present access status for eligible owners, exceptions, and completion in compact
Markdown tables. Use **Person**, **Affected process**, **Current
result**, and **Approval or next action** when applicable. The consultant
confirms a table or chat decision; do not ask them to inspect or approve request
bodies, identifiers, polling data, or JSON files.

## Usage

Use this skill when planning, sequencing, or validating the **Assign Risk
Power User Role** setup task under **Assign Initial Users**.

## Required upstream skill

Require the verified coverage result from the parent [Risk Administrator
Assignment Verification](../SKILL.md#risk-administrator-assignment-verification). Do not begin
Risk Power User discovery, planning, or access-request preparation until the
parent reports verified coverage for the selected project and environment.

## Core execution delegation

Prepare every Fusion or BOSS request in this skill and defer its execution to
`core.fusion-api.rest-api-client`; that skill's `SKILL.md` governs when its
Python client may run. Do not import, launch, or duplicate the Core client's
OAuth, token-cache, transport, retry, or response-processing behavior here.

Use [`scripts/transform_results.py`](scripts/transform_results.py) only after
the relevant Core results have been returned. It performs deterministic joins,
eligibility checks, and postcondition evaluation; it neither creates request
manifests nor calls Fusion. Its machine-readable input and output are internal;
use its Markdown table result when communicating with the consultant.

A successful, valid role response that omits `members` means no people are
assigned, just like `members: []`. Report “No people are currently assigned to
the Risk Power User role.” and continue the existing eligibility and approval
flow. An explicitly null or non-list `members` value remains invalid. Empty
membership does not verify provisioning or automatically complete this task.

## Authentication

Use `core.fusion-api.rest-api-client` for authentication and every Fusion
request. Never request, persist, or display a Fusion password, access token,
refresh token, or client secret. At the start of discovery, prepare this
Core-executed, read-only request to resolve the signed-in user:

```http
GET /hcmRestApi/resources/11.13.18.05/selfDetails?fields=Username
```

The returned `Username` is supplied by Fusion from the security token. It is
the only permitted requester identity for this workflow; do not present it for
confirmation or accept an override. Do not decode a token in this skill.

Before supplying `current_user` to the discovery transformer, accept either a
non-empty root `Username` or exactly one `items` entry with a non-empty
`Username` and `hasMore=false`. For the collection form, construct the
transformer's minimal root-shaped `current_user` input in memory. Treat zero or
multiple entries, pagination, malformed data, or a blank username as an
identity blocker. Do not persist or display the signed-in username or the
normalized identity object.

Prepare the matching authenticated-user resolution through:

```http
GET /hcmRestApi/scim/Users?filter=userName eq "<selfDetails Username>"&count=2
```

Its unique, active, case-insensitive SCIM `userName` match provides the `id`
used as `requestedByUserGuid`. If either authenticated-user result is missing,
ambiguous, inactive, or mismatched, stop before preparing any AAR submission.

## Execution

1. Prepare the signed-in-user request shown above. Normalize its valid
   root-shaped or collection-shaped result as described above, then derive the
   requester solely from that result; do not request consultant confirmation or
   an alternate username.
2. Prepare these read-only Core requests, using that authenticated username:

   ```http
   GET /api/boss/data/objects/ora/riskMgmtRisk/core/v1/referenceDataValues?$filter=referenceCode!='SOURCE.ORA.ORA' AND referenceCode!='SOLUTION.FND.ORA' AND attributeCode='PROCESSES.ORA'&$fields=valueCode,referenceCode,attributeCode,levelOne,levelTwo,levelThree,description&$sortBy=levelTwo:asc,referenceCode:asc&$limit=100&$offset=0
   GET /api/boss/data/objects/ora/riskMgmtRisk/core/v1/referenceDataValueProperties/$views/detailed?$limit=100&$offset=0&$sortBy=valueCode:asc
   GET /hcmRestApi/scim/Users?filter=userName eq "<selfDetails Username>"&count=2
   GET /hcmRestApi/scim/Roles?filter=name eq "ORA_GTG_RISK_POWER_USER_JOB"&count=2
   ```

3. Run the transformer with `--stage discovery`, `process_catalog_endpoint` set exactly to
   `/api/boss/data/objects/ora/riskMgmtRisk/core/v1/referenceDataValues`, and
   those results passed under their documented response IDs. If it returns `needs_role_membership`,
   prepare `GET /hcmRestApi/scim/Roles/<role_id>`. For each value in
   `needs_user_lookups`, prepare `GET /hcmRestApi/scim/Users/<user_id>`.
   Re-run discovery after those reads. It separates `candidates_requiring_decision`,
   `already_assigned`, and `ineligible` owners. If the first group is empty,
   finish with **No changes required**; do not ask for approvals or make further
   calls. Read each nonempty page while `hasMore=true`, advancing `$offset` by
   the returned page size; Boolean `hasMore=false` completes the inventory.
   This direct business object returns provided records only. Do not use the
   `allReferenceDataValues` union extraction, and stop if the declared direct
   source is not present. Stop if authenticated-user or role resolution is ambiguous.
4. Without prompting the customer, prepare a fresh role-membership read and a
   fresh SCIM user read for every `candidates_requiring_decision` entry. Run the
   transformer with `--stage preflight`. It returns only assignments that remain
   eligible at this final check. If it returns `awaiting_core_results`, perform
   its requested reads and re-run preflight.

   During discovery and preflight, immediately perform each required safe read
   and re-run the applicable transformer stage until it produces an approval
   table, verified no-change result, or genuine blocker. Do not end a response
   after an internal read, normalization step, or `awaiting_core_results`. In
   these read-only phases, an otherwise unspecified `continue` or `resume`
   request authorizes the outstanding reads only; it is not a person selection
   or approval. Once the approval table is ready, stop for the explicit approval.
5. Present the exact environment and target users as an approval table. Ask the
customer to select the entries to submit and state clearly that their response
is the **final approval** for the selected people and will immediately submit
only those requests; do not ask again. Retain every unselected eligible person
as a remaining candidate. A partial approval is never an implicit decision to
skip the other people. Retain the following body internally for execution:

```http
POST /fscmRestApi/resources/11.13.18.05/advancedAccessRequests/action/createAccessRequest
Content-Type: application/vnd.oracle.adf.action+json

{
  "requestedByUserGuid": "<requested_by_user_guid>",
  "requestedForUserGuid": "<user_guid>",
  "isTemporary": false,
  "justification": "Needed for role as business process owner",
  "requestAttributes": [{
    "roleCode": "ORA_GTG_RISK_POWER_USER_JOB",
    "securityContextId": "",
    "securityValueId": "",
    "OraGrcAssignAccess": "Y"
  }]
}
```

   Access requests are individual, never retried automatically, and never use
   bulk or PATCH.
6. Record each returned access-request ID with its user and process details.
   Before the first status read, record `poll_started_at` in UTC. Supply the
   positive, caller-approved `poll_interval_seconds` and
   `max_poll_wait_seconds` values, plus the UTC `observed_at` timestamp, to
   every `--stage poll` transformer input. The transformer returns
   `elapsed_wait_seconds` and, while work remains, a
   `next_check_after_seconds` value. For each returned
   `pending_aar_ids`, prepare:

   ```http
   GET /fscmRestApi/resources/11.13.18.05/advancedAccessRequestApprovals?q=AccessRequestId=<aar_id>&limit=2
   ```

   Re-run it only after the returned next-check interval. Never exceed
   `max_poll_wait_seconds`. When the transformer returns `timed_out`, stop
   polling and persist a redacted `process_timeout` diagnostic containing the
   environment, operation, AAR IDs, last known statuses, elapsed wait, and
   next-check guidance. Do not submit another request or continue polling
   without a fresh customer decision. When `needs_role_membership` is true,
   prepare a fresh `GET /hcmRestApi/scim/Roles/<role_id>`.
7. Run the transformer with `--stage verify` and that membership result. Do not
   mark a successful access request complete until its user is present in the
   verified role membership. Then prepare a fresh role-membership read and a
   fresh SCIM user read for every unselected candidate and every person whose
   submitted request was not verified. Run the transformer with
   `--stage continuation`, passing the verify `executions` as
   `verification_executions` and the unselected candidates as
   `remaining_candidates`.

   If continuation returns `awaiting_remaining_decision`, present the remaining
   table and ask a direct question that offers two paths: assign access to one
   or more listed people, or leave every remaining assignment unassigned and
   resume the runbook. Make clear that the second path records this task as
   complete with the remaining assignments skipped. Describe the available
   response intents—selected people, all remaining people, or moving on—without
   requiring literal wording. Each later approval covers only its selected
   people and requires the same fresh preflight. Treat an otherwise unspecified
   request to continue, a polling response, or a prior partial approval as
   ambiguous and re-present the table and question. If the consultant
   unambiguously chooses to skip remaining people and proceed, record
   `consultant_decision: SKIP_REMAINING_AND_PROCEED` internally and return its
   `completed_deferred` result to the calling runbook. The caller
   then runs its next eligible task, or finishes if none remains. Otherwise,
   return `completed_verified` only for `completed_all_resolved` or a verified
   no-changes-required outcome.
   An explicit request to defer and switch tasks records the outstanding people
   and returns `deferred`; it is not a skip decision. A failed, uncertain, or
   unverified submission or membership result returns `blocked`.
   Persist the readable receipt and exceptions after every batch.

The run creates a customer-controlled receipt plus redacted receipt, exception,
run-record, and token-usage artifacts under the project workspace.

## Core result ledger

Use these stable response IDs when passing returned data to the transformer.
They are internal workflow labels, not customer-facing content.

| Response ID | Core result |
| --- | --- |
| `current_user` | Signed-in user lookup. Its `Username` is the sole requester identity. |
| `process_catalog` | Direct BOSS `referenceDataValues` provided-process catalog; the union extraction is not eligible. |
| `properties` | BOSS default-owner properties. |
| `authenticated_user` | Exact active SCIM result for the signed-in user. |
| `role` | Risk Power User role SCIM result. |
| `role_members` | Current role membership; read again during preflight, verification, and continuation. |
| `user:<user_guid>` | A default owner, preflight candidate, or continuation candidate's SCIM result. |
| `poll:<aar_id>` | One Advanced Access Request status result. |

## Execution handoff

Invoke `core.fusion-api.rest-api-client` for each prepared discovery,
access-request, polling, and verification operation. Keep the returned IDs and
redacted responses in this skill's durable receipt; never run a pillar helper
as an alternate Fusion client.

## Preflight and failure handling

Before executing any Core request, verify the selected project workspace,
environment context, required prior owner configuration, request-plan/result
environment match, and the presence of every required Core response. Treat a
missing, inactive, ambiguous, or mismatched signed-in-user result as an
`auth_or_identity` exception; an ambiguous role as
`catalog_or_metadata_mismatch`; and a missing
or inactive owner as an actionable eligibility exception. Let the Core skill
handle its documented one-time authentication refresh for read failures.

Do not retry an access-request submission automatically. On a submission,
status, or membership-verification failure, persist redacted diagnostics and
the completed or partial receipt, then require fresh customer approval before
another submission attempt. The receipt distinguishes `verified`,
`remaining_pending_decision`, `resolved_without_change`, and
`skipped_by_explicit_consultant_decision`; only the final category permits the
runbook to move on while a person remains unassigned.
