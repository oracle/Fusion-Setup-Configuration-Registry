---
skill_id: "cx.sales.opportunities"
name: "Opportunities Implementation Guidance"
description: "Provides CX Sales Opportunities implementation guidance, routes profile-option inventory/current-value/Set requests to the exact task with its export-omission or export-failure Apps Common fallback, and routes set-enabled lookup tasks through their catalog identity and declared FSM adapter."
layer: "pillar"
pillar: "CX"
offering: "Sales"
functional_area: "Opportunities"
functional_area_code: "ORA_MOO_OPPORTUNITIES"
type: "planning"
execution_mode: "assisted"
owner_team: "CX sales pillar team"
version: "0.12.4"
inputs:
  - "implementation_objective"
  - "project_context"
  - "opportunities_scope"
  - "opportunities_requirements"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/sales/opportunities/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/sales/opportunities/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/sales/opportunities/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "MOO_MANAGE_SALES_METHODS_AND_SALES_STAGES"
  - "MOO_MANAGE_SALES_STATUS"
  - "MOO_MANAGE_SALES_STATUS_CATEGORY_MAPPINGS"
  - "MOO_MANAGE_SALES_STAGE_PHASE_CODES"
  - "MOO_MANAGE_OPPORTUNITY_PROFILE_OPTIONS"
  - "MOO_MANAGE_REVENUE_CATEGORIES"
  - "ZBS_MANAGE_SALES_TASK_TEMPLATE"
  - "FND_MANAGE_SET_ENABLED_LOOKUPS"
  - "MOO_MANAGE_LEVELS_OF_RISK"
  - "MOO_MANAGE_STRATEGIC_VALUES"
  - "MOO_MANAGE_DECISION_LEVELS"
  - "MOO_MANAGE_DEAL_HORIZONS"
  - "MOO_MANAGE_WIN/LOSS_REASONS"
  - "MOO_MANAGE_REVENUE_TYPES"
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

# Opportunities Implementation Guidance

## FSM Task Identity Policy

Require the exact catalog task code/name, selected child `SKILL.md`,
child-declared FSM execution task code/name, target environment, and, when an
archive is involved, immutable archive SHA-256 throughout review, export,
package preparation, and validation.
The catalog and execution identities are normally the same. Preserve both when
a child declares a transport exception.

- Review, export, and package preparation do not require Data Loader task context.
- Every Core Data Loader mutation handoff requires a persisted project
  `TaskContextPath`, exact `TaskName`, and positive `TaskSequence`.
- The selected context entry must resolve to the exact child skill path,
  catalog `TaskCode`, catalog `TaskName`, offering, and functional area. The
  package metadata must independently resolve to the child-declared FSM
  execution task identity.

The persisted context may be generated from the project's resolved setup-task
plan without creating an Oracle Run Book. Never hand-author, infer, or
synthesize a context entry merely to satisfy Data Loader. Each selected child
must enforce this contract before its FSM mutation handoff. A child-declared
REST fallback binds its own immutable preview and does not require a Data Loader
task context or import package.

## Purpose

Provide CX Sales implementation guidance for the Opportunities functional area
and route opportunity quoting or Sales-side Oracle CPQ setup to the canonical
integration skill.

## When to Use

Use this functional-area skill after Sales scope is confirmed and the project needs opportunities setup planning, baseline export, import sequencing, validation checkpoints, or opportunity quoting integration with Oracle CPQ.

## Catalog Metadata

- Pillar: `CX`
- Offering: `Sales` (`ORA_MIDSIZE_SALES`)
- Functional area / Setup Object: `Opportunities` (`ORA_MOO_OPPORTUNITIES`)

## Setup Task Scope

This inventory lists the setup tasks currently generated and maintained as
children of this skill; it is not a claim that every task in the Opportunities
catalog has a child artifact. Resolve additional catalog tasks through the
implementation router and generate a child only when that task enters project
scope. In particular, the Opportunity and Revenue record-set tasks remain
explicit prerequisites here rather than lookup-code maintenance children.

