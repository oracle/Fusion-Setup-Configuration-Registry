---
skill_id: "erp.financials.payables.manage-invoice-holds-and-releases"
name: "Manage Invoice Holds and Releases Setup Task Guidance"
description: "Plans, builds, validates and reconciles create and update packages for Manage Invoice Holds and Releases under Payables."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payables"
functional_area_code: "FIN_PAYABLES_DEPLOYED"
task_code: "AP_MANAGE_INVOICE_HOLDS_AND_RELEASES"
task_name: "Manage Invoice Holds and Releases"
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
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "configuration_blueprint"
  - "offline_task_package"
  - "comparison_only_report"
  - "scoped_recovery_plan"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
  - "core.data-loader.task-hook"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-invoice-holds-and-releases/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/manage-invoice-holds-and-releases/current/"
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
  - "Writes local setup blueprints, previews, candidate ZIPs, validation reports and recovery artifacts under the selected project workspace."
  - "Delegates approved Fusion imports to core.data-loader and Task Hook; the task adapter makes no network calls."
required_privileges: []
---

# Manage Invoice Holds and Releases Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Invoice Holds and Releases` under `Payables`.

## Setup Task Skill Contract

- task_code: `AP_MANAGE_INVOICE_HOLDS_AND_RELEASES`
- task_name: `Manage Invoice Holds and Releases`
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

## Task-specific readiness and resource contract

<!-- fscr-supported-operations: create, update -->
<!-- fscr-update-fields: AP_HOLD_CODE::UserUpdateableFlag, AP_HOLD_CODE::ExternalDescription, AP_HOLD_CODE::HoldInstruction, AP_HOLD_CODE::WaitBeforeNotifyDays, AP_HOLD_CODE::ReminderDays, AP_HOLD_CODE::InitiateWorkflowFlag, AP_HOLD_CODE::UserReleaseableFlag, AP_HOLD_CODE::InactiveDate, AP_HOLD_CODE::PostableFlag, AP_HOLD_CODE::DspDescription -->

The task-owned profile holds-definition-create-and-updates-v4 normalizes, builds,
validates and reconciles create and supported update packages. It defines setup
hold/release codes; transactional invoice hold application or release belongs to
another workflow. The single package entity is AP_HOLD_CODE at
/ApprovalCodeVO/ApprovalCodeVORow, matched by exact HoldLookupCode. Supporting
lookups and accounting consumers are not additional task entities.

Allow Accounting accepts Yes or No, serialized as PostableFlag Y or N. Do not
offer code X as a user option; preserve it only as an unchanged exported value
when the request omits that field, under Input Validation.

The adapter runs offline. The declared workflow owns fresh identity checks,
Data Loader approval and execution. Status checks and reconciliation are requested
follow-up or conditional failure, uncertain-outcome and recovery steps. A valid
preview does not authorize an import or establish saved values.

### Rule ownership and read order

Load the resources in this order; each owns the detailed rules named below.

1. [Input validation](ora-resource/ora_input_validation.md): required fields,
   accepted values, optional clears, date handling and full-row CSV validation.
2. [Design enforcement](ora-resource/ora_design_enforcement.md): operation scope,
   existing-row update restrictions, pre-import field combinations and import processing.
3. [Dependency readiness](ora-resource/ora_dependency_readiness.md): task/package
   prerequisites, importer semantics and declared workflow readiness.
4. [Reference lookups](ora-resource/ora_reference_lookups.md): exact identity,
   type label/code mapping and embedded lookup behavior.
5. [Defaulting rules](ora-resource/ora_defaulting_rules.md): create defaults and
   explicit-input precedence.
6. [Error handling](ora-resource/ora_error_handling.md): diagnostics, handoff
   disclosures, process results, optional reconciliation and recovery.

### Preparation and handoff

