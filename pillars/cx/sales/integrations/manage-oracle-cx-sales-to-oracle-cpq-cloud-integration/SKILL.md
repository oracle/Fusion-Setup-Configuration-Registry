---
skill_id: "cx.sales.integrations.manage-oracle-cx-sales-to-oracle-cpq-cloud-integration"
name: "Manage Oracle CX Sales to Oracle CPQ Cloud Integration"
description: "Orchestrates the CX Sales-side FSM setup for embedded Fusion Application CPQ (FACPQ), including mandatory target-environment Sales and Configure Price Quote offering verification through versioned Fusion Features item GET requests, the IDCS OAuth-client CPQ-scope prerequisite, fresh Fusion OAuth login using the dedicated cpq_scope property in fusionEnv.properties, a host-only Sales integration endpoint, direct GET-only metadata discovery through <FA_HOST>/cpq/rest, fixed OpenID Connect action URL construction, task-level export/import routing, credential-safe package validation, and post-import verification; BM CPQ is out of scope."
layer: "pillar"
pillar: "CX"
offering: "Sales"
functional_area: "Integrations"
functional_area_code: "ORA_ZCA_INTEGRATIONS"
task_code: "ORA_ZCA_OSC_CPQ_INTEGRATION"
task_name: "Manage Oracle CX Sales to Oracle CPQ Cloud Integration"
parent_skill_id: "cx.sales.integrations"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "orchestration"
execution_mode: "hybrid"
owner_team: "CX sales pillar team"
version: "0.12.7"
inputs:
  - "implementation_objective"
  - "project_context"
  - "fusion_environment_context"
  - "facpq_environment_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "facpq_metadata_evidence"
  - "offering_opt_in_evidence"
  - "cpq_oauth_scope_configuration"
  - "authentication_references"
  - "execution_options"
outputs:
  - "setup_task_plan"
  - "offering_prerequisite_validation"
  - "facpq_metadata_manifest"
  - "fsm_export_result"
  - "sanitized_import_package"
  - "fsm_import_result"
  - "post_import_validation"
  - "diagnostics"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "cx.configure-price-quote.quoting.oracle-sales-to-quoting-integration"
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
uses_core:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "core.data-loader"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
oracle_supplied_guidance_files:
  - purpose: "Validate the Fusion host-only Sales integration endpoint, identifiers, fixed OpenID Connect URL values, and revenue-edit decision."
    location: "pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/ora-resource/ora_input_validation.md"
  - purpose: "Verify the required Sales and CPQ offering states through versioned Fusion Features item GET requests, then resolve FACPQ process, document, Copy action, and Version action metadata through <FA_HOST>/cpq/rest GET collections."
    location: "pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/ora-resource/ora_reference_lookups.md"
  - purpose: "Verify Fusion OAuth, FACPQ metadata, action URL, artifact, and import-approval dependencies."
    location: "pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/ora-resource/ora_dependency_readiness.md"
  - purpose: "Enforce the one-site design, five action URLs, exact identifiers, and secret-free artifacts."
    location: "pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/ora-resource/ora_design_enforcement.md"
  - purpose: "Classify lookup, authentication, FSM process, revision-mismatch, endpoint, and validation failures."
    location: "pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/ora-resource/ora_error_handling.md"
oracle_supplied_guidance_status: "Task-specific Oracle guidance is available."
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "Performs two target-environment GET-only offering checks through core.fusion-api.rest-api-client against the versioned Fusion Features item resource and writes only sanitized evidence to the selected project workspace."
  - "For live metadata discovery, reads the target-host Fusion OAuth cpq_scope property, passes its value directly to the shared OAuth helper for a fresh login, and may refresh only the authentication service's managed private cache outside the repository."
  - "Performs one Fusion-OAuth-authenticated documents GET and one dependent actionDefs GET under the selected Fusion host."
  - "May create Fusion task-level export and import processes through shared skills after required approvals."
  - "Writes sanitized implementation artifacts to an approved project workspace."
required_privileges:
  - "Fusion OAuth access to the target-environment versioned Features item resource under /fscmRestApi/resources/11.13.18.05/features/{FeatureCode}"
  - "The CPQ resource scope assigned to the target IDCS OAuth client and configured in the non-empty cpq_scope property of the selected Fusion OAuth properties file"
  - "Fusion OAuth access for the target host and read privilege for /cpq/rest Commerce document and action metadata"
  - "Fusion privileges to export, import, and review task ORA_ZCA_OSC_CPQ_INTEGRATION"
