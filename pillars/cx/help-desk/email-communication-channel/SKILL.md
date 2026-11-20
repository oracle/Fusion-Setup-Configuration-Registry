---
skill_id: "cx.help-desk.email-communication-channel"
name: "Email Communication Channel Implementation Guidance"
description: "Provides CX Help Desk implementation guidance for the Email Communication Channel functional area."
layer: "pillar"
pillar: "CX"
offering: "Help Desk"
functional_area: "Email Communication Channel"
functional_area_code: "ORA_SVC_EMAIL_COMMUNICATION_CHANNEL"
type: "planning"
execution_mode: "assisted"
owner_team: "CX help desk pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "email_communication_channel_scope"
  - "email_communication_channel_requirements"
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
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.apps-common"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/email-communication-channel/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/email-communication-channel/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/email-communication-channel/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS"
  - "ORA_SVC_MANAGE_COMMON_OUTBOUND_EMAIL_PROFILE_OPTIONS"
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

# Email Communication Channel Implementation Guidance

## Purpose

Provides CX Help Desk implementation guidance for the Email Communication Channel functional area.

## When to Use

Use this functional-area skill after Help Desk scope is confirmed and the project needs email communication channel setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `CX`
- Offering: `Help Desk` (`ORA_SVC_HELP_DESK`)
- Functional area / Setup Object: `Email Communication Channel` (`ORA_SVC_EMAIL_COMMUNICATION_CHANNEL`)

## Setup Tasks

1. [Manage Email Templates for HR Help Desk](manage-email-templates-for-hr-help-desk.md) (`ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTIONS_FOR_HR_SERVICE_REQUESTS`)
2. [Manage Common Outbound Email Profile Options](manage-common-outbound-email-profile-options.md) (`ORA_SVC_MANAGE_COMMON_OUTBOUND_EMAIL_PROFILE_OPTIONS`)

## Inputs

- `implementation_objective`
- `project_context`
- `email_communication_channel_scope`
- `email_communication_channel_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated setup-task metadata files for task-level planning and sequencing. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Oracle Guidance Resource Execution Boundary

Before running the task-local `fusion-rest` reference lookup in `ora-resource/ora_rule_registry.json`, establish the authenticated Fusion context with `core.auth.fusion-oauth-authentication` and perform the allow-listed profile-value read through the approved `core.fusion-api.apps-common` route. Do not issue direct REST requests from this pillar skill or its resource guidance.

The configured-profile lookup branch is read-only. The separate FSM update branch validates intent and evidence for the owning Data Loader workflow only. A registry node, metadata file, or lookup result never authorizes a profile-value update; stop unless a separate source-backed task contract, exact preview, explicit approval, and authorized core executor are present.

Use the Oracle Help Desk email configuration guide for the supported HR Help Desk email-template profile options: `SVC_SR_RESPONSE_TEMPLATE_NAME_HRD`, `SVC_SR_FORWARD_TEMPLATE_NAME_HRD`, and `SVC_SR_SYSTEM_RESPONSE_TEMPLATE_NAME_HRD`.

Common Outbound currently supports same-task package inspection and validation only. Its header-only export does not establish profile-definition or level readiness. Follow its task guidance and do not use the HR template read registry or a legacy outbound task to enable an import.

Common Outbound has a registered local refusal-only rule plan. Task Hook ready
means the plan can be evaluated, not that import is ready. Evaluate its rules
and return ordered blocked ruleResults to the owning Data Loader Task Hook
`build-data-load-preview` before any import preview. It requires the exact task
context and finalData.archiveSha256 and rejects blocked or missing results,
including with a readiness waiver. Only for supported tasks whose rules pass,
the owning workflow uses `approve-data-load-preview` after explicit approval and
`verify-approved-data-load-archive` before upload. Preserve the approved preview
and exact archive; any change requires a fresh preview and approval. Do not use
removed memory-session APIs or invoke Task Validator directly.
There is no passed or overridden import outcome. The execution_blocker field is
descriptive metadata and is not automatically enforced by the current core.
Selected shared export/package validation remains separate and available; a
missing/skipped rule entry, structural package, ZIP or prior approval never
enables import.
