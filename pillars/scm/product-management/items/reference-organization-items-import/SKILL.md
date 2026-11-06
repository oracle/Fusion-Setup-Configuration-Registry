---
skill_id: "scm.product-management.items.reference-organization-items-import"
name: "Reference Organization Items Import Setup Task Guidance"
description: "Prepares or validates a Reference Organization Items FBDI source ZIP and delegates approval and import to the installed core.data-loader approval workflow."
layer: "pillar"
pillar: "SCM"
offering: "Product Management"
functional_area: "Items"
functional_area_code: "ORA_EGP_FA_ITEMS"
task_code: "CUSTOM_EGP_FBDI_IMPORT_REF_ORG_ITEMS"
task_name: "Reference Organization Items Import"
parent_skill_id: "scm.product-management.items"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "FBDI"
businessObject: "Reference Organization Items"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "import"
execution_mode: "hybrid"
owner_team: "SCM product management pillar team"
version: "0.3.12"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "customer_reference_org_source"
  - "reference_organization_import_mode"
  - "reference_organization_readiness_evidence"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "generated_fbdi_zip"
  - "reference_organization_mapping"
  - "core_data_loader_handoff"
  - "data_load_execution_result"
  - "skill_run_record"
  - "token_usage_record"
uses_core:
  - "core.data-loader"
  - "core.fusion-api.rest-api-client"
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
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/product-management/items/reference-organization-items-import/current/"
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
  - "Checks Item Index availability through declared read-only Core REST; delegates registered BO routing and deployed import-mode configuration to Core Data Loader."
  - "Prepares a validated reference-organization source ZIP in an explicitly selected controlled transient location outside the repository; delegates metadata reads, approval, upload and import initiation to core.data-loader."
  - "Registers non-sensitive business decisions, run references and token usage through the declared project services; loader control-state retention follows the selected Core contract."
required_privileges:
  - "Access to the Fusion Item Search endpoint required by the declared Item Index readiness check."
  - "Manage File Import and Export (FND_MANAGE_FILE_IMPORT_AND_EXPORT_PRIV)."
  - "Manage Item (EGP_MANAGE_ITEM_PRIV)."
  - "Target-environment access and Data Loader metadata, upload, initiation and requested-status privileges required by core.data-loader."
---

# Reference Organization Items Import Setup Task Guidance

## Purpose

Prepare the mapping and validate the dedicated FBDI package for assigning existing items and, when selected, making their structures common to reference organizations. Use this task's own template and dedicated Reference Organization Items FBDI registration with the standard project/task and Core approval route. All Fusion transport and submission belong to `core.data-loader`.

Reviewer group: SCM Pillar Development Lead/SME and FSCR A-Team/core; QA reviews the functional test scenarios.

## Setup Task Skill Contract

- task_code: `CUSTOM_EGP_FBDI_IMPORT_REF_ORG_ITEMS`
- task_name: `Reference Organization Items Import`
- parent_skill_id: `scm.product-management.items`
- pillar: `SCM`
- offering: `Product Management`
- functional_area: `Items`
- functional_area_code: `ORA_EGP_FA_ITEMS`
- available_flag: `Y`
- export_import_supported_flag: `N`
- csv_export_import_supported_flag: `N`
- dataloader_import_mode: `FBDI`
- businessObject: `Reference Organization Items`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill for `Reference Organization Items Import` under `Items`. This assigns existing items using the registered Reference Organization Items FBDI object and its reference-organization template. It does not create items or use FSM setup-data CSV import.

## Setup Task Metadata

- Task name: `Reference Organization Items Import`
- Task code: `CUSTOM_EGP_FBDI_IMPORT_REF_ORG_ITEMS`
- Available: `Y`
- Export/import supported: `N`
- CSV export/import supported: `N`
- CSV export/import routing: `not supported`
- Data Loader import mode: `FBDI`
- Business Object: `Reference Organization Items`

## Source and route

Use the current release-compatible public Oracle `ItemImportReferenceOrgTemplate.xlsm`, its export instructions and linked control files as the schema authority. Oracle documents `EGP_IMPORT_REF_ORG_ITEMS_INT`, `EGP_IMPORT_REF_ORG_ORGS_INT`, and `EGP_IMPORT_REF_ORG_STRUCT_INT`, with the process `Import Reference Organization Items` and public UCM account `scm/item/import`. Keep template and package integrity values inside the selected Core validation lifecycle, never project records. Persist only public page/workbook URLs, release and retrieval time as template provenance.

