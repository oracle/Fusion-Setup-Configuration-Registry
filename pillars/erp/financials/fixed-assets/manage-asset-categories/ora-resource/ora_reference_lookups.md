# Reference Lookups

## Data Authority

Use read-only Fusion REST or verified BOSS results to fill and validate current
System Controls, category, structure, value-set, book, ledger, COA, account,
method, convention, book-level Reference Data Object set, reference-set, and
existing-state values. Do not fill those values from a donor category. Existing-category state may use
the governed complete-export fallback defined below when REST and BOSS cannot
provide the required evidence. Depreciation-method validation may also use the governed export fallback below.
Apart from these declared validation fallbacks,
use the current same-task export only for ZIP member/header shape, CSV
serialization, and compatible default-rule behavior. Use System Controls for category Active From and the selected
book fiscal-year calendar for default-rule Start DPIS. All evidence must be from the target
environment; each resolver's declared target evidence is authoritative.

The DFF definition export is an additional metadata authority. Its rows
establish current DFF requirements; they never supply category setup values
or defaults copied from another category.

## Lookup Context

Use read-only lookups and same-task export evidence before package generation. A lookup result can prove existence or readiness; it does not authorize live import. For CAT# metadata, delegate to `erp.financials.fixed-assets.manage-fixed-assets-key-flexfields` with task `FA_MANAGE_FIXED_ASSETS_KEY_FLEXFIELDS`, application `140`, and flexfield `CAT#`. That skill obtains the current KFF task export through `shared.setup-export.task-level-export`; match the System Controls-selected `CatStructureInstanceCode` to that export. **Use the target `valueSets` REST resource and its child `values` endpoint as the primary evidence for category component value existence, enabled state, effectivity, and dependent-parent mapping. A Flexfield Value Sets CSV export may support a REST-unavailable investigation, but does not replace successful REST verification.**

Treat the CAT# delimiter as internal structure metadata. Collect customer input as
ordered category component values, preserve their supplied case until the assigned
value-set metadata is verified through resolve_category_component_values, and
assemble the category combination internally from the case-validated values. Do not ask the customer to supply,
select, or correct a delimiter.

### Asset Book Nearest-Match Policy

