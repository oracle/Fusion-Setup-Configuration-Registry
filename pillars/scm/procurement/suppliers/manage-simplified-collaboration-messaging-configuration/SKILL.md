---
skill_id: "scm.procurement.suppliers.manage-simplified-collaboration-messaging-configuration"
name: "Manage Simplified Collaboration Messaging Configuration Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Simplified Collaboration Messaging Configuration under the Suppliers functional area."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "Suppliers"
functional_area_code: "ORA_EGP_SUPPLIERS"
task_code: "ORA_CMK_MNGE_SIMPLIFIED_COLLAB_MSG_CONFIG"
task_name: "Manage Simplified Collaboration Messaging Configuration"
parent_skill_id: "scm.procurement.suppliers"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM procurement pillar team"
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
  - "core.runbook"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/suppliers/manage-simplified-collaboration-messaging-configuration/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/suppliers/manage-simplified-collaboration-messaging-configuration/current/"
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
side_effects:
  - "Declared CMK setup operations may change messaging configuration after their owning approval gate."
required_privileges:
  - "Privileges for the selected CMK operation, environment and setup scope."
---

# Manage Simplified Collaboration Messaging Configuration Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Simplified Collaboration Messaging Configuration` under `Suppliers`.

## Progress and Continuation Guidance

Read Customer Progress and Continuation Disclosure in
[ora_error_handling.md](ora-resource/ora_error_handling.md#customer-progress-and-continuation-disclosure)
for permitted CMK handoffs. Explain the current component and remaining
business-document scope before delegating, without adding an approval gate.
Preserve Core Data Loader's initiation report unchanged; status checks and
continuation use their existing explicit-request workflows. This guidance
adds no export, import, polling, retry, batching or cross-task execution route.

## Supported Execution Route

This task supports FSM task-CSV export/import only. REST is limited to the
read-only GET lookups explicitly declared by this skill. No business-resource
REST POST, PATCH, PUT, DELETE, batch, action export or direct UI setup is a
supported creation/update route. Availability in describe does not authorize
another route. The existing shared FSM export and Core Data Loader services
own their own technical transport calls; those services are the authorized
FSM route, not direct CMK business REST operations.

Normalize a customer business requirement, resolve current readable references,
obtain the exact-task template and setup baseline through the shared exporter,
prepare the qualified native CSV/ZIP representation, and use Core Data Loader
plus Task Hook validation and approval. Verify the actual FSM result and every
intended saved field through a fresh exact-task export. Never count a prior
REST result as FSM acceptance evidence. A missing safe native representation
is a specific preparation blocker, not permission to switch routes.

## Implementer Messages

Apply **Business Name Presentation** in
[task outcomes](ora-resource/ora_error_handling.md) at every terminal and
permitted handoff. Use business task names in routine explanations and retain
exact technical task identity in the operational record. Preserve every
response field required by the unchanged shared execution guide, including
task code, rule identity and resume context. Present required technical fields
separately when the owning response contract permits; never suppress a
required field or alter a mandatory executor report.

## Setup Task Skill Contract

- task_code: `ORA_CMK_MNGE_SIMPLIFIED_COLLAB_MSG_CONFIG`
- task_name: `Manage Simplified Collaboration Messaging Configuration`
- parent_skill_id: `scm.procurement.suppliers`
- pillar: `SCM`
- offering: `Procurement`
- functional_area: `Suppliers`
- functional_area_code: `ORA_EGP_SUPPLIERS`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Supplied Task Inputs

Reuse clearly mapped requirements and answers from supplied spreadsheets,
CSVs, images, tables, and text, retaining source references without requiring
repetition or reformatting. Distinguish requested changes from current-state
examples; group only missing, unreadable, conflicting, ambiguous, or unsupported
in-scope values into one prompt. Preserve unrequested settings and explicit
Preserve choices; blanks do not mean Clear or false. Supplied snapshots do not
replace fresh lookups. Keep the task's validation, prerequisite checks, execution
route, and approval gates; do not ask twice for the same operation's approval.

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Simplified Collaboration Messaging Configuration` under `Suppliers`.

## Supported Operation Matrix

This matrix summarizes existing resource contracts, not live acceptance or new
execution authority. Every profile needs its declared current request, target and references. Import
profiles additionally need field mapping, collision/package checks, active Run
Book preparation and Core Data Loader approval; read-only qualification does
not require an import package or approval. Preparation and graph readiness do not prove
that Fusion saved the intended configuration. Provider, delivery, format,
message-definition and connection scope belongs to the
[provider task matrix](../manage-collaboration-messaging-service-providers/SKILL.md#supported-operation-matrix).

| Setup scope | Declared operation or preparation | Prerequisites and boundaries | Saved-state verification |
|---|---|---|---|
| Supplier or customer messaging property | ensure_partner_setup; Prepare Partner Properties CSV ZIP | One Supplier or Customer component under [Partner Properties Intake](#partner-properties-intake) and [Partner Representation Contract](ora-resource/ora_input_validation.md#partner-representation-contract); exact master/site/account/provider grain and fifteen native fields. Reconciliation compares every supplied set/clear value and may return verified reuse; new-row preparation is separate. Updates/renames need their own qualified processing contract | post_import_verify; actual import, exact requested values and preserved existing state |
| Supplier-site B2B account | create_account_number_fsm | Existing supplier/site/Procurement BU, four-field native mapping and complete duplicate checks. No supplier-level account or master creation. See [Native FSM Account Number Creation](ora-resource/ora_input_validation.md#native-fsm-account-number-creation) | verify_account_number_fsm |
| Physical ship-to assignment | create_ship_to_assignment_fsm | Existing saved account and physical location, exact supplier/site/BU ownership and no conflicting assignment. A customer location code is not this physical-location parent. See [Native FSM Physical Ship-To Assignment Creation](ora-resource/ora_input_validation.md#native-fsm-physical-ship-to-assignment-creation) | verify_ship_to_assignment_fsm |
| New account and physical assignment together | create_account_ship_to_combined_fsm | Exactly one account plus one physical assignment; bounded package-local account relationship. Historical 26D acceptance is reported but is not independently verifiable from this package; current-target qualification and saved-state verification remain required. See [Combined Account and Physical Ship-To](ora-resource/ora_input_validation.md#combined-account-and-physical-ship-to) | verify_account_ship_to_combined_fsm; both additions and all-eight-object preservation |
| Customer location code | create_location_code_fsm | native_customer_party for represented ship-to sites, preserving effective bill-to purpose; native_customer_bill_to with customer_account_finder for physically bill-to-only sites. Thirteen-cell mapping and complete same-site purposes/account joins required. See [Existing CMK Customer Location References](#existing-cmk-customer-location-references) | verify_location_code_fsm |
| Processing settings, delivery limits and document properties | configure_initial_settings_fsm | Existing selected rows with qualified meanings, units and encodings. Retain identities and unspecified cells. Same-value settings return no change. See [Native FSM Initial Settings Inputs](ora-resource/ora_input_validation.md#native-fsm-initial-settings-inputs) | verify_initial_settings_fsm; distinguish unchanged values from approved changed cells |
| Default or supplier-site outbound routing | create_document_routing_fsm | One new Disabled top-level rule; existing document/provider/connection and qualified eight-cell native/JSON mapping. Preview any supplier-site communication-method callback. Enabled requests require a separate activation/delivery contract. See [Native FSM Document Routing Creation](ora-resource/ora_input_validation.md#native-fsm-document-routing-creation) | verify_document_routing_fsm; actual rule/coupled effects and prior-state preservation |
| Seven-row configuration composition | qualify_configuration_task_composition_fsm | Qualification candidate: one account, one physical assignment, supplier and customer-account properties, one customer location and two selected existing settings rows (one messaging parameter and one File Export type limit). Only account-to-assignment may use a new parent. Decision Details and document properties excluded. No prior live pass is established by this contract. See [Configuration Task Composition](ora-resource/ora_input_validation.md#configuration-task-composition) | verify_configuration_task_composition_fsm; five additions, two complete approved settings rows and all-eight-object preservation |
| Existing supplier-property qualification | qualify_existing_supplier_property | Retained private supplier/site/provider expectation, same target and read-only prerequisites. See [Read-Only Supplier Qualification Inputs](ora-resource/ora_input_validation.md#read-only-supplier-qualification-inputs) | Current scoped property comparison only; no create/import qualification |
| Existing task-data migration | Shared task export and Core Data Loader task-CSV import | Complete supported members/relationships and All Object Package Validation. Configuration-package requests use their declared project/package workflow | Actual native result plus scoped saved-value/preservation checks |

For native export-based import verification, bind the original approved intent and immutable ZIP
hash to the actual terminal native result and available per-object logs. Use
fresh complete same-target before/after exports to compare every intended cell,
identity and relationship, and preserve prior rows and unspecified cells across
all eight task objects. Missing, partial or differing evidence blocks a verified
result; report actual saved effects separately and never infer rollback.

Retained REST-write and operator-setup descriptions in the detailed resources
do not override [Supported Execution Route](#supported-execution-route). Missing
native field coverage remains a blocker. Offering and functional-area selection
remain owned by the existing routing workflow; this task does not change the
selected project context.

**Evidence status:** ordinary rows declare contracts, not a recorded live pass.
The two-row account/assignment profile has reported historical 26D acceptance
without a linked reusable evidence bundle; that history cannot be independently
verified from this package. The seven-row profile remains a qualification
candidate. Require current-run import and saved-state evidence before reporting
success. The seven-row profile
has five creates and two selected complete existing settings rows; same-value
settings remain separately reported as unchanged. Neither profile permits
arbitrary row counts or other new-parent relationships.

The matrix does not qualify arbitrary batching, master creation, every update
or clear variant, or transaction delivery. Every requested location cell and
setting needs a qualified representation; missing coverage returns the exact
field/profile gap rather than silently dropping a requirement.

## CMK Resource Workflow

For a broad messaging goal without selected partner properties, use the
[Suppliers functional-area guidance](../SKILL.md)
with the router-resolved Procurement/Suppliers context. Explain supplier/site
and customer/account messaging properties in business terms and establish
scope without requiring the user to know the BO inventory. Provider,
delivery-method, message-definition and connection requests belong to
[Manage Collaboration Messaging Service Providers](../manage-collaboration-messaging-service-providers/SKILL.md).
Preserve explicit partner-property requests and proceed with Partner Properties
Intake without adding provider or connection creation. The shared roadmap owns
cross-task planning and summaries; this task retains its source, lookup,
mapping and import gates below.

Read the task's ora-resource rules through the compiled registry and the
FusionApps task-node execution guide before evaluation. Task identity and FSM
import mode are generated by pillar-skill-gen; all task-specific input, lookup,
dependency, design and error rules belong to the standard ora-resource files.
Do not create a second contract/configuration file or task-local processor.
Run Books own business inputs and processing/payload preparation; shared export
services own export mechanics and core.data-loader owns every import.

For create requests, use a completed exact-task header-only template and add
only the requested new records. Preserve all template members, CSV headers and
metadata; leave unrelated CSVs headers only. Existing setup rows are not part
of a create import. Initial-settings and seven-row composition profiles retain
only their explicitly selected complete existing settings rows under their own
contracts; they never reimport the populated baseline. Separate populated exports may qualify an unresolved
mapping, reference or duplicate check, but are not the import seed. A template
never proves target uniqueness or supplies missing relationship mappings.
Keep the existing validation and immutable Data Loader approval gates. This
is FSCR preparation policy; connection and partner-property import
qualification remains separate from the successful provider-only import.

1. Resolve the project, exact task, operation and requested BO. For native
   greenfield account or physical ship-to creation, select the dedicated
   Native FSM Account and Ship-To workflow below. For customer or
   supplier messaging properties, use the Partner Properties Intake below.
   Collect only missing business inputs according to ora_input_validation.md.
2. Execute applicable reference_lookup nodes using the declared Core client.
   Offer readable labels from the fresh REST response, validate supplied values
   and preserve exact returned codes. Do not report input completion before
   applicable resolver checks pass or treat values from another field as valid.
3. Check the selected Run Book processing step and source-guided CSV rules.
   Preserve the source export and bind prepared-data review to the final bytes.
   If field representation, keys, relationships or a supported preparation step
   are missing, report the exact gap; do not invent data or an execution route.
4. Apply the existing same-host feature, catalog, privilege and environment
   gates. For create, use the completed header-only task template and add only
   the intended new rows allowed by the selected qualified profile. Export a missing template through the shared route
   with its required approval. If a specific evidence gap needs populated task
   data, use the shared route with --data and export approval; keep that evidence
   separate from the create ZIP. Templates are not populated baselines.
5. Route the final immutable task ZIP through core.data-loader, its Task Hook
   evaluation and its single import-approval lifecycle. The resource graph's
   read-only success means ready for the next declared gate, not import success.
6. Return the prescribed Data Loader result; use its status/ProcessLog workflow
   when requested. Never replay an uncertain write or modify approved bytes.

Persist sanitized runtime artifacts and skill-run/token records through the
selected project's standard services. Never copy customer packages, protected
row values or credentials into tracked repository files or project artifacts.

### Business Object Ownership

Provider, delivery-method, collaboration/external message-definition and
inbound/outbound connection requests evidenced by the supplied Service Providers
template belong to ORA_CMK_COLLAB_MESG_SERVICE_PROVIDER. Route them to that task's
resource workflow. This task's completed populated export establishes eight
CSV BOs: ORA_CMK_PARTNER_PROP, ORA_CMK_DECISION_DETAIL, ORA_CMK_SHIP_TO_ASSIGN,
ORA_CMK_ACCOUNT_NUMBER, ORA_CMK_LOC_CODE, ORA_CMK_COLLAB_MSG_PARAM,
ORA_CMK_DELIVERY_METHOD_TYPE and ORA_CMK_COLLAB_MSG_PARAM_DATA. Partner-property
creation belongs to ORA_CMK_PARTNER_PROP; its schema and preparation evidence
requirements are in ora_input_validation.md. Inventory is not evidence that
every BO has a business-input creation contract.
A bare create CMK request requires exact object/task scope. Do not copy another
task's CSV members or metadata under this task code. Apply all-object package
validation to the genuine task template.
configuration-package migration on its separate declared project/package route.

### Partner Properties Intake

Recognize add/create customer or supplier B2B properties, messaging properties,
partner properties, or add a provider to a partner as ORA_CMK_PARTNER_PROP work.
The invoking Run Book may supply a provider already selected for a connection;
retain it for same-target revalidation. This task does not create a connection
or schedule another task. A completed connection alone does not authorize
creating properties for an unspecified partner.

Ask "Who do you want to configure messaging for: a supplier or a customer?"
only when the request does not identify that choice. Use business names and
dependent lookup choices, not internal key questions. For a supplier, select
supplier then site and derive Procurement Business Unit. For a customer, select
customer then customer-wide or specific-account scope; resolve the account
only within that customer. Reuse the provider choice when supplied, otherwise
ask for an existing provider. Offer optional settings together and retain
explicit omissions. Provider Type is derived display context, never a
provider-creation question. A Direct-provider example does not establish automatic Partner ID/ID Type
derivation for every service provider.

Follow the six partner lookup nodes and their selection terminals before
package preparation. A missing final ZIP must not be treated as a missing
partner selection. The full task plan remains required before source export or
preparation.
Run Books own the assisted Prepare Partner Properties CSV ZIP step: export the
exact task, prepare the requested new row after mapping checks, validate the
derived ZIP, then hand it to core.data-loader in FSM mode. Shared export and
Data Loader keep their existing approval lifecycles. Lookup captures authorize
no direct partner-properties POST. Structural readiness does not establish
verified CSV mapping or a successful live import; report each stage separately.
For create, do not add a separate readiness blocker for undocumented internal
FSM importer match keys or insert/update behavior. Validate the requested
business scope and one-row package, then let the supported FSM import job
perform record matching and report its terminal result.

## Setup Task Metadata

- Task name: `Manage Simplified Collaboration Messaging Configuration`
- Task code: `ORA_CMK_MNGE_SIMPLIFIED_COLLAB_MSG_CONFIG`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

Before exporting or importing this task's setup data, verify that
**Simplified B2B Messaging (Gen2)** (technical feature code
`ORA_CMK_B2B_DOCUMENT_SETUP`) is enabled on the exact source or destination
Fusion host selected for the operation. Use the shared Core REST client for
this read-only preflight before an export process is created or an import
approval is presented:

```text
python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py \
  --properties <selected-fusionEnv.properties> \
  --method GET \
  --query "q=FeatureCode='ORA_CMK_B2B_DOCUMENT_SETUP'" \
  --query "fields=FeatureCode,FeatureType,EnabledFlag" \
  --query "onlyData=true" \
  /fscmRestApi/resources/11.13.18.05/features
```

Confirm that `restBaseUrl` resolves to the selected host and proceed only when
the response contains exactly one item with `FeatureCode:
ORA_CMK_B2B_DOCUMENT_SETUP`, `FeatureType: FEATURE`, and `EnabledFlag: Y`.
Recheck for each operation and target. Present feature status and blockers
using **Feature State Presentation** in `ora-resource/ora_error_handling.md`.
Use the business feature name in customer messages and retain the technical
code and flags in sanitized diagnostics. Distinguish an unverified feature
from a confirmed disabled feature; apply the blocker only to the selected
operation governed by this gate.
The shared export and import CLIs do not invoke this preflight automatically;
route work through this skill.

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader`.

For a standalone task-CSV import, use a completed exported FSM ZIP for this exact
task, or a prepared ZIP satisfying the task's standard resource rules and declared Run Book processing route.
An implementation-project configuration package and prior package upload apply
only to the separate all-object configuration-package migration. Do not impose
those package steps on the standalone Data Loader route. This task skill does
not execute the separate configuration-package migration; that operation must
be routed and approved through its own project/package workflow. Before Core
Data Loader approval, bind the completed export, immutable ZIP and SHA-256, task identity,
destination host, and Run Book context to its Task Hook validated preview.
Core Data Loader owns upload and submission. When status is explicitly requested,
use its status-only route and ProcessLog/result retrieval. Bound repeated checks
to ten minutes at intervals of at least thirty seconds. Confirm the task result
and target setup before reporting a completed import; an accepted upload or
ESS success alone is not verification. See `ora-resource/ora_input_validation.md` and
`ora-resource/ora_error_handling.md` for the route-specific gates.

Use this task metadata when invoking those skills:

- Offering: `Procurement`
- Functional area / Setup Object: `Suppliers`
- Setup task name: `Manage Simplified Collaboration Messaging Configuration`
- Setup task code: `ORA_CMK_MNGE_SIMPLIFIED_COLLAB_MSG_CONFIG`




## Inputs

- implementation_objective
- project_context
- setup_task_scope
- setup_data_artifacts

## Outputs

- setup_task_plan
- setup_data_routing
- validation_checkpoints
- skill_run_record
- token_usage_record

## Implementation Notes

Use the parent functional-area skill `scm.procurement.suppliers` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.


## Fresh Environment Capability Selection

At intake use the task-owned [metadata qualification](ora-resource/ora_reference_lookups.md#current-public-setup-capability-assessment) through the existing Core REST client
for the configured active project and only the current operation's resources:
b2bProviders and suppliersLOV for supplier scope, or b2bCustomersLOV,
b2bCustomerAccountsLOV, finBusinessUnitsLOV and b2bCustomerPartnerProperties
for the applicable customer scope. Returned links must pass the existing
finder/projection and parent-identity checks. No customer supplies runtime URLs.
Select an already qualified public/native FSM reference profile at intake
when its prerequisites match the requested scope. If its required resources
are not published, return the exact reference or capability gap before
preparation. Metadata, authorization and schema failures retain their actual
failure class; they do not select an assisted screen route or guessed endpoint.

## Customer Business-Document Acceptance

An existing supplier/site is an input to messaging configuration, not a CMK
create-supplier requirement. Accept the business objective and resolve current
identities through the selected configuration route. Never require a fresh PO
or Supplier Import package merely to validate messaging setup.

For a customer business document requesting greenfield setup, validate the
required new configuration through native FSM imports and fresh exact-task
exports. Reuse and preservation alone do not prove creation. For separately
requested positive/negative message-processing tests, select the declared
Customer Acceptance workflow in the canonical Service Providers skill at intake,
retaining this task's partner/document configuration scope and current model.
The roadmap owns this cross-task handoff. Its generated sample is a messaging
test, not a newly created transactional PO. Record every synthetic customer
prompt/document and actual result, including passed and blocked cases. Customer
acceptance must not report unavailable privileges or an unexecuted Process
operation as a pass.

## Complete Object Coverage and Customer Readiness

Use All Object Package Validation in ora_input_validation.md for every CSV
member, including objects without a dedicated business-intake profile. Apply
its schema checks at the existing input node before any import approval.
Do not treat a task's catalog flags, empty template or compiled graph as proof
of successful object creation. All-object migration and one-object business
creation have different evidence requirements.

[Oracle's CMK migration guidance](https://docs.oracle.com/en/cloud/saas/readiness/scm/26c/sccv26c/26C-sccv-wn-f46531.htm)
requires both tasks for complete configuration migration. Preserve the complete
supported package and relationships. For a task CSV request, keep the declared
Core Data Loader route and task-specific checks. A configuration-package request
uses only its declared project/package workflow; this skill does not invent a
package adapter or switch routes after failure.

Customer responsibilities are business choices, approved test destinations,
access, and current existing supplier/site or customer/account setup. Resolve
technical keys from supported current evidence. A missing CSV mapping, parser
contract, executor or verification rule is a skill limitation to research and
repair, never a request for the customer to edit resource files, invent IDs or
supply an internal design document. Name and record the precise limitation.

For acceptance, start with the customer's document and record task selection,
input validation, dependencies, prepared artifact and actual execution result.
An optional manual Oracle action is recorded as a customer handoff. Oracle UI
field validation is supporting evidence, not an FSCR end-to-end passing result.

## Routing Connection Reference Preflight

Before asking for operator context for configure_document_messaging, validate an
explicitly named connection against current supported setup evidence. The
invoking Run Book selects the existing shared provider-task populated export
step when this reference is needed. Supply its completed same-target full-scope
private result to the routing-reference node; the node does not orchestrate or
submit another task. A missing connection returns the precise prerequisite
before any routing preview or Save. Existing matches continue to the unchanged
operator-context, design, approval and verification workflow; an existence
check is not routing execution or permission to edit serialized decision rows.

## Native FSM Account and Ship-To Workflow

For greenfield supplier-site B2B account setup, select
`create_account_number_fsm`. The resource graph validates the current request,
resolves the existing supplier/site and Procurement BU, and checks the requested
account number against a complete current task export. Its native profile maps
the four exported business fields; it never asks the customer for generated
account IDs. A duplicate or conflicting parent stops preparation.

When the customer requests a new account and its physical ship-to assignment
together, select create_account_ship_to_combined_fsm and the Combined Account
and Physical Ship-To rules in ora_input_validation.md. Use the existing active
Run Book's Prepare Combined Account and Ship-To CSV ZIP step and delegate one
immutable two-row package to Core Data Loader and Task Hook. The new account
is a package-local parent; do not demand a separate account import for this
qualified combination. Historical notes report a 26D single-job import and
saved-state/preservation comparison for this scope; no linked reusable evidence
bundle establishes that result within this package. The separate seven-row
qualify_configuration_task_composition_fsm profile composes this pair with two
property creates, one customer location create and two selected existing
settings rows under Configuration Task Composition in ora_input_validation.md.
It is a qualification candidate, not another recorded live pass. Other
combinations require their own qualified contracts.
For the requested completed-result follow-up select
verify_account_ship_to_combined_fsm with approved original intent and complete
fresh before/after exports. This proves saved setup only.

For a physical ship-to assignment to an already saved account, select
`create_ship_to_assignment_fsm`. Resolve the existing physical location through
the declared read-only lookup and bind its current identity and code to the
exact supplier/site/BU/account. An existing location assignment at that site
blocks strict creation, including assignment to a different account. Retain a
missing account as a prerequisite and resume after its saved-state verification.

Read Native FSM Account Number Creation and Native FSM Physical Ship-To
Assignment Creation in `ora-resource/ora_input_validation.md` and their owned
reference contracts through the current compiled graph. The preparation
terminals return work to the active Run Book's standard CSV/ZIP processing
steps. They do not approve or submit a load. Pass the immutable prepared ZIP
through Core Data Loader and Task Hook using the selected native operation.

After a requested import result completes successfully, select
`verify_account_number_fsm` or `verify_ship_to_assignment_fsm` with the approved
intent/hash, actual result and fresh full before/after task exports. The
dedicated verifier checks every intended cell, exactly one addition and
preservation of existing rows and other objects. Report the actual FSM outcome
separately from this comparison. Saved setup does not prove document delivery.

## Native FSM Initial Settings

For initial processing settings, delivery-type limits or document properties,
select `configure_initial_settings_fsm`. Read Native FSM Initial Settings
Inputs, its reference resolver and Native Initial Settings Design through the
current graph. Resolve the existing target configuration identities and the
requested business field meanings, units, encodings and constraints. Document
properties are selected under their exact current document by name or meaning;
the four-column export does not itself identify those properties by business
label. Never ask the customer for parameter IDs or select a row by position.

Greenfield initial settings can update existing global rows. Preserve their
IDs and every unspecified field; do not create duplicate parameter or delivery
type records. Evaluate effective dependencies using requested values and
retained current values together. Already matching settings return a separate
verified no-change result. Changed settings return to the Run Book's Prepare
Initial Settings CSV ZIP step, which copies only selected complete rows into
the genuine header-only template and changes only qualified requested cells.
Core Data Loader and Task Hook retain their immutable validation and approval.

For a requested successful completed import result, select
`verify_initial_settings_fsm`. Compare approved changed cells, all preserved
cells and identities, complete row counts and unrelated objects against fresh
full before/after exports. Report same-value settings separately from actual
changes. Saved setup does not prove that a reprocessing schedule ran or that a
message was delivered.

## Existing CMK Customer Location References

For greenfield native CSV creation, select `create_location_code_fsm` and the
matching reference profile before reads. Use
`location_reference_profile native_customer_party` for a represented customer
ship-to site. For a physically bill-to-only site, select
`location_reference_profile native_customer_bill_to` with
`bill_to_reference_profile customer_account_finder`; apply Bill-To-Only Customer
Location Reference Profile and Customer Account Bill-To Reference Qualification
in ora_reference_lookups.md. Read Native FSM Customer Location Code Creation
and its selected reference branch through the current graph.
Resolve the existing customer/site, complete effective ship-to and
bill-to purposes, and any same-site account references before preparation.
Preserve every qualified purpose and all thirteen native fields. Missing or
conflicting purpose/account evidence blocks preparation; it is never resolved
by dropping a bill-to flag or inventing an ID. This standard profile covers
represented customer ship-to sites, including their bill-to purpose. The
bill-to-only profile requires effective BILL_TO and proven absence of SHIP_TO,
with unique same-site account references; it cannot mask a real ship-to
purpose on a dual-purpose site. Separate bill-only and ship-only codes on the
same dual-purpose site, multiple codes for one site and other domains remain
outside these qualified profiles. Do not drop a purpose or relax a collision
rule to satisfy such a request. Declaring either profile does not establish a
successful live import.

After a requested successful completed import result, use
`verify_location_code_fsm` with the current request, immutable approved intent
and full before/after task exports. Verify every cell, exactly one added
location mapping and preservation of previous rows and other objects. The
current template omits the generated location-value key; do not add an older
identity column or claim its unexported numeric value.

The retained `create_location_code` reference description also uses
`native_customer_party` for read qualification. Under this task's FSM-only
setup boundary, select `create_location_code_fsm` for creation. The invoking
Run Book supplies the fresh completed full task export through the shared
export step; the native reference node applies the exact public party/site
joins in `ora_reference_lookups.md`. The customer chooses a business site or
delegates the non-production fixture choice. A missing current join blocks
preparation. This profile does not resolve an unrepresented customer, create
customer/site/address masters or bypass location-code collisions.
