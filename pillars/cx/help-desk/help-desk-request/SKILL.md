---
skill_id: "cx.help-desk.help-desk-request"
name: "Help Desk Request Implementation Guidance"
description: "Provides CX Help Desk implementation guidance for the Help Desk Request functional area."
layer: "pillar"
pillar: "CX"
offering: "Help Desk"
functional_area: "Help Desk Request"
functional_area_code: "ORA_SVC_HELP_DESK_REQUEST"
type: "planning"
execution_mode: "assisted"
owner_team: "CX help desk pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "help_desk_request_scope"
  - "help_desk_request_requirements"
outputs:
  - "functional_area_setup_plan"
  - "configuration_guidance"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "cx.service.service-request"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/help-desk-request/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/help-desk-request/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/help-desk-request/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS"
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

# Help Desk Request Implementation Guidance

## Purpose

Provides CX Help Desk implementation guidance for the Help Desk Request functional area.

## When to Use

Use this functional-area skill after Help Desk scope is confirmed and the project needs help desk request setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `CX`
- Offering: `Help Desk` (`ORA_SVC_HELP_DESK`)
- Functional area / Setup Object: `Help Desk Request` (`ORA_SVC_HELP_DESK_REQUEST`)

## Setup Tasks

1. [Manage Categories for HR Help Desk Requests](manage-categories-for-hr-help-desk-requests.md) (`ORA_SVC_MANAGE_CATEGORIES_FOR_HR_SERVICE_REQUESTS`)

## Inputs

- `implementation_objective`
- `project_context`
- `help_desk_request_scope`
- `help_desk_request_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated setup-task metadata files for task-level planning and sequencing. Track token usage for any generated project artifact or skill-run record using the manifest policy.
