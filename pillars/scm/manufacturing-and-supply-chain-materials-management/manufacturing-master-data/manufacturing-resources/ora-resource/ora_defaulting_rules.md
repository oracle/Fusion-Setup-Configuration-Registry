# Defaulting Rules

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| CostedFlag | N | Creating a resource and CostedFlag is omitted; never on PATCH | No |  |
| UOMCode | Exact ORA_RCS_HOUR_UOM value verified by MFGRES.RESOLVE_UOM, including active UOM validity; no literal default | Parent create in either mode with UOM omitted; never on PATCH or an existing native FSM row. Preserve any valid user-supplied code. Missing or invalid profile-derived UOM blocks preview and requires a user UOM; never hardcode HRS or select the class base unit | No | resolve_resource_hour_uom_profile |
| OrganizationId | No client-side payload default; retain a code-only REST create source without adding OrganizationId | OrganizationId is omitted and OrganizationCode is supplied; any service-derived or lookup-resolved ID remains validation context under the REST Organization Identity Contract in ora_input_validation.md | No |  |
| DefaultExpenditureTypeId | Derived from DefaultExpenditureTypeName | The ID is omitted and a name is supplied | Yes |  |
| PrimaryWorkCenterId | Derived from PrimaryWorkCenterCode | The ID is omitted and a code is supplied for a valid instance | Yes |  |
| PartyId, LaborIdentifier, LaborInstanceName | Derived from RegistryId or party data where documented | Creating a labor instance with the applicable alternate identifier | Yes |  |
| AssetId, EquipmentIdentifier, EquipmentInstanceName, PrimaryWorkCenterId | Derived from AssetNumber or asset data where documented | Creating an eligible equipment instance with the applicable alternate identifier | Yes | resolve_equipment_asset_by_id |

## Update Boundary

Create-only defaults do not apply to PATCH. Preserve an omitted CostedFlag and omitted expenditure-type fields; do not add them to the update source. Explicit supplied values take precedence over defaults. See the Update Contract and PATCH omission rule in ora_input_validation.md.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MFGRES.APPLY_UOM_DEFAULT | decision | 4 | apply_default | ready->MFGRES.DEPENDENCIES;failure->MFGRES.BLOCKED | MFGRES.RESOLVE_UOM | stop | Apply only the UOMCode default in Standard Defaults when the create input omitted UOM and this run has verified profile and UOM evidence. Preserve explicit valid input and record whether the selected value is user-supplied or profile-derived. Map the value to REST UOMCode or the verified target-exported native FSM UOM field before source preparation. For updates and child-only requests, apply no UOM default. Stale, mismatched or missing required evidence blocks. |
