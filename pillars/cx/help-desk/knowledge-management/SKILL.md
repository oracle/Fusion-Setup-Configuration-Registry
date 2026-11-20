---
skill_id: "cx.help-desk.knowledge-management"
name: "Knowledge Management Implementation Guidance"
description: "Provides CX Help Desk implementation guidance for the Knowledge Management functional area."
layer: "pillar"
pillar: "CX"
offering: "Help Desk"
functional_area: "Knowledge Management"
functional_area_code: "ORA_CSO_KNOWLEDGE_MANAGEMENT"
type: "planning"
execution_mode: "assisted"
owner_team: "CX help desk pillar team"
version: "0.1.1"
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
  - "cx.service.knowledge-management"
  - "shared.implementation-planning.offering-task-map-builder"
  - "shared.implementation-planning.task-dependency-resolver"
  - "shared.setup-export.functional-area-export"
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "cx.service.knowledge-management.manage-knowledge-content-types-redwood"
uses_core:
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
  - "core.diagnostics.role-access-check"
  - "core.auth.fusion-oauth-authentication"
  - "core.data-loader"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/knowledge-management/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/knowledge-management/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/help-desk/knowledge-management/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_CSO_LOCALES_MGMT"
  - "ORA_MANAGE_KNOWLEDGE_WORKFLOWS"
  - "ORA_CSO_CONTENT_TYPES_MGMT"
  - "ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT"
  - "ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT"
  - "ORA_CSO_USER_GROUPS_MGMT"
  - "ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS"
  - "ORA_CSO_CONTENT_TYPES_INDEXING_MGMT_REDWOOD"
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

Provides CX Help Desk implementation guidance for the Knowledge Management functional area.

## When to Use

Use this functional-area skill after Help Desk scope is confirmed and the project needs knowledge management setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `CX`
- Offering: `Help Desk` (`ORA_SVC_HELP_DESK`)
- Functional area / Setup Object: `Knowledge Management` (`ORA_CSO_KNOWLEDGE_MANAGEMENT`)

## Setup Tasks

1. [Manage Knowledge Locales](manage-knowledge-locales.md) (`ORA_CSO_LOCALES_MGMT`)
2. [Manage Knowledge Workflows](manage-knowledge-workflows.md) (`ORA_MANAGE_KNOWLEDGE_WORKFLOWS`)
3. [Manage Knowledge Content Types Classic](manage-knowledge-content-types-classic.md) (`ORA_CSO_CONTENT_TYPES_MGMT`)
4. [Manage Knowledge Panel Profile Options](manage-knowledge-panel-profile-options.md) (`ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT`)
5. [Manage My Knowledge Profile Options](manage-my-knowledge-profile-options.md) (`ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT`)
6. [Manage Knowledge User Groups](manage-knowledge-user-groups.md) (`ORA_CSO_USER_GROUPS_MGMT`)
7. [Manage Knowledge for Service Requests with Redwood User Interface Profile Options](manage-knowledge-for-service-requests-with-redwood-user-interface-profile-options.md) (`ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS`)
8. [Manage Knowledge Content Types Redwood](manage-knowledge-content-types-redwood.md) (`ORA_CSO_CONTENT_TYPES_INDEXING_MGMT_REDWOOD`)

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

Use the flat task files only for catalog identity and routing. This functional-area skill owns the Help Desk handoff below; Service owns the reused domain workflows and field contracts. Track token usage for project artifacts and skill runs using the manifest policy.

## Help Desk Task Handoff

Apply this handoff for every task entry, including direct invocations of a flat
metadata file. Read this section before following its Service target. Flat task
files contain no independent FSM field contract or execution workflow.

1. Consume the existing project objective, scope and approved decisions. Resolve
   the exact Help Desk task code from its flat metadata and effective catalog;
   stop on an ambiguous identity, unsupported operation or missing guidance.
2. Retain offering `Help Desk` (`ORA_SVC_HELP_DESK`), functional area
   `ORA_CSO_KNOWLEDGE_MANAGEMENT`, the requested task code, environment,
   project ID, approved operation and source artifact in the handoff context.
   Identify the approved HR Help Desk or Internal Service Requests scope when
   relevant. Never default to the Service offering, copy a CRM stripe, or
   substitute Service project output paths merely because guidance is reused.
3. Load the exact Service task linked by the flat file and every applicable
   resource in the mandatory resource table below. Select rules by task code,
   not by a similarly named task. For Classic content types, return an assisted `redirect_required` handoff
   to the nested Redwood task. This is a routing instruction, not a core resolver status.
   Stop Classic setup-data preparation and preview.
   Preserve the original context and Run Book binding; the active router/Run Book
   workflow must select or plan and merge Redwood as a separate task and establish
   its own task context, binding and approval before validation or execution.
   Never rewrite Classic identity or reuse its approval for Redwood.
