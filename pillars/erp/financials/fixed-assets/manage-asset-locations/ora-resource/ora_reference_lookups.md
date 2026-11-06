# Reference Lookups

## Lookup Operations

Resolve the LOC# structure and validate supplied values for every required
physical segment first. Then run `resolve_location_dff_segments` for Asset
Location creation. Its definition export identifies required extra columns;
missing required input ends input validation before value-set lookup or
prerequisite preparation.

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_location_system_control | A new location requires its configured structure | Target environment; application 140; LOC#; System Controls LocStructureInstanceCode | Obtain current System Controls evidence through the declared shared export route. Delegate LOC# discovery to `erp.financials.fixed-assets.manage-fixed-assets-key-flexfields`. | Enterprise identity, exported instance code and numeric instance number only when required by the import contract | Require one enterprise/export match and its System Controls-selected enabled LOC# instance. | LocStructureInstanceCode and contract-required identity | Missing BOSS structure fields do not block export discovery; stop on incomplete, conflicting or ambiguous identity/export evidence. |
| discover_location_kff_structure | Current LOC# instance/segment metadata is needed | Target environment; selected System Controls instance; application 140; LOC# | Delegate to `erp.financials.fixed-assets.manage-fixed-assets-key-flexfields` with task `FA_MANAGE_FIXED_ASSETS_KEY_FLEXFIELDS`, application `140`, and flexfield `LOC#`. That skill obtains the current KFF task export through `shared.setup-export.task-level-export`. | Instance/structure identifiers, enabled state, delimiter, ColumnName, displayed order, prompts, requiredness, ValueSetCode and defaults | Reuse complete evidence from this procedure; require unique instance-to-structure and segment joins. | Current validated mapping and evidence | Match `LocStructureInstanceCode` to exactly one enabled LOC# instance in the returned current KFF export. Auth failures, incomplete baseline, or ambiguous mapping block. A blank string StructureInstanceIdentifier alone does not block. |
| resolve_location_kff_combination | A location code or labelled segments need mapping, including an undelimited value | Current System Controls-selected LOC# instance and supplied values | Map the current exported KFF structure using discover_location_kff_structure evidence | Delimiter, displayed sequence, ColumnName, requiredness, instance value sets and defaults | Map to the selected instance and physical Segment1 through Segment7; never select an alternative caller-supplied instance for creation. | Structure identity, mapped segments and validation findings | Stop on incomplete mapping or unresolved required inputs after discovery. Do not infer a delimiter or call FND_FLEX_KEYVAL directly; the supported import validates persistence. |
| resolve_location_segment_values | Once per batch after the batch-current DFF required-input check passes | Distinct values grouped by exact set and dependent parent | Delegate only to `erp.financials.fixed-assets.manage-fixed-assets-flexfield-value-sets` for its grouped REST workflow. This task must not call `core.fusion-api.apps-common.value-sets` directly or accept its direct result as evidence. The delegated workflow uses `REST-Framework-Version: 2` and follows only the `values` and `validationTable` links returned by its matched root response; it must not construct a child path from a value-set code, identifier, or other ID. | REST definitions, values, eligibility, parents and query coverage | Compare every requested key locally against complete covered data | Grouped findings with affected records | Classify absent only after effective exact filters, complete pagination and verified visibility. Missing coverage or required fields remains unverified. |
| resolve_location_dff_segments | For each immutable Asset Location batch, after LOC# structure and required segment input validation, before value-set lookup or prerequisite preparation | Immutable batch identity, target environment, one new same-environment Manage Fixed Assets Descriptive Flexfields export, and supplied DFF values | Obtain one completed `FA_MANAGE_FIXED_ASSETS_DESCRIPTIVE_FLEXFILEDS` metadata export through `core.fusion-api.apps-common.descriptive-flexfields`, following the DFF handoff in [Batch Import Preparation](ora_dependency_readiness.md#batch-import-preparation), after batch membership is final. Read global rows from `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_GLOBAL_SEGMENT.csv` where DescriptiveFlexfieldCode=`FA_LOCATIONS`, ApplicationId=`140`, EnabledFlag=`Y`, and RequiredFlag=`Y`; if a context is selected, also read matching rows from `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv` where ContextCode is exact, EnabledFlag=`Y`, and RequiredFlag=`Y`. Record the process identity, target environment, and immutable batch identity. | Export process identity, target environment, batch identity, ColumnName, SegmentCode, Prompt, RequiredFlag, EnabledFlag, ValueSetCode, DisplayType, and context | One completed export matches the target environment and immutable batch. Every required global row and every required selected-context row has one nonblank supplied value mapped by unique current ColumnName, SegmentCode, or Prompt; value-set contract checks follow this required-input gate. | Batch-current required DFF field map and supplied FA_LOCATION.csv attribute values | Stop when the export is absent, belongs to another target/batch, a required row has no value, or input maps ambiguously. Never use an export from a prior batch, cached segment list, example prompt, or hardcoded DFF segment. A blank `ATTRIBUTE_CATEGORY_CODE` omits only context-sensitive rows, never global rows. |
| resolve_location_dff_context | A DFF context is supplied | Current-request DFF export plus ATTRIBUTE_CATEGORY_CODE or DFF context name | Read `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv` from the same fresh `FA_MANAGE_FIXED_ASSETS_DESCRIPTIVE_FLEXFILEDS` export used by resolve_location_dff_segments; match DescriptiveFlexfieldCode=`FA_LOCATIONS`, ApplicationId=`140` | ContextCode, Name, EnabledFlag | Trim outer whitespace. First require one exact ContextCode match to ATTRIBUTE_CATEGORY_CODE; if none exists, require one exact Name match. Only EnabledFlag Y contexts are valid. | ATTRIBUTE_CATEGORY_CODE as the resolved ContextCode | Stop on no match, disabled context, many matches, or DFF export evidence that is not current for this request. Do not guess or choose the first context. |
| resolve_existing_asset_location | Location creation, search, or mapping import is requested | Resolved LOC# structure and Segment1 through Segment7 values | Use complete paged BOSS `assetLocations` evidence through `core.fusion-api.rest-api-client` as the primary existing-location lookup. A complete exact BOSS no-match permits create readiness. Use a current same-target populated Asset Locations export through `shared.setup-export.task-level-export --data` only when BOSS is unavailable, incomplete, ambiguous, or lacks required fields. | BOSS rows, or exported Asset Location CSV rows with StructureInstanceCode, Location, Segment1 through Segment7, EnabledFlag, StartDateActive, and EndDateActive | Use one complete evidence source only. Page BOSS completely when it succeeds; otherwise require a completed current FSM export and inspect every Asset Location row. Match one row on StructureInstanceCode and every supplied Segment1 through Segment7 value, treating unused segments as blank. | Existing location identity, enabled state, create/update readiness, and source type | A complete BOSS or FSM no-data result permits create readiness. More than one exact match, conflicting rows, incomplete export, or missing serialized fields blocks the work. |
| resolve_enabled_asset_location | Mapping import is requested | Exact resolved Asset Location row from resolve_existing_asset_location | The complete BOSS or FSM fallback result returned by `resolve_existing_asset_location` | EnabledFlag from the exact resolved Asset Location result | Require one exact parent Asset Location whose EnabledFlag is Y. | Parent Asset Location identity and enabled state | Stop and report Enable Location to assign location mapping when no exact enabled parent exists. |
| resolve_hr_location_reference | HR mapping import is requested | HR Location Code and HR Set Code | GET /hcmRestApi/resources/11.13.18.05/locationsV2 with fields=LocationId,LocationCode,SetCode,EffectiveStartDate,EffectiveEndDate, onlyData=true, and an exact LocationCode plus SetCode query | LocationId, LocationCode, SetCode, EffectiveStartDate, EffectiveEndDate | Require exactly one row whose LocationCode and SetCode exactly equal the supplied values and whose effective range includes TRUNC(SYSDATE). | SOURCE_LOCATION_ID | Reject the row with FA_INVALID_HRCOMBINATION on zero, multiple, or ineffective matches. |
| resolve_tca_mapping_feature | Customer Site Number is supplied | Target environment; lookup type ORA_ERP_CONTROLLED_CONFIG; exact code FA_38101956 | This skill's read-only controlled-configuration procedure through core.fusion-api.apps-common.lookups and the shared Fusion REST client | Per-code eligibility and redacted evidence returned by this procedure | Read the exact feature result for diagnostics only. The result cannot enable a TCA mapping while no approved customer-site resolver contract exists. | Diagnostic feature status | Do not create a TCA mapping regardless of feature status. |
| resolve_tca_customer_site | Customer Site Number is supplied | Customer Site Number | No approved callable customer-site lookup contract exists. Do not infer an endpoint or resolve an identity. | None | Blocked | None | Stop and report the missing approved resolver contract. |
| resolve_existing_location_mapping | Mapping import is requested | Exact Asset Location structure/location, HR Location Code and Set Code, mapping type, and Customer Site Number when supplied | Current same-environment FA_MANAGE_FIXED_ASSET_LOCATION export through shared.setup-export.task-level-export | Exported Asset Location structure code and location value, HRLocationCode, HRSetCode, EnabledFlag, LocationMappingTypeCode, PartySiteNumber, and PartySiteId from ORA_FA_ASSET_LOCATION_TO_HR_LOCATION_MAPPING.csv | Match the complete serialized mapping business key. Zero rows is create readiness; one row is existing-mapping state; more than one row or conflicting export rows blocks the work. | Existing-mapping state and exported mapping business key | Do not fabricate LOCATION_MAPPING_ID: that field is not present in ORA_FA_ASSET_LOCATION_TO_HR_LOCATION_MAPPING.csv. Existing-mapping maintenance is unsupported in this skill; stop and report the mapping as already existing. |

