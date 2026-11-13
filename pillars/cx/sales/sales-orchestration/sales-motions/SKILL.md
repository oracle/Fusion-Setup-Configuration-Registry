---
skill_id: "cx.sales.sales-orchestration.sales-motions"
name: "Sales Motions Guidance and Read Operations"
description: "Answers source-backed questions about Sales Motions, including purpose, setup, lifecycle and status, fields, objectives, high-value activities, agentic UI authoring prompts, relationships, prerequisites, Security Console role provisioning, profile options, roles, privileges, permission groups, API/query behavior, troubleshooting, import/export limits, write-support status, and help sources. Also lists, filters, and retrieves Sales Motions through read-only Fusion BOSS LIST, exact-ID GET, and semantic-read POST $query workflows with OAuth, authorization, retry, and diagnostic guardrails. Use for any Sales Motion question, Fusion UI agentic-authoring prompt example, security-provisioning question, or read request; explain or classify unsupported Create/Update/Delete requests without generating a mutation payload or bypassing the routed workflow."
layer: "pillar"
pillar: "CX"
offering: "Sales"
functional_area: "Sales Orchestration"
functional_area_code: "CUSTOM_SALES_ORCHESTRATION"
task_code: "CUSTOM_SALES_MOTIONS"
task_name: "Sales Motions"
parent_skill_id: "cx.sales.sales-orchestration"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "verification"
execution_mode: "hybrid"
owner_team: "CX sales pillar team"
version: "0.8.3"
inputs:
  - "implementation_objective"
  - "project_context"
  - "fusion_environment_context"
  - "acting_user_identity"
  - "sales_motion_operation"
  - "sales_motion_id"
  - "sales_motion_query"
  - "sales_motion_question"
  - "requested_answer_mode"
outputs:
  - "question_classification"
  - "sales_motion_answer"
  - "operation_support_status"
  - "source_gap"
  - "sales_motion_list"
  - "sales_motion_detail"
  - "security_prerequisite_summary"
  - "effective_read_access_result"
  - "diagnostics"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
uses_core:
  - "core.auth.fusion-oauth-authentication"
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
  - "validation_results"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/sales/sales-orchestration/sales-motions/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
oracle_supplied_guidance_files:
  - purpose: "Sales Motion read-operation input validation"
    location: "ora-resource/ora_input_validation.md"
  - purpose: "Sales Motion environment and OAuth readiness"
    location: "ora-resource/ora_dependency_readiness.md"
  - purpose: "Sales Motion list, get, and advanced-query lookup contracts"
    location: "ora-resource/ora_reference_lookups.md"
  - purpose: "Sales Motion read error handling and refusal rules"
    location: "ora-resource/ora_error_handling.md"
oracle_supplied_guidance_status:
  access_verification: "Effective read access is established only by a successful requested LIST, GET, or QUERY; role and permission-group membership remain unknown without authorized administrator evidence"
  boss_read_contract: "Verified against the 26C internal BOSS OpenAPI source"
  security_contract: "Complete guidance includes the site profile option, predefined-role enablement, custom-role Security Console steps, two custom-job-role duties, setup-screen privilege, read/create/update/delete permission groups, All Rows security view, synchronization procedures, and effective-access verification boundaries; this skill executes read operations only"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Oracle Fusion Cloud Applications 26C"
    - "Later releases after endpoint contract verification"
side_effects:
  - "Reads Sales Motion setup data through Fusion BOSS REST APIs."
  - "May refresh the managed external BOSS OAuth profile cache once after a cache-managed 401 or 403 response to LIST or GET; QUERY is not automatically retried."
required_privileges:
  - "ORA_ZBS_SALES_ADMINISTRATOR_JOB, or a custom job role with ORA_DR_FAI_GENERATIVE_AI_AGENT_RUNTIME_DUTY and ORA_ZCA_ACCESS_GROUPS_ENABLEMENT_DUTY"
  - "The custom job role also needs the documented operation-specific Sales Motion permission groups and All Rows security view"
  - "ZCA_VIEW_SALES_MOTIONS_PRIV for access to the Sales Motions setup screen"
