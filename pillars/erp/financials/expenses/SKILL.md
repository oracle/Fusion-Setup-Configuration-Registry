---
skill_id: "erp.financials.expenses"
name: "Expenses Implementation Guidance"
description: "Provides ERP Financials implementation guidance for the Expenses functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Expenses"
functional_area_code: "FIN_EXPENSES_DEPLOYED"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.1.3"
inputs:
  - "implementation_objective"
  - "project_context"
  - "expenses_scope"
  - "expenses_requirements"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/expenses/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/expenses/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/expenses/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "EXM_MANAGE_CONVERSION_RATES_AND_POLICIES"
  - "EXM_MANAGE_EXPENSE_FIELDS_BY_CATEGORY"
  - "EXM_MANAGE_EXPENSE_REPORT_TEMPLATES"
  - "EXM_MANAGE_EXPENSES_SYSTEM_OPTIONS"
  - "EXM_MANAGE_TAX_FIELDS"
  - "ORA_EXM_MANAGE_AUTO_SUBMISSION_AND_MATCHING_OPTIONS"
  - "ORA_EXM_MANAGE_POLICIES_BY_EXPENSE_CATEGORY"
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

# Expenses Implementation Guidance

## Purpose

Provides ERP Financials implementation guidance for the Expenses functional area.

## When to Use

Use this functional-area skill after Financials scope is confirmed and the project needs expenses setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `ERP`
- Offering: `Financials` (`XLE_FINANCIALS_JUR`)
- Functional area / Setup Object: `Expenses` (`FIN_EXPENSES_DEPLOYED`)

## Setup Tasks

1. [Manage Expense Fields by Category](manage-expense-fields-by-category/SKILL.md) (`EXM_MANAGE_EXPENSE_FIELDS_BY_CATEGORY`)
2. [Manage Expense Report Templates](manage-expense-report-templates/SKILL.md) (`EXM_MANAGE_EXPENSE_REPORT_TEMPLATES`)
3. [Manage Expenses System Options](manage-expenses-system-options/SKILL.md) (`EXM_MANAGE_EXPENSES_SYSTEM_OPTIONS`)
4. [Manage Tax Fields](manage-tax-fields/SKILL.md) (`EXM_MANAGE_TAX_FIELDS`)
5. [Manage Auto Submission and Matching Options](manage-auto-submission-and-matching-options/SKILL.md) (`ORA_EXM_MANAGE_AUTO_SUBMISSION_AND_MATCHING_OPTIONS`)
6. [Manage Conversion Rates and Policies](manage-conversion-rates-and-policies/SKILL.md) (`EXM_MANAGE_CONVERSION_RATES_AND_POLICIES`)
7. [Manage Policies by Expense Category](manage-policies-by-expense-category/SKILL.md) (`ORA_EXM_MANAGE_POLICIES_BY_EXPENSE_CATEGORY`)

For Report Templates, System Options, and Conversion Rates and Policies, use each linked skill's task-local
input workbook and setup contract.

## Inputs

- `implementation_objective`
- `project_context`
- `expenses_scope`
- `expenses_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated nested setup-task skills for task-level planning, sequencing, setup-data routing, and validation. Track token usage for any generated project artifact or skill-run record using the manifest policy.