## Lookup Execution Rules

### Structure and Value-Set Scope

Use the rules below for System Controls and KFF task exports, physical-column
mapping, prerequisite continuation, defaults, and BOSS-based post-import
reconciliation.

Manage Asset Locations maintains LOC# combinations, not the LOC# structure or
its value-set entries. BOSS establishes enterprise identity, and the matching
current `FA_SYSTEM_CONTROL.csv` row supplies `LocStructureInstanceCode`.
Delegate LOC# structure discovery to
`manage-fixed-assets-key-flexfields`, using
`FA_MANAGE_FIXED_ASSETS_KEY_FLEXFIELDS`. Resolve the exported code to one
enabled LOC# instance in its current KFF export before mapping values.
The System Controls-selected Asset Location flexfield structure determines the
Asset Location structure context; the exported code is a lookup key, not a
numeric instance number. Preserve verified `StructureInstanceCode` for an FSM
contract and resolve a numeric instance separately only when that contract
exposes and requires it. A blank `StructureInstanceIdentifier` is valid
metadata for code-based resolution.

Segment count, labels, requiredness, value sets, dependent parents, and defaults
are deployed-structure facts, rather than fixed seven-segment requirements.

### Batch Lookup Scope

For a CSV or list of locations, resolve system-control and LOC# mappings once
per structure and environment.

