---
task_code: "ORA_SVC_SERVICE_REQUEST_STATUS"
task_name: "Manage Service Request Status Values"
parent_skill_id: "cx.service.service-request"
pillar: "CX"
offering: "Service"
functional_area: "Service Request"
functional_area_code: "ORA_SVC_SERVICE_REQUEST"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
---

# Manage Service Request Status Values

## Setup Task Metadata

- Task name: `Manage Service Request Status Values`
- Task code: `ORA_SVC_SERVICE_REQUEST_STATUS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`


## Redirect To Skill

### Manage Standard Lookups

- Task code: FND_MANAGE_STANDARD_LOOKUPS
- Applies when: Creating a status lookup code or changing its Meaning, Description, enabled state, active dates, or other lookup-code fields under ORA_SVC_SR_STATUS_CD.
- Requirement: Acquire and validate a separate standard-lookup FSM package through prepare_service_request_status_lookup_package. Complete the approved lookup-code import before importing a dependent SR parent mapping; never add standard-lookup objects to the mapping-only SR export.
## FSM Contract

- `baseline_requirement`: The inspected completed ORA_SVC_SERVICE_REQUEST_STATUS export declares only ORA_SVC_LOOKUP_CODE_RELS at /LookupCodeRelationVO/LookupCodeRelationVORow, node sequence 1. Validate every fresh export against its own ASM_SETUP_CSV_METADATA.xml. Missing standard-lookup objects are outside this mapping package contract, not missing SR templates. Obtain any lookup-code package separately through FND_MANAGE_STANDARD_LOOKUPS and require its own structural evidence.

### ORA_SVC_LOOKUP_CODE_RELS

- `ChildLookupCode`: Set to the approved Service Request status lookup code.
- `ParentLookupCode`: Resolve the approved ParentLookupCode from the Service Request Statuses LOV rows through core.fusion-api.rest-api-client using the read contract in view_service_request_status_values, with ParentLookupType fixed to ORA_SVC_SR_STATUS_TYPE_CD. Stop if the requested parent cannot be resolved unambiguously. Leave blank only when same-task export evidence permits a status without a parent relationship.
- `RelationCode`: Set to ORA_SVC_STATUS_TYPE_STATUS.
- `ChildLookupType`: Set to ORA_SVC_SR_STATUS_CD.
- `LookupTypeRelationRelationCode`: Set to ORA_SVC_STATUS_TYPE_STATUS.
- `ChildLookupCodeMeaning`: Set to the selected status lookup's Meaning; preserve the exported value for an existing relationship unless an approved lookup-code Meaning change has been separately imported and verified.
- `EnabledFlag`: Set to Y to enable or N to deactivate the status relationship. Retain the exported value for an existing relationship unless an approved enabled-state change is supported by same-task package evidence.
- `DisplaySequence`: Set to the status display sequence. Leave blank only when no display sequence is supplied and same-task package evidence permits it.
- `ParentLookupType`: Set to ORA_SVC_SR_STATUS_TYPE_CD.
## Purpose

Manage the status values and parent-status relationships used by Service Requests.
## Use Cases

### Prepare Service Request Status Lookup Package

Obtain the standard-lookup package structure required for status definition changes.