---

# Sales Motions Guidance and Read Operations

## Purpose

Answer source-backed questions about Sales Motions and, when the routed project
workflow selects a live read, list, filter, or retrieve Sales Motions for setup
task `CUSTOM_SALES_MOTIONS`. Keep executable operations strictly read-only.

## Question and Execution Scope

Handle conceptual, model, lifecycle, setup, security, API, live-read,
troubleshooting, import/export, write-support, and help-source questions. Use
the response statuses in
`../references/sales-orchestration-question-routing.md` so every material part
is answered from source, clarified, routed, marked as a source gap, or refused
safely.

An explanatory question does not authorize authentication or a Fusion call.
Only these live operations are executable:

- list Sales Motions with bounded query parameters;
- get one Sales Motion by exact ID;
- query Sales Motions with the semantically read-only
  `POST .../salesMotions/$query` endpoint.

Treat `CREATE`, `UPDATE`, `DELETE`, `PATCH`, `PUT`, and bulk-write requests as
unsupported. Treat every `POST` as unsupported except the exact documented
`salesMotions/$query` read endpoint. Do not build a mutation preview, request
mutation approval, or invoke a write endpoint. Data Loader does not currently
support the applicable BOSS REST endpoints. Write support may be introduced
only after that dependency is available and payload, identity, concurrency,
idempotency, approval, retry, diagnostic, and recovery behavior has passed a
reviewed skill revision.

Do not route this task through FSM CSV export or import because both catalog
support flags are `N`.

## Required Read Order

Choose the read path from the user's intent.

For every question:

1. Read `../references/sales-orchestration-question-routing.md`.
2. Classify the subject, question classes, and answer mode before loading OAuth
   or execution resources.
3. Continue with only the task sources required by the selected classes.

## General Question Handling

- For a definition, purpose, business value, use case, strategy scope,
  objective, or high-value-activity question, read
  `references/sales-motions-overview.md`.
- For Fusion UI agentic authoring prompt examples, read
  `references/sales-motions-agentic-prompts.md` and follow its Prompt Emission
  Rules. Emit concrete, synthetic, copy-ready prompts without user-replacement
  placeholders; treat them as UI guidance, not authorization for this skill to
  write through BOSS or REST.
- For object-model, field, status, accessor, relationship, lifecycle, or
  API-capability questions, read
  `references/sales-motions-boss-read.md`. Return only facts established by the
  target-release contract.
- For prerequisites, profile-option readiness, predefined-role enablement,
  custom-role provisioning, setup-screen access, roles, duties, privileges,
  permission groups, security views, or ESS synchronization, read
  `references/sales-motions-security.md`,
  `../references/security-console-role-provisioning.md`, and
  `../references/security-synchronization-processes.md` in full.
- For input, dependency, lookup, filter, or troubleshooting questions, load only
  the applicable file under `ora-resource/` plus the relevant BOSS or security
  reference.
- For import, export, bulk, Create, Update, Delete, activation, archive, or other
  possible side-effect questions, explain the documented catalog and security
  prerequisites, state the Data Loader blocker, and return
  `UNSUPPORTED` for execution.
- For a question spanning Sales Plays, content, Data Capture Rules, or the wider
  functional area, route to `cx.sales.sales-orchestration` and preserve this
  skill's execution boundary.
- If the loaded sources do not establish a business definition, transition,
  validation, UI step, integration behavior, or release-specific fact, return
  `SOURCE_GAP` and identify the exact Oracle source or SME confirmation needed.
  Do not infer the answer from field names or prior chat history.

For a prerequisite, profile-option, predefined-role enablement, custom-role
provisioning, role, privilege, permission-group, or access question:

