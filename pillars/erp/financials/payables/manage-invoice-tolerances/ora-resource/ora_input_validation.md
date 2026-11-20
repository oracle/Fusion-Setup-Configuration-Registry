# Input Validation

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_TOLERANCE_TEMPLATE::Description, AP_TOLERANCE_TEMPLATE::MaxQtyConTolerance, AP_TOLERANCE_TEMPLATE::MaxQtyOrdTolerance, AP_TOLERANCE_TEMPLATE::MaxQtyRecTolerance, AP_TOLERANCE_TEMPLATE::PriceTolerance, AP_TOLERANCE_TEMPLATE::QtyConsumedTolerance, AP_TOLERANCE_TEMPLATE::QtyReceivedTolerance, AP_TOLERANCE_TEMPLATE::QuantityTolerance, AP_TOLERANCE_TEMPLATE::RateAmtTolerance, AP_TOLERANCE_TEMPLATE::ShipAmtTolerance, AP_TOLERANCE_TEMPLATE::ToleranceName, AP_TOLERANCE_TEMPLATE::ToleranceType, AP_TOLERANCE_TEMPLATE::TotalAmtTolerance -->
<!-- fscr-update-fields: AP_TOLERANCE_TEMPLATE::Description, AP_TOLERANCE_TEMPLATE::MaxQtyConTolerance, AP_TOLERANCE_TEMPLATE::MaxQtyOrdTolerance, AP_TOLERANCE_TEMPLATE::MaxQtyRecTolerance, AP_TOLERANCE_TEMPLATE::PriceTolerance, AP_TOLERANCE_TEMPLATE::QtyConsumedTolerance, AP_TOLERANCE_TEMPLATE::QtyReceivedTolerance, AP_TOLERANCE_TEMPLATE::QuantityTolerance, AP_TOLERANCE_TEMPLATE::RateAmtTolerance, AP_TOLERANCE_TEMPLATE::ShipAmtTolerance, AP_TOLERANCE_TEMPLATE::ToleranceType, AP_TOLERANCE_TEMPLATE::TotalAmtTolerance -->

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Exact task package | AP_TOLERANCE_TEMPLATE.csv and ASM_SETUP_CSV_METADATA.xml; metadata ObjectShortName AP_MANAGE_INVOICE_TOLERANCES, BusinessObjectShortName AP_TOLERANCE_TEMPLATE, node /InvoiceToleranceSetVO/InvoiceToleranceSetVORow | Block candidate | Re-export the same task template and preserve exact members, header order, and metadata | Always | |
| New tolerance name | ToleranceName is required on create and at most 255 characters; a newly requested create must not reuse an exact current or newly proposed name | Block create candidate | Supply a different name | Create only | |
| Tolerance type | Explicit nonblank ToleranceType on create; a supplied update type must also be valid | Block candidate | Accept either exact CSV code or its UI label in the request, then write only QUANTITY BASED or AMOUNT BASED to the CSV | Create; update when supplied | |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Package member, metadata identity, node path, header order, or CSV row width differs from the same-task template | Blocked | Restore exact package fidelity and rerun structural validation | |
| A create name is supplied | Fresh-export uniqueness required | Build the set of existing exact ToleranceName values across all current rows regardless of ToleranceType; block a proposed name present in that set or repeated among newly requested create names. Zero exact matches do not prove a case/space variant will be accepted | |
| A create omits ToleranceType, supplies it blank, or requests a code outside QUANTITY BASED or AMOUNT BASED | Blocked before ZIP creation | Supply one of the two supported FSM import codes explicitly; Fusion rejected a blank create type as required | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Package fidelity | Require exactly one AP_TOLERANCE_TEMPLATE.csv with the 18 ordered headers from the same-task template and exact ASM_SETUP_CSV_METADATA.xml identity | Always | |
| CSV row width | Require every logical record to have exactly 18 fields, including explicit trailing blank cells | Always | |
| Create-name uniqueness | Require a nonblank ToleranceName of at most 255 characters. For a new create only, scan a fresh same-task export using exact CSV strings across all types and reject an existing or repeated newly proposed name. The UI shows AP-810297 for an existing name; FSM CSV mapping and case/space comparison semantics remain unverified | Create only | |
| Existing name immutability | ToleranceName is the record key and cannot be renamed. Description, ToleranceType, and ten tolerance-limit fields can be updated subject to their business rules; five audit fields are system-managed. Do not apply the create-name uniqueness scan or a duplicate-name warning to update. For a name shared by existing rows, use the governed Fusion import and report that row-specific verification is unavailable | Update | |
| Description | Optional for both types. When supplied, limit it to 255 characters; preserve a requested blank | When supplied | |
| Type code | Require a nonblank ToleranceType on create. Permit only exact package codes QUANTITY BASED or AMOUNT BASED; reject blank or unsupported create codes before ZIP creation. On update, validate the code when supplied and allow an unchanged type to be omitted. A controlled import rejected a blank create type with JBO-27014 | Create; update when supplied | |
| Amount-based conflict | When ToleranceType is AMOUNT BASED, PriceTolerance, ShipAmtTolerance, QtyConsumedTolerance, and MaxQtyConTolerance must be blank. For a CSV type change, include the required blanks explicitly and show each before-to-blank change in the preview. Block a request to keep a conflicting value | Before candidate preparation | |
| All ten tolerance-limit fields | No minimum populated limit count is required. For either type, parse every applicable supplied limit as a decimal and reject nonnumeric input; four quantity-only limits must be blank for AMOUNT BASED. Preserve blanks without zero fill. Do not invent range, precision, or sign limits absent source evidence | When supplied and applicable | |
| Audit fields | Do not accept requester-authored LastUpdateDate, LastUpdatedBy, LastUpdateLogin, CreationDate, or CreatedBy values; preserve existing export context only as required by the package contract | Create or update | |
| Unsupported operation | Do not infer end-date or physical-delete behavior from generic AM flags or an omitted export row | Any removal request | |

