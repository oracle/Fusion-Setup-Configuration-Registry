# Manage Data Access for Users Input Validation

## Common Section

### Request Classification

MDA.CLASSIFY_REQUEST evaluates supplied intent locally before method selection or any Fusion lookup. A request for a submitted load's status, progress, results, errors, or verification selects loader_status; a new Grant/Revoke or ordinary assignment read/export selects assignment. Conflicting new-mutation and submitted-job intent returns invalid until scoped separately. A verification request referring to a loader job is never silently converted to an ordinary assignment GET.

At MDA.LOADER_STATUS_INPUT, require a positive numeric Request ID or core-supported UCM Content ID from the caller or one unambiguous retained submission receipt, plus the same environment. Validate the local reference shape using the core status contract; do not invent an ID. Retain requested follow-up kind and any method, artifact fingerprint, and normalized-scope linkage from the accepted submission. Missing linkage does not prevent a status lookup, but blocks later semantic verification. Return valid to MDA.LOADER_STATUS_READY or invalid to RETURN_ISSUES. Do not require mutation fields, active users/roles, new approvals, loader registration, or source artifacts for a status-only lookup.

### Method Selection Policy

MDA.SELECT_METHOD applies this policy before method-specific required-field
checks or live lookups. At this node, classify supplied intent as mutation or
customer read/export and inspect only the supplied request. Normalize an
explicit method to FSM or REST; reject conflicting or unsupported methods.

For a new mutation request, use this single routing rule:

```text
REST_RECORD_THRESHOLD = 10

if user_method is supplied:
    method = user_method
elif record_count <= REST_RECORD_THRESHOLD:
    method = REST
else:
    method = FSM
```

For automatic mutation selection, record_count must be a known, positive count
of requested assignment rows after expanding unambiguous supplied lists. Count
before deduplication, reconciliation, or no-op filtering. Exclude headers, blank
rows, mapping rows, provisioning-rule rows, and metadata; a multi-part context
is one assignment. Empty, unreadable, or ambiguously expanded input returns
invalid with the input issue; never assume zero or query Fusion to obtain the
routing count. An explicit method does not require a count for selection, but
all selected-method input checks still apply.

For ordinary customer List/search, Get, Count, or assignment verification with
no method, select REST. Mutation record_count is not applicable to these reads;
do not use returned rows or a preliminary count query to select or change their
method. Explicit FSM exports retain the shared-export workflow. Unclear
operation or export-format intent requires clarification; an explicit REST
request for an FSM configuration package is invalid.

Retain the selection and its evidence for the same request through
deduplication, no-op detection, Data Loader validation, and resume, even if the
policy later changes. Existing FSM and REST artifact handoffs use their retained
selection; they are not new omitted-method intake and generated rows do not
become the routing count. Removing no-ops or duplicates must not change the
method. A REST Task Hook invocation carries the original normalized request
and workflow_stage=task_validation; missing context blocks instead of defaulting
from the archive. If unsubmitted request scope or method instructions
change, reapply this policy to the updated user inputs, discard obsolete
method-derived fields, rerun applicable validation, and invalidate affected
previews/approvals. Resolve submitted, pending, or uncertain operations through
their existing recovery contract before planning replacement work.

After selection, explicit and derived methods use identical branch-specific
field derivation, validation, and execution. Unsupported intent or failed
validation must not switch the method automatically.

### Required Inputs

| Input | Rule | Applies When |
|---|---|---|
| Route | Optional; apply Method Selection Policy in this file | Every request |
| Operation | Classify mutation versus customer read/export for Method Selection Policy, then validate the selected method's supported operation | Every request |
| Action | Explicit Grant or Revoke per row, including an unambiguous synonym | Mutation |
| Target User Name | Explicit exact target for mutation; optional supported search predicate for reads | Mutation; REST collection read only when supplied |
| Role | Exact display name or RoleCode for mutation; optional supported search predicate for reads | Mutation; REST collection read only when supplied |
| Security Context | Explicit supported label, alias, or primary FSM carrier label | Mutation |
| Context values | Every ordered position required by the context table | Mutation |
| Effective dates | Apply FSM Grant/Revoke date rules | FSM mutation only |
| Export scope | Follow the selected task exporter's input contract | FSM export/list |
| REST read scope | Supplied predicates, assignment ID, or explicit all-assignment scope | REST read |
| REST read options | Optional output fields, sort, offset, maximum results, or count kind for the selected mode | REST read |

Trim outer whitespace only to detect blank inputs; preserve supplied business values. Do not ask REST users for dates.

