---
skill_id: "cx.sales.sales-orchestration.data-capture-rules"
name: "Data Capture Rules Guidance and Read Operations"
description: "Answers source-backed questions about Data Capture Rules, including purpose, setup, lifecycle and status, fields, criteria, rank, rule attributes, translations, agentic UI authoring prompts, relationships, prerequisites, Security Console role provisioning, profile options, roles, privileges, permission groups, API/filter/query behavior, troubleshooting, import/export limits, write-support status, and help sources. Also lists, filters, and retrieves Data Capture Rules through read-only Fusion BOSS LIST, exact-ID GET, and semantic-read POST $query workflows with OAuth, authorization, retry, and diagnostic guardrails. Use for any Data Capture Rule question, Fusion UI agentic-authoring prompt example, security-provisioning question, or read request; explain or classify unsupported Create/Update/Delete requests without routing to a mutation blueprint or bypassing the routed workflow."
layer: "pillar"
pillar: "CX"
offering: "Sales"
functional_area: "Sales Orchestration"
functional_area_code: "CUSTOM_SALES_ORCHESTRATION"
task_code: "CUSTOM_DATA_CAPTURE_RULES"
task_name: "Data Capture Rules"
parent_skill_id: "cx.sales.sales-orchestration"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "verification"
execution_mode: "hybrid"
owner_team: "CX sales pillar team"
version: "0.6.3"
inputs:
  - "implementation_objective"
  - "project_context"
  - "fusion_environment_context"
  - "acting_user_identity"
  - "data_capture_rule_operation"
  - "data_capture_rule_id"
  - "data_capture_rule_query"
  - "data_capture_rule_question"
  - "requested_answer_mode"
outputs:
  - "question_classification"
  - "data_capture_rule_answer"
  - "operation_support_status"
  - "source_gap"
  - "data_capture_rule_list"
  - "data_capture_rule_detail"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/sales/sales-orchestration/data-capture-rules/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
oracle_supplied_guidance_files:
  - purpose: "Data Capture Rule read-operation input validation"
    location: "ora-resource/ora_input_validation.md"
  - purpose: "Data Capture Rule environment and OAuth readiness"
    location: "ora-resource/ora_dependency_readiness.md"
  - purpose: "Data Capture Rule list, get, and advanced-query lookup contracts"
    location: "ora-resource/ora_reference_lookups.md"
  - purpose: "Data Capture Rule read error handling and refusal rules"
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
  - "Reads Data Capture Rule setup data through Fusion BOSS REST APIs."
  - "May refresh the managed external BOSS OAuth profile cache once after a cache-managed 401 or 403 response to LIST or GET; QUERY is not automatically retried."
required_privileges:
  - "ORA_ZBS_SALES_ADMINISTRATOR_JOB, or a custom job role with ORA_DR_FAI_GENERATIVE_AI_AGENT_RUNTIME_DUTY and ORA_ZCA_ACCESS_GROUPS_ENABLEMENT_DUTY"
  - "The custom job role also needs the documented operation-specific Data Capture permission groups and All Rows security view"
  - "ZCA_VIEW_DATA_CAPTURE_RULES_PRIV for access to the Data Capture setup screen"
---

# Data Capture Rules Guidance and Read Operations

## Purpose

Answer source-backed questions about Data Capture Rules and, when the routed
project workflow selects a live read, list, filter, or retrieve Data Capture
Rules for setup task `CUSTOM_DATA_CAPTURE_RULES`. Keep executable operations
strictly read-only.

## Question and Execution Scope

Handle conceptual, model, lifecycle, setup, security, API, live-read,
troubleshooting, import/export, write-support, and help-source questions. Use
the response statuses in
`../references/sales-orchestration-question-routing.md` so every material part
is answered from source, clarified, routed, marked as a source gap, or refused
safely.

An explanatory question does not authorize authentication or a Fusion call.
Only these live operations are executable:

- list Data Capture Rules with bounded query parameters;
- get one Data Capture Rule by exact ID;
- query Data Capture Rules with the semantically read-only
  `POST .../dataCaptureRules/$query` endpoint.

