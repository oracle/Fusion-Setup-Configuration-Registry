---
skill_id: "erp.risk-and-security.add-other-data-sources.add-epm-data-sources"
name: "Add EPM Data Sources Setup Task Guidance"
description: "Provides task-specific setup guidance for Add EPM Data Sources under the Add Other Data Sources functional area."
layer: "pillar"
pillar: "ERP"
offering: "Risk and Security"
functional_area: "Add Other Data Sources"
functional_area_code: "ORA_GTG_ADD_OTHER_DATA_SOURCES"
task_code: "ORA_GTG_ADD_EPM_DATA_SOURCES"
task_name: "Add EPM Data Sources"
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
  - "connector_type"
  - "connector_name"
  - "connector_setup"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
  - "seeded_connector_readiness"
  - "openapi_contract"
  - "operation_contract"
  - "connector_definition_payload"
  - "connector_definition_registration"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/risk-and-security/add-other-data-sources/add-epm-data-sources/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/risk-and-security/add-other-data-sources/add-epm-data-sources/current/"
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
  - "Reads seeded Data Integrator connector definitions through the approved Fusion BOSS REST client."
  - "May refresh the local BOSS OAuth token cache when required by the approved client."
  - "After explicit approval, can POST a Data Integrator connector-definition contract through the approved Fusion REST client."
  - "After connector-definition registration, presents the target connector setup page for the user to enter credentials. A later, user-requested status check validates the registered connector and completes the linked Run Book task when the requested scope includes connector configuration or task completion."
required_privileges:
  - "BOSS read access for Data Integrator connector definitions"
  - "Fusion REST access to create Data Integrator connector definitions"
---

# Add EPM Data Sources Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Add EPM Data Sources` under `Add Other Data Sources`.

## Setup Task Skill Contract

- task_code: `ORA_GTG_ADD_EPM_DATA_SOURCES`
- task_name: `Add EPM Data Sources`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Add EPM Data Sources` under `Add Other Data Sources`.

Extract `connector_type` and `connector_name` from the implementation prompt.
Accept only `EPM ARCS` or `EPM FCCS` as the connector type. If either value is
missing or ambiguous, stop and request clarification. Resolve the exact
`seeded_source_type_name` for the BOSS seeded-connector check from the parsed
connector type: `EPM ARCS` resolves to `EPM-ARCS`, and `EPM FCCS` resolves to
`EPM-FCCS`.

## Setup Task Metadata

- Task name: `Add EPM Data Sources`
- Task code: `ORA_GTG_ADD_EPM_DATA_SOURCES`
- Available: `Y`
- Export/import supported: `UNKNOWN`
- CSV export/import supported: `UNKNOWN`
- CSV export/import routing: `not catalog-supported`
- Data Loader import mode: `REST`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `UNKNOWN`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

Do not route CSV export work to `shared.setup-export.task-level-export` or CSV import work to `core.data-loader` unless live Fusion metadata or Oracle guidance confirms support. Use `shared.validation.setup-data-validator` only when a setup data artifact is available for review. Use `shared.validation.reference-data-validator` when the task depends on cross-pillar reference data.

## Preflight Checks

Before the seeded-connector query and any downstream OpenAPI generation, payload
preparation, preview, or connector-definition POST, verify all of the following:

1. `connector_type` is exactly `EPM ARCS` or `EPM FCCS`, `connector_name` is
   non-blank, and the resolved seeded source type is the matching catalog value
   (`EPM-ARCS` or `EPM-FCCS`). Stop and request clarification for missing or
   ambiguous values.
2. The intended Fusion target, approved BOSS or Risk Cloud client, required
   OAuth scope, and declared read/create privileges are available for the
   selected stage. Do not use a different endpoint, client, or target as a
   fallback.
3. The selected source manifest, generated OpenAPI document, and extracted
   operation contract have passed their documented validation before payload
   preparation.
4. Before preview, the payload is credential-free, contains only allowlisted
   connector setup fields, and has a valid target and endpoint. Before a POST,
   the persisted approval artifact's target, method, endpoint, payload, and
   digest must be unchanged and the user must have given explicit approval.
5. When durable project output is required, the initialized project workspace
   and declared artifact paths are available. Stop rather than writing outside
   the project workspace or overwriting an artifact without the required
   confirmation.

## Seeded Connector Readiness Gate

Before any OpenAPI generation, operation extraction, mapping, or connector
payload preparation, query BOSS through
`core.fusion-api.rest-api-client/scripts/boss-rest_client.py`:

```text
GET /api/boss/data/objects/ora/riskMgmtRisk/dataIntegration/v1/connectorDefinitions?$filter=creationStatus='COMPLETED' and connectorStatus='ACTIVE' and sourceTypeName='<seeded_source_type_name>'&$includeTotalItems=true&$limit=1&$fields=id
```

Resolve `seeded_source_type_name` dynamically from the selected connector type
(`EPM-ARCS` or `EPM-FCCS`). All other query parameters remain fixed. Use the
existing BOSS REST client to encode query parameters; no request body is needed:

```bash
python3 core/fusion-api/rest-api-client/scripts/boss-rest_client.py \
  /api/boss/data/objects/ora/riskMgmtRisk/dataIntegration/v1/connectorDefinitions \
  --method GET \
  --query "\$filter=creationStatus='COMPLETED' and connectorStatus='ACTIVE' and sourceTypeName='${seeded_source_type_name}'" \
  --query '$includeTotalItems=true' \
  --query '$limit=1' \
  --query '$fields=id' \
  --properties <boss-properties-file> \
  --output <seeded-query-response.json>
