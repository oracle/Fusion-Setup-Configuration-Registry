# Import Route Safety

## Error Situations

| Situation | What Should Happen |
|---|---|
| Required domain evidence is absent, stale, inconsistent, incomplete or unavailable | Stop before preview at MRINST.BLOCKED; identify the missing resolver or reviewed-input fact, retain a sanitized reason and safe resume node. Never mark metadata validation as domain success or defer a required preflight check to import. |
| A REST source is selected and productionResources is not confirmed as the registered parent Data Loader business object | Stop before sample generation, validation, or import and obtain confirmation. |
| Parent ResourceId, or ResourceCode and OrganizationCode pair, does not resolve to one active resource | Stop before selecting a child route and request a valid parent identifier or a complete exact code-and-organization pair. |
| Parent ResourceId conflicts with the supplied ResourceCode and OrganizationCode | Stop before selecting a child route and correct the conflicting parent identity. |
| productionResources collection lookup fails or the single limit=1 response does not return an exact active ResourceId | Stop before selecting a child route, preserve redacted diagnostics, and correct the documented collection request or parent identity; do not advance offset. |
| Parent ResourceType is neither EQUIPMENT nor LABOR | Stop before child payload preparation and request correction or clarification. |
| Equipment child is requested for a LABOR parent or labor child is requested for an EQUIPMENT parent | Stop and select the child collection that matches the parent ResourceType. |
| REST Data Loader package populates the root section, both child resources, or the child resource that does not match ResourceType | Stop before upload and rebuild the child-only package with EquipmentInstance for EQUIPMENT or LaborInstance for LABOR. |
| Data Loader Business Object Validation returns HTTP 502 | Treat the response as a Fusion transport or environment failure. The generic source-alignment message is not evidence of a child-resource mismatch; preserve redacted diagnostics and do not retry automatically. |
| Inactive date is not future or exceeds the parent resource inactive date | Stop and supply a valid future date within the parent lifecycle. |
| A create, update, or delete targets an inactive parent resource | Stop; reactivate or select an active parent resource before proceeding. |
| An update targets an inactive resource instance without changing InactiveDate | Stop and use the allowed inactive-date handling path. |
| A LABOR create or update is requested while Workforce Scheduling is enabled | Stop and use the supported Workforce Scheduling process or resolve the prerequisite. |
| An EQUIPMENT asset is ineligible or already associated | Stop and select an active, in-plant, work-center asset not actively associated elsewhere. |
| A LABOR party is ineligible, duplicate, or conflicts with primary-resource uniqueness | Stop and select an eligible unique person association. |
| Person, Person Name, or Party Name is supplied without PartyId or RegistryId and laborResourceInstancesLOV returns no exact PartyName match, multiple matches, or a blank PartyId | Stop before payload preparation and request a more specific person name, PartyId, or RegistryId. |
| Delete targets an instance used in work execution or an equipment instance assigned to a workstation | Stop; remove the dependent usage or workstation association before a separately approved delete. |
| REST preflight or metadata validation shows the selected child operation is unsupported | Do not attempt a direct REST call or retry a live import. Use FSM only through core.data-loader after validating an immutable FSM artifact and obtaining explicit approval. |
| REST validation or live import fails for another reason | Stop, classify the failure, redact diagnostics, and do not retry a live import without idempotency or explicit approval. |
| An approved FSM artifact changes | Invalidate approval and restart Core Data Loader validation for the changed artifact. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input_validation | Parent ResourceId, or a complete exact ResourceCode and OrganizationCode pair, or a compatible ResourceType is missing | Supply a valid parent resource identity. |
| input_validation | Child type, inactive date, primary work center, asset, person association, or PartyName derivation fails validation | Correct the supplied child data and rerun read-only validation. |
| catalog_or_metadata_mismatch | REST metadata establishes that the selected child operation is unsupported | Prepare and validate the FSM artifact through core.data-loader, then obtain approval. |
| fusion_api_error | REST validation or execution reports an API failure | Stop and report redacted diagnostics; do not retry automatically. |
| transport_or_environment | Data Loader Business Object Validation returns HTTP 502 without a business diagnostic | Wait for service recovery, then restart the Data Loader validation and approval cycle; do not infer a source mapping error or retry automatically. |
| fusion_api_error | The productionResources collection lookup fails or the single limit=1 response omits an exact active ResourceId | Correct the collection request or parent identity before another parent lookup; do not advance offset. |
| approval_blocker | The immutable REST or FSM import artifact is not approved | Wait for approval of the exact artifact. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Parent and labor-person route selection | Parent identity source, derived or supplied ResourceId, returned ResourceType, selected child collection, PartyName lookup result when used, and validation result. |
| Native FSM selection | The selected manifest mode or explicit override, catalog support, validated target-exported package, parent/type and domain evidence, exact immutable artifact, target and requested operation before approval; no REST failure is required. |
| REST-to-FSM fallback | The REST metadata finding, exact immutable FSM artifact, target environment, and requested operation before approval. |
| Failure report | Failure class, safe diagnostic summary, current route, and next action; never tokens, credentials, or raw sensitive payloads. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Any Manufacturing Resource Instances import | Do not bypass core.data-loader with direct REST, FSM, upload, or import execution. |
| Parent ResourceType is unresolved or incompatible | Do not choose a child collection by inference. |
| REST is unavailable or unsupported | Do not silently switch to FSM. |
| Uncertain or failed live import | Do not automatically retry the live operation. |
| Data Loader Business Object Validation returns HTTP 502 | Do not treat the generic source-alignment response as proof that the wrong child resource was selected. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MRINST.ROUTE_REST | decision | 10 | execution_gate | equipment_rest_supported->MRINST.EQUIPMENT_READY;labor_rest_supported->MRINST.LABOR_READY;rest_unsupported->MRINST.FSM_APPROVAL;fsm_selected->MRINST.FSM_APPROVAL;resource_type_invalid->MRINST.BLOCKED | MRINST.DESIGN | stop | All parent and domain checks have passed. Select the manifest dataloader_import_mode unless an explicit supported override is recorded: native FSM selects fsm_selected after task/package validation; REST retains its preflight and child metadata checks. |
| MRINST.EQUIPMENT_READY | terminal | 11 | terminal | none | MRINST.ROUTE_REST | stop | The parent ResourceType is EQUIPMENT and core.data-loader validated productionResources/{ResourceId}/child/EquipmentInstance. |
| MRINST.LABOR_READY | terminal | 12 | terminal | none | MRINST.ROUTE_REST | stop | The parent ResourceType is LABOR and core.data-loader validated productionResources/{ResourceId}/child/LaborInstance. |
| MRINST.FSM_APPROVAL | decision | 13 | execution_gate | approved->MRINST.FSM_READY;approval_missing->MRINST.BLOCKED | MRINST.ROUTE_REST | stop | The manifest default or an explicit supported override selects native FSM and CSVExportImportSupportedFlag is Y, or REST metadata proves the selected child operation is unsupported. |
| MRINST.FSM_READY | terminal | 14 | terminal | none | MRINST.FSM_APPROVAL | stop | core.data-loader validated the immutable FSM artifact and the user explicitly approved it, including artifact-bound same-request auto approval through the core workflow. |
| MRINST.BLOCKED | terminal | 15 | terminal | none | none | stop | A required identity, applicable domain evidence, child route, metadata contract, or approval is missing or failed. |
