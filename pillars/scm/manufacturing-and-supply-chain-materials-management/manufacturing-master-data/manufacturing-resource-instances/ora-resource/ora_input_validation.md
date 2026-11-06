# Input Validation

## Import Mode and Source Contract

Use the manifest dataloader_import_mode unless the active workflow records an
explicit supported override. The business-field names below identify validation
facts for either route. For native FSM, map the exact target-exported columns to
those facts without renaming CSV headers or injecting REST identifiers. An
unresolved mapping blocks before preview. Keep required CSV members and
ASM_SETUP_CSV_METADATA.xml, exact parent-child keys, native Y/N flags, and only
requested records; unused child CSVs remain header-only. The exported FSM schema
owns file and column shape, while the same parent, lifecycle, asset, work-center,
person and scheduling checks still apply. A read-only product REST lookup for
domain evidence does not require HCM Data Loader BO registration.

When REST is selected, retain productionResources registration and the existing
EquipmentInstance/LaborInstance child-only Data Loader contract. Native FSM
shape exceptions never change REST package validation.

## Domain Evidence Inputs

Core Data Loader metadata validates field shape, not these business facts. A
source-stage terminal means ready for the separate Core approval gate, not that
Fusion has accepted the data. This assisted task consumes read-only resolver
evidence and, for person eligibility, explicit reviewed input. A generic service
success, proposed value, unchecked box, or unrelated prior run is not evidence.

