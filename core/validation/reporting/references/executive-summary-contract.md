# Executive summary contract

This local helper produces the project executive `index.html` approved in the validation report examples, using recorded evidence rather than example numbers. It does not execute validation checks or call Fusion. A shared validation/reporting request authorizes the local report; all live checks, transaction creation and cleanup keep their routed prerequisites and approvals.

## Inputs and source selection

Use an existing initialized project. Read its registered reports and select explicit immutable source pairs. Include relevant unresolved historical failures alongside newer passing runs; do not select only favorable results. The helper checks the supplied sources but cannot discover an omitted report or prove source truth. Different requirement versions require separate summaries. Different stage `scope_ref` values remain visible and are never treated as equivalent coverage; a single transaction may cover only part of an implementation review. Prevalidation scope remains explicitly separate from implementation requirement coverage.

The manifest is a JSON object with exactly these fields:

| Field | Contract |
| --- | --- |
| `schema_version` | `1.0` |
| `project_id` | Existing project identifier; safe lowercase letters/numbers, `.`, `_`, `-`; starts with a letter/number; at most 120 characters |
| `summary_id` | New unused safe identifier with the same character rules |
| `generated_at` | ISO-8601 timestamp with timezone, no earlier than included report/task/check evidence |
| `environment` | Exact environment label in every included report |
| `environment_url` | Credential-free HTTPS base origin; must match prevalidation sources. Other sources use their workflow-verified environment label; this helper does not bind a label to Fusion itself |
| `redaction_reviewed` | `true` only after all sources and manifest are reviewed for redaction |
| `sources` | Nonempty array of source descriptors below |

Each source descriptor has exactly five fields:

- `kind`: `prevalidation` or `validation`.
- `result_ref`: project-relative `.json` path beneath `artifacts/shared/validation/`.
- `result_sha256`: SHA-256 of the exact sanitized JSON report bytes.
- `report_ref`: corresponding `.html` path with the same directory and stem.
- `report_sha256`: SHA-256 of the sanitized HTML report bytes.

Hashes identify report files only. Do not save Data Loader source bytes, payload hashes, approval objects, preview snapshots or encoded payloads. Never add credentials, raw customer records or sensitive screenshot content. No raw Data Loader runtime objects are inputs to this reporter.

Current prevalidation has seven read-only categories; historical reports containing Run Book write verification retain their original eight-category decision rules. The summary does not remove historical write findings or reinterpret them as passing.

For `prevalidation`, JSON is the existing readiness contract (`readiness.json`); stage outcomes are recomputed through its validator. That legacy contract does not require a project ID: the owning skill must verify project membership before selecting it, and the helper confines it to the selected project's local artifacts. Any supplied `project_id` must match. For `validation`, JSON is the published `{ "run": ..., "assessment": ... }` wrapper; the helper reruns the strict implementation-validation contract and requires the stored assessment to agree. Raw unassessed run input is not accepted here.

The helper rejects duplicate paths/run IDs, changed hashes, mismatched projects/environments, mixed implementation requirement baselines, unsafe or symlink paths, future source evidence and conflicting same-time task observations. It reads/hashes/parses JSON from the same bytes. HTML source hashes are checked but source HTML is not executed or redacted by the helper. Sources must remain immutable; the summary is not a tamper-proof signature or archive.

## Commands and outputs

```bash
python3 core/validation/reporting/scripts/executive_summary.py --input /path/to/summary-manifest.json --dry-run
python3 core/validation/reporting/scripts/executive_summary.py --input /path/to/summary-manifest.json --publish
```

Dry-run computes counts and validates sources without writes or network calls. Publication writes:

```text
project/{project_id}/artifacts/shared/validation/{summary_id}/index.html
project/{project_id}/artifacts/shared/validation/{summary_id}/index.json
project/{project_id}/state/runs/{summary_id}.json
```

It also registers two draft artifacts, updates the latest reporting-run reference and appends a chars/4 token estimate. It does not mark implementation complete or alter the active route. Reuse the common reporter lock, overwrite protections and handled-error rollback. Other project writers must be idle. Reconcile a process crash/remaining lock locally; never rerun a Fusion action to repair report persistence. Exit `0` means index generation/validation succeeded, not that the project passed. Exit `1` means input or artifact failure.

## What the user sees

1. **Run Book tasks first:** latest supplied observation per task, recorded status, source completion time, capture time, source run and current/stale evidence. An incomplete task never receives a completion time. A completed task lacking one shows **Not recorded**. This is not proof that every live Run Book task was supplied; planned prevalidation tasks are not counted as execution results.
2. **Executive numbers:** number of selected reports, recorded check results, distinct supplied task IDs, and all eight result categories: PASS, FAIL, BLOCKED, REVIEW_NEEDED, INDETERMINATE, SKIPPED, NOT_RUN and NOT_APPLICABLE. Prevalidation `REVIEW NEEDED` and historical prevalidation `FAIL`, `POTENTIAL BLOCKER` and `BLOCKED` normalize to `REVIEW_NEEDED`; other validation stages retain `BLOCKED`. Prevalidation `NOT APPLICABLE` normalizes to `NOT_APPLICABLE`. Repeated checks count once per recorded run; this is historical activity, not a unique coverage denominator or success percentage. Missing prerequisite categories are findings, not invented check rows.
3. **Stage cards:** immutable report links, outcome, scope, baseline and observation time. Stages without a selected report are labeled **no supplied report**, not successful or bypassed. No overall project traffic light is calculated.
4. **Findings:** historical result, expected/observed values, source/evidence/time, owner and next action. Where a legacy source lacks an owner, show **Not recorded — assign an owner**. Derived coverage gaps can overlap a check finding and are not an issue-count metric. A later PASS never auto-closes an earlier failure. Closure requires relevant reassessment evidence and an explicit referenced decision.
5. **Transactions and cleanup:** known created primary-record counts across runs, unknown-count runs, reused-record runs and cleanup disposition counts. These are not unique/current Fusion-record counts; cleanup is independent of scenario success. Preserve each detailed report's cleanup owner, rationale and evidence.
6. **Boundaries:** sources/hashes and provenance in `index.json`, stage scope limits, no external calls, no unsupported truth/currentness claims. `project_readiness` is always `NOT_ASSESSED` in this history index.

## Worked behavior

If prevalidation recorded seven PASS and one NOT_APPLICABLE, implementation review recorded two PASS, one FAIL and one NOT_RUN, and a later transaction recorded one PASS, the index shows **3 reports / 13 recorded results: 10 PASS, 1 FAIL, 1 NOT_RUN, 1 NOT_APPLICABLE**. The implementation stage remains BLOCKED in history. The later transaction reports READY_WITHIN_VERIFIED_SCOPE for that one check. It does not close the old failure or assert that the current implementation is ready. The same rule applies to unknown transaction outcomes and unresolved cleanup.
