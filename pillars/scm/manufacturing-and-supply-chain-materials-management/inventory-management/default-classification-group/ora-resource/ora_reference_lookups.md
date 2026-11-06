# Default Classification Group Reference Lookups

## Source Evidence

| Source | Used For |
|---|---|
| Redwood source: default-classification-page.json and default-classification-page.js | Confirms catalog display and key attributes, criteria-type display/value mapping, and literal CriteriaValue transformation |
| Fusion REST lookup verification in SILVER_UNLOCKED | Confirms itemCatalogs, minMaxGroups, ORA_MSC_ROP_CRITERIA_TYPE, and ORA_MSC_ROP_CRITERIA_CONDITION collection paths and requested attributes |
| Fusion Data Loader live metadata for Classification Groups in SILVER_UNLOCKED | Confirms the target minMaxGroups hierarchy used by the resolved values |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_item_catalog | A current parent or target CatalogId, CatalogCode, CatalogName, or combination is supplied | CatalogId, CatalogCode, CatalogName | /fscmRestApi/resources/11.13.18.05/itemCatalogs?onlyData=true&fields=CatalogId,CatalogCode,CatalogName&limit=500&offset=0&totalResults=true | CatalogId, CatalogCode, CatalogName, count, hasMore, limit, offset, totalResults | Retrieve every page through core.fusion-api.rest-api-client. Match CatalogId exactly; match trimmed CatalogCode and CatalogName case-insensitively and exactly. When multiple forms are supplied, require one returned row to satisfy all forms. | For existing parent context, retain canonical values as evidence and preserve the BO user-key representation. For a group catalog update, retain the existing identity and map the target result to `minMaxGroups.CatalogId`. | Stop before Data Loader handoff on zero matches, multiple matches, conflicting forms, incomplete pagination, or an inaccessible route. |
| resolve_existing_group | A group-header update or a child create, update, or delete is requested | Current catalog identity and GroupCode | /fscmRestApi/resources/11.13.18.05/minMaxGroups?onlyData=true&fields=GroupId,CatalogId,GrpCatalogName,GroupCode | GroupId, CatalogId, GrpCatalogName, GroupCode | Match GroupCode and the current catalog identity exactly and require one row. Use the result to validate parent context. Keep GroupCode and current catalog user-key values in the Data Loader source so the registered BO performs surrogate-key resolution. | Returned GroupId, CatalogId, GrpCatalogName, and GroupCode as evidence; BO-declared parent user keys in the source | Stop before Data Loader handoff on zero or multiple matches. |
| resolve_criteria_entity | CriteriaEntity is supplied as LookupCode, Meaning, or both, including the sourced default | CriteriaEntity | /fscmRestApi/resources/11.13.18.05/standardLookups/ORA_MSC_ROP_CRITERIA_TYPE/child/lookupCodes?onlyData=true&fields=LookupCode,Meaning,EnabledFlag,StartDateActive,EndDateActive&limit=500&offset=0&totalResults=true | LookupCode, Meaning, EnabledFlag, StartDateActive, EndDateActive, count, hasMore, limit, offset, totalResults | Retrieve every page through core.fusion-api.rest-api-client. Require one enabled, currently effective row whose LookupCode or trimmed case-insensitive Meaning matches the supplied value. When both are supplied, require the same row. | ClassCriterias.CriteriaEntity: LookupCode; resolved Meaning as evidence | Stop before Data Loader handoff on zero matches, multiple matches, a disabled or ineffective row, conflicting forms, incomplete pagination, or an inaccessible route. |
| resolve_criteria_condition | CriteriaOperator or a condition meaning is supplied, including the sourced default | CriteriaOperator, condition meaning | /fscmRestApi/resources/11.13.18.05/standardLookups/ORA_MSC_ROP_CRITERIA_CONDITION/child/lookupCodes?onlyData=true&fields=LookupCode,Meaning,EnabledFlag,StartDateActive,EndDateActive&limit=500&offset=0&totalResults=true | LookupCode, Meaning, EnabledFlag, StartDateActive, EndDateActive, count, hasMore, limit, offset, totalResults | Retrieve every page through core.fusion-api.rest-api-client. Require one enabled, currently effective row whose LookupCode or trimmed case-insensitive Meaning matches the supplied value. When both are supplied, require the same row. | ClassCriterias.CriteriaOperator: LookupCode; resolved Meaning as evidence | Stop before Data Loader handoff on zero matches, multiple matches, a disabled or ineffective row, conflicting forms, incomplete pagination, or an inaccessible route. |

## Lookup Execution Rules

All resolver invocations use the declared read-only Fusion GET route through
core.fusion-api.rest-api-client. This resource supplies the task-specific
paths, pagination, fields, mappings, and exact-match rules; it does not
provide direct Fusion write guidance.

| Situation | What Happens |
|---|---|
| A display value is supplied | Resolve it through its named resolver before Data Loader handoff and retain the canonical returned value. |
| A code or identifier is supplied | Validate it through the same named resolver; do not defer a failed code to Data Loader. |
| Code and display value are both supplied | Require them to resolve to the same returned row. |
| Any lookup fails or returns an incomplete page sequence | Stop with lookup readiness. Do not select a first value, fuzzy-match, or fall back to direct REST write guidance. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DCG.RESOLVE_CRITERIA_ENTITY | decision | 30 | reference_lookup | resolved->DCG.RESOLVE_CRITERIA_CONDITION;not_required->DCG.RESOLVE_CRITERIA_CONDITION;blocked->DCG.HANDLE_ERROR;failure->DCG.HANDLE_ERROR | DCG.APPLY_UI_DEFAULTS | stop | Validate or resolve a supplied or defaulted criteria entity |
| DCG.RESOLVE_CRITERIA_CONDITION | decision | 40 | reference_lookup | resolved->DCG.RESOLVE_ITEM_CATALOG;not_required->DCG.RESOLVE_ITEM_CATALOG;blocked->DCG.HANDLE_ERROR;failure->DCG.HANDLE_ERROR | DCG.RESOLVE_CRITERIA_ENTITY | stop | Validate or resolve a supplied or defaulted criteria condition |
| DCG.RESOLVE_ITEM_CATALOG | decision | 50 | reference_lookup | resolved->DCG.RESOLVE_EXISTING_GROUP;not_required->DCG.RESOLVE_EXISTING_GROUP;blocked->DCG.HANDLE_ERROR;failure->DCG.HANDLE_ERROR | DCG.RESOLVE_CRITERIA_CONDITION | stop | Resolve or validate current and target catalog identities |
| DCG.RESOLVE_EXISTING_GROUP | decision | 55 | reference_lookup | resolved->DCG.DATA_LOADER_HANDOFF;not_required->DCG.DATA_LOADER_HANDOFF;blocked->DCG.HANDLE_ERROR;failure->DCG.HANDLE_ERROR | DCG.RESOLVE_ITEM_CATALOG | stop | Validate the existing group context for a group-header update or child operation |
