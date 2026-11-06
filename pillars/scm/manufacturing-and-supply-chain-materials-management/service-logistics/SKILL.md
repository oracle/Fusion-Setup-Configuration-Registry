---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.service-logistics"
name: "Service Logistics Implementation Guidance"
description: "Provides SCM Manufacturing and Supply Chain Materials Management implementation guidance for the Service Logistics functional area."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Service Logistics"
functional_area_code: "ORA_RCL"
type: "planning"
execution_mode: "hybrid"
owner_team: "SCM manufacturing and supply chain materials management pillar team"
version: "0.1.3"
inputs:
  - "implementation_objective"
  - "project_context"
  - "service_logistics_scope"
  - "service_logistics_requirements"
  - "stocking_location_operation_and_input_values"
  - "organization_and_subinventory_selection"
  - "site_dedicated_location_customer_and_site_selection"
  - "current_site_dedicated_location_identity_for_update"
  - "explicit_stocking_location_update_request"
  - "operation_specific_update_approval"
  - "explicit_site_dedicated_location_update_request"
  - "operation_specific_site_dedicated_location_update_approval"
  - "explicit_stocking_location_delete_request"
  - "operation_specific_delete_approval"
outputs:
  - "functional_area_setup_plan"
  - "configuration_guidance"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
  - "resolved_stocking_location_input_mapping"
  - "site_dedicated_location_create_and_relationship_result"
  - "stocking_location_update_result"
  - "site_dedicated_location_update_result"
  - "stocking_location_delete_result"
depends_on:
  - "shared.implementation-planning.offering-task-map-builder"
  - "shared.implementation-planning.task-dependency-resolver"
  - "shared.setup-export.functional-area-export"
uses_core:
  - "core.data-loader"
  - "core.fusion-api.rest-api-client"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/service-logistics/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/service-logistics/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "design_decision"
    default_location: "project/{project_id}/decisions/"
    versioning_policy: "append-only"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/service-logistics/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
required_setup_tasks:
  - "ORA_RCL_STOCKING_LOCATIONS"
  - "ORA_RCL_BILLING_TYPES"
  - "ORA_RCL_FIELD_SERVICE_TECHNICIANS"
  - "ORA_RCL_RESOURCE_ITEM_MAPPING"
  - "ORA_RCL_RETURN_ROUTING_RULES"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "For an explicit Stocking Locations parent or Site-Dedicated Location child create request, prepares a validated import and delegates the approved upload and initiation to core.data-loader."
  - "Delegates explicit Stocking Locations parent and Site-Dedicated Location child updates exclusively to core.data-loader using its validated session and submission authorization."
  - "Delegates explicit Stocking Locations parent and Site-Dedicated Location child deletions exclusively to core.data-loader; performs only declared read-only identity and preservation checks."
required_privileges:
  - "Access to the selected Fusion environment and privileges to view stocking locations, organization/subinventory LOVs, customer accounts and addresses, and site-dedicated children; Data Loader upload/import privileges for creation; update privileges for an approved parent or child update; delete privileges for an approved parent deletion."
---

# Service Logistics Implementation Guidance

## Purpose

Provides SCM Manufacturing and Supply Chain Materials Management implementation guidance for the Service Logistics functional area.

## When to Use

Use this functional-area skill after Manufacturing and Supply Chain Materials Management scope is confirmed and the project needs service logistics setup planning, baseline export, import sequencing, or validation checkpoints.

## Catalog Metadata

- Pillar: `SCM`
- Offering: `Manufacturing and Supply Chain Materials Management` (`ORA_MANUFACTURING_AND_SUPPLY_C`)
- Functional area / Setup Object: `Service Logistics` (`ORA_RCL`)

## Setup Tasks

1. [Stocking Locations](stocking-locations/SKILL.md) (`ORA_RCL_STOCKING_LOCATIONS`)
2. [Billing Types](billing-types/SKILL.md) (`ORA_RCL_BILLING_TYPES`)
3. [Field Service Technicians](field-service-technicians/SKILL.md) (`ORA_RCL_FIELD_SERVICE_TECHNICIANS`)
4. [Manage Resource to Item Mapping](manage-resource-to-item-mapping/SKILL.md) (`ORA_RCL_RESOURCE_ITEM_MAPPING`)
5. [Return Routing Rules](return-routing-rules/SKILL.md) (`ORA_RCL_RETURN_ROUTING_RULES`)

## Inputs

