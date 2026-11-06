# Defaulting Rules

## Default Sources

| Source | Defaulting use |
|---|---|
| Complete same-task FSM export | Reuse target-supported technical forms, member names, headers, date pattern, and row shape only. Never reuse a business value. |
| Fixed Assets enum references | Validate customer-selected dropdown values. Do not choose a value on the customer's behalf. |
| Oracle Financials 26C business-object docs | Use `AssetCategoryBook` for account/default-expense fields and `AssetCategoryBookDefault` for depreciation default-rule field meaning. |
| Approved client design | Required source for every category, book, account, and depreciation business choice. |
| Resolved CAT# structure and component mapping | Fill structure, delimiter, exported KFF segment order, component mapping, and unused package-position blanks only from the System Controls-selected current CAT# metadata. |
| Existing category or category-book read-back | Preserve values only for an explicitly requested update of that same target row. |
| Selected book fiscal-year calendar | Default From Date Placed in Service from the first available start date for the selected book's fiscal-year calendar. |
| Book ledger and natural-account lookups | When no complete customer account selection is supplied, derive category-book account combinations from the selected book's ledger, COA, and account skeleton through `resolve_category_book_accounts`; preserve a complete customer selection unchanged under Category-Book Account Preparation in ora_reference_lookups.md. |

For a category-header create, use customer-supplied business choices and only the explicit
defaults or derivations listed below. Category-book account proposals use
resolve_category_book_accounts; a unique ledger-derived vector with resolved Natural Account and valid COA format is accepted without a separate account-mapping or shared-account approval;
Category Active From uses System Controls; From Date Placed in Service uses the selected book's fiscal-year calendar.
Do not borrow business values or account segments from another category or donor export row.

## Standard Defaults

Each default applies only when the customer leaves the field blank and never
replaces an explicit client value. Stored values are authoritative for package
authoring; use the UI wording below in customer prompts and previews. This file
is the single owner of category and category-book default values;
`ora_input_validation.md` validates the resulting values but does not define
competing defaults.

