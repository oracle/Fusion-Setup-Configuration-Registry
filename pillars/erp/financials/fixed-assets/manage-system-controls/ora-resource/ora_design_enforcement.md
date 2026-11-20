# Manage System Controls: Design Enforcement

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Confirmed create path | Error | resolve_system_controls_dff_segments | Required DFF values are blank, any supplied value/context is invalid or unverified, or serialized values differ from the reviewed proposal | Resolve against the batch-current definition and actual import contract before approval | Yes, before ZIP creation |
| Before System Controls ZIP creation | Error | resolve_assets_flexfield_structures | Any requested structure is disabled, selected instance is disabled or ambiguous, newly deployed structure lacks parent-verified target context, any structure field is not populated from the selected enabled `StructureInstanceCode`, or Oldest Date Placed in Service is not serialized as `YYYY/MM/DD`. | Use the three selected enabled `StructureInstanceCode` values and serialize Oldest Date Placed in Service as `YYYY/MM/DD`. | Yes, before ZIP creation |
| Before System Controls ZIP creation | Error | resolve_system_controls_export_metadata | Any requested structure is disabled, selected instance is disabled or ambiguous, newly deployed structure lacks parent-verified target context, any structure field is not populated from the selected enabled `StructureInstanceCode`, or Oldest Date Placed in Service is not serialized as `YYYY/MM/DD`. | Use the three selected enabled `StructureInstanceCode` values and serialize Oldest Date Placed in Service as `YYYY/MM/DD`. | Yes, before ZIP creation |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_system_controls_dff_segments | Confirmed create path and final-artifact validation | Current definition, context, required-field map, validated values, and mappings | ora_reference_lookups.md |
| resolve_assets_flexfield_structures | Before System Controls ZIP creation | Current enabled structure-instance mappings for the same target | ora_reference_lookups.md |
| resolve_system_controls_export_metadata | Before System Controls ZIP creation | Current same-target System Controls package metadata | ora_reference_lookups.md |

## DFF Preview and Artifact Enforcement

Include applicable DFF business prompts and reviewed values in the Reference
Validation, Design, and Final ZIP previews. Keep physical columns and metadata
identifiers internal unless diagnostics are requested.

Before execution approval, validate the actual FA_SYSTEM_CONTROL.csv row
against its required-field map, approved context/values/conversions, current
headers, and serialization. Any mismatch blocks import.
These checks never introduce an update path for existing System Controls.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| SYS.ENFORCE_DESIGN | decision | 50 | design_enforcement | pass->SYS.IMPORT_GATE;blocked->SYS.HANDLE_DESIGN | SYS.APPLY_DEFAULTS | stop | Defaults and lookup results are available |
