# Data Capture Rules Read Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Required read input is missing or invalid | Stop before a BOSS call and show the exact missing or invalid field. |
| A mutation operation is requested | Return unsupported, state that the current skill revision is read-only, and stop without a preview; do not misclassify the exact dataCaptureRules/$query semantic-read POST. |
| A request asks to create, generate, draft, or sample a Data Capture Rule or local blueprint | Return UNSUPPORTED within this skill. Do not route to the parent skill, generate an artifact or payload, request approval, authenticate, or call Fusion. |
| A LIST or QUERY equality filter uses OData eq, double-quoted literals, pre-encoded text, or lacks the BOSS double parentheses | Fail input validation before Fusion. Normalize to ((field = 'value')) only when the user's field, operator, and value are unambiguous. |
| A QUERY body wraps the documented fields in query, payload, or data | Fail input validation before Fusion and require one top-level query object with collection.filter and collection.limit. |
| LIST or GET receives a cache-managed 401 or 403 | Refresh once through the shared BOSS client and retry once. |
| QUERY receives 401 or 403 | Stop and report the sanitized authentication or authorization failure. The shared BOSS client does not automatically refresh or retry POST; validate a new requested read after the issue is resolved. |
| Explicitly supplied credential or token receives 401 or 403 | Do not validate, replace, or reuse it; stop and require the shared OAuth flow. |
| A second 403 occurs after cache-managed refresh | Classify as authorization or privilege failure. |
| GET by exact ID returns 404 | Return a not-found result for that ID without selecting another record. |
| QUERY returns a deterministic 400 for an invalid body or filter | Stop, identify the invalid query field or expression, and do not retry or weaken the filter. |
| A read-only call has a known transient transport failure | Permit one bounded retry and retain environment and endpoint evidence. |
| BOSS returns another deterministic 4xx or 5xx | Stop, disclose sanitized diagnostics, and do not retry automatically. |
| Artifact persistence fails | Preserve redacted diagnostics safely and report the intended project path. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Unsupported operation | The request is create, update, delete, PATCH, PUT, bulk write, sample or blueprint generation, or POST to any endpoint other than the exact dataCaptureRules/$query read endpoint. | Return UNSUPPORTED within this skill without routing or artifact generation; use LIST, GET, or QUERY, or wait for a reviewed write-enabled skill revision. |
| Input validation | Environment, operation, exact ID, or query value is missing or invalid. | Correct only the invalid read input and rerun preflight. |
| Authentication | Shared OAuth configuration or token acquisition fails. | Correct the shared OAuth configuration and authenticate again. |
| QUERY authentication or authorization | QUERY returns 401 or 403 without an automatic refresh or retry. | Report the status and sanitized evidence; verify OAuth configuration and effective read access before a new requested read. Do not infer the missing role or permission group. |
| Authorization or privilege | LIST or GET returns a second 403 after cache-managed refresh. | Confirm the read role, four read permission groups, and All Rows security view. |
| Not found | GET by exact ID returns 404. | Verify the supplied ID; do not infer or substitute another record. |
| Transport or environment | VPN, DNS, timeout, or service connectivity fails. | Confirm the target environment before one bounded read-only retry. |
| Fusion API | BOSS returns another non-authentication 4xx or 5xx. | Correct the request or environment issue using sanitized response evidence. |
| Artifact persistence | A requested durable read result cannot be written or validated. | Correct the project path without exposing protected response material. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Read preflight | Target environment, LIST, GET, or QUERY, exact ID when applicable, and bounded query parameters or body criteria. |
| Read success | Operation, relative endpoint, record count or exact record result, hasMore and totalItems when present, and effective read status. |
| Read failure | Operation, relative endpoint, status, redacted response summary, request identifier when available, and confirmed side effects. |
| Unsupported operation | Requested mutation and the fact that no parent routing, blueprint, payload, preview, authentication, or Fusion write was attempted. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Password, Basic credential, bearer token, refresh token, client secret, Authorization header, credential-bearing token command, or token-cache content is supplied | Do not validate, execute, reuse, echo, log, persist, or place it in a command or tracked file. |
| CREATE, UPDATE, DELETE, PATCH, PUT, bulk write, sample or blueprint generation, or POST outside the exact dataCaptureRules/$query read endpoint is requested | Do not route to the parent skill, create a blueprint or payload, build a preview, request approval, authenticate, or call Fusion. |
| An exact GET ID is absent or ambiguous | Do not infer an ID from display text. |
| Target release contract differs from the verified 26C read paths or fields | Do not infer the contract; obtain the target-release OpenAPI source. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DCR.SELECT_READ | decision | 3 | execution_gate | list->DCR.LIST;get->DCR.GET;query->DCR.QUERY;blocked->DCR.ERROR;unsupported->DCR.ERROR | DCR.ACCESS | stop | Environment and authentication dependencies are ready; select LIST, GET, or QUERY only. |
| DCR.LIST_DONE | terminal | 7 | terminal | none | DCR.LIST | stop | The LIST result was returned successfully, including an empty list. |
| DCR.GET_DONE | terminal | 8 | terminal | none | DCR.GET | stop | The exact Data Capture Rule was returned successfully. |
| DCR.NOT_FOUND | terminal | 9 | terminal | none | DCR.GET | stop | No Data Capture Rule exists for the exact supplied ID. |
| DCR.QUERY_DONE | terminal | 10 | terminal | none | DCR.QUERY | stop | The bounded QUERY result was returned successfully, including an empty list. |
| DCR.ERROR | terminal | 99 | terminal | none | none | stop | The request was unsupported, invalid, unauthorized, or failed. |
