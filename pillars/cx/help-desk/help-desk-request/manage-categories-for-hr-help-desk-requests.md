---
task_code: "ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS"
task_name: "Manage Categories for HR Help Desk Requests"
parent_skill_id: "cx.help-desk.help-desk-request"
pillar: "CX"
offering: "Help Desk"
functional_area: "Help Desk Request"
functional_area_code: "ORA_SVC_HELP_DESK_REQUEST"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
depends_on:
  - cx.service.service-request

---

# Manage Categories for HR Help Desk Requests

## Setup Task Metadata

- Task name: `Manage Categories for HR Help Desk Requests`
- Task code: `ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``







## FSM Contract

### ORA_SVC_CATEGORY

- `node_sequence`: 1
- `xml_node_path`: /SrCategoryVO/SrCategoryVORow
- `CategoryName`: Retain the exported category name unless an approved create or update targets it. For a new row, set the approved Help Desk category name exactly.
- `CategoryCode`: Retain the exported globally unique category code for an existing category. For a new row, set only the approved code after confirming no exact CategoryCode exists across business units and application stripes.
- `CategoryDescription`: Retain the exported description unless an approved change targets it. Leave blank only when the approved request and same-task package evidence allow a blank description.
- `BusinessUnitName`: Retain the exported business unit for an existing category. For a new top-level category, set the approved business unit; for a child category, inherit the root category business unit confirmed by same-task evidence.
- `StripeCd`: Preserve the HR Help Desk stripe value from the same-task export; do not use a Service or non-HR stripe unless the selected task export proves it is valid for this setup task.
- `EnabledFlag`: Retain the exported active state unless an approved activation or deactivation targets it. For a new row, default to active only when the approved request does not state otherwise and package evidence supports the default.
- `CategoryShortName`: Preserve the exported short name for updates; require an explicit approved short name for creates. Do not infer equality with CategoryCode.
- `ParentCategoryCode`: Preserve the exported parent code for updates; use the uniquely resolved parent's code for a child. Leave blank for an approved root only when same-task evidence permits it.
- `DeletedFlag`: Preserve the exported value; deletion is unsupported by this workflow.
- `CSSFlag`: Preserve exported self-service visibility for updates; require an approved visibility choice for creates.
- `BUOrgId`: Preserve the exported business-unit identity; resolve it from same-task evidence for creates, never invent it.
- `Depth`: Preserve exported hierarchy metadata for updates; derive new-row values only when the same-task package contract establishes them.
- `Hierarchy`: Preserve exported hierarchy metadata; do not copy another category's hierarchy into a new row.
- `ChildCountParentCategoryId`: Preserve exported relationship metadata; this is not a replacement for ParentCategoryCode.
- `CategoryIdHierarchy`: Preserve exported hierarchy identities for updates; do not synthesize IDs for creates.
- `RootCategoryCode`: Preserve the exported root code for updates; resolve the root from same-task hierarchy evidence for creates.

### ORA_SEVICE_CATEGORY_ASSOCIATION

- `node_sequence`: 2
- `xml_node_path`: /SrCategoryVOAsso/SrCategoryVOAssoRow
- `StripeCd`: Retain the child's same-task stripe; preserve the exported object spelling SEVICE exactly.
- `CategoryShortName`: Link to the child ORA_SVC_CATEGORY short name.
- `BUOrgId`: Link to the child's resolved business-unit identity.
- `CategoryShortNameParent`: Link to the uniquely resolved parent's short name; retain existing relationships on updates.
- `BUOrgIdParent`: Link to the resolved parent's business-unit identity.
- `StripeCdParent`: Link to the resolved parent's stripe. Preserve required association rows and node order; do not infer a root association.
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

Route to cx.service.service-request.
## Use Cases

### View Hr Help Desk Categories

View the Categories list and its available Category Name, Category Code, and Category Description result information.

1. Open the Categories page for the Manage Categories for HR Help Desk Requests task.
2. Review the displayed category records and their visible category identity and description information.

### View Default Hr Help Desk Root Categories

View active top-level Help Desk categories using the default category filter.

1. Apply "StripeCd = 'ORA_SVC_HCM' and EnabledFlag = true and ParentCategoryId is null".
2. Review the returned active root-category records.

### View Active Hr Help Desk Categories

Limit the Categories list to active category records.

1. Enable Show Active Only on the Categories page.
2. Review the resulting active category records.

### Search Hr Help Desk Categories

Find HR Help Desk categories using a supported screen field, matching condition, and search text.

1. Select one search field: Category Name, Category Code, Category Description, Created By, Creation Date, Last Updated Date, Last Updated By, or Business Unit Name.
2. Select one matching condition: Equals, Contains, Starts With, or Ends With.
3. Enter search text and run the page search.
4. Review the returned category records.

### Create Top Level Hr Help Desk Category

Create a top-level HR Help Desk category with the fields shown in the Create Category dialog.

1. Select Create Top-Level Category.
2. Collect the required Category Name, Category Code, and Business Unit; ask for missing values rather than inventing them.
3. Collect an optional Category Description and the Active choice; the supplied dialog shows Active on initially.
4. Keep the category without a parent. The default list filter is a read filter, not a create payload.
5. Export this setup task with shared.setup-export.task-level-export and resolve the field mappings and required package structure from the same-task export metadata.
6. Validate the prepared package with shared.validation.setup-data-validator, then route it through core.data-loader for preview, approval, and import.
7. Verify the created category in the selected business unit, including its code, active state, and absence of a parent.

### Create Child Hr Help Desk Category

Create an HR Help Desk category beneath a selected parent using the fields shown in the Create Category dialog.

1. Select Create Child Category.
2. Collect the required Parent Category Name, Category Name, and Category Code; ask for missing values rather than inventing them.
3. Collect an optional Category Description and the Active choice; the supplied dialog shows Active on initially.
4. Resolve the selected parent unambiguously before preparing the category relationship. Oracle documents that the child inherits the root category's business unit; confirm the FSM mapping and relationship keys from same-task evidence.
5. Export this setup task with shared.setup-export.task-level-export and resolve the parent identity, field mappings, and required relationship rows from the same-task export metadata.
6. Validate the prepared package with shared.validation.setup-data-validator, then route it through core.data-loader for preview, approval, and import.
7. Verify the created child and its parent relationship using same-task evidence; the default root-only list cannot verify a child category.

### View Hr Help Desk Category Children

Inspect children of an explicitly selected Help Desk category.

1. Resolve the parent by category identity, business unit, and stripe; stop on ambiguous matches.
2. Replace the root-only ParentCategoryId restriction with the resolved parent identity, preserving the requested stripe and active-state scope.
3. Review the returned children and their parent relationship through the workflow's declared read route.

### Update Hr Help Desk Category

Update the name or description of an existing top-level or child category through FSM.

1. Resolve exactly one category, including inactive or child records when explicitly requested.
2. Export the same task and retain the selected category's exported keys, scope, parent linkage, and required relationship rows.
3. Change only the approved name or description; do not rename business keys or reparent a category as an incidental update.
4. Validate the complete package with shared.validation.setup-data-validator and submit through core.data-loader preview, approval, and FSM import.
5. Verify the changed values and unchanged identity and relationship using a scoped read or same-task export.

### Activate Hr Help Desk Category

Enable an existing inactive category through FSM.

1. Resolve exactly one category with the active-only restriction explicitly removed.
2. Export the same task and set only EnabledFlag to Y for the selected row, preserving its keys and required relationships.
3. Validate the package and route preview, approval, and FSM import through core.data-loader.
4. Verify the selected category is active; use a parent-aware read for child categories.

### Deactivate Hr Help Desk Category

Disable an existing category without deleting it.

1. Resolve exactly one category and review its children and usage before proposing deactivation; do not infer cascade behavior.
2. Export the same task and set only EnabledFlag to N for the selected row, preserving its keys and required relationships.
3. Validate the package and present the deactivation impact in the core.data-loader preview for approval before FSM import.
4. Verify the disabled record with the active-only restriction removed; absence from the default list is not sufficient proof.

### Export Hr Help Desk Categories

Obtain the same-task FSM template or baseline for a category change.

1. Confirm the project, target environment, exact task code, privileges, and effective-catalog CSV support.
2. Route a template export for new rows or a scoped data export for updates to shared.setup-export.task-level-export.
3. Check completion and preserve the package metadata and both CSV members; record export provenance without copying unrelated baseline data into an import.

### Verify Hr Help Desk Category Import

Check an existing Data Loader submission and verify the resulting category data without resubmitting it.

1. Use the existing Data Loader request and FSM process identifiers with the declared status workflow.
2. Report the terminal status and processed, successful, and failed row counts; retrieve process diagnostics on failure.
3. After success, verify the category fields, business unit, stripe, active state, and parent relationship using the declared read or export route.
4. On timeout or partial failure, retain identifiers and diagnostics, report the last status and next-check path, and stop without automatic reimport.

### Delete Hr Help Desk Category

Permanently delete a Help Desk category.

Not supported. Deletion is not enabled by the rerouted category workflow; the visible Delete control and exported DeletedFlag do not establish safe delete semantics. Use the deactivation use case when appropriate.
## Purpose

Review and search HR Help Desk categories, and create, update, activate, or deactivate categories through validated same-task FSM packages.
## Guard Rails

1. Require the active project workflow, authenticated environment identity, task privileges, and catalog CSV support before any Fusion operation.
2. Route category mutations through core.data-loader in FSM mode; do not substitute direct REST writes or shared.setup-import.task-level-import.
3. Export with shared.setup-export.task-level-export and validate with shared.validation.setup-data-validator before the Data Loader preview and approval workflow.
4. Preserve same-task XML metadata, CSV headers, object names, node order, and required relationships. Do not upload a reduced-column CSV or a REST JSON payload as an FSM package.
5. Treat the default category filter as a list-only default; remove only the relevant active or root restriction for explicit inactive or child-category lookups and verification.
6. Require globally unique CategoryCode across business units and application stripes for creates; a filtered root-only list is not a sufficient duplicate check.
7. Preserve exported keys for updates. Do not synthesize a category-code suffix from the stripe or business unit or infer that CategoryCode must equal CategoryShortName.
8. Obtain preview approval through core.data-loader for the exact target and immutable package. Never retry a failed or uncertain import without reconciliation and explicit approval or supported idempotency.
## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export task setup data with `shared.setup-export.task-level-export`.
2. Validate exported or prepared task setup data with `shared.validation.setup-data-validator`.
3. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Help Desk`
- Functional area / Setup Object: `Help Desk Request`
- Setup task name: `Manage Categories for HR Help Desk Requests`
- Setup task code: `ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS`




## Usage

Use this metadata file when planning, sequencing, exporting, importing, or validating setup data for `Manage Categories for HR Help Desk Requests` under `Help Desk Request`.
