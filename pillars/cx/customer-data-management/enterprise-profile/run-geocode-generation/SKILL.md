---
skill_id: "cx.customer-data-management.enterprise-profile.run-geocode-generation"
name: "Run Geocode Generation"
description: "Submits and monitors the Oracle Fusion Populate Location Latitude and Longitude Information ESS process for CX Customer Data Management. Use when a user asks to run, schedule, monitor, or resume geocode generation for eligible active and verified addresses."
layer: "pillar"
pillar: "CX"
offering: "Customer Data Management"
functional_area: "Enterprise Profile"
functional_area_code: "ORA_ASK_ENTERPRISE_PROFILE"
setup_task_code: "ORA_HZ_RUN_GEOCODE_LOADER"
setup_task_name: "Run Geocode Generation"
task_code: "ORA_HZ_RUN_GEOCODE_LOADER"
task_name: "Run Geocode Generation"
parent_skill_id: "cx.customer-data-management.enterprise-profile"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "import"
execution_mode: "hybrid"
owner_team: "CX customer data management pillar team"
version: "0.1.1"
inputs:
  - "execution_intent"
  - "execution_mode_selection"
  - "monitoring_choice"
  - "fusion_environment_context"
  - "country"
  - "country_code"
  - "start_date"
  - "end_date"
  - "regenerate_geocode"
  - "batch_size"
  - "requestId"
  - "execution_options"
  - "project_id"
outputs:
  - "execution_preview"
  - "ess_execution_result"
  - "diagnostics"
  - "skill_run_record"
  - "token_usage_record"
uses_core:
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
  - "reports"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/customer-data-management/enterprise-profile/run-geocode-generation/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/customer-data-management/enterprise-profile/run-geocode-generation/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "report"
    default_location: "project/{project_id}/artifacts/pillars/cx/customer-data-management/enterprise-profile/run-geocode-generation/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
oracle_supplied_guidance_files:
  - purpose: "Input modes and supported optional geocode parameters"
    location: "ora-resource/ora_input_intake.md"
  - purpose: "Environment, parameter, date, polling, and project-path validation"
    location: "ora-resource/ora_input_validation.md"
  - purpose: "Geocoding setup, address eligibility, privilege, and core-skill readiness"
    location: "ora-resource/ora_dependency_readiness.md"
  - purpose: "Country-code and shared ESS capability lookups"
    location: "ora-resource/ora_reference_lookups.md"
  - purpose: "ESS job, optional parameter, polling, batch, and retry defaults"
    location: "ora-resource/ora_defaulting_rules.md"
  - purpose: "Single-request and unsupported CSV or bulk behavior"
    location: "ora-resource/ora_bulk_intake.md"
  - purpose: "ESS payload mapping, preview, submission, polling, and resume contract"
    location: "ora-resource/ora_rest_execution.md"
  - purpose: "Process scope, parameter semantics, and result boundaries"
    location: "ora-resource/ora_design_advisory.md"
  - purpose: "Failure classification, disclosure, retry, and recovery"
    location: "ora-resource/ora_error_handling.md"
  - purpose: "Mandatory mode, environment, date, and one-POST gates"
    location: "ora-resource/ora_design_enforcement.md"
oracle_supplied_guidance_status:
  source_alignment: "Current Oracle Fusion Cloud documentation, internal HZ-HZGEOCODER metadata, and task-owner SME decisions from 2026-08-03"
  execution_contract: "Uses core.fusion-api.ess-job-submitter; no task-local REST, authentication, or polling implementation"
applicability:
  industries:
    - "All"
  countries:
    - "All countries configured for Fusion geocoding"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "When directly requested, submits the HZ-HZGEOCODER ESS process once to the selected Fusion environment."
  - "The process may update latitude and longitude on eligible HZ_LOCATIONS records and may spawn child processes."
  - "May refresh the local gitignored OAuth token cache through the invoked core skill."
required_privileges:
  - "Application Implementation Consultant role or a role containing the Run Geocode Loader privilege"
  - "Fusion ESS privileges required to submit and monitor HZ-HZGEOCODER"
---

# Run Geocode Generation

## Purpose

