# Manage Legal Addresses Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Target task export | Bind one fresh same-target, same-release, scope-complete address package and exact ASM/header shape for reference and duplicate checks only; never replay its existing rows |
| 2 | Country territory | Resolve one enabled non-obsolete territory |
| 3 | Address style layout | Resolve the complete country layout and require every mandatory component |
| 4 | Optional time zone | Resolve an exact enabled code only when supplied |
| 5 | Existing legal address and CREATE carriers | Reuse one exact active natural key or establish zero-match candidacy; set XLE_CREATE_LE and generate a new collision-checked source reference for CREATE |
| 6 | Validation-status disclosure | Record that layout-complete import can persist N/DIRTY and does not prove geography canonicalization |
| 7 | Required formatted import value | Every new row has a nonblank LeFormattedAddress derived from reviewed inputs with every comma replaced by slash, as defined in ora_defaulting_rules.md |
| 8 | New-row-only package | The final upload contains exactly the reviewed new address rows; all companion CSVs retain only their exact headers, with zero existing rows in any member |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| la_package | Current address package shape | Yes | Always | Verify | Fresh target FSM export | verify_address_package_baseline | Current metadata and headers own package shape and collision scope | Re-export when stale, partial, failed, or wrong-target | Package shape and evidence fingerprint |
| la_territory | Country territory | Yes | Always | Lookup | Fusion territories LOV | resolve_address_territory | Country controls address layout | Supply a country name or two-letter code | Country and display receipt |
| la_layout | Country address style | Yes | Always | Lookup | Fusion address-style resources | resolve_address_style_layout | Mandatory components vary by country | Supply every mandatory component | AddressStyle and component set |
| la_timezone | Time zone | Conditional | TimezoneCode supplied | Lookup | Fusion time-zone LOV | resolve_address_timezone | Optional free text must resolve exactly | Correct the code or omit it | TimezoneCode |
| la_existing | Existing legal address | Yes | Before CREATE | Verify | Fresh target legal-address export | find_existing_legal_address | Prevent duplicate internal locations and permit the sole approved export natural-key reuse | Reuse one exact match or establish complete-scope zero match | Formatted natural key or create candidacy |
| la_status | Validation-status disclosure | Yes | New address | Verify | Preview plus re-export status | record_address_validation_status | Formatting and persistence do not prove geography validation | Accept the disclosed N/DIRTY state or use a future validation capability | Disclosure receipt |
| la_formatted_value | Nonblank normalized LeFormattedAddress | Yes | Every new row | Verify | Reviewed full address or country-layout components; ora_defaulting_rules.md |  | Blank or incorrectly transformed values are not valid create candidates | Complete the inputs and rederive the final value | Exact authored value and derivation receipt |
| la_create_scope | New addresses only | Yes | Final package | Verify | Baseline duplicate evidence and final per-member row inventory | verify_address_package_baseline | Baseline export is evidence, not data to replay | Exclude all existing rows; retain exact metadata and CSV headers | New-row count, identities, zero-existing-row and zero-companion-row proof |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Exact current evidence already exists | Continue |
| Lookup | A documented read-only Fusion resolver is required | Read-only lookup only |
| Verify | Current local export or preview evidence must be checked | Local verification only |
| Blocked | Required identity, shape, eligibility, uniqueness, or evidence is missing | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| LA.CHECK_DEPENDENCIES | decision | 30 | resolve_dependency | ready->LA.APPLY_DEFAULTS;blocked->LA.HANDLE_ERROR | LA.RESOLVE_REFERENCES | stop | After reference resolution |
