# Assign Security Profiles to Role Defaulting Rules

Source: HCMDS Assign Security Profiles to Role Skill, version 5.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| Delegation Allowed | False | Creating a new data role and Delegation Allowed is not specified | No | resolve_delegation_allowed_yes_no |
| Role Name | Derive a display name from the inherited job role and at least one security-scope descriptor; keep the display name below 100 characters | Creating a new data role and Role Name is not specified | No; retain a user-supplied Role Name | derive_available_data_role_name_and_code |
| Role Code | Derive only from the final data-role Role Name: `role_name.upper().replace(" ", "_") + "_DATA"` | Creating a new data role | Yes; ignore every user-supplied data-role Role Code | derive_available_data_role_name_and_code |

The security-scope descriptor may be an audience, a hierarchy type or level, or
another configuration qualifier that distinguishes the data role. Require a
meaningful descriptor only when Role Name is absent and must be derived.
Resolve the final Role Name first, retaining a supplied name, then derive the
Role Code from that name alone. Replace each literal space with one underscore
as is; preserve repeated, leading, and trailing spaces as repeated, leading,
and trailing underscores. Do not trim, collapse spaces, tokenize, remove
punctuation, or substitute the inherited job-role name or code. Always append
`_DATA`, even when the transformed name already ends in `_DATA`. If the result
fails target validation, stop and request an alternate Role Name rather than
silently normalizing it. Apply this rule only to new data roles; preserve the
resolved existing Role Code for updates.

Examples: `Regional HR Access` becomes `REGIONAL_HR_ACCESS_DATA`;
`HR  East-West` becomes `HR__EAST-WEST_DATA`; `Scoped_DATA` becomes
`SCOPED_DATA_DATA`. Do not append numeric
or timestamp suffixes: a derived display name and internally derived role code
must each be unique and available before preview or import.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ASPR.APPLY_DEFAULTS | decision | 2 | apply_default | defaults_applied->ASPR.LOOKUP_MAPPINGS;blocked->ASPR.ERROR | ASPR.VALIDATE | stop | A new data role is being created or updated and defaultable values have been evaluated |
