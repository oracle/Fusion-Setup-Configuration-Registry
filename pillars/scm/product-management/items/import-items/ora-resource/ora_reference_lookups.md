# Reference Lookups

Execute the lookup below only through `core.fusion-api.rest-api-client` after
loading its standard Fusion REST instructions. The pillar skill supplies the
domain-specific GET path, query parameters, and result interpretation; the core client
owns authentication, trusted-host validation, token refresh, request transport,
and sanitized response handling. Do not substitute direct HTTP execution.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| verify_item_search_index_readiness | Before the current Import Items preparation and validation workflow begins | Fixed Item index fa-fscm-item; no item identity required | GET /fscmRestApi/applcoreApi/search/v1/fa-fscm-item/_search?size=0; no request body | HTTP status; hits.hits; timed_out; _shards.failed; errorCode | Apply scripts/item_index_readiness.py classify_readiness. HTTP 200 with an empty hits.hits array, no error, no timeout, and zero failed shards means available, even when total hits is zero. HTTP 404 with an errorCode field equal to FND_ERROR_SEARCH_SERVICE_UNKNOWN_INDEXES in the decoded response means index_remediation_required. Every other result means failure. | index_readiness_status: ready for available; index_readiness_status: index_remediation_required for the matching HTTP 404 condition | Stop for failure. Do not infer readiness from an item-record match, change the endpoint, or bypass the dependency check. |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| The lookup returns a valid HTTP 200 zero-result search response | Mark the item-index dependency ready and continue with the current Import Items workflow. |
| The lookup returns HTTP 404 and the response body contains errorCode FND_ERROR_SEARCH_SERVICE_UNKNOWN_INDEXES | Return index_remediation_required. End the current Import Items task at its remediation handoff; the offering-level orchestration owns any separate index-management task and later continuation. |
| The lookup returns any other result | Stop and classify the result using ora_error_handling.md. Do not treat the dependency as passed. |

Do not automatically retry this GET after an uncertain transport result. The
core REST client may refresh a cache-managed token once after 401 or 403; a
second authentication response, missing privilege, timeout, or transport error
stops the task with sanitized evidence and one safe next action.

## Deterministic Interpretation

Use readiness_request() to obtain the fixed GET contract and route it through
core.fusion-api.rest-api-client. Pass the observed status and decoded response
to classify_readiness(); a transport/authentication failure uses a missing status
and produces failure. The classifier performs no transport or artifact creation.
Only available may continue to package preparation; both other outcomes stop
at their declared terminal. No individual item needs to exist for this check.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ITEM_IMPORT.CHECK_ITEM_INDEX | decision | 1 | reference_lookup | available->ITEM_IMPORT.INDEX_DEPENDENCY_READY;index_remediation_required->ITEM_IMPORT.INDEX_REMEDIATION_REQUIRED;failure->ITEM_IMPORT.FAILED | none | stop | Before the current Import Items preparation and validation workflow begins; use verify_item_search_index_readiness. |
