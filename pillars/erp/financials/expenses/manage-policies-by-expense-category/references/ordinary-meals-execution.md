# Ordinary Meals Excel-to-FSM execution

Use this route for user values within meals-single-currency-v2. No task-local
trial vector, private companion or test name/date/amount is required. Two Meals
entities are ready for input validation and native preflight; other17remain
outside authoring scope. Native import approval remains mandatory.

## Supported workbook values

Create one or more policies, each with one or more effective-dated rates. Enter Policy Name, optional Description
(skill bounds80/240characters), a currency currently enabled/active in the target,
Single Instance Limit Yes/No, Daily Sum Limit Yes/No, either Policy Enforcement
label and explicit warning/display/prevention Yes/No controls. At least one limit
must be enabled. Rate amounts must be finite and nonnegative, supplied for each
enabled limit and blank for disabled limits. Rate Start Date is required on
create and for locating an existing rate. Supply End Date for bounded periods;
blank means open-ended. Each period must end on/after its Start Date, and periods
for the same policy must not overlap (both endpoints are inclusive). Full rate
keys and alternate keys excluding Start Date must be unique. An unmatched key
requests CREATE; an exact existing key requests UPDATE. Never infer a key rename
or automatically close an existing open period. End Date uses YYYY/MM/DD as a
user-authorized engineering extension; it has not been live reconciled.

Reimburse upper limit maps to UPPER and requires all three warning/display/
prevention flags No. Generate policy violation maps to VIOLATION and permits
warning/display/prevention controls. Warning Yes requires Warning Tolerance;
prevention Yes requires Error Tolerance. Display Yes requires warning Yes.
Tolerance values are nonnegative percentage numbers, not fractional percentage
format cells; warning must be strictly less than error when both are present.
New/changed inactive tolerance inputs are rejected, while existing inactive
stored tolerances may be preserved after turning controls off.

Mode remains SINGLE, with protected DRAFT policy/rate statuses and disabled
role/location flags. Child currency/type remain blank rather than copying the
parent code. Hidden include flags serialize blank on create and are expected to
export N under the original accepted observation; audits are system-generated.
Disclose/reconcile actual differences instead of silently normalizing the CSV.

Updates can change Description, either amount, limit flags, enforcement,
warning/display/prevention controls and active tolerances. Preserve the exact
Policy Name, Start Date/End Date keys, currency, statuses and hidden fields. Parent-only and
rate-only requests are allowed for compatible policies with multiple rates. All omitted cells
preserve existing values. Enabling a limit requires its rate amount in the same
request unless already present. Disabling a populated limit cannot implicitly
clear the saved amount and remains unsupported. There is no rename, blank
clearing, currency/mode/existing-date-key/status/determinant change. New
nonoverlapping rates may be added to existing policies. These restrictions are
validated against every resulting policy and all its rates, including retained
rows absent from the workbook. A parent flag change must be compatible with
every sibling rate, not just rates supplied in the request. Retained currencies
must be checked for every selected parent, including rate-only selections in a
mixed request. Only supplied rows and exact parent context go into the sparse ZIP.

Batch operations retain requires_live_qualification=true until actual reconciliation.
An invalid row blocks the entire local candidate; this does not promise Fusion
batch atomicity. Native preview/approval covers the exact whole ZIP. Reconcile
each policy, each full rate key, untouched siblings and unrelated baseline rows;
preserve partial results and errors without automatic replay or rollback.

The original basic USD/single-instance/VIOLATION/controlsNo create and Description/
limit update have accepted live observations. Expanded input combinations have
source-backed local validation and explicit user authorization to broaden input,
but no new live reconciliation yet. The build review flags expanded inputs with
requires_live_qualification=true and live_qualified=false. Rule evaluation retains
a warning; disclose it before the native approval preview. Do not relabel those
combinations as accepted live outcomes or promise guaranteed success.

## Current target and baseline

The historical observation release and result hashes are retained in
accepted-meals-profile.json; its private target identity is omitted. No target
receives historical qualification from that redacted identity. Runtime may use any explicitly
selected environment/release with a fresh approved baseline, exact task schema,
matching target and release provenance, and operation-bound currency evidence.
A different environment or release is
not a live-qualified outcome: retain requires_live_qualification=true and
live_qualified=false through candidate review and native rule warnings until
per-run reconciliation. Schema drift fails closed pending a reviewed contract
extension and evidence; removing the release allowlist does not establish live
equivalence across releases. Reusable input parameterization remains a bounded engineering
extension, not proof of every possible input. See that profile for observation
hashes and limits; its summary is shipped with the skill, with no dependency on
private project files or development-only services.

1. Use the active project and Run Book through implementation-router. Read the
   configured environment/origin through the core authentication service and
   verify the task binding. A workbook or historical acceptance is not execution
   authority. Local parser and dry-run work do not require a live call.
