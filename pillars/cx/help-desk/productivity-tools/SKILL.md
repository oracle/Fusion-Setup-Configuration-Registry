---
skill_id: "cx.help-desk.productivity-tools"
name: "Productivity Tools Implementation Guidance"
description: "Provides CX Help Desk implementation guidance for the Productivity Tools functional area."
layer: "pillar"
pillar: "CX"
offering: "Help Desk"
functional_area: "Productivity Tools"
functional_area_code: "ORA_SVC_PRODUCTIVITY"
type: "planning"
execution_mode: "assisted"
owner_team: "CX help desk pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "productivity_tools_scope"
  - "productivity_tools_requirements"
outputs:
  - "functional_area_setup_plan"
  - "configuration_guidance"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "cx.service.productivity-tools"
  - "shared.implementation-planning.offering-task-map-builder"
  - "shared.implementation-planning.task-dependency-resolver"
  - "shared.setup-export.functional-area-export"
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
uses_core:
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
  - "core.diagnostics.role-access-check"
  - "core.data-loader"
  - "core.auth.fusion-oauth-authentication"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/productivity-tools/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/productivity-tools/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/productivity-tools/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_SVC_MANAGE_SERVICE_REQUEST_DYNAMIC_LINKS"
  - "ORA_SVC_MANAGE_TAGS"
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

# Productivity Tools Implementation Guidance

## Purpose

Provides CX Help Desk implementation guidance for the Productivity Tools functional area.

## When to Use

Use this functional-area skill after Help Desk scope is confirmed and the project needs productivity tools setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `CX`
- Offering: `Help Desk` (`ORA_SVC_HELP_DESK`)
- Functional area / Setup Object: `Productivity Tools` (`ORA_SVC_PRODUCTIVITY`)

## Setup Tasks

1. [Manage Service Request Dynamic Links](manage-service-request-dynamic-links.md) (`ORA_SVC_MANAGE_SERVICE_REQUEST_DYNAMIC_LINKS`)
2. [Manage Tags](manage-tags.md) (`ORA_SVC_MANAGE_TAGS`)

## Inputs

- `implementation_objective`
- `project_context`
- `productivity_tools_scope`
- `productivity_tools_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated setup-task metadata files for task-level planning and sequencing. Track token usage for any generated project artifact or skill-run record using the manifest policy.


## Assisted Task Handoff

Load the exact Service task and five rule resources named in each Help Desk
flat task's Guard Rails. Those handoff rules take precedence over generic
CSV/FSM package instructions. Evaluate only the requested operation as assisted
guidance while preserving Help Desk offering, task identity/sequence, project,
environment, source provenance and Run Book binding.

The current core resolver reports these tasks as skipped because this overlay
has no local ora-resource directory. It does not select the Service registry.
Never report that result as canonical validation or use it to continue a load.
Missing guidance or unresolved Help Desk applicability blocks readiness.

This overlay enables guidance/readiness only. Create, update, delete and import
stop before source preparation, preview or external writes until a supported
Help Desk task-validation path, operation-specific same-task contract and owning
workflow are separately established. ZIP shape, catalog flags, prior approval
and historical runs do not clear these prerequisites. Do not rewrite source
context, request duplicate approval or substitute REST, browser or importer.
Live reads also require a separately selected supported project read step.

Preserve explicit Tag boolean intent and exported update flags. Default only
omitted create intent to true for explicit administrator intent, otherwise
false; FSM encoding still requires exact same-task export/XML evidence. Record
sanitized review results through the existing Help Desk project services.
