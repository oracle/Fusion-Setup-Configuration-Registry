---
skill_id: "erp.risk-and-security"
name: "Risk and Security"
description: "Coordinates ERP Risk and Security implementation guidance and routes work to developer-created functional-area skills."
layer: "pillar"
pillar: "ERP"
offering: "Risk and Security"
type: "orchestration"
execution_mode: "hybrid"
owner_team: "ERP Risk and Security pillar team"
version: "0.2.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "erp_scope"
  - "risk_and_security_requirements"
outputs:
  - "risk_and_security_scope"
  - "functional_area_skill_plan"
  - "risk_and_security_work_products"
  - "risk_and_security_prerequisite_result"
  - "runbook_lifecycle_result"
  - "token_usage_record"
depends_on:
  - "shared.project-intake.scope-definition"
  - "shared.implementation-planning.offering-task-map-builder"
  - "shared.implementation-planning.fsm-set-optin.fsm-set-optin-features"
  - "core.fusion-api.fsm-rest-client"
  - "core.runbook"
uses_core:
  - "core.fusion-api.fsm-rest-client"
  - "core.project-mgmt.project-state-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.artifact-version-manager"
  - "core.runbook"
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
  - "scope"
  - "skill_path"
  - "setup_task_sequence"
  - "design_decisions"
  - "configuration_blueprints"
  - "validation_results"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "scope"
    default_location: "project/{project_id}/artifacts/pillars/erp/risk-and-security/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "setup_task_sequence"
    default_location: "project/{project_id}/artifacts/pillars/erp/risk-and-security/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/erp/risk-and-security/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/risk-and-security/current/"
    versioning_policy: "append-only"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "Reads Core-managed FSM promotion-code and feature-choice evidence without changing Fusion setup."
  - "Writes redacted prerequisite evidence to the selected project workspace."
required_privileges:
  - "Read access to Fusion FSM promotion-code and feature metadata."
---

# Risk and Security

## Purpose

Coordinates ERP Risk and Security implementation guidance across functional areas, setup tasks, and standard implementation activities.

## When to Use

Use this offering-level skill after Risk and Security is in scope and before routing to a specific functional-area skill.

## Catalog Identity

- Pillar: `ERP`
- Pillar slug: `erp`
- Offering code: `ORA_RISK_AND_CONTROLS`
- Offering slug: `risk-and-security`
- Offering folder: `pillars/erp/risk-and-security`
- Offering mapping source: `knowledge/setup-task-catalog/effective/pillars-offerings-mapping.json`
- Setup task catalog source: `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json`

## Routing Responsibility

This skill routes control to functional-area skills created by developers under this folder. Developers should create functional-area skills with the approved catalog-backed pillar-skill generator using the catalog-backed path pattern:

```text
pillars/erp/risk-and-security/{functional-area-slug}/
```

When a requested functional area is not yet present under this offering, use the setup catalog below to identify the matching functional area and invoke the approved catalog-backed pillar-skill generator to generate the child skill before adding functional-area-specific guidance.

## Local Entry Path

Use this offering-level entry path to route the currently implemented Risk and
Security work. It coordinates the Run Book lifecycle for its selected setup
tasks; the durable workflow retains sequencing and approval state. Do not
invoke child implementation scripts directly.

1. [Assign Initial Users](assign-initial-users/SKILL.md)
2. [Activate Algorithms](activate-algorithms/SKILL.md)

## Run Book task lifecycle

For any selected project-backed leaf task under this offering, use the existing
`core.runbook` task-list and task-update flow after the offering prerequisite
and immediately before the functional-area parent starts the child. Resolve the
active Run Book from project state, then require exactly one task-context row
with the selected `skill_path` and task code and exactly one remote task with
its exact task name. An explicit consultant request to start, resume, or
continue that task authorizes this scoped status update.