4. Apply the Service task's domain preconditions, input validation, reference
   resolution, dependency readiness, defaulting and design enforcement before
   package preparation or preview. Reconcile its entire FSM contract against
   a completed export of the same task from the selected Help Desk environment.
   Preserve all required root, child and localized objects and exact parent
   linkages. Do not infer offering-specific object names or fill unresolved
   fields from another task. A mismatch is a blocker requiring source evidence.
5. Delegate an export only to `shared.setup-export.task-level-export` after
   its active workflow checks pass. Use `shared.validation.setup-data-validator`
   for package validation in addition to the domain gates. Delegate every
   import to `core.data-loader`; its immutable-artifact, Task Hook validation
   and approval workflow is authoritative. Carry the Help Desk context into
   that workflow and require the applicable domain rules to be evaluated;
   missing rule selection must not silently turn these gates into optional
   checks. Do not directly invoke an API, adapter, Task Validator or import
   utility. This guidance does not authorize any live operation.
6. Preserve diagnostics and partial successes in the Help Desk project workspace.
   Register outputs and record the skill run and token usage through the
   declared project services. Link the selected guidance, rule results, source
   provenance, exact target context and any approved loader artifact. Reuse of
   Service guidance must not create a second Service project artifact tree.

### Mandatory Service Resources

Paths below are relative to the repository root. Load every listed file, then
apply the rows for the resolved task and requested operation. The selected task
may impose additional resources; follow those references as well.

| Task route | Required resource directory | Files to load |
| --- | --- | --- |
| Locales, workflows, user groups and profile options | `pillars/cx/service/knowledge-management/ora-resource/` | `ora_input_validation.md`, `ora_reference_lookups.md`, `ora_dependency_readiness.md`, `ora_defaulting_rules.md`, `ora_design_enforcement.md`, `ora_error_handling.md` |
| Classic and Redwood content types | `pillars/cx/service/knowledge-management/manage-knowledge-content-types-redwood/ora-resource/` | `ora_input_validation.md`, `ora_reference_lookups.md`, `ora_dependency_readiness.md`, `ora_defaulting_rules.md`, `ora_design_enforcement.md`, `ora_error_handling.md` |

For locales, the inherited gates require an active selected default and prevent
disabling the current default without a verified replacement. For workflows,
verify activity/outcome enablement, content types and approver access, then
reconcile all four workflow CSV objects and the separate content-type linkage.
These are repository domain gates; the linked Service resources define their
complete behavior and evidence requirements.

### Missing Guidance and Failure Handling

This package includes only the eight tasks listed in its Setup Tasks index,
each with an exact Service guidance target. Other effective-catalog Knowledge
Management tasks are outside this package scope. Their catalog records remain
unchanged. Stop an out-of-scope request before package preparation, export,
preview, import or alternate execution; record a `catalog_or_metadata_mismatch`
diagnostic and request task-specific guidance through the active workflow.
Do not substitute a similarly named task or infer an FSM or REST contract.

Classify missing inputs as `input_validation`, access failures separately from
expired authentication, and source/contract mismatches as
`catalog_or_metadata_mismatch`. Delegate bounded authentication recovery,
transport handling, polling timeouts and failed-job diagnostics to the selected
core/shared workflow. Never retry a live import automatically. Stop on a failed
domain gate, unsafe path, overwrite conflict or unresolved context. Preserve
sanitized diagnostics and process IDs; redact tokens, secrets and sensitive
payloads. Data Loader owns approval for the exact import artifact; do not add
a duplicate approval gate.

### Validation Scenarios

| Synthetic request | Required result |
| --- | --- |
| Set an inactive locale as the default | Block before preview under inherited locale validation. |
| Disable the current default without a verified active replacement | Block before preview; preserve the current default. |
| Update a workflow without verified outcome/approver prerequisites | Block before package preparation. |
| Prepare a workflow package with only root and step CSVs | Block until required localized objects and linkages reconcile with the same-task contract. |
| Reuse Service guidance with Help Desk scope | Retain Help Desk offering, environment, stripe evidence and project paths; reject any unresolved context substitution. |
| Request a task outside the eight-task package scope | Record the unsupported scope; prepare no package or live operation. |
| Route Classic content type configuration | Follow the exact Service Classic-to-Redwood handoff; load nested task resources. |

## Source Boundaries

Repository contracts and domain gates are reused from the linked Service tasks;
no copied field names in this Help Desk package establish Oracle runtime behavior.
The [current Oracle Help Desk guidance](https://docs.oracle.com/en/cloud/saas/fusion-service/farhd/implement-knowledge-for-help-desk.html)
delegates Knowledge setup to the Knowledge Management guide and calls for Help
Desk roles. The [Oracle release index](https://docs.oracle.com/en/cloud/saas/fusion-service/cloud-readiness-whats-new.html)
identifies Help Desk 26D as latest (checked 2026-10-20). The current topic is
unversioned and does not document the FSM field contract. Accordingly, treating
Service guidance as a reusable starting point is an implementation decision;
actual Help Desk package compatibility requires same-task evidence and the
active workflow checks. No older release field contract is substituted.
