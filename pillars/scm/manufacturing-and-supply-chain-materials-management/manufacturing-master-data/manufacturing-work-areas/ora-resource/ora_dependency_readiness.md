# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Existing inventory organization | Confirm that the target organization exists through `verify_inventory_organization` before creating or updating a work area. |
| 2 | Validated Data Loader source | Validate the source for the selected import mode through core.data-loader before any import approval. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| WA.DEP.EXISTING_ORGANIZATION | Existing inventory organization | Yes | Every work-area request | Verify | Read-only Fusion inventoryOrganizations response | verify_inventory_organization | A work area must be scoped to a valid organization. | Provide a valid organization code and resolve any validation failure before approval. | Confirmed organization identity |
| WA.DEP.FSM_ARTIFACT | Validated FSM source | Yes | Before FSM import | Verify | core.data-loader validation result | | When FSM is selected, use its native package contract; this resource does not define an FSM file layout. | Use only the immutable source validated by core.data-loader. | Artifact name and SHA-256 |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Existing organization, work-area identity, and validated Data Loader source are confirmed | Yes |
| Blocked | Existing plant cannot be confirmed or the validated Data Loader source for the selected import mode is absent | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| WA.DEPENDENCIES | step | 3 | resolve_dependency | ok->WA.DESIGN;failure->WA.FAILED | WA.REFERENCE_LOOKUPS | stop | Validated work-area request |