For `Not Started`, update status to `in-progress` and require refreshed task
detail to report `In Progress`. Resume an already In Progress task without a
status update. To continue a completed task, reopen it and require `Not
Started`, then update status to `in-progress` and require `In Progress`. Never
infer a remote task from conversational text, and never change its percentage
or comments.

Do not enter a child preflight, preview, discovery, approval, or execution
phase until the lifecycle result confirms `In Progress`. If it fails, is
ambiguous, or is indeterminate, stop without starting the child and do not
retry its status update.

Each child returns `runbook_lifecycle_result` as one of `active`, `deferred`,
`completed_verified`, `completed_deferred`, or `blocked`. Update status to
`completed` only for `completed_verified` or `completed_deferred`; all other
results remain In Progress. Use the same exact mapping and require refreshed
task detail to report Completed. A completed task may be reopened only when the
consultant explicitly asks to continue that same task.

An explicit consultant request to defer the current task and move to a named
task, or to the next task, ends the current child with `deferred`. Persist its
task-local deferral evidence and outstanding work, leave its Run Book status
as In Progress, and route immediately to the selected task. The active local
workflow is the selected task; a deferred task is not active work even though
the Run Book displays it as In Progress.

For “next task,” choose the first later persisted Run Book task whose remote
status is neither Completed nor Not Applicable. For a named task, require one
unambiguous exact task-context match. Start or resume the selected task through
the normal exact-mapping lifecycle flow, then apply that task's own prerequisite,
validation, approval, and mutation gates. A task switch never bypasses those
gates.

When the consultant returns to an earlier task, first defer the currently
active task, then resume the requested task. Do not run two child workflows at
once or change the deferred task's Run Book percentage, comments, or status.

## Run Book status display

Treat a request to show Run Book task status, the task list, or current Risk
and Security task progress as a dashboard request. Return the complete
sanitized dashboard Markdown unchanged. Do not rebuild, condense, or wrap its
table: preserve the Run Book title, aggregate status sentence, functional-area
headings, and the `Sequence`, `Task`, `Status`, `% Completed`, and `Required`
columns.

Use task-list retrieval only for internal task resolution; never present its
raw or condensed output as a status view. For a requested task subset, use the
filtered dashboard flow so the same dashboard format is retained. Use the Run
Book summary only when the consultant explicitly asks for counts without task
rows.

## Required precondition

Before routing to a functional-area or nested task, complete the internal
Risk and Security setup prerequisite for the selected project and environment.
It is a read-only gate. The root offering skill delegates all Fusion retrieval
to the named Core and Shared skills; it does not call a REST or OAuth client.

1. Use `core.fusion-api.fsm-rest-client` and its `promo-code-feature`
   capability to produce the complete internal promotion-code export. Require
   at least one row where
   `SOLUTION_BUNDLE_CODE=ORA_GTG_SECURITY_ANALYSIS_PROMOTION_CODE` and
   `FEATURE_CODE=ORA_GTG_SECURITY_ANALYSIS`.
2. Use `shared.implementation-planning.fsm-set-optin.fsm-set-optin-features`
   with feature code `ORA_GTG_SECURITY_ANALYSIS`, offering code
   `ORA_RISK_AND_CONTROLS`, action `opt-in`, and `dry-run`. Require the exact
   feature and one selected `Yes` choice with `checkedFlag=true`.

Both conditions must pass. A missing, malformed, incomplete, or
environment-mismatched delegated result does not pass.

If the prerequisite passes, retain its redacted same-environment result and
continue without a consultant-facing technical update. Reuse that result only
within the active offering workflow. Repeat the check for a new workflow run,
an environment change, or an explicit restart.

If either required condition is not enabled, state: **“Risk and Security setup
is blocked until the Algorithms and Internal Controls promotion code is added
and ORA_GTG_SECURITY_ANALYSIS is enabled.”** If either condition cannot be
confirmed, state that setup readiness could not be confirmed, confirm that no
Risk and Security work was started, and give one administrator-facing next
action. Do not expose endpoints, artifacts, or internal status fields to
consultants.

