---
skill_id: "cx.configure-price-quote.pricing"
name: "Pricing Implementation Guidance"
description: "Provides CX Configure Price Quote implementation guidance for the Pricing functional area."
layer: "pillar"
pillar: "CX"
offering: "Configure Price Quote"
functional_area: "Pricing"
functional_area_code: "CUSTOM_PRICING"
type: "planning"
execution_mode: "assisted"
owner_team: "CX configure price quote pillar team"
version: "0.1.8"
inputs:
  - "implementation_objective"
  - "project_context"
  - "pricing_scope"
  - "pricing_requirements"
  - "sync_direction_from_prompt"
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
  - "core.project-mgmt.project-workspace-initializer"
  - "core.runbook"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/pricing/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/pricing/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/pricing/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "CUSTOM_FUSION_PRICING_SYNC"
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

# Pricing Implementation Guidance

## Purpose

Provides CX Configure Price Quote implementation guidance for the Pricing functional area.

## When to Use

Use this functional-area skill after Configure Price Quote scope is confirmed and the project needs pricing setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `CX`
- Offering: `Configure Price Quote` (`ORA_CONFIGURE_PRICE_QUOTE`)
- Functional area / Setup Object: `Pricing` (`CUSTOM_PRICING`)

## Setup Tasks

1. [Fusion Pricing Sync](fusion-pricing-sync/SKILL.md) (`CUSTOM_FUSION_PRICING_SYNC`)

## Inputs

- `implementation_objective`
- `project_context`
- `pricing_scope`
- `pricing_requirements`
- `sync_direction_from_prompt`: source and target stated or inferred from the user's request; the child task validates the supported direction.

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

The only executable CPQ Pricing task skill here is
`fusion-pricing-sync/SKILL.md`. Route CPQ Pricing requests to set up pricing,
run or submit Fusion Pricing Sync, or sync pricing between Fusion and CPQ to
that skill. Detect source and target from the user's prompt before any live
workflow step, then apply the child skill's direction validation. The supported
direction is Fusion as source and CPQ as target. If the prompt omits direction,
recommend Fusion to CPQ. If it requests CPQ to Fusion, explain the mismatch
and offer Fusion to CPQ for the user's confirmation; do not silently reverse
the request. Users do not need to request DAT generation or Data Loader
initiation explicitly.
For a fresh implementation request, route project initialization and initial
Run Book creation through the implementation router and the core initializer /
Run Book workflow before invoking the child task's live loader steps. Include
CUSTOM_FUSION_PRICING_SYNC in the canonical task mapping, deliver the created
Run Book dashboard, then continue to DAT generation and validation. Reuse an
existing active Run Book with the exact sequenced task. The child task obtains
one Data Loader approval before upload; Run Book preparation does not replace it.
Track token usage for any generated project artifact or skill-run record using
the manifest policy.

The Pricing functional area routes setup wording to its runtime sync task.
Keep existing request phrases, including "Sync Fusion to CPQ" and "Setup Fusion
Pricing," as triggers for that task. The user-facing wording below changes the
response, not which prompts select the workflow.

This task does not call CPQ REST or poll a CPQ task status. Its only setup-data
execution route is the approved `CpqChargeSetSync` Data Loader import. It is a
trigger-only sync, so the workflow must not ask users for charge-set rows or
mapping data.
The registered pricing operation is POST with no business payload. The DAT
contains a loader trigger, with optional integer chargeId when generated, rather
than charge-set input rows. Keep REST routing for CpqChargeSetSync and use the
child task's explicit create-mode DAT workflow.

In user-facing progress and result messages, describe the work as "syncing Fusion
pricing reference data." Keep the supported Fusion-to-CPQ direction available
when it is needed to resolve or explain a source/target choice. Treat charge-set
terminology and `CpqChargeSetSync` as internal workflow details.
