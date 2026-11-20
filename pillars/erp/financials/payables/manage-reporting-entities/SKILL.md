---
skill_id: "erp.financials.payables.manage-reporting-entities"
name: "Manage Reporting Entities Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Reporting Entities under the Payables functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payables"
functional_area_code: "FIN_PAYABLES_DEPLOYED"
task_code: "AP_MANAGE_REPORTING_ENTITIES"
task_name: "Manage Reporting Entities"
parent_skill_id: "erp.financials.payables"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
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
uses_core:
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-reporting-entities/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-reporting-entities/current/"
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

# Manage Reporting Entities Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Reporting Entities` under `Payables`.

## Setup Task Skill Contract

- task_code: `AP_MANAGE_REPORTING_ENTITIES`
- task_name: `Manage Reporting Entities`
- parent_skill_id: `erp.financials.payables`
- pillar: `ERP`
- offering: `Financials`
- functional_area: `Payables`
- functional_area_code: `FIN_PAYABLES_DEPLOYED`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Reporting Entities` under `Payables`.

## Setup Task Metadata

- Task name: `Manage Reporting Entities`
- Task code: `AP_MANAGE_REPORTING_ENTITIES`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Financials`
- Functional area / Setup Object: `Payables`
- Setup task name: `Manage Reporting Entities`
- Setup task code: `AP_MANAGE_REPORTING_ENTITIES`




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

Use the parent functional-area skill `erp.financials.payables` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Source-Backed Task Behavior

- Location preflight uses HCM locationsLov with exact LocationCode and SetCode; its PrimaryKey finder verifies the returned LocationId and effective boundaries. Map LocationCode to CSV InternalLocationCode and retain context from one selected record. Do not import Common Options bill-to restrictions. The code/set and exact-date finder paths have live sample evidence; each operational request still needs current target-bound receipts.

- BSV checks before import are local: require a supplied balancing value, resolve its BU/location parent, and reject duplicate child tuples under that same parent, including preserved rows. FSM validates value-set membership, enabled status, summary status, effectivity and application-specific eligibility. Report its exact rejection to the user.

- BSV eligibility does not require a separate REST lookup, ledger/COA export or ValueSetCode discovery. Preserve the supplied value and submit through the normal Data Loader approval workflow. No BSV lookup evidence or exception approval is required.

- BU eligibility is documented as a PAYABLES_INVOICING_BF usage. The optional finBusinessUnitsLOV ModuleIdFinder with ModuleId=10 and task Intent is documented in Reference Lookups. Keep EnterpriseId matching, shared-helper ambiguity and live receipt qualification separate; no internal ID is added to the CSV.

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_REPORTING_ENTITY::TaxIdentificationNum, AP_REPORTING_ENTITY::EntityName, AP_REPORTING_ENTITY::EffectiveStartDate, AP_REPORTING_ENTITY::EffectiveEndDate, AP_REPORTING_ENTITY::BuName, AP_REPORTING_ENTITY::InternalLocationCode, AP_REPORTING_ENTITY::SetCode, AP_REPORTING_ENTITY::EnterpriseId, AP_REPORTING_ENTITY_LINE::BalancingSegmentValue, AP_REPORTING_ENTITY_LINE::AP_REPORTING_ENTITY.BuName, AP_REPORTING_ENTITY_LINE::AP_REPORTING_ENTITY.InternalLocationCode, AP_REPORTING_ENTITY::GlobalAttributeCategory, AP_REPORTING_ENTITY::GlobalAttribute1, AP_REPORTING_ENTITY::GlobalAttribute2, AP_REPORTING_ENTITY::GlobalAttribute3, AP_REPORTING_ENTITY::GlobalAttribute4, AP_REPORTING_ENTITY::GlobalAttribute5, AP_REPORTING_ENTITY::GlobalAttribute6, AP_REPORTING_ENTITY::GlobalAttribute7, AP_REPORTING_ENTITY::GlobalAttribute8, AP_REPORTING_ENTITY::GlobalAttribute9, AP_REPORTING_ENTITY::GlobalAttribute10, AP_REPORTING_ENTITY::GlobalAttribute11, AP_REPORTING_ENTITY::GlobalAttribute12, AP_REPORTING_ENTITY::GlobalAttribute13, AP_REPORTING_ENTITY::GlobalAttribute14, AP_REPORTING_ENTITY::GlobalAttribute15, AP_REPORTING_ENTITY::GlobalAttribute16, AP_REPORTING_ENTITY::GlobalAttribute17, AP_REPORTING_ENTITY::GlobalAttribute18, AP_REPORTING_ENTITY::GlobalAttribute19, AP_REPORTING_ENTITY::GlobalAttribute20 -->
<!-- fscr-update-fields: AP_REPORTING_ENTITY::TaxIdentificationNum, AP_REPORTING_ENTITY::GlobalAttributeCategory, AP_REPORTING_ENTITY::GlobalAttribute1, AP_REPORTING_ENTITY::GlobalAttribute2, AP_REPORTING_ENTITY::GlobalAttribute3, AP_REPORTING_ENTITY::GlobalAttribute4, AP_REPORTING_ENTITY::GlobalAttribute5, AP_REPORTING_ENTITY::GlobalAttribute6, AP_REPORTING_ENTITY::GlobalAttribute7, AP_REPORTING_ENTITY::GlobalAttribute8, AP_REPORTING_ENTITY::GlobalAttribute9, AP_REPORTING_ENTITY::GlobalAttribute10, AP_REPORTING_ENTITY::GlobalAttribute11, AP_REPORTING_ENTITY::GlobalAttribute12, AP_REPORTING_ENTITY::GlobalAttribute13, AP_REPORTING_ENTITY::GlobalAttribute14, AP_REPORTING_ENTITY::GlobalAttribute15, AP_REPORTING_ENTITY::GlobalAttribute16, AP_REPORTING_ENTITY::GlobalAttribute17, AP_REPORTING_ENTITY::GlobalAttribute18, AP_REPORTING_ENTITY::GlobalAttribute19, AP_REPORTING_ENTITY::GlobalAttribute20 -->