---

# Manage Oracle CX Sales to Oracle CPQ Cloud Integration

## Purpose

Configure and verify the CX Sales side of setup task
`ORA_ZCA_OSC_CPQ_INTEGRATION` for embedded Fusion Application CPQ (FACPQ).
Resolve identifiers through `<FA_HOST>/cpq/rest/...`, construct the FACPQ
OpenID Connect action URLs, and route Fusion setup data through existing shared
export, validation, and import skills. Do not route this skill to BM CPQ.

## Setup Task Skill Contract

- task_code: `ORA_ZCA_OSC_CPQ_INTEGRATION`
- task_name: `Manage Oracle CX Sales to Oracle CPQ Cloud Integration`
- parent_skill_id: `cx.sales.integrations`
- pillar: `CX`
- offering: `Sales`
- functional_area: `Integrations`
- functional_area_code: `ORA_ZCA_INTEGRATIONS`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Opportunity Routing

This skill is the canonical execution target for Oracle CPQ quoting and
Sales-side CPQ integration requests routed from the
[Opportunities functional-area skill](../../opportunities/SKILL.md). Treat that
route as an Opportunities-related capability while preserving this task's
catalog ownership under Sales → Integrations (`ORA_ZCA_INTEGRATIONS`); do not
add `ORA_ZCA_OSC_CPQ_INTEGRATION` to the native Opportunities setup-task list.

Return sanitized readiness, terminal status, blockers, artifact references,
and the safe next action to the Opportunities setup plan. Distinguish a
completed CX Sales-side configuration from unresolved CPQ-side administration,
which requires a CPQ-owner handoff.

## CX Sales-Only Execution Boundary

| In Scope | Read-Only Dependency Evidence | Out of Scope |
|---|---|---|
| CX Sales Order Instance fields, host-only Fusion integration endpoint, five FACPQ action URL parameters, Active selection, Restrict Revenue Edit decision, Sales-side export/import, and validation | Target-environment Sales and Configure Price Quote offering opt-ins, Fusion host identity, IDCS OAuth-client CPQ-scope assignment, and direct FACPQ document and action metadata GETs | BM CPQ instances, standalone BM CPQ login or credentials, BM CPQ browser sessions, CPQ administrative setup, and CPQ deployment |

A missing FACPQ prerequisite is a blocker, not authority to configure CPQ.
Never call BM CPQ or any CPQ mutation, setup, credential, or deployment endpoint.

## Conditional CPQ Task Handoff

When Configure Price Quote is in scope, complete this Sales task first, then
conditionally route the CPQ-side CRM and Generic Integration work to
`cx.configure-price-quote.quoting.oracle-sales-to-quoting-integration`.
When CPQ is not in scope, do not invoke that task. The referenced CPQ task owns
CPQ Integration Center administration, customer-managed credentials, and CPQ
vendor mutations; this Sales task retains its CPQ-administration boundary.

## Sales Integration Instance Verification

Do not ask an implementation user whether the Sales Integration Instance and
Actions exist. First invoke `shared.setup-export.task-level-export` in its
read-only path for `ORA_ZCA_OSC_CPQ_INTEGRATION`, then inspect the exported
configuration for the selected active/default Sales Order Instance, its host-only
endpoint, process/document identifiers, and the five generated action parameters:
Create, Edit, Copy, Version, and Proposal Download. Return a sanitized ready
result when those values match the fresh FACPQ metadata evidence.

If the task export is empty, the instance is absent, or one of those required
values differs, return a field-level gap report and continue by preparing an
immutable import preview. Ask for explicit approval only immediately before the
import, because that is the first Fusion mutation. If the read-only export is
not authorized, state the missing privilege and provide the Setup and Maintenance
navigation path; do not request a user assertion in place of evidence.

## Required Resource Loading

Before preview or execution, read the task-local resources relevant to the
request:

- `ora_input_validation.md` for required fields and blockers.
- `ora_reference_lookups.md` for the shared offering REST gate and scoped direct-OAuth metadata contract.
- `ora_dependency_readiness.md` and `ora_design_enforcement.md` before package
  approval.