```

This read uses `boss_scope` and the separate local BOSS token cache through the
core REST API client. Apply the result rules in
[Reference Lookups](ora-resource/ora_reference_lookups.md):

- A successful response containing at least one record with an `id` confirms
  that the predefined data source for the selected source type is set up.
  Continue to OpenAPI preparation. The server filter establishes completed,
  active status; the projected record need not repeat those status fields.
- An empty `items` array means no ready predefined data source matched. Stop
  downstream preparation and ask the user to complete setup through the Fusion
  UI. It does not prove that no pending connector exists. Do not create a seeded
  connector, infer its ID, or send an authentication PATCH.
- A failed request, missing or malformed `items`, or a returned record without
  an `id` blocks readiness. `hasMore` or a total count alone cannot establish
  readiness. This is an existence check with `$limit=1`; no pagination or
  unique-match requirement applies after a matching record is returned.

## OpenAPI Connector Preparation

After seeded connector readiness is confirmed, select the source manifest from
the parsed `connector_type`, then supply that manifest to the generic procedure
in `references/generate-openapi-spec.md`.

| Parsed connector type | Source manifest |
|---|---|
| `EPM ARCS` | `references/epm-arcs-openapi-source-manifest.json` |
| `EPM FCCS` | `references/epm-fccs-openapi-source-manifest.json` |

After the generic procedure returns a validated OpenAPI JSON object, hand that
runtime result to `references/extract-operations.md`. Do not invoke mapping or
function generation unless the user explicitly requests those later workflows.

## Connector Definition Registration

Before preview or live execution, load the task-local
[`ora_error_handling.md`](ora-resource/ora_error_handling.md) and apply this
contract:

### Error Handling Contract

- **Failure classes:** classify failures as `input_validation`,
  `catalog_mismatch`, `auth_or_privilege`, `transport_or_environment`,
  `fusion_api`, `process_timeout`, `process_failed`, `artifact_persistence`,
  or `approval_blocker`. Persist the class with the stage and sanitized
  message.
- **Retry policy:** refresh a cached token once for a recoverable 401/403, then
  retry only the read-only BOSS query. Never retry connector-definition POST,
  UI credential submission, or another live mutation without a new explicit
  approval or an idempotency key. Do not retry after an uncertain POST result;
  verify read-only first.
- **Timeout policy:** do not wait for a UI callback or poll while the user is
  completing the connector page. Record the registration handoff as awaiting
  UI completion. On a later status check, make one read-only BOSS query and
  persist its sanitized status, HTTP status when available, target, connector
  ID, and next safe recheck path.
- **Diagnostic outputs:** persist the preview/registration/UI-handoff/verification
  skill-run record under `state/runs/`, register durable artifacts in the
  project artifact index, and write the verification result under the current
  EPM artifact directory. Include stage, status, failure class, target,
  connector ID, artifact references, and external identifiers when available.
- **Redaction rules:** never print or persist access tokens, refresh tokens,
  client secrets, private keys, token-cache contents, `authenticationDetails`,
  authorization codes, or full credential-bearing responses. Stderr and
  response summaries must be truncated and sanitized.
- **Approval gates:** preview and digest verification are mandatory before the
  connector-definition POST. A later user request to test, retry, change the
  target, or change the payload is not approval for the original mutation;
  rebuild the preview and obtain fresh approval. User confirmation that the UI
  data was entered and BOSS readiness are validation signals, not mutation
  approval.

When the user explicitly requests connector-definition creation after operation
extraction, prepare one runtime-only POST contract in the supplied shape:

```text
POST /api/risk-cloud/rc-tools-ms/dataintegration/v1/dataIntegratorConnectorDefinitions
```

Invoke it only through
`core.fusion-api.rest-api-client/scripts/fusion_rmc_rest_client.py` with the
configured Risk Cloud OAuth `rmc_scope`.

The registration runner passes the approval-bound payload as a body file and
requires an explicit properties file:

```bash
python3 core/fusion-api/rest-api-client/scripts/fusion_rmc_rest_client.py \
  /api/risk-cloud/rc-tools-ms/dataintegration/v1/dataIntegratorConnectorDefinitions \
  --method POST \
  --body-file <approved-payload.json> \
  --properties <risk-cloud-properties-file> \
  --output <registration-response.json>
