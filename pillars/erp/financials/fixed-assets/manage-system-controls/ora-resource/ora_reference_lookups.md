# Manage System Controls: Reference Lookups

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_system_controls_export_metadata | Before package preparation | A current target-environment FSM export for FA_MANAGE_SYSTEM_CONTROL | Accept only the current export for this exact task. | CSV file names, XML metadata, headers, required fields, internal IDs, accepted flag values, and documented defaults | Stop package preparation. Record the missing technical lookup as a blocker. |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_existing_system_controls | Before a create decision | Enterprise Name | Primary: BOSS System Controls resource through `core.fusion-api.rest-api-client`. Fallback: current same-target-environment `FA_MANAGE_SYSTEM_CONTROL` FSM export through `shared.setup-export.task-level-export` only when BOSS is unavailable, fails, or returns no exact Enterprise Name row. | Existing system-control fields, current values, and enterprise identity | Require one exact Enterprise Name match. A successful fallback export with the expected `FA_SYSTEM_CONTROL.csv` header and zero data rows confirms no System Controls record. | Existing definition and read-only status, or confirmed absence | An exact BOSS or fallback row means System Controls is already set: show it as read-only and do not prepare a ZIP or allow an update. A confirmed empty fallback export permits a create path after all other gates pass. Multiple rows, an incomplete export, or an unavailable fallback export blocks the work. |
| resolve_assets_flexfield_structures | Before package preparation | Selected Category, Location, and Asset Key structure names or identifiers | Current same-target-environment `FA_MANAGE_FIXED_ASSETS_KEY_FLEXFIELDS` FSM export through `shared.setup-export.task-level-export` | Structure Code, structure `EnabledFlag`, matching `StructureInstanceCode`, separate instance `EnabledFlag`, and Assets applicability | Require one exact enabled structure and one matching enabled instance for each required flexfield type. If multiple matching enabled instances exist, require the user's exact instance selection. | Populate the three `FA_SYSTEM_CONTROL.csv` structure fields from the selected enabled `StructureInstanceCode`; retain the identifier only as read-back evidence. | No enabled structure, no enabled matching instance, multiple enabled instances without selection, incomplete export, or unavailable export blocks the work. |

### Existing-State BOSS Lookup

Use the BOSS client through `core.fusion-api.rest-api-client` first, with:

```text
GET /api/boss/data/objects/ora/erpCore/fixedAssetsSetup/v1/assetSystemControlsView
```

Request `$limit=100` and page with `$offset` until `hasMore` is `false`.
Use one exact `enterpriseName` match for the existing-state decision. When
BOSS is unavailable, fails, or has no exact Enterprise Name row, use the
same-target FSM export fallback. A successful fallback export containing the
expected `FA_SYSTEM_CONTROL.csv` header and zero data rows confirms the create
path. When one exact row is found, show that System Controls is already set and
read-only. Do not prepare a ZIP or allow an update. Do not substitute an
unrelated enterprise's controls.

For this fallback, request setup **data** with
`shared/setup-export/task-level-export/scripts/export_setup_task_csv.py`
using `--task-code FA_MANAGE_SYSTEM_CONTROL --data` and the selected project
and target OAuth properties. The script's default template-only export is not
existing-state evidence. Inspect the downloaded `FA_SYSTEM_CONTROL.csv` rows;
report a zero-row data export as an absent configuration, not as a missing
download or a populated System Controls value.

### Existing System Controls Customer Display

When one exact Enterprise Name row is found, show this customer-facing result:

> System Controls are set and cannot be changed.

Do not show the lookup source, business values, BOSS, FSM export, technical
identifiers, or internal evidence details in this customer-facing result.
Retain that evidence internally for the existing-state decision.

### Key Flexfields Discovery

Use a fresh `FA_MANAGE_FIXED_ASSETS_KEY_FLEXFIELDS` FSM data export for CAT#,
KEY#, and LOC# discovery. Do not use an inferred KFF REST or BOSS resource,
an older export, or a structure name as an instance-code substitute.

In the customer-facing `Reference Validation Preview`, show the requested
Category, Location, and Asset Key structure names and their validation outcome.
Retain structure codes, `StructureInstanceCode`, enabled flags, and segment
details as internal validation evidence. Both the structure and selected
matching instance must be enabled; when multiple matching enabled instances
exist, require the user's exact selection before continuing.
When the fresh FSM export contains no enabled matching structure,
structure, state for that requested code: `No enabled structure found in
current target evidence.` Ask whether to begin Key Flexfields resolution or
enablement work;
do not start it, prepare a System Controls package, or submit any change before
the user answers. This is an observability result, not a claim that disabled
structures do not exist.

### Mandatory Reference Validation Preview Gate

Before reporting a create path, readiness, a design result, ZIP status, or an
approval request, render a customer-facing `Reference Validation Preview` with
one row for each requested Category, Location, and Asset Key structure. Each
row must contain the following business-facing evidence from the current KFF
export:

