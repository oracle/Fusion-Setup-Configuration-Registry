# Workstations Design Enforcement

## Source Evidence

| Source | Verified Fact | Source Anchor |
|---|---|---|
| Workstation design and technical specification | A Workstation belongs to exactly one existing Work Center. WorkstationCode and WorkstationName are unique within the plant/organization. | [Workstation - Design & Technical Specification](https://confluence.oraclecorp.com/confluence/pages/viewpage.action?pageId=8555976642), version 151, retrieved 2026-10-05, Workstation relationship/Create attributes and WorkstationEO business rules |
| Workstation design and technical specification | A Workstation can have zero or more equipment-resource-instance associations after creation. Any associated equipment resource instance belongs to the parent Work Center. | [Workstation - Design & Technical Specification](https://confluence.oraclecorp.com/confluence/pages/viewpage.action?pageId=8555976642), Equipment Resource Instance Association |
| FDD - 24C Manage Workstation (marked Draft) | A Workstation must belong to a manufacturing-plant organization; its Work Center must be valid and in that same organization. An equipment association must be active equipment, in the same organization, and not already associated with another Workstation. | [FDD - 24C Manage Workstation](https://confluence.oraclecorp.com/confluence/pages/viewpage.action?pageId=8819715515), WIS-WS-020 through WIS-WS-024 |
| FDD - 24C Manage Workstation (marked Draft) | Duplicate Workstation Name is rejected for create; duplicate name on update is documented separately and does not authorize this create-only graph to update. | [FDD - 24C Manage Workstation](https://confluence.oraclecorp.com/confluence/pages/viewpage.action?pageId=8819715515), version 42, retrieved 2026-10-05, WIS-WS-004 and WIS-WS-006 |


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

## Source Authority

Supply and completion subinventory policies were previously mixed into ora_input_validation.md. Their sources remain [FMFG-96707](https://jira.oraclecorp.com/jira/browse/FMFG-96707), [FMFG-96708](https://jira.oraclecorp.com/jira/browse/FMFG-96708) and [OraReview 157453186](https://orareview.oraclecorp.com/157453186), WorkstationEOImpl.java and WorkstationEO.xml. This restoration moves those existing sourced policies to their design owner; it does not infer their missing current lookup requests, parser errors or live results.

## Acknowledged Equipment Source Difference

The Workstation - Design & Technical Specification, version 151 retrieved 2026-10-05, WorkstationEquipmentInstanceEO business rules, states one **active** workstation per equipment instance. The FDD - 24C Manage Workstation, version 42 retrieved 2026-10-05 and marked Draft, WIS-WS-013, states the instance must not belong to **any** other workstation and must be removed from its current workstation before association. These sources differ. The inherited stronger check here follows WIS-WS-013; it does not infer an exception for an inactive workstation or claim the two sources agree. The equipment preflight rejects every observed other-workstation assignment under the stronger source rule; no inactive-workstation exception is accepted. Actual service outcomes remain to be tested.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| WORKSTATIONS.DESIGN_CREATE_CONTRACT | decision | 20 | design_enforcement | pass->WORKSTATIONS.IMPORT_APPROVAL;failure->WORKSTATIONS.RETURN_ISSUES;incomplete->WORKSTATIONS.RETURN_ISSUES | WORKSTATIONS.RESOLVE_DESIGN_REFERENCES | stop | Evaluate only the source-backed Design Rules using their named authoritative results; missing lookup contract blocks planning. |
