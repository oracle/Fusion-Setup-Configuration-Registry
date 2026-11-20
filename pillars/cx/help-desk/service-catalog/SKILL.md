---
skill_id: "cx.help-desk.service-catalog"
name: "Service Catalog Implementation Guidance"
description: "Provides CX Help Desk implementation guidance for the Service Catalog functional area."
layer: "pillar"
pillar: "CX"
offering: "Help Desk"
functional_area: "Service Catalog"
functional_area_code: "ORA_SVC_SERVICE_CATALOG"
type: "planning"
execution_mode: "assisted"
owner_team: "CX help desk pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "service_catalog_scope"
  - "service_catalog_requirements"
outputs:
  - "functional_area_setup_plan"
  - "configuration_guidance"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "cx.service.service-catalog"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/service-catalog/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/service-catalog/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/service-catalog/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "QSC_MANAGE_PRODUCT_GROUPS"
  - "QSC_MANAGE_PRODUCT_GROUP_USAGE"
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

# Service Catalog Implementation Guidance

## Purpose

Provides CX Help Desk implementation guidance for the Service Catalog functional area.

## When to Use

Use this functional-area skill after Help Desk scope is confirmed and the project needs service catalog setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `CX`
- Offering: `Help Desk` (`ORA_SVC_HELP_DESK`)
- Functional area / Setup Object: `Service Catalog` (`ORA_SVC_SERVICE_CATALOG`)

## Setup Tasks

1. [Manage Product Groups](manage-product-groups.md) (`QSC_MANAGE_PRODUCT_GROUPS`)
2. [Manage Product Group Usage](manage-product-group-usage.md) (`QSC_MANAGE_PRODUCT_GROUP_USAGE`)

## Inputs

- `implementation_objective`
- `project_context`
- `service_catalog_scope`
- `service_catalog_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated setup-task metadata files for task-level planning and sequencing. Track token usage for any generated project artifact or skill-run record using the manifest policy.


## Assisted Usage Handoff

Manage Product Group Usage reuses Service rules as assisted guidance only.
Load `pillars/cx/service/service-catalog/manage-product-group-usage.md`, then
its exact `QSC_MANAGE_PRODUCT_GROUP_USAGE` / Manage Product Group Usage entries
in `ora-resource/ora_rule_registry.json` and their validation, reference-lookup
and error resources. Resolve resource filenames relative to the Service package.
Missing or ambiguous providers, mismatched task identity, missing resources or
unresolved Help Desk applicability block the review; never substitute another task.

The current core resolver does not follow depends_on or Route To declarations.
It returns skipped with zero resources for this Help Desk overlay. That is not
canonical validation and must not be used to continue a load. Selecting the
Service rules for review does not replace the selected Help Desk context.
Preserve offering, functional area, task code/name, sequence, project, environment,
source provenance and active Run Book binding.

These rules take precedence over generic CSV/FSM workflow and package instructions.
This overlay provides guidance/readiness only. Stop create/update/delete/import
before source preparation, preview or external writes until a supported Help Desk
task-validation path, operation-specific same-task contract and owning workflow
are separately established. Live reads also require a separately selected supported
project read step. Do not rewrite context or use Service REST creation, a browser,
generic client, prior approval or ZIP shape to bypass a missing execution path.
Core Data Loader owns any subsequently selected preview, exact-artifact approval,
execution and verification. Record the review and blockers through project services.

Manage Product Groups remains blocked on missing Help Desk source guidance and
catalog N/N import flags. It inherits neither Usage delegation nor Service REST
creation. No Data Loader import mode is selected for it.
