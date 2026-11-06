---
skill_id: "cx.sales.integrations"
name: "Integrations Implementation Guidance"
description: "Provides CX Sales implementation guidance for the Integrations functional area."
layer: "pillar"
pillar: "CX"
offering: "Sales"
functional_area: "Integrations"
functional_area_code: "ORA_ZCA_INTEGRATIONS"
type: "planning"
execution_mode: "assisted"
owner_team: "CX sales pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "integrations_scope"
  - "integrations_requirements"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/sales/integrations/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/sales/integrations/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/sales/integrations/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_ZCA_OSC_CPQ_INTEGRATION"
  - "ORA_MANAGE_DATA_ENRICHMENT_INTEGRATION"
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

# Integrations Implementation Guidance

## Purpose

Provides CX Sales implementation guidance for the Integrations functional area.

## When to Use

Use this functional-area skill after Sales scope is confirmed and the project needs integrations setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `CX`
- Offering: `Sales` (`ORA_MIDSIZE_SALES`)
- Functional area / Setup Object: `Integrations` (`ORA_ZCA_INTEGRATIONS`)

## Setup Tasks

1. [Manage Oracle CX Sales to Oracle CPQ Cloud Integration](manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/SKILL.md) (`ORA_ZCA_OSC_CPQ_INTEGRATION`)
2. [Manage Data Enrichment Integration](manage-data-enrichment-integration/SKILL.md) (`ORA_MANAGE_DATA_ENRICHMENT_INTEGRATION`)

## Inputs

- `implementation_objective`
- `project_context`
- `integrations_scope`
- `integrations_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated nested setup-task skills for task-level planning, sequencing, setup-data routing, and validation. Track token usage for any generated project artifact or skill-run record using the manifest policy.
