# Input Validation

Use the six task business objects only through the task's `core.data-loader` REST route. For imports, evaluate the exact final immutable upload artifact after Data Loader completes preparation and verifies its persisted preflight, using Task Hook's data-load route and returned execution guide. Do not change the artifact during task evaluation; corrections require fresh preparation and validation. The public REST reference is the source for service shape; Fusion remains the final validator.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Project target environment | Active project Run Book server URL and configured REST base URL | Stop before any Fusion lookup | Compare normalized scheme, host and port; require the configured REST host to equal the active Run Book host for this project. Correct the project/environment selection through its owning workflow; do not reuse identities from a different pod | Any live describe, GET, preview, or import for a project with an active Run Book | |
| Global recall parameters | One or more requested changes to TimeFrameForTrackingRecall, BypassTaskFlag, TimeFenceForAutoWithdrawal, TimeFenceForAutoClosure, or AutoCloseInTransitTasksFlag | Stop before a singleton lookup or import | Ask the user which supported values must change; do not accept or invent ParameterValueId from user input | recallGlobalParams is supplied | find_existing_recall_global_params |
| Item validation organization | ItemValidationOrganizationName | Stop before a singleton lookup or import | Ask the user for the replacement organization name; do not accept or invent ParameterValueId from user input | recallItemValidationOrganizations is supplied | find_existing_recall_item_validation_organization |
| Participating inventory organization | InventoryOrganizationName or OrganizationName from an approved source | Stop the affected row | Resolve each exact name with the routed read-only inventoryOrganizations GET; fill the code and ID only from one active inventory-organization response. Provide no rows only when all inventory organizations must participate | recallInventoryOrganizations is supplied | resolve_inventory_organization |
| Containment task owner | OrganizationName, OwnerName, zero or one of SubinventoryName or CostCenterDescription; ActiveFlag is optional for a new mapping and defaults true, while a deactivation requires explicit false | Stop the affected row | Use the approved mapping source. Resolve OrganizationName and OwnerName through their routed read-only GETs; require one active inventory organization and one exact current worker. Blank dimension fields mean an approved organization-level mapping, while both populated is invalid. Resolve every named coordinator separately when the source lists multiple owners | recallContainmentTaskOwners is supplied | resolve_owner_or_coordinator_worker |
| Default traceability task group | InventoryOrganizationId = -1, ProductTraceabilityGrouping | Stop the affected row | Supply one default row for all inventory organizations. InventoryOrganizationName and InventoryOrganizationCode are not required and must be blank; -1 is a scope marker, not an organization to resolve. Reconcile the existing default before selecting create or update | recallProductTraceabilityGroupings contains a default row | find_existing_recall_parameter_rows |
| Traceability task-group exception | Positive InventoryOrganizationId, or InventoryOrganizationName or InventoryOrganizationCode resolving to a positive ID; ProductTraceabilityGrouping | Stop the affected row | Supply a specific active inventory organization and its grouping override. Resolve its exact ID, code, or name; keep the default separate | recallProductTraceabilityGroupings contains an organization-specific exception | resolve_inventory_organization |
| Recall subinventory | InventoryOrganizationName, Subinventory, PickSubinventoryFlag; StockLocator when the selected subinventory is locator controlled | Stop the affected row | Supply the inventory organization, quarantine subinventory, pick flag, and locator if applicable | recallSubinventories is supplied | resolve_active_subinventory |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Environment identity | Reject a configured Fusion REST host that differs from the active project Run Book host before resolving names or reading current setup. A prior result from another host is not target evidence | Any project-bound external operation | |
| Singleton update intent | When the corresponding singleton already exists, require the user to provide the values to update; do not create a second record | recallGlobalParams or recallItemValidationOrganizations is supplied | find_existing_recall_parameter_rows |
| Singleton cardinality and key | Reject more than one source row or more than one existing singleton row. When exactly one existing row is found, require its server-returned ParameterValueId in the Data Loader update record | recallGlobalParams or recallItemValidationOrganizations is supplied | find_existing_recall_parameter_rows |
| Participating-organization semantics | Treat zero supplied and existing rows as all inventory organizations participating; when any rows are supplied or retained, treat only those organizations as participants | recallInventoryOrganizations is in scope | find_existing_recall_parameter_rows |
| Lookup code | Require an exact active generic lookup code; a supplied meaning alone must resolve to exactly one code | A lookup code is supplied or required by the selected configuration | resolve_generic_lookup_code |
| Inventory organization | Require exactly one active inventory organization, not an item-only organization, for the supplied exact ID, code, or name; require all supplied identifiers to agree. Do not send the traceability default marker -1 to this resolver | An inventory-organization field is supplied, except the recallProductTraceabilityGroupings default row with InventoryOrganizationId = -1 | resolve_inventory_organization |
| Subinventory and locator | Require an exact active subinventory for its resolved inventory organization and, if a locator is supplied or required, an exact active locator for that organization and subinventory | recallSubinventories or a subinventory owner mapping is supplied | resolve_active_subinventory |
| Owner or coordinator | Query the approved full OwnerName with publicWorkers exact DisplayName q, page to completion, deduplicate by PersonId, and require one exact active directory worker before mapping OwnerId. If none or several remain, or the approved source contains only one name token, require PersonNumber or another approved unique key | recallContainmentTaskOwners is supplied | resolve_owner_or_coordinator_worker |
| Business unit and ledger | Require one exact active business unit and, where a ledger is supplied or derived, one exact ledger | A business-unit or ledger context is supplied by the Data Loader schema | resolve_business_unit |
| Owner mapping dimension | Reject a row with both SubinventoryName and CostCenterDescription. Accept neither only for an approved inventory-organization-level mapping; require the organization identity and target contract to support that row shape | recallContainmentTaskOwners is supplied | resolve_cost_center_or_location |
| Owner mapping lifecycle | Reject a delete request; an existing mapping may only be deactivated by setting ActiveFlag to false | recallContainmentTaskOwners is supplied | find_existing_recall_parameter_rows |
| Traceability scope discriminator | Accept InventoryOrganizationId = -1 only as the default task group; accept positive integer IDs only as organization-specific exceptions. A name or code may resolve an exception ID. Reject an unresolved blank scope, zero, noninteger IDs, other negative IDs, or a default marker combined with an organization name or code; never reinterpret a missing organization as -1 | recallProductTraceabilityGroupings is supplied | |
| Traceability source default cardinality | Reject more than one supplied row with InventoryOrganizationId = -1 across the entire selected batch, including repeated updates to the same default. An exception-only delta need not repeat the retained default; resulting-state cardinality is checked by design enforcement | recallProductTraceabilityGroupings is supplied | |
| Traceability grouping value | Reject a value other than Subinventory, Location, or Inventory Organization for both the default and exception task groups | recallProductTraceabilityGroupings is supplied | |
| Recall subinventory suitability | Block preview when supplied evidence does not confirm a quantity-tracked, non-reservable subinventory; require StockLocator when it is locator controlled | recallSubinventories is supplied | |
| In-transit auto-close dependency | Block a true AutoCloseInTransitTasksFlag unless BypassTaskFlag is true | AutoCloseInTransitTasksFlag is true | |