### Validation Stages

MDA.CLASSIFY_REQUEST is the entry node; assignment requests reach MDA.SELECT_METHOD.
Load Method Selection Policy, retaining evidence under SKILL.md's Output Contract.
Do not infer the method from the manifest's dataloader_import_mode or a REST
lookup used by an FSM flow. Method selection makes no external calls and does not
apply method-specific business-field requirements.

MDA.VALIDATE_INPUT runs after MDA.SELECT_METHOD. Classify supplied intent and
check the required inputs for the selected method and operation only. For an
FSM mutation, apply the FSM date-intake rules; for a REST mutation, reject
explicit scheduling or effective-date intent without asking for dates. REST
reads use their own scope/options contract and do not require mutation fields.
FSM export/list uses the selected task exporter's scope contract and does not
require mutation fields. Record supplied/unknown FSM Revoke date intent, never
export during intake. Do not perform live lookups in this node.

For each mutation row, call resolve_mutation_context_label before reporting a
missing, generic, unknown, or conflicting Security Context. Load its definition
and the Security Context Mapping from ora_reference_lookups.md at this node;
do not defer this local label lookup until identity or membership validation.
Only a resolved result satisfies the context-label input requirement. Retain
the result in context_resolution. Follow the resolver outcome for clarification
or a resource failure; neither outcome permits an inferred replacement context.
Classify customer reads and FSM export/list before considering this resolver;
bypass it and its required fields for those operations. REST reads retain their
existing handling of explicit literals and patterns, including literals absent
from the mutation table.

For a resumed pre-execution validation pass, reconstruct an absent
context_resolution locally from the retained explicit context label and mapping
before checking context readiness. Preserve the selected method and environment,
each row's supplied/resolved dates and date sources, and unknown_confirmed state.
Reconstructing label evidence does not repeat an export, import, or REST write.
If an external operation was already submitted, is pending, or has an uncertain
outcome, use the existing selected-method recovery contract and recorded operation
identity; absence of this new record alone must not restart that operation.

MDA.SELECT_OPERATION uses the normalized operation and already selected method. For selected REST:

| Requested operation | Outcome |
|---|---|
| List/search, details for a supplied filter, or a requested result window | rest_list |
| Retrieve one explicit assignment ID with no additional predicates | rest_get |
| Retrieve an assignment ID combined with additional predicates | rest_list; retain the ID and every condition |
| Assignment count, including a count filtered by assignment ID | rest_count |
| Grant/Revoke | mutation |

Apply this operation table to both explicit and derived REST selections from
Method Selection Policy. Operation dispatch must not select the method again.

FSM export/list selects fsm_export. An explicit REST request for an FSM configuration-package export is invalid; do not silently reinterpret its output. Missing mutation fields never turn a read into a mutation. Validate read options against the selected operation before the resolver runs.

MDA.VALIDATE_CONTEXT_VALUES runs only after common mutation identities and membership pass. Require this row's resolved context_resolution from intake and bind exactly its mapped ordered value positions. Do not re-interpret a resolved alias or ask for the same context again. If the record is still missing at this node, or the explicit label or matched mapping row has changed, take failed->RETURN_ISSUES and stop this validation pass. Rebuild the local evidence in the next permitted pre-execution validation pass; do not jump backward in the graph or restart an external operation. Preserve values; no value existence/eligibility lookup runs in this version.

MDA.SELECT_MUTATION_METHOD dispatches the already validated FSM mutation to the
local mapping decision or the already validated REST mutation to assignment
reconciliation. It must not reselect the method or apply another method's
required fields.

### Duplicate and Conflicting Requests

Require a nonempty mutation request. Collapse only identical normalized requests. Reject conflicting Grant/Revoke intents for one complete assignment identity; do not allow input order to choose a winner. Preserve FSM date distinctions and block contradictory dates for the same portable identity rather than silently collapsing them. Retain per-row date source and unknown-date state.

### Target User — Mutations Only

- Query using the supplied username spelling.
- Compare usernames case-insensitively after retrieval.
- Retain only unsuspended accounts.
- Deduplicate by `GUID` and `UserId` before cardinality.
- One eligible account proceeds; zero blocks; more than one requires an exact `GUID` or `UserId` choice.
- Bind Oracle's returned `Username` as canonical.

### Role — Mutations Only

- Match the supplied RoleName or RoleCode exactly.
- Retain only `ActiveFlag=true` and `DataRole=N` rows.
- Deduplicate by `RoleId` and `RoleCode` before cardinality.
- One eligible role proceeds; zero blocks; more than one requires an exact `RoleId` or `RoleCode` choice.

