# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Parent resource | Resolve the exact active productionResources parent and its ResourceType from ResourceId or from the ResourceCode and OrganizationCode pair. |
| 2 | Child route | For REST, retain productionResources registration and select only EquipmentInstance for EQUIPMENT or LaborInstance for LABOR. For native FSM, validate each instance against its resolved parent ResourceType and target-exported CSV component. |
| 3 | Labor person derivation | When PartyId and RegistryId are absent, derive PartyId from one exact laborResourceInstancesLOV PartyName match. |
| 4 | Child-specific prerequisites | Validate a supplied primary work center and the applicable asset or person association. |
| 5 | Child payload contract | Validate the selected route contract: live child Data Loader metadata for REST, or the exact target-exported CSV metadata for native FSM. |
| 6 | Import approval | Obtain approval for the immutable Core Data Loader artifact before live import. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| parent_production_resource | Active productionResources parent | Yes | Every instance import | Lookup | productionResources read-only resource | resolve_parent_production_resource | The child route depends on the parent ResourceType | Supply a valid ResourceId, or supply ResourceCode and OrganizationCode together | ResourceId, ResourceType, OrganizationId, OrganizationCode, InactiveDate |
| equipment_child_route | EquipmentInstance child collection | Conditional | REST is selected and ResourceType is EQUIPMENT | Verify | core.data-loader metadata validation |  | Equipment instances must invoke the productionResources EquipmentInstance child resource and must not include LaborInstance rows | Validate a productionResources package with EquipmentInstance as the only populated child collection through core.data-loader | productionResources/{ResourceId}/child/EquipmentInstance |
| labor_child_route | LaborInstance child collection | Conditional | REST is selected and ResourceType is LABOR | Verify | core.data-loader metadata validation |  | Labor instances must invoke the productionResources LaborInstance child resource and must not include EquipmentInstance rows | Validate a productionResources package with LaborInstance as the only populated child collection through core.data-loader | productionResources/{ResourceId}/child/LaborInstance |
| primary_work_center | Parent-resource work center assignment | Conditional | PrimaryWorkCenterId or PrimaryWorkCenterCode is supplied or asset-derived for either child type | Verify | Declared read-only work-center and assignment results | verify_primary_work_center_assignment | MRINST.WORK_CENTER requires exact parent-resource membership | Resolve and verify the supplied or derived work center before preview | PrimaryWorkCenterId and assignment evidence |
| equipment_asset | Eligible active asset | Conditional | AssetId or AssetNumber is supplied for EQUIPMENT | Verify | Declared asset lookup and complete organization equipment-association scan | verify_equipment_asset | MRINST.ASSET owns eligibility and uniqueness policy | Supply an eligible asset or omit the optional association | AssetId and current eligibility facts |
| labor_person_name | Labor person PartyId derivation | Conditional | Person, Person Name, or Party Name is supplied for LABOR and PartyId and RegistryId are absent | Lookup | laborResourceInstancesLOV REST endpoint | resolve_labor_party_by_name | A person name must resolve to one PartyId before it can be used as a labor association | Supply one exact person name or provide PartyId or RegistryId directly | PartyId, PartyName |
| labor_person | Eligible unique labor person | Conditional | PartyId, RegistryId, or a derived person association is supplied for LABOR | Verify | Explicit reviewed LaborEligibilityEvidence input validated at MRINST.VALIDATE_DOMAIN_EVIDENCE | | MRINST.PERSON requires person eligibility and association facts unavailable from metadata or a name match | Complete the documented SME evidence review before preview; missing facts block | Bound reviewed person facts; no automatic eligibility assertion |
| workforce_scheduling | Workforce Scheduling disabled | Yes | Creating or updating a LABOR instance | Verify | Fresh plant-parameters GET result | resolve_workforce_scheduling | MRINST.SCHEDULING requires explicit false | Resolve the plant parameter; null or missing is not disabled | OrganizationId and HCMSchedulerEnabledFlag |
| native_fsm_package | Target task CSV package | Conditional | Native FSM is selected | Verify | Target-exported task CSV metadata validated through core.data-loader |  | Bind each instance to its resolved parent and validate the selected FSM schema without requiring REST BO registration | Preserve native column names, keys and Y/N flags; stop on unresolved mappings or unsupported operations | Validated immutable native FSM artifact |
| immutable_import_approval | Approved immutable import artifact | Yes | A live REST or FSM import is requested | Verify | core.data-loader approval workflow |  | Live import must be bound to the reviewed artifact | Approve the exact validated artifact | Approved artifact fingerprint |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| satisfied | Parent, child route, applicable domain evidence, payload metadata, and approval gates pass | Read-only lookup only; core.data-loader owns import execution. |
| blocked | Parent is missing or inactive, ResourceType is unsupported, the selected route metadata cannot support the operation, applicable domain evidence is missing or invalid, or approval is missing | Read-only validation only; stop before import. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MRINST.DEPENDENCIES | decision | 8 | resolve_dependency | ready->MRINST.DESIGN;blocked->MRINST.BLOCKED | MRINST.VALIDATE_DOMAIN_EVIDENCE | stop | Require all applicable named resolver results and reviewed person evidence before evaluating readiness; metadata-only or unavailable domain evidence is blocked. |
