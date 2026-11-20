---
skill_id: "cx.service.knowledge-management.manage-knowledge-content-types-redwood"
name: "Manage Knowledge Content Types Redwood Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Knowledge Content Types Redwood under the Knowledge Management functional area."
layer: "pillar"
pillar: "CX"
offering: "Service"
functional_area: "Knowledge Management"
functional_area_code: "ORA_CSO_KNOWLEDGE_MANAGEMENT"
task_code: "ORA_CSO_CONTENT_TYPES_INDEXING_MGMT_REDWOOD"
task_name: "Manage Knowledge Content Types Redwood"
parent_skill_id: "cx.service.knowledge-management"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "CX service pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
  - "pillars/cx/service/knowledge-management/manage-knowledge-locales.md"
uses_core:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
persists_project_state: true
token_usage_tracking:
  enabled: true
  granularity: "per_skill_run"
  artifact_type: "token_usage_record"
  default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
  estimation_method: "chars/4 estimate unless exact tokenizer or API accounting is available"
  required_fields:
    - "activity_start_time"
    - "skill_id"
    - "task"
    - "trigger"
    - "artifacts_written"
    - "files_read"
    - "estimated_input_tokens"
    - "estimated_output_tokens"
    - "estimated_total_tokens"
    - "estimation_method"
    - "notes"
state_updates:
  - "setup_task_sequence"
  - "configuration_blueprints"
  - "validation_results"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/service/knowledge-management/manage-knowledge-content-types-redwood/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/service/knowledge-management/manage-knowledge-content-types-redwood/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects: []
required_privileges: []
---

# Manage Knowledge Content Types Redwood Setup Task Guidance

## Purpose

Define Knowledge article content types and their article schemas.
## Setup Task Skill Contract

- task_code: `ORA_CSO_CONTENT_TYPES_INDEXING_MGMT_REDWOOD`
- task_name: `Manage Knowledge Content Types Redwood`
- parent_skill_id: `cx.service.knowledge-management`
- pillar: `CX`
- offering: `Service`
- functional_area: `Knowledge Management`
- functional_area_code: `ORA_CSO_KNOWLEDGE_MANAGEMENT`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Guard Rails

1. Require an authenticated Fusion user context before any Fusion operation; use `core.auth.fusion-oauth-authentication`.
2. Do not use `core.fusion-api.rest-api-client` to create, update, or delete records.
3. Do not use `shared.setup-import.task-level-import` to create, update, or delete records.
## Use Cases

### View Knowledge Content Types

View the list of Knowledge content types with their names and descriptions.

1. Export content-type setup data with shared.setup-export.task-level-export.

### Create Knowledge Content Type

Create a Knowledge content type with its name, reference key, document ID prefix, description, locale, and department.

1. Export content-type setup data with shared.setup-export.task-level-export.
2. Use the completed export of the same setup task as the package baseline; preserve its package structure and modify only task-owned rows required for the approved change.
3. Preserve every approved explicit value, including referenceKey and schema required settings. Apply documented defaults only to omitted values after reconciling same-task evidence. Do not generate or replace a supplied referenceKey; require an approved unique key before linking child rows. Reject a value that violates a mandatory constraint rather than silently replacing it.
4. Use the Manage Knowledge Locales skill to identify every active Knowledge locale.
5. Define the name, reference key, article ID prefix, description, and department. A nonblank Content Type Name is required for every Knowledge locale that is active; add localized content type name and description rows for every active locale and do not limit localization to the default locale. When locale-specific names are not supplied, ask the customer to provide them or confirm that the provided Content Type Name may be used for every active locale.
6. Optionally configure AI Assist and its content type description.
7. Optionally allow unrestricted JavaScript and HTML and enable a default article review date.
8. Define the required title field.
9. Add and order additional content schema attributes with their names, descriptions, reference keys, field types, and required settings.
10. Select an attribute field type using one of the allowed values - TEXT_AREA, WYSIWYG_EDIT, TEXT_FIELD, FILE, BOOLEAN, LIST, COUNTER, DATE, DATETIME, TIME, INTEGER, or FLOAT.
11. Configure attribute visibility after selecting the content type department, and add localized names and descriptions for the title and every additional schema attribute for every active Knowledge locale.
12. Configure searchable or available-for-filtering attribute options when the selected field type supports them.
13. Optionally enable file attachments.
14. Validate the FSM package with shared.validation.setup-data-validator.
15. Import the approved ZIP with core.data-loader.
16. Verify the content type with a fresh export.

