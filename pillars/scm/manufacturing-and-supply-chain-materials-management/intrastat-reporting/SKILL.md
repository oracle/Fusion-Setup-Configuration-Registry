---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.intrastat-reporting"
name: "Intrastat Reporting Implementation Guidance"
description: "Provides SCM Manufacturing and Supply Chain Materials Management implementation guidance for the Intrastat Reporting functional area."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Intrastat Reporting"
functional_area_code: "JMF_INTRASTAT"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM manufacturing and supply chain materials management pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "intrastat_reporting_scope"
  - "intrastat_reporting_requirements"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/intrastat-reporting/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/intrastat-reporting/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/intrastat-reporting/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_INTRASTAT_PARAMETERS"
  - "ORA_INTRASTAT_COUNTRY_CHARACTERISTICS"
  - "ORA_INTRASTAT_RULES"
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

# Intrastat Reporting Implementation Guidance

## Purpose

Provides SCM Manufacturing and Supply Chain Materials Management implementation guidance for the Intrastat Reporting functional area.

## When to Use

Use this functional-area skill after Manufacturing and Supply Chain Materials Management scope is confirmed and the project needs intrastat reporting setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `SCM`
- Offering: `Manufacturing and Supply Chain Materials Management` (`ORA_MANUFACTURING_AND_SUPPLY_C`)
- Functional area / Setup Object: `Intrastat Reporting` (`JMF_INTRASTAT`)

## Setup Tasks

1. [Intrastat Parameters](intrastat-parameters/SKILL.md) (`ORA_INTRASTAT_PARAMETERS`)
2. [Intrastat Country Characteristics](intrastat-country-characteristics/SKILL.md) (`ORA_INTRASTAT_COUNTRY_CHARACTERISTICS`)
3. [Intrastat Rules](intrastat-rules/SKILL.md) (`ORA_INTRASTAT_RULES`)

## Inputs

- `implementation_objective`
- `project_context`
- `intrastat_reporting_scope`
- `intrastat_reporting_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated nested setup-task skills for task-level planning, sequencing, setup-data routing, and validation. Track token usage for any generated project artifact or skill-run record using the manifest policy.
