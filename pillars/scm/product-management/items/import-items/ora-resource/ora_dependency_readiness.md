# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Item search index readiness | Run verify_item_search_index_readiness. Continue immediately for valid HTTP 200 zero-result search response. For HTTP 404 whose response body contains errorCode FND_ERROR_SEARCH_SERVICE_UNKNOWN_INDEXES, return the index-remediation handoff; do not continue this Import Items task. |
| 2 | Customer item source | Confirm a supplied source or prebuilt FBDI ZIP is readable. |
| 3 | Current public Oracle template | Fetch ItemImportTemplate.xlsm and bind its source, digest, sheet sequence, filenames, and export columns to the run. |
| 4 | Normalized item mapping | Resolve required or ambiguous business values and disclose unsupported facts. |
| 5 | Generated Item Import ZIP | Validate members, relative order, rows, Batch ID, and digest against the current workbook. |
| 6 | Core Data Loader handoff | Provide the unchanged ZIP and read-only validation evidence to core.data-loader preflight with `--business-object item`; the loader validates this selection against live FBDI metadata. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| item_search_index_readiness | Item search index readiness | Yes | Before the current Import Items preparation and validation workflow begins | Verify | Fusion Search API HTTP status and response body | verify_item_search_index_readiness | Detects whether the Item Index is available before preparing an item import | valid HTTP 200 zero-result search response passes. The documented HTTP 404 condition returns the index-remediation handoff to Product Management orchestration; do not prepare or import items until a later fresh lookup returns valid HTTP 200 zero-result search response. | index_readiness_status |
| customer_item_source | Customer item source | Yes | Always | Satisfied | Supplied customer source or prebuilt FBDI ZIP |  | Import preparation requires readable source evidence | Supply a readable customer item source or prebuilt FBDI ZIP | customer_item_source |
| item_import_template_mapping | Current public Oracle template | Yes | Always | Satisfied | Current public Oracle Item Import workbook |  | The package must use the current public workbook contract | Fetch and record the current public workbook before package generation | template source; digest; sheet sequence; filenames; export columns |
| normalized_item_mapping | Normalized item mapping | Yes | For non-ZIP input | Satisfied | Validated customer source mapping |  | Required and ambiguous values must be resolved before CSV generation | Complete every required mapping and resolve each ambiguity | normalized item mapping |
| generated_item_import_zip | Generated Item Import ZIP | Yes | Before handoff | Satisfied | Locally generated and validated immutable ZIP |  | Only a template-valid immutable package may be handed off | Correct any member, order, row, Batch ID, or digest validation issue | ZIP digest; member manifest; row counts; Batch ID |
| core_data_loader_handoff | Core Data Loader handoff | Yes | After validation | Satisfied | Import Items skill contract |  | Core Data Loader exclusively owns subsequent loader execution and live FBDI route validation | Pass the unchanged ZIP and validation evidence to core.data-loader preflight with `--business-object item` | ZIP digest; member manifest; validated item route outcome |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | The item-index lookup returns valid HTTP 200 zero-result search response | Yes; continue the current Import Items workflow |
| Remediation Required | The lookup returns HTTP 404 and the response body contains errorCode FND_ERROR_SEARCH_SERVICE_UNKNOWN_INDEXES | No; end Import Items with the index-remediation handoff and let Product Management orchestration select the separate remediation task |
| Blocked | The lookup returns any result other than the documented valid HTTP 200 zero-result search response or matching HTTP 404 condition | No; stop without beginning or continuing Import Items preparation |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ITEM_IMPORT.INDEX_DEPENDENCY_READY | step | 2 | resolve_dependency | ready->ITEM_IMPORT.VALIDATE_FBDI;blocked->ITEM_IMPORT.FAILED | none | stop | The lookup returned valid HTTP 200 zero-result search response. |
| ITEM_IMPORT.CONFIRM_LOADER_ROUTE | step | 4 | resolve_dependency | ready->ITEM_IMPORT.HANDOFF_GATE;blocked->ITEM_IMPORT.FAILED | ITEM_IMPORT.VALIDATE_FBDI | stop | Confirm the immutable ZIP and handoff evidence are complete; pass `--business-object item` during core.data-loader preflight for live FBDI route validation. |
