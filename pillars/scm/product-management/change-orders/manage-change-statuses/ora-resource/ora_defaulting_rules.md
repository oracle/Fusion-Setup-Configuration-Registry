# Defaulting Rules

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| Description | Exact OperationalPurpose | Optional Operational Purpose is supplied | No |  |
| StatusType | Numeric value mapped from the user-selected fixed catalog type | StatusTypeName is supplied or selected | No | resolve_change_status_type |
| SeededFlag | N | Create only; never default or overwrite the exported value on Update | Yes |  |
| Unspecified fields | Leave optional template cells blank; do not invent sort order or language | Source contract permits blank | No |  |
| Update identity and required carriers | Use a valid selector combination to find current rows in the fresh export: Existing Internal Name; Existing Status; Existing Status with Existing Status Type; or Internal Name with either or both additional checks. Existing Status alone proceeds when one row matches; it requires bulk-scope approval before rows are prepared only when multiple rows match. Copy the complete selected export row into its import row, then replace only requested StatusName, Description, or StatusType values. Do not create a partial update row from a template or user input. | Update | Yes | resolve_existing_change_status |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MCS.DEFAULTS | step | 30 | apply_default | applied->MCS.DESIGN;invalid->RETURN_ISSUES | MCS.LOOKUPS | stop | Required lookups passed |
