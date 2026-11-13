---
skill_id: "cx.sales.sales-orchestration.sales-plays-and-content"
name: "Sales Plays and Content Guidance, Read, and Search"
description: "Answers source-backed questions about Sales Plays, content bundles or packets, salesPlayType, criteria, status, fields, content artifacts, translations, setup, lifecycle, agentic UI authoring prompts, Knowledge authoring and consumption, prerequisites, Security Console role provisioning, profile options, roles, privileges, permission groups, data security policies, BOSS API/query behavior, Content Intelligence, troubleshooting, import/export limits, write-support status, and help sources. Also lists, filters, classifies, and retrieves SALES_PLAY and CONTENT_BUNDLE records and performs the documented Content Intelligence semantic-read search with OAuth, authorization, retry, and diagnostic guardrails. Use for any Sales Plays and Content question, Fusion UI agentic-authoring prompt example, security-provisioning question, or read/search request; explain or classify unsupported Create/Update/Delete requests without generating a mutation payload or bypassing the routed workflow."
layer: "pillar"
pillar: "CX"
offering: "Sales"
functional_area: "Sales Orchestration"
functional_area_code: "CUSTOM_SALES_ORCHESTRATION"
task_code: "CUSTOM_SALES_PLAYS_AND_CONTENT"
task_name: "Sales Plays and Content"
parent_skill_id: "cx.sales.sales-orchestration"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "verification"
execution_mode: "hybrid"
owner_team: "CX sales pillar team"
version: "0.7.6"
inputs:
  - "implementation_objective"
  - "project_context"
  - "fusion_environment_context"
  - "acting_user_identity"
  - "sales_play_operation"
  - "sales_play_id"
  - "sales_play_type"
  - "sales_play_query"
  - "content_intelligence_question"
  - "content_intelligence_sales_play_id"
  - "sales_play_and_content_question"
  - "requested_answer_mode"
outputs:
  - "question_classification"
  - "sales_play_and_content_answer"
  - "operation_support_status"
  - "source_gap"
  - "sales_play_list"
  - "sales_play_detail"
  - "sales_play_type_summary"
  - "content_intelligence_result"
  - "content_intelligence_status"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/sales/sales-orchestration/sales-plays-and-content/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
oracle_supplied_guidance_files:
  - purpose: "Sales Play and content bundle read-operation input validation"
    location: "ora-resource/ora_input_validation.md"
  - purpose: "Sales Play environment and OAuth readiness"
    location: "ora-resource/ora_dependency_readiness.md"
  - purpose: "Sales Play list, get, content-accessor, and advanced-query lookup contracts"
    location: "ora-resource/ora_reference_lookups.md"
  - purpose: "Sales Play and content bundle read error handling and refusal rules"
    location: "ora-resource/ora_error_handling.md"
oracle_supplied_guidance_status:
  access_verification: "Effective access is established only by the requested LIST, GET, QUERY, or CONTENT_SEARCH call; role, permission-group, and data-security-policy membership remain unknown without authorized administrator evidence"
  boss_read_contract: "Verified against the 26C internal BOSS OpenAPI source; LIST type-filter and descending creation-sort query syntax are runtime-validated"
  content_intelligence_contract: "Developer-provided semantic-read POST contract for /api/knowledge-management/v2/contentIntelligence with fixed Sales Play connector and published-content filters, using the task-local Knowledge Management wrapper with the knowledge-management scope token selected from the regular scope property"
  sales_play_type_contract: "The salesPlays collection contains SALES_PLAY and CONTENT_BUNDLE records, distinguished by the salesPlayType attribute; content bundle and content packet are equivalent user-facing terms"
  security_contract: "Complete guidance includes the site profile option, predefined-role enablement, custom-role Security Console steps, three custom-administrator duties, setup-screen privilege, read/create/update/delete permission groups, All Rows security view, Knowledge authoring and end-user content data policies, synchronization procedures, and effective-access verification boundaries; this skill executes read operations only"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Oracle Fusion Cloud Applications 26C"
    - "Later releases after endpoint contract verification"