## Setup Tasks

1. [Manage Sales Methods and Sales Stages](manage-sales-methods-and-sales-stages/SKILL.md) (`MOO_MANAGE_SALES_METHODS_AND_SALES_STAGES`)
2. [Manage Sales Status](manage-sales-status/SKILL.md) (`MOO_MANAGE_SALES_STATUS`)
3. [Manage Sales Status Category Mappings](manage-sales-status-category-mappings/SKILL.md) (`MOO_MANAGE_SALES_STATUS_CATEGORY_MAPPINGS`)
4. [Manage Sales Stage Phase Codes](manage-sales-stage-phase-codes/SKILL.md) (`MOO_MANAGE_SALES_STAGE_PHASE_CODES`)
5. [Manage Opportunity Profile Options](manage-opportunity-profile-options/SKILL.md) (`MOO_MANAGE_OPPORTUNITY_PROFILE_OPTIONS`)
6. [Manage Opportunity Revenue Categories](manage-opportunity-revenue-categories/SKILL.md) (`MOO_MANAGE_REVENUE_CATEGORIES`)
7. [Manage Sales Task Templates](manage-sales-task-templates/SKILL.md) (`ZBS_MANAGE_SALES_TASK_TEMPLATE`)
8. [Manage Set Enabled Lookups](manage-set-enabled-lookups/SKILL.md) (`FND_MANAGE_SET_ENABLED_LOOKUPS`)
9. [Manage Levels of Risk](manage-levels-of-risk/SKILL.md) (`MOO_MANAGE_LEVELS_OF_RISK`)
10. [Manage Strategic Values](manage-strategic-values/SKILL.md) (`MOO_MANAGE_STRATEGIC_VALUES`)
11. [Manage Decision Levels](manage-decision-levels/SKILL.md) (`MOO_MANAGE_DECISION_LEVELS`)
12. [Manage Deal Horizons](manage-deal-horizons/SKILL.md) (`MOO_MANAGE_DEAL_HORIZONS`)
13. [Manage Win/Loss Reasons](manage-win-loss-reasons/SKILL.md) (`MOO_MANAGE_WIN/LOSS_REASONS`)
14. [Manage Opportunity Revenue Types](manage-opportunity-revenue-types/SKILL.md) (`MOO_MANAGE_REVENUE_TYPES`)

## Profile Option Routing

Route requests to list Opportunity profile options, return current/latest or
configured environment values, review one exact profile-option code, or set
profile-option values to
[Manage Opportunity Profile Options](manage-opportunity-profile-options/SKILL.md).
This includes a short follow-up such as "check the latest value" when the
immediately preceding context contains exactly one unambiguous profile-option
code. Do not answer a current-value request from Oracle documentation,
delivered defaults, or the FSM export alone.
Exact-code Review uses the child-declared Apps Common GET workflow directly;
do not require a setup-data export, export approval, archive SHA-256, or Data
Loader context to read one option. A new export is a separate POST operation
with its own approval gate, not a prerequisite for exact-code Review.
The child selects FSM for exported existing Site/User values. When its complete
successful export omits the requested option and the exact live definition
resolves, it selects its declared Apps Common Site/Product/User POST/PATCH
fallback, including Create when the selected live child is absent. A classified
failed exact-task export also continues to Apps Common reads; an existing exact
live child selects PATCH after preview and approval, while absence blocks the
update. Missing value rows for successfully exported options do not select REST.

## Set ID Selection Policy

For every Opportunity setup request that requires a reference-data set, treat
set selection as an explicit user decision. Never assign or infer the Common
Set merely because `SetId`, `SetCode`, or another set selector is absent.

