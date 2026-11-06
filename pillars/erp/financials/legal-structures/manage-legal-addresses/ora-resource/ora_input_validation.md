# Manage Legal Addresses Input Validation

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Country context | Country name or two-letter country code | Block before preview | Resolve one enabled, non-obsolete territory | Always | resolve_address_territory |
| Address identity | Every component whose resolved AddressStyleFormatLayout row has MandatoryFlag true; tested US scope requires Address1, City, State, PostalCode | Block before preview | Resolve the country address style and complete layout, then request each missing mandatory component | Always | resolve_address_style_layout |
| CSV CREATE carriers | CreatedByModule and OrigSystemReference | Block package preview | Write CreatedByModule as XLE_CREATE_LE and generate a new nonblank collision-checked FDoS-owned OrigSystemReference | New legal address | find_existing_legal_address |
| Authored legal-address value | Nonblank LeFormattedAddress or complete reviewed inputs from which it can be deterministically derived | Block package preview if outgoing value is blank or ambiguous | Apply the construction and comma-to-slash contract in ora_defaulting_rules.md; validate the reparsed final CSV | Every new legal address |  |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Country input is present | Continue only with one enabled non-obsolete territory and one complete address-style layout | Validate the exact mandatory component set | resolve_address_style_layout |
| TimezoneCode is supplied | Continue only with one exact enabled code | Retain the resolved code or omit the optional value | resolve_address_timezone |
| A complete address candidate is ready | Existing Match on one exact active internal natural key; Create Candidate on zero matches after scope-complete export; ambiguity on many | Reuse the exact natural key, generate a new row, or block respectively | find_existing_legal_address |
| Address layout is complete but no dependent-geography validation is performed | Accept with warning | Disclose ValidatedFlag N and GeometryStatusCode DIRTY without claiming canonicalization | record_address_validation_status |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Required country and layout components | Reject blank-after-trim Country or any component marked mandatory by the complete resolved layout | Always | resolve_address_style_layout |
| Time zone | Reject a supplied value longer than 50 or not exactly resolved to one enabled TimezoneCode | TimezoneCode is supplied | resolve_address_timezone |
| Address component ownership | Preserve each supplied value in its declared component; never copy State, Province, County, City, or PostalCode into a different component and never apply a universal postal expression | Always |  |
| Address validation state | Accept ValidatedFlag N and GeometryStatusCode DIRTY after layout validation; describe the candidate as unvalidated and claim persistence only after log and exact-row verification | New address | record_address_validation_status |
| LeFormattedAddress | Reject blank-after-trim output, remaining commas, or a value that differs from the deterministic derivation in ora_defaulting_rules.md; preserve spaces when replacing commas in a supplied full line | Every new row and final package |  |
| New-row-only upload scope | Require exactly the reviewed, unique, zero-existing-match new addresses in XLE_LE_LEGAL_ADDRESS.csv and zero data rows in every companion CSV; reject every existing or unrelated row | Before preview and on the final immutable archive | find_existing_legal_address |
| CREATE source values | Reject copied LocationId, audit, ESS, object-version, formatted-display, login, CreatedByModule, or OrigSystemReference values; the two required carriers follow the documented workflow rules | New address |  |
| DFF and localization | Keep DFF families null unless an active runtime context exposes or requires them; then validate that exact context and segments | A DFF context or value is supplied |  |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| LA.VALIDATE_INPUT | step | 10 | validate_input | valid->LA.RESOLVE_REFERENCES;invalid->LA.HANDLE_ERROR | none | stop | Before any lookup or package preview |