side_effects:
  - "Reads Sales Play and content-artifact setup data through Fusion BOSS REST APIs."
  - "Searches published Sales Play content through the Content Intelligence semantic-read POST endpoint."
  - "May refresh the managed external BOSS OAuth profile cache once after a cache-managed 401 or 403 response to LIST or GET; QUERY is not automatically retried."
  - "May refresh the managed external Knowledge Management OAuth profile cache once after a cache-managed 401 or 403 response to CONTENT_SEARCH."
required_privileges:
  - "ORA_ZBS_SALES_ADMINISTRATOR_JOB, or a custom job role with ORA_DR_FAI_GENERATIVE_AI_AGENT_RUNTIME_DUTY and ORA_ZCA_ACCESS_GROUPS_ENABLEMENT_DUTY"
  - "The custom job role also needs the documented operation-specific Sales Play permission groups and All Rows security view"
  - "ZCA_VIEW_SALES_PLAYS_PRIV for access to the Sales Plays setup screen"
  - "ORA_CSO_KNOWLEDGE_AUTHORING_DUTY plus the documented Sales Administrator Knowledge data security policies when the out-of-box Sales Administrator role cannot be assigned to a Knowledge authoring administrator"
  - "The acting Content Intelligence end-user role needs the documented Sales Play Consumer user-group and Sales Force Automation department access policies"
---

# Sales Plays and Content Guidance, Read, and Search

## Purpose

Answer source-backed questions about Sales Plays, content bundles or packets,
their artifacts, and Sales Play Content Intelligence. When the routed project
workflow selects a live read, list, filter, search, or retrieve records for
setup task `CUSTOM_SALES_PLAYS_AND_CONTENT`. The shared `salesPlays` collection
uses `salesPlayType` to distinguish both record types. Keep executable
operations strictly read-only, including Content Intelligence POST requests
whose documented purpose is search rather than mutation.

## Question and Execution Scope

Handle conceptual, model, lifecycle, setup, security, BOSS API, Knowledge
Management, Content Intelligence, live-read, troubleshooting, import/export,
write-support, and help-source questions. Use the response statuses in
`../references/sales-orchestration-question-routing.md` so every material part
is answered from source, clarified, routed, marked as a source gap, or refused
safely.

An explanatory question does not authorize authentication or a Fusion call.
Only these live operations are executable:

- list Sales Plays and content bundles or packets with bounded query
  parameters, optionally restricted by `salesPlayType`;
- get one Sales Play or content bundle by exact ID and report its
  `salesPlayType`;
- query Sales Plays, content bundles, and documented `salesPlayArtifacts` or `$translations`
  children with the semantically read-only `POST .../salesPlays/$query`
  endpoint;
- test published Sales Play content search for one exact question and Sales
  Play ID with the semantically read-only
  `POST .../knowledge-management/v2/contentIntelligence` endpoint.

Treat `CREATE`, `UPDATE`, `DELETE`, `PATCH`, `PUT`, and bulk-write requests as
unsupported. Treat every `POST` as unsupported except the exact documented
`salesPlays/$query` and `/api/knowledge-management/v2/contentIntelligence`
semantic-read endpoints. Do not build a mutation preview, request mutation
approval, or invoke a write endpoint. Data Loader does not currently support
the applicable BOSS REST endpoints. Write support may be introduced only after
that dependency is available and payload, article/artifact, translation,
identity, concurrency, idempotency, approval, retry, diagnostic, and recovery
behavior has passed a reviewed skill revision.

Do not route this task through FSM CSV export or import because both catalog
support flags are `N`.

## Sales Play Type Discriminator

Use the `salesPlayType` attribute as the only type discriminator for records in
the `salesPlays` collection.

| User-facing type | Accepted request wording | Canonical `salesPlayType` |
|---|---|---|
| Sales Play | sales play, sales plays | `SALES_PLAY` |
| Content bundle or packet | content bundle, content bundles, content packet, content packets, bundle, packet | `CONTENT_BUNDLE` |

Normalize an explicitly requested type to its canonical value. Reject any
other supplied `salesPlayType`. When the request refers to the collection
generally and does not distinguish a type, do not infer a value or add a type
filter; return both types within the requested bound and include
`salesPlayType` in the result.

