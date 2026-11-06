# Registration golden scenarios

Reviewed on 2026-10-14 for skill version 0.1.1, task ORA_MANAGE_REGISTRATION_TO_RECEIVE_RECALL_ALERTS. All facts below are synthetic. This is a developer review of assisted task guidance, declared graph outcomes, and delegated session behavior; it is not live Fusion validation or an executable replacement for server checks.

## Source and review method

- Input requirements: [ora_input_validation.md](../ora-resource/ora_input_validation.md), Required Groups and Field Validation.
- Profile and feature matching: [ora_reference_lookups.md](../ora-resource/ora_reference_lookups.md), Live Lookups.
- Singleton, identity, terms, uniqueness, and contract gates: [ora_design_enforcement.md](../ora-resource/ora_design_enforcement.md), Design Rules.
- Failure disclosure and recovery: [ora_error_handling.md](../ora-resource/ora_error_handling.md).
- Declared transitions: [ora_rule_registry.json](../ora-resource/ora_rule_registry.json).
- Captured-source and approval lifecycle: [Data Loader](../../../../../../core/data-loader/SKILL.md#host-workflow) and [Task Hook](../../../../../../core/data-loader/task-hook/SKILL.md).

For each scenario, change only the named fact from its baseline. Review the owning rule, choose its declared outcome, and follow registry transitions with prerequisites until the expected terminal. Verify the stated next action does not authorize a write or bypass a stop condition. Results below record that source/graph review. Provider display labels are conceptual inputs, not invented REST attribute contracts. No payload, source snapshot, preview, approval envelope, or credential value is retained here.

## Synthetic baselines

Import baseline: selected project/pod identity agrees; one captured registration root; Microsoft mail address recall-ms@example.invalid; terms accepted; required Microsoft credential group privately supplied (presence only, no values); metadata confirms fields and create support; no current registration; mail uniqueness confirmed. Exact SITE profile child has 2026-10-01; one exact feature in the correct offering has EnabledFlag Y. Current-state evidence is assumed supplied for this review, not retrieved from an invented endpoint.

Google baseline changes the provider to Google, mail address to recall-google@example.invalid, and credential group to Client ID, Refresh Token, and Client Secret privately supplied; no Tenant ID substitution. Update baseline has exactly one existing record with a server-returned key and metadata-confirmed update support; credential requirements come from that verified update contract.

Validation baseline: explicit validateCredentials request and existing registration identity; all common design gates pass. The current package has no verified validation operation contract, so the actual supported result is a contract blocker. A hypothetical reviewed contract is not treated as present.

Paths below abbreviate RECALL.REGISTRATION node IDs: INPUT = VALIDATE-INPUT; SITE = LOOKUP-SITE-START-DATE; FEATURE = LOOKUP-FEATURE-OPTIN; DESIGN = ENFORCE-DESIGN; ISSUE = HANDLE-ISSUE; STOP = RETURN-ISSUES; IMPORT = DONE-IMPORT-PREFLIGHT. IMPORT permits only the core session preview/approval stage, never immediate submission.

## Task-specific scenario results

Every row was reviewed against the owning source and declared graph. PASS means the guidance and expected path agree; it does not certify a live endpoint or runtime implementation of these assisted checks.

| Case | Synthetic change | Expected path and result | Safe next action / disclosure | Review |
|---|---|---|---|---|
| REG-01 | Microsoft create baseline | INPUT valid → SITE valid → FEATURE enabled → DESIGN import_ready → IMPORT | Return rules to the same session and present its preview; wait for approval | PASS |
| REG-02 | Google create baseline | INPUT valid → SITE valid → FEATURE enabled → DESIGN import_ready → IMPORT | Use Google input group; no Tenant ID substitution | PASS |
| REG-03 | Zero populated captured roots | INPUT invalid → ISSUE handled → STOP | Report root count zero; correct source and start a fresh session | PASS |
| REG-04 | Two populated captured spreadsheet roots | INPUT invalid → ISSUE handled → STOP | Report root count two; no partial import preview | PASS |
| REG-05 | Two populated captured DAT roots | INPUT invalid → ISSUE handled → STOP | Count captured native rows; no conversion or reread needed | PASS |
| REG-06 | Microsoft new registration lacks Client Secret | INPUT invalid → ISSUE handled → STOP | Identify missing field only; request private administrator input | PASS |
| REG-07 | Google new registration lacks Refresh Token; Tenant ID provided | INPUT invalid → ISSUE handled → STOP | Request Refresh Token privately; do not substitute Tenant ID | PASS |
| REG-08 | Unsupported mixed provider credentials | INPUT invalid → ISSUE handled → STOP | Resolve the selected provider and required input group | PASS |
| REG-09 | Unknown or read-only field rejected by verified metadata | INPUT invalid → ISSUE handled → STOP | Correct mapping and start a fresh session; do not guess attribute names | PASS |
| REG-10 | No profile definition, SITE child, or populated SITE value | INPUT valid → SITE missing_or_invalid → ISSUE handled → STOP | Route to profile-options for Site-level correction; no default date | PASS |
| REG-11 | SITE date 2026-02-30 or 20261001 | INPUT valid → SITE missing_or_invalid → ISSUE handled → STOP | Require a real calendar date in yyyy-MM-dd format | PASS |
| REG-12 | Effective session/user-level value exists but SITE is blank | INPUT valid → SITE missing_or_invalid → ISSUE handled → STOP | Effective or non-Site value is insufficient | PASS |
| REG-13 | Multiple SITE records | INPUT valid → SITE missing_or_invalid → ISSUE handled → STOP | Resolve ambiguous profile evidence | PASS |
| REG-14 | Feature EnabledFlag N | INPUT valid → SITE valid → FEATURE disabled → ISSUE handled → STOP | Route exact feature to its opt-in workflow; approval, refresh, and reread precede a new preflight | PASS |
| REG-15 | Zero/multiple exact feature matches, missing flag, or uncertain offering | INPUT valid → SITE valid → FEATURE ambiguous_or_failed → ISSUE handled → STOP | Resolve feature identity; existence/choices do not prove enablement | PASS |
| REG-16 | Unknown current registration count | INPUT valid → SITE valid → FEATURE enabled → DESIGN blocked → ISSUE handled → STOP | Obtain authorized current-state evidence; do not assume zero | PASS |
| REG-17 | Two existing registrations | INPUT valid → SITE valid → FEATURE enabled → DESIGN blocked → ISSUE handled → STOP | Resolve singleton conflict; never add a third registration | PASS |
| REG-18 | One existing registration with verified key and update support | INPUT valid → SITE valid → FEATURE enabled → DESIGN import_ready → IMPORT | Preview update in core session; create is not the intended operation | PASS |
| REG-19 | One existing registration lacks server key or update capability | INPUT valid → SITE valid → FEATURE enabled → DESIGN blocked → ISSUE handled → STOP | Resolve key/support; never synthesize a key or add another record | PASS |
| REG-20 | Zero existing registrations but create support unverified | INPUT valid → SITE valid → FEATURE enabled → DESIGN blocked → ISSUE handled → STOP | Obtain target metadata before preview | PASS |
| REG-21 | Terms not accepted | INPUT invalid → ISSUE handled → STOP | Required input group fails; do not continue to design or a write | PASS |
| REG-22 | Mail uniqueness unconfirmed or address reused across pods | INPUT valid → SITE valid → FEATURE enabled → DESIGN blocked → ISSUE handled → STOP | Require distinct pod mail registration; preserve clone warning | PASS |
| REG-23 | Environment identity missing/mismatched | Pre-execution gate stops; if mismatch arises during a lookup, SITE lookup_failed or FEATURE ambiguous_or_failed → ISSUE handled → STOP | Discard cross-pod evidence and resolve target; no exploratory substitute call | PASS |
| REG-24 | Explicit credential validation with identity but no verified path/method/payload/privilege/side effects | INPUT valid → SITE valid → FEATURE enabled → DESIGN blocked → ISSUE handled → STOP | Report missing contract; no Data Loader import or UI substitution | PASS |
| REG-25 | Credential validation request lacks existing identity | INPUT invalid → ISSUE handled → STOP | Ask for existing registration identity; no validation call | PASS |
| REG-26 | Credential source resides in tracked files or project artifacts | INPUT invalid → ISSUE handled → STOP | Require private source; disclose field names only | PASS |
| REG-27 | Sanitized failure/result contains a credential-related server message | ISSUE disclosure rule applies; validation success cannot be claimed without a verified operation | Report failure class, missing field/contract, and sanitized message; omit client secret, refresh/access token, and full payload | PASS, guidance review |

## Captured-source lifecycle review

| Case | Synthetic event | Expected behavior | Evidence / review |
|---|---|---|---|
| SESSION-01 | Source file edited/deleted after capture | Evaluate returned captured records/native sources; never reread file into pending preview | Updated skill and input guidance; core MemorySessionTests.test_source_deleted_config_changed_uses_snapshot_without_writes passed |
| SESSION-02 | XLSX validation reaches preview before approval | No DAT/ZIP serialization, upload, or initiation | Core MemorySessionTests.test_no_serialization_or_writes_before_approval and full session suite passed |
| SESSION-03 | User corrects data, target, mapping, or task rules | Cancel and start a new session; obtain that session's approval | Updated skill and error recovery guidance reviewed; core tests enforce frozen-plan integrity |
| SESSION-04 | Approval arrives for the pending live preview | Submit through retained session using captured records/configuration; generate DAT/ZIP only now | Full core session suite passed, including test_actions_and_effective_dates_survive_approval_without_source_rereads |
| SESSION-05 | Session lost, expired, or old approval supplied | Fresh validation and approval; no replay into a new process | Updated skill/error guidance and session invalid-approval/expiry tests in passing core suite |

## Verification record

- In-memory recompilation of the task from Markdown matches the stored eight-node registry after regeneration.
- Execution planner returns planned, task readiness ready, eight nodes, and no override.
- `python3 -B -m unittest discover -s tests -p 'test_load_session.py'` from core/data-loader: 40 tests passed; all Fusion writes mocked.
- `python3 -B -m unittest discover -s core/data-loader/task-hook/tests -p 'test_task_hook.py'` from repository root: seven tests passed.
- Source/graph review above covers the registration-specific gates without creating a duplicate pillar validator or guessing a Fusion contract.

Runtime redaction of registration credential payloads and the undocumented validateCredentials operation remain outside this local review. These require a verified operation contract and authorized integration evidence before live use. No live execution, human merge approval, or functional SME approval is claimed.
