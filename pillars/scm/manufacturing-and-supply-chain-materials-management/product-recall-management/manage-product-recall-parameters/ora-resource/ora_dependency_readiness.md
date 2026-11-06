# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 0 | Project environment identity | The configured Fusion REST host must equal the active Run Book server host before any task lookup or Data Loader metadata call. |
| 1 | Product Recall Management access | The executor has the Manage Product Recall Parameters privilege and Data Loader can describe the selected business objects. |
| 2 | Referenced setup identities | Resolve approved actual inventory-organization IDs, names or codes through the describe-backed inventoryOrganizations GET; exclude the traceability default marker -1 and reconcile that default through find_existing_recall_parameter_rows instead. Resolve coordinator display names through the publicWorkers finder GET. Require one exact active/current match before deriving IDs. Validate other referenced setup through its named resolver. |
| 3 | Product recall lookups | Containment action codes are configured before a true BypassTaskFlag is used, where the configured business process requires them. |
| 4 | Preflight handoff | Require Data Loader's verified persisted preflight for the final immutable artifact before Task Hook data-load. Return ordered task rule results to Task Hook for preview creation; approval follows successful task validation under core.data-loader's policy, not as a prerequisite of this task graph. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| recall_project_environment | Bound project target environment | Yes | Any project-bound external operation | Verify | Active project Run Book server URL and configured restBaseUrl | | A result from another Fusion pod cannot validate this project's setup | Select the matching project environment through the owning workflow; do not reinterpret cross-pod GET results | Matching scheme, host and port; no customer payload |
| recall_parameters_privilege | Manage Product Recall Parameters access | Yes | Always | Verify | Assigned role and Data Loader describe result | describe_recall_parameter_business_objects | Oracle documents ENQ_MANAGE_PRODUCT_RECALL_PARAMETERS for manage access to the recall parameter resources | Provide an authorized implementation identity; stop if describe is denied | Supported business objects and methods |
| recall_reference_identities | Referenced lookup code, organization, subinventory, locator, cost center/location, business unit, ledger, owner, or coordinator | Conditional | A supplied row refers to the relevant identity; the traceability default marker -1 is not an inventory-organization reference | Lookup | Target-environment lookup result | resolve_inventory_organization | Every referenced identity must resolve exactly before a payload is shaped | Provide the exact approved name and parent context; a name can supply a code or ID only after the routed GET returns one active exact match | Resolved canonical values and IDs required by the current contract |
| recall_owner_coordinator | Active owner or coordinator worker | Conditional | recallContainmentTaskOwners supplies OwnerName | Lookup | publicWorkers finder GET result | resolve_owner_or_coordinator_worker | A display name is a search term, not identity evidence until all results have been paged, exact-matched, deduplicated and checked current | Supply an approved full display name; if it resolves to zero or multiple current workers, provide PersonNumber or a supported unique worker identifier | Sanitized row-level match status, count and canonical identity for the current run only |
| recall_financial_context | Business unit and ledger | Conditional | The selected Data Loader schema exposes a business-unit or ledger field | Lookup | finBusinessUnitsLOV and ledgersLOV lookup results | resolve_business_unit | Business-unit and ledger relationships must be exact and active when attributes are exposed | Provide an exact name or ID; reconcile a supplied ledger to the business unit's PrimaryLedgerId | BusinessUnitId, PrimaryLedgerId, LedgerId, CurrencyCode |
| recall_bypass_lookup | Containment action code lookup | Conditional | BypassTaskFlag is true and bypass count or disposal tasks are used | Verify | Product Recall Lookups configuration | | Oracle documentation requires this lookup when the bypass attribute is enabled | Confirm the required containment action codes exist before preview | Validation evidence |

For traceability default and exception reconciliation, use find_existing_recall_parameter_rows before selecting create or update. A default-only change requires no actual inventory-organization lookup. Organization-specific exception rows retain the exact active-organization dependency. Default-cardinality enforcement belongs to ora_design_enforcement.md.

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | The required preflight access and identity evidence is present | Yes for documented read-only lookups; no create |
| Lookup | An exact display value must be resolved before preview | Yes for describe-backed read-only lookup only |
| Blocked | A required privilege, identity, or lookup is missing or ambiguous | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RECALL.PARAMETERS.RESOLVE-DEPENDENCIES | decision | 25 | resolve_dependency | ready->RECALL.PARAMETERS.DESCRIBE-CONTRACT;blocked->RECALL.PARAMETERS.HANDLE-DEPENDENCY-ERROR | RECALL.PARAMETERS.LOOKUP-EXISTING | stop | A payload or operation is being prepared |
