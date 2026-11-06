---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.manufacturing-master-data"
name: "Manufacturing Master Data Implementation Guidance"
description: "Provides SCM Manufacturing and Supply Chain Materials Management implementation guidance for the Manufacturing Master Data functional area."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Manufacturing Master Data"
functional_area_code: "ORA_WIS_COMMON_MFG_WORK_SETUP"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM manufacturing and supply chain materials management pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "manufacturing_master_data_scope"
  - "manufacturing_master_data_requirements"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/manufacturing-master-data/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/manufacturing-master-data/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/manufacturing-master-data/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_WIS_MANAGE_DATA_SECURITY_CONTROLS"
  - "ORA_WIS_WORK_SETUP_DESCRIPTIVE_FLEXFIELDS"
  - "ORA_WIS_MANAGE_PRODUCTION_LOOKUPS"
  - "ORA_WIP_WORK_EXECUTION_DESCRIPTIVE_FLEXFIELDS"
  - "ORA_RCS_MANAGE_PLANT_PARAMETERS"
  - "ORA_WIS_WORKSTATIONS"
  - "ORA_REDWOOD_MANUFACTURING_WORK_AREAS"
  - "ORA_REDWOOD_MANUFACTURING_WORK_CENTERS"
  - "ORA_REDWOOD_MANUFACTURING_RESOURCES"
  - "ORA_REDWOOD_MANUFACTURING_RESOURCE_INSTANCES"
  - "ORA_REDWOOD_MANUFACTURING_WORK_ORDER_STATUSES"
  - "ORA_WIE_WORK_ORDER_GROUPS"
  - "ORA_WIE_SMART_OPERATIONS_CONFIGURATIONS"
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

# Manufacturing Master Data Implementation Guidance

## Purpose

Provides SCM Manufacturing and Supply Chain Materials Management implementation guidance for the Manufacturing Master Data functional area.

## When to Use

Use this functional-area skill after Manufacturing and Supply Chain Materials Management scope is confirmed and the project needs manufacturing master data setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `SCM`
- Offering: `Manufacturing and Supply Chain Materials Management` (`ORA_MANUFACTURING_AND_SUPPLY_C`)
- Functional area / Setup Object: `Manufacturing Master Data` (`ORA_WIS_COMMON_MFG_WORK_SETUP`)

## Setup Tasks

1. [Manage Data Security Controls for Manufacturing](manage-data-security-controls-for-manufacturing/SKILL.md) (`ORA_WIS_MANAGE_DATA_SECURITY_CONTROLS`)
2. [Manage Work Setup Descriptive Flexfields](manage-work-setup-descriptive-flexfields.md) (`ORA_WIS_WORK_SETUP_DESCRIPTIVE_FLEXFIELDS`)
3. [Manage Production Lookups](manage-production-lookups.md) (`ORA_WIS_MANAGE_PRODUCTION_LOOKUPS`)
4. [Manage Work Execution Descriptive Flexfields](manage-work-execution-descriptive-flexfields.md) (`ORA_WIP_WORK_EXECUTION_DESCRIPTIVE_FLEXFIELDS`)
5. [Manage Plant Parameters](manage-plant-parameters/SKILL.md) (`ORA_RCS_MANAGE_PLANT_PARAMETERS`)
6. [Workstations](workstations/SKILL.md) (`ORA_WIS_WORKSTATIONS`)
7. [Manufacturing Work Areas](manufacturing-work-areas/SKILL.md) (`ORA_REDWOOD_MANUFACTURING_WORK_AREAS`)
8. [Manufacturing Work Centers](manufacturing-work-centers/SKILL.md) (`ORA_REDWOOD_MANUFACTURING_WORK_CENTERS`)
9. [Manufacturing Resources](manufacturing-resources/SKILL.md) (`ORA_REDWOOD_MANUFACTURING_RESOURCES`)
10. [Manufacturing Resource Instances](manufacturing-resource-instances/SKILL.md) (`ORA_REDWOOD_MANUFACTURING_RESOURCE_INSTANCES`)
11. [Manufacturing and Maintenance Work Order Statuses](manufacturing-and-maintenance-work-order-statuses/SKILL.md) (`ORA_REDWOOD_MANUFACTURING_WORK_ORDER_STATUSES`)
12. [Manufacturing Work Order Groups](manufacturing-work-order-groups/SKILL.md) (`ORA_WIE_WORK_ORDER_GROUPS`)
13. [Smart Operations Configurations](smart-operations-configurations/SKILL.md) (`ORA_WIE_SMART_OPERATIONS_CONFIGURATIONS`)

## Inputs

- `implementation_objective`
- `project_context`
- `manufacturing_master_data_scope`
- `manufacturing_master_data_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated nested setup-task skills for task-level planning, sequencing, setup-data routing, and validation. Track token usage for any generated project artifact or skill-run record using the manifest policy.