- The child CSV business fields are AP_REPORTING_ENTITY.BuName, AP_REPORTING_ENTITY.InternalLocationCode and BalancingSegmentValue. The parent references link the line to its reporting entity; the balancing value is supplied business data. Their use as the adapter's portable row identity does not require another business field. TaxEntityId is an internal Fusion identifier and is not a CSV input. A child create may carry these three fields in targetKey with an empty values object; all existing reference, required-field, duplicate, key/audit and ownership checks still apply.

- Create a reporting entity for US 1099 reporting with its existing BU, location and one or more primary balancing segment values. Update the tax identifier or explicitly requested GlobalAttributeCategory and GlobalAttribute1–20 values while preserving identity and untouched rows. These global flexfield fields are exposed by the FSM header import. Accept the supplied context and values without an additional uncertainty override; Fusion enforces configured flexfield rules. Do not invent ordinary Attribute/DFF columns absent from the task package. Global-field live persistence testing remains separate from support.

- Before creating a package, resolve each requested child to exactly one header using its BU and location references across the fresh baseline and requested header creates. Reject missing or ambiguous parents. Each new header must have at least one matching baseline or requested child. Validate the whole request before writing a candidate, independent of operation order. Untouched baseline aggregates and header updates retain their existing behavior. These local checks do not establish live Fusion acceptance.
- Process each reporting entity and its child records together. Identify each reporting entity using its business unit (`BuName`), location (`InternalLocationCode`) and reporting entity name (`EntityName`). Keep the entity name unchanged during updates and preserve the existing CSV fields and parent references. Each child record must match exactly one parent reporting entity. If no parent matches or multiple parents match, stop and request a clarified mapping before preparing the import. Local matching checks do not guarantee application acceptance; validate the prepared package through the supported application workflow and verify the saved records after import.

- SetCode is required and must be nonblank on header creates, including EBS migration. Reject missing, null, empty or whitespace-only values before candidate generation; a reference-validation receipt or override does not populate a missing required value. Preserve the existing set on unrelated updates.

- SetCode is location/import context, not a visible Create Reporting Entity control. Preserve an explicit code and corroborate it through the documented read-only set lookup when the routed workflow reaches validation. A location record may provide canonical set/effective-date context only after exact record selection. Never default COMMON from observed sample data. The setIdSetsLOV resource does not return SetId; never invent it. Do not apply Common Options bill-to-location restrictions to this task.

- Read task resources in this order: input validation, dependency readiness, reference lookups, defaulting rules, design enforcement, error handling. Apply their documented validation rules to each requested field. If a field has no supported validation or import path, explain the limitation and stop the affected operation; do not assume support or bypass validation.

- Run Book owns intake/orchestration and core.data-loader owns package processing, immutable preview, approval, submission and later authorized status. Follow the active memory-only session contract. Never persist approval envelopes, bypass Task Hook, automatically retry a rejected write, or use browser submission as fallback. No live import is authorized by this skill generation.

