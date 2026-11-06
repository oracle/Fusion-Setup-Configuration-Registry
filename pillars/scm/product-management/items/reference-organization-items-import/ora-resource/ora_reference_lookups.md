# Reference Organization Items Import Reference Lookups

Use the installed Core workflow selected at intake; see references/core-loader-handoff.md.
Business-scope evidence is supplied by the named project baseline; it is not a
live existence probe. The Item Index is this pillar's declared read-only Fusion
check. Core owns authentication, environment validation, registered FBDI routing
and execution using the selected BO's deployed configuration. The pillar does
not retrieve or inspect LoadAdapterConfig, its links, SQL or ESS argument mapping.
Absence of that enclosure in a BO response is not a pillar validation failure.

## Live Lookups

Before preparing the current import, use `scripts/item_index_readiness.py`'s `readiness_request()` and route the GET through `core.fusion-api.rest-api-client` with its standard Fusion REST instructions and `REST-Framework-Version: 9`. Retain sanitized status/classifier evidence in memory for this validation cycle's Task Hook; do not repeat the lookup during Task Hook. This checks search availability, not item existence or index-build completion.

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| verify_item_search_index_readiness | Before preparation | Fixed Item Index fa-fscm-item | GET /fscmRestApi/applcoreApi/search/v1/fa-fscm-item/_search?size=0; no request body | HTTP status; hits.hits; timed_out; _shards.failed; errorCode | Apply scripts/item_index_readiness.py classify_readiness: HTTP 200, empty hits.hits, timed_out false, zero failed shards and no error means available, including zero total hits. HTTP 404 containing errorCode FND_ERROR_SEARCH_SERVICE_UNKNOWN_INDEXES means index_remediation_required. Every other result means failure. | index_readiness_status | Stop preparation/submission. Unknown index returns remediation to Product Management orchestration; other failures return sanitized diagnostics. No automatic retry, endpoint substitution or index mutation; core may refresh a cache-managed token once after 401/403. |

## Core Routing Boundary

Pass the unchanged validated source to Core with the exact business object
`Reference Organization Items`. Reuse Core's successful native-FBDI routing and
artifact preflight at its task-validation handoff; do not repeat metadata calls
or access private Core lookup helpers. Missing or ambiguous registration,
unmatched CSV members and conflicting routing remain Core blockers. Never
substitute the ordinary `item` BO, guess an adapter or modify BO configuration.
Import Mode is supplied by the deployed BO during execution. The pillar's
resolved mode records supported source intent; it is not proof of the deployed
value and is not forwarded as a per-run ESS argument.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| verify_reference_org_readiness | After source validation | Named project baseline/business-scope evidence; requested items/organizations and conditional source structures | Require supplied business evidence to identify existing items and organizations, intended definition/reference associations, and selected source structures; derive scope from current template selector metadata and compare exact requested identities against supplied evidence without an environment probe | Item/organization and conditional structure scope results | Block on missing or conflicting business scope; no inferred values, live call or approval question |
| verify_reference_org_loader_route | At Core task-validation handoff | Core-returned successful routing/preflight evidence; exact selected BO; final immutable source; active Run Book/task context | Require Core to have accepted the source as FBDI under Reference Organization Items; validate CSV Batch ID and requested scope against the bound source, without a separate metadata/configuration request | Core-validated route and source/task consistency | Preserve Core routing failures; block on missing/conflicting handoff evidence; no generic BO fallback |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| REF_ORG_ITEMS.CHECK_ITEM_INDEX | decision | 1 | reference_lookup | available->REF_ORG_ITEMS.DEFAULT_MODE;index_remediation_required->REF_ORG_ITEMS.INDEX_REMEDIATION_REQUIRED;failure->REF_ORG_ITEMS.FAILED | none | stop | Before preparation, run verify_item_search_index_readiness; at Task Hook verify the same-validation-cycle retained result. |
| REF_ORG_ITEMS.RESOLVE_CONTEXT | step | 4 | evaluate_result | verified->REF_ORG_ITEMS.CONFIRM_DEPENDENCIES;blocked->REF_ORG_ITEMS.FAILED | REF_ORG_ITEMS.VALIDATE_FBDI | stop | Resolve supplied business scope and evaluate Core-returned BO preflight evidence against the bound source and task; retain the validated batch and requested mode intent without inspecting BO configuration. |
