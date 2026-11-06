---
skill_id: "core.project-mgmt.project-workspace-initializer"
name: "Project Workspace Initializer"
description: "Initializes the local project workspace, state file, artifact folders, and starting artifact index for a Fusion implementation project."
layer: "core"
pillar: "Core"
type: "planning"
execution_mode: "assisted"
owner_team: "Central platform team"
version: "0.1.2"
inputs:
  - "project_name"
  - "customer"
  - "implementation_objective"
  - "pillar"
  - "workspace_root"
  - "identified_task_mapping"
outputs:
  - "project_state"
  - "artifact_index"
  - "workspace_folder_structure"
  - "project_readme"
  - "identified_task_mapping"
  - "runbook_control"
uses_core: []
persists_project_state: true
state_updates:
  - "objective"
  - "skill_path"
  - "runbook_control"
workspace_outputs:
  - artifact_type: "objective"
    default_location: "project/{project_id}/artifacts/router/project-objective-classifier/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "other"
    default_location: "project/{project_id}/artifacts/shared/runbook/current/identified-task-mapping.json"
    versioning_policy: "major-new-version-minor-confirm-update"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "Creates local project workspace folders and initial state files."
required_privileges: []
---

# Project Workspace Initializer

## Purpose

Initializes the local project workspace, state file, artifact folders, and starting artifact index for a Fusion implementation project.

## When to Use

Use this skill before guided implementation work starts in a freshly cloned repository or when creating a new implementation project workspace.

## Inputs

- `project_name` (optional; defaults from the implementation objective)
- `customer`
- `implementation_objective`
- `pillar`
- `workspace_root`
- `identified_task_mapping` — required JSON file containing identified project tasks.

## Outputs

- `project_state`
- `artifact_index`
- `workspace_folder_structure`
- `project_readme`

## Implementation Notes

Create a project-specific workspace folder at `project/{project_id}/` from the tracked templates under `project/_template/`. When an implementation objective is available, derive a concise default project name and workspace ID from that objective; cap the generated project name at 50 characters. Use `draft-impl-project-<date>` only when no objective is available at creation time. Never write credentials into the workspace. Initialize `project/{project_id}/state/project-state.json`, `project/{project_id}/artifacts/artifact-index.json`, and the mirrored artifact root folders.

Use `scripts/initialize_project_workspace.py` to create workspaces deterministically from the template:

```bash
python3 core/project-mgmt/project-workspace-initializer/scripts/initialize_project_workspace.py \
  --project-name "Order Management Implementation" \
  --customer "Example Customer" \
  --implementation-objective "Implement Oracle Fusion Cloud Order Management" \
  --pillar SCM \
  --offering "Order Management" \
  --identified-task-mapping "path/to/identified-task-mapping.json" \
  --no-create-runbook
```

The script creates `project/{project_id}/README.md` with the local workspace ignore notice, seeds the objective artifact, writes the initializer run record, and updates the project state and artifact index. Every new implementation project must first pass the `shared.validation.prevalidation` run-or-skip checkpoint, including projects from plain-language requests without an attachment. The workspace template does not seed `runbook_control`; after the planning wrapper successfully persists all initial Run Book planning artifacts, it adds `runbook_control` with `status: pending`. Use `--no-create-runbook` to hold Oracle creation while that checkpoint is resolved. After accepted assessment or explicit skip, resume the originally authorized creation through `core.runbook` and persist its outcome. A separate user instruction to defer Run Book creation remains in force and requires a later explicit creation request.

## Project Initialization Completion Gate

### Prevalidation handoff for every new project

Route every new implementation project through `shared.validation.prevalidation`,
including plain-language requests and explicitly selected tasks. Honor the
requested name and accept the task-map builder's validated
local bootstrap mapping. Use `--no-create-runbook` to hold Oracle creation while
the local project, task mapping and planning artifacts are prepared. Persist the
staged source/scope/ordered-sequence evidence under the new workspace and index
it before invoking the planning wrapper. This hold is required by the selected
workflow even when the original request authorizes eventual Run Book creation.

Offer run or skip prevalidation through that skill before creating any Oracle
Run Book. An explicit run request already supplies the run choice. Resume the
original authorized creation workflow through `core.runbook` only after the
stage assessment is accepted or the user explicitly skips; a blocked assessment
alone is not a skip. This workflow-specific handoff is the exception to waiting
for a separate creation request after `--no-create-runbook`. An explicit user
instruction to defer Run Book creation still controls. All other initialization,
task-mapping and core Run Book gates remain in force.

Do not report project initialization complete until all required artifacts have been created and verified. Report the exact paths for:

