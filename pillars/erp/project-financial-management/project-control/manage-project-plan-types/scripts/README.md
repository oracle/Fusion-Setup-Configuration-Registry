# Project Plan Types import gate

`validate_import.py` validates the actual ZIP without modifying it. It returns
package integrity, task-contract validation, deferred checks, and server-side
validation separately. Missing required business inputs block; they are never
silently defaulted. Local success leaves server validation `not_run`.

Checks include calendar-dependent rate derivation, the separate conversion-date
domain and budget/forecast target requirements. A synchronization buffer is
optional business input; preparation applies the 0-day save default when
synchronization is Y and the effective buffer is empty. Supplied active values
must be integers. The byte validator rejects an unmaterialized active blank;
it never fills defaults. Rate mode belongs to each BU
row, including actual-rate fallback schedules. Inactive retained rollup or rate
settings are disclosed as deferred context, not silently reset; the assisted
rules distinguish preserved values from requested changes to inactive controls.

`import_preview.py` adds the task-local preview/approval gate. It calls the
existing shared Task Hook using the selected project task context, rechecks the
ZIP before approval, and verifies the exact prepared bytes before handoff. It
performs no upload, retry, token refresh, or Fusion operation.

Build returns a task preview record with the unchanged core `preview`, plus
`archiveValidation` and `taskRoutingContext` alongside it. Approve delegates to
Task Hook's `approve_data_load_preview`; task evidence and the record digest
remain outside the core preview and approval objects. Verify delegates to
`verify_approved_data_load_archive` over the supplied prepared bytes and returns
its unchanged `taskValidationEnvelope` for the loader. The approval must match
the current project, active Run Book and server binding. A changed binding or
an older local envelope without this contract requires a fresh preview and
approval. Never add a missing binding by hand.

After approval, `verify` checks the retained task-record digest and task identity,
then delegates approval, current Run Book binding and archive SHA-256 checks to
the canonical verifier. It does not rerun the task ZIP validator, resolve current
task rules, rebuild a preview or read the original source/task-context file.
Current planner availability or unrelated rule changes do not invalidate an
intact approved artifact. Changed bytes, retained evidence, approval or bindings
still block the handoff.

## Input and commands

### Prepare from the current target

`prepare_import.py` builds one named type from a completed target template and
data baseline. It never exports, acquires references, approves or calls Fusion.
Resolve business labels and LOV identities through the task rules first. Its
internal JSON accepts `operation`, `rows` and the explicit actions described
below, with rows keyed by exact CSV member
and values serialized as canonical strings. For example, a create request has
one PJO_PLAN_TYPE_PROJECT.csv row containing Name and StartDate, an optional
PJO_PPT_PLAN_OPTION_GEN_OPT.csv row of explicit choices, and explicitly requested
set/rate/currency/translation rows. Do not ask consultants to author this JSON.

```bash
python prepare_import.py --target-origin https://selected-pod.example.com --template /absolute/project/exports/current-template.zip --baseline /absolute/project/exports/current-data.zip --request /absolute/project/artifacts/canonical-request.json --output /absolute/project/artifacts/prepared.zip --dry-run
```

Use the exact approved Fusion origin from the environment/Run Book context.
After the dry-run passes, repeat without `--dry-run` to create a new output file.
The helper never overwrites a file. Changed exported members or columns require
contract review, not a guessed mapping. Metadata is copied byte-for-byte.

Create defaults cover PROJECT_PLAN/BUDGET/COST_ONLY and its COST child only.
Separately, submitted create/update planning-options rows apply the conditional
save default: SyncTaskTxnPlanDates Y plus an empty effective SyncTxnDateBuffer
becomes 0 after explicit choices and retained values are merged. An explicit
integer overrides the baseline; an omitted nonempty baseline buffer is retained.
An explicit empty active buffer also defaults to 0. With synchronization N,
the inactive buffer stays unchanged. Omitted options rows on parent-only updates
are not added. Duplicate applies the same conditional rule after source merging.
Each applied zero appears as conditional_save_default in defaultsApplied with
before/after/reason for the Task Hook preview.
No effective date, set, BU row, rate schedule, currency rate, DFF or translation
is invented. Explicit choices, including N and blank required values, are not
silently defaulted. The result reports applied defaults in the Task Hook change
shape (`path`, `before`, `after`, `reason`) alongside member/attribute provenance.

