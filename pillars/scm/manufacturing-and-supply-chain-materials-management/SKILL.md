---
skill_id: "scm.manufacturing-and-supply-chain-materials-management"
name: "Manufacturing and Supply Chain Materials Management"
description: "Coordinates SCM Manufacturing and Supply Chain Materials Management implementation guidance and routes work to developer-created functional-area skills."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
type: "orchestration"
execution_mode: "assisted"
owner_team: "SCM Manufacturing and Supply Chain Materials Management pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "scm_scope"
  - "manufacturing_and_supply_chain_materials_management_requirements"
outputs:
  - "manufacturing_and_supply_chain_materials_management_scope"
  - "functional_area_skill_plan"
  - "manufacturing_and_supply_chain_materials_management_work_products"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "setup_task_sequence"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/current/"
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

# Manufacturing and Supply Chain Materials Management

## Purpose

Coordinates SCM Manufacturing and Supply Chain Materials Management implementation guidance across functional areas, setup tasks, and standard implementation activities.

## When to Use

Use this offering-level skill after Manufacturing and Supply Chain Materials Management is in scope and before routing to a specific functional-area skill.

## Catalog Identity

- Pillar: `SCM`
- Pillar slug: `scm`
- Offering code: `ORA_MANUFACTURING_AND_SUPPLY_C`
- Offering slug: `manufacturing-and-supply-chain-materials-management`
- Offering folder: `pillars/scm/manufacturing-and-supply-chain-materials-management`
- Offering mapping source: `knowledge/setup-task-catalog/release/pillars-offerings-mapping.json`
- Setup task catalog source: `knowledge/setup-task-catalog/release/offering-functional-area-task-catalog.json`

## Routing Responsibility

```text
pillars/scm/manufacturing-and-supply-chain-materials-management/{functional-area-slug}/
```

## Inputs

- `implementation_objective`
- `project_context`
- `scm_scope`
- `manufacturing_and_supply_chain_materials_management_requirements`

## Outputs

- `manufacturing_and_supply_chain_materials_management_scope`
- `functional_area_skill_plan`
- `manufacturing_and_supply_chain_materials_management_work_products`
- `token_usage_record`

## Functional Areas From Catalog

Source: `knowledge/setup-task-catalog/release/offering-functional-area-task-catalog.json`
Offering code: `ORA_MANUFACTURING_AND_SUPPLY_C`
Functional area count: `25`
Setup task count: `515`

- `ORA_ASK_INITIAL_USER`: Initial Users
- `ORA_ASK_ENTERPRISE_PROFILE`: Enterprise Profile
- `ORA_ASK_LEGAL_STRUCTURES`: Legal Structures
- `ORA_ASK_FIN_REPORTING_STRUCT`: Financial Reporting Structures
- `ORA_ASK_ORGANIZATION_STRUCTURE`: Organization Structures
- `ORA_EGP_CUSTOMER`: Customers
- `ORA_EGP_SUPPLIERS`: Suppliers
- `ORA_RCS_FACILITIES`: Facilities
- `ORA_ASK_USERS_AND_SECURITY`: Users and Security
- `ORA_EGP_FA_ITEMS`: Items
- `ORA_RCS_CARRIERS_TRANSIT_TIMES`: Carriers and Transit Times
- `ORA_EGP_FA_CATALOGS`: Catalogs
- `ORA_WSH_INVENTORY_MGMT`: Inventory Management
- `WSH_ENABLE_RECEIVING`: Receiving
- `WSH_ENABLE_SHIPPING`: Shipping
- `CMR_RECEIPT_ACCOUNTING`: Receipt Accounting
- `CST_DEFINE_COST_MANAGEMENT`: Cost Accounting
- `CST_COST_AND_PROFIT_PLANNING`: Cost and Profit Planning
- `ORA_CML_LANDED_COST_MGMT`: Landed Cost Management
- `JMF_INTRASTAT`: Intrastat Reporting
- `ORA_WIS_COMMON_MFG_WORK_SETUP`: Manufacturing Master Data
- `EGO_ADVANCED_PRODUCT_STRUCT`: Structures
- `ORA_VCS_SUPPLY_COLLABORATION`: Supply Chain Collaboration
- `ORA_DOS_SUPPLY_CHAIN_ORCH`: Supply Chain Orchestration
- `ORA_MNT_MGMT`: Maintenance Management

## Implementation Notes

- Keep offering-level planning, scope decisions, sequencing, and cross-functional-area handoffs in this skill.
- Put functional-area-specific implementation guidance in generated child skills under this offering folder.
- Do not create setup-task-specific skills directly under this offering folder unless the user explicitly requests nested task-level skill generation through the pillar skill generator.
