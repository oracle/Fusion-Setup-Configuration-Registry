---
skill_id: "erp.financials.budgetary-control-and-encumbrance-accounting.manage-budgetary-control"
name: "manage-budgetary-control-setup-task-guidance"
description: "Use when the implementation router selects ORA_XCC_ENABLE_BUDGETARY_CONTROL, or for explicitly requested advisory guidance about that exact task; plans, sequences, exports, validates, imports, and verifies Manage Budgetary Control setup."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Budgetary Control and Encumbrance Accounting"
functional_area_code: "ORA_XCC_PUBLICSECTOR"
task_code: "ORA_XCC_ENABLE_BUDGETARY_CONTROL"
task_name: "Manage Budgetary Control"
parent_skill_id: "erp.financials.budgetary-control-and-encumbrance-accounting"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/budgetary-control-and-encumbrance-accounting/manage-budgetary-control/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/budgetary-control-and-encumbrance-accounting/manage-budgetary-control/current/"
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
  - "Writes versioned configuration-blueprint, validation, skill-run, and token-usage artifacts in the selected project through the declared project services."
  - "Delegates requested same-task exports and approved immutable FSM imports to the declared shared and core workflows. Planning alone performs no Fusion mutation."
required_privileges:
  - "Write access to the selected project workspace."
  - "Fusion read/export or setup privileges only when the selected shared export or Core Data Loader workflow requires them."
---

# Manage Budgetary Control Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Budgetary Control` under `Budgetary Control and Encumbrance Accounting`.

## Setup Task Skill Contract

