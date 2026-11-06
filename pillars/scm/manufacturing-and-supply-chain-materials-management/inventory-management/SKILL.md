---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.inventory-management"
name: "Inventory Management Implementation Guidance"
description: "Provides SCM Manufacturing and Supply Chain Materials Management implementation guidance for the Inventory Management functional area."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Inventory Management"
functional_area_code: "ORA_WSH_INVENTORY_MGMT"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM manufacturing and supply chain materials management pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "inventory_management_scope"
  - "inventory_management_requirements"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/inventory-management/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/inventory-management/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/inventory-management/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_INVENTORY_TRANSACTION_SOURCES_AND_TYPES"
  - "ORA_INVENTORY_TRANSACTION_REASONS"
  - "ORA_MATERIAL_STATUSES"
  - "ORA_INV_CONFIGURE_SUBINVENTORIES"
  - "ORA_INV_CONFIGURE_ITEM_TRANSACTION_DEFAULTS"
  - "ORA_LOT_GRADES"
  - "ORA_LOT_EXPIRATION_ACTIONS"
  - "ORA_INVENTORY_ABC_ANALYSIS"
  - "ORA_LOT_AND_SERIAL_ATTRIBUTE_MAPPINGS"
  - "ORA_INTERORGANIZATION_PARAMETERS"
  - "ORA_PICKING_RULES"
  - "ORA_UNITS_OF_MEASURE_USAGES"
  - "ORA_PICK_SLIP_GROUPING_RULES"
  - "ORA_INV_CONFIGURE_BARCODE_FORMATS"
  - "ORA_PICKING_RULE_ASSIGNMENTS"
  - "ORA_INTERSUBINVENTORY_PARAMETERS"
  - "ORA_CONSUMPTION_RULES"
  - "ORA_INVENTORY_BUSINESS_EVENT_CONFIGURATIONS"
  - "ORA_INV_CONFIGURE_ITEM_SHORTAGE_PARAMETERS"
  - "ORA_INV_CONFIGURE_RFID_INTEGRATIONS_AND_DEVICES"
  - "ORA_INVENTORY_ZONES"
  - "ORA_CONFIGURE_INVENTORY_ATTRIBUTE_EXCEPTIONS"
  - "ORA_INVENTORY_DOCUMENT_OUTPUT_PREFERENCES"
  - "ORA_LABEL_OUTPUT_PREFERENCES"
  - "ORA_LOT_SELECTOR_VIEW_CONFIGURATION"
  - "ORA_INV_POLICY_PROFILES"
  - "ORA_INV_DEFAULT_CLASSIFICATION_GROUP"
  - "ORA_MANAGE_MIN_MAX_PLANNING_POLICY_PROFILE_ASSIGNMENTS"
  - "ORA_INVENTORY_ATTRIBUTE_CONFIGURATION"
  - "ORA_ACCOUNT_ALIASES"
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

# Inventory Management Implementation Guidance

## Purpose

Provides SCM Manufacturing and Supply Chain Materials Management implementation guidance for the Inventory Management functional area.

## When to Use

Use this functional-area skill after Manufacturing and Supply Chain Materials Management scope is confirmed and the project needs inventory management setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `SCM`
- Offering: `Manufacturing and Supply Chain Materials Management` (`ORA_MANUFACTURING_AND_SUPPLY_C`)
- Functional area / Setup Object: `Inventory Management` (`ORA_WSH_INVENTORY_MGMT`)

## Setup Tasks