For LIST or QUERY, preserve the normalized type as an exact `salesPlayType`
predicate. For GET, use only the exact record ID, then report the returned type
and treat a mismatch with an explicitly requested type as a type mismatch; do
not substitute another record. This discriminator does not change the fixed
Content Intelligence connector or filter contract.

## Required Read Order

Choose the read path from the user's intent.

For every question:

1. Read `../references/sales-orchestration-question-routing.md`.
2. Classify the subject, question classes, and answer mode before loading OAuth
   or execution resources.
3. Continue with only the task sources required by the selected classes.

## General Question Handling

- For a Sales Play definition, purpose, business value, collateral use, or
  design-scope question, read
  `references/sales-plays-and-content-overview.md`.
- For Fusion UI agentic authoring prompt examples, read
  `references/sales-plays-and-content-agentic-prompts.md` and follow its Prompt
  Emission Rules and content-source boundary. Emit concrete, synthetic,
  copy-ready prompts without user-replacement placeholders; treat them as UI
  guidance, not authorization for this skill to write through BOSS or REST.
- For type, field, status, criteria, artifact, translation, accessor,
  relationship, lifecycle, or BOSS API-capability questions, read
  `references/sales-plays-and-content-boss-read.md` and retain the
  `SALES_PLAY` versus `CONTENT_BUNDLE` distinction.
- For prerequisites, profile-option readiness, predefined-role enablement,
  custom-role provisioning, setup-screen access, roles, duties, privileges,
  permission groups, security views, Knowledge authoring, end-user content
  access, data security policies, or ESS synchronization, read
  `references/sales-plays-and-content-security.md`,
  `../references/security-console-role-provisioning.md`, and
  `../references/security-synchronization-processes.md` in full.
- For Content Intelligence concepts, request rules, access checks, result
  classifications, OAuth scope, or troubleshooting, read both
  `references/sales-plays-content-intelligence-read.md` and
  `references/knowledge-management-rest-api.md` as applicable.
- For input, dependency, lookup, filter, or troubleshooting questions, load only
  the applicable file under `ora-resource/` plus the relevant BOSS, Knowledge,
  or security reference.
- For import, export, bulk, Create, Update, Delete, activation, publication,
  archive, copy, article mutation, or another possible side-effect question,
  explain documented catalog and security prerequisites, state the Data Loader
  blocker, and return `UNSUPPORTED` for execution.
- For a question spanning Sales Motions, Data Capture Rules, or the wider
  functional area, route to `cx.sales.sales-orchestration` and preserve this
  skill's execution boundary.
- If the loaded sources do not establish a business definition, transition,
  validation, UI step, integration behavior, Knowledge response field, or
  release-specific fact, return `SOURCE_GAP` and identify the exact Oracle
  source or SME confirmation needed. Do not infer the answer from field names
  or prior chat history.

For a prerequisite, profile-option, predefined-role enablement, custom-role
provisioning, role, privilege, permission-group, or access question:

1. Read `references/sales-plays-and-content-security.md` in full.
2. Read `../references/security-console-role-provisioning.md` in full.
3. Read `../references/security-synchronization-processes.md` in full.
4. Return the complete security contract plus target-environment and shared
   OAuth readiness as technical prerequisites for a live read or content
   search.
5. Do not load API execution resources, authenticate, call Fusion, persist a
   project artifact, or submit an ESS job unless the user separately requests
   an authorized operation.

For a LIST, GET, or QUERY operation:

1. Read `ora-resource/ora_input_validation.md`.
2. Read `ora-resource/ora_dependency_readiness.md`.
3. Read `ora-resource/ora_reference_lookups.md`.
4. Read `references/sales-plays-and-content-security.md` and apply its Read row.
5. Read `references/sales-plays-and-content-boss-read.md`.
6. Read `ora-resource/ora_error_handling.md` before any live call.

For a CONTENT_SEARCH operation:

1. Read `ora-resource/ora_input_validation.md`.
2. Read `ora-resource/ora_dependency_readiness.md`.
3. Read `references/sales-plays-and-content-security.md` and apply the
   Content Intelligence end-user policies.
