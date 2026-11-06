---
skill_id: "scm.procurement.procurement-foundation"
name: "Procurement Foundation Implementation Guidance"
description: "Provides SCM Procurement implementation guidance for the Procurement Foundation functional area."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "Procurement Foundation"
functional_area_code: "ORA_PO_PROC_FOUNDATION_FA"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM procurement pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "procurement_foundation_scope"
  - "procurement_foundation_requirements"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/procurement-foundation/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/procurement-foundation/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/procurement-foundation/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_PO_MANAGE_PROCUREMENT_DOCUMENT_NUMBERING"
  - "PO_MANAGE_PURCHASING_LINE_TYPES"
  - "PO_MANAGE_DOCUMENT_STYLES"
  - "POR_MANAGE_AGENT_ASSIGNMENTS_CATEGORY_HIERARCHY"
  - "PO_MANAGE_PROCUREMENT_AGENTS"
  - "POR_CONFIGURE_REQUISITIONING_BUSINESS_FUNCTION"
  - "PO_MANAGE_PURCHASING_PROFILE_OPTIONS"
  - "PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION"
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

# Procurement Foundation Implementation Guidance

## Purpose

Provides SCM Procurement implementation guidance for the Procurement Foundation functional area.

## When to Use

Use this functional-area skill after Procurement scope is confirmed and the project needs procurement foundation setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `SCM`
- Offering: `Procurement` (`PO_PROCUREMENT`)
- Functional area / Setup Object: `Procurement Foundation` (`ORA_PO_PROC_FOUNDATION_FA`)

## Setup Tasks

1. [Manage Procurement Document Numbering](manage-procurement-document-numbering/SKILL.md) (`ORA_PO_MANAGE_PROCUREMENT_DOCUMENT_NUMBERING`)
2. [Manage Purchasing Line Types](manage-purchasing-line-types/SKILL.md) (`PO_MANAGE_PURCHASING_LINE_TYPES`)
3. [Manage Document Styles](manage-document-styles/SKILL.md) (`PO_MANAGE_DOCUMENT_STYLES`)
4. [Manage Procurement Category Hierarchy](manage-procurement-category-hierarchy/SKILL.md) (`POR_MANAGE_AGENT_ASSIGNMENTS_CATEGORY_HIERARCHY`)
5. [Manage Procurement Agents](manage-procurement-agents/SKILL.md) (`PO_MANAGE_PROCUREMENT_AGENTS`)
6. [Configure Requisitioning Business Function](configure-requisitioning-business-function/SKILL.md) (`POR_CONFIGURE_REQUISITIONING_BUSINESS_FUNCTION`)
7. [Manage Purchasing Profile Options](manage-purchasing-profile-options/SKILL.md) (`PO_MANAGE_PURCHASING_PROFILE_OPTIONS`)
8. [Configure Procurement Business Function](configure-procurement-business-function/SKILL.md) (`PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION`)

## Inputs

- `implementation_objective`
- `project_context`
- `procurement_foundation_scope`
- `procurement_foundation_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated nested setup-task skills for task-level planning, sequencing, setup-data routing, and validation. Track token usage for any generated project artifact or skill-run record using the manifest policy.
