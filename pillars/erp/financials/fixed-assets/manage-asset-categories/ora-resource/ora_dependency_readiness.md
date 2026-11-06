# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---:|---|---|
| 1 | Asset system control | Use `resolve_category_system_control` to establish enterprise identity and obtain the exported `CatStructureInstanceCode`. |
| 2 | CAT# structure | Use `discover_category_kff_structure` to obtain a new KFF task export for this request and target environment, then resolve one enabled CAT# structure, its delimiter, displayed components, requiredness, and value-set mappings. |
| 3 | CAT# component input | Use `resolve_category_component_mapping` to map supplied category components to the selected CAT# instance. Validate that every required component has a supplied value. |
| 4 | Category component values | Verify every supplied component value exists, is enabled and effective, and has the required dependent-parent mapping in its resolved value set. |
| 5 | Existing category state | Apply Category Existence Evidence Routes: prefer metadata-grounded BOSS `assetAllSegmentsCategoriesView`, then governed complete export when BOSS evidence is insufficient. Match the exact selected structure and every component. For header work resolve create or update/preserve readiness; for book-only work require one exact existing category. |
| 6 | Asset book | Resolve the exact book before authoring category-book or default rows through `resolve_asset_book_for_category`. |
| 7 | Ledger and account chain | Resolve the selected book ledger, COA, Natural Account segment/value set, and supplied or derived account vectors under Category-Book Account Preparation before populating an account role; do not verify full-combination existence. |
| 8 | Book fiscal-year calendar start | Use `resolve_book_fiscal_year_start` to obtain the selected book fiscal-year calendar's earliest start date before defaulting From Date Placed in Service. |
| 9 | Depreciation setup and reference sets | Resolve the user-supplied method and conventions first. A valid Common Set definition needs no book assignment check. Only for a non-Common definition, resolve the relevant book assignment through `resolve_book_reference_object_sets`: method against Depreciation Methods, and conventions against Prorate Conventions. |
| 10 | Package-format evidence | After all dependency gates pass, use `resolve_export_package_inventory` for the current same-task package shape and optional-field representation. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| asset_system_control | Asset system control | Yes | Create, validate, or resolve an Asset Category for category-book work | Verify | Read-only AssetSystemControl BOSS row plus current same-environment `FA_MANAGE_SYSTEM_CONTROL` export | resolve_category_system_control | Asset Category resolution derives its structure from System Controls. | Configure System Controls first, then provide current System Controls export evidence when required. | `CatStructureInstanceCode` and contract-required identity |
| category_kff_structure | CAT# structure | Yes | Create, validate, or resolve an Asset Category for category-book work | Verify | Current `FA_MANAGE_FIXED_ASSETS_KEY_FLEXFIELDS` KFF export and selected `CatStructureInstanceCode` | discover_category_kff_structure | The selected System Controls instance determines the deployed CAT# structure. | Resolve one enabled CAT# instance and its current metadata before mapping input values. | Delimiter, displayed components, requiredness, and value sets |
| category_component_mapping | CAT# component mapping | Yes | Create, validate, or resolve an Asset Category for category-book work | Verify | Selected CAT# structure and supplied category components | resolve_category_component_mapping | Category resolution must use the selected instance's component mapping. | Map all supplied components before value-set validation. | Normalized components and mapped value-set/value pairs |
| category_component_values | CAT# component values | Yes | Create, validate, or resolve an Asset Category for category-book work | Verify | Current value-set checks with verified filters, pagination, and visibility | resolve_category_component_values | Every supplied component must be a valid current member of its mapped value set. | Create or enable an exact missing value through Manage Fixed Assets Flexfield Value Sets, then re-verify it. | `ValueSetCode`, value, enabled/effective state, and dependent parent value when applicable |
| existing_category_state | Existing category state | Yes | Create, update, validate, or resolve an Asset Category for category-book work | Verify | Complete across-structure candidate evidence plus selected-structure identity/material comparison through the preferred BOSS `assetAllSegmentsCategoriesView` route or the governed current category-export fallback in Category Existence Evidence Routes; complete standard REST evidence may supplement either route | resolve_existing_asset_category | Category-header create readiness requires no exact component collision in any structure under the conservative workflow policy; category-book work needs one exact existing category. | For category-header work, distinguish selected-structure absence with cross-structure collision clearance, exact material match, one exact material difference, cross-structure create-policy hold, ambiguity, and lookup failure. Show the delta and require an explicit update-existing or preserve/create-new decision only for one exact material difference. For category-book work, resolve one exact existing category before authoring its row. | Existing identity; exact material comparison; create readiness; explicit update-or-preserve decision requirement; ambiguity/failure blocker; or exact category-book assignment identity |
| asset_book | Asset book | Conditional | Category-book or default-rule work | Verify | Exact active target book | resolve_asset_book_for_category | Category-book rows require one selected active book. | Select one exact active code; never auto-select a nearest candidate. | `BookTypeCode`, class, calendar, ledger, and currency |
| ledger_account_chain | Ledger and account chain | Conditional | Category-book account work | Verify | Selected book, ledger, COA metadata, supplied account segments, and Natural Account/skeleton evidence when deriving | resolve_category_book_accounts | Resolve complete account input or derivation without requiring a pre-existing full combination. | Follow Category-Book Account Preparation in ora_reference_lookups.md. Ask only for unresolved required input, Natural Account, skeleton, or format. | Per-role segment vector, source, and format evidence; no CCID/existence validation |
| impairment_accounts | Impairment-account dependency | Conditional | Selected book enables impairment | Verify | Exact selected-book `AllowImpairmentFlag` evidence | resolve_category_book_accounts | Both impairment roles are required when impairment is enabled. | Resolve both exact ledger-valid impairment accounts. | Impairment Expense and Impairment Reserve combinations |
| book_fiscal_year_start | Book fiscal-year calendar start | Conditional | Defaulting Start DPIS | Verify | Selected book fiscal-year date evidence | resolve_book_fiscal_year_start | Defaults must use the selected book's earliest fiscal-year start. | Resolve the selected book fiscal year and calendar start. | Fiscal year and earliest valid start date |
| depreciation_setup | Depreciation setup and reference sets | Conditional | Category-book default-rule work | Verify | Active compatible methods/conventions and required non-Common book assignments | resolve_category_book_defaults | Default rules require compatible target setup. | Supply valid method and conventions; resolve non-Common reference-set assignments. | Method, life, conventions, fiscal year, and reference-set evidence |
| package_format | Package-format evidence | Yes | Package generation | Verify | Current same-target task export with complete members and headers | resolve_export_package_inventory | Package rows must match the target contract. | Obtain a current complete task export before package generation. | Members, headers, row shape, and duplicate-key report |

## Value-Set Handoff

If `resolve_category_component_values` identifies a missing, disabled, expired,
or parent-unmapped component, stop category authoring. Retain the normalized
component, its supplied or defaulted `ComponentNDescription`, target environment,
and parent-request fingerprint. Ask whether to create or enable the exact value
through Manage Fixed Assets Flexfield Value Sets, then resume only after that
prerequisite completes and fresh target verification passes. Do not discard an
explicit `ComponentNDescription` or use it as a category package field.

## Ownership Boundary

This file owns prerequisite availability and stop conditions. Input shape and
field validation belong to `ora_input_validation.md`; lookup mechanics belong
to `ora_reference_lookups.md`; defaults belong to `ora_defaulting_rules.md`; and
package uniqueness and design safeguards belong to `ora_design_enforcement.md`.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| MAC.CHECK_DEPENDENCIES | decision | 20 | resolve_dependency | ready->MAC.RESOLVE_REFERENCES;blocked->MAC.HANDLE_DEPENDENCY | MAC.VALIDATE_INPUT | stop | Valid input before package authoring. |