- `implementation_objective`
- `project_context`
- `service_logistics_scope`
- `service_logistics_requirements`
- `stocking_location_operation_and_input_values`
- `organization_and_subinventory_selection`
- `site_dedicated_location_customer_and_site_selection`
- `current_site_dedicated_location_identity_for_update`
- `explicit_stocking_location_update_request`
- `operation_specific_update_approval`
- `explicit_site_dedicated_location_update_request`
- `operation_specific_site_dedicated_location_update_approval`
- `explicit_stocking_location_delete_request`
- `operation_specific_delete_approval`

## Outputs

- `functional_area_setup_plan`
- `configuration_guidance`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`
- `resolved_stocking_location_input_mapping`
- `site_dedicated_location_create_and_relationship_result`
- `stocking_location_update_result`
- `site_dedicated_location_update_result`
- `stocking_location_delete_result`

## Implementation Notes

Select [Site-Dedicated Location creation and relationship](stocking-locations/SKILL.md#create-a-site-dedicated-location-and-relationship) for an explicit child create. Resolve the existing parent and the customer's active site, including its authoritative PartySiteId, before preparing a child-only stockingLocations import. For an existing child update, keep the current child selector separate from the requested replacement customer/site. Read [input validation](stocking-locations/ora-resource/ora_input_validation.md), [reference lookups](stocking-locations/ora-resource/ora_reference_lookups.md), [defaults](stocking-locations/ora-resource/ora_defaulting_rules.md), and [error handling](stocking-locations/ora-resource/ora_error_handling.md) for the selected operation. All creates, updates and deletions use the task Data Loader mutation workflow. The registry must validate the selected operation; unsupported rules block submission.

For parent or Site-Dedicated Location child updates and deletions, select the corresponding task workflow and [Data Loader Mutation Workflow](stocking-locations/SKILL.md#data-loader-mutation-workflow). Use RestAction=PATCH for updates and RestAction=DELETE for deletions in validated loader records. Never dispatch mutation endpoints through the REST client. Task validation does not request approval; core.data-loader owns the single session preview and submission-authorization process. The REST client is used only for declared read-only lookups and verification.

Use the generated setup-task metadata files for task-level planning and sequencing. Track token usage for any generated project artifact or skill-run record using the manifest policy.

For Stocking Locations imports and their Site Dedication child imports, follow the [task's Data Loader Results workflow](stocking-locations/SKILL.md#data-loader-results). Display the helper report for the stage reached. For explicit status/results requests, use the Data Loader status workflow; do not automatically poll after initiation or report initiation as completed loading. Keep this reporting preference scoped to Stocking Locations.

Before preparing a Stocking Locations import, follow [Input Selection and Import Preparation](stocking-locations/SKILL.md#input-selection-and-import-preparation). Resolve organization name/code/ID to a verified OrganizationId, select the subinventory under that organization, and retain exact mappings in the source. Use the task-scoped [reference resolvers](stocking-locations/ora-resource/ora_reference_lookups.md) and compiled registry; do not skip these checks merely because Data Loader schema validation passed. Identity resolution and preview are read-only; mutations remain subject to core.data-loader approval and submission gates.

## Business Object Operation Policy

Select each nested task's declared workflow and current capability gate. Catalog flags and a REST import mode do not establish a working business-record reader. Field Service Technicians and Manage Resource to Item Mapping currently support Data Loader metadata/sample generation and explicitly requested status/diagnostics only. Their business/reference reads, saved-record verification and identity-dependent create/update/delete preparation are unsupported until a reviewed core reader and task integration are delivered. Stop with catalog_or_metadata_mismatch before those operations; no alternate client, browser or caller-provided evidence may bypass the gate.

## Preflight, Failure Handling and Redaction

Before any external operation, load the selected task's workflow, reference guidance and ora_error_handling.md. Verify project and environment identity, task/catalog match, declared capability, required privileges, safe artifact paths and applicable source validation. Delegate mutation approval, immutable-artifact integrity, bounded retries, timeouts and process diagnostics to core.data-loader. A missing capability or failed prerequisite stops the selected operation before side effects; approval cannot waive it.

Retain only redacted capability, validation, status and run evidence in declared project locations. Never persist credentials, token caches, customer values, reference rows or sensitive source/response bodies under project/ or tracked files. Keep permitted customer inputs in memory or private ignored staging outside project/. Do not replay uncertain mutations; reconcile through the selected core status workflow and require fresh validation for corrected input.
