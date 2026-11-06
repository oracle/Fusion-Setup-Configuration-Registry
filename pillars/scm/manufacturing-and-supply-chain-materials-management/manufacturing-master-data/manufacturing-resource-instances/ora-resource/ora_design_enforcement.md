# Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Confirm parent identity | Use the exact active parent ResourceId, or derive it from the exact ResourceCode and OrganizationCode pair, and retain the returned ResourceType. |
| 2 | Enforce child compatibility | Match each instance to its resolved parent ResourceType. For REST, retain productionResources registration and populate only EquipmentInstance for EQUIPMENT or LaborInstance for LABOR. For native FSM, retain the exported component and parent keys without REST DAT conversion. |
| 3 | Enforce instance readiness | Validate a supplied primary work center and, when supplied, an eligible asset or person association; derive PartyId from one exact PartyName match when a labor person name is supplied. |
| 4 | Enforce lifecycle rules | Use a future inactive date, preserve parent lifecycle boundaries, and do not delete an instance in work execution. |
| 5 | Enforce import route | Use core.data-loader for selected-route metadata and artifact validation, approval, and live import; sample generation from REST BO metadata applies only to REST. |
| 6 | Enforce mode selection | Use the manifest dataloader_import_mode unless an explicit supported override is recorded. Native FSM selection requires catalog support, target-exported metadata and approved immutable artifact; it does not require a REST failure. A fallback from selected REST still requires a documented unsupported operation and separate FSM artifact validation and approval. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| REST is selected and ResourceType is EQUIPMENT | Error | resolve_parent_production_resource | The selected child collection is not EquipmentInstance | Use productionResources/{ResourceId}/child/EquipmentInstance through core.data-loader | Yes |
| REST is selected and ResourceType is LABOR | Error | resolve_parent_production_resource | The selected child collection is not LaborInstance | Use productionResources/{ResourceId}/child/LaborInstance through core.data-loader | Yes |
| A child-only REST Data Loader package is prepared | Error | resolve_parent_production_resource | The root productionResources section contains a data row, both child collections contain data rows, or the populated child collection does not match ResourceType | Keep the root section headers-only and populate exactly one child resource: EquipmentInstance for EQUIPMENT or LaborInstance for LABOR | Yes |
| ResourceType is absent or unsupported | Error | resolve_parent_production_resource | No compatible child route can be selected | Correct the parent ResourceId, the ResourceCode and OrganizationCode pair, or ResourceType | Yes |
| A primary work center is supplied or asset-derived | Error | verify_primary_work_center_assignment | MRINST.WORK_CENTER fails | Resolve exact membership before preview | Yes |
| An equipment asset is supplied | Error | verify_equipment_asset | MRINST.ASSET fails | Supply an eligible unassociated asset or omit the optional association | Yes |
| A labor Person, Person Name, or Party Name is supplied without PartyId or RegistryId | Error | resolve_labor_party_by_name | The laborResourceInstancesLOV PartyName lookup does not return exactly one PartyId | Supply a more specific exact person name or provide PartyId or RegistryId | Yes |
| A labor person is supplied | Error | | MRINST.PERSON fails, including missing reviewed evidence | Complete the explicit evidence review or correct the association | Yes |
| A LABOR instance is created or updated | Error | resolve_workforce_scheduling | MRINST.SCHEDULING fails | Resolve explicit plant-state evidence; use the supported scheduling process when enabled | Yes |
| An inactive date is supplied | Error | resolve_parent_production_resource | The date is not future or is later than the parent resource inactive date | Supply a permitted future date | Yes |
| Delete is requested | Error |  | The instance is used in work execution, or an EQUIPMENT instance is assigned to a workstation | Remove the usage or workstation association before a separately approved delete | Yes |
| Native FSM is selected | Error |  | CSV export/import is unsupported, the target-exported contract or parent mapping is unresolved, or immutable artifact approval is missing | Validate the FSM task package through core.data-loader and retain all domain gates; no REST BO registration or REST failure is required | Yes |
| A fallback from selected REST to FSM is requested | Error |  | The REST limitation is not established or the new immutable FSM artifact is not validated and approved | Retain the selected REST route until fallback evidence and the separate artifact approval pass; never replay an uncertain write | Yes |

## Domain Eligibility Rules

| Policy ID | Required When | Pass Condition | Missing or Failed Evidence |
|---|---|---|---|
| MRINST.WORK_CENTER | Primary work center supplied or asset-derived | Exactly one same-organization work center and one assignment of the resolved parent ResourceId; all input/derived identities agree | Block preview; no optional-association bypass after a value is supplied |
| MRINST.ASSET | Equipment asset supplied | Exact asset is active, LocationOrganizationId equals the parent organization, CurrentLocationContext is ORA_WORK_CENTER, WorkCenterId is nonblank, and complete organization scan gives zero other active associations. Exclude only the exact updated instance; also reject duplicate assets across proposed rows | Block preview for inactive, wrong-location, associated, partial or unknown evidence |
| MRINST.PERSON | Labor person association supplied or derived | Bound reviewed evidence explicitly proves active status, employee/contingent-worker/partner-contact eligibility, matching PartyId/RegistryId, zero other associations on this parent, and zero other primary resources in this organization when PrimaryResourceFlag is true for REST or Y for native FSM. Exclude only the exact updated instance; reject conflicting proposed associations too | Missing review, missing fact, ineligible status, duplicate/primary conflict or wrong/stale binding blocks; a name lookup or metadata success cannot substitute |
| MRINST.SCHEDULING | Any LABOR create/update | Exactly one same-organization plant result with HCMSchedulerEnabledFlag strictly Boolean false | True, null, missing, string values, wrong organization, multiple rows or failed lookup block; no local false default |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_parent_production_resource | Every instance import | ResourceId, ResourceCode, OrganizationCode, ResourceType, OrganizationId, InactiveDate | ora_reference_lookups.md |
| resolve_labor_party_by_name | A LABOR instance supplies Person, Person Name, or Party Name without PartyId or RegistryId | PartyId, PartyName | ora_reference_lookups.md |
| verify_primary_work_center_assignment | Supplied or asset-derived primary work center | Exact membership evidence for MRINST.WORK_CENTER | ora_reference_lookups.md |
| verify_equipment_asset | Equipment asset supplied | Exact identity, activity, location and complete association scan for MRINST.ASSET | ora_reference_lookups.md |
| resolve_workforce_scheduling | Any LABOR create/update | Same-organization Boolean HCMSchedulerEnabledFlag for MRINST.SCHEDULING | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MRINST.DESIGN | decision | 9 | design_enforcement | compliant->MRINST.ROUTE_REST;blocked->MRINST.BLOCKED | MRINST.DEPENDENCIES | stop | All applicable domain evidence passes dependency validation; evaluate every Domain Eligibility Rule before ready. |
