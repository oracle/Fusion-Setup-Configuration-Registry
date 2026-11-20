---
skill_id: "cx.service.productivity-tools"
name: "Productivity Tools Implementation Guidance"
description: "Provides CX Service implementation guidance for the Productivity Tools functional area."
layer: "pillar"
pillar: "CX"
offering: "Service"
functional_area: "Productivity Tools"
functional_area_code: "ORA_SVC_PRODUCTIVITY"
type: "planning"
execution_mode: "assisted"
owner_team: "CX service pillar team"
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
  - "core.fusion-api.apps-common.profile-options"
  - "core.fusion-api.rest-api-client"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/service/productivity-tools/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/service/productivity-tools/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/service/productivity-tools/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_SVC_MANAGE_SEARCH_OPTIONS"
  - "ORA_SVC_MANAGE_STANDARD_TEXT_PROFILE_OPTS"
  - "ORA_SVC_MANAGE_SERVICE_REQUEST_DYNAMIC_LINKS"
  - "ORA_SVC_MANAGE_TAGS"
  - "ORA_CONFIGURE_ACTION_BAR_PARAMETERS"
  - "ORA_SVC_MANAGE_NOTE_TYPES"
  - "ORA_MANAGE_SERVICE_REQUEST_MESSAGE_TYPES_AND_SUBTYPES"
  - "ORA_SVC_MANAGE_PASSIVE_BEACON_CONFIGURATION"
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

Provides CX Service implementation guidance for the Productivity Tools functional area.

## When to Use

Use this functional-area skill after Service scope is confirmed and the project needs productivity tools setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `CX`
- Offering: `Service` (`ORA_SVC`)
- Functional area / Setup Object: `Productivity Tools` (`ORA_SVC_PRODUCTIVITY`)

## Setup Tasks

1. [Manage Global Search Profile Options](manage-global-search-profile-options.md) (`ORA_SVC_MANAGE_SEARCH_OPTIONS`)
2. [Manage Standard Text Profile Options](manage-standard-text-profile-options.md) (`ORA_SVC_MANAGE_STANDARD_TEXT_PROFILE_OPTS`)
3. [Manage Service Request Dynamic Links](manage-service-request-dynamic-links.md) (`ORA_SVC_MANAGE_SERVICE_REQUEST_DYNAMIC_LINKS`)
4. [Manage Tags](manage-tags.md) (`ORA_SVC_MANAGE_TAGS`)
5. [Configure Action Bar Parameters](configure-action-bar-parameters.md) (`ORA_CONFIGURE_ACTION_BAR_PARAMETERS`)
6. [Manage Note Types](manage-note-types.md) (`ORA_SVC_MANAGE_NOTE_TYPES`)
7. [Manage Service Request Message Types and Subtypes](manage-service-request-message-types-and-subtypes.md) (`ORA_MANAGE_SERVICE_REQUEST_MESSAGE_TYPES_AND_SUBTYPES`)
8. [Manage Passive Beacon Configuration](manage-passive-beacon-configuration.md) (`ORA_SVC_MANAGE_PASSIVE_BEACON_CONFIGURATION`)

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

## Rule Validation and Execution Handoff

Read the selected task's rows in `ora-resource/ora_input_validation.md`,
`ora_reference_lookups.md`, `ora_defaulting_rules.md`,
`ora_design_enforcement.md`, and `ora_error_handling.md` with the compiled
`ora_rule_registry.json`. These resources return task-validation results; a
ready terminal does not mean that Fusion was changed or that a write is approved.

Configured Global Search Site values are read through
`core.fusion-api.apps-common.profile-options`. Its configured-profile service
contract and privileges must be available; otherwise stop with the missing
prerequisite. The public effective-session `profileValues` resource cannot
establish configured Site state. Keep the current value and requested stored
`Y` or `N` separate; `Yes` and `No` are display labels only.

For catalog-supported setup changes, including Dynamic Link creation/updates,
Tag creation/updates and Note Type Meaning updates, retain the selected Run Book task and use `core.data-loader`
with its FSM workflow. That workflow prepares the source from the selected
task's export and live schema, completes source and Task Hook validation, and
owns the immutable preview, approval, submission and verification. Do not
construct a CSV layout from REST fields. Task rules must not request a separate
load approval, submit a POST/PATCH, or switch to direct REST after validation.
Missing Run Book, source, schema or supported execution steps block the handoff.

After the owning workflow confirms a Global Search change, verify its configured
Site value and ask the user to sign out and sign back in before checking search
visibility. Session refresh is a post-change check, not a pre-preview condition.

## Review Scenarios

| Scenario | Expected rule result |
|---|---|
| Current Site N, enable requested with Y | Accept the planned change; current N does not block preview. |
| Enable requested without a supplied value | Default the requested stored value to Y; preserve the current value. |
| Current Site Y, disable requested with N | Preserve N and return the validated disable intent. |
| Disable requested with Y, or an unsupported stored value | Reject the contradictory or invalid request. |
| User effective value Y but configured Site N | Use the configured Site result; do not treat the session value as Site evidence. |
| Site definition, configured value or required privilege unavailable | Stop with the missing prerequisite; do not substitute the effective-session API. |
| Tag duplicate found | Block the create intent; no mutation or retry. |
| Tag absent, valid intent and matching FSM preflight | Return validation to Data Loader for its exact-artifact approval; do not POST here. |
| Note Type target missing or ambiguous | Block the update intent. |
| Unique Note Type target and valid Meaning | Return validation to the owning FSM workflow; do not PATCH here. |

| Dynamic Link FSM create with exact same-task source and no existing match | Return validated intent to its owning FSM workflow; no direct REST write. |
| Dynamic Link or Tag FSM update with zero/multiple exported targets | Block the update; retain source evidence without selecting another target. |
| Dynamic Link or Tag FSM update with one target and approved export-supported changes | Preserve identity and unchanged values; return evidence to the owning FSM workflow. |
| New administrator Tag with omitted intent flag | Default boolean intent to true; serialize only using confirmed same-task FSM encoding. |
| Generic Tag create with omitted intent flag | Default boolean intent to false; do not assume the FSM encoding. |
| Explicit Tag true/false or an unchanged exported update flag | Preserve the supplied or retained value; create defaults do not overwrite it. |
| FSM flag encoding or owner/preflight unavailable | Block before preview; do not guess Y/N or switch execution routes. |
