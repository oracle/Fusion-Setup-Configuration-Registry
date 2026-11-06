# Runtime metadata and FSCR environment binding

The extraction planner prepares read-only BOSS requests and transforms current-run
Core results into a complete tree. It uses the same Core-delegation pattern as
Activate Algorithms. It never performs HTTP or OAuth or launches a Core client.
Do not use an earlier catalog or a different environment as a fallback.

## Environment source

Use the active workflow's `fusion_environment_context` and selected
`core/auth/fusionEnv.properties`, following the
[core REST client](../../../../../core/fusion-api/rest-api-client/SKILL.md).
The base URL is `restBaseUrl`; BOSS uses `boss_scope`, managed by core OAuth.
Callers supply role evidence, not host prefixes or application usernames.
The local `fscr_context.py` helper uses core's properties reader without login,
token-cache access, or external requests. It records the canonical HTTPS origin
as `environment` and rejects mismatched normalized input.

## Core extraction contract

Only a declared routed operation may retrieve metadata. Hand every request to
`core.fusion-api.rest-api-client` using its BOSS route. Resource paths below are
relative to `/api/boss/data/objects/ora/riskMgmtRisk/accessControls/v1/` on the
selected configured origin. The active skill workflow owns the declared read step
and its project, identity, privilege, configuration, path, and evidence preflight.

1. `providedAccessAlgorithms/$views/detailed`: filter by each configured
   reference code and select `id,name`; require exactly one record.
2. `providedAccessAlgorithms/<id>/algorithmReferences`: filter
   `referenceType='ENTITLEMENTS'`, select `referenceId`, and paginate.
3. `providedEntitlements/$views/detailed`: filter by exact reference ID,
   select `name`, and require exactly one record.
4. `providedEntitlements/<id>/accesses`: select
   `primaryAccessPoint.code,primaryAccessPoint.name` and paginate.

Preserve string IDs, exact codes/names, all pages, and the six-algorithm order
in [design enforcement](design-enforcement.md). Reject malformed pagination,
empty entitlement accesses, missing algorithms, and ambiguous lookups. Authentication,
transport, scope selection, and bounded refresh remain core responsibilities.
No application username is needed for the evaluation catalog or result.

## Request and result handoff

Start `scripts/run_checkup.py --input <prepared-request.json> --output
<project-request-directory>/security_checkup_result.json`. Alternatively,
`extract_tree.py` accepts the same options and writes only a complete runtime
metadata tree. Both accept `--properties`, `--request-plan-output`, repeated
`--core-response`, and `--dry-run`. No host prefix or login username is accepted.

The default plan is `<project-request-directory>/core-requests.json`. Each
`requests` item includes `id`, `service: boss`, `method: GET`, a relative
`endpoint`, query parameters, environment and assessment context, and
`core_client_request`. All currently independent missing reads are emitted;
additional pages remain dependency-ordered. Request IDs bind the operation to
the assessment request, configured origin, and output run directory.

The active workflow must execute **each** emitted GET through
`core.fusion-api.rest-api-client` using its BOSS route. Follow that skill's
preflight, `boss_scope`, private cache, and one-refresh policy. Pass query
parameters as separate `--query` arguments and pass the same selected
`--properties` profile when applicable. Do not pass the request manifest as an
HTTP body. Do not run a shared helper as an alternate Core client.

For each actual returned Core result, the workflow retains a minimal envelope
under the current request directory (for example `core/<request-id>.json`):

```json
{
  "request_id": "<exact emitted request id>",
  "environment": "<selected FSCR HTTPS origin>",
  "status": 200,
  "body": {"items": [], "hasMore": false}
}
```

Use the actual HTTP status and unmodified parsed Core collection body. Attach
the environment and request ID from the verified Core execution context; do not
accept unrelated raw JSON, invent a successful status, or copy an earlier run's
evidence. Never include authorization headers, token values, or credentials.
A response path must resolve inside this run directory. Output paths must
resolve inside a selected project with `state/project-state.json`.

Resume with **all** collected results, including earlier phases:

```powershell
python scripts/run_checkup.py --input "<prepared-request.json>" --output "<project-request-directory>/security_checkup_result.json" --core-response "<id>=<project-request-directory>/core/<id>.json"
```

Repeat `--core-response` once per result. Exit code `2` and
`awaiting_core_responses` mean the workflow should execute the next Core batch
and continue internally, not ask the consultant to manage evidence files.
Exit `0` means completion (or a successful `--dry-run`); other nonzero exits
are failures. Preserve error diagnostics and resolve the classified cause.

Incomplete results never publish a tree or assessment. Successful extraction
validates all six algorithms, dimensions, exact codes and names, duplicate
constraints, and pagination before publishing. The page loop is bounded at
1,000 pages per collection; exhaustion is a timeout, not a truncated success.
There are no mutations, polling loops, or skill-owned network retries.

## Verification and persistence

`run_checkup.py` passes the complete tree directly into rule generation and
role evaluation in the same invocation. It exports the exact tree bytes, both
rule exports, generation summary, and result under the project request directory.
No standalone static-tree input is used by the ordinary assessment path.
Verify shared environment provenance, request IDs, digest, counts, and finding
rule IDs before delivery. Never reuse review exports for another assessment.

After each durable batch or terminal outcome, the active workflow registers
artifacts through the core registry, updates project state, records a skill run,
and appends token usage using `core/project-mgmt/scripts/token_usage_logger.py`.
The helper's request plan and failure diagnostic are intermediate evidence;
they do not replace the project run record. Source guidance is the uploaded
package's lookup contract and the local Activate Algorithms delegation pattern;
synthetic tests do not establish live tenant availability or read privileges.
