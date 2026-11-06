---
skill_id: "cx.configure-price-quote.products-setup"
name: "Products Setup Implementation Guidance"
description: "Plans new-instance CPQ product setup by reusing Sales and PIM skills for standard and model products; defines CPQ acceptance and unresolved dependencies."
layer: "pillar"
pillar: "CX"
offering: "Configure Price Quote"
functional_area: "Products Setup"
functional_area_code: "CUSTOM_PRODUCTS_SETUP"
type: "planning"
execution_mode: "assisted"
owner_team: "CX configure price quote pillar team"
version: "0.4.8"
inputs:
  - "implementation_objective"
  - "project_context"
  - "products_setup_scope"
  - "products_setup_requirements"
outputs:
  - "functional_area_setup_plan"
  - "configuration_guidance"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.implementation-planning.offering-task-map-builder"
  - "shared.implementation-planning.task-dependency-resolver"
  - "shared.implementation-planning.fsm-set-optin.fsm-set-optin-functional-areas"
  - "shared.implementation-planning.fsm-set-optin.fsm-set-optin-features"
  - "cx.configure-price-quote.company-profile.cpq-setup-assistant"
  - "cx.sales.sales-catalog-and-products.manage-product-group-profile-option-values"
  - "cx.sales.sales-catalog-and-products.manage-sales-functional-area-catalog"
  - "scm.product-management.catalogs.manage-functional-area-catalogs"
  - "scm.product-management.items"
  - "scm.product-management.items.import-items"
  - "scm.product-management.structures.item-structure-import"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/products-setup/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/products-setup/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/products-setup/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "Writes a project setup plan, dependency decisions, and sanitized readiness evidence."
required_privileges:
  - "Privileges required by each selected Sales, PIM, CPQ, or shared task; validate them through that task before execution."
---

# Products Setup Implementation Guidance

## Purpose

Plan product setup for a new Fusion CPQ instance using implementer-supplied
data. Support both standard items and configurable/model products through the
same PIM item-import route, with structures when required. Sales functional-area
setup is required; Sales Catalog migration and eligibility-rule authoring are
out of scope. PIM Item Rule Sets are not CPQ eligibility rules.

## When to Use

Use after the implementation router selects the project and Products Setup
scope. This parent owns requirements, upstream handoffs, and CPQ acceptance;
the upstream skills own setup procedures and execution.

## Catalog Metadata

Products Setup (`CUSTOM_PRODUCTS_SETUP`) is a repository grouping under
Configure Price Quote (`ORA_CONFIGURE_PRICE_QUOTE`), not a live Fusion
feature or exportable task. It has no CPQ-owned child setup tasks.

## Inputs

Reuse the four manifest inputs and existing project evidence. Collect only the
next missing detail: target pod, organization/catalog requirements, and references
to the implementer's item and optional structure data. Collect runtime user,
accessible quote, and known products when acceptance is reached. Keep raw
product data, import archives, and credentials outside project records.

## Planning and Readiness

Use [Offering Task Map Builder](../../../../shared/implementation-planning/offering-task-map-builder/SKILL.md),
which invokes [Task Dependency Resolver](../../../../shared/implementation-planning/task-dependency-resolver/SKILL.md).
Consume its persisted sequence and diagnostics; table order is not execution
order. Keep tasks in their owning offering/functional-area contexts. Return
missing cross-pillar scope to the router; do not fabricate CPQ task membership.

Verify prerequisites through their owning skills. Reuse current successful
evidence, route missing setup to its owner, and preserve pending/stop conditions.
CPQ foundation gates quote acceptance, not independently ready PIM work.
Upstream workflows own privileges, approvals, execution, retries, and recovery;
do not add duplicate approvals or substitute parent-level REST, FBDI, ESS, or
browser actions. Reconcile uncertain results before any repeated operation.

Set the requested finish line from the user's scope: preparation or full CPQ
quote acceptance. Report completion only at the level supported by the
evidence; a preparation request does not require executing later phases.

Before executing the selected flow, verify that its required upstream skills
are available and its tasks resolve in their owning contexts. Once a Run Book
is active, check that it contains the tasks needed for the selected flow,
including downstream index tasks when full setup is requested. Repeat this
check when scope expands. Return missing tasks or skills to their owner before
the affected handoff; independently ready work may continue. A skill file or
task catalog entry alone does not establish Run Book membership.

On each start or resume, show a brief **Completed / Current / Next** checkpoint
from project state, with the target pod and relevant task, request, and artifact
references. Interpret an unambiguous "proceed" as continuing the saved pending
step: check the existing operation's status when one is in progress, then use
its result to choose the next action. Never resubmit merely to resume or ask
again for an answer already recorded. Preserve the owning skill's approval and
stop conditions for any new write.

## Setup Tasks

**Upstream reuse is mandatory.** Read each selected upstream `SKILL.md` and
its required resources, map project requirements to its declared inputs, and
follow its routed workflow. Retain its result references. Do not copy its
procedures, profiles, task resources, or validation rules into CPQ.

