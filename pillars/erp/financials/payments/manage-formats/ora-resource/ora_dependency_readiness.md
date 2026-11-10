# Manage Formats dependencies

Source-backed static guidance; live qualification remains separate.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Format type and template route | Establish exact type, direction and report/upload mechanism |
| 2 | Optional references and children | Verify only the references required by the requested fields |
| 3 | Template attachment | Track as separate manual action; metadata success does not satisfy runtime readiness |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| FMT-DEP-TYPE | Target format type | Yes | All requests | Blocked | Target task UI/export evidence |  | Exact target code and applicable route needed | Supply exact verified type; do not create a type through Manage Formats | FormatTypeCode |
| FMT-DEP-TEMPLATE | Selected or uploaded template | Conditional | Template-required format | Blocked | Target BI Publisher report/layout or manual upload evidence |  | Binary installation is outside CSV | Select exact report template or perform the manual XML upload; no dummy template | FormatTemplateCode and separate attachment evidence |
| FMT-DEP-CHILD | Validation/translation context | Conditional | Child rows requested | Blocked | Exact target set/parameter/language and parent evidence |  | Generic migration rows do not imply UI auto-defaults | Provide verified context and explicit child values | Exact child parent/key context |
| FMT-DEP-DFF | Deployed flexfield metadata | Conditional | DFF change requested | Blocked | Current deployed IBY_FORMATS context/segment metadata |  | Source sample contexts are not target configuration | Refresh context, segment, value set before changing DFF | Requested DFF values |

Blocked above means missing applicable evidence for the current candidate; evidence can satisfy the dependency. Optional unused fields do not block an unrelated request. Partial target verification never removes task-level create/update support.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FMT-DEPENDENCIES | step | 30 | resolve_dependency | pass->FMT-DEFAULTS;missing->FMT-MISSING | FMT-REFERENCES | stop | Evaluate only applicable dependencies against current candidate evidence |


## Validation assignment package dependencies

A validation parameter create/update package must contain its exact assignment
parent and owning format/payment-method parent. The runtime carries required
existing ancestors from the fresh baseline, preserving business values and
blanking import audit fields. These dependencies are not additional requested
business changes. Explicit parent operations take precedence. Missing or
ambiguous parents, changed dependency content and unrelated rows fail validation.
For Payment Methods, existing parent identity and import-side-effect checks also
apply to included dependencies. Verify the requested parameter and preservation
of all other business values through a fresh export after import.
