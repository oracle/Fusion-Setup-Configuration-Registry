---
task_code: "ORA_CSO_ARTICLE_STATUS_MGMT"
task_name: "Manage Knowledge Article Statuses"
parent_skill_id: "cx.service.knowledge-management"
pillar: "CX"
offering: "Service"
functional_area: "Knowledge Management"
functional_area_code: "ORA_CSO_KNOWLEDGE_MANAGEMENT"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
---

# Manage Knowledge Article Statuses

## Setup Task Metadata

- Task name: `Manage Knowledge Article Statuses`
- Task code: `ORA_CSO_ARTICLE_STATUS_MGMT`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``


## FSM Contract

### ORA_KNOWLEDGE_ARTICLE_STATUS_MANAGEMENT

- `propertyReferenceKey`: Use KM_ARTICLE_STATUS_ENABLED as the exact exported configuration-property key. Do not add, remove, or substitute a property row without a fresh same-task export and approved task scope.
- `value`: Use only TRUE or FALSE for the KM_ARTICLE_STATUS_ENABLED feature-state value. Retain the exported value unless an approved Article Status feature-state change targets that exact property row.

### ORA_CSO_KNOWLEDGE_ARTICLE_STATUS

- `referenceKey`: Retain the exact exported key for an existing article status. For an approved new status, generate the reference key from the customer-provided name and use it as the parent linkage for localized-attribute rows.
- `recordId`: Retain the exported value when present. Leave it blank when it is absent from the exported row so Fusion generates the value.
- `name`: Retain the exported status name for an existing article status. For an approved new status, use the customer-provided name.
- `dateAdded`: Retain the exported value for an existing article status. For an approved new status, set the current date.
- `dateModified`: Set the current date for an approved new or updated article status.
- `active`: Retain the exported value for an existing article status. For an approved new status without an explicit active-state value, default to TRUE.

### ORA_KNOWLEDGE_ARTICLE_STATUS_LOCALIZED_ATTRIBUTE_OBJECT

- `ORA_CSO_KNOWLEDGE_ARTICLE_STATUS.referenceKey`: Link every localized-attribute row to its Knowledge Article Status parent with that status's exact exported or approved reference key. Do not add an orphan localized row.
- `localeId`: Fetch active Knowledge locales through the Manage Knowledge Locales task and use the selected active locale's exact locale ID, such as en_US only when that is the exact returned export value. Do not infer a locale ID from a display name.
- `name`: Retain the exported localized status text unless it is an approved localized-text change. For an approved new or changed localized row, use the customer-provided localized text.
## Guard Rails

1. Require an authenticated Fusion user context before any Fusion operation; use `core.auth.fusion-oauth-authentication`.
2. Do not use `core.fusion-api.rest-api-client` to create, update, or delete records.
3. Do not use `shared.setup-import.task-level-import` to create, update, or delete records.
## Purpose

Manage article statuses and localized status labels for Knowledge publishing.
## Use Cases

### Review Article Statuses

View article statuses and their feature state.

1. Export article statuses with shared.setup-export.task-level-export.
2. Read the feature state, status names, active states, and localized labels.

### Review Article Status Localizations

View localized article status names.

1. Export article statuses with shared.setup-export.task-level-export.
2. Read the selected status's localized labels.

### Create Article Status

Create an article status.

1. Export article statuses with shared.setup-export.task-level-export.
2. Generate a unique referenceKey and leave recordId blank.
3. Add the status and its localized label for every active locale.
4. Validate the FSM package with shared.validation.setup-data-validator.
5. Import the approved ZIP with core.data-loader.
6. Verify the status with a fresh export.

### Enable Article Statuses

Enable Article Statuses.

1. Export article statuses with shared.setup-export.task-level-export.
2. Enable Article Statuses.
3. Validate the FSM package with shared.validation.setup-data-validator.
4. Import the approved ZIP with core.data-loader.
5. Verify the feature state with a fresh export.

### Update Article Status Active State

Change an article status's active state.

1. Export article statuses with shared.setup-export.task-level-export.
2. Update the selected status's active state.
3. Validate the FSM package with shared.validation.setup-data-validator.
4. Import the approved ZIP with core.data-loader.
5. Verify the status with a fresh export.

### Update Localized Article Status Name

Update a localized article status name.

1. Export article statuses with shared.setup-export.task-level-export.
2. Update the selected status's localized label.
3. Validate the FSM package with shared.validation.setup-data-validator.
4. Import the approved ZIP with core.data-loader.
5. Verify the localized label with a fresh export.

### Delete Article Status

Delete an article status.

Not supported. Article status deletion is not supported through this flow. Delete it from the UI.
## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export task setup data with `shared.setup-export.task-level-export`.
2. Validate exported or prepared task setup data with `shared.validation.setup-data-validator`.
3. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Service`
- Functional area / Setup Object: `Knowledge Management`
- Setup task name: `Manage Knowledge Article Statuses`
- Setup task code: `ORA_CSO_ARTICLE_STATUS_MGMT`




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
