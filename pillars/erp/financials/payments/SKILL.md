---
skill_id: "erp.financials.payments"
name: "Payments Implementation Guidance"
description: "Provides ERP Financials implementation guidance for the Payments functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payments"
functional_area_code: "ORA_FIN_PAYMENTS"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "payments_scope"
  - "payments_requirements"
outputs:
  - "functional_area_setup_plan"
  - "configuration_guidance"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payments/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payments/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payments/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "IBY_MANAGE_FORMATS"
  - "IBY_MANAGE_PAYMENT_SYSTEMS"
  - "IBY_MANAGE_PAYMENT_CODES"
  - "IBY_MANAGE_DISBURSEMENT_SYSTEM_OPTIONS"
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

# Payments Implementation Guidance

## Purpose

Apply [the core Data Loader execution contract](../../../../core/data-loader/SKILL.md)
to tasks with a supported FSM route. Route setup creates and changes through
`core.data-loader`; UI inspection remains read-only. Missing prerequisites block
execution, and Data Loader's approval workflow must not be duplicated.

Provides ERP Financials implementation guidance for the Payments functional area.

## When to Use

Use this functional-area skill after Financials scope is confirmed and the project needs payments setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `ERP`
- Offering: `Financials` (`XLE_FINANCIALS_JUR`)
- Functional area / Setup Object: `Payments` (`ORA_FIN_PAYMENTS`)

## Setup Tasks

1. [Manage Formats](manage-formats/SKILL.md) (`IBY_MANAGE_FORMATS`)
2. [Manage Payment Systems](manage-payment-systems/SKILL.md) (`IBY_MANAGE_PAYMENT_SYSTEMS`)
3. [Manage Payment Codes](manage-payment-codes/SKILL.md) (`IBY_MANAGE_PAYMENT_CODES`)
4. [Manage Disbursement System Options](manage-disbursement-system-options/SKILL.md) (`IBY_MANAGE_DISBURSEMENT_SYSTEM_OPTIONS`)

## Inputs

- `implementation_objective`
- `project_context`
- `payments_scope`
- `payments_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated nested setup-task skills for task-level planning, sequencing, setup-data routing, and validation. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Task Selection

Resolve the exact requested FSM task through the effective catalog and the
project-objective classifier before choosing a nested task workflow. The authored
child-skill list above is an implementation inventory, not a complete Payments task
catalog or a default task selection. For a vague request such as "configure Payments
setup using standard values", ask which exact setup task is intended; keep task
selection pending until the user resolves that scope. Resolve offering ambiguity
under the classifier's existing offering-scope rules as well.

When several tasks are explicitly requested, retain their separate identities and
route each through its owning guidance. An MPS package contains only the exact MPS
task; missing guidance for another task is a separate readiness gap.
