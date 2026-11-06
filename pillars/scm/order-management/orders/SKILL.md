---
skill_id: "scm.order-management.orders"
name: "Orders Implementation Guidance"
description: "Provides SCM Order Management implementation guidance for the Orders functional area."
layer: "pillar"
pillar: "SCM"
offering: "Order Management"
functional_area: "Orders"
functional_area_code: "ORA_DOO_ORDER_FULLFILLMENT"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM order management pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "orders_scope"
  - "orders_requirements"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/order-management/orders/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/order-management/orders/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/order-management/orders/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_RESERVATION_PRIORITY_FOR_SALES_ORDERS"
  - "ORA_FOM_REVISION_PREFERENCES_FOR_SALES_ORDERS"
  - "DOO_MANAGE_EXTERNAL_INTERFACE_WEB_SERVICE_DETAILS"
  - "ORA_DOO_MANAGE_BUSINESS_EVENT_TRIGGER_POINTS"
  - "ORA_FOM_MANAGE_ORDER_MANAGEMENT_SYSTEM_PARAMETERS"
  - "DOO_MANAGE_ORCHESTRATION_LOOKUPS"
  - "DOO_MANAGE_ORCHESTRATION_PROFILES"
  - "DOO_MANAGE_HOLD_CODE"
  - "DOO_MANAGE_ORCHESTRATION_EXTENSIBLE_FLEXFIELDS"
  - "DOO_MANAGE_ORCHESTRATION_PROCESS_ASSIGNMENT_RULES"
  - "ORA_FOM_MANAGE_ORDER_APPROVAL_RULES"
  - "DOO_MANAGE_EXTERNAL_INTERFACE_ROUTING_RULES"
  - "ORA_FOM_MANAGE_ORDER_MANAGEMENT_EXTENSIONS"
  - "DOO_MANAGE_ORDER_ATTRIBUTES_IDENTIFYING_CHANGE"
  - "DOO_MANAGE_TASK_TYPES"
  - "DOO_MANAGE_STATUS_VALUES"
  - "DOO_MANAGE_TASK_STATUS_CONDITIONS"
  - "DOO_MANAGE_ORCHESTRATION_PROCESS_DEFINITIONS"
  - "DOO_MANAGE_PROCESS_CONSTRAINTS"
  - "DOO_MANAGE_ORCHESTRATION_ATTACHMENT_CATEGORIES"
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

# Orders Implementation Guidance

## Purpose

Provides SCM Order Management implementation guidance for the Orders functional area.

## When to Use

Use this functional-area skill after Order Management scope is confirmed and the project needs orders setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `SCM`
- Offering: `Order Management` (`DOO_ORCHESTRATION`)
- Functional area / Setup Object: `Orders` (`ORA_DOO_ORDER_FULLFILLMENT`)

## Setup Tasks

1. [Reservation Priority for Sales Orders](reservation-priority-for-sales-orders/SKILL.md) (`ORA_RESERVATION_PRIORITY_FOR_SALES_ORDERS`)
2. [Revision Preferences for Sales Orders](revision-preferences-for-sales-orders/SKILL.md) (`ORA_FOM_REVISION_PREFERENCES_FOR_SALES_ORDERS`)
3. [Manage External Interface Web Service Details](manage-external-interface-web-service-details/SKILL.md) (`DOO_MANAGE_EXTERNAL_INTERFACE_WEB_SERVICE_DETAILS`)
4. [Manage Business Event Trigger Points](manage-business-event-trigger-points/SKILL.md) (`ORA_DOO_MANAGE_BUSINESS_EVENT_TRIGGER_POINTS`)
5. [Manage Order Management Parameters](manage-order-management-parameters/SKILL.md) (`ORA_FOM_MANAGE_ORDER_MANAGEMENT_SYSTEM_PARAMETERS`)
6. [Manage Order Lookups](manage-order-lookups/SKILL.md) (`DOO_MANAGE_ORCHESTRATION_LOOKUPS`)
7. [Manage Order Profiles](manage-order-profiles/SKILL.md) (`DOO_MANAGE_ORCHESTRATION_PROFILES`)
8. [Manage Hold Codes](manage-hold-codes/SKILL.md) (`DOO_MANAGE_HOLD_CODE`)
9. [Manage Order Extensible Flexfields](manage-order-extensible-flexfields/SKILL.md) (`DOO_MANAGE_ORCHESTRATION_EXTENSIBLE_FLEXFIELDS`)
10. [Manage Orchestration Process Assignment Rules](manage-orchestration-process-assignment-rules.md) (`DOO_MANAGE_ORCHESTRATION_PROCESS_ASSIGNMENT_RULES`)
11. [Manage Order Approval Rules](manage-order-approval-rules.md) (`ORA_FOM_MANAGE_ORDER_APPROVAL_RULES`)
12. [Manage External Interface Routing Rules](manage-external-interface-routing-rules.md) (`DOO_MANAGE_EXTERNAL_INTERFACE_ROUTING_RULES`)
13. [Manage Order Management Extensions](manage-order-management-extensions.md) (`ORA_FOM_MANAGE_ORDER_MANAGEMENT_EXTENSIONS`)
14. [Manage Order Attributes That Identify Change](manage-order-attributes-that-identify-change.md) (`DOO_MANAGE_ORDER_ATTRIBUTES_IDENTIFYING_CHANGE`)
15. [Manage Task Types](manage-task-types.md) (`DOO_MANAGE_TASK_TYPES`)
16. [Manage Status Values](manage-status-values.md) (`DOO_MANAGE_STATUS_VALUES`)
17. [Manage Task Status Conditions](manage-task-status-conditions.md) (`DOO_MANAGE_TASK_STATUS_CONDITIONS`)
18. [Manage Orchestration Process Definitions](manage-orchestration-process-definitions.md) (`DOO_MANAGE_ORCHESTRATION_PROCESS_DEFINITIONS`)
19. [Manage Processing Constraints](manage-processing-constraints.md) (`DOO_MANAGE_PROCESS_CONSTRAINTS`)
20. [Manage Order Attachment Categories](manage-order-attachment-categories.md) (`DOO_MANAGE_ORCHESTRATION_ATTACHMENT_CATEGORIES`)

## Inputs

- `implementation_objective`
- `project_context`
- `orders_scope`
- `orders_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated setup-task metadata files for task-level planning and sequencing. Track token usage for any generated project artifact or skill-run record using the manifest policy.
