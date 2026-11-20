---
skill_id: "erp.financials.payables"
name: "Payables Implementation Guidance"
description: "Provides ERP Financials implementation guidance for the Payables functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payables"
functional_area_code: "FIN_PAYABLES_DEPLOYED"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "payables_scope"
  - "payables_requirements"
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
  - "core.data-loader"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payables/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "AP_MANAGE_COMMON_OPTIONS_FOR_PAYABLES_AND_PROCUREMENT"
  - "ORA_AP_MANAGE_BANK_CHARGES"
  - "AP_MANAGE_PAYMENT_TERMS"
  - "AP_MANAGE_INVOICE_OPTIONS"
  - "AP_MANAGE_PAYMENT_OPTIONS"
  - "AP_MANAGE_PAYABLES_CALENDARS"
  - "AP_MANAGE_INVOICE_TOLERANCES"
  - "AP_MANAGE_INTEREST_RATES"
  - "ORA_MANAGE_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS"
  - "AP_MANAGE_AGING_PERIODS"
  - "AP_MANAGE_DISTRIBUTION_SETS"
  - "AP_MANAGE_REPORTING_ENTITIES"
  - "AP_MANAGE_INVOICE_HOLDS_AND_RELEASES"
  - "ORA_AP_MANAGE_PAYMENT_PROCESS_REQUEST_TEMPLATE"
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

# Payables Implementation Guidance

## Purpose

Helps teams plan and validate Payables setup in ERP Financials.

## When to Use

Use this skill after confirming the Financials scope. It helps with Payables
setup planning, baseline exports, import order, and validation checks.

## Catalog Metadata

- Pillar: `ERP`
- Offering: `Financials` (`XLE_FINANCIALS_JUR`)
- Functional area / Setup Object: `Payables` (`FIN_PAYABLES_DEPLOYED`)

## Setup Tasks

1. [Manage Common Options for Payables and Procurement](manage-common-options-for-payables-and-procurement/SKILL.md) (`AP_MANAGE_COMMON_OPTIONS_FOR_PAYABLES_AND_PROCUREMENT`)
2. [Manage Bank Charges](manage-bank-charges/SKILL.md) (`ORA_AP_MANAGE_BANK_CHARGES`)
3. [Manage Payment Terms](manage-payment-terms/SKILL.md) (`AP_MANAGE_PAYMENT_TERMS`)
4. [Manage Invoice Options](manage-invoice-options/SKILL.md) (`AP_MANAGE_INVOICE_OPTIONS`)
5. [Manage Payment Options](manage-payment-options/SKILL.md) (`AP_MANAGE_PAYMENT_OPTIONS`)
6. [Manage Payables Calendars](manage-payables-calendars/SKILL.md) (`AP_MANAGE_PAYABLES_CALENDARS`)
7. [Manage Invoice Tolerances](manage-invoice-tolerances/SKILL.md) (`AP_MANAGE_INVOICE_TOLERANCES`)
8. [Manage Interest Rates](manage-interest-rates/SKILL.md) (`AP_MANAGE_INTEREST_RATES`)
9. [Manage Intelligent Document Recognition Options](manage-intelligent-document-recognition-options/SKILL.md) (`ORA_MANAGE_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS`)
10. [Manage Aging Periods](manage-aging-periods/SKILL.md) (`AP_MANAGE_AGING_PERIODS`)
11. [Manage Distribution Sets](manage-distribution-sets/SKILL.md) (`AP_MANAGE_DISTRIBUTION_SETS`)
12. [Manage Reporting Entities](manage-reporting-entities/SKILL.md) (`AP_MANAGE_REPORTING_ENTITIES`)
13. [Manage Invoice Holds and Releases](manage-invoice-holds-and-releases/SKILL.md) (`AP_MANAGE_INVOICE_HOLDS_AND_RELEASES`)
14. [Create Payment Process Request Templates](create-payment-process-request-templates/SKILL.md) (`ORA_AP_MANAGE_PAYMENT_PROCESS_REQUEST_TEMPLATE`)

## Inputs

- `implementation_objective`
- `project_context`
- `payables_scope`
- `payables_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the task skills below for task-level planning, sequencing, data routing, and
validation. For each generated project artifact or skill run, record token use
as required by the manifest.