- `ora_error_handling.md` before any live request, retry, import, or diagnostic.

## Execution Workflow

Run a preflight before every external action. Validate the target environment,
both offering opt-ins, privileges, catalog flags, OAuth scope configuration,
endpoint and package shape, destination paths, and the applicable approval
gate. Redact credentials, tokens, cookies, authorization codes, OAuth state,
Authorization headers, and sensitive payload values from every preview,
diagnostic, artifact, and user response.

1. Confirm both required offerings in the exact target environment through
   `core.fusion-api.rest-api-client`, using exactly these GET item paths:
   - Sales: `/fscmRestApi/resources/11.13.18.05/features/ORA_MIDSIZE_SALES`.
   - Configure Price Quote:
     `/fscmRestApi/resources/11.13.18.05/features/ORA_CONFIGURE_PRICE_QUOTE`.
   Build both URLs from the selected `<FA_HOST>`; never copy an example host
   into a reusable artifact. Require HTTP 200, the exact requested
   `FeatureCode`, `FeatureType=OFFERING`, and `EnabledFlag=Y` in each response.
   Do not replace this route with direct curl, a repository catalog snapshot,
   BOSS discovery, or UI-only evidence. If either item is absent, disabled,
   mismatched, unauthorized, or cannot complete safely, stop and return the
   remediation steps in **Offering Opt-In Remediation**.
2. Bind the run to exactly one Fusion host and one FACPQ commerce-process
   variable name. Reject a standalone BM CPQ host or a host value that already
   contains `/cpq`.
3. Preview `scripts/facpq_integration.py metadata` without `--execute`.
   Require a GET-only plan in this order: `/cpq/rest/.../documents`, then the
   selected document's `actionDefs`.
4. Before execution, read the selected Fusion OAuth properties through
   `core.auth.fusion-oauth-authentication` and require a non-empty `cpq_scope`
   property. Read its value directly; do not split or filter the standard
   `scope` property or use it as a fallback. Require the properties
   `restBaseUrl` origin to equal `--fa-host-url`. Pass the `cpq_scope` value
   to the shared OAuth helper as its runtime `scope` value in an in-memory
   copy; leave the properties file unchanged.
   Force one fresh target-host login, and pass the returned Fusion OAuth token directly
   to the documents GET. The Fusion OAuth response may be cached only in the
   authentication service's managed private cache outside the repository; never place that cache
   under `project/`. Use that same returned OAuth token for `actionDefs`.
   A successful fresh login and documents GET verifies the effective configured OAuth
   client, `cpq_scope`, and FACPQ read privilege. Treat HTTP 401 or 403 from either
   metadata GET as a terminal auth/authz failure for the run; provide the **OAuth Client
   Scope Remediation** below before starting a new login. Do not call
   `/api/rwdtools/tokenrelay`, accept another bearer, reuse BM CPQ credentials,
   or use browser cookies. Select one Main Document and one Copy and Version
   action; fail closed on ambiguity or conflicting evidence.
5. Ask only for selectors listed in `required_user_inputs`. The FACPQ action
   contract does not require a commerce-process `version_id` or Edit action ID.
6. Require `status: ready`, then run
   `scripts/facpq_integration.py action-urls` to construct and validate the
   fixed OpenID Connect Create, Edit, Duplicate, Version, and Proposal Download
   values.
7. Export the target Fusion task with `shared.setup-export.task-level-export`.
   Inspect every CSV for embedded credentials before retaining or transforming
   the package; quarantine unsafe raw exports outside the project workspace.
   Use only the authentication route declared by those shared workflows; never
   add BM CPQ credentials or browser-session artifacts to the package.
8. Build a credential-free package and validate setup/reference data. Before
   import approval, show every field of the proposed new Sales Order Instance:
   reference code, name, description, endpoint, document/process/REST values,
   revenue policy and reconciliation option, active/default flags, mapping and
   legacy-row behavior, all five action parameter names and complete generated
   action URL expressions, package path, and package digest. Omit credentials,
   tokens, cookies, and Authorization values. Set `EndPointUrl` to exactly the
   selected Fusion host origin, for example `https://<fusion-host>`. Reject
   `https://ThisURLMustBeChanged.com`, any other placeholder host, and any
   endpoint ending in `/cpq`.
