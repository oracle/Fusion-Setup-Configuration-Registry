# Manage Ledger Sets Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Identity and intent | Distinguish create, existing-object review and explicit update; reject existing-set deletion and deletion-equivalent cleanup/replacement. Ledger sets group processing/reporting and do not replace data access security. |
| 2 | Effective membership | Validate every direct member and expanded leaf against the shared accounting structure. |
| 3 | Classification | Validate currency and ledger-family restrictions before first assignment; preserve established classification. |
| 4 | Default and DFF | Confirm requested default remains eligible and every requested context/segment is deployed. |
| 5 | Artifact boundary | Hand the exact validated FSM bytes to core.data-loader; its approval is authoritative and must not be duplicated by this task graph. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Any task check or operation | Error |  | Requested or delegated route would access Fusion UI, scrape browser state, use screenshots/grid extracts as runtime evidence, issue ad hoc SQL or call an undeclared endpoint | Use only the declared FSCR endpoint/export/loader route. Return ui_execution_prohibited for a UI request; report missing_framework_evidence when no supported source supplies a required fact | No |
| Existing ledger-set deletion, any route | Error |  | Request would delete an already-created set, including cleanup, purge, reset, rollback-by-deletion or delete-and-recreate | Preserve the set and return ledger_set_deletion_prohibited; do not suggest UI, REST, another adapter or import as a bypass. General test/import approval and Oracle delete capability do not waive this FSCR policy | No |
| FSM candidate or delegated action | Error | inspect_ledger_set_package | Intended changes or actual row/control semantics would delete an existing parent set, or use replacement/removal as a deletion workaround | Reject the candidate before loader handoff and preserve the parent. Individual assignment removal remains a distinct supported update with a nonempty final membership; ordinary scoped-create rows are not deletion instructions | No |
| Create | Error | find_ledger_set_by_exact_name | Any exact L/S match, failed/incomplete query, conflicting source facts or known restriction invalidating the selected setup check | Resolve conflict/access; fresh completed zero results permit scoped preparation, not a global uniqueness claim | Before candidate approval |
| FSM create supplies or derives ShortName | Error | find_ledger_set_by_exact_short_name | Any exact short-name match, failed/incomplete query or known restriction invalidating this check | Resolve a distinct short identity; preserve queried-scope limitations in the preview | Before candidate approval |
| Update/review | Error | find_ledger_set_by_exact_name | No exact S object, ambiguous distinct identities or stable ID mismatch | Resolve the intended ledger set | Before candidate approval |
| All final membership | Error | find_ledger_by_exact_name | Effective members differ from the set in ChartOfAccountsId, PeriodSetName or AccountedPeriodType, or an attribute is unproved | Correct members or use a separately compatible set | Before candidate approval |
| Selected COA import keys | Error | resolve_ledger_set_chart_of_accounts | Selected chart is disabled/ambiguous, code missing, or StructureInstanceNumber differs from member ChartOfAccountsId | Resolve the exact chart; never use StructureInstanceId as ChartOfAccountsId. Reject a conflicting explicit user choice; do not silently replace it with the member chart | Before candidate approval |
| Selected calendar import keys | Error | resolve_ledger_set_accounting_calendar | Display/internal names, accounting calendar type or period type fail the selected member compatibility check | Resolve the exact selected calendar and period tuple. Reject a conflicting explicit user choice; do not silently replace it or alter the member ledger | Before candidate approval |
| Balancing column supplied from lookup | Error | resolve_ledger_set_balancing_segment_column | Column comes from a different COA, conflicting member facts or guessed ordinal position | Resolve consistent selected-COA structural evidence | Before candidate approval |
| FSM create structural values | Error | resolve_ledger_set_structural_profile | Scoped primary identity/alias check fails, selected structure differs, required balancing pair is unresolved, facts conflict or primary accounting options were copied | Validate exact scoped structural values and packaged field dispositions; conditional COA joins address only a named required gap | Before candidate approval |
| Nested assignment | Error | inspect_ledger_set_evidence | Self-reference, cycle, incomplete expansion, inconsistent direct/flattened membership or a nested set whose classification differs from the parent | Supply a complete hierarchy with matching set classifications; do not rely only on leaf currency compatibility | Before candidate approval |
| Currency-specific or GAAP view | Error | inspect_ledger_set_evidence | Any effective leaf currency differs from LedgerSetCurrencyCode, or a nested set's classified currency conflicts | Choose compatible members; use None for an intended mixed-currency processing set before initial creation | Before candidate approval |
| GAAP view | Error | inspect_ledger_set_evidence | Effective membership has other than exactly one primary, includes an unrelated or ineligible secondary/other category, or lacks relationship/level eligibility evidence | Use exactly one primary and its associated eligible secondary ledgers. Treat a verified SUBLEDGER conversion level as eligible under the configured FSCR policy without a per-run eligibility waiver; resolve other levels through existing current declared metadata/export evidence | Before candidate approval |
| Existing assignment exists | Error | inspect_ledger_set_evidence | Requested Classification differs from current Classification | Preserve classification or create a separately named new set; removing all members is not a workaround | No |
| Existing structure/currency update | Error | inspect_ledger_set_evidence | Requested change is unsupported by current declared task metadata or lacks same-release import evidence and a compatible final membership | Preserve the field or obtain supported framework change evidence before preparation; UI editability is not an execution contract | Only with supported evidence |
| Default Ledger supplied or existing default removed | Error | inspect_ledger_set_evidence | Default is absent from eligible final leaf members, is a set rather than eligible ledger, or eligibility is unproved | Select an eligible member or explicitly clear/replace the default with supported import evidence | Before candidate approval |
| DFF supplied | Error | inspect_ledger_set_evidence | Context/segment mapping, requiredness or value-set validation is unproved | Obtain deployed metadata and exact import mapping | Before candidate approval |
| FSM write | Error | inspect_ledger_set_package | Candidate carries unrelated rows, guessed placeholders, unresolved foreign keys or a changed digest | Prepare only intended rows using current template contract; rerun Task Hook after any change | Before loader approval |
| FSM create | Error | resolve_ledger_set_create_profile | Current template has an unclassified field, incompatible XML type, known required-value difference or unsupported requested operation | Apply the packaged contract; report the concrete field difference. Do not block because a project/environment/COA has no historical profile | Before loader approval |
| Packaged contract disclosure | Error | resolve_ledger_set_create_profile | Preview claims universal Oracle acceptance, automatic blank-cell defaulting, global uniqueness or complete verification without evidence | Record base-profile ID, explicit values/omissions, current lookup scope and server/persisted verification still required | Before loader approval |
| Assignment removal or field clear | Error | inspect_ledger_set_package | Candidate relies on omission to delete/clear without proven task-specific import semantics | Obtain a controlled same-release import/re-export result for the explicit operation; retain current values otherwise | Only after proven contract |
| Regression qualification | Error |  | Evidence claims a policy, ambiguity, DFF value-set or GAAP eligibility restriction was server-tested when only a local rejection, absent fixture or multiply invalid request was observed | Distinguish assisted rule evaluation, automated validation, Oracle import outcome and persisted-state comparison. Record untested or unqualified behavior explicitly | No unsupported coverage claim |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| find_ledger_set_by_exact_name | Identity and duplicate checks | Stable identity, object type, fresh precheck result and queried scope | ora_reference_lookups.md |
| find_ledger_set_by_exact_short_name | Explicit or derived short identity on create | Independent fresh short-name precheck and scope disclosure | ora_reference_lookups.md |
| find_ledger_by_exact_name | Member/default identity and structure | COA/calendar/period tuple and actual returned currency/type/category | ora_reference_lookups.md |
| resolve_ledger_set_chart_of_accounts | COA import keys on create or supported structure change | Enabled chart code and exact StructureInstanceNumber agreement | ora_reference_lookups.md |
| resolve_ledger_set_accounting_calendar | Calendar import keys on create or supported calendar change | Display/internal keys, accounting type and member period agreement | ora_reference_lookups.md |
| resolve_ledger_set_balancing_segment_column | Candidate needs the balancing column | Consistent selected-COA column | ora_reference_lookups.md |
| resolve_ledger_set_structural_profile | FSM create structural handling | Exact primary-scoped structural fields and explicit omissions; conditional COA role joins only for a named required gap | ora_reference_lookups.md |
| resolve_ledger_set_create_profile | FSM create initialization and field handling | Packaged defaults/omissions and current template compatibility | ora_reference_lookups.md |
| inspect_ledger_set_evidence | Membership, classifications, defaults, DFF and update restrictions | Direct/effective members, current fields, relationships, eligibility and deployed metadata | ora_reference_lookups.md |
| inspect_ledger_set_package | Candidate graph, parent preservation and assignment-remove/clear contracts | Exact task package, intended deltas, destructive row/control semantics, shape and immutable digest | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MLS.ENFORCE_DESIGN | decision | 50 | design_enforcement | pass->MLS.EXECUTION_GATE;blocked->MLS.HANDLE_ERROR | MLS.APPLY_DEFAULTS | stop | Validate all applicable design rules, including framework-only execution, prohibition of existing-set deletion and parent-preserving candidate semantics, before core presents approval. No Fusion mutation occurs here. |

## SUBLEDGER Eligibility Policy

SUBLEDGER is an accepted secondary conversion level for GAAP view under the user-approved FSCR policy. Apply it only to a currently resolved secondary associated with the single selected primary, using inspect_ledger_set_evidence. Keep the existing currency, chart/calendar/period, relationship, default-ledger, package, approval and verification checks. Missing or conflicting level/relationship evidence still blocks. This rule does not classify other conversion levels as ineligible and does not claim that an Oracle import or release qualification has passed.
