---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.service-logistics.stocking-locations"
name: "Stocking Locations Setup Task Guidance"
description: "Provides task-specific setup guidance for Stocking Locations under the Service Logistics functional area."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Service Logistics"
functional_area_code: "ORA_RCL"
task_code: "ORA_RCL_STOCKING_LOCATIONS"
task_name: "Stocking Locations"
parent_skill_id: "scm.manufacturing-and-supply-chain-materials-management.service-logistics"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "REST"
businessObject: "stockingLocations"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "hybrid"
owner_team: "SCM manufacturing and supply chain materials management pillar team"
version: "0.1.6"
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
  - "explicit_site_dedicated_location_delete_request"
  - "operation_specific_site_dedicated_location_delete_approval"
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
  - "site_dedicated_location_delete_result"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "shared.implementation-planning.offering-task-map-builder"
  - "shared.implementation-planning.task-dependency-resolver"
  - "shared.setup-export.functional-area-export"
uses_core:
  - "core.data-loader"
  - "core.data-loader.task-hook"
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
  - "configuration_blueprints"
  - "validation_results"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/service-logistics/stocking-locations/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/service-logistics/stocking-locations/current/"
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
  - "Delegates all approved parent and Site-Dedicated Location child creates, updates and deletions exclusively to core.data-loader."
  - "Performs declared read-only identity checks and saved-result verification; no direct REST mutations."
required_privileges:
  - "Access to the selected Fusion environment and privileges to view stocking locations, technician assignments, organization/subinventory LOVs, customer accounts and addresses, and site-dedicated children; Data Loader upload/import privileges for all mutations; update privileges for an approved parent or child update; operation-specific delete privileges for an approved parent or child deletion."
---

# Stocking Locations Setup Task Guidance

## Purpose

Set up Unmanned, Manned, Site Dedicated, and Technician Field Parts Stocking Locations for use throughout Service Logistics: replenishment sourcing and ordering, receiving, transfers, and returns. This task owns stocking-location configuration and its customer-site relationships; operational parts transactions remain with their corresponding Service Logistics tasks.

Support editing or deleting an existing RCL stocking location only when it is not tied to a field technician. Support adding and deleting Site-Dedicated Location relationships under an existing stocking location. These relationships create site-dedicated stocking-location addresses in RCL_SITE_DEDICATED_LOCATIONS and define the customer sites for which parts in the associated Service Logistics stocking location may be used. The child record represents the relationship; it does not create or delete the customer's master address.

Delegate all parent and child creates, updates (PATCH) and deletions (DELETE) exclusively to core.data-loader, using business object stockingLocations and child section siteDedicatedLocations. The core.fusion-api.rest-api-client dependency is read-only for declared reference and verification checks. Validate organization, subinventory, customer-site identity, current relationship, operation-specific privileges, and applicable technician-assignment restrictions before execution; verify saved results or absence afterward. Use the existing approval, diagnostics, and no-replay controls in the operation workflows below. Changing technician assignments is outside this skill's mutation scope.

## Setup Task Metadata