9. Route the validated package through `core.data-loader` by default and import
   only after its immutable preview and explicit approval gates succeed. Use
   Fusion Setup Task CSV Import only as a fallback when Data Loader fails before
   accepting the configuration. Preserve the Data Loader failure evidence,
   revalidate the immutable package if needed, and obtain a new explicit
   approval immediately before the fallback import. Never retry a POST or
   submit a revision override without separate approval.
   When Fusion reports a revision mismatch, use `SourceTargetDiffOkFlag=Y` only
   after that approval.
10. After Data Loader initiation is accepted, return Core's accepted-initiation
    Markdown verbatim and stop. Do not poll automatically or continue to
    post-import verification. An accepted submission does not establish load
    success. On a later explicit user request for status, results, or errors,
    invoke the Core status workflow for the same request and use its returned
    ProcessLog status and object totals to determine the outcome. Apply the
    same explicit-request boundary to a separately approved FSM fallback.
    If Fusion returned a `ProcessId` but the wrapper failed to persist local
    metadata, classify the local write as `artifact_persistence`, retain the
    process identity, and stop. On a later explicit status request, query that
    same `ProcessId`; do not resubmit or mark the process failed solely because
    of the local write error.
11. Only after that requested status check confirms success, perform a new task
    export for field-level verification. Oracle FSM may
    replace an environment-specific `EndPointUrl` in an exported migration CSV
    with the portable sentinel `https://ThisURLMustBeChanged.com`. When that
    exact sentinel appears only in the post-import export, classify it as
    `export_portability_substitution`, not as the live saved endpoint and not as
    an import failure. Continue to verify the reference code, active/default
    flags, REST version, process/document names, reconciliation policy, five
    action parameters, mappings, and absence of credential parameters.
12. Verify the live endpoint separately when direct evidence is available. A
    same-target FSM task screenshot or authorized live task view may confirm
    that the selected reference code is active and that its complete visible
    endpoint is exactly `<FA_HOST>` with no path or `/cpq` suffix. Do not use
    task UI evidence as a substitute for offering, OAuth, or metadata REST
    prerequisites. If no live endpoint evidence is available and the export
    contains only the exact portability sentinel, report
    `process_success_with_endpoint_export_substitution`; do not report failure
    and do not generate a corrective import solely from that sentinel. Reject a
    placeholder in the proposed package, immutable import artifact, or live FSM
    value, and reject any standalone BM CPQ hostname.

## Offering REST Prerequisite

Use `core.fusion-api.rest-api-client`; do not duplicate its OAuth, token-cache,
401/403 refresh, request, or response handling inside this skill. Build the
paths from the selected target environment and run from the repository root:

```bash
python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py \
  /fscmRestApi/resources/11.13.18.05/features/ORA_MIDSIZE_SALES \
  --method GET

python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py \
  /fscmRestApi/resources/11.13.18.05/features/ORA_CONFIGURE_PRICE_QUOTE \
  --method GET
```

The core client reads `restBaseUrl` and `scope` from
`core/auth/fusionEnv.properties`, joins each relative item path to the selected
Fusion host, uses the authentication service's managed private cache outside the repository,
and retries the GET once after a cached-token 401 or 403. Require both item
responses to come from the same target origin. Persist only sanitized fields
needed for prerequisite evidence: endpoint path, HTTP status, `FeatureName`,
`FeatureCode`, `FeatureType`, and `EnabledFlag`. Never persist the token,
Authorization header, token-cache contents, or full unrelated response data.

## Offering Opt-In Remediation

When either prerequisite is not confirmed, do not create the integration or
prepare an import. Return these steps to the user:

1. Sign in to the target Fusion environment with an Application Implementation
   Consultant or another role authorized to configure offerings.
2. Open **Setup and Maintenance**, then **Configure Offerings**.
3. Find **Sales** (`ORA_MIDSIZE_SALES`), enable or opt in to the offering, and
   save.
4. Find **Configure Price Quote** (`ORA_CONFIGURE_PRICE_QUOTE`), enable or opt
   in to the offering, and save.
5. Sign out and back in if Fusion requests it, then collect fresh evidence from
   the same target environment and rerun this prerequisite gate.

If an offering is absent, frozen, unavailable for selection, or cannot be
enabled, stop and ask the Fusion provisioning administrator to verify the
subscription and pod provisioning or open an Oracle Support service request.
Do not bypass the gate with task visibility, a repository catalog snapshot, or
evidence from another environment.