Run and monitor Oracle Fusion's `Populate Location Latitude and Longitude
Information` scheduled process for eligible active and verified addresses. The
setup task is `Run Geocode Generation`; its fixed ESS job is
`HZ-HZGEOCODER`.

## When to Use

Use this skill when the user asks to:

- run geocode generation with no optional parameters;
- restrict the run by country or location last-update date range;
- regenerate coordinates that are already populated;
- choose a batch size;
- monitor a submitted geocode request; or
- resume monitoring by an existing `requestId`.

This skill does not configure country geography structures, enable geocoding,
cleanse addresses, or import geography reference data.

## Inputs

- `execution_intent`: infer live authorization from a direct request to run
  geocode generation; advisory or hypothetical requests do not authorize a
  submission.
- `execution_mode_selection`: `parameterless` or `parameterized`. Infer
  parameterized when the user supplies filters. Otherwise resolve it with the
  user-friendly scope question before execution.
- `monitoring_choice`: `request_id_only` or `monitor_status`. Resolve this
  before preview and submission unless the user's request already states it.
- `fusion_environment_context`: required unless exactly one configured target
  can be resolved without ambiguity.
- `country`: optional country name, common country alias, or two-letter code.
  Resolve it to one documented country and `country_code` before submission.
- `country_code`: resolved two-letter Fusion geography code sent to ESS.
- `start_date` and `end_date`: optional paired inclusive date range. Accept
  Fusion UI-style `M/D/YY` or `MM/DD/YY`, and accept ISO `YYYY-MM-DD`; apply the
  range to the location last-update date. Always serialize ESS arguments as
  `YYYY-MM-DD`.
- `regenerate_geocode`: optional `Y` or `N`; the process default is `N`.
- `batch_size`: optional positive integer. Default is `50`; values above the
  SME-confirmed runtime limit are normalized to `100` and disclosed.
- `requestId`: optional existing ESS request to monitor. It is mutually
  exclusive with new-submission parameters.
- `execution_options`: optional positive `wait_seconds` and `poll_interval`.
- `project_id`: required only when the user explicitly requests durable project
  output or supplies a project ID. Its absence means a transient live run and
  must not trigger project-workspace creation.

All five business process parameters are optional. If none is supplied, run in
parameterless mode and let Fusion apply the scheduled process defaults.

## Outputs

- `execution_preview`: informational target environment, mode, normalized
  inputs, effective defaults, impact, and execution-intent state.
- `ess_execution_result`: request ID and terminal or last-known ESS status.
- `diagnostics`: redacted failure classification and recovery guidance.
- `skill_run_record` and `token_usage_record` when a project workspace is used.

## Ownership and Review

- Owner: CX Customer Data Management pillar team.
- Required functional reviewer: CX Pillar Development Lead or Geography SME.
- Required platform reviewer: FSCR A-Team/core reviewer.
- Required behavior reviewer: QA, including approval, privilege, retry, timeout,
  diagnostics, and redaction coverage for this hybrid skill.

## Read Order

1. Read [input intake](ora-resource/ora_input_intake.md).
2. Read [reference lookups](ora-resource/ora_reference_lookups.md).
3. Read [input validation](ora-resource/ora_input_validation.md).
4. Read [defaulting rules](ora-resource/ora_defaulting_rules.md).
5. Read [dependency readiness](ora-resource/ora_dependency_readiness.md).
6. Read [bulk behavior](ora-resource/ora_bulk_intake.md).
7. Read [design advisory](ora-resource/ora_design_advisory.md).
8. Read [design enforcement](ora-resource/ora_design_enforcement.md).
9. Before preview or execution, read [REST and ESS execution](ora-resource/ora_rest_execution.md)
   and [error handling](ora-resource/ora_error_handling.md).
10. Use [the compiled task registry](ora-resource/ora_rule_registry.json) as
    the task-local execution graph.

## Workflow

### 1. Resolve parameters naturally

Use one of:

- parameterless new submission;
- parameterized new submission; or
- tracking an existing `requestId`.

For a direct request such as "Run geocode generation" that does not already
specify filters or no-filter behavior, ask:

> Should I run geocode generation for all eligible addresses in countries where
> geocoding is enabled, or narrow it to a specific country or other filters?

Do not use the terms `parameterless` and `parameterized` in the normal user
prompt. Interpret "all eligible addresses" or "without filters" as
parameterless. Interpret a specific country, date range, regenerate option, or
batch size as parameterized. If the original request already resolves the
scope, do not repeat the question.

When the user asks to narrow or parameterize the run but has not supplied the
values, ask in plain language:

> You can optionally narrow the run. Send any values you want to use:
> - Country name or code, for example `India` or `IN`
> - Start and end dates like the Fusion UI, for example `8/4/26` and `8/6/26`
> - Regenerate existing coordinates: `Y` or `N`
> - Batch size; default and recommended is `50`
>
> Reply `none` to run all eligible addresses for geocoding-enabled countries.
> See [Oracle's parameter documentation](https://docs.oracle.com/en/cloud/saas/sales/fauss/populate-location-latitude-and-longitude-information.html#Parameters)
> for details.

Do not ask separately for omitted parameters because all five are optional. If
the user provides one date, ask only for the missing paired date. Normalize and
validate values after collection.

After mode and any parameters are resolved, but before previewing or submitting
a new request, ask when the monitoring choice is not already explicit:

> After submission, should I return the ESS request ID only, or monitor the
> status here?

Use `request_id_only` to submit once in the core skill's submit-only mode,
return the `requestId`, and end without polling. Use `monitor_status` to submit
once, return the `requestId`, and poll that same request using the configured
`wait_seconds` and `poll_interval`. Include the selected behavior in the
business-level execution summary. Do not choose a monitoring mode silently.

Do not combine `requestId` with fields for a new submission. Reject arrays,
CSV, spreadsheets, and multi-request input.

### 2. Resolve and validate the target

Bind the run to exactly one Fusion environment. Validate only the fields the
user supplied. Resolve a supplied country name, alias, or common misspelling
through `ora-resource/ora_reference_lookups.md`, then send only its normalized
uppercase two-letter code to ESS. Require both dates when either is supplied.
Parse UI-style `M/D/YY` or `MM/DD/YY` as a real calendar date, interpret a
two-digit year as `20YY`, accept ISO `YYYY-MM-DD` as already normalized, and
serialize both ESS date arguments strictly as ISO `YYYY-MM-DD`. Compare the
normalized dates and ensure the start date is not later than the end date.
Never pass slash-formatted dates to ESS. Perform this task-specific
normalization as part of the skill's validation and mapping workflow; do not
add task-local executable code or modify the shared ESS submitter.

Show the resolved country and code in the informational execution summary. If
the resolver corrected spelling, disclose it without asking for confirmation
when the match is uniquely high confidence. Ask a short clarification question
instead of submitting when the input is unknown or ambiguous.

Do not ask the user to confirm that geocoding is enabled for the intended
country or countries. Treat that configuration, along with active and verified
address status, as Fusion selection criteria rather than manual approval gates.
Disclose briefly that Fusion processes only eligible addresses in countries
already enabled for geocoding and that a successful request can legitimately
select no rows.

Let Fusion enforce the declared ESS privilege at submission and classify an
access rejection as `auth_or_authorization`.

### 3. Confirm execution intent without a second approval

Treat a direct imperative request to run geocode generation as authorization
for one submission after validation and readiness checks pass. Do not ask the
user to approve the environment, dependency, payload, or core skill again.
After the user answers any required scope and monitoring questions, continue
directly to one submission in the same flow. The execution preview is
informational and must not pause the flow. Never ask the user to reply
`Approve`, `Confirm`, or equivalent when the original request was a direct
imperative.

Before execution, give a short business-level update naming the environment,
whether optional filters are being used, and whether the skill will return only
the request ID or monitor status. If regeneration is `Y`, warn that already
populated coordinates may be processed again. Reveal the technical payload only
when the user asks for it. When dates are supplied, show their normalized ISO
values in the informational summary so the user can verify the effective range.

If the request is advisory, hypothetical, or ambiguous about whether to run,
stop before submission and ask one short execution-intent question.

### 4. Submit or monitor through the core ESS skill

Invoke `core.fusion-api.ess-job-submitter`; do not call Scheduler REST directly
and do not add task-local authentication or polling code.

For a new request, use the fixed job definition and mapping in
`ora-resource/ora_rest_execution.md`, including application `CrmEss`. Submit
exactly once with no automatic POST retry and capture the returned `requestId`.
When `monitoring_choice=request_id_only`, use submit-only mode and return
immediately. When `monitoring_choice=monitor_status`, poll the same request with
bounded defaults of `wait_seconds=300` and `poll_interval=10` unless valid
overrides are supplied.

For an existing `requestId`, use the core tracking path and never submit a
replacement request.

### 5. Report the outcome

On terminal success, report the environment, request ID, and terminal status.
State that the scheduled process completed; do not claim that every selected
address received coordinates.

On polling timeout, report that the process is still nonterminal, preserve the
request ID and last status, and resume the same request later. On failure,
return the failure class, available ESS status and ECID, and the recommended
next action. A new submission after failure requires a new direct run request.

## Persistence

When `project_id` is explicitly supplied or the user explicitly requests
durable project output, persist redacted validation, preview, request ID,
terminal or last-known status, diagnostics, skill-run, and token-usage records
under the manifest paths. Otherwise run transiently: do not create a draft
implementation project, audit workspace, run workspace, artifact, or
token-usage record, and do not pause submission for persistence approval.
Never persist credentials, bearer tokens, client secrets, token-cache contents,
private keys, or sensitive payloads.

## Error and Retry Policy

- Allow only the shared cached-token refresh behavior for a `401` or `403`.
- Never retry a new ESS `POST` automatically.
- Treat a missing request ID after POST as an uncertain outcome; do not
  resubmit.
- Treat a polling timeout as nonterminal and resume the same request ID.
- Classify failures using `governance/error-handling-guidelines.md`.

## Refusal Rules

- Do not submit without one exact environment and direct execution intent.
- Do not invent a country code outside the documented resolver or silently
  repair an ambiguous country or invalid date range.
- Do not default regeneration to `Y`.
- Do not submit again when Fusion rejects the required privilege.
- Do not issue more than one POST or replace an uncertain or timed-out request.
- Do not report success before a terminal successful ESS status.

## Golden Scenarios

| Scenario | Expected Result |
|---|---|
| User says "Run geocode generation" without stating scope | Ask whether to run for all eligible addresses in geocoding-enabled countries or narrow the run |
| User chooses all eligible addresses | Resolve parameterless, ask for monitoring behavior when missing, and submit once without a second approval prompt |
| User directly requests a run, then selects all addresses and monitoring | Show a short informational summary and submit immediately; never ask for `Approve submission` |
| No project ID or durable-output request is supplied | Run transiently without creating or requesting approval for a project workspace |
| User chooses all eligible addresses but has not confirmed country setup | Do not ask for setup confirmation; explain that Fusion automatically limits processing to eligible addresses in geocoding-enabled countries |
| User supplies one or more supported filters | Infer parameterized, validate the supplied values, and do not ask for omitted optional filters |
| User says `Australia` | Resolve and disclose `Australia (AU)`, then pass `AU` as submit.argument1 |
| User says `austraila` | Resolve the unique adjacent-letter spelling correction to `Australia (AU)`, disclose it, and pass `AU` |
| Country text has no unique high-confidence match | Ask the user to choose from the closest documented candidates; do not submit |
| User asks for filters but supplies none | Show the friendly parameter list and allow `none` to select parameterless execution |
| User does not state a monitoring preference | Before preview, ask whether to return only the request ID or monitor status here |
| User chooses request ID only | Submit once in submit-only mode, return the request ID, and end without polling |
| User chooses monitor status | Submit once, return the request ID, and poll that same request using the selected timeout |
| User supplies `US`, a valid date pair, `N`, and batch `50` | Use the normalized ordered values and submit once according to the selected monitoring behavior |
| User supplies batch `150` | Normalize to `100`, disclose the change, and continue under the original direct execution intent |
| User supplies only a start date | Stop as `input_validation` and request the end date |
| User supplies `8/4/26` through `8/6/26` | Accept the UI-style input, show `2026-08-04` through `2026-08-06`, and pass those ISO values as submit.argument2 and submit.argument3 |
| User supplies `08/04/26` | Never pass it unchanged to ESS; normalize it to `2026-08-04` |
| User supplies an invalid calendar date such as `2/30/26` | Stop as `input_validation`; do not submit |
| User supplies regeneration `Y` | Warn that already geocoded locations may be processed again before submission |
| User supplies an existing request ID | Monitor that request without a POST |
| Polling times out | Preserve the request ID and resume it later; do not submit again |

## Source Boundaries

- Process guidance:
  `https://docs.oracle.com/en/cloud/saas/sales/fauss/populate-location-latitude-and-longitude-information.html`
- Geocoding setup:
  `https://docs.oracle.com/en/cloud/saas/applications-common/26b/facia/set-up-geocoding.html`
- Scheduler REST contract:
  `https://docs.oracle.com/en/cloud/saas/applications-common/26c/farca/op-ess-rest-scheduler-v1-requests-post.html`
- Effective task catalog:
  `knowledge/setup-task-catalog/effective/setupTasksAll.json`

Use the parent skill
`cx.customer-data-management.enterprise-profile` for functional-area scope and
sequencing.
