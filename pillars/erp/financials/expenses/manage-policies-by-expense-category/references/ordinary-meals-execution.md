# Policies Excel-to-FSM execution

Use this ordinary workbook route for the eight reviewed category profiles in
[Supported profiles](../SKILL.md#supported-profiles). The legacy runtime name
meals-single-currency-v2 is retained for compatibility, not as a category allowlist.
No private trial vector, companion or test name/date/amount is required.
All sixteen category policy/rate entities have their own bounded create/update
contracts. Per Diem value rows are dependent task effects, never independent
workbook targets; the two determinant entities remain preservation-only.
Source-qualified preparation does not establish target parity or live creation.
The independently reconciled five-category case is recorded in
[live verification](live-verification-scope.md); its result is separate from
source qualification and does not waive any gate for subsequent candidates.
Respect each category's remaining shape limits and existing update uncertainty.
Native final-artifact validation and import approval remain mandatory.

## Initial Meals and Accommodations values

Within these two profiles, create one or more policies, each with one or more effective-dated rates. Enter Policy Name, optional Description
(skill bounds80/240characters), a currency currently enabled/active in the target,
For Meals, enter Single Instance Limit Yes/No and Daily Sum Limit Yes/No. For
Accommodations, the grey merged Daily Limit? Yes applies to every policy row;
blank row indicators inherit Yes and explicit No/N is rejected. Supply Daily Limit
on its rates. Both categories accept either Policy Enforcement
label; VIOLATION uses explicit warning/display/prevention choices, while UPPER
derives those disabled controls as No and both tolerances as empty. At least one limit
must be enabled. Rate amounts must be finite and nonnegative, supplied for each
enabled limit and blank for disabled limits. Rate Start Date is required on
create and for locating an existing rate. Supply End Date for bounded periods;
blank means open-ended. Each period must end on/after its Start Date, and periods
for the same policy must not overlap (both endpoints are inclusive). Full rate
keys and alternate keys excluding Start Date must be unique. An unmatched key
requests CREATE; an exact existing key requests UPDATE. Never infer a key rename
or automatically close an existing open period. End Date uses YYYY/MM/DD as a
user-authorized engineering extension; it has not been live reconciled.

Reimburse upper limit maps to UPPER. Selecting it in a policy row supplies
Policy Violation Warning, Display Warning to User and Prevent Report Submission
as No, and Warning/Error Tolerance as empty, without separate input or
confirmation. Explicit No/N is accepted; explicit Yes or any nonempty tolerance,
including zero, returns a cell-specific upper-limit-policy error. This selection
also resets saved values for these five fields on an update; the reset is part
of the exact candidate review, not generic blank clearing. Omitting enforcement
from an update preserves existing values. This rule applies to Meals,
Accommodations, Entertainment, Car Rental and admitted Miscellaneous UPPER modes;
it does not broaden category operation or rate-mode support.
Generate policy violation maps to VIOLATION and permits
warning/display/prevention controls. Warning Yes requires Warning Tolerance;
prevention Yes requires Error Tolerance. Display Yes requires warning Yes.
Tolerance values are nonnegative percentage numbers, not fractional percentage
format cells; warning must be strictly less than error when both are present.
New/changed inactive tolerance inputs are rejected, while existing inactive
stored tolerances may be preserved after turning controls off, except for an
explicit UPPER selection's No/empty reset.

Mode remains SINGLE, with protected DRAFT policy/rate statuses and disabled
role/location flags. Child currency/type remain blank rather than copying the
parent code. Hidden include flags serialize blank on create and are expected to
export N under the original accepted observation; audits are system-generated.
Disclose/reconcile actual differences instead of silently normalizing the CSV.

Updates can change Description, either amount, limit flags, enforcement,
warning/display/prevention controls and active tolerances. Preserve the exact
Policy Name, Start Date/End Date keys, currency, statuses and hidden fields. Parent-only and
rate-only requests are allowed for compatible policies with multiple rates. All omitted cells
preserve existing values except for the explicit UPPER reset described above.
Enabling a limit requires its rate amount in the same
request unless already present. Disabling a populated limit cannot implicitly
clear the saved amount and remains unsupported. There is no rename, generic blank
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

## Additional category profiles

Use the owning sheets, [field contracts](fsm-runtime-contract.json), and
[category guidance](../SKILL.md#supported-profiles), not the initial Meals fields
or observation as substitutes for another category's business rules.

- Entertainment includes attendee controls and optional single/daily/yearly
  limits; some count-only or attendee-information policies require no rates.
- Car Rental uses complete SINGLE daily-limit groups and its fixed grey Yes
  indicator. Airfare uses explicit no-determinant CATCH_ALL flight-class groups
  without currency inputs; target lookup eligibility cannot admit UI-excluded FIRST.
- Miscellaneous supports LIMIT, PERCENT and BOTH with explicit eligibility,
  enabled amounts and annual reset choices. PERCENT deliberately has no monetary
  currency setting; do not supply a currency default by analogy.
- Mileage requires its complete base and enabled add-on groups, full rate keys
  and qualified company-code evidence. Its reviewed inactive commute encoding
  never supplies an active business choice or changes update omission behavior.
- Per Diem admits the reviewed wholly new formula/component groups with exact
  internal deduction effects. ANCHOR status is derived VALID; other admitted
  rates are DRAFT. New percentage time ranges, OTHER_STANDARD lower bounds,
  equal-hour minute ties, dormant time-MEALS components and existing-parent
  child/value creation remain outside the admitted create recipe.

Existing expanded-category business updates retain their exact-field uncertainty
decision route. A decision for one plan never qualifies another field/candidate
or grants an operation, missing reference, implicit clearing or import authority.
All Rate Determinants remain excluded.

## Current target and baseline

The historical observation target is retained in accepted-meals-profile.json
as historical evidence, not a release allowlist. Runtime may use any explicitly
selected environment/release with a fresh approved baseline, exact task schema,
matching target and release provenance, and operation-bound currency evidence.
Pod labels compare case-insensitively across exports, reference receipts and the
configured profile; their original spelling and artifact bytes are preserved.
Different pod names or origins still fail target checks. Business identifiers,
lookup codes, immutable approval hashes and source bindings remain exact.
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
   Use the exact category entity, policy name, actual baseline operation and
   supplied/retained currency selected by the ordinary reference gate. Rate-only
   selections still validate any consumed retained parent currency; use the
   actual parent operation rather than guessing it from the child operation.
   Airfare has no currency input. Apply the separate requirements of nonmonetary
   branches rather than copying the initial Meals currency example.
   Other consumed lookup choices use capture_policy_lookup.py through its
   declared reference route, with exact field, code, policy and operation.
   For a workbook with multiple choices, use its JSON-array batch selection
   input and consume the resulting single lookup-receipts.json index. Missing
   evidence is a normal reference-capture step, not a per-field approval or
   manual-workbook correction. See [batch capture](expanded-lookup-capture.md#workbook-batches).
   The lookup receipt index supports a single path or a literal per-code path
   map; every receipt and consumed context must pass ordinary preflight.
   Dynamic Mileage company references use their qualified consuming context.
   No geography/role lookup or Rate Determinant admission follows from this step.
   Capture eligibility is not field-write or import approval.
5. Run the normal build_fsm_from_workbook.py CLI with --workbook, --baseline-zip,
   --project-root, --output-dir, --environment, --baseline-process-id, --baseline-receipt,
   --baseline-export-plan, --baseline-export-approval,
   --target-origin and --validation-date YYYY-MM-DD. Use --dry-run first. The
   ordinary default runtime applies; never pass a private trial contract. Include
   currency evidence when required, the lookup receipt index for consumed choices,
   and any separately accepted exact-field decision requested by preparation.
   It validates the rule plan, exact19schemas/634columns, selected target and release provenance,
   fresh evidence, final profile and identities before writing candidate.zip.
   The ZIP contains selected rows/owning parent only; other entities are
   header-only. Descriptor/nonCSV members/inventory/order remain baseline-exact.

All local writers, including workbook_intake.py read/project and the currency
capture planner, require the selected initialized --project-root and a new
destination below its artifacts directory. The task-local path preflight rejects
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
follow the exact category's reviewed managed, derived and empty-field contracts.
The initial Meals observation permits only its two disclosed hidden blank-to-N
values and generated audits; do not apply that normalization to another category
by analogy. Report actual raw differences rather than claiming exact submitted-cell equality.
UPDATE preserves all other cells/creation audits; report actual update audit
effects. Structural or undeclared sequence drift remains a blocker. The source-reviewed
export-local policy admits only validated sequence-only changes, retains their raw
differences, and never rewrites submission metadata. See metadata-sequence-evidence.md.
Failure/partial/mismatch stops without replay/repair; obtain a human completion
or retry decision. No outcome promises guaranteed cleanup or success for every
value or circumstance.

## Accommodations extension

The same workflow also supports Accommodations and Accommodations Rates. Each
populated Accommodations policy row inherits the grey merged Daily Limit? value
Yes when blank; explicitly entering No/N returns a cell-specific preflight error. The
indicator is workbook-only and is never serialized as a parent CSV attribute.
Rates accept Policy Name, Daily Limit, Start Date and optional End Date. Daily
Limit is always applicable and must be finite and nonnegative. Blank updates
preserve saved amounts; zero is explicit. Currency, enforcement and warning
controls follow the same reduced model as Meals. Role, location, seasonal rate
and gender determinants are excluded, including retained selected baseline rows.

Policy/rate identities and currency receipts are scoped by category. Meals and
Accommodations may use the same Policy Name without sharing parent context or
reference evidence. Only selected rows and exact category parents are submitted;
other CSVs remain header-only. Accommodations always reports live qualification
pending. The authoring source, serialization assumptions and historical source
facts are recorded in accommodations-profile.json; no Meals observation is
claimed as an Accommodations result. Native approval authorizes an attempt,
followed by fresh export reconciliation through the declared workflow.
