# FACPQ Integration Parameter Resolution

Resolve identifiers only through the embedded FACPQ route on the selected
Fusion host. Read target-matching Fusion OAuth properties and require a non-empty
`cpq_scope` property. Pass its complete value directly to the shared OAuth helper's
runtime `scope` field for a fresh login. Use the returned token on the documents
GET and dependent actionDefs GET. The selected CPQ resource scope must already
be assigned to the target IDCS OAuth client. The original configured `scope`
continues to serve Features offering checks. The Fusion OAuth response may use
only the authentication service's managed private cache outside the repository. BM CPQ endpoints and authentication
are outside this skill.

Resolve the Sales and Configure Price Quote offering prerequisites first through
the versioned Fusion Features item resource. Delegate OAuth, token-cache,
request, 401/403 refresh, and response handling to
core.fusion-api.rest-api-client. Never use direct curl, BOSS discovery, a
repository catalog snapshot, or a different environment as prerequisite proof.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| verify_required_offering_opt_ins | Before creating an integration or generating its import package | Exact Fusion host, target-matching OAuth properties, standard scope, and offering codes ORA_MIDSIZE_SALES and ORA_CONFIGURE_PRICE_QUOTE | Through core.fusion-api.rest-api-client, GET /fscmRestApi/resources/11.13.18.05/features/ORA_MIDSIZE_SALES and GET /fscmRestApi/resources/11.13.18.05/features/ORA_CONFIGURE_PRICE_QUOTE against the same restBaseUrl origin | HTTP status, FeatureName, FeatureCode, FeatureType, EnabledFlag | Require HTTP 200 for both requests; require each response FeatureCode to equal its path key, FeatureType to equal OFFERING, EnabledFlag to equal Y, and both responses to come from the requested Fusion origin | SalesOfferingName, SalesOfferingCode, SalesOfferingType, SalesOfferingEnabledFlag, CpqOfferingName, CpqOfferingCode, CpqOfferingType, CpqOfferingEnabledFlag | Stop integration creation and return Configure Offerings remediation when either item is missing, disabled, or mismatched; classify 401/403 after the core client's one refresh as auth/authz and other transport, API, or payload failures under the owning failure class; do not substitute UI, BOSS, or repository-catalog evidence |

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_cpq_integration_parameters | FACPQ identifiers are missing or must be verified | Fusion host, verified IDCS client assignment for the configured CPQ resource scope, target-matching Fusion OAuth properties with a non-empty `cpq_scope`, approved private token-cache path outside the repository, REST version, process variable name, and optional document, Copy, or Version selectors | Copy the complete `cpq_scope` value to the core OAuth helper's runtime `scope` key in memory and force a fresh login; OAuth GET `/cpq/rest/{version}/commerceProcesses/{processVarName}/documents`; then GET `/cpq/rest/{version}/commerceProcesses/{processVarName}/documents/{documentVarName}/actionDefs` with the same bearer | Documents: id, variableName, label, type, process.id, process.variableName; actions: id, variableName, label, type, isAvailable | Require the IDCS client scope assignment, properties restBaseUrl equal to the requested Fusion origin, and a non-empty `cpq_scope`; do not split, filter, or fall back to `scope`; select exactly one Main Document plus one available Copy and Version action | FaHostUrl, FacpqEndpointUrl, CommerceProcessId, DocumentId, DocumentName, CopyActionId, VersionActionId, ProcessName, RestFrameworkVersion | Return sanitized candidates and ask only for the exact ambiguous selector; never return the token or scope values |
| resolve_cpq_action_url_contract | Metadata manifest is ready | Ready FACPQ manifest | Run `scripts/facpq_integration.py action-urls`; no network request | Process Name, Document ID, Copy Action ID, Version Action ID | Require the GET-only FACPQ boundary and require the Sales EndPointUrl to exactly equal `<FA_HOST>` without `/cpq`; retain `/cpq` only inside the fixed metadata and action paths | CreateQuoteUrl, EditQuoteUrl, CopyQuoteUrl, CreateVersionUrl, GetProposalUrl | Stop if the manifest is incomplete, mutation-capable, BM-enabled, cross-host, placeholder-based, or has `/cpq` in EndPointUrl |

## Required User Inputs After GET Discovery

| Field | Ask When | User Prompt | Accepted Value |
|---|---|---|---|
| DocumentName | The documents GET returns zero or multiple Main Document candidates | Select the exact main-document variable name returned by FACPQ | Exact returned `variableName` |
| CopyActionVarName | The actionDefs GET does not return exactly one Copy candidate | Select the exact Copy action variable name returned by FACPQ | Exact returned `variableName` |
| VersionActionVarName | The actionDefs GET does not return exactly one Version candidate | Select the exact Version action variable name returned by FACPQ | Exact returned `variableName` |

Do not request `CommerceProcessVersionId` or `EditActionId`; neither is used by
the supplied FACPQ action URL contract.

