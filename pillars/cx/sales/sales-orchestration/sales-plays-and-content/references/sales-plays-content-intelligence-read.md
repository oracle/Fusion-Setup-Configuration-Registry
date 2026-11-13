# Sales Play Content Intelligence Search

## Contents

- [Source and Scope](#source-and-scope)
- [Shared Client](#shared-client)
- [Required Inputs](#required-inputs)
- [Request Contract](#request-contract)
- [Security Gate](#security-gate)
- [Result Classification](#result-classification)
- [Retry and Side-Effect Boundary](#retry-and-side-effect-boundary)

## Source and Scope

This contract contains the developer-provided Sales Play Content Intelligence
request and the applicable Knowledge Management security policies.

Use this local contract to test semantic content search for one exact Sales
Play ID and one user question. The POST
request has read semantics and does not create or modify Sales Play or
Knowledge content.

## Task-Local Client

Invoke the endpoint through the Knowledge Management OAuth client:

`pillars/cx/sales/sales-orchestration/sales-plays-and-content/scripts/knowledge_rest_client.py`

Read `knowledge-management-rest-api.md` before execution. The task-local client
uses the configured `restBaseUrl`, reads the regular `scope`, selects the single
scope token containing `knowledge-management`, and uses the shared managed
external profile cache (`--token-cache auto`) under `~/.fusionaim/`. The cache
is bound to the selected OAuth profile; never store tokens in the checkout or
project workspace. Treat a missing `scope` or missing `knowledge-management`
token inside that property as an authentication
configuration blocker. Do not copy an Authorization header or a pasted bearer
token into the command, skill, payload, log, or diagnostic.

The credential-free command shape is:

```bash
python3 pillars/cx/sales/sales-orchestration/sales-plays-and-content/scripts/knowledge_rest_client.py \
  '/api/knowledge-management/v2/contentIntelligence' \
  --method POST \
  --header 'Content-Type=application/json' \
  --body '<serialized-request-body>'
```

## Required Inputs

| Input | Requirement |
|---|---|
| Target environment | Confirm the intended Fusion host through the configured environment. |
| Acting user | Use the end user whose effective content-search access is being tested. |
| User question | Require non-empty question text and preserve its meaning exactly. |
| Sales Play ID | Require one exact, non-empty Sales Play ID; never infer it from a display name. |

## Request Contract

Construct this logical request body:

```json
{
  "userInput": "{\"additionalFilters\":[],\"question\":\"<JSON-escaped user question>\",\"extractFiltersFromQuestion\":false}",
  "connectorDetails": {
    "connectorId": "ORA_CX_SALES_PLAY"
  },
  "filters": [
    {
      "fieldName": "contentState",
      "value": "PUBLISHED",
      "operator": "eq"
    },
    {
      "fieldName": "contentTypeAttributes.ORA_CX_SALES_PLAY.SALES_PLAY",
      "value": "<exact Sales Play ID>",
      "operator": "eq"
    }
  ]
}
```

Build the inner `userInput` object first with `additionalFilters` as an empty
array, the exact question, and `extractFiltersFromQuestion` as false. Serialize
that inner object once and assign the resulting JSON string to the outer
`userInput` field. Then serialize the complete outer body. Never interpolate
unescaped question text into JSON or shell syntax.

Keep `ORA_CX_SALES_PLAY`, `PUBLISHED`, both field names, both `eq` operators,
the empty `additionalFilters`, and `extractFiltersFromQuestion=false` fixed.
Replace only the user question and exact Sales Play ID.

## Security Gate

Before the call, read `sales-plays-and-content-security.md` and distinguish:

- a Knowledge authoring administrator, who needs the out-of-box Sales
  Administrator bundle or the custom-role authoring duty and administrator
  data policies; and
- a Content Intelligence end user, whose role needs access to the Sales Play
  Consumer user group and Sales Force Automation department.

Do not claim that the acting user has either policy without authorized
administrator evidence. The requested search may serve as the effective access
check for that one call.

## Result Classification

| Observed Result | Classification | Meaning |
|---|---|---|
| OAuth callback returns `unauthorized_client` | AUTHENTICATION_CONFIGURATION_FAILED | The configured OAuth client or selected `knowledge-management` scope token is not accepted for `/api/knowledge-management`; no Content Intelligence request was sent. |
| HTTP 2xx with an unambiguous returned content result | WORKING_WITH_RESULTS | The endpoint accepted the request and returned content for this user, question, and Sales Play ID. |
| HTTP 2xx with an empty or no-match response | WORKING_NO_RESULTS | The endpoint accepted the request, but no matching published content was returned; do not call this an authorization failure. |
| HTTP 401 | AUTHENTICATION_FAILED | OAuth authentication using the selected `knowledge-management` scope token was not accepted for the Knowledge Management endpoint. |
| HTTP 403 after one cache-managed refresh | AUTHORIZATION_FAILED | The acting user lacks effective access for the request; confirm the applicable Knowledge data security policies. |
| Deterministic HTTP 400 | REQUEST_INVALID | The request body was rejected; report the sanitized error without changing the fixed contract or retrying. |
| Transport failure or another deterministic error | SEARCH_FAILED | Report sanitized environment, endpoint, status, and request identifiers when available. |

For `AUTHENTICATION_CONFIGURATION_FAILED`, stop without retrying and require an
approved OAuth client registration and regular scope that can obtain a token
for the selected `knowledge-management` scope token. Do not substitute a
separate Knowledge Management scope property or a pasted bearer token.

The developer source does not define a response schema. Preserve the sanitized
response shape and classify content as returned only when that is unambiguous;
do not invent field names, relevance thresholds, or result-count semantics.

## Retry and Side-Effect Boundary

Allow the shared client to refresh its cache and retry once after HTTP 401 or
403. Permit one bounded retry only for a known transient read-only transport
failure. Do not retry deterministic request errors, weaken filters, substitute
another Sales Play ID, or submit any write operation.