A request that names a functional area or nested task directly is still a
Risk and Security offering request. Re-enter this prerequisite before any
child preflight, discovery, preview, or execution begins.

### Failure behavior

Fail closed and do not route a child when the prerequisite is blocked or
unconfirmed. Classify a missing project, environment, or completed delegated
artifact as `input_validation`; an absent promotion-code association or
unexpected feature identity as `catalog_or_metadata_mismatch`; and a malformed
or environment-mismatched result as `artifact_persistence`. Retain a redacted
validation result with its status, stage, failure class, business message, safe
next action, target environment, and artifact references.

Core FSM and Shared FSM skills own authentication, authorization, transport,
Fusion API, and timeout handling for their delegated reads. Follow their retry
contracts; this offering skill does not retry, substitute a data source, or
perform a live opt-in action. Do not retain or display credentials, tokens,
raw Core responses, request details, or full promotion-code exports.

## Execution discipline

Run one selected child workflow at a time. A request to run every available
step starts with **Assign Initial Users**; it does not authorize concurrent
discovery, preflight, or execution in **Activate Algorithms**.

Before entering the next child workflow, the active child must return
`completed_verified`, `completed_deferred`, or an explicit `deferred` handoff.
A `deferred` handoff permits only the requested task switch; it does not permit
concurrent work. A `blocked` result stops the workflow and cannot advance or
switch work until the consultant explicitly defers the current task.
When the active child is awaiting a consultant selection, confirmation, or
approval, present its required decision table and stop. Do not use time while
that decision is pending to run an otherwise independent read-only check in a
different child workflow.

An internal request plan, incomplete read-only collection, or interim Core
result is not a child-workflow terminal result. Continue the active child's
declared read-only batches and re-evaluate in the same workflow until its
decision table, completed result, or genuine blocker is ready. Do not return a
final consultant response merely because the next internal batch has been
prepared.

When the durable project workflow re-invokes a selected child, it may provide
the child-local [Phase Evidence Handoff](references/phase-evidence-handoff.md)
instead of repeating valid same-environment reads. The handoff is not routing
state: the router and durable workflow retain task selection, sequencing, and
pause/resume authority. It never bypasses a fresh mutation preflight, approval,
verification, or the child ordering above.

## Consultant interaction standard

Every child workflow that communicates with an implementation consultant must
follow the [Consultant Interaction Contract](references/consultant-interaction-contract.md).
Use business-labelled Markdown tables for review and approval; retain any
machine-readable evidence internally rather than asking the consultant to work
with it.

## Inputs

- `implementation_objective`
- `project_context`
- `erp_scope`
- `risk_and_security_requirements`

## Outputs

- `risk_and_security_scope`
- `functional_area_skill_plan`
- `risk_and_security_work_products`
- `risk_and_security_prerequisite_result`
- `token_usage_record`

## Functional Areas From Catalog

Source: `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json`
Offering code: `ORA_RISK_AND_CONTROLS`
Functional area count: `3`
Setup task count: `6`

- `ORA_GTG_RM_INITIAL_USERS`: Assign Initial Users
- `ORA_GTG_ACTIVATE_ALGORITHMS`: Activate Algorithms
- `ORA_GTG_ADD_OTHER_DATA_SOURCES`: Add Other Data Sources

## Implementation Notes

- Keep offering-level planning, scope decisions, sequencing, and cross-functional-area handoffs in this skill.
- Put functional-area-specific implementation guidance in generated child skills under this offering folder.
- Use the approved catalog-backed pillar-skill generator for child functional-area skill creation so generated skills follow the repository contract.
- Use the approved resource-authoring workflow after child skill creation when Oracle FusionApps `ora-resource/` guidance is needed.
- Do not create setup-task-specific skills directly under this offering folder unless the user explicitly requests nested task-level skill generation through the pillar skill generator.