| Evidence Input | Required When | Required Content | Validation and Failure |
|---|---|---|---|
| LaborEligibilityEvidence | A LABOR row supplies or derives PartyId, RegistryId, or person association | Review by the authorized Manufacturing/HCM SME of current target-system person status, eligible employee/contingent-worker/partner-contact category, exact PartyId and RegistryId mapping when used, existing parent associations, and plant-wide primary designation. Include reviewer, reviewed-at time, effective date, sanitized source references and digests, target fingerprint, proposed artifact/request fingerprint, parent organization/resource and exact person/instance binding; include each fact named in MRINST.PERSON. | Require an explicit fact for every applicable check and exact bindings. Missing, stale, ambiguous, unsupported or conflicting evidence stops before preview as input_validation. No auto-attestation; no schema validation substitution. |
| Evidence freshness | Every applicable domain check | Evidence gathered/reviewed in the current validation cycle against the selected target and immutable request | Any target, request, identity, effective-date or relevant source change invalidates it; resume requires refreshing affected evidence. Keep only sanitized rule outcomes and secure evidence references in audit records; no person records or customer payloads in the repository/project workspace. |

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Parent resource identity | ResourceId; or ResourceCode and OrganizationCode together | Block preview | Supply the exact parent productionResources identifier, or supply both resource code and organization code for parent resolution | Creating or updating a Manufacturing Resource Instance | resolve_parent_production_resource |
| Child type selection | ResourceType returned by parent preflight | Block preview | Resolve the parent resource before selecting a child route | Every instance import | resolve_parent_production_resource |
| Equipment instance identity | EquipmentIdentifier and EquipmentInstanceName | Block preview | Supply a unique identifier and name for the equipment instance | Creating an EQUIPMENT child instance |  |
| Labor instance identity | LaborInstanceName; optionally LaborIdentifier; or PartyId, RegistryId, or one exact Person/Person Name/Party Name | Block preview only when neither a LaborIdentifier nor a valid person association is supplied | Supply a LaborIdentifier, or provide PartyId, RegistryId, or one exact person name so the eligible party can derive the LaborIdentifier | Creating a LABOR child instance | resolve_labor_party_by_name |
| Labor person association | PartyId, RegistryId, or Person/Person Name/Party Name | Block preview | Supply PartyId or RegistryId, or supply one exact person name for PartyId derivation | Creating a LABOR child instance with a person association | resolve_labor_party_by_name |
| Optional primary work center | PrimaryWorkCenterId or PrimaryWorkCenterCode | Continue without a value; validate it when supplied | Use the declared assignment resolver after asset derivation | Creating or updating either child type | verify_primary_work_center_assignment |
| Child payload | Attributes accepted by the selected route metadata | Block preview | For REST, validate the productionResources child-only Data Loader package selected by ResourceType; for FSM, validate the target-exported CSV structure and exact parent linkage. Do not invent attributes or include unrequested root mutations. | Creating or updating a child instance |  |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| REST is selected and parent ResourceType is EQUIPMENT | Prepare productionResources with EquipmentInstance as the only populated child resource | Continue to preflight and payload validation for EquipmentInstance; block when any LaborInstance row is present or EquipmentInstance is not selected | resolve_parent_production_resource |
| REST is selected and parent ResourceType is LABOR | Prepare productionResources with LaborInstance as the only populated child resource | Continue to preflight and payload validation for LaborInstance; block when any EquipmentInstance row is present or LaborInstance is not selected | resolve_parent_production_resource |
| Parent ResourceType is absent or is neither EQUIPMENT nor LABOR | The requested child route is unsupported | Stop and request a valid parent resource or correction | resolve_parent_production_resource |
| Equipment instance includes AssetId or AssetNumber | The asset must be active, in the parent organization, located in a work center, and not actively associated to another equipment instance | Stop until verify_equipment_asset and MRINST.ASSET pass | verify_equipment_asset |
| Labor instance includes PartyId or RegistryId | The party must be active, eligible as an employee, contingent worker, or partner contact, and not duplicate the parent-resource association | Stop until the reviewed LaborEligibilityEvidence passes MRINST.PERSON |  |
| Labor instance includes Person, Person Name, or Party Name and PartyId is absent | Derive PartyId only from one exact laborResourceInstancesLOV PartyName match | Stop when the PartyName lookup has no match or more than one match | resolve_labor_party_by_name |
| Labor instance is created or updated | Workforce Scheduling must not be enabled for the parent organization | Stop unless resolve_workforce_scheduling returns explicit disabled evidence and MRINST.SCHEDULING passes | resolve_workforce_scheduling |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Parent resource identity | Require one exact ResourceId, or a complete ResourceCode and OrganizationCode pair; reject a partial code-and-organization pair | Every instance import | resolve_parent_production_resource |
| ResourceCode and OrganizationCode | When used instead of ResourceId, derive ResourceId from one exact active productionResources collection result; when supplied with ResourceId, require the resolved parent to match both values | Every instance import | resolve_parent_production_resource |
| ResourceType | Accept only EQUIPMENT or LABOR after read-only parent preflight | Every instance import | resolve_parent_production_resource |
| Child collection | Require EquipmentInstance for EQUIPMENT and LaborInstance for LABOR | Every REST instance import | resolve_parent_production_resource |
| Data Loader child resource | Retain productionResources as the registered Data Loader business object; populate only EquipmentInstance for EQUIPMENT or only LaborInstance for LABOR, and leave the root section without data rows for a child-only request | Creating or updating a child instance through REST | resolve_parent_production_resource |
| EquipmentIdentifier | Require uniqueness within the organization and parent resource | Create or update an EQUIPMENT instance |  |
| LaborIdentifier | When supplied, require uniqueness within the parent resource. When omitted, derive it from the eligible party resolved through PartyId, RegistryId, or one exact Person/Person Name/Party Name. | Create or update a LABOR instance | resolve_labor_party_by_name |
| Person, Person Name, or Party Name | Accept as a PartyId derivation input only when the laborResourceInstancesLOV PartyName query returns exactly one PartyId | Create or update a LABOR instance when PartyId and RegistryId are absent | resolve_labor_party_by_name |
| PrimaryWorkCenterId | Validate the supplied or asset-derived identity using verify_primary_work_center_assignment; a conflicting code/ID blocks | Create or update an instance | verify_primary_work_center_assignment |
| InactiveDate | Require a future date that does not exceed the parent resource inactive date | Create, update, or deactivate an instance | resolve_parent_production_resource |
| Generated child ID | Do not send EquipmentInstanceId or LaborInstanceId on create | Creating a child instance |  |
| Child payload | Validate through core.data-loader before preview: use live selected child metadata for REST, or the exact target-exported task CSV metadata for native FSM. Every instance must match its resolved parent ResourceType; omit unrelated baseline records and preserve required empty members. | Creating or updating a child instance |  |

## Reviewed Person Evidence Procedure

| Step | Action | Required Result |
|---|---|---|
| 1 | For each associated person, collect the required LaborEligibilityEvidence from the authorized SME's review of the current target and its complete relevant associations | Explicit identity, activity, eligible category, parent duplicate count, and plant primary count; counts exclude only the exactly identified instance being updated |
| 2 | Bind the review to the resolved parent, person, requested operation, effective date and immutable request | A source reference/digest for every asserted fact, reviewer identity and current-cycle review time; do not treat user approval of an upload as this review |
| 3 | Evaluate MRINST.PERSON before dependency readiness | Missing evidence returns MRINST.BLOCKED, not ready; a provided PartyId or a PartyName LOV match establishes identity only |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MRINST.VALIDATE_INPUT | decision | 1 | validate_input | valid->MRINST.RESOLVE_PARENT;invalid->MRINST.BLOCKED | none | stop | A Manufacturing Resource Instances import is prepared. |
| MRINST.VALIDATE_DOMAIN_EVIDENCE | decision | 7 | validate_input | valid->MRINST.DEPENDENCIES;invalid->MRINST.BLOCKED | MRINST.VERIFY_WORK_CENTER | stop | Check required LaborEligibilityEvidence content and binding after all applicable read-only domain lookups; no person association requires no person evidence. |
