# Reference Lookups

## Data Authority

Use a fresh same-task FSM template and ASM_SETUP_CSV_METADATA.xml for package
shape. Existing CSV data rows are never a prerequisite or a donor for new rows.

Keep target-state evidence separate: a template proves format, not absence.
A complete current same-task state export with expected members and zero rows
can verify an empty target. Where rows exist, inspect them only for identity,
duplicates, conflicts, explicit updates, or post-import verification. Do not
infer a KFF REST/BOSS discovery route. Value sets use the documented lookup below.

The seeded Category and Location label mappings below are authoritative for preparation;
exported label rows are neither required nor used to derive them.

## Local Lookups

Use the fresh task-specific exports supplied by the governed export workflow.
Do not reuse stale or combined-task exports. These resolvers read the supplied
evidence; they do not introduce a new live execution route.

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_existing_kff_structure | Before deciding create, update, disable, replacement, or no change. | Selected KFF/application, requested structure and instance, complete current KFF export and metadata. | Retain all structures for the selected pair, then match requested parent/child identities exactly. Include instances, structure and instance segments, labels, and every structure EnabledFlag. | Full existing-state comparison, enabled-structure count, instance enabled state, and verified absence where coverage is complete. | Verified absence permits a create candidate only. Missing coverage, ambiguous identities, or an absent update target blocks classification. |
| resolve_segment_label | During dependency readiness when labels or Category changes are in scope. | Documented seeded mappings, selected KFF/application, and explicit segment selection; authoritative evidence for other labels. | Use the seeded mappings below directly for their specified KFF/application without exported values. Preserve explicit choices; resolve custom, unknown, or conflicting labels separately. | Label identity, applicable assignment constraints, and selected segment. | Missing exported seeded-label data does not block preparation or require a waiver. Ask only for unresolved segment selection; other unresolved labels or conflicts remain blockers. |
| verify_segment_tree | Tree Code is supplied. | Tree Code, effective Value Set Code, supplied approved target tree metadata, and current same-task export. | Exactly one registered tree linked to the effective value set. | Tree identity and verified association. | Missing, ambiguous, or incompatible evidence blocks the supplied tree; do not invent a live tree endpoint. |
| parent_post_import_verification_kff | After an accepted Data Loader operation completes. | Completed process logs/status, approved scope, and fresh same-task KFF export. | Terminal import status plus fresh read-back must match the complete approved structure, instance, segment, label, and enabled-state delta. | Parent verification result or precise mismatch. | The Fixed Assets parent owns the verification and blocks completion on missing evidence or target mismatch. Loader-wrapper success alone is insufficient. |

Do not add a separate deployment-status check or deployment approval after this
setup import. Deployment is a separate workflow only when explicitly requested.
A deployment-status response saying "not Submitted" does not make this verified
setup task pending or justify submitting deployment again.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_compatible_value_set | A segment references a value set or default. | Explicit or derived ValueSetCode, approved definition, supplied default, and parent context. | Read-only GET /fscmRestApi/resources/11.13.18.05/valueSets?q=ValueSetCode='{ValueSetCode}', then returned canonical child values links. Use the owning value-set workflow's grouped retrieval and pagination. | Code, identifier, validation type, datatype, subtype, maximum length, enabled/effective values, independent parent, and dependent mappings. | One exact compatible definition with complete requested coverage; compare definition and parent relationship, not name alone. Verify supplied defaults against effective values and mappings. | Verified reference, compatibility/default evidence, or absent-definition result. | Missing definition returns to dependency readiness. Ambiguous, incompatible, inactive, or incomplete results block binding. Use a complete current value-set export only when REST is unavailable or incomplete; never override contradictory REST evidence. |

## Lookup Result Classification

## Customer-Facing Label Wording

Seeded CAT#/140 definitions supplied in the Manage Segment Labels screenshot:

| Segment Label Code | Name | Description | Global | Required | Unique | BI Object Name |
|---|---|---|---|---|---|---|
| BASED_CATEGORY | Major Category | Major category for each asset | No | Yes | Yes | Segment1 |
| MINOR_CATEGORY | Minor Category | Minor category for each asset | No | No | Yes | Segment2 |

Reuse these definitions; do not create them or require exported label rows.
Assign Major Category exactly once to the selected segment. Assign optional
Minor Category only when explicitly selected, at most once. BI Object Name
does not select the customer's segment or its position.

Seeded LOC#/140 definition supplied in the Manage Segment Labels screenshot:

| Segment Label Code | Name | Global | Required | Unique | BI Object Name |
|---|---|---|---|---|---|
| LOC_STATE | State Segment | No | No | Yes | Segment2 |

For a Location design containing a state segment, suggest the optional State
Segment label. Assign it only when the customer requests or accepts the suggestion
and selects the segment; otherwise omit it without blocking preparation. Assign
it at most once per structure. Reuse the seeded definition without exported label
rows. BI Object Name does not force assignment to the second segment.

For CAT# structure and instance creation, use `BASED_CATEGORY` in FSM import
rows, schema validation, reference lookups, and technical package evidence. Do
not substitute display wording for that required technical value.

Previews, review requests, status updates, completion reports, and other
customer-facing UI must show the same requirement only as **Major Category
label**. Do not display `BASED_CATEGORY` in customer-facing text.

| Situation | What Happens |
|---|---|
| Full requested state matches | Take KFF.DONE_MATCH only after comparing the complete requested material scope, not merely structure name or code. |
| Requested new object is absent | Take absent to apply defaults and evaluate the proposed complete delta; absence does not bypass design checks. |
| Existing state needs an approved change | Take approved_change only for the exact approved delta with resolved identities and no unapproved difference. |
| Difference is unapproved or identity ambiguous | Take different_or_ambiguous to disclose the unresolved decision. Never use approval to bypass ambiguous identity. |
| Lookup fails | Take failure; do not treat a failed lookup as absence. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| KFF.LOOKUP_EXISTING | decision | 30 | reference_lookup | match->KFF.DONE_MATCH;absent->KFF.APPLY_DEFAULTS;approved_change->KFF.APPLY_DEFAULTS;different_or_ambiguous->KFF.HANDLE_LOOKUP;failure->KFF.HANDLE_LOOKUP | KFF.RESOLVE_DEPENDENCIES | stop | Dependencies are ready. |
