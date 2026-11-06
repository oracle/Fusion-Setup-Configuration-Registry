---
skill_id: "erp.risk-and-security.add-other-data-sources.add-other-data-sources"
name: "Add Other Data Sources Setup Task Guidance"
description: "Provides task-specific setup guidance for Add Other Data Sources under the Add Other Data Sources functional area."
layer: "pillar"
pillar: "ERP"
offering: "Risk and Security"
functional_area: "Add Other Data Sources"
functional_area_code: "ORA_GTG_ADD_OTHER_DATA_SOURCES"
task_code: "ORA_GTG_ADD_OTHER_DATA_SOURCES"
task_name: "Add Other Data Sources"
parent_skill_id: "erp.risk-and-security.add-other-data-sources"
available_flag: "Y"
export_import_supported_flag: "UNKNOWN"
csv_export_import_supported_flag: "UNKNOWN"
dataloader_import_mode: "REST"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "hybrid"
owner_team: "ERP risk and security pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
  - "runbook_task_completion"
uses_core:
  - "core.fusion-api.rest-api-client"
  - "core.auth.fusion-oauth-authentication"
  - "core.runbook"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/risk-and-security/add-other-data-sources/add-other-data-sources/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/risk-and-security/add-other-data-sources/add-other-data-sources/current/"
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
  - "Reads Data Integrator connector definitions through the approved Fusion BOSS REST client for exact post-registration verification."
  - "After explicit approval, can POST a validated connector-definition payload through the approved Risk Cloud REST client."
  - "After the final connector-definition result is verified successful, can complete the linked Add Other Data Sources Run Book task through core.runbook when the originating request includes configuration or task completion."
required_privileges:
  - "BOSS read access for Data Integrator connector definitions"
  - "Risk Cloud REST access to create connector definitions"
---

# Add Other Data Sources Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Add Other Data Sources` under `Add Other Data Sources`.

## Setup Task Skill Contract

