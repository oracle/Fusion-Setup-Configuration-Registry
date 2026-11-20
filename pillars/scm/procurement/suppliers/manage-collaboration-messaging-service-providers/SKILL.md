---
skill_id: "scm.procurement.suppliers.manage-collaboration-messaging-service-providers"
name: "Manage Collaboration Messaging Service Providers Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Collaboration Messaging Service Providers under the Suppliers functional area."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "Suppliers"
functional_area_code: "ORA_EGP_SUPPLIERS"
task_code: "ORA_CMK_COLLAB_MESG_SERVICE_PROVIDER"
task_name: "Manage Collaboration Messaging Service Providers"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/suppliers/manage-collaboration-messaging-service-providers/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/suppliers/manage-collaboration-messaging-service-providers/current/"
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

# Manage Collaboration Messaging Service Providers Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Collaboration Messaging Service Providers` under `Suppliers`.

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

- task_code: `ORA_CMK_COLLAB_MESG_SERVICE_PROVIDER`
- task_name: `Manage Collaboration Messaging Service Providers`
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

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Collaboration Messaging Service Providers` under `Suppliers`.

## Development Readiness

For a broad messaging goal without a selected object, use the
[Suppliers functional-area guidance](../SKILL.md)
with the router-resolved Procurement/Suppliers context. Explain provider,
delivery-method, message-definition and connection components as candidates;
resolve the requested scope before selecting this task's object workflow.
Supplier/site or customer/account messaging properties belong to
[Manage Simplified Collaboration Messaging Configuration](../manage-simplified-collaboration-messaging-configuration/SKILL.md).
Preserve precise provider/connection requests and supplied values without
expanding scope. The shared roadmap owns cross-task planning and summaries;
this task's ora-resource graph retains its input, lookup and design gates,
with preparation and import owned by the existing Run Book and Core workflows.

This is a draft catalog-generated skill structure. Task-specific resource rules
and a rule registry are present. UI-to-CSV mappings are qualified only for the
selected detailed profile and its represented fields. Provider
creation uses the declared field/default and insert/update rules
and the task's assisted ZIP preparation workflow; their actual checks
are evaluated by CMKSP.INPUT_CONTRACT.
Registry readiness means the validation graph is well formed, not that a
provider-create request has passed its runtime checks. A live import still requires
the exact target feature check, immutable ZIP validation, project Run Book
binding, Task Hook approval preview, and Data Loader approval. Historical 26D
acceptance is reported for the bounded four-component profile, but no reusable
evidence bundle is linked in this package. That history does not establish
current-target or customer-release-wide import qualification.

Before using a live workflow, establish the applicable release and feature state, supported task-specific import contract, required privileges, validation rules, and outcome verification. Catalog export/import flags do not establish the exact create/update package contract. Resolve missing evidence through the declared workflow; do not substitute an undocumented API or browser route. Customer shipment requires completed functional testing and the applicable release reviews.

## CMK Resource Workflow

### Delivery Method Requests

For a request to configure delivery, retain the supplied business name,
existing provider, transport and applicable recipient/attachment/extension choices. Use
`ensure_delivery_method_setup` to compare current settings; retain strict
`create_delivery_method` intent when the user explicitly requests a new method.
Do not ask for a Document or connection status to configure a delivery method.

Select the supported native FSM delivery profile at intake. An explicit
unzipped-PDF choice, credential entry or another setting without a qualified
native CSV representation returns that precise preparation gap while retaining
the customer's nonsecret inputs. The retained assisted-delivery descriptions
do not select a setup route under this task's FSM-only boundary. Never ask for
credentials in chat or a business-input workbook.

Follow Standalone Delivery Method Inputs, Assisted Email Delivery Method
Preparation and File Export and Expanded Email Preparation in
`ora-resource/ora_input_validation.md` through the compiled
resource graph. A compatible existing method can be reused only after its
requested settings are verified. For an absent method, the graph checks the
transport policy, global name availability and supported preparation scope before returning
`create_needed` to the existing Run Book's Prepare Delivery Method CSV ZIP
processing step. This handoff means preparation is needed, not that a method
was created or that an import was approved.

The `create_needed` terminal ends resource-rule evaluation and hands work back
to the invoking Run Book; it does not end the selected business task. Continue
to template export when needed, assisted preparation and Data Loader preflight
using the retained inputs. Ask for approval at the existing export or import
gate when that operation requires it. Do not ask whether to continue merely
because the rule graph returned a preparation handoff. If this delivery method
is a prerequisite of an already selected connection, keep that connection
pending and refresh its own delivery lookup after the method is verified.
Report a blocker only for the actual failed check or unsupported requested
setting; do not apply a blanket creation-workflow blocker to supported profiles.

The DM4/DM5 profiles cover one provider-owned Email or standard File Export
method, using a verified user-defined provider and the exact-task header-only
FSM template. Email supports comma-separated recipients and a supplied file
extension; standard File Export reports the account displayed by the application, without
inventing a fixed account value. Shared export obtains a missing template through
its existing approval workflow. The provider resolver retrieves the stored flag through the public service-provider
read and binds it to the selected identity. No customer-supplied flag or extra
populated export is required solely to infer that representation. The Run Book appends only the requested delivery-method
row and passes the immutable ZIP to `core.data-loader`. Preserve
`create_delivery_method` and the `prepared_import` stage during its Task Hook
evaluation, which rechecks the name and type for the final row before normal
Data Loader approval. Within this FSM preparation branch, do not create another validator, loader
or REST fallback. Retained public-operation descriptions are historical
contracts and do not authorize new setup writes.

Business Event is recognized as a product option, but the attempted DM6
user-defined creation profile failed native FSM qualification. The controlled
26D import returned a predefined-type restriction. An enabled lookup code and
compatible CSV fields do not establish create eligibility. Block new
user-defined Business Event methods before preparation or approval under this
profile; do not retry with another name, provider flag or executor.
See [Business Event qualification](ora-resource/ora_reference_lookups.md#business-event-native-qualification).
A separate, bounded predefined_business_event_fsm connection-reference branch
now uses compatible current native reference evidence for an Inactive outbound
invoice XSLT connection under the same existing user-defined Service Provider.
It prepares only the new connection, with no delivery-method row. Native FSM
import acceptance remains pending its own approved create and saved-state test;
the failed method-create test qualifies neither this branch nor OIC setup.

For business-intake explanation, Oracle's
[26C Gen2 instructions](https://docs.oracle.com/en/cloud/saas/readiness/scm/26c/sccv26c/26C-sccv-wn-f46530.htm)
identify `ORA_BusinessEvent` as a predefined delivery-method selection when
creating a connection, without creating a delivery method. This explicit
selection detail is from 26C readiness; the latest verified messaging guide
is 26D. It does not establish a native FSM CSV value, provider relationship or
current-target eligibility. Explain the distinction and the missing
qualification; do not request a new method name or repurpose the DM4/DM5 create
profiles. Select the bounded branch only as described below; other predefined
method scopes still require separate qualification.

Updates/clears and predefined-provider preparation remain outside these
profiles. B2B Adapter still requires its own qualified native FSM and
external-prerequisite contracts; the retained screen instructions do
not authorize assisted setup. SFTP and web-service creation still lack complete transport/security
representation in this FSM profile. Name the affected setting and retain the
user's nonsecret choices; do not silently omit uncompressed-attachment or a
requested custom account, collect secrets for a blocked route or switch
transport. An accepted Data Loader initiation ends that request with its required
in-progress report. Do not automatically poll or verify after submission.
When results are requested, retain processing status, errors and partial
success separately from saved-setting verification. A completed approved
import uses `post_import_verify_delivery_method` and its dedicated verified
result; it must not be reported as an unchanged reused method. Keep a dependent
connection pending if required delivery settings remain unverified. Customer
acceptance and actual document delivery are separate.


### Public Documentation Basis

Use public Oracle documentation for CMK product guidance. This update requires
no internal documents, Confluence pages or retained implementation archives.
Existing Core routing, current metadata, exported templates and approvals remain
execution prerequisites; public UI instructions do not authorize another route.

For message definitions, select verified Oracle-delivered setup when it meets
the requirement. An explicitly requested new custom definition retains create
intent. A new XSL-based
definition needs its document, external format, transformation and validation
sample. The [26D public guide](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/facmm/configuring-and-managing-b2b-messaging.pdf)
describes creation, duplication and transformation-package export. The
[published REST schema](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-b2bmessagedefinitions-post.html)
is supplemental field-reference evidence. It does not establish native CSV
cell equivalence or authorize a REST creation route.

For greenfield XSL message creation when the native export has no custom
message rows, select `reference_profile provider_message_operation_fsm` at
intake. Its owned reference resolver qualifies an existing reference provider's
returned `messageDefinitions` child and joins the exact message, document and direction
before mapping `DocumentOperationId` to native `DocOperationId`. The public
document master `DocumentId` remains a different reference. A delivered message
may supply operation evidence without being reported as newly created setup.
That reference provider may differ from the new provider being implemented.
Apply the source-qualified saved-name rule, preserve the requested XSL/sample
content, and block a missing or ambiguous join before preparation. Keep the
existing export-join profile for its already represented message scope.

For outbound creation, require a primary delivery method and keep the alternate
optional. Before approving a new Active connection, evaluate the graph's
activation check; never deactivate another definition implicitly. Retention
settings and Loopback remain explicit business choices. Verify saved settings
separately from the later customer test of an actual purchase order.

For a new external-format definition, select
`create_external_message_definition` with
`reference_profile native_fsm_external_definition`. Apply Native FSM External
Definition Inputs and its reference resolver through the compiled graph.
Resolve document type and messaging standard from current qualified evidence;
require both the new name and identification tuple to be absent before strict
creation. The native custom-name rule and current exact-task template govern
the row. Run Book processing prepares the CSV ZIP and Core Data Loader owns
preflight, Task Hook evaluation, approval and submission. Requested fields
without a qualified native column remain explicit preparation gaps.

For completed successful imports, select
`post_import_verify_external_message_definition` for that external format, or
`post_import_verify_message_definition` with
`verification_profile native_fsm_export` for an XSL message. Supply the approved
intent/hash, actual result and fresh full before/after exact-task exports.
These dedicated comparisons check all intended values, including literal
transformation and sample XML cells for messages, and preservation of existing
rows. They issue no setup writes. Keep the existing public message-verification
profile available for its declared scope; neither profile proves PO delivery.

## Supported Operation Matrix

This matrix summarizes existing resource contracts; it does not add execution
authority or replace their staged checks. Every profile needs its declared current target/reference/schema qualification.
Import profiles additionally need active Run Book preparation and Core Data
Loader approval; read-only reviews do not require an import package or approval. A compiled graph or prepared package does not prove
a live import. Acceptance for one bounded scope does not qualify another.
Partner properties, accounts, locations, settings and routing belong to the
[configuration task matrix](../manage-simplified-collaboration-messaging-configuration/SKILL.md#supported-operation-matrix).

| Setup scope | Declared operation or preparation | Prerequisites and boundaries | Saved-state verification |
|---|---|---|---|
| New provider | Prepare Provider CSV ZIP | Exact-task create template; qualified type, identifier type, required/default fields and namespace absence. See [Provider CSV Input Collection](ora-resource/ora_input_validation.md#provider-csv-input-collection) and [Confirmed Assisted Provider ZIP Preparation](ora-resource/ora_input_validation.md#confirmed-assisted-provider-zip-preparation) | post_import_verify_provider; completed import and full before/after evidence |
| Provider identifier correction | update_provider_identifier_fsm | existing_provider_identifier_fsm profile; change PartnerId on one existing customer-defined row only. No rename, clear, other edits or create. See [Existing Provider Identifier Update Inputs](ora-resource/ora_input_validation.md#existing-provider-identifier-update-inputs) | post_import_verify_provider_identifier_update |
| Provider-owned delivery | ensure_delivery_method_setup or create_delivery_method | DM4 Email or DM5 standard File Export under a verified existing user-defined provider. Business Event user-defined creation is blocked: its DM6 attempt failed native FSM qualification with a predefined-type restriction. A live eligible lookup value is insufficient. Updates/clears, predefined-provider preparation and other transports remain outside these create profiles. See [Standalone Delivery Method Inputs](ora-resource/ora_input_validation.md#standalone-delivery-method-inputs), [File Export and Expanded Email Preparation](ora-resource/ora_input_validation.md#file-export-and-expanded-email-preparation) and [Business Event Qualification](ora-resource/ora_reference_lookups.md#business-event-native-qualification) | post_import_verify_delivery_method for supported profiles; failed Business Event processing cannot become a creation or OIC-delivery pass |
| External message format | create_external_message_definition | native_fsm_external_definition; qualified document/standard/subtype, current native columns and unique name/identification tuple. Unrepresented requested fields block. See [Native FSM External Definition Inputs](ora-resource/ora_input_validation.md#native-fsm-external-definition-inputs) | post_import_verify_external_message_definition |
| XSL message definition | create_message_definition or duplicate_message_definition | Qualified document-operation join, existing external format and literal XSL/sample mapping under [XSL Message Preparation](ora-resource/ora_input_validation.md#xsl-message-preparation). A new format is not an implied package-local parent | post_import_verify_message_definition with native_fsm_export for full CSV comparison |
| Inbound or outbound connection | Prepare Connection CSV ZIP; ensure_connection_setup for reconciliation | Existing eligible message/provider; outbound primary delivery required. Active requests need the activation check. Mapping file remains gated until its runtime code and scoped request qualify. See [Connection Intake and Assisted ZIP Preparation](ora-resource/ora_input_validation.md#connection-intake-and-assisted-zip-preparation) | post_import_verify_connection or post_import_verify_connection_export under its selected evidence profile |
| Four-component provider package | qualify_combined_provider_setup | Exactly one Generic user-defined Service provider, one standard File Export method and two inactive XSL connections (outbound supplier purchase order and inbound supplier invoice) with existing eligible delivered definitions. Historical 26D acceptance is reported but is not independently verifiable from this package; current-target qualification and saved-state verification remain required. See [Combined Provider Creation Qualification](ora-resource/ora_input_validation.md#combined-provider-creation-qualification) | post_import_verify_combined_provider_setup; four additions and all-six-object preservation |
| Nine-row provider composition | qualify_provider_task_composition_fsm | Qualification candidate: one provider, two File Export methods, one independent external format, one independent XSL message and four inactive connections (outbound supplier purchase order/customer invoice; inbound supplier invoice/customer purchase order). Both outbound rows use the first method as primary and the second as alternate; inbound rows have no delivery fields. Only provider/delivery relationships are package-local; message/connections require already-saved format/message parents. No prior all-object live pass is established by this contract. See [Provider Task Composition](ora-resource/ora_input_validation.md#provider-task-composition) | verify_provider_task_composition_fsm; nine additions, exact cells and all-six-object preservation |
| Existing provider review | review_provider_setup | Qualified public identity/type GET only; active Run Book and configured-origin checks. See [Read-Only Existing Provider Review](#read-only-existing-provider-review). No create or transport test | Current identity/type observation only; no import or full-setting acceptance |
| Messaging acceptance test | customer_acceptance_prepare / customer_acceptance_execute | Separately requested test with the declared adapter, privileges, safe destination and exact-action approval. See [Customer Acceptance](#customer-acceptance-in-the-configured-environment) | Actual message status and separately observed destination receipt; no transactional PO creation or general setup acceptance |
| Existing task-data migration | Shared task export and Core Data Loader task-CSV import | Complete supported package/relationships and All Object Package Validation. Configuration-package requests use their declared project/package workflow | Actual native result plus scoped saved-value/preservation checks; catalog flags alone are insufficient |

For native export-based import verification, bind the original approved intent and immutable ZIP
hash to the actual terminal native result and available per-object logs. Use
fresh complete same-target before/after exports to compare every intended cell,
identity and relationship, and preserve prior rows and unspecified cells across
all six task objects. Missing, partial or differing evidence blocks a verified
result; report actual saved effects separately and never infer rollback.

Retained REST-write and operator-setup descriptions in the detailed resources
do not override [Supported Execution Route](#supported-execution-route). A missing
native mapping remains a blocker, not authority to select those descriptions.
Offering and functional-area selection remain owned by the existing routing
workflow; this task does not change the selected project context.

**Evidence status:** ordinary rows declare contracts, not a recorded live pass.
The four-component profile has reported historical 26D acceptance without a
linked reusable evidence bundle; that history cannot be independently verified
from this package. The nine-row profile remains a qualification candidate.
Require current-run import and saved-state evidence before reporting success. Neither
profile permits arbitrary row counts, additional objects or other new-parent
edges; standalone cardinalities remain binding.

Import completion and saved-setting verification do not prove activation,
transaction processing, transformation execution, delivery or atomic rollback.
The separately requested Customer Acceptance workflow covers its declared
messaging-test scope; it does not create a transactional purchase order.

### Common Resource Execution

Read the task's ora-resource rules through the compiled registry and the
FusionApps task-node execution guide before evaluation. Task identity and FSM
import mode are generated by pillar-skill-gen; all task-specific input, lookup,
default, dependency, design and error rules belong to the standard ora-resource files.
Do not create a second contract/configuration file or task-local processor.
Run Books own business inputs and processing/payload preparation; shared export
services own export mechanics and core.data-loader owns every import.

For create requests, use a completed exact-task header-only template and add
only the requested new records. Preserve all template members, CSV headers and
metadata; leave unrelated CSVs headers only. Existing setup rows are not part
of a create import. Identifier correction uses its own minimal existing-row
update contract, not the create template. Separate populated exports may qualify an unresolved
mapping, reference or duplicate check, but are not the import seed. A template
never proves target uniqueness or supplies missing relationship mappings.
Keep the existing validation and immutable Data Loader approval gates. This
is FSCR preparation policy; connection and partner-property import
qualification remains separate from the successful provider-only import.

For a customer request to create a new user-defined Service provider with a
Generic identifier, one standard File Export method and inactive XSL outbound
PO and inbound invoice connections together, select the bounded combined
profile in ora_input_validation.md (Combined Provider Creation Qualification).
Use operation qualify_combined_provider_setup and the existing assisted
Prepare Combined Provider CSV ZIP Run Book step. Historical notes report a
26D single-job import and saved-state preservation comparison for this scope;
no linked reusable evidence bundle establishes that result within this package.
Validate every component before delegating one immutable ZIP to Core Data
Loader; do not require separate parent creation jobs for this qualified scope.
For its requested follow-up verification use
post_import_verify_combined_provider_setup with the actual job and fresh
complete before/after exports. Other combinations retain their own qualified
profiles; this bounded contract does not establish arbitrary batching or rollback.

1. Resolve the project, exact task, operation and requested BO. Collect only
   missing business inputs according to ora_input_validation.md.
2. Execute applicable reference_lookup nodes using the declared Core client.
   Offer readable labels from the fresh REST response, validate supplied values
   and preserve exact returned codes. Do not report input completion before
   applicable resolver checks pass or treat values from another field as valid.
3. For one-provider create, select the confirmed assisted Prepare Provider CSV
   ZIP step in ora_input_validation.md within the existing Run Book provider
   task. Check the selected processing step and source-guided CSV rules.
   Preserve the source export and bind prepared-data review to the final bytes.
   If field representation, keys, relationships or a supported preparation step
   are missing, report the exact gap; do not invent data or an execution route.
4. Apply the existing same-host feature, catalog, privilege and environment
   gates. Export populated task data only through the shared task-export route
   with --data and the repository's required export approval. A completed header-only
   export may seed the declared provider-create preparation route;
   it is not a populated baseline and must never be imported unchanged.
5. Route the final immutable task ZIP through core.data-loader, its Task Hook
   evaluation and its single import-approval lifecycle. The resource graph's
   read-only success means ready for the next declared gate, not import success.
6. Return the prescribed Data Loader result; use its status/ProcessLog workflow
   when requested. Never replay an uncertain write or modify approved bytes.

Persist sanitized runtime artifacts and skill-run/token records through the
selected project's standard services. Never copy customer packages, protected
row values or credentials into tracked repository files or project artifacts.

### Business Object Scope and Lookup Intake

This task includes six FSM CSV BOs, not just providers. Recognize provider,
delivery method, collaboration message definition, external message definition,
and inbound/outbound connection creation requests; require direction for a
connection. For connection transformation mode, offer XSLT style sheet and
Mapping file and apply Connection Transformation Mode Selection in
ora_reference_lookups.md. Accept readable labels without defaulting XSLT;
Mapping file lookup remains gated until its runtime code and scoped request
are verified. The exact BO/member inventory, UI-required fields and observed
26D template types are in ora_input_validation.md. Public Documentation for Message Definitions in that resource owns the
current product guidance. Public API fields and task CSV cells are different
contracts; qualify their mapping through template/reference evidence.
These CSV BOs are not
registered Data Loader RESTBO names; do not populate the generated businessObject
or businessObjects manifest fields from this inventory.

For a provider create request, the resource graph starts with the Provider Type
and ID Type resolvers before input/package validation. Display live choices for
missing/invalid selections and retain valid customer values. There are no stored
dropdown results, static value restrictions, custom lookup adapters, or task-local
CSV builders. Resource registry readiness confirms its read-only graph, not a
release-qualified complete creation process.

Ask only for the four mandatory provider inputs defined in
ora_input_validation.md. Preserve optional values when supplied and leave
unspecified optional CSV cells empty; do not prompt for every source column.
The declared UserDefined and DelStatusUpdateEnabled defaults are
owned by ora_defaulting_rules.md and are applied only after the input and preparation
contract passes. Complete CSV input collection is followed by the confirmed assisted ZIP
preparation checks; source-export provenance and Data Loader approval remain
required.

Select the project and target host from confirmed project context before these
reads; ask for the target only if it remains ambiguous. Execute the declared
Core lookup clients, offer current Provider Type labels when missing, and
validate supplied ID Type through its own resolver after Provider Type resolves.
Do not ask for name, Provider ID or ID Type again when already supplied.
The task graph collects these lookup selections before the input, package and
import gates. A missing final ZIP does not change the lookup requirements;
package preparation starts only after the applicable input contract passes.

Customer responses should state the missing field with live choices or the
specific lookup failure and next action. Keep rule IDs, source file paths,
internal qualification instructions and token estimates in developer diagnostics
unless the user requests them. Never ask a customer to edit ora-resource files.

## Setup Task Metadata

- Task name: `Manage Collaboration Messaging Service Providers`
- Task code: `ORA_CMK_COLLAB_MESG_SERVICE_PROVIDER`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

Before a template export, populated setup-data export, or task-CSV import,
verify that **Simplified B2B Messaging (Gen2)** (technical feature code
`ORA_CMK_B2B_DOCUMENT_SETUP`) is enabled in the environment that
will perform that operation. Check the source environment before the export
POST. For import, check the destination during Task Hook preapproval validation
for the exact immutable ZIP, before presenting upload approval. Require a
fresh, exact-code, same-target result showing `EnabledFlag: Y`; a catalog flag,
prior export, Redwood page profile, or another environment's result does not
establish current opt-in state. If the feature is disabled, missing, ambiguous,
or cannot be read, stop before creating an export process or uploading an
import. Use the declared read-only client and decision rules in
`ora-resource/ora_reference_lookups.md` and
`ora-resource/ora_dependency_readiness.md`; do not enable the feature as part of
an export or import request.

Run the shared Core REST client against the exact host already selected by the
export or import workflow:

```text
python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py \
  --properties <selected-fusionEnv.properties> \
  --method GET \
  --query "q=FeatureCode='ORA_CMK_B2B_DOCUMENT_SETUP'" \
  --query "fields=FeatureCode,FeatureType,EnabledFlag" \
  --query "onlyData=true" \
  /fscmRestApi/resources/11.13.18.05/features