### Update Knowledge Content Type

Update a Knowledge content type's properties, content schema, field visibility, attachment setting, scripting setting, or default article review-date setting.

1. Export content-type setup data with shared.setup-export.task-level-export.
2. Use the completed export of the same setup task as the package baseline; preserve its package structure and modify only task-owned rows required for the approved change.
3. Preserve every approved explicit value, including referenceKey and schema required settings. Apply documented defaults only to omitted values after reconciling same-task evidence. Do not generate or replace a supplied referenceKey; require an approved unique key before linking child rows. Reject a value that violates a mandatory constraint rather than silently replacing it.
4. Use the Manage Knowledge Locales skill to identify every active Knowledge locale.
5. Update the selected content type's name, reference key, article ID prefix, description, or department. Maintain a nonblank Content Type Name and localized description row for every Knowledge locale that is active. When locale-specific names are not supplied, ask the customer to provide them or confirm that the provided Content Type Name may be used for every active locale.
6. Update AI Assist, unrestricted JavaScript and HTML, default article review date, or file attachment settings as required.
7. Add, edit, reorder, or configure visibility for content schema attributes.
8. Update attribute names, descriptions, reference keys, required settings, localized values, or supported searchable and filtering options; maintain localized names and descriptions for every schema attribute in every active Knowledge locale, and use only these allowed field type values when changing a field type - TEXT_AREA, WYSIWYG_EDIT, TEXT_FIELD, FILE, BOOLEAN, LIST, COUNTER, DATE, DATETIME, TIME, INTEGER, or FLOAT.
9. Validate the FSM package with shared.validation.setup-data-validator.
10. Import the approved ZIP with core.data-loader.
11. Verify the content type with a fresh export.

### Delete Knowledge Content Type

Delete a Knowledge content type.

Not supported. Content type deletion is not supported through the FSM workflow; delete the content type from the UI.
## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Knowledge Content Types Redwood` under `Knowledge Management`.

## Setup Task Metadata

- Task name: `Manage Knowledge Content Types Redwood`
- Task code: `ORA_CSO_CONTENT_TYPES_INDEXING_MGMT_REDWOOD`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``


## FSM Contract

### ORA_CSO_CONTENT_TYPE_OBJECT

