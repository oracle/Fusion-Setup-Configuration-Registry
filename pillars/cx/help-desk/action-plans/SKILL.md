---
skill_id: "cx.help-desk.action-plans"
name: "Action Plans Implementation Guidance"
description: "Provides CX Help Desk implementation guidance for the Action Plans functional area."
layer: "pillar"
pillar: "CX"
offering: "Help Desk"
functional_area: "Action Plans"
functional_area_code: "ORA_SVC_ACTION_PLANS"
type: "planning"
execution_mode: "assisted"
owner_team: "CX help desk pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "action_plans_scope"
  - "action_plans_requirements"
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
  - "cx.service.action-plans"
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
uses_core:
  - "core.data-loader"
  - "core.auth.fusion-oauth-authentication"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/action-plans/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/action-plans/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/action-plans/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_SVC_MANAGE_ACTION_PLAN_PROFILE_OPTIONS"
  - "ORA_SVC_MANAGE_ACTION_CATEGORIES_FOR_ACTION_PLANS"
  - "ORA_SVC_MANAGE_TEMPLATE_CATEGORIES_FOR_ACTION_PLANS"
  - "ORA_SVC_MANAGE_ACTION_PLAN_ACTION_STATUS_MAPPING"
  - "ORA_SVC_MANAGE_ACTION_PLAN_ACTIONS"
  - "ORA_SVC_MANAGE_ACTION_PLAN_TEMPLATES"
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

# Action Plans Implementation Guidance

## Purpose

Provides the Help Desk overlay for Action Plans. Shared setup tasks are owned by and executed through the CX Service Action Plans baseline.

## When to Use

Use this functional-area skill after Help Desk scope is confirmed and the implementation requires Action Plans setup planning, configuration, or validation. Add local guidance only for a documented Help Desk-specific difference.

## Catalog Metadata

- Pillar: `CX`
- Offering: `Help Desk` (`ORA_SVC_HELP_DESK`)
- Functional area / Setup Object: `Action Plans` (`ORA_SVC_ACTION_PLANS`)

## Use Cases and Route To

| Help Desk use case | Route to CX Service baseline |
| --- | --- |
| Configure Action Plan Profile Options | [Manage Action Plan Profile Options](../../service/action-plans/manage-action-plan-profile-options.md) (`ORA_SVC_MANAGE_ACTION_PLAN_PROFILE_OPTIONS`) |
| Manage Action Plan Action Categories | [Manage Action Categories for Action Plans](../../service/action-plans/manage-action-categories-for-action-plans.md) (`ORA_SVC_MANAGE_ACTION_CATEGORIES_FOR_ACTION_PLANS`) |
| Manage Action Plan Template Categories | [Manage Template Categories for Action Plans](../../service/action-plans/manage-template-categories-for-action-plans.md) (`ORA_SVC_MANAGE_TEMPLATE_CATEGORIES_FOR_ACTION_PLANS`) |
| Manage Action Plan Status Values | [Manage Mapping of Action Plan Status Values](../../service/action-plans/manage-mapping-of-action-plan-status-values.md) (`ORA_SVC_MANAGE_ACTION_PLAN_ACTION_STATUS_MAPPING`) |
| Manage Action Plan Actions | [Manage Action Plan Actions](../../service/action-plans/manage-action-plan-actions.md) (`ORA_SVC_MANAGE_ACTION_PLAN_ACTIONS`) |
| Manage Action Plan Templates | [Manage Action Plan Templates](../../service/action-plans/manage-action-plan-templates.md) (`ORA_SVC_MANAGE_ACTION_PLAN_TEMPLATES`) |

### Task Use Cases

- **Manage Action Plan Profile Options:** review profile option definitions and configured values; configure an enabled, updatable profile option scope.
- **Manage Action Categories for Action Plans:** review, create, update, or disable Action Plans action-category lookup codes.
- **Manage Template Categories for Action Plans:** review, create, update, or disable Action Plans template-category lookup codes.
- **Manage Mapping of Action Plan Status Values:** review, create, or update status-condition mappings for an action type and Action Plan status.
- **Manage Action Plan Actions:** review, create, or update actions within the Service contract. Dynamic Process actions cannot include attribute or status mappings; stop before preparing mapping rows, preview or import, including through generic create/update. Preserve supported operations for other action types and existing exported data.
- **Manage Action Plan Templates:** review templates and action flows; create a parent template, add an action, or update an unpublished template within the supported Service contract. Creating new template-action prerequisite relationships is unsupported; stop before constructing or importing relationship rows, including through a generic template update.

The named use cases, detailed steps, safety checks, and execution routes are authoritative in the corresponding CX Service task artifact linked above.

## Setup Tasks

1. [Manage Action Plan Profile Options](manage-action-plan-profile-options.md) (`ORA_SVC_MANAGE_ACTION_PLAN_PROFILE_OPTIONS`)
2. [Manage Action Categories for Action Plans](manage-action-categories-for-action-plans.md) (`ORA_SVC_MANAGE_ACTION_CATEGORIES_FOR_ACTION_PLANS`)
3. [Manage Template Categories for Action Plans](manage-template-categories-for-action-plans.md) (`ORA_SVC_MANAGE_TEMPLATE_CATEGORIES_FOR_ACTION_PLANS`)
4. [Manage Mapping of Action Plan Status Values](manage-mapping-of-action-plan-status-values.md) (`ORA_SVC_MANAGE_ACTION_PLAN_ACTION_STATUS_MAPPING`)
5. [Manage Action Plan Actions](manage-action-plan-actions.md) (`ORA_SVC_MANAGE_ACTION_PLAN_ACTIONS`)
6. [Manage Action Plan Templates](manage-action-plan-templates.md) (`ORA_SVC_MANAGE_ACTION_PLAN_TEMPLATES`)

## Inputs

- `implementation_objective`
- `project_context`
- `action_plans_scope`
- `action_plans_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the [CX Service Action Plans baseline](../../service/action-plans/SKILL.md) and its `ora-resource/` guidance for every routed task. The generated Help Desk task metadata captures catalog identity and routes task execution to that baseline; it does not replace the baseline's task guidance or resources. Before invoking a routed task, verify that its baseline artifact and required guidance are present, then follow its readiness checks, supported execution route, and approval gates. Do not substitute another execution route or bypass an unsupported CSV export/import flag.
