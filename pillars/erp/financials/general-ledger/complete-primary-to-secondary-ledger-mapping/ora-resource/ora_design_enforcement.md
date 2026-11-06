# Complete Primary to Secondary Ledger Mapping Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Confirm lifecycle boundary | Treat this task as mapping policy only; exclude Review and Submit, activation, conversion enablement, and period opening |
| 2 | Confirm relationship design | Compare conversion level, structures, currencies, current relationship state, and existing rules |
| 3 | Enforce conditional choices | Require mapping only for different COAs, rate type only for different currencies, and BSV inputs only for selected controlled conversion |
| 4 | Enforce supported scope | Preserve existing journal rules; permit only the proven controlled catch-all role; hand off custom or unsupported option paths to the UI |
| 5 | Enforce smallest delta | Preserve package closure, aliases, manifest, unchanged rows, blanks, and service-owned fields |
| 6 | Build preview | Show semantic and raw diff, warnings, resolver receipts, handoffs, exclusions, and checksum-bound approval request |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Always | Error | Exact scoped relationship and child tuples | Source and target do not form exactly one current relationship, or the mapping delta changes exported OrgIdTrans, RelationshipTypeCode, or any child parent reference | Correct the scope or obtain a fresh matching export; preserve exported keys for Name4/rate changes and handle any separately evidenced key transition outside this baseline | Yes, before preview |
| COAs differ | Error | Exact directional COA mapping | No single From source to To target mapping exists | Create or select the mapping through the supported Financial Reporting Structures workflow, then re-export | Yes, through owning setup workflow |
| COAs are the same | Warning | Exact relationship comparison | Accountable GL-781805 decision is absent | Explain the warning and record accept or cancel; keep Name4 blank on accept | Yes, decision only |
| Currencies differ | Error | Exact conversion rate type | Rate type is absent, disabled, ineffective, ambiguous, or resolver failed | Ask the user for an exact eligible rate type | Yes, before preview |
| Controlled BSV conversion is selected | Error | Exact balancing value set and effective values | Value set, source value, Meaning, effectivity, or semantic uniqueness fails | Correct the value selection; never author a guessed or casual display string | Yes, before preview |
| Matching controlled Journal-secondary path | Warning | Existing rule set | Controlled Other/Other Y/Y catch-all is added or retained | Explain that all unselected source/category combinations are included and let rejection trigger UI handoff | Yes, user may reject direct baseline |
| Custom journal policy is requested | Error | Existing rule set only | Direct selective source/category authoring lacks an exact supported contract or access | Preserve current rules; configure custom include or exclude rules in the Complete Primary to Secondary Ledger Mapping UI and re-export | No direct CSV fix |
| Tree, replication, segment-type, DFF, or other optional family is requested | Error | Exact same-role evidence | Export headers and same-role evidence do not fully define the requested combination | Use the named task UI, then re-export; do not create another formal TBD | No direct CSV fix |
| Any proposed write changes lifecycle status | Error | None | Delta includes enablement, activation, submission, confirmation, period opening, or conversion start | Remove the field and keep this task mapping-only | Yes, remove before preview |
| Any dependency member changes without ownership | Error | Exact package diff | Root, ledger aliases, journal config detail, legal-entity definition, manifest, or unrelated rows changed | Rebuild from the exact baseline with the smallest owned delta | Yes, before preview |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_primary_secondary_relationship | Always | Exact parent tuple; structures; currencies; level; current OrgIdTrans | ora_reference_lookups.md |
| resolve_directional_coa_mapping | Structures differ | Name4 and exact source-to-target direction | ora_reference_lookups.md |
| find_conversion_rate_type_exact | Currencies differ | AlcDefaultConvRateTypeTrans and eligible display receipt | ora_reference_lookups.md |
| derive_balancing_value_set | Controlled BSV conversion is selected | ValueSetCode and balancing segment role | ora_reference_lookups.md |
| verify_balancing_value_set_exact | Controlled BSV conversion is selected | Exact current value-set identity agreeing with the source balancing role | ora_reference_lookups.md |
| find_balancing_segment_value_exact | Each controlled BSV row | SourceSegmentValue, Meaning, and effectivity | ora_reference_lookups.md |
| resolve_existing_conversion_rules | Existing rules, controlled catch-all, or custom policy decision | Full rule semantic keys, flags, and parent aliases | ora_reference_lookups.md |

## Business Intent Advisory

| Question | Guidance |
|---|---|
| Why is the secondary different? | Record whether the difference is currency, COA, calendar, accounting representation, adjustment-only purpose, or another approved design driver; the reason determines conditional dependencies |
| Same COA | Recommend intentional blank mapping after the GL-781805 decision; do not add a mapping merely to populate Name4 |
| Different currency | Require the business to choose the rate type based on reporting policy; do not propose Corporate as an independent default |
| Journal policy | Do not ask in the baseline. Explain any controlled catch-all in preview. If the user wants selective policy, use the task UI and re-export |
| BSV replication or conversion | Explain downstream accounting and reversibility impact before opt-in; resolve only exact effective values in the correct source value set |

## Preview and Approval Contract

| Preview Item | Required Evidence |
|---|---|
| Identity | Environment, release, task, accounting-configuration scope, package provenance, and baseline checksum captured at runtime rather than embedded in this resource |
| Intake | Raw and normalized inputs plus user, conditional, resolver-derived, export-derived, controlled-default, intentional-blank, and service-owned classifications |
| Resolution | Resolver name, source, exact filter or key, page completion, match count, eligible result, and auth/transport state |
| Package | All member checksums; actual headers/order; manifest validation; alias symmetry; exact row add, update, and delete counts; parent-key changes |
| Mapping diff | Name4 decision, rate-type decision, OrgId transition, child-rule parent update, journal-rule semantics, BSV rows, warnings, and unrelated-row check |
| Boundary | UI handoffs; open-contract impacts; explicit exclusion of Review and Submit, activation, conversion enablement, and period opening |
| Approval | Explicit accountable approval bound to the final preview checksum; any input, resolver, package, or diff change invalidates approval and requires a new preview |
| Verification export isolation | After a successful approved import, if Fusion cannot source-filter the populated identical-task export, stage it only in transient untracked storage, exact-filter the approved primary-secondary relationship and its exact parent-linked rules, persist only the filtered comparison, and discard the unfiltered package and every unrelated row. Fail closed on direction, identity, linkage, or cardinality ambiguity; never reuse verification rows as design input, defaults, or a carrier |

## Contract Disposition

| Contract | Status | Mapping Consequence |
|---|---|---|
| TBD-GL-01 | Open; outside the FSCR create and mapping paths | Mapping never changes an accounting method. A newly created ledger uses Standard Accrual; if another method was requested, its primary- or secondary-options UI handoff and same-scope re-export must be complete before Review and Submit |
| TBD-GL-07 | Open | Review and Submit remains a separate read-only, non-automated boundary |
| GL-03 | Closed | Proven package shape covers Subledger physical aliases and relationship; do not invent design-specific journal rows |
| GL-09 | Closed | Optional families are opt-in; preserve or disabled baseline plus UI handoff |
| GL-12 | Closed | Posting cutoff baseline is N with blank timezone/date; explicit enablement belongs in the ledger-options UI |
| GL-13 | Closed | Preserve rules; controlled catch-all only for matching role; custom and unsupported Subledger rules use UI handoff |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| GLMAP.ENFORCE | decision | 50 | design_enforcement | pass->GLMAP.ERROR_POLICY;blocked->GLMAP.RETURN_ISSUES | GLMAP.DEFAULTS | stop | A complete proposed delta exists |
