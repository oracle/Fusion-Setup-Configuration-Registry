---
skill_id: "scm.procurement.purchasing-foundation"
name: "Purchasing Foundation Implementation Guidance"
description: "Provides SCM Procurement implementation guidance for the Purchasing Foundation functional area."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "Purchasing Foundation"
functional_area_code: "ORA_PO_PURCHASING_FOUNDATION"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM procurement pillar team"
version: "0.1.1"
inputs:
  - "implementation_objective"
  - "project_context"
  - "purchasing_foundation_scope"
  - "purchasing_foundation_requirements"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/purchasing-foundation/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/purchasing-foundation/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/purchasing-foundation/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "PO_MANAGE_PURCHASING_VALUE_SETS"
  - "PO_MANAGE_PURCHASING_DESCRIPTIVE_FLEXFIELDS"
  - "PO_MANAGE_HAZARD_CLASSES"
  - "PO_MANAGE_UN_NUMBERS"
  - "PO_MANAGE_APPROVED_SUPPLIER_LIST_STATUSES"
  - "ORA_PO_MANAGE_BUYER_ASSIGNMENT_RULES"
  - "ORA_PO_MANAGE_ASSIGNMENT_RULE_SETS_LOOKUP"
  - "PO_MANAGE_CHANGE_ORDER_TEMPLATES"
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

# Purchasing Foundation Implementation Guidance

## Purpose

Provides SCM Procurement implementation guidance for the Purchasing Foundation functional area.

## When to Use

Use this functional-area skill after Procurement scope is confirmed and the project needs purchasing foundation setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `SCM`
- Offering: `Procurement` (`PO_PROCUREMENT`)
- Functional area / Setup Object: `Purchasing Foundation` (`ORA_PO_PURCHASING_FOUNDATION`)

## Setup Tasks

1. [Manage Purchasing Value Sets](manage-purchasing-value-sets/SKILL.md) (`PO_MANAGE_PURCHASING_VALUE_SETS`)
2. [Manage Purchasing Descriptive Flexfields](manage-purchasing-descriptive-flexfields/SKILL.md) (`PO_MANAGE_PURCHASING_DESCRIPTIVE_FLEXFIELDS`)
3. [Manage Hazard Classes](manage-hazard-classes/SKILL.md) (`PO_MANAGE_HAZARD_CLASSES`)
4. [Manage UN Numbers](manage-un-numbers/SKILL.md) (`PO_MANAGE_UN_NUMBERS`)
5. [Manage Approved Supplier List Statuses](manage-approved-supplier-list-statuses/SKILL.md) (`PO_MANAGE_APPROVED_SUPPLIER_LIST_STATUSES`)
6. [Manage Buyer Assignment Rules](manage-buyer-assignment-rules/SKILL.md) (`ORA_PO_MANAGE_BUYER_ASSIGNMENT_RULES`)
7. [Manage Buyer Assignment Rule Sets Lookup](manage-buyer-assignment-rule-sets-lookup/SKILL.md) (`ORA_PO_MANAGE_ASSIGNMENT_RULE_SETS_LOOKUP`)
8. [Manage Change Order Templates](manage-change-order-templates/SKILL.md) (`PO_MANAGE_CHANGE_ORDER_TEMPLATES`)

## Inputs

- `implementation_objective`
- `project_context`
- `purchasing_foundation_scope`
- `purchasing_foundation_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated nested setup-task skills for task-level planning, sequencing, setup-data routing, and validation. Track token usage for any generated project artifact or skill-run record using the manifest policy.


## Hazard Class Validation Routing

Route Manage Hazard Classes preparation to the nested task's
[local validation contract](manage-hazard-classes/SKILL.md#hazard-class-resource-contract).
It requires both name and code on every row, preserves optional values and field
omission, and does not require create/update intent or a record-existence lookup.
Supplied IDs pass through unchanged for Data Loader to evaluate.

Use its single local graph through `READY_FOR_DATALOADER_REVIEW`. Do not add an
external identity check or select POST/PATCH at the functional-area level.
Data Loader owns identity and operation handling, metadata/source checks,
preview, approval, submission, and verification. Automatic operation selection
remains an approved working assumption, not a verified server capability.
Local validation readiness does not mean that a load has succeeded.
