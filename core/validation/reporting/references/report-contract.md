# Validation reporting contract

## Inputs

`schemas/implementation-validation-run.schema.json` is the new versioned input contract. It leaves `schemas/validation-result.schema.json` unchanged. `references/example-implementation-review.json` and `references/example-transactional-validation.json` are synthetic fixtures, not actual implementation evidence.

Required run fields: project/run identity, stage, environment, timestamp, request, approved scope reference and requirement version, redaction-review attestation, requirements, task evidence, check results, decisions, recommendations, limitations, diagnostics.

- Requirement: approved expected setup, task/check references, owner and required flag.
- Task: status, source, capture time, environment, freshness, details and owner; optional nullable `completed_at` records the actual completion timestamp including timezone. It is independent of `captured_at`. The Run Book task list appears first, before scope/readiness, preserving input order. Completed tasks without a timestamp show “Not recorded”; incomplete tasks show “Not completed”. No tasks supplied produces an explicit missing-evidence notice. Do not turn completion into verification.
- Check: unique result/check ID and version, source, owner, required/blocking flags, requirement/task links, outcome, verification method, observation time, freshness, reason, evidence and next action.
- Assertion: expected, observed, PASS/FAIL/NOT_OBSERVED and evidence references.
- Transaction: stable test key, safe record/request/approval references, count 0/1/null, reuse flag, effects, cleanup outcome/evidence/owner/next action. Null count is allowed only for INDETERMINATE; it does not authorize a retry.

One transaction invocation contains exactly one result. Multiple prior invocations remain separate immutable runs and may be linked in an assisted project summary. Local report generation never executes or chains those checks.

## Derived readiness

The derived assessment contains stage-scoped readiness, status counts, requirement/task counts, gaps, blockers and next actions. It is stored beside the unchanged input under `{"run": ..., "assessment": ...}`. Feed `run`, not this output wrapper, back to the input validator. Readiness does not independently verify the supplied evidence or approve a release.

PASS requires nonempty passing assertions with observations and evidence references. Required attestation-only or stale checks remain NEEDS_REVIEW. Missing required mappings/check results and all-not-applicable required coverage remain gaps. A selected transaction with no passing result cannot claim readiness. Cleanup pending/failed/unknown remains visible separately from transaction success.

## Publication

Run `--dry-run` first, then `--publish` for an authorized local report request. The helper writes to its repository's existing `project/<project_id>`, not an arbitrary output directory. It refuses symlinks and existing run IDs. HTML is standalone, escapes all input and contains no scripts or external resources; evidence references are displayed as text to avoid unsafe-link execution.

Publication generates draft artifact-index records and a reporting skill-run, updates `latest_run_ref` and `updated_at`, and appends a token estimate. It does not change implementation status or active route. No customer data or production values belong in the input, report or JSON. The caller performs redaction review; HTML escaping and schema validation are not sanitization.

Use one project writer at a time. Handled write failures restore metadata and remove the newly created report folder. A crash can leave partial files or a lock; manually reconcile the index, run record and report folder before retrying. Never discard a lock until its process is confirmed inactive. The helper lock does not coordinate unrelated services.

## Commands and exit codes

```bash
python3 core/validation/reporting/scripts/validation_report.py --check-definition /path/to/check.json
python3 core/validation/reporting/scripts/validation_report.py --input /path/to/run.json --dry-run
python3 core/validation/reporting/scripts/validation_report.py --input /path/to/run.json --publish
```

| Exit | Meaning |
| --- | --- |
| 0 | Input is valid and assessment is READY_WITHIN_VERIFIED_SCOPE, or check-definition validation succeeded. |
| 1 | Invalid input/project metadata or local persistence failure. No Fusion action occurs. |
| 2 | Valid report with incomplete/blocked readiness. |
| 3 | Valid report with INDETERMINATE transaction outcome. |
| 4 | Valid report with a recorded FAIL. |

Codes 2–4 still publish reports when `--publish` is selected. Reporting skill-run status records publication completion, while the result JSON retains actual business failures. Recovery never reruns a transaction.

## Validation dependencies

Runtime: Python 3.10+, standard library only. The contract validator supports the exact JSON Schema features used by these contracts and rejects unsupported keywords/formats; it is not a general JSON Schema engine. No browser, testing-platform service, Fusion network, or credentials are needed for local tests.

## Executive presentation and consolidation

Per-run HTML includes calculated status/scope cards, a leading Run Book task table, explicit gaps/blockers, owners/actions, requirement mappings, expected/observed assertion evidence, manual attribution and cleanup disposition. Counts are derived from validated input; missing observations and unknown transaction counts remain visibly unknown. A task's completed status is not a passing value assertion.

For the final project handoff, use the separate [executive summary contract](executive-summary-contract.md) to publish an append-only `index.html` and `index.json` from explicitly selected prior report pairs. It preserves historical failures, missing stages and separate stage scopes. It never concatenates transaction runs into one check invocation or converts historical counts into overall project readiness. This local step does not authorize additional live status calls or persistence of Data Loader session data.
