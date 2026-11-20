---
task_code: "QSC_MANAGE_PRODUCT_GROUP_USAGE"
task_name: "Manage Product Group Usage"
parent_skill_id: "cx.help-desk.service-catalog"
pillar: "CX"
offering: "Help Desk"
functional_area: "Service Catalog"
functional_area_code: "ORA_SVC_SERVICE_CATALOG"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
depends_on:
  - cx.service.service-catalog

---

# Manage Product Group Usage

## Setup Task Metadata

- Task name: `Manage Product Group Usage`
- Task code: `QSC_MANAGE_PRODUCT_GROUP_USAGE`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``







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
## Route To

Route to cx.service.service-catalog.
## Use Cases

### Read Help Desk Product Group Usage

Review Help Desk Product Group Usages and their usage-scoped engines, modes, preferences, and roots.

1. Read the Product Group Usage collection through the documented read-only resource contract.
2. Resolve the exact UsageCode before reading one usage item or any usage-scoped child collection.
3. Return UsageCode, UsageName, UsageDescText, AllowDupContentFlag, and requested child records without changing Product Group Usage data.

### Create Help Desk Product Group Usage

Create an approved Help Desk Product Group Usage configuration.

1. Export Product Group Usage setup data with shared.setup-export.task-level-export.
2. Use the completed export of the same Help Desk setup task as the package baseline.
3. Add only the approved task-owned Product Group Usage row and required child rows using the current export field shape.
4. Validate the FSM package with shared.validation.setup-data-validator.
5. Import the approved ZIP with core.data-loader.
6. Verify the created Product Group Usage with a fresh task export and documented read-only usage lookup.

### Update Help Desk Product Group Usage

Update an approved Help Desk Product Group Usage configuration.

1. Export Product Group Usage setup data with shared.setup-export.task-level-export.
2. Resolve exactly one existing UsageCode through the documented read-only usage lookup and retain its exported identity.
3. Modify only approved task-owned fields for that UsageCode while preserving package structure and unchanged child rows.
4. Validate the FSM package with shared.validation.setup-data-validator.
5. Import the approved ZIP with core.data-loader.
6. Verify the updated Product Group Usage with a fresh task export and documented read-only usage lookup.

### Delete Help Desk Product Group Usage

Delete a Help Desk Product Group Usage configuration.

Not supported. Deletion is outside the supported Product Group Usage FSM workflow; do not prepare or import a deletion package from this task metadata.
## Purpose

Manage Help Desk Product Group Usage setup data and its usage-scoped configuration.
## FSM Contract

### QSC_PRODUCT_GROUP_USAGE

- `UsageCode`: Retain the exported usage code for an existing Product Group Usage. For a new row, set only the approved code after confirming no exact UsageCode exists.
- `UsageName`: Retain the exported name unless an approved change targets it. For a new row, set the approved Help Desk usage name exactly.
- `UsageDescText`: Retain the exported description unless an approved change targets it. Leave blank only when the approved request and package evidence allow a blank description.
- `AllowDupContentFlag`: Retain the exported value unless an approved change targets duplicate-content behavior.

### QSC_PRODUCT_GROUP_USAGE_ENGINE

- `UsageCode`: Link to the approved or retained QSC_PRODUCT_GROUP_USAGE.UsageCode.
- `UsageModeCode`: Retain the exported usage mode code unless an approved child-row change targets it.
- `UsagePrefCode`: Retain the exported usage preference code unless an approved child-row change targets it.
- `UsagePrefValue`: Retain the exported preference value unless an approved child-row change targets it.
- `ProductGroupUsageEngineUniqID`: Retain the exported identity for an existing child row. Omit only when same-task package evidence confirms it is generated for a new child row.

### QSC_PRODUCT_GROUP_USAGE_MODE

- `UsageCode`: Link to the approved or retained QSC_PRODUCT_GROUP_USAGE.UsageCode.
- `ProductGroupUsageModeSetupUniqID`: Retain the exported identity for an existing mode row. Omit only when same-task package evidence confirms it is generated for a new mode row.

### QSC_PRODUCT_GROUP_USAGE_PREFERENCE

- `UsageCode`: Link to the approved or retained QSC_PRODUCT_GROUP_USAGE.UsageCode.
- `ProductGroupUsagePreferenceSetupUniqID`: Retain the exported identity for an existing preference row. Omit only when same-task package evidence confirms it is generated for a new preference row.

### QSC_PRODUCT_GROUP_USAGE_ROOT

- `UsageCode`: Link to the approved or retained QSC_PRODUCT_GROUP_USAGE.UsageCode.
- `ProdGrpRootsId`: Retain the exported root identifier for an existing root row. For a new root row, use only an approved product group root confirmed by same-task package evidence.
## Guard Rails

1. These assisted handoff rules take precedence over generic CSV/FSM workflow, package instructions and Route To. This overlay enables guidance/readiness only; catalog Y and FSM metadata do not authorize execution.
2. Explicitly load pillars/cx/service/service-catalog/manage-product-group-usage.md, then the unique QSC_MANAGE_PRODUCT_GROUP_USAGE / Manage Product Group Usage entry in pillars/cx/service/service-catalog/ora-resource/ora_rule_registry.json and its referenced validation, lookup and error resources relative to that folder. Block missing or ambiguous providers, task identity mismatch, missing resources and unresolved Help Desk applicability; never choose a different task or silently replace the provider.
3. The current core resolver does not follow depends_on or Route To and returns skipped with zero resources here. This is not canonical validation and cannot continue a load. Preserve Help Desk offering, functional area, task code/name, sequence, project, environment, source provenance and active Run Book binding; never rebind the source as Service.
4. Stop create/update/delete/import before source preparation, preview or external writes until a supported Help Desk task-validation path, operation-specific same-task contract and owning workflow are separately established. A ZIP, prior approval or Service REST command does not clear these prerequisites. Live reads also require a separately selected supported project read step.
5. Use current completed same-task Help Desk export and ASM_SETUP_CSV_METADATA.xml evidence for any later selected FSM contract; do not infer members, fields, keys or identities from Service REST. Core Data Loader retains preview, exact-artifact approval, execution and verification ownership. Record review results and blockers through existing project services.
## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export task setup data with `shared.setup-export.task-level-export`.
2. Validate exported or prepared task setup data with `shared.validation.setup-data-validator`.
3. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Help Desk`
- Functional area / Setup Object: `Service Catalog`
- Setup task name: `Manage Product Group Usage`
- Setup task code: `QSC_MANAGE_PRODUCT_GROUP_USAGE`




## Usage

Use this metadata file when planning, sequencing, exporting, importing, or validating setup data for `Manage Product Group Usage` under `Service Catalog`.
