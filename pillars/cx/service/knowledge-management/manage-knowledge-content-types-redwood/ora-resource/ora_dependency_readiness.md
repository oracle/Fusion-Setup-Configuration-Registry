# Content Type Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Department | Select the content type department before configuring attribute visibility. |
| 2 | Department user groups | Resolve the user groups available for the selected department before restricting field visibility. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| content_type_department | Department | Yes | Create or update a content type | Required | User-provided content type definition | | The department determines the relevant products, categories, and users. | Select a department. | Department |
| attribute_visibility_groups | Department user groups | Conditional | Restricting a schema attribute's visibility | Lookup | Knowledge User Groups REST API | resolve_department_user_groups | Only user groups mapped to the selected department are available for visibility. | Select the department, then resolve the available user groups before setting visibility. | Available user groups |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Required | A department has not been provided | No |
| Lookup | Attribute visibility is restricted | Yes; read-only department user-group lookup |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CONTENT_TYPES_REDWOOD.DEPENDENCIES | step | 8 | resolve_dependency | satisfied->CONTENT_TYPES_REDWOOD.VISIBILITY_REQUIRED;blocked->CONTENT_TYPES_REDWOOD.BLOCKED | CONTENT_TYPES_REDWOOD.DEFAULT_LOCALE_LOOKUP | stop | Check Dependency Rules using the supplied department and resolved locale evidence. Do not infer a department-to-stripe mapping or create a missing reference object. |
| CONTENT_TYPES_REDWOOD.VISIBILITY_REQUIRED | decision | 9 | resolve_dependency | required->CONTENT_TYPES_REDWOOD.VISIBILITY_LOOKUP;not_required->CONTENT_TYPES_REDWOOD.DEFAULTS;blocked->CONTENT_TYPES_REDWOOD.BLOCKED | CONTENT_TYPES_REDWOOD.DEPENDENCIES | stop | Restricted attribute visibility requires the declared department user-group lookup. Unrestricted visibility needs no group GET; record the dependency not applicable and use the separate not_required transition. |