Sources: [Reference Org Item Import](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/oefsc/referenceorgitemimport-3174.html), [template and scope guidance](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/faipr/organize-your-data-in-the-fbdi-spreadsheet-import-template.html), [interface loading](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/faipr/load-data-from-oracle-webcenter-to-interface-tables.html), [import modes and verification](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/faipr/import-data-from-the-item-management-interface-tables.html), and [feature enablement and access](https://docs.oracle.com/en/cloud/saas/readiness/scm/26b/plm26b/26B-plm-wn-f43267.htm). The public facts were checked against 26B; confirm the target release and retrieve its compatible template before each test. Do not assume a later release has the same export contract.

The custom setup task has `CSVExportImportSupportedFlag: N`; this flag concerns FSM setup-data CSV export/import. It does not rule out the separate FBDI process documented by Oracle.

## Template and Package Contract

Derive the export contract from this run's reference-organization workbook and
control files. Validate headerless root-level CSVs,
exact member names and relative workbook order, complete field counts including
trailing blanks, encoding, lengths, and one numeric Batch ID. For this template,
BATCH_ID is the first exported field.

Supported members are EgpImportRefOrgItemsInt.csv, EgpImportRefOrgOrgsInt.csv,
and EgpImportRefOrgStructInt.csv. Include only populated sheets and require the
members needed by the resolved assignment/structure mode. Unexpected members,
headers, mixed batches, changed columns, or unsafe ZIP paths block validation.
Use the preparation helper's `--dry-run` for local validation. For supplied
facts, select `--output-zip <absolute-transient-path>` to create a source ZIP;
for an existing archive, select `--native-zip <source.zip> --handoff-check`.
The helper never starts a Core session or submits a load.

## Core Contract and Source Boundary

Before source preparation or Fusion calls, select the installed Core contract
using [Core loader handoff](references/core-loader-handoff.md). Read the current
Core skill and CLI capabilities; use its documented in-memory session or retained
preflight workflow. Do not infer capabilities from an environment/branch name,
require a private Core Python module, or change Core to fit this pillar.
Unknown/inconsistent capabilities block before side effects.

Local preparation is domain-only and independent of Core Python imports. Create
one validated source ZIP in an explicitly selected owner-only transient location
outside repository/project workspaces, without overwrite; keep raw mapping JSON
in memory. A supplied native ZIP is validated unchanged. Preparation never
starts a Core session, authenticates, uploads or submits.

Core owns artifact capture/retention, task validation dispatch, preview, approval,
integrity verification and submission. Apply the selected contract's lifecycle:
sessions keep their state in memory; preflight Core may retain only the artifacts
and envelopes its documented workflow requires. Never manufacture approvals,
substitute a custom adapter, or switch routes after a failed submission. Keep customer rows, payload copies and credentials out of project records.
The pillar creates no independent preview/approval files. Core-required
non-sensitive integrity metadata and Task Hook evidence follow the installed
Core contract; session control state remains memory-only.

Use the registered Reference Organization Items object through Core's normal FBDI routing.
The declared readiness, mode, batch and business-scope gates apply to both Core
contracts; source preparation alone authorizes no Fusion change.

## User Intake and Missing Requirements

At intake, assess all applicable requirements below using the request, supplied
files and existing project business context. Report every known missing or
invalid requirement together, rather than asking for one field per turn. Do not
perform Fusion calls merely to populate this checklist.

| Requirement | What the user provides or selects | When needed |
|---|---|---|
| Project / Run Book | Existing project and Run Book, or a request to create them through the routed workflow | Before execution |
| Import operation | Assign items, make structures common, or both | Always |
| Batch ID | One numeric ID shared by the populated sheets and import request | Always |
| Existing items | Item numbers and their existing definition-organization context | Assignment, or structure selection using the item list |
| Organizations | Target reference organizations, or definition organizations with an explicit intended scope of associated references | Always |
| Association context | Supplied project/business evidence identifying the definition/reference organization relationships | Before scope validation |
| Structures | Existing structure selectors and intended common-structure scope | Structure-only mode, or supplied selectors in combined mode |
| Oracle template | Compatible ItemImportReferenceOrgTemplate.xlsm, with its export instructions available for validation | Before package validation |
| Import source | Item/organization/conditional structure facts in the request, table, document or workbook; alternatively an existing FBDI CSV ZIP | Always |

Explain that this is an FBDI flow: template mapping and CSV ZIP preparation,
interface loading, then Reference Organization Items Import with Batch ID and
Import Mode. Link the [file preparation steps](references/fbdi-processing.md).
For request/document/workbook input, the assistant extracts facts and maps them
to the current template, resolving ambiguity with the user before invoking the
preparation helper. The user does not need to run Excel macros or supply a ZIP.
The helper creates a validated transient source ZIP for the selected Core workflow; creating this source does not authorize upload or import.
A supplied native FBDI ZIP remains supported and is validated unchanged.

For a blocked intake or task validation, show a concise table:

| Requirement | Status | What is missing or invalid | Next action |
|---|---|---|---|
| Applicable requirement | Missing, Invalid, Ready, Not applicable, or Not assessed | Exact field/file or conflicting business scope, without customer rows | Concrete action and whether the user or workflow supplies it |

Use Ready only for requirements actually assessed. Mark conditional structure
requirements Not applicable for assignment-only mode. Use Not assessed for
checks requiring a later stage; never treat an unassessed item as passed.
Do not ask for execution approval while a mandatory requirement is missing or
invalid. Once core owns validation/preview, keep its prescribed output unchanged
and put task blockers into its rule-result issues rather than replacing its
final preview with this checklist.

Environment identity, connectivity, authentication, privileges and live loader
metadata remain with `core.data-loader` and its declared dependencies. Do not
add independent pillar environment checks or ask the user for secrets, tokens
or duplicate environment evidence. The privilege declarations and Oracle
feature references document product prerequisites, not an executable pillar
probe; feature opt-in is not independently checked by this version. Do not
claim core verifies feature enablement unless its actual result says so.

## Loader Handoff Scope

Batch ID is carried in CSV fields;
source mode is validated against populated members and requested scope. The
registered FBDI route and active Core Run Book/task bind standard submission.
The live route supports only `ORA_REF_ORG_ASSGN_BOM_COMMON`. Block other requested modes without replacing them; offline validation remains available. Core executes using the registered BO's configured Import Mode; the pillar does not inspect `LoadAdapterConfig` or forward a per-run mode argument. The validated source mode records intent, not a verified deployed setting.
Report initiation acceptance only; status and business completion require later
evidence. A separate ESS step remains outside this loader handoff.

## Workflow

1. First select the documented installed Core contract through references/core-loader-handoff.md; inconsistent capabilities block before preparation or Fusion calls. Use the routed implementation project and Run Book task `CUSTOM_EGP_FBDI_IMPORT_REF_ORG_ITEMS`. Resolve the existing task context; confirm Batch ID, source and import mode. Use the Data Loader-selected environment context without adding pillar environment checks. Complete the user intake checklist above. Apply [FBDI preparation and handoff](references/fbdi-processing.md), then read every task-local rule resource and the compiled registry. Apply [Import Mode defaulting](ora-resource/ora_defaulting_rules.md): omitted mode defaults to `ORA_REF_ORG_ASSGN_BOM_COMMON`; preserve explicit intent, blocking non-default modes for live execution until per-run ESS forwarding is supported.
2. Run the declared Item Index readiness GET through Core REST and retain its classified result for this validation cycle. Continue only for available; unknown index returns the remediation handoff to Product Management orchestration, and all other failures stop. Confirm the existing item/organization business context and, for structure modes, the source structures using the named project baseline/business evidence in `ora_reference_lookups.md`. Resolve missing or conflicting business scope before preview. Do not add environment identity, connectivity, authentication, privilege or feature-enablement checks here. Core owns its declared environment/authentication/metadata preflight; feature availability is documented context, not a separate task gate in this version. Do not imply that core automatically verifies feature opt-in.
3. Map facts against the reference-org workbook/control files. Derive organization scope from supplied selectors: a supplied reference is the target; retain its definition as business context. Resolve ambiguity before preparation. For raw facts, run the local helper with `--output-zip` to create one validated source ZIP in the controlled transient location. For a supplied ZIP, run `--native-zip ... --handoff-check` without modifying it. Both paths reject unsupported live modes before handoff. Read [preparation and invocation](references/fbdi-processing.md) for exact commands.
4. Follow the selected workflow in [Core loader handoff](references/core-loader-handoff.md) with the exact business object, active Run Book/task context and run configuration. Select the Core contract before invoking the source helper or any Fusion call. Core owns its metadata, target and artifact preflight; never substitute another object or adapter.
5. At Core's task-validation handoff, evaluate its captured nativeSources (session) or final immutable artifact (preflight) against this run's template contract, Batch ID and intended scope. Do not reopen the original source after Core fixes the upload artifact. Apply the compiled task graph, retained Item Index result, supplied business evidence and Core-returned routing/preflight evidence. Put validated Batch ID, requested Import Mode intent and ordered findings into ruleResults; do not claim the deployed mode was independently verified. These are validation evidence, not extra outbound ESS parameters; missing evidence blocks approval.
6. Use the installed Core's preview and contextual approval lifecycle unchanged. For a session, retain its handle and previewId. For a preflight, use only Core/Task Hook-generated artifacts and envelopes and verify the approved final artifact through Task Hook. Never fabricate or manually edit approval material. Changed/missing state requires fresh validation and approval; preserve the selected contract rather than falling back to another execution route.
7. After acceptance, return the core initiation report unchanged. Acceptance is not completion. Do not poll automatically. A later user status request follows the core status workflow with the accepted request in the same environment; never upload or initiate again as a status check.

## Error Handling and Redaction

Load `ora-resource/ora_error_handling.md` before preview or live work. Classify
failures as input_validation, catalog_or_metadata_mismatch,
auth_expired_or_invalid, authorization_or_privilege, transport_or_environment,
fusion_api_error, process_timeout, process_failed, artifact_persistence, or
approval_blocker. Stop on a failed validation or missing prerequisite. Core
owns permitted read-only recovery and authentication; no mutation is
automatically retried. Use an explicitly supplied compatible ref-org template and
control files for this run without first attempting a download. Otherwise resolve
the workbook and linked controls from the cited public Oracle page. Public reads
have a maximum 60-second timeout and no automatic retry. Report the attempted
public URL, elapsed time and actual transport/HTTP error; a fetch failure does
not prove schema drift. Stop on an unverified release or export contract. A pending requested status is not a polling timeout:
return it immediately and wait for another user request.

Redact credentials, secrets, tokens, token-cache contents, private keys,
authorization URLs and raw customer rows. Never print loader hashes, previews, approval JSON or encoded payloads.
Session mode retains these only in memory; the preflight workflow retains only
Core-required control files in its private transient location. Return actionable field-level
issues without reproducing source data. Follow core's separate status-log
contract rather than generating pillar diagnostic reports.

## Result Verification and Recovery

For a requested terminal-success status, verify the intended assignments and common structures in the reference organizations using approved target-environment readback evidence or the Fusion application. Check selected items, organization membership, structure selection and any unexpected broad assignments. Without result evidence, report submission/load status only, not verified business completion. This skill declares no direct Fusion readback endpoint; request evidence or a separately routed readback workflow rather than guessing one.

Core status handling owns authoritative FBDI ESS diagnostics and any logs permitted by its status workflow. Retain only non-sensitive business decisions, public provenance, task/run references and token usage through the project services; never independently persist loader snapshots, previews or approvals, and never store raw rows or payload copies in project records. Core-generated non-sensitive integrity metadata and required Task Hook evidence follow the installed Core contract; loader control files use its controlled transient location. The one transient source ZIP created by the local preparation step follows the separate source-artifact contract above; Core retention follows the selected contract; session mode creates no disk-backed approval copies. Do not use project evidence to reconstruct a missing or expired Core approval.

Interface cleanup is optional and separate: Oracle documents `Purge Interface Tables` with this import process and request ID. Do not purge as part of an import or test; use a separately selected workflow and its approval gate. Never substitute the enterprise-wide Upgrade Product Management Data process.

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `N`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

Do not route FSM setup-data CSV export work to `shared.setup-export.task-level-export` or FSM CSV import work to `core.data-loader` unless live Fusion metadata or Oracle guidance confirms support. The dedicated FBDI workflow above is a distinct route. Use `shared.validation.setup-data-validator` only when a setup data artifact is available for review. Use `shared.validation.reference-data-validator` when the task depends on cross-pillar reference data.
## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`
- `customer_reference_org_source`
- `reference_organization_import_mode`
- `reference_organization_readiness_evidence`

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `generated_fbdi_zip` (validated transient source ZIP; existing native ZIP preserved)
- `reference_organization_mapping` (in memory)
- `core_data_loader_handoff` (selected Core contract and approved artifact)
- `data_load_execution_result`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `scm.product-management.items` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

The Oracle documentation establishes the template and scheduled process, not a live adapter identity or parameter contract. This skill delegates execution to the selected core Data Loader workflow; it never authorizes direct UI, REST or ESS execution. Its registry validates task rules, not environment availability. The Data Loader metadata, active Core Run Book/task binding and project workflow must pass preflight before live work.
