# Import Route Safety

## Error Situations

| Situation | What Should Happen |
|---|---|
| The create UOM is omitted and ORA_RCS_HOUR_UOM is missing, unavailable, empty or invalid | Block preview and request a UOM, then validate the supplied code in the selected environment. Report whether the profile lookup returned no usable value or failed; do not claim an inaccessible profile is unset. Never hardcode HRS, choose the class base unit or omit REST UOMCode. |
| A supplied UOM is invalid or inactive | Preserve the requested input in diagnostics and request a corrected UOM. Do not replace it automatically with the hour profile or another unit. |
| REST service validation reports a scheduling-class eligibility error | Surface the service error through core.data-loader, preserve the requested UOM and stop for correction. Do not add a client-side class-profile lookup, change the UOM automatically or retry a live operation without the existing retry safeguards. |
| Final REST UOMCode or its Data Loader mapping is absent, blank, changed or unverified | Block readiness as input_validation; return for source correction and fresh validation and artifact-bound approval. Do not rely on a server default or repair an already approved artifact in place. |
| A prepared REST productionResources parent source contains both OrganizationId and OrganizationCode, even with a blank or null alternative | Block before approval or upload as input_validation. Apply the REST Organization Identity Contract in ora_input_validation.md, rebuild the source with one organization column, then repeat core.data-loader validation and artifact-bound approval. |
| A submitted batch returns 27035, Attribute OrganizationId is required., although its parent payload contains both identifiers | Treat the dual-field shape as the reported workaround case, not proof that the supplied ID is missing. Preserve the failed part and known job status; reconcile partial or uncertain results before any resubmission. Prepare a corrected single-identifier artifact only for confirmed outstanding rows. Do not automatically retry or change to FSM; a changed artifact needs fresh validation and approval under core.data-loader. |
| A REST Data Loader source is requested and productionResources is not confirmed as the exact registered business object | Stop before sample generation, validation, or import and obtain confirmation. |
| REST preflight or read-only metadata validation shows that REST Data Loader cannot support the requested operation | Do not attempt a direct REST call or retry a live import. Use the FSM route only through core.data-loader after an immutable FSM artifact has been validated and the user explicitly approves that exact artifact. |
| REST Data Loader validation or a live operation fails for any other reason | Stop, classify the failure, redact sensitive values, and do not retry a live operation without idempotency or explicit user approval. |
| FSM fallback artifact changes after approval | Invalidate the approval and return to core.data-loader validation for the changed artifact. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input_validation | A REST source business object is not confirmed; organization identifiers conflict or are missing/invalid; a UOM or required hour-profile default is invalid or missing; or the final source violates organization or UOM serialization | Confirm productionResources, request a valid UOM or correct the missing configuration/input/source; rerun validation for a changed artifact. |
| catalog_or_metadata_mismatch | Read-only metadata establishes an unsupported upload operation or an incompatible required lookup contract | Only an unsupported upload operation permits preparation and approval of an FSM artifact through core.data-loader. A profile or UOM lookup contract gap blocks verification in either mode; it does not authorize fallback. |
| auth_expired_or_invalid | Profile or UOM lookup rejects the active cached token | Use only the core client's single allowed refresh; stop if verification still fails. No inferred default. |
| authorization_or_privilege | The workflow identity lacks access to required profile or UOM data | Stop the affected lookup and report the access requirement. A user UOM still requires validation; never change profile securing categories automatically. |
| transport_or_environment | Profile or UOM verification fails due to connectivity, timeout or environment mismatch | Stop and report the selected environment and unresolved lookup. Do not substitute another environment's value or classify the failure as an unset profile. |
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
| MFGRES.ROUTE_REST | decision | 7 | execution_gate | rest_supported->MFGRES.VALIDATE_REST_ORGANIZATION;rest_unsupported->MFGRES.FSM_APPROVAL;fsm_selected->MFGRES.FSM_APPROVAL;business_object_unconfirmed->MFGRES.BLOCKED | MFGRES.DESIGN | stop | A Manufacturing Resources import is requested; use the manifest dataloader_import_mode unless the active workflow records an explicit supported mode override. Organization or UOM validation failure does not establish unsupported REST and must not trigger FSM fallback. |
| MFGRES.REST_READY | terminal | 10 | terminal | none | MFGRES.VALIDATE_REST_UOM | stop | REST Data Loader preflight, metadata validation, and the final artifact's REST organization and UOM checks support the requested operation. |
| MFGRES.FSM_APPROVAL | decision | 11 | execution_gate | approved->MFGRES.FSM_READY;approval_missing->MFGRES.BLOCKED | MFGRES.ROUTE_REST | stop | The manifest default or an explicit supported override selects native FSM and CSVExportImportSupportedFlag is Y, or REST preflight establishes that REST cannot support the requested operation. Validate selected UOM values against the exact native exported UOM mapping; preserve omitted update fields. |
| MFGRES.FSM_READY | terminal | 12 | terminal | none | MFGRES.FSM_APPROVAL | stop | core.data-loader validated an immutable FSM artifact and the user explicitly approved that exact artifact. |
| MFGRES.BLOCKED | terminal | 13 | terminal | none | none | stop | Required input, organization identity, UOM resolution/defaulting or artifact checks, REST business-object confirmation, route determination, or FSM approval are missing or failed. |

## Native FSM selection

| Situation | What Should Happen |
|---|---|
| The manifest default or an explicit supported override selects FSM and the selected task catalog declares CSV export/import supported | MFGRES.ROUTE_REST selects fsm_selected after core.data-loader validates the native task/environment package. Continue to MFGRES.FSM_APPROVAL. Retain exact artifact-bound approval, including same-request auto approval; no REST source conversion or fabricated REST failure is required. REST business-object registration is required only for a REST source; a native FSM source is bound to its exported setup-task metadata instead. |

Source: [Oracle Fusion 26D CSV package import](https://docs.oracle.com/en/cloud/saas/applications-common/26d/oafsm/export-and-import-csv-file-packages.html) and the task catalog CSVExportImportSupportedFlag.
