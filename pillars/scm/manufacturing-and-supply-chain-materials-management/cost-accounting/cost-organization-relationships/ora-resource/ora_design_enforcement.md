# Design Enforcement

## Source

| Source | Location | Used For |
|---|---|---|
| Oracle Cost Organization Relationship | https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/faims/cost-organization-relationship.html | Mandatory association and period-end-validation design constraints |
| Oracle Create Cost Organization Relationships | https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/faims/create-cost-organization-relationships.html | Date, book, ledger, and validation configuration rules |
| Oracle Important Points to Know Before Creating Cost Organization Relationships | https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/faims/important-points-to-know-before-creating-cost-organization-relationships.html | Post-save restrictions and period-impact guidance |
| Cost Book-only review scope | An association-only request must not create or submit a Cost Organization Relationship record | Scope enforcement for Cost Book-only requests |
| Cost Organization Book Relationships Period End Validations operation policy | This Business Object supports update or PATCH only; creation and deletion are not allowed | Period End Validations operation enforcement |
| Period End Validations PATCH business validations | Resolve PeriodicAverageCostBook through costBooksLOV; restrict updates to existing validation types; enforce the supplied PeriodPendingCloseFlag and PeriodCloseFlag update restrictions | Period End Validations PATCH design enforcement |

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Validate organization compatibility | Confirm the Cost Organization, Item Validation Organization, and each Inventory Organization meet the documented legal-entity, business-unit, and item-master constraints. |
| 2 | Validate primary costing design | Confirm a primary Cost Book is associated with the primary Ledger of the Cost Organization legal entity. |
| 3 | Validate effective dating and period design | Confirm the effective start dates and first opened periods reflect the intended transaction-costing start and period treatment. |
| 4 | Validate close controls when configured | For each selected period-end validation, confirm its existing-record eligibility, Cost Book type, timing, and State. This follow-on close-process configuration does not block creation of a Cost Book association. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Creating or updating the relationship header or associations | Error | | The Item Validation Organization is not an item master organization in the same legal entity as the Cost Organization | Use a compliant item master organization and do not use it as a transactional inventory organization. | Yes |
| The user asks only to associate or map a Cost Book to an existing Cost Organization | Error | | A `costOrgRelationships` record is created, presented, validated, or submitted without an explicit request to create or update the Cost Organization Relationship | Prepare and present only the editable `costOrgCostBooks` data file. Treat Item Validation Organization and Set assignment values as dependency-validation inputs; omit attribute-details and key-fields workbooks unless explicitly requested. | Yes |
| An Inventory Organization is associated | Error | | The Inventory Organization has a different legal entity or Profit Center Business Unit, a different item master organization, or an existing Cost Organization association | Associate only inventory organizations that satisfy all documented constraints. | Yes |
| A ledger-less Cost Book association is being created | Error | resolve_primary_cost_book_by_cost_organization | The automatic association lookup finds no primary Cost Book for the Cost Organization | Add a primary Cost Book associated with the legal entity's primary Ledger, then rerun the ledger-less association validation. | Yes |
| A periodic average cost enabled Cost Book is associated | Error | | Pending Period Close is selected for a validation that does not support it | Restrict Pending Period Close to the documented periodic-average-cost validations. | Yes |
| Cost Organization Book Relationships Period End Validations is requested | Error | | The source operation is create, POST, delete, or DELETE | Permit only a PATCH update for an existing Period End Validations record. | Yes |
| A Cost Organization Book Relationships Period End Validations PATCH update is requested | Error | resolve_cost_book_exact | PeriodicAverageCostBook is not resolved from costBooksLOV | Resolve the Cost Book first and retain PeriodicAverageCostBook as the Cost Book type evidence. | Yes |
| A Cost Organization Book Relationships Period End Validations PATCH update is requested | Error | resolve_existing_period_end_validations | The requested ValidationType is not present for the resolved CostOrgId and CostBookId | Update only the exact returned existing ValidationType. | Yes |
| PeriodicAverageCostBook is Y and ValidationType is PENDING_ACCOUNTING_EVENTS or UNPROCESSED_JOURNALS | Error | resolve_cost_book_exact | The PATCH changes PeriodPendingCloseFlag or PeriodCloseFlag | Do not update either attribute for these validation types when the Cost Book is periodic average cost enabled. | Yes |
| RenderPeriodPendingCloseFlag is not true | Error | resolve_existing_period_end_validations | The PATCH changes PeriodPendingCloseFlag | Update PeriodPendingCloseFlag only when RenderPeriodPendingCloseFlag is true. | Yes |
| DisablePeriodPendingCloseFlag is true | Error | resolve_existing_period_end_validations | The PATCH changes PeriodPendingCloseFlag | Do not update PeriodPendingCloseFlag. | Yes |
| DisablePeriodPendingCloseFlag is true | Error | resolve_existing_period_end_validations | The PATCH changes PeriodCloseFlag | Do not update PeriodCloseFlag. | Yes |
| A relationship has already been saved | Error |  | The change attempts to alter an immutable effective start date, first opened period, processed Inventory Organization association, or processed Cost Book Ledger | Create a new compliant relationship or Cost Book where Oracle requires it; do not overwrite processed history. | No |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_primary_cost_book_by_cost_organization | A ledger-less Cost Book association is being created | Primary CostBookId, Primary CostBookCode, PrimaryBookFlag | ora_reference_lookups.md |
| resolve_cost_book_exact | A Cost Organization Book Relationships Period End Validations PATCH update is requested | CostBookId, CostBookCode, PeriodicAverageFlag from PeriodicAverageCostBook | ora_reference_lookups.md |
| resolve_existing_period_end_validations | A Cost Organization Book Relationships Period End Validations PATCH update is requested | ValidationType and returned Period End Validation field controls | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COR.ENFORCE_DESIGN | decision | 17 | design_enforcement | compliant->COR.PREVIEW_GATE;blocked->COR.HANDLE_ISSUE | COR.APPLY_DEFAULTS | stop | Creating or updating Cost Organization Relationships |