4. Read `references/knowledge-management-rest-api.md` for the task-local client,
   OAuth scope, cache, and endpoint boundary.
5. Read `references/sales-plays-content-intelligence-read.md` for the fixed
   request contract and result classifications.
6. Read `ora-resource/ora_reference_lookups.md` for the executable lookup.
7. Read `ora-resource/ora_error_handling.md` before the live search.

## Read Security Boundary

Use either:

- confirmed membership in `ORA_ZBS_SALES_ADMINISTRATOR_JOB`; or
- a custom job role containing both documented duty roles, the Sales Play read
  permission groups, and the `All Rows` security view.

For Knowledge article administration when the out-of-box Sales Administrator
role cannot be assigned, also require
`ORA_CSO_KNOWLEDGE_AUTHORING_DUTY` and the documented Sales Administrator
Knowledge data security policies.

For a Content Intelligence search, require the acting Sales Representative,
Sales Manager, Sales Administrator, or equivalent custom role to have access
to both the Sales Play Consumer user group and the Sales Force Automation
department.

Treat the documented role and permission groups as prerequisites, not proof of
the acting user's membership. Do not claim membership without authorized
administrator evidence.

A requested read operation may proceed as the effective access check. A
successful LIST, GET, QUERY, or CONTENT_SEARCH response proves access only for
that call.
HTTP 403 proves that the acting user lacks effective read authorization for
that request; it does not identify which role, privilege, permission group, or
security view is missing.

The security reference also documents the Create, Update, and Delete permission
groups so implementers can prepare custom roles. Those grants do not expand
this skill's executable scope.

## Security and Prerequisite Questions

When the user asks for Sales Play prerequisites, the permission-group profile
option, predefined-role enablement, custom-role provisioning, roles, duty
roles, privileges, permission groups, or access requirements, read
`references/sales-plays-and-content-security.md`,
`../references/security-console-role-provisioning.md`, and
`../references/security-synchronization-processes.md` in full and return all
of the following:

- the `ORA_ASE_SAS_INTEGRATION_ENABLED` Site profile-option requirement;
- the predefined Sales Administrator role permission-group enablement steps;
- the out-of-box Sales Administrator job role;
- both duty roles required on a custom job role and what each enables;
- the Knowledge authoring duty required for a custom administrator role;
- the setup-screen functional privilege;
- every Read, Create, Update, and Delete BOSS permission group;
- the `All Rows` security view requirement;
- every administrator Knowledge data security policy;
- both Knowledge content-consumption policies for Sales Representative, Sales
  Manager, and Sales Administrator end users;
- the custom-role steps for adding permission groups, security views,
  privileges, duty roles, and Knowledge data security policies;
- the one-time **Retrieve Latest LDAP Changes** procedure;
- the daily **Import User and Role Application Security Data** schedule; and
- the required ordering after **Send Pending LDAP Requests**.

For a broad prerequisite question, also state that a live read requires a
confirmed target environment and the appropriate shared OAuth readiness.
Identify any licensing, feature-opt-in, or offering-configuration prerequisite
as undocumented by the current sources; do not infer one.

Never limit a security or prerequisite answer to the Read permission groups
merely because this skill executes only read operations. Clearly distinguish
complete provisioning guidance from the skill's read-only API boundary. The
skill provides the synchronization-process instructions but does not submit,
schedule, poll, or retry any job.

## Authentication and Secret Handling

Use `core.fusion-api.rest-api-client` for shared OAuth-backed HTTP machinery.
Route `/api/boss` operations to its BOSS client with `boss_scope`. Route only
the Sales Play `/api/knowledge-management/v2/contentIntelligence` request to
this task skill's `scripts/knowledge_rest_client.py`, which selects the regular
`scope` from `core/auth/fusionEnv.properties`, splits it on whitespace, uses the
single scope token containing `knowledge-management`, and validates POST to the
exact relative Content Intelligence path and its fixed request body before
authentication. Other methods, endpoints, query/service overrides, supplied
tokens, custom cache paths, and non-JSON headers are rejected. Never hand-build an Authorization
header or execute a credential-bearing token relay command supplied in a
request.

