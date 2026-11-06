# Design Enforcement

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Package contains structure, instance, segment, or label-assignment rows. | Blocker | | A referenced KFF/application pair lacks exactly one matching parent in FND_APP_KEY_FLEXFIELD.csv, or a required structure/instance/segment parent link is missing, duplicated, or mismatched. | Apply the parent-row defaults in ora_defaulting_rules.md and verify same-package parent links before approval; seeded target rows do not replace package parents. | Correct the package before approval |
| A material target difference is not covered by the approved request. | Blocker |  | Preserve a materially different deployed design check fails. | Stop package authoring for an update, preserve, or replacement decision. Reuse an existing approval only when its scope and target evidence remain unchanged. | Only an explicitly approved supported correction |
| A change affects an existing deployed structure segment. | Blocker |  | Preserve deployed segment order and API names check fails. | Do not reorder a deployed segment or change its API Name. Use an approved new structure or segment when the design requires that change. | Only an explicitly approved supported correction |
| A structure is created, updated, enabled, or disabled. | Blocker |  | The proposed delta leaves zero or multiple enabled structures for the selected pair. | Keep exactly one enabled structure for the selected CAT#/140, KEY#/140, or LOC#/140 pair. A replacement must explicitly disable the existing enabled structure and pass the replacement-impact assessment; do not create a second concurrently enabled structure. | Approved replacement only after impact review |
| A label assignment is authored. | Blocker | resolve_segment_label | Required or unique assignment check fails. | Enforce the documented seeded Category label properties; for other labels enforce resolved required/unique properties. Do not assume all labels are unique. | Only an explicitly approved supported correction |
| A CAT# structure is created or updated. | Blocker | resolve_segment_label | Required Category assignment is missing, duplicated, or conflicts with the selected segment. | Assign the documented Major Category default exactly once to the explicitly selected segment. Exported label metadata is not required. Preserve existing assignments outside approved updates. | Only an explicitly approved supported correction |
| A segment uses dependent validation. | Blocker |  | Preserve dependent-segment ordering check fails. | Require an earlier independent parent segment and approved parent-value mappings; do not infer the relationship from segment names. | Only an explicitly approved supported correction |
| An instance segment has Required Flag N. | Blocker |  | Require an approved nullable design check fails. | Require an explicit approved null/default decision. Default field values remain owned by ora_defaulting_rules.md. | Only an explicitly approved supported correction |
| Approved design selects NONE or NA for a nonnullable or explicitly defaulted segment. | Blocker | resolve_compatible_value_set | Validate a placeholder default check fails. | Require an enabled, effective value verified by resolve_compatible_value_set; a dependent segment also requires a mapping to the selected parent value. Do not invent a placeholder value. | Only an explicitly approved supported correction |
| A structure, segment, instance, label, or assignment is authored. | Blocker |  | Keep package actions explicit check fails. | Package only the customer-approved create, update, disable, or removal action; do not infer an unrequested destructive action. | Only an explicitly approved supported correction |
| An existing structure would be disabled or replaced. | Blocker |  | Review replacement impact check fails. | Require an approved impact assessment covering System Controls references, structure instances, existing combinations, and asset usage. If System Controls is already configured, block the replacement: System Controls must not be updated to point to a replacement structure, and disabling its referenced structure is unsupported. If usage or a supported transition is unproven, block replacement; disabling a structure is not a data migration. | Only an explicitly approved supported correction |
| An instance is created or changed. | Blocker |  | Preserve instance inheritance check fails. | Retain the complete parent segment set and order. Instance-specific value sets and permitted overrides do not alter the parent layout. | Only an explicitly approved supported correction |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_segment_label | Label property or required Category label checks | Documented standard mapping or resolved custom label properties, and proposed assignments | ora_reference_lookups.md |
| resolve_compatible_value_set | A placeholder default is proposed | Effective default value and dependent-parent mapping when applicable | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| KFF.ENFORCE_DESIGN | decision | 50 | design_enforcement | pass->KFF.IMPORT_GATE;blocked->KFF.HANDLE_DESIGN | KFF.APPLY_DEFAULTS | stop | Defaults applied. |
