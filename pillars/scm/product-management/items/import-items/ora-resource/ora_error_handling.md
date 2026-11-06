# Error Handling

## Error Situations

| Situation | Required action |
|---|---|
| Item-index lookup returns HTTP 404 and the response body contains errorCode FND_ERROR_SEARCH_SERVICE_UNKNOWN_INDEXES | End this task with index_remediation_required. Do not prepare or import items, retry this GET, or treat the dependency as passed. Product Management orchestration owns the separate remediation-task selection and any later fresh readiness lookup. |
| Item-index lookup returns any result other than a valid zero-result HTTP 200 search response or the documented matching HTTP 404 condition | Stop, classify the failure, and report the target environment, operation, stage, sanitized response, and one safe next action. Do not bypass or retry the dependency check automatically. |
| Source is unreadable, ambiguous, or missing required values | Stop before CSV generation and request the smallest clarification. |
| Current public template cannot be fetched or differs from the local contract | Stop as template drift; do not use a stale layout. |
| CSV or ZIP validation fails | Discard the incomplete transient artifact and regenerate after correcting the local issue. |
| ZIP changes after validation | Restart template-driven validation and produce new handoff evidence. |
| Handoff metadata is incomplete | Stop before handing the ZIP to `core.data-loader`. |
| Core Data Loader cannot validate `item` as a highest-scoring live FBDI route for the ZIP CSV filenames | Let core.data-loader stop before approval or upload; retain its route diagnostic and correct the archive or live metadata before a new validation cycle. |

Classify item-index lookup failures as authentication, authorization,
transport/environment, or Fusion API failures. Classify the remaining local
failures as input validation, catalog mismatch, or artifact persistence. This
skill performs only the documented read-only Fusion Search GET; it does not
upload, import, invoke ESS, or perform a Fusion mutation. core.data-loader
handles any later execution failure in its own workflow.

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input_validation | Source, template provenance, mapping, ZIP shape, Batch ID, or handoff metadata is missing or invalid | Stop before handoff, identify the exact invalid field or artifact property, and correct it before a new validation cycle. |
| catalog_or_metadata_mismatch | Task identity, template contract, member name, member order, or registered business object conflicts with the current catalog or template | Stop and reconcile the authoritative catalog or current template; do not select a close match. |
| auth_expired_or_invalid | The core REST client receives 401 or 403 from a cache-managed session | Permit one core-client token refresh; stop after a second authentication response. Do not replace an explicitly supplied token. |
| authorization_or_privilege | Fusion rejects the lookup after refresh or the required privilege is absent | Stop and report the missing access or privilege without retry. |
| transport_or_environment | DNS, VPN, connection, trusted-host, timeout, or environment validation fails | Stop with environment, operation, stage, elapsed time, sanitized diagnostic, and one safe next action. Do not automatically replay the GET after an uncertain result. |
| fusion_api_error | Fusion returns an HTTP error other than the documented unknown-index branch | Stop with HTTP status, endpoint path, sanitized response summary, ECID when available, and recommended action. |
| artifact_persistence | A transient destination is unsafe or unwritable, or a local artifact cannot be created, reopened, validated, or removed | Stop, preserve only sanitized diagnostics, and select a controlled writable transient location before restarting. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Lookup failure | Target environment identity, operation, stage, HTTP status when available, endpoint path, ECID when available, sanitized message, and one safe next action. |
| Template or mapping failure | Public template provenance, affected sheet or source field, failure class, sanitized issue, and correction required; never show raw customer rows. |
| ZIP validation failure | Artifact basename, digest, affected member, failed invariant, and regeneration action; never show member contents or full payloads. |
| Timeout | Environment, operation, stage, elapsed time, last status, and next-check guidance. |
| Final task result | Machine-readable status ready, blocked, or failed; failure class; stage; sanitized message; recommended action; artifact references; and available HTTP status or ECID. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Sensitive material is present | Do not print or persist credentials, tokens, authorization headers, token-cache contents, secrets, private keys, certificates, full base64 content, raw customer rows, complete payloads, or unsanitized response bodies. |
| Lookup route is unavailable or ambiguous | Do not call the Fusion endpoint directly or substitute another endpoint; stop until core.fusion-api.rest-api-client and the documented route are available. |
| Retry would follow an uncertain GET or handoff | Do not retry automatically. A later live loader operation remains exclusively governed by core.data-loader. |
| Template contract or archive changed | Do not reuse prior preview, digest, validation, or handoff evidence; restart the complete validation cycle. |
| Destination is tracked, outside the controlled transient location, or unsafe | Do not create or copy customer-bearing CSV, ZIP, or workbook artifacts there. |
| Required source guidance is missing | Do not invent or apply a default; require an explicit customer value or authoritative source evidence. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ITEM_IMPORT.HANDOFF_GATE | decision | 5 | execution_gate | ready->ITEM_IMPORT.READY_FOR_CORE_DATA_LOADER;blocked->ITEM_IMPORT.FAILED | ITEM_IMPORT.CONFIRM_LOADER_ROUTE | stop | Immediately before handing the unchanged validated ZIP to core.data-loader. |
| ITEM_IMPORT.READY_FOR_CORE_DATA_LOADER | terminal | 6 | terminal | none | ITEM_IMPORT.HANDOFF_GATE | continue | Local validation and immutable handoff evidence are complete. |
| ITEM_IMPORT.INDEX_REMEDIATION_REQUIRED | terminal | 7 | terminal | none | ITEM_IMPORT.CHECK_ITEM_INDEX | stop | The Item Index is unavailable. Return the index-remediation handoff to Product Management orchestration; do not continue Import Items. |
| ITEM_IMPORT.FAILED | terminal | 8 | terminal | none | none | continue | Any item-index lookup, local validation, template, or artifact-persistence failure occurs. |
