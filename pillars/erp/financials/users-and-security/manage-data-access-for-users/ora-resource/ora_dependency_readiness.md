# Manage Data Access for Users Dependency Readiness

This file owns task-local readiness, not lookup mechanics or mutation execution.

## Common Section

### Required Order

| Sequence | Dependency | Ready When |
|---|---|---|
| 1 | Classification | Operation, method, environment, and scope are normalized |
| 2 | Applicable inputs | Selected-operation inputs are valid |
| 3 | Mutation identities | Every mutation row has canonical user, role, and membership evidence |
| 4 | Mutation context | Explicit context and ordered exact values are bound |
| 5 | Method dependencies | Applicable FSM or REST requirements below pass |
| 6 | Aggregate readiness | No requested row is blocked or unresolved |

Customer reads/export follow their own branches. Planning readiness does not authorize a mutation. A resumed/changed request must refresh applicable evidence rather than reuse stale readiness.

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| MDA-USER | Canonical active user | Yes | Mutation | Lookup | Fusion user account | resolve_active_user | Avoid ambiguous/suspended mutation targets | Select one exact user when ambiguous | Username, GUID, UserId |
| MDA-ROLE | Canonical active non-data role | Yes | Mutation | Lookup | Fusion roles list | resolve_active_nondata_role | Retain the existing mutation role eligibility | Select one exact role when ambiguous | RoleId, RoleName, RoleCode |
| MDA-MEMBERSHIP | Exact role membership | Yes | Mutation | Verify | Fusion user-role assignments | verify_user_role_membership | MDA does not provision prerequisite roles in normal assignment requests | Resolve membership outside the assignment workflow | Membership result |
| MDA-ROLE-OBJECT-CATALOG | Mapping decision | Yes | FSM mutation | Resolve | Available Role/Object Mappings table | resolve_role_object_mapping | Select permitted mapping rows | Correct malformed reference data | Match status, Application IDs, mapping-row requirement |
| MDA-REVOKE-START-DATE | Original assignment start date | Yes | FSM Revoke only | Resolve | Valid supplied date or validated data export | resolve_active_revoke_assignment | Preserve portable import identity | Follow date intake; never re-ask after unknown_confirmed | StartDateActive, source, resolution state, permitted receipt reference |
| MDA-TEMPLATE | Exact-task Template Only source | Yes | FSM mutation | Resolve | Shared task exporter and validated extracted package | | Preserve package members and ordered headers | Follow SKILL.md acquisition and validation | Template/package provenance and validation |
| MDA-REST-ASSIGNMENT | Complete assignment reconciliation | Yes | REST mutation | Resolve | Target dataSecurities collection | resolve_rest_assignment | Establish safe lifecycle classification | Resolve incomplete or ambiguous evidence | Per-row state, runtime ID, completeness |
| MDA-REST-LOADER | Registered MDA loader contract | Yes | REST rows requiring writes only | Resolve | Selected operation/environment, fresh exact reconciliation, and current core.data-loader registration/template/attributes/keys | resolve_rest_loader_contract | Derive the selected minimal source and check needed fields and keys against the current schema | Stop on missing, ambiguous, or contradictory contract; no direct write fallback | Object, current evidence set, operation/field/key decisions, target and schema/template fingerprints, verdict and reasons |
| MDA-REST-LIST | Requested List/search scope | Yes | REST List/search or window | Lookup | dataSecurities | list_rest_assignments | Evaluate completion for the requested collection or window | Supply valid scope and read options | Filter scope, options, assignments, requested_scope_complete, collection_complete, continuation |
| MDA-REST-GET | Definitive item result | Yes | REST Get one assignment | Lookup | dataSecurities | get_rest_assignment | Return found or not_found for the selected item scope | Supply a valid assignment ID and optional fields | Read scope, found status, requested_scope_complete |
| MDA-REST-COUNT | Requested count evidence | Yes | REST Count | Lookup | dataSecurities | count_rest_assignments | Distinguish complete retrieved counts from estimates | Supply valid scope and exact/estimated kind | Count kind/value, requested_scope_complete, collection_complete, continuation |

