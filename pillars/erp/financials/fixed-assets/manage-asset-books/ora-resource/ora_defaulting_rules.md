# Defaulting Rules

## Standard Defaults

Apply documented defaults automatically before asking for missing inputs.
Resolve internal fields and import mappings without asking the user. Use the
system date for Last Depreciation Run on create, resolve the selected ledger's
identifier, and default Natural Account check to Yes. Preserve supported
overrides and unchanged update values. Leave optional fields without defaults
blank; resolve required mapping gaps internally before import.

| Functional field | Internal | Default Value | Applies When | User Override |
|---|---|---|---|---|
| FSM package contract | Yes | Use only the current target CSV headers and structural metadata XML; never use exported data rows. | Any FSM CSV export/import work | No |
| Technical identifier or lookup code | Yes | Resolve from current exported metadata first, then documented supported read-only metadata. | A required field uses an internal code or identifier | No |
| Asset Book Code | No | Validate the supplied value. When it is blank, use the supplied, validated Book Name. | Every create or update; default only when Asset Book Code is blank and Book Name matches `^[A-Z][A-Z0-9 ]{0,29}$` | Yes |
| Name / Asset Book Name | No | Use the resolved, validated Asset Book Code. | Name is blank after Asset Book Code resolves and Asset Book Code matches `^[A-Z][A-Z0-9 ]{0,29}$` | Yes |
| Description | No | Use the resolved, validated Name / Asset Book Name when Description is omitted. | A valid supplied or defaulted Name / Asset Book Name and no Description | Yes |
| Book Class | No | Default to `Corporate`; use Tax only when explicitly selected. | New book when Tax is not explicitly selected | Yes |
| Associated Corporate Book | No | For a Corporate book, automatically select its own resolved Asset Book Name. For a Tax book, require the user to select one exact existing compatible Corporate book; do not choose that book on the user's behalf. In the current FSM contract, write the resolved value to `DistributionSourceBook` in every applicable parent-book row; never leave it blank. | Every Corporate or Tax book | Yes |
| Depreciation Calendar | No | Required user input; no automatic default. Accept the supplied calendar label and resolve its technical identifier through the approved lookup. Do not request the technical name again. | Every create or update | Yes |
| Fiscal Year | No | Use the fiscal year resolved from the selected Depreciation Calendar and current period. | Fiscal Year is blank after the Depreciation Calendar resolves | Yes, only when the supplied Fiscal Year belongs to the selected calendar |
| Prorate Calendar | No | use the exact resolved Depreciation Calendar value. | Prorate Calendar is blank and Depreciation Calendar is resolved | Yes |
| Allow amortized changes | No | `NO`.  use `YES` only when the request or approved policy enables it. | New book when request/policy does not enable it | Yes |
| Depreciate if retired in the first year | No | `YES`. Use `NO` only when the request or approved policy disables it. | New book when request/policy does not disable it | Yes |
| Copy retirements | No | `NO`. Use `YES` only when the request or approved policy enables it. | New book when request/policy does not enable it | Yes |
| Copy adjustments | No | `NO`. Use `YES` only when the request or approved policy enables it. | New book when request/policy does not enable it | Yes |
| Allow mass changes | No | `NO`. Use `YES` only when the request or approved policy enables it. | New book when request/policy does not enable it | Yes |
| Allow cost ceiling | No | `NO`. Use `YES` only when the request or approved policy enables it. | New book when request/policy does not enable it | Yes |
| Allow depreciation expense ceiling | No | `NO`. Use `YES` only when the request or approved policy enables it. | New book when request/policy does not enable it | Yes |
| Allow mass copy | No | `NO`. Use `YES` only when the request or approved policy enables it. | New book when request/policy does not enable it | Yes |
| Allow purge | No | `NO`. Use `YES` only when the request or approved policy enables it. | New book when request/policy does not enable it | Yes |
| Copy salvage value | No | `NO`. Use `YES` only when the request or approved policy enables it. | New book when request/policy does not enable it | Yes |
| Copy additions | No | `NO`. Use `YES` only when the request or approved policy enables it. | New book when request/policy does not enable it | Yes |
| Allow CIP assets | No | `NO`. Use `YES` only when the request or approved policy enables it. | New book when request/policy does not enable it | Yes |
| Default revaluation for fully reserved assets | No | `NO`. Use `YES` only when the request or approved policy enables it. | New book when request/policy does not enable it | Yes |
| Select Book by Clearing Account Segment: Natural Account check | No | `Y`. Use `N` only when the request or approved policy disables it. | New book when request/policy does not disable it | Yes |
| Select Book by Clearing Account Segment: clearing-account | No | `N`. Use `Y` only when the request or approved policy enables it. | New book when request/policy does not enable it | Yes |
| Select Book by Clearing Account Segment: Primary Balancing | No | `N`. Use `Y` only when the request or approved policy enables it. | New book when request/policy does not enable it | Yes |
| Book Info | No | Blank; it is a descriptive flexfield. | No explicit DFF requirement | Yes |
| Allow cost sign changes | No | Leave `Allow cost sign changes` blank when the request or policy does not set it. | Request/policy does not enable it | Yes |
| Allow impairment | No | Blank. | Request/policy does not enable it | Yes |
| Allow ledger posting | No | `NO`.  use `YES` only when the request or approved policy enables it. | New book when request/policy does not enable it | Yes |
| Allow physical inventory | No | Blank. | Request/policy does not enable it | Yes |
| Allow leased assets | No | Blank. | Request/policy does not enable it | Yes |
| Use NBV threshold for depreciation | No | Blank. | Request/policy does not enable it | Yes |
| Allow transfer to another book | No | Blank. | Request/policy does not enable it | Yes |
| Allow annuity depreciation | No | Blank. | Request/policy does not enable it | Yes |
| Last Depreciation Run | Yes | Runtime system date (`sysdate`). | Create mode | No |
| Last Depreciation Run Status | Yes | `Completed`. | Create mode | No |
| Depreciation allocation | No | Map the business label `Evenly` to the technical CSV value `E` and `By Days` to `D`. Show `Evenly` or `By Days` in the preview. Never write a display label into `Depreciation allocation`. | Depreciation allocation is blank or supplied as the display label `Evenly` or `By Days` | Yes |
| Asset Bonus Rules reference-data set | No | `Enterprise Set`. A supplied shared or field-specific Reference Data Set overrides this default. | Blank | Yes |
| Asset Depreciation Ceilings reference-data set | No | `Enterprise Set`. A supplied shared or field-specific Reference Data Set overrides this default. | Blank | Yes |
| Asset Depreciation Methods reference-data set | No | `Enterprise Set`. A supplied shared or field-specific Reference Data Set overrides this default. | Blank | Yes |
| Asset Descriptions reference-data set | No | `Enterprise Set`. A supplied shared or field-specific Reference Data Set overrides this default. | Blank | Yes |
| Asset Prorate Conventions reference-data set | No | `Enterprise Set`. A supplied shared or field-specific Reference Data Set overrides this default. | Blank | Yes |
| Asset Queue Names reference-data set | No | `Enterprise Set`. A supplied shared or field-specific Reference Data Set overrides this default. | Blank | Yes |
| Asset Retirement Types reference-data set | No | `Enterprise Set`. A supplied shared or field-specific Reference Data Set overrides this default. | Blank | Yes |
| Asset Unplanned Types reference-data set | No | `Enterprise Set`. A supplied shared or field-specific Reference Data Set overrides this default. | Blank | Yes |
| Required Natural Accounts | Yes | When the ledger and book are resolved and no account value is supplied, derive every required Natural Account from the selected ledger. Do not ask the user to provide default accounts. | Every required account field without a user-supplied override | Yes |
| Required value resolution | Yes | Stop package generation and report the unresolved value and its resolution evidence. Do not substitute a guessed value or solicit an internally derived value from the user. | A required value cannot be resolved uniquely and validly | No |
| Account Defaults | Yes | Preserve supplied Account Defaults exactly and apply the supplied-input rule in ora_reference_lookups.md without a full-combination lookup or existence requirement. When omitted, derive one complete valid combination from the selected ledger through the approved COA-scoped lookup; do not copy, normalize, or infer it from an existing book or export row. | Every new or changed book | No |
| Net Book Value Retired Gain | No | Derive one enabled, effective, non-summary Natural Account matching `Gain`, `NBV`/`Net Book Value`, and `Retirement`/`Retired`. | Field is required | Yes |
| Net Book Value Retired Loss | No | Derive one enabled, effective, non-summary Natural Account matching `Loss`, `NBV`/`Net Book Value`, and `Retirement`/`Retired`. | Field is required | Yes |
| Proceeds of Sale Gain | No | Derive one enabled, effective, non-summary Natural Account matching `Gain`, `Proceeds`, and `Sale`. | Field is required | Yes |
| Proceeds of Sale Loss | No | Derive one enabled, effective, non-summary Natural Account matching `Loss`, `Proceeds`, and `Sale`. | Field is required | Yes |
| Proceeds of Sale Clearing | No | Derive one enabled, effective, non-summary Natural Account matching `Proceeds`, `Sale`, and `Clearing`. | Field is required | Yes |
| Cost of Removal Gain | No | Derive one enabled, effective, non-summary Natural Account matching `Cost`, `Removal`, and `Gain`. | Field is required | Yes |
| Cost of Removal Loss | No | Derive one enabled, effective, non-summary Natural Account matching `Cost`, `Removal`, and `Loss`. | Field is required | Yes |
| Cost of Removal Clearing | No | Derive one enabled, effective, non-summary Natural Account matching `Cost`, `Removal`, and `Clearing`. | Field is required | Yes |
| Deferred Depreciation Expense | No | Derive one enabled, effective, non-summary Natural Account matching `Deferred`, `Depreciation`, and `Expense`. | Field is required | Yes |
| Deferred Depreciation Reserve | No | Derive one enabled, effective, non-summary Natural Account matching `Deferred`, `Depreciation`, and `Reserve`. | Field is required | Yes |
| Nonsale Gain | No | Leave blank; do not derive from the ledger. If the customer provides a value, validate and use it. | Optional field | Yes |
| Allow revaluation | No | `NO`. Use `YES` only when the request or approved policy enables it. | Every new or changed book | No |
| Allow Cost-Based Revaluation | No | Blank. | Every new or changed book | No |
| Allow Net Book Value-Based Revaluation | No | Blank. | Every new or changed book | No |
| Allow revaluation of accumulated depreciation | No | `NO`. Use `YES` only when the request or approved policy enables it. | Every new or changed book | No |
| Allow Revaluation of Current-Year Depreciation | No | `NO`. Use `YES` only when the request or approved policy enables it. | Every new or changed book | No |
| Transfer Revaluation Reserve on Retirement | No | Blank. | Every new or changed book | No |
| Allow Amortization of Revaluation Reserve | No | `NO`. Use `YES` only when the request or approved policy enables it. | Every new or changed book | No |
| Default to Period-End Revaluation | No | Blank. | Every new or changed book | No |
| Include Fully Depreciated Assets in Revaluation | No | Blank. | Every new or changed book | No |
| Default Useful-Life Extension Factor | No | Blank. | Every new or changed book | No |
| Revaluation Reserve Retired Gain | No | Blank when revaluation is not enabled. When enabled, derive one enabled, effective, non-summary Natural Account matching `Revaluation`, `Reserve`, `Retired`, and `Gain`. | Revaluation-related configuration | No |
| Revaluation Reserve Retired Loss | No | Blank when revaluation is not enabled. When enabled, derive one enabled, effective, non-summary Natural Account matching `Revaluation`, `Reserve`, `Retired`, and `Loss`. | Revaluation-related configuration | No |
| Book Control ID | Yes | Leave blank; Fusion resolves it at import runtime. | New-book creation | No |
| Current Fiscal Year | Yes | Use the selected Fiscal Year only when it contains the user-selected current period. | Every create or update | No |
| Last Period Fiscal Year | Yes | Leave blank; Fusion manages the value at runtime. | Every create or update | No |
| Last Period Num | Yes | Leave blank; Fusion manages the value at runtime. | Every create or update | No |
| Last Period Name | Yes | Leave blank; Fusion manages the value at runtime. | Every create or update | No |
| Fiscal Year Start Date | Yes | Leave blank; Fusion manages the value at runtime. | Every create or update | No |
| Fiscal Year End Date | Yes | Leave blank; Fusion manages the value at runtime. | Every create or update | No |
| Ledger Name | No | Resolve the selected ledger and include its exact name in the prepared import data. | Every create or update using the current FSM contract | Yes |
| Inactive Date | Yes | Leave blank; Fusion manages the date when a book is inactivated. | Every create or update | No |
| Last Mass Copy Period Counter | Yes | Leave blank; Fusion manages the value at runtime. | Every create or update | No |
| Last Purge Period Counter | Yes | Leave blank; Fusion manages the value at runtime. | Every create or update | No |
| Create Accounting Request ID | Yes | Leave blank; Fusion manages the value at runtime. | Every create or update | No |
| Initial Date (`Initial Date`) | Yes | Use the start date of the period immediately before the resolved current depreciation period. | Every create or update after the selected book calendar and current period are resolved | No; do not request or accept user input |