- `referenceKey`: Retain the exact exported content-type reference key for an existing content type. For an approved new content type, use the approved unique reference key and use it as the parent linkage for every child row.
- `workflowRefKey`: Retain the exported value unless an approved workflow change supplies a compatible reference key.
- `stripeCd`: Retain the exported value for an existing content type. In the FSM package, this is the representation of the selected content-type department. For an approved new or updated content type, use only the caller-supplied mapping to ORA_SVC_CRM, ORA_SVC_HRHD, or ORA_SVC_ISR; do not infer or substitute another stripe code.
- `articleGroup`: Retain the exported value for an existing content type. For a new content type, default to ARTICLE.
- `contentSourceType`: Retain the exported value when present. If the exported value is missing, default to INTERNAL.
- `allowCheckOut`: Retain the exported value. For a new content type, default to TRUE from the completed export.
- `allowRecommendations`: Retain the exported value unless an approved content-type change targets it.
- `counterPrefix`: Retain the exported value for an existing content type. For an approved new or changed content type, ask the customer to provide the required counter prefix; do not generate or infer it from the content-type name or export.
- `defaultLifespan`: Retain the exported value unless an approved content-type change targets it.
- `enableUserActivityLogging`: Retain the exported value unless an approved content-type change targets it.
- `hasPriority`: Retain the exported value. For a new content type, default to FALSE from the completed export.
- `hasRelatedContent`: Retain the exported value. For a new content type, default to FALSE from the completed export.
- `hasTalkBack`: Retain the exported value. For a new content type, default to FALSE from the completed export.
- `isEvent`: Retain the exported value. For a new content type, default to FALSE from the completed export.
- `isModerated`: Retain the exported value. For a new content type, default to FALSE from the completed export.
- `requireAtLeastOneProduct`: Retain the exported value. For a new content type, default to FALSE from the completed export.
- `requireAtLeastOneCategory`: Retain the exported value. For a new content type, default to FALSE from the completed export.
- `requireAtLeastOneUserGroup`: Retain the exported value. For a new content type, default to FALSE from the completed export.
- `restrictToOneUserGroupSelection`: Retain the exported value. For a new content type, default to FALSE from the completed export.
- `categoriesRequireWorkflowApproval`: Retain the exported value. For a new content type, default to TRUE from the completed export.
- `userGroupRequireWorkflowApproval`: Retain the exported value. For a new content type, default to TRUE from the completed export.
- `viewsRequireWorkflowApproval`: Retain the exported value. For a new content type, default to TRUE from the completed export.
- `displayDatesRequireWorkflowApproval`: Retain the exported value. For a new content type, default to TRUE from the completed export.
- `eventDatesRequireWorkflowApproval`: Retain the exported value. For a new content type, default to TRUE from the completed export.
- `restrictAuthoringToWorkflowUser`: Retain the exported value. For a new content type, default to TRUE from the completed export.
- `notifyOnWorkflowApproval`: Retain the exported value. For a new content type, default to FALSE from the completed export.
- `notifyOnWorkflowRejection`: Retain the exported value. For a new content type, default to FALSE from the completed export.
- `notifyGroupOnWorkflowRejection`: Retain the exported value. For a new content type, default to FALSE from the completed export.
- `removeVersions`: Retain the exported value. For a new content type, default to FALSE from the completed export.
- `reviewDays`: Retain the exported value unless an approved content-type change targets it.
- `extendReviewDate`: Retain the exported value unless an approved content-type change targets it.
- `validateHtml`: Retain the exported value. For a new content type, default to FALSE from the completed export.
- `enableIndexing`: Retain the exported value unless an approved content-type change targets it. If the export does not provide a value, default to TRUE.
- `indexStatus`: Retain the exported value unless an approved content-type change targets it. If the export does not provide a value, leave it blank.
- `allowUnsafeHTMLAndJS`: Retain the exported value. For a new content type, default to FALSE from the completed export.
- `hasProducts`: Retain the exported value for an existing content type. For a new content type, default to TRUE.
- `hasCategories`: Retain the exported value for an existing content type. For a new content type, default to TRUE.
- `hasUserGroups`: Retain the exported value. For a new content type, default to TRUE from the completed export.

### ORA_CSO_CONTENT_TYPE_LOCALIZED_ATTRIBUTE_OBJECT

- `ORA_CSO_CONTENT_TYPE_OBJECT.referenceKey`: Link each localized content-type row to the exact root content-type reference key. Do not add an orphan row.
- `localeId`: Resolve every required active Knowledge locale through Manage Knowledge Locales and use its exact locale code, such as en_US. Do not generate a GUID or infer the locale ID from a display name.
- `name`: Retain the exported localized name unless it is an approved change. Provide a nonblank localized name for every required active locale.
- `description`: Retain the exported localized description unless it is an approved change. Provide the approved localized description for every required active locale.

### ORA_CSO_CONTENT_TYPE_SCHEMA_ATTRIBUTE_OBJECT

