# Input Validation

## Required Client Inputs

Validate only the business values required by the requested category scope.
This file owns required-input, format, enum, and cross-field checks. Apply a
default only through `ora_defaulting_rules.md`; resolve a target value only
through `ora_reference_lookups.md`; and enforce package/design safeguards only
through `ora_design_enforcement.md`.

| Input | Required When | Validation |
|---|---|---|
| Category component values | Every create, update, or existence check | Require a nonblank category component for every required mapped CAT# KFF segment. Normalize supplied component values to uppercase. When one concatenated category value is supplied, parse it only with the resolved CAT# delimiter; reject any other supplied separator before component or value-set validation. Build the category combination internally using the resolved delimiter; never ask the customer to provide or correct a delimiter. |
| Category component description | A labelled `ComponentN` value is supplied | A supplied `ComponentNDescription` is the requested description for the corresponding ordered category-component value-set value. When that value is confirmed absent and `ComponentNDescription` is blank, default it to the human-readable sentence-case form of `ComponentN`. |
| Category Type and Ownership | Creating or changing a category | Require a nonblank user value or the resulting defaulted/derived value. When blank, defaulting derives both from whether a category component contains the word `lease`. |
| Capitalized, Enabled, and Summary Category | Creating or changing a category | Require a nonblank user value or the resulting defaulted value: `YES`, `Y`, and `N`, respectively. |
| Structure Instance | Every create, update, or existence check | Derive only from System Controls `CatStructureInstanceCode` and its exact matching enabled CAT# export instance. It is not a customer input. |
| Category header values in scope | Creating or changing category details | Require each field that the approved scope marks mandatory. Validate only target-supported stored values; do not prompt for optional fields that are outside scope. |
| Category identity for category-book work | Assigning, changing, removing, or preserving a category-book row | Treat the supplied category combination as the existing-category identifier. First resolve the target CAT# structure, then parse a supplied concatenated category with its resolved delimiter and locate one exact existing category. Do not request category-header fields or labelled components before this resolution. |
| Asset book and assignment action | Assigning, changing, removing, or preserving a category-book row | Require one exact asset book and one category-book assignment action: create, update, remove, or preserve. This action never means create or update the category header. |
| Account overrides | A customer requests a category-book account override | Preserve complete supplied segments under Category-Book Account Preparation in ora_reference_lookups.md. Require COA format and serialization, not a pre-existing full combination. |
| Default-rule inputs | Creating or changing a category-book default row | Require a nonblank From Date Placed in Service, Depreciate Flag, and Use Straight-Line Retirements after defaulting. Require user input for Depreciation Method, Prorate Convention, and Retirement Convention. |
| Translation | A translated description is supplied | Require translated text and validate its language/source-language fields. |

## Combination and Value Validation

| Check | Required behavior |
|---|---|
| CAT# structure | Accept category component values only after `resolve_category_flexfield_structure` provides the System Controls-selected enabled CAT# structure, delimiter, and ordered KFF segment metadata. |
| Component mapping | Map supplied category components to that structure's KFF segments through `resolve_category_component_mapping`. Do not ask the customer for technical KFF identifiers or package positions. |
| Component count and delimiter | Require one value for every required mapped KFF segment in exported order. For a concatenated category value, accept only the exact delimiter returned by the selected CAT# structure and reject a different separator before splitting. The workflow assembles and validates the combination with the resolved delimiter; it must not ask the customer to supply, choose, or correct that delimiter. |
| Component values | Require every mapped category component to resolve uniquely, be enabled and effective, and satisfy any dependent-parent mapping through `resolve_category_component_values`. |
| Component description | Retain each supplied `ComponentNDescription` with the parent request. Use it only through the resolved Flexfield Value Sets prerequisite route when its corresponding category component is confirmed absent; it is not a Manage Asset Categories package field. |
| Existing category state | For category-header work, use `resolve_existing_asset_category` to distinguish create readiness with cross-structure collision clearance, a held cross-structure collision, an exact existing match, and an update-or-preserve decision. A remaining-only retry must retain explicit included/held scope and fresh target reconciliation. For category-book work, require one exact existing category; no match or multiple matches blocks the assignment. |
| Customer-facing labels | Use labels returned by the CAT# lookup. Do not assume labels such as Major or Minor. |

## Field Validation

