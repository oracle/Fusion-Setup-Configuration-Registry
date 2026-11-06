---
skill_id: "scm.procurement.self-service-procurement"
name: "Self Service Procurement Implementation Guidance"
description: "Provides SCM Procurement implementation guidance for the Self Service Procurement functional area."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "Self Service Procurement"
functional_area_code: "PO_SSP_DEPLOYED"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM procurement pillar team"
version: "0.1.1"
inputs:
  - "implementation_objective"
  - "project_context"
  - "self_service_procurement_scope"
  - "self_service_procurement_requirements"
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
  - "core.fusion-api.apps-common"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/self-service-procurement/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/self-service-procurement/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/self-service-procurement/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "POR_MANAGE_REQUISITION_DESCRIPTIVE_FLEXFIELDS"
  - "POR_MANAGE_INFORMATION_TEMPLATE_DESCRIPTIVE_FLEXFIELDS"
  - "POR_MANAGE_SELF_SERVICE_PROCUREMENT_PROFILE_OPTIONS"
  - "POR_MANAGE_REQUISITION_VALUE_SETS"
  - "POR_MANAGE_INFORMATION_TEMPLATE_VALUE_SETS"
  - "POR_MANAGE_CATALOG_CATEGORY_HIERARCHY"
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

# Self Service Procurement Implementation Guidance

## Purpose

Provides SCM Procurement implementation guidance for the Self Service Procurement functional area.

## When to Use

Use this functional-area skill after Procurement scope is confirmed and the project needs self service procurement setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `SCM`
- Offering: `Procurement` (`PO_PROCUREMENT`)
- Functional area / Setup Object: `Self Service Procurement` (`PO_SSP_DEPLOYED`)

## Setup Tasks

1. [Manage Requisition Descriptive Flexfields](manage-requisition-descriptive-flexfields/SKILL.md) (`POR_MANAGE_REQUISITION_DESCRIPTIVE_FLEXFIELDS`)
2. [Manage Information Template Descriptive Flexfields](manage-information-template-descriptive-flexfields/SKILL.md) (`POR_MANAGE_INFORMATION_TEMPLATE_DESCRIPTIVE_FLEXFIELDS`)
3. [Manage Self Service Procurement Profile Options](manage-self-service-procurement-profile-options.md) (`POR_MANAGE_SELF_SERVICE_PROCUREMENT_PROFILE_OPTIONS`)
4. [Manage Requisition Value Sets](manage-requisition-value-sets.md) (`POR_MANAGE_REQUISITION_VALUE_SETS`)
5. [Manage Information Template Value Sets](manage-information-template-value-sets.md) (`POR_MANAGE_INFORMATION_TEMPLATE_VALUE_SETS`)
6. [Manage Catalog Category Hierarchy](manage-catalog-category-hierarchy/SKILL.md) (`POR_MANAGE_CATALOG_CATEGORY_HIERARCHY`)

## Inputs

- `implementation_objective`
- `project_context`
- `self_service_procurement_scope`
- `self_service_procurement_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated nested setup-task skills for task-level planning, sequencing,
setup-data routing, REST execution planning, and validation. Track token
usage for any generated project artifact or skill-run record using the manifest
policy.

For direct profile-option and value-set operations, follow the applicable flat
task metadata file and route the request through `core.fusion-api.apps-common`.
Keep task-level CSV export, validation, and import on their declared shared and
Data Loader routes.
