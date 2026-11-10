# Manage Data Access for Users Defaulting Rules

## Common Section

MDA.SELECT_METHOD applies Method Selection Policy in ora_input_validation.md before input validation.
MDA.APPLY_COMMON_DEFAULTS runs after selected-method input validation and before
operation branching. Apply only action-derived desired state; do not reselect
the method or run FSM date/CSV defaults here. Explicit supported values win.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| Route (MDA.SELECT_METHOD only) | Method selected by Method Selection Policy in ora_input_validation.md | Method omitted; preserve an existing selection under that policy | No | |
| Desired active state | Active for Grant; inactive for Revoke | Explicit unambiguous mutation action | No | |
| FSM StartDateActive | Execution date in YYYY/MM/DD | FSM Grant omits start date | No | |
| FSM Revoke StartDateActive | No default; retain validated original date/source | FSM Revoke | No | |
| FSM EndDateActive | Blank | FSM mutation omits end date | No | |
| FSM assignment ActiveFlag | Y for Grant; N for Revoke | Generated FSM assignment row | No; conflicting explicit state blocks | |
| FSM assignment RecordTypeCode | USER_DEFINED | Every generated FSM assignment row | Yes | |
| FSM mapping RecordTypeCode | USER_DEFINED | Deduplicated unlisted FSM Grant/reactivation pair | Yes | |
| FSM mapping ApplName | Blank, resolving to user-defined Application ID -99 | Generated FSM mapping row | Yes | |
| FSM mapping CreatedBy, LastUpdatedBy, SecurityContext | Blank | Generated FSM mapping row | Yes | |

## FSM Method

### Common for Grant and Revoke

MDA.APPLY_DEFAULTS runs only after FSM dependencies pass. Apply only the applicable Standard Defaults rows. Never copy SEEDED from a reference or exported row into generated assignment/mapping rows.

Listed Application IDs are reference evidence only. Do not place them in ApplName or any other CSV field.

### Grant

Preserve valid explicit dates. Default only an omitted start date to the execution date and an omitted end date to blank.

### Revoke

Never default or infer StartDateActive, including from today or another row. Use its validated supplied original date or resolve_active_revoke_assignment evidence after explicit unknown-date intent. Preserve valid explicit end dates; omission remains blank.

## REST Method

### Common for Grant and Revoke

Do not default dates, audit values, assignment IDs, FSM carriers, RecordTypeCode, or context values. Use SKILL.md's lifecycle table and the current registered loader schema. IDs used for updates come only from complete reconciliation; generated IDs remain omitted on create. Loader metadata defines field names and writable/key roles, not the requested business identity.

Set every executable row's operation explicitly from its lifecycle decision. Do not inherit RestAction or any value from a sample: even an update sample may contain a create operation when enrichment is unavailable. Preserve identifiers and leading zeroes as text. For the registered `dataSecurities.ActiveFlag` `String(1)` field, map desired active to `Y` and inactive to `N`; if current metadata declares a different type or encoding, resolve that conflict before preview. Do not copy JSON or Python boolean spellings into a string DAT field.

Missing/null/nonboolean observed ActiveFlag is not a desired-state default. It blocks safe lifecycle classification.

### Grant

For a new assignment, use `RestAction=POST` with canonical identity and context fields. Omit the generated assignment ID, `ActiveFlag`, and unrelated optional fields; Oracle documents active-by-default behavior for the MDA assignment POST. For reactivation, Grant intent and the exact inactive match select `RestAction=PATCH` and the active state; no other business field may change.

### Revoke

Revoke intent and the exact active match select `RestAction=PATCH` and the inactive state. Never default to DELETE, export a start date, or clear another field. Absent/already-inactive assignments produce no executable record; an all-no-op request generates no sample or job.

### Read Defaults

Apply these defaults within the reached read resolver, only for options applicable to its mode; do not run FSM defaults or mutation desired-state derivation for reads.

| Input omitted | Default |
|---|---|
| Search operator | Equality |
| Ordinary exact username equality | Userrf finder selection with a case-insensitive returned UserName check; no redundant q identity term; explicit case-sensitive/raw-q semantics win |
| Ordinary exact display-role equality | Rolerf finder selection with a returned RoleNameCr check; combine Rolerf and Userrf when both exact identities are supplied |
| Collection GET plan | Prefer a finder implied by the full scope; for several exact users with one shared display role use its Rolerf finder plus `Userrf IN (...)`; otherwise cover finite alternatives with their exact finder-bound GETs. Use a collection GET with the supplied validated q, if any, when no exhaustive finder plan exists; never invent a user, role, or wildcard finder or infer completeness from a finder-free HTTP 200 |
| Combination between independent filters | AND |
| ActiveFlag filter | None; include both states |
| Output fields for List/Get | Existing assignment projection |
| Sort for collection retrieval | UserRoleDataAssignmentId ascending |
| Starting offset | Zero |
| Result cap for ordinary List | None; retrieve complete scope |
| Count kind for "how many" | Exact distinct-assignment count after complete retrieval |

Explicit operators, patterns, lists, grouping, fields, ordering, and paging override applicable defaults. Transport page size is not the customer's total-result cap; respect the server's returned page size while satisfying the requested scope.

Never default a missing user, role, context, or context value. Never infer all-assignment scope merely because filters are absent. Read defaults must not change mutation reconciliation, FSM defaults, or Grant/Revoke payloads.

## Explicit Values Win

Preserve explicit method and business inputs. An explicit active state must agree with the action. Incompatible instructions block rather than being overwritten; date intent with selected REST must not be silently omitted.

## Never Default

Never infer username, role/code, action, context, ordered values, internal IDs, an existing assignment, or an FSM Revoke original date. Preserve meaningful suffixes and exact value contents.

Observed export/response values are evidence for that observation, not universal defaults. ContextValueHandlingStatus=not_prevalidated is this version's behavior; future declared validation sources require coordinated contract updates, not a new implicit default.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When | Resolver |
|---|---|---|---|---|---|---|---|---|
| MDA.APPLY_COMMON_DEFAULTS | step | 15 | apply_default | applied->MDA.SELECT_OPERATION;not_applicable->MDA.SELECT_OPERATION | MDA.VALIDATE_INPUT | stop | Derive mutation desired state only; method was selected before validation |  |
| MDA.APPLY_DEFAULTS | step | 100 | apply_default | applied->MDA.ENFORCE_DESIGN;not_applicable->MDA.ENFORCE_DESIGN | MDA.CHECK_DEPENDENCIES | stop | Apply FSM-only defaults after its dependencies |  |
