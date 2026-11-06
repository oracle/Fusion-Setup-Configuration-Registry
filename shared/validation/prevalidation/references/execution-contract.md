# Declared execution routes

This skill selects these core operations after workspace and identity preflight. Every new implementation project, including plain-language requests without attachments, first prepares the local project and mapped tasks, then resolves the user's run-or-skip choice. A skip performs none of the assessment operations below. Read each referenced core manifest/contract before use. Check CLI `--help` locally for current arguments. Follow core policies when stricter; old cache examples in references do not override core auth's external `--token-cache auto` policy. Pass `REST-Framework-Version: 9` for Fusion REST requests. Do not run an external operation while merely authoring or reviewing this skill.

## Stage boundary

`pre_runbook` is the creation stage for every new implementation project,
including plain-language setup requests, single-task projects and artifact-led
requirements. It permits the read routes
below and forbids all Run Book creation, including a connectivity test. Keep
project control pending/unbound. Successful empty listing excludes existing-book
detail checks only; Run Book writes are outside prevalidation and have no required check row;
write access remains unverified. After
reports are saved or the user explicitly skips, return to `core.runbook` for
the original implementation request and its creation gates. Do not silently
switch to `full_readiness` to create a test book.

`full_readiness` is the standalone read-only assessment stage. Neither stage
includes Run Book write verification or creates a test Run Book. Readiness does
not certify write privileges. A skip or override never removes mandatory core
execution checks from a later implementation workflow.

| Check | Selected core route | Bounds |
| --- | --- | --- |
| Authentication | `core/auth/fusion-oauth-authentication/SKILL.md` and its login/cache helpers | Configured service only; no token contents in artifacts |
| FSM/BOSS identities and hierarchy | `core/fusion-api/fsm-rest-client/SKILL.md`, through `core/fusion-api/rest-api-client/SKILL.md` and `scripts/boss-rest_client.py` | GET only, BOSS scope, selected offering and dependency closure |
| Live task relationships | FSM references `tasks-by-feature.md`, `offering-fa-feature-tl-task-bo.md`, `parent-child-feature-hierarchy.md`, `tasks-bo.md` | Full pagination for the required scope; preserve codes/IDs, nesting, and errors |
| Opt-in evidence | Fields explicitly defined by the selected FSM/BOSS read contract; documented Fusion Common GET only through the shared REST client with `--service fusion-common` | Read the current service contract first. If it does not define readable enabled/selection state, REVIEW NEEDED. No guessed endpoints, Set Optin execution, PATCH, refresh action, or browser fallback |
| Data Loader API accessibility | Standard service GET through `core.fusion-api.rest-api-client`, path from `core/data-loader/scripts/data_loader_metadata.py::BUSINESS_OBJECTS_PATH` | One bounded collection request: `onlyData=true`, `limit=1`, `offset=0`; no individual BO checks, metadata reads or pagination |
| Run Book list/read | `core/runbook/scripts/runbook_rest.py list-runbooks`, `get-journey`, `list-tasks`, `get-task` | Explicit journey ID for reads; no dashboard/config activation, export/import, merge, updates, attachments, or force-complete |

`list-runbooks` uses the core-declared read-semantic POST search; this is permitted for read readiness. No other arbitrary POST is authorized. Do not invoke `task-detail`'s Data Loader summary action for this assessment.

## Catalog coverage and Data Loader API accessibility

Use `knowledge/setup-task-catalog/effective/Offerings_catalog.json`, `Functional_areas_catalog.json`, `setupTasksAll.json`, `offering-functional-area-task-catalog.json`, and `pillars-offerings-mapping.json` as applicable. Record exact file/key evidence and the resolved pillar skill paths. Do not edit effective catalogs during assessment. Names are lookup aids; compare stable identity codes and context. Keep live-only additions and stale repository entries visible.

The FSM references declare available-offering, area/feature, task-list, task, business-object, and relationship GET routes. Use current declared query parameters and pagination from those references; this assessment explicitly requires full coverage within scope, so a bounded default preview is insufficient. Save full catalog exports only under the project's `exports/`; persist sanitized counts/identity evidence under assessment artifacts. Never use `/tmp` for durable exports.

### Data Loader accessibility probe

Data Loader prevalidation checks **API accessibility only**, independently of the
planned tasks' individual business-object declarations. Issue one authenticated
standard-service GET to `BUSINESS_OBJECTS_PATH` with `onlyData=true`, `limit=1`
and `offset=0` through the declared core REST client. This is a bounded probe,
not a catalog export; the full-pagination requirements above apply to the
FSM/BOSS scope checks, not this probe.

PASS requires HTTP 200 and a parsed JSON object containing an `items` array.
An empty array passes: no business object is required to demonstrate collection
API access. `hasMore: true` does not require another request. A login page,
redirect to sign-in, malformed response or HTTP failure cannot pass. Use
REVIEW NEEDED for unavailable/unverified access and classify the observed
failure; apply only the skill's existing bounded read-recovery policy.

Do not enumerate required BOs, match discriminators, validate registration,
retrieve individual BO details or UCM templates, read components/attributes,
compare schemas/baselines, or call `load_business_object_schema`. Do not refresh
metadata, generate samples, validate/upload/submit a load, or inspect datasets.
Object-specific checks remain the responsibility of a separately selected
implementation/load workflow when required by that workflow.

Persist only the check time, standard service, method, sanitized collection
endpoint/query, safe HTTP result/request identifiers and envelope-validation
result. Discard returned object rows from evidence. Report one required
`data_loader_readiness` check named `Data Loader API accessibility`, with
`notes` stating that object registration, templates, schemas, load/write
privileges and future job success were not assessed. An access failure must
include a concrete recommended diagnostic/fix based on the evidence (for
example, verify network reachability for a transport failure or ask the owner
to review the selected service's access after a 403); do not infer a specific
missing role from the status alone. Always offer the existing result overrides.

## Oracle source verification

At execution time verify the latest available Fusion documentation for each relevant product/topic; record the checked release, target environment release, retrieval date, exact source, and any gap. Do not assume a REST path's `11.13.18.05` version is the Fusion quarterly release.

Authoring lookup on 2026-10-15 found Oracle's [Overview of Configuring Offerings, 26A](https://docs.oracle.com/en/cloud/saas/applications-common/26a/oafsm/overview-of-configuring-offerings.html), which explains core functionality versus optional opt-ins. Direct checks of the same topic in 26C and 26D were inaccessible through the lookup tool. This is an older-source gap, not evidence that 26A is the latest release. Oracle's [current Configure Offerings tutorial](https://docs.oracle.com/en/cloud/saas/applications-common/faqac/configure-offerings.html) also distinguishes availability, enablement, core functionality, and parent-child opt-ins but is not release-stamped. These support interpretation only; they do not supply BOSS endpoint contracts or authorize enabling anything. Re-verify before relying on release-dependent behavior.