Preparation also checks explicit requests against the merged control state:
third-party scheduling, revenue/cost enablement, summary-task actual association,
periodic spread, forecast approval and cost rollup. It reports
`INACTIVE_OPTION` before writing when a requested activation is incompatible.
Defaults and unchanged inactive update values are preserved. This distinction
requires the normalized request plus retained baseline; CSV bytes alone cannot
establish which values the consultant asked to change.

The shared-conversion checkbox is transient. For an explicit request to apply
the same conversion attributes, use `copyConversionAttributes: true` after
resolving the source values. In the supported COST_ONLY PLAN_TYPE branch,
multicurrency copies Pc Cost/Rev rate type, date basis and date independently to
Pfc and RateSch, plus SpecPc to SpecPfc override flags. Single currency copies
Pfc Cost/Rev rate attributes to RateSch. It never copies cost values into revenue
values. A conflicting explicitly supplied destination blocks preparation.
The action requires a known cost rate type and date basis; none is defaulted.
For independent attributes, omit the action and supply the applicable fields.
There is no persistent checkbox column or `false` action.

For source-form business input, retain the effective input object in the
canonical request's optional `sourceInput`. `Curr_Set_Use_Conversion` accepts
Boolean true/false or those strings. True materializes the existing copy action;
false rejects a contradictory copy action and otherwise leaves independent
attributes alone. Invalid nonblank values block. This preserves canonical-only
callers and does not infer shared intent from equal rate values.
Pass that same object as `finalData.sourceInput` when building the preview.
The preview checks the actual persistent copy destinations before approval,
so a source true value cannot disappear behind a schema-valid ZIP. It also
adds explicit unverified warnings for each supplied profile, budget target
and forecast target; local validation does not prove their target eligibility.

### Check complete Business Unit evidence

The workflow's existing core GET client owns transport and header selection.
After its declared reference-acquisition step, save an evidence object with
`intent`, `requestContext` and ordered `pages`. `requestContext` contains
`targetOrigin`, `identity` (non-secret identity label), `language`, `runId`,
`acquiredAt`, `q`, and actual outgoing `headers`. If the workflow deliberately
uses the server default, retain `defaultFrameworkVersion` and its current
`defaultVersionEvidence` instead. Each page is the actual response including
items/count/offset/hasMore. Continue the same query/header/scope until hasMore
is false; advance offset by actual returned count. Never put tokens in headers
evidence; retain only the non-secret framework header.

```bash
python reference_evidence.py --input /absolute/project/artifacts/bu-evidence.json
```

The offline checker returns a unique visible active identity only after
completeness checks pass. No-match means absence within that visible query
scope. Existing FSM references require reconciliation with lookup visibility
and active state; do not label an incomplete search globally missing or choose
a similarly named BU automatically.

### Retain an accepted execution receipt

Before the authorized loader handoff, preflight the project artifacts directory
and retain a separate copy of the task-approved envelope. Preserve the actual
structured return value of the selected core adapter (including fileName,
dataSetName, uploadStatus, initiationStatus, ContentId and RequestId). Then:

```bash
python execution_receipt.py --envelope /absolute/project/artifacts/retained-approval.json --result /absolute/project/artifacts/initiation-result.json --archive /absolute/project/artifacts/prepared.zip --output /absolute/project/artifacts/execution-receipt.json --dry-run
```

