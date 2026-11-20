# Live CREATE workflow and QA handoff

This is the selected service route for the bounded CREATE task. Enter it only
from an active implementation project and an explicit request to create in
Fusion. A request for a template, analysis, or package alone does not select
submission. Task identity is EXM_MANAGE_CORPORATE_CARD_PROGRAMS, Financials,
Expenses, Manage Corporate Card Programs; businessObject remains empty and the
Data Loader import mode is FSM.

## Fresh-login contract for every live execution

This is a supervised route. Every live invocation must obtain a fresh token
through core authentication. Previous-session cache reuse and caller-supplied
access tokens or authorization codes are not supported. There is no cached
production mode or QA-only exception. The adapter always sets `force_login=True`;
its legacy `--force-login` flag is accepted for compatibility and cannot disable
fresh login. It preserves the selected configuration around authentication and
reads. Core still owns OAuth, token storage, origin checks and transport.

Before each sign-in, the operator checks the selected target and intended account
in the active Run Book and uses a dedicated browser profile. During sign-in, the
operator verifies the actual account before authorizing access. If an existing
SSO session skips an observable account check, or selects another account, stop
and correct the session through onboarding/core authentication before continuing.
Do not treat a configured username, a changed cache filename, or a generic prior
confirmation as identity evidence. Record the target, account, performer and
fresh sign-in time as manual evidence for that invocation. No account switching
or concurrent use of the selected OAuth profile is permitted during the run.

`--force-login` skips cached-token reads; it does not force an SSO logout or
verify the token subject. Manual account confirmation is a declared human step,
not an automated authentication claim. If the operator cannot complete it, stop.
An account/environment change requires new prevalidation and candidate review.

Apply this handoff table before executing each service; omission of the required
option is a failed preflight, not permission to use the service's default:

| Live phase | Selected service | Required authentication selection |
| --- | --- | --- |
| Template/baseline/issuer/mapping export and download | Task export adapter calling shared task-level export | Fresh login enforced in code; `--open-browser` lets core open sign-in |
| Reference GETs | Core REST client | `--force-login`, selected properties and service; no explicit-token/auth-code override |
| ZIP validation and Task Hook service calls | Core Data Loader | `--force-login` on every network-capable invocation |
| UCM upload and initiation | Core Data Loader | `--force-login` with the exact approved artifact and target |
| Explicit status/result inspection | Core Data Loader | `--force-login` for the new session |
| Post-import export/read-back | Task export adapter; local verifier | Fresh login enforced for export; local comparison has no authentication |

For programmatic supported handoffs, the equivalent is `force_login=True` in the
service's public OAuth options. Reject an explicit bearer token/auth code that
would take precedence over this setting. Within a single core session, use only
the token acquired by that session. Core may persist its normal external cache;
this task never consumes that cache in a later session. If a core handoff lacks
this supported option, stop with a service-contract blocker, without a direct
REST/browser/import substitute. These controls do not waive approvals, privilege
checks, immutable candidate validation or post-import verification.

## 1. Preflight and business inputs

Resolve project, exact environment and requested operation before external calls.
Use core/getting-started/onboarding for auth diagnosis and
core/auth/fusion-oauth-authentication for selected login/renewal. Use current
catalog metadata and require CSV export/import support Y. Check task/reference,
export and import privileges; visible BU data alone is not proof of import access.
Confirm one new TRAVEL program and only supported child rows/fields. Present all
missing business inputs together. Never convert an existing program into UPDATE.

Resolve the business values using ora-resource/ora_reference_lookups.md through
core/fusion-api/rest-api-client and its references/fusion-rest-api.md. That is the
selected route for the documented read-only lookups in this workflow, with
REST-Framework-Version: 9, explicit fields and complete pagination. Resolve only
requested/applicable fields; zero matches, ambiguous results, missing pages and
failed requests block. Validate company payment, clearing account/COA/ledger,
issuer/site, BU, currency, terms, mapping/source pairs and enabled codes before
package construction. Keep leading zeros. Existing issuer/site evidence comes
from the task-level export service below; never invent party/address values.

## 2. Acquire trusted template and baseline

Select shared/setup-export/task-level-export/SKILL.md. It owns catalog checking
and delegates to shared/setup-export/fsm-csv-export. Use the task-owned adapter below with the selected task code, active project
and environment configuration. Template mode obtains the
blank template; omitting `--template-only` obtains the unfiltered setup baseline. Do not
supply export criteria for the baseline. If company rows need issuer/site
resolution, explicitly select EXM_MANAGE_CORPORATE_CARD_ISSUERS data export through
the same service. When mapping rules are supplied, also select
EXM_MANAGE_CORPORATE_CARD_EXPENSE_TYPE_MAPPING_RULES data export through this
adapter to resolve the mapping header/source as required by the reference rules.
Request approval immediately before each export POST, showing
the actual target, endpoint and exact TaskCode/process-child payload. Export
approval is distinct from import approval. A supplied current export may be reused
only with matching provenance, task, target, release, completeness and scope.

For this credential-bearing task, use `scripts/export_evidence.py` as the
task-owned adapter around those shared services. Read export-response-recovery.md.
Do not use the generic export-and-write CLI to persist raw bytes. After the exact
export approval, create one job and its receipt:

```text
python3 <task>/scripts/export_evidence.py create --properties <selected.properties> \
  --project-dir project/<id> --receipt project/<id>/exports/<unique-receipt>.json \
  --template-only --approve-export --force-login --open-browser
```