Read the complete paginated BOSS `assetLocations` collection once for the
unchanged batch and index existing locations by structure plus all seven
segments. When fallback is required, obtain one current populated Asset
Locations export through `shared.setup-export.task-level-export --data` and use
it for location duplicate, update, enabled-parent, and existing-location
evidence. Do not require this export after a complete exact BOSS result.
Retain the selected source type, process identity, environment, and
complete-coverage evidence with the batch. Do not combine partial BOSS pages
with FSM rows. A template or specification package cannot establish target
state. For mapping imports, use the populated task export's mapping rows only
for the mapping business key.

### DFF Metadata Export

For each immutable Asset Location import batch, request one new same-environment
DFF metadata export through [Apps Common Descriptive Flexfields](../../../../../../core/fusion-api/apps-common/descriptive-flexfields/SKILL.md).
Use the **Manage Fixed Assets Descriptive Flexfields** task
(`FA_MANAGE_FIXED_ASSETS_DESCRIPTIVE_FLEXFILEDS`) in offering `Financials` and
functional area `Fixed Assets` (`FIN_FIXED_ASSETS_DEPLOYED`), with its task
sequence resolved from the authoritative catalog. Request current setup data,
not a template. The generic skill owns export, polling, download, and
persistence; retain its ZIP reference, `ProcessId`, outcome, diagnostics, batch
identity, and target environment.

Use the completed export to derive the `FA_LOCATIONS` DFF definition. Inspect
global and selected-context rows, mapping only by a unique current `ColumnName`,
`SegmentCode`, or Prompt. The export is evidence only for its unchanged batch;
when batch membership or target environment changes, obtain a new export.

### Controlled Configuration Lookup

For task-supplied `FA_...` codes, use the shared lookup client against the
active-enabled `ORA_ERP_CONTROLLED_CONFIG` view. Retrieve one complete paginated
lookup-type result for the unchanged request, then compare each exact requested
code locally. Return `active_enabled`, `no_active_match`, `ambiguous`, or
`unverified` with redacted evidence. The consuming task owns feature
applicability and behavior; this lookup does not change configuration.

### Batch KFF Value Mapping