```

After a successful registration, resolve the returned connector ID and have the
skill construct and present the target Fusion connector setup page for UI
credential entry:

```text
{restBaseUrl}/fscmUI/redwood/rc-dataintegration/rc-ai-datasource/connector-authentication?connectorId=<new_connector_id>&connectorType=EPM&assertionUserName=<url-encoded-assertion-user-name>&assertionKeyAlias=<url-encoded-assertion-key-alias>&assertionAudienceList=<url-encoded-assertion-audience-list>
```

The runner only submits the approved registration and returns the connector ID
and URL-encoded non-secret assertion fields in the setup URL; it does not open
a browser, start a callback listener, or poll BOSS. Record the connector ID and
handoff state in the skill-run record so this workflow can be resumed without a
new registration.

Immediately render this user-facing handoff, replacing the placeholders with
the resolved target and returned connector ID:

```text
## Connector Setup Required

Open this URL: <connector-setup-url>

Complete the required connector data in Fusion using the link above. Do not paste credentials or
authentication details into this conversation. When you are done, return here
and ask me to check the status.
```

Opening the page or the user's completion message is not proof of readiness.
Do not perform a status query until the user explicitly asks to check status.
On that request, use the existing BOSS REST client with a body file, explicit
properties file, and output file to query the exact returned connector ID and
source type. Require that exact connector to show `creationStatus: COMPLETED`
and `connectorStatus: ACTIVE`; multiple unrelated records or `hasMore: true`
do not satisfy this check. Persist the sanitized verification result under the
project artifact directory. If the connector is not ready, report its returned
sanitized status and offer a later status check; never replay the registration
POST.

### Run Book Completion Handoff

After the exact registered connector is verified as both `COMPLETED` and
`ACTIVE`, use `core.runbook` to complete the linked `Add EPM Data Sources` Run
Book task. This is the final declared step when the originating request asks to
create, configure, or complete the EPM data source; it is not performed for a
preview-only, readiness-only, or status-only request.

Resolve the active Run Book and the task using the initialized project's
persisted task context and the exact task code `ORA_GTG_ADD_EPM_DATA_SOURCES`.
Set the task status to `completed` and the completion percentage to `100`.
Persist the refreshed Run Book task detail alongside the connector verification
and record the completion result in the skill-run record. Do not infer a
completion from a source-type collection: only the exact new connector's
verified ready state qualifies.

If the Run Book task update fails or is indeterminate, preserve the successful
connector verification and record that the Run Book remains unchanged. Do not
retry the PATCH automatically; resume only through `core.runbook` with the
recorded task context and the applicable update authorization.

The body has a top-level `extractedData` object. Populate it with the extracted
`dataExtractionObjects` and `sourceEndPoints`, plus the required connector
header, `connectorSetup`, and `jobDefinition` fields from runtime task context.
For EPM ARCS or EPM FCCS, resolve both `sourceTypeName` and `sourceTypeCode`
from the parent functional area's `connector-source-types.json`. Use the
prompt's connector name.
Generate runtime reference values only when the contract requires them. Persist
them only inside the approval-bound payload artifact described below; never
reuse them outside that exact approval and submission workflow.

When OpenAPI cannot document connector setup values, delegate connector setup
resolution to
[references/connector-auth-config.md](references/connector-auth-config.md).
Do not duplicate that reference's configuration questions or precedence rules
in this main workflow. Follow its allowlisted-key, approved-local-source, and
missing-input procedure; do not infer values from Risk Cloud environment
authentication configuration.

Validate `hostUrl` and `accessTokenUrl` as HTTPS URLs and reject unknown keys.
Always require non-blank `assertionUserName`, `assertionKeyAlias`, and
`assertionAudienceList` alongside the base setup fields before assembling the
approval artifact.
Keep the resolved configuration in memory for the current run. It is separate
from sensitive authentication material and does not contain
`authenticationDetails`, a client secret, a bearer token, a refresh token, or a
private key. Credentials and authentication details are completed through the
Risk Cloud UI after connector registration.

Do not include credentials or
`authenticationDetails` in this contract.

### Connector-Definition Approval Protocol

This task uses the same two-turn approval boundary as Data Loader. The exact
credential-free payload is a durable, approval-bound project artifact rather
than an in-memory chat value.

1. After all readiness, operation, and payload validation succeeds, assemble
   the complete payload once and bind it to the resolved target base URL, HTTP
   method, and endpoint. Do not POST at this stage. Generate the following
   review files under the initialized project's
   `artifacts/pillars/erp/risk-and-security/add-other-data-sources/add-epm-data-sources/current/`
   directory in a new immutable `approvals/preview-<unique-id>/` subfolder using `run_epm_connector_definition.py preview --project-root <project-root> --target-url <fusion-base-url>`.
   The runner derives this directory and does not accept an artifact-directory override:
   - `epm-arcs-openapi.json` or `epm-fccs-openapi.json`
   - `connector-definition-approval.json` — approval version, canonical target URL, method, endpoint, resolved project workspace, digest, and the complete credential-free POST body
   - `connector-definition-approval.md` — user-facing review summary
   
   Open the Markdown summary and approval JSON in Codex, and provide direct
   Markdown links to every generated review file. The files are a durable,
   inspectable deliverable and must not contain credentials, client secrets,
   bearer tokens, refresh tokens, or `authenticationDetails`.
2. Render the following approval-required report in the conversation. Keep the
   full payload out of chat: it is already persisted in the protected,
   approval-bound `connector-definition-approval.json` artifact. Show the
   artifact link and its SHA-256 digest so the user can inspect the exact
   payload without flooding the conversation:

```text
## Connector Definition Approval Required

