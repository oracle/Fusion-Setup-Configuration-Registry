# Dependency Readiness

## Batch Import Preparation

For a CSV or list of locations, partition mixed structures into explicitly
resolved batches. Read the applicable system-control and KFF evidence once per
structure and environment, and retain one current-batch DFF export.

Detect duplicate physical seven-segment combinations within the input locally.

Use complete paged BOSS `assetLocations` evidence as the primary Asset Location
duplicate and update source. A complete exact BOSS no-match permits create
readiness. Use one current same-target populated
`FA_MANAGE_FIXED_ASSET_LOCATION` setup-data export only when BOSS evidence is
unavailable, incomplete, ambiguous, or lacks required fields. Do not combine
partial BOSS pages with export rows. A populated task export remains the source
for an Asset Location-to-HR Location mapping business-key check.

Only after the required dependency order has resolved and
`MAL.ENFORCE_DESIGN` has passed, enter `MAL.PREPARE_ARCHIVE`. At that node,
verify the ordered rule-result record and the batch-current DFF-definition
evidence before requesting this task's CSV template or specification package
through `shared.setup-export.task-level-export` in template mode. Use its
verified members, headers, row widths, and metadata as the package-shape source
for the immutable import artifact. Do not send export criteria with template
mode, and do not use the template as target-state or duplicate evidence.

If the template or specification package cannot be downloaded or inspected
unambiguously, stop before archive preparation. Do not prepare a location ZIP
unless the batch's current DFF-definition evidence can be completed and mapped
unambiguously.

## Batch Evidence Lifecycle

Obtain the DFF definition export after resolving the LOC# structure and
validating the supplied location segments, but before value-set lookup or
prerequisite preparation. Use it to find required FA_LOCATIONS columns,
compare them with supplied input, and stop on a missing value. The completed
export may be reused for every row in that
unchanged batch. If the target environment or batch membership changes, or a
new import batch starts, export again and recompute the required-input map
before archive preparation.

Retain a per-location DFF validation result containing the resolved context,
required physical columns, input mappings, and value-validation outcomes.
Each result references the same batch-level DFF definition export.
All applicable checks must pass before preview. Archive preparation must
also verify that the final serialized create rows preserve those values
and satisfy the same required-field map.