Retain environment, resolved structure and segment mappings, business date,
source fingerprint and current grouped value-set evidence identity. Map each enabled segment
to its exact exported ValueSetCode and RequiredFlag. Use dependent parent mappings
only when the exported definition declares them. Preserve exact strings and pad
unused segments only after structure validation.

Follow [the value-set batch workflow](../../manage-fixed-assets-flexfield-value-sets/ora-resource/ora_reference_lookups.md#lookup-execution-rules) for one local indexed
comparison of the complete batch with the grouped REST evidence. Check location business
keys against the complete selected BOSS or FSM Asset Location evidence.
Incomplete value-set coverage cannot authorize creation. After prerequisite
changes, repeat the grouped value-set REST checks and refresh the selected
Asset Location evidence.
Do not reuse pre-import verification evidence.

### Other Lookup Execution Rules

| Situation | What Happens |
|---|---|
| BOSS Asset Location read fails | After the REST client's permitted authentication refresh, do not retry the BOSS endpoint. Use exactly one current `FA_MANAGE_FIXED_ASSET_LOCATION` setup-data export as the duplicate-check fallback. Require a completed process for the same target environment and the exported Asset Location CSV member with all required serialized location fields; otherwise report the location state as unverified and stop. |
| A conditional lookup has no approved callable route | Do not call an inferred endpoint or substitute browser navigation. Block only that conditional branch until an approved execution contract is available. This does not apply to the documented LOC# KFF and filtered value-set export routes. |
| System control is resolved | Use the BOSS row only to establish the current system-control identity. Use the matching FA_SYSTEM_CONTROL.csv LocStructureInstanceCode as the location-structure source, then delegate to `manage-fixed-assets-key-flexfields` and verify it maps to one enabled LOC# structure in the current KFF export. |
| A concatenated location is supplied | Parse it only with the delimiter returned by `resolve_location_kff_combination`. Do not infer or substitute a delimiter. |
| Complete combination validation is needed | Do not invoke FND_FLEX_KEYVAL directly. `core.data-loader` and its post-import flow own submission and any accepted or rejected combination outcome. This skill reports validation findings only and returns `validated_for_import`. |
| DFF context is supplied | Resolve one exact enabled FA_LOCATIONS context from the same fresh DFF export before validating its context-sensitive attributes. |
| Existing Asset Location is resolved | Use complete exact BOSS `assetLocations` evidence as the primary source for duplicate, update, enabled-parent, or existing-location evidence. Use the completed current same-target FSM export only when BOSS is unavailable, incomplete, ambiguous, or lacks required fields. Do not infer location state from a partial result or a template/spec package. |
| HR lookup is used interactively | Treat only locations effective on TRUNC(SYSDATE) with an associated set as selectable. |
| TCA feature is checked | Feature evidence is diagnostic only. It cannot enable the TCA branch until an approved customer-site resolver contract exists. |
| Existing mapping is found | A zero-match result permits creation. One exact exported mapping is an unsupported-maintenance blocker; do not update, overwrite, delete, or duplicate it. Do not add an inferred LocationMappingId to LocationMappings.csv. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---:|---:|---|---|---|---|---|
| MAL.RESOLVE_REFERENCES | decision | 20 | reference_lookup | resolved->MAL.RESOLVE_SEGMENT_VALUES;required_input_missing->MAL.HANDLE_INPUT;unresolved_or_ambiguous->MAL.HANDLE_LOOKUP | MAL.VALIDATE_INPUT | stop | Resolve System Controls and LOC# structure; map all physical segments and stop on missing required segment input. Then export the batch-current DFF definition, identify required FA_LOCATIONS columns, and stop on missing DFF input before value-set lookup or prerequisite preparation. |
| MAL.RESOLVE_SEGMENT_VALUES | decision | 25 | reference_lookup | resolved->MAL.CHECK_DEPENDENCIES;missing_confirmed->MAL.CHECK_DEPENDENCIES;unresolved_or_ambiguous->MAL.HANDLE_LOOKUP | MAL.RESOLVE_REFERENCES | stop | After both KFF and DFF input gates pass, validate mapped segment values. Send confirmed missing value-set members to dependency evaluation; stop on unverified evidence. |
| MAL.RESOLVE_OPERATION | decision | 35 | evaluate_result | create_new->MAL.APPLY_DEFAULTS;update_existing->MAL.APPLY_DEFAULTS;decision_required->MAL.HANDLE_OPERATION_DECISION | MAL.CHECK_DEPENDENCIES | stop | Compare requested operation with exact existing-location evidence. |
