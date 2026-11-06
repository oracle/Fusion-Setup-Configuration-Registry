---
skill_id: "scm.product-management.items"
name: "Items Implementation Guidance"
description: "Provides SCM Product Management implementation guidance for the Items functional area."
layer: "pillar"
pillar: "SCM"
offering: "Product Management"
functional_area: "Items"
functional_area_code: "ORA_EGP_FA_ITEMS"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM product management pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "items_scope"
  - "items_requirements"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/product-management/items/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/product-management/items/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/product-management/items/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "INV_MANAGE_UNITS_OF_MEASURE"
  - "ORA_MANAGE_UNIT_OF_MEASURE_CLASSES"
  - "RCS_MANAGE_UOM_INTER_CLASS_CONV"
  - "RCS_MANAGE_UOM_INTRA_CLASS_CONV"
  - "ORA_RCS_MANAGE_UOM_DESCRIPTIVE_FLEXFIELDS"
  - "ORA_RCS_MANAGE_UOM_PROFILE"
  - "EGP_MANAGE_LIFECYCLE_PHASES"
  - "EGP_MANAGE_DEFAULT_ITEM_CLASS"
  - "EGP_MANAGE_ITEM_STATUSES"
  - "EGP_IMPORT_ITEMS"
  - "EGP_TRADING_PARTNER_ITEMS_DFFS"
  - "EGP_ITEM_RELATIONSHIP_DFFS"
  - "EGP_MANAGE_RELATED_ITEM_SUBTYPES"
  - "EGP_MANAGE_CROSS_REFERENCE_TYPES"
  - "ORA_MANAGE_RELATED_ITEM_TYPES"
  - "EGP_MANAGE_ITEM_TYPES"
  - "EGP_MANAGE_ITEM_PROFILE_OPTIONS"
  - "EGO_MANAGE_ADVANCED_ITEM_PROFILE_OPTIONS"
  - "EGP_MANAGE_OPERATIONAL_ATTRIBUTES_GROUPS"
  - "EGP_MANAGE_ITEM_DESCRIPTIVE_FLEXFIELDS"
  - "EGO_MANAGE_ITEM_ATTRIBUTE_GROUPS_AND_ATTRIBUTES"
  - "ORA_EGP_MANAGE_ATTACH_CAT_FOR_PIM"
  - "EGO_DEPLOY_EFFS"
  - "EGO_MANAGE_ITEM_CLASSES"
  - "EGP_MANAGE_PRODUCT_VALUE_SETS"
  - "EGP_ITEM_CLASS_DFFS"
  - "EGI_MANAGE_IMPORT_MAPS"
  - "CUSTOM_EGP_FBDI_IMPORT_REF_ORG_ITEMS"
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

# Items Implementation Guidance

## Purpose

Provides SCM Product Management implementation guidance for the Items functional area.

## When to Use

Use this functional-area skill after Product Management scope is confirmed and the project needs items setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `SCM`
- Offering: `Product Management` (`PIM_PROD_MNG`)
- Functional area / Setup Object: `Items` (`ORA_EGP_FA_ITEMS`)

## Setup Tasks