## Action Parameter Mapping

| Action | Required Values | Endpoint Contract |
|---|---|---|
| Create | Process Name, opportunity number, account ID | `/cpq/sso/openid_connect_request.jsp` relays to the Redwood FACPQ quotes-detail page with `create=true`, `currency=USD`, `mode=live`, fixed page ID `100106915720776`, and `groupNode_RedwoodSales` |
| Edit | Process Name and quote external reference | `/cpq/sso/openid_connect_request.jsp` relays to the Redwood FACPQ quotes-detail page |
| Duplicate | Copy Action ID, Version Action ID, Document ID, and quote external reference | `/sso/openid_connect_request.jsp` relays to `/cpq/commerce/buyside/copy_processing.jsp`; use Version Action ID as `version_id` |
| Version | Process Name, Version Action ID, and quote external reference | `/sso/openid_connect_request.jsp` relays to `/cpq/commerce/buyside/document.jsp` |
| Proposal Download | Process Name and quote external reference | `/sso/openid_connect_request.jsp` relays to `/cpq/rest/v10/.../attachments/oRCL_OSC_FileAttachment_t` |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Either versioned offering item GET does not return HTTP 200 with the exact FeatureCode, FeatureType OFFERING, and EnabledFlag Y | Stop before integration creation or package generation and return the Configure Offerings remediation steps |
| Offering evidence comes only from a repository catalog snapshot, BOSS response, UI-only review, or a different Fusion environment | Reject it as prerequisite proof and run both versioned Features item GETs against the requested pod |
| The two offering responses come from different hosts or use a collection, latest-version, or non-item path | Reject the evidence and rerun both exact 11.13.18.05 item paths against one target restBaseUrl |
| Offering authentication returns 401 or 403 after the core client's one cached-token refresh | Stop as auth/authz; verify the standard scope, confidential-application assignment, Fusion privileges, and target identity before a new login |
| An offering item GET returns 404 | Treat the prerequisite as unconfirmed; verify the feature code and target pod, then return Configure Offerings or provisioning remediation rather than assuming disabled state |
| Preview does not contain exactly the documents GET followed by the dependent actionDefs GET | Reject the plan |
| Fusion host or process variable name is missing | Ask for the exact value before constructing a request |
| The proposed package, immutable import artifact, or live FSM integration endpoint is a placeholder, differs from the selected Fusion host, or appends `/cpq` | Reject it and regenerate EndPointUrl from the exact Fusion host origin |
| A successful import's post-import FSM task export replaces only EndPointUrl with the exact `https://ThisURLMustBeChanged.com` sentinel | Record `export_portability_substitution`, verify the remaining exported fields, and accept same-target live FSM task evidence for the endpoint when available; do not mark the process failed or generate a correction solely from the sentinel |
| Live discovery lacks verified IDCS client assignment for the configured CPQ scope, target-matching OAuth properties with a non-empty `cpq_scope`, or an approved private cache path outside the repository | Stop; complete the missing authentication prerequisite before login or any request |
| Documents GET succeeds with Fusion OAuth | Use the same captured OAuth token for actionDefs |
| Documents GET or actionDefs returns HTTP 401/403 | Stop as auth/authz; verify the IDCS client assignment for `cpq_scope` and FACPQ read privilege before a new login |
| A metadata GET returns another HTTP, transport, timeout, or payload failure | Stop under the applicable failure class |
| A plan includes `/api/rwdtools/tokenrelay`, a documents retry, another bearer, or derives metadata authentication scope from the standard `scope` property | Reject the plan; this task uses only the fresh OAuth token requested with the dedicated `cpq_scope` value |
| Documents GET returns exactly one Main Document | Map its document ID/name and optional process ID |
| Documents GET is ambiguous | Return candidates and ask for `documentVarName` |
| ActionDefs GET returns one unambiguous Copy or Version action | Map its ID and variable name |
| Copy or Version selection is ambiguous | Return candidates and ask for the exact role-specific variable name |
| An exact selector or ID identifies the wrong role or an unavailable action | Reject it and recollect from the same FACPQ process |
| A BM CPQ endpoint, Basic credential, direct-login page, or browser cookie is supplied | Reject it; this skill supports headless FACPQ access through the Fusion host only |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CPQ.INT.OFFERINGS | step | 2 | reference_lookup | enabled->CPQ.INT.PARAMETERS;blocked->CPQ.INT.RETURN_MISSING;failed->CPQ.INT.RETURN_FAILED | CPQ.INT.VALIDATE | stop | Verify both required offerings through exact versioned Fusion Features item GETs |
| CPQ.INT.PARAMETERS | step | 3 | evaluate_result | resolved->CPQ.INT.DEPENDENCIES;missing->CPQ.INT.RETURN_MISSING | CPQ.INT.OFFERINGS | stop | Resolve FACPQ metadata and the action URL contract |
