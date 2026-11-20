# Reference Lookups

Task scope: AP_MANAGE_AGING_PERIODS / Manage Aging Periods. Use a fresh exact-task export to match existing records. Run Book supplies inputs. Create and update are supported. Submit the validated package through Data Loader after its required approval.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| match_aging_period_by_name | update or create existence check | Fresh exact-task current export AP_AGING_PERIOD.PeriodName | Exact case-sensitive PeriodName; do not fuzzy match | Existing row and original values; preserve unrelated rows | Create requires zero; update requires exactly one; duplicates stop |
| match_aging_detail_by_period_and_sequence | line operation | Fresh exact-task AP_AGING_PERIOD_LINE.csv parent PeriodName and PeriodSequenceNum | Exact composite parent name and integer sequence | Existing line and original values | Create requires zero; update requires exactly one; duplicates stop |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| No supported public lookup contract reviewed | Do not invent a REST path; use the authorized export baseline for matching and retain FSM import qualification. |
| DFF context or segment requested | Accept user-supplied DFF storage values unchanged; configured context/value validation is owned by FSM. No domain lookup/preflight is required. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AGING.MATCH | decision | 30 | evaluate_result | pass->AGING.DEPENDENCY;missing->AGING.RETURN_ISSUES;ambiguous->AGING.RETURN_ISSUES | AGING.DEFAULTS | stop | create or update |

## Selected Fusion target and authentication profile

Before preparing exports or task data, retain the independently confirmed Fusion
environment name and credential-free HTTPS origin in the project target context.
Retain the selected OAuth `environment` value separately as the authentication
profile. The names may be unrelated (for example, profile `DEV` and Fusion
environment `example-fusion`). Reuse a previously confirmed target; ask for its
actual identity only when it is missing or ambiguous. Never derive it by removing
a profile suffix or guessing from a hostname, ZIP or reference receipt.

Pass the actual selected Fusion name to task manifest/target-validation inputs,
and require it to match export `ProcessEnv`. Require the selected origin to match
the authenticated configured origin. Compare the login profile only with the
profile bound to the Data Loader preflight; do not compare it with `ProcessEnv`.
Keep task, release/schema, Run Book, archive-integrity and approval checks intact.
If a workflow accepts `referenceContext`, supply the separately selected target
there; do not invent that CLI option for adapters that do not declare it. This
identity handling grants no additional execution or import capability.
