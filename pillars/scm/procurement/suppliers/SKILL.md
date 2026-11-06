---
skill_id: "scm.procurement.suppliers"
name: "Suppliers Implementation Guidance"
description: "Provides SCM Procurement implementation guidance for the Suppliers functional area."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "Suppliers"
functional_area_code: "ORA_EGP_SUPPLIERS"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM procurement pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "suppliers_scope"
  - "suppliers_requirements"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/suppliers/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/suppliers/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/procurement/suppliers/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "POZ_SPECIFY_SUPPLIER_NUMBERING"
  - "POZ_CONFIGURE_SUPPLIER_REGISTRATION"
  - "ORA_POZ_CONFIGURE_SUPPLIER_PROFILE_CHANGE_REQUEST"
  - "ORA_POZ_CONFIGURE_NEW_SUPPLIER_NOTIFICATION"
  - "ORA_POZ_MANAGE_CERTIFYING_AGENCIES"
  - "POZ_MANAGE_SUPPLIER_TYPE_LOOKUP"
  - "POZ_MANAGE_TAX_ORGANIZATION_TYPE_LOOKUP"
  - "POZ_MANAGE_SUPPLIER_DESCRIPTIVE_FLEXFIELDS"
  - "ORA_MANAGE_SUPPLIER_BANK_ACCOUNT_DESCRIPTIVE_FLEXFIELDS"
  - "POZ_MANAGE_SUPPLIER_REGISTRATION_DESCRIPTIVE_FLEXFIELDS"
  - "POZ_MANAGE_BUSINESS_CLASSIFICATION_LOOKUP"
  - "POZ_MANAGE_MINORITY_GROUP_LOOKUP"
  - "POZ_MANAGE_SUPPLIER_VALUE_SETS"
  - "POZ_MANAGE_SUPPLIER_REGISTRATION_VALUE_SETS"
  - "ORA_POZ_MANAGE_SUPPLIER_PROFILE_OPTIONS"
  - "POR_MANAGE_SUPPLIER_PRODUCTS_AND_SERVICES_CATEGORY_HIERARCHY"
  - "ORA_POZ_MANAGE_SUPPLIER_MESSAGES"
  - "POZ_IMPORT_SUPPLIERS"
  - "ORA_CMK_COLLAB_MESG_SERVICE_PROVIDER"
  - "ORA_CMK_MNGE_SIMPLIFIED_COLLAB_MSG_CONFIG"
  - "ORA_POZ_CONFIGURE_SUPPLIER_OUTBOUND_SYNCHRONIZATION_SERVICE"
  - "ORA_MANAGE_ADDRESS_VERIFICATION_CLOUD_TO_CX_CLOUD_INTEGRATION"
  - "HZ_MANAGE_TRADING_COMMUNITY_PERSON_DESCRIPTIVE_FLEXFIELDS"
  - "HZ_TRADING_COMMUNITY_ORGANIZATION_SITE_DESC_FLEXFIELDS"
  - "ZCQ_MANAGE_SERVER_CONFIGURATIONS"
  - "HZ_MANAGE_GEOGRAPHIES"
  - "HZ_MANAGE_ADDRESS_FORMATS"
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

# Suppliers Implementation Guidance

## Purpose

Provides SCM Procurement implementation guidance for the Suppliers functional area.

## When to Use

Use this functional-area skill after Procurement scope is confirmed and the project needs suppliers setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `SCM`
- Offering: `Procurement` (`PO_PROCUREMENT`)
- Functional area / Setup Object: `Suppliers` (`ORA_EGP_SUPPLIERS`)

## Setup Tasks