## New-Create Name Uniqueness Preflight

This validation applies only to a newly requested create. It does not run for update.

1. Before a new create candidate, obtain a fresh same-task current export and compare the proposed `ToleranceName` with the set of existing names across the complete `AP_TOLERANCE_TEMPLATE.csv`, regardless of `ToleranceType`. Use exact CSV string equality; case/space equivalence remains unverified.
2. Reject a new create if its name is in the existing-name set or matches another newly requested create. Duplicate rows in the existing baseline contribute one name to the set; their duplicate count is ignored. A name absent from the set is not blocked because other baseline names are duplicated. A zero exact match does not guarantee Fusion will accept a case/space variant.
3. Preserve existing rows. Do not add a general validation, deletion, or merge step for them.

Fusion reports `AP-810297` for a new create using an existing name. Apply the create-only check using exact CSV strings without extra case or whitespace normalization; report FSM errors as returned.

## Type-Specific Tolerance Rows

The table maps each tolerance row and associated hold name to its CSV column. “Not applicable” means the row is absent for AMOUNT BASED and its CSV value must be blank.

| Tolerance row | CSV column | Quantity based hold | Amount based hold |
|---|---|---|---|
| Ordered Percentage | `QuantityTolerance` | Ordered quantity | Amount ordered |
| Maximum Ordered | `MaxQtyOrdTolerance` | Maximum ordered quantity | Maximum ordered amount |
| Received Percentage | `QtyReceivedTolerance` | Received quantity | Amount received |
| Maximum Received | `MaxQtyRecTolerance` | Maximum received quantity | Maximum received amount |
| Price Percentage | `PriceTolerance` | Price | Not applicable |
| Conversion Rate Amount | `RateAmtTolerance` | Maximum rate amount | Maximum rate amount |
| Schedule Amount | `ShipAmtTolerance` | Maximum schedule amount | Not applicable |
| Total Amount | `TotalAmtTolerance` | Maximum total amount | Maximum total amount |
| Consumed Percentage | `QtyConsumedTolerance` | Consumed quantity | Not applicable |
| Maximum Consumed | `MaxQtyConTolerance` | Maximum consumed quantity | Not applicable |

### Natural-language resolution

Use the type-specific hold label as a synonym for its displayed tolerance row, not as a separate field. Resolve a create only with an explicit type; resolve an update against the type in a fresh export unless the requester asks to change it. If a phrase matches several rows or does not establish the type, ask for the row or CSV column before preparing a candidate. A phrase from the other type does not silently change the template type. Preview the interpreted type, row, CSV column, and value.

