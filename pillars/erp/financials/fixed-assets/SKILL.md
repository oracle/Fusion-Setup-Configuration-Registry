---
skill_id: "erp.financials.fixed-assets"
name: "Fixed Assets Implementation Guidance"
description: "Provides ERP Financials implementation guidance for the Fixed Assets functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Fixed Assets"
functional_area_code: "FIN_FIXED_ASSETS_DEPLOYED"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.1.8"
inputs:
  - "implementation_objective"
  - "project_context"
  - "fixed_assets_scope"
  - "fixed_assets_requirements"
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
  - "core.data-loader"
  - "core.fusion-api.apps-common.lookups"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/fixed-assets/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/fixed-assets/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/fixed-assets/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "FA_MANAGE_FIXED_ASSETS_FLEXFIELD_VALUE_SETS"
  - "FA_MANAGE_FIXED_ASSETS_KEY_FLEXFIELDS"
  - "FA_MANAGE_SYSTEM_CONTROL"
  - "FA_MANAGE_FISCAL_YEAR"
  - "FA_MANAGE_CALENDAR"
  - "FA_MANAGE_PRORATE_CONVENTION"
  - "FA_MANAGE_ASSET_BOOK"
  - "FA_MANAGE_ASSET_CATEGORY"
  - "FA_MANAGE_ASSET_KEY"
  - "FA_MANAGE_FIXED_ASSET_LOCATION"
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

# Fixed Assets Implementation Guidance

## Purpose

Provides ERP Financials implementation guidance for the Fixed Assets functional area.

## When to Use

Use this functional-area skill after Financials scope is confirmed and the project needs fixed assets setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `ERP`
- Offering: `Financials` (`XLE_FINANCIALS_JUR`)
- Functional area / Setup Object: `Fixed Assets` (`FIN_FIXED_ASSETS_DEPLOYED`)

Select tasks from the requested scope and resolve their prerequisites and order
through `shared.implementation-planning.task-dependency-resolver` and each child
task's `ora-resource/ora_dependency_readiness.md`. The generated task index below
is not an execution sequence or a requirement to run every task. Verify existing
prerequisites and route missing setup through its owning task's approval workflow.

## Setup Tasks

1. [Manage Fixed Assets Flexfield Value Sets](manage-fixed-assets-flexfield-value-sets/SKILL.md) (`FA_MANAGE_FIXED_ASSETS_FLEXFIELD_VALUE_SETS`)
2. [Manage Fixed Assets Key Flexfields](manage-fixed-assets-key-flexfields/SKILL.md) (`FA_MANAGE_FIXED_ASSETS_KEY_FLEXFIELDS`)
3. [Manage System Controls](manage-system-controls/SKILL.md) (`FA_MANAGE_SYSTEM_CONTROL`)
4. [Manage Fiscal Years](manage-fiscal-years/SKILL.md) (`FA_MANAGE_FISCAL_YEAR`)
5. [Manage Asset Calendars](manage-asset-calendars/SKILL.md) (`FA_MANAGE_CALENDAR`)
6. [Manage Prorate Conventions](manage-prorate-conventions/SKILL.md) (`FA_MANAGE_PRORATE_CONVENTION`)
7. [Manage Asset Books](manage-asset-books/SKILL.md) (`FA_MANAGE_ASSET_BOOK`)
8. [Manage Asset Categories](manage-asset-categories/SKILL.md) (`FA_MANAGE_ASSET_CATEGORY`)
9. [Manage Asset Keys](manage-asset-keys/SKILL.md) (`FA_MANAGE_ASSET_KEY`)
10. [Manage Asset Locations](manage-asset-locations/SKILL.md) (`FA_MANAGE_FIXED_ASSET_LOCATION`)


## Inputs

- `implementation_objective`
- `project_context`
- `fixed_assets_scope`
- `fixed_assets_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Track token usage for generated project artifacts and skill-run records using the manifest policy.

Use the generated nested setup-task skills for task-level planning, sequencing, setup-data routing, and validation.

## Shared Fixed Assets Preview and Approval Gates

Every Fixed Assets child skill must show each applicable named preview in the
active chat. A child may add task-specific checks but must not skip, weaken, or
repeat these shared gates. A preview records evidence; it does not replace
validation, approval, import status, or target-state verification.

Render the complete applicable preview as the user-facing message in the active
chat. A project artifact may retain the same preview for audit and continuity,
but it is never a substitute for that inline rendering: do not provide only a
file link, ask the user to open an artifact, or describe an artifact in place
of the preview. Persisting an artifact must not delay or suppress the chat
preview.

In every preview, omit fields marked `Internal: Yes`. State only whether the
technical check passed or is unresolved; use internal values only for package
preparation and validation.

| Gate | Required chat preview | Requirement |
|---|---|---|
| Input validation | `Input Preview` | Show the target, requested scope, and supplied business values before live lookup or package work. |
| Reference and readiness | `Reference Validation Preview` | Show resolved business identities, prerequisites, and any unresolved or ambiguous business value. |
| Design and defaults | `Design Preview` | Before ZIP creation, show resolved non-internal defaults and obtain approval to create the ZIP. This does not approve submission. |
| Final ZIP or artifact review | `Final ZIP Preview` for ZIPs; `Final Artifact Preview` otherwise | After creation, validate and show the final reviewed artifact, including its scope and content hash. |
| Execution approval | `Execution Approval Preview` | Obtain separate approval for the exact target, operation, final reviewed artifact, and hash. |
| Post-execution verification | `Post-Execution Verification Preview` | Show terminal status and fresh target-state read-back before claiming completion or starting dependent-task work. |

Do not create a ZIP before design approval. Do not submit it before final ZIP
review and execution approval. If its contents change, repeat the final review
and execution approval. An approval never transfers to another artifact,
environment, or operation.

## CSV Encoding Fidelity

For every Fixed Assets FSM ZIP, preserve the exact CSV encoding contract of the
current same-task FSM export. Before creating the archive, compare each
generated CSV's header bytes with its corresponding export member. If the
export is UTF-8 without a byte-order mark (BOM), generate UTF-8 without a BOM;
do not use an exporter that prefixes `EF BB BF`. A BOM changes the first header
name and can make Fusion report missing headers even when the visible text
matches. Reject the archive before review or submission when a generated CSV
has a different BOM state or header bytes from the export.

## Import Scope

Construct every import from the approved request: include only requested changes
and supporting records required by the import contract. Use reference exports
to resolve data and package structure. Preserve required files, headers,
encoding, and metadata; files with no requested records remain header-only.
Verify the final contents and row counts against the approved scope before
submission.

Do not ask for approval during task discovery, reference lookups, or validation. Package-creation and ZIP-submission approvals are governed by the Shared Fixed Assets Preview and Approval Gates above; an approval for one final reviewed ZIP cannot be applied to another ZIP.

## Post-Submission Status Tracking

After an FSM submission is accepted, the Fixed Assets parent retains the
request context and reports `accepted — pending parent verification`.
`core.data-loader` performs the routed status and ProcessLog retrieval; the
parent applies the child-supplied target-state criteria and shows the
`Post-Execution Verification Preview`. A child task must not claim completion,
poll, or perform post-import verification itself. Dependent tasks may reuse
only parent-verified context.
