# Meals dependency readiness

Classification: Oracle Highly Restricted.

Use [ordinary Meals execution](../references/ordinary-meals-execution.md) for
the supported workbook and governed workflow.

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| BASELINE | Fresh exact-task baseline | Yes | Every request | Satisfied only after binding checks | Approved shared export and actual same-day download at qualified target/release | | Before-state and schema authority | Use declared export route; retain process ID on timeout | Before-images only |
| CURRENCY | Eligible single currency | Yes | Create/update including retained parent | Verify | Operation-bound reference evidence | resolve_policy_currency | Current target eligibility | Complete reference_lookup before building | No generated input |
| PARENT | Unique compatible parent per rate | Yes | Every rate | Satisfied only on exact resolution | Included parent on create or baseline on update | | Each rate resolves its own parent; validate every retained sibling | Repeat exact parent Policy Name; use distinct nonoverlapping periods with full rate keys | Exact parent context once per selected parent |
| CONTRACT | Supported Meals runtime | Yes | Native handoff | Satisfied only after validation | Shipped source-bound profile and final candidate checks | | No historical trial or readiness override | Correct unsupported inputs; preserve native gates | Validated candidate only |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| POLICY.DEPENDENCIES | step | 30 | resolve_dependency | passed->POLICY.DEFAULTS;failed->POLICY.RETURN_ISSUES | POLICY.REFERENCES | stop | This task is requested |