1. Preflight the active project workflow, target environment, privileges, effective-catalog flags, and workspace paths for Manage Standard Lookups (FND_MANAGE_STANDARD_LOOKUPS).
2. Use core.fusion-api.apps-common.lookups with the Standard Lookup Codes read contract to resolve ORA_SVC_SR_STATUS_CD and the exact requested LookupCode. Do not infer that a lookup code is absent merely because it has no SR parent mapping.
3. Export FND_MANAGE_STANDARD_LOOKUPS through shared.setup-export.task-level-export, selecting ORA_SVC_SR_STATUS_CD only when the task workflow supports that scope. Wait for a completed export and retain its provenance separately from the SR-status mapping export.
4. Inspect that export's ASM_SETUP_CSV_METADATA.xml and CSV members for the lookup definition and lookup-code structure. Require evidence for FND_APP_STANDARD_LOOKUP and ORA_FND_APP_STANDARD_LOOKUP_CODE or a documented equivalent contract before constructing rows; do not assume catalog CSV support proves those members are present.
5. Retain the existing ORA_SVC_SR_STATUS_CD parent definition and required linkage. Derive headers, node paths, order, required fields, and generated-field handling from this standard-lookup export and its documented contract; do not synthesize metadata, copy unrelated task templates, or create a replacement lookup type.
6. For a new code, require a unique customer-owned LookupCode and Meaning; default an omitted EnabledFlag to Y only where the validated lookup-code contract supports it. Populate only approved fields supported by that contract and preserve required parent rows. Header-only members are usable when their structure and required values are fully resolved.
7. Validate the separate standard-lookup package with shared.validation.setup-data-validator. If the completed export does not establish the required creation structure, record a catalog mismatch with task code, missing objects, export reference, and the required contract correction; stop before any import rather than requesting an unspecified creation package or repeatedly exporting the SR mapping task.

### View Service Request Status Values

View all configured Service Request status values, their parent relationships, and active states.

1. Preflight the active project workflow, target Fusion environment, read privileges, and safe audit destination before the external read; follow core.fusion-api.rest-api-client and its references/fusion-rest-api.md instructions.
2. Read Service Request Statuses with core.fusion-api.rest-api-client using GET /crmRestApi/resources/11.13.18.05/serviceRequestStatusesLOV.
3. Use finder=SrStatusCdFinder;BindChildLookupType=ORA_SVC_SR_STATUS_CD,BindParentLookupType=ORA_SVC_SR_STATUS_TYPE_CD and fields=LookupCode,ParentLookupCode,Meaning,EnabledFlag,StartDateActive,EndDateActive,DisplaySequence. Do not use IsEnabledFinder for the configured-status list because disabled statuses must remain visible.
4. Retrieve all pages with limit and offset until hasMore is false; advance offset using the returned offset and count. Stop and report incomplete retrieval on a failed page, lack of progress, or the configured finite page budget; never report partial results as a complete list.
5. For a selected status, filter the collected rows by exact LookupCode and optional ParentLookupCode. Preserve distinct parent relationships and require an unambiguous match where the use case requires one.
6. Persist the read result and redacted audit or classified failure diagnostics in the active project workspace; stop on read failure rather than treating it as an absent status.
7. Return LookupCode, ParentLookupCode, Meaning, EnabledFlag, StartDateActive, EndDateActive, and DisplaySequence.

### View Service Request Status Value

View a selected Service Request status value before changing it.

1. Read the requested Service Request status with core.fusion-api.rest-api-client using GET /crmRestApi/resources/11.13.18.05/serviceRequestStatusesLOV and the read contract in view_service_request_status_values.
2. Require exactly one match for the requested LookupCode and ParentLookupCode when supplied; stop when no matching status or multiple matches are returned.

### Create Service Request Status Value

Create a Service Request status value with its required code, meaning, active state, display sequence, and optional parent status.

1. Read the requested Service Request status with core.fusion-api.rest-api-client using GET /crmRestApi/resources/11.13.18.05/serviceRequestStatusesLOV and the read contract in view_service_request_status_values.
2. Run prepare_service_request_status_lookup_package and use its standard-lookup read to reject an existing LookupCode; absence from the status LOV alone is not proof that the code is new.
3. Confirm the LookupCode, Meaning, EnabledFlag, DisplaySequence, optional ParentLookupCode, and optional active dates.
4. Export Service Request status setup data with shared.setup-export.task-level-export.
5. Treat the completed SR-status export as the parent-mapping baseline only. Prepare a separate mapping package when a parent relationship is requested, retaining only metadata-declared objects and fields; do not insert lookup-definition or lookup-code CSV members into it.
6. Validate the standard-lookup package and any requested mapping package with shared.validation.setup-data-validator before the first mutation.
7. Import the approved standard-lookup ZIP once with core.data-loader and verify the new code through core.fusion-api.apps-common.lookups before importing its mapping.
8. If a parent relationship is requested, import its separately approved mapping ZIP with core.data-loader; otherwise skip the mapping import. If the mapping fails after code creation, record the partial success and stop without automatically retrying or recreating the code.
9. Verify the new lookup code through core.fusion-api.apps-common.lookups; when a mapping was requested, also verify the relationship with a fresh core.fusion-api.rest-api-client GET using the read contract in view_service_request_status_values.

