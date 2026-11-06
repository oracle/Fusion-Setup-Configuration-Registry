# Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---:|---|---|
| 1 | Asset Location lifecycle | Create only after the system-control and KFF checks pass; do not physically delete an existing location. After an explicit Update decision, a persisted location may change only EnabledFlag, StartDateActive, and EndDateActive. |
| 2 | Asset Location change boundary | Keep segments 1 through 7 unchanged after insert; use Enabled to retire a location. |
| 3 | Mapping maintenance boundary | Do not use the Manage Asset Locations mapped-HR-location dialog for mapping maintenance; it is display-only. The supported Advanced import may create a verified new mapping, but this skill does not update or delete an existing FA_LOCATION_MAPPINGS row. |
| 4 | Bulk import route | core.data-loader owns import; a selected mapping adapter must preserve the ADFdi/Rapid Start ADVANCED contract. Source-format guidance never authorizes bypassing Data Loader. |
| 5 | Archive preparation | Verify the completed task-rule outcomes and batch-current DFF-definition evidence, then obtain and inspect the FSM template/spec package. |
| 6 | Import approval | Preview the exact import artifact and obtain approval immediately before the selected import executor submits it. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Create or validate an Asset Location | Error | resolve_location_system_control | Structure or physical mapping is unresolved, deployed requiredness is unsatisfied, a mapped segment exceeds 30 characters, or a LOC# component is missing, disabled, ineffective, ambiguous or parent-unmapped. | Use current LOC# metadata, including required hidden segments; do not assume segment requirements from a pre-existing structure instance. Honor existing authorization for confirmed prerequisite changes. | Yes, before preview. |
| Create or validate an Asset Location | Error | discover_location_kff_structure | Structure or physical mapping is unresolved, deployed requiredness is unsatisfied, a mapped segment exceeds 30 characters, or a LOC# component is missing, disabled, ineffective, ambiguous or parent-unmapped. | Use current LOC# metadata, including required hidden segments; do not assume segment requirements from a pre-existing structure instance. Honor existing authorization for confirmed prerequisite changes. | Yes, before preview. |
| Create or validate an Asset Location | Error | resolve_location_kff_combination | Structure or physical mapping is unresolved, deployed requiredness is unsatisfied, a mapped segment exceeds 30 characters, or a LOC# component is missing, disabled, ineffective, ambiguous or parent-unmapped. | Use current LOC# metadata, including required hidden segments; do not assume segment requirements from a pre-existing structure instance. Honor existing authorization for confirmed prerequisite changes. | Yes, before preview. |
| Create or validate an Asset Location | Error | resolve_location_segment_values | Structure or physical mapping is unresolved, deployed requiredness is unsatisfied, a mapped segment exceeds 30 characters, or a LOC# component is missing, disabled, ineffective, ambiguous or parent-unmapped. | Use current LOC# metadata, including required hidden segments; do not assume segment requirements from a pre-existing structure instance. Honor existing authorization for confirmed prerequisite changes. | Yes, before preview. |
| Create Asset Location | Error | resolve_location_dff_segments | A required enabled FA_LOCATIONS global or selected-context DFF segment is blank, ambiguous or invalid, or its export does not belong to this immutable batch and environment. | Supply the exact value from the current batch's DFF contract; a blank context never waives required global segments. | Yes, before preview. |
| Create Asset Location | Error | resolve_existing_asset_location | A structure-plus-seven-physical-segment combination already exists. | Report the existing identity and enabled/date state; do not prepare a duplicate create. | Yes, before preview. |
| Create request matches an existing exact Asset Location | Error | resolve_existing_asset_location | The requested operation is Create and an exact record exists in the selected structure. | Stop and request an explicit update-versus-new decision. Do not prepare an artifact or reinterpret the request as maintenance. | No. |
| A DFF context is supplied | Error | resolve_location_dff_context | The context is absent, disabled, ambiguous or not for FA_LOCATIONS application 140 in the current batch export. | Correct the exact context and affected values using current evidence. | Yes, before preview. |
| Customer Site Number is supplied for a mapping import | Error | resolve_tca_customer_site | No approved callable customer-site resolver contract exists. | Remove Customer Site Number to use the HR branch, or provide an approved resolver contract. | No. |
| Repeated source location for one parent mapping type occurs in a mapping import | Error | resolve_existing_location_mapping | Duplicate source mappings remain in the prepared artifact. | Apply the supported duplicate-discard behavior and report retained and excluded row counts before artifact review. | Yes, before preview. |
| Validate a location artifact through Data Loader Task Hook | Error | resolve_location_system_control | The exact immutable artifact, target identity or applicable current evidence is missing, changed or incomplete. | Revalidate the actual artifact, including all required fields from its same-task contract; approval follows successful read-only validation. | Yes, before approval feedback. |
| Validate a location artifact through Data Loader Task Hook | Error | discover_location_kff_structure | The exact immutable artifact, target identity or applicable current evidence is missing, changed or incomplete. | Revalidate the actual artifact, including all required fields from its same-task contract; approval follows successful read-only validation. | Yes, before approval feedback. |
| Validate a location artifact through Data Loader Task Hook | Error | resolve_location_kff_combination | The exact immutable artifact, target identity or applicable current evidence is missing, changed or incomplete. | Revalidate the actual artifact, including all required fields from its same-task contract; approval follows successful read-only validation. | Yes, before approval feedback. |
| Validate a location artifact through Data Loader Task Hook | Error | resolve_location_segment_values | The exact immutable artifact, target identity or applicable current evidence is missing, changed or incomplete. | Revalidate the actual artifact, including all required fields from its same-task contract; approval follows successful read-only validation. | Yes, before approval feedback. |
| Delete existing Asset Location | Error | resolve_existing_asset_location | Existing persisted row is targeted for deletion. | Disable the location instead. | No physical deletion. |
| Update location segments | Error | resolve_existing_asset_location | Existing row has a change to any of Segment1 through Segment7. | Create a new valid location or retain the original segments. | No in-place segment change. |
| Update persisted lifecycle fields | Error | resolve_existing_asset_location | The requested update changes any field other than EnabledFlag, StartDateActive, or EndDateActive. | Stop; preserve identity, segment, summary, audit, DFF, and combination fields. | No. |
| Import FA_LOCATION_MAPPINGS | Error | resolve_enabled_asset_location | Parent is disabled, reference is unresolved, or execution mode is not ADVANCED. | Enable and resolve prerequisites, then stage a corrected CSV. | Yes, before preview. |
| Mapping import through page popup | Error | | Request attempts page-based maintenance. | Use the supported ADFdi/Rapid Start flow. | No. |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_location_system_control | Create or validate an Asset Location | Current enterprise identity and LocStructureInstanceCode | ora_reference_lookups.md |
| discover_location_kff_structure | Create or validate an Asset Location | One enabled LOC# structure and its current metadata | ora_reference_lookups.md |
| resolve_location_kff_combination | Asset Location create or validation | Valid combination and segment state | ora_reference_lookups.md |
| resolve_location_segment_values | Asset Location create or validation | Exact value-set/value pairs and dependent parent mapping when applicable | ora_reference_lookups.md |
| resolve_location_dff_segments | Asset Location create | Required global/context DFF field map and values | ora_reference_lookups.md |
| resolve_existing_asset_location | Create, update, delete or post-import reconciliation | Existing identity, all seven physical segments and enabled/date state | ora_reference_lookups.md |
| resolve_location_dff_context | A DFF context is supplied | Exact enabled context in the current batch export | ora_reference_lookups.md |
| resolve_existing_location_mapping | Mapping duplicate validation or reconciliation | Serialized mapping identity and duplicate findings | ora_reference_lookups.md |
| resolve_enabled_asset_location | Mapping import | Parent enabled state | ora_reference_lookups.md |
| resolve_tca_customer_site | Customer Site Number is supplied | An approved callable customer-site contract; its documented absence blocks this branch | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---:|---:|---|---|---|---|---|
| MAL.ENFORCE_DESIGN | decision | 50 | design_enforcement | pass->MAL.PREPARE_ARCHIVE;blocked->MAL.HANDLE_DESIGN | MAL.APPLY_DEFAULTS | stop | Validation, dependencies, and defaults are complete. |
