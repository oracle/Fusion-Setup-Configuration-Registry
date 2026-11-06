# FACPQ Sales Integration Input Validation

Use these rules for setup task `ORA_ZCA_OSC_CPQ_INTEGRATION`. This skill
supports embedded Fusion Application CPQ (FACPQ) only. Reject standalone BM CPQ
hosts, BM CPQ credentials, browser-session reuse, and BM CPQ URL variants.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Required offering opt-ins | Fresh same-target responses from GET /fscmRestApi/resources/11.13.18.05/features/ORA_MIDSIZE_SALES and GET /fscmRestApi/resources/11.13.18.05/features/ORA_CONFIGURE_PRICE_QUOTE through core.fusion-api.rest-api-client; each returns HTTP 200, its exact FeatureCode, FeatureType OFFERING, and EnabledFlag Y | Block integration creation and package generation | Run both exact versioned Features item GETs against the selected restBaseUrl; enable a missing or disabled offering in Configure Offerings and rerun; correct authentication, host, payload, or response mismatches before proceeding | Before creating any FACPQ Sales integration | verify_required_offering_opt_ins |
| Fusion host | One HTTPS Fusion Application host origin with no path, query, credentials, or fragment | Block metadata discovery | Supply `<FA_HOST>` without `/cpq` | Every FACPQ request | resolve_cpq_integration_parameters |
| Sales integration endpoint | Exactly `<FA_HOST>` with no path | Block configuration handoff | Copy the validated Fusion host origin into EndPointUrl; reject placeholders and do not append `/cpq` | Every Sales Order Instance | resolve_cpq_integration_parameters |
| FACPQ discovery seed | Fusion host, REST version, process variable name, and a Fusion OAuth properties file whose restBaseUrl matches the target and whose `cpq_scope` property is non-empty | Block live metadata discovery | Read `cpq_scope` directly and force a fresh target-host login through the core OAuth helper using that value as runtime `scope`; the resulting documents GET verifies effective client-scope access | Before the documents GET | resolve_cpq_integration_parameters |
| FACPQ URL parameters | Process Name, Document Name, Document ID, Copy Action ID, and Version Action ID | Block URL construction | Run the OAuth-authenticated documents GET, then resolve actionDefs using the same in-memory Fusion OAuth bearer | Before constructing action URLs | resolve_cpq_integration_parameters |
| Sales action URLs | Create, Edit, Duplicate, Version, and Proposal Download | Block configuration handoff | Construct the fixed OpenID Connect FACPQ expressions | Before saving the Sales Order Instance | resolve_cpq_action_url_contract |
| Revenue edit policy | Restricted field selection or an explicit unrestricted decision | Require design review | Confirm which opportunity revenue fields become read-only after quoting | Before activating the instance |  |
| Revenue reconciliation option | `ORA_ROOTS` (Root) or `ORA_PARTS` (Part) | Block package generation | Select one supported `RevnReconcileOption` CSV value | Before saving the Sales Order Instance |  |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| A required versioned Features item response is missing, cross-environment, disabled, mismatched, UI-only, BOSS-derived, or based only on a repository catalog snapshot | Blocked | Run both exact item GETs against the selected target; return Configure Offerings remediation for a disabled result; escalate an absent or frozen offering to provisioning or Oracle Support | verify_required_offering_opt_ins |
| An offering response lacks HTTP 200, its exact FeatureCode, FeatureType OFFERING, or EnabledFlag Y | Blocked | Reject the result and rerun the exact 11.13.18.05 item path through core.fusion-api.rest-api-client | verify_required_offering_opt_ins |
| Offering authentication remains 401 or 403 after the core client's one cached-token refresh | Blocked | Verify the standard scope, target confidential-application assignment, OAuth identity, Fusion privileges, and target restBaseUrl before a new login | verify_required_offering_opt_ins |
| The host contains `/cpq`, `/rest`, another path, credentials, query, or fragment | Blocked | Reduce it to the Fusion host origin | resolve_cpq_integration_parameters |
| A proposed package, immutable import artifact, or live FSM value has EndPointUrl `https://ThisURLMustBeChanged.com`, another placeholder, or a value ending in `/cpq` | Blocked | Replace it with the exact selected Fusion host origin and rerun package preview | resolve_cpq_integration_parameters |
| The exact `https://ThisURLMustBeChanged.com` sentinel appears only in a post-import FSM task export after a successful ProcessLog | `export_portability_substitution`; do not mark the Fusion process failed | Verify all non-endpoint exported fields and use same-target live FSM task evidence when available; never create a corrective import solely from the exported sentinel |  |
| The metadata request does not start with `/cpq/rest/{version}/commerceProcesses/` | Blocked | Regenerate the two FACPQ GET paths | resolve_cpq_integration_parameters |
| A standalone BM CPQ host or direct BM CPQ login is supplied | Blocked | Replace it with the paired Fusion host and Fusion OAuth reference | resolve_cpq_integration_parameters |
| Fresh OAuth or the documents/actionDefs GET returns HTTP 401/403 | Blocked | Direct the OAuth-client administrator to assign `cpq_scope` to the target client and grant FACPQ metadata-read access; then rerun the read-only verification | resolve_cpq_integration_parameters |
| The selected OAuth properties omit or leave `cpq_scope` blank, or restBaseUrl identifies a different Fusion host | Blocked | Correct the target-host properties; require a non-empty `cpq_scope` without falling back to `scope` | resolve_cpq_integration_parameters |
| The OAuth token cache resolves inside the repository, including project/{project_id} | Blocked | Use an authentication service's managed private cache outside the repository | resolve_cpq_integration_parameters |
| A request plan includes `/api/rwdtools/tokenrelay` or any bearer other than the token returned by the fresh scoped login | Blocked | Restore the direct two-GET plan | resolve_cpq_integration_parameters |
| Documents or actionDefs discovery is ambiguous | Blocked | Ask for the exact returned document, Copy action, or Version action variable name | resolve_cpq_integration_parameters |
| Commerce-process version ID or Edit action ID is supplied | Ignored for the FACPQ action contract | Do not add it to required inputs or action URL construction | resolve_cpq_action_url_contract |
| Any generated URL uses SAML or omits the required `/cpq` segment | Blocked | Regenerate the fixed FACPQ OpenID Connect URL family | resolve_cpq_action_url_contract |
| Credentials or tokens appear in a tracked file, diagnostic, or artifact | Blocked | Remove and rotate the secret; use a runtime Fusion authentication reference |  |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| The Sales and Configure Price Quote versioned item GETs return HTTP 200 from the same target with exact FeatureCode values ORA_MIDSIZE_SALES and ORA_CONFIGURE_PRICE_QUOTE, FeatureType OFFERING, and EnabledFlag Y | Accept for execution | Before integration creation or package generation | verify_required_offering_opt_ins |
| Fusion host is one HTTPS origin | Accept for review | Every FACPQ request | resolve_cpq_integration_parameters |
| EndPointUrl exactly equals `<FA_HOST>` and contains no path, placeholder, query, or fragment | Accept for review | Creating the Sales Order Instance | resolve_cpq_integration_parameters |
| A same-target live FSM task view shows the selected reference code active with EndPointUrl exactly equal to `<FA_HOST>` | Accept as post-import live-endpoint evidence only | Post-import verification; never offering, OAuth, or metadata prerequisite verification |  |
| The dedicated `cpq_scope` property is non-empty and its configured scope is assigned to the target IDCS OAuth client | Accept for execution | Authentication prerequisite | resolve_cpq_integration_parameters |
| Documents GET uses the access token returned by a forced fresh Fusion login using the complete `cpq_scope` value directly | Accept for execution | Metadata authentication | resolve_cpq_integration_parameters |
| REST path is `/cpq/rest/v19/commerceProcesses/{process}/documents` or its document `actionDefs` child | Accept for execution | Metadata discovery | resolve_cpq_integration_parameters |
| ActionDefs uses the same Fusion OAuth token as documents and neither request is retried with another bearer | Accept for execution | Metadata discovery | resolve_cpq_integration_parameters |
| Process and document names are exact returned variable names | Accept for review | Creating the Sales Order Instance | resolve_cpq_integration_parameters |
| Document, Copy action, and Version action IDs are positive numeric values | Accept for review | Constructing Duplicate and Version | resolve_cpq_integration_parameters |
| Create and Edit use `/cpq/sso/openid_connect_request.jsp` plus the Redwood quotes-detail RelayState | Accept for review | Validating action URLs | resolve_cpq_action_url_contract |
| Duplicate, Version, and Proposal use `/sso/openid_connect_request.jsp` with RelayState beginning `/cpq/` | Accept for review | Validating action URLs | resolve_cpq_action_url_contract |
| Duplicate uses Version Action ID as `version_id` | Accept for review | Validating Duplicate | resolve_cpq_action_url_contract |
| Parameter Name or Value has leading or trailing spaces | Reject before save | Validating any action row |  |
| `RevnReconcileOption` is `ORA_ROOTS` or `ORA_PARTS` | Accept for review | Creating or updating the Sales Order Instance |  |

## Revenue Reconciliation Option Values

Use these exact values in the `ORA_ZCA_SALES_TRANS_INTEG_CONFIG.csv`
`RevnReconcileOption` column:

| User-facing option | CSV value | Meaning |
|---|---|---|
| Root | `ORA_ROOTS` | Reconcile aggregate values for root model revenue lines. |
| Part | `ORA_PARTS` | Reconcile individual values for part and non-root revenue lines. |

Reject blank, legacy, or unrecognized values rather than carrying a value from
an unrelated integration row.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CPQ.INT.VALIDATE | step | 1 | validate_input | success->CPQ.INT.OFFERINGS;missing->CPQ.INT.RETURN_MISSING | none | stop | Every FACPQ Sales integration request |