- task_code: `ORA_GTG_ADD_OTHER_DATA_SOURCES`
- task_name: `Add Other Data Sources`
- parent_skill_id: `erp.risk-and-security.add-other-data-sources`
- pillar: `ERP`
- offering: `Risk and Security`
- functional_area: `Add Other Data Sources`
- functional_area_code: `ORA_GTG_ADD_OTHER_DATA_SOURCES`
- available_flag: `Y`
- export_import_supported_flag: `UNKNOWN`
- csv_export_import_supported_flag: `UNKNOWN`
- dataloader_import_mode: `REST`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Add Other Data Sources` under `Add Other Data Sources`.

## Setup Task Metadata

- Task name: `Add Other Data Sources`
- Task code: `ORA_GTG_ADD_OTHER_DATA_SOURCES`
- Available: `Y`
- Export/import supported: `UNKNOWN`
- CSV export/import supported: `UNKNOWN`
- CSV export/import routing: `not catalog-supported`
- Data Loader import mode: `REST`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `UNKNOWN`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

Do not route CSV export work to `shared.setup-export.task-level-export` or CSV import work to `core.data-loader` unless live Fusion metadata or Oracle guidance confirms support. Use `shared.validation.setup-data-validator` only when a setup data artifact is available for review. Use `shared.validation.reference-data-validator` when the task depends on cross-pillar reference data.

## Hybrid Execution Preflight Checks

Complete these checks before the preview creates an approval artifact and repeat
the execution-specific checks immediately before the REST POST. Stop on any
failed, missing, or ambiguous check; do not use another client, endpoint, or
target as a fallback.

1. Confirm `project_context` resolves to an initialized FSCR project workspace
   when preview, execution, Run Book completion, or durable artifacts are in
   scope. Confirm the declared project artifact paths are writable without an
   unapproved overwrite.
2. Confirm the connector type has one valid local profile and a matching
   `sourceTypeName` and `sourceTypeCode` in `connector-source-types.json`.
   Confirm the documentation-backed OpenAPI input and extracted REST Operations
   pass their respective validation before payload generation.
3. Confirm the target is an explicit HTTPS Fusion base URL, the only mutation
   route is `POST /api/risk-cloud/rc-tools-ms/dataintegration/v1/dataIntegratorConnectorDefinitions`,
   and the approved Risk Cloud client, `rmc_scope`, and create/read privileges
   are available for the target environment.
4. Confirm the generated payload is credential-free, recursively rejects
   prohibited fields, uses only profile-allowlisted setup keys, and contains no
   undocumented setup values. Preview may write only review artifacts; it must
   not call Fusion.
5. Before execution, confirm a clear, contextual user approval exists for the
   exact persisted artifact. Recalculate the approval-envelope digest and require the
   target, method, endpoint, and payload to match the approval artifact.
6. Before execution, require `restBaseUrl` in the supplied properties file to
   equal the approval-bound target after URL normalization. The runner fails
   closed on mismatch before it writes a request body or sends the POST.
7. Before Run Book completion, confirm the exact registered connector is
   `COMPLETED` and `ACTIVE`, the project task context resolves the exact task
   code, and the originating request includes configuration or task completion.

## Failure Handling and Redaction

Classify every failure using the task-local
[`ora_error_handling.md`](ora-resource/ora_error_handling.md) contract. On an
input, catalog, target-binding, privilege, payload, or approval failure, stop
before the POST, retain only sanitized diagnostic metadata, and report the next
safe action. Refresh a cached token at most once for a recoverable 401/403
read-only check; never retry a connector-definition POST or an indeterminate
Run Book PATCH without fresh approval or an idempotency guarantee. On an
uncertain POST, use the declared read-only BOSS verification path before any
new preview.

Redact and never print or persist credentials, `authenticationDetails`, client
secrets, bearer or refresh tokens, private keys, complete authorization
headers, token-cache contents, or full untrusted response bodies. Persist only
the approved credential-free payload, digest, target, method, endpoint,
sanitized HTTP status, connector identifier, and next safe action in the
declared project artifacts.


## REST connector-definition workflow

This task uses the Risk Cloud REST connector-definition POST. It does not use
a Data Loader business object or Data Loader upload/initiation.

1. Resolve the connector type and load its profile from
   `connector-profiles/`. New connector types add a profile rather than a new
   orchestration branch. Resolve `sourceTypeName` and `sourceTypeCode` from
   the parent functional area's `connector-source-types.json`; do not accept
   either value as a task-local runtime input.
2. Use `references/generate-openapi-spec.md` to discover and validate the
   connector's OpenAPI JSON. OCI is a temporary, explicitly scoped exception:
   use the validated pinned document at `references/oci-openapi-spec.json` as
   directed by that workflow. For every other connector, if discovery cannot
   establish a usable, documentation-backed specification, stop and request
   the required documentation or clarification; do not use a local sample or
   fallback.
3. Use `references/extract-operations.md` to derive the complete `REST
   Operations` contract from the validated OpenAPI JSON. Keep both contracts
   in memory until preview creates the approval-bound payload artifact.
4. Convert the extracted operations into connector extraction objects and
   source endpoints, then build the connector-definition payload:

   ```bash
   python3 scripts/run_connector_definition.py format \
     --operations <rest-operations.json> \
     --output <formatted-operations.json>
   ```

5. Validate the complete credential-free payload, target environment, and
   endpoint before any write. Reject credentials, `authenticationDetails`,
   bearer tokens, refresh tokens, private keys, and undocumented setup keys.
   Persist the exact payload, canonical target URL, method, endpoint, resolved project workspace, approval version, and approval-envelope SHA-256 digest as an
   approval-bound project artifact. Do not POST during preview:

   ```bash
   python3 scripts/run_connector_definition.py preview \
     --operations <rest-operations.json> \
     --openapi-spec <discovered-openapi.json> \
     --profile connector-profiles/<connector-type>.json \
     --connector-name <connector-name> \
     --connector-setup-json <connector-setup.json> \
     --target-url <fusion-base-url> \
     --project-root <project-root>
   ```
6. After a later clear approval, execute the unchanged approval artifact once:

   ```bash
   python3 scripts/run_connector_definition.py execute \
     --approval-state <approval-state> \
     --approve-digest <approved-digest> \
     --project-root <project-root> \
     --properties <fusion-properties-file>
   ```

7. Return the sanitized HTTP result and server request/connector identifier.
   When an exact connector identifier is returned, present the connector setup
   page for the user to enter credentials:

   ```text
   {restBaseUrl}/fscmUI/redwood/rc-dataintegration/rc-ai-datasource/connector-authentication?connectorId=<connector_id>&connectorType=OCI
   ```

   Never retry an uncertain POST. Instead, use the exact read-only BOSS
   registration recovery query below to reconcile the original attempt.

### Predefined Data Source Readiness

Use the following GET through the approved BOSS client for predefined-source
readiness. Resolve `source_type_name` from the selected connector type in the
central registry; only this value is dynamic. The existing OCI prerequisite
applies to OCI; USER-DEFINED continues to skip that seeded-source prerequisite.

```text
GET /api/boss/data/objects/ora/riskMgmtRisk/dataIntegration/v1/connectorDefinitions?$filter=creationStatus='COMPLETED' and connectorStatus='ACTIVE' and sourceTypeName='<source_type_name>'&$includeTotalItems=true&$limit=1&$fields=id
```

```bash
python3 core/fusion-api/rest-api-client/scripts/boss-rest_client.py \
  /api/boss/data/objects/ora/riskMgmtRisk/dataIntegration/v1/connectorDefinitions \
  --method GET \
  --query "\$filter=creationStatus='COMPLETED' and connectorStatus='ACTIVE' and sourceTypeName='${source_type_name}'" \
  --query '$includeTotalItems=true' \
  --query '$limit=1' \
  --query '$fields=id' \
  --properties <boss-properties-file> \
  --output <seeded-query-response.json>