### User-Role Membership — Mutations Only

- Match both the selected `RoleId` and `RoleCode` in the user's role assignments.
- Complete pagination before deciding membership.
- Collapse repeated physical rows for the same canonical pair.
- Zero canonical pairs means the prerequisite role is not assigned; inconsistent pairs block.

### Security Context — Mutations Only

- Use resolve_mutation_context_label at intake; its definition and the approved vocabulary are owned by `ora_reference_lookups.md`.
- Accept resolved labels without asking the user to expand or reconfirm an approved alias.
- Clarify only the resolver's missing, unknown, or conflicting result; invalid_catalog is a resource failure, not missing customer input.
- `ABC`, `XYZ`, `access`, `organization`, `org`, `unit`, `set`, `book`, and `plant` are not standalone aliases.

### Ordered Security Context Values — Mutations Only

Require the ordered positions from ora_reference_lookups.md and preserve each supplied value exactly. ContextValueHandlingStatus=not_prevalidated describes this version. Assignment comparison is permitted only through the documented FSM date or REST reconciliation/readback resolver; the policy and future-validation extension point are in ora_design_enforcement.md.

## FSM Method

### Common for Grant and Revoke

- Require the Available Role/Object Mappings table in `ora_reference_lookups.md` with exact fields `RoleCode,ObjectName,ApplicationId`.
- Reject blank RoleCode, blank ObjectName, nonnumeric ApplicationId, or duplicate `(RoleCode,ObjectName,ApplicationId)` rows.
- Resolve existence by `(RoleCode,ObjectName)` and treat all matching Application IDs as evidence for one positive pair match.
- When a Grant/reactivation pair is not listed, require exactly one deduplicated user-defined mapping row for that pair.
- When a Revoke/deactivation pair is not listed, do not generate a mapping row.

### Grant Date Handling

Preserve existing Grant date defaults and validation. A Grant row does not
require an original assignment date or the Revoke start-date resolver.

### Revoke Start-Date Resolution

Evaluate these cases for each Revoke row in order:

1. If the user supplies its original start date, validate it, preserve any valid end date, and set `StartDateSource=user_supplied`. Reject malformed dates or start later than end; do not substitute an export or a default date.
2. If the user already indicates that the date is unknown, retain `StartDateResolution=unknown_confirmed` for that row and defer resolution to `MDA.CHECK_DEPENDENCIES` after the common checks pass. Recognize equivalent intent such as “I don't know,” “not sure,” “don't remember,” “please check,” or “find it”; do not require an exact phrase or ask again.
3. Only if neither case applies, ask: “Do you know the exact date when this data role access was assigned? If yes, provide the date in YYYY/MM/DD format. If you do not know, I'll perform a read-only export of the current data access assignments to identify the original start date, then proceed with the revoke.”

An explicit unknown-date response is valid intake, not a missing-date error.
`MDA.VALIDATE_INPUT` records FSM date intent only; it must not invoke the Revoke
export resolver. The dependency gate resolves the original date after user,
role, membership, context, and role/object mapping checks pass.

For multiple FSM Revoke rows, ask one grouped question identifying only the rows
with neither a supplied date nor an unknown-date response. Accept dates for
some rows and unknown-date intent for others; never re-ask for dates already
supplied or declared unknown.

Do not treat silence as an unknown-date response. Preserve the row's state
across a lookup failure or retry. A subsequently supplied valid original date
takes precedence over its earlier unknown-date state. Do not infer that a date
or an unknown response applies to other rows unless the user's scope is clear.

### Package Input Validation

- Task code must be `ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS`.
- Mutation source must be an exact-task Template Only ZIP downloaded through `setupTaskCSVTemplateExports` and extracted before any row is constructed; `--data` and `setupTaskCSVExports` are invalid as mutation-package sources. The separate Revoke date lookup is evidence only.
- Require `ASM_SETUP_CSV_METADATA.xml` and the four expected CSV members.
- Require exact ordered headers from the same Template.
- Permit generated assignment rows in `ORA_FUN_ALL_USER_DATA_ACCESS.csv` and require `RecordTypeCode=USER_DEFINED` on each generated row.
- Permit generated rows in `ORA_FUN_SECURITY_CONTEXT_MAPPING.csv` only for deduplicated unlisted Grant/reactivation RoleCode/ObjectName pairs, using the documented user-defined field defaults.
- Require `ORA_FUN_DATA_PROVISIONING_RULES.csv` and `ORA_FUN_DATA_PROVISIONING_RULE_DETAIL.csv` to remain header-only.
- Reject a data-bearing export as a mutation baseline.

