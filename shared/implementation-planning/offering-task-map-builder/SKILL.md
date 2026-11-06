---
skill_id: "shared.implementation-planning.offering-task-map-builder"
name: "Offering Task Map Builder"
description: "Provides cross-pillar offering task map builder guidance for Oracle Fusion Cloud implementations."
layer: "shared"
pillar: "Common"
type: "planning"
execution_mode: "assisted"
owner_team: "Shared enablement team with pillar review"
version: "0.1.3"
inputs: 
  - "implementation_objective"
  - "project_context"
  - "pillar_scope"
  - "offering_scope"
  - "functional_area_scope"
outputs: 
  - "recommendations"
  - "work_products"
  - "review_points"
  - "token_usage_record"
depends_on:
  - "shared.implementation-planning.task-dependency-resolver"
uses_core:
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
  - "setup_task_sequence"
  - "design_decisions"
  - "configuration_blueprints"
workspace_outputs:
  - artifact_type: "setup_task_sequence"
    default_location: "project/{project_id}/artifacts/shared/implementation-planning/{skill-name}/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/shared/implementation-planning/{skill-name}/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
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

# Offering Task Map Builder

## Purpose

Provides cross-pillar offering task map builder guidance for Oracle Fusion Cloud implementations.

## When to Use

Use this shared skill when the implementation activity applies across multiple pillars or should be standardized before being specialized by ERP, HCM, SCM, CX, or common setup areas.

## Inputs

- `implementation_objective`
- `project_context`
- `pillar_scope`
- `offering_scope`
- `functional_area_scope`

## Outputs

- `recommendations`
- `work_products`
- `review_points`

## Implementation Notes

Keep outputs reusable by pillar skills. Where the guidance depends on a specific offering, country, or release, capture that condition in the work product rather than hardcoding it in the generic shared method.

## Task sequencing

### Local bootstrap for new-project prevalidation

When `shared.validation.prevalidation` prepares any new implementation project,
from a plain-language request, selected tasks or an artifact, there is no
initialized workspace yet. Prepare intake, classification,
the resolver's ordered sequence and the resulting mapping in a private temporary
staging directory using local catalogs/graphs only. For this bootstrap only,
the persisted staged sequence satisfies step 1 below. All identity, completeness,
sequence and ambiguity gates still apply; this is not a default-sequence approval
or permission to discover tasks through Fusion before workspace initialization.
Pass the staged mapping to the initializer with `--no-create-runbook`. Immediately
persist and register the intake, scope, sequence, diagnostics and mapping under
the new project's normal artifact paths before generating its Run Book plan or
starting live validation. Remove staging after successful persistence; if
initialization fails, report the blocker and retain only safe recovery evidence.
Staging is not the durable project destination and must contain no Fusion exports,
credentials or tokens. Do not use `--force` or overwrite an existing project to
resolve a bootstrap conflict.

After validating the selected offering and functional-area contexts, invoke
`shared.implementation-planning.task-dependency-resolver` before persisting a
task map. When it succeeds, use its persisted `setup_task_sequence` as the
source of task order for the offering task map and every downstream Run Book
plan. Preserve the resolver's stable task identifiers, dependencies, context,
and diagnostic status.

Before writing `identified-task-mapping.json`, the agent must complete this
gate:

1. Read the persisted ordered `setup_task_sequence`. If it is absent, stop
   before writing the mapping or Run Book plan, except for an explicitly
   approved default sequence under the FSM/BOSS failure fallback below.
2. For each selected task, match its stable task identifier and offering and
   functional-area context to one task in the ordered sequence. Write a task
   mapping row only for a matched ordered task. Copy its resolved order exactly
   into `Resolver Sequence` and preserve its stable identifier, dependencies,
   context, sequence source, and diagnostic status. Do not derive `Resolver
   Sequence` from catalog `displaySequence`, task-list position, or mapping-row
   position.
3. Keep every pre-release or custom task diagnosed as `sequence_unresolved` out
   of the mapping's `tasks` array. Report its task code and reason separately
   in the resolver diagnostics. Do not give it a number to satisfy a requested
   task count.
4. Before handing the mapping to the project initializer, check that every
   mapping row has a unique positive `Resolver Sequence` copied from its
   matched ordered task and that no `sequence_unresolved` task is present.
   Report the selected, included, and excluded task counts. Stop if this check
   fails; do not generate a Run Book plan.

For an explicitly approved default sequence, copy its approved order into
`Resolver Sequence` and retain its `default-approved` source label.

If the resolver's FSM/BOSS task-discovery API fails, persist the diagnostic and
tell the user: `FSM-backed task sequence is unavailable right now.` Offer to
continue using the default task sequence. Do not select or persist that default
sequence unless the user explicitly accepts the offer; label an accepted
fallback as `default-approved` in the planning artifact and keep the FSM
diagnostic alongside it.