## FSM Method

### Common for Grant and Revoke

At MDA.CHECK_DEPENDENCIES, acquire and validate the exact-task Template source under SKILL.md's acquisition contract, resolve applicable Revoke dates, and confirm that remaining FSM defaults can be applied. Reuse common identity/membership and local mapping evidence; do not rerun those resolvers implicitly.

Do not require generated rows or already-applied defaults at this dependency gate. After MDA.APPLY_DEFAULTS, MDA.ENFORCE_DESIGN and MDA.HANDOFF_GATE require the completed package to satisfy all of the following:

- the downloaded and extracted exact-task Template Only package supplies the package shape and ordered headers;
- all four CSV members and metadata are present;
- normalized assignment rows populate `ORA_FUN_ALL_USER_DATA_ACCESS.csv` with `RecordTypeCode=USER_DEFINED`;
- `ORA_FUN_SECURITY_CONTEXT_MAPPING.csv` is header-only for listed pairs and contains only deduplicated user-defined rows for unlisted Grant/reactivation pairs;
- both provisioning-rule CSVs are header-only;
- each assignment row has canonical UserName, canonical RoleCode, mapped context branch, exact carrier values, ActiveFlag, resolved dates, and `RecordTypeCode=USER_DEFINED`; and
- all non-applicable carrier fields are blank.

The existing dependency gate evaluates the Revoke date dependency only for
FSM Revoke rows. A user-supplied valid original date satisfies it without an export.
For a derived date, require the validated ZIP evidence and receipt from
`resolve_active_revoke_assignment`; a pending process or log alone is not ready.
Map missing user input or an ambiguous match to the needs_input
outcome. A pending/unavailable export, missing active match, or invalid date
must not return ready; use invalid with the detailed resolver outcome retained
for ora_error_handling.md. Do not convert lookup failures into another date question.
Every requested row must pass its applicable checks before the combined
package is handed off. Retain row-level blockers; do not silently submit a subset.

The available-mappings table supplies the package-construction decision for the
RoleCode/ObjectName pair. Listed Application IDs are reference information only; a generated
mapping uses blank `ApplName` and therefore the user-defined Application ID
`-99`. Context values are passed through as supplied; the absence of a separate
value endpoint does not block package construction.

### Grant

Require validated explicit dates or eligibility for the permitted FSM defaults. No Revoke date dependency runs for Grant.

### Revoke

Require a valid original date and recorded source. Preserve the existing per-row supplied/unknown-date distinction; do not infer a no-op from a failed date export.

### Export/List

MDA.FSM_EXPORT_CHECK requires selected task ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS, environment identity, requested scope, catalog support, required exporter privileges, safe destination paths, and a usable declared shared-export route. It verifies handoff facts only; it does not create the export.

Return ready only when prerequisites pass; missing input is needs_input and unsupported/inconsistent execution context is invalid. Export execution, polling, download, and artifacts are owned by the SKILL.md shared-export handoff. No mutation rows, membership, original dates, or Template source are required.

## REST Method

### Common for Grant and Revoke

MDA.REST_CHECK_DEPENDENCIES requires common mutation validation, no unresolved scheduled/date-limited intent, complete reconciliation for every requested row, unambiguous absent/active/inactive classifications, usable IDs for existing rows, and the same selected environment.

Do not require an FSM mapping-catalog match, original date, or FSM Template/CSV package. This early semantic gate precedes no-op classification and does not require loader registration or a source artifact. Use already collected evidence; do not repeat a resolver implicitly. Return ready, needs_input, or invalid.

### Grant and Revoke

Use the single lifecycle table in SKILL.md. A planned write needs a valid permitted business specification. An all-no-op request bypasses loader metadata, sample generation, artifact construction, and mutation approval. For writes_needed, MDA.REST_LOADER_CONTRACT subsequently proves the registered contract; it must not become a common dependency for FSM or customer reads.

### Execution Readiness

