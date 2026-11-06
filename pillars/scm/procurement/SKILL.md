---
skill_id: "scm.procurement"
name: "Procurement"
description: "Coordinates SCM Procurement implementation guidance and routes work to developer-created functional-area skills."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
type: "orchestration"
execution_mode: "assisted"
owner_team: "SCM Procurement pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "scm_scope"
  - "procurement_requirements"
outputs:
  - "procurement_scope"
  - "functional_area_skill_plan"
  - "procurement_work_products"
  - "token_usage_record"
depends_on:
  - "shared.project-intake.scope-definition"
  - "shared.implementation-planning.offering-task-map-builder"
uses_core:
  - "core.project-mgmt.project-state-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.artifact-version-manager"
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
  - "scope"
  - "skill_path"
  - "setup_task_sequence"
  - "design_decisions"
  - "configuration_blueprints"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "scope"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "setup_task_sequence"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
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

# Procurement

## Purpose

Coordinates SCM Procurement implementation guidance across functional areas, setup tasks, and standard implementation activities.

## When to Use

Use this offering-level skill after Procurement is in scope and before routing to a specific functional-area skill.

## Catalog Identity

- Pillar: `SCM`
- Pillar slug: `scm`
- Offering code: `PO_PROCUREMENT`
- Offering slug: `procurement`
- Offering folder: `pillars/scm/procurement`
- Offering mapping source: `knowledge/setup-task-catalog/release/pillars-offerings-mapping.json`
- Setup task catalog source: `knowledge/setup-task-catalog/release/offering-functional-area-task-catalog.json`

## Routing Responsibility

This skill routes control to existing catalog-backed functional-area skills under this folder:

```text
pillars/scm/procurement/{functional-area-slug}/
```

When a requested functional-area skill is missing, identify the exact catalog match, record the missing capability in the selected project workspace, and stop that route with the next action to request a developer-authored skill. Do not generate skills or substitute a direct execution route during implementation.

## Inputs

- `implementation_objective`
- `project_context`
- `scm_scope`
- `procurement_requirements`

## Outputs

- `procurement_scope`
- `functional_area_skill_plan`
- `procurement_work_products`
- `token_usage_record`

## Functional Areas From Catalog

Source: `knowledge/setup-task-catalog/release/offering-functional-area-task-catalog.json`
Offering code: `PO_PROCUREMENT`
Functional area count: `25`
Setup task count: `462`

- `ORA_ASK_INITIAL_USER`: Initial Users
- `ORA_ASK_ENTERPRISE_PROFILE`: Enterprise Profile
- `ORA_ASK_LEGAL_STRUCTURES`: Legal Structures
- `ORA_ASK_FIN_REPORTING_STRUCT`: Financial Reporting Structures
- `ORA_ASK_ORGANIZATION_STRUCTURE`: Organization Structures
- `ORA_ASK_WORKFORCE_STRUCTURE`: Workforce Structures
- `ORA_ASK_USERS_AND_SECURITY`: Users and Security
- `ORA_PO_PURCHASING_CAT_FA`: Purchasing Categories
- `ORA_EGP_SUPPLIERS`: Suppliers
- `ORA_PO_APPROVAL_MANAGEMENT_FA`: Approval Management
- `ORA_PO_PROC_FOUNDATION_FA`: Procurement Foundation
- `ORA_EGP_FA_ITEMS`: Items
- `ORA_PO_PURCHASING_FOUNDATION`: Purchasing Foundation
- `ORA_PO_PRC_TRX_ACC_RULES_FA`: Procurement Transaction Account Rules
- `PO_SSP_DEPLOYED`: Self Service Procurement
- `ORA_EXTERNAL_PURCHASE_PRICES`: External Purchase Prices
- `WSH_ENABLE_RECEIVING`: Receiving
- `CMR_RECEIPT_ACCOUNTING`: Receipt Accounting
- `FIN_PAYABLES_DEPLOYED`: Payables
- `ORA_FIN_PAYMENTS`: Payments
- `ORA_CE_CASH_MGMT_BANK`: Cash Management
- `FIN_APPLICABILITY_ZX`: Transaction Tax
- `PO_SUP_PORTAL_DEPLOYED`: Supplier Portal
- `PO_SOURCING_DEPLOYED`: Sourcing
- `ORA_PO_QUALIFICATION_DEPLOYED`: Supplier Qualification

## Implementation Notes

- Keep offering-level planning, scope decisions, sequencing, and cross-functional-area handoffs in this skill.
- Put functional-area-specific implementation guidance in generated child skills under this offering folder.
- Use only existing catalog-backed child skills and their declared task-local guidance.
- Report missing skills or guidance to repository maintainers; authoring belongs to the development workflow.
- Route setup-task work to its existing functional-area or nested task skill; do not create skills during implementation.
