# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Plant organization access | The authenticated user must have access to the resource organization before a create or program-file association. |
| 2 | Resource prerequisites | On create, the organization, resource type, UOM, and resource identity must pass validation. On PATCH, resolve the existing target and validate applicable prerequisites for the explicitly supplied changes; unchanged create fields need not be resupplied. |
| 3 | Instance prerequisites | The parent resource must be active and of the matching type before a labor or equipment instance is changed. |
| 4 | Association prerequisites | A primary work center must be assigned to the parent resource; an equipment asset must satisfy the documented plant and work-center eligibility rules. |
| 5 | Automation prerequisites | Robotics must be enabled and the parent equipment resource must have AutomationEquipmentFlag set before associating a program file. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| organization_access | Organization access | Yes | Create resource or program-file association | Verify | Core Data Loader service validation |  | The REST service rejects an inaccessible organization | Obtain access to the target plant organization | OrganizationId |
| parent_resource_type | Active matching parent resource | Yes | Create labor or equipment instance | Verify | productionResources REST resource | resolve_parent_resource | Labor and equipment instances are restricted to the matching parent type | Use an active parent resource with the matching type | ResourceId, ResourceType |
| work_center_assignment | Work center assigned to resource | Conditional | PrimaryWorkCenterId or PrimaryWorkCenterCode is supplied | Verify | Work Centers REST resource | resolve_work_center_by_id | Primary work centers must be associated with the parent resource | Select an assigned work center or omit the optional primary work center | PrimaryWorkCenterId |
| asset_eligibility | Eligible maintenance asset | Conditional | AssetId or AssetNumber is supplied for equipment | Verify | Installed Base Assets REST resource | resolve_equipment_asset_by_id | The asset must be in the plant, in work-center context, active, and not already actively associated | Supply an eligible asset or omit the asset association | AssetId |
| automation_readiness | Plant robotics and automation-enabled equipment resource | Yes | Program-file association or AutomationEquipmentFlag is Y | Verify | Core Data Loader service validation and parent resource |  | Robotics is required for automation equipment and program files | Enable the documented prerequisite or remove the automation request | AutomationEquipmentFlag, ProgramFileId |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| satisfied | All applicable prerequisites are verified | No create action is authorized by this task guidance |
| blocked | A required organization, parent, work-center, asset, or robotics prerequisite is missing or invalid | Read-only verification only; stop before preview |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MFGRES.DEPENDENCIES | decision | 2 | resolve_dependency | ready->MFGRES.DESIGN;blocked->MFGRES.BLOCKED | MFGRES.VALIDATE_INPUT | stop | Applicable Manufacturing Resources dependencies are evaluated. |
