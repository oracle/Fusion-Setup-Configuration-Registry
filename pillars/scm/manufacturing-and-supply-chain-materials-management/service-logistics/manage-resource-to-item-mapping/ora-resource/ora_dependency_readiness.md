# Manage Resource to Item Mapping Dependency Readiness

Current capability gate: the task SKILL.md permits metadata/sample and explicitly requested status only. Complete business/reference reads and create/update/delete preparation are unsupported. Return blocked (invalid at input validation) before external activity or source preparation; the remaining domain contracts do not enable those operations.

Evaluate only operation-specific Data Loader evidence. No foreign objects are created by this task.

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| RIM.MAPPING | Exact current mapping | Yes | Update or delete | Verify | Complete core Data Loader mapping evidence | resolve_resource_item_mapping | Current identity must be verified | Select one exact current mapping | Current key and retained values |
| RIM.ORGANIZATION | Organization identity | Yes | Create; update changing organization | Verify | Complete core Data Loader organization evidence | resolve_mapping_organization | Destination identity must be verified | Supply one active organization | Verified OrganizationId |
| RIM.RESOURCE | Resource identity and destination compatibility | Yes | Create; update changing resource or organization | Verify | Complete core Data Loader production resource evidence | resolve_mapping_resource | Retained resource must be rechecked when organization changes | Select a resource in the destination organization | Verified ResourceId |
| RIM.INVENTORY_ITEM | Item identity and organization association | Yes | Create; update changing item or organization | Verify | Complete core Data Loader itemsV2 evidence | resolve_mapping_item | Item must belong to the intended organization | Select one item/organization pair | Verified InventoryItemId |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RIM.CHECK_DEPENDENCIES | decision | 3 | resolve_dependency | ready->RIM.EXECUTION_GATE;not_applicable->RIM.EXECUTION_GATE;blocked->RIM.RETURN_REFUSAL | RIM.RESOLVE_IDENTITIES | stop | Require every applicable Data Loader-owned identity and association check; mark only unrelated dependencies not_applicable |
