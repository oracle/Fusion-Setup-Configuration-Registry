---
skill_id: "scm.supply-chain-planning.supply-chain-planning-configuration.load-planning-data-from-files"
name: "Load Planning Data from Files Setup Task Guidance"
description: "Prepares and validates Planning FBDI ZIPs for ATP rules (including Backlog Planning rules), ATP rule assignments, sourcing rules, and sourcing assignment sets. Supports deletion of sourcing rules, sourcing sources, ATP rules, and ATP rule assignments through published XLSM/CTL flags and Planning Common via core.data-loader. Other Planning entities and assignment-set deletion are out of scope."
layer: "pillar"
pillar: "SCM"
offering: "Supply Chain Planning"
functional_area: "Supply Chain Planning Configuration"
functional_area_code: "ORA_MSC_VC_PLANNING_CONFIGURAT"
task_code: "ORA_MSC_LOAD_PLANNING_DATA_FROM_FLAT_FILES"
task_name: "Load Planning Data from Files"
parent_skill_id: "scm.supply-chain-planning.supply-chain-planning-configuration"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "FBDI"
businessObject: "Planning Common"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "import"
execution_mode: "hybrid"
owner_team: "SCM supply chain planning pillar team"
version: "0.5.1"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "planning_collection_entity"
  - "operation"
  - "deletion_targets_and_baselines"
  - "source_system"
  - "collection_type"
  - "target_fusion_release"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "template_resolution_record"
  - "csv_contract_validation_result"
  - "generated_fbdi_zip"
  - "fbdi_preview"
  - "deletion_summary"
  - "core_data_loader_handoff"
  - "skill_run_record"
  - "token_usage_record"
uses_core:
  - "core.data-loader"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/supply-chain-planning/supply-chain-planning-configuration/load-planning-data-from-files/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/supply-chain-planning/supply-chain-planning-configuration/load-planning-data-from-files/current/"
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
  - "Creates local CSV/ZIP preparation artifacts outside the repository; supplied files and existing outputs are never overwritten."
required_privileges: []
---

# Load Planning Data from Files Setup Task Guidance

## Purpose

Prepare one validated, immutable Planning FBDI ZIP from a business request,
a CSV, or a supplied ZIP. Hand that exact artifact to `core.data-loader` for
any later import. This skill does not authenticate, upload, submit ESS jobs,
or monitor a load.

Treat requests for a "Backlog Planning rule" or "Backlog rule" as requests
for this skill's ATP-rule FBDI flow. Use `ATPRules.csv` for the rule and
`ATPRuleAssignments.csv` for its requested assignments, including an
organization-level assignment. Do not require a separate Backlog/REST skill
or switch branches merely because the request uses Backlog terminology.
This routing alias does not add another CSV, business object, or supported
operation; requested fields must still map to the published ATP contract.

## Supported files

This table is the single maintained allowlist and direct template route.
The preparation scripts read it; there is no separate executable allowlist.

| Requested entity | Canonical CSV member | Published template | CTL target table |
|---|---|---|---|
| ATP Rules | ATPRules.csv | ScpATPRulesImportTemplate.xlsm | MSC_ST_ATP_RULES |
| ATP Assignments | ATPRuleAssignments.csv | ScpATPRulesImportTemplate.xlsm | MSC_ST_ATP_ASSIGNMENTS |
| Sourcing Rules | SourcingRules.csv | ScpSourcingImportTemplate.xlsm | MSC_ST_SOURCING_RULES |
| Sourcing Assignment Sets | AssignmentSets.csv | ScpSourcingImportTemplate.xlsm | MSC_ST_ASSIGNMENT_SETS |

Accept any nonempty requested subset, not all four by default. An unsupported
entity in a prompt blocks the whole request. A mixed ZIP is different: retain
the supported files in a **new** ZIP, preserve their bytes/order and the original
archive, and report exclusions. No supported files means no output or load.
Never rename an unsupported entity to a supported filename.

The registered BO display name is `Planning Common`. Product labels, tables,
or descriptions may still contain `Msc Common` / `MSC`; do not rename them.
The interface remains 135 and the existing UCM account remains unchanged;
Core resolves and binds live routing values rather than this skill hardcoding
transport parameters. Broader BO registration never expands the four-file scope.

## Preparation workflow

Read [CSV preparation](references/csv-preparation.md),
[template lookups](ora-resource/ora_reference_lookups.md), and
[input validation](ora-resource/ora_input_validation.md) for local preparation.
Read the remaining resource files and registry only when Core's Task Hook
selects their rules.

### Source system and collection mode

For every new request (prompt, CSV, or ZIP), require the user to explicitly
provide the Source System value in that request or a follow-up reply. If it is
missing or blank, ask: "Please enter the Source System value for this request."
Wait for that value before template downloads, CSV preparation, or live work.
Do not infer it from file contents, examples, environment configuration, saved
project context, or an earlier request. If the user already supplied it for this
request, do not ask again during preparation, preview, or upload approval.

Default collection_type to Net Change. This flow supports Net Change collection
only. Give this FYI once during intake, alongside the source-system question
when needed: "FYI: This flow supports Net Change collection and will use that
mode." Do not ask the user to choose or approve the collection mode. If Targeted
or another mode is explicitly requested, explain that it is unsupported and stop
that request; do not silently substitute Net Change or offer a mode-approval gate.
Core's separate approval for upload and initiation remains required.

### Steps

