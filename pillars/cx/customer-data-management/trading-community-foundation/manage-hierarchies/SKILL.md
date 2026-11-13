---
skill_id: "cx.customer-data-management.trading-community-foundation.manage-hierarchies"
name: "Manage Hierarchies"
description: "Lists UI-eligible hierarchies by default, reads hierarchy detail through Applcore Trees REST resources, and imports user-supplied Hierarchy or HierarchyNode CSV files through Oracle CX Import Management. Node reads use a returned child link or a describe-confirmed exact fndTreeNodes collection fallback; the default list retains hierarchies with an active, currently effective version containing at least one node."
layer: "pillar"
pillar: "CX"
offering: "Customer Data Management"
functional_area: "Trading Community Foundation"
functional_area_code: "ORA_HZ_CDM_FOUNDATION"
task_code: "HZ_MANAGE_HIERARCHIES"
task_name: "Manage Hierarchies"
parent_skill_id: "cx.customer-data-management.trading-community-foundation"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "CXIMPORT"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "import"
execution_mode: "hybrid"
owner_team: "CX customer data management pillar team"
version: "1.2.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "fusion_environment_context"
  - "operation"
  - "read_operation"
  - "tree_structure_code"
  - "tree_code"
  - "tree_version_id"
  - "as_of_date"
  - "hierarchy_csv"
  - "hierarchy_node_csv"
  - "ordered_hierarchy_csvs"
  - "import_operation"
  - "import_activity_name"
  - "execution_approval"
  - "party_hierarchy_generation_options"
  - "party_hierarchy_generation_approval"
outputs:
  - "ui_aligned_hierarchy_inventory"
  - "hierarchy_inventory"
  - "hierarchy_detail"
  - "hierarchy_version_summary"
  - "hierarchy_node_summary"
  - "immutable_import_preview"
  - "ucm_upload_checkpoint"
  - "cx_import_activity_result"
  - "import_status_and_diagnostics"
  - "party_hierarchy_generation_result"
  - "post_import_verification"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "cx.customer-data-management.trading-community-foundation"
  - "cx.customer-data-management.trading-community-foundation.import-trading-community-data"
  - "cx.customer-data-management.trading-community-foundation.run-trading-community-party-hierarchy-generation"
  - "core.data-loader"
uses_core:
  - "core.data-loader"
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "core.fusion-api.ucm-rest-client"
  - "core.fusion-api.cx-import-export-management"
  - "core.fusion-api.ess-job-submitter"
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
  - "reports"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/customer-data-management/trading-community-foundation/manage-hierarchies/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/customer-data-management/trading-community-foundation/manage-hierarchies/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "report"
    default_location: "project/{project_id}/artifacts/pillars/cx/customer-data-management/trading-community-foundation/manage-hierarchies/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
oracle_supplied_guidance_files:
  - purpose: "Read and supplied-file routing checks"
    location: "ora-resource/ora_input_validation.md"
  - purpose: "Read resolvers and hierarchy import object routing"
    location: "ora-resource/ora_reference_lookups.md"
  - purpose: "Safe create-or-update import default"
    location: "ora-resource/ora_defaulting_rules.md"
  - purpose: "Read and import failure handling"
    location: "ora-resource/ora_error_handling.md"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "Uploads each approved user-supplied hierarchy CSV unchanged through the shared Trading Community CX Import workflow."
  - "Creates and activates one approved create, update, or delete CX Import Management activity for each supplied hierarchy object."
  - "May submit Party Hierarchy Generation only as a separate, freshly approved post-import action."
required_privileges:
  - "Fusion privileges to view Trees Management resources and the selected hierarchy."
  - "Privileges to upload to the live metadata-resolved UCM document account."
  - "CX Import Management privileges for Hierarchy and HierarchyNode."
  - "ESS privilege for Party Hierarchy Generation when separately requested and approved."
---

# Manage Hierarchies

## Purpose

Read accessible hierarchies and import user-supplied hierarchy header or member
CSV files through the shared Trading Community CX Import workflow. This skill
binds the hierarchy object, mode, and activity order, then delegates source
processing to `Import Trading Community Data`, `core.data-loader`, and their
declared dependencies. Those workflows may read, inspect, decode, parse,
classify, validate, hash, package, and otherwise process the supplied CSVs as
required by their existing contracts.

## Setup Task Contract

