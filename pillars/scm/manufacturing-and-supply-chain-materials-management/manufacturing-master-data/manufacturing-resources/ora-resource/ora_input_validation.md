# Input Validation

## Validation Applicability

Apply the Required Groups and Field Validation rules before source preparation,
using each row's Applies When scope for the selected mode and operation. REST
parent creates follow the REST Organization Identity Contract; parent UOM
validation applies to both REST and native FSM under the Resource UOM Contract.
PATCH and child-only operations retain their scoped rules below.

Validate the exact prepared artifact again before Task Hook approval. REST uses
the organization and UOM artifact-validation nodes below; native FSM preserves
its exported mappings and uses the task's FSM artifact-validation and approval
gate. Lookup execution belongs to the task-validation nodes and
[Reference Lookups](ora_reference_lookups.md); default application belongs to
[Defaulting Rules](ora_defaulting_rules.md).

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Resource creation identity | OrganizationId or OrganizationCode; ResourceType; ResourceName; ResourceCode; UOMCode (UomCode in an existing source mapping) | Block missing identity fields; defer an omitted UOM to MFGRES.RESOLVE_UOM, then require a validated UOM before preview | Supply missing identity fields. Apply the Resource UOM Contract below. For REST, apply the REST organization identity contract; accept both identifiers at intake only for verification, never together in the outbound parent payload | Creating a production resource |  |
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

## Resource UOM Contract

The profile-based default is FSCR preparation policy requested for this task; it is not a claim that productionResources defaults an omitted REST field. The public [create contract](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-productionresources-post.html) requires `UOMCode`.

