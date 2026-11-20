# Error Handling

## Source

| Source | Location | Used For |
|---|---|---|
| Oracle Important Points to Know Before Creating Cost Organization Relationships | https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/faims/important-points-to-know-before-creating-cost-organization-relationships.html | Association troubleshooting, restrictions, and no-retry remediation |
| Oracle Cost Organization Relationship | https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/faims/cost-organization-relationship.html | Relationship and period-end-validation constraints |
| Developer-validated Period End Validations Data Loader response behavior | A successful REST entity response may be recorded as a Data Loader object error; central team owns the registered response-contract correction | Safe disclosure and no-retry behavior for a response-classification failure |
| Cost Organization Relationships deletion behavior | Cost Organization Relationships UI | Relationship and association deletion scope; the supplied source does not establish owned Period End Validation cleanup after Cost Book association deletion |

## Error Situations

| Situation | What Should Happen |
|---|---|
| An Inventory Organization cannot be associated | Stop and verify its Profit Center Business Unit, legal entity, Below Legal Entity option, existing Cost Organization association, and item master organization before revalidating. |
| The required Ledger is unavailable for Cost Book association | Stop; run Update Subledger Application Options from Scheduled Processes, verify the Ledger is available, then revalidate. |
| A change targets an Inventory Organization association after transactions were processed | Stop; do not delete, reassign, or change the effective start date for the processed association. |
| A change targets a Cost Book Ledger after transactions were processed | Stop; do not change the Ledger. Create and associate a new Cost Book if a new Ledger is required. |
| Cost processing errors exist for the first opened period | Stop; resolve the cost processing errors before continuing. |
| A Cost Book association PATCH rejects CustomSurrogateId as not a whole number | Stop; leave CustomSurrogateId blank, identify the existing association with CostOrgId, CostBookId, and CostBookCode, then create a new validated archive and approval preview. |
| A Cost Book association PATCH rejects Maximum Open Periods | Stop; correct the value from user-confirmed business input, then create a new validated archive and approval preview. Do not infer the current open-period count from costOrgBooksLOV because that lookup does not expose it. |
| A create or delete is requested for Cost Organization Book Relationships Period End Validations | Stop; this Business Object permits only a PATCH update to an existing record. |
| A requested Period End Validation is not returned for the resolved Cost Organization and Cost Book | Stop; update only a ValidationType returned by costOrgBookPeriodEndValidations for the exact CostOrgId and CostBookId. |
| A Period End Validations PATCH changes a prohibited flag | Stop; retain the returned field control values and remove the prohibited PeriodPendingCloseFlag or PeriodCloseFlag update before creating a new approval preview. |
| A Period End Validations ValidationType has no exact CST_PERIOD_VALIDATION_TYPES match | Stop; provide a ValidationType returned by the authoritative lookup. Do not infer another validation type. |
| A Period End Validations State has no exact CST_PERIOD_VALIDATION_ACTIONS match | Stop; provide a State returned by the authoritative lookup. Do not infer another action code. |
| A Period End Validations PATCH Data Loader result records a returned updated REST entity as a data-set object error | Stop; preserve the Data Loader diagnostics, classify the result as a registered response-contract failure, and do not replay the import. Central team must correct the registered PATCH success-response handling before another retry. |
| Data Loader source or one of costOrgRelationships, costOrgInventoryOrgs, or costOrgCostBooks fails validation | Stop before preview, correct the source data, and revalidate through core.data-loader. |
| A Data Loader upload or initiation is requested without a current immutable approval preview and a later standalone approval | Stop before the first POST. |
| A direct REST submission is requested | Route the operation through core.data-loader; do not construct a direct REST request. |
| A delete request reaches a create/update-only input, dependency, or defaulting node | Stop before preview; correct operation routing and revalidate through the deletion branch rather than requiring new setup data. |
| Fusion rejects a deletion because of processed transactions, dependent references, or a changed target | Preserve the exact server error and confirmed partial outcomes. Stop; do not bypass the business restriction, expand the target scope, or automatically retry. |
| Cost Book association DELETE reports Not Found but the scoped association lookup still returns the selected book | Stop and preserve diagnostics and partial outcomes. Reconcile failed targets through resolve_existing_cost_book_associations_by_cost_organization and fresh registered Data Loader metadata. If the failure remains unexplained, obtain HCM Data Loader Error Analysis or backend routing diagnostics before proposing another attempt. Correct only failed rows and require new validation and approval; never replay successful rows or submit the parent while Cost Books remain. |
| A delete source or sample is needed | Delegate preparation to core.data-loader for only the requested costOrgRelationships, costOrgInventoryOrgs, or costOrgCostBooks objects, using its delete sample operation and metadata-declared keys. Do not use the default create-sample batch or request costOrgBookPeriodEndValidations deletion. The loader owns validation, preview, approval, submission, status, and result handling. |
| Deletion initiation succeeds but completion is unconfirmed | Report initiation only. Do not submit a dependent parent deletion or report that the target is gone. A later status/verification request uses the owning workflow and existing request identifiers. |
| Parent-only deletion completes or is rejected | Reconcile the actual relationship and child state after the load; preserve any server rejection without automatically deleting children. |
| The last Cost Book association is deleted | Disclose that the retained parent can have an incomplete costing design; do not silently create a replacement association or delete the parent. |
| Owned Period End Validation cleanup is claimed after Cost Book association deletion | Do not assume or promise cleanup; verify any claimed cleanup through the declared read-only lookup before reporting it. If no verification exists, disclose that cleanup is unverified. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | A required relationship, association, effective date, Cost Book, or close-validation input is missing or invalid | Correct the supplied relationship data. |
| Dependency readiness | A required organization, Cost Book, Ledger, or organization assignment is not ready | Complete or correct the prerequisite setup, then revalidate. |
| Design enforcement | A relationship violates legal-entity, business-unit, item-master, primary-cost-book, or immutable-history rules | Redesign the association without modifying processed history. |
| Process readiness | The required Ledger is not available for selection | Run Update Subledger Application Options and verify availability before retrying. |
| Data Loader validation | The source or a configured Business Object does not pass Data Loader validation | Correct the source data and generate a new immutable approval preview. |
| Fusion API | Fusion rejects a Cost Book association PATCH identifier or Maximum Open Periods value during import or load | Correct the documented field values from authoritative input, generate a new immutable archive, and obtain a new approval. |
| Fusion API response contract | A Period End Validations PATCH response contains the returned updated entity but Data Loader records it as an object error | Do not infer a failed business update or replay the import. Preserve the diagnostics and route the response-contract correction to the central team. |
| Approval blocker | Upload or initiation lacks current approval for its exact immutable preview | Stop before upload and obtain a new preview and separate approval. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Validation, dependency, or design failure | The affected association, violated rule, and corrective action. |
| Immutable-history restriction | The processed relationship attribute that cannot be changed and the documented safe alternative. |
| Data Loader validation failure | The affected Business Object, source validation result, and corrective action. |
| Data Loader approval gate | The immutable preview and required standalone approval action. |
| Period End Validations response-contract failure | The affected validation identities, Data Loader status, returned entity evidence, and the central-team remediation owner. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Missing, invalid, or noncompliant relationship input | Do not infer an organization, ledger, date, period, validation action, or legal-entity assignment. |
| Processed relationship history | Do not retry a prohibited change, delete a processed Inventory Organization association, or modify a locked Cost Book Ledger. |
| Data Loader validation or approval gate is incomplete | Do not upload, initiate, retry, or construct a direct REST request. |
| Period End Validations response-contract failure | Do not replay an import solely because Data Loader classified a returned updated REST entity as an object error. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COR.PREVIEW_GATE | decision | 18 | execution_gate | ready->COR.COMPLETE;blocked->COR.HANDLE_ISSUE | COR.ENFORCE_DESIGN | stop | A validated relationship change is ready for preview and later approval |
| COR.HANDLE_ISSUE | step | 30 | error_handler | disclosed->RETURN_ISSUES | none | stop | A prior node reports invalid, blocked, or failed |
| COR.COMPLETE | terminal | 20 | terminal | none | COR.PREVIEW_GATE | stop | The task-local validation and readiness workflow completed |
| RETURN_ISSUES | terminal | 31 | terminal | none | none | stop | Error disclosure completed |
| COR.DELETE_PREVIEW_GATE | decision | 26 | execution_gate | ready->COR.DELETE_COMPLETE;blocked->COR.HANDLE_ISSUE | COR.CHECK_DELETE_DEPENDENCIES | stop | The exact deletion source passed input and dependency validation and is ready for core Data Loader validation, preview, and its authoritative approval workflow |
| COR.DELETE_COMPLETE | terminal | 27 | terminal | none | COR.DELETE_PREVIEW_GATE | stop | Task-local deletion validation completed; this terminal is not evidence of a completed live deletion |
