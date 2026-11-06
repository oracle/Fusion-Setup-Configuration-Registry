# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| The prompt has no one exact supported connector type and connector name | Stop and request the missing or ambiguous value. |
| BOSS OAuth cannot be acquired or is rejected | Classify as authentication or authorization; return sanitized diagnostics and stop before the query. |
| The seeded-connector query returns an empty collection | Report that no ready predefined data source matched and ask the user to complete setup through the Fusion UI. Do not create a seeded connector from this task. |
| The seeded response is malformed or lacks usable record identity | Block readiness, return sanitized input-validation diagnostics, and do not infer setup from hasMore or total count. |
| The BOSS query returns a deterministic 4xx or 5xx | Classify as Fusion API; return sanitized diagnostics and do not retry automatically. |
| OpenAPI response schema cannot produce extraction attributes | Stop; correct the documentation-backed response schema and regenerate the REST-operation contract before creating a revised approval artifact. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Connector type or connector name is missing or ambiguous | Request one exact value. |
| Seeded connector not set up | The query returns an empty collection | Stop and ask the user to complete setup through the Fusion UI; do not infer absence of pending connectors or invent a connector ID. |
| Authentication or authorization | boss_scope cannot be acquired or is rejected | Correct the BOSS OAuth configuration or read privilege. |
| Transport or environment | BOSS endpoint connectivity fails | Confirm the target environment before one bounded read-only retry. |
| Fusion API | BOSS returns another 4xx or 5xx | Correct the request or environment issue using sanitized response evidence. |
| OpenAPI extraction schema gap | A selected successful JSON response has no derivable extraction attributes | Correct the OpenAPI response schema and regenerate REST Operations. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| EPMDS.HANDLE_ISSUE | step | 50 | error_handler | handled->EPMDS.RETURN_ISSUES | none | stop | Any input, BOSS authentication, transport, or API issue |
| EPMDS.RETURN_ISSUES | terminal | 60 | terminal | none | none | stop | A blocking issue was classified and disclosed |
| EPMDS.SEEDED_CONNECTOR_MISSING | terminal | 80 | terminal | none | EPMDS.ENFORCE_DESIGN | stop | No ready predefined data source matched; request UI setup and stop downstream preparation |
| EPMDS.OPENAPI_READY | terminal | 100 | terminal | none | EPMDS.VALIDATE_RESPONSE_SCHEMA | stop | OpenAPI response schemas are extraction-ready and connector preparation may continue |
| EPMDS.HANDLE_OPENAPI_SCHEMA_ISSUE | step | 105 | error_handler | handled->EPMDS.RETURN_OPENAPI_SCHEMA_ISSUE | none | stop | OpenAPI response schema validation failed |
| EPMDS.RETURN_OPENAPI_SCHEMA_ISSUE | terminal | 110 | terminal | none | none | stop | A blocking OpenAPI extraction schema issue was classified and disclosed |