At MDA.REST_PREPARE_READY, the selected operation has a minimal source derived from the current registered schema and assignment rules. At MDA.REST_READY, the exact immutable artifact has passed Task Hook validation; return to the calling core preview workflow. Require the same environment, selected method, current schema, all-row accounting, and immutable archive/digest/readback. A successful assignment GET does not prove loader privileges. No readiness result grants approval or claims submission. These contract and archive checks apply only to REST writes, not FSM, REST reads, loader follow-ups, or all-no-op outcomes.

Data Loader owns approval and its post-approval immutable-artifact checks. Freshness checks occur before preview, not as an extra MDA lookup after approval. Missing/stale preapproval contract evidence or a changed reconciliation result requires fresh preparation. No re-entry may regenerate a sample, switch method, change the final artifact, or invoke another loader submission.

### Loader Follow-up Readiness

MDA.LOADER_STATUS_READY requires only a valid loader reference and environment for the requested core status lookup. It bypasses mutation eligibility, membership, dates, samples, and artifact preparation. Later semantic verification additionally requires terminal success for the bound MDA artifact and its submitted scope. Missing linkage allows status reporting but never a claim of verified assignment success. Pending, failed, or partial results stop at the core status/diagnostic report.

### Read Readiness

| Read mode | Required evidence |
|---|---|
| Complete List | Valid GET plan covering the full query, all required finder-bound branches complete, and consistent distinct IDs; finder-free GET requires independent exhaustive evidence |
| Requested window | Valid GET plan, valid options, and distinct-assignment window satisfied after any branch merge; finder-free GET without exhaustive evidence remains an observed window, not a proven complete requested scope |
| Get one | Valid assignment ID and a definitive found/not-found response |
| Exact count | Complete ID retrieval for every required finder-bound branch, merged distinct-ID count, or independent exhaustive evidence for a finder-free scope |
| Estimated count | Complete finder-bound query with valid API totalResults labeled estimated; multiple branch estimates may be summed only when their assignment sets are provably disjoint; an unverified finder-free total is not a full-scope estimate |

Require the selected environment and read access for the chosen operation. Do not require an active target user, active role, membership, complete context-value identity, effective dates, or FSM artifacts.

Evaluate completion against the requested mode. A requested window does not require full-collection retrieval. Reuse the reached resolver's evidence; do not repeat lookups implicitly. These read dependencies never replace mutation reconciliation or verification requirements.

## Readiness Results

| Result | Meaning |
|---|---|
| Ready | Applicable handoff/planning prerequisites are satisfied; no write implied |
| Needs input | Missing business input or exact identity selection |
| Invalid | Inconsistent/unsupported request, invalid source, incomplete evidence, or method invariant failure |
| Not prevalidated | Current context-value handling; no existence/eligibility validator is enabled |
| Mapping listed/unlisted | FSM package decision only; never a REST eligibility decision |

The future context-value-validation extension point in SKILL.md does not enable extra dependencies in this version.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When | Resolver |
|---|---|---|---|---|---|---|---|---|
| MDA.CHECK_DEPENDENCIES | decision | 90 | resolve_dependency | ready->MDA.APPLY_DEFAULTS;needs_input->RETURN_ISSUES;invalid->RETURN_ISSUES | MDA.RESOLVE_ROLE_OBJECT_MAPPING | stop | FSM mutation dependencies including applicable original-date resolution |  |
| MDA.REST_CHECK_DEPENDENCIES | decision | 150 | resolve_dependency | ready->MDA.REST_ENFORCE_DESIGN;needs_input->RETURN_ISSUES;invalid->RETURN_ISSUES | MDA.REST_RECONCILE | stop | REST-only dependency and aggregate reconciliation checks |  |
| MDA.FSM_EXPORT_CHECK | decision | 210 | resolve_dependency | ready->MDA.FSM_EXPORT_READY;needs_input->RETURN_ISSUES;invalid->RETURN_ISSUES | MDA.SELECT_OPERATION | stop | Check selected shared-exporter scope and prerequisites only |  |