## REST Method

### Common for Grant and Revoke

Require common mutation inputs. Do not ask for, default, or send start/end dates or the original assignment date. If the user explicitly requests scheduled or date-limited access, stop with an input issue, explain that REST cannot fulfill it, and obtain the user's method selection. Do not discard date intent or switch methods automatically.

Do not require an FSM mapping decision, original StartDateActive, or FSM Template/CSV package. Assignment reconciliation supplies planning evidence; use the lifecycle table in SKILL.md. REST mutation rows additionally require the registered loader contract and exact artifact validation below. These requirements do not apply to REST customer reads, loader-status requests, or an all-no-op result.

### Grant

The proposed create/reactivate/no-op must agree with Grant. Validate the selected loader operation and intended field changes under the Grant and Revoke Artifact Rules in SKILL.md. Never use sample operations or row values as the source of assignment intent.

### Revoke

The proposed deactivate/no-op must agree with Revoke. An already-inactive exact assignment needs no payload, approval, or date question.

### REST Artifact Validation

MDA.REST_VALIDATE_ARTIFACT consumes the current registered schema resolution and original normalized request. For workflow_stage=planning with no final artifact, return needs_preparation to MDA.REST_PREPARE_READY. This terminal hands preparation to the SKILL.md Data Loader workflow; it does not approve or submit.

For workflow_stage=task_validation, require the final immutable archive and archiveSha256, same environment/task, resolved business object, retained method-selection evidence, reviewed source mappings, and same current metadata/template evidence. Read back actual prepared DAT records, not merely the workbook preview. Require exactly the requested non-no-op assignments with explicit permitted operations and the minimal fields derived in SKILL.md. Create records require canonical identity, exact ordered context values, `RestAction=POST`, and no generated assignment ID or ActiveFlag attribute. State-only PATCH records use the reconciled assignment ID without copying context fields. Detect sample/placeholder rows, unrelated sections, duplicate/conflicting tuples, unexpected columns, DELETE directives, and changed identifier precision. Account for every requested row as an exact executable row or reconciled no-op; no silent subset is allowed.

For each state-only PATCH, compare the executable DAT assignment record with fresh, complete reconciliation and the selected action. Revoke of an active assignment requires only `UserRoleDataAssignmentId=<reconciled ID>`, `RestAction=PATCH`, and `ActiveFlag=N` for a current `String(1)` target; Grant of an inactive assignment uses `ActiveFlag=Y`. Required DAT section structure is not an extra assignment attribute. Reject extra assignment attributes, wrong IDs, wrong state values, and records for no-op rows. If current metadata declares a different type or encoding, resolve it before preview.

For every REST write, return the ordered MDA.REST_LOADER_CONTRACT and MDA.REST_VALIDATE_ARTIFACT rule results through the normal Task Hook preview. Bind them to the selected request, environment, current schema, and final archive fingerprint. Missing or mismatched context blocks handoff. Do not add a separate approval gate. This requirement applies only to REST writes, never to FSM, REST customer reads, loader-status follow-ups, or all-no-op requests.

If fresh preapproval reconciliation changes an operation/key/no-op decision, return blocked and require a new artifact and validation. Do not fix the archive within Task Hook, regenerate samples, re-count rows for method selection, or call the loader recursively. For an intact artifact return validated to MDA.REST_HANDOFF_GATE. An unknown workflow stage or missing re-entry evidence returns blocked. After approval, submission follows core's immutable-envelope checks without repeating this validation.

### Read Input Validation

Separate predicate validity from collection completeness under Read Collection Selection in ora_reference_lookups.md. A username alone is sufficient and never requires a role; requested output fields remain optional. Accept finite exact user/role sets and grouped AND/OR combinations without requiring one finder to cover the whole expression. A valid q-only expression may execute as a REST GET, but its response remains observed-only until the requested collection is independently shown exhaustive; an empty HTTP 200 is not a zero finding. Do not demand the complete mutation tuple.

| Input | Validation |
|---|---|
| Read mode | List/search, Get one assignment, or Count |
| Search predicates | Supported fields, type-correct operators, and explicit grouping under Read Scope Resolution; standalone unary NOT returns invalid_scope with unsupported_query_operator before REST invocation |
| Assignment ID | Valid integer representation within the documented int64 contract; preserve full precision without floating-point conversion |
| Fields | Optional documented readable attributes; reject unknown attributes |
| Sort | Optional documented sortable attributes with asc/desc directions |
| Offset | Nonnegative integer |
| Maximum results | Positive integer when supplied |
| Count kind | Exact or estimated |

