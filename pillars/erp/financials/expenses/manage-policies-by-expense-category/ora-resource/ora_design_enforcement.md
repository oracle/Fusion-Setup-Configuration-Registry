# Meals design enforcement

Use [ordinary Meals execution](../references/ordinary-meals-execution.md) for
the supported workbook and governed workflow.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Resulting policy groups | Validate every compatible parent and all its rates, including retained siblings and effective periods |
| 2 | Candidate integrity | Selected rows and exact parent context only; preserve baseline metadata/nonCSV bytes |
| 3 | Native handoff | Exact final artifact evaluation, native preview and later core approval |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Meals limits | Error | | Neither enabled; missing enabled amount; populated disabled amount; negative/nonfinite number | Supply applicable amounts; no implicit clearing | User input only |
| UPPER | Error | | Any warning/display/prevention control Yes | Use controls No or supported VIOLATION | User input only |
| VIOLATION | Error | | Display without warning; missing active tolerance; negative value; warning not below error when both exist | Correct resulting controls/tolerances; unchanged inactive stored values may remain | User input only |
| Policy/rate groups | Error | | Existing key/status/currency/determinant change, ambiguous/duplicate full or NoStart key, reversed/overlapping inclusive periods, or missing parent/rate | Exact compatible DRAFT policies/rates, SINGLE, role/location disabled; multiple policies and nonoverlapping rates allowed | No automatic closing/deleting or key repair |
| Every candidate | Error | resolve_policy_currency | Missing bound evidence, failed planner or final artifact/metadata mismatch | Stop before native handoff; no trial/override | No |
| Expanded settings/batches | Warning | | None when local/source checks pass | Retain pending-live disclosure for batches, nonblank EndDate and expanded settings; no atomicity or broad qualification claim | No readiness promotion |

After native approval verify retained integrity only: do not rebuild, requery
references or rerun rules. Partial results/metadata drift require a human
completion/retry decision; never replay, repair, clean up or roll back automatically.

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_policy_currency | Every selected parent create/update, including rate-only update | Bound currency eligibility | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| POLICY.DESIGN | step | 50 | design_enforcement | passed->POLICY.RULES_COMPLETE;failed->POLICY.RETURN_ISSUES | POLICY.DEFAULTS | stop | This task is requested |