### Update Service Request Status Value

Update an existing Service Request status value's meaning, parent status, active dates, display sequence, or enabled state.

1. Read the requested Service Request status with core.fusion-api.rest-api-client using GET /crmRestApi/resources/11.13.18.05/serviceRequestStatusesLOV and the read contract in view_service_request_status_values.
2. Require exactly one match for the requested LookupCode and ParentLookupCode when supplied and validate the approved changes.
3. Export Service Request status setup data with shared.setup-export.task-level-export.
4. Separate lookup-code changes from relationship changes. For lookup-code fields, run prepare_service_request_status_lookup_package; for relationship fields, use only the metadata-declared ORA_SVC_LOOKUP_CODE_RELS structure from the SR-status export. ChildLookupCodeMeaning is relationship data and is not proof that the lookup-code Meaning was changed.
5. Keep lookup-code and mapping packages separate; report partial success if a later stage fails.
6. Validate each required package separately with shared.validation.setup-data-validator before any import.
7. Import each required approved ZIP through core.data-loader, lookup-code package before a dependent mapping package; verify each stage and stop on failure, recording any earlier successful stage.
8. Verify changed lookup-code fields through core.fusion-api.apps-common.lookups, and verify relationship changes with a fresh core.fusion-api.rest-api-client GET using the read contract in view_service_request_status_values.

### Activate Service Request Status Value

Activate an existing Service Request status value.

1. Read the requested Service Request status with core.fusion-api.rest-api-client using GET /crmRestApi/resources/11.13.18.05/serviceRequestStatusesLOV and the read contract in view_service_request_status_values.
2. Export Service Request status setup data with shared.setup-export.task-level-export.
3. Run prepare_service_request_status_lookup_package for the lookup-code enabled-state change. Separately prepare a mapping enabled-state change only when requested and supported by the SR export; a relationship EnabledFlag change alone does not prove the lookup code is enabled.
4. Validate each required package separately with shared.validation.setup-data-validator before any import.
5. Import each required approved ZIP through core.data-loader, lookup-code package before a dependent mapping package; verify each stage and stop on failure, recording any earlier successful stage.
6. Verify the lookup code is enabled through core.fusion-api.apps-common.lookups, and verify any approved mapping change with a fresh core.fusion-api.rest-api-client GET using the read contract in view_service_request_status_values.

### Deactivate Service Request Status Value

Deactivate an existing Service Request status value.

1. Read the requested Service Request status with core.fusion-api.rest-api-client using GET /crmRestApi/resources/11.13.18.05/serviceRequestStatusesLOV and the read contract in view_service_request_status_values.
2. Export Service Request status setup data with shared.setup-export.task-level-export.
3. Show "The Service Request status value will be deactivated. Do you want to continue?" and wait for confirmation.
4. Run prepare_service_request_status_lookup_package for the lookup-code enabled-state change. Separately prepare a mapping enabled-state change only when requested and supported by the SR export; a relationship EnabledFlag change alone does not prove the lookup code is disabled.
5. Validate each required package separately with shared.validation.setup-data-validator before any import.
6. Import each required approved ZIP through core.data-loader, lookup-code package before a dependent mapping package; verify each stage and stop on failure, recording any earlier successful stage.
7. Verify the lookup code is disabled through core.fusion-api.apps-common.lookups, and verify any approved mapping change with a fresh core.fusion-api.rest-api-client GET using the read contract in view_service_request_status_values.

### Delete Service Request Status Value

Delete a Service Request status value.

Not supported. Service Request status-value deletion is not supported through this FSM workflow; deactivate the status instead.
## Guard Rails

