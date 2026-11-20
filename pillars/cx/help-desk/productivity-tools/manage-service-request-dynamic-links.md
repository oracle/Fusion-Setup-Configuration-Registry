---
task_code: "ORA_SVC_MANAGE_SERVICE_REQUEST_DYNAMIC_LINKS"
task_name: "Manage Service Request Dynamic Links"
parent_skill_id: "cx.help-desk.productivity-tools"
pillar: "CX"
offering: "Help Desk"
functional_area: "Productivity Tools"
functional_area_code: "ORA_SVC_PRODUCTIVITY"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
depends_on:
  - cx.service.productivity-tools

---

# Manage Service Request Dynamic Links

## Setup Task Metadata

- Task name: `Manage Service Request Dynamic Links`
- Task code: `ORA_SVC_MANAGE_SERVICE_REQUEST_DYNAMIC_LINKS`
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

Route to cx.service.productivity-tools.
## Use Cases

### Review Help Desk Task Through Assisted Guidance

Review Manage Service Request Dynamic Links rules without claiming automatic canonical selection or live configuration verification.

1. Load pillars/cx/service/productivity-tools/manage-service-request-dynamic-links.md and the five mandatory same-task rule resources explicitly.
2. Evaluate only the requested operation using preserved Help Desk context and record applicability, validation evidence and unresolved prerequisites.
3. Return assisted guidance/readiness only. A skipped core result supplies no canonical validation and no execution authority.

### Create Update Delete Or Import Help Desk Configuration

Keep unsupported execution blocked until its task-validation path and operation contract are established.

Not supported. The current overlay has no working canonical rule-selection route or independently approved Help Desk mutation contract. Stop before source preparation, preview or external write; retain original context and report the missing supported workflow.
## Purpose

Provide assisted Manage Service Request Dynamic Links guidance from the exact Service task while preserving Help Desk context; no local mutation contract is enabled.
## Guard Rails

1. These assisted handoff rules take precedence over Route To, generic CSV/FSM workflow and package sections. This overlay authorizes guidance/readiness only; catalog Y and FSM labels do not enable external execution or package preparation.
2. Load pillars/cx/service/productivity-tools/manage-service-request-dynamic-links.md for exact task code ORA_SVC_MANAGE_SERVICE_REQUEST_DYNAMIC_LINKS, then its same-task rows in pillars/cx/service/productivity-tools/ora-resource/ora_input_validation.md, ora_reference_lookups.md, ora_defaulting_rules.md, ora_design_enforcement.md and ora_error_handling.md. Resolve filenames relative to that resource folder. Missing or mismatched guidance blocks the review.
3. The current core resolver returns skipped because this Help Desk package has no local ora-resource directory. It does not load canonical rules or return ruleSkillPath/registryPath. Treat this as missing automated validation, never as canonical success or permission to continue a load.
4. Preserve offering Help Desk ORA_SVC_HELP_DESK, functional area ORA_SVC_PRODUCTIVITY, original task code/sequence, project, selected environment, source provenance and Run Book binding. Require Help Desk applicability evidence; never rewrite context to Service/CRM or use Service project output paths.
5. Evaluate applicable operation-specific inputs, exact-name duplicates, target identity, dependencies, defaults and refusal rules as assisted guidance. A read result does not establish write readiness. Retain explicit true/false and exported update values; apply Tag create defaults only to omitted business intent, and never infer FSM encoding from REST.
6. Stop create/update/delete/import requests with catalog_or_metadata_mismatch before source preparation, preview or any external write. Resume only after a supported Help Desk task-validation path, operation-specific same-task contract and active owning project workflow are separately established. Source evidence, ZIP, prior approval or skipped validation cannot replace them.
7. A live read is not selected by this overlay. It requires a separately selected supported project read step with identity, environment, privilege, catalog and Help Desk scope checks. Do not call direct REST, a browser, Task Validator or an importer as a fallback.
8. Persist sanitized readiness/blocked results, stage, failure class, message, next action and task/environment under the Help Desk project; use the parent project services for artifact registration and token usage. Redact secrets and never retry a mutation automatically.
## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export task setup data with `shared.setup-export.task-level-export`.
2. Validate exported or prepared task setup data with `shared.validation.setup-data-validator`.
3. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Help Desk`
- Functional area / Setup Object: `Productivity Tools`
- Setup task name: `Manage Service Request Dynamic Links`
- Setup task code: `ORA_SVC_MANAGE_SERVICE_REQUEST_DYNAMIC_LINKS`




## Usage

Use this metadata file when planning, sequencing, exporting, importing, or validating setup data for `Manage Service Request Dynamic Links` under `Productivity Tools`.
