# Reference Lookups

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_loader_business_object | Step 1 | Registered business object name CpqChargeSetSync | Delegate to core.data-loader live dataLoaderBusinessObjects metadata and DAT-template/schema workflow; no task-local REST call | Registered discriminator, template/schema, action and attribute metadata including chargeId when present | Exact CpqChargeSetSync match accepted by core metadata/schema validation | Registered DAT schema and template for the POST trigger | Stop with catalog_or_metadata_mismatch and the exact core failure stage |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Data Loader metadata is needed | Delegate schema and DAT-template retrieval to core.data-loader. |
| The source DAT is prepared | Generate through core.data-loader with operation create and format dat; apply the immutable-source validation owned by ora_input_validation.md. |
| chargeId has a generated integer placeholder | No business-record lookup applies; this optional surrogate has no business significance. |
| A direct pricing endpoint or independent REST execution document is absent | The declared execution route remains the registered Data Loader adapter. Do not substitute direct REST or reject REST-backed DAT merely because no direct-call document exists. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DATA_LOADER_SYNC.RESOLVE_CHARGE_SET | step | 10 | reference_lookup | resolved->DATA_LOADER_SYNC.VALIDATE_CHARGE_SET_LOAD;invalid->DATA_LOADER_SYNC.HANDLE_ISSUE | none | stop | Resolve the Data Loader business object and download its DAT template/schema |