1. For updates, follow the check order under Design Enforcement's
   [Update Restrictions](ora-resource/ora_design_enforcement.md#update-restrictions)
   before suggesting corrected values. Use the task adapter and catalog to
   validate the selected operation and prepare only the requested rows.
   Keep original inputs, applied defaults,
   sourceDrivenEffects and accountingEffects distinct
   in provenance. Show supporting lookup maintenance notices separately from
   requested text changes, including when a full-row update preserves description.
2. Validate the candidate package before handoff through the CSV workflow below.
   Enforce the design-owned pre-import consistency rules. Reject conflicting
   supplied values; derive only omitted dependent values. Lookup/accounting
   processing requires disclosure, not proof of setter order or saved state.
3. For an execution request, complete Data Loader preflight for the final ZIP,
   then use the [Task Hook](../../../../../core/data-loader/task-hook/SKILL.md)
   at handoff to resolve the compiled registry. Read its returned execution guide
   and source rules, require a current ready plan, and evaluate applicable nodes
   in prerequisite and transition order. Report missing evidence at the affected
   node; do not override readiness. Preparation-only requests stop before handoff.
4. Follow core.data-loader through accepted initiation and report its response.
   Do not automatically poll, export or reconcile afterward. Use the selected
   follow-up workflow when requested or required for a failed, uncertain or
   recovery operation; apply ora_error_handling.md to those outcomes.

Create and update have separate contracts. This adapter does not support
overriding a failed field-validation rule through implementor acceptance.
Apply its declared validation and preservation controls before handoff. The
runtime, catalog, tests and hash-bound campaign determine technical readiness;
report create and update readiness separately.

Financials / Payables is the selected authoring context. Other catalog placements
under Student Management and Procurement do not authorize cross-offering writes.
The owner_team field identifies the repository maintenance owner. Required
product reviewers are the Payables Pillar Lead or SME and an FSCR core reviewer.

### Maintenance

scripts/fsm_task_adapter.py and e2e-adapter.json are the tracked task
implementation. The developer [test catalog](../noship/tests/manage-invoice-holds-and-releases/e2e-test-catalog.json)
and regression tests reside in the Payables noship test bundle. The local
scripts/fsm_package_runtime.py is a thin
bridge to the task-owned package primitives.
Package [the local primitives script](scripts/fsm_package_primitives.py) with this
task. It owns package parsing, structural validation, candidate assembly,
comparison, safe publication and CLI diagnostics. This task extends its isolated
namespace with field validation,
date serialization, lookup/accounting disclosures and recovery rules. These local
calls do not load environment configuration, authenticate, upload or initiate a load.
Core Data Loader and Task Hook retain live execution and approval ownership.
Preserve these boundaries during regeneration.

Use `python3 scripts/fsm_task_adapter.py --help` from this task folder for the
task CLI. It binds e2e-adapter.json and applies the Holds business rules; other
contract paths are rejected. The lower-level primitives CLI requires an explicit
--contract and does not replace the task adapter's validation. Package the
complete task-owned scripts and follow
[package prerequisites](ora-resource/ora_dependency_readiness.md#package-and-runtime-prerequisites).

After changing the adapter, wrapper or primitives, run
`python3 -m unittest discover -s ../noship/tests/manage-invoice-holds-and-releases/tests`
from this task folder. The noship bundle is developer-only and is not required
by the runtime. CLI outputs must use new, distinct paths
inside --workspace (the current directory by default); reports cannot overwrite
inputs or existing artifacts.
Candidate ZIPs are published only after independent validation. Reconciliation
returns COMPARISON_ONLY for matching values, with persistenceVerified=false;
the selected workflow establishes the export's acquisition and freshness.
Full-row Holds imports perform supporting lookup maintenance even when visible
values match, so scalar equality alone does not suppress an explicitly requested
candidate.
Compile ora-resource/ora_rule_registry.json after changing canonical rule tables.

Use the [contract guide](references/contract-guide.md) to resolve local rule
identifiers in the descriptor and emitted receipts. These identifiers select
the applicable task rules; they do not certify execution outcome or saved values.

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Financials`
- Functional area / Setup Object: `Payables`
- Setup task name: `Manage Invoice Holds and Releases`
- Setup task code: `AP_MANAGE_INVOICE_HOLDS_AND_RELEASES`
## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `configuration_blueprint`
- `offline_task_package`
- `comparison_only_report`
- `scoped_recovery_plan`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `erp.financials.payables` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

Reuse the selected project's existing requirements, decisions and artifacts before
requesting the same information again. Keep exports under project/{project_id}/exports
and generated designs, candidates and reports under the declared task artifact path.
Register durable artifacts through core.project-mgmt.artifact-registry-manager
using the project artifact contract. Use core.project-mgmt.project-state-manager
to update only the declared affected state and record each run, including failed
or partial outcomes with diagnostics. Use core.project-mgmt.artifact-version-manager
for new major versions; obtain confirmation before a minor replacement. The local
CLI requires fresh output paths and does not register artifacts or overwrite an
existing version on the caller's behalf. The selected workflow owns those steps.