| Structure type | Structure name | Validation result |
|---|---|---|
| Category, Location, or Asset Key | Exact selected structure name | One matching enabled structure instance verified, or the blocking result |

If any required row or validation result is missing, the
Reference Validation Preview is incomplete. Treat it as a technical lookup gap:
do not call the target ready, do not create a ZIP, and do not request approval.

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| A current export is not available | Do not infer headers, internal IDs, flags, or defaults from a failed import or a different task. |
| A required FSM export is unavailable, incomplete, or has unexpected CSV structure | Do not claim existence or structure validation is complete. Record the technical lookup gap and stop before package preparation. |
| A current FSM export has the expected `FA_SYSTEM_CONTROL.csv` header and zero data rows | Treat the System Controls record as absent and use the create path after all remaining input, structure, design, and approval gates pass. |
| BOSS or the FSM fallback returns one exact Enterprise Name row | Show the existing System Controls definition as already set and read-only. Do not create, update, or prepare a ZIP. It is immutable: do not propose or perform a System Controls structure-reference update as part of a KFF replacement or migration. |
| A System Controls structure field is being populated | Confirm the matching structure and selected matching instance are both enabled using `KEY_FLEXFIELD_STRUCTURE.csv` and `ORA_FND_APP_KEY_FLEXFIELD_STRUCTURE_INSTANCE.csv`, then populate `LocStructureInstanceCode`, `CatStructureInstanceCode`, and `AssetStructureInstanceCode` from that selected enabled instance. Do not substitute `StructureInstanceIdentifier` or a display name. |
| Fresh KFF FSM export shows no enabled matching structure or instance | Show `No enabled usable structure instance found in current target evidence.` for that requested code in the Reference Validation Preview and ask whether to begin Key Flexfields resolution or enablement work. Do not treat this as proof that disabled structures or instances are absent; stop before package preparation or KFF changes until the user answers. |
| Reference Validation Preview is incomplete or omitted | Treat this as a technical lookup gap. Do not report readiness, create a ZIP, or request approval until the complete three-column preview is rendered. |

## Post-Import Target Verification

A successful Data Loader response, accepted FSM initiation, terminal FSM status,
or ProcessLog alone is not completion evidence. The Fixed Assets parent owns
this verification after the request is accepted. After terminal success, it
queries the BOSS System Controls resource first and requires one exact
Enterprise Name row that matches the approved System Controls scope. Use a
fresh same-target `FA_MANAGE_SYSTEM_CONTROL` FSM export only when BOSS is
unavailable, fails, or returns no exact Enterprise Name row.

| Evidence | Required result | If absent or different |
|---|---|---|
| Accepted request | Preserve the Data Loader request/content identity and immutable archive hash. | Treat missing correlation as an unresolved import-process blocker. |
| Terminal process | Preserve terminal status and FSM ProcessLog, including created, skipped, warned, and failed counts when available. | Pending, failed, timed-out, or conflicting status blocks completion; never resubmit automatically. |
| Primary BOSS verification | Page the BOSS resource and require exactly one approved `enterpriseName` row. Reconcile every approved field BOSS returns. | If BOSS is unavailable, fails, or has no exact row, continue to fresh FSM export. A returned row that differs from the approved scope is a target-state mismatch. |
| Fallback fresh System Controls export | Re-export `FA_MANAGE_SYSTEM_CONTROL` only after BOSS is unavailable, fails, or returns no exact row; require exactly one approved Enterprise Name row. | Missing, stale, zero-row, multiple-row, malformed, or unavailable fallback read-back blocks completion. |
| Field reconciliation | Reconcile Enterprise Name, the CSV-normalized Oldest Date Placed in Service (`YYYY/MM/DD`), Initial Asset Number, and the three approved `StructureInstanceCode` values from the selected verification source. | Report the target-state mismatch; do not correct by trial and error. |

When BOSS returns one exact Enterprise Name row that matches the approved scope,
it completes the post-import target verification. Do not perform an additional
FSM export merely to duplicate successful BOSS evidence. A returned BOSS row
that differs from the approved scope is an unresolved target-state mismatch;
do not correct it by trial and error.

A verification blocker never authorizes another System Controls package or
import.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| SYS.LOOKUP_EXISTING | decision | 30 | reference_lookup | create_path->SYS.COLLECT_CREATE_INPUTS;already_configured->SYS.DONE_READ_ONLY;unresolved->SYS.HANDLE_LOOKUP | SYS.VALIDATE_INPUT | stop | Enterprise Name is valid |
| SYS.PRESENT_REFERENCE_PREVIEW | decision | 39 | evaluate_result | complete->SYS.APPLY_DEFAULTS;incomplete->SYS.HANDLE_LOOKUP | SYS.RESOLVE_DEPENDENCIES | stop | The System Controls create path is confirmed |
