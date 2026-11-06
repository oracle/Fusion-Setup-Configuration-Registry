# Default Classification Group Defaulting Rules

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| ClassCriterias.CriteriaEntity | 1 | Creating a classification criterion and CriteriaEntity is blank | No | resolve_criteria_entity |
| ClassCriterias.CriteriaOperator | 1 | Creating a classification criterion and CriteriaOperator is blank | No |  |

The Redwood page supplies these defaults before its classification-criterion
create transformation.

## Condition Normalization

| Supplied Condition | CriteriaOperator | Cardinality |
|---|---|---|
| Starts with | 1 | One literal CriteriaValue |
| Among | 4 | One or more distinct literal CriteriaValues |

The Fusion `ORA_MSC_ROP_CRITERIA_CONDITION` lookup identifies `Starts with`
as operator 1. The page's load chain identifies operator 4 as `Among`.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DCG.APPLY_UI_DEFAULTS | step | 20 | apply_default | defaulted->DCG.RESOLVE_CRITERIA_ENTITY;not_required->DCG.RESOLVE_CRITERIA_ENTITY;blocked->DCG.HANDLE_ERROR | DCG.VALIDATE_INPUT | stop | Before resolving classification criteria and Data Loader handoff |