When the request does not identify a set, stop the set-dependent path and ask
whether the Common Set should be used or a different set should be selected.
If the user chooses a different set, require its exact Set ID or Set Code, or a
business-unit/organization selector that the task's documented read-only
resolver can map to exactly one set. If the user confirms Common Set, resolve
its current environment identity rather than hard-coding a numeric Set ID.
Preserve the confirmed set choice in every review draft, package row, preview,
handoff, and verification artifact. Common Set confirmation is a scope choice;
it is not approval for a Fusion mutation.

## Negative Scenario Policy

Fail closed on identity errors; never repair them by choosing a close match,
reusing a value from another environment, or silently changing request scope.

| Negative scenario | Required behavior |
|---|---|
| Unknown, misspelled, or wrong Opportunity profile-option code | Return not found for the exact case-sensitive code and ask for a valid code; do not substitute a display-name match, delivered default, or similar code |
| Profile-option code and display name identify different options, or prior-turn context contains zero or multiple codes | Block and request one exact profile-option code; do not inherit ambiguous context |
| Profile-option target has an unsupported level, missing existing exported row on the FSM route, or invalid stored value | Block the selected route and show exact evidence; confirmed definition omission or classified exact-task export failure can select the child's REST fallback; the latter requires an existing live value |
| Set ID or Set Code is malformed, absent after a different-set choice, not found in the selected environment, or resolves to multiple/conflicting identities | Stop before lookup, draft completion, package preparation, or preview and request one valid exact set identity |
| Supplied Set ID and Set Code resolve to different sets, or a confirmed Common Set choice resolves to a non-Common set | Reject the combination and ask the user to reconfirm Common Set or provide one different exact set |
| Business-unit/organization assignment belongs to another reference group or set | Block the task and report the exact record-set prerequisite; never reassign it through an Opportunity child skill |
| A package row's set differs from its confirmed or export-derived set identity | Reject the package as an identity/scope mismatch; do not rewrite the row to make validation pass |

## Set-Enabled Lookup Coordination

Use one common set-enabled lookup workflow while preserving the exact catalog
task identity required by project task context and the exact execution identity
required by FSM export/import package metadata. The six named tasks route to
lightweight task adapters; each adapter fixes its lookup type, catalog identity,
FSM execution identity, record-set prerequisite, and task-local rule registry.

| Setup task | Lookup type | Routed child skill | Catalog task code | FSM execution task code | Record-set prerequisite |
|---|---|---|---|---|---|
| Manage Levels of Risk | MOO_SETID_RISK_LEVEL | [manage-levels-of-risk](manage-levels-of-risk/SKILL.md) | MOO_MANAGE_LEVELS_OF_RISK | MOO_MANAGE_LEVELS_OF_RISK | ORA_MOO_MANAGE_OPPORTUNITY_RECORD_SET_VALUES |
| Manage Strategic Values | MOO_SETID_STRATEGIC_VALUE | [manage-strategic-values](manage-strategic-values/SKILL.md) | MOO_MANAGE_STRATEGIC_VALUES | MOO_MANAGE_STRATEGIC_VALUES | ORA_MOO_MANAGE_OPPORTUNITY_RECORD_SET_VALUES |
| Manage Decision Levels | MOO_SETID_DECISION_LEVEL | [manage-decision-levels](manage-decision-levels/SKILL.md) | MOO_MANAGE_DECISION_LEVELS | MOO_MANAGE_DECISION_LEVELS | ORA_MOO_MANAGE_OPPORTUNITY_RECORD_SET_VALUES |
| Manage Deal Horizons | MOO_SETID_DEAL_HORIZION | [manage-deal-horizons](manage-deal-horizons/SKILL.md) | MOO_MANAGE_DEAL_HORIZONS | MOO_MANAGE_DEAL_HORIZONS | ORA_MOO_MANAGE_OPPORTUNITY_RECORD_SET_VALUES |
| Manage Win/Loss Reasons | MOO_SETID_WIN_LOSS_REASON | [manage-win-loss-reasons](manage-win-loss-reasons/SKILL.md) | MOO_MANAGE_WIN/LOSS_REASONS | FND_MANAGE_SET_ENABLED_LOOKUPS | ORA_MOO_MANAGE_OPPORTUNITY_RECORD_SET_VALUES |
| Manage Opportunity Revenue Types | MOO_SETID_REVENUE_TYPE | [manage-opportunity-revenue-types](manage-opportunity-revenue-types/SKILL.md) | MOO_MANAGE_REVENUE_TYPES | MOO_MANAGE_REVENUE_TYPES | ORA_MOO_MANAGE_REVENUE_RECORD_SET_VALUES |