When an exact active `BookTypeCode` lookup finds no result, retrieve active book
codes through the documented paged LOV and rank the nearest candidates. Normalize
both the requested value and candidate codes by trimming, uppercasing, and
collapsing whitespace before comparison. Rank exact normalized matches first,
then prefix/containment matches, then token similarity and edit-distance matches;
break ties by preferring the candidate with fewer edits and then lexical
`BookTypeCode` order. Return up to three candidates with the match reason, book
class, currency, and depreciation calendar. A nearest candidate is a lookup
result only: never automatically assign, map, or import it. The user must select
one exact active code before category-book authoring continues.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_category_dff_segments | After CAT# structure/input mapping, before prerequisite preparation, no-op classification, or package readiness | Immutable batch identity, target environment, requested row actions, supplied DFF values, and exact current-row preservation evidence when needed | One FA_MANAGE_FIXED_ASSETS_DESCRIPTIVE_FLEXFILEDS data export through core.fusion-api.apps-common.descriptive-flexfields; execute Category DFF Resolution | Application/DFF/context identity, enabled definitions, requiredness, physical columns, type/value-set contracts, applicability, and process evidence | Resolve each applicable row independently against the same batch definition export, including JG_FA_CATEGORY_BOOKS separately from FA_CATEGORY_BOOKS | Per-row required-field maps, validated values, conversions, and comparison evidence | Missing required input, invalid values, ambiguous scope, incomplete evidence, or unsupported validation blocks readiness |
| resolve_category_system_control | A category requires its configured structure or Active From date | Target environment; application 140; CAT#; System Controls `CatStructureInstanceCode` | Obtain current System Controls evidence through the declared shared export route. Delegate CAT# discovery to `erp.financials.fixed-assets.manage-fixed-assets-key-flexfields`. | Enterprise identity, `DatePlacedInService` when authoring Active From, exported instance code, and numeric instance number only when required by the category import or LOV contract | Require one enterprise/export match and its System Controls-selected enabled CAT# instance; require a valid minimum date when authoring Active From. | `CatStructureInstanceCode`, contract-required identity, and minimum category date when required | Missing BOSS structure fields do not block export discovery; stop on incomplete, conflicting, or ambiguous identity/export evidence. |
| discover_category_kff_structure | Current CAT# metadata is needed | Target environment; System Controls-selected `CatStructureInstanceCode`; application `140`; flexfield `CAT#` | Delegate to `erp.financials.fixed-assets.manage-fixed-assets-key-flexfields` with task `FA_MANAGE_FIXED_ASSETS_KEY_FLEXFIELDS`, application `140`, and flexfield `CAT#`. That skill obtains the current KFF task export through `shared.setup-export.task-level-export`. | Instance and structure identifiers, enabled state, delimiter, KFF segment metadata, and value-set assignments | Match `CatStructureInstanceCode` to exactly one enabled CAT# instance in the current export. | Current CAT# export evidence and the selected instance's metadata. | Missing export, incomplete evidence, or zero/multiple matching enabled instances blocks. |
| resolve_category_flexfield_structure | Before parsing category components | System Controls-selected `CatStructureInstanceCode` and `discover_category_kff_structure` evidence | Current Key Flexfields export evidence | Selected CAT# instance, delimiter, ordered KFF segment metadata, and value-set assignments | Use only the exact enabled CAT# instance matched to `CatStructureInstanceCode`. | Structure identity, delimiter, ordered KFF segment metadata, and value-set mapping. | Do not select another enabled instance or a customer-selected replacement. |
| resolve_category_component_mapping | Before component-value validation or package authoring | Supplied labelled category components or one concatenated category value, and the selected CAT# instance's exported ordered KFF segment metadata | Current Key Flexfields export evidence | Delimiter, exported segment order, label or prompt, requiredness, and `ValueSetCode` | Map every supplied category component to one KFF segment in the selected instance's exported order. For a concatenated category value, parse only with the selected CAT# delimiter and require the resulting component count. Reject any other separator; never infer or substitute a delimiter. Require one unambiguous mapping for each required component; category components are not KFF segments. | Component-to-KFF-segment mapping and the value-set assignment for each component. | Missing, ambiguous, incomplete mapping, invalid delimiter, or unresolved required inputs blocks validation and package authoring. Do not ask the customer for KFF identifiers or package positions. |
| resolve_category_component_values | After category-component mapping is complete | Mapped category components, their assigned value sets, and retained `ComponentNDescription` intent | Primary: `GET /fscmRestApi/resources/11.13.18.05/valueSets?q=ValueSetCode='{ValueSetCode}'`, then follow the returned canonical child `values` link. When the response omits links, use the code-based child path `valueSets/{URL-encoded ValueSetCode}/child/values`; never construct a numeric `ValueSetId` path. Filter `Value='{Value}'`. Fallback: use a current same-environment Flexfield Value Sets export only when REST is unavailable or incomplete, and record why. | ValueSetCode, ValueDataType, UppercaseOnlyFlag, Value, EnabledFlag, effectivity dates, dependent parent value when applicable; see [Oracle 26D value-set options](https://docs.oracle.com/en/cloud/saas/applications-common/26d/oaext/considerations-for-planning-value-sets.html) | Retrieve the exact assigned value-set definition before filtering child values. For character values, convert to uppercase only when verified UppercaseOnlyFlag is Y; when N, preserve supplied case and match the exact stored Value without case-insensitive substitution. Preserve non-character datatype representations. Resolve each dependent parent under its own value set's case rule and verify the exact child-parent mapping. Require exactly one enabled, effective match. Retain original and resolved values; use resolved values consistently for existence/collision checks, prerequisite handoff, combination assembly, and serialization. | Verified per-value-set case metadata and original/resolved component/parent values, or exact missing value-set/value pairs with retained ComponentNDescription. For each case conversion, show one row in the inline Reference Validation Preview and Design Preview with supplied value, actual value-set name/code, Uppercase only = Yes, and resolved value. Example wording: You provided 'computer'. Your value set 'FA_MAJOR_CATEGORY' allows uppercase only (Yes), so we will use 'COMPUTER'. Substitute actual values; preserve original input in Input Preview and retain existing approval gates. | Missing, unrecognized, conflicting, or ambiguous applicable case metadata blocks resolution; never infer it from another value or segment. Missing, disabled, out-of-date, or unresolved parent mapping pauses category creation. A mixed-case mismatch does not authorize substitution or member creation. For a confirmed missing component, retain its description intent and ask whether to create or enable the prerequisite through Manage Fixed Assets Flexfield Value Sets. A fallback export cannot override contradictory REST evidence. |
| resolve_existing_asset_category | Before category-header create/update preview or category-book assignment validation | Resolved CAT# structure, category-component mapping, category component values, requested material fields, and requested scope | Apply Category Existence Evidence Routes below: prefer metadata-grounded BOSS `assetAllSegmentsCategoriesView`; use a governed complete current category export when BOSS evidence is insufficient; standard REST may supplement complete evidence | BOSS `categoryId`, `structureInstanceNumber`, mapped `segment1` through `segment7`, and required material fields from verified target metadata; equivalent standard REST or export fields when that route is used | Match every exact ordered component tuple across structures for create-collision checks, then match the route-specific selected structure identity for existence and material comparison using Category Existence Evidence Routes. On standard REST, match locally against actual dynamic attributes; use a component filter only when current metadata proves it queryable. Never substitute illustrative attribute names. Compare every requested material category-header, category-book, or default-rule field with the one exact matching target record. | `absent`, `match`, `update_selected` for an explicitly selected exact material delta, `existing_different` with an unresolved exact material delta, `ambiguous`, `failure`, or exact category-book assignment identity | For category-header create, complete selected-structure absence permits create readiness only when the cross-structure collision check is also clear; a cross-structure collision returns `ambiguous` with a create-policy hold and must not be mapped to an update action. One exact material match returns `match`. One exact category with a complete material comparison returns `update_selected` only when the current request explicitly selects update for that exact category and material delta. For category-book or default-rule updates, removals, or preservation, require the exact existing assignment/default identity and explicit corresponding scope; that choice never authorizes a category-header change. Preserve unchanged state and continue through defaults, design, and all package gates. The update choice is business intent, not ZIP-creation or submission approval. Without the exact current update choice, return `existing_different`, show the field-by-field delta, and request only the unresolved update-existing or preserve/create-new decision. An absent update target, incomplete comparison, stale evidence, or cross-structure collision cannot return update_selected. Multiple exact matches or conflicting target evidence return `ambiguous`; incomplete lookup, pagination, or required-field evidence returns `failure`. For category-book work, require one exact active category match. When complete current evidence confirms that the requested assignment is absent and the explicit assignment action is create, return `absent` for that assignment scope and continue through defaults, design, and package gates while preserving the existing category header. For update, remove, or preserve, no exact assignment match blocks. Assignment absence must never be converted into a category-header creation request. |
| resolve_category_header_defaults | When category header defaults may fill blanks | Parsed category components, blank create fields, UI default evidence, and existing category state when updating | Parsed category combination plus target lookup values when available | Category type, ownership, capitalization, enabled flag, summary flag, physical inventory flag, intangible flag, property fields, active dates, DFF context | For blank Category Type and Ownership, test whether any parsed category component contains the word `lease`: set `LEASE`/`LEASED` when true, otherwise `NON-LEASE`/`OWNED`. For blank Capitalized, Enabled, and Summary Category, use `YES`, `Y`, and `N`. Updates preserve existing values. | Approved defaulted category header values | Unsupported default value, unparsed category components, or missing lookup evidence blocks preview. |
| resolve_asset_book_for_category | Before category-book assignment or default row | Exact asset book code | First `GET /fscmRestApi/resources/11.13.18.05/fixedAssetBooksLOV?q=BookTypeCode='{book_code}'&onlyData=true&totalResults=true&limit=10&offset=0`; use same-task export only for additional account/default context | `BookTypeCode`, `BookClass`, `DeprnCalendar`, `GlPostingAllowedFlag`, ledger `Name`, `CurrencyCode`, and `DateIneffective` | Exactly one row whose `BookTypeCode` equals the supplied code and whose `DateIneffective` is blank or later than the validation date | Resolved book identity and assignment readiness | If no exact active row exists, page the documented LOV fields, rank active `BookTypeCode` values after trim/case/whitespace normalization, and show at most three suggestions with book class, currency, and calendar. The user must select one exact code, which must then pass this exact lookup. Never auto-select or map a suggestion. Multiple exact rows or an ineffective selected row blocks category-book work. Do not query the LOV using an undocumented `BookName` field. |
| resolve_book_fiscal_year_start | Before defaulting category-book Start DPIS | Exact selected book and its fiscal-year name | `GET /api/boss/data/objects/ora/erpCore/fixedAssetsSetup/v1/assetFiscalYearDatesView` through `core.fusion-api.rest-api-client`, with `$limit`/`$offset` paging until `hasMore` is false; locally retain rows whose `fiscalYearName` equals the selected book fiscal-year name. | Fiscal-year name, asset fiscal year, start date, end date, and target export date pattern | Require one or more valid date ranges for the exact selected book fiscal year; choose the earliest `startDate` as the default. A customer-supplied date remains an explicit override and must belong to one of the selected fiscal-year ranges. | Package-ready Start DPIS default, fiscal-year evidence, and date format | Missing fiscal year, no date range, invalid start/end date, or ambiguous/conflicting earliest start date blocks preview. This resolver supplies book-calendar dates, not Category Active From. |
| resolve_book_ledger | Before category-book account resolution | Book ledger name or selected book's ledger context | `GET /fscmRestApi/resources/11.13.18.05/ledgersLOV?q=Name='{LedgerName}'&fields=LedgerId,Name,ChartOfAccountsId,LedgerCategoryCode,LedgerTypeCode,PeriodSetName,AccountedPeriodType,CurrencyCode&onlyData=true&totalResults=true&limit=10&offset=0` | LedgerId, Name, ChartOfAccountsId, LedgerCategoryCode, LedgerTypeCode, PeriodSetName, AccountedPeriodType, CurrencyCode | Exactly one ledger matching the selected book's ledger name or ledger identifier | Ledger and COA structure number used for account validation | Missing or multiple ledgers blocks account generation. |
| resolve_chart_of_accounts | After ledger resolves | Ledger `ChartOfAccountsId` or structure instance number | `GET /fscmRestApi/resources/11.13.18.05/chartOfAccountsLOV?q=StructureInstanceNumber={ChartOfAccountsId}&fields=Name,StructureInstanceId,StructureInstanceNumber,StructureInstanceCode,EnabledFlag&onlyData=true&totalResults=true&limit=10&offset=0` | Name, StructureInstanceId, StructureInstanceNumber, StructureInstanceCode, EnabledFlag | Exactly one enabled COA for the ledger | COA identity for `accountCombinationsLOV` polymorphic describe | Missing, disabled, or ambiguous COA blocks account generation. |
| verify_natural_account_label | After COA resolves | COA structure instance number and segment label `GL_ACCOUNT` | `GET /fscmRestApi/resources/11.13.18.05/chartOfAccountsLOV?finder=COABySegmentLabelCodeFinder;SegmentLabelCodeVar=GL_ACCOUNT&q=StructureInstanceNumber={StructureInstanceNumber}&fields=Name,StructureInstanceId,StructureInstanceNumber,StructureInstanceCode,EnabledFlag&onlyData=true&totalResults=true&limit=10&offset=0` | Name, StructureInstanceId, StructureInstanceNumber, StructureInstanceCode, EnabledFlag | The same enabled COA must be returned for `GL_ACCOUNT` | Evidence that the COA exposes a natural-account segment | No matching COA or a different COA means natural-account substitution is unsafe. |
| describe_account_combination_segments | After COA natural-account label is verified | COA structure instance number | `GET /fscmRestApi/resources/11.13.18.05/accountCombinationsLOV/describe?polymorphicType=accountCombinationsLOV:{StructureInstanceNumber}` | `FND_ACFF_Delimiter`, segment `name`, `title`, `sequence`, `valueSet`, `labels`, and `lovResource` when exposed | Identify exactly one segment whose labels include `GL_ACCOUNT`; preserve segment order and delimiter | Natural-account segment position and natural-account value set code | Missing delimiter, missing segment list, no `GL_ACCOUNT` segment, or multiple natural-account segments blocks account generation. |
| resolve_natural_account_value_set | After segment metadata identifies the natural-account value set | Natural-account value set code from COA describe | `GET /fscmRestApi/resources/11.13.18.05/valueSets?q=ValueSetCode='{ValueSetCode}'&fields=ValueSetId,ValueSetCode,ValidationType,ValueDataType,ValueSubtype,MaximumLength,UppercaseOnlyFlag,ZeroFillFlag,SecurityEnabledFlag&totalResults=true&limit=1` | ValueSetId, ValueSetCode, ValidationType, ValueDataType, ValueSubtype, MaximumLength, UppercaseOnlyFlag, ZeroFillFlag, SecurityEnabledFlag, returned child values link | Exactly one compatible natural-account value set; retain the returned child `values` link | Natural-account value set metadata and canonical child values URL | Missing value set or no child `values` link blocks account search. Do not construct a numeric child path from `ValueSetId`. |
| list_natural_account_values | When selecting role accounts | Canonical child values link from `resolve_natural_account_value_set`; resolved category components/descriptions and requested account role | Follow the returned values link, such as GET /fscmRestApi/resources/11.13.18.05/valueSets/Operations%20Account/child/values?fields=Value,Description,EnabledFlag,StartDateActive,EndDateActive,SummaryFlag,DetailPostingAllowed,DetailBudgetingAllowed,AccountType&onlyData=true&totalResults=true&limit=10&offset=0, and follow pagination | Value, Description, EnabledFlag, StartDateActive, EndDateActive, SummaryFlag, DetailPostingAllowed, DetailBudgetingAllowed, AccountType | Apply Category Account Matching below to enabled, effective, non-summary, detail-posting candidates unique by Value | Role candidates, match reason, category context, and lookup completeness | Return the per-role outcome defined below. No candidate or multiple plausible candidates prevents automatic selection; failed or incomplete reads do not prove absence. |
| resolve_category_book_accounts | When accounts tab is authored or reviewed | Selected category/book, ledger and COA metadata, selected-book account skeleton, Natural Account values, feature enablement, category type, and supplied accounts | For a complete customer account, preserve its exact segments and apply Category-Book Account Preparation below. Otherwise resolve the role from selected-ledger Natural Account values and assemble it with the selected-book skeleton. Copy resolved expense/reserve accounts to omitted bonus roles. Resolve conditional roles only when applicable. Do not search full combinations. | Required and supplied account roles | Require a unique Natural Account and usable skeleton only when deriving; complete customer selections need format/serialization checks only. Never use donor category segments. | Resolved segment vectors and customer-supplied or ledger-derived source; no CCID/existence verification | Missing required input after derivation, ambiguous Natural Account, malformed skeleton, or invalid format blocks. Absence of a pre-existing full combination does not block. |
| resolve_book_reference_object_sets | Only when an otherwise-valid selected method or convention is not in Common Set | Exact selected book and its numeric `bookControlId`; the already-resolved definition set codes | Primary: `GET /fscmRestApi/resources/11.13.18.05/setIdAssignmentsSetLOV?q=DeterminantType='AB' AND DeterminantValue='{bookControlId}'&fields=DeterminantType,DeterminantValue,ReferenceGroupName,SetId,SetCode&onlyData=true&totalResults=true&limit=100&offset=0`, paging until `hasMore` is false. Retain exactly one row for `FA_DEPRECIATION_METHODS` only when the method is non-Common, and exactly one row for `FA_PRORATE_CONVENTIONS` only when either convention is non-Common. Require `DeterminantType=AB` and the exact book-control determinant. A zero-row response or missing required group for a confirmed book-control ID is **incomplete REST evidence**: use the current same-target Manage Asset Books export member `ORA_FA_ASSIGNMENT_UPDATE.csv` for the exact `BookTypeCode`, record the fallback, and retain only the required group(s). | Determinant type/value, reference group name, set ID, and set code | The required book-level reference-object set(s) for non-Common definitions. Never resolve, compare, or require a book assignment for a Common Set definition. | Exact required book-level set IDs/codes, if any | Multiple, wrong-determinant, missing required non-Common set after fallback, or nonmatching set-ID/code blocks default-rule authoring. A missing book assignment does not block a valid Common Set definition. |
| resolve_category_book_defaults | For every new category-book assignment, or when a default-rule row is created or changed | Selected book, selected book fiscal-year name/start date, user-supplied Depreciation Method, life, Prorate Convention, Retirement Convention, and requested default fields | Resolve the exact active book and its numeric `bookControlId` from the paged BOSS `GET /api/boss/data/objects/ora/erpCore/fixedAssetsSetup/v1/assetBooksView`, then run `resolve_book_fiscal_year_start`. Existing default-rule lookup/export provides row-shape evidence. Resolve the exact method through `GET /api/boss/data/objects/ora/erpCore/fixedAssetsSetup/v1/assetDepreciationMethodsView` using target-supported request parameters. Match `methodCode`, `lifeInMonths`, `disabledFlag`, and `setIdSet.setId` to the requested method, life, and reference set; do not accept a same-code method with a different life. Apply Depreciation Method Evidence below: a BOSS response with `hasMore: true` requires the governed method export rather than further BOSS paging. Resolve each supplied prorate or retirement convention and its reference set; require its fiscal-year/calendar to equal the selected book's fiscal-year name. If every resolved definition is Common Set, accept them without running `resolve_book_reference_object_sets`. Otherwise run it and compare each non-Common method only with **Depreciation Methods**, and each non-Common convention only with **Prorate Conventions**. For conventions, use the BOSS resource's actual returned field names; retrieve its readable collection first when the documented filter field is rejected, then exact-match the supplied convention code. | From Date Placed in Service, To Date Placed in Service, Depreciate Flag, book fiscal-year start, exact method/life/reference-set record, Prorate Convention/fiscal-year/reference set, Retirement Convention/fiscal-year/reference set, and required non-Common book reference-object set IDs/codes | No date overlap; From Date Placed in Service is the selected book fiscal-year calendar's earliest start date unless customer supplied another approved date; Depreciate Flag defaults to `NO` when blank; any valid Common Set method or convention is accepted irrespective of the book assignment; each non-Common method must equal the resolved **Depreciation Methods** set and each non-Common convention must equal the resolved **Prorate Conventions** set. | Package-ready default-rule values and reference-set evidence | Missing/ambiguous book, exact method/life record, convention fiscal-year mismatch, missing book fiscal-year start, overlap, unresolved setup, a missing/exact-code-ambiguous convention result, a required non-Common assignment gap, or comparison against the wrong book reference-object set blocks preview. |
| verify_post_import | After accepted import completes | Completed process log and exact approved scope | Fresh read-back/export for Manage Asset Categories | Category, category-book, required accounts, and default-rule state | Target state exactly matches approved package scope | Verified completion evidence | Failed process log, missing read-back, or mismatch blocks success claim. |

## Lookup Execution Rules

### Structure and Value-Set Scope

Use the rules below for System Controls and KFF task exports, component mapping,
prerequisite continuation, defaults, and target-state reconciliation.

Manage Asset Categories maintains CAT# combinations, not the CAT# structure or
its value-set entries. BOSS establishes enterprise identity, and the matching
current `FA_SYSTEM_CONTROL.csv` row supplies `CatStructureInstanceCode`.
Delegate CAT# structure discovery to `manage-fixed-assets-key-flexfields`,
using `FA_MANAGE_FIXED_ASSETS_KEY_FLEXFIELDS`. Resolve the exported code to one
enabled CAT# instance in its current KFF export before mapping values.

The System Controls-selected Asset Category flexfield structure determines the
Asset Category structure context; the exported code is a lookup key, not a
numeric instance number. Preserve verified `StructureInstanceCode` for an FSM
contract and resolve a numeric instance separately only when that contract
exposes and requires it. A blank `StructureInstanceIdentifier` is valid
metadata for code-based resolution.

Component count, labels, requiredness, value sets, dependent parents, and
defaults are deployed-structure facts, rather than assumed category-component
requirements.

### Other Lookup Execution Rules

| Situation | What Happens |
|---|---|
| System control is resolved | Use the BOSS row only to establish the current system-control identity. Use the matching `FA_SYSTEM_CONTROL.csv` `CatStructureInstanceCode` as the category-structure source, then delegate to `manage-fixed-assets-key-flexfields` and verify it maps to one enabled CAT# structure in the current KFF export. |
| A concatenated category is supplied | Parse it only with the delimiter returned by `resolve_category_component_mapping`. Reject a supplied separator that differs from the selected CAT# delimiter; do not infer or substitute a delimiter. |
| Category components are supplied | Map them only with the selected CAT# instance's current exported metadata. Do not infer a delimiter, KFF identifier, or package position. |
| Category component values are resolved | Use resolve_category_component_values for the assigned value-set checks, case handling, and customer disclosure. Incomplete evidence does not establish a missing value. |

## Category Existence Evidence Routes

1. **BOSS first:** Use the Core BOSS client for
   `/api/boss/data/objects/ora/erpCore/fixedAssetsSetup/v1/assetAllSegmentsCategoriesView`.
   Verify target metadata and map components to verified storage attributes.
   Retrieve candidate combinations across structures before applying the selected
   structure identity locally; a selected-structure-only query misses collisions.
   Prefer a bounded `$filter` using `in` lists for requested component values when
   the target accepts that syntax. For example, verified attributes may support
   `segment1 in ('MACHINERY','COMPUTER') and segment2 in ('CONVEYORS','PC')`.
   This returns a candidate superset: locally match each exact ordered component
   tuple, rather than treating every major/minor cross-product as requested.
   Alternatively use OR groups of exact component predicates. Escape string
   literals, pass query arguments separately, and split large filters into bounded
   batches without dropping any requested tuple. Rejected filters require the
   governed export fallback; never interpret a filter error as absence.
   Request `$limit=500` or a lower target-supported page size and follow `$offset`
   or the returned next link until `hasMore=false` for every batch. A page-size
   limit is not a total-result limit. If the target caps results without complete
   continuation, visibility is insufficient, or a page repeats, use the export
   fallback. Never claim complete absence from the first 500 rows.
   Oracle documents SQL-like BOSS filters with case-sensitive payload attributes,
   AND/OR conjunctions, and grouped predicates in
   [BOSS Data Filtering](https://docs.oracle.com/en/database/oracle/apex/26.1/htmdb/data-filtering.html).
   Acceptance of `in` and page continuation must still be verified on the target.
2. **Export fallback:** If BOSS evidence is insufficient, use a complete same-target
   `FA_MANAGE_ASSET_CATEGORY` export through the shared workflow and approval gate.
   Validate completion and file integrity, then match requested component tuples
   across all exported structures for collision holds and the exact selected
   structure code for existence/material comparison. Standard REST may supply
   missing evidence when complete.

Only complete evidence for all requested tuples can prove `absent`. Compare all
requested fields for selected-structure `match`, `update_selected`, or
`existing_different`; duplicates
or conflicts are `ambiguous`, and unresolved incomplete evidence is `failure`.
Keep selected-structure existence separate from cross-structure collision evidence.
Under this workflow's conservative create policy, an identical ordered component
tuple in another structure blocks that category's create readiness even when the
selected structure is absent. Report the existing category and structure identity;
do not reuse, move, update, or attach books to the other-structure category. This is
a preventive workflow rule, not proof of a universal Fusion uniqueness constraint.
Do not depend solely on `categoryConcatenatedSegment`, which may be null.
Record the evidence and fallback reason, retain update/preserve and import
approvals, and never use donor defaults or mix targets.

### Restart after an import failure

Reconcile fresh category, category-book, and default state after a failed or
partially successful import before selecting retry rows. Never map generated log
row IDs to source combinations by numeric order or assume rows without errors
committed. If the customer requests the remaining categories, exclude every held
category and all its book/default children together. Preserve the original full
scope and show submitted versus held combinations. Resolve existing selected-
structure rows and material deltas before authoring update actions. Fresh input,
dependency, reference, default, design, and import-gate validation must cover the
new subset, and Core Data Loader must generate a new approval preview.

## Depreciation Method Evidence

Read `GET /api/boss/data/objects/ora/erpCore/fixedAssetsSetup/v1/assetDepreciationMethodsView`
using target-supported request parameters.
If the response has `hasMore: true`, use a complete same-target depreciation-method
export through the shared task-level export workflow and its approval gate instead
of continuing BOSS paging. A failed or incomplete BOSS lookup uses the same fallback.
Verify export task, completion, scope, and file integrity; match exact method code,
life in months, enabled state, and reference set. Partial responses cannot establish
absence or complete validation. Record the fallback and evidence; never use donor defaults.

## Category Account Matching

| Situation | What Happens |
|---|---|
| Selecting a natural account | Match the requested account role from the selected book ledger's Natural Account values. Category component values/descriptions may improve role matching, but a unique role-specific ledger candidate is eligible even when its description is generic. Normalize case and punctuation, but do not accept a nearest-text score or category keyword alone. Record the role-match evidence. |
| Description varies from the UI role label | Literal words such as Cost are not mandatory when the description and account metadata clearly identify the role. For example, Machinery and Equipment may identify asset cost, while Depreciation Machinery and Equipment and Accumulated Depreciation Machinery and Equipment identify different roles. An account merely mentioning furniture must not fill every furniture role. |
| Major-category or subcategory account | Record whether the role match is expressed at full-category, major-category, subcategory, or generic-ledger level. Do not reuse a category-book mapping as evidence or as a derivation seed. If more than one ledger candidate remains plausible for the role, return all choices rather than selecting automatically. |
| Customer-supplied account | Preserve a complete customer selection unchanged under Category-Book Account Preparation. Do not replace it with a text-derived candidate or search for an existing full combination. |
| Lookup outcome per category/book/role | Return customer-supplied account, uniquely derived segment vector, unresolved Natural Account/skeleton, multiple Natural Account candidates, lookup failure, or invalid format. A missing full combination is not a failure. |

## Category-Book Account Preparation

Preserve complete customer-supplied account segments exactly. Check required
input, selected-COA segment count/order and format, and the CSV serialization
contract below. Do not query the accountCombinationsLOV collection or verify
full-combination existence, CCID, enabled/effective/posting/summary state, or
require a dynamic-creation flag or waiver. Do not ask for replacements or
prerequisite combination creation solely because a full combination is absent.
Record supplied accounts as customer-supplied, not target-verified combinations.

For an incomplete or omitted account, retain Natural Account value/role lookup
and unique derivation from the selected book's own skeleton. Assemble the complete
segment vector without a full-combination search. Metadata describe requests
remain allowed for COA segment format. Fusion enforces combination-level rules
at import; this preparation does not guarantee import success or authorize a retry.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_export_package_inventory | A complete same-task export is supplied; repeat actual-package checks after approved ZIP creation | `FA_MANAGE_ASSET_CATEGORY` export ZIP with all CSV members and `ASM_SETUP_CSV_METADATA.xml`; proposed rows before creation approval, actual immutable candidate ZIP only after approved creation | Validate export structure and proposed member/row inventory before ZIP-creation approval. After approved creation, require the actual ZIP's members and headers to match the task export, rows to parse with exact field counts, unique package keys, and one matching `FA_ASSET_CATEGORY` parent for every category-book/default row. At both stages, require at least one matching default depreciation date-range row for every new category-book assignment; a header-only default member does not satisfy this check. Apply default-row input and reference validation before approval. Never require or create a candidate ZIP before creation approval. | Supported package fields, date/datetime patterns, CSV quoting shape, stage-specific row inventory, parent-child member relationship, and duplicate-key report | Missing member, header mismatch, malformed row, orphan child row, duplicate key, or conflicting action blocks the next stage: creation approval for proposed data, or Final ZIP Preview and handoff for the actual archive. |
| resolve_full_category_book_account_combination | After a complete customer selection, or Natural Account and selected-book skeleton, resolve | Selected COA segment metadata plus exact supplied segments or the selected-book skeleton and resolved Natural Account | Apply Category-Book Account Preparation. For derivation replace only the Natural Account in the selected-book skeleton; for a complete customer account preserve all segments. Check format without a combination collection query. | One resolved full segment vector and input/derivation source; no existence or CCID claim | Missing/malformed skeleton when deriving, ambiguous Natural Account, missing segment metadata, or invalid format blocks. A full combination need not already exist. |
| validate_category_book_account_serialization | Before ZIP-creation approval using proposed data; after approved ZIP creation, before Final ZIP Preview and immediately before Data Loader handoff | Proposed segment vectors and in-memory CSV records before creation approval; actual immutable candidate ZIP only after approved creation; current same-target FA_MANAGE_ASSET_CATEGORY structural contract and active COA segment order for both stages | Reparse proposed in-memory CSV records before ZIP-creation approval without creating an archive. After approved creation, parse the actual ZIP's CSV records. In both stages enforce Category-Book Account Format below for every populated account field, including unused positions and the terminator, and require each record to have exactly its header's field count. | Stage-specific per-role serialization receipt with segment-position count, terminator check, and exact value/order comparison | Missing or altered blank positions, missing/extra terminator, flattened or literal escaped line breaks, unquoted multiline fields, changed values/order, or CSV field-count mismatch blocks the next stage: creation approval for proposed data, or Final ZIP Preview and handoff for the actual archive. |
| resolve_same_book_donor_row | Optional formatting review when a default-rule row is authored and a populated export is available | Selected book and exported default rows | Use only one unambiguous same-book row as formatting evidence; do not use a donor when rows are ambiguous | Date pattern and optional-field representation only; never depreciation defaults, account combinations, or account segments | Missing, duplicate, or ambiguous donor rows do not block when approved customer values and current export-format evidence are available. |

## Category DFF Resolution

### Validation Stages

Use this resolver in two declared stages:

- `input_gate` at MAC.RESOLVE_DFF_INPUT: after read-only System Controls,
  CAT# structure discovery, and required component mapping, obtain the single
  batch definition export and check definition identity, applicability,
  context, supplied-field mapping, and required input for new in-scope rows.
  Do not run value-set membership checks or require unchanged update values
  at this stage. Record preservation checks as pending, not passed.
- `full_validation` at MAC.RESOLVE_REFERENCES: reuse the same definition
  export and current foundation evidence; resolve exact-row preservation
  and perform the remaining datatype/value-set and comparison checks. This
  stage remains mandatory before match, create/update readiness, or packaging.

If later scope resolution identifies another new row, repeat its input checks
using the same export before any prerequisite preparation. Changed batch
membership or target follows the existing new-export rule. Completing the
input gate alone never means validated_for_import.

### Definition and Value Checks

Obtain one completed same-environment Manage Fixed Assets Descriptive
Flexfields setup-data export per immutable batch through
core.fusion-api.apps-common.descriptive-flexfields.
Use task FA_MANAGE_FIXED_ASSETS_DESCRIPTIVE_FLEXFILEDS, offering Financials,
and functional area Fixed Assets; resolve sequence and eligibility through
the authoritative catalog and shared export workflow.
Retain ProcessId, ZIP reference, outcome, environment, and batch identity.

Reuse this one export across all four DFF codes and applicable records in the
unchanged batch. Do not export separately per category, book, default row,
or DFF code. Export again for a new batch or changed batch/environment.

1. Confirm application 140 and the three FA DFF identities from current
   metadata: FA_CATEGORIES for headers, FA_CATEGORY_BOOKS for assignments,
   and FA_CATEGORY_BOOK_DEFAULTS for default rules. Resolve the application
   identity and regional applicability of JG_FA_CATEGORY_BOOKS separately
   from authoritative metadata; do not assume application 140. Stop on
   identity mismatches or unverified applicability.
2. Scope global definitions from
   ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_GLOBAL_SEGMENT.csv to each exact
   application/DFF. Retain all enabled segments, not only required ones.
3. Resolve each selected context from
   ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv in the same export.
   Require one exact enabled ContextCode, otherwise one exact enabled Name,
   within that application/DFF.
4. Read enabled context-sensitive definitions from
   ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv for the same application,
   DFF, and resolved context. Blank context never waives global requirements.
5. Use RequiredFlag to identify mandatory values, including hidden segments.
   Map supplied values by unique current ColumnName, SegmentCode, or Prompt
   within the exact row/DFF/context. Reject unknown, disabled, out-of-context,
   ambiguous, or conflicting assignments.
6. Check required input for every newly created in-scope row before any
   value-set prerequisite preparation. A new category-book assignment
   includes its required new default-rule rows even for an existing category.
   For updates, resolve omitted unchanged values from exact current-row
   evidence; unresolved preservation cannot waive a required segment.
7. Delegate only read-only value-set verification through Manage Fixed Assets
   Flexfield Value Sets. Never create, enable, or modify sets or values.
   No ValueSetCode requires column-contract validation. Format Only requires
   applicable type/format/length/precision/scale/range checks, not enumerated
   membership. Independent requires exact eligible membership; Dependent
   also requires the exact eligible parent/value pair. Table membership is
   unsupported by the current delegated workflow: report unverified and stop.
   Unsupported types, incomplete coverage, and unresolved visibility block.
8. Retain supplied values and documented canonical conversions separately.
   Show conversions in the reviewed proposal. Resolve actual import headers
   from the current task contract, never from assumed database column names.

For JG_FA_CATEGORY_BOOKS, discover applicable required regional segments and
validate supplied or preserved values using the same read-only checks.
Keep its regional context and GLOBAL_ATTRIBUTE* mappings separate from the
FA_CATEGORY_BOOKS context and ATTRIBUTE* mappings. Use current metadata and
the import contract to resolve the actual context and CSV headers; never
copy ordinary DFF mappings into regional fields.

Check the batch export for all four definitions. Do not silently skip
JG_FA_CATEGORY_BOOKS or infer nonapplicability from missing metadata.
If the declared export route cannot establish its definition/applicability,
report the source gap and block the affected scope. Do not substitute a
different external route. A nonapplicable result requires affirmative evidence.

Attribute values belong to their category, category/book, or category/book/
default-date-range row. Retain source-row attribution until derived keys are
resolved. Never copy a parent's DFF values into a child or between default
date ranges.

Preserve update values only for the same resolved segment/context and exact
target row. Physical column equality across contexts is insufficient.
Clearing or remapping needs an explicit change and supported import semantics.
Missing live DFF evidence has no inferred fallback route.

An unchanged reference-parent row does not authorize category-header changes.
Use an identity-only parent form only when the target contract supports it;
if included parent DFF fields must be serialized, preserve their exact current
values. Do not invent or blank them.

Before match/no-op, require complete comparison of applicable supplied DFF
criteria and resulting in-scope values. Pure existence checks must not demand
new-record inputs or imply that unexamined DFF values were validated.

## Category-Book Account Format

For every populated category-book account field, first use
`resolve_book_ledger`, `resolve_chart_of_accounts`, and
`describe_account_combination_segments`. The returned
`FND_ACFF_Delimiter` and active segment order are the only authority for the
readable COA display combination; CAT# delimiters and donor display strings are
not account-format evidence.

After `resolve_full_category_book_account_combination` prepares the full segment
vector under Category-Book Account Preparation, serialize each populated account field in `FA_ASSET_CATEGORY_BOOKS.csv`
as one quoted multiline CSV cell containing **30 segment positions followed by
`CSV_END`**. The corrected customer-supplied CSV establishes this format:

1. Place the account's exact stored segment strings in COA order, preserving
   leading zeros and any blank positions within that order.
2. Fill the remaining positions through position 30 with empty strings, not
   spaces. A five-segment COA needs 25 trailing empty positions; a six-segment
   COA needs 24. Never truncate a COA exceeding 30 positions; report a contract gap.
3. Append `CSV_END` as position 31. Join the 31 elements with actual LF characters
   and quote the whole cell using a CSV writer. Do not append a newline after
   the terminator, trim trailing empty positions before it, use literal escaped
   newline text, or replace line breaks with the readable COA delimiter.
4. Reparse the generated CSV. Each populated account cell must split on LF into
   exactly 31 elements: 30 segment positions plus the final `CSV_END`. Compare
   every active position exactly with its resolved segment and every unused
   position with the empty string. These are positions inside one cell, not
   separate CSV records. Leave omitted optional account fields entirely empty.

Use structural export evidence for member names, columns, and CSV encoding;
do not copy exported account values or require populated donor rows to apply
this serialization contract.

## Field Lookup Notes

| Field or group | Lookup behavior |
|---|---|
| `StructureInstanceCode` | Resolve only from System Controls `CatStructureInstanceCode`, then require its exact enabled CAT# export match. Never ask the customer to choose an enabled structure. |
| `fixedAssetBooksLOV` output | Resolve the selected book with the documented `BookTypeCode` query attribute, not a display-name guess. Treat `Name` as the returned ledger name. `DateIneffective` is the active-state evidence; the LOV does not expose an `EnabledFlag`. If exact resolution fails, use only active paged `BookTypeCode` results to offer up to three ranked, user-selectable suggestions; do not infer a selection from a ledger name or use an undocumented display-name query. |
| `fixedAssetCategoriesLOV` output | Use as supplementary or independently complete category existence/read-back evidence under Category Existence Evidence Routes. BOSS `assetAllSegmentsCategoriesView` is the preferred existence route. Call `describe` first and compare the selected structure and actual component attributes across complete paging. If required structure/component evidence is missing, follow Category Existence Evidence Routes; absence of attributes is not category absence. The fixed documented fields include `_CATEGORY_ID`, `_STRUCTURE_INSTANCE_NUMBER`, `EnabledFlag`, `StartDateActive`, `EndDateActive`, and links. Do not use this LOV to infer delimiter or value-set mapping. |
| CAT# KFF export | Delegate to `erp.financials.fixed-assets.manage-fixed-assets-key-flexfields` with task `FA_MANAGE_FIXED_ASSETS_KEY_FLEXFIELDS`, application `140`, and flexfield `CAT#`. Use its current Key Flexfields export and match `CatStructureInstanceCode` to one enabled CAT# instance. Do not use Asset Key examples such as `FA_ASSET_KEY`, `KEY#`, or `LOC#` for category parsing. |
| Existing values for a structure instance | Use the verified BOSS `structureInstanceNumber`, REST `_STRUCTURE_INSTANCE_NUMBER`, or export `StructureInstanceCode` to confirm the category belongs to the resolved CAT# structure, then use the component-to-KFF-segment mapping to identify each component's value set. Query those value sets through `valueSets` and child `values` REST links as the primary check. A current same-environment export may support a documented REST fallback, but does not replace successful REST evidence. Do not treat the categories LOV result list as the complete set of allowed category component values because it only shows category combinations that already exist. |
| KFF export freshness | Use the current target Key Flexfields export delegated through `discover_category_kff_structure`. Require it to contain the System Controls-selected enabled CAT# instance and its required segment/value-set columns. |
| Category combination and mapped components | Map category components to the selected structure's KFF segments, verify each component value through REST value-set endpoints, then derive package component positions only from that mapping. Display prompts using the mapped KFF segment labels for that customer's structure. |
| Category header fields | Validate category type, ownership, capitalization, property type/class, physical inventory, intangible flag, active dates, and supplied DFF context/segments against target lookup/export metadata before preview. |
| Translation language and source language | Resolve from existing translation/session language when a translation row is needed. |
| Asset book | Resolve from the asset book LOV/read result; do not infer from ledger alone. |
| Account resolution sequence | Resolve the asset book to its ledger; resolve that ledger to its chart-of-accounts structure; inspect the structure's segment metadata to identify the Natural Account segment and its value set; follow the returned canonical child-values URL for that value set. Do not construct numeric value-set URLs. |
| Natural-account search | Use list_natural_account_values and Category Account Matching for derivation. Accept one unique role-specific Natural Account after selected-book skeleton substitution and format checks; do not verify full-combination existence. |
| Selected-book account skeleton | Read the selected book's `FlexbuilderCcidSegments`, map it to the resolved COA segment order, and use it only as the selected-book default skeleton. The Natural Account segment is replaced per account role; all other segments remain as the selected book returned them. |
| Full account combination | Use resolve_full_category_book_account_combination and Category-Book Account Preparation to preserve supplied segments or assemble the selected-book skeleton with the resolved Natural Account. No full-combination collection query. A multiline representation is one account cell, not separate account values. |
| Same-book donor row | When a populated `FA_MANAGE_ASSET_CATEGORY` export already includes the selected book, use it only for date formatting and optional-field representation. It is not evidence for depreciation defaults or accounts and must not supply values, account segments, or an account skeleton. |
| Account field role map | Map every populated account field to its business role before searching natural-account values: Asset Cost, Asset Clearing, Depreciation Expense, Depreciation Reserve, Bonus Depreciation Expense, Bonus Depreciation Reserve, CIP/WIP Cost, CIP/WIP Clearing, Impairment Expense, Impairment Reserve, Unplanned Depreciation Expense, Revaluation Amortization, Revaluation Reserve, Revaluation Loss, Cost Write Off, lease roles, and annuity interest expense or revenue roles. |
| Account description matching | Category Account Matching owns Natural Account role derivation; ora_design_enforcement.md owns resolved-account and serialization gates; ora_error_handling.md owns per-role review and customer requests. |
| Required and optional account combinations | Resolve every required or supplied role through resolve_category_book_accounts. Copy resolved expense/reserve vectors to omitted bonus roles. Derive conditional accounts only when required by book/category features. Apply Category-Book Account Preparation and serialize complete vectors under Category-Book Account Format; never write an unresolved placeholder or natural-account value alone. |
| Default depreciation expense combination (`DefaultExpenseCcidFlag`) | Preserve or default blank/unchecked. Present the UI value as Yes or No. Accept `Y`/`N` or `YES`/`NO` case-insensitively; translate affirmative input to stored `Y` and negative input to stored `N`. Never serialize `YES`, `NO`, selected, or cleared. |
| Category Active From and From/To Date Placed in Service | Default Category Active From from System Controls and From Date Placed in Service from the selected book calendar. Apply `ora_defaulting_rules.md`, preserve the target date pattern, and validate dates through `ora_input_validation.md`. |
| Depreciate Flag (`DepreciateFlag`, also called DepreciationFlag) | When blank, default to `NO`; validate the supplied or defaulted value against target-supported default-rule values. |
| Depreciation Method | Resolve the user-supplied exact method/life record and its reference set. Accept Common Set without checking book assignments; otherwise compare only with the selected book's Depreciation Methods Reference Data Object set. |
| Life | Convert Life in Years and Life in Months to package-ready month value when required. |
| Prorate Convention | Resolve the user-supplied fiscal-year-compatible convention and its reference set. Accept Common Set without checking book assignments; otherwise compare only with the selected book's Prorate Conventions Reference Data Object set. |
| Retirement Convention | Resolve the user-supplied fiscal-year-compatible convention and its reference set. Accept Common Set without checking book assignments; otherwise compare only with the selected book's Prorate Conventions Reference Data Object set. |
| Optional default depreciation fields | Resolve bonus rule, ceiling, limit, salvage percent, group asset, threshold, low-value, and tracking setup only when supplied/requested. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| MAC.RESOLVE_DFF_INPUT | decision | 15 | reference_lookup | ready->MAC.CHECK_DEPENDENCIES;missing_or_invalid_input->MAC.HANDLE_INPUT;unverified->MAC.HANDLE_DFF_LOOKUP | MAC.VALIDATE_INPUT | stop | Resolve the read-only System Controls/CAT# foundation and required component mapping. Execute resolve_category_dff_segments in input_gate mode for new in-scope rows before dependency assessment or prerequisite preparation. Pure existence checks without DFF criteria do not request create input or export DFF definitions. |
| MAC.RESOLVE_REFERENCES | decision | 30 | reference_lookup | match->MAC.DONE_MATCH;absent->MAC.APPLY_DEFAULTS;update_selected->MAC.APPLY_DEFAULTS;existing_different->MAC.HANDLE_EXISTING_DIFFERENT;ambiguous->MAC.HANDLE_LOOKUP;failure->MAC.HANDLE_LOOKUP;missing_dff_input->MAC.HANDLE_INPUT;invalid_dff_value->MAC.HANDLE_INPUT | MAC.CHECK_DEPENDENCIES | stop | Reuse the current System Controls/CAT# mapping and batch DFF definition from MAC.RESOLVE_DFF_INPUT. Execute resolve_category_dff_segments in full_validation mode for the resolved row scopes, including regional applicability, exact-row preservation, datatype/value-set checks, and comparison. Recheck newly identified create-row input before any prerequisite preparation without re-exporting the unchanged batch definition. Require full validation before match, absent/create readiness, or update_selected; unverified DFF evidence follows failure. Preserve across-structure collision clearance and fresh reconciliation before any reduced retry scope. |
