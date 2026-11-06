# Defaulting Rules

## Source Precedence

| Sequence | Source | Use |
|---|---|---|
| 1 | Fresh same-task FSM template and ASM_SETUP_CSV_METADATA.xml | Package members, headers, column order, encoding, supported columns, and accepted value formats only. |
| 2 | Approved customer design and explicit values | Business names, segments, relationships, and requested overrides. |
| 3 | This skill's naming and default rules | Fill omitted new-object fields; do not invent business values. |
| 4 | Verified target metadata and current Oracle documentation | Resolve technical references and supported semantics, never donor business defaults. |

Always author new import rows from the template, approved inputs, and these
defaults. Do not copy, require, or use existing CSV data rows as donor records.
If a fresh export contains data, use only its schema for new-row authoring;
keep any read-only existing-state evidence separate from the import rows.
An empty environment is supported without populated data rows. Explicit updates
still require verified identities and preserve fields outside the approved delta.

## Derived Naming

These are task naming conventions, not Oracle defaults. Use enterprise and
segment names from the customer's request or requirements. Preserve supplied
names, codes, and existing identities, including approved ENTERPRISE_SEGMENT
value-set names. Display-name changes must not generate new identities on updates.

KFF.DERIVE_NAMES prepares names and the single-segment default before validation
and lookups. KFF.APPLY_DEFAULTS applies the other defaults after lookups.
Generated names are proposals, not proof that objects exist.

| Field | Internal | Default Value | Applies When | Override User Value? | Source | Resolver |
|---|---|---|---|---|---|---|
| Enterprise naming prefix | No | Use the approved prefix; otherwise uppercase the enterprise name, replace each run of spaces or punctuation with one underscore, and trim outer underscores. | New-object naming needs a prefix. | No | Customer enterprise name and approved naming decisions |  |
| StructureCode | No | Enterprise prefix plus _CATEGORY for CAT#, _ASSET_KEY for KEY#, or _LOCATION for LOC#. | New structure code is absent. | No | Enterprise naming prefix and selected KFF |  |
| Structure Name | No | Enterprise display name plus Category, Asset Key, or Location. Prefer an approved short enterprise name. | New structure name is absent. | No | Customer enterprise name and selected KFF |  |
| SegmentCode | No | Uppercase the segment name and remove spaces and punctuation. Prefix SEG when the result starts with a digit. | New segment technical names are absent. | No | Customer segment name |  |
| SegmentIdentifier/API Name | Yes | Use the derived SegmentCode, subject to API identifier validation. | New segment API Name is absent. | No | Derived segment code |  |
| Segment Prompt and ShortPrompt | No | Segment display name, subject to target length and uniqueness checks. | New segment prompts are absent. | No | Customer segment name |  |
| Proposed ValueSetCode/name | No | Normalized SegmentCode + underscore + normalized enterprise prefix: SEGMENT_ENTERPRISE. Use it for both structure and instance segments unless the approved design overrides it. | No explicit, previously approved, or verified existing value set is selected for the segment. | No | Enterprise name and customer segment name |  |
| StructureInstanceCode | Yes | Matching parent StructureCode. | A matching instance is requested and its names are absent. | No | Derived or explicitly selected parent structure |  |
| Structure Instance Name | No | Matching parent Structure Name. | A matching instance is requested and its name is absent. | No | Selected parent structure |  |
| StructureInstanceIdentifier/API name | Yes | Parent StructureCode with punctuation removed; prefix KFF when it starts with a digit. | A new matching instance is requested and its API identifier is absent. | No | Selected parent structure code |  |

### Generated-Name Length Handling

Validate generated names against the field limits in ora_input_validation.md
and target metadata. If a name is too long, shorten it and append a stable
six-character hash, leaving room for any required suffix. API identifiers
must start with a letter and contain only letters and digits.

Record generated names for reuse and check for collisions before proceeding.

### Name Collisions and Value-Set Ownership

If different segment names normalize to the same code, qualify the generated
value-set name with the KFF code without #, then the segment position if needed.
Never merge segments or value sets to resolve a collision. Send unresolved
collisions and invalid display names to input validation. Use
ora_reference_lookups.md to check target collisions; never overwrite an existing
definition to resolve them.

The approved segment design and value-set skill govern values, datatype, parent
mappings, maximum length, and value defaults. Do not invent business values or
treat a name as a complete value-set definition.

## Single-Segment Value-Set Default

This task default does not restrict Oracle's supported validation types. Count
all segments in the intended structure, not just partial-update rows, enabled
segments, or segments needing new value sets.

| Field | Internal | Default Value | Applies When | Override User Value? | Source | Resolver |
|---|---|---|---|---|---|---|
| Proposed value-set Validation Type | No | Independent | Exactly one segment in the full design; a new value set is proposed subject to lookup; no validation type, dependent-parent design, or existing value set is supplied. | No | Single-segment business design and this task default |  |

Pass Independent to the value-set task without asking the customer to choose
again. Do not apply this default when the total count is unknown or above one.
Preserve and validate explicit choices and existing definitions. A Dependent
choice without a valid parent remains an error; do not replace it with Independent.

The value-set task owns definition fields, supplied values, preview, approval,
creation, and target verification. This default supplies no business values
and authorizes no Fusion write.

## Category Label Default