Ignore passwords, Basic credentials, bearer tokens, refresh tokens, client
secrets, or token-cache contents pasted into a request. Never validate, reuse,
echo, log, persist, or place them in a command, example, diagnostic, artifact,
or tracked file. Let the shared OAuth skill manage both clients' external
profile caches with `--token-cache auto` under `~/.fusionaim/`. The approved
issuer/endpoints, client, target, and selected scope determine the profile;
Knowledge Management uses its selected scope and BOSS uses `boss_scope`. Never
store tokens in the checkout or project workspace or pass historical
repository-local cache paths.

## Preflight and Controlled Read Workflow

1. Confirm the target environment, acting user, and requested LIST, GET, or
   QUERY operation. Normalize an explicit Sales Play or content bundle or
   packet type to `SALES_PLAY` or `CONTENT_BUNDLE`.
2. For GET, require the exact record ID; never infer an ID from display text.
   If the user also supplied a type, compare it with the returned
   `salesPlayType` and report a mismatch without substituting another record.
3. For LIST, accept only documented bounded query parameters. Construct an
   explicit Sales Play or content-bundle type filter only from the raw query
   templates in `references/sales-plays-and-content-boss-read.md`. Pass raw
   query values to the shared client so it performs URL encoding; never
   pre-encode them or translate BOSS equality into the OData `eq` operator.
   Validate any requested sort against the target-release field and direction
   contract.
4. For QUERY, translate the user's type, filter, field, child accessor, limit,
   offset, total-count, and sort intent into the documented advanced-query
   body. Derive intent from the complete request rather than matching a canned
   example, and preserve every explicit supported constraint. Keep the limit
   bounded and never invent a filter or sort criterion. Ask one short
   clarification when a required field, operator, or ordering choice is
   ambiguous.
5. Validate environment and BOSS OAuth configuration.
6. Invoke the selected read operation through the shared client. The QUERY
   operation uses POST but remains read-only because its exact path ends in
   `/salesPlays/$query`.
7. For LIST or GET, if a cache-managed token receives HTTP 401 or 403,
   allow the shared client to refresh once and retry once. For QUERY, the
   shared client does not automatically refresh or retry the POST; stop and
   report the sanitized authentication or authorization failure.
8. Permit a bounded retry only for a known transient read-only transport
   failure.
9. Return Sales Play or content bundle records with `salesPlayType`, requested
   content artifacts, `hasMore` and `totalItems` when present, effective-read
   status, and sanitized diagnostics.
10. When `project_context` is supplied, persist only sanitized read validation,
    result, diagnostic, and token-usage records.

## Content Intelligence Search Validation Workflow

1. Confirm the target environment and acting end user.
2. Require one non-empty user question and one exact, non-empty Sales Play ID.
3. Confirm that the acting role has access to the Sales Play Consumer user
   group and Sales Force Automation department; treat membership as unknown
   without administrator evidence.
4. Read `references/sales-plays-content-intelligence-read.md` and construct its
   fixed body. Replace only the user question and Sales Play ID. Serialize the
   inner `userInput` object safely; never interpolate raw question text into
   JSON or shell syntax.
5. Invoke the exact Content Intelligence path through this task skill's
   `scripts/knowledge_rest_client.py`, which selects the scope token containing
   `knowledge-management` from the regular `scope` property and uses the shared
   managed external profile cache (`--token-cache auto`). Do not supply an
   Authorization header or explicit access token.
6. Permit the shared client to refresh its Knowledge Management OAuth cache and
   retry once after HTTP 401 or 403.
7. Return `WORKING_WITH_RESULTS`, `WORKING_NO_RESULTS`,
   `AUTHENTICATION_FAILED`, `AUTHORIZATION_FAILED`, `REQUEST_INVALID`, or
   `SEARCH_FAILED` using the reference's observed-result rules.
8. Report the sanitized response shape. Do not invent a response field,
   relevance threshold, or result-count meaning not present in the response.
