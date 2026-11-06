---
skill_id: "shared.common.security.risk-and-security-checkup"
name: "Risk and Security Checkup"
description: "Assess Fusion role sets across pillars for sensitive access and toxic combinations using runtime risk metadata; delegates authenticated BOSS reads to FSCR core services."
layer: "shared"
type: "assessment"
execution_mode: "assisted"
owner_team: "FSCR Shared Framework"
version: "2.0.1"
inputs:
  - "project_id"
  - "project_context"
  - "fusion_environment_context"
  - "assessment_scope"
  - "role_and_privilege_evidence"
  - "current_run_core_responses"
outputs:
  - "risk_and_security_checkup_report"
  - "risk_and_security_checkup_result"
  - "runtime_tree"
  - "sensitive_access_rules"
  - "toxic_combination_rules"
  - "generation_summary"
  - "evidence_gaps"
  - "remediation_recommendations"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
uses_core:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "core.project-mgmt.project-state-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.artifact-version-manager"
persists_project_state: true
token_usage_tracking:
  enabled: true
  granularity: "per_skill_run_and_artifact"
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
state_updates: ["reports", "validation_results", "token_usage_records"]
workspace_outputs:
  - artifact_type: "report"
    default_location: "project/{project_id}/artifacts/shared/common/security/risk-and-security-checkup/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/shared/common/security/risk-and-security-checkup/"
    versioning_policy: "append-only"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
applicability:
  industries: ["All"]
  countries: ["All"]
side_effects:
  - "Delegates read-only BOSS metadata retrieval to the core REST client when selected by the active workflow."
  - "Writes request plans, assessment artifacts, run records, and token usage to the selected project workspace."
required_privileges:
  - "BOSS read access to providedAccessAlgorithms, algorithmReferences, providedEntitlements, and entitlement accesses in the selected environment."
---


# Risk and Security Checkup

## Purpose

Assess caller-supplied complete Fusion role sets using metadata freshly retrieved from that environment's BOSS endpoints. This skill stores extraction and generation logic, never a static access-point tree or rule catalog.

## FSCR integration and execution boundary

Adapted from the caller-supplied version 2.2.6 macOS/Windows ZIP. This is a
cross-pillar shared assessment skill, not a catalog-backed functional area or setup task.
Read [the FSCR adaptation notes](references/fscr-adaptation.md) for the
repository-specific execution and dependency boundaries.
Reviewer group: FSCR Shared Framework owner, FSCR A-Team/core, Risk and Security SME, and QA.

Begin implementation work through
[the implementation router](../../../../router/implementation-router/SKILL.md).
Reuse the selected project and prior scope. If no project exists for a run,
create `draft_impl_project_<date>` from `project/_template`, inform the user,
and offer to rename it for the objective.

Python 3.10+ is required. The bundled extraction helper follows the same
Core-delegation pattern as Activate Algorithms: it prepares read-only request
manifests and interprets returned Core results. It never performs HTTP, OAuth,
token-cache work, or launches a Core client. The active workflow executes the
prepared requests through `core.fusion-api.rest-api-client` after the preflight
below. Do not substitute a direct HTTP client or the personal installed skill.

All durable inputs and outputs belong under
`project/{project_id}/artifacts/shared/common/security/risk-and-security-checkup/<request_id>/`;
Fusion exports belong under `project/{project_id}/exports/`. Never place
customer output in the skill folder. Validate source and destination paths and
use a new request directory to avoid overwriting an earlier assessment.
The command-line helpers enforce this exact path, match the request ID to its
directory, verify the selected `project-state.json`, and reject symlink escapes.

## FSCR environment and authentication context

Consume `fusion_environment_context` from the active implementation workflow;
it is framework context, not a new question or a field in the uploaded role data.
Like the [core REST client](../../../../core/fusion-api/rest-api-client/SKILL.md),
use the selected `core/auth/fusionEnv.properties`: `environment` identifies the
profile and `restBaseUrl` supplies the Fusion base URL. Do not construct a tenant
URL from a caller-provided host prefix or assume an `oc-test.com` suffix.
The local helper reuses the core `read_properties` function and binds the
canonical HTTPS origin to internal `environment` provenance. An existing
normalized request must match that origin; conflicting input fails closed.
CLI defaults use the shared properties path. A `--properties` override may only
represent the profile already selected by the active workflow, matching core
client behavior. Do not print the configuration file or copy it into artifacts.