| Required capability | Upstream skill and CPQ handoff |
|---|---|
| Sales functional-area setup | [FSM Set Optin Functional Areas](../../../../shared/implementation-planning/fsm-set-optin/fsm-set-optin-functional-areas/SKILL.md): resolve Sales Catalog and Products (`ORA_QSC_DEFINE_SALES_CATALOG_AND_PRODUCTS`) in the target pod. Repository flags do not prove readiness. |
| CPQ foundation | [CPQ Setup Assistant](../company-profile/cpq-setup-assistant/SKILL.md) and [FSM Set Optin Features](../../../../shared/implementation-planning/fsm-set-optin/fsm-set-optin-features/SKILL.md): verify current setup and release-applicable Unified CPQ readiness. |
| Item reference setup | [PIM Items](../../../scm/product-management/items/SKILL.md): select only the setup required by the supplied data, reusing valid existing setup. |
| Sales item organization | [Manage Product Group Profile Option Values](../../sales/sales-catalog-and-products/manage-product-group-profile-option-values/SKILL.md): supply the intended organization when Sales setup requires it; PIM-native lookup alone does not justify a profile change. |
| Catalogs and categories | [Manage Functional Area Catalogs](../../../scm/product-management/catalogs/manage-functional-area-catalogs/SKILL.md): supply catalog/category requirements; new Sales catalogs must allow item assignment at any node, not only leaf categories. |
| Sales catalog assignment | [Manage Sales Functional Area Catalog](../../sales/sales-catalog-and-products/manage-sales-functional-area-catalog/SKILL.md): use this Sales-owned workflow for every catalog-to-Sales functional-area assignment, including changing the assigned catalog. Supply the selected catalog and environment; verify the assignment. This may complete before product loading and does not start indexing. |
| Standard and model item load | [Import Items](../../../scm/product-management/items/import-items/SKILL.md): supply the implementer's item source; require completed import evidence, not package preparation alone. |
| Structures, when required | [Item Structure Import](../../../scm/product-management/structures/item-structure-import/SKILL.md): supply structure/component data after referenced items are ready; retain uncovered model requirements as gaps. |
| Post-load indexing | Use the [Sales-owned index handoff](#sales-owned-index-handoff) after relevant loads and assignments succeed; Sales delegates index execution to PIM. |

## Implementation Notes

### Sales catalog creation and assignment

When creating a catalog for Sales, pass the any-node requirement to PIM:
`AssignItemsToLeafOnlyFlag=false` (the leaf-only restriction is **off**), mapped
by the upstream skill to `CatalogContentCode=ALL_ITEMS`. Require its validated
preview to preserve this setting; do not claim runtime verification without
supporting upstream evidence.

Assign the created or existing catalog to the **Sales functional area** through
Manage Sales Functional Area Catalog. Let Sales delegate execution to PIM;
do not bypass Sales with a direct PIM assignment. This is a catalog-to-functional-
area association, not a link between two catalogs or an item-to-category
assignment. For assignment-only requests, do not add catalog/category changes
solely to restate the any-node policy; use the upstream Sales scope and approvals.

### Sales-owned index handoff

Use the transitive chain: Sales Functional Area Catalog → Sales Index → PIM
Index Management. Sales owns index profiles and input mapping; PIM owns execution.
Do not invoke PIM directly or create a CPQ adapter.

For this new-instance rollout, perform final index rebuilds after the relevant
item loads, required structures, and catalog/category assignments succeed.
Earlier rebuilds do not establish readiness for subsequently changed data.

Retain both Item and Catalog index requirements and pass them through the
Sales-owned request contract. Sales owns their sequencing and continuation;
PIM owns each single-index invocation, state archival, and approval gates.
Do not independently queue, start, or replace child invocations from CPQ.
An assignment-acceptance notification
does not start indexing or verify the assignment. Require terminal assignment
success and same-pod association evidence before Sales-originated indexing;
do not repeat an existing assignment merely to trigger indexes.

Missing or incompatible upstream contracts block the affected handoff. Record
the owner and next action; independently ready work may continue. Reuse current
successful results rather than automatically importing or rebuilding again.

### CPQ acceptance

Full CPQ quote acceptance requires the following evidence from the owning
workflows:

- Successful item loads, required structures, intended organization and
  catalog/category assignments, plus successful Item and Catalog index rebuilds
  covering the latest data. Submission or skipped rebuilds are not completion.
- Verified runtime-user access and resolved snapshot applicability, including
  successful execution evidence if a snapshot is required.
- In the same pod and runtime-user context, finding and selecting every
  expected product in an accessible quote's Add Products experience.
  Catalog or item setup evidence alone does not pass this acceptance level.

Use the supported CPQ validation route once delivered; do not invent endpoint
or browser procedures. Test each product type present in project data. Reusable
skill coverage requires both standard and model products; an absent project
type is not applicable, not passed coverage. Selection does not establish full
model configuration or pricing.

### Open dependencies

Keep acceptance blocked until these have supported owners/contracts:

- Runtime-user PIM security: owner and executable check/remediation skill TBD.
- Product Hub snapshot applicability: PIM confirmation and, if required, an
  owning execution skill are still needed.
- CPQ Add Products validation: executable CPQ route TBD.

## Outputs

Persist the manifest's standard CPQ outputs through the existing project
managers: reference the shared sequence, record handoff inputs and unresolved
decisions, and retain sanitized upstream results and acceptance findings.
Use the repository artifact, validation-result, and skill-run schemas; register
and version artifacts, update project state, and log token usage. Do not create
a separate readiness framework. Unmet required checks prevent acceptance;
a completed planning run is not a passed instance.

## Repository Validation

Run the CPQ repository contract checks from the repository root:

```bash
python3 -B -m unittest discover -s pillars/cx/configure-price-quote/products-setup/tests -v
```

The suite checks the CPQ manifest, catalog discovery, upstream references, and
the Sales/PIM dependency chain. Execution internals remain covered by the
upstream teams' tests; passing repository checks is not instance acceptance.

Use [Products Setup review scenarios](tests/products-setup-scenarios.md) to
review data readiness, handoffs, reuse, and CPQ acceptance separately.
