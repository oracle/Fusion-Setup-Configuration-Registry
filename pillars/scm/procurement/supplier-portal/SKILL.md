---
skill_id: "scm.procurement.supplier-portal"
name: "Supplier Portal Implementation Guidance"
description: "Provides SCM Procurement implementation guidance for the Supplier Portal functional area."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "Supplier Portal"
functional_area_code: "PO_SUP_PORTAL_DEPLOYED"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM procurement pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "supplier_portal_scope"
  - "supplier_portal_requirements"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/supplier-portal/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/supplier-portal/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/supplier-portal/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "POZ_MANAGE_SUPPLIER_USER_ROLES"
  - "POZ_SPECIFY_SUPPLIER_NEWS_CONTENT"
  - "ORA_POZ_CONFIGURE_SUPPLIER_NOTIFICATIONS_FOR_PROFILE_MGMT"
  - "POZ_MANAGE_SUPPLIER_USER_ROLE_USAGES"
  - "ORA_POZ_MANAGE_SUPPLIER_PORTAL_MESSAGES"
  - "ORA_POZ_MANAGE_SUPPLIER_REGISTRATION_APPROVALS"
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

# Supplier Portal Implementation Guidance

## Purpose

Provides SCM Procurement implementation guidance for the Supplier Portal functional area.

## When to Use

Use this functional-area skill after Procurement scope is confirmed and the project needs supplier portal setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `SCM`
- Offering: `Procurement` (`PO_PROCUREMENT`)
- Functional area / Setup Object: `Supplier Portal` (`PO_SUP_PORTAL_DEPLOYED`)

## Setup Tasks

1. [Manage Supplier User Roles](manage-supplier-user-roles/SKILL.md) (`POZ_MANAGE_SUPPLIER_USER_ROLES`)
2. [Specify Supplier News Content](specify-supplier-news-content/SKILL.md) (`POZ_SPECIFY_SUPPLIER_NEWS_CONTENT`)
3. [Configure Supplier Notifications](configure-supplier-notifications/SKILL.md) (`ORA_POZ_CONFIGURE_SUPPLIER_NOTIFICATIONS_FOR_PROFILE_MGMT`)
4. [Manage Supplier User Role Usages](manage-supplier-user-role-usages/SKILL.md) (`POZ_MANAGE_SUPPLIER_USER_ROLE_USAGES`)
5. [Manage Supplier Portal Messages](manage-supplier-portal-messages/SKILL.md) (`ORA_POZ_MANAGE_SUPPLIER_PORTAL_MESSAGES`)
6. [Manage Supplier Registration Approvals](../approval-management/manage-supplier-registration-approvals.md) (`ORA_POZ_MANAGE_SUPPLIER_REGISTRATION_APPROVALS`)

## Inputs

- `implementation_objective`
- `project_context`
- `supplier_portal_scope`
- `supplier_portal_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Add setup-task metadata files later if the functional area scope is decomposed into setup tasks. Track token usage for any generated project artifact or skill-run record using the manifest policy.