## Traceability Rule Evidence

The developer's 2026-10-23 requirement defines exactly one default task group with InventoryOrganizationId = -1 and optional organization-specific exceptions with positive IDs. The supplied Task Groups screenshots show Default for all organizations separately from Exceptions. The supplied SCH_PRODUCT_TRACE_GROUPING.csv corroborates one default and four positive-ID exceptions. These are authoring evidence, not a live target snapshot; runtime checks still require target reconciliation. No customer records or images are copied into the skill.

## Traceability Review Cases

| Case | Supplied change and current state | Expected result |
|---|---|---|
| TG-01 | One -1 row, Subinventory, blank organization name/code; no current default | Input valid; reconcile zero defaults; permit a supported create only when the projected state has exactly one default |
| TG-02 | One -1 row and exactly one current default | Reconcile an update to that server-returned ParameterValueId; never create another default; rebuild the artifact and repeat validation if a correction is needed |
| TG-03 | Two supplied -1 rows, even with different grouping values or the same update key | Input invalid; stop before preview |
| TG-04 | More than one current -1 row | Reconciliation ambiguous; stop and request repair; never choose the first row |
| TG-05 | Default marker -1 and nonblank organization name or code | Input invalid; resolve conflicting scope |
| TG-06 | Positive organization ID and Location; exactly one active matching organization and a retained default | Validate the exception identity; keep the default and other exceptions unchanged |
| TG-07 | New default plus multiple valid positive-ID exceptions; no current default | Accept the batch only when reconciliation and supported operations leave exactly one default |
| TG-08 | Exception-only delta; one current default remains | Accept without requiring the default in every source file |
| TG-09 | Exception-only delta; no current default | Design blocked; provide a default in the supported plan before preview |
| TG-10 | Zero, another negative ID, noninteger ID, or blank scope without an exception name/code | Input invalid; never infer default scope |
| TG-11 | Default update addressed to a different existing record or explicit second-default create | Reconciliation or design blocked; use the one reconciled default key |
| TG-12 | Proposed change removes or converts the only default, leaving none | Design blocked; preserve exactly one default |
| TG-13 | Default or exception with unsupported grouping value | Input invalid; retain the documented grouping choices |
| TG-14 | Current default cardinality cannot be established because pagination or access is incomplete | Reconciliation failed; no preview and no assumption that zero defaults exist |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RECALL.PARAMETERS.VALIDATE-INPUT | decision | 10 | validate_input | valid->RECALL.PARAMETERS.LOOKUP-EXISTING;invalid->RECALL.PARAMETERS.HANDLE-INPUT-ERROR | none | stop | A create, update, deactivate, or participating-organization scope change is requested |