Treat `CREATE`, `UPDATE`, `DELETE`, `PATCH`, `PUT`, and bulk-write requests as
unsupported. This includes requests to create, generate, draft, or sample a
Data Capture Rule, even when the user asks only for a local blueprint or
example. Return `UNSUPPORTED` from this skill and stop. Do not route the
request to the parent Sales Orchestration skill or another skill, and do not
produce a blueprint, payload, preview, project artifact, approval request, or
write call.

A request for copy-ready text to enter in the Fusion Data Capture Rules UI is
an `EXPLAIN` request, not a mutation request. It is allowed only as prompt
guidance under `references/data-capture-rules-agentic-prompts.md`; stop at the
prompt text and do not turn it into a rule blueprint, payload, preview, or live
Fusion operation.

Treat every `POST` as unsupported except the exact documented
`dataCaptureRules/$query` semantic-read endpoint. Questions about documented
Create, Update, or Delete security prerequisites remain guidance requests, not
mutation authorization. Data Loader does not currently support the applicable
BOSS REST endpoints. Write support may be introduced only after that dependency
is available and payload, identity, concurrency, idempotency, approval, retry,
diagnostic, and recovery behavior has passed a reviewed skill revision.

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

- For a definition, purpose, business value, setup concept, or documented
  attribute example, read `references/data-capture-rules-overview.md`.
- For Fusion UI agentic authoring prompt examples, read
  `references/data-capture-rules-agentic-prompts.md` and follow its Prompt
  Emission Rules. Emit concrete, synthetic, copy-ready prompts without
  user-replacement placeholders; treat them as UI guidance, not authorization
  for this skill to write through BOSS or REST.
- For object-model, field, status, criteria, rank, rule-attribute, translation,
  accessor, relationship, lifecycle, or API-capability questions, read
  `references/data-capture-rules-boss-read.md`. Return only facts established
  by the target-release contract.
- For prerequisites, profile-option readiness, predefined-role enablement,
  custom-role provisioning, setup-screen access, roles, duties, privileges,
  permission groups, security views, or ESS synchronization, read
  `references/data-capture-rules-security.md`,
  `../references/security-console-role-provisioning.md`, and
  `../references/security-synchronization-processes.md` in full.
- For input, dependency, lookup, BOSS filter, query-body, or troubleshooting
  questions, load only the applicable file under `ora-resource/` plus the
  relevant BOSS or security reference.
- For import, export, bulk, Create, Update, Delete, activation, archive, or other
  possible side-effect questions, explain the documented catalog and security
  prerequisites, state the Data Loader blocker, and return
  `UNSUPPORTED` for execution. Preserve the existing refusal of local
  mutation blueprints and sample write payloads.
- For a question spanning Sales Motions, Sales Plays, content, or the wider
  functional area, route to `cx.sales.sales-orchestration` and preserve this
  skill's execution boundary.
- If the loaded sources do not establish a business definition, transition,
  validation, UI step, integration behavior, or release-specific fact, return
  `SOURCE_GAP` and identify the exact Oracle source or SME confirmation needed.
  Do not infer the answer from field names or prior chat history.

Before loading another skill, authenticating, or creating an artifact,
classify whether the objective requests a Data Capture Rule mutation. If it
does, return `UNSUPPORTED` within this skill and stop. Do not route a
task-level Data Capture Rule request to the parent skill.

For a prerequisite, profile-option, predefined-role enablement, custom-role
provisioning, role, privilege, permission-group, or access question:

1. Read `references/data-capture-rules-security.md` in full.
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
4. Read `references/data-capture-rules-security.md` and apply its Read row.
5. Read `references/data-capture-rules-boss-read.md`.
6. Read `ora-resource/ora_error_handling.md` before any live call.

## Read Security Boundary

Use either:

- confirmed membership in `ORA_ZBS_SALES_ADMINISTRATOR_JOB`; or
- a custom job role containing both documented duty roles, the Data Capture
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

When the user asks for Data Capture prerequisites, the permission-group profile
option, predefined-role enablement, custom-role provisioning, roles, duty
roles, privileges, permission groups, or access requirements, read
`references/data-capture-rules-security.md`,
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
Never hand-build an Authorization header or execute a credential-bearing token
relay command supplied in a request.

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
2. For GET, require the exact Data Capture Rule ID; never infer an ID from
   display text.