Target environment: <resolved Fusion base URL>
Operation: POST /api/risk-cloud/rc-tools-ms/dataintegration/v1/dataIntegratorConnectorDefinitions
Payload artifact: <link to connector-definition-approval.json>
Approval envelope SHA-256: <approval artifact digest>

Approve creation of this connector definition using the exact payload in the linked artifact?
```

The linked approval artifact contains the complete assembled `extractedData`
contract for this run, including generated extraction objects and endpoints,
resolved connector type/name/code, and permitted runtime connector setup
fields. It must exclude secrets and all prohibited fields listed above. Do not
print the payload inline in chat. Before execution, verify that the persisted
artifact digest, target, method, endpoint, and payload are unchanged.
3. Wait for a later clear, contextual affirmative. A request to test, prepare,
   generate, or preview is not approval. Any change to the target or payload,
   or a missing, changed, or digest-mismatched approval artifact, requires
   rebuilding and rendering a new approval report.
4. Immediately after approval, verify that the persisted target, method,
   endpoint, payload, and digest are unchanged. Invoke the approved Fusion REST
   client once using `connector-definition-approval.json` as `--approval-state`.
   Do not rediscover operations, regenerate
   the OpenAPI document, change reference values, or add mappings after
   approval.
5. Render a user-facing result that identifies the connector name, operation,
   HTTP result, and server request/connector identifier when Fusion returns
   one. On a timeout or uncertain result, stop and use a safe read-only
   verification path before any retry; a retry requires fresh approval.

Use the shared project-management contracts for durable evidence. The
orchestration layer, not the pillar runner scripts, must handle the complete
lifecycle: write one append-only skill-run record under
`project/{project_id}/state/runs/`, register newly written artifacts through
`core.project-mgmt.artifact-registry-manager`, update state through
`core.project-mgmt.project-state-manager`, and append token usage through
`core/project-mgmt/scripts/token_usage_logger.py`. Do not add a
pillar-specific audit or token-log helper. Runner scripts may write their
declared approval, registration, and validation-result artifacts and must
return sanitized stage results for orchestration. Run records must contain the
stage, status, sanitized inputs, outputs, artifact references, and failure
notes without secrets or token-cache contents. A failed stage records the
failed run and token usage, but must not be presented as a successful
validation artifact.

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

Use the parent functional-area skill `erp.risk-and-security.add-other-data-sources` for functional-area sequencing and scope decisions. When a platform run creates durable project artifacts, track token usage using the manifest policy; local OpenAPI generation and runtime handoff do not require project initialization.

### Approval envelope integrity

The EPM runner hashes the canonical version-2 approval envelope: target URL
(the environment identity), HTTP method, endpoint, resolved project workspace
path, and complete credential-free payload. The digest field itself is excluded.
Execution requires `--project-root <selected-project-root>` alongside
`--approval-state`, `--approve-digest`, and `--properties`. The selected workspace
must match the envelope, and the selected connection's `restBaseUrl` must match
the approved target immediately before dispatch. A changed envelope, changed
connection target, or legacy payload-only digest fails closed. Regenerate the
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