```

Use `boss_scope` and its separate local token cache. A successful response with
at least one record containing an `id` confirms the selected predefined data
source is set up. The server filter establishes readiness, so status fields
need not appear in the projected record. This is an existence check: no
pagination or unique-match requirement applies once a record is returned.

An empty `items` array means no ready match was found. Stop downstream work and
ask the user to complete setup in the Data Integration UI. It does not prove
that a pending connector is absent. A failed request, missing or malformed
`items`, or a record without an `id` blocks readiness. Neither `hasMore` nor a
total count alone proves setup.

### Connector Registration Verification and Recovery

The predefined-source query above does not verify a newly registered connector:
it can return an unrelated ready connector and it excludes unfinished records.
Never use its result to authorize recreation or Run Book completion.

After an uncertain POST or a user-requested post-setup status check, use the
approved BOSS client for a separate GET collection read filtered only by the
centrally resolved source type. Include unfinished records:

```bash
python3 core/fusion-api/rest-api-client/scripts/boss-rest_client.py \
  /api/boss/data/objects/ora/riskMgmtRisk/dataIntegration/v1/connectorDefinitions \
  --method GET \
  --query "\$filter=sourceTypeName='${source_type_name}'" \
  --query '$includeTotalItems=true' \
  --query '$limit=100' \
  --query '$fields=id,name,creationStatus,connectorStatus' \
  --properties <boss-properties-file> \
  --output <connector-verification-response.json>
