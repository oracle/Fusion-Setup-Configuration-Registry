# Manage System Controls: Input Validation

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| System control identity | Enterprise Name | Stop before package preparation | Provide the enterprise name. It is the system-control primary key and appears on Assets reports. | Always | |
| Asset setup baseline | Oldest Date Placed in Service, Category Flexfield Structure, Location Flexfield Structure, Asset Key Flexfield Structure, Initial Asset Number | Stop before package preparation | Provide the date, the three Oracle Assets flexfield structures, and the initial asset number. | Confirmed create path | resolve_assets_flexfield_structures |
| Asset-numbering policy | `PreventUserAssetNumberFlag` | Do not block package preparation | Validate only when the user supplies a value. | Confirmed create path | resolve_system_controls_export_metadata |

## DFF Input Intake

Preserve supplied DFF context and values with the Enterprise Name.
Do not demand creation-only DFF values until absence of System Controls
is confirmed. An existing exact row retains the read-only terminal path.

On the confirmed create path, discover required segments from current
metadata through resolve_system_controls_dff_segments. Recover supplied
input before asking for missing business values; do not hardcode prompts
or require users to supply internal attribute-column names.

## Field Validation

### Flag Value Normalization

Accept affirmative user input (Yes or Y) and negative user input (No or N)
case-insensitively. Before field validation, storage, or serialization,
translate that input to the exact uppercase value listed below.
Reject unrecognized input. Preserve existing optionality and blank behavior;
these mappings do not introduce defaults or authorize additional fields.

| Database table | Database column | Affirmative stored value | Negative stored value |
|---|---|---|---|
| FA_SYSTEM_CONTROLS | PREVENT_USER_ASSET_NUMBER_FLAG | `Y` | `N` |
| FA_SYSTEM_CONTROLS | USE_CUSTOM_ASSET_NUMBERS_FLAG | `Y` | `N` |

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Enterprise Name | Reject when empty or longer than 30 characters. | Enterprise Name is supplied | |
| Oldest Date Placed in Service | Reject when missing or not a valid `YYYY/MM/DD` date. | Confirmed create path | |
| Flexfield structures | Reject when any requested structure is missing, disabled, lacks an enabled matching instance, or has multiple enabled matching instances without an exact user selection. | Confirmed create path | resolve_assets_flexfield_structures |
| Initial Asset Number | Reject when missing, non-numeric, non-integral, or not representable as a target `NUMBER(18)` value. Do not derive it from an existing enterprise or asset. | Confirmed create path | resolve_system_controls_export_metadata |
| Numbering flag (`PreventUserAssetNumberFlag`) | Translate supplied affirmative input to `Y` and negative input to `N`, case-insensitively. Validate and serialize only `Y` or `N`; leave omitted values blank. | A numbering option is supplied on the confirmed create path | resolve_system_controls_export_metadata |

## System Controls Input Preview

For every System Controls request, before a live lookup, render this identity
preview in the active chat. Use `Required` only when Enterprise Name is missing.
Validate Enterprise Name, then perform the read-only existing-state lookup. Do
not request or validate creation-only values until that lookup confirms the
create path.

```text
Input Preview

| Field | Value |
|---|---|
| Target | <environment name> |
| Task | Manage System Controls |
| Enterprise Name | <supplied value or Required> |
| Existing-state lookup | Pending |
```

When the read-only lookup confirms absence, render the creation input preview
and validate the supplied values before package work:

```text
Input Preview — Create System Controls

| Field | Value |
|---|---|
| Target | <environment name> |
| Task | Manage System Controls |
| Enterprise Name | <validated value> |
| Oldest Date Placed in Service | <supplied value or Required> |
| Category structure | <supplied value or Required> |
| Location structure | <supplied value or Required> |
| Asset Key structure | <supplied value or Required> |
| Initial Asset Number | <supplied value or Required> |
```

After all creation inputs pass format validation, follow the Reference
Validation Preview, Design Preview, Final ZIP Preview, Execution Approval
Preview, and Post-Execution Verification Preview gates in the parent Fixed
Assets skill. When one exact existing System Controls row is found, use only
the prescribed read-only customer display from `ora_reference_lookups.md`.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| SYS.VALIDATE_INPUT | decision | 10 | validate_input | valid->SYS.LOOKUP_EXISTING;invalid->SYS.HANDLE_INPUT | none | stop | Enterprise Name is supplied |
| SYS.COLLECT_CREATE_INPUTS | decision | 35 | validate_input | valid->SYS.RESOLVE_DFF;invalid->SYS.HANDLE_INPUT | SYS.LOOKUP_EXISTING | stop | Existing System Controls absence is confirmed |
