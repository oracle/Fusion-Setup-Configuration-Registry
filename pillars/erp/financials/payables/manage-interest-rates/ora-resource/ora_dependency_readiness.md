# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Exact task template | Confirm AP_MANAGE_INTEREST_RATES metadata, AP_INTEREST_PERIOD node, and exact header. |
| 2 | Current task state | Obtain a fresh same-task export. For every update, find exactly one period whose StartDate (UI From Date) matches the requested key, after valid date normalization; use the export for duplicate and overlap checks. A screenshot or row position is insufficient. |
| 3 | Data Loader governance | Keep candidate preview, approval, import, and reconciliation with core.data-loader. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| IRATE-PACKAGE | Exact task archive | Yes | Every operation | Verify | Same-task template and metadata | | Prevents wrong-task or malformed package | Re-export if identity or header differs | Exact metadata and header |
| IRATE-BASELINE | Fresh current periods | Yes | Create or update | Verify | Same-task current-data export | | Supports overlap check and a unique StartDate match for each update | Obtain fresh export before preview; identify the exact From Date and keep it on update | Existing period dates and rate |
| IRATE-AUDIT-CREATE | Audit serialization on create | Yes | Create | Verify | Same-task FSM package contract and export verification | | Fusion manages audit values; create candidates leave audit cells blank | Keep create audit cells blank and never accept user values; revalidate if the task template or release changes | Blank create audit cells |
| IRATE-AUDIT-UPDATE | Audit serialization on update | Yes | Update | Verify | Same-task FSM package contract and export verification | | Update candidates leave read-only audit cells blank and preserve unrelated business values | Keep update audit cells blank, never accept user audit values, and revalidate if the task template or release changes | Blank update audit cells |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Verify | Exact package and baseline available | No external lookup; perform local evidence checks |
| Blocked | Exact package or unique target is unresolved, or current release/template differs from the validated audit serialization evidence | No |

No external reference lookup was identified for the eight package fields. Do not invent a REST resolver.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| IRATE.CHECK_DEPENDENCIES | step | 20 | resolve_dependency | ready->IRATE.ENFORCE_DESIGN;blocked->IRATE.DEPENDENCY_BLOCKED | IRATE.VALIDATE_INPUT | stop | Always |

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
