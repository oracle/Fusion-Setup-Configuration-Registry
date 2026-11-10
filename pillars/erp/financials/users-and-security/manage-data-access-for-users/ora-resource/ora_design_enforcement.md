# Manage Data Access for Users Design Enforcement

## Common Section

### Mandatory Invariants

1. Honor the selected operation and inherited environment; select and preserve the method through Method Selection Policy in ora_input_validation.md.
2. Classify mutation versus read/export before applying mutation prerequisites.
3. For mutations, resolve an eligible active user, active non-data role, and exact membership before method-specific preparation.
4. Filter eligibility before deduplication and cardinality; ambiguity requires an exact selection.
5. For mutations, resolve Security Context only from an explicit supported label or alias; customer read literals follow Read Invariants below.
6. For mutations, preserve every required ordered value exactly; use the single context table in ora_reference_lookups.md for arity and binding.
7. Current context values are not prevalidated. Assignment comparison is permitted only through the documented selected-method resolver; it never permits value replacement.
8. Future context-value validators may use a source independent of the assignment method, but require explicit resolver, applicability, readiness, and failure contracts before activation.
9. Validate all requested rows before the first mutation; reject conflicting desired states for the same complete assignment.
10. Never invent identifiers, silently replace values, or switch methods after a failure.
11. Distinguish readiness, execution, and verified completion. A readiness terminal never writes.

## FSM Method

### Common for Grant and Revoke

The local role/object catalog controls FSM package construction only.

1. FSM mutation downloads and extracts an exact-task Template Only ZIP through `setupTaskCSVTemplateExports`; it never uses `--data`, `setupTaskCSVExports`, or current exported data as its mutation-package source.
2. `ORA_FUN_ALL_USER_DATA_ACCESS.csv` contains generated direct-assignment rows; `ORA_FUN_SECURITY_CONTEXT_MAPPING.csv` may contain only deduplicated unlisted Grant/reactivation mapping rows.
3. Standard-context rows leave `DatasecContextTypeCode` blank; non-standard rows use the documented code.
4. Each FSM row populates only the selected context branch's carriers and leaves all other carriers blank.
5. The canonical RoleCode is written to the FSM `RoleName` column.
6. Every generated assignment and mapping row explicitly uses `RecordTypeCode=USER_DEFINED`; never copy `SEEDED` from the available-mappings table.
7. Mapping availability is decided by RoleCode/ObjectName. Multiple Application IDs are one positive pair match and are retained only as reference information.
8. A generated mapping leaves `ApplName`, `CreatedBy`, `LastUpdatedBy`, and `SecurityContext` blank. Blank `ApplName` intentionally produces Application ID `-99`.
9. `ORA_FUN_SECURITY_CONTEXT_MAPPING.csv` remains header-only for listed pairs and for unlisted Revoke/deactivation requests.

### Revoke

- A Revoke must use its own valid original StartDateActive with source user_supplied or derived_from_current_mda_export; it must not default or borrow that date.
- Preserve valid supplied end dates and use ActiveFlag=N. Source ActiveFlag=Y is only an assignment-match condition.
- The explicitly selected MDA task supplies the offering metadata for its Revoke lookup; do not ask the user to select an offering.
- Preserve each row's unknown_confirmed state across lookup failures; do not re-ask or expose export implementation details.
- Export-derived dates require completed, validated data ZIP evidence. Keep the mutation-package source Template Only.


### Grant

Apply only the documented FSM Grant defaults. Generate at most one user-defined mapping row per unlisted RoleCode/ObjectName pair; listed pairs require no mapping row.

### Portable Locator

Use the normalized values for:

- `UserName`, `RoleName`, and `ObjectName`;
- `DatasecContextTypeCode`;
- every documented context carrier in Template order; and
- requested lifecycle dates.

Explicit blanks in non-applicable carrier columns are part of the portable representation. Do not copy a current row to construct a create or update.

### Package Boundary

| Member | Rule |
|---|---|
| `ORA_FUN_ALL_USER_DATA_ACCESS.csv` | Contains generated direct-assignment rows with `RecordTypeCode=USER_DEFINED` |
| `ORA_FUN_SECURITY_CONTEXT_MAPPING.csv` | Header-only for listed pairs; otherwise one deduplicated user-defined row per unlisted Grant/reactivation pair |
| `ORA_FUN_DATA_PROVISIONING_RULES.csv` | Header-only companion |
| `ORA_FUN_DATA_PROVISIONING_RULE_DETAIL.csv` | Header-only companion |
| `ASM_SETUP_CSV_METADATA.xml` | Required package metadata |

