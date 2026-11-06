# Manage System Controls: Design Enforcement

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Before System Controls ZIP creation | Error | resolve_assets_flexfield_structures | Any requested structure is disabled, selected instance is disabled or ambiguous, newly deployed structure lacks parent-verified target context, any structure field is not populated from the selected enabled `StructureInstanceCode`, or Oldest Date Placed in Service is not serialized as `YYYY/MM/DD`. | Use the three selected enabled `StructureInstanceCode` values and serialize Oldest Date Placed in Service as `YYYY/MM/DD`. | Yes, before ZIP creation |
| Before System Controls ZIP creation | Error | resolve_system_controls_export_metadata | Any requested structure is disabled, selected instance is disabled or ambiguous, newly deployed structure lacks parent-verified target context, any structure field is not populated from the selected enabled `StructureInstanceCode`, or Oldest Date Placed in Service is not serialized as `YYYY/MM/DD`. | Use the three selected enabled `StructureInstanceCode` values and serialize Oldest Date Placed in Service as `YYYY/MM/DD`. | Yes, before ZIP creation |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_assets_flexfield_structures | Before System Controls ZIP creation | Current enabled structure-instance mappings for the same target | ora_reference_lookups.md |
| resolve_system_controls_export_metadata | Before System Controls ZIP creation | Current same-target System Controls package metadata | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| SYS.ENFORCE_DESIGN | decision | 50 | design_enforcement | pass->SYS.IMPORT_GATE;blocked->SYS.HANDLE_DESIGN | SYS.APPLY_DEFAULTS | stop | Defaults and lookup results are available |