## Resolver CLI

Run from the repository root. Preview is the default and performs no network
request:

```bash
python3 pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/scripts/facpq_integration.py metadata \
  --fa-host-url https://fa.example.com \
  --process-var-name oraclecpqo
```

The preview must contain exactly these paths in dependency order:

```text
/cpq/rest/v19/commerceProcesses/oraclecpqo/documents
/cpq/rest/v19/commerceProcesses/oraclecpqo/documents/{documentVarName}/actionDefs
```

Execute the same GET-only plan. The resolver reads the selected OAuth
properties file's dedicated `cpq_scope` value and forces a fresh login using
that value directly before the first documents GET. Missing or blank
`cpq_scope` blocks execution; the standard `scope` is not a fallback:

```bash
python3 pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/scripts/facpq_integration.py metadata \
  --fa-host-url https://fa.example.com \
  --process-var-name oraclecpqo \
  --properties core/auth/fusionEnv.properties \
  --token-cache auto \
  --output project/<project_id>/artifacts/pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/current/facpq-metadata-manifest.json \
  --execute
```

The live resolver verifies the client-side prerequisite itself. It requires a non-empty `cpq_scope`,
passes the complete value directly to the core OAuth helper's runtime `scope`
field for this login, and passes the returned access token in memory to both
metadata requests. It does not search for a `cpq` substring or split either
property. The versioned Fusion Features offering checks continue to use the
original configured `scope` value through the core REST client.
The resolver rejects an OAuth properties host that differs from
`--fa-host-url`, any token cache inside the repository (including `project/`), and output paths outside an
existing non-template `project/{project_id}` workspace. Do not place the token
on the command line or in project artifacts. This skill has no BM CPQ Basic or
direct-login mode, never uses browser cookies, never accepts another token on
the command line, and never calls the Fusion token-relay endpoint. When Codex
cannot open the authorization page in its browser, use `--no-open-browser`,
return the fresh authorization URL directly to the user as a clickable callback
link, and keep the local callback listener active until it completes or times
out. Do not persist the ephemeral URL, authorization code, or state value.

## OAuth Client Scope Remediation

If the fresh OAuth login or read-only FACPQ metadata request is rejected with HTTP
401 or 403, report that the configured OAuth client and CPQ scope could not be
verified. Direct the OAuth-client administrator to assign the resource scope represented
by `cpq_scope` to the target client and grant the caller FACPQ metadata-read access.
After that manual, permission-protected change, rerun the same read-only verification.
Do not ask the implementation user to confirm an IDCS configuration they cannot inspect.

After the resolver returns `status: ready`, construct the five deterministic
Sales parameter values without a network request:

```bash
python3 pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/scripts/facpq_integration.py action-urls \
  --manifest project/<project_id>/artifacts/pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/current/facpq-metadata-manifest.json
```

The action-URL command prints its result by default. To save it, pass `--output`
with an artifact path in the same initialized repository project as the input
manifest. External workspaces, `_template`, symlinks, parent-directory traversal,
and uninitialized projects are rejected. Existing outputs are rejected unless
the user approves replacing that exact artifact and `--overwrite-output` is
supplied. Publication is atomic; an output appearing after preflight is also
preserved unless overwrite was explicitly approved.

## Package Builder Contract

Use only the parameterized `facpq_integration.py build-package` route. Do not
retain or invoke environment-specific package helpers in reusable skill source.
Keep run-specific reference codes, names, descriptions, endpoints, and package
artifacts under the selected `project/{project_id}` workspace.

Before writing a package, require the selected metadata manifest to be complete
and GET-only, its consumer to be this skill, and the action contract to be a
non-mutating FACPQ OpenID Connect contract bound to that exact manifest. Require
`--fusion-environment`, `faHostUrl`, and `facpqEndpointUrl` to resolve to the
same HTTPS Fusion origin. Recompute all five fixed action expressions and reject
any mismatch instead of trusting a caller-supplied `status: ready` value.

Write the ZIP and preview only beneath an initialized repository
`project/{project_id}` workspace. Reject existing outputs by default. Use
`--overwrite-output` only after the user explicitly approves replacing both
named artifacts. Persist the package digest plus the baseline, metadata, and
action-contract digests in the preview.