9. When `project_context` is supplied, persist only sanitized validation,
   result, diagnostic, and token-usage records.

## API Contract

| Action | Method | Relative path |
|---|---|---|
| List | GET | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesPlays |
| Get | GET | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesPlays/{salesPlays_id} |
| Advanced query all | POST, read semantics | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesPlays/$query |
| Content Intelligence search | POST, read semantics | /api/knowledge-management/v2/contentIntelligence |

Use the exact target-release OpenAPI contract if it differs from this 26C
summary. Quote shell arguments containing `$en` or `$query`.

The canonical 26C OpenAPI paths include `$en`. A runtime-validated collection
path without that segment also succeeded. Keep the canonical path unless
target-specific evidence requires the shorter form, and do not change the path
merely because a query expression fails to parse.

## Inputs

- `implementation_objective`
- `project_context`
- `fusion_environment_context`
- `acting_user_identity`
- `sales_play_operation`: LIST, GET, QUERY, or CONTENT_SEARCH only
- `sales_play_id`: exact record ID required only for GET
- `sales_play_type`: optional type discriminator for LIST or QUERY, or expected
  returned type for GET; normalize only `SALES_PLAY` or `CONTENT_BUNDLE`
- `sales_play_query`: documented LIST parameters or QUERY body values
- `content_intelligence_question`: required only for CONTENT_SEARCH
- `content_intelligence_sales_play_id`: exact Sales Play ID required only for
  CONTENT_SEARCH
- `sales_play_and_content_question`: any explanatory, support, or execution
  question about Sales Plays, content bundles or packets, artifacts, or Content
  Intelligence
- `requested_answer_mode`: EXPLAIN, READ, CLARIFY, ROUTE, GAP, or REFUSE

## Outputs

- `question_classification`
- `sales_play_and_content_answer`
- `operation_support_status`
- `source_gap`
- `sales_play_list`
- `sales_play_detail`
- `sales_play_type_summary`
- `content_intelligence_result`
- `content_intelligence_status`
- `security_prerequisite_summary`
- `effective_read_access_result`
- `diagnostics`
- `skill_run_record`
- `token_usage_record`

## Failure and Retry Rules

Classify failures as input validation, catalog mismatch, authentication,
authorization or privilege, transport or environment, Fusion API, artifact
persistence, or unsupported operation. Use catalog mismatch when documented or
generated LIST query grammar differs from a runtime-validated target contract.

For LIST or GET, allow one cache-managed 401 or 403 refresh and retry through
the shared BOSS client. For QUERY, stop on 401 or 403 without automatically
refreshing or replaying the POST; a new requested read requires validation
after the authentication or authorization issue is resolved. For CONTENT_SEARCH,
allow the Knowledge Management wrapper to refresh and retry once. Retry a
known transient transport failure only within a bounded read-only retry policy.
Do not retry malformed requests or deterministic 4xx responses.

For any mutation request, return `UNSUPPORTED`, state that this skill revision
is read-only, and stop without previewing or calling Fusion. Do not classify
the exact `POST .../salesPlays/$query` or
`POST /api/knowledge-management/v2/contentIntelligence` semantic-read operation
as a mutation.

## Help Sources

- Public Sales Play and collateral overview:
  `references/sales-plays-and-content-overview.md`
- Fusion UI agentic authoring prompts: `references/sales-plays-and-content-agentic-prompts.md`
- Complete prerequisite and security matrix:
  `references/sales-plays-and-content-security.md`
- Step-by-step Security Console role provisioning:
  `../references/security-console-role-provisioning.md`
- Step-by-step security synchronization processes:
  `../references/security-synchronization-processes.md`
- Read endpoint and command patterns:
  `references/sales-plays-and-content-boss-read.md`
- Content Intelligence request, security gate, and result classification:
  `references/sales-plays-content-intelligence-read.md`
- Task-local Knowledge Management client, OAuth scope, and cache boundary:
  `references/knowledge-management-rest-api.md`
- Cross-task question classification and response contract:
  `../references/sales-orchestration-question-routing.md`

Use the parent skill `cx.sales.sales-orchestration` only for functional-area
scope and cross-task sequencing.