1. [Manage Units of Measure](manage-units-of-measure/SKILL.md) (`INV_MANAGE_UNITS_OF_MEASURE`)
2. [Manage Unit of Measure Classes](manage-unit-of-measure-classes/SKILL.md) (`ORA_MANAGE_UNIT_OF_MEASURE_CLASSES`)
3. [Manage Units of Measure for Interclass Conversion](manage-units-of-measure-for-interclass-conversion/SKILL.md) (`RCS_MANAGE_UOM_INTER_CLASS_CONV`)
4. [Manage Units of Measure for Intraclass Conversion](manage-units-of-measure-for-intraclass-conversion/SKILL.md) (`RCS_MANAGE_UOM_INTRA_CLASS_CONV`)
5. [Manage Units of Measure Descriptive Flexfields](manage-units-of-measure-descriptive-flexfields.md) (`ORA_RCS_MANAGE_UOM_DESCRIPTIVE_FLEXFIELDS`)
6. [Manage Units of Measure Profiles](manage-units-of-measure-profiles.md) (`ORA_RCS_MANAGE_UOM_PROFILE`)
7. [Manage Lifecycle Phases](manage-lifecycle-phases.md) (`EGP_MANAGE_LIFECYCLE_PHASES`)
8. [Manage Default Item Class](manage-default-item-class.md) (`EGP_MANAGE_DEFAULT_ITEM_CLASS`)
9. [Manage Item Statuses](manage-item-statuses/SKILL.md) (`EGP_MANAGE_ITEM_STATUSES`)
10. [Import Items](import-items/SKILL.md) (`EGP_IMPORT_ITEMS`)
11. [Manage Trading Partner Item Descriptive Flexfields](manage-trading-partner-item-descriptive-flexfields/SKILL.md) (`EGP_TRADING_PARTNER_ITEMS_DFFS`)
12. [Manage Item Relationship Descriptive Flexfields](manage-item-relationship-descriptive-flexfields/SKILL.md) (`EGP_ITEM_RELATIONSHIP_DFFS`)
13. [Manage Related Item Subtypes](manage-related-item-subtypes/SKILL.md) (`EGP_MANAGE_RELATED_ITEM_SUBTYPES`)
14. [Manage Cross Reference Types](manage-cross-reference-types/SKILL.md) (`EGP_MANAGE_CROSS_REFERENCE_TYPES`)
15. [Manage Related Item Types](manage-related-item-types/SKILL.md) (`ORA_MANAGE_RELATED_ITEM_TYPES`)
16. [Manage Item Types](manage-item-types.md) (`EGP_MANAGE_ITEM_TYPES`)
17. [Manage Item Profile Options](manage-item-profile-options.md) (`EGP_MANAGE_ITEM_PROFILE_OPTIONS`)
18. [Manage Advanced Item Profile Options](manage-advanced-item-profile-options.md) (`EGO_MANAGE_ADVANCED_ITEM_PROFILE_OPTIONS`)
19. [Manage Operational Attributes Groups](manage-operational-attributes-groups/SKILL.md) (`EGP_MANAGE_OPERATIONAL_ATTRIBUTES_GROUPS`)
20. [Manage Item Descriptive Flexfields](manage-item-descriptive-flexfields/SKILL.md) (`EGP_MANAGE_ITEM_DESCRIPTIVE_FLEXFIELDS`)
21. [Manage Item Attribute Groups and Attributes](manage-item-attribute-groups-and-attributes/SKILL.md) (`EGO_MANAGE_ITEM_ATTRIBUTE_GROUPS_AND_ATTRIBUTES`)
22. [Deploy Item Extensible Flexfields](deploy-item-extensible-flexfields/SKILL.md) (`EGO_DEPLOY_EFFS`)
23. [Manage Item Classes](manage-item-classes/SKILL.md) (`EGO_MANAGE_ITEM_CLASSES`)
24. [Manage Product and Child Value Sets](manage-product-and-child-value-sets/SKILL.md) (`EGP_MANAGE_PRODUCT_VALUE_SETS`)
25. [Manage Item Class Descriptive Flexfields](manage-item-class-descriptive-flexfields/SKILL.md) (`EGP_ITEM_CLASS_DFFS`)
26. [Manage Attachment Categories for Product Management](manage-attachment-categories-for-product-management/SKILL.md) (`ORA_EGP_MANAGE_ATTACH_CAT_FOR_PIM`)
27. [Manage Import Maps](manage-import-maps/SKILL.md) (`EGI_MANAGE_IMPORT_MAPS`)
28. [Reference Organization Items Import](reference-organization-items-import/SKILL.md) (`CUSTOM_EGP_FBDI_IMPORT_REF_ORG_ITEMS`)

## Inputs

- `implementation_objective`
- `project_context`
- `items_scope`
- `items_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated nested setup-task skills for task-level planning, sequencing, setup-data routing, and validation. Track token usage for any generated project artifact or skill-run record using the manifest policy.