For new Category structures, use the documented seeded Major Category mapping
in ora_reference_lookups.md during dependency readiness, before ordinary defaults.
Reuse explicit Major/Minor Category segment selections; if unclear, ask which
segment has each role. Assign the Major Category label exactly once to the
selected segment. Use the seeded Minor Category mapping only when its optional
label assignment is explicitly selected.
Exported data values must not supply new-row values, defaults, or label resolution;
use exports only for package schema and existing-state or post-import checks.

## Standard Defaults

Populate `FND_APP_KEY_FLEXFIELD.csv` with exactly one parent row per distinct
KFF/application pair referenced by the approved child rows: selected `CAT#`,
`LOC#`, or `KEY#`, each paired with `140`. Never suffix these seeded keys.
These same-package linking rows are required even when the template is empty
and the KFFs already exist in Fusion. Include only referenced pairs; preserve
the template headers and encoding. Other unchanged members remain header-only.

Apply these proposals only to omitted fields on new objects. For updates,
preserve the current value unless an explicit approved change is supplied.
Never overwrite a supplied value with a default; invalid inputs are blockers,
not permission to replace them. Blank means no authored default, not No.
Naming is defined only in Derived Naming above. Literal values below are task
proposals, not claims about Oracle-delivered defaults.

| Field | Internal | Default Value | Applies When | Override User Value? | Source | Resolver |
|---|---|---|---|---|---|---|
| KeyFlexfieldCode | Yes | Selected seeded code: CAT#, KEY#, or LOC# | Every package | No | Fixed Assets template metadata |  |
| ApplicationId | Yes | 140 paired with the selected seeded code | Every package | No | Fixed Assets template metadata |  |
| Structure Description | No | No generic default | Blank | No | Approved design or this task proposal; export only to preserve updates |  |
| Delimiter | No | Hyphen (-); allowed values are owned by ora_input_validation.md. | Blank for a new structure; preserve the existing delimiter on an unchanged field during an amendment. | No | This task default or approved design; existing export for preservation only |  |
| Structure EnabledFlag | No | Y | Blank | No | Approved design or this task proposal; export only to preserve updates |  |
| Segment ColumnName | Yes | Preserve the verified existing column; for a new segment use a target-supported column for its approved position | Blank | No | Target package metadata and approved segment position |  |
| Segment Description | No | No generic default | Blank | No | Approved design or this task proposal; export only to preserve updates |  |
| Segment SequenceNumber | No | Approved segment position | Blank | No | Approved ordered design; export only to preserve updates |  |
| Segment EnabledFlag | No | Y | Blank | No | Approved design or this task proposal; export only to preserve updates |  |
| Segment DisplayWidth | No | 6 | Blank | No | Approved design or this task proposal; export only to preserve updates |  |
| Segment RangeType | No | No generic default | Blank | No | Approved design or this task proposal; export only to preserve updates |  |
| DefaultValueSetCode and Instance ValueSetCode | No | Verified referenced ValueSetCode | Blank after successful lookup | No | resolve_compatible_value_set | resolve_compatible_value_set |
| SegmentLabelCode | Yes | Documented seeded Major Category mapping; no generic default for other labels | New Category structure with an explicitly selected Major Category segment | No | ora_reference_lookups.md; preserve explicit choices | resolve_segment_label |
| Structure Instance Description | No | Blank | Blank | No | Approved design |  |
| Structure Instance EnabledFlag | No | Y | Blank | No | Approved design or this task proposal; export only to preserve updates |  |
| DynamicCombinationCreationAllowed | No | Y (Yes) | Omitted on a new structure instance | No | This task default or explicit approved override; preserve existing values on updates |  |
| ShorthandAliasEnabledFlag | No | N | Blank | No | Approved design or this task proposal; export only to preserve updates |  |
| Structure Instance StructureCode | No | Resolved StructureCode | Blank | No | Resolved existing or approved same-package parent design |  |
| Instance SegmentCode | No | Parent structure SegmentCode | Blank | No | Resolved existing or approved same-package parent design |  |
| Instance TreeCode | No | Blank | No approved tree design | No | Approved design |  |
| Instance RequiredFlag | No | Y | Blank | No | Approved design or this task proposal; export only to preserve updates |  |
| Instance DisplayFlag | No | Y | Blank | No | Approved design or this task proposal; export only to preserve updates |  |
| Instance DefaultType | No | Blank | No approved default | No | Approved default decision; resolve_compatible_value_set verifies referenced values | resolve_compatible_value_set |
| Instance DefaultValue | No | Blank | No approved default | No | Approved default decision; resolve_compatible_value_set verifies referenced values | resolve_compatible_value_set |
| Instance DefaultValueNumber | No | Blank | No approved default | No | Approved default decision; resolve_compatible_value_set verifies referenced values | resolve_compatible_value_set |
| Instance BIEnabledFlag | No | N | Blank | No | Approved design or this task proposal; export only to preserve updates |  |
| Instance QueryRequiredType | No | OPTIONAL | Blank | No | Approved design or this task proposal; export only to preserve updates |  |

Show Dynamic Combination Creation Allowed in the Design Preview. For every new
structure instance, serialize the resolved Yes/No value using the target CSV
format; never leave it blank. Preserve an explicit No.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| KFF.DERIVE_NAMES | step | 5 | apply_default | prepared->KFF.VALIDATE_INPUT | none | stop | Every request; prepare missing new-object names and the applicable single-segment value-set proposal, preserving explicit inputs and unresolved issues for validation. |
| KFF.APPLY_DEFAULTS | step | 40 | apply_default | applied->KFF.ENFORCE_DESIGN | KFF.LOOKUP_EXISTING | stop | Lookup resolved |