1. Require an authenticated Fusion user context before any Fusion operation; use `core.auth.fusion-oauth-authentication`.
2. Do not use `core.fusion-api.rest-api-client` to create, update, or delete records.
3. Do not use `shared.setup-import.task-level-import` to create, update, or delete records.
## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export task setup data with `shared.setup-export.task-level-export`.
2. Validate exported or prepared task setup data with `shared.validation.setup-data-validator`.
3. Import reviewed task setup data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Service`
- Functional area / Setup Object: `Service Request`
- Setup task name: `Manage Service Request Status Values`
- Setup task code: `ORA_SVC_SERVICE_REQUEST_STATUS`


## FSM Data Loader Package Requirements

1. Read the task's fsm_contract first when it is present. Treat its objects and field guidance as the task-specific starting point for classifying each requested change as an existing-root update, new root, existing-child update, new child of an existing parent, new relationship, or mixed package change.
2. Read `ASM_SETUP_CSV_METADATA.xml` in the task export package for business objects, XML paths, node sequence, attributes, scope, and relationships; reconcile it with the task's fsm_contract when one is present.
3. Use the fsm_contract object and field guidance together with metadata-defined node sequence and relationships to determine package order and required object coverage.
4. Verify the selected baseline or template package includes the members, file names, structure, headers, encoding, scope, relationship rows, and fsm_contract objects and fields required for the requested change.
5. Treat a completed export of this same setup task as authoritative evidence for package structure, headers, node order, key and linkage shape, and generated-identity handling. Use it to corroborate the fsm_contract and record provenance for copied template values.
6. For existing-row updates, retain exported identities and all unchanged values, parent rows, child rows, and relationships required by the fsm_contract and package evidence; do not carry unrelated baseline rows into the change package unless they are required for import integrity. Change only approved fields.
7. For a new child or relationship, retain the existing parent identity and use only linkage, keys, and required values specified by the fsm_contract or confirmed by same-task package evidence.
8. For greenfield rows, construct the create contract from the fsm_contract, task-specific documented requirements, `ASM_SETUP_CSV_METADATA.xml`, a completed export of this same task, and supported preview or dry-run results where available.
9. An export whose data CSV members contain only headers is valid structural evidence for a greenfield contract, not an automatic blocker. Use the fsm_contract, exported package structure, and explicit supported inputs to construct the rows; stop only when required fields, keys, relationships, or values remain unresolved or validation rejects the package.
10. Populate every root, child, scoped, localized, and relationship object required by the fsm_contract or confirmed package contract. Populate approved business keys, required values, and reference values; omit generated identities unless explicitly required.
11. Classify every populated fsm_contract field as request-provided, documented requirement, export-derived structural value, export-derived template value, generated or omittable, or unresolved.
12. A fsm_contract field may be omitted only when it is documented as generated or optional, is absent or consistently blank in semantically comparable exports of this same task, or is accepted as omitted by supported preview or dry-run validation. Do not infer a value solely from a field name or description.
13. Do not copy identities, reference keys, parent keys, scope values, localized values, lookup codes, or behavior-changing settings unless the fsm_contract, request, documented guidance, or approved compatible template default explicitly supports the value.
14. Verify every non-generated parent, lookup, code, scope, locale, and related-object reference required by the fsm_contract against approved same-task package evidence or the workflow's documented resolver; include required parents or relationship rows only when the package contract requires them.
15. Build the complete package required by the fsm_contract and package evidence; never use a child-only package or infer fields, defaults, identities, or relationships from another task or object type.
16. Validate package members, fsm_contract objects and fields, metadata, keys, scopes, references, relationships, node order, field-value provenance, and approved changes before import; confirm that no baseline identity, template-only setting, or unrelated row is introduced or modified unintentionally. Use preview or dry-run validation when available.
17. Stop when a required fsm_contract field or object, identity rule, parent-child linkage, scope, dependency, or behavior-changing setting remains unresolved and lacks an explicit approved value or sufficient same-task evidence. Do not block for fields evidenced as generated or validated-omittable.
## Usage

Use this metadata file when planning, sequencing, exporting, importing, or validating setup data for `Manage Service Request Status Values` under `Service Request`.
