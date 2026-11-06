# FACPQ Sales Integration Dependency Readiness

These gates authorize only the CX Sales-side setup for embedded FACPQ. They do
not authorize BM CPQ access or CPQ administrative mutations.

## Submission and Status Boundary

After an accepted initiation, return Core's accepted-initiation report and stop.
Do not retrieve status, ProcessLog, errors, or post-import verification as an
automatic follow-up. Resume those steps only on a later explicit user request
for load status, progress, results, or errors. A ProcessId followed by a local
artifact write failure must be retained for that later request; never resubmit
or poll automatically. This boundary also applies to a separately approved FSM
fallback. Report initiation and confirmed successful completion distinctly.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Offering REST authentication | Confirm target-matching Fusion OAuth properties provide restBaseUrl and the standard scope used by core.fusion-api.rest-api-client; keep the standard token cache in the authentication service's approved private storage outside the repository |
| 2 | Sales offering opt-in | GET /fscmRestApi/resources/11.13.18.05/features/ORA_MIDSIZE_SALES through the core client; require HTTP 200, exact FeatureCode, FeatureType OFFERING, and EnabledFlag Y |
| 3 | Configure Price Quote offering opt-in | GET /fscmRestApi/resources/11.13.18.05/features/ORA_CONFIGURE_PRICE_QUOTE through the core client against the same target; require HTTP 200, exact FeatureCode, FeatureType OFFERING, and EnabledFlag Y |
| 4 | Fusion Application host with embedded FACPQ | Confirm exactly one target Fusion environment and copy its host origin unchanged into the Sales EndPointUrl; do not append `/cpq` |
| 5 | IDCS OAuth-client CPQ scope | Verify effective CPQ scope access through a fresh OAuth login and the read-only FACPQ documents request |
| 6 | Fusion OAuth authentication | Require target-matching restBaseUrl and a non-empty `cpq_scope`; pass the complete value directly to the OAuth helper's runtime `scope` field in memory for a fresh login; do not derive it from the standard `scope` property; permit caching only in the authentication service's approved private token cache outside the repository |
| 7 | FACPQ documents read | Use that exact OAuth token on `/cpq/rest/.../documents` |
| 8 | FACPQ action metadata | Use the same OAuth token on actionDefs and resolve Main Document, Copy, and Version |
| 9 | FACPQ action URLs | Construct the fixed OpenID Connect Create, Edit, Duplicate, Version, and Proposal Download expressions |
| 10 | Sales Order Instance | Use Data Loader as the default approved import adapter; use Fusion Setup Task CSV Import only after a Data Loader failure and a new immediate approval |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| CPQ.INT.SALES_OFFERING | Sales offering opt-in | Yes | Before creating an integration | Verify | Fresh same-target response from the versioned Sales Features item GET | verify_required_offering_opt_ins | The Sales-side CPQ integration cannot be created unless Fusion Sales is enabled | Run the exact ORA_MIDSIZE_SALES item GET through the core client; if the response is absent or EnabledFlag is not Y, enable Sales and rerun | SalesOfferingName, SalesOfferingCode, SalesOfferingType, SalesOfferingEnabledFlag |
| CPQ.INT.CPQ_OFFERING | Configure Price Quote offering opt-in | Yes | Before creating an integration | Verify | Fresh same-target response from the versioned Configure Price Quote Features item GET | verify_required_offering_opt_ins | Embedded Fusion CPQ must be enabled on the target pod | Run the exact ORA_CONFIGURE_PRICE_QUOTE item GET through the core client; if the response is absent or EnabledFlag is not Y, enable Configure Price Quote and rerun | CpqOfferingName, CpqOfferingCode, CpqOfferingType, CpqOfferingEnabledFlag |
| CPQ.INT.FA_HOST | Fusion host and Sales integration endpoint | Yes | Every request | Verify | Target environment context | resolve_cpq_integration_parameters | EndPointUrl must identify the selected Fusion environment itself while FACPQ request paths add `/cpq` separately | Supply the Fusion origin without `/cpq`; reject `https://ThisURLMustBeChanged.com` and other placeholders | FaHostUrl, FacpqEndpointUrl |
| CPQ.INT.AUTH | Effective OAuth-client CPQ scope access and dedicated target-host `cpq_scope` configuration | Yes | Live metadata discovery | Verify | Fresh OAuth login, documents GET, core.auth.fusion-oauth-authentication, and selected Fusion properties | resolve_cpq_integration_parameters | A fresh OAuth bearer requested with the dedicated `cpq_scope` value directly authorizes both metadata GETs | Require a non-empty `cpq_scope`, pass its complete value directly to OAuth as runtime `scope`, and use the successful documents GET as proof; on 401/403, direct the OAuth-client administrator to correct the assignment and read privilege | FusionOAuthReference, CpqScopeMetadataAccessVerified |
| CPQ.INT.PARAMS | FACPQ parameters | Yes | Constructing action URLs | Lookup | Direct OAuth documents GET followed by actionDefs GET with the same bearer | resolve_cpq_integration_parameters | Duplicate and Version require exact FACPQ identifiers | Resolve one Main Document and one Copy and Version action | ProcessName, DocumentName, DocumentId, CopyActionId, VersionActionId |
| CPQ.INT.URLS | Five FACPQ action URL values | Yes | Creating the Sales Order Instance | Lookup | Fixed FACPQ OpenID Connect contract | resolve_cpq_action_url_contract | Sales invokes embedded FACPQ through these expressions | Preserve all `/cpq` segments and expression syntax | CreateQuoteUrl, EditQuoteUrl, CopyQuoteUrl, CreateVersionUrl, GetProposalUrl |
| CPQ.INT.IMPORT | Data Loader approval and fallback approval | Yes | Applying the Sales configuration | Verify | Immutable package preview, explicit Data Loader approval, and a separate immediate fallback approval if Data Loader fails |  | Both adapters mutate Fusion setup | Show environment, package digest, selected adapter, endpoint, and action rows immediately before each approval | ApprovalReference |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Fresh same-target versioned item GETs return HTTP 200 with exact FeatureCode, FeatureType OFFERING, and EnabledFlag Y for Sales and Configure Price Quote, and the Fusion host, verified IDCS client CPQ-scope assignment, a non-empty `cpq_scope` in target-matching properties, fresh OAuth result, FACPQ metadata, five URLs, and import approval are ready | GET-only lookup and approved Fusion configuration |
| Offering opt-in blocker | Either versioned item GET is missing, disabled, mismatched, cross-environment, unauthorized, or invalid | No integration creation; return Configure Offerings remediation and provisioning or Oracle Support escalation when the offering cannot be enabled |
| Missing environment value | Fusion host, target-matching offering REST evidence, process variable, OAuth properties, `cpq_scope`, IDCS scope-assignment evidence, or selector is absent | Ask only for the missing value |
| Authentication blocker | A versioned Features item GET or direct FACPQ metadata GET remains 401 or 403 after its allowed cached-token refresh | Verify the applicable configured scope or CPQ assignment, the configured `cpq_scope`, OAuth identity, target host, and required read privilege before a new login; do not substitute another route |
| FACPQ contract blocker | EndPointUrl in the proposed package, immutable import artifact, or live FSM value is a placeholder, differs from the Fusion host, includes `/cpq`, or an action URL does not match the supplied FACPQ contract | No import |
| Post-import export substitution | A terminally successful import is followed by an FSM task export that replaces only EndPointUrl with the exact `https://ThisURLMustBeChanged.com` portability sentinel | Keep the Fusion process successful, verify all other exported fields, and record `process_success_with_endpoint_export_substitution` until same-target live endpoint evidence is available; do not import a correction solely for the sentinel |
| Local artifact persistence issue | Fusion returned a ProcessId but the wrapper failed afterward while writing local metadata or logs | Stop after the local failure. On a later explicit status request, query the same ProcessId through Core and retain the requested recovered ProcessLog; keep artifact persistence separate from the Fusion process result and never resubmit automatically |
| Approval blocker | Immutable Fusion import approval is missing | No mutation |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CPQ.INT.DEPENDENCIES | step | 4 | resolve_dependency | ready->CPQ.INT.DESIGN;blocked->CPQ.INT.RETURN_MISSING | CPQ.INT.PARAMETERS | stop | Before creating the FACPQ Sales configuration package |
