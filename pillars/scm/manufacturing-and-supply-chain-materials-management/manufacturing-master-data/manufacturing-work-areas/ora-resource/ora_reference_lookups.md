# Manufacturing Work Areas Reference Lookups

All resolvers below are read-only Fusion REST `GET` operations. Invoke them only through `core.fusion-api.rest-api-client` with `REST-Framework-Version: 9`, `onlyData=true`, and the listed `fields`; never use them to create, update, or delete Fusion data.

## Live Lookups

| Resolver | Runs when | Request | Fields | Match rule | Result / failure rule |
|---|---|---|---|---|---|
| verify_inventory_organization | Every request | `GET /fscmRestApi/resources/11.13.18.05/inventoryOrganizations?q=OrganizationCode='<organization-code>'` | OrganizationId, OrganizationCode, OrganizationName | Exactly one record with the supplied code | Return confirmed organization identity. Zero or multiple results block the workflow. |
| verify_work_area_absent_for_create | Before create | `GET /fscmRestApi/resources/11.13.18.05/workAreas?q=OrganizationCode='<organization-code>' and WorkAreaCode='<work-area-code>'`; repeat with `WorkAreaName` | WorkAreaId, OrganizationCode, WorkAreaCode, WorkAreaName, InactiveDate | Both code and name queries return zero records | Continue only when both identities are absent. Any result blocks the create. |
| resolve_existing_work_area_for_update | Before update | `GET /fscmRestApi/resources/11.13.18.05/workAreas?q=OrganizationCode='<organization-code>' and WorkAreaName='<work-area-name>'` | WorkAreaId, OrganizationCode, WorkAreaCode, WorkAreaName, WorkAreaDescription, InactiveDate | Exactly one matching active record | Return the existing work-area identity. Zero, multiple, or inactive results block the update. |

The Oracle `workAreas` collection supports filtering by OrganizationCode, WorkAreaCode, WorkAreaName, WorkAreaId, and InactiveDate. Source: https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/25c/fasrp/op-workareas-get.html

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| WA.REFERENCE_LOOKUPS | step | 2 | reference_lookup | resolved->WA.DEPENDENCIES;blocked->WA.FAILED;failure->WA.FAILED | WA.VALIDATE | stop | Resolve organization and create/update work-area identity before source preparation. |