No individual user, role, context, or value filter is mandatory. Require a predicate, assignment ID, or explicit all-assignment scope; ask only when scope is genuinely missing. Validate query structure without requiring a unique matching user, role, context, or assignment. Multiple matches are valid; zero is definitive only for a completed collection scope.

Interpret a request for assignments for several named users as a set/OR scope and generate `Userrf IN (...)` when one shared display-role finder applies; otherwise cover each exact user with a finder-bound GET. Preserve an explicitly stated Boolean AND on one assignment instead of silently rewriting its logic. Apply the same full-expression rule to user/role combinations and grouped alternatives.

Normalize known exact security-context business labels and aliases through the owning context table in ora_reference_lookups.md. Preserve explicitly supplied REST literals, including those absent from the local mutation table, and preserve requested patterns. Never infer a context from a value. Companion-value predicates may be supplied independently; do not require complete multi-part mutation identity.

List/search accepts fields, sort, offset, and maximum results. Get accepts fields and one assignment ID; additional predicates select List/search. Count accepts the search scope and count kind and uses its own internal ID projection. A requested row projection, sort, or window on Count, or a window/sort on Get, requires clarification or invalid_scope; never silently ignore the option or count only a page as the complete scope. Do not silently discard unsupported filters, fields, ordering, paging, grouping, or operators.

Customer reads skip mutation-only active-user, active-role, membership, context-value arity, effective-date, and package checks. Authentication and the caller's read privileges remain required. These exemptions do not apply to reconciliation or verification supporting a mutation.

## Route Validation