Start authentication preflight from the selected
[`core/auth/fusionEnv.properties`](../../../../core/auth/fusionEnv.properties),
using Core's reader. Reuse `environment`, `restBaseUrl`, `clientId`,
`redirectUrl`, and `boss_scope` as the configured context for Core BOSS
authentication. Do not ask the caller to supply a checkup-specific environment
or re-enter configuration merely to run this assessment.

Distinguish missing configuration from missing independent OAuth trust. If
Core reports a missing or invalid `~/.fusionaim/oauth-trust.json` policy,
explain that the properties file was found and used, but the separate Core
trust prerequisite has not passed. Point the caller to the existing properties
file and the relevant keys (`restBaseUrl`, `environment`, `clientId`) when
handing off enrollment through Core OAuth's prescribed intake. Request only
the enrollment input Core requires; never imply that the assessment needs a
second configuration file. Properties alone do not establish OAuth trust:
do not create or replace the trust policy, bypass its checks, or infer approved
OAuth endpoints from this file. After Core enrollment/login succeeds, resume
the preserved assessment request through the declared Core BOSS route.

Before requesting enrollment, distinguish an absent policy from an unreadable
existing policy using sanitized Core diagnostics. A Windows sandbox identity
may differ from the owner of `~/.fusionaim`; in that case, use the approved
execution-permission mechanism to run Core as the owning user. Do not replace
the existing policy, change its ownership, relax its ACLs, or copy private
authentication files into the workspace to work around the identity mismatch.

Do not request an application username, password, or token. Authentication and
BOSS scope selection belong to
[core OAuth](../../../../core/auth/fusion-oauth-authentication/SKILL.md) and the
[core BOSS route](../../../../core/fusion-api/rest-api-client/references/boss-rest-api.md).
The evaluator does not require or persist a login username. `subjectUser` remains
optional assessment data for an explicit user-assignment grouping; it is not the
signed-in identity. If a future operation genuinely requires the signed-in user,
resolve it through core `GET /hcmRestApi/resources/11.13.18.05/selfDetails?fields=Username`
under the active workflow and keep it in memory. Never decode a token or accept a caller identity override.
No identity read is needed for offline normalization or evaluation.

For missing or inconsistent configuration, report the exact non-secret missing
field or environment mismatch and route setup guidance to
[FSCR Onboarding](../../../../core/getting-started/onboarding/SKILL.md).
Do not ask for a checkup-specific host or username or start a login as a fallback.

## Inputs and boundaries