[Manage Set Enabled Lookups](manage-set-enabled-lookups/SKILL.md) defines the
common Opportunity workflow and owns the `FND_MANAGE_SET_ENABLED_LOOKUPS`
catalog identity and rule graph only for Opportunity Assessment Override
Reasons (`MOO_SETID_ASSESS_OVRRIDE_RSN`) and explicitly requested set-enabled
Sales Revenue Categories (`MOO_SETID_REVN_CATEGORY`). Manage Win/Loss Reasons
is the sole transport exception in this table: its child retains the catalog
identity `MOO_MANAGE_WIN/LOSS_REASONS` and its own lookup scope and rule graph,
but exports and imports the `FND_MANAGE_SET_ENABLED_LOOKUPS` package because the
catalog code contains `/`. Do not substitute the FND execution task for any of
the other five named tasks.

Every adapter resolves the exact reference group and reference data set. When
the request is business-unit scoped, it also verifies the returned record-set
assignment as a read-only prerequisite; it never assumes that the lookup type
is the assignment reference group and does not manage Opportunity or Revenue
Record Set Values.

Do not route Sales Status, Sales Stage Phase Codes, standard MOO_REVN_CATEGORY
maintenance, sales methods and stages, or status-category mappings through
this coordinator.

## Task Ownership

Use this parent only for functional-area selection and cross-task sequencing.
After selecting a setup task, load its nested `SKILL.md` and task-local
`ora-resource/` graph. The child skill owns its required inputs, source rules,
review draft, route-specific pre-handoff gate, diagnostics, retry boundary, and
verification. It owns the immutable preview and approval only for a documented
direct REST route; Core Data Loader owns those artifacts for FSM. Do not
duplicate or override either contract in this parent.

## Runtime Interface and Handoff

Prefer the interfaces declared by the selected child skill. Load Apps Common
only when the child graph reaches a read-only lookup or an explicitly supported
REST exception. Load Data Loader only after a mutation has produced the exact
fresh-export-derived FSM ZIP and the child graph reaches its handoff terminal.
For Win/Loss Reasons, the child-declared failed, timed-out, or unusable
same-target FSM export returns `OPP.WIN_LOSS.RETURN_FALLBACK_REQUIRED`.
Continue the unchanged Create, Update, or Disable request once through that
child's `REST_FALLBACK` graph and direct Apps Common REST. Do not require a
registered loader lookup, Data Loader task context, final FSM ZIP, or repeated
export approval. The child still requires fresh exact reads, its independent
immutable REST preview, and explicit approval immediately before submission.
Respect an explicit FSM-only or Data Loader-only constraint and stop route
changes after any submitted or uncertain upload, import, or mutation.
For the profile-options export-omission or export-failure branch, load Apps Common Profile Options
when APPS_COMMON_DESIGN/APPS_COMMON_GATE is reached. The child owns the REST
preview, approval, immediate stale-state check, and same-run verification; do
not demand Data Loader context or a ZIP for this branch. Mixed-route BulkSet
returns a separate-batch plan before any submission.

