# Intrastat Rules Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| `RuleSetCode` is missing or already exists | Stop before preview; return the value and the Fusion duplicate-rule-set diagnostic. |
| A supplied rule-type code or name has no single exact `JMF_IN_RULE_TYPE` match | Stop before preview; return the unresolved or conflicting rule-type value without guessing a code. |
| A supplied attribute-validation source type is `ALL` or has no single exact `JMF_IN_SOURCE_DOCUMENT` match | Stop before preview; return the unresolved source type without guessing a code. |
| A supplied attribute-validation attribute has no single exact `JMF_IN_ATTRIBUTE_CODE` match | Stop before preview; return the unresolved attribute without guessing a code. |
| A supplied fiscal-regime source transaction is `ALL` or has no single exact `JMF_IN_SOURCE_DOCUMENT` match | Stop before preview; return the unresolved source transaction without guessing a code. |
| A supplied fiscal-regime trading-partner type has no single exact `JMF_IN_TRADING_PARTNER_TYPE` match | Stop before preview; return the unresolved trading-partner type without guessing a code. |
| A supplied Intrastat Catalog has no single exact `intrastatCatalogs` match | Stop before preview; return the unresolved catalog without guessing `CategorySetId`. |
| A supplied parent `CategorySetId` conflicts with the exact Intrastat Catalog match | Stop before preview; return both supplied values and require a corrected source. |
| A supplementary-UOM child provides `CategoryCodeName` but has no resolved parent Intrastat Catalog ID | Stop before preview; resolve the parent catalog first and copy its canonical `CategorySetId` to the child. |
| A Fusion-owned `EstablishmentName` cannot be resolved | Stop before preview; return the unresolved field without guessing its identifier. |
| A supplied freight-terms code or meaning has no single exact `JMF_IN_DELIVERY_TERM` match | Stop before preview; return the unresolved or conflicting freight-terms value without guessing a code. |
| A supplied transport-mode code or meaning has no single exact `JMF_IN_TRANSPORT_MODE` match | Stop before preview; return the unresolved or conflicting transport-mode value without guessing a code. |
| A supplied rounding-rule code or meaning has no single exact `JMF_IN_DECIMAL_ROUND_METHOD` match | Stop before preview; return the unresolved or conflicting rounding-rule value without guessing a code. |
| A generated child row places a repeated numeric sentinel, such as `15` or `16`, in fields not supplied by the source | Stop before preview; regenerate the XLSX/DAT source with empty cells. Do not submit values that override BO foreign-key targets such as `CategoryId`, `CategorySetId`, or `SupplementaryUOM`. |
| A child row has no matching parent `RuleSetCode` | Stop before preview; provide or correct the parent rule set. |
| A requested child collection is absent from registered BO metadata | Classify as `catalog_or_metadata_mismatch`; obtain updated BO guidance. |
| Data Loader validation, preview, or import fails | Preserve redacted diagnostics; do not retry an upload or substitute direct REST. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input_validation | Required parent input or child-parent reference is missing or invalid. | Correct the stated source value and restart validation. |
| catalog_or_metadata_mismatch | The published BO metadata cannot express the requested record. | Obtain clarified registration or Data Loader guidance. |
| transport_or_environment | A read-only metadata, validation, or preview request is unavailable. | Restore access and rerun documented preflight. |
| approval_blocker | The immutable preview or execution approval is missing or stale. | Rebuild the preview and complete the Data Loader approval gate. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| A create or update is requested | Do not use direct REST POST, PATCH, or DELETE instead of `core.data-loader`. |
| A friendly value or lookup is unresolved | Do not guess, fuzzy-match, or select the first candidate. |
| A live operation fails or is indeterminate | Do not automatically retry or submit another load. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| INTRASTAT_RULES.PREPARE_LOADER | step | 120 | execution_gate | ready->RETURN_SUCCESS;blocked->RETURN_ISSUES | INTRASTAT_RULES.CHECK_READINESS | stop | The Data Loader source has passed task validation and is ready for the separate immutable-preview approval flow. |
| RETURN_SUCCESS | terminal | 130 | terminal | none | INTRASTAT_RULES.PREPARE_LOADER | continue | The validated source is ready for the Data Loader preview and approval workflow. |
| RETURN_ISSUES | terminal | 140 | terminal | none | none | continue | An input, dependency, metadata, preview, or approval gate failed. |