```

Confirm that `restBaseUrl` resolves to the selected host. Proceed only when the
response contains exactly one item with `FeatureCode:
ORA_CMK_B2B_DOCUMENT_SETUP`, `FeatureType: FEATURE`, and `EnabledFlag: Y`.
For import, record that result as evidence for
`verify_cmksp_b2b_document_setup_enabled` in the Task Hook rule results before
building the approval preview. A failed lookup blocks this task's export or
import. Recheck for each operation and target; do not reuse an earlier result.
The command only reads feature state.

Present feature status and blockers using **Feature State Presentation** in
`ora-resource/ora_error_handling.md`. Use the business feature name in customer
messages and retain the technical code and flags in sanitized diagnostics.
Distinguish an unverified feature from a confirmed disabled feature; apply
the blocker only to the selected operation governed by this gate.

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Procurement`
- Functional area / Setup Object: `Suppliers`
- Setup task name: `Manage Collaboration Messaging Service Providers`
- Setup task code: `ORA_CMK_COLLAB_MESG_SERVICE_PROVIDER`

This is an assisted, task-specific gate. The shared export CLI and Data Loader
do not invoke the preflight automatically. Route Service Providers work through
this skill and stop before those CLIs when the preflight is absent or blocked.
Direct use of the generic CLIs bypasses this gate and is not a verified
Service Providers workflow.




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