The child hands Data Loader its exact catalog task code/name, declared FSM
execution task code/name, selected child skill path, persisted task-context
path, positive task sequence, environment, immutable package path and SHA-256,
operation, expected state, proposed delta, impact evidence, task-rule result,
and export identity and release. The persisted context must resolve to the
exact child skill and catalog task, offering, and functional area; archive
metadata must resolve independently to the declared execution task. A lookup
or set-enabled child also supplies its fixed lookup type and code plus resolved
set identity; non-lookup children supply only the task-specific identities
their child contract requires. Data Loader
binds `finalData.archiveSha256` to the unchanged package SHA-256 while owning
Task Hook validation, its immutable preview and session approval lifecycle,
authentication, upload, and accepted initiation result. Delegated results are
intermediate; resume the child graph at its next node or terminal instead of
reconstructing core envelopes here.

Accepted Data Loader initiation is terminal for that request. Retrieve status,
errors, ProcessLog, and live post-change verification only after a later
explicit status or results request; never poll or resubmit automatically.

## Related Opportunity Integration Skill

Route an Opportunities request to
[Manage Oracle CX Sales to Oracle CPQ Cloud Integration](../integrations/manage-oracle-cx-sales-to-oracle-cpq-cloud-integration/SKILL.md)
when it includes Oracle CPQ quoting, a Sales Order Instance, Create Quote, Edit
Quote, Copy Quote, Create a Version, Get Proposal, CPQ commerce-process
metadata, or setup task `ORA_ZCA_OSC_CPQ_INTEGRATION`.

Preserve the catalog identity of that setup task as Sales → Integrations
(`ORA_ZCA_INTEGRATIONS`). Treat it as a related Opportunities capability, not a
native Opportunities setup task. Invoke the canonical integration skill
for its validation, CPQ GET-only metadata resolution, Fusion export/import,
approval, diagnostics, and verification workflow. Do not copy its scripts,
resources, credentials flow, or task registry into this skill.

## Default Mutation Route

For every Opportunities setup task with `dataloader_import_mode: FSM`, use the
Functional Setup Manager CSV package route by default: export the package using
the child-declared FSM execution task, validate the intended rows and reference
data under the child's catalog scope, and hand the unchanged immutable package
to `core.data-loader`. Data Loader owns its session approval preview and waits
for the later contextual approval required by its current contract. Read-only REST
discovery may support package preparation and later explicit verification, but
it is not the default mutation route.

The profile-options child automatically selects its declared Apps Common
fallback when a successful complete export omits the requested option or the
exact-task export attempt fails. Exact live identity is required in both cases;
export failure additionally requires an existing value and PATCH only. This
task-local exception still requires a separate
immutable REST preview and explicit approval immediately before execution.
The Win/Loss Reasons child likewise automatically selects direct Apps Common
REST after a failed, timed-out, or unusable exact-target FSM export. Its
unavailability receipt and fresh reads replace only the unavailable baseline;
the separate REST preview and approval remain mandatory.
For other direct REST mutations, require the requester to select the route and
the nested task contract to document it as supported. They still require
an independent immutable REST preview and approval; it must never be inferred
from a generic request to create, update, disable, or delete setup data.

Record the routed skill ID, setup task code, catalog owner, child readiness or
terminal status, sanitized artifact references, blockers, and safe next action
in the Opportunities setup plan. Keep CPQ-side mutations outside the
Opportunities skill boundary.

If "configure Oracle CPQ" includes CPQ-side process, document, action, SSO, or
deployment changes, split the scope explicitly. Execute only the CX Sales-side
integration task through the routed skill and return a CPQ-owner handoff with
the unresolved CPQ-side prerequisites and next action; do not report the full
request complete from this skill.

## Inputs

- `implementation_objective`
- `project_context`
- `opportunities_scope`
- `opportunities_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated nested setup-task skills for native Opportunities task-level
planning and sequencing. When CPQ is in scope, route its work to the canonical
integration skill and include the sanitized result in the Opportunities plan
without changing its catalog ownership. Track token usage for any generated
project artifact or skill-run record using the manifest policy.
