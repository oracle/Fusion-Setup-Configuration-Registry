---
task_code: "ORA_MANAGE_MCA_PROFILE_OPTIONS"
task_name: "Manage MCA Profile Options"
parent_skill_id: "cx.service.communication-channels"
pillar: "CX"
offering: "Service"
functional_area: "Communication Channels"
functional_area_code: "ORA_SVC_COMM_CHANNELS"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
depends_on:
  - core.fusion-api.apps-common

---

# Manage MCA Profile Options

## Setup Task Metadata

- Task name: `Manage MCA Profile Options`
- Task code: `ORA_MANAGE_MCA_PROFILE_OPTIONS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``


## FSM Contract

### FND_APP_PROFILE_OPTION

- `ProfileOptionName`: Set to the approved existing Communication Channels profile option name. Do not create a profile option definition through this workflow.
- `ApplicationId`: Retain the exported application ID when present. If a seeded existing option is omitted from the same-task export, take this immutable identity from the authenticated read-only Profile Options definition snapshot.
- `ModuleId`: Retain the exported module ID when present; otherwise use the definition snapshot for a seeded option omitted from the export.
- `Description`: Retain the exported description when present; otherwise use the definition snapshot for a seeded option omitted from the export.
- `SqlValidation`: Retain the exported SQL validation when present; otherwise use the definition snapshot for a seeded option omitted from the export.
- `StartDateActive`: Retain the exported start date when present; otherwise use the definition snapshot for a seeded option omitted from the export.
- `EndDateActive`: Retain the exported end date when present; otherwise use the definition snapshot for a seeded option omitted from the export.
- `UserProfileOptionName`: Retain the exported user-facing name when present; otherwise use the definition snapshot for a seeded option omitted from the export.

### ORA_FND_APP_PROFILE_OPTION_LEVEL

- `FND_APP_PROFILE_OPTION.ProfileOptionName`: Set to the approved existing Communication Channels profile option name.
- `FND_APP_PROFILE_OPTION.ApplicationId`: Retain the exported application ID when present; otherwise use the authenticated definition snapshot for a seeded option omitted from the export.
- `LevelName`: Retain the exported supported profile level; for a seeded option omitted from the export, use SITE only when the authenticated level snapshot reports SITE as enabled and updateable.
- `UpdateableFlag`: Retain the exported value; for a seeded option omitted from the export, retain the authenticated level snapshot value. Do not enable an unsupported profile level.
- `EnabledFlag`: Retain the exported value; for a seeded option omitted from the export, retain the authenticated level snapshot value. Do not enable an unsupported profile level.

### FND_APP_PROFILE_VALUE

- `FND_APP_PROFILE_OPTION.ProfileOptionName`: Set to the approved existing Communication Channels profile option name.
- `FND_APP_PROFILE_OPTION.ApplicationId`: Retain the exported application ID when present; otherwise use the authenticated definition snapshot for a seeded option omitted from the export.
- `LevelName`: Retain the exported supported profile level; for a seeded option omitted from the export, use SITE only when the authenticated level snapshot reports SITE as enabled and updateable.
- `LevelValue`: Retain the exported level value; for a seeded option omitted from the export, use SITE only when LevelName is a verified SITE level.
- `ProfileOptionValue`: Derive the value from the customer's stated business intent and the selected profile option's documented semantics. Present the derived value for approval before import; do not infer a value when the intent or documented semantics are insufficient.
- `LastUpdateDate`: Set to the current date and time for an approved value update.
- `LastUpdatedBy`: Retain the exported value when present; otherwise leave blank for an approved value update.
## Route To

Route to core.fusion-api.apps-common.
## Purpose

Manage supported multichannel architecture (MCA) profile-option values.
## Use Cases

### View Mca Profile Option Value

View the configured or explicitly requested session-effective value for a selected MCA profile option.

1. Follow the parent Profile Task Handoff and selected core.fusion-api.apps-common.profile-options configured-level read workflow. Resolve the exact profile definition and supported Site or User child/key from the matching task rules.
2. Return the configured ProfileOptionValue with its resolved level/key. Use profileValues only for an explicitly requested current-session effective value; label it separately and never treat it as configured-target verification.

### View Mca Profile Option Values

View configured or explicitly requested session-effective values for supported MCA profile options.

1. Resolve each documented requested profile code through the selected core configured-level read workflow with its exact supported level and target key.
2. Return configured values with their scopes; report explicitly requested current-session effective values separately.

### Update Mca Profile Option Value

Update a supported MCA profile-option value through FSM.

1. Resolve the profile definition and configured value for the exact supported level/key through the core profile-options read workflow and matching task lookup rules. Confirm the level is enabled and updateable; stop on missing identity or unsupported scope.
2. Validate the selected profile option code, requested value, and target profile level against the documented guidance; change Oracle Support-directed settings only with that direction.
3. Export the setup task with shared.setup-export.task-level-export.
4. Use the completed export as the package-structure baseline and change only the approved existing profile-value row. When a seeded existing profile option is omitted from the export, assemble its unchanged definition, supported-level, and current-value fields exclusively from authenticated read-only Profile Options snapshots; retain the export's members, headers, encoding, metadata, and node order.
5. Validate the FSM package with shared.validation.setup-data-validator.
6. Import the approved ZIP with core.data-loader.
7. Verify the exact configured profile, level/key and approved value with a fresh scoped configured-value read or same-task export. Effective-value reads are supplementary and cannot replace configured-level verification.

### Create Mca Profile Option

Create a new MCA profile-option definition.

Not supported. This task manages values for documented profile options; creation of profile-option definitions is outside the supported workflow.

### Delete Mca Profile Option

Delete an MCA profile-option definition or value.

Not supported. Deleting profile options or their values is outside the supported workflow.
## Guard Rails

1. Require an authenticated Fusion user context before any Fusion operation; use `core.auth.fusion-oauth-authentication`.
2. Do not use `core.fusion-api.rest-api-client` to create, update, or delete records.
3. Do not use `shared.setup-import.task-level-import` to create, update, or delete records.
## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export task setup data with `shared.setup-export.task-level-export`.
2. Validate exported or prepared task setup data with `shared.validation.setup-data-validator`.
3. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Service`
- Functional area / Setup Object: `Communication Channels`
- Setup task name: `Manage MCA Profile Options`
- Setup task code: `ORA_MANAGE_MCA_PROFILE_OPTIONS`

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

Use this metadata file when planning, sequencing, exporting, importing, or validating setup data for `Manage MCA Profile Options` under `Communication Channels`.