- Delete and reporting-entity retirement are unsupported. Reject either request; do not propose deletion, cascade handling or deletion recovery as pending functionality. Location dates do not provide a reporting-entity retirement operation. Preserve non-requested children and technical export columns.


## EBS Migration to Fusion

### Source scope

Migrate the supplied EBS reporting-entity data through the supported Fusion task
contract. Do not validate, filter, exclude or defer entities based on country,
or infer country eligibility from entity, organization or location names. The
documented US 1099 reporting purpose is functional context, not a migration
eligibility restriction or a reason to request country-based scope approval.
Preserve supplied business and flexfield data and apply the existing required
fields, BU/location reference, parent-linkage and duplicate checks. Fusion
determines application acceptance through the normal approved import; surface
its exact errors without inventing additional country restrictions.

### Source intake and field mapping

Treat EBS, E-Business Suite and R12 as source-system terms for this workflow.
Keep the supplied XML unchanged; its minimum API/patch metadata does not prove
the actual source release. Inspect real APReportingEntityVO records containing
EntityName, excluding the same-named view wrapper, and all nested
APReportingEntityLinesVO children. Report source counts and missing, empty,
populated or unmapped fields before preparing a separate normalized design.

| EBS source | Fusion FSM destination / treatment |
|---|---|
| EntityName | AP_REPORTING_ENTITY.EntityName; stable target identity on updates |
| TaxIdentificationNum | Same-named header field; preserve text, punctuation and leading zeros |
| OrgName | Resolve the intended Fusion BuName; an EBS operating-unit name is not proof of an identical target BU |
| LocationName | Resolve the intended existing location to InternalLocationCode, mandatory nonblank SetCode and exact effective boundaries from one selected target record; a display name is not the target code |
| BusinessGroupName | Retain as source scope/traceability; independently establish target EnterpriseId, never copy the name or an EBS identifier into it |
| GlobalAttributeCategory and GlobalAttribute1–20 | Same-named supported header fields, under the flexfield preservation policy below |
| Nested BalancingSegmentValue | Child BalancingSegmentValue; populate both parent-reference fields from the resolved header BuName and InternalLocationCode |
| PrimaryEntityFlag / PRIMARY_ENTITY_FLAG | Omit from the Fusion payload under the agreed migration policy; this field is not needed in Fusion. Preserve the source unchanged. No separate user question or substitute field is needed, including if supplied nonblank. |

Do not request EBS TaxEntityId or manufacture Fusion row IDs, audit values or
object versions. Missing source fields do not require invented replacements.
Disclose any additional supplied field without a supported target mapping and
resolve the affected mapping before proceeding; absence in this extract is not
proof that a field is unused throughout EBS.

### User decision for unresolved BU/location mappings

When a BU or location lookup returns no exact match or multiple matches, list
all affected reporting entities with their EBS organization/location, lookup
outcome and any supported target candidates. Explain that no match in a secured
result does not prove the organization or location is absent throughout Fusion;
report authorization or transport failures separately from missing matches.

Ask how the user wants to proceed: provide or select the intended existing
Fusion BU/location mapping, explicitly defer the affected records and continue
only with an agreed unaffected scope, or pause the migration while the mapping,
access or prerequisite setup is resolved. State the consequence of each option.
Do not choose an alternative, silently omit records, fabricate references or
create BU/location setup through this task. A request to resolve or create a
prerequisite needs its own supported workflow. Keep affected candidate
preparation blocked until the user decides; selected mappings must still pass
normal reference and parent-linkage checks. Record the explicit decision and
reuse it for unchanged records and scope. Do not resume a user-stopped load
merely because mapping discussion continues.

### Missing balancing lines

For user-declared EBS / E-Business Suite / R12 migration, inspect every reporting
entity and its nested balancing lines before preparing creates. A new reporting
entity requires at least one primary balancing segment value; an empty source
line collection does not waive this requirement.

List each affected entity with its source organization and location. Tell the
user: "These reporting entities have no balancing-segment lines. Provide at
least one balancing segment value for each entity before creating it in Fusion,
or explicitly choose to defer those entities."

Keep the affected creates pending until the user supplies the intended values or
explicitly selects deferral. Never invent or borrow a balancing value, silently
skip an entity, or create a header without a matching child. Proceed with an
unaffected partial batch only after the user explicitly selects that scope;
report deferred entities separately from completed migration work. Preserve the
original XML and record supplied values or deferral decisions in the active
project's migration mapping. Reuse an explicit decision for the same unchanged
records and scope. Mapping or deferral consent does not replace normal Data
Loader approval of the final package.

This source-intake guidance uses the existing header/child validation; it does
not add a direct EBS XML import route. Existing target entities and preserved
children must still be assessed against a fresh target baseline rather than
being assumed to be new creates.