| Request | Result |
|---|---|
| Omitted method | Apply Method Selection Policy in this file, then the selected branch below |
| Selected FSM mutation | FSM validation and package handoff |
| Selected FSM export/list | Shared data-bearing exact-task export |
| Selected REST unscheduled mutation | REST reconciliation, contract resolution, artifact preparation, and Data Loader validation |
| Submitted loader status/results/verification | Loader reference validation and status handoff; no new mutation |
| REST scheduled/date-limited request | Input issue; obtain method selection before proceeding |
| Selected REST List/search or result window | rest_list with supplied scope and validated options |
| Selected REST item retrieval with ID only | rest_get with optional output fields |
| Selected REST assignment count | rest_count with supplied scope and exact/estimated kind |
| Conflicting methods or unsupported scope | Block with the exact input issue |

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Direct-assignment intent | Action, Target User Name, Role, Security Context label or alias, ordered values | Block validation after context-label resolution | Ask only for genuinely unresolved business inputs; report mapping-source failures separately | Mutation intake | resolve_mutation_context_label |
| FSM Grant dates | Optional start/end dates | Apply permitted FSM defaults after dependencies | Validate supplied dates | FSM Grant | |
| FSM Revoke date intent | Original StartDateActive or explicit unknown response; optional end date | Ask the existing grouped date question only for unresolved intent | Follow FSM Revoke Start-Date Resolution; resolve unknown dates at MDA.CHECK_DEPENDENCIES | FSM Revoke | |
| FSM package source | Exact-task Template Only ZIP, metadata, four members | Block handoff | Download, extract, and validate under the SKILL.md FSM contract | FSM mutation | |
| FSM mapping reference | Existing valid local mapping table | Block package construction | Correct the table contract | FSM mutation | resolve_role_object_mapping |
| REST unscheduled intent | No explicit effective dates or scheduling | Block incompatible intent | Explain this asynchronous REST workflow's date limitation and obtain method selection | REST mutation | |
| REST loader contract | Current registered business object, template, attributes, keys, and the selected operation's minimal source shape | Block mutation preparation | Follow the selected core sample/metadata workflow and REST Loader Contract Resolution | REST rows requiring a mutation | resolve_rest_loader_contract |
| REST final artifact | Immutable archive, digest, exact rows, method evidence, and matching contract/artifact results | Block Task Hook approval | Prepare through core.data-loader before final validation | REST Task Hook re-entry | |
| Loader follow-up reference | Request ID or UCM Content ID and environment | Request the missing reference | Reuse one unambiguous accepted submission receipt | Loader status/results/verification | |
| REST read scope/options | Predicate, assignment ID, or explicit all-assignment scope; applicable optional read controls | Clarify genuinely missing scope or incompatible options | Follow Read Input Validation; never require missing mutation fields | REST read | |
| FSM export scope | Selected task, environment, shared-exporter scope | Block export readiness | Complete the shared-exporter prerequisites | FSM export/list | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Required business values | Require explicit mutation fields without inference | Mutation | |
| Explicit context label | Require resolved context_resolution before accepting or questioning the context input; preserve the supplied values separately | Mutation intake | resolve_mutation_context_label |
| Method/operation shape | Follow Method Selection Policy in this file and validate supported selected-method combinations | Every request | |
| Ordered context values | Require exactly the mapped positions and retain supplied values | Mutation | |
| Grant date shape | Validate explicit dates and reject contradictions | FSM Grant | |
| Revoke date shape | Require valid original date/source before construction; explicit end date cannot precede it | FSM Revoke | |
| Package shape | Require exact Template metadata/members/ordered headers and permitted generated rows | FSM mutation | |
| REST date shape | Do not collect dates; report explicitly requested dates as unsupported for REST | REST mutation | |
| REST artifact shape | Match exact create or state-only PATCH records, desired ActiveFlag value, and no-op exclusion against the selected request, current loader metadata, and immutable artifact readback | REST Task Hook validation | |
| REST read shape | Validate the supplied scope, typed predicates, full-precision ID, and mode-specific options under Read Input Validation; no mutation identity requirements | REST customer read | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When | Resolver |
|---|---|---|---|---|---|---|---|---|
| MDA.CLASSIFY_REQUEST | decision | 1 | evaluate_result | assignment->MDA.SELECT_METHOD;loader_status->MDA.LOADER_STATUS_INPUT;invalid->RETURN_ISSUES | none | stop | Classify supplied assignment versus submitted-loader follow-up intent locally before lookups |  |
| MDA.LOADER_STATUS_INPUT | step | 2 | validate_input | valid->MDA.LOADER_STATUS_READY;invalid->RETURN_ISSUES | MDA.CLASSIFY_REQUEST | stop | Validate locally supplied or retained loader reference and environment; no mutation prerequisites |  |
| MDA.SELECT_METHOD | decision | 5 | evaluate_result | fsm->MDA.VALIDATE_INPUT;rest->MDA.VALIDATE_INPUT;invalid->RETURN_ISSUES | MDA.CLASSIFY_REQUEST | stop | Apply Method Selection Policy in this file before method-specific input checks; preserve the selected method for the same request during handoff or resume |  |
| MDA.VALIDATE_INPUT | step | 10 | validate_input | valid->MDA.APPLY_COMMON_DEFAULTS;invalid->RETURN_ISSUES;failed->RETURN_ISSUES | MDA.SELECT_METHOD | stop | Classify intent; for mutations resolve the explicit context label before any missing-context decision; check selected-operation inputs without external calls | resolve_mutation_context_label |
| MDA.SELECT_OPERATION | decision | 20 | evaluate_result | mutation->MDA.RESOLVE_USER;fsm_export->MDA.FSM_EXPORT_CHECK;rest_list->MDA.REST_LIST;rest_get->MDA.REST_GET;rest_count->MDA.REST_COUNT;invalid->RETURN_ISSUES | MDA.APPLY_COMMON_DEFAULTS | stop | Branch on normalized operation and selected method; reads bypass mutation-only checks |  |
| MDA.VALIDATE_CONTEXT_VALUES | step | 60 | validate_input | valid->MDA.SELECT_MUTATION_METHOD;invalid->RETURN_ISSUES;failed->RETURN_ISSUES | MDA.VERIFY_MEMBERSHIP | stop | Require the unchanged resolved intake context and bind exact ordered values; no existence prevalidation |  |
| MDA.SELECT_MUTATION_METHOD | decision | 70 | evaluate_result | fsm->MDA.RESOLVE_ROLE_OBJECT_MAPPING;rest->MDA.REST_RECONCILE;invalid->RETURN_ISSUES | MDA.VALIDATE_CONTEXT_VALUES | stop | Dispatch the already selected mutation method after common checks; never reselect it |  |
| MDA.REST_VALIDATE_ARTIFACT | decision | 180 | validate_input | needs_preparation->MDA.REST_PREPARE_READY;validated->MDA.REST_HANDOFF_GATE;blocked->RETURN_ISSUES | MDA.REST_LOADER_CONTRACT | stop | REST writes only: match final DAT records and archive digest to fresh reconciliation, current schema, and request; never rebuild or submit |  |
