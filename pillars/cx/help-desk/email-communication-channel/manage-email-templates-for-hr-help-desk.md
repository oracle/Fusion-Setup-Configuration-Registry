---
task_code: "ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS"
task_name: "Manage Email Templates for HR Help Desk"
parent_skill_id: "cx.help-desk.email-communication-channel"
pillar: "CX"
offering: "Help Desk"
functional_area: "Email Communication Channel"
functional_area_code: "ORA_SVC_EMAIL_COMMUNICATION_CHANNEL"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
depends_on:
  - core.fusion-api.apps-common

---

# Manage Email Templates for HR Help Desk

## Setup Task Metadata

- Task name: `Manage Email Templates for HR Help Desk`
- Task code: `ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``







## Use Cases

### Read Hr Help Desk Email Template Profile Value

Read an allow-listed HR Help Desk email-template profile option value before planning a change.

1. Validate that the requested profile option is SVC_SR_RESPONSE_TEMPLATE_NAME_HRD, SVC_SR_FORWARD_TEMPLATE_NAME_HRD, or SVC_SR_SYSTEM_RESPONSE_TEMPLATE_NAME_HRD.
2. Validate that the requested operation is read and that an explicit Site, Product or User target level and its documented scope key are supplied.
3. Resolve exactly one configured profile value through the level-specific profileOptions GET route, using SITE, application short name or UserName as the selected level key. Do not infer configured scope from session-effective profileValues.
4. Return the profile option code, target profile level, and current profile value without changing configuration.

### Update Hr Help Desk Email Template Profile Value

Update an approved HR Help Desk email-template profile option value through the FSM package workflow.

1. Export the same Help Desk setup task with shared.setup-export.task-level-export.
2. Confirm the requested profile option is allow-listed and the target profile level and replacement template value are explicit.
3. Change only the approved task-owned FND_APP_PROFILE_VALUE row in the exported package.
4. Validate the FSM package with shared.validation.setup-data-validator.
5. Import the approved ZIP with core.data-loader.
6. Verify the value with a fresh export or approved read lookup.

### Reject Unsupported Email Template Profile Request

Reject unsupported HR Help Desk email-template profile option operations.

1. Stop when the requested profile option is outside the three-code HR Help Desk email-template allow-list.
2. Stop when the target profile level or replacement value is missing for an update preview.
3. Do not update a profile value through the selected read-only configured-profile lookup.
## FSM Contract

### FND_APP_PROFILE_OPTION

- `ProfileOptionName`: Set to SVC_SR_RESPONSE_TEMPLATE_NAME_HRD, SVC_SR_FORWARD_TEMPLATE_NAME_HRD, or SVC_SR_SYSTEM_RESPONSE_TEMPLATE_NAME_HRD only.
- `ApplicationId`: Retain the exported application ID for the selected profile option.
- `UserProfileOptionName`: Retain the exported user-facing profile option name.
- `Description`: Retain the exported description.

### ORA_FND_APP_PROFILE_OPTION_LEVEL

- `FND_APP_PROFILE_OPTION.ProfileOptionName`: Link to the selected allow-listed profile option.
- `FND_APP_PROFILE_OPTION.ApplicationId`: Retain the exported application ID.
- `LevelName`: Retain the exported enabled profile level selected for the HR Help Desk email-template value.
- `EnabledFlag`: Retain the exported value; do not enable an unsupported profile level.
- `UpdateableFlag`: Retain the exported value; do not make a non-updateable level updateable.

### FND_APP_PROFILE_VALUE

- `FND_APP_PROFILE_OPTION.ProfileOptionName`: Link to the selected allow-listed profile option.
- `FND_APP_PROFILE_OPTION.ApplicationId`: Retain the exported application ID.
- `LevelName`: Set to the approved target profile level after confirming it is supported by the same-task export.
- `LevelValue`: Retain the exported level value for the target profile level.
- `ProfileOptionValue`: Set only the approved replacement HR Help Desk email-template value; do not infer a template name.
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

Route to core.fusion-api.apps-common.
## Purpose

Read and update the values of the HR Help Desk email-response template profile options.
## Oracle Documentation Guidance

Use the Help Desk email configuration guidance as the source for this task:

- [Configure Help Desk email](https://docs.oracle.com/en/cloud/saas/fusion-service/farhd/configure-help-desk-email.html)
- [Configure profile options for inbound and outbound email](https://docs.oracle.com/en/cloud/saas/fusion-service/farhd/configure-profile-options-for-inbound-and-outbound-email.html)
- [Define email templates](https://docs.oracle.com/en/cloud/saas/fusion-service/faemp/define-email-templates.html)

The Help Desk guidance identifies the HR Help Desk email-template profile options with the `_HRD` suffix:

- `SVC_SR_RESPONSE_TEMPLATE_NAME_HRD`
- `SVC_SR_FORWARD_TEMPLATE_NAME_HRD`
- `SVC_SR_SYSTEM_RESPONSE_TEMPLATE_NAME_HRD`
## Guard Rails

1. Require the active project workflow, authenticated Fusion identity through core.auth.fusion-oauth-authentication, task privileges, and catalog CSV support before any external operation.
2. Do not substitute direct REST writes or shared.setup-import.task-level-import for the core.data-loader FSM route.
3. Select the read branch only for configured-profile reads and the separate FSM update validation/handoff branch for updates. Neither branch performs a mutation; core.data-loader owns execution and approval.
4. Route supported HR template updates through the task FSM use case, shared.setup-export.task-level-export, shared.validation.setup-data-validator, and core.data-loader preview and approval gates.
5. Require exact same-task profile ownership, enabled and updateable target-level evidence, an explicit replacement value, and retained exported keys; stop on missing or ambiguous evidence.
6. Do not create profile definitions, change level enablement or updateability, or write through the selected read-only configured-profile lookup.
7. Preserve XML, object names, headers, node order, unrelated values, and audit fields; reconcile uncertain imports before any retry.
## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export task setup data with `shared.setup-export.task-level-export`.
2. Validate exported or prepared task setup data with `shared.validation.setup-data-validator`.
3. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Help Desk`
- Functional area / Setup Object: `Email Communication Channel`
- Setup task name: `Manage Email Templates for HR Help Desk`
- Setup task code: `ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS`




## Usage

Use this metadata file when planning, sequencing, exporting, importing, or validating setup data for `Manage Email Templates for HR Help Desk` under `Email Communication Channel`.
