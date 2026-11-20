# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 10 | Exact same-task export contract | Bind AP_TOLERANCE_TEMPLATE.csv and metadata to AP_MANAGE_INVOICE_TOLERANCES before building a candidate |
| 15 | Name uniqueness scan | Build the set of existing ToleranceName values in a fresh current export across both types; reject a proposed create name in that set or repeated among new creates |
| 30 | Supported type code | Use either of the two exact supported FSM import codes; Fusion validates at runtime |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| same_task_package | Exact task CSV and metadata | Yes | Always | Satisfied only for matching task identity and ordered schema | Same-task template/current export | | Prevent cross-task or drifted import packages | Re-export AP_MANAGE_INVOICE_TOLERANCES if package identity differs | AP_TOLERANCE_TEMPLATE.csv; ASM_SETUP_CSV_METADATA.xml |
| unique_create_name | New tolerance name | Conditional | Create | Satisfied only for a new create when its exact name is absent from a fresh full current export and unique among newly requested create rows | Fresh current data export and newly requested create rows | | UI raises AP-810297 for a name already present | Provide a different name if matched; do not infer case/space equivalence | ToleranceName |
| type_code | Supported ToleranceType code | Conditional | Create; update when type supplied | Satisfied by local validation of either exact accepted code; no lookup GET call | Same-task CSV and confirmed import behavior | | Only the two supported codes may be submitted; verify any import result | Preserve the exact code and monitor actual loader diagnostics | ToleranceType |

## Dependency Classification

| Result Category | When Used | Can Continue? |
|---|---|---|
| Satisfied | Package identity is valid; a create has one supported type code and a unique new name; an update keeps its current type or supplies one supported replacement code | Only governed central preview may continue |
| Blocked | Any required identity is unavailable or the supplied type code is outside the two-code domain | No; stop before live import |