1. Read `references/sales-motions-security.md` in full.
2. Read `../references/security-console-role-provisioning.md` in full.
3. Read `../references/security-synchronization-processes.md` in full.
4. Return the complete security contract plus target-environment and shared
   BOSS OAuth readiness as technical prerequisites for a live read.
5. Do not load API execution resources, authenticate, call Fusion, persist a
   project artifact, or submit an ESS job unless the user separately requests
   an authorized operation.

For a LIST, GET, or QUERY operation:

1. Read `ora-resource/ora_input_validation.md`.
2. Read `ora-resource/ora_dependency_readiness.md`.
3. Read `ora-resource/ora_reference_lookups.md`.
4. Read `references/sales-motions-security.md` and apply its Read row.
5. Read `references/sales-motions-boss-read.md`.
6. Read `ora-resource/ora_error_handling.md` before any live call.

## Read Security Boundary

Use either:

- confirmed membership in `ORA_ZBS_SALES_ADMINISTRATOR_JOB`; or
- a custom job role containing both documented duty roles, the Sales Motion
  read permission groups, and the `All Rows` security view.

Treat the documented role and permission groups as prerequisites, not proof of
the acting user's membership. Do not claim membership without authorized
administrator evidence.

A requested read operation may proceed as the effective access check. A
successful LIST, GET, or QUERY response proves read access only for that call.
HTTP 403 proves that the acting user lacks effective read authorization for
that request; it does not identify which role, privilege, permission group, or
security view is missing.

The security reference also documents the Create, Update, and Delete permission
groups so implementers can prepare custom roles. Those grants do not expand
this skill's executable scope.

## Security and Prerequisite Questions

When the user asks for Sales Motion prerequisites, the permission-group profile
option, predefined-role enablement, custom-role provisioning, roles, duty
roles, privileges, permission groups, or access requirements, read
`references/sales-motions-security.md`,
`../references/security-console-role-provisioning.md`, and
`../references/security-synchronization-processes.md` in full and return all
of the following:

- the `ORA_ASE_SAS_INTEGRATION_ENABLED` Site profile-option requirement;
- the predefined Sales Administrator role permission-group enablement steps;
- the out-of-box Sales Administrator job role;
- both duty roles required on a custom job role and what each enables;
- the setup-screen functional privilege;
- every Read, Create, Update, and Delete BOSS permission group;
- the `All Rows` security view requirement;
- the custom-role steps for adding permission groups, security views,
  privileges, and duty roles;
- the one-time **Retrieve Latest LDAP Changes** procedure;
- the daily **Import User and Role Application Security Data** schedule; and
- the required ordering after **Send Pending LDAP Requests**.

For a broad prerequisite question, also state that a live read requires a
confirmed target environment and shared BOSS OAuth readiness. Identify any
licensing, feature-opt-in, or offering-configuration prerequisite as
undocumented by the current sources; do not infer one.

Never limit a security or prerequisite answer to the Read permission groups
merely because this skill executes only read operations. Clearly distinguish
complete provisioning guidance from the skill's read-only API boundary. The
skill provides the synchronization-process instructions but does not submit,
schedule, poll, or retry any job.

## Authentication and Secret Handling

Use `core.fusion-api.rest-api-client` and its BOSS client with `boss_scope`.
Never hand-build an Authorization header.

Ignore passwords, Basic credentials, bearer tokens, refresh tokens, client
secrets, or token-cache contents pasted into a request. Never validate, reuse,
echo, log, persist, or place them in a command, example, diagnostic, artifact,
or tracked file. Let the shared OAuth skill manage the external BOSS profile
cache with `--token-cache auto`. The cache is scoped to the selected OAuth
profile under `~/.fusionaim/`; never store tokens in the checkout or project
workspace or pass a historical repository-local cache path.

## Preflight and Controlled Read Workflow

1. Confirm the target environment, acting user, and requested LIST, GET, or
   QUERY operation.