The field descriptions in this table are business descriptions and can differ from the field names shown in Default Accounts. Use the same customer-facing label for the same value in input preview, reference validation, design review, package review, and verification. Confirm each field against the current CSV header or structural metadata before package generation; do not expose raw technical names in the default review.

## CSV Fields with No Default

Preserve every valid user-provided value for non-system-managed fields; do not
replace it with a default or a blank. Apply a documented default only when the
user has not provided a value. For a field marked `Blank` below, leave it blank
only when the implementation request does not supply a value and no prerequisite
workflow resolves one. This preservation rule does not apply to WHO/audit
fields, which are Fusion-managed and must follow the current target contract's
blank or system-managed representation.

The following current `asset book data file` fields have **no configured default**. Leave them blank in generated packages unless the implementation request explicitly supplies a value for a non-system-managed field, a prerequisite workflow resolves it, or Fusion resolves it at runtime. Do not infer a value from another book or export. Rows marked **Internal — Fusion runtime** are system-managed and must never be supplied as a business default.

| Functional field | Default |
|---|---|
| Capital Gain Threshold | Blank when omitted. Do not derive a value; validate a user-provided value against the target contract. |
| Mass Copy Source Book | Blank |
| Net Book Value Fraction Threshold | Blank |
| Immediate Copy | Blank |
| Use Percent Salvage Value | Blank |
| Allow Backdated Transfers | Blank |
| Allow Group Depreciation | Blank |
| Allow Construction-in-Progress Depreciation Group | Blank |
| Allow Intercompany Group | Blank |
| Copy Group Assignment Flag | Blank |
| Copy Group Addition Flag | Blank |
| Allow Construction-in-Progress Member | Blank |
| Allow Member Tracking | Blank |
| Global Attribute Date 1 | Blank |
| Global Attribute Date 2 | Blank |
| Global Attribute Date 3 | Blank |
| Global Attribute Date 4 | Blank |
| Global Attribute Date 5 | Blank |
| Global Attribute Number 1 | Blank |
| Global Attribute Number 2 | Blank |
| Global Attribute Number 3 | Blank |
| Global Attribute Number 4 | Blank |
| Global Attribute Number 5 | Blank |
| Allow Fund Accounting | Blank |
| Global Attribute 1 | Blank |
| Global Attribute 10 | Blank |
| Global Attribute 11 | Blank |
| Global Attribute 12 | Blank |
| Global Attribute 13 | Blank |
| Global Attribute 14 | Blank |
| Global Attribute 15 | Blank |
| Global Attribute 16 | Blank |
| Global Attribute 17 | Blank |
| Global Attribute 18 | Blank |
| Global Attribute 19 | Blank |
| Global Attribute 2 | Blank |
| Global Attribute 20 | Blank |
| Global Attribute 3 | Blank |
| Global Attribute 4 | Blank |
| Global Attribute 5 | Blank |
| Global Attribute 6 | Blank |
| Global Attribute 7 | Blank |
| Global Attribute 8 | Blank |
| Global Attribute 9 | Blank |
| Global Attribute Category | Blank |
| Cap Threshold Amount | Blank |
| Cap Threshold Type | Blank |
| Low Value Threshold Amount | Blank |
| Allow Unallocated Lines | Blank |
| Suppress Invoice Auto Merge | Blank |
| Round Annual Depreciation | Blank |
| Use First Date as Transaction Date | Blank |
| Copy Amortization Adjustment Expense | Blank |
| Copy Transfers Flag | Blank |
| Copy Lease Assets Flag | Blank |
| Copy All Cost Adjustments | Blank |
| Allow UK Government Revaluation | Blank |
| Attribute Date 1 | Blank |
| Attribute Date 2 | Blank |
| Attribute Date 3 | Blank |
| Attribute Date 4 | Blank |
| Attribute Date 5 | Blank |
| Attribute Number 1 | Blank |
| Attribute Number 2 | Blank |
| Attribute Number 3 | Blank |
| Attribute Number 4 | Blank |
| Attribute Number 5 | Blank |
| Copy Group Change Flag | Blank |
| Prevent Prior Period Txns Flag | Blank |
| Additions Approval Flag | Blank |
| Adjustments Approval Flag | Blank |
| Transfers Approval Flag | Blank |
| Retirements Approval Flag | Blank |
| Depreciation Adjustment Account | Blank |
| Track Source Lines in Tax Book | Blank |
| Allow Direct Tax Addition | Blank |
| Enable Payables AutoPost | Blank |
| Select Book by Clearing Account Segment: Secondary Balancing | Blank |

