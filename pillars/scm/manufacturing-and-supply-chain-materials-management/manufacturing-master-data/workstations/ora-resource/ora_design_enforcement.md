# Workstations Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Organization and parent identity | Require manufacturing-plant organization and one existing same-organization parent Work Center |
| 2 | Workstation code and name uniqueness | Require the supported visible duplicate preflight; retain authoritative code and name duplicate rejection within the selected plant/organization during actual creation |
| 3 | Optional supplied associations | Evaluate supplied equipment and supply/completion subinventory/locator rules only with their authoritative lookup findings |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Creating a Workstation | Blocker | verify_workstations_manufacturing_organization | Current organization fitness cannot be verified or organization is not a manufacturing plant | Supply verified manufacturing-plant organization; no positional selection or inferred fitness | Only reviewed correction; no automatic organization change |
| Creating a Workstation | Blocker | verify_workstations_parent_work_center | Parent is absent, ambiguous, outside the organization or more than one parent would result | Supply one existing same-organization parent Work Center | Only reviewed correction; no automatic parent creation |
| Creating a Workstation | Blocker | check_workstations_code_duplicate | Duplicate preflight cannot complete or a visible code conflict exists in the selected organization | Supply a different code or obtain the approved update contract; do not silently switch create to update | Only reviewed correction |
| Creating a Workstation | Blocker | check_workstations_name_duplicate | Duplicate-name preflight cannot complete or a visible name conflict exists within the selected plant/organization | Supply a unique name; do not silently switch create to update or infer name-comparison/collation semantics | Only reviewed correction |
| Equipment association requested | Blocker | verify_workstations_equipment_association | Instance not active equipment, not in same organization/parent Work Center, already assigned to another Workstation or lookup unresolved | Omit the requested association or select a verified eligible instance; no inferred partial-import behavior | Only reviewed input correction |
| Either supply field supplied | Blocker | verify_workstations_supply_subinventory_locator | Subinventory absent/wrong organization; required locator absent; locator outside organization/subinventory; pair assigned to another Workstation; or lookup unresolved | Supply a verified consistent pair and satisfy documented locator-control requirement | Only reviewed input correction |
| Either completion field supplied | Blocker | verify_workstations_completion_subinventory_locator | Subinventory absent/wrong organization; required locator absent; locator outside organization/subinventory; or lookup unresolved | Supply verified completion values satisfying documented locator-control requirement | Only reviewed input correction |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| verify_workstations_manufacturing_organization | Creation | Verified manufacturing organization identity | ora_reference_lookups.md / Live Lookups |
| verify_workstations_parent_work_center | Creation | Verified existing same-organization single parent | ora_reference_lookups.md / Live Lookups |
| check_workstations_code_duplicate | Creation | Current within-organization visible code duplicate preflight and separately pending service acceptance | ora_reference_lookups.md / Live Lookups |
| check_workstations_name_duplicate | Creation | Current same-plant/organization visible duplicate-name preflight, with native query discrepancies and separately pending service acceptance | ora_reference_lookups.md / Live Lookups |
| verify_workstations_equipment_association | Equipment supplied | Equipment type, active state, organization/parent Work Center and association finding | ora_reference_lookups.md / Live Lookups |
| verify_workstations_supply_subinventory_locator | Supply values supplied | Subinventory/locator identity, locator control and assignment finding | ora_reference_lookups.md / Live Lookups |
| verify_workstations_completion_subinventory_locator | Completion values supplied | Subinventory/locator identity and locator control | ora_reference_lookups.md / Live Lookups |

## Equipment Association Scope

A Workstation can have zero or more equipment-resource-instance associations
after creation. Each supplied association must satisfy the Design Rules above.
The equipment preflight rejects every observed assignment to another
Workstation, including an inactive Workstation. Remove an existing association
through its separately approved workflow before associating the instance with
a new Workstation. Actual service outcomes remain to be tested.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| WORKSTATIONS.DESIGN_CREATE_CONTRACT | decision | 20 | design_enforcement | pass->WORKSTATIONS.IMPORT_APPROVAL;failure->WORKSTATIONS.RETURN_ISSUES;incomplete->WORKSTATIONS.RETURN_ISSUES | WORKSTATIONS.RESOLVE_DESIGN_REFERENCES | stop | Evaluate only the source-backed Design Rules using their named authoritative results; missing lookup contract blocks planning. |