| Request wording | Resolution |
|---|---|
| “Create an AMOUNT BASED template; set Amount ordered to 5” | Ordered Percentage → `QuantityTolerance=5`; associated hold name is context, not a CSV field |
| “Create a QUANTITY BASED template; set Ordered quantity to 5 and Maximum ordered quantity to 10” | Ordered Percentage → `QuantityTolerance=5`; Maximum Ordered → `MaxQtyOrdTolerance=10` |
| “Update a known AMOUNT BASED template; set Amount received to 4” | Received Percentage → `QtyReceivedTolerance=4`; preserve type |
| “Set ordered to 5” | Ask whether Ordered Percentage or Maximum Ordered is intended; no candidate |
| “Set amount to 10” | Ask which of the applicable amount-based rows is intended; no candidate |
| “For this QUANTITY BASED template, set Amount ordered to 5” | Clarify whether a type change is requested; no silent type switch or candidate |
| “Create a template; set Maximum Received to 8” | Ask for QUANTITY BASED or AMOUNT BASED; row maps to `MaxQtyRecTolerance` for either type |
| “Create an AMOUNT BASED template; set Price Percentage to 2” | Reject the type-inapplicable `PriceTolerance` value; request a compatible design |

When changing from QUANTITY BASED to AMOUNT BASED, explicitly blank the four quantity-only fields and preserve the six amount-applicable values unless requested otherwise. The candidate must contain the explicitly requested or derived blanks. Do not rely on automatic clearing during import.

## Blank Description and Limits

Description and every applicable tolerance limit may be blank. Description and applicable limits are optional for both supported types. No minimum populated-limit count is required; preserve blanks rather than filling them with zero.

## Numeric Validation

Numeric validation applies to every applicable tolerance-limit field in both types. The ten package fields are `PriceTolerance`, `QuantityTolerance`, `QtyReceivedTolerance`, `MaxQtyOrdTolerance`, `MaxQtyRecTolerance`, `ShipAmtTolerance`, `RateAmtTolerance`, `TotalAmtTolerance`, `MaxQtyConTolerance`, and `QtyConsumedTolerance`. Four quantity-only fields are inapplicable to AMOUNT BASED. Reject nonnumeric input before building a candidate. The UI reports “The value is not a number” and “The value must be a number” for nonnumeric limits in both types. Its format hint does not establish a general CSV precision, scale, range, sign, or locale rule.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| TOLERANCE.VALIDATE_INPUT | step | 10 | validate_input | valid->TOLERANCE.ENFORCE_DESIGN;invalid->TOLERANCE.INPUT_BLOCKED | none | stop | Always |

## Dependent-clear normalization

For an explicit update to `ToleranceType=AMOUNT BASED`, include blank `PriceTolerance`, `ShipAmtTolerance`, `QtyConsumedTolerance` and `MaxQtyConTolerance` values during normalization, and disclose each derived clear with its prior value in the preview. Reject conflicting explicit nonblank inputs. Validate, serialize and reconcile the same effective values; a prepared ZIP must contain the agreed blanks and is never rewritten during validation. Preserve all unrelated fields and all omitted fields on unrelated updates. This is a source-backed type-switch consequence, not a create default or an import-side automatic clear.

## Candidate row integrity

Generated and uploaded candidate ZIPs must contain exactly one CSV row per requested `ToleranceName` target. Reject identical as well as conflicting repeated target rows before choosing or indexing a candidate row. Report the CSV member, exact target key and logical record numbers; never silently choose a first/last row, deduplicate, rewrite the upload or retry an import. A corrected artifact needs renewed validation and the normal candidate-bound approval.

This package-integrity rule is separate from create-name uniqueness. It does not require repairing unrelated historical duplicate names in the baseline and does not add a product-name uniqueness preflight to update requests. Preserve every unrelated baseline row and retain the existing target-matching and verification limitations.

## Duplicate Resolution Before Candidate Approval

For duplicate source records or proposed candidate targets, show all source
references and each name/type/value row; ask whether to merge, explicitly
ignore/exclude identified records, or defer. If merge is selected, obtain the
final type and field-by-field value mapping first. Never pick first/last,
minimum/maximum, zero-over-blank or another precedence rule silently. Identical
rows also require a decision. Preserve the original source. Exclusion is scoped
to the proposed import and does not delete source or Fusion records.

Block the affected scope until its exact decision is recorded and a separate
revised one-row-per-name design/candidate passes validation. Generic package
approval does not resolve duplicates. Do not rewrite uploaded ZIPs or repair
unrelated baseline duplicates. See the task skill's Duplicate Records Require a
User Decision section for the available choices and execution boundary.