Repeat without `--dry-run` to write a new receipt, then register it with the
existing project artifact/state services. The helper verifies local approval,
Run Book binding, bytes, filename and accepted IDs. It allowlists receipt
fields, refuses overwrite, never calls Fusion, and records initiated with
completionVerified=false. Do not recreate lost approval evidence or substitute
invented structured results. A receipt failure after acceptance permits local
evidence recovery only, never another upload. A later results request checks
this same accepted request before any fresh readback.

An update changing multicurrency includes the exact retained options rows and
propagates the parent choice, matching the task importer. Switching Y to N when
retained currency rows exist blocks as `DESTRUCTIVE_CURRENCY_RESET_EXCLUDED`:
the importer would delete those rows, even if they were omitted from the ZIP.
These transformations appear in `derivedChanges` with before/after provenance;
include them in the design-enforcement resource's Task Hook changes. They are
separate from `defaultsApplied`, which belongs to the defaulting resource.

An update requires the exact existing parent and patched child identities in its fresh
baseline. It merges only requested changes into those complete retained rows;
unrequested child collections remain absent, except retained options rows needed
for an explicit multicurrency or conversion-copy action. New children use
`insertRows`. It never removes children or deletes records. Preserve existing
data rather than using create defaults; submitted active empty buffers still
receive the conditional save default above. Run the same preview and byte checks
for every output.

### Insert children on an existing type

Keep `operation: update` and one retained parent identity in `rows`. Put explicitly
new rows under `insertRows`, keyed by set, rate, currency or translation member.
The helper requires every insert identity to be absent, rejects duplicate or
cross-parent rows, and leaves omitted existing collections untouched. Use `rows`
for existing-child changes; inserting an existing identity never becomes an
implicit update. A new translation requires Name, Language and SourceLang.
Only a new BU rate row receives its documented omitted mode default N. Currency
insertion includes the exact retained options/amount tuple and requires enabled
multicurrency; new rate rows require an eligible effective cost/revenue context.

### Rename using retained translation identity

Use `operation: update`, `rows` containing only the old parent Name, and
`rename: {"name": "New business name", "languages": ["US"]}`. Codex obtains
the application language from verified context; US here is synthetic example
data, never a universal default. Require one complete retained translation for
each selected language. The parent CSV Name and translation parent links stay
at the old name so FSM resolves the existing PlanTypeId; only selected translation
Name values change. SourceLang, descriptions and all other languages remain
retained. Reject name collisions visible in the complete baseline, unknown
languages and mixed rename/other changes. No old-name delete/new-parent create
is used. After successful import, re-export and verify names in the requested
languages before using the new identity in another operation. Do not claim a
global translation change from a one-language request.

### Duplicate with an absent new identity

Use `operation: create`, `duplicateFrom: "Existing business name"` and a new
parent Name in `rows`. Source parent/options must be uniquely retained and in
the supported PROJECT_PLAN/BUDGET/COST_ONLY branch. Copy the supported source
configuration without replaying general create defaults. Ordinary Duplicate
intent includes its set, BU-rate and currency collections; an explicit
`copyChildren` list selects a subset (an empty list excludes all three). Its
members are the exact corresponding CSV filenames. Planning options always
copy. Re-key every copied child to the new name and preserve the source rows.
Explicit requested values override the copied values and undergo normal gates.

Source-backed duplicate defaults are StartDate 1957/01/01, empty EndDate and
DefaultFinPlanTypeFlag N; DefaultAwdFinPlanTypeFlag remains new-record N. Explicit
dates and flags override them. Source-null fallbacks are N for
AsgnResInSingleCurrFlag, ManualSpreadFlag, MapActSummaryFlag,
EnableCostsForProjPlan and AllowFcstAmtCarryFlag, and START_DATE_PRJ_PLAN for
NtpRateDateType. Every applied fallback is disclosed. These defaults are specific
to Duplicate and differ from the new-type create-date policy.

