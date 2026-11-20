# Manage Change Order Types Defaulting Rules

Source: user instructions to copy source or target values and apply only requested changes. These defaults do not invent enterprise policy values.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| Attachment Entity Name | EGO_ENGINEERING_CHANGES_B; apply before attachment-category validation and delegation, and pass explicitly to the owning skill | An attachment category is requested through Manage Change Order Types and Entity Name is omitted or blank | No; report an explicitly different entity as a mismatch | |
| Change Type header Start Date and End Date | Unsupported by FSM import/export. When supplied, show the established warning and skip the date change; do not map, default, derive, or invent either header date column. | Creating or updating a change type | No | |
| New Internal Name | If supplied nonblank, preserve and validate it. Otherwise construct from new change type Name by replacing each literal space with _, preserving case and other characters; validate and obtain user confirmation. Never copy source Internal Name; do not remove punctuation or invent a suffix | Create, including cloning; not Update | No | |
| New change type Category Code | Exact accepted Internal Name, supplied or confirmed constructed value; never copy source Category Code. Map to the evidenced current-export carrier and validate equality in the final ZIP | Create, including cloning; not Update | No | resolve_change_type_identity_fields |
| CopiedFrom | Retain the selected source's CopiedFrom using the Base Change Type Mapping in ora_reference_lookups.md and the fresh exported source row; do not substitute its TypeInternalName | Creating a type by copying the explicitly selected source | No | resolve_change_type_relationship |
| EffectiveImmediatelyFlag and EffectivityIncrementDays | Preserve both exported values unchanged | No item-effectivity change is requested, for creation or update | No | resolve_change_type_dependencies |
| EffectiveImmediatelyFlag | Set to Y; preserve EffectivityIncrementDays unless separately requested | The user explicitly requests immediate change-order effectivity | No | |
| EffectiveImmediatelyFlag and EffectivityIncrementDays | Set EffectiveImmediatelyFlag to N and EffectivityIncrementDays to the supplied number of days | The user explicitly provides item-effectivity days greater than zero | No | |
| Unchanged creation values | Preserve exported source values, subject to required new identity/reference changes and the child header-attribute exclusion in ora_design_enforcement.md | Creating a type and the user did not request a value change | No | resolve_change_type_dependencies |
| Unchanged update values | Preserve exported target values, identifiers, and relationships, subject to requested changes and the child header-attribute exclusion in ora_design_enforcement.md | Updating an existing type | No | resolve_change_type_dependencies |
| Sequence Generated numbering | No invented defaults for Prefix, Suffix, Starting Number, or Increment. Require Starting Number, Increment, and Prefix or Suffix before export/import; do not copy source settings to fill missing requested sequence details. Preserve valid unchanged baseline settings for unrelated updates | Sequence Generated is selected or is the known existing method | No | |
| Default Assignee and Assignee Role | For cloning copy each source value unless explicitly overridden; copy a complete unchanged pair without re-entry or reconfirmation. Updates retain omitted fields. Explicit blank/clear takes precedence and must not be refilled from source. Validate partial overrides against the resulting role. No role permits blank without prompting; a present role always requires a nonblank member. Do not preserve an invalid role/blank-user pair or invent a user. Resolve baseline before treating request omission as missing input | Every Create/cloning or Update; source/existing baseline plus explicit changes | No | |
| Business policy values | Retain the selected exported baseline unless a change was requested; do not invent priorities, reasons, numbering settings, effective dates, assignees, or workflow statuses | Preparing either operation | No | resolve_change_type_dependencies |
| Requested default lookup | Use the exact enabled `LookupCode` from the Standard Lookup mapped to `PriorityCode` or `ReasonCode` | A user requests either field | No | resolve_default_lookup |
| Requested default lookup removal | Clear PriorityCode, ReasonCode, or both only as explicitly requested. Apply Start Date rules independently; allow other independently valid requested changes and applicable defaults in the same package. Preserve unrelated values and shared lookup definitions; require the final ZIP to pass Fusion validation | A user explicitly requests removal | No | resolve_default_lookup_removal |
| Attachment category | Do not create, resolve, or associate a category when `attachment_category` is absent. When supplied for creation, reuse the exact resolved category or use the category created by the attachment-category skill, and preserve/add its exact Change Policy association. Use the supplied association Start Date when present; otherwise default it to the current date at package preparation in the export's date format and record the applied date as defaulted in the preview | Creating a change order type | Yes, current-date default only when no Start Date is supplied | resolve_attachment_category |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COT.PRESERVE_VALUES | step | 40 | apply_default | applied->COT.ENFORCE_DESIGN;invalid->COT.REPORT_ISSUES | COT.CHECK_DEPENDENCIES | stop | A selected-type package is being prepared |