1. Classify the request as prompt generation, supplied CSV, or supplied ZIP;
   collect the required Source System and apply the collection-mode policy above;
   determine the supported members before downloading templates. For a load
   request, check the saved project/task/Run Book/environment context early,
   without authentication or live calls. A missing route must not cause
   automatic Run Book creation, merging, or configuration changes.
2. Use the user-provided source system and resolve the documentation release.
   Use the table above directly, verify its current pairing and source-system
   eligibility, and fetch each needed XLSM and CTL once for this run. Do not
   rediscover unrelated templates or use a prior run's cached layout.
3. Extract only requested tabs and CTLs with
   `scripts/inspect_planning_fbdi_template.py`. Save the compact contract once.
   XLSM labels/constraints map user intent; paired CTL positions define loader
   columns. Do not run macros, scan VBA, generate a filled XLSM, or render a
   spreadsheet merely to prepare machine-consumed CSVs.
4. For a prompt, resolve business values against the extracted contract, then
   use `scripts/prepare_planning_fbdi.py` to generate full-width CSVs with CTL
   headers and terminal `END`. For supplied CSV/ZIP input, use its source mode:
   validate and package/select existing bytes, without regeneration. A valid
   supported-only ZIP is returned unchanged. Save new ZIPs in a user-approved
   folder or controlled transient location outside the repository/project;
   there is no fixed Downloads or Temp path. Follow the output-location and
   access guidance in `references/csv-preparation.md`.
5. That same preparation command performs package/content validation, reopens
   newly written ZIPs, and returns SHA-256-bound evidence, row counts, member
   selection/exclusions, and template provenance. No separate scope-validator
   invocation or second template-resolution cycle is required.
6. Show the local preparation preview. Prepare-only requests stop here with
   `READY_FOR_CORE_DATA_LOADER`, explicitly not live-validated or submitted.
   Consolidate required redacted project artifacts, run record, and token log
   at this checkpoint; keep business rows and raw files outside the repository.

For updates, reuse a trustworthy prior full row supplied for this request or
available in an authorized local artifact, overlay only the requested changes,
and preserve unspecified values. Without a baseline, do not assume blanks mean
"unchanged"; resolve the missing values or documented update semantics first.
Do not retrieve Fusion state through an undeclared route.

### Deletion requests

Support exactly four deletion targets: entire sourcing rule, sourcing sources,
ATP rule, and ATP-rule assignment. Use the deletion section of
[CSV preparation](references/csv-preparation.md#deletion) for the flag mapping,
target identity, and full-baseline request format. A source deletion must not
be converted into a whole-rule deletion. AssignmentSets.csv deletion and sourcing
exclusion deletion remain unsupported; do not add related deletions implicitly.

When the user explicitly requests deletion of both a sourcing rule and its
source, allow both published deletion flags on the same SourcingRules.csv row.
Use the combined targets format in CSV preparation; keep the full baseline and
source identity checks. Also accept both flags in supplied CSV/ZIP rows without
rewriting them, and disclose both effects before Core approval. This is an
allowed combination of the existing targets, not a fifth target or an exception
for other flags. Leave combined-operation business validation and the actual
deletion outcome to Fusion's load job; do not infer cascade behavior or success.

Prompt deletions use the explicit delete operation, not create or update with
hidden delete flags. Supplied CSVs/ZIPs are also inspected for deletion flags
during the existing preparation pass, without rewriting their bytes. Review
the report's deletion entries against the exact rows and user intent; resolve
ambiguous targets before handoff. Preparation is not confirmation that the
target exists or has been deleted in Fusion.

## Immutable Core handoff

For a requested load, pass the exact ZIP path/name/bytes/SHA-256, member manifest,
row counts, template provenance, source-to-column mapping, selected source
system, collection type, and local validation evidence to `core.data-loader`.
The task remains `ORA_MSC_LOAD_PLANNING_DATA_FROM_FLAT_FILES`, with FBDI mode
and registered BO `Planning Common`; the FSM CSV flag remains N.

Core owns one live preflight, Task Hook evaluation, approval, upload, initiation,
and requested status/diagnostics. Task rules consume the same-run preparation
evidence; they do not rerun downloads, CSV generation, or ZIP filtering.
Core's routing result is not a claim that it validated every member's schema;
the pillar preparation evidence covers all selected CSVs.

Before execution approval, disclose retained/excluded files, source system,
the defaulted Net Change collection mode, and intended effect. For deletions,
include the deletion summary and exact target identities (rule, local/global
scope, source/effectivity or assignment level/keys) in Core's existing approval
preview, including flags discovered in supplied files. Do not interpret a generic
import approval as approval for undisclosed deletion or add a second approval
gate. Do not promise automatic cascade behavior or remove related assignments
without a separately supported, explicitly requested operation. Retain evidence
that the source system was supplied for this request, not inferred. Approval
binds to the final selected ZIP, never an original mixed ZIP. The collection-mode
notice is an FYI, not a question or a second pillar approval gate.

After approval, follow Core's envelope/integrity checks only. Do not refetch
templates, rerun task rules, regenerate files, or requery routing. A changed
artifact, target, or execution context requires fresh validation and approval.
Stop after accepted initiation; status is a separate user-requested Core action.
Never automatically resubmit a previously attempted or uncertain load.

## Boundaries and persistence

Use the parent functional-area skill for task sequencing. Preserve the nested
skill structure and project workflow. Read
[error handling](ora-resource/ora_error_handling.md) for blockers/recovery.
Persist redacted metadata only under the manifest workspace paths. Raw CSVs,
ZIPs, downloaded templates, and business values belong in a controlled transient
or user-approved location outside the repository/project.