### Ambiguous parent linkage

After resolving source organizations and locations to Fusion references, compare
all mapped headers with each other and the fresh target baseline. The child CSV
identifies its parent only by AP_REPORTING_ENTITY.BuName and
AP_REPORTING_ENTITY.InternalLocationCode; it has no EntityName parent-reference
column. Distinct reporting entity names therefore do not disambiguate children
when multiple headers share the same mapped BU/location.

List the affected entity names, source organizations/locations and mapped Fusion
BU/location. Stop affected candidate preparation and ask the user to correct the
mapping to the intended distinct existing references or explicitly defer the
affected records. Do not invent a location, merge entities, rename them, select
the first parent or add an unsupported EntityName/TaxEntityId CSV column.
Splitting records into separate batches does not establish correct linkage:
recheck the entire proposed state, including existing and previously loaded
headers, before proceeding. An explicit request to continue cannot waive known
parent ambiguity. Any proposed alternative linkage requires a supported,
validated task contract before use. Preserve the decision in the project mapping
and retain normal Data Loader approval for the final package.

### Preserve flexfield data

Preserve all supplied descriptive and global descriptive flexfield (DFF/GDF)
contexts and values in the unchanged source and project migration mapping. Map
GlobalAttributeCategory and GlobalAttribute1–20 to the same-named supported FSM
header fields, keeping their supplied text together with its context. Do not
trim, translate, recode, truncate, substitute or silently drop values. Fusion
enforces its configured flexfield rules; report an exact rejection for user
correction rather than automatically clearing or changing the data.

Inventory any other supplied DFF/GDF fields against the fresh task template and
supported field contract. If a field has no supported destination, identify its
source record, field, context and value, preserve it in the source/mapping, and
stop the affected mapping for the user's decision. Do not invent Attribute or
other CSV columns, assume a DFF/GDF equivalence, or claim unmapped data migrated.
An explicit decision to defer or exclude data must remain visible in the mapping
and completion result; a generic import approval does not authorize data loss.

Distinguish missing elements, empty values and populated values. Missing or empty
source fields do not implicitly authorize clearing existing target flexfields.
Show any proposed clearing explicitly and obtain the user's decision. Preserve
unrequested target values on updates and reconcile the requested mapped contexts
and values through the normal post-import export workflow.

### Literal balancing values

Preserve supplied balancing segment values as text, including leading zeros and
the literal value `-`. A hyphen is a populated value, not a blank or a missing-line
marker. Flag it for review in the source-to-target mapping and preview without
silently removing, replacing or converting it. The agreed treatment is to retain
it unchanged; do not request the same preservation decision again for unchanged
records. This flag does not require a separate BSV lookup or exception approval.
Apply the existing nonblank, parent-linkage and duplicate-child checks, then let
FSM determine acceptance through the normal Data Loader approval workflow.
Report any exact FSM rejection and request corrected input; never automatically
substitute a value or retry the import.

### Target preparation, approval and verification

1. Establish the selected Fusion target and use fresh exact-task current data and
   template exports through the existing routed export workflow. The EBS XML is
   source data, not a compatible Fusion package; never relabel its provenance.
2. Record the source-to-target mapping and user decisions. Match by the resolved
   BU/location/entity identity against the full baseline. Distinguish creates,
   supported tax-ID/global-field updates and already-matching records. A matching
   name or key alone is not permission to overwrite target data. Do not change
   location effective dates to represent reporting-entity activation/retirement.
3. Resolve missing lines and ambiguous parent references as described above;
   apply required-field, reference, duplicate and aggregate checks to the whole
   proposed state. Show proposed changes, omissions and explicitly selected
   partial scope before preparing the candidate. Do not invent defaults.
4. Build a separate candidate using the exact template headers, hierarchy and
   metadata. Preserve untouched target values and rows. Use normal Run Book,
   Task Hook and core Data Loader validation, immutable preview and package
   approval. Mapping decisions do not authorize upload or submission.
5. Report the actual import result and exact FSM errors. After a successful
   import, reconcile a fresh same-target export against the requested and loaded
   headers, children, contexts and global values, including preservation checks.
   Distinguish completed, rejected and explicitly deferred records. Offline
   preparation and a successful job alone do not prove saved-state equivalence.

## References

- [Reporting Entities](https://docs.oracle.com/en/cloud/saas/financials/26d/faipp/reporting-entities.html).
- [Get all set ID sets](https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/op-http-servername-fscmrestapi-resources-11.13.18.05-setidsetslov-get.html).