2. Validate the workbook using workbook_intake.py. Obtain a fresh same-task
   current-data export through shared.setup-export.task-level-export after its
   exact target/POST/body approval. Store the ZIP under the current project's
   exports directory. Reuse a same-day actual export only if still current and
   correctly bound. On timeout retain the process ID and wait for user retry;
   never repeat the POST automatically.
3. Record the actual shared-route observation, not a made-up receipt. The existing
   baseline_evidence.verify contract requires plan/approval fields environment,
   origin, method POST, path /fscmRestApi/resources/11.13.18.05/setupTaskCSVExports,
   body with TaskCode and its identical SetupTaskCSVExportProcess child code.
   Approval planSha256 binds the plan bytes. Receipt fields recordedFrom
   observed-declared-route-result, processId, taskCode, environment, origin,
   completed true, retrieved FileContent, artifactSha256, artifactBytes,
   exportPlanSha256 and approvalSha256 bind the actual result. Also record
   observed_at_utc from the actual completed download; it must be today's UTC
   observation, not a refreshed timestamp on an old result. Never author an
   approval before the user's actual decision.
4. Select reference_lookup and plan then run capture_currency_reference.py
   through its declared core REST client. Bind the current workbook/baseline/
   runtime/target/date. Supply --project-root and a new --output-dir under that
   project's artifacts directory for both plan-only and --execute modes.
   Operations contain entity ORA_EXM_MEALS_POLICY, exact
   policy_name, create or update determined from baseline, currency_code equal to the exact supplied/retained code.
   For rate-only updates validate the retained parent's currency as update.
   Capture eligibility is not import approval. No geography/role reference
   lookups apply to this fixed profile. The source-backed choice domains plus existing
   source-bound label/code mappings resolve them locally.
5. Run the normal build_fsm_from_workbook.py CLI with --workbook, --baseline-zip,
   --project-root, --output-dir, --environment, --baseline-process-id, --baseline-receipt,
   --baseline-export-plan, --baseline-export-approval, --currency-receipt,
   --target-origin and --validation-date YYYY-MM-DD. Use --dry-run first. The
   ordinary default runtime applies; never pass a private trial contract.
   It validates the rule plan, exact19schemas/634columns, selected target and release provenance,
   fresh evidence, final profile and identities before writing candidate.zip.
   The ZIP contains selected rows/owning parent only; other entities are
   header-only. Descriptor/nonCSV members/inventory/order remain baseline-exact.

All local writers, including workbook_intake.py read/project and the currency
capture planner, require the selected initialized --project-root and a new
destination below its artifacts directory. The core artifact service rejects
outside-project paths, another project, `_template`, missing/invalid project
state, traversal, symlinked ancestors/leaves and existing outputs before writing.
Dry-runs validate the same destination without creating it. Python callers pass
project_root explicitly; Task Hook's in-memory evaluation does not write files.
Artifact registration/versioning remains owned by the active workflow's declared
core services; this preflight does not create a project or grant approval.

## Native import and reconciliation

Follow core.data-loader's current normal FSM workflow with the generated ZIP and
selected task. Only after native final-artifact/preflight validation invoke
the core Task Hook data-load route. At its planned read-only rule evaluation
step run check_candidate_rules.py with the same builder inputs plus
--candidate-zip pointing at the exact final immutable native upload artifact.
It regenerates the candidate in memory before preview, checks byte identity and
emits actual passed results for the five resources. Any mismatch stops; do not
pass blank results or use historical waivers. Feed its ruleResults unchanged to
the native Task Hook evaluation/preview sequence. This helper creates no native
approval envelope and grants no submission authority.

Render the core native preview and wait for later contextual approval, unless
the current core flow's explicit same-request auto-approval rule applies. After
approval, verify retained artifact/context/native envelope integrity only; do
not reopen/rebuild the workbook, requery references or rerun task rules. Use
native approve-preview and verify-approved-archive output unchanged with core
Data Loader's approved-preflight service. Never use a development companion,
direct import endpoint or manually constructed envelope. Return native Markdown.
Accepted initiation is terminal; query load status/errors only when requested.

After a successful requested status check, obtain separate approval for a fresh
current-data export and reconcile complete business rows and audits, all
non-target full rows,19schemas and37ordered metadata records. CREATE expectations
include only the two disclosed hidden blank-to-N values and generated audits;
report these raw differences rather than claiming exact submitted-cell equality.
UPDATE preserves all other cells/creation audits; report actual update audit
effects. Sequence-only metadata drift remains a strict finding, not equivalence.
Two consecutive controlled exports reproduced changes in four Mileage
NodeSequence values without an intervening setup import; all 19 CSV row
multisets, including audit cells, were identical. This supports a bounded
export-variance disposition for that observation, not a policy-update effect
or universal sequence equivalence. Retain the original strict comparison and
its evidence. Build every later candidate from its own fresh descriptor and
require byte-identical submission metadata; structural metadata drift still
stops execution. Do not rewrite sequence values or reuse an older descriptor.
Failure/partial/mismatch stops without replay/repair; obtain a human completion
or retry decision. No outcome promises guaranteed cleanup or success for every
value or circumstance.
