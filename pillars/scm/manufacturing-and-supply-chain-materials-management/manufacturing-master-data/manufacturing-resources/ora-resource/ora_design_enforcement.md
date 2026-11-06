# Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Validate resource identity | On create, confirm required organization, type, unique code/name, and UOM. On PATCH, resolve the existing resource identity and validate only explicitly supplied changes; do not require unchanged create fields. |
| 2 | Validate supported configuration | Confirm resource class, costing, HCM scheduling, automation, and inactive-date rules that apply. |
| 3 | Validate child compatibility | Confirm labor and equipment instances match the parent resource type and are valid for their associations. |
| 4 | Enforce import route | Use core.data-loader with the manifest dataloader_import_mode unless the active workflow records an explicit supported mode override. Validate the selected native FSM package or REST source and retain the task-local artifact validation and approval gate. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Resource is scheduled in a work definition or work order | Error |  | Usage UOM is not in the profile-defined service-duration UOM class | Use a UOM class suitable for Time for scheduled resources | Yes |
| HcmSchedulingGroupCode is supplied for a LABOR resource | Error |  | The plant HCM scheduler is disabled or the group is invalid | Enable the plant prerequisite and select a valid scheduling group | Yes |
| AutomationEquipmentFlag is Y | Error |  | ResourceType is not EQUIPMENT or plant robotics is disabled | Use EQUIPMENT and enable the plant robotics prerequisite | Yes |
| Labor instance is associated to a party | Error |  | The party is not an eligible employee, contingent worker, or partner contact, or violates uniqueness | Use an eligible, unique party association | Yes |
| Equipment instance is associated to an asset | Error | resolve_equipment_asset_by_id | The asset is not eligible for the plant and work-center context or is already associated | Use an eligible, unassociated asset | Yes |
| A program file is associated | Error | resolve_parent_resource | The resource is not automation-enabled, robotics is disabled, the file is invalid, or the association is duplicated | Resolve the prerequisite and use one valid program file | Yes |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_parent_resource | A child request needs its parent identity, type, organization, or automation flag | ResourceId, OrganizationId, ResourceType, AutomationEquipmentFlag | ora_reference_lookups.md |
| resolve_work_center_by_id | A primary work center is supplied by ID | WorkCenterId and returned work-center identity | ora_reference_lookups.md |
| resolve_equipment_asset_by_id | An equipment asset is supplied by ID | AssetId and returned asset identity | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MFGRES.DESIGN | decision | 3 | design_enforcement | compliant->MFGRES.ROUTE_REST;blocked->MFGRES.BLOCKED | MFGRES.DEPENDENCIES | stop | A Manufacturing Resources request passes input and dependency validation. |
