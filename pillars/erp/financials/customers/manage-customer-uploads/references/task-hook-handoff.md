# Customers FBDI phase contract


The central Task Hook plans non-write, nonterminal registry nodes before the
candidate preview. It does not schedule a task-owned post-import phase. Keep
these responsibilities distinct:

| Phase | Owner and evidence | Exit |
|---|---|---|
| Candidate preparation | Task skill: known input/package checks, exact identity and ownership, reviewed intended effects, before-state, eligible business gaps, and a readback plan covering the requested values | Ready for central preview; no import result is expected |
| Preview and approval | Task Hook and Data Loader: actual Run Book task context, ordered rule results, archive hash, environment, current registration and arguments; normal explicit candidate approval and any eligible gap acceptance | Approved exact candidate only |
| Submission and monitoring | Core Data Loader: one authorized attempt, actual returned IDs, interface and scoped product-stage status/counts/errors | Process result, including unknown or partial results |
| Business reconciliation | Declared read-only route: persisted identities, ownership, requested values, defaults and intended update/reuse effects compared with reviewed expectations | Verified, mismatched or incomplete business outcome |
| Journey completion or recovery | Run Book: separate synchronization evidence and normal human completion/retry decision | Recorded completion, or a new corrected candidate and approval |

Use `core/data-loader/task-hook/scripts/task_hook.py` with the actual selected
Run Book task context. Its `data-load` command resolves the plan;
`build-data-load-preview` consumes ordered evaluated rule results and
`finalData.archiveSha256`. After explicit approval, the central approval and
archive-verification commands produce the Data Loader validation envelope.
The task skill must not manufacture passed rule results, a run ID, an approval
or a verification envelope. A synthetic integration test is not run evidence.

The existing-target node evaluates supplied evidence through the declared assisted
route. The [central handoff evaluation](central-handoff.md) and
[verification plan](verification-plan.md) define the remaining checks. A compiled
ready registry permits planning, not a passed candidate. Do not use
`allowReadinessOverride` to turn missing hard evidence into a live candidate. Named eligible business
uncertainty is handled by the separate loader-validation acceptance contract.

The pre-import terminal `ARCU.READY` means `READY_FOR_CENTRAL_PREVIEW` only.
Post-import reconciliation must not be an input required to obtain that preview,
and reaching the terminal must not update Journey completion. A timeout resumes
status for the original attempt; it never authorizes resubmission. Successful
entities remain visible during partial failure; no inverse rollback is assumed.
