---
task_code: "ORA_CSO_CONTENT_TYPES_MGMT"
task_name: "Manage Knowledge Content Types Classic"
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
route_to: "cx.service.knowledge-management.manage-knowledge-content-types-redwood"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
depends_on:
  - cx.service.knowledge-management.manage-knowledge-content-types-redwood

---

# Manage Knowledge Content Types Classic

## Setup Task Metadata

- Task name: `Manage Knowledge Content Types Classic`
- Task code: `ORA_CSO_CONTENT_TYPES_MGMT`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``



## Use Cases

### Route Classic Content Types To Redwood

Resolve the nested Redwood task and delegate the request without preparing Classic setup data.

1. Resolve cx.service.knowledge-management.manage-knowledge-content-types-redwood at pillars/cx/service/knowledge-management/manage-knowledge-content-types-redwood/SKILL.md.
2. Return an assisted router handoff instruction before any setup-data operation; keep the original Classic task context unchanged. The local Classic ready plan is guidance only, not a structured core redirect or permission to prepare source data.
3. Use the active router/Run Book workflow to select or plan/merge the destination as its own catalog task, preserving project and environment identity.
4. Validate using the destination persisted task identity, sequence and Run Book binding; do not reuse Classic approval.
5. Use the Redwood task's prerequisites, package contract and approval gates; stop if the dependency cannot be resolved.
## Purpose

Delegate Classic content-type requests to the nested Redwood task before any setup-data operation.
## Guard Rails

1. Route every request to cx.service.knowledge-management.manage-knowledge-content-types-redwood before export, package preparation, validation or import.
2. Do not execute a Classic setup-data workflow. If the nested Redwood skill is unavailable, stop and report the missing dependency.
3. Use an assisted router/Run Book handoff. Task Hook returns the local Classic plan, not redirect_required or redirectTarget; ready grants no source export, package preparation, preview or import. Require a separately selected and bound Redwood task before resuming setup work.
4. The FSM Data Loader Package Requirements are reusable package-integrity guidance for the destination task after handoff; they do not authorize a Classic export or import. The Redwood task identity, contract and approval gates govern every package operation.
## Route To

Route to cx.service.knowledge-management.manage-knowledge-content-types-redwood.
## CSV Export, Import, and Validation Workflow

Delegate to `cx.service.knowledge-management.manage-knowledge-content-types-redwood` before any setup-data operation. Do not export, prepare, validate or import a package for this task. Stop if the dependency is unavailable.
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

Use this metadata file when planning, sequencing, exporting, importing, or validating setup data for `Manage Knowledge Content Types Classic` under `Knowledge Management`.


## Assisted Router Handoff

Task Hook returns the local Classic rule plan with its original identity. It
does not emit `redirect_required` or a `redirectTarget`. A ready Classic plan
provides routing guidance only; stop all Classic export, setup-data preparation,
preview and import. The assistant returns the exact Redwood task path/code as
its next-action instruction to the active router/Run Book workflow.

That workflow must select the destination as its own catalog task, or plan/merge
it if absent, and establish its persisted identity, sequence and environment-bound
Run Book context before invoking Redwood validation. If the destination, binding
or supported planning workflow is unavailable, stop with the missing prerequisite.
Do not rewrite Classic context, reuse Classic approval, or substitute REST or a
browser. The existing generic source Task Hook readiness is never destination
readiness or permission to bypass this handoff.
