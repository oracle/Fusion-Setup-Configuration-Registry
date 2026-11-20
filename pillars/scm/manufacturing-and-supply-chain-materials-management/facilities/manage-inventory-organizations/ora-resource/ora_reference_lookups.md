# Manage Inventory Organizations Reference Lookups

## Source Evidence

| Source | Used For |
|---|---|
| Oracle BestPractise guide | Definition/reference count requests for the required design check |
| Oracle Fusion Cloud SCM REST API: Get all organizations, https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/fasrp/op-inventoryorganizations-get.html | Read-only collection endpoint, query support, and organization response fields |
| Oracle Fusion Cloud SCM REST API: Inventory Organizations Open List of Values REST Endpoints, https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/api-scm-common-list-values-scm-common-inventory-organizations-open-list-values.html | Globally accessible organization LOV endpoint |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| find_inventory_organization_exact | A source organization must be identified for a copy request, or a proposed organization must be checked for a duplicate | OrganizationId, OrganizationCode, OrganizationName | /fscmRestApi/resources/11.13.18.05/inventoryOrganizations?fields=OrganizationId,OrganizationCode,OrganizationName,Status,InventoryFlag&onlyData=true&q=<exact OrganizationCode or OrganizationName expression> | OrganizationId, OrganizationCode, OrganizationName, Status, InventoryFlag | Use OrganizationId when supplied. Otherwise trim outer whitespace and require exactly one exact OrganizationCode or OrganizationName match; for a source copy, require InventoryFlag=true. For duplicate checking, check every proposed OrganizationCode and OrganizationName and retrieve all result pages. Any exact matching OrganizationCode or OrganizationName is a conflict. Retain checked codes, matched codes, environment, lookup time, and completion evidence for reuse by the design check; an empty result is valid only after all proposed identities and result pages have been checked. | OrganizationId: OrganizationId; OrganizationCode: OrganizationCode; OrganizationName: OrganizationName; Status: Status; InventoryFlag: InventoryFlag; for duplicate checking also retain CheckedOrganizationCodes, ExistingSubmittedOrganizationCodes, and DuplicateCheckComplete | For source copy, stop and request one unambiguous inventory organization. For duplicate checking, stop and request a distinct name or code. Do not fuzzy-match or select the first result. |
| count_definition_inventory_organizations | Any request creates inventory organizations, including copy-to-new and bulk creation | ItemGroupingCode; optional MasterOrganizationId when evaluating one master organization | /fscmRestApi/resources/11.13.18.05/inventoryOrganizations?q=ItemGroupingCode='ORA_RCS_IGB_DFTN'&totalResults=true&limit=1&fields=OrganizationId&onlyData=true | totalResults | URL-encode query values. When scoped to one master organization, add the same MasterOrganizationId filter to this request and the reference count request. Read totalResults as an estimated count, not count; require a nonnegative integer, accept zero, and block absent, negative, fractional, or nonnumeric values. Preserve the environment, scope, lookup time, and count evidence. Do not load all organizations. | ExistingDefinitionCount: totalResults | If the count is unavailable, return an error and stop creation until it can be resolved. |
| count_reference_inventory_organizations | Any request creates inventory organizations, including copy-to-new and bulk creation | ItemGroupingCode; optional MasterOrganizationId when evaluating one master organization | /fscmRestApi/resources/11.13.18.05/inventoryOrganizations?q=ItemGroupingCode='ORA_RCS_IGB_RFRC'&totalResults=true&limit=1&fields=OrganizationId&onlyData=true | totalResults | URL-encode query values. Apply the same optional MasterOrganizationId scope used for the definition count. Read totalResults as an estimated count, not count; require a nonnegative integer, accept zero, and block absent, negative, fractional, or nonnumeric values. Preserve the environment, scope, lookup time, and count evidence. Do not load all organizations. | ExistingReferenceCount: totalResults | If the count is unavailable, return an error and stop creation until it can be resolved. |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Direct OrganizationId is provided for a source copy | Use the ID to retrieve and confirm the source organization before approving a copy workflow |
| OrganizationCode or OrganizationName is provided | Run the exact-match lookup before duplicate validation or source-copy selection |
| A required source or duplicate lookup is unavailable, inaccessible, or returns an ambiguous source | Stop before any copy, create, or update operation |
| A required definition/reference count or completed duplicate-check evidence is unavailable | Return an error stating which value is missing and stop creation until the design check can be completed |
| A lookup result belongs to a different environment or count scope | Stop and repeat the declared lookup in the selected environment and scope; do not combine mismatched evidence |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| INVORG.RESOLVE_EXISTING | decision | 20 | reference_lookup | resolved->INVORG.COUNT_DEFINITION;not_required->INVORG.COUNT_DEFINITION;blocked->INVORG.HANDLE_ERROR;failure->INVORG.HANDLE_ERROR | INVORG.VALIDATE_INPUT | stop | Resolve a source organization or check exact name/code conflicts when the request supplies an organization identifier |
| INVORG.COUNT_DEFINITION | decision | 30 | reference_lookup | counted->INVORG.COUNT_REFERENCE;not_required->INVORG.READY_NOT_REQUIRED;unavailable->INVORG.HANDLE_ERROR | INVORG.RESOLVE_EXISTING | stop | For a proposed inventory-organization create, resolve the estimated existing definition-organization count; an unavailable count is an error |
| INVORG.COUNT_REFERENCE | decision | 40 | reference_lookup | counted->INVORG.ENFORCE_DEFINITION_REFERENCE_MIX;unavailable->INVORG.HANDLE_ERROR | INVORG.COUNT_DEFINITION | stop | Resolve the estimated existing reference-organization count using the same scope as the definition count |
