# Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---:|---|---|
| 1 | Structure ownership | Use the System Controls KEY# structure; do not define structures or value-set entries in this task. |
| 2 | Combination validation | Resolve the deployed structure and validate all supplied values before preview; use the supported FSM/UI process as the authority for complete-combination acceptance. |
| 3 | Lifecycle boundary | Create a new key for changed segments. After an explicit Update decision, a persisted key may change only EnabledFlag, StartDateActive, and EndDateActive. |
| 4 | Deletion boundary | Do not delete a persisted key; disable it instead. |
| 5 | Archive preparation | Verify the completed task-rule outcomes, then obtain and inspect the FSM template/spec package. |
| 6 | Import approval | Preview the exact FSM artifact and use core.data-loader's approval workflow immediately before submission. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Create or validate an Asset Key | Error | resolve_asset_key_system_control | Structure or physical mapping is unresolved, deployed requiredness is unsatisfied, a mapped segment exceeds 30 characters, or a value is invalid, disabled, ineffective, ambiguous or parent-unmapped. | Use current KEY# metadata and complete only confirmed prerequisite changes. The supported FSM process remains authoritative for full-combination acceptance. | Yes, before preview. |
| Create or validate an Asset Key | Error | discover_asset_key_kff_structure | Structure or physical mapping is unresolved, deployed requiredness is unsatisfied, a mapped segment exceeds 30 characters, or a value is invalid, disabled, ineffective, ambiguous or parent-unmapped. | Use current KEY# metadata and complete only confirmed prerequisite changes. The supported FSM process remains authoritative for full-combination acceptance. | Yes, before preview. |
| Create or validate an Asset Key | Error | resolve_asset_key_kff_combination | Structure or physical mapping is unresolved, deployed requiredness is unsatisfied, a mapped segment exceeds 30 characters, or a value is invalid, disabled, ineffective, ambiguous or parent-unmapped. | Use current KEY# metadata and complete only confirmed prerequisite changes. The supported FSM process remains authoritative for full-combination acceptance. | Yes, before preview. |
| Create or validate an Asset Key | Error | resolve_asset_key_segment_values | Structure or physical mapping is unresolved, deployed requiredness is unsatisfied, a mapped segment exceeds 30 characters, or a value is invalid, disabled, ineffective, ambiguous or parent-unmapped. | Use current KEY# metadata and complete only confirmed prerequisite changes. The supported FSM process remains authoritative for full-combination acceptance. | Yes, before preview. |
| Create an Asset Key | Error | resolve_existing_asset_key | An exact record exists in the selected structure, or all ten segment positions collide in another structure. | Report exact-record and cross-structure collision findings separately; do not update another structure's record as if it were the requested key. Treat duplicate checks as preflight only because runtime locking is configuration-dependent. | Yes, before preview. |
| Create request matches an existing exact Asset Key | Error | resolve_existing_asset_key | The requested operation is Create and an exact record exists in the selected structure. | Stop and request an explicit update-versus-new decision. Do not prepare an artifact or reinterpret the request as maintenance. | No |
| Update persisted segments or CodeCombinationId | Error | resolve_existing_asset_key | A persisted identity or segment changes. | Create another key for the new combination. | No in-place change. |
| Update persisted lifecycle fields | Error | resolve_existing_asset_key | The requested update changes any field other than EnabledFlag, StartDateActive, or EndDateActive. | Stop; preserve identity, segment, summary, audit, and combination fields. | No |
| Delete a persisted key | Error | resolve_existing_asset_key | Any persisted key is targeted for deletion, regardless of apparent usage. | Disable the key. | No physical deletion. |
| Validate a key artifact through Data Loader Task Hook | Error | resolve_asset_key_system_control | The exact immutable artifact, target identity or current applicable validation evidence is missing, changed or incomplete. | Revalidate the actual artifact and all required fields from its same-task contract. Approval follows successful read-only validation in Data Loader. | Yes, before approval feedback. |
| Validate a key artifact through Data Loader Task Hook | Error | discover_asset_key_kff_structure | The exact immutable artifact, target identity or current applicable validation evidence is missing, changed or incomplete. | Revalidate the actual artifact and all required fields from its same-task contract. Approval follows successful read-only validation in Data Loader. | Yes, before approval feedback. |
| Validate a key artifact through Data Loader Task Hook | Error | resolve_asset_key_kff_combination | The exact immutable artifact, target identity or current applicable validation evidence is missing, changed or incomplete. | Revalidate the actual artifact and all required fields from its same-task contract. Approval follows successful read-only validation in Data Loader. | Yes, before approval feedback. |
| Validate a key artifact through Data Loader Task Hook | Error | resolve_asset_key_segment_values | The exact immutable artifact, target identity or current applicable validation evidence is missing, changed or incomplete. | Revalidate the actual artifact and all required fields from its same-task contract. Approval follows successful read-only validation in Data Loader. | Yes, before approval feedback. |
| A decision relies on controlled locking or combination-attribute behavior | Error | resolve_asset_key_controlled_configurations | The relevant flag is ambiguous or unverified, or its effect is not supported by the consuming rule. | Resolve exact lookup-code eligibility through the shared Fixed Assets procedure before relying on that behavior. A verified no_active_match alone does not invalidate the key. | Yes, before the dependent decision. |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_asset_key_system_control | Create or validate a key | Current enterprise identity and AssetStructureInstanceCode | ora_reference_lookups.md |
| discover_asset_key_kff_structure | Create or validate a key | One enabled KEY# structure and its current metadata | ora_reference_lookups.md |
| resolve_asset_key_kff_combination | Create or validate a key | Valid physical mapping and normalized segments | ora_reference_lookups.md |
| resolve_asset_key_segment_values | Create or validate a key | Exact values and dependent parent mappings | ora_reference_lookups.md |
| resolve_existing_asset_key | Create, update, or deletion | Existing key identity and lifecycle state | ora_reference_lookups.md |
| resolve_asset_key_controlled_configurations | A decision relies on controlled locking or combination-attribute behavior | Independent eligibility results for FA_36589233 and FA_37089538 | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---:|---:|---|---|---|---|---|
| MAK.ENFORCE_DESIGN | decision | 50 | design_enforcement | pass->MAK.PREPARE_ARCHIVE;blocked->MAK.HANDLE_DESIGN | MAK.APPLY_DEFAULTS | stop | Validation, dependencies, and defaults are complete. |
