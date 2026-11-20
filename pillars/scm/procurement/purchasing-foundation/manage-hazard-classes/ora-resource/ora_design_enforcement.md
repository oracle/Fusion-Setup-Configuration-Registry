# Hazard Class Design Enforcement

The approved authoring plan makes the submitted fields the local authority for
preservation checks. This package does not determine regulatory classification,
uniqueness, record existence, user privileges, or Data Loader registration. It
introduces no business-unit or UN-number prerequisite.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Preserve submitted data | Compare values, types, and field presence after applying the declared empty-date omission rule with the submitted business fields |
| 2 | Prepare local handoff | Proceed directly to Data Loader review after local checks; no operation branch or identity verification |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| After defaulting | Error | | Any submitted value or type changed, any omitted field filled, or any explicit null lost, including a supplied HazardClassId; omission of an empty CSV/XLSX InactiveDate cell is the sole allowed presence normalization | Restore original submitted values and field presence, then revalidate | No silent correction |
| Every row | Error | | An ID was fabricated, name/code inferred from a regulatory assumption, or the pillar assigned POST/PATCH or reinterpreted code as lookup-only data | Preserve supplied business values and defer identity and operation handling to Data Loader | No |
| Source contract incomplete | Error | | A required local rule has an unresolved contract or the compiled plan is not ready | Resolve the authoring gap and recompile; do not bypass readiness | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| HAZ.CHECK_DESIGN | decision | 30 | design_enforcement | valid->HAZ.HANDOFF;blocked->HAZ.HANDLE_ISSUES | HAZ.PRESERVE_VALUES | stop | Enforce local preservation policies and proceed to the single Data Loader handoff regardless of eventual operation |