## Verification Coverage

The authored routes cover preparation, immutable review, approval, dispatch
and saved-setting checks. Runtime target compatibility and task-specific
privileges remain preflight requirements. No static default ID, retained
customer configuration or internal documentation link replaces that evidence.

Greenfield setup-skill acceptance requires the actual native import outcome
and a fresh exact-task exported-state comparison. A separately requested
message-processing test may use the declared Customer Acceptance workflow
after setup verification, with a generated sample and an existing supplier/site. A new
transactional PO is not a prerequisite to that standard CMK validation. A
separate real-PO event test needs the approved purchasing transaction and its
own execution route. Record configuration, sample processing, PO event
processing and destination receipt separately; none proves the others.

For a historical declared REST result, the retained `runbook_rest_verify`
branch may reconcile its saved-state evidence. It cannot select a new REST
write or count as greenfield FSM creation evidence.


## Fresh Environment Capability Selection

Select and retain the operation and reference profile at business intake,
before capability qualification or any reference GET. For
`qualify_combined_provider_setup`, select the bounded **Combined Provider
Creation Qualification** profile and its
`qualify_cmk_combined_provider_references` resolver. Its
[public capability bootstrap](ora-resource/ora_reference_lookups.md#combined-provider-public-capability-bootstrap)
qualifies only already-declared public resource paths through Core per-resource
describe checks, even when root discovery omits them. A successful compatible
describe is required before the corresponding collection read; feature and
generic lookup parent/child qualification follow their distinct contracts there.
Root discovery is not a prerequisite for this bounded profile. It does not
require `b2bDocuments`, `b2bProviders`, `b2bConnections` or `b2bDeliveryMethods`.

For general runtime-resource profiles, retain the task-owned
[metadata qualification](ora-resource/ora_reference_lookups.md#runtime-route-handoff-and-recovery) through the existing Core REST client
for the configured active project. Connection automation requires the exact
b2bDocuments, b2bProviders, b2bConnections and b2bDeliveryMethods resources;
message selection uses b2bMessageDefinitions and genericLookups under their
existing contracts. Request only resources applicable to the operation.

Current named metadata links and passing per-resource describe checks qualify
automated reads; a prior capture is optional evidence, not a bootstrap input
required from the customer. Select an already qualified public/native FSM
reference profile at intake when its prerequisites match the requested scope.
A missing required resource returns the exact reference or capability gap;
it does not select assisted screen setup. Do not reinterpret an API, schema
or authorization failure as absence. Preserve the selected profile and stop
before preparation when its required evidence is unavailable.

The bounded exception does not apply to other operations merely because they
reuse a resolver. It permits no undeclared endpoint, scope expansion, profile
switch after failure, UI fallback or REST write. Preserve target identity,
privilege, schema, finder, pagination, native export, collision, immutable
package, Task Hook and approval gates. Honor enforced approval restrictions for
the current operation; never bypass an enforced rejection or replay a rejected
check. Any live qualification must pass the current workflow's normal
automatic approval review.


## Customer Acceptance in the Configured Environment

Select this workflow only for a separately requested message-processing test.
A customer business document requesting initial setup is tested through FSM
creation and fresh-export verification, without entering this browser flow.
This is a qualified UI validation route, separate from configuration imports, operator-performed setup, and transactional PO creation. It never resumes or retries
an earlier uncertain write. The project Run Book must be active and its origin
must match the configured environment. Preserve the project's offering context.
Use existing suppliers and sites; do not create them as a CMK prerequisite.

Oracle's [outbound validation procedure](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/facmm/validate-outbound-collaboration-messaging-setup.html)
provides sample-message processing without a new purchasing transaction.
The sample validates messaging setup; it does not establish that purchasing
created, approved or communicated a real PO. [Redwood navigation](https://docs.oracle.com/en/cloud/saas/readiness/scm/26d/proc26d/26D-procurement-wn-f50500.htm)
depends on the current model; never enable or disable features just to test.

### Declared browser adapter and preflight

The browser adapter is the available CUA browser API, using only its documented
navigation, rendered-page reads and UI controls. No injected network calls,
credential extraction, guessed REST endpoints, or direct database access.
The implementing assistant may operate nonsecret UI controls in this route;
credential entry remains with the user in their own browser. This does not
alter the separate Core assisted-save contract.

1. Run customer_acceptance_prepare through the task graph. Its terminal
   ACCEPTANCE_UI_READY permits read-only preflight only. Open the configured
   HTTPS origin in a browser and use an existing authenticated session. If the
   application requires sign-in, record auth/authz blocked and request user
   sign-in through the normal login screen; never collect credentials or use
   an API access token as a browser login. A gateway failure is transport/environment.
2. Navigate through the visible Collaboration Messaging work area. For classic
   flows select Validate Outbound Collaboration Messaging Setup. If the
   current Redwood experience exposes History and Validate Outbound Messaging,
   use that visible action. Determine classic versus Simplified Configuration
   from the current page and preserve it. Missing task access is an auth/authz
   or catalog/feature blocker; do not flip the model or probe hidden pages.
3. Verify current test privilege, exact existing supplier/site, provider and
   outbound PO document/definition. Read all applicable choices and current
   connection status. Do not choose an arbitrary first supplier or change a
   shared connection solely to induce an error. A record must be an identifiable
   test fixture in the current environment before processing a test payload.
4. Select the document's business process and existing recipient. Generate the
   sample payload through the visible Create Message Payload action. Retain
   real identifiers and the immutable payload only in a protected local folder
   outside the repository/project. The customer document may name business
   entities; resolve them here rather than asking for TaskCodes or numeric IDs.
5. For each Process action, resume customer_acceptance_execute. Require current
   page/privilege evidence, exact selected identities, payload hash, destination
   and effect. Use an already confirmed Loopback connection for processing-only
   tests, or a confirmed controlled test destination for a delivery case. An
   Active connection to an unverified supplier endpoint cannot pass the gate.
   Do not create or alter transport configuration in this acceptance route.
6. Present the exact environment and nonsecret test preview before Process and
   retain operation-specific approval according to the active project rules.
   A user's request for a suite does not fabricate approval timestamps or waive
   a route's approval gate. Click Process once; a timeout/uncertain response is
   reconciled through the visible history/detail screen, never clicked again.
7. Record the actual message result and inspect Details, Configuration, Delivery
   Methods, Original Message and Transformed Message as available. For negative
   malformed-payload cases, use only the isolated test scope; if the UI cannot
   accept an edited payload, mark that case unsupported instead of inventing
   an injection route. Never corrupt shared supplier, connection or credentials.
8. Resume customer_acceptance_verify with actual observations. Record input
   rejection separately from transformation/processing failure. Successful
   Loopback processing has delivery not_attempted. A delivery pass additionally
   requires matched destination receipt; a UI success alone cannot prove it.

### Customer test record

Record every test prompt, exact synthetic business document, expected behavior,
actual response, execution level (conversation, live UI validation, live message
processing or destination receipt), times, result, diagnostic class and evidence
reference. Keep passing cases as well as failures and blocked/not-run cases.
Use safe aliases in durable HTML records; never publish real supplier records,
payloads, credentials, opaque routes or private IDs. Synthetic documents must be
marked synthetic, and author-created test prompts must not be attributed to the
human customer. A planned case is never a passed case. Persist through existing
project services and token logging without changing central implementations.

## Read-Only Existing Provider Review

For a business request to check an existing provider before reuse, select
review_provider_setup at intake. This reads public provider identity/type only;
it does not create a supplier, provider, connection, purchase order or message.
Use the existing Core Fusion REST client after active Run Book/configured-origin
checks. The customer supplies a readable provider name; if omitted, return
current choices, never choose the first record. Keep current identities private.

The [public service-provider GET contract](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-b2bserviceproviders-get.html)
uses b2bServiceProviders. It is distinct from the b2bProviders UI runtime model.
First qualify its documented per-resource describe; then perform the owned
resolve_cmk_public_provider_review lookup. A missing UI runtime catalog entry
does not establish that this separate public resource is unavailable. Select
this public review independently before its first call; it is no retry or write
fallback. Stop on failed schema/auth/transport checks and report that result.

Return exact match, no match or business selection required using the actual
complete collection. A matching provider proves identity/stored type coverage
only. Delivery, supplier linkage and receipt need their own evidence. Do not
state that a provider is fully reusable from its existence alone. The 26D URL
for this REST topic was unavailable when checked; 26C is the latest accessible
public contract and must be checked against deployed metadata.

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

## Provider Saved-State Verification

After a requested provider import result is completed successfully through
Core Data Loader, use post_import_verify_provider with its approved private
intent, final archive hash, processing result and before-namespace evidence.
The invoking Run Book obtains a fresh populated exact-task export through the
existing shared task-export workflow after the normal feature, identity,
privilege, catalog and export-approval checks. This is verification evidence,
not another import seed, and it remains private. Reenter this task's provider
verification resource branch with the completed export. Do not poll an accepted
initiation automatically; follow Data Loader's result-request boundary.

Compare every explicitly requested provider value and declared CSV preparation
default against one exact exported name/stored-flag identity. Optional settings
that were unspecified are observed separately; do not claim their server
defaults were supplied by the customer. Service Provider public identity reads
can corroborate their documented scope; Direct-provider verification must not
fail solely because that distinct public collection does not expose Direct.
No verification step writes, repairs or resubmits a provider. Report processing,
requested-state comparison, and created-versus-existing evidence separately.

## 26D Documentation Qualification

Use the 26D Collaboration Messaging guides and current configured-target
schema/export evidence for this acceptance campaign. Oracle's
[26D book index](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/books.html)
currently links its SCM REST guide to the published 26C API reference.
Keep that public linked reference where applicable rather than inventing a 26D
REST URL. The index link does not itself qualify a target model, field mapping
or operation; retain all current deployment, scope and privilege checks.

## Public Message-Backed FSM Connection Profile

For a new Inactive inbound/outbound connection using an existing Service
Provider and an already represented public document/message pair, select
reference_profile public_message_backed_fsm at intake. This is the existing
FSM connection preparation/import workflow, with a separately qualified public
reference profile. It is not a fallback write after an API or import failure.
Resolve its document/provider/message/status/delivery contracts through the
same five owning resolvers; all other requests retain their existing profiles.

Use the existing header-only exact-task template for preparation and a separate
fresh complete provider-task populated export for full provider/connection/
delivery reference and name coverage. Never use populated rows as the create
import seed. The existing connection field mappings in ora_input_validation.md
apply: append only the requested direction-specific row; preserve the other
members, metadata and headers. All keys remain business references; do not
allocate PartnerMessageId or a customization ID. New connections use their
exact customer name, selected MessageName/ServiceProviderName, stored
SPUserDefined, current OverrideStatus code and selected TransformMode. Outbound
also uses the verified primary DeliveryMethodName and any explicit alternate.
No new retention, attachment or XPath mapping is introduced by this profile;
unspecified optional cells remain empty.

The supported current-reference pair must exist in the published message
collection, including its document/direction/type and provider-or-unassigned
eligibility. The profile does not create an unrepresented document, transform
or external format. Inactive test setup neither activates a document nor sends
a message. Active and other modes retain their existing conflict/design checks.

For requested test results after successful processing, select
post_import_verify_connection_export with approved immutable row intent and
complete before/after exact-task exports from the declared shared export step.
The input resource compares every supplied field and explicit blank in the
intended connection row, including direction-specific membership and retained
provider/message relationships. Require before-absent and after-one identity
for a strict create; preserve unrelated rows. This is exported business-state
verification, without a claim about REST IDs, credential connectivity or PO
receipt. The existing live-connection verification profile remains available.

Public sources: [26D outbound setup](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/facmm/define-outbound-collaboration-messages.html),
[26D inbound setup](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/facmm/define-inbound-collaboration-messages.html),
[public message eligibility](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-b2bmessagedefinitions-get.html)
and [CMK setup export/import](https://docs.oracle.com/en/cloud/saas/readiness/scm/26c/sccv26c/26C-sccv-wn-f46531.htm).

## Predefined Business Event FSM Connection Profile

Select `reference_profile public_provider_or_unassigned_fsm` together with
`delivery_evidence_profile predefined_business_event_fsm` at intake for one new
**Inactive Invoice - Outbound XSLT** connection under an existing user-defined
Service Provider. Retain the existing document, provider, eligible-message and
status resolvers. The owning delivery resolver's
[Predefined Business Event Connection References](ora-resource/ora_reference_lookups.md#predefined-business-event-connection-references)
requires a compatible current saved connection demonstrating this predefined
primary value in the same provider/document/mode scope, plus independent
eligibility of the requested message. No customer fixture is a fixed input.

This branch accepts the predefined primary reference without a provider-owned
method row. It does not create a delivery method, qualify another provider,
document, transformation mode or alternate method, permit Active/Loopback,
change an existing row, or waive an already-configured association conflict.
Apply [the bounded inputs](ora-resource/ora_input_validation.md#predefined-business-event-connection-inputs),
existing assisted template-based one-row preparation, Core Data Loader approval
and FSM import, then all-object exported-state verification. UI/export evidence
qualifies representation; native FSM create acceptance remains to be tested.
The supported-operation matrix's ordinary connection route uses this exception
only when this exact profile and all its prerequisites apply.

## Existing-Association FSM Reference Profile

A customer may request verification or reuse of an already configured
provider/document/message combination. Select reference_profile
existing_connection_reference_fsm at intake. Require a current complete
same-target provider-task export containing that exact existing connection
association and its provider/stored flag, plus a current public message tuple
with the same MessageName, document/direction and TransformMode. The existing
association is current Fusion evidence for this narrowly retained relationship;
it does not establish eligibility of a different message or a new provider.

A current existing association qualifies its references and read-only reuse;
it does not establish permission to insert that association under a new name.
Strict create checks the provider/document/message association in addition to
the name before Core Task Hook/Data Loader approval. A known existing tuple
returns an association conflict even when Inactive was requested. Reuse
only the explicit current primary/alternate names belonging to that provider;
never substitute the isolated test provider's method under another provider.
No source connection key enters the new row. Omitted optional settings remain
unspecified; source values are copied only when the customer explicitly asks
for those exact values and their existing mappings are qualified.

The five owning reference resolvers use the profile's exact existing
association contract before any legacy runtime lookup. A current public
finder no-match is preserved as coverage evidence and is not silently widened.
This independently selected existing-association profile uses the supported
complete task export as its relationship source; it cannot validate a new
unrepresented association or turn a failed write into another route.

## Existing Connection Reuse from Exported State

For ensure_connection_setup with existing_connection_reference_fsm, the invoked
shared workflow provides a fresh completed full task export. The same owning
connection-state resolver compares the requested business name/provider/flag,
exact public document/direction/message/mode tuple, current status code and any
explicit mapped delivery selections to one exported row. Preserve unspecified
settings, and require every supplied setting to have a qualified comparison.
No numeric ConnectionId, API child visibility or historical import is required
for this business-state reuse profile; none is invented or claimed. Complete
scope and no match return absence; multiple names or requested unmatched fields
block the reuse claim. A matching row follows the existing reconciliation/reuse
terminal and performs no write. This profile cannot verify credentials or a
field missing from the task export.

## Existing Outbound Delivery Reference Verification

For existing-connection reuse, select delivery_evidence_profile
public_provider_child at intake when public provider-owned delivery evidence
is intended. The owning delivery resolver follows the current provider's
returned deliveryMethods link, qualifies its metadata and complete scope, and
checks exact method name and provider identity. The public contract is
[Get all delivery methods](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-b2bserviceproviders-serviceproviderid-child-deliverymethods-get.html).
An export omission is not proof the referenced method does not exist. This
profile supports only the existing requested-state reuse comparison; it does
not establish new connection eligibility, global delivery-name absence or
method-setting verification. Preserve the original export-only profile and
all downstream feature, requested-field and reconciliation checks. A failed
read is not permission to choose another provider, invent an identity or
create a replacement method.