The Field Validation and Standard Defaults tables govern both parent resource preparation modes. REST uses `UOMCode`; native FSM keeps its target-exported UOM field and metadata. Scheduling-class eligibility is left to REST service validation; do not request scheduling intent or perform a separate class lookup for UOM preparation. See [Public Sources](ora_reference_lookups.md#public-sources) for lookup contracts and release gaps.

## REST Organization Identity Contract

The reported productionResources batch-create defect returns `27035`, `Attribute OrganizationId is required.`, when both organization attributes are sent. The single-identifier rule is a workaround supplied by the developer, not an Oracle-documented exclusivity requirement. The public [26C create contract](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-productionresources-post.html) lists both attributes and shows an ID-only request. See [Public Sources](ora_reference_lookups.md#public-sources) for the latest-release documentation check.

The following Field Validation rows own the workaround. Apply them to every productionResources parent record in the exact prepared artifact before Task Hook approval. A successful check of one row or of the original workbook does not validate the final batch.

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
| REST organization input | Require at least one nonblank organization identifier on parent create. Validate every supplied nonblank ID as a positive integer without precision loss and every supplied code against the live field contract. A supplied invalid value blocks; never discard it to make the other identifier pass | REST parent create, including every batch part |  |
| REST organization selection | Keep ID-only input as ID-only and code-only input as code-only. If both are nonblank, require resolve_production_resource_organization evidence first, then retain OrganizationId and omit OrganizationCode from the parent source. Keep the verified pair in validation evidence, separate from upload data | REST parent create | resolve_production_resource_organization |
| REST organization serialization | Require exactly one organization attribute in each parent create payload. Remove the unselected attribute from the productionResources worksheet/CSV columns and DAT METADATA mapping, not just its value. Empty text, null, or a blank cell in a retained column is not proof of omission. Inspect the prepared ZIP and exact live mapping; block if omission cannot be established. Do not reinsert an ID resolved from a code or a code resolved from an ID | REST parent create and final immutable artifact validation |  |
| REST mixed organization columns | If rows use different identifier alternatives, prepare separate homogeneous sources and separate core.data-loader loads, each with one organization column. Do not combine them into a two-column source or an archive with duplicate business-object roots. Preserve every requested row and its original organization | REST create batch with ID-only and code-only rows |  |
| REST organization scope | On PATCH, retain ResourceId and only the requested writable changes; do not add organization attributes to the parent request body. For child-only operations, preserve required child organization keys and metadata-only ancestors without inventing a parent create. Native FSM packages keep their exported columns and key mappings; this REST workaround does not strip FSM or child fields | PATCH, child-only operations, or native FSM |  |
| ResourceType | Accept only a valid ORA_WIS_RESOURCE_TYPE value; normalize a supplied value to uppercase before persistence | Create; update only when supplied |  |
| ResourceClassCode | Require an active ORA_WIS_RESOURCE_CLASS value when supplied | Create or update |  |
| ResourceCode and ResourceName | Require uniqueness within OrganizationId; an update must not conflict with another resource | Create; update only when supplied |  |
| UomCode | Normalize an explicitly supplied source UomCode to the REST UOMCode mapping without changing its value; conflicting aliases block. Preserve a valid supplied code even if it differs from ORA_RCS_HOUR_UOM. Validate the exact code in the selected environment; never replace an invalid supplied code with a default. A nonblank unknown, malformed, inactive or ambiguous UOM requires correction. Do not change UOM after work-center assignment or resource-rate use; core.data-loader service validation remains authoritative for update eligibility | Parent create in either mode; update only when UOM is explicitly supplied | resolve_resource_uom |
| Omitted resource UOM | On parent create only, treat absent, null or whitespace-only UOM as omitted. Read ORA_RCS_HOUR_UOM through resolve_resource_hour_uom_profile, then validate that exact configured code through resolve_resource_uom before applying the default. If unavailable, empty, invalid or ambiguous, block preview and request a UOM. Never hardcode HRS, select a class base unit, infer a code from a display name, or rely on server-side defaulting | Parent create in either mode with UOM omitted | resolve_resource_hour_uom_profile |
| REST UOM serialization | Every parent create in the final artifact must map one explicit nonblank REST UOMCode equal to its verified selected code. A source header UomCode is permitted only if the exact live Data Loader mapping proves it serializes as UOMCode; do not send UomCode, UnitOfMeasure, a display name, a profile name or a class code as a substitute. Bind evidence to the row, selected environment, execution identity and artifact. Reject omitted, blank, changed or unverified codes and conflicting mappings | REST parent create and final immutable artifact validation; explicit UOM changes on PATCH |  |
| UOM update and format scope | On PATCH or an existing native FSM row, never default an omitted UOM. Preserve an explicitly requested valid UOM change only when allowed by the service. Child-only operations do not create or default parent UOM fields. Native FSM retains exported UOM columns and keys, including supplied existing values | Updates, child-only operations and native FSM |  |
| PATCH omission | Leave omitted fields unchanged; do not inject create-only defaults, unchanged create fields, or inferred expenditure-type clears | Update |  |
| InactiveDate | Require a future date; an instance cannot end after its parent resource | Deactivation or update |  |
| Client-generated IDs | Do not send ResourceId, LaborInstanceId, EquipmentInstanceId, or EquipmentProgramFileId on create | Create |  |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MFGRES.VALIDATE_INPUT | decision | 1 | validate_input | valid->MFGRES.RESOLVE_ORGANIZATION;invalid->MFGRES.BLOCKED | none | stop | Validate supplied Manufacturing Resources input and operation. For REST parent creates apply REST organization input; both nonblank identifiers require the next lookup before selection. Normalize UOM aliases and reject conflicts. Defer omitted create UOM and live UOM validity to MFGRES.RESOLVE_UOM; never require unchanged PATCH fields. Defer final serialized-artifact checks to the REST artifact nodes. |
| MFGRES.VALIDATE_REST_ORGANIZATION | decision | 8 | validate_input | valid->MFGRES.VALIDATE_REST_UOM;invalid->MFGRES.BLOCKED | MFGRES.ROUTE_REST | stop | Inspect every parent record and its column mapping in the exact prepared REST upload artifact under REST organization selection, serialization, mixed organization columns, and scope. Reject both organization attributes even if one is blank or null; require exactly one for creates. Verify PATCH and child-only boundaries without requiring create fields. Missing artifact or mapping evidence is invalid. Do not repair an immutable artifact here; return the correction for fresh core.data-loader preparation, validation, and approval. |
| MFGRES.VALIDATE_REST_UOM | decision | 9 | validate_input | valid->MFGRES.REST_READY;invalid->MFGRES.BLOCKED | MFGRES.VALIDATE_REST_ORGANIZATION | stop | Apply REST UOM serialization and UOM update and format scope to every applicable parent row in the exact prepared artifact. Require current same-target and execution-identity lookup evidence, explicit UOMCode mapping on creates and supplied changes. An omitted PATCH UOM remains absent; child-only operations add no parent UOM. Missing evidence, a changed code or unproven mapping blocks readiness; any correction requires fresh preparation, validation and artifact-bound approval. |