For the baseline omit `--template-only`; for issuer data also supply
`--task-code EXM_MANAGE_CORPORATE_CARD_ISSUERS`. Each new create needs its own
immediate approval and unused receipt. The adapter checks catalog support and
records the selected target before invoking the public shared `create_export` interface once. The shared service owns its request body, media type and framework settings; this task does not override or monkey-patch them. A service incompatibility stops with a dependency diagnostic. Retrieve
only that receipt's job through the same adapter:

```text
python3 <task>/scripts/export_evidence.py download --force-login --open-browser --properties <selected.properties> \
  --project-dir project/<id> --receipt project/<id>/exports/<same-receipt>.json \
  --template-only --environment <expected-ProcessEnv> \
  --output project/<id>/exports/<unique-sanitized-export>.zip
```

Match the create command's task and template mode exactly. The adapter polls the
existing job with bounded read-only checks for up to 300 seconds by default
(`--wait-seconds`, 0 through 300; `--poll-interval`, 2 through 30). On timeout,
retain the receipt and a new sanitized diagnostic/status snapshot under exports,
including target, task, process, last status and elapsed wait, then report PENDING; a subsequent requested check reuses it.
Never create another job because the existing job is still processing. The download stays in
memory until sanitization and task/environment validation succeed. Save the
returned provenance report with the export. Do not edit an uncertain receipt,
repeat its POST, or copy sensitive raw bytes to temporary or project files.

Record template and baseline ProcessId, completion status, acquisition time,
source environment, ProcessEnv, release, task, unfiltered scope and artifact refs.
An old run's export is not evidence of current duplicates. Invalidate the baseline
when the target changes or known setup changes occur before validation. The
package helper checks embedded identity; the workflow verifies freshness and
provenance. Run its dry-run and output stages as described in SKILL.md.

## 3. Validate and submit through core Data Loader

Read core/data-loader/SKILL.md and its current FSM contract before using its
helpers; do not copy an old invocation or approval envelope from another run.
Provide the prepared ZIP and this task's context to the normal Data Loader
validation path. Retain the selected task code through final immutable artifact
preparation. Immediately afterward use Data Loader's single Task Hook `data-load`
route and evaluate every applicable rule against that exact artifact. The task
rules include required fields, same-target provenance, duplicate guard, reference
eligibility and header-only issuer/party/download members. A generated ready
registry alone does not satisfy the rules. No silent readiness override is allowed.

Data Loader owns preflight, Task Hook preview, approval, envelope verification,
UCM upload and initiation. Do not reconstruct an envelope, force readiness flags,
call a separate FSM import adapter, or duplicate the core approval. Follow its
current supported same-request auto-approval behavior only when explicitly given.
Otherwise request its exact validated-artifact approval after all checks pass.
Persist only the evidence and internal artifacts required by the current core
contract. If the approved artifact or context changes, return through core's
validation/approval process. No automatic resubmission after an uncertain outcome.

After accepted initiation, return core's complete Markdown report unchanged and
stop. Acceptance means submitted, not configured. Do not automatically poll or
start the read-back export. Record returned identifiers through the core project
evidence handoff. A prior historical successful import is not qualification of
this branch or of the currently selected environment.

## 4. Explicit status and setup verification request

When the user asks for status/results, select core Data Loader's
get_data_load_info.py for the returned request ID or UCM Content ID. Use its
project diagnostic directory option, retrieve dataSetErrors and applicable FSM
ProcessLog, and preserve the helper's report. Missing datasets remain pending;
failed/partial loads remain failed/partial even if some requested rows exist.
A status-only request does not start an additional export.

When the user explicitly requests persisted-setup verification, obtain a fresh
unfiltered program export through step 2, including its immediate export approval.
Do not reuse the pre-import baseline as the post-import evidence. Then run:

```text
python3 <task>/scripts/verify_fsm_setup.py \
  --baseline <pre-import.zip> --after <post-import.zip> \
  --input <reviewed-design.json> --environment <expected-ProcessEnv>
```

The local verifier checks the root and requested child values/parent links,
derived upload format, duplicate/missing rows, unexpected child rows, and
preservation of baseline nonsecret rows, including issuer/party/download data. It does
not require unspecified blank fields to remain blank: Fusion may default them.
No value mismatches may be hidden by a successful job status. A mismatch or
unrelated change is a failed comparison requiring investigation; concurrent
changes can explain a difference but must not silently turn it into PASS.

Save the redacted comparison report with both exports' provenance and the load
result separately. Overall setup success requires a successful completed load,
no applicable error evidence, and passing fresh same-target value verification.
Credential values withheld by the export adapter remain NOT_VERIFIED; matching
redaction markers do not prove unchanged credentials. No automatic deletion/cleanup is included. Corrective writes require a separately
supported workflow and approval.

## QA retest

From a clean customer package (noship absent), request CREATE in the selected
Fusion environment using a reviewed synthetic fixture within the supported scope.
Verify that the skill enters the above service route rather than stopping merely
because its package helper reports prepared_offline. Exercise root-only and
company/upload variants, all supported brand defaults, Both/Company Pay, optional
blanks, duplicate names, invalid references, wrong environment/headers, denied
export approval, changed approval artifacts, failed jobs and unknown outcomes.
A user-requested verification phase must detect wrong persisted values and changes
to protected rows. Record skipped stages as NOT RUN and actual service gaps as
BLOCKED, never PASS. Local unit tests do not replace this live qualification.
