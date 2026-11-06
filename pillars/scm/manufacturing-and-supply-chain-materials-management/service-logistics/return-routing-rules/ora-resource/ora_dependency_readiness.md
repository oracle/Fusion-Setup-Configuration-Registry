# Return Routing Rules Dependency Readiness

For supplied subinventory or category values, establish their parent organization or catalog in the reviewed, environment-bound ephemeral reference bundle defined in `ora_reference_lookups.md` before checking the child value. Confirm the selected Data Loader Business Object supports each mapped attribute. These are conditional relationship checks, not claims that every optional attribute is required.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Destination and source organizations | Confirm the respective organization value before checking a supplied destination or source subinventory |
| 2 | Item catalog | Confirm the category set or catalog value before checking a supplied category |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| RRR.DEP.DEST_ORG | Destination organization | Conditional | DestinationSubinventory is supplied | Local check | Reviewed ephemeral reference bundle | resolve_return_routing_destination_organization | A subinventory must belong to the chosen destination organization | Supply a unique destination organization value | Confirmed destination organization |
| RRR.DEP.SOURCE_ORG | Source organization | Conditional | SourceSubinventory is supplied | Local check | Reviewed ephemeral reference bundle | resolve_return_routing_source_organization | A subinventory must belong to the chosen source organization | Supply a unique source organization value | Confirmed source organization |
| RRR.DEP.CATALOG | Item catalog | Conditional | CategoryId or CategoryName is supplied | Local check | Reviewed ephemeral reference bundle | resolve_return_routing_category_set | A category must belong to the chosen catalog | Supply a unique item catalog value | Confirmed item catalog |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RRR.RESOLVE_DEPENDENCIES | step | 3 | resolve_dependency | ready->RRR.EXECUTION_GATE;blocked->RRR.RETURN_REFUSAL | RRR.LOOKUP_VALUES | stop | After local reference checks, confirm each supplied subinventory or category belongs to its selected parent |