2. For GET, require the exact Sales Motion ID; never infer an ID from display
   text.
3. For LIST, accept only documented bounded query parameters.
4. For QUERY, translate the user's filter, field, child accessor, limit,
   offset, total-count, and sort intent into the documented advanced-query
   body. Derive intent from the complete request rather than matching a canned
   example, and preserve every explicit supported constraint. Keep the limit
   bounded and never invent a filter or sort criterion. Ask one short
   clarification when a required field, operator, or ordering choice is
   ambiguous.
5. Validate environment and BOSS OAuth configuration.
6. Invoke the selected read operation through the shared client. The QUERY
   operation uses POST but remains read-only because its exact path ends in
   `/salesMotions/$query`.
7. For LIST or GET, if a cache-managed token receives HTTP 401 or 403,
   allow the shared client to refresh once and retry once. For QUERY, the
   shared client does not automatically refresh or retry the POST; stop and
   report the sanitized authentication or authorization failure.
8. Permit a bounded retry only for a known transient read-only transport
   failure.
9. Return records, `hasMore` and `totalItems` when present, effective-read
   status, and sanitized diagnostics.
10. When `project_context` is supplied, persist only sanitized read validation,
   result, diagnostic, and token-usage records.

## API Contract

| Action | Method | Relative path |
|---|---|---|
| List | GET | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesMotions |
| Get | GET | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesMotions/{salesMotions_id} |
| Advanced query all | POST, read semantics | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesMotions/$query |

Use the exact target-release OpenAPI contract if it differs from this 26C
summary. Quote shell arguments containing `$en` or `$query`.

## Inputs

- `implementation_objective`
- `project_context`
- `fusion_environment_context`
- `acting_user_identity`
- `sales_motion_operation`: LIST, GET, or QUERY only
- `sales_motion_id`: required only for GET
- `sales_motion_query`: documented LIST parameters or QUERY body values
- `sales_motion_question`: any explanatory, support, or execution question about
  Sales Motions
- `requested_answer_mode`: EXPLAIN, READ, CLARIFY, ROUTE, GAP, or REFUSE

## Outputs

- `question_classification`
- `sales_motion_answer`
- `operation_support_status`
- `source_gap`
- `sales_motion_list`
- `sales_motion_detail`
- `security_prerequisite_summary`
- `effective_read_access_result`
- `diagnostics`
- `skill_run_record`
- `token_usage_record`

## Failure and Retry Rules

Classify failures as input validation, authentication, authorization or
privilege, transport or environment, Fusion API, artifact persistence, or
unsupported operation.

For LIST or GET, allow one cache-managed 401 or 403 refresh and retry through
the shared BOSS client. For QUERY, stop on 401 or 403 without automatically
refreshing or replaying the POST; a new requested read requires validation
after the authentication or authorization issue is resolved. Retry a
known transient transport failure only within a bounded read-only retry policy.
Do not retry malformed requests or deterministic 4xx responses.

For any mutation request, return `UNSUPPORTED`, state that this skill revision
is read-only, and stop without previewing or calling Fusion. Do not classify
the exact `POST .../salesMotions/$query` operation as a mutation.

## Help Sources

- Public business overview and conceptual guidance:
  `references/sales-motions-overview.md`
- Fusion UI agentic authoring prompts: `references/sales-motions-agentic-prompts.md`
- Complete prerequisite and security matrix:
  `references/sales-motions-security.md`
- Step-by-step Security Console role provisioning:
  `../references/security-console-role-provisioning.md`
- Step-by-step security synchronization processes:
  `../references/security-synchronization-processes.md`
- Read endpoint and command patterns: `references/sales-motions-boss-read.md`
- Cross-task question classification and response contract:
  `../references/sales-orchestration-question-routing.md`

Use the parent skill `cx.sales.sales-orchestration` only for functional-area
scope and cross-task sequencing.