Support persona/job-role design review, user-role assignment checks, and bulk
provisioning checks through the same evaluation contract. For each invocation,
read all supplied evidence, whether one file, multiple files, archive members,
sheets, sections, screenshots, or mixed readable formats. Consolidate by exact
role code within the applicable user/persona scope and produce validated JSON
before evaluation. When a user is specified, use the user and role code together
as the consolidation key; keep different users' resulting role sets separate.
Follow the [use-case-aware consolidation contract](references/input-validation.md#use-case-aware-consolidation)
for extraction, grouping, reconciliation, and final-input handling. This is
agent-assisted intake using suitable readers, not a universal parser script.

The request to assess supplied input authorizes local inspection and extraction
of its ZIP or other readable archives. Do not ask for separate approval or
confirmation to unzip input. Apply the archive safety and destination checks in
input validation; this authorization does not bypass project workflow gates or
authorize external operations.

Require complete role sets with role codes, names, and exact associated access-point codes, including resolved inherited access. Preserve support for any readable format and normalize per [input validation](references/input-validation.md). Preserve request IDs; generate `RSC-<UUID>` when absent. Treat the user-provided role evaluation file as the final and complete assessment input. Do not ask the caller to confirm completeness, inherited-access completeness, or whether the file is final. Assess the supplied access points without hierarchy expansion; this input assumption does not establish actual environment-wide access completeness. Request only genuinely missing required context or clarification of unreadable, malformed, or ambiguous values needed for correct evaluation. Do not infer privileges, expand role hierarchies, provision users, modify roles, or approve changes.

For an SSM/FSM job-role ZIP, read [job-role CSV normalization](references/input-validation.md#ssmfsm-job-role-csv-exports). Join the role and privilege-membership CSVs by exact role code, omit privilege names when not supplied, and exclude the hierarchy CSV. Treat the submitted membership CSV as complete and preserve roles with no membership rows as empty access-point arrays. Pass `--complete-privilege-information` automatically; do not request a separate declaration. Use `scripts/normalize_job_roles_zip.py` for this format. Evaluate every role listed in the submitted input, regardless of category; never ask whether to assess only GRC roles or all roles. Preserve source categories without filtering or relabeling non-job roles as job roles. Assess each exported role independently unless the caller supplies a user assignment or another explicit grouping; retain every role in the evaluation scope. A normalization-only request ends with the validated JSON; do not present risk findings before runtime evaluation.
The normalizer streams bounded ZIP members, rejects encrypted or linked entries,
and publishes `normalization-complete.json` last. Runtime evaluation rejects a
normalized directory whose marker is absent, mismatched, or fails digest checks.

## Mandatory runtime workflow

1. Inventory and read all submitted role evidence, unpacking archives safely when present. Consolidate exact role codes within the use-case/user/persona scope per input validation, then write normalized JSON with `requestId` and `roleSets`. Bind `environment` internally from the selected FSCR configuration as described below. Reconcile the JSON against every relevant source and validate the complete request in the project artifact location before preparing runtime reads.
2. For every assessment, use `scripts/run_checkup.py` to prepare runtime metadata reads, then execute each emitted GET through `core.fusion-api.rest-api-client` using its BOSS route. Save current-run Core evidence and resume with `--core-response` until retrieval is complete, as described in [runtime metadata extraction](references/runtime-metadata-execution.md). No static catalog, prior assessment metadata, direct authentication, or cross-environment fallback is allowed.
3. Generate the JSON tree and derive Rule-1 (one check per sensitive access point) and Rule-2 (all pairs across the two toxic entitlement dimensions) according to [design enforcement](references/design-enforcement.md). Counts are runtime-derived; do not enforce 90 access points, 41 sensitive checks, 126 toxic checks, or 167 total checks.
4. Evaluate every generated check per independent role set with exact case-sensitive matching. Deduplicate submitted codes for matching and preserve all contributing roles. Retain every matched check.
5. Export the exact generated sensitive and toxic rules used for evaluation, their runtime-derived counts, and the assessment in the caller's output location. Verify their request IDs, FSCR-derived environment, source digest, counts, and finding rule IDs agree. Present numbered points: #1 is the recommendation in bold with a normal-font evaluation summary and complete Rule-1/Rule-2 tables mapping each affected role to exact privileges, identified conflicts, conflict-count calculations, and remediation or documented-retention actions. Never omit Rule-1 results when explaining Rule-2. Result #3 (or the established artifacts point when coverage is absent) must link the generated JSON tree and state its runtime-derived algorithm, entitlement, access-point-occurrence, and unique access-point counts. Keep the established top-level numbering and conditional coverage/artifact behavior per [evaluation contract](references/evaluation-contract.md). Read [failure handling](references/error-handling.md) when a step fails. Never return a clean assessment on extraction or authentication failure.

## First completion response

Read and apply the [evaluation contract](references/evaluation-contract.md)
before delivering a completed assessment. Present the detailed Rule-1 and Rule-2
results directly in the first completion response in chat, including every
affected role, exact privilege code and runtime name, algorithm, conflict-count
calculation, and actionable remediation or documented-retention option.
Artifact links support these results; a summary and report link alone do not
complete delivery. Do not wait for the user to ask for the findings. Group shared
privilege dimensions to avoid repeating pairs only when every privilege, its
contributing role, and the complete matched-pair arithmetic remain explicit.
Honor an explicit user request for a summary-only or file-only delivery.

## Runtime metadata preflight and execution handoff

Before the first delegated read, verify the selected project state and request
workspace, bind the normalized role input to the selected FSCR environment,
verify the BOSS profile/scope and read privileges through the selected Core
workflow, confirm source metadata and output paths, and check for overwrite
conflicts. The six algorithm codes are metadata lookup identifiers, not FSM
setup-task catalog claims. No role mutation, publication, import, or ESS job is
part of this workflow. If identity, scope, privilege, metadata availability, or
workflow selection is missing or ambiguous, persist a classified blocker before
external execution. Login and a single cached-token refresh remain Core-owned.

Start or resume the assessment:

```powershell
python scripts/run_checkup.py --input "<prepared-role-request.json>" --output "<project-request-directory>/security_checkup_result.json"
```

Exit code `2` with `awaiting_core_responses` is an internal handoff, not a failed
assessment or a customer approval question. Execute the returned read requests
through Core, wrap each response per the reference contract, then rerun with
all collected `--core-response "<request-id>=<core-result.json>"` arguments.
Continue additional pages and dependency phases internally until the tree and
assessment are complete or a genuine blocker occurs. Never ask the consultant
to execute Core calls or assemble technical evidence files.

Use `--dry-run` to inspect the next read plan without writing files or calling
Fusion. `scripts/extract_tree.py` exposes the same planning/response interface
for a metadata-only request; its `--output` is the runtime tree path. Both
helpers delegate every external operation to Core. Keep each assessment in its
own directory; identifiers bind evidence to its request, environment, and run
directory. The assessment helper refuses to overwrite prior assessment outputs.
The request plan is intentionally refreshed as same-run results arrive.

Normalization-only mode remains available:

```powershell
python scripts/run_from_zip.py --zip "<source.zip>" --output-directory "<project-request-directory>" --normalize-only
```

Retain the exact runtime tree bytes, both generated rule exports, generation
summary, and result together. Verify request IDs, FSCR-derived environment,
source digest, counts, and finding IDs before delivery. Do not reuse exported
runtime metadata for a new assessment. The response-based extraction and end-to-end
handoff are tested with synthetic results; live endpoint availability and tenant
privileges must be verified by the authorized routed execution.

## Local tests

Runtime helpers live in `scripts/`; offline tests live in `tests/`, matching
the Activate Algorithms layout. Run the suite from the repository root:

```powershell
python -B -m unittest discover -s shared/common/security/risk-and-security-checkup/tests -p "test_*.py"
```

The standalone rule generator and evaluator also refuse existing output files.
Use a new destination to preserve earlier rule exports and assessment evidence.
Metadata handoffs and assessment publication serialize each request directory
with `.risk-and-security-checkup.lock`. Staging files are uniquely and
exclusively created; final tree, rule, summary, and assessment artifacts are
published without replacing existing files. Only the validated same-run Core
request plan may be refreshed. If a lock remains after interruption, confirm
that its process has stopped and preserve the run evidence before recovering
the lock; never remove the lock of a running assessment.

## Coverage and recommendations

Report unmatched codes in `accessPointsOutsideCatalog`. When any are present, emit this exact `securityCheckupMessage`, retaining recognized findings and `risk_found`:

Some submitted access points are outside the runtime catalog coverage. Review the reported findings and run Risk Management analysis for a complete security analysis at regular intervals before going live.

This coverage message applies whether or not recognized risks were found; it must not claim that no risks were identified. Explain that unmatched codes remain outside the runtime catalog coverage; this message does not certify the set. No findings means no match within the runtime-derived catalog using caller-supplied access points. Severity `high` remains an implementation default, not an API-derived value. The caller decides remediation and risk acceptance.



## Persistence, diagnostics, and recovery

Register durable reports and validation results using the core artifact registry,
update project state, and record every durable run under
`project/{project_id}/state/runs/`. Append token usage to the declared project
log and report measured or explicitly estimated input/output/total usage.
Follow artifact and skill-run schemas; require the prescribed decision before
updating an existing artifact. Keep customer data untracked and never persist
credentials or tokens.

Before local execution, validate input shape, source readability, environment
identity, request grouping, destination containment, and artifact conflicts.
Follow [error handling](references/error-handling.md). Missing or malformed
input is `input_validation`; incomplete or ambiguous runtime metadata is
`catalog_or_metadata_mismatch`; missing workflow or approval prerequisites are
`approval_blocker`; write failures are `artifact_persistence`. Classify delegated
Core 401 as `auth_expired_or_invalid`, 403 as `authorization_or_privilege`, and
other unsuccessful HTTP results as `fusion_api_error`. Bounded pagination
exhaustion is `process_timeout`. Persist status,
stage, failure class, sanitized message, next action, environment, artifact
references, and external IDs when present. Preserve partial results explicitly;
never report a clean assessment after retrieval or generation failure.
No polling or external retry is supported by this package. Do not retry
validation failures or overwrite earlier results. Resume after corrected input
or successful Core recovery, using a new request directory for a new assessment.