| Field / valid name | Default Value | Possible values / source | Resolver |
|---|---|---|---|
| ComponentNDescription | Human-readable sentence-case form of the corresponding `ComponentN` value | The corresponding category component is confirmed absent from its resolved value set and its description is blank | resolve_category_component_values |
| Category structure | System Controls-selected `CatStructureInstanceCode` and its exact enabled current CAT# export match | Current System Controls and CAT# export metadata | resolve_category_flexfield_structure |
| Category combination and components | Map customer-supplied category components to KFF segments in exported order; normalize each supplied value to uppercase and blank unused package positions. The CAT# delimiter is internal metadata and is never requested from the customer. | Customer component values plus resolved CAT# structure, component mapping, and delimiter | resolve_category_component_mapping |
| Summary Category | `N` | `Y`, `N` | resolve_category_header_defaults |
| Enabled | `Y` | `Y`, `N` | resolve_category_header_defaults |
| Ownership | `LEASED` when a category component contains the word `lease`; otherwise `OWNED` | `OWNED`, `LEASED` | resolve_category_header_defaults |
| Category Type | `LEASE` (Lease) when a category component contains the word `lease`; otherwise `NON-LEASE` (NonLease) | `LEASE`, `LEASEHOLD IMPROVEMENT`, `NON-LEASE` | resolve_category_header_defaults |
| Capitalized | `YES` | `YES`, `NO` | resolve_category_header_defaults |
| Description | Require customer-supplied text only on category-header create; preserve on category-header update | Customer text or existing row | resolve_existing_asset_category |
| Active From date | Default to the earliest date allowed by System Controls; treat it as an internal, system-derived attribute. | Current target System Controls; target export date pattern | resolve_category_system_control |
| Active To date | Blank/open-ended unless supplied | Target export date pattern when populated | resolve_category_header_defaults |
| Property Type | `PERSONAL` | `PERSONAL` (Personal), `REAL` (Real) | resolve_category_header_defaults |
| Property Class | `1245` (1245 Property) | `1245` (1245 Property), `1250` (1250 Property) | resolve_category_header_defaults |
| In Physical Inventory | Blank unless supplied | Target-supported flag values | resolve_category_header_defaults |
| Intangible | Blank unless supplied | Target-supported flag values | resolve_category_header_defaults |
| Category descriptive flexfields | Blank on create; preserve on update | Supplied or preserved context-compatible values | resolve_category_header_defaults |
| Asset book | No default unless one exact book is supplied/resolved. When exact lookup fails, retrieve nearest active book candidates for user selection; do not assign one automatically. | Exact asset book or nearest active candidate result | resolve_asset_book_for_category |
| Book context | Populate only from resolved book or same-book export evidence | Selected book metadata; Book Class values include `CORPORATE`, `TAX` | resolve_asset_book_for_category |
| Book assignment removal action | Blank or `N` for category-book assignment create/update | Removal value only when customer requests removal | resolve_asset_book_for_category |
| Category-book flags | Blank/unchecked unless supplied or same-book evidence proves them | Target-supported checkbox values; commonly `Y`, `N`, or blank as exported | resolve_category_book_accounts |
| Default depreciation expense combination (`DefaultExpenseCcidFlag`) | Blank/unchecked unless supplied | UI Yes → stored `Y`; UI No → stored `N` | resolve_category_book_accounts |
| Category-book account combinations | When no complete customer selection is supplied, automatically derive every required role through the account resolver. Preserve an explicit complete customer selection under Category-Book Account Preparation in ora_reference_lookups.md without full-combination search or existence verification. | Category/book/role result from the account resolver; no generic fallback | resolve_category_book_accounts |
| Bonus Depreciation Expense | Use the resolved Depreciation Expense segment vector when no complete Bonus Depreciation Expense selection is supplied. | Resolved Depreciation Expense segment vector | resolve_category_book_accounts |
| Bonus Depreciation Reserve | Use the resolved Depreciation Reserve segment vector when no complete Bonus Depreciation Reserve selection is supplied. | Resolved Depreciation Reserve segment vector | resolve_category_book_accounts |
| CIP Cost, CIP Clearing, and Unplanned Depreciation Expense | Derive each populated or required role from the selected book ledger. | Role-specific ledger-derived complete combination | resolve_category_book_accounts |
| Impairment Expense and Impairment Reserve | No default; require resolved complete combinations. | The selected book enables `AllowImpairmentFlag`. | resolve_category_book_accounts |
| Revaluation Reserve Amortization, Revaluation Reserve, and Revaluation Loss Expense | Blank unless the selected book enables revaluation; when enabled, derive each required role from the selected book ledger. | Selected-book revaluation enablement and role-specific ledger-derived complete combination | resolve_category_book_accounts |
| Optional account combinations | Blank unless supplied or required by the selected book | Same account resolver and design gates as required accounts | resolve_category_book_accounts |
| Lease Liability, Lease Expense, and Lease Exchange-Rate Gain/Loss | Blank unless the category is lease type; when lease type applies, derive each required role from the selected book ledger. | Lease category type and role-specific ledger-derived complete combination | resolve_category_book_accounts |
| Transaction and transfer account combinations | Blank unless supplied or required by the selected book | Account resolver result for the transaction or transfer role | resolve_category_book_accounts |
| Annuity account combinations | Blank unless supplied or annuity context proves required | Account resolver result for annuity interest expense or revenue | resolve_category_book_accounts |
| Category-book descriptive/global flexfields | Blank on create; preserve on update | Supplied or preserved context-compatible values | resolve_asset_book_for_category |
| Default Rules parent identity | Derive from resolved category-book row | Resolved category and book identity | resolve_category_book_defaults |
| Default Rules: From/To Date Placed in Service | Default Start DPIS from the earliest available start date in the selected book's fiscal-year calendar; End DPIS is optional. Treat the Start DPIS as an internal, system-derived attribute, not a customer input. | Validate the selected fiscal-year calendar; use export only for date format | resolve_category_book_defaults |
| Default Rules: Depreciate Flag (`DepreciateFlag`, also called DepreciationFlag) | `NO` | `YES`, `NO` | resolve_category_book_defaults |
| Default Rules: Use Straight-Line Retirements (`UseStlRetirementsFlag`) | `NO` | `YES`, `NO` | resolve_category_book_defaults |
| Default Rules: Depreciation Method | Customer must supply. | Accept a valid Common Set method independently of book assignments; otherwise validate the supplied method against the selected book's `FA_DEPRECIATION_METHODS` (Depreciation Methods) reference-object set. | resolve_category_book_defaults |
| Default Rules: Life in Years and Life in Months | Required when the resolved UI marks them required; ask the customer when missing. | Validate the supplied life | resolve_category_book_defaults |
| Default Rules: Prorate Convention | Customer must supply. | Accept a valid Common Set convention independently of book assignments; otherwise validate the supplied convention against the selected book's `FA_PRORATE_CONVENTIONS` (Prorate Conventions) reference-object set. | resolve_category_book_defaults |
| Default Rules: Retirement Convention | Customer must supply. | Accept a valid Common Set convention independently of book assignments; otherwise validate the supplied convention against the selected book's `FA_PRORATE_CONVENTIONS` (Prorate Conventions) reference-object set. | resolve_category_book_defaults |
| Remaining default-rule controls | Leave blank unless the customer supplies them. | Validate populated values only | resolve_category_book_defaults |
| Subcomponent life defaults | Customer must supply or explicitly leave blank | `SAME END DATE`, `SAME LIFE`; numeric life values | resolve_category_book_defaults |
| Group asset options | Customer must supply or explicitly leave blank | Target-supported group, allocation, and tracking values | resolve_category_book_defaults |
| Production defaults | Customer must supply or explicitly leave blank | Target setup values and numeric/date-compatible values | resolve_category_book_defaults |
| Low-value asset defaults | Customer must supply or explicitly leave blank | Target low-value-asset method, rate, convention, life, and set values | resolve_category_book_defaults |
| Annuity defaults | Customer must supply or explicitly leave blank | Target annuity setup values and numeric values | resolve_category_book_defaults |
| Default-rule descriptive flexfields | Blank on create; preserve on update | Supplied or preserved context-compatible values | resolve_category_book_defaults |
| Translation | Author only when supplied or preserving update | Resolved language/source language from existing target/session | resolve_existing_asset_category |
| Audit values | Leave blank on create | System-managed values only | resolve_existing_asset_category |

