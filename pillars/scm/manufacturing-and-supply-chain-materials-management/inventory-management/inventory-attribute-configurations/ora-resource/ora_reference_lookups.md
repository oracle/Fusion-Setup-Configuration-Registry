# Inventory Attribute Configurations Reference Lookups

## Source Evidence

| Source | Used For |
|---|---|
| Redwood `applicabilityLevelLOVFetch.js` | Applicability Level uses `ORA_INV_ATTR_APPL_CODE`, excludes `ORA_FEATURE_SPECIFIC`, and returns `LookupCode` with `Meaning`. |
| Redwood `attribute-mapping-rules-page-chains/getall_genericLookupsLOVFetch.js` | Source Type uses `ORA_INV_ATTR_MAP_SRC_TYPES` and returns `LookupCode` with `Meaning`. |
| User-provided lookup type | Status uses `ORA_INV_ATTR_STATUS`. |
| User-provided REST URL convention | The complete resource path is `/fscmRestApi/resources/11.13.18.05/{resource name}`. |
| User approval | Author the Applicability Level, Source Type, and Status resolvers. |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_inventory_attribute_applicability_level | After control normalization and before Data Loader handoff | Supplied Applicability Level Meaning and/or `ApplicabilityCode` | GET `/fscmRestApi/resources/11.13.18.05/genericLookupsLOV` with `q=LookupType='ORA_INV_ATTR_APPL_CODE' and LookupCode NOT IN ('ORA_FEATURE_SPECIFIC')` and `onlyData=true` | `LookupCode`, `Meaning` | Retrieve the scoped rows. Match Meaning and directly supplied LookupCode using trim plus case-insensitive exact comparison. With both supplied, require both to identify the same single row. Do not fuzzy-match or select the first row. | `ApplicabilityCode` from `LookupCode`; retain `Meaning` as resolution evidence. | Stop before Data Loader handoff on no match, multiple matches, or conflicting supplied code and Meaning. |
| resolve_inventory_attribute_mapping_source_type | After Applicability Level resolution and before Data Loader handoff | Supplied Source Type Meaning and/or `SourceType` | GET `/fscmRestApi/resources/11.13.18.05/genericLookupsLOV` with `q=LookupType='ORA_INV_ATTR_MAP_SRC_TYPES'` and `onlyData=true` | `LookupCode`, `Meaning` | Retrieve the scoped rows. Match Meaning and directly supplied LookupCode using trim plus case-insensitive exact comparison. With both supplied, require both to identify the same single row. Do not fuzzy-match or select the first row. | `SourceType` from `LookupCode`; retain `Meaning` as resolution evidence. | Stop before Data Loader handoff on no match, multiple matches, or conflicting supplied code and Meaning. |
| resolve_inventory_attribute_status | After Source Type resolution and before Data Loader handoff | Supplied Status Meaning and/or `Status` | GET `/fscmRestApi/resources/11.13.18.05/genericLookupsLOV` with `q=LookupType='ORA_INV_ATTR_STATUS'` and `onlyData=true` | `LookupCode`, `Meaning` | Retrieve the scoped rows. Match Meaning and directly supplied LookupCode using trim plus case-insensitive exact comparison. With both supplied, require both to identify the same single row. Do not fuzzy-match or select the first row. | `Status` from `LookupCode`; retain `Meaning` as resolution evidence. | Stop before Data Loader handoff on no match, multiple matches, or conflicting supplied code and Meaning. |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Applicability Level is omitted | Do not run this resolver; preserve the blank for Data Loader and Fusion to evaluate. |
| Applicability Level Meaning is supplied | Resolve it through the declared read-only resource and fill `ApplicabilityCode` from `LookupCode`. |
| ApplicabilityCode is supplied | Validate it through the same resolver before Data Loader handoff. |
| Both representations are supplied | Resolve both and require the same single returned row. |
| Source Type is omitted | Do not run this resolver; preserve the blank for Data Loader and Fusion to evaluate. |
| Source Type Meaning is supplied | Resolve it through the declared read-only resource and fill `SourceType` from `LookupCode`. |
| SourceType is supplied | Validate it through the same resolver before Data Loader handoff. |
| Both Source Type representations are supplied | Resolve both and require the same single returned row. |
| Status is omitted | Do not run this resolver; preserve the blank for Data Loader and Fusion to evaluate. |
| Status Meaning is supplied | Resolve it through the declared read-only resource and fill `Status` from `LookupCode`. |
| Status is supplied | Validate it through the same resolver before Data Loader handoff. |
| Both Status representations are supplied | Resolve both and require the same single returned row. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| IAC.RESOLVE_APPLICABILITY_LEVEL | decision | 20 | reference_lookup | resolved->IAC.RESOLVE_SOURCE_TYPE;skipped->IAC.RESOLVE_SOURCE_TYPE;blocked->IAC.HANDLE_ERROR | IAC.NORMALIZE_CONTROLS | stop | An Applicability Level Meaning and/or ApplicabilityCode is supplied. |
| IAC.RESOLVE_SOURCE_TYPE | decision | 25 | reference_lookup | resolved->IAC.RESOLVE_STATUS;skipped->IAC.RESOLVE_STATUS;blocked->IAC.HANDLE_ERROR | IAC.RESOLVE_APPLICABILITY_LEVEL | stop | A Source Type Meaning and/or SourceType is supplied. |
| IAC.RESOLVE_STATUS | decision | 27 | reference_lookup | resolved->IAC.DATA_LOADER_HANDOFF;skipped->IAC.DATA_LOADER_HANDOFF;blocked->IAC.HANDLE_ERROR | IAC.RESOLVE_SOURCE_TYPE | stop | A Status Meaning and/or Status is supplied. |