- Task: `Manage Hierarchies` (`HZ_MANAGE_HIERARCHIES`)
- Read route: `core.fusion-api.rest-api-client`, GET only
- Import route: `cx.customer-data-management.trading-community-foundation.import-trading-community-data`
- Import executor: `core.fusion-api.cx-import-export-management`, governed by `core.data-loader`
- FSM export/import: not supported
- FSM CSV export/import: not supported
- CX Import objects: `Hierarchy` and `HierarchyNode`

The catalog's FSM flags remain `N`/`N`; they do not prohibit this separate CX
Import Management route. Never substitute FSM import or generic Data Loader
`initiateDataLoad` for the declared CX Import adapter.

## Operation Routing

| User intent | Supplied file role | Exact object code | Exact ImportMode |
|---|---|---|---|
| Create hierarchy | Hierarchy CSV | Hierarchy | CREATE_ONLY |
| Import, create or update hierarchy | Hierarchy CSV | Hierarchy | CREATE_RECORD |
| Delete hierarchy | Hierarchy CSV | Hierarchy | DELETE_RECORD |
| Create hierarchy members | HierarchyNode CSV | HierarchyNode | CREATE_ONLY |
| Import, create, update, move, or reparent hierarchy members | HierarchyNode CSV | HierarchyNode | CREATE_RECORD |
| Delete hierarchy members | HierarchyNode CSV | HierarchyNode | DELETE_RECORD |

When the user says only `import`, default to `CREATE_RECORD` so Fusion may
create new records and update matching records. Preserve an explicit
create-only choice as `CREATE_ONLY`. Route an explicit literal delete as
`DELETE_RECORD`. For an unchanged user-supplied CSV, do not inspect or resolve
row identities before submission. Bind the destructive effect to Core Data
Loader's immutable preview and approval, then let Fusion Import Management
accept or reject the rows. Exact member-edge validation remains available only
when the user explicitly requests data validation or supplies identities
separately for record-level verification.

When both files are supplied, execute two independent activities. For create or
update, use dependency order: `Hierarchy` first, then `HierarchyNode`. For
delete, remove `HierarchyNode` members first, then the `Hierarchy` header. Each
activity has its own exact object, mode, immutable group digest, UCM checkpoint,
Data Loader authorization, and result. When exactly two unlabeled CSV paths are
supplied in one request, map the first path to `Hierarchy` and the second path
to `HierarchyNode`, then apply the operation-specific execution order. Present
that deterministic mapping and execution order in the immutable preview. Do
not combine the two files into one activity or infer roles from their
filenames. The declared shared and Core Data Loader workflows may inspect
either file as required by their contracts.

## Supplied CSV Contract

For a user-supplied hierarchy file:

- preserve the supplied source path and basename when handing it to the shared
  importer;
- allow `Import Trading Community Data`, `core.data-loader`, and every declared
  dependency they select to read, inspect, decode, parse, classify, validate,
  hash, package, or otherwise process its headers, rows, and bytes as required;
- do not stop, request a waiver, or report a contract conflict merely because a
  declared dependency inspects, parses, or validates the CSV;
- do not add independent Manage Hierarchies business-data checks or task-local
  blocking validations beyond the selected shared and Core Data Loader
  contracts;
- invoke an optional generation or preparation helper such as
  `prepare_tca_import_csv.py` only when the selected shared workflow requires it
  or the user explicitly requests CSV generation or preparation.

The shared route remains authoritative for source review, file eligibility,
mapping detection, live object metadata, UCM account resolution, immutable
preview and digest generation, approval, upload, and activity creation. Normal
shared/Core Data Loader validation may reject an unusable source; this skill
must not preempt that workflow with a stricter hierarchy-specific rule. Fusion
Import Management remains authoritative for accepting or rejecting submitted
data.

## Import Workflow

1. Begin through the implementation router and select the implementation
   project. Load this skill's ready task-node plan.
2. Resolve exactly one configured Fusion environment and the supplied file role.
   Prefer explicit roles; for exactly two unlabeled paths, use request order:
   first `Hierarchy`, second `HierarchyNode`. Apply the operation table, then
   permit the declared dependencies to inspect the CSVs as required.
3. For each activity, invoke `Import Trading Community Data` with the exact
   object code, exact mode, and the single unchanged CSV. Use fixed high-volume
   routing for both hierarchy objects. For delete, pass `DELETE_RECORD`; do not
   inspect supplied rows or require a pre-delete Trees lookup. Fusion Import
   Management is authoritative for row acceptance or rejection.
