---
skill_id: "erp.financials.budgetary-control-and-encumbrance-accounting"
name: "Budgetary Control and Encumbrance Accounting Implementation Guidance"
description: "Provides ERP Financials implementation guidance for the Budgetary Control and Encumbrance Accounting functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Budgetary Control and Encumbrance Accounting"
functional_area_code: "ORA_XCC_PUBLICSECTOR"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "budgetary_control_and_encumbrance_accounting_scope"
  - "budgetary_control_and_encumbrance_accounting_requirements"
outputs:
  - "functional_area_setup_plan"
  - "configuration_guidance"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "erp.financials.budgetary-control-and-encumbrance-accounting.manage-budgetary-control"
  - "erp.financials.budgetary-control-and-encumbrance-accounting.manage-control-budgets"
  - "shared.implementation-planning.offering-task-map-builder"
  - "shared.implementation-planning.task-dependency-resolver"
  - "shared.setup-export.functional-area-export"
uses_core:
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
  - "core.diagnostics.role-access-check"
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
  - "design_decisions"
  - "configuration_blueprints"
  - "validation_results"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "setup_task_sequence"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/budgetary-control-and-encumbrance-accounting/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/budgetary-control-and-encumbrance-accounting/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/budgetary-control-and-encumbrance-accounting/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_XCC_ENABLE_BUDGETARY_CONTROL"
  - "ORA_XCC_MANAGE_CONTROL_BUDGETS"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "Writes versioned planning, blueprint, decision, validation, run and token-usage artifacts in the selected project through the declared project services."
  - "Delegates requested baseline exports to shared.setup-export.functional-area-export; delegates task work to the nested skill, whose Core Data Loader approval workflow owns any import. Planning alone performs no Fusion mutation."
required_privileges:
  - "Access to the selected project workspace; Fusion read/export or setup privileges only when the routed export or task workflow requires them."
---

# Budgetary Control and Encumbrance Accounting Implementation Guidance

## Purpose

Provides ERP Financials implementation guidance for the Budgetary Control and Encumbrance Accounting functional area.

## When to Use

Use this functional-area skill after Financials scope is confirmed and the project needs budgetary control and encumbrance accounting setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `ERP`
- Offering: `Financials` (`XLE_FINANCIALS_JUR`)
- Functional area / Setup Object: `Budgetary Control and Encumbrance Accounting` (`ORA_XCC_PUBLICSECTOR`)

## Setup Tasks

1. [Manage Budgetary Control](manage-budgetary-control/SKILL.md) (`ORA_XCC_ENABLE_BUDGETARY_CONTROL`)
2. [Manage Control Budgets](manage-control-budgets/SKILL.md) (`ORA_XCC_MANAGE_CONTROL_BUDGETS`)

## Inputs

- `implementation_objective`
- `project_context`
- `budgetary_control_and_encumbrance_accounting_scope`
- `budgetary_control_and_encumbrance_accounting_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated nested setup-task skills for task-level planning, sequencing, setup-data routing, and validation. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Local Planning Workflow

### Preconditions and dependency readiness

- Require a confirmed Financials objective, this functional area's scope and requirements, and a selected project in `project_context`. If the project is absent, use the repository project-initialization workflow before persisting output; do not guess a project or silently reuse another target.
- Resolve `ORA_XCC_PUBLICSECTOR`, `ORA_XCC_ENABLE_BUDGETARY_CONTROL`, and `ORA_XCC_MANAGE_CONTROL_BUDGETS` against the effective setup-task catalog through the declared task-map and dependency-resolver skills. Record required upstream setup and its evidence as satisfied, pending or blocked; this skill does not configure those upstream objects or own the overall implementation program.
- Confirm the declared nested skill and project services are available. For requested external work, require the selected workflow's environment identity, role/access checks and approval gates before delegation. A planning request does not authorize an export, login or import.

### Planning, routing and acceptance

1. Map each in-scope requirement to the catalog-backed task, its inputs, dependencies and validation checkpoint. Record unresolved decisions explicitly rather than inventing setup values.
2. Produce `functional_area_setup_plan` with task identity, scope, dependency status/evidence, required inputs, selected route, blockers and next action. Produce `configuration_guidance` from the nested skill and its task resources, not a competing copy of their rules.
3. Route requested Manage Control Budgets work to [the nested skill](manage-control-budgets/SKILL.md). It owns the Control Budget gate, independent Supplemental, Revenue, and Override rule checks, template/CSV preparation, shared validation and Core Data Loader handoff. Planning, baseline export, preparation and live execution remain distinct operations.
4. When the active workflow explicitly requests a functional-area baseline export, delegate to `shared.setup-export.functional-area-export` and retain its target, task scope, status and export references under the project's `exports/`. Do not substitute a baseline data export for the nested task's template export.
5. Build `validation_checkpoints` with each applicable check's status, evidence reference, unresolved item and correction. Accept the local plan only when task scope, dependencies, decisions and routing are traceable; unresolved execution prerequisites may yield a useful blocked plan, never an execution-ready result. Never represent a deferred Fusion check as a pre-import pass.

### Postconditions, evidence and persistence

Persist the plan, guidance/blueprint and validation checkpoints as structured project artifacts at the manifest locations. Include task/skill identity, source requirements, target when applicable, dependency evidence, decisions, blockers, status and safe next action. Use the declared version/registry/state services to register artifact references and update only the manifest's affected state fields. Create new versions for major revisions; obtain confirmation before replacing an existing minor revision.

Record `skill_run_record` under `state/runs/` and append `token_usage_record` using the manifest policy, including failed or partially completed durable runs. Postconditions are the registered artifacts and run references, consistent checkpoints and an explicit planning or delegated-execution status; producing a plan does not prove that Fusion configuration was changed. Preserve the nested workflow's import and verification evidence separately when that workflow is selected.

### Failure and recovery

Classify missing inputs as input validation, catalog/dependency gaps as catalog or metadata mismatch, and project writes as artifact persistence failures. Delegate auth/authz, transport, Fusion API, process-failure/timeout and approval diagnostics to the selected core/shared workflow; retain sanitized status, stage, task, target, artifact/external identifiers and one safe next action. On an unresolved dependency, preserve the blocked plan and stop before the dependent external step. Do not bypass a missing route with direct REST, browser or loader calls.

Do not retry a live import or uncertain write automatically. Corrections require revalidation and the existing workflow's fresh approval; polling timeouts retain the process identifier and last status without resubmission. Report partial persistence honestly and resume through the project services rather than silently overwriting artifacts. Never store credentials, tokens, private keys or sensitive payloads in plans, diagnostics or logs.
