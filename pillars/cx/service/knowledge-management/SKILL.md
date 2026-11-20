---
skill_id: "cx.service.knowledge-management"
name: "Knowledge Management Implementation Guidance"
description: "Provides CX Service implementation guidance for the Knowledge Management functional area."
layer: "pillar"
pillar: "CX"
offering: "Service"
functional_area: "Knowledge Management"
functional_area_code: "ORA_CSO_KNOWLEDGE_MANAGEMENT"
type: "planning"
execution_mode: "assisted"
owner_team: "CX service pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "knowledge_management_scope"
  - "knowledge_management_requirements"
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
  - "core.data-loader"
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.apps-common"
  - "core.fusion-api.rest-api-client"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/service/knowledge-management/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/service/knowledge-management/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/service/knowledge-management/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_CSO_LOCALES_MGMT"
  - "ORA_CSO_CONTENT_TYPES_MGMT"
  - "ORA_CSO_FILE_ATTACHMENTS_MGMT"
  - "ORA_CSO_SEARCH_DICT_MGMT"
  - "ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT"
  - "ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT"
  - "ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT"
  - "ORA_MANAGE_KNOWLEDGE_COMMON_PROFILE_OPTION"
  - "ORA_CSO_ARTICLE_STATUS_MGMT"
  - "ORA_CSO_USER_GROUPS_MGMT"
  - "ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS"
  - "ORA_CSO_CONTENT_TYPES_INDEXING_MGMT_REDWOOD"
  - "ORA_MANAGE_KNOWLEDGE_WORKFLOWS"
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

# Knowledge Management Implementation Guidance

## Purpose

Provides CX Service implementation guidance for the Knowledge Management functional area.

## When to Use

Use this functional-area skill after Service scope is confirmed and the project needs knowledge management setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `CX`
- Offering: `Service` (`ORA_SVC`)
- Functional area / Setup Object: `Knowledge Management` (`ORA_CSO_KNOWLEDGE_MANAGEMENT`)

## Setup Tasks

1. [Manage Knowledge Locales](manage-knowledge-locales.md) (`ORA_CSO_LOCALES_MGMT`)
2. [Manage Knowledge Content Types Classic](manage-knowledge-content-types-classic.md) (`ORA_CSO_CONTENT_TYPES_MGMT`)
3. [Manage Knowledge Files and Images](manage-knowledge-files-and-images.md) (`ORA_CSO_FILE_ATTACHMENTS_MGMT`)
4. [Manage Knowledge Search Dictionary](manage-knowledge-search-dictionary.md) (`ORA_CSO_SEARCH_DICT_MGMT`)
5. [Manage Knowledge Search Profile Options](manage-knowledge-search-profile-options.md) (`ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT`)
6. [Manage Knowledge Panel Profile Options](manage-knowledge-panel-profile-options.md) (`ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT`)
7. [Manage My Knowledge Profile Options](manage-my-knowledge-profile-options.md) (`ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT`)
8. [Manage Knowledge Common Profile Options](manage-knowledge-common-profile-options.md) (`ORA_MANAGE_KNOWLEDGE_COMMON_PROFILE_OPTION`)
9. [Manage Knowledge Article Statuses](manage-knowledge-article-statuses.md) (`ORA_CSO_ARTICLE_STATUS_MGMT`)
10. [Manage Knowledge User Groups](manage-knowledge-user-groups.md) (`ORA_CSO_USER_GROUPS_MGMT`)
11. [Manage Knowledge for Service Requests with Redwood User Interface Profile Options](manage-knowledge-for-service-requests-with-redwood-user-interface-profile-options.md) (`ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS`)
12. [Manage Knowledge Content Types Redwood](manage-knowledge-content-types-redwood/SKILL.md) (`ORA_CSO_CONTENT_TYPES_INDEXING_MGMT_REDWOOD`)
13. [Manage Knowledge Workflows](manage-knowledge-workflows.md) (`ORA_MANAGE_KNOWLEDGE_WORKFLOWS`)

## Inputs

- `implementation_objective`
- `project_context`
- `knowledge_management_scope`
- `knowledge_management_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated setup-task metadata files for task-level planning and sequencing. Track token usage for any generated project artifact or skill-run record using the manifest policy.


## Task Validation Boundaries

Classic content types use an assisted router/Run Book handoff to the separately
persisted Redwood task before setup-data work. Task Hook returns the local
Classic plan, not a structured redirect; ready means guidance only and cannot
authorize Classic export, source preparation, preview or import. Resolve and
bind Redwood separately through the active workflow; never coerce Classic
identity into Redwood identity or transfer source approval. Redwood task validation
executes all returned input, lookup, dependency, default and design resources
before its final FSM handoff. User Groups explicitly distinguishes BU-required
and BU-not-required branches; a disabled feature requires no fabricated lookup.
Locale support comparison may normalize separators/case, while FSM output
always preserves the exact approved export-derived identifier.
