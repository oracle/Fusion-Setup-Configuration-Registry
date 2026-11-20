# Meals dependency readiness


Use [ordinary Meals execution](../references/ordinary-meals-execution.md) for
the supported workbook and governed workflow.

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| BASELINE | Fresh exact-task baseline | Yes | Every request | Satisfied only after binding checks | Approved shared export and actual same-day download at qualified target/release | | Before-state and schema authority | Use declared export route; retain process ID on timeout | Before-images only |
| CURRENCY | Eligible single currency | Conditional | Owning monetary branch consumes supplied or retained parent currency, including rate-only selections | Verify | Operation-bound reference evidence | resolve_policy_currency | Current target eligibility; Airfare has no currency input and nonmonetary Miscellaneous PERCENT may require no currency | Complete applicable reference_lookup before building; never invent a currency for an exempt branch | No generated input |
| PARENT | Unique compatible parent per rate | Yes | Every rate | Satisfied only on exact resolution | Included parent on create or baseline on update | | Each rate resolves its own parent; validate every retained sibling | Repeat exact parent Policy Name; use distinct nonoverlapping periods with full rate keys | Exact parent context once per selected parent |
| CONTRACT | Owning reviewed category runtime | Yes | Native handoff | Satisfied only after validation | Shipped source-bound category profile and final candidate checks | | No historical trial or readiness override | Correct unsupported inputs; preserve native gates | Validated candidate only |
| ENTERTAINMENT-CURRENCY | Rate or attendee-count threshold currency | Conditional | Entertainment selected with applicable currency | Verify | Operation-bound reference evidence | resolve_policy_currency | Currency eligibility is target-specific | Capture each supplied or retained currency before candidate generation | No generated input |
| ENTERTAINMENT-PROFILE | Reviewed Entertainment operation profile | Yes | Entertainment selected | Satisfied only after validation | Entertainment source-bound contract and resulting-state checks | | Static authoring remains live-pending | Preserve native preview, approval and reconciliation gates | Validated candidate only |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| POLICY.DEPENDENCIES | step | 30 | resolve_dependency | passed->POLICY.DEFAULTS;failed->POLICY.RETURN_ISSUES | POLICY.REFERENCES | stop | This task is requested |

Accommodations follows the same task workflow with category-specific parent/rate
identities and currency evidence. Daily Limit? must remain Yes on every populated
Accommodations policy row; it is a grey workbook-only indicator, never a CSV
flag. Each resulting rate requires DailyLimit. Role, location, seasonal rate and
gender determinants are excluded; reject incompatible retained settings. Use
[Accommodations evidence](../references/accommodations-profile.json) for the
local authoring extension and its mandatory live reconciliation boundary.
