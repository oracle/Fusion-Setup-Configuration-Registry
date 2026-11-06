# Manage Legal Addresses Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Territory and layout gate | One territory and complete address layout resolve; all mandatory components are present |
| 2 | Duplicate and source-carrier gate | No equivalent active internal address exists unless it is intentionally reused; CREATE carriers follow the proven contract |
| 3 | Validation-status gate | Preview explicitly states that N/DIRTY is accepted and is not geography validation or canonicalization |
| 4 | Required formatted import value | Every new row has nonblank LeFormattedAddress matching the deterministic comma-to-slash construction in ora_defaulting_rules.md |
| 5 | Package boundary | Preserve target ASM, CSV member hierarchy, exact header bytes/order, encoding and system-owned blanks; include only reviewed new address rows, with zero existing rows and header-only companion CSVs. This graph validates readiness; the task skill constructs the package and core.data-loader owns approval/upload/import |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Every candidate | Error | resolve_address_territory | Country is missing, inactive, obsolete, or ambiguous | Resolve one enabled territory | Yes |
| Every candidate | Error | resolve_address_style_layout | A mandatory layout component is blank or layout evidence is incomplete | Complete the exact country layout | Yes |
| Before CREATE | Error | find_existing_legal_address | Equivalent or multiple active internal addresses exist | Reuse the single match or resolve ambiguity | Yes |
| New layout-complete address | Warning | record_address_validation_status | Preview omits or misstates N/DIRTY semantics | State that persistence and formatting do not prove geography validation | Yes |
| Every CSV CREATE | Error | find_existing_legal_address | CreatedByModule is not XLE_CREATE_LE or OrigSystemReference is blank, copied, or collides | Apply the constant and generate a new FDoS-owned value | Yes |
| Every CSV CREATE | Error |  | LeFormattedAddress is blank, contains commas, or differs from the reviewed full-line transformation or component derivation | Apply ora_defaulting_rules.md and verify the exact final CSV value; generated displays remain blank | Yes |
| Final upload archive | Error | find_existing_legal_address | Any existing address, legal entity, establishment, registration, function, or other unrelated data row is included, or the new-row set differs from the reviewed candidate set | Use the baseline only for evidence; rebuild with new address rows only and header-only companion CSVs | Yes |
| Package preview | Error | verify_address_package_baseline | Current shape, hierarchy, header, null/system-field treatment, or evidence fingerprint is unproven | Refresh the target export and rerun the selected task SKILL.md local FSM package-preparation workflow | Yes |

## Resolved Scope Decisions

| ID | Status | Enforced Contract | Future Expansion Gate |
|---|---|---|---|
| LS-TBD-001 | Resolved | Permit a layout-complete address with ValidatedFlag N and GeometryStatusCode DIRTY; write XLE_CREATE_LE and a new collision-checked OrigSystemReference | Optional dependent-geography validation may be added later but is not a current blocker |
| LA-CREATE-SCOPE | Resolved | Create imports contain only new reviewed address rows and no existing data rows; preserve metadata and headers, not baseline data | Updates, migrations and replay require a separately defined workflow; never widen a create request to a full-baseline import |
| LA-FORMATTED-VALUE | Resolved | Every new row has nonblank comma-to-slash-normalized LeFormattedAddress; preserve the other input characters and spaces | System-generated output must be verified separately; upload normalization does not control display formatting |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_address_territory | Every candidate | Country code and display receipt | ora_reference_lookups.md |
| resolve_address_style_layout | Every candidate | AddressStyle and mandatory component set | ora_reference_lookups.md |
| find_existing_legal_address | Before CREATE | Existing natural key or complete-scope zero match | ora_reference_lookups.md |
| record_address_validation_status | Every new address | N/DIRTY disclosure receipt | ora_reference_lookups.md |
| verify_address_package_baseline | Before final-package readiness validation | Current package shape, hierarchy, headers, system-field treatment, baseline fingerprint, and exact new-row-only upload scope | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| LA.ENFORCE_DESIGN | decision | 50 | design_enforcement | passed->LA.PACKAGE_PREVIEW_GATE;blocked->LA.HANDLE_ERROR | LA.APPLY_DEFAULTS | stop | Before final-package readiness validation |