## Book-account representation

For every derived book-account field, write only the resolved Natural Account (`GL_ACCOUNT`) value to its CSV field. Do not use the Account Defaults combination as a segment skeleton, do not write a full combination, and do not add any non-Natural Account segment values. Preserve the supplied Account Defaults combination only in its own field.

## FSM Representation Corrections

- In `FA_BOOK.csv` and `FA_CORPORATE_BOOK.csv`, use the current target's canonical technical values: `BookClass` is `CORPORATE` for a Corporate book and `DeprnStatus` is `Completed`. For a Corporate book, write its own resolved Asset Book Name to `DistributionSourceBook`. For a Tax book, write the exact user-provided, validated Corporate book. A blank `DistributionSourceBook` is invalid.
- Write `account combination segments` only in the exact, export-supported segment representation. Preserve each supplied segment's width and order; never pad, trim, concatenate, or infer a segment width. For the approved Corporate-book pattern, the representation is five newline-separated segments: `01`, `000`, `9999`, `0000`, `000`.
- Do not create a header-only `alternate asset book data file`. Include that member only when the current target contract explicitly requires it or the requested Alternate/Tax-book scope supplies at least one row.
- WHO audit fields are Fusion-managed. Preserve the current target header and use only its prescribed blank or system-managed representation. Never request, derive, copy, supply, or modify `Created By`, `Creation Date`, `Last Update Date`, `Last Update Login`, or `Last Updated By`.

Default depreciation expense combination belongs to Category-Book setup under
Manage Asset Categories. Do not include it in Asset Books rows or treat its
mapping as an Asset Books blocker.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FA_BOOK.DEFAULTS_RESOLVED | step | 5 | apply_default | resolved->FA_BOOK.DESIGN_ENFORCED;blocked->FA_BOOK.RETURN_ISSUES | FA_BOOK.DEPENDENCIES_READY | stop | Required dependencies are complete and documented defaults are applicable. |
