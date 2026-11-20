---
skill_id: "cx.service.communication-channels"
name: "Communication Channels Implementation Guidance"
description: "Provides CX Service implementation guidance for the Communication Channels functional area."
layer: "pillar"
pillar: "CX"
offering: "Service"
functional_area: "Communication Channels"
functional_area_code: "ORA_SVC_COMM_CHANNELS"
type: "planning"
execution_mode: "assisted"
owner_team: "CX service pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "communication_channels_scope"
  - "communication_channels_requirements"
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
  - "core.fusion-api.apps-common"
  - "core.fusion-api.apps-common.profile-options"
  - "core.fusion-api.rest-api-client"
  - "core.auth.fusion-oauth-authentication"
  - "core.data-loader"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/service/communication-channels/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/service/communication-channels/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/service/communication-channels/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_SVC_MANAGE_COMM_CHANNELS"
  - "ORA_SVC_MANAGE_INBOUND_EMAIL_PROFILE_OPTS"
  - "ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTS"
  - "ORA_SVC_MANAGE_EMAIL_FILTERS"
  - "ORA_SVC_MANAGE_OMNI_CHANNEL_PROFILE_OPTS"
  - "ORA_MANAGE_MCA_PROFILE_OPTIONS"
  - "ORA_SVC_INTERACTION_PROFILE_OPTIONS"
  - "ORA_MANAGE_EMAIL_PROFILE_OPTIONS"
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

# Communication Channels Implementation Guidance

## Purpose

Provides CX Service implementation guidance for the Communication Channels functional area.

## When to Use

Use this functional-area skill after Service scope is confirmed and the project needs communication channels setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `CX`
- Offering: `Service` (`ORA_SVC`)
- Functional area / Setup Object: `Communication Channels` (`ORA_SVC_COMM_CHANNELS`)

## Setup Tasks

1. [Manage Communication Channels](manage-communication-channels.md) (`ORA_SVC_MANAGE_COMM_CHANNELS`)
2. [Manage Inbound E-Mail Profile Options](manage-inbound-e-mail-profile-options.md) (`ORA_SVC_MANAGE_INBOUND_EMAIL_PROFILE_OPTS`)
3. [Manage Outbound E-Mail Profile Options](manage-outbound-e-mail-profile-options.md) (`ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTS`)
4. [Manage E-Mail Filters](manage-e-mail-filters.md) (`ORA_SVC_MANAGE_EMAIL_FILTERS`)
5. [Manage Omnichannel Profile Options](manage-omnichannel-profile-options.md) (`ORA_SVC_MANAGE_OMNI_CHANNEL_PROFILE_OPTS`)
6. [Manage MCA Profile Options](manage-mca-profile-options.md) (`ORA_MANAGE_MCA_PROFILE_OPTIONS`)
7. [Manage Interaction Profile Options](manage-interaction-profile-options.md) (`ORA_SVC_INTERACTION_PROFILE_OPTIONS`)
8. [Manage Email Profile Options](manage-email-profile-options.md) (`ORA_MANAGE_EMAIL_PROFILE_OPTIONS`)

### Advisory-Only Catalog Entries

The following entries are excluded from `required_setup_tasks` and executable
implementation scope. They identify catalog tasks and missing source contracts
only; their catalog Y flags do not enable execution.

- [Manage Service Assignment Objects](manage-service-assignment-objects.md) (`ORA_SVC_MANAGE_SERVICE_REQUEST_ASSIGNMENT_OBJECTS`) — advisory only; execution unsupported.
- [Manage Service Regions](manage-service-regions.md) (`ORA_SVC_MANAGE_SERVICE_ZONES`) — advisory only; execution unsupported.
- [Manage Service Assignment Rules](manage-service-assignment-rules.md) (`ORA_SVC_MANAGE_SERVICE_REQUEST_ASSIGNMENT_RULES`) — advisory only; execution unsupported.

These three tasks must stop before validation execution, export, package
preparation, preview, import or mutation. Preserve the incomplete registry and
canonical resolver refusal; do not waive readiness or substitute another route.
Use their advisory workflow to record the gap and request source-backed task
contracts. Only after resource authoring, recompilation and readiness/audit review
may they be proposed as executable implementation tasks.

## Inputs

- `implementation_objective`
- `project_context`
- `communication_channels_scope`
- `communication_channels_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated setup-task metadata files for task-level planning and sequencing. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Profile Task Handoff

Before profile reads or FSM preparation, load the exact selected task and its
matching validation, lookup, dependency, default, design and error rules from
`ora-resource/`. Use `core.fusion-api.apps-common.profile-options` for technical
reads only after the active workflow selects them and checks identity, access
and scope. Preserve the original task code, sequence, environment, project and
Run Book binding throughout.

Inbound and Outbound E-Mail Profile Options use Manage Email Profile Options
(`ORA_MANAGE_EMAIL_PROFILE_OPTIONS`) as an assisted guidance handoff. Load that
exact task and its matching resources in addition to the original task's rules.
This is not an automatic core task redirect: do not rewrite the original task
identity or reuse an approval for another task. Missing or ambiguous guidance
blocks the handoff.

Distinguish current-session effective values from configured-level values.
`profileValues` may answer an explicitly effective-value question, but cannot
prove the configured value for a requested Site or User target. Resolve the
profile definition and the exact configured child/key through the selected core
profile-options workflow and task lookup rules. Do not enable a level or infer
scope from an effective value; reject unsupported or unresolved targets.

FSM changes require same-task export/XML, task-owned profile identity, verified
enabled/updateable level, retained keys, explicit approved replacement, package
validation and the owning `core.data-loader` preview, approval, execution and
verification gates. Verify the exact configured target using a fresh scoped
read or same-task export; effective-value reads are supplementary only. A ready
rule plan or lookup result never grants write permission. No direct REST write
or substitute execution route is enabled by this handoff.
