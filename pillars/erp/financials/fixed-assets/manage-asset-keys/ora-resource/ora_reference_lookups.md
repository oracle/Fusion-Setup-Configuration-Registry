# Reference Lookups

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_asset_key_system_control | A new Asset Key requires its configured structure | Target environment; application 140; KEY#; System Controls AssetStructureInstanceCode | Obtain current System Controls evidence through the declared shared export route. | Enterprise identity, exported AssetStructureInstanceCode, and numeric instance number only when required by the import contract | Require one enterprise/export match and its System Controls-selected AssetStructureInstanceCode. | AssetStructureInstanceCode and contract-required identity | Missing BOSS structure fields do not block export discovery; stop on incomplete, conflicting, or ambiguous identity/export evidence. |
| discover_asset_key_kff_structure | Current KEY# instance/segment metadata is needed | Target environment; selected System Controls AssetStructureInstanceCode; application 140; KEY# | Delegate to `erp.financials.fixed-assets.manage-fixed-assets-key-flexfields` with task `FA_MANAGE_FIXED_ASSETS_KEY_FLEXFIELDS`, application `140`, and flexfield `KEY#`. That skill obtains the current KFF task export through `shared.setup-export.task-level-export`. | Instance/structure identifiers, enabled state, delimiter, ColumnName, displayed order, prompts, requiredness, ValueSetCode and defaults | Reuse complete evidence from this procedure; require unique instance-to-structure and segment joins. | Current validated mapping and evidence | Match `AssetStructureInstanceCode` to exactly one enabled KEY# instance in the returned current KFF export. Auth failures, incomplete baseline, or ambiguous mapping block. A blank string StructureInstanceIdentifier alone does not block. |
| resolve_asset_key_kff_combination | An Asset Key code or labelled segments need mapping, including an undelimited value | Current System Controls-selected KEY# instance and supplied values | Map the current exported KEY# structure using discover_asset_key_kff_structure evidence | Delimiter, displayed sequence, ColumnName, requiredness, instance value sets and defaults | Map to the selected instance and physical Segment1 through Segment10; never select an alternative caller-supplied instance for creation. | Structure identity, mapped segments and validation findings | Stop on incomplete mapping or unresolved required inputs after discovery. Do not infer a delimiter or call FND_FLEX_KEYVAL directly; the supported import validates persistence. |
| resolve_asset_key_segment_values | One or more KEY# segment values are supplied | Resolved active structure; distinct ValueSetCode/value pairs; dependent parent when mapped | Delegate only to `erp.financials.fixed-assets.manage-fixed-assets-flexfield-value-sets` for its grouped REST workflow. This task must not call `core.fusion-api.apps-common.value-sets` directly or accept its direct result as evidence. The delegated workflow uses `REST-Framework-Version: 2` and follows only the `values` and `validationTable` links returned by its matched root response; it must not construct a child path from a value-set code, identifier, or other ID. | Value-set code, value, enabled state, effective range, parent mapping, query coverage | Compare every requested value against complete current grouped evidence. | Validated segment values and prerequisite findings | Stop as unverified on incomplete coverage; classify absent only after complete coverage. |
| resolve_asset_key_controlled_configurations | A decision or claim depends on controlled locking or combination-attribute behavior | Target environment; lookup type ORA_ERP_CONTROLLED_CONFIG; exact codes FA_36589233 and FA_37089538 | Shared Fixed Assets controlled-configurations read-only procedure through core.fusion-api.apps-common.lookups and the shared Fusion REST client | Per-code eligibility and redacted evidence returned by the shared procedure | Resolve both exact codes in one complete lookup-type retrieval; retain each code's result independently. | Per-code active_enabled, no_active_match, ambiguous, or unverified result | A verified no_active_match does not by itself block ordinary key creation. Stop feature-dependent decisions on ambiguous or unverified evidence; do not infer a code-specific behavior or change either flag. |
| resolve_existing_asset_key | Create, maintenance, duplicate validation or post-import reconciliation | Resolved structure and all ten normalized physical segments | Use complete paged BOSS `assetKeys` evidence through `core.fusion-api.rest-api-client` as the primary existing-key lookup. A complete exact BOSS no-match permits create readiness. Use a current same-target populated Asset Keys export through `shared.setup-export.task-level-export --data` only when BOSS is unavailable, incomplete, ambiguous, or lacks required fields. | BOSS rows, or `FA_ASSET_KEY.csv` rows with StructureInstanceCode, AssetKey, Segment1 through Segment10, enabled state, and dates | Use one complete evidence source only. Page BOSS completely when it succeeds; otherwise require a completed current FSM export and inspect every CSV row. Resolve exact records by structure plus all ten columns including blanks, then check alternate-key collisions by segments alone across structures. | Exact existing-record identity, lifecycle state, source type, and separate cross-structure collisions | A complete BOSS or FSM no-data result permits create only when no physical-combination collision exists. A template/spec package, failed export, incomplete page set, missing CSV member, or ambiguous records blocks. |