## User-Facing Category Header Values

Use the UI wording in customer prompts and previews. Retain the paired stored
value in package evidence and serialization; never substitute a UI label into a
stored-value field.

| Field | UI wording | Stored value |
|---|---|---|
| Category Type | Lease | `LEASE` |
| Category Type | Leasehold Improvement | `LEASEHOLD IMPROVEMENT` |
| Category Type | Nonlease | `NON-LEASE` |
| Ownership | Leased | `LEASED` |
| Ownership | Owned | `OWNED` |
| Capitalized | Yes | `YES` |
| Capitalized | No | `NO` |
| Enabled | Yes | `Y` |
| Enabled | No | `N` |

Capitalized and Enabled are checkboxes in the UI. Present their state as Yes or
No, never as selected/cleared or as their stored values alone.

## User-Facing Category-Book Values

| UI label | UI value | Stored value |
|---|---|---|
| Default depreciation expense combination | Yes | `Y` |
| Default depreciation expense combination | No | `N` |

## Default Safety Rules

| Situation | What Happens |
|---|---|
| A required business value is absent and no approved source proves it | Do not guess and do not create a ZIP/import. Ask the customer for that exact value. Leave a blank only when the target export/metadata proves the field is optional. |
| A client supplies a business value | Preserve it. A default may fill only a blank field unless the client explicitly approves a correction. |
| A category value is missing, disabled, ambiguous, expired, or parent-unmapped | Pause category package work and ask whether to create or enable the exact value through Manage Fixed Assets Flexfield Value Sets first. |
| A required customer value is absent or conflicting | Stop before package generation and ask the customer for the exact value. |
| A mandatory header/default-rule value remains blank after defaulting | Stop before package generation and identify the exact missing field within the requested scope. Category-header creation or changes require Category Combination, Category Type, Ownership, Capitalized, Enabled, and Summary Category after applicable defaults or preservation. Category-book work requires Asset Book. Creating or changing a default-rule row additionally requires From Date Placed in Service, Depreciate Flag, Use Straight-Line Retirements, Depreciation Method, Prorate Convention, and Retirement Convention. Do not require book or default-rule fields for category-header-only work, or header changes for category-book-only work. |
| A default-rule reference-set check fails | Do not substitute a convention or method. Stop until the supplied value resolves to the required book-level or Common Set reference set. |
| Selected book fiscal-year calendar has no available start date | Stop before package generation. Resolve the book fiscal-year/calendar setup first. |
| An account role is absent from the request | Run resolve_category_book_accounts before asking the customer; the absence alone does not block package preparation. |
| An account role remains unresolved after derivation | Apply the account gates in ora_design_enforcement.md and the Account Review Disclosure in ora_error_handling.md; ask only when no unique valid ledger-derived combination resolves, and never fill the unresolved role. |
| The staged package repeats a category, category-book, default-rule, or translation business key | Keep one intended row only. If duplicates differ, stop and ask which row is authoritative. |
| A blank is intentional | Serialize a true empty field, never whitespace, `null`, `None`, or escaped control text. |
| A proposed default changes after preview | Invalidate approval and regenerate preview/readiness evidence. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| MAC.APPLY_DEFAULTS | step | 40 | apply_default | applied->MAC.ENFORCE_DESIGN | MAC.RESOLVE_REFERENCES | stop | Lookup resolved and defaultable fields are blank. |