Do not copy existing translated names to the new identity: supply new translation
rows explicitly when requested. Preserve DFF values by their exact attribute
names; do not reproduce the UI source's shifted parent Attribute1–Attribute20
setter anomaly. BudgetaryControlsFlag Y is blocked because the broad editor's
additional XCC children are not represented by this task's six-member package.
This is a disclosed mapping boundary, never a silently partial copy.

All actions use the same current target metadata, local byte validation and
checksum-bound Data Loader approval. Add `derivedChanges` to design-enforcement
rule changes, defaults to the defaulting rule, and preparation intent/row counts
to `finalData`. A validated package still reports server validation not_run until
the approved import and fresh export establish the actual result.

### Preview and approval

First follow the routed project workflow to select the task and evaluate the
ordered rule resources. Save the existing Task Hook input as JSON, retaining
the exact target environment and all other approval context in `finalData`:

```json
{
  "taskContextPath": "/absolute/project/state/task-context.json",
  "taskName": "Manage Project Plan Types",
  "sequence": 1,
  "finalData": {
    "archivePath": "/absolute/project/artifacts/plan-type.zip",
    "archiveSha256": "<SHA-256 of the exact prepared ZIP bytes>",
    "operation": "create",
    "environment": "<exact selected target environment>"
  },
  "ruleResults": []
}
```

The empty `ruleResults` above is a placeholder. Supply every evaluated resource
exactly once in the shared rule plan's order, including its status, issues, and
changes. Each change requires nonempty `path` and `reason`, plus `before` and
`after`; preparation's `defaultsApplied` entries can be used for the defaulting
resource. It cannot replace executable byte checks. Use `update` for an update
package; separate mixed-operation packages. Retain additional environment,
target, and payload context already required by the active project workflow.

From this `scripts` directory:

```bash
python import_preview.py build --input /absolute/project/artifacts/task-hook-input.json
```

Save the returned preview as a project artifact. Present that preview, the
exact target environment, and the immutable ZIP through the existing Data Loader
approval workflow. Only after explicit user approval of that result:

```bash
python import_preview.py approve --input /absolute/project/artifacts/preview.json
```

Save the returned approval envelope. Immediately before a separately authorized
loader handoff, verify the actual prepared ZIP:

```bash
python import_preview.py verify --input /absolute/project/artifacts/approved-envelope.json --archive /absolute/project/artifacts/plan-type.zip
```

The successful output is the core Task Hook's shared-loader envelope. Preserve it and
the exact verified bytes for the existing routed loader operation. These commands
do not submit anything. Changed bytes, target context, findings, or rule results
require rebuilding and approving the preview. A readiness waiver cannot bypass
this local task gate.

## Enforcement boundary

All new enforcement lives in this ERP task folder. Shared Task Hook and Data
Loader code are unchanged. Directly invoking generic loader commands can bypass
this task-local executable gate; the task workflow therefore mandates these
commands. This wrapper is not a claim that the unchanged generic loader has
independent task-contract or preview-digest enforcement. The wrapper's `verify`
step checks the prepared bytes, task-record digest and core Run Book approval
binding; the generic loader's
existing archive digest check then protects that handoff's byte identity.

Offline Python tests and synthetic fixtures live in this skill's
[`noship/tests/`](../noship/tests/README.md) folder. Run from the repository root:

```bash
python3 -B -m unittest discover -s pillars/erp/project-financial-management/project-control/manage-project-plan-types/noship/tests -v
```

The functional example YAML and historical regression notes remain under
`pillars/erp/project-financial-management/noship/tests/project-control/manage-project-plan-types/`.
See the [no-ship test README](../../../noship/tests/project-control/manage-project-plan-types/README.md)
for coverage and historical acceptance limits.

The [UI coverage record](../noship/tests/ui-coverage.md) lists the non-delete
acceptance target and remaining preparation/evidence gaps. Passing local tests
does not establish complete UI parity or deployed-target import acceptance.