4. Let `core.data-loader` produce the authoritative source review, UCM account,
   ordered group digest, Task Hook preview, and approval request. Run the
   task-local read-only bridge as
   `python3 scripts/hierarchy_cx_preflight.py <csv> --object-code <Hierarchy|HierarchyNode>`
   from this skill folder. It invokes Core Data Loader and extracts the
   authoritative `response.preflight.archiveSha256` from Core's structured
   approval-stop result. Consume that JSON internally to build Task Hook; do
   not stop because Core's user-facing Markdown omits the digest, and never
   compute or reconstruct a replacement digest. Core's normal CSV inspection,
   parsing, classification, validation, hashing, and packaging are explicitly
   permitted and must not be treated as a Manage Hierarchies contract conflict.
5. The Data Loader approval is authoritative for the matching unchanged CX
   import. Do not add a second Manage Hierarchies approval prompt. Any change to
   environment, bytes, basename, object, mode, activity name, UCM account, or
   schedule invalidates that approval.
6. After approval, follow the shared importer's checkpointed UCM upload and
   mode-aware CX Import activity creation exactly once. Never retry an uncertain
   upload or POST. Monitor and report Fusion's activity and data-file counts.
7. If both files were supplied for create or update, begin the `HierarchyNode`
   preview only after the `Hierarchy` activity succeeds. For delete, begin the
   `Hierarchy` header preview only after the `HierarchyNode` delete succeeds.
   Let the declared shared/Core workflow perform any source inspection it
   requires; Fusion remains authoritative for the import result.
8. Report the terminal CX Import activity and data-file result as Fusion's
   authoritative import outcome. If the user separately asks for hierarchy
   generation or record-level absence verification, route the shared
   `hierarchy-post-process` strategy. Party Hierarchy Generation is a separate
   ESS mutation with its own resolved parameters, preview, and fresh approval;
   an import approval never authorizes it. Without optional record-level
   verification, report a successful delete activity as processed in
   `DELETE_RECORD` mode, not as independently verified absent.

## Preflight

For supplied-file import, this skill preflights routing inputs: one configured
environment, a usable path, its explicit role or deterministic two-file
request-order role, and the exact object and ImportMode. Delegate source
inspection and all further preflight to the selected shared/Core Data Loader
workflow, including file eligibility, mapping detection, metadata, UCM account,
digest, adapter readiness, and approval freshness. For an unchanged supplied
CSV, exact-object `ImportSupport=Y` plus mode-aware `DELETE_RECORD` adapter
readiness is the live capability gate; Fusion may still reject unsupported or
invalid delete rows. Use only the bridge-returned
`archiveSha256` for the Task Hook preview. A missing digest in rendered
Data Loader Markdown is not a blocker when the structured bridge result is
`preflight_ready`; a missing or invalid digest in that structured result is a
real preflight-contract failure. CSV inspection, parsing, or validation by a
declared dependency is expected and must never be treated as a Manage
Hierarchies contract conflict.

Do not inspect a supplied `HierarchyNode` delete CSV to require `PartyId`,
`PartyNumber`, parent identity, `AsOfDate`, or any other row field. Fusion
evaluates those values after the approved unchanged file is submitted.

For reads, require the configured environment, supported operation, applicable
exact identifiers, ready task-node plan, and GET-only client route. Stop on an
unavailable declared route rather than substituting another endpoint.

## Supported Read Operations

| Operation | Required input | Result |
|---|---|---|
| `describe` | Exactly one configured Fusion environment | Live describe metadata for the read-only Trees resources |
| `list` | Optional exact Tree Structure Code and optional as-of date | One row per hierarchy having exactly one active version effective on the as-of date with NodeCount greater than zero |
| `inventory` | Optional exact Tree Structure Code | Raw header inventory: every accessible or exactly matching hierarchy after pagination completes, regardless of version status, effective dates, or node count |
| `hierarchy_detail` | Tree Structure Code and Tree Code | One exact hierarchy and its returned canonical and child links |
| `versions` | Tree Structure Code and Tree Code | Every version for the exact hierarchy after pagination completes |
| `nodes` | Tree Structure Code, Tree Code, and Tree Version ID | Nodes returned for the exact version after pagination completes |
| `full_read` | Tree Structure Code and Tree Code; optional Tree Version ID | Exact hierarchy, versions, selected-version nodes, labels, and data-source parameters |

