# Input Validation

## Required Client Inputs

Ask only for the business fields needed for the requested action. Do not ask for
audit fields, export keys, package order, technical column positions, or optional
fields the customer has not chosen to create or change. Accept enterprise name
instead of technical structure names and segment names instead of technical
segment/value-set names. Apply Derived Naming and any applicable single-segment
value-set default in ora_defaulting_rules.md before checking those generated
fields. Do not request a validation type already supplied by that default.
Enterprise name alone is enough for naming a
structure in a selected KFF, not for inventing its segment design.

| Requested action | Required inputs | Ask only when applicable |
|---|---|---|
| Select a Fixed Assets KFF | Category, Asset Key, or Location, mapped to CAT#/140, KEY#/140, or LOC#/140. | Ask only when the requested KFF is unclear. Do not ask the customer for ApplicationId. |
| Create a structure | Enterprise name, or explicit Structure Code and Name. For CAT#, the segment selected for the required category label. | Delimiter, Enabled flag, and Description only as customer overrides to the documented defaults. |
| Update a structure | Existing structure selection and the requested changes. | Do not derive a replacement identity from a changed enterprise name. |
| Create or update structure segments | Complete ordered segment design, or an explicit partial change to an identified existing structure. Accept business validation choices from the customer or applicable documented defaults. Use supplied values, parent mappings, or an existing value-set selection when available. | Technical names are optional overrides. Resolve columns from target metadata; ask only for unresolved business choices, not technical positions. |
| Create or update a structure instance | Selected parent structure and whether a matching instance is in scope. | Names, API identifier, flags, and Description may be supplied as overrides. Otherwise apply documented naming and flag defaults. |
| Create or update instance segments | Parent segment design and any instance-specific business overrides. | Required/default decisions, Tree Code, or alternate value set only when that design requires them. |
| Create or update a segment-label definition | Label Name and explicit requested change. | A new custom definition also needs an approved technical code and target support; do not recreate seeded labels. Description and BI Object Name are optional. |
| Assign, change, or remove a segment label | Parent structure, selected segment, label display Name or supplied code, and explicit action. | Only for a label-assignment change. |
| Use a dependent or nullable segment | Explicit parent segment and approved parent-value mapping for dependent validation; explicit null/default decision for a nullable segment. | Only for those segment designs. |

## Field Validation

### Flag Value Normalization

Accept affirmative user input (Yes or Y) and negative user input (No or N)
case-insensitively. Before field validation, storage, or serialization,
translate that input to the exact uppercase affirmative or negative value
listed for its database column below. Never choose a representation at runtime
or serialize user-facing wording directly. Reject unrecognized input.

The table specifies populated boolean values only. It does not add defaults,
make optional fields mandatory, authorize changes to read-only or system-managed
fields, or change existing blank and update-preservation rules. Retain returned
target values as evidence; do not normalize them to conceal a target mismatch.

| Database table | Database column | Affirmative stored value | Negative stored value |
|---|---|---|---|
| FND_KF_STRUCTURES_B | ENABLED_FLAG | `Y` | `N` |
| FND_KF_SEGMENTS_B | ENABLED_FLAG | `Y` | `N` |
| FND_KF_STR_INSTANCES_B | ENABLED_FLAG | `Y` | `N` |
| FND_KF_STR_INSTANCES_B | DYNAMIC_COMBO_CREATION_FLAG | `Y` | `N` |
| FND_KF_STR_INSTANCES_B | SHA_ENABLED_FLAG | `Y` | `N` |
| FND_KF_SEGMENT_INSTANCES | REQUIRED_FLAG | `Y` | `N` |
| FND_KF_SEGMENT_INSTANCES | DISPLAY_FLAG | `Y` | `N` |
| FND_KF_SEGMENT_INSTANCES | BI_ENABLED_FLAG | `Y` | `N` |
| FND_KF_SEGMENT_LABELS_B | GLOBAL_FLAG | `Y` | `N` |
| FND_KF_SEGMENT_LABELS_B | REQUIRED_FLAG | `Y` | `N` |
| FND_KF_SEGMENT_LABELS_B | UNIQUE_FLAG | `Y` | `N` |

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| KFF code and application | Accept only CAT#/140, KEY#/140, or LOC#/140. | Field is in the requested scope | |
| Unresolved naming | Missing enterprise/segment names needed for derivation, invalid generated names, or unresolved code collisions fail input validation. Ask only for the missing business name or affected short-name override. | Field is in the requested scope | |
| Structure and instance codes | Required after naming resolution, not necessarily customer-supplied; each must be nonblank and no longer than 30 characters. | Field is in the requested scope | |
| Structure name and parent structure | Structure Name is required for a new structure. An instance must identify one selected parent structure. | Field is in the requested scope | |
| Structure instance identifier | Required and nonblank for every new structure instance. Accept an explicit or derived API identifier in the naming proposal; do not copy a blank identifier from a seeded or existing export. | Field is in the requested scope | |
| Dynamic Combination Creation Allowed | Required for every new structure instance. Default to Yes when omitted; preserve explicit Yes/No and serialize in the target-supported format. A blank packaged value blocks ZIP submission. | New structure instance is in scope | |
| Segment name | No more than 30 characters; no leading/trailing whitespace; cannot start with at sign, backslash, braces, comma, equals sign, less-than sign, parentheses, period, plus sign, vertical-bar character, space, hyphen, apostrophe, or underscore; cannot contain comma, ampersand, or forward slash. | Field is in the requested scope | |
| Segment Code and API Name | Required when authored, no more than 30 characters. API Name starts with a letter and then contains letters or digits only. | Field is in the requested scope | |
| Delimiter | Must be one supported structure delimiter: exclamation mark (!), asterisk (*), plus sign (+), hyphen (-), period (.), colon (:), equals sign (=), caret (^), tilde (~), or vertical bar (&#124;). | Field is in the requested scope | |
| Sequence and display fields | Sequence is a positive integer. Display Width is an integer when supplied. Short Prompt is required and unique within the structure. | Field is in the requested scope | |
| Value-set fields | Accept explicit or derived codes. Definition inputs must satisfy the owning value-set skill; compatibility and existence are resolved through ora_reference_lookups.md before binding the reference. | Field is in the requested scope | |
| Nullable segment and defaults | A supplied Required Flag is Y or N. Use Default Value Number only for numeric value sets; never populate it together with Default Value.  | Field is in the requested scope | |
| Segment labels | A label Name or supplied code identifies the requested label. Before authoring, definitions require a nonblank resolved internal code and Name; assignments require resolved parent/segment/label keys and an explicit action. | Field is in the requested scope | |
| Audit fields | Never request, derive, or modify Creation Date, Created By, Last Update Date, Last Updated By, or Last Update Login. | Field is in the requested scope | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| KFF.VALIDATE_INPUT | decision | 10 | validate_input | valid->KFF.RESOLVE_DEPENDENCIES;invalid->KFF.HANDLE_INPUT | KFF.DERIVE_NAMES | stop | Every request. |
