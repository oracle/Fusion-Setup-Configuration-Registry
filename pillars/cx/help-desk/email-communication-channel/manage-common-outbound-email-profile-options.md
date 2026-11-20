---
task_code: "ORA_SVC_MANAGE_COMMON_OUTBOUND_EMAIL_PROFILE_OPTIONS"
task_name: "Manage Common Outbound Email Profile Options"
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
  - shared.validation.setup-data-validator
execution_blocker: "Common Outbound supports export and package validation only; task-owned profile/level evidence and an enabled import contract are missing."
---

# Manage Common Outbound Email Profile Options

## Setup Task Metadata

- Task name: `Manage Common Outbound Email Profile Options`
- Task code: `ORA_SVC_MANAGE_COMMON_OUTBOUND_EMAIL_PROFILE_OPTIONS`
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

Route to shared.validation.setup-data-validator.
## Use Cases

### Inspect Common Outbound Fsm Package

Validate the task identity and exported package shape without changing Fusion.

1. Obtain a completed same-task export through shared.setup-export.task-level-export when the active workflow selects that step.
2. Confirm the XML task code, three object names, headers, relationships, and node order against the same-task metadata.
3. Route package validation to shared.validation.setup-data-validator and disclose whether each CSV is header-only.
4. Report structure validation separately from task-owned profile, level, value, and sender verification; stop when required evidence is absent.

### Update Common Outbound Profile Value

Change a Common Outbound profile value.

Not supported. The retained same-task export is header-only, so profile ownership and enabled, updateable target levels are unproven. Supply completed task-owned definition, level, and value evidence and review the execution contract before enabling this capability; do not submit an import from this guidance.
## Purpose

Inspect and validate the Common Outbound same-task FSM package. Profile-value mutation is not enabled by this task guidance until task-owned profile and level evidence is supplied and reviewed.
## FSM Contract

### FND_APP_PROFILE_OPTION

- `node_sequence`: 1
- `xml_node_path`: /ProfileOptionLoaderVO/ProfileOptionLoaderVORow
- `ProfileOptionName`: Require a task-owned exported definition; a requested code alone is not evidence of membership.
- `ApplicationId`: Retain the exact exported application identity; never invent it.
- `ModuleId`: Preserve the exported module identity.
- `Description`: Preserve the exported description.
- `SqlValidation`: Preserve exported validation semantics; do not infer accepted values.
- `StartDateActive`: Preserve the exported active-start date.
- `EndDateActive`: Preserve the exported active-end date.
- `UserProfileOptionName`: Preserve the exported display name.
- `CreationDate`: Preserve exported audit data; do not fabricate it.
- `CreatedBy`: Preserve exported audit data.
- `LastUpdateDate`: Preserve exported audit data.
- `LastUpdatedBy`: Preserve exported audit data.
- `LastUpdateLogin`: Preserve exported audit data.

### ORA_FND_APP_PROFILE_OPTION_LEVEL

- `node_sequence`: 2
- `xml_node_path`: /ProfileOptionLoaderVO/ProfileOptionLoaderVORow/ProfileOptionLevelLoaderVO/ProfileOptionLevelLoaderVORow
- `FND_APP_PROFILE_OPTION.ProfileOptionName`: Link to the exact task-owned definition.
- `FND_APP_PROFILE_OPTION.ApplicationId`: Link to the same definition's application identity.
- `LevelName`: Require an explicit target level proven by same-task evidence.
- `UpdateableFlag`: Require enabled updateability for a proposed value change; never alter this flag to bypass the gate.
- `EnabledFlag`: Require an enabled level; never enable it to bypass the gate.
- `CreationDate`: Preserve exported audit data.
- `CreatedBy`: Preserve exported audit data.
- `LastUpdateDate`: Preserve exported audit data.
- `LastUpdatedBy`: Preserve exported audit data.
- `LastUpdateLogin`: Preserve exported audit data.

### FND_APP_PROFILE_VALUE

- `node_sequence`: 3
- `xml_node_path`: /ProfileOptionLoaderVO/ProfileOptionLoaderVORow/ProfileOptionValueLoaderVO/ProfileOptionValueLoaderVORow
- `FND_APP_PROFILE_OPTION.ProfileOptionName`: Link to the exact task-owned definition.
- `FND_APP_PROFILE_OPTION.ApplicationId`: Link to the same definition's application identity.
- `LevelName`: Match the proven enabled, updateable level.
- `LevelValue`: Preserve the unambiguously resolved target-level identity; never infer a new identity.
- `ProfileOptionValue`: Require an explicit approved replacement satisfying exported validation; mutation remains unsupported until the execution contract is reviewed.
- `CreationDate`: Preserve exported audit data.
- `CreatedBy`: Preserve exported audit data.
- `LastUpdateDate`: Preserve exported audit data.
- `LastUpdatedBy`: Preserve exported audit data.
- `LastUpdateLogin`: Preserve exported audit data.
## Guard Rails

1. Use the active project workflow for authenticated same-task export and shared.validation.setup-data-validator for package validation; this guidance does not authorize an import.
2. These refusal rules take precedence over generic CSV/FSM package guidance. Before any import preview, select and evaluate the local Common Outbound refusal plan through the owning Data Loader Task Hook; ready means rule-plan availability only. Return ordered blocked ruleResults to build-data-load-preview with the exact task context and finalData.archiveSha256, with no passed or overridden mutation outcome. That command rejects blocked or missing ruleResults, including with a readiness waiver. For supported tasks only, the owning workflow uses approve-data-load-preview after explicit approval and verify-approved-data-load-archive before upload. Preserve the approved preview and exact archive; changes require fresh preview and approval. Do not use removed memory-session APIs or invoke Task Validator directly. A ZIP, prior approval or header-only export does not enable import.
3. execution_blocker is descriptive metadata in the current core, not automatic enforcement. Never treat missing/skipped guidance as permission; the registered refusal nodes and existing blocked-ruleResults preview validation own the stop. Selected export and package inspection remain separate shared workflows.
4. Require a completed export whose XML task code equals ORA_SVC_MANAGE_COMMON_OUTBOUND_EMAIL_PROFILE_OPTIONS, preserving all three CSV members, headers, and XML node order.
5. A header-only package establishes structure only. It does not establish task-owned profile definitions, application IDs, supported levels, current values, or sender verification.
6. Require exactly one task-owned ProfileOptionName and ApplicationId pair, exactly one requested LevelName with EnabledFlag and UpdateableFlag enabled, and an unambiguous target LevelValue before considering a value change.
7. Do not create profile definitions, infer application IDs, enable or make levels updateable, copy rows from a different task, or substitute a legacy outbound task automatically.
8. Record missing ownership or level evidence as input validation or catalog mismatch and stop. Do not label package structure validation as Fusion configuration verification or successful import.
## CSV Export, Import, and Validation Workflow

Only export and validation are supported by the current task guidance. The catalog CSV flag establishes package transport support; it does not enable the unsupported update use case.

1. Export this exact task with shared.setup-export.task-level-export when selected by the active workflow.
2. Inspect the same-task XML and all three CSV members, then validate with shared.validation.setup-data-validator.
3. Report package structure separately from profile ownership, level readiness, current values, and sender verification. Do not submit an import until the missing evidence and execution contract are reviewed.

Task identity: Help Desk / Email Communication Channel / ORA_SVC_MANAGE_COMMON_OUTBOUND_EMAIL_PROFILE_OPTIONS.


## Usage

Use this metadata file when planning, sequencing, exporting, importing, or validating setup data for `Manage Common Outbound Email Profile Options` under `Email Communication Channel`.
