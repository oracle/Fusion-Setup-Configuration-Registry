# Design Enforcement

The rules below preserve the documented product-recall configuration behavior before a Data Loader preview is generated.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Reconcile current state | For a singleton update, complete find_existing_recall_global_params or find_existing_recall_item_validation_organization; retain the returned ParameterValueId and singleton count. Complete find_existing_recall_parameter_rows for all other selected business objects. |
| 2 | Describe current contract | Complete describe_recall_parameter_business_objects and restrict the preview to supported methods and updateable attributes. |
| 3 | Validate reference identities | Resolve the applicable generic lookup, inventory organization, active subinventory, active locator, cost center/location, business unit, ledger, and public worker references in dependency order. |
| 4 | Evaluate configuration rules | Apply singleton, organization-scope, owner-mapping, grouping, subinventory, and auto-close dependency rules. |
| 5 | Return preflight result | End at DONE-READY-FOR-PREVIEW and return ordered rule results to Task Hook for build-data-load-preview bound to the final artifact digest. Core Data Loader owns the approval policy and submission; Task Hook owns preview approval and archive verification. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| recallGlobalParams already has one record | Blocker | find_existing_recall_global_params | The user has not supplied the desired updated global values, the lookup does not return exactly one row, or the Data Loader update record omits the returned ParameterValueId | Ask for the values to update, then use the returned server ParameterValueId for the Data Loader update; do not create another row | Yes |
| recallItemValidationOrganizations already has one record | Blocker | find_existing_recall_item_validation_organization | The user has not supplied a replacement ItemValidationOrganizationName, the lookup does not return exactly one row, or the Data Loader update record omits the returned ParameterValueId | Ask for the replacement organization, then use the returned server ParameterValueId for the Data Loader update; do not create another row | Yes |
| recallInventoryOrganizations scope changes | Blocker | find_existing_recall_parameter_rows | The request assumes all organizations participate while any selected rows will remain, or supplies selected rows without acknowledging that only those organizations participate | Reconcile the full desired selected set; use no rows only for enterprise-wide participation | Yes |
| recallContainmentTaskOwners is supplied | Blocker | find_existing_recall_parameter_rows | Both mapping dimensions are present, an organization-only row lacks approved source or target-contract support, duplicate active organization + dimension + owner combinations are proposed, or a delete is requested | Use zero or one mapping dimension as supported, resolve each named owner, and deactivate with ActiveFlag false instead of deleting | Yes |
| A reference field is supplied, excluding the traceability default scope marker -1 | Blocker | resolve_inventory_organization | Any supplied lookup code, organization, subinventory, locator, cost center/location, business unit, ledger, owner, or coordinator does not return one exact current result through its named resolver | Correct the value or parent context; do not substitute a near match or create reference data during this task | Yes |
| recallProductTraceabilityGroupings is supplied | Blocker | find_existing_recall_parameter_rows | The reconciled projected state does not contain exactly one default with InventoryOrganizationId = -1, an existing default would be duplicated by a create instead of updated by its returned key, or an update key does not identify that reconciled default | Retain or create exactly one default and preserve optional positive-ID exceptions. Count a supported update to the same default key once; never count exceptions as defaults. Stop on a proposed removal or conversion of the only default, an explicit second-default create, or unknown resulting cardinality. Apply grouping-value validation from ora_input_validation.md | Yes |
| recallSubinventories is supplied | Blocker | describe_recall_parameter_business_objects | The chosen subinventory is not evidenced as quantity tracked and non-reservable, or a locator-controlled subinventory has no StockLocator | Use a suitable quarantine subinventory and its default locator where required | Yes |
| AutoCloseInTransitTasksFlag is true | Blocker | find_existing_recall_parameter_rows | BypassTaskFlag is not true | Enable the bypass-count-and-disposal behavior first, or set the auto-close flag false | Yes |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| find_existing_recall_parameter_rows | Every requested state change | Existing row keys, singleton count, selected inventory organizations, and owner-mapping identity | ora_reference_lookups.md |
| find_existing_recall_global_params | An existing recallGlobalParams row is being changed | One server-returned ParameterValueId and the user-approved global field changes | ora_reference_lookups.md |
| find_existing_recall_item_validation_organization | An existing recallItemValidationOrganizations row is being changed | One server-returned ParameterValueId and the user-approved replacement organization name | ora_reference_lookups.md |
| describe_recall_parameter_business_objects | Every import preview | Current field contract, supported method, mutability, keys, and LOV behavior | ora_reference_lookups.md |
| resolve_generic_lookup_code | A lookup code or meaning is supplied | One exact current lookup row and canonical code | ora_reference_lookups.md |
| resolve_inventory_organization | An actual inventory organization is supplied; exclude the traceability default marker -1 | One exact current organization and canonical identity | ora_reference_lookups.md |
| resolve_active_subinventory | A subinventory is supplied | One exact active subinventory and resolved organization context | ora_reference_lookups.md |
| resolve_active_locator | A StockLocator is supplied or required | One exact active locator and resolved organization/subinventory context | ora_reference_lookups.md |
| resolve_cost_center_or_location | A cost center or location lookup is required | One exact source-confirmed lookup result or a describe-backed alternative | ora_reference_lookups.md |
| resolve_business_unit | A business unit is supplied | One exact active business unit and any returned PrimaryLedgerId | ora_reference_lookups.md |
| resolve_ledger | A ledger is supplied or derived | One exact ledger and, where applicable, matching PrimaryLedgerId | ora_reference_lookups.md |
| resolve_owner_or_coordinator_worker | OwnerName is supplied | One exact active/current public worker from the approved full-name finder or a supplied unique identifier; zero or multiple matches block preview | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RECALL.PARAMETERS.ENFORCE-DESIGN | decision | 50 | design_enforcement | compliant->RECALL.PARAMETERS.DONE-READY-FOR-PREVIEW;blocked->RECALL.PARAMETERS.HANDLE-DESIGN-BLOCKER | RECALL.PARAMETERS.DESCRIBE-CONTRACT,RECALL.PARAMETERS.APPLY-DEFAULTS | stop | A create, update, deactivate, or participating-organization scope change is requested |