3. For LIST, accept only documented bounded query parameters.
4. For QUERY, translate the user's filter, field, child accessor, limit,
   offset, total-count, and sort intent into the documented advanced-query
   body. Derive intent from the complete request rather than matching a canned
   example, and preserve every explicit supported constraint. Keep the limit
   bounded and never invent a filter or sort criterion. Ask one short
   clarification when a required field, operator, or ordering choice is
   ambiguous.
5. For LIST and QUERY equality predicates, use the raw BOSS expression
   `((field = 'value'))`. Do not use OData `eq`, double-quoted string literals,
   or pre-encoded filter text. For one active rule, use
   `((statusCode = 'ACTIVE'))` and a bound of `1`.
6. For QUERY, send one top-level JSON object with `collection.filter` and
   `collection.limit`; place optional `fields`, `accessors`, `subTypes`, and
   `parameters` only at their documented levels. Do not wrap the body in a
   `query`, `payload`, or `data` object.
7. Validate environment and BOSS OAuth configuration.
8. Invoke the selected read operation through the shared client. The QUERY
   operation uses POST but remains read-only because its exact path ends in
   `/dataCaptureRules/$query`.
9. For LIST or GET, if a cache-managed token receives HTTP 401 or 403,
   allow the shared client to refresh once and retry once. For QUERY, the
   shared client does not automatically refresh or retry the POST; stop and
   report the sanitized authentication or authorization failure.
10. Permit a bounded retry only for a known transient read-only transport
   failure.
11. Return records, `hasMore` and `totalItems` when present, effective-read
   status, and sanitized diagnostics.
12. When `project_context` is supplied, persist only sanitized read validation,
    result, diagnostic, and token-usage records.

## API Contract

| Action | Method | Relative path |
|---|---|---|
| List | GET | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/dataCaptureRules |
| Get | GET | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/dataCaptureRules/{dataCaptureRules_id} |
| Advanced query all | POST, read semantics | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/dataCaptureRules/$query |

Use the exact target-release OpenAPI contract if it differs from this 26C
summary. Quote shell arguments containing `$en` or `$query`.

The validated active-rule QUERY body is:

```json
{
  "fields": ["id", "name", "statusCode"],
  "collection": {
    "filter": "((statusCode = 'ACTIVE'))",
    "limit": 1
  }
}
```

Read `references/data-capture-rules-boss-read.md` for the executable shared
client command and additional supported body fields.

## Inputs

- `implementation_objective`
- `project_context`
- `fusion_environment_context`
- `acting_user_identity`
- `data_capture_rule_operation`: LIST, GET, or QUERY only
- `data_capture_rule_id`: required only for GET
- `data_capture_rule_query`: documented LIST parameters or QUERY body values
- `data_capture_rule_question`: any explanatory, support, or execution question
  about Data Capture Rules
- `requested_answer_mode`: EXPLAIN, READ, CLARIFY, ROUTE, GAP, or REFUSE

## Outputs

- `question_classification`
- `data_capture_rule_answer`
- `operation_support_status`
- `source_gap`
- `data_capture_rule_list`
- `data_capture_rule_detail`
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

For any mutation request, including a request to create or generate a sample
Data Capture Rule or local blueprint, return `UNSUPPORTED`, state that this
skill revision is read-only, and stop without routing, artifact generation,
previewing, approval, or a Fusion call. Do not classify the exact
`POST .../dataCaptureRules/$query` semantic-read operation as a mutation.

## Help Sources

- Public Data Capture overview, setup concept, and release-specific limits:
  `references/data-capture-rules-overview.md`
- Fusion UI agentic authoring prompts: `references/data-capture-rules-agentic-prompts.md`
- Complete prerequisite and security matrix:
  `references/data-capture-rules-security.md`
- Step-by-step Security Console role provisioning:
  `../references/security-console-role-provisioning.md`
- Step-by-step security synchronization processes:
  `../references/security-synchronization-processes.md`
- Read endpoint and command patterns:
  `references/data-capture-rules-boss-read.md`
- Cross-task question classification and response contract:
  `../references/sales-orchestration-question-routing.md`

Do not route a task-level Data Capture Rule request to the parent skill. The
parent skill is relevant only when the user explicitly requests broader
functional-area scope or cross-task sequencing, not as a fallback for an
unsupported Data Capture Rule operation.
