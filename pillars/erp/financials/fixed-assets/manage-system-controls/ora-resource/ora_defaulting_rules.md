# Manage System Controls: Defaulting Rules

## Standard Defaults

| Field | Internal | Resolved Value | Applies When | User Override | Resolver |
|---|---|---|---|---|---|
| Flexfield structure fields | Yes | Use only the exact selected enabled target `StructureInstanceCode` values for Category, Location, and Asset Key. | Each requested structure and its selected matching instance are enabled and uniquely resolved. | No | resolve_assets_flexfield_structures |
| FSM package format | Yes | Use the skill's declared System Controls field mapping. Validate only the CSV member names, headers, field order, encoding, and XML contract against the current target export and metadata. Never copy or infer a new System Controls row from an existing row. | FSM CSV package preparation | No | resolve_system_controls_export_metadata |

## Default Disclosure

After user inputs are collected and before package preparation, list every
business default and resolved value in the user-facing proposal. Package-format
rules remain internal; all new-row values come from validated inputs and
declared task defaults, not from an existing exported row. User overrides are
allowed only where the defaulting table permits them.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| SYS.APPLY_DEFAULTS | step | 40 | apply_default | applied->SYS.ENFORCE_DESIGN;blocked->SYS.HANDLE_DEPENDENCY | SYS.PRESENT_REFERENCE_PREVIEW | stop | Confirmed create path and export metadata are resolved |
