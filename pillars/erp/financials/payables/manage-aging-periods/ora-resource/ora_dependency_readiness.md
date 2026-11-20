# Dependency Readiness

Task scope: AP_MANAGE_AGING_PERIODS / Manage Aging Periods. Use a fresh exact-task export to match existing records. Run Book supplies inputs. Create and update are supported. Submit the validated package through Data Loader after its required approval.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Header | Resolve exact parent identity before line operation |
| 2 | Line | Use exact parent PeriodName and sequence; retain package relationship |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| header_parent | Aging period header | Yes | line operation | Verify | Fresh exact-task export or an explicit header create in the same candidate | match_aging_period_by_name | Child parent reference is portable PeriodName | Provide exact parent name; do not create unrelated prerequisite setup | Matched or explicitly requested header identity |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Exact match or explicit same-package parent create | Read-only matching; same-task create only within requested scope |
| Blocked | Missing or duplicate parent identity | No automatic prerequisite create |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AGING.DEPENDENCY | decision | 40 | resolve_dependency | pass->AGING.DESIGN;missing->AGING.RETURN_ISSUES | AGING.MATCH | stop | create or update |
