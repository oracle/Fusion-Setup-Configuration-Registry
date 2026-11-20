# UN Number Design Enforcement

Original input is the authority for preservation; Fusion is the authority for
Hazard Class identity. No regulatory classification, inactive-date restriction,
write privilege or Data Loader registration is inferred from a lookup.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Association evidence | Applicable create/update association has a complete, unique, matching lookup result |
| 2 | Preserve input | Compare the separate prepared record against original input allowing only declared enrichment/context separation and create/update empty-date omission |
| 3 | Preserve captured source | Captured records remain immutable; any needed correction cancels and restarts loader validation |
| 4 | Handoff | Preserve operation controls and pass only loader-ready writable data to Data Loader review |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Create/update with name or non-null ID | Error | resolve_hazard_class | Missing, incomplete, ambiguous or conflicting identity evidence; result from a different environment or artifact validation cycle | Resolve exactly one agreeing Hazard Class before preparation; no fabricated ID | Only documented preparation enrichment |
| Preparation after lookup | Error | | Supplied ID changed; null overwritten; name sent as writable data; missing ID filled without unique evidence; any other input value/type changed | Preserve original input and build a separate loader-ready record with only resolved ID enrichment, HazardClass context separation and empty-date omission | No silent corrections |
| Captured-record validation | Error | | Any proposed edit to captured data, or a missing/incorrect association needing correction | Cancel pending validation cycle, prepare corrected source and validate afresh; ruleResults cannot mutate records | No artifact modification |
| Every row | Error | | ID fabricated, operation inferred from ID, RestAction rewritten, or name/code changed by a regulatory assumption | Preserve approved business data and operation controls | No |
| Intent preservation | Error | | Explicit intent lost or changed during handoff, intent leaked into business fields, or Description fabricated to bypass input requiredness | Preserve scoped intent and its source separately; correct missing input before fresh preparation and approval | No |
| Delete rows | Error | | Association lookup attempted, explicit DELETE lost, extra business fields removed silently, or conflicting operation instructions | Use existing ID-only delete contract and bypass association lookup | No |
| Source contract incomplete | Error | | Required rule/lookup contract unresolved or compiled plan not ready | Correct source, recompile, then plan again | No bypass |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_hazard_class | Create/update with name or non-null ID | Unique verified identity, supplied-key agreement and current scoped evidence | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| UN.CHECK_DESIGN | decision | 30 | design_enforcement | valid->UN.HANDOFF;blocked->UN.HANDLE_ISSUES | UN.PRESERVE_VALUES | stop | Check conditional association evidence, approved preparation transformations and captured-record immutability before Data Loader review |
