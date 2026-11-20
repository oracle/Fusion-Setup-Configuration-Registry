---
skill_id: "cx.service.service-catalog"
name: "Service Catalog Implementation Guidance"
description: "Provides CX Service implementation guidance for the Service Catalog functional area."
layer: "pillar"
pillar: "CX"
offering: "Service"
functional_area: "Service Catalog"
functional_area_code: "ORA_SVC_SERVICE_CATALOG"
type: "planning"
execution_mode: "assisted"
owner_team: "CX service pillar team"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/service/service-catalog/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/service/service-catalog/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/service/service-catalog/current/"
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

Provides CX Service implementation guidance for the Service Catalog functional area.

## When to Use

Use this functional-area skill after Service scope is confirmed and the project needs service catalog setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `CX`
- Offering: `Service` (`ORA_SVC`)
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


## Task Rule Handoff

Read the task-scoped validation, dependency, lookup, default, design and error
resources in `ora-resource/` and use the compiled registry for the selected task.
Perform GET lookups only when the active workflow selects its read step, using
`core.fusion-api.rest-api-client` after identity and privilege checks.
Relationship and Usage child-item reads return their own results without a
mutation approval gate. Filter-attribute reads resolve the parent first.

Product Group Usage has separate GET and catalog-supported FSM import branches.
Return validated FSM intent to the active Run Book and `core.data-loader`;
`shared.setup-export.task-level-export` and
`shared.validation.setup-data-validator` supply export and validation through
that workflow. Core owns live schema, immutable artifact, exact preview,
approval, execution and verification. Task-rule success authorizes no write.

Manage Product Groups has no selected FSM import mode because both catalog
import flags are N. For an explicit create, use the Product Groups-specific
[command](scripts/product_group_rest.py) and its
[operation contract](ora-resource/ora_rest_documentation.md). It implements the
three preview/verify/create commands for this exact Service task only, delegates
all HTTP/authentication to the existing core REST client, and reuses core
Run Book/context guards. Evidence outputs are restricted to the selected Product Groups directory. Core Task Hook is not claimed to
provide those REST commands. Preserve domain validation, reviewed privileges,
immutable preview, exact immediate approval, one attempt and fresh verification.
No other mutation or unsupported CSV/FSM import is enabled. Read the operation
contract and ora_error_handling.md before preview or execution.
