# Intrastat Rules Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Registered business object | Confirm `intrastatRules` metadata is the active Data Loader contract. |
| 2 | Intrastat Catalog | Resolve the parent catalog name to `CategorySetId` before preparing a supplementary-UOM child with `CategoryCodeName`. |
| 3 | Rule type | Resolve a supplied friendly rule-type meaning before preparing the parent row. |
| 4 | Attribute-validation source type | Resolve a supplied source-transaction meaning before preparing the affected attribute-validation row. |
| 5 | Attribute-validation attribute | Resolve a supplied required-attribute meaning before preparing the affected attribute-validation row. |
| 6 | Fiscal-regime source type | Resolve a supplied source-transaction meaning before preparing the affected fiscal-regime row. |
| 7 | Fiscal-regime trading-partner type | Resolve a supplied trading-partner-type meaning before preparing the affected fiscal-regime row. |
| 8 | Freight terms | Resolve a supplied friendly freight-terms value before preparing the affected statistical-value row. |
| 9 | Mode of transport | Resolve a supplied friendly transport-mode meaning before preparing the affected statistical-value row. |
| 10 | Rounding rule | Resolve a supplied friendly rounding-rule meaning before preparing the affected supplementary-UOM row. |
| 11 | Parent rule set | Prepare a parent row with `RuleSetCode` before preparing child rows that reference it. |
| 12 | Child records | Use only the seven registered child collections for the requested rule types. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| intrastat_rules_bo | Registered `intrastatRules` business object | Yes | Every request | Verify | User-provided registration and Data Loader metadata | | The BO is the governed execution contract. | Do not substitute a direct REST payload or an unregistered object. | BO name; metadata version |
| intrastat_catalog | Parent `CategorySetName` resolved as Intrastat Catalog | Conditional | A `supplementaryUOMRules` child supplies `CategoryCodeName` | Resolve | Verified `intrastatCatalogs` lookup | resolve_intrastat_catalog | The catalog's `CategorySetId` scopes the supplementary-UOM category. | Provide the parent catalog name; use the resolved ID in the parent and affected child. | CategorySetId |
| parent_rule_set | Parent `RuleSetCode` | Yes | Any child record is supplied | Verify | Parent source row | | All registered child records include `RuleSetCode`. | Provide the matching parent rule set in the same source or identify the existing authoritative parent. | RuleSetCode |
| child_collection | Supported child collection | Conditional | A child row is supplied | Verify | Registered BO metadata | | Only source-confirmed child accessors are supported. | Use the exact published child record name, including `exlusionRules`. | Child record name |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | The registered BO, parent rule set, and requested child collection are identified. | Yes |
| Blocked | BO metadata, the parent rule set, or the requested child collection is missing or inconsistent. | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| INTRASTAT_RULES.CHECK_READINESS | decision | 110 | resolve_dependency | ready->INTRASTAT_RULES.PREPARE_LOADER;blocked->RETURN_ISSUES | INTRASTAT_RULES.RESOLVE_ROUNDING_RULE | stop | Before preparing a Data Loader source or preview. |