Reject a package with missing, duplicate, renamed, reordered, or unexpected members or headers.


## REST Method

### Common for Grant and Revoke

Require complete exact reconciliation, including inactive assignments, before selecting an operation from the lifecycle table in SKILL.md. Every required ordered value participates in matching. Multiple distinct exact assignment IDs, missing state, invalid state, or incomplete pagination blocks mutation.

Do not apply the FSM mapping catalog, original-date lookup, Template package, CSV carriers, RecordTypeCode, or effective-date defaults. Explicit scheduled/date-limited intent blocks REST until the user selects a compatible method. Do not silently discard the intent.

Every REST mutation uses core.data-loader's registered business-object artifact workflow. The shared REST client performs declared GETs only. Data Loader owns its single preview/approval gate, upload, initiation, retries, and job diagnostics. No hidden Fusion write is permitted in a reference lookup, gate, or terminal, and a previously approved direct-REST payload is not loader-artifact approval.

MDA.REST_ENFORCE_DESIGN applies semantic reconciliation/date/identity rules before no-op classification; it must not demand loader artifacts at this early stage. After writes_needed, MDA.REST_LOADER_CONTRACT resolves the current registered schema and derives the selected minimal source. MDA.REST_VALIDATE_ARTIFACT and MDA.REST_HANDOFF_GATE enforce the final artifact contract on Task Hook re-entry. Readiness must never bypass this phase distinction or recursively call the loader.

Require immutable artifact readback matching every requested write and excluding no-op, sample, and unrelated rows. Check explicit operations, exact identity keys, state-only updates, and omitted attributes. Retain original method and routing-count evidence across core conversion and re-entry. Missing or contradictory metadata, a changed normalized request, or a changed artifact blocks preview; do not repair it during approval or submission. Sample generation does not prove load success.

### Grant

Use a minimal create row only for a complete no-match result; use a minimal state-only activation update for one inactive exact assignment. Already-active is a no-op. Creation may create a missing role/context mapping; disclose this potential side effect. Never inherit a sample's POST default for an update.

### Revoke

Use a minimal state-only deactivation update for one active exact assignment. An inactive or absent assignment is a no-op. No DELETE, original-date question, mapping creation, or effective-date payload is permitted. Omit unchanged fields instead of serializing blanks.

### Read Invariants

1. Classify reads versus mutations before applying operation-specific checks.
2. Honor supplied predicates, supported operators, and grouping. Reject standalone unary NOT under Query Syntax and Framework before a read; never interpret HTTP 200 as proof that an unsupported exclusion was applied.
3. Do not require missing mutation identity fields for a customer read.
4. Do not restrict explicit read literals solely through the local mutation-context catalog.
5. Honor requested projection, sorting, offset, and result cap for applicable read modes.
6. Distinguish requested_scope_complete from collection_complete.
7. Label estimated counts explicitly; incomplete retrieval cannot produce an exact count.
8. An empty List is definitive only after a GET plan covering the full requested scope and complete retrieval; finder-free, unbound-finder, or wildcard-finder emptiness does not prove absence. Multiple matches are valid search results.
9. A missing single assignment is a not-found read result.
10. Never remove a rejected filter or silently downgrade syntax or output options.
11. Read output does not authorize a subsequent mutation and is not an FSM export artifact.
12. Mutation reconciliation and verification always retain complete evidence requirements, independently of customer read preferences.
13. Keep each selected finder and every remaining q predicate on all collection pages; ordinary exact user and display-role identities may be carried by the finder without redundant q terms. A finder must be implied by the entire request or by its complete decomposed alternative. Cover every OR alternative, verify returned finder-bound identities, and never invent filters or an alternate route. A valid finder-free GET may report observed rows, but not a complete collection or exact count without independent exhaustive evidence.
14. Advance offsets by raw rows while reporting distinct assignment IDs. Finish every required finder-bound branch before reporting complete, then merge/deduplicate and apply global ordering/windowing. Consistent duplicate observations count once; conflicting observations prevent completion.

