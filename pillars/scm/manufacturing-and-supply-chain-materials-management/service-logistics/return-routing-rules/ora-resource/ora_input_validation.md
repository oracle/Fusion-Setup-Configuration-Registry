# Return Routing Rules Input Validation

Validate the REST setup-data import against the selected Fusion environment's registered BO for REST, `returnRoutingRules`. If the caller supplies `ReturnRoutingRules`, resolve it to the exact registered discriminator before proceeding. Generate its sample, attribute-details workbook, and key-fields workbook through `core.data-loader`; never infer import columns or keys from a similarly named resource. Field requirements are operation-specific and must pass Data Loader source validation and preview.

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Business Object equals the live registered `returnRoutingRules` object | Stop if registration is absent, ambiguous, or names a different object | Before Data Loader preparation | |
| Supplied columns match live Business Object attributes | Reject unknown, duplicate, or ambiguous mappings; use the attribute-details workbook's type and length constraints | Every supplied field | |
| Enabled status field | Use only the exact accepted column and value format in the live Business Object attributes; stop if no status mapping is confirmed | When status is supplied or required by the operation | |
| Create, update, or delete keys and required values | Use the live key-fields and attribute-details workbooks for the selected operation, then require `core.data-loader` source validation and preview | Before import handoff | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RRR.VALIDATE_INPUT | step | 1 | validate_input | valid->RRR.LOOKUP_VALUES;invalid->RRR.RETURN_REFUSAL | none | stop | When Return Routing Rules setup data is prepared |
