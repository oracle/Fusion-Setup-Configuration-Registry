---
skill_id: "cx.help-desk"
name: "Help Desk"
description: "Coordinates CX Help Desk implementation guidance and routes work to developer-created functional-area skills."
layer: "pillar"
pillar: "CX"
offering: "Help Desk"
type: "orchestration"
execution_mode: "assisted"
owner_team: "CX Help Desk pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "cx_scope"
  - "help_desk_requirements"
outputs:
  - "help_desk_scope"
  - "functional_area_skill_plan"
  - "help_desk_work_products"
  - "token_usage_record"
depends_on:
  - "shared.project-intake.scope-definition"
  - "shared.implementation-planning.offering-task-map-builder"
uses_core:
  - "core.fusion-dev.pillar-skill-gen"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "setup_task_sequence"
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/current/"
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

# Help Desk

## Purpose

Coordinates CX Help Desk implementation guidance across functional areas, setup tasks, and standard implementation activities.

## When to Use

Use this offering-level skill after Help Desk is in scope and before routing to a specific functional-area skill.

## Catalog Identity

- Pillar: `CX`
- Pillar slug: `cx`
- Offering code: `ORA_SVC_HELP_DESK`
- Offering slug: `help-desk`
- Offering folder: `pillars/cx/help-desk`
- Offering mapping source: `knowledge/setup-task-catalog/effective/pillars-offerings-mapping.json`
- Setup task catalog source: `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json`

## Routing Responsibility

This skill routes control to functional-area skills created by developers under this folder. Developers should create functional-area skills with `core.fusion-dev.pillar-skill-gen` using the catalog-backed path pattern:

```text
pillars/cx/help-desk/{functional-area-slug}/
```

When a requested functional area is not yet present under this offering, use the setup catalog below to identify the matching functional area and invoke `core.fusion-dev.pillar-skill-gen` to generate the child skill before adding functional-area-specific guidance.

## Inputs

- `implementation_objective`
- `project_context`
- `cx_scope`
- `help_desk_requirements`

## Outputs

- `help_desk_scope`
- `functional_area_skill_plan`
- `help_desk_work_products`
- `token_usage_record`

## Functional Areas From Catalog

Source: `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json`
Offering code: `ORA_SVC_HELP_DESK`
Functional area count: `12`
Setup task count: `87`

- `ORA_SVC_COMPANY_PROFILE`: Company Profile
- `ORA_ASK_USERS_AND_SECURITY`: Users and Security
- `ORA_SVC_HELP_DESK_REQUEST`: Help Desk Request
- `ORA_SVC_ASSIGNMENT_AND_ROUTING`: Assignment and Routing
- `ORA_SVC_EMAIL_COMMUNICATION_CHANNEL`: Email Communication Channel
- `ORA_SVC_OTHER_COMMUNICATION_CHANNELS`: Other Communication Channels
- `ORA_SVC_SERVICE_CATALOG`: Service Catalog
- `ORA_CSO_KNOWLEDGE_MANAGEMENT`: Knowledge Management
- `ORA_SVC_ACTION_PLANS`: Action Plans
- `ORA_SVC_CASE`: Case Management
- `ORA_SVC_PRODUCTIVITY`: Productivity Tools
- `ORA_SVC_BUSINESS_UNITS`: Business Units

## Implementation Notes

- Keep offering-level planning, scope decisions, sequencing, and cross-functional-area handoffs in this skill.
- Put functional-area-specific implementation guidance in generated child skills under this offering folder.
- Use `core.fusion-dev.pillar-skill-gen` for child functional-area skill creation so generated skills follow the repository contract.
- Use `core.fusion-dev.fusionapps-resource-authoring` after child skill creation when Oracle FusionApps `ora-resource/` guidance is needed.
- Do not create setup-task-specific skills directly under this offering folder unless the user explicitly requests nested task-level skill generation through the pillar skill generator.
