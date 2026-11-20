---
task_code: "ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT"
task_name: "Manage Knowledge Panel Profile Options"
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

# Manage Knowledge Panel Profile Options

## Setup Task Metadata

- Task name: `Manage Knowledge Panel Profile Options`
- Task code: `ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## FSM Contract

### FND_APP_PROFILE_OPTION

- `ProfileOptionName`: Set to the approved existing Knowledge Panel profile option name. Do not create a profile option definition through this workflow.
- `ApplicationId`: Retain the exported application ID for the selected existing profile option.
- `ModuleId`: Retain the exported module ID for the selected existing profile option.
- `Description`: Retain the exported description for the selected existing profile option.
- `SqlValidation`: Retain the exported SQL validation for the selected existing profile option.
- `StartDateActive`: Retain the exported start date for the selected existing profile option.
- `EndDateActive`: Retain the exported end date for the selected existing profile option.
- `UserProfileOptionName`: Retain the exported user-facing name for the selected existing profile option.
- `CreationDate`: Retain the exported value.
- `CreatedBy`: Retain the exported value.
- `LastUpdateDate`: Retain the exported value unless the same approved package updates the profile option definition.
- `LastUpdatedBy`: Retain the exported value unless the same approved package updates the profile option definition.
- `LastUpdateLogin`: Retain the exported value.

### ORA_FND_APP_PROFILE_OPTION_LEVEL

- `FND_APP_PROFILE_OPTION.ProfileOptionName`: Set to the approved existing Knowledge Panel profile option name.
- `FND_APP_PROFILE_OPTION.ApplicationId`: Retain the exported application ID for the selected existing profile option.
- `LevelName`: Retain the exported supported profile level for the selected profile option. When no supported level is supplied for a task-owned profile-value row, default to SITE.
- `UpdateableFlag`: Retain the exported value; do not enable an unsupported profile level.
- `EnabledFlag`: Retain the exported value; do not enable an unsupported profile level.
- `CreationDate`: Retain the exported value.
- `CreatedBy`: Retain the exported value.
- `LastUpdateDate`: Retain the exported value.
- `LastUpdatedBy`: Retain the exported value.
- `LastUpdateLogin`: Retain the exported value.

### FND_APP_PROFILE_VALUE

- `FND_APP_PROFILE_OPTION.ProfileOptionName`: Set to the approved existing Knowledge Panel profile option name.
- `FND_APP_PROFILE_OPTION.ApplicationId`: Retain the exported application ID for the selected existing profile option.
- `LevelName`: Retain the exported supported profile level for the selected profile option. When no supported level is supplied for a task-owned profile-value row, default to SITE.
- `LevelValue`: Retain the exported level value for the selected profile level. When LevelName defaults to SITE and no level value is supplied, default to SITE.
- `ProfileOptionValue`: Derive the value from the customer's stated business intent and the selected Knowledge Panel profile option semantics. Present the derived value for approval before import; do not infer a value when the intent or documented semantics are insufficient.
- `CreationDate`: Retain the exported value.
- `CreatedBy`: Retain the exported value.
- `LastUpdateDate`: Set to the current date and time for an approved value update.
- `LastUpdatedBy`: Retain the exported value when present; otherwise leave blank for an approved value update.
- `LastUpdateLogin`: Retain the exported value unless same-task package evidence requires an update.
## Guard Rails

1. Require an authenticated Fusion user context before any Fusion operation; use `core.auth.fusion-oauth-authentication`.
2. Do not use `core.fusion-api.rest-api-client` to create, update, or delete records.
3. Do not use `shared.setup-import.task-level-import` to create, update, or delete records.
## Use Cases

### View Knowledge Panel Profile Options

View Knowledge Panel profile options (ORA_CSO_ENABLE_KNOWLEDGE_INSERT_AS_TEXT, CSO_ENABLE_CATEGORY_FILTER, CSO_ENABLE_KNOWLEDGE_LINKING, CSO_ENABLE_LOCALE_FILTER, CSO_ENABLE_PRODUCT_FILTER, CSO_SHOW_ARTICLE_SNIPPET).

1. Read the selected profile option with core.fusion-api.apps-common using the Profile Values REST.

### Update Knowledge Panel Profile Options

Update Knowledge Panel profile options (ORA_CSO_ENABLE_KNOWLEDGE_INSERT_AS_TEXT, CSO_ENABLE_CATEGORY_FILTER, CSO_ENABLE_KNOWLEDGE_LINKING, CSO_ENABLE_LOCALE_FILTER, CSO_ENABLE_PRODUCT_FILTER, CSO_SHOW_ARTICLE_SNIPPET).

1. Export Knowledge Panel profile options with shared.setup-export.task-level-export.
2. Update the selected Knowledge Panel profile option(s).
3. Validate the FSM package with shared.validation.setup-data-validator.
4. Import the approved ZIP with core.data-loader.
5. Verify the updated option(s) with a fresh export.
## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export task setup data with `shared.setup-export.task-level-export`.
2. Validate exported or prepared task setup data with `shared.validation.setup-data-validator`.
3. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Service`
- Functional area / Setup Object: `Knowledge Management`
- Setup task name: `Manage Knowledge Panel Profile Options`
- Setup task code: `ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT`




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

Use this metadata file when planning, sequencing, exporting, importing, or validating setup data for `Manage Knowledge Panel Profile Options` under `Knowledge Management`.