- `state/project-state.json`
- `artifacts/artifact-index.json`
- `artifacts/shared/runbook/current/identified-task-mapping.json`
- `artifacts/shared/token-usage/current/token-usage-log.md`

A copied `project/_template` directory is not an initialized project, and an `.example.json` artifact cannot substitute for a required populated artifact. If required source data is missing, create a required artifact only with explicitly known values and mark unresolved fields as pending; otherwise stop and report the blocker. Run schema/JSON validation and `git diff --check` before handoff.

Before running the initializer, create or locate one valid JSON task mapping. `--identified-task-mapping` is mandatory for every initialization. The initializer rejects calls without it, persists the exact file at `artifacts/shared/runbook/current/identified-task-mapping.json`, and indexes it.

For every task row, identify `Offering`, `Pillar`, and `Functional Area` from the user-provided intent and data using `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json`. Use the task-and-offering combination; a task name alone is not sufficient. If more than one offering remains plausible, ask the user to provide the current offering for that task. Do not infer a replacement offering or create a separate offering-mapping artifact. Task-context creation records unmatched contexts and candidate offerings against the same catalog but continues with the supplied mapping so the user can correct it later.

## Task-Mapping Completeness

When the mapping is based on a user-supplied workbook, document, export, or catalog selection, preserve the complete matching task set eligible for the resolver's ordered `setup_task_sequence`. Do not condense, group, merge, omit, or infer eligible tasks in order to make the plan shorter. Copy each included task's resolved order into `Resolver Sequence`; do not use catalog display sequence or mapping-row position as a replacement. Keep pre-release and custom tasks diagnosed as `sequence_unresolved` out of the mapping's `tasks` array and report them separately. Each mapped task must retain a stable task identifier, the exact source reference (sheet and row, or equivalent source location), its requested phase, and the applicable FSCR skill path. Validate and report the source-match count before initialization; if the task count is ambiguous, the source cannot be read, or a complete match cannot be established, stop and report the gap rather than creating a partial mapping.

Before calling `scripts/create_project_runbook.py`, use the mapping produced
under the offering task-map builder's sequence gate. Do not add tasks to it or
fill missing `Resolver Sequence` values in the initializer. If that mapping is
absent or contains a `sequence_unresolved` pre-release or custom task, stop and
report the mapping gap; do not create a Run Book plan.

The generic `artifacts/shared/runbook/current/identified-task-mapping.json` location is the initializer's traceability input for the later Run Book workflow. When a user also requests an implementation-facing plan, persist that plan separately under the applicable project implementation artifact path (for example, `artifacts/{pillar}/{offering}/`) and index both artifacts.

For every initialization, the LLM must call `scripts/create_project_runbook.py --project-root project/{project_id} --refresh-artifacts` to generate and persist `setup-task-plan.json`, `task-context.json`, and `runbook-plan.json`. This script is planning-only and never creates or updates an Oracle Run Book. When `runbook_control` is absent, it adds `status: pending` only after all three artifacts are written. When control already exists, artifact generation and refresh leave the entire project-state file untouched, regardless of the Run Book status. Keep `status: pending` while the prevalidation choice or assessment is unresolved. Once accepted readiness or an explicit skip is registered for the same scope and environment, invoke `core.runbook` to resume the originally authorized Oracle Run Book creation, unless the user separately deferred it. A separate deferral requires a later explicit request; that request still does not waive the prevalidation checkpoint. Invoke creation and supply the absolute project workspace path to its `create-runbook --project-root` option. Only that creation command requires pending, unbound state. It persists the active reference and `status: active` on success, `status: failed` on a confirmed failure, or `status: unknown` on a partial or indeterminate creation. Both failure states block downstream Fusion submission and must not be retried automatically.

## Multi-Context Runbook Planning

A Run Book may contain tasks from multiple offerings, functional areas, or pillars. Preserve each task's catalog-resolved offering and functional area in the task mapping, setup-task plan, task context, and runbook plan. For a mixed-context plan, set the plan-level `offering` and `functional_area` to `Multiple Offerings` and `Multiple Functional Areas`; task-level values remain authoritative for task routing and Run Book grouping.

If the identified task mapping changes, regenerate the local planning artifacts with:

```bash
python3 core/project-mgmt/project-workspace-initializer/scripts/create_project_runbook.py \
  --project-root project/{project_id} \
  --refresh-artifacts
```

Refresh can regenerate the persisted setup-task plan, task context, and runbook plan before or after Oracle Run Book creation. It leaves the existing `runbook_control` state untouched and does not change the live Run Book.
