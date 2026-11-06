# Input Validation

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Resource creation identity | OrganizationId or OrganizationCode; ResourceType; ResourceName; ResourceCode; UomCode | Block preview | Supply the missing create fields; OrganizationCode may derive OrganizationId through the documented REST validation path | Creating a production resource |  |
| Resource update identity | ResourceId; explicit PATCH intent; at least one explicitly changed writable attribute | Block preview | Resolve the existing ResourceId and validate only supplied changes; do not require unchanged creation fields | Updating a production resource | resolve_parent_resource |
| Costing | Optional CostedFlag; optional DefaultExpenditureTypeId or DefaultExpenditureTypeName | On create, use the create-only default in ora_defaulting_rules.md. On PATCH, leave an omitted CostedFlag unchanged. Block invalid supplied flag values. | Use Y or N when CostedFlag is supplied; allow a blank expenditure type with either Y or N on create and validate an expenditure type only when supplied | Creating or updating a resource |  |
| Labor instance | LaborInstanceCode; LaborInstanceName; optional PartyId or RegistryId; optional PrimaryWorkCenterId or PrimaryWorkCenterCode | Block the child request | Supply values valid for a LABOR parent resource | Creating or updating a labor instance | resolve_parent_resource |
| Equipment instance | EquipmentInstanceCode; EquipmentInstanceName; optional AssetId or AssetNumber; optional PrimaryWorkCenterId or PrimaryWorkCenterCode | Block the child request | Supply values valid for an EQUIPMENT parent resource | Creating or updating an equipment instance | resolve_parent_resource |
| Automation program file | ProgramFileId or ProgramFileName | Block the child request | Supply one program-file identifier for an automation-enabled equipment resource | Creating a program-file association | resolve_parent_resource |

## Expenditure Type Contract

Oracle's [Create one resource REST contract](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-productionresources-post.html) makes `DefaultExpenditureTypeId` and `DefaultExpenditureTypeName` optional and nullable. Do not require either field solely because `CostedFlag` is Y. Preserve a blank expenditure type with either Y or N; REST represents these flags as `true` and `false`.

For project-specific manufacturing transactions, Oracle derives a missing resource expenditure type from the Labor/Nonlabor Transaction Type configured in Manage Default Expenditure Types. Resources with costing disabled are not transferred to Costing. These transaction rules do not make expenditure type mandatory at resource creation. See [Transfer Transactions from Production to Costing](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26a/faumf/transfer-transactions-from-production-to-costing.html).

## Update Contract

Oracle's [Update one resource REST contract](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-productionresources-resourceid-patch.html) identifies the target by ResourceId and does not require the create fields in every PATCH body. The Data Loader must validate the exact live update mapping. Its source must retain the resolved target identity and only the explicitly requested writable changes. Omission is not an instruction to reset a value or clear an expenditure type. An explicit clear requires a supported, validated core.data-loader mapping; never infer a clear from an empty source cell.

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| ResourceType is LABOR and HcmSchedulingGroupCode is supplied | Plant HCM scheduling must be enabled and the scheduling group must be valid | Stop if the service validation fails |  |
| AutomationEquipmentFlag is Y | ResourceType must be EQUIPMENT and plant robotics must be enabled | Stop until the service validation passes |  |
| A primary work center is supplied for an instance | The work center must be assigned to the parent resource | Stop until the association is valid | resolve_work_center_by_id |
| An equipment asset is supplied | The asset must be eligible for the plant and work-center context and not already actively associated | Stop until a valid asset is supplied | resolve_equipment_asset_by_id |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| ResourceType | Accept only a valid ORA_WIS_RESOURCE_TYPE value; normalize a supplied value to uppercase before persistence | Create; update only when supplied |  |
| ResourceClassCode | Require an active ORA_WIS_RESOURCE_CLASS value when supplied | Create or update |  |
| ResourceCode and ResourceName | Require uniqueness within OrganizationId; an update must not conflict with another resource | Create; update only when supplied |  |
| UomCode | Require a valid unit of measure; do not change it after work-center assignment or resource-rate use | Create; update only when supplied |  |
| PATCH omission | Leave omitted fields unchanged; do not inject create-only defaults, unchanged create fields, or inferred expenditure-type clears | Update |  |
| InactiveDate | Require a future date; an instance cannot end after its parent resource | Deactivation or update |  |
| Client-generated IDs | Do not send ResourceId, LaborInstanceId, EquipmentInstanceId, or EquipmentProgramFileId on create | Create |  |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MFGRES.VALIDATE_INPUT | decision | 1 | validate_input | valid->MFGRES.DEPENDENCIES;invalid->MFGRES.BLOCKED | none | stop | A Manufacturing Resources create, update, child-instance, or program-file request is prepared. |
