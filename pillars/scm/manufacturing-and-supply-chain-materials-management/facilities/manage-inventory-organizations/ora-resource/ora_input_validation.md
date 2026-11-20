# Manage Inventory Organizations Input Validation

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Organization identity | Accept OrganizationCode or OrganizationName; block and ask for organization code or name when neither is supplied | Always |  |
| Inventory organization classification and status | Apply InventoryFlag=true and Status=Active when either value is not explicitly supplied. After defaults are applied, require InventoryFlag=true and Status=Active; false or a non-Active status does not create an inventory organization | Creating an inventory organization |  |
| Master organization | Accept MasterOrganizationId, MasterOrganizationCode, or MasterOrganizationName; block and ask for one master organization reference when none is supplied | Always |  |
| Item-definition organization | Accept ItemDefinitionOrganizationId, ItemDefinitionOrganizationCode, or ItemDefinitionOrganizationName; block and ask for a reference when none is supplied | Inventory organization create|  |
| Management business unit | Accept ManagementBusinessUnitId or ManagementBusinessUnitName; block when neither is supplied | Inventory organization create |  |
| Profit center business unit | Accept ProfitCenterBusinessUnitId or ProfitCenterBusinessUnitName; preserve null or blank values when optional. Block when neither is supplied only if the selected environment metadata or a verified organization-specific rule requires a profit center business unit | Inventory organization create |  |
| Legal entity | Accept LegalEntityId or LegalEntityName; block when neither is supplied | Inventory organization create|  |
| Location | Accept LocationId, LocationCode; block when none is supplied | Inventory organization create |  |
| OrganizationCode length | Reject a value longer than 18 characters | OrganizationCode is supplied |  |
| OrganizationName length | Reject a value longer than 240 characters | OrganizationName is supplied |  |
| Item grouping code | Accept only ORA_RCS_IGB_DFTN (Definition Organization) or ORA_RCS_IGB_RFRC (Reference Organization). ORA_RCS_IGB_DFTN means the organization stores its own item attribute values; ORA_RCS_IGB_RFRC means it inherits item attribute values from an associated definition organization | ItemGroupingCode is supplied |  |
| Reference item grouping | Require an item-definition organization reference when ItemGroupingCode is ORA_RCS_IGB_RFRC; the reference must identify the associated definition organization | A reference organization is requested |  |
| Contract manufacturing | Require supplier and supplier site information before parameter completion | ContractManufacturingFlag is true |  |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| INVORG.VALIDATE_INPUT | step | 10 | validate_input | valid->INVORG.RESOLVE_EXISTING;invalid->INVORG.HANDLE_ERROR | none | stop | Before planning an inventory-organization create, copy, or parameter-update request |