When `--deactivate-existing` is selected, change only reviewed configuration
fields: set `ActiveFlag=N` for active non-target integrations and clear their
`DefaultFlag` before setting the target flags. Never replace an unrelated
integration endpoint merely because an FSM export contains the portable
sentinel. If a non-target row contains that sentinel, require
`--existing-endpoints-file` with a JSON object mapping each exact reference code
to its verified same-target Fusion origin. Stop when evidence is missing or
cross-environment. Include every per-row before/after field delta, every action
URL, and every endpoint-evidence reference in the immutable preview.

Example builder invocation:

```bash
python3 pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/scripts/facpq_integration.py build-package \
  --baseline-zip project/<project_id>/exports/cpq-task-baseline.zip \
  --manifest project/<project_id>/artifacts/pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/current/facpq-metadata-manifest.json \
  --action-contract project/<project_id>/artifacts/pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/current/facpq-action-contract.json \
  --setup-ref-code SAMPLE_FACPQ \
  --name "Sample FACPQ" \
  --description "Synthetic FACPQ integration" \
  --fusion-environment https://fa.example.com \
  --output-zip project/<project_id>/artifacts/pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/current/cpq-import.zip \
  --preview-output project/<project_id>/artifacts/pillars/cx/sales/integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/current/cpq-import-preview.json \
  --revenue-policy unrestricted \
  --reconciliation-option ORA_PARTS \
  --deactivate-existing \
  --create-if-missing
```

## FACPQ Action URL Contract

Use these exact OpenID Connect families. Substitute only the resolved process,
copy action, version action, and document identifiers. Preserve the expression
syntax and `%26` separators.

```text
Create:
#{'/cpq/sso/openid_connect_request.jsp?RelayState=/fscmUI/redwood/cx-cpq/application/container/quotes/quotes-detail?create=true%26currency=USD%26mode=live%26processVariableName={process}%26id=100106915720776%26inAppId=groupNode_RedwoodSales%26_partnerOpportunityNumber=' + (osc_param_OptyNumber ?: '') + '%26_partnerAccountId=' + (osc_param_AccountId ?: '')}

Edit:
#{'/cpq/sso/openid_connect_request.jsp?RelayState=/fscmUI/redwood/cx-cpq/application/container/quotes/quotes-detail?processVariableName={process}%26inAppId=groupNode_RedwoodSales%26id=' + (osc_quote_ExternalReferenceNumber ?: '')}

Version:
#{'/sso/openid_connect_request.jsp?RelayState=/cpq/commerce/buyside/document.jsp?_partnerIdentifier=fusion%26process={process}%26formaction=version%26action_id={action_id_version}%26bs_id=' + osc_quote_ExternalReferenceNumber}

Duplicate:
#{'/sso/openid_connect_request.jsp?RelayState=/cpq/commerce/buyside/copy_processing.jsp?_partnerIdentifier=fusion%26action_id={action_id_copy}%26version_id={action_id_version}%26bs_id=' + osc_quote_ExternalReferenceNumber + '%26document_id={document_id}'}

Proposal download:
#{'/sso/openid_connect_request.jsp?RelayState=/cpq/rest/v10/commerceProcesses/{process}/transactions/' +osc_quote_ExternalReferenceNumber+ '/attachments/oRCL_OSC_FileAttachment_t'}
```

Validate the returned five values before passing them to the Data Loader
preview. Do not generate SAML or BM CPQ URL variants.

## Setup Task Metadata

- Task name: `Manage Oracle CX Sales to Oracle CPQ Cloud Integration`
- Task code: `ORA_ZCA_OSC_CPQ_INTEGRATION`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`

## Result and Error Contract

- Persist sanitized metadata, process IDs, terminal statuses, validation
  findings, and artifact references under the active project workspace.
- Classify failures as input validation, catalog mismatch, auth/authz,
  transport/environment, Fusion API, process timeout, process failed, artifact
  persistence, or approval blocker.
- On timeout, stop with environment, task code, ProcessId, last status, elapsed
  time, and a same-ProcessId retry path.
- Treat a successful import with an unresolved endpoint as partial success, not
  completed setup.
- Track token usage for every durable skill run; never persist credentials,
  Authorization headers, base64 package content, or unsafe raw exports.
