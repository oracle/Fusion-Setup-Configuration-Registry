---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.items.configure-remaining-shelf-life-rule"
name: "Configure Remaining Shelf Life Rule Setup Task Guidance"
description: "Provides task-specific setup guidance for Configure Remaining Shelf Life Rule under the Items functional area."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Items"
functional_area_code: "ORA_EGP_FA_ITEMS"
task_code: "ORA_MSC_CONFIGURE_REMAINING_SHELF_LIFE_RULE"
task_name: "Configure Remaining Shelf Life Rule"
parent_skill_id: "scm.manufacturing-and-supply-chain-materials-management.items"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "REST"
businessObject: "remainingShelfLifeRest"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM manufacturing and supply chain materials management pillar team"
version: "0.1.1"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "core.data-loader"
  - "core.fusion-api.rest-api-client"
uses_core:
  - "core.data-loader"
  - "core.fusion-api.rest-api-client"
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/items/configure-remaining-shelf-life-rule/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/items/configure-remaining-shelf-life-rule/current/"
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
side_effects: []
required_privileges: []
---

# Configure Remaining Shelf Life Rule Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Configure Remaining Shelf Life Rule` under `Items`.

## Setup Task Skill Contract

- task_code: `ORA_MSC_CONFIGURE_REMAINING_SHELF_LIFE_RULE`
- task_name: `Configure Remaining Shelf Life Rule`
- parent_skill_id: `scm.manufacturing-and-supply-chain-materials-management.items`
- pillar: `SCM`
- offering: `Manufacturing and Supply Chain Materials Management`
- functional_area: `Items`
- functional_area_code: `ORA_EGP_FA_ITEMS`
- available_flag: `Y`
- export_import_supported_flag: `N`
- csv_export_import_supported_flag: `N`
- dataloader_import_mode: `REST`
- businessObject: `remainingShelfLifeRest`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Configure Remaining Shelf Life Rule` under `Items`.

## Setup Task Metadata

- Task name: `Configure Remaining Shelf Life Rule`
- Task code: `ORA_MSC_CONFIGURE_REMAINING_SHELF_LIFE_RULE`
- Available: `Y`
- Export/import supported: `N`
- CSV export/import supported: `N`
- CSV export/import routing: `not supported`
- Data Loader import mode: `REST`
- Business Object: `remainingShelfLifeRest`

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `N`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

Do not route CSV export work to `shared.setup-export.task-level-export` or CSV import work to `core.data-loader` unless live Fusion metadata or Oracle guidance confirms support. Use `shared.validation.setup-data-validator` only when a setup data artifact is available for review. Use `shared.validation.reference-data-validator` when the task depends on cross-pillar reference data.


## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task's business object.

1. Confirm that `remainingShelfLifeRest` is the exact registered Data Loader business object.
2. Generate the default editable XLSX sample through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "remainingShelfLifeRest" \
     --output-dir "<project-artifact-directory>"
   ```

3. Keep the generated workbooks together:
   - editable sample
   - attribute-details workbook
   - key-fields workbook
4. Review the generated headers and key fields before preparing source data. The operation uses read-only Fusion metadata and does not upload or import data.
5. Use the generated editable workbook as the starting point for the later Data Loader preparation and approval workflow.



## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `scm.manufacturing-and-supply-chain-materials-management.items` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Header catalog identity

For a supplied catalog name, follow `resolve_mrsl_category_set` in
[reference lookups](ora-resource/ora_reference_lookups.md). It calls the catalog
`SpEgpCatalogLookupV1` finder, matches the supplied name to CategorySetName,
and maps the returned CategorySetId directly to the header field CategorySetId,
which scopes category-detail lookups. Preserve unrequested header fields and use
Core Data Loader validation and approval for any requested configuration change.

For every category-based assignment (AssignmentType 11 through 20) supplied with
a Category or CategoryName, use resolve_mrsl_item_category in the same reference.
It calls planningObjects/getEntityDetails with the effective rule header's
CategorySetId as bCategorySetId and matches the supplied category name to the
returned CategoryName to populate each detail's CategoryId.

For item-name inputs, resolve ItemName through SpEgpSystemItemsV1 with the exact
`q=ItemName='<ItemName>'` filter and populate
the returned InventoryItemId. For OrganizationCode inputs, resolve through
SpEgpItemOrganizationsV1 using the resolved InventoryItemId as bItemId for item/org
assignments and a null bItemId for category/org assignments, returning OrganizationId.
Item lookup consumes one response without pagination. See reference lookups for bind and validation rules.

For CustomerName (customer_name), use SpCustomerAtSourceV1 and read CustomerId, CustomerName and PartyNumber one page at a time with limit=25 and offset. Display only the first page initially; offer Next 25 when hasMore=true and fetch another page only on explicit user request. A user may select any displayed customer without reading the remaining pages. Send CustomerName as an exact server-side q filter and keep it on every requested page. Auto-resolve only a sole initial-page record when hasMore=false. If multiple records match the name, ask the user to select a displayed customer before using that record's CustomerId. A failed requested page or malformed page evidence blocks resolution; pages the user has not requested do not.
For CustomerSiteCode, use SpCustomerSiteAtSourceV1 with validated input CustomerId
as bCustomerId and map returned CustomerSiteId. The customer-site lookup consumes
a single response without offset or pagination. CustomerId input may be direct or name-resolved;
a customer name is optional when the site lookup has a valid CustomerId.

For Region, use addressGeographies with the supplied GeographyName/RegionName,
returning GeographyIdentifierId and hierarchy through GeographyLevel5Value.
Keep the server-side name filter and show at most 25 matches initially. Offer
Next 25 when hasMore=true and fetch another page only on explicit user request.
The user may select a displayed hierarchy record without fetching the rest;
same-ID hierarchy variants remain separate. Auto-resolve only a sole initial-page
record with hasMore=false. Retain and revalidate the selected page and hierarchy.

For Zone, use geoZones with the server-side ZoneName filter. Display at most
25 matches with ZoneId, ZoneName, ZoneCode, ZoneType and ZoneCategory. Offer
Next 25 when hasMore=true and fetch only on explicit user navigation; a valid
displayed-record selection does not require unseen pages. Auto-resolve only
a sole initial-page record with hasMore=false. Retain stable options and
revalidate the selected page and zone identity.

For Demand Class, supply Meaning and use FndLookupValuesV1 with
LookupType='ORA_DOO_DEMAND_CLASS', returning LookupCode. Demand Class retains
its single-response/no-offset contract; see reference lookups.

Catalog, Category, Organization, Customer, Customer Site and Demand Class lookups
send exact server-side q filters for CategorySetName, CategoryName,
OrganizationCode, CustomerName, CustomerSiteCode and Meaning respectively.
Preserve the existing finder scope binds and verify returned values; rejected
or ignored filtering blocks rather than falling back to an unfiltered scan.

## Review Scenarios

Use the [synthetic MRSL review scenarios](references/mrsl-review-scenarios.md)
to review task-specific defaults, header preservation, catalog scope, lookup
ambiguity, assignment inputs, and request-wide linkage. These are offline
review cases, not evidence of live Fusion execution.
