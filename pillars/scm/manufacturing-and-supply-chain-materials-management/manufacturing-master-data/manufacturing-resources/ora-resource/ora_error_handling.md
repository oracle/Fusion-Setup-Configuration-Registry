# Import Route Safety

## Error Situations

| Situation | What Should Happen |
|---|---|
| A REST Data Loader source is requested and productionResources is not confirmed as the exact registered business object | Stop before sample generation, validation, or import and obtain confirmation. |
| REST preflight or read-only metadata validation shows that REST Data Loader cannot support the requested operation | Do not attempt a direct REST call or retry a live import. Use the FSM route only through core.data-loader after an immutable FSM artifact has been validated and the user explicitly approves that exact artifact. |
| REST Data Loader validation or a live operation fails for any other reason | Stop, classify the failure, redact sensitive values, and do not retry a live operation without idempotency or explicit user approval. |
| FSM fallback artifact changes after approval | Invalidate the approval and return to core.data-loader validation for the changed artifact. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input_validation | A REST source business object is not confirmed | Confirm productionResources before proceeding. |
| catalog_or_metadata_mismatch | Read-only REST metadata establishes that the requested operation is unsupported | Prepare and validate an FSM artifact through core.data-loader, then obtain explicit approval. |
| fusion_api_error | REST validation or execution reports an API failure | Stop and report redacted diagnostics; do not automatically retry a live operation. |
| approval_blocker | FSM fallback has not been explicitly approved for the exact immutable artifact | Wait for explicit approval. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| REST-to-FSM fallback | The REST preflight or metadata finding, the exact immutable FSM artifact, the target environment, and the requested FSM operation before approval. |
| Failure report | Failure class, safe diagnostic summary, current route, and next action; never tokens, credentials, or raw sensitive payloads. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Any Manufacturing Resources import | Do not bypass core.data-loader with direct REST, FSM, upload, or import execution. |
| REST is unavailable or unsupported | Do not silently switch to FSM. |
| Uncertain or failed live import | Do not automatically retry the live operation. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MFGRES.ROUTE_REST | decision | 4 | execution_gate | rest_supported->MFGRES.REST_READY;rest_unsupported->MFGRES.FSM_APPROVAL;fsm_selected->MFGRES.FSM_APPROVAL;business_object_unconfirmed->MFGRES.BLOCKED | MFGRES.DESIGN | stop | A Manufacturing Resources import is requested; use the manifest dataloader_import_mode unless the active workflow records an explicit supported mode override. |
| MFGRES.REST_READY | terminal | 5 | terminal | none | MFGRES.ROUTE_REST | stop | REST Data Loader preflight and metadata validation support the requested operation. |
| MFGRES.FSM_APPROVAL | decision | 6 | execution_gate | approved->MFGRES.FSM_READY;approval_missing->MFGRES.BLOCKED | MFGRES.ROUTE_REST | stop | The manifest default or an explicit supported override selects native FSM and CSVExportImportSupportedFlag is Y, or REST preflight establishes that REST cannot support the requested operation. |
| MFGRES.FSM_READY | terminal | 7 | terminal | none | MFGRES.FSM_APPROVAL | stop | core.data-loader validated an immutable FSM artifact and the user explicitly approved that exact artifact. |
| MFGRES.BLOCKED | terminal | 8 | terminal | none | none | stop | A required REST business-object confirmation, route determination, or FSM approval is missing. |

## Native FSM selection

| Situation | What Should Happen |
|---|---|
| The manifest default or an explicit supported override selects FSM and the selected task catalog declares CSV export/import supported | MFGRES.ROUTE_REST selects fsm_selected after core.data-loader validates the native task/environment package. Continue to MFGRES.FSM_APPROVAL. Retain exact artifact-bound approval, including same-request auto approval; no REST source conversion or fabricated REST failure is required. REST business-object registration is required only for a REST source; a native FSM source is bound to its exported setup-task metadata instead. |

Source: [Oracle Fusion 26D CSV package import](https://docs.oracle.com/en/cloud/saas/applications-common/26d/oafsm/export-and-import-csv-file-packages.html) and the task catalog CSVExportImportSupportedFlag.