Use the template or specification package for immutable import-package shape
only. Use complete exact BOSS `assetLocations` evidence as the primary Asset
Location target-state source. Use the current same-target populated task export
only when BOSS evidence is unavailable, incomplete, ambiguous, or lacks
required fields. Do not require that export after a complete exact BOSS result.
Use the DFF export for current DFF requirements; use a populated task export
for mapping evidence.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---:|---|---|
| 1 | Asset system control | Use `resolve_location_system_control` to establish enterprise identity and obtain the exported LocStructureInstanceCode. |
| 2 | LOC# structure | Use `discover_location_kff_structure` to obtain a new KFF task export for this request and target environment, then resolve one enabled LOC# structure, its delimiter, displayed segments, requiredness, and value-set mappings. |
| 3 | LOC# segment input | Use `resolve_location_kff_combination` to map supplied values to the selected instance and physical Segment1 through Segment7 columns. Validate that every required segment has a supplied value. Stop on missing input before DFF export or prerequisite preparation. |
| 4 | Location DFF definition and input gate | After fixing immutable batch membership, obtain one new Manage Fixed Assets Descriptive Flexfields export through `core.fusion-api.apps-common.descriptive-flexfields` as declared in [Batch Import Preparation](#batch-import-preparation). Find enabled required FA_LOCATIONS global and selected-context columns and check that each has a supplied value. Missing required input stops the parent request before any prerequisite preparation. |
| 5 | Location KFF segment values | Verify every supplied segment value exists, is enabled and effective, and has the required dependent parent mapping in its resolved value set. |
| 6 | Parent Asset Location | Resolve the Asset Location combination and confirm it is enabled before importing a mapping. |
| 7 | Source location | Resolve the HR Location Code plus HR Set Code only when Customer Site Number is blank. When it is supplied, block because the approved customer-site resolver contract is absent. |
| 8 | Existing mappings | Identify existing mapping state by the complete serialized mapping business key from ORA_FA_ASSET_LOCATION_TO_HR_LOCATION_MAPPING.csv. A zero-match result is create-ready; an exact existing mapping is an unsupported-maintenance blocker. |
| 9 | Archive preparation | After `MAL.ENFORCE_DESIGN` passes, verify the ordered rule-result record and batch-current DFF-definition evidence, then obtain and inspect the task template/spec package. |
| 10 | Import route | Delegate import to core.data-loader; any selected LocationMappings.csv adapter must preserve the supported ADFdi/Rapid Start ADVANCED contract. Do not invoke that adapter directly. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| asset_system_control | Asset system control | Yes | Create Asset Location | Verify | Read-only AssetSystemControl BOSS row plus current same-environment FA_MANAGE_SYSTEM_CONTROL export | resolve_location_system_control | LocationEO creation requires it and derives the structure from it. | Configure system controls first, then provide current system-control export evidence when required. | STRUCTURE_INSTANCE_NUMBER and LocStructureInstanceCode |
| location_kff_structure | LOC# structure | Yes | Create or validate Asset Location | Verify | Current `FA_MANAGE_FIXED_ASSETS_KEY_FLEXFIELDS` KFF export and the selected LocStructureInstanceCode | discover_location_kff_structure | The selected System Controls instance determines the deployed LOC# structure. | Resolve one enabled LOC# instance and its current metadata before mapping input values. | Delimiter, displayed segments, requiredness, and value sets |
| location_kff_combination | LOC# combination mapping | Yes | Create or validate Asset Location | Verify | Selected LOC# structure and supplied location code or labelled segments | resolve_location_kff_combination | Creation must use the selected instance's physical mapping. | Map all supplied values to physical Segment1 through Segment7 before value-set validation. | Normalized segments and mapped value-set/value pairs |
| location_dff_segments | Required FA_LOCATIONS DFF segments | Yes | Create Asset Location batch | Verify | One new same-environment FA_MANAGE_FIXED_ASSETS_DESCRIPTIVE_FLEXFILEDS export created after the immutable batch scope is final: `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_GLOBAL_SEGMENT.csv` and, for a selected context, `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv` | resolve_location_dff_segments | Global DFF segments remain applicable when no context is selected; required segments are dynamic configuration and must not be inferred from a prior batch export, prior request, or hardcoded attribute. | Supply each required DFF value using its uniquely exported Prompt, SegmentCode, or ColumnName. | Export process identity, batch identity, target environment, ColumnName, Prompt, RequiredFlag, ValueSetCode, and supplied value |
| location_segment_values | Location KFF segment values | Yes | Create or validate Asset Location | Verify | Current grouped REST checks with verified filters, pagination and visibility | resolve_location_segment_values | Every supplied segment must be a valid current member of its mapped value set. | Create or enable an exact missing value through Manage Fixed Assets Flexfield Value Sets, then re-verify it. | ValueSetCode, Value, enabled/effective state, and dependent parent value when applicable |
| location_dff_context | FA_LOCATIONS DFF context | Conditional | Additional Information is supplied | Verify | Enabled DFF contexts for application 140 | resolve_location_dff_context | A selected context must be enabled. | Select an enabled context or remove the context-dependent values. | ATTRIBUTE_CATEGORY_CODE |
| enabled_asset_location | Parent Asset Location | Yes | Import mapping | Verify | Resolved FA_LOCATIONS row | resolve_enabled_asset_location | A disabled parent cannot receive a mapping. | Enable the location before importing the mapping. | FA_LOCATION_ID |
| hr_location | HR Location Code and HR Set Code | Yes | HR mapping import | Lookup | HR reference data | resolve_hr_location_reference | Both values resolve the mapping source location. | Supply the exact code and set. | SOURCE_LOCATION_ID |
| tca_mapping_feature | TCA mapping configuration | Conditional | Customer Site Number is supplied | Verify | Active-enabled fndStaticLookups row: ORA_ERP_CONTROLLED_CONFIG / FA_38101956 | resolve_tca_mapping_feature | Diagnostic only; it cannot enable TCA mapping. | Remove Customer Site Number or provide an approved resolver contract. | None |
| tca_customer_site | Customer site | Conditional | Customer Site Number is supplied | Blocked | No approved callable contract | resolve_tca_customer_site | Customer-site identity cannot be resolved. | Remove Customer Site Number to use the HR branch, or provide an approved resolver contract. | None |
| existing_mapping | Existing location mapping | Yes | Import mapping | Lookup | Current same-environment ORA_FA_ASSET_LOCATION_TO_HR_LOCATION_MAPPING.csv export | resolve_existing_location_mapping | The export exposes the complete serialized mapping business key but not LocationMappingId. | Permit a new mapping only on a verified zero-match result. Block maintenance of an existing mapping because no supported update identity is available. | Existing-mapping state and exported business key |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Ready | All applicable mandatory dependencies resolve uniquely with current evidence. | Proceed to defaults and design validation. |
| Blocked | Required system control, parent, source reference, or feature is absent or invalid. | Stop; create or enable related setup only through its approved task. |
| Ambiguous | More than one matching source or existing mapping is found. | Stop for a precise business selection. |

## Value-Set Handoff Rule

When a missing or disabled LOC# segment value is delegated to Manage Fixed
Assets Flexfield Value Sets, follow that skill's scoped existing-definition
export procedure before preparing the prerequisite artifact. For a confirmed
missing segment value required by a new Asset Location, pass `EnabledFlag=Y` to
the owning Value Sets workflow. This does not change the Asset Location
combination's separate `EnabledFlag` choice. Export only the resolved
`ValueSetCode` definition; do not use an unfiltered value-set data
export for this handoff. This is the exclusive Asset Location value-set route:
do not invoke `core.fusion-api.apps-common.value-sets` from Manage Asset
Locations or accept its direct REST output as readiness evidence. The delegated
workflow must send `REST-Framework-Version: 2` and use only the `values` and
`validationTable` links returned by the matched root response. Never construct
a child URL from `ValueSetCode`, a returned identifier, or any other ID.

Do not delegate, preview, prepare, or import a Value Sets prerequisite while
the parent Asset Location has an unresolved required DFF input. A confirmed
missing value-set member does not waive the step-4 DFF input gate.

## Ownership Boundary

This file owns dependency availability, prerequisite handoff, continuation, and
stop conditions. `ora_reference_lookups.md` owns evidence authority, resolver
mechanics, and the mandatory delegated value-set route. Input shape and field
validation belong to `ora_input_validation.md`; defaults belong to
`ora_defaulting_rules.md`; package/design safeguards belong to
`ora_design_enforcement.md`; and disclosure, recovery, and execution-boundary
handling belong to `ora_error_handling.md`.

## Prerequisite Continuation

Treat a request to create an Asset Location as one durable parent request. When
LOC# component values need prerequisite work, retain the normalized segments,
target environment, requested defaults, and parent-request fingerprint in the
project run record. Route only confirmed missing values to Manage Fixed Assets
Flexfield Value Sets, honoring existing authorization. Ambiguous or unverified
evidence requires resolution rather than speculative value creation.

After a successful prerequisite import and post-import verification, resume the
same parent request with fresh dependency and reference checks. Re-read the
affected value sets and current Asset Location state before continuing. A
failed, uncertain, or partially successful prerequisite import remains at its
recorded recovery stage and must not be replayed or inferred complete.

Manage Asset Locations creates a location combination only after every supplied
LOC# component value exists in its resolved value set. Invoke
resolve_location_segment_values once for the immutable batch. It owns the
grouped REST evidence, complete query coverage and local batch comparison. Reuse its
indexed evidence across rows; do not repeat live reads per component per row.
Unverified evidence blocks creation and does not establish a missing value.

When a value is missing, disabled, ineffective, ambiguous, or lacks its
required dependent parent mapping, do not create the Asset Location or prepare
a mapping import. Identify the exact value set, value, enabled state,
effective dates when supplied, and dependent parent value when applicable. If
the parent request already authorizes prerequisite creation, retain its
normalized request fingerprint and route only the missing values through Manage
Fixed Assets Flexfield Value Sets. Otherwise ask for that authorization once.
After a successful prerequisite import and post-import verification, resume the
same Asset Location request automatically without asking the user to resupply
segments. Perform fresh value-set and duplicate checks; resume does not reuse a
stale approval or retry an uncertain import.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---:|---:|---|---|---|---|---|
| MAL.CHECK_DEPENDENCIES | decision | 30 | resolve_dependency | ready->MAL.RESOLVE_OPERATION;blocked_or_ambiguous->MAL.HANDLE_DEPENDENCY | MAL.RESOLVE_SEGMENT_VALUES | stop | Evaluate dependencies after the DFF input gate and segment-value findings; route only confirmed missing values through the approved prerequisite workflow. |