1. [Inventory Transaction Sources and Types](inventory-transaction-sources-and-types/SKILL.md) (`ORA_INVENTORY_TRANSACTION_SOURCES_AND_TYPES`)
2. [Inventory Transaction Reasons](inventory-transaction-reasons/SKILL.md) (`ORA_INVENTORY_TRANSACTION_REASONS`)
3. [Material Statuses](material-statuses/SKILL.md) (`ORA_MATERIAL_STATUSES`)
4. [Configure Subinventories](configure-subinventories/SKILL.md) (`ORA_INV_CONFIGURE_SUBINVENTORIES`)
5. [Configure Item Transaction Defaults](configure-item-transaction-defaults/SKILL.md) (`ORA_INV_CONFIGURE_ITEM_TRANSACTION_DEFAULTS`)
6. [Lot Grades](lot-grades/SKILL.md) (`ORA_LOT_GRADES`)
7. [Lot Expiration Actions](lot-expiration-actions/SKILL.md) (`ORA_LOT_EXPIRATION_ACTIONS`)
8. [Inventory ABC Analysis](inventory-abc-analysis/SKILL.md) (`ORA_INVENTORY_ABC_ANALYSIS`)
9. [Lot and Serial Attribute Mappings](lot-and-serial-attribute-mappings/SKILL.md) (`ORA_LOT_AND_SERIAL_ATTRIBUTE_MAPPINGS`)
10. [Interorganization Parameters](interorganization-parameters/SKILL.md) (`ORA_INTERORGANIZATION_PARAMETERS`)
11. [Picking Rules](picking-rules/SKILL.md) (`ORA_PICKING_RULES`)
12. [Units of Measure Usages](units-of-measure-usages/SKILL.md) (`ORA_UNITS_OF_MEASURE_USAGES`)
13. [Pick Slip Grouping Rules](pick-slip-grouping-rules/SKILL.md) (`ORA_PICK_SLIP_GROUPING_RULES`)
14. [Configure Barcode Formats](configure-barcode-formats/SKILL.md) (`ORA_INV_CONFIGURE_BARCODE_FORMATS`)
15. [Picking Rule Assignments](picking-rule-assignments/SKILL.md) (`ORA_PICKING_RULE_ASSIGNMENTS`)
16. [Intersubinventory Parameters](intersubinventory-parameters/SKILL.md) (`ORA_INTERSUBINVENTORY_PARAMETERS`)
17. [Consumption Rules](consumption-rules/SKILL.md) (`ORA_CONSUMPTION_RULES`)
18. [Inventory Business Event Configurations](inventory-business-event-configurations/SKILL.md) (`ORA_INVENTORY_BUSINESS_EVENT_CONFIGURATIONS`)
19. [Configure Item Shortage Parameters](configure-item-shortage-parameters/SKILL.md) (`ORA_INV_CONFIGURE_ITEM_SHORTAGE_PARAMETERS`)
20. [Configure RFID Integrations and Devices](configure-rfid-integrations-and-devices/SKILL.md) (`ORA_INV_CONFIGURE_RFID_INTEGRATIONS_AND_DEVICES`)
21. [Inventory Zones](inventory-zones/SKILL.md) (`ORA_INVENTORY_ZONES`)
22. [Configure Inventory Attribute Exceptions](configure-inventory-attribute-exceptions/SKILL.md) (`ORA_CONFIGURE_INVENTORY_ATTRIBUTE_EXCEPTIONS`)
23. [Inventory Document Output Preferences](inventory-document-output-preferences/SKILL.md) (`ORA_INVENTORY_DOCUMENT_OUTPUT_PREFERENCES`)
24. [Label Output Preferences](label-output-preferences/SKILL.md) (`ORA_LABEL_OUTPUT_PREFERENCES`)
25. [Lot Selector Views](lot-selector-views/SKILL.md) (`ORA_LOT_SELECTOR_VIEW_CONFIGURATION`)
26. [Policy Profiles](policy-profiles/SKILL.md) (`ORA_INV_POLICY_PROFILES`)
27. [Default Classification Group](default-classification-group/SKILL.md) (`ORA_INV_DEFAULT_CLASSIFICATION_GROUP`)
28. [Manage Min-Max Planning Policy Profile Assignments](manage-min-max-planning-policy-profile-assignments/SKILL.md) (`ORA_MANAGE_MIN_MAX_PLANNING_POLICY_PROFILE_ASSIGNMENTS`)
29. [Inventory Attribute Configurations](inventory-attribute-configurations/SKILL.md) (`ORA_INVENTORY_ATTRIBUTE_CONFIGURATION`)
30. [Account Aliases](account-aliases/SKILL.md) (`ORA_ACCOUNT_ALIASES`)

## Inputs

- `implementation_objective`
- `project_context`
- `inventory_management_scope`
- `inventory_management_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated nested setup-task skills for task-level planning, sequencing, setup-data routing, and validation. Track token usage for any generated project artifact or skill-run record using the manifest policy.
