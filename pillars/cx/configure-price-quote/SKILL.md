---
skill_id: "cx.configure-price-quote"
name: "Configure Price Quote"
description: "Coordinates CX Configure Price Quote implementation guidance and routes work to developer-created functional-area skills."
layer: "pillar"
pillar: "CX"
offering: "Configure Price Quote"
type: "orchestration"
execution_mode: "assisted"
owner_team: "CX Configure Price Quote pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "cx_scope"
  - "configure_price_quote_requirements"
outputs:
  - "configure_price_quote_scope"
  - "functional_area_skill_plan"
  - "configure_price_quote_work_products"
  - "token_usage_record"
depends_on:
  - "shared.project-intake.scope-definition"
  - "shared.implementation-planning.offering-task-map-builder"
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
  - "scope"
  - "skill_path"
  - "setup_task_sequence"
  - "design_decisions"
  - "configuration_blueprints"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "scope"
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "setup_task_sequence"
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
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

# Configure Price Quote

## Purpose

Coordinates CX Configure Price Quote implementation guidance across functional areas, setup tasks, and standard implementation activities.

## When to Use

Use this offering-level skill after Configure Price Quote is in scope and before routing to a specific functional-area skill.

## Catalog Identity

- Pillar: `CX`
- Pillar slug: `cx`
- Offering code: `ORA_CONFIGURE_PRICE_QUOTE`
- Offering slug: `configure-price-quote`
- Offering folder: `pillars/cx/configure-price-quote`
- Offering mapping source: `knowledge/setup-task-catalog/effective/pillars-offerings-mapping.json`
- Setup task catalog source: `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json`

## Routing Responsibility

Route control to available functional-area skills under this folder using the catalog-backed path pattern:

```text
pillars/cx/configure-price-quote/{functional-area-slug}/
```

Match the requested functional area against the setup catalog below and verify that its child skill is available before handing off. If it is missing, record the coverage gap and return it to the router and responsible pillar team. Stop the affected handoff until the skill is delivered; do not create a skill or substitute an execution route during implementation.

## Inputs

- `implementation_objective`
- `project_context`
- `cx_scope`
- `configure_price_quote_requirements`

## Outputs

- `configure_price_quote_scope`
- `functional_area_skill_plan`
- `configure_price_quote_work_products`
- `token_usage_record`

## Functional Areas From Catalog

Source: `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json`
Offering code: `ORA_CONFIGURE_PRICE_QUOTE`
Functional area count: `5`
Setup task count: `28`

- `ORA_SVC_COMPANY_PROFILE`: Company Profile
- `ORA_ASK_USERS_AND_SECURITY`: Users and Security
- `CUSTOM_QUOTING`: Quoting
- `CUSTOM_PRICING`: Pricing
- `CUSTOM_PRODUCTS_SETUP`: Products Setup

## Implementation Notes

- Keep offering-level planning, scope decisions, sequencing, and cross-functional-area handoffs in this skill.
- Put functional-area-specific implementation guidance in generated child skills under this offering folder.
- Follow each selected child skill's declared workflow and required resources.
- Report missing task guidance to the responsible pillar team and preserve the affected handoff as blocked.
