# Default Classification Group Input Validation

## Source Evidence

| Source | Used For |
|---|---|
| Fusion Data Loader live metadata for Classification Groups in SILVER_UNLOCKED | Confirms the minMaxGroups root and its GroupClassifications, ClassCriterias, and CriteriaValues sections |
| Redwood source: default-classification-page.json, default-classification-page.js, and GroupClassifications layout.json | Confirms the rendered controls, UI defaults, LOV attributes, and create transformation |
| Redwood source: default-classification-page-chains/loadMinMaxGroupsGroupClassificationsChain.js and saveMinMaxGroupsGroupClassificationsChain.js | Confirms the edit route and operator-specific cardinality |

## Scope Boundary

| Boundary | What Happens |
|---|---|
| Local validation ownership | Validate the documented group and classification input representations, apply the sourced UI defaults, and resolve approved friendly lookup inputs before Data Loader handoff |
| Backend-owned validation | Data Loader and Fusion own required fields, keys, uniqueness, lengths, server-side domains, optimistic-lock fields, and all unsupported input checks |
| Execution route | core.data-loader owns immutable preview, approval, metadata preflight, and all Fusion writes for Classification Groups |
| Parent context | For a group-header update or a child operation, require the existing GroupCode and current catalog identity. Validate that they identify one group, but retain the user-key values in the Data Loader source so the registered business object resolves surrogate identifiers and REST addresses. |
| Supported operations | Normalize `minMaxGroups` updates and create, update, and delete requests for GroupClassifications, ClassCriterias, and CriteriaValues. |

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Existing parent context | Current CatalogId, CatalogCode, or CatalogName; GroupCode | Stop before Data Loader handoff | Provide the existing group's code and one current catalog identity | Creating, updating, or deleting a child row | resolve_existing_group |
| Group catalog update | Existing GroupCode and current catalog identity; target CatalogId, CatalogCode, or CatalogName | Stop before Data Loader handoff | Resolve both catalog inputs, then validate the existing group; retain the current identity for the group key and use the target CatalogId in the patch | Updating `minMaxGroups.CatalogId` | resolve_item_catalog |
| Classification identity | ClassificationName | Stop before Data Loader handoff | Provide ClassificationName | Creating, updating, or deleting a GroupClassifications row or one of its descendants |  |
| Child operation | Operation | Stop before Data Loader handoff | Use create, update, or delete and provide the BO-declared key fields required by that operation | Any child row is supplied |  |
| Criterion value | CriteriaValue | Stop before Data Loader handoff | Provide a nonblank literal value | Creating or updating a ClassCriterias row that has a criterion value |  |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| More than one current catalog representation is supplied | Continue only when all supplied values resolve to the same catalog | Preserve the canonical catalog ID, code, and name as evidence and retain the BO user-key representation in the source | resolve_item_catalog |
| CriteriaEntity code or meaning is supplied | Continue only when it resolves to one enabled effective ORA_MSC_ROP_CRITERIA_TYPE row | Fill CriteriaEntity with LookupCode and retain Meaning as evidence | resolve_criteria_entity |
| CriteriaOperator code or condition meaning is supplied | Continue only when it resolves to one enabled effective ORA_MSC_ROP_CRITERIA_CONDITION row | Fill CriteriaOperator with LookupCode and retain Meaning as evidence | resolve_criteria_condition |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Current catalog normalization | Accept CatalogId, CatalogCode, or CatalogName for the existing parent. Trim outer whitespace from code and name inputs; match codes and names case-insensitively and exactly. Do not fuzzy-match or select a first result. | Parent context is supplied for a child operation | resolve_item_catalog |
| Target catalog normalization | For a group catalog update, accept a target CatalogId, CatalogCode, or CatalogName. Resolve it exactly and send the returned CatalogId in `minMaxGroups.CatalogId`; preserve the existing `GroupCode` and `GrpCatalogName` as the source identity used to locate the group. | Updating a group catalog | resolve_item_catalog |
| Literal criterion value | Preserve the supplied CriteriaValue as text. It is not an item-category identifier or LOV value. | A criterion value is supplied |  |
| Criteria entity normalization | Accept LookupCode or Meaning for ORA_MSC_ROP_CRITERIA_TYPE. Resolve either representation through the same lookup and require both to identify the same row when both are supplied. | CriteriaEntity is supplied or defaulted | resolve_criteria_entity |
| Criteria condition normalization | Accept LookupCode or Meaning for ORA_MSC_ROP_CRITERIA_CONDITION. Resolve either representation through the same lookup and require both to identify the same row when both are supplied. | CriteriaOperator or a friendly condition is supplied or defaulted | resolve_criteria_condition |
| Child operation normalization | Prepare only the requested create, update, or delete operation for GroupClassifications, ClassCriterias, or CriteriaValues. Preserve all BO-declared user-key fields needed to locate the parent and target child. | A supported child operation is requested |  |
| Group-header operation normalization | Prepare a requested group-header update as a `minMaxGroups` PATCH. Preserve the existing group identity and map a resolved target catalog only to `CatalogId`. | A supported group-header update is requested |  |
| Classification create mapping | For a GroupClassifications create, map one supplied ClassificationName to both `ClassificationCode` and `ClassificationName`. Preserve `ClassificationDesc` when supplied. | Creating a GroupClassifications row |  |
| UI default normalization | When absent, set CriteriaEntity to 1 and CriteriaOperator to 1. Preserve explicit supported values. | Creating a classification criterion |  |
| Criteria-value cardinality | Normalize a scalar criterion value to one CriteriaValues row. For operator 4 (Among), normalize a set or array to one distinct CriteriaValues row per value. All other operators, including 1 (Starts with), use one value. | CriteriaValue is supplied |  |
| Operator change behavior | Clear a pending CriteriaValue before applying a changed CriteriaOperator. | Updating a classification criterion |  |
| Unsupported fields or friendly values | Stop before Data Loader handoff. Do not invent a value or bypass the documented resolver. | Any supplied value is outside this task contract |  |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DCG.VALIDATE_INPUT | step | 10 | validate_input | valid->DCG.APPLY_UI_DEFAULTS;invalid->DCG.HANDLE_ERROR | none | stop | Before normalizing Default Classification Group input for Data Loader |