- `ORA_CSO_CONTENT_TYPE_OBJECT.referenceKey`: Link each schema attribute to its exact root content-type reference key.
- `xpath`: Retain the exact exported schema-attribute path for an existing attribute. For an approved new attribute, generate the xpath from that attribute's referenceKey and its ORA_CSO_CONTENT_TYPE_OBJECT.referenceKey parent.
- `requireWorkflowApproval`: Retain the exported value. For a new attribute, default to TRUE.
- `allowPreselectedUserGroupChange`: Retain the exported value. For a new attribute, default to TRUE.
- `counter`: Retain the exported value. For a new attribute, default to 0.
- `counterPrefix`: Retain the exported value. For a new attribute, default to blank.
- `enableFullTextSearch`: Retain the exported value. For a new attribute, default to TRUE.
- `includeInMasterIdentifier`: Retain the exported value. For a new attribute, default to TRUE.
- `isNode`: Retain the exported value. For a new attribute, default to FALSE.
- `allowMultipleNodes`: Retain the exported value. For a new attribute, default to FALSE.
- `isRequired`: Retain the exported value. For a new attribute, default to TRUE.
- `readOnly`: Retain the exported value. For a new attribute, default to FALSE.
- `enableAttributeLevelSearch`: Retain the exported value. For a new attribute, default to FALSE.
- `referenceKey`: Retain the exported value for an existing attribute. For an approved new attribute, use the approved unique reference key.
- `schemaAttrType`: Use only TEXT_AREA, WYSIWYG_EDIT, TEXT_FIELD, FILE, BOOLEAN, LIST, COUNTER, DATE, DATETIME, TIME, INTEGER, or FLOAT for an approved field-type change.
- `secureWithUserGroups`: Retain the exported value unless an approved schema change targets it.
- `securedFileResource`: Retain the exported value unless an approved schema change targets it.
- `userGroupSelectionRequired`: Retain the exported value unless an approved schema change targets it.
- `securityRegex`: Retain the exported value unless an approved schema change targets it.
- `sortOrder`: Retain the exported value unless an approved schema change targets it.
- `textHeight`: Retain the exported value unless an approved schema change targets it.
- `textWidth`: Retain the exported value unless an approved schema change targets it.
- `wysiwygType`: Retain the exported value for an existing attribute. For a new or changed attribute whose schemaAttrType is WYSIWYG_EDIT, set to FULL.

### ORA_CSO_CONTENT_TYPE_SCHEMA_ATTRIBUTE_LOCALIZED_ATTRIBUTE_OBJECT

- `ORA_CSO_CONTENT_TYPE_OBJECT.referenceKey`: Link each localized schema-attribute row to its exact root content-type reference key.
- `ORA_CSO_CONTENT_TYPE_SCHEMA_ATTRIBUTE_OBJECT.xpath`: Link each localized schema- attribute row to its exact parent schema-attribute xpath. Do not add an orphan row.
- `localeId`: Resolve every required active Knowledge locale through Manage Knowledge Locales and use its exact locale code, such as en_US. Do not generate a GUID or infer the locale ID from a display name.
- `name`: Retain the exported localized name unless it is an approved change. Provide the approved localized name for every required active locale.
- `description`: Retain the exported localized description unless it is an approved change. Provide the approved localized description for every required active locale.
## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Service`
- Functional area / Setup Object: `Knowledge Management`
- Setup task name: `Manage Knowledge Content Types Redwood`
- Setup task code: `ORA_CSO_CONTENT_TYPES_INDEXING_MGMT_REDWOOD`

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
## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `cx.service.knowledge-management` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.


## Executable Task Validation

The registry classifies export reviews separately from FSM changes. For a
change, execute input, baseline, active/default locale, department, conditional
visibility, defaulting and design nodes before the final owning-workflow gate.
Read every returned rule resource and retain reached-node outcomes in order.
Missing or conflicting evidence blocks; a generic baseline-ready assertion is
insufficient. Preserve approved explicit values and exported identities. The
active Run Book and core.data-loader own exact preview, approval and import.
