# FACPQ Sales Integration Error Handling

Stop safely at FACPQ metadata, action URL, artifact, approval, and Fusion import
boundaries. Never substitute BM CPQ authentication or endpoints.

## Submission and Status Boundary

After an accepted initiation, return Core's accepted-initiation report and stop.
Do not retrieve status, ProcessLog, errors, or post-import verification as an
automatic follow-up. Resume those steps only on a later explicit user request
for load status, progress, results, or errors. A ProcessId followed by a local
artifact write failure must be retained for that later request; never resubmit
or poll automatically. This boundary also applies to a separately approved FSM
fallback. Report initiation and confirmed successful completion distinctly.

## Error Situations

| Situation | What Should Happen |
|---|---|
| A Sales or Configure Price Quote versioned Features item GET returns a missing, disabled, mismatched, malformed, or cross-environment response | Classify as an offering opt-in blocker or the owning REST failure class, stop before integration creation or package generation, and return the Configure Offerings remediation steps when the offering is not enabled |
| A required offering is absent, frozen, or cannot be enabled | Stop and ask the Fusion provisioning administrator to verify the subscription and pod provisioning or open an Oracle Support service request |
| An offering result is not from the exact /fscmRestApi/resources/11.13.18.05/features/{FeatureCode} item path | Classify as input validation and stop; discard collection, latest-version, BOSS, UI-only, or catalog-derived evidence and rerun the exact item GET through the core client |
| An offering item GET returns 401 or 403 | Allow only core.fusion-api.rest-api-client's single cached-token refresh behavior, then stop as auth/authz if rejected again; do not substitute UI evidence or direct curl |
| An offering REST lookup has a transport, timeout, non-authentication HTTP, malformed payload, or FeatureCode, FeatureType, or EnabledFlag mismatch | Stop under the applicable transport/environment, Fusion API, catalog mismatch, or offering-blocker class and preserve only the sanitized endpoint path, status, and required feature fields |
| Fusion host contains `/cpq` or another path | Reject it and request the Fusion origin only |
| EndPointUrl in a proposed package, immutable import artifact, or live FSM value is `https://ThisURLMustBeChanged.com`, another placeholder, or `<FA_HOST>/cpq` | Classify as input validation, regenerate it as exactly `<FA_HOST>`, and stop before import approval |
| A post-import FSM task export replaces EndPointUrl with the exact `https://ThisURLMustBeChanged.com` sentinel | Classify the field as `export_portability_substitution`; keep a terminally successful Fusion process successful, verify the other exported fields, and use same-target live FSM task evidence when available. Do not submit a correction solely because of the exported sentinel |
| Fresh OAuth login or an OAuth-authenticated metadata GET returns 401 or 403 | Classify as auth/authz, stop, and direct the OAuth-client administrator to assign `cpq_scope` to the target client and grant FACPQ metadata-read access; do not ask the implementation user for confirmation |
| OAuth properties omit or leave `cpq_scope` blank, or restBaseUrl differs from the requested Fusion host | Classify as input validation and stop before login or any metadata GET; do not fall back to `scope` |
| OAuth token-cache path is inside the repository, including project/{project_id} | Classify as input validation and require an authentication service's managed private cache outside the repository |
| Codex browser cannot open the OAuth authorization page | Start the approved `--no-open-browser` flow, provide the fresh authorization URL directly to the user as a clickable link, and keep the local callback listener active; never persist the URL, authorization code, or state value |
| Metadata path omits `/cpq/rest` | Classify as input validation and regenerate the plan |
| OAuth-authenticated documents or actionDefs GET returns 401 or 403 | Stop as auth/authz; direct the OAuth-client administrator to verify `cpq_scope`, OAuth identity, and FACPQ read privilege before a new login |
| A metadata GET returns a non-authentication HTTP failure | Stop as Fusion API |
| A metadata GET has a transport, TLS, DNS, timeout, or payload failure | Stop under the applicable failure class |
| A request plan includes `/api/rwdtools/tokenrelay`, a documents retry, or another bearer | Classify as input validation and restore the direct two-GET plan |
| Transport, TLS, DNS, or timeout failure | Stop as transport/environment; verify the Fusion host and `/cpq` route before retrying the read |
| FACPQ response is non-JSON, malformed, or non-success | Stop as Fusion API; preserve sanitized response metadata |
| Main Document, Copy action, or Version action is ambiguous | Return sanitized candidates and request the exact variable selector |
| Identifier evidence conflicts across hosts or processes | Stop as catalog mismatch and recollect from one FACPQ process |
| Generated action URL uses SAML, legacy BM Create/Edit, or misses `/cpq` | Stop as input validation; regenerate the fixed FACPQ contract |
| Package contains a credential, token, cookie, or Authorization value | Delete the unsafe generated package, rotate the secret, and stop as artifact persistence/security |
| Fusion import approval is missing | Stop as approval blocker |
| Data Loader import fails before accepting the configuration | Preserve the Data Loader evidence, revalidate the immutable package, and require a new explicit approval before attempting Fusion Setup Task CSV Import fallback |
| Fusion import times out or fails | Preserve ProcessId, request ID, status, ProcessLog, elapsed time, and safe next action; do not retry automatically |
| Fusion returns a ProcessId and the wrapper then fails while persisting local metadata or a log | Classify the local error as artifact persistence and stop; on a later explicit user status request, query the same ProcessId through Core and derive the Fusion result from its ProcessLog. Do not mark the process failed or submit another import because of the local write error |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Offering opt-in blocker | A fresh same-target versioned item GET does not return HTTP 200 with exact FeatureCode, FeatureType OFFERING, and EnabledFlag Y for Sales or Configure Price Quote | Enable both under Setup and Maintenance → Configure Offerings, save, refresh the session if requested, and rerun both exact item GETs; escalate absent or frozen offerings to provisioning or Oracle Support |
| Input validation | Host, IDCS CPQ-scope prerequisite, OAuth properties, `cpq_scope` configuration, cache location, `/cpq` path, identifier, or action URL is malformed, missing, or ambiguous | Correct and rerun preview |
| Catalog mismatch | Values belong to different Fusion hosts or processes | Recollect from one target |
| Auth/authz | A Features item or FACPQ request remains 401/403 after the one allowed cached-token refresh | Revalidate the applicable configured scope or CPQ client assignment, the configured `cpq_scope`, Fusion OAuth identity, target restBaseUrl, and read privilege |
| Transport/environment | DNS, TLS, network, or timeout prevents a GET | Verify environment route before retrying |
| Fusion API | FACPQ or Fusion returns a non-auth 4xx/5xx or invalid payload | Preserve sanitized evidence and stop |
| Process timeout | Fusion import does not reach terminal status in the allowed window | Report ProcessId and next-check path |
| Process failed | Fusion import reaches a failed terminal state | Persist ProcessLog and do not resubmit automatically |
| Artifact persistence | Output path, overwrite, package shape, secret scan, or post-ProcessId local metadata write fails | Correct the artifact issue; when a ProcessId already exists, stop and retain it; query that same process only on a later explicit status request and report its Fusion outcome separately |
| Approval blocker | Import or retry approval is absent | Stop without mutation |
| Data Loader failure | Data Loader does not accept the approved package | Preserve its failure evidence; do not automatically start Fusion Setup Task CSV Import |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Offering prerequisite review | Target Fusion environment; both exact versioned item paths; HTTP status; FeatureName, FeatureCode, FeatureType, and EnabledFlag for each response; omit tokens, OAuth state, Authorization headers, token-cache contents, and unrelated response content |
| Metadata review | Fusion environment, effective CPQ-scope access verified by fresh OAuth and read-only metadata requests, `cpq_scope` as the dedicated source passed directly to OAuth, direct `/cpq/rest` endpoint family, process/document names, Copy and Version selectors; omit the token and every configured scope value |
| Configuration review | Every new-record field: reference code, name, description, host-only `<FA_HOST>` endpoint, document/process/REST values, revenue policy, reconciliation option, Active/default flags, mapping and legacy-row behavior, all five action parameter names with their complete generated action URL expressions, package path, and package digest; confirm no placeholder or `/cpq` suffix; omit credentials, tokens, cookies, and Authorization values |
| Post-import verification | Fusion ProcessLog terminal status and object totals; post-import task export fields; whether EndPointUrl was exported as the portability sentinel; same-target live FSM endpoint evidence when supplied. Keep process status, artifact persistence, and endpoint evidence as separate results |
| Failure report | Failure class, redacted endpoint family, status, external IDs, sanitized message, and one safe next action |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Both required offerings are not confirmed by fresh same-target exact versioned Features item GETs with HTTP 200, exact FeatureCode, FeatureType OFFERING, and EnabledFlag Y | Do not create an integration, generate its import package, or request import approval; do not substitute UI-only, BOSS, or repository-catalog evidence |
| A BM CPQ hostname, direct login, Basic credential, or browser cookie is supplied | Do not use it; this skill supports headless FACPQ access through direct Fusion OAuth only |
| Credentials or tokens are supplied for persistence | Do not write them to repository or project files |
| A request asks to call `/api/rwdtools/tokenrelay` or use another bearer | Refuse that route; require the IDCS CPQ-scope prerequisite and direct Fusion OAuth authentication |
| Exact FACPQ IDs are missing | Do not substitute documentation or cross-environment values |
| User requests automatic Fusion import without immutable preview approval | Do not execute or simulate it |
| A prior Fusion import outcome is uncertain | Do not retry until current state is reconciled |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CPQ.INT.EXECUTION_GATE | decision | 6 | execution_gate | approved->CPQ.INT.RETURN_READY;rejected->CPQ.INT.RETURN_MISSING;failed->CPQ.INT.RETURN_FAILED | CPQ.INT.DESIGN | stop | Immediately before an approved Fusion import handoff |
| CPQ.INT.RETURN_READY | terminal | 7 | terminal | none | CPQ.INT.EXECUTION_GATE | continue | FACPQ configuration is validated and approved for execution |
| CPQ.INT.RETURN_MISSING | terminal | 8 | terminal | none | none | continue | Required FACPQ value, dependency, or approval is missing |
| CPQ.INT.RETURN_FAILED | terminal | 9 | terminal | none | none | continue | Validation or Fusion execution failed |