| Business field or group | Required When | Validation |
|---|---|---|
| Summary Category, Enabled, Ownership, Category Type, and Capitalized | Creating or changing a category | Require every resulting value. Validate the supplied, derived, or defaulted stored value against the target-supported enum. |
| Description | Creating a category header or changing its description | Require description only for a category-header create when the approved scope includes it; do not use it as identity and never request it for category-book-only work. |
| Active dates | Dates are supplied or defaulted | Require Active From on or after the earliest date allowed by current System Controls. Block missing minimum-date evidence or an earlier date. Validate date format and that Active To does not precede Active From; do not silently change a supplied date. |
| Property Type, Property Class, In Physical Inventory, and Intangible | The field is supplied or its owning defaulting rule applies | Validate the resulting stored value. Do not define the default in this file. |
| Category descriptive flexfields | A context or segment is supplied | Validate the supplied context and segments only. |
| Category parent row | A category-book or default-rule row is authored | Require its matching `FA_ASSET_CATEGORY` parent row in the same candidate ZIP. For a new category, the parent must be a header create row using the resolved category combination and validated header values. For an existing category, use only the parent identity/action representation proven by the current target export; do not turn a book-only request into a header create. |
| Category-book accounts | Creating or changing a book assignment | Preserve complete supplied accounts; derive missing/incomplete accounts from the selected-book ledger, COA, skeleton and Natural Account values. Apply Category-Book Account Preparation without full-combination search or existence verification. Ask only for unresolved input or derivation. |
| Category-book account serialization | A candidate ZIP contains a populated category-book account field | Apply Category-Book Account Format in ora_reference_lookups.md to each supplied or derived vector: preserve segment values/order, leading zeros, all 30 positions, CSV_END, and multiline CSV quoting. |
| Default depreciation expense combination (`DefaultExpenseCcidFlag`) | The customer supplies this UI value | Accept Yes or No only. Convert Yes to stored `Y` and No to stored `N` before package serialization. Reject `YES`, `NO`, selected, cleared, blank text, and every value longer than one character. |
| Bonus depreciation accounts | Bonus Depreciation Expense or Bonus Depreciation Reserve is blank | Copy the resolved Depreciation Expense or Depreciation Reserve vector respectively. Apply format and serialization checks without full-combination existence verification. |
| CIP and unplanned-depreciation accounts | CIP Cost, CIP Clearing, or Unplanned Depreciation Expense is populated or required | Require a unique valid combination derived from the selected book ledger; do not copy another category-book mapping. |
| Impairment Expense and Impairment Reserve | The assigned asset book has `AllowImpairmentFlag` enabled | Require both complete, ledger-valid account combinations in the category-book mapping. Do not create, update, or preserve an incomplete mapping. |
| Revaluation accounts | The assigned asset book enables revaluation | Require complete, ledger-valid Revaluation Reserve Amortization, Revaluation Reserve, and Revaluation Loss Expense combinations when the corresponding roles are required. |
| Lease accounts | Category Type is `LEASE` | Require complete, ledger-valid Lease Liability, Lease Expense, and Lease Exchange-Rate Gain/Loss combinations when the corresponding roles are required. |
| From and To Date Placed in Service | A default row is authored | Require a nonblank From Date Placed in Service after defaulting, an effective date range without overlap, and selected-book fiscal-year/calendar coverage through `resolve_category_book_defaults`. To Date Placed in Service remains optional. |
| Depreciate Flag (`DepreciateFlag`, also called DepreciationFlag) | A default row is authored | Require the supplied or defaulted value and validate the target-supported enum. Defaulting uses `NO` only when blank. |
| Use Straight-Line Retirements (`UseStlRetirementsFlag`) | A default row is authored | Require the supplied or defaulted value and validate the target-supported `YES`/`NO` enum. Defaulting uses `NO` only when blank. |
| Depreciation Method | A default row is authored | Require user input. Require one active record matching the supplied method code and resulting life in months. A Common Set record is valid independently of book assignments; only a non-Common record must equal the selected book's `FA_DEPRECIATION_METHODS` (Depreciation Methods) reference-object set. |
| Prorate Convention | A default row is authored | Require user input. Require an exact active convention whose fiscal-year/calendar equals the selected book fiscal year. A Common Set record is valid independently of book assignments; only a non-Common record must equal the selected book's `FA_PRORATE_CONVENTIONS` (Prorate Conventions) reference-object set. |
| Retirement Convention | A default row is authored | Require user input. Require an exact active convention whose fiscal-year/calendar equals the selected book fiscal year. A Common Set record is valid independently of book assignments; only a non-Common record must equal the selected book's `FA_PRORATE_CONVENTIONS` (Prorate Conventions) reference-object set. |
| Salvage percentage | Supplied | Require a decimal fraction from 0 through 1. |
| Depreciation limits, Bonus Rule, Depreciation Ceiling, Subcomponent Rules, and Group Asset Options | Supplied or required by the resolved book/method | Validate only the supplied or required values and their stated cross-field relationships. |

## Optional Inputs

Do not prompt for optional descriptive/global flexfields, account families,
method variants, thresholds, or default-rule controls that are outside the
approved scope. Validate an optional value when supplied; otherwise apply the
preservation-or-blank behavior defined in `ora_defaulting_rules.md`.

`ComponentNDescription` is not a Manage Asset Categories package field. It is
business intent for the associated ordered category-component value-set value.
Preserve it with the parent request and apply it only through the resolved
value-set prerequisite route; never discard it or treat its absence from the
category package contract as an ambiguity. When a category component is
confirmed absent from its resolved value set and has no corresponding
`ComponentNDescription`, default the description to the human-readable
sentence-case form of that component. Do not request confirmation for this
default and do not replace an explicit `ComponentNDescription`.

## Concatenated Category Input

Prefer labelled category components. A delimiter is not required from the
customer. For a concatenated category value, use only the delimiter returned by
the selected CAT# structure. Do not treat punctuation as a generic separator:
if a supplied separator differs from the resolved delimiter, reject the input
without splitting it or validating any component value.

For category-book-only work, a supplied concatenated category is sufficient
identity input. Resolve CAT# first, parse it, and find the exact existing
category before requesting any additional input. Do not reinterpret the
category-book assignment action as a category-header action.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| MAC.VALIDATE_INPUT | decision | 10 | validate_input | valid->MAC.CHECK_DEPENDENCIES;invalid->MAC.HANDLE_INPUT | none | stop | Every request before lookup, export, preview, or import. |