- task_code: `ORA_XCC_ENABLE_BUDGETARY_CONTROL`
- task_name: `Manage Budgetary Control`
- parent_skill_id: `erp.financials.budgetary-control-and-encumbrance-accounting`
- pillar: `ERP`
- offering: `Financials`
- functional_area: `Budgetary Control and Encumbrance Accounting`
- functional_area_code: `ORA_XCC_PUBLICSECTOR`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Budgetary Control` under `Budgetary Control and Encumbrance Accounting`.

## Setup Task Metadata

- Task name: `Manage Budgetary Control`
- Task code: `ORA_XCC_ENABLE_BUDGETARY_CONTROL`
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
- Functional area / Setup Object: `Budgetary Control and Encumbrance Accounting`
- Setup task name: `Manage Budgetary Control`
- Setup task code: `ORA_XCC_ENABLE_BUDGETARY_CONTROL`

### Preconditions and task-rule handoff

Require a confirmed implementation objective, exact task scope, and selected
`project_context` before producing durable output. If no project is selected,
return an input-validation blocker and route project selection or creation
through the canonical implementation workflow; do not guess or silently reuse a
different project.

For setup-data preparation or validation, require a current same-task export
for `ORA_XCC_ENABLE_BUDGETARY_CONTROL` and resolve the ordered rule plan from
[`ora-resource/ora_rule_registry.json`](ora-resource/ora_rule_registry.json).
Require the registry readiness status to be `ready`, start at its declared
`start_node`, and load every complete source file selected by that plan. Registry
anchors and line numbers identify the generated `Task Nodes` rows; they are
navigation metadata, not permission to omit the substantive rules elsewhere in
the selected source file.
Stop when a required node, source, transition, template member, identity, or
current-state value is missing or ambiguous.

For a mutation candidate, immutable preview, import, or post-import verification,
`current` means a fresh populated same-task export created after the latest known
setup mutation. A cached export may support a read-only answer only when its
process ID and timestamp are recorded and there is affirmative evidence that no
setup mutation occurred afterward. Elapsed time alone never proves currency; if
the mutation boundary is unknown, obtain a fresh export.

`core.data-loader` owns the live task-hook evaluation, immutable preview,
approval receipt, archive creation, submission, polling, and process
diagnostics. Pass the exact task code and selected skill context so its task
hook evaluates this package's registry. Do not parse around a task-hook blocker,
substitute direct REST or browser execution, or treat planning as authorization
for an export or import. Task rules return an `approval_required` gate with the
exact target, immutable package, fingerprint, warnings, and intended operation;
only `core.data-loader` presents that gate and records the approval receipt. Do
not ask for a second approval in this skill.

### Planning, execution routing, and acceptance

1. Build `setup_task_plan` from the requested scope, current same-task evidence,
   unresolved decisions, dependency status, applicable rule nodes, blockers,
   and safe next action. Keep planning, export, preparation, import, and
   verification as distinct stages.
2. Route a requested baseline or template export to
   `shared.setup-export.task-level-export` with the exact task name and code.
   Store the resulting export only under the selected project's `exports/`
   directory and retain its process and artifact references.
3. Route generic package-shape validation to
   `shared.validation.setup-data-validator` and reference-data validation to
   `shared.validation.reference-data-validator`. Preserve this package's
   task-rule results separately; generic validation does not replace the
   registry plan.
4. Route only the exact validated candidate to `core.data-loader` in FSM mode.
   Its own approval workflow is authoritative: present the immutable preview
   and do not request a second approval for the same import. Any input, target,
   current-state evidence, rule result, or candidate-package change invalidates
   that preview and approval.
5. After a terminal successful import, obtain a fresh same-task export through
   the declared export route and compare every requested value, required parent
   and child identity, coordinated representation, and preserved unrelated
   value. A successful process status without this read-back is incomplete, not
   a passed validation checkpoint.

### Execution checklist

- [ ] Confirm the implementation objective, selected project, exact task scope,
  and target identity.
- [ ] Obtain or qualify the same-task export using the mutation-boundary rule
  above; require a fresh export for every mutation package.
- [ ] Resolve the ready registry plan and load every complete selected rule file.
- [ ] Validate identity, dependencies, references, generic package shape, task
  rules, preservation, and archive encoding.
- [ ] Bind the exact target, changes, warnings, package fingerprint, and approval
  state into one immutable preview.
- [ ] Hand the preview to `core.data-loader`; let it collect the single
  authoritative approval and submit at most once.
- [ ] Monitor that exact process and preserve terminal diagnostics.
- [ ] After success, obtain a fresh populated same-task export and verify every
  requested, coordinated, and preserved value before reporting completion.

Accept a planning result only when its scope, dependencies, selected rules,
decisions, routes, evidence references, blockers, and next action are explicit.
Accept an execution result only when the approved package, terminal process
result, and fresh read-back agree with the requested configuration and the
applicable `ora-resource` rules.

### Outputs, evidence, and persistence

- `setup_task_plan` records the task identity, requested scope, dependency and
  rule-plan status, source evidence, decisions, blockers, and next action.
- `setup_data_routing` records the selected export, validation, import, or
  read-back route with target environment identity when applicable and the
  immutable artifact or external process references returned by that route.
- `validation_checkpoints` records each applicable registry node and generic
  validation with status, evidence reference, unresolved item, and correction.

Persist the blueprint and validation result at the manifest locations through
the artifact version and registry services, then update only the declared
project-state fields. Create a new version for a major revision and obtain
confirmation before replacing a current minor revision. Record every durable
attempt, including blocked, failed, timed-out, and partial work, under
`state/runs/`; append the token-usage record required by the manifest. Never
store credentials, token contents, private keys, or sensitive payloads in these
artifacts.

### Failure and recovery

Classify missing scope, project, or evidence as `input_validation`; unresolved
task identity or rule metadata as `catalog_or_metadata_mismatch`; authentication
and privilege failures through the delegated workflow; connectivity failures as
`transport_or_environment`; Fusion errors as `fusion_api_error`; polling expiry
as `process_timeout`; terminal job failure as `process_failed`; persistence
failure as `artifact_persistence`; and a missing required approval as
`approval_blocker`.

Preserve sanitized diagnostics, artifact references, and external identifiers
returned by the selected route. Retry only a declared recoverable read or the
single cached-token refresh permitted by that workflow. Never automatically
retry or resubmit an import, an uncertain write, or a failed live process.
Corrections require fresh evidence, full revalidation, a new immutable preview,
and the Core Data Loader workflow's approval.




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

Use the parent functional-area skill `erp.financials.budgetary-control-and-encumbrance-accounting` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Validation and examples

Example: for a request to enable Requisitioning Budgetary Control for one
business unit, first resolve its exact ledger and current parent state from the
qualified same-task export. Build the required parent and dependent
business-function rows in registry order, preserve unrelated setup, validate
the immutable package, and return its `approval_required` gate to
`core.data-loader`. After its one approved submission succeeds, verify the
requested and preserved values from a new populated same-task export.

- Use [`noship/tests/junit/README.md`](noship/tests/junit/README.md) for the
  offline CE-01, CE-02, and CE-03 contract suite.
- Use [`noship/tests/python/README.md`](noship/tests/python/README.md) for the
  portable package and read-back validators.
- Use [`noship/tests/e2e/controller/README.md`](noship/tests/e2e/controller/README.md)
  for the isolated live E2E controller and its no-retry execution boundary.
- Use [`tests/prompts/manage-budgetary-control-routing.json`](tests/prompts/manage-budgetary-control-routing.json)
  for positive, negative, and ambiguous routing cases.
