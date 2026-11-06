---
skill_id: "router.next-action-planner"
name: "Next Action Planner"
description: "Determines the next recommended skill or human action based on workflow state, dependencies, and readiness."
layer: "router"
pillar: "Router"
type: "orchestration"
execution_mode: "hybrid"
owner_team: "Central architecture or platform team"
version: "0.1.1"
inputs: 
  - "objective_classification"
  - "workflow_state"
  - "dependency_graph"
  - "validation_results"
outputs: 
  - "next_action_plan"
  - "recommended_skill_ids"
  - "human_review_points"
  - "token_usage_record"
depends_on:
  - "router.project-objective-classifier"
uses_core: []
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

# Next Action Planner

## Purpose

Determines the next recommended skill or human action based on workflow state, dependencies, and readiness.

## When to Use

Use this router skill at the start of an implementation workflow or whenever the current workflow state must be reclassified, resequenced, or routed to the next responsible skill.

## Inputs

- `objective_classification`
- `workflow_state`
- `dependency_graph`
- `validation_results`

## Outputs

- `next_action_plan`
- `recommended_skill_ids`
- `human_review_points`

## Implementation Notes

Keep routing decisions explainable. Persist the selected skill IDs, confidence, assumptions, and human review points so downstream skills can continue from the same context.

## Preflight, failure and redaction

Before proposing an action, confirm the objective classification, selected
project/scope, current workflow-state evidence, dependency results and the
availability of the proposed skill. Distinguish a recommendation from an
approved or executed action. Preserve pending, skipped and uncertain states;
never infer completion, approval or fresh evidence from elapsed time.

For missing or conflicting inputs, report `input_validation` or
`catalog_or_metadata_mismatch` with the affected prerequisite, owner and next
action. Keep an unavailable approval as `approval_blocker`. Stop dependent
routing until that condition is resolved. Follow
[error handling guidance](../../governance/error-handling-guidelines.md) and
preserve the owning workflow's failure classification and partial outcomes;
this planner does not retry operations, acquire credentials or substitute a
live execution route.

Hand durable next-action decisions, sanitized diagnostic references and the
declared token estimate to the selected project's owning workflow for
persistence through its project services. When no project is selected, return
that limitation and the appropriate project-resolution step. Redact credentials, tokens,
secrets and sensitive customer values. Keep safe evidence references and
accountable owners instead of raw payloads or reusable approval objects.

## Validation Next Actions

Read [the common validation workflow](../../shared/validation/references/validation-workflow.md)
for validation results. Select next actions from evidence, not task completion:

- Missing requirement coverage or unverified setup: recommend
  `shared.validation.configuration-completeness-validator` and the responsible
  pillar/implementer action.
- Review complete: offer relevant transactional checks or SVFs as optional next
  actions through `shared.validation.transactional-validation-coordinator`.
  Never schedule run-all, automatic creation, or chained tests.
- User asks for HTML/evidence only: select
  `shared.validation.implementation-summary-and-evidence`; do not refresh live
  state or execute tests implicitly.
- FAIL/BLOCKED: assign corrective work to its owning setup or pillar workflow;
  do not repair it inside validation.
- INDETERMINATE: reconcile the previous request before proposing another live
  attempt. Pending/failed cleanup remains a separate owned action.
- SKIPPED/NOT_RUN: retain unverified scope. An accepted gap is a referenced
  decision, not PASS or permission to bypass an execution prerequisite.

Do not mark a project complete from stage-scoped readiness. The project owner
makes the progression/release decision against agreed required checks.