1. [Specify Supplier Numbering](specify-supplier-numbering/SKILL.md) (`POZ_SPECIFY_SUPPLIER_NUMBERING`)
2. [Configure Supplier Registration](configure-supplier-registration/SKILL.md) (`POZ_CONFIGURE_SUPPLIER_REGISTRATION`)
3. [Configure Supplier Profile Change Request](configure-supplier-profile-change-request/SKILL.md) (`ORA_POZ_CONFIGURE_SUPPLIER_PROFILE_CHANGE_REQUEST`)
4. [Configure New Supplier Notification](configure-new-supplier-notification/SKILL.md) (`ORA_POZ_CONFIGURE_NEW_SUPPLIER_NOTIFICATION`)
5. [Manage Certifying Agencies](manage-certifying-agencies/SKILL.md) (`ORA_POZ_MANAGE_CERTIFYING_AGENCIES`)
6. [Manage Supplier Type Lookup](manage-supplier-type-lookup/SKILL.md) (`POZ_MANAGE_SUPPLIER_TYPE_LOOKUP`)
7. [Manage Tax Organization Type Lookup](manage-tax-organization-type-lookup/SKILL.md) (`POZ_MANAGE_TAX_ORGANIZATION_TYPE_LOOKUP`)
8. [Manage Supplier Descriptive Flexfields](manage-supplier-descriptive-flexfields/SKILL.md) (`POZ_MANAGE_SUPPLIER_DESCRIPTIVE_FLEXFIELDS`)
9. [Manage Supplier Bank Account Descriptive Flexfields](manage-supplier-bank-account-descriptive-flexfields/SKILL.md) (`ORA_MANAGE_SUPPLIER_BANK_ACCOUNT_DESCRIPTIVE_FLEXFIELDS`)
10. [Manage Supplier Registration Descriptive Flexfields](manage-supplier-registration-descriptive-flexfields/SKILL.md) (`POZ_MANAGE_SUPPLIER_REGISTRATION_DESCRIPTIVE_FLEXFIELDS`)
11. [Manage Business Classification Lookup](manage-business-classification-lookup/SKILL.md) (`POZ_MANAGE_BUSINESS_CLASSIFICATION_LOOKUP`)
12. [Manage Minority Group Lookup](manage-minority-group-lookup/SKILL.md) (`POZ_MANAGE_MINORITY_GROUP_LOOKUP`)
13. [Manage Supplier Value Sets](manage-supplier-value-sets/SKILL.md) (`POZ_MANAGE_SUPPLIER_VALUE_SETS`)
14. [Manage Supplier Registration Value Sets](manage-supplier-registration-value-sets/SKILL.md) (`POZ_MANAGE_SUPPLIER_REGISTRATION_VALUE_SETS`)
15. [Manage Supplier Profile Options](manage-supplier-profile-options/SKILL.md) (`ORA_POZ_MANAGE_SUPPLIER_PROFILE_OPTIONS`)
16. [Manage Supplier Products and Services Category Hierarchy](manage-supplier-products-and-services-category-hierarchy/SKILL.md) (`POR_MANAGE_SUPPLIER_PRODUCTS_AND_SERVICES_CATEGORY_HIERARCHY`)
17. [Manage Supplier Messages](manage-supplier-messages/SKILL.md) (`ORA_POZ_MANAGE_SUPPLIER_MESSAGES`)
18. [Import Suppliers](import-suppliers/SKILL.md) (`POZ_IMPORT_SUPPLIERS`)
19. [Manage Collaboration Messaging Service Providers](manage-collaboration-messaging-service-providers/SKILL.md) (`ORA_CMK_COLLAB_MESG_SERVICE_PROVIDER`)
20. [Manage Simplified Collaboration Messaging Configuration](manage-simplified-collaboration-messaging-configuration/SKILL.md) (`ORA_CMK_MNGE_SIMPLIFIED_COLLAB_MSG_CONFIG`)
21. [Configure Supplier Outbound Synchronization Service](configure-supplier-outbound-synchronization-service.md) (`ORA_POZ_CONFIGURE_SUPPLIER_OUTBOUND_SYNCHRONIZATION_SERVICE`)
22. [Manage Integration with Oracle Verification Services](manage-integration-with-oracle-verification-services.md) (`ORA_MANAGE_ADDRESS_VERIFICATION_CLOUD_TO_CX_CLOUD_INTEGRATION`)
23. [Manage Trading Community Person Descriptive Flexfields](../../../cx/customer-data-management/trading-community-foundation/manage-trading-community-person-descriptive-flexfields/SKILL.md) (`HZ_MANAGE_TRADING_COMMUNITY_PERSON_DESCRIPTIVE_FLEXFIELDS`)
24. [Manage Trading Community Organization Site Descriptive Flexfields](../../../cx/customer-data-management/trading-community-foundation/manage-trading-community-organization-site-descriptive-flexfields/SKILL.md) (`HZ_TRADING_COMMUNITY_ORGANIZATION_SITE_DESC_FLEXFIELDS`)
25. [Manage Server Configurations](../../../cx/customer-data-management/data-quality-foundation/manage-server-configurations/SKILL.md) (`ZCQ_MANAGE_SERVER_CONFIGURATIONS`)
26. [Manage Geographies](../../../cx/customer-data-management/enterprise-profile/manage-geographies/SKILL.md) (`HZ_MANAGE_GEOGRAPHIES`)
27. [Manage Address Formats](../../../cx/customer-data-management/trading-community-foundation/manage-address-formats/SKILL.md) (`HZ_MANAGE_ADDRESS_FORMATS`)