```

The BOSS resource does not support `name` in its server-side filter; perform
name matching locally. Match the retained registration ID when available; otherwise select an exact
approved connector-name match locally. Require valid records and explicit
Boolean `hasMore=false` before deciding from this collection. Missing identity,
malformed results, `hasMore=true`, or multiple exact matches block recovery;
do not select arbitrarily or replay the POST. If the required read contract is
rejected by the service, report the contract gap and stop without a fallback.

- No exact match: the outcome remains unresolved. Keep the task open and retain
  sanitized diagnostics for read-only reconciliation. Do not infer that the
  original POST failed or rebuild a creation preview based on this result.
- One exact match not both `COMPLETED` and `ACTIVE`: present the existing
  connector's setup URL, keep the task open, and wait for setup and a later
  user-requested status check. Do not submit another registration.
- One exact match both `COMPLETED` and `ACTIVE`: verification succeeds; continue
  to Run Book completion only when the originating request includes it.

Persist only the exact connector ID, status fields, HTTP status, target and next
safe action. Any subsequent creation requires independent reconciliation of the
original attempt and fresh approval; neither query authorizes an automatic retry.

### Run Book Completion Handoff

After the final REST workflow result is verified successful, invoke
`core.runbook` to complete the linked `Add Other Data Sources` task. This step
applies when the originating request asks to configure or complete the task;
preview-only, readiness-only, and contract-only requests stop after their
declared result.

Resolve the active Run Book and the exact task code
`ORA_GTG_ADD_OTHER_DATA_SOURCES` from the initialized project's task context.
Set the task status to `completed` and completion percentage to `100`, then
persist the refreshed task detail and the update result in the skill-run
record. A successful HTTP response alone is not sufficient when the connector
registration result is uncertain or the required verification artifact is
missing.

If the Run Book PATCH fails or is indeterminate, preserve the successful REST
result, record that the Run Book task was not updated, and do not retry the
PATCH automatically.

The generic reference procedures are in `references/`: OpenAPI generation,
operation extraction, connector authentication configuration, mapping, and
function generation. They are connector-neutral and may be reused by every
profile.

The REST execution route owns approval immediately before the mutation. Do not
request a second Data Loader approval or upload a loader artifact.

## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `erp.risk-and-security.add-other-data-sources` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

### Approval envelope integrity

The runner hashes the canonical version-2 approval envelope: target URL
(the environment identity), HTTP method, endpoint, resolved project workspace
path, and complete credential-free payload. The digest field itself is excluded.
Execution requires `--project-root <selected-project-root>` alongside
`--approval-state`, `--approve-digest`, and `--properties`. The selected workspace
must match the envelope, and the selected connection's `restBaseUrl` must match
the approved target immediately before dispatch. Changed envelopes, mismatched
connections, and legacy payload-only approvals fail closed. Regenerate the
preview and obtain fresh approval; never upgrade an old approval in place.

### Retained approval previews

Each preview creates a new `current/approvals/preview-<unique-id>/` directory
containing its approval JSON and Markdown summary (and the EPM OpenAPI file
when applicable). Files are created exclusively and never replaced by another
preview. Existing files at the old fixed paths are left intact.

Only `current/latest-approval.json` is replaced atomically, after every file in
the new preview has been written successfully. It points to the latest preview
for discovery; it is not an approval artifact or an execution input. Link the
versioned files returned by the runner, retain the exact `approvalState` path
and digest that the user reviewed, and execute that path even if a later
preview changes the pointer. A later preview does not grant approval, revoke
an earlier approval, or authorize replay of a submitted operation.

### Artifact path and overwrite protection

Both connector runners use the functional-area `../scripts/connector_artifacts.py`
helper. Preview and execution artifacts must remain inside the selected initialized
project workspace. Symlinked artifact directories, approval files, payload files,
and current pointers are rejected, including links that point inside the workspace.
Directories are opened without following symlinks, and artifact files are created
exclusively with mode `0600`. Only the regular current pointer is replaced atomically.

Execution creates the derived `.payload.json` beside the approved versioned JSON.
If that destination already exists, execution stops before dispatch and preserves
the existing file. Do not delete it to retry a possibly submitted POST. Reconcile
the prior result through the documented recovery route; obtain a new preview and
approval only when a new submission has been established as appropriate.