Do not restrict reads to a client-side Tree Structure Code allowlist. Use live
describe metadata to select only readable projection fields; do not hardcode an
optional field such as `TreeName`, `Description`, or `Status` when describe does
not expose it. Query collections with exact filters and follow all pages. For
node reads, prefer the same-environment child link returned by Fusion. If that
link is absent, use the describe-confirmed `fndTreeNodes` collection only with
the exact current-run `TreeStructureCode`, `TreeCode`, and `TreeVersionId`;
never use an unscoped node query or another namespace.

Interpret an unqualified request to `list`, `show`, or `list hierarchies` as
`read_operation=list`. Default its as-of date to the current date in the
configured environment's execution context and disclose that date in the
result. This is a UI-aligned hierarchy-level list: its eligibility criteria
match hierarchies that can contribute rows to the UI's All Parties in
Hierarchies result. It returns one hierarchy row, not one party-membership row,
for each eligible hierarchy. Use `nodes` when the user asks for the detailed
membership rows. Run raw `inventory` only when the user explicitly requests all
headers, raw inventory, inactive/future/expired hierarchies, or empty
hierarchies.

## Read Workflow

1. Resolve one configured environment and load the task-node plan.
2. Default an unqualified list intent to `list`, resolve and disclose its
   as-of date, and validate the read operation and required exact identifiers.
3. Execute only the applicable GET resolvers from
   `ora-resource/ora_reference_lookups.md` through the core REST client.
4. Return environment, scope, match count, pagination completion, sanitized
   hierarchy data, applied eligibility criteria and as-of date when listing,
   and confirmation that no Fusion data changed.

Read-only operations do not require mutation approval.

## Result and Failure Contract

For import, return the target, object, mode, filename, canonical digest, activity
ID and name, UCM document name, status, counts, diagnostics, and any separate
generation result. Never expose credentials, authorization headers, token-cache
contents, encoded source data, or source rows.

If Fusion rejects supplied data, including `DELETE_RECORD` for the exact target
object, report its diagnostics and stop. Do not repair, rewrite, validate, or
resubmit the file automatically. If an upload or import POST has an uncertain
outcome, reconcile the existing checkpoint or activity; never repeat the
mutation. A successful delete-mode activity proves that Fusion processed the
activity in `DELETE_RECORD` mode. It does not independently prove a particular
record is absent; perform optional record-level verification only when
separately requested and the necessary identities are supplied outside the
opaque CSV.

## Redaction

Persist and display only sanitized routing, digest, external-ID, status, count,
and diagnostic evidence. Redact credentials, authorization headers, token-cache
contents, encoded documents, source rows, customer-sensitive values, opaque
canonical URLs, and raw Fusion payloads from output, diagnostics, run records,
and project artifacts.

## Hard Boundaries

- Never add an independent Manage Hierarchies CSV validation gate that blocks a
  source before the selected shared/Core Data Loader workflow evaluates it.
- Never block because `Import Trading Community Data`, `core.data-loader`, or a
  declared dependency reads, inspects, decodes, parses, classifies, validates,
  hashes, packages, or otherwise processes a supplied CSV.
- Never derive approval from a source-file hash or an agent-computed CSV-group
  hash. Use only `archiveSha256` extracted from Core Data Loader's structured
  preflight response by the task-local bridge.
- Never import both object files in one activity.
- Never route delete through a mode other than `DELETE_RECORD` or bypass Core
  Data Loader's immutable preview, destructive disclosure, and approval.
- Never inspect an unchanged supplied Hierarchy Member CSV to enforce PartyId,
  PartyNumber, parent, as-of-date, identifier-only, or pre-delete match rules.
  Fusion Import Management owns row validation for this pass-through branch.
- Never invoke FSM import/export or generic Data Loader `initiateDataLoad`.
- Never issue direct Trees REST `POST`, `PATCH`, `DELETE`, or `/action/` calls.
- Never duplicate Core Data Loader's approval for the same CX import activity.
- Never submit Party Hierarchy Generation without a separate fresh approval.

## Sources

- Oracle Cloud Customer Data Management: `How You Manage Hierarchies`,
  `Hierarchy Validation Rules`, and `How do I import hierarchy data?`, used for
  hierarchy scope and CX Import capability.
- `Import Trading Community Data`, used as the repository execution contract for
  unchanged supplied CSVs, object/mode routing, Data Loader authorization, UCM
  staging, CX Import activity creation, monitoring, and hierarchy post-processing.