## Lookup Execution Rules

### Structure and Value-Set Scope

Use the rules below for System Controls and KFF task exports, physical-column
mapping, prerequisite continuation, defaults, and BOSS-based post-import
reconciliation.

Manage Asset Keys maintains KEY# combinations, not the KEY# structure or its
value-set entries. BOSS establishes enterprise identity, and the matching
current `FA_SYSTEM_CONTROL.csv` row supplies `AssetStructureInstanceCode`.
Delegate KEY# structure discovery to
`manage-fixed-assets-key-flexfields`, using
`FA_MANAGE_FIXED_ASSETS_KEY_FLEXFIELDS`. Resolve the exported code to one
enabled KEY# instance in its current KFF export before mapping values.
The System Controls-selected Asset Key flexfield structure determines the Asset
Key structure context; the exported code is a lookup
key, not that numeric instance number. Preserve verified `StructureInstanceCode`
for an FSM contract and resolve a numeric instance number separately only when
that contract exposes and requires it. A blank `StructureInstanceIdentifier` is
valid metadata for code-based resolution.

Segment count, labels, requiredness, value sets, dependent parents, and defaults
are deployed-structure facts, rather than fixed ten-segment requirements.

### Batch Lookup Scope

For a CSV or list of asset keys, resolve system-control and KEY# mappings once
per structure and environment.

Read the complete paginated BOSS `assetKeys` collection once for the unchanged
batch and index existing keys by structure plus all ten segments. When fallback
is required, obtain one current populated Asset Keys export through
`shared.setup-export.task-level-export --data` and use it for duplicate, update,
and existing-key evidence. Do not require this export after a complete exact
BOSS result. Retain the selected source type, process identity, environment,
and complete-coverage evidence with the batch. Do not combine partial BOSS
pages with FSM rows. A template or specification package never establishes
target state.

### Controlled Configuration Lookup

For task-supplied `FA_...` codes, use the shared lookup client against the
active-enabled `ORA_ERP_CONTROLLED_CONFIG` view. Retrieve one complete paginated
lookup-type result for the unchanged request, then compare each exact requested
code locally. Return `active_enabled`, `no_active_match`, `ambiguous`, or
`unverified` with redacted evidence. The consuming task owns feature
applicability and behavior; this lookup does not change configuration.

### Batch KFF Value Mapping

Resolve required value-set codes from current KEY# segments, then use the
[value-set batch workflow](../../manage-fixed-assets-flexfield-value-sets/ora-resource/ora_reference_lookups.md#lookup-execution-rules)
for distinct set codes and requested values by returned parent link. The
delegated workflow must send `REST-Framework-Version: 2`; it must not call the
generic value-set skill from this task or construct a child URL from a value-set
code, identifier, or other ID. Confirm filters, pagination, and visibility for
every mapped set and dependent parent before classifying a value as missing.

### Other Lookup Execution Rules

| Situation | What Happens |
|---|---|
| System Controls is resolved | Use BOSS only for enterprise identity. Match the current System Controls AssetStructureInstanceCode to exactly one enabled KEY# instance in the task export. Preserve StructureInstanceCode when the Asset Keys FSM contract uses that field. AssetStructureInstanceCode is a lookup key, not a numeric instance number; do not substitute StructureInstanceIdentifier or StructureInstanceId. Require a verified numeric instance separately only when the selected import contract requires it. Do not require AssetKeyFlexStructure in BOSS or treat a blank optional string identifier as missing configuration. |
| BOSS Asset Key read fails | After the REST client's permitted authentication refresh, do not retry the BOSS endpoint. Use exactly one current `FA_MANAGE_ASSET_KEY` setup-data export as the duplicate-check fallback. Require a completed process for the same target environment and a readable `FA_ASSET_KEY.csv` with the full serialized combination fields; otherwise report the duplicate state as unverified and stop. |
| A concatenated key is supplied | Parse it only with the delimiter returned by resolve_asset_key_kff_combination. Do not infer or substitute a delimiter. |
| Complete combination validation is needed | Do not invoke FND_FLEX_KEYVAL directly. `core.data-loader` and its post-import flow own submission and any accepted or rejected combination outcome. This skill reports validation findings only and returns `validated_for_import`. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---:|---:|---|---|---|---|---|
| MAK.RESOLVE_REFERENCES | decision | 20 | reference_lookup | resolved->MAK.CHECK_DEPENDENCIES;unresolved_or_ambiguous->MAK.HANDLE_LOOKUP | MAK.VALIDATE_INPUT | stop | Obtain applicable current references after valid intake; record verified findings before dependency evaluation. |
| MAK.RESOLVE_OPERATION | decision | 35 | evaluate_result | create_new->MAK.APPLY_DEFAULTS;update_existing->MAK.APPLY_DEFAULTS;decision_required->MAK.HANDLE_OPERATION_DECISION | MAK.CHECK_DEPENDENCIES | stop | Compare requested operation with exact existing-key evidence. |