REST create/update records retain common user, role, and exact membership validation. Customer reads and loader-status follow-ups do not require mutation eligibility, membership, effective dates, or packages. Job acceptance is not semantic verification; status-only responses must not generate a new load.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Preserve explicit intent | Honor normalized operation, selected method, inherited environment, and requested scope |
| 2 | Apply applicable common checks | Mutations require identity, membership, and ordered context values; reads use their own scope checks |
| 3 | Enforce selected-method prerequisites | FSM checks mapping, dates, and package; REST checks reconciliation and unscheduled state, then contract/artifact checks only when writes are needed |
| 4 | Enforce execution boundary | Both mutation methods use Data Loader approval/submission; REST verification follows a later request and terminal success |
| 5 | Report evidence | Readiness alone is not execution; retain partial and uncertain outcomes |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Any mutation | Error | | User, role, context, or ordered value was inferred | Obtain explicit business input | Yes |
| Any mutation | Error | | Exact user-role membership is unproven | Complete common membership verification | Yes |
| Mutation context value binding | Error | | Count or order differs from the single context table | Supply the documented ordered values | Yes |
| FSM mapping decision | Error | resolve_role_object_mapping | Catalog missing, malformed, blank-keyed, nonnumeric in Application ID, or duplicate full key | Correct the existing catalog before package construction | Yes |
| FSM package | Error | | Package is not an extracted exact-task Template Only package, contains unauthorized mapping rows, or provisioning-rule data | Rebuild from the validated Template Only package | Yes |
| FSM Revoke | Error | | Original StartDateActive/source is invalid or end date precedes start date | Resolve this row's original date; never default it | Yes |
| FSM Revoke with unknown date | Error | resolve_active_revoke_assignment | Unique active assignment/date lacks completed validated export evidence | Preserve unknown_confirmed and follow lookup recovery | Yes |
| FSM Revoke task selection | Error | | User is asked for offering selection despite selected MDA task metadata | Use the declared task metadata | Yes |
| REST mutation | Error | resolve_rest_assignment | Reconciliation is ambiguous, incomplete, or invalid | Resolve the evidence before preview | Yes |
| REST date intent | Error | | Scheduled or date-limited access was requested | Explain the unsupported intent and obtain method selection | Yes |
| REST loader contract | Error | resolve_rest_loader_contract | Exact MDA registration is missing or ambiguous, needed operation fields/keys are absent, or current metadata contradicts the minimal source | Resolve the current target schema and selected operation before artifact preparation | Yes |
| REST artifact validation | Error | | Archive/digest differs from the reviewed artifact, or an executable PATCH has the wrong reconciled ID, RestAction, ActiveFlag value, or extra assignment attributes; examples, no-ops, DELETE, or unrelated changes remain | Rebuild and revalidate before approval | Yes |
| REST submission | Error | | Exact immutable artifact, retained method/context, or Data Loader approval is missing | Complete the core workflow; no direct REST fallback | Yes |
| Loader follow-up | Error | | A submitted-job request starts preparation, or processing/scope linkage is insufficient for semantic verification | Report status through core and retain unverified outcome | Yes |
| REST verification | Error | verify_rest_assignment | Tuple or desired ActiveFlag does not match, or readback is unavailable | Stop; report mismatch or unverified completion | Yes |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_active_user | Mutation | Canonical eligible user | ora_reference_lookups.md |
| resolve_active_nondata_role | Mutation | Canonical eligible role | ora_reference_lookups.md |
| verify_user_role_membership | Mutation | Exact membership result | ora_reference_lookups.md |
| resolve_role_object_mapping | FSM mutation | Pair status and conditional mapping decision | ora_reference_lookups.md |
| resolve_active_revoke_assignment | FSM Revoke with unknown original date | Unique active assignment date and validated receipt | ora_reference_lookups.md |
| resolve_rest_assignment | REST mutation reconciliation | Complete exact tuple and valid state | ora_reference_lookups.md |
| resolve_rest_loader_contract | REST rows requiring mutation, before preparation or final-artifact validation | Current registered object and supported operation/serialization evidence | ora_reference_lookups.md |
| verify_rest_assignment | Later results/verification after terminal success for the bound REST artifact | Exact submitted tuple and desired state | ora_reference_lookups.md |
| list_rest_assignments | REST List/search or requested window | Valid requested scope and separate scope/collection completion evidence | ora_reference_lookups.md |
| get_rest_assignment | REST item retrieval | Definitive found/not-found result for the validated ID | ora_reference_lookups.md |
| count_rest_assignments | REST assignment count | Completed requested count kind and exact/estimated distinction | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When | Resolver |
|---|---|---|---|---|---|---|---|---|
| MDA.ENFORCE_DESIGN | step | 110 | design_enforcement | enforced->MDA.HANDOFF_GATE;blocked->RETURN_ISSUES | MDA.APPLY_DEFAULTS | stop | Enforce FSM design and validated package boundaries |  |
| MDA.REST_ENFORCE_DESIGN | step | 160 | design_enforcement | enforced->MDA.REST_CLASSIFY_PLAN;blocked->RETURN_ISSUES | MDA.REST_CHECK_DEPENDENCIES | stop | Enforce REST unscheduled-state and reconciliation policy before no-op classification; defer loader artifact checks to their reached stages |  |