For the five CX-owned tasks above, delegate execution to the linked skill; that skill determines the inputs, validation, execution route, and approvals. Do not duplicate its guidance in Suppliers.

## Related Supplier Approval Tasks

These manual tasks belong to the Procurement Approval Management functional area. Use the linked task guidance for execution; the links here provide supplier-focused discovery without duplicating that guidance.

- [Manage Internal Supplier Registration Approvals](../approval-management/manage-internal-supplier-registration-approvals.md) (`ORA_POZ_MANAGE_INTERNAL_SUPPLIER_REGISTRATION_APPROVALS`)
- [Manage Supplier Registration Approvals](../approval-management/manage-supplier-registration-approvals.md) (`ORA_POZ_MANAGE_SUPPLIER_REGISTRATION_APPROVALS`)
- [Manage Internal Supplier Profile Change Approvals](../approval-management/manage-internal-supplier-profile-change-approvals.md) (`ORA_POZ_MANAGE_INTERNAL_SUPPLIER_PROFILE_CHANGE_APPROVALS`)
- [Manage Supplier Spend Authorization Approvals](../approval-management/manage-supplier-spend-authorization-approvals.md) (`ORA_POZ_MANAGE_SUPPLIER_SPEND_AUTHORIZATION_APPROVALS`)
- [Manage Supplier Profile Change Approvals](../approval-management/manage-supplier-profile-change-approvals.md) (`ORA_POZ_MANAGE_SUPPLIER_PROFILE_CHANGE_APPROVALS`)

## Inputs

- `implementation_objective`
- `project_context`
- `suppliers_scope`
- `suppliers_requirements`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the generated nested setup-task skills for task-level planning, sequencing, setup-data routing, and validation. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Reuse Supplied Supplier Inputs

Before asking for business values in an automated Supplier task, read the
available project requirements, decisions, conversation answers, and supplied
spreadsheets, CSVs, images, or pasted tables. Reuse clearly mapped values within
the requested task scope; do not require the user to restate them or complete a
new questionnaire. Retain source references for interpreted values in the
task's existing project outputs, not in reusable skill files.

Ask only for required values that remain missing, unreadable, ambiguous,
conflicting, or unsupported after the declared validation and reference
lookups. Group related gaps in one concise prompt and omit answered items.
Distinguish requested changes from current-state screenshots or examples;
blank cells are not instructions to clear a value. Preserve out-of-scope
settings and explicit Preserve choices. Supplied snapshots do not replace a
fresh environment read where the task requires one.

For delegated tasks, pass the supplied values, artifacts, source references,
and unresolved gaps to the owning skill. Let it determine required inputs,
validation, execution, and approval; do not add a Supplier-side questionnaire.
For manual tasks, retain their instruction-only behavior: tailor guidance to
supplied context without collecting configuration values or credentials in
chat. Clarify task identity or scope only when necessary.

Reuse of inputs does not bypass required validation, prerequisite checks, or
the selected execution route's live approval gate. Do not request approval
twice for the same operation.

## Supplier Setup Run Book Scope

When planning or simulating a Supplier Setup run book, include only the
requested setup tasks. Do not add `Import Suppliers` by default.

If the proposed run book does not already contain `Import Suppliers` and the
user has not stated whether supplier data will be migrated, ask once:

> Will this implementation include supplier-data migration? If so, add Import
> Suppliers as a separate post-configuration stage.

If the user confirms migration, add `Import Suppliers` after the required
configuration tasks. Add its child import tasks only when the user selects the
applicable entities. Do not ask again when the run book already includes
`Import Suppliers`, or when the user has excluded migration.
