---
task_code: "ORA_MANAGE_KNOWLEDGE_WORKFLOWS"
task_name: "Manage Knowledge Workflows"
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

# Manage Knowledge Workflows

## Setup Task Metadata

- Task name: `Manage Knowledge Workflows`
- Task code: `ORA_MANAGE_KNOWLEDGE_WORKFLOWS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``






## FSM Contract

### ORA_KNOWLEDGE_WORKFLOW

- `referenceKey`: Retain the exact exported key for an existing workflow and use it for every child linkage. For a new workflow, use only an approved unique key validated against a fresh same-task export; do not derive a key from the workflow name or copy an existing key.
- `name`: Retain the exported name unless the workflow name is an approved change. For a new workflow, use the approved name.
- `workflowVersion`: Retain the exact exported value for an existing workflow. The single populated export shows version 1 but does not establish a general create default; resolve a new workflow's value with supported same-task package evidence or validation before import.
- `enabled`: Retain the exported value unless an approved workflow-state change targets it. Preserve the export's boolean representation; workflow feature enablement is a separate prerequisite.
- `autoPublish`: Set the approved Publish articles automatically when complete choice. Retain the exported value when publication behavior is not changing, and use the export's boolean representation.

### ORA_KNOWLEDGE_WORKFLOW_STEP

- `ORA_KNOWLEDGE_WORKFLOW.referenceKey`: Link the step to its workflow using that workflow's exact exported or approved referenceKey.
- `referenceKey`: Retain the exported step key for an existing step. For a new step, use the approved unique key; Oracle uses this key for the step's data security policy, so do not infer it from the step name.
- `name`: Retain the exported step name unless an approved change targets it. For a new step, use the approved Step Name.
- `allowDocumentEditing`: Set the approved Allow editing in step choice and preserve the export's boolean representation for unchanged steps.
- `defaultStepDurationInMinutes`: Retain the exact exported value for an unchanged step. The UI describes Duration in days while the CSV field is named in minutes; confirm the numeric mapping with same-task evidence or supported validation before setting an approved duration. Do not assume that the observed -1 value defines a general no-duration rule.
- `sortOrder`: Retain the exported order for an unchanged step. For a new or reordered step, use the approved sequence and verify its CSV ordering against a fresh same-task export.
- `onlyAssigneeCanApprove`: Set the approved Only assigned users can approve choice and preserve the export's boolean representation for unchanged steps.
- `rejectionSteps`: Retain the exported value. The observed row is blank; do not invent rejection routing without an approved design and a validated same-task representation.
- `workflowConditions`: Retain the exported value. The observed row is blank; do not invent conditions without an approved design and a validated same-task representation.

### ORA_KNOWLEDGE_WORKFLOW_STEP_LOCALIZED_ATTRIBUTE

- `ORA_KNOWLEDGE_WORKFLOW.referenceKey`: Link every localized step row to the exact workflow referenceKey. Do not add an orphan row.
- `ORA_KNOWLEDGE_WORKFLOW_STEP.referenceKey`: Link every localized step row to the exact parent step referenceKey. Do not substitute a display name.
- `localeId`: Retain the exported locale code for an existing localized row. For an approved new localization, resolve the exact supported locale through Manage Knowledge Locales; do not infer it from a display name.
- `name`: Retain the exported localized step name unless it is an approved change. Use the approved locale-specific name for a new localized row.

### ORA_KNOWLEDGE_WORKFLOW_LOCALIZED_ATTRIBUTE

- `ORA_KNOWLEDGE_WORKFLOW.referenceKey`: Link every localized workflow row to the exact workflow referenceKey. Do not add an orphan row.
- `localeId`: Retain the exported locale code for an existing localized row. For an approved new localization, resolve the exact supported locale through Manage Knowledge Locales; do not infer it from a display name.
- `name`: Retain the exported localized workflow name unless it is an approved change. Use the approved locale-specific name for a new localized row.
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
## Use Cases

### Review Knowledge Workflows

Review article workflows, publication behavior, steps, and content-type associations.

1. Export Knowledge workflows with shared.setup-export.task-level-export.
2. Review each workflow name and whether articles publish automatically when the workflow completes.
3. Review step names, reference keys, durations, editing permissions, assigned-user approval restrictions, and associated content types before proposing changes.

### Create Knowledge Workflow

Create a governed article review and approval workflow.

1. Confirm the Article Workflow activity and approval outcome lookups are enabled.
2. Obtain the approved workflow name and decide whether articles should publish automatically when the workflow completes.
3. Confirm the planned steps, their reference keys and durations, editing permissions, assigned-user approval restrictions, and content-type associations.
4. Enter the workflow name and publication setting in the Manage Knowledge Workflows setup task, then add the approved steps and associate the approved content types.
5. Save and verify the workflow, steps, publication setting, and content-type associations in Fusion.

### Add Knowledge Workflow Step

Add a review or approval step to a Knowledge workflow.

1. Select the intended workflow and open Add Step.
2. Enter the required Step Name and Reference Key, and set Duration when specified by the approved design.
3. Set Allow editing in step and Only assigned users can approve according to the approved review and approval design.
4. Create the step and verify its name, reference key, duration, and permission settings in the workflow.

### Associate Workflow Content Types

Associate approved Knowledge content types with a workflow.

1. Identify the approved content types and confirm their intended review and approval path.
2. Add the content types in the workflow's Content Types section.
3. Save and verify each content-type association in Fusion.
## Purpose

Define article review and approval workflows for Knowledge content types.
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
- Functional area / Setup Object: `Knowledge Management`
- Setup task name: `Manage Knowledge Workflows`
- Setup task code: `ORA_MANAGE_KNOWLEDGE_WORKFLOWS`




## Usage

Use this metadata file when planning, sequencing, exporting, importing, or validating setup data for `Manage Knowledge Workflows` under `Knowledge Management`.
