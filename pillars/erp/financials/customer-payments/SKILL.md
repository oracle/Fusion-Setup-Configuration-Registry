---
skill_id: "erp.financials.customer-payments"
name: "Customer Payments Implementation Guidance"
description: "Provides ERP Financials implementation guidance for the Customer Payments functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Customer Payments"
functional_area_code: "ORA_FIN_CUSTOMER_PAYMENTS"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "customer_payments_scope"
  - "customer_payments_requirements"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/customer-payments/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/customer-payments/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/customer-payments/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "AR_MANAGE_RECEIPT_SOURCES"
  - "IBY_MANAGE_FUNDS_CAPTURE_PROCESS_PROFILES"
  - "IBY_MANAGE_INTERNAL_PAYEES"
  - "AR_MANAGE_RECEIPT_CLASSES_AND_METHODS"
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

# Customer Payments Implementation Guidance

## Purpose

Provides ERP Financials implementation guidance for the Customer Payments functional area.

## When to Use

Use this functional-area skill after Financials scope is confirmed and the project needs customer payments setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `ERP`
- Offering: `Financials` (`XLE_FINANCIALS_JUR`)
- Functional area / Setup Object: `Customer Payments` (`ORA_FIN_CUSTOMER_PAYMENTS`)

## Setup Tasks

1. [Manage Receipt Sources](manage-receipt-sources/SKILL.md) (`AR_MANAGE_RECEIPT_SOURCES`)
2. [Manage Funds Capture Process Profiles](manage-funds-capture-process-profiles/SKILL.md) (`IBY_MANAGE_FUNDS_CAPTURE_PROCESS_PROFILES`)
3. [Manage Internal Payees](manage-internal-payees/SKILL.md) (`IBY_MANAGE_INTERNAL_PAYEES`)
4. [Manage Receipt Classes and Methods](manage-receipt-classes-and-methods/SKILL.md) (`AR_MANAGE_RECEIPT_CLASSES_AND_METHODS`)

## Inputs

- `implementation_objective`
- `project_context`
- `customer_payments_scope`
- `customer_payments_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated nested setup-task skills for task-level planning, sequencing, setup-data routing, and validation. Track token usage for any generated project artifact or skill-run record using the manifest policy.
