# Sales Motions Read Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Required read input is missing or invalid | Stop before a BOSS call and show the exact missing or invalid field. |
| A mutation operation is requested | Return unsupported, state that the current skill revision is read-only, and stop without a preview; do not misclassify the exact salesMotions/$query semantic-read POST. |
| LIST or GET receives a cache-managed 401 or 403 | Refresh once through the shared BOSS client and retry once. |
| QUERY receives 401 or 403 | Stop and report the sanitized authentication or authorization failure. The shared BOSS client does not automatically refresh or retry POST; validate a new requested read after the issue is resolved. |
| Explicitly supplied token receives 401 or 403 | Do not replace or reuse it; stop and require the shared OAuth flow. |
| A second 403 occurs after cache-managed refresh | Classify as authorization or privilege failure. |
| GET by exact ID returns 404 | Return a not-found result for that ID without selecting another record. |
| QUERY returns a deterministic 400 for an invalid body or filter | Stop, identify the invalid query field or expression, and do not retry or weaken the filter. |
| A read-only call has a known transient transport failure | Permit one bounded retry and retain environment and endpoint evidence. |
| BOSS returns another deterministic 4xx or 5xx | Stop, disclose sanitized diagnostics, and do not retry automatically. |
| Artifact persistence fails | Preserve redacted diagnostics safely and report the intended project path. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Unsupported operation | The request is create, update, delete, PATCH, PUT, bulk write, or POST to any endpoint other than the exact salesMotions/$query read endpoint. | Use LIST, GET, or QUERY, or wait for a reviewed write-enabled skill revision. |
| Input validation | Environment, operation, exact ID, or query value is missing or invalid. | Correct only the invalid read input and rerun preflight. |
| Authentication | Shared OAuth configuration or token acquisition fails. | Correct the shared OAuth configuration and authenticate again. |
| QUERY authentication or authorization | QUERY returns 401 or 403 without an automatic refresh or retry. | Report the status and sanitized evidence; verify OAuth configuration and effective read access before a new requested read. Do not infer the missing role or permission group. |
| Authorization or privilege | LIST or GET returns a second 403 after cache-managed refresh. | Confirm the read role, read permission groups, and All Rows security view. |
| Not found | GET by exact ID returns 404. | Verify the supplied ID; do not infer or substitute another record. |
| Transport or environment | VPN, DNS, timeout, or service connectivity fails. | Confirm the target environment before one bounded read-only retry. |
| Fusion API | BOSS returns another non-authentication 4xx or 5xx. | Correct the request or environment issue using sanitized response evidence. |
| Artifact persistence | A requested durable read result cannot be written or validated. | Correct the project path without exposing protected response material. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Read preflight | Target environment, LIST, GET, or QUERY, exact ID when applicable, and bounded query parameters or body criteria. |
| Read success | Operation, relative endpoint, record count or exact record result, hasMore when present, and effective read status. |
| Read failure | Operation, relative endpoint, status, redacted response summary, request identifier when available, and confirmed side effects. |
| Unsupported operation | Requested mutation and the fact that no preview or Fusion write was attempted. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Password, Basic credential, bearer token, refresh token, client secret, Authorization header, or token-cache content is supplied | Do not validate, reuse, echo, log, persist, or place it in a command or tracked file. |
| CREATE, UPDATE, DELETE, PATCH, PUT, bulk write, or POST outside the exact salesMotions/$query read endpoint is requested | Do not build a preview, request approval, or call Fusion. |
| An exact GET ID is absent or ambiguous | Do not infer an ID from display text. |
| Target release contract differs from the verified 26C read paths or fields | Do not infer the contract; obtain the target-release OpenAPI source. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| SM.SELECT_READ | decision | 3 | execution_gate | list->SM.LIST;get->SM.GET;query->SM.QUERY;blocked->SM.ERROR;unsupported->SM.ERROR | SM.ACCESS | stop | Environment and authentication dependencies are ready; select LIST, GET, or QUERY only. |
| SM.LIST_DONE | terminal | 7 | terminal | none | SM.LIST | stop | The LIST result was returned successfully, including an empty list. |
| SM.GET_DONE | terminal | 8 | terminal | none | SM.GET | stop | The exact Sales Motion was returned successfully. |
| SM.NOT_FOUND | terminal | 9 | terminal | none | SM.GET | stop | No Sales Motion exists for the exact supplied ID. |
| SM.QUERY_DONE | terminal | 10 | terminal | none | SM.QUERY | stop | The bounded QUERY result was returned successfully, including an empty list. |
| SM.ERROR | terminal | 99 | terminal | none | none | stop | The request was unsupported, invalid, unauthorized, or failed. |