- Task name: `Stocking Locations`
- Task code: `ORA_RCL_STOCKING_LOCATIONS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `REST`
- Business Object: `stockingLocations`

## CSV Export, Import, and Validation Workflow

Use `shared.validation.reference-data-validator` for reference-data validation alongside the task's organization, subinventory, and customer-site resolvers. Task-level export, setup-data validation, and import retain the routes below.

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export task setup data with `shared.setup-export.task-level-export`.
2. Validate exported or prepared task setup data with `shared.validation.setup-data-validator`.
3. Import setup task data with `core.data-loader` using stockingLocations as the BusinessObject.

Use this task metadata when invoking those skills:

- Offering: `Manufacturing and Supply Chain Materials Management`
- Functional area / Setup Object: `Service Logistics`
- Setup task name: `Stocking Locations`
- Setup task code: `ORA_RCL_STOCKING_LOCATIONS`


## Update a Stocking Location

1. Resolve exactly one current parent from its exact name or verified organization/subinventory pair. Require all supplied selectors to agree.
2. Validate requested changes against current Data Loader metadata. Resolve type meanings through the named lookup; never invent codes. Retain current values for readback comparison.
3. Execute check_stocking_location_technician_assignment during declared read-only validation. Require absent, count zero, complete pagination and verified visibility. Assigned or unknown blocks; do not unassign technicians.
4. Prepare verified parent keys, requested changes and loader-required fields with RestAction=PATCH. Include no child operations. Reject POST fallback rows in generated update samples.
5. Follow [Data Loader Mutation Workflow](#data-loader-mutation-workflow). After confirmed completion, verify the same parent and requested saved values. Report mismatch without replay.

## Update a Site-Dedicated Location

1. Resolve the exact parent and current child using resolve_site_dedicated_location_by_exact_identity. Use current selectors, never replacement values. Zero or multiple matches blocks; do not create a missing child.
2. Resolve replacement customer/site values through resolve_customer_party_site. Require the authoritative PartySiteId/PartySiteNumber pair. Reject parent reassignment and conflicting selectors. Check duplicates excluding only the selected child; an unchanged saved pair is a no-op.
3. Prepare one child row with verified parent/child linkage, RestAction=PATCH, requested changes and loader-required fields. Include no parent data operation or other child row.
4. Follow [Data Loader Mutation Workflow](#data-loader-mutation-workflow). After confirmed completion, verify the original child key, parent and requested saved values using verify_site_dedicated_location_relationship.

## Create a Site-Dedicated Location and Relationship

1. Resolve exactly one existing parent and active customer/site through the named reference contracts. Verify all supplied selectors, authoritative PartySiteId, exact PartySiteNumber and absence of the relationship.
2. Prepare only requested child rows with verified linkage and RestAction=POST. Omit generated SiteDedicatedLocId and unspecified optional values. Never include a parent data operation in a child-only load.
3. Let Data Loader own current template, hierarchy and packaging validation. Do not force historical root-header rules or hand-build an archive outside its preparation workflow.
4. Follow [Data Loader Mutation Workflow](#data-loader-mutation-workflow). After confirmed completion, verify the saved relationship. Do not claim the existing parent was created. Duplicates block creation.

## Delete a Stocking Location

1. Resolve the exact parent and verify supplied selectors. Verified absence is a no-op; ambiguous, incomplete or denied reads block.
2. Require a complete child check with zero relationships. Do not cascade or delete children implicitly.
3. Execute check_stocking_location_technician_assignment. Require absent, count zero, complete pagination and verified assignment visibility. Assigned or unknown blocks.
4. Prepare only loader-required verified parent keys and RestAction=DELETE. Confirm current loader support and operation-specific privileges. Include no sampled or child records.
5. Follow [Data Loader Mutation Workflow](#data-loader-mutation-workflow). After confirmed completion verify parent absence. Uncertain submission followed by absence is reconciled absence, not verified successful deletion. Recreation requires a separate request.

## Delete a Site-Dedicated Location

1. Resolve one exact parent and current child through resolve_site_dedicated_location_by_exact_identity. Require all customer/site selectors to agree and complete pagination. Verified zero matches is a no-op; ambiguity or failed reads block.
2. Retain the parent and sibling identity set transiently for preservation checks. Verify operation-specific privileges and current loader child-delete support.
3. Prepare only the selected child row with verified parent/child linkage, loader-required keys and RestAction=DELETE. No parent data operation, customer master-address change or sibling deletion is allowed.
4. Follow [Data Loader Mutation Workflow](#data-loader-mutation-workflow). After confirmed completion verify child absence, parent existence and unchanged sibling identities. Report verification failures without compensation or replay.

## Data Loader Mutation Workflow

This route is mandatory for parent and child POST, PATCH and DELETE. Delegate mutations exclusively to `core.data-loader`; task-declared read-only checks do not authorize another executor.

1. Preflight project, exact task, environment, Run Book context, operation, current Data Loader metadata and operation-specific privileges. Use the current core immutable-artifact workflow in `core/data-loader/SKILL.md`.
2. Prepare operation-specific input: explicit RestAction=POST, PATCH or DELETE, verified keys and only requested changes plus loader-required fields. Sample generation is not submission. Core owns conversion, hierarchy, packaging and source validation.
3. Core prepares and persists the final immutable upload artifact before invoking Task Hook. Validate its exact bytes using the task Operation Contract and operation-aware Task Nodes: parent_create, parent_update, parent_delete, child_create, child_update or child_delete. Run applicable identity, technician, customer-site and preservation checks before approval. Corrections require a newly prepared artifact and fresh validation; never modify the artifact being reviewed.
4. Require every applicable rule to pass. RCL.SLOC.NOOP stops an all-no-op request without approval, upload or initiation. Mixed actions or mixed no-op/actionable rows require separate corrected sources. Unsupported loader metadata blocks; never force POST defaults or use direct REST as fallback.
5. Let core build its Task Hook preview and retain its internal preflight/Task Hook envelopes. Show the normal core approval report and follow its authoritative approval policy once. No extra task-level approval is required. Bind submission to the exact immutable artifact, environment and Run Book context.
6. After approval, use core's approved-preflight invocation. Core verifies the saved artifact and context and submits those same bytes without reopening the source, rebuilding, refreshing metadata or repeating reference validation. Missing/changed artifacts or context mismatch require fresh preparation and approval. Retain artifacts and envelopes after partial or uncertain failure for reconciliation; let core clean up its internal state after accepted initiation. Never replay upload/initiation.
7. Display the complete helper report and return immediately after accepted initiation. Follow Data Loader Results for explicitly requested status or verification. Keep load outcome separate from readback; persist only permitted redacted project evidence. Core artifacts and envelopes stay in private ignored staging outside tracked files and project workspaces.

Use Data Loader failure classification and recovery. Missing operation support blocks execution and never authorizes a different route.

## Input Selection and Import Preparation

Read the task-scoped validation, lookup, defaulting and error resources. Preserve the selected operation throughout preparation.

1. Resolve organization name/code/ID consistently and select subinventory within that organization. Reject conflicting aliases. An exact existing parent can supply verified references; never split its name to manufacture IDs.
2. Validate coordinates, field lengths, exact integer IDs and current type/condition meanings. Leave optional unspecified values blank.
3. Parent create requires absence; update/delete requires a uniquely resolved target (verified deletion absence is a no-op). Child create requires an existing parent and absent relationship; update/delete selects the current child.
4. Reject duplicate source targets and preserve row-level errors. Create-only defaults must not override PATCH/DELETE. Child-only operations contain no parent data row; current loader hierarchy rules govern conversion.
5. Follow [Data Loader Mutation Workflow](#data-loader-mutation-workflow) for validation, approval and submission. Corrections require fresh immutable-artifact preparation and validation. Never reuse mappings across environments.

## Data Loader Results

Always show the complete Data Loader helper report for the stage reached, including parent and child updates and deletions. Accepted initiation is not completed loading.

For an explicit status/results request, use core.data-loader's current status workflow with the returned request ID or Content ID. Show its exact data-set status, Total/Loaded/Failed counts, business errors and applicable log links. Do not automatically poll after initiation or resubmit because status is pending. If results are unavailable, report that state and the next status-check action.

After confirmed load completion and when saved details are requested, use the declared read-only verification contracts. Updates require the same identity and approved saved values; deletion requires absence and applicable parent/sibling preservation. Show environment, operation, saved identity, loader outcome and verification in a table. A target already absent without submission is a no-op; uncertain submission plus absence is reconciled absence. Do not claim a parent was created by child-only work or infer component counts from aggregate results.

Keep core.data-loader authoritative for approval, transport, status, error retrieval and formatting. Results requests never authorize another load.

## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task’s business object.

1. Confirm that `stockingLocations` is the exact registered Data Loader business object.
2. Generate the default editable XLSX sample through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "stockingLocations" \
     --output-dir "<project-artifact-directory>"
   ```

3. Keep the generated workbooks together:
   - editable sample
   - attribute-details workbook
   - key-fields workbook
4. Review the generated headers and key fields before preparing source data. The operation uses read-only Fusion metadata and does not upload or import data.
5. Use the generated editable workbook as the starting point for the later Data Loader preparation and approval workflow.



## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Stocking Locations` under `Service Logistics`.
