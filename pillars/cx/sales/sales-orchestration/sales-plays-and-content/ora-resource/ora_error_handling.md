# Sales Plays and Content Read Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Required read input is missing or invalid | Stop before a Fusion call and show the exact missing or invalid field. |
| An explicit salesPlayType is not SALES_PLAY or CONTENT_BUNDLE | Stop before a Fusion call, show the unsupported type, and list the two accepted canonical values. |
| GET returns the exact requested ID with a salesPlayType different from the explicitly expected type | Return the record with a type-mismatch diagnostic; do not substitute another record or reinterpret its type. |
| A mutation operation is requested | Return unsupported, state that the current skill revision is read-only, and stop without a preview; do not misclassify the exact salesPlays/$query or /api/knowledge-management/v2/contentIntelligence semantic-read POST. |
| LIST or GET receives a cache-managed 401 or 403 | Refresh once through the shared BOSS client and retry once. |
| QUERY receives 401 or 403 | Stop and report the sanitized authentication or authorization failure. The shared BOSS client does not automatically refresh or retry POST; validate a new requested read after the issue is resolved. |
| CONTENT_SEARCH receives a cache-managed 401 or 403 | Refresh once through the Knowledge Management wrapper and retry the semantic read once. |
| Explicitly supplied credential or token receives 401 or 403 | Do not validate, replace, or reuse it; stop and require the shared OAuth flow. |
| The OAuth callback returns unauthorized_client after the `knowledge-management` scope token is selected from regular `scope` | Stop without retrying; classify the configured OAuth client or selected scope token as not accepted for `/api/knowledge-management`, and record that no Content Intelligence request was sent. |
| A second 403 occurs after cache-managed refresh | Classify as authorization or privilege failure. |
| GET by exact ID returns 404 | Return a not-found result for that ID without selecting another record. |
| LIST returns deterministic 400 for $filter or $sortBy | Stop, report the rejected raw expression and sanitized trace identifier, classify missing or drifted grammar as catalog mismatch, and do not retry or broaden the request. |
| QUERY returns a deterministic 400 for an invalid body, accessor, or filter | Stop, identify the invalid query field or expression, and do not retry or weaken the request. |
| CONTENT_SEARCH returns a deterministic 400 | Stop, report the sanitized body error, and do not retry, alter the fixed connector or filters, or substitute another Sales Play ID. |
| CONTENT_SEARCH returns HTTP 2xx without an unambiguous content result | Return WORKING_NO_RESULTS; distinguish successful request execution from a positive content match. |
| A read-only call has a known transient transport failure | Permit one bounded retry and retain environment and endpoint evidence. |
| Fusion returns another deterministic 4xx or 5xx | Stop, disclose sanitized diagnostics, and do not retry automatically. |
| Artifact persistence fails | Preserve redacted diagnostics safely and report the intended project path. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Unsupported operation | The request is create, update, delete, PATCH, PUT, bulk write, or POST to an endpoint other than the exact salesPlays/$query or /api/knowledge-management/v2/contentIntelligence semantic-read endpoint. | Use LIST, GET, QUERY, or CONTENT_SEARCH, or wait for a reviewed write-enabled skill revision. |
| Input validation | Environment, operation, exact ID, salesPlayType, field, accessor, enum, query value, Content Intelligence question, or Content Intelligence Sales Play ID is missing or invalid. | Correct only the invalid read input and rerun preflight. |
| Catalog mismatch | Documented or generated LIST query grammar is rejected while a source-backed runtime form differs. | Stop without retry, preserve the sanitized failing expression and trace identifier, update the skill from authorized evidence, and start a new requested read only after validation. |
| Authentication | Applicable shared BOSS or Knowledge Management OAuth configuration or token acquisition fails. | Correct the applicable OAuth configuration and authenticate again. |
| OAuth client registration | The authorization callback returns unauthorized_client for the selected `knowledge-management` scope token before CONTENT_SEARCH is sent. | Have the identity administrator approve the OAuth client and regular `scope` property for the selected `knowledge-management` token, or provide the approved client configuration; do not substitute a separate Knowledge Management scope property or a pasted bearer token. |
| QUERY authentication or authorization | QUERY returns 401 or 403 without an automatic refresh or retry. | Report the status and sanitized evidence; verify OAuth configuration and effective read access before a new requested read. Do not infer the missing role or permission group. |
| Authorization or privilege | LIST or GET returns a second 403 after cache-managed refresh. | Confirm the read role, four read permission groups, and All Rows security view. |
| Knowledge data security | CONTENT_SEARCH returns a second 403 after cache-managed refresh. | Confirm access to the Sales Play Consumer user group and Sales Force Automation department for the acting end-user role. |
| Not found | GET by exact ID returns 404. | Verify the supplied ID; do not infer or substitute another record. |
| Transport or environment | VPN, DNS, timeout, or service connectivity fails. | Confirm the target environment before one bounded read-only retry. |
| Fusion API | BOSS or Content Intelligence returns another non-authentication 4xx or 5xx. | Correct the request or environment issue using sanitized response evidence. |
| Artifact persistence | A requested durable read result cannot be written or validated. | Correct the project path without exposing protected response material. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Read preflight | Target environment, LIST, GET, QUERY, or CONTENT_SEARCH; acting user; exact ID when applicable; normalized salesPlayType only when explicitly requested; and bounded query parameters, content accessors, or fixed Content Intelligence criteria. |
| Read success | Operation, relative endpoint, record count or exact record result, salesPlayType for returned BOSS records, requested content result, hasMore and totalItems when present, Content Intelligence classification when applicable, and effective read status. |
| Read failure | Operation, relative endpoint, status, rejected raw query expression when safe, redacted response summary, traceId or request identifier when available, and confirmed side effects. |
| Unsupported operation | Requested mutation and the fact that no preview or Fusion write was attempted. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Password, Basic credential, bearer token, refresh token, client secret, Authorization header, credential-bearing token command, or token-cache content is supplied | Do not validate, execute, reuse, echo, log, persist, or place it in a command or tracked file. |
| CREATE, UPDATE, DELETE, PATCH, PUT, bulk write, or POST outside the exact salesPlays/$query and /api/knowledge-management/v2/contentIntelligence semantic-read endpoints is requested | Do not build a preview, request approval, or call Fusion. |
| An exact GET ID is absent or ambiguous | Do not infer an ID from display text. |
| A supplied record type cannot be normalized to SALES_PLAY or CONTENT_BUNDLE | Do not call Fusion, silently drop the type, or broaden the request to both types. |
| A CONTENT_SEARCH question or Sales Play ID is absent or ambiguous | Do not infer either value, weaken the fixed filters, or call Fusion. |
| Target release contract differs from the verified 26C read paths, fields, accessors, or enums | Do not infer the contract; obtain the target-release OpenAPI source. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| SPC.SELECT_READ | decision | 3 | execution_gate | list->SPC.LIST;get->SPC.GET;query->SPC.QUERY;content_search->SPC.CONTENT_SEARCH;blocked->SPC.ERROR;unsupported->SPC.ERROR | SPC.ACCESS | stop | Environment and authentication dependencies are ready; select LIST, GET, QUERY, or CONTENT_SEARCH only. |
| SPC.LIST_DONE | terminal | 7 | terminal | none | SPC.LIST | stop | The LIST result was returned successfully, including an empty list. |
| SPC.GET_DONE | terminal | 8 | terminal | none | SPC.GET | stop | The exact Sales Play or content bundle record was returned successfully, with any expected-type mismatch disclosed. |
| SPC.NOT_FOUND | terminal | 9 | terminal | none | SPC.GET | stop | No record exists for the exact supplied ID. |
| SPC.QUERY_DONE | terminal | 10 | terminal | none | SPC.QUERY | stop | The bounded QUERY result was returned successfully, including an empty list. |
| SPC.CONTENT_SEARCH_DONE | terminal | 12 | terminal | none | SPC.CONTENT_SEARCH | stop | The CONTENT_SEARCH result was returned as WORKING_WITH_RESULTS or WORKING_NO_RESULTS. |
| SPC.ERROR | terminal | 99 | terminal | none | none | stop | The request was unsupported, invalid, unauthorized, or failed. |
