---
skill_id: "scm.product-management"
name: "Product Management"
description: "Coordinates SCM Product Management implementation guidance and routes work to developer-created functional-area skills."
layer: "pillar"
pillar: "SCM"
offering: "Product Management"
type: "orchestration"
execution_mode: "assisted"
owner_team: "SCM Product Management pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "scm_scope"
  - "product_management_requirements"
outputs:
  - "product_management_scope"
  - "functional_area_skill_plan"
  - "product_management_work_products"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/product-management/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "setup_task_sequence"
    default_location: "project/{project_id}/artifacts/pillars/scm/product-management/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/product-management/current/"
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

# Product Management

## Purpose

Coordinates SCM Product Management implementation guidance across functional areas, setup tasks, and standard implementation activities.

## When to Use

Use this offering-level skill after Product Management is in scope and before routing to a specific functional-area skill.

## Catalog Identity

- Pillar: `SCM`
- Pillar slug: `scm`
- Offering code: `PIM_PROD_MNG`
- Offering slug: `product-management`
- Offering folder: `pillars/scm/product-management`
- Offering mapping source: `knowledge/setup-task-catalog/release/pillars-offerings-mapping.json`
- Setup task catalog source: `knowledge/setup-task-catalog/release/offering-functional-area-task-catalog.json`

## Routing Responsibility

```text
pillars/scm/product-management/{functional-area-slug}/
```

## Inputs

- `implementation_objective`
- `project_context`
- `scm_scope`
- `product_management_requirements`

## Outputs

- `product_management_scope`
- `functional_area_skill_plan`
- `product_management_work_products`
- `token_usage_record`

## Functional Areas From Catalog

Source: `knowledge/setup-task-catalog/release/offering-functional-area-task-catalog.json`
Offering code: `PIM_PROD_MNG`
Functional area count: `25`
Setup task count: `234`

- `ORA_ASK_INITIAL_USER`: Initial Users
- `ORA_ASK_ENTERPRISE_PROFILE`: Enterprise Profile
- `ORA_ASK_USERS_AND_SECURITY`: Users and Security
- `ORA_ASK_APPLICATION_EXTENSIONS`: Application Extensions
- `ORA_EGP_FA_INVENTORY_ORGANIZAT`: Inventory Organizations
- `ORA_EGP_FA_ITEM_ORGANIZATIONS`: Item Organizations
- `ORA_EGP_FA_ITEMS`: Items
- `ORA_EGP_FA_CATALOGS`: Catalogs
- `EGO_ADVANCED_PRODUCT_STRUCT`: Structures
- `ORA_EGP_SUPPLIER_FOR_PIM`: Suppliers for Product Management
- `ORA_EGP_MASS_UPDATE`: Item Mass Update
- `EGI_ADVANCED_CATALOGS`: Advanced Catalogs
- `EGO_NEW_ITEM_REQUESTS`: New Item Requests
- `EGO_CHANGE_ORDERS`: Change Orders
- `EGO_PRODUCT_RULES`: Product Rules
- `ORA_EGI_DATA_QLTY_RULES_PROD`: Data Quality Rules for Products
- `ORA_EGI_AUDIT_TRAIL`: Audit Trail
- `EGI_PRODUCT_SOURCE_SYSTEMS`: Product Spoke Systems
- `ORA_EGI_PRODUCT_BATCH_IMPORT`: Item Batches
- `ORA_EGP_DATA_POOL_INTEGRATION`: Data Pool Integration
- `EGI_PRODUCT_DATA_QUALITY`: Data Quality for Products
- `PO_SUP_PORTAL_DEPLOYED`: Supplier Portal
- `ORA_ACA_PROD_DEV`: Product Development
- `ORA_ACN_PROD_RQMNTS_IDEA`: Product Requirements and Ideation Management
- `ORA_ACD_CONCEPT_DESIGN_MGMT`: Concept Design Management

## Implementation Notes

- Keep offering-level planning, scope decisions, sequencing, and cross-functional-area handoffs in this skill.
- Put functional-area-specific implementation guidance in generated child skills under this offering folder.

## Item Index Remediation Handoff

When `scm.product-management.items.import-items` ends at
`ITEM_IMPORT.INDEX_REMEDIATION_REQUIRED`, this offering skill owns the
cross-functional-area continuation. The Import Items task itself must not
invoke or wait for another task.

1. Tell the user: `The Product Management item search index is unavailable. Manage Product Management Indexes is now the required remediation task; it will collect the index-specific inputs before making any change.`
2. Route to `scm.product-management.index-management.manage-product-management-indexes` (`CUSTOM_EGP_MANAGE_PM_INDEXES`) in the same target environment and project context. Do not infer an index name, requested attribute changes, rebuild option, approval, or completion from the failed lookup.
3. Let that task collect its own one-index request and follow its normal Data Loader, status, readback, ESS, and approval gates. Report that the remediation task is executing only after it has begun its selected workflow; do not claim that an index rebuild was submitted or completed before its verified result.
4. Wait at the remediation task's documented user-input, approval, status, or completion terminal. Resume the Import Items task only after the index task reports verified completion for the same environment.
5. Restart Import Items from `ITEM_IMPORT.CHECK_ITEM_INDEX` and require a new `verify_item_search_index_readiness` GET result classified as `available`. Do not reuse the original HTTP 404 result or continue directly to FBDI preparation.

The offering-level handoff selects the remediation task but does not bypass its
input collection, approval, Data Loader, or ESS controls.
