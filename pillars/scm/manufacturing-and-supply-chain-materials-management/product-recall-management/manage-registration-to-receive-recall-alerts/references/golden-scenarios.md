# Registration golden scenarios

Reviewed on 2026-11-10 for skill version 0.1.2, task ORA_MANAGE_REGISTRATION_TO_RECEIVE_RECALL_ALERTS. All facts below are synthetic. This is a developer review of assisted task guidance, declared graph outcomes, and delegated immutable-artifact behavior; it is not live Fusion validation or an executable replacement for server checks.

## Source and review method

- Input requirements: [ora_input_validation.md](../ora-resource/ora_input_validation.md), Required Groups and Field Validation.
- Profile and feature matching: [ora_reference_lookups.md](../ora-resource/ora_reference_lookups.md), Live Lookups.
- Singleton, identity, terms, uniqueness, and contract gates: [ora_design_enforcement.md](../ora-resource/ora_design_enforcement.md), Design Rules.
- Failure disclosure and recovery: [ora_error_handling.md](../ora-resource/ora_error_handling.md).
- Declared transitions: [ora_rule_registry.json](../ora-resource/ora_rule_registry.json).
- Immutable-artifact and approval lifecycle: [Data Loader](../../../../../../core/data-loader/SKILL.md#host-workflow) and [Task Hook](../../../../../../core/data-loader/task-hook/SKILL.md).

For each scenario, change only the named fact from its baseline. Review the owning rule, choose its declared outcome, and follow registry transitions with prerequisites until the expected terminal. Verify the stated next action does not authorize a write or bypass a stop condition. Results below record that source/graph review. Provider display labels are conceptual inputs, not invented REST attribute contracts. No payload, source snapshot, preview, approval envelope, or credential value is retained here.

## Synthetic baselines

Import baseline: selected project/pod identity agrees; private staging, containment, disclosure and operation-routing gates pass; one registration root in the final prepared archive; Microsoft mail address recall-ms@example.invalid; terms accepted; required Microsoft credential group privately supplied (presence only, no values); metadata confirms fields and create support; no current registration; mail uniqueness confirmed. Exact SITE profile child has 2026-10-01; one exact feature in the correct offering has EnabledFlag Y. Current-state evidence is assumed supplied for this review, not retrieved from an invented endpoint.

Google baseline changes the provider to Google, mail address to recall-google@example.invalid, and credential group to Client ID, Refresh Token, and Client Secret privately supplied; no Tenant ID substitution. Update baseline has exactly one existing record with a server-returned key and metadata-confirmed update support; credential requirements come from that verified update contract.

Validation baseline: explicit validateCredentials request and existing registration identity; all common design gates pass. The current package has no verified validation operation contract, so the actual supported result is a contract blocker. A hypothetical reviewed contract is not treated as present.

Paths below abbreviate RECALL.REGISTRATION node IDs: INPUT = VALIDATE-INPUT; SITE = LOOKUP-SITE-START-DATE; FEATURE = LOOKUP-FEATURE-OPTIN; DESIGN = ENFORCE-DESIGN; ISSUE = HANDLE-ISSUE; STOP = RETURN-ISSUES; IMPORT = DONE-IMPORT-PREFLIGHT. IMPORT permits only the core Task Hook preview/approval stage, never immediate submission.

## Task-specific scenario results

Every row was reviewed against the owning source and declared graph. PASS means the guidance and expected path agree; it does not certify a live endpoint or runtime implementation of these assisted checks.

| Case | Synthetic change | Expected path and result | Safe next action / disclosure | Review |
|---|---|---|---|---|
| REG-01 | Microsoft create baseline | INPUT valid → SITE valid → FEATURE enabled → DESIGN import_ready → IMPORT | Return ordered rule results to Task Hook and present the Data Loader preview; wait for approval | PASS |
| REG-02 | Google create baseline | INPUT valid → SITE valid → FEATURE enabled → DESIGN import_ready → IMPORT | Use Google input group; no Tenant ID substitution | PASS |
| REG-03 | Zero populated final-archive roots | INPUT invalid → ISSUE handled → STOP | Report root count zero; correct source and start a fresh preflight | PASS |
| REG-04 | Two populated roots converted from a spreadsheet | INPUT invalid → ISSUE handled → STOP | Report root count two; no partial import preview | PASS |
| REG-05 | Two populated DAT roots in the final archive | INPUT invalid → ISSUE handled → STOP | Count final archive rows; do not substitute the original source | PASS |
| REG-06 | Microsoft new registration lacks Client Secret | INPUT invalid → ISSUE handled → STOP | Identify missing field only; request private administrator input | PASS |
| REG-07 | Google new registration lacks Refresh Token; Tenant ID provided | INPUT invalid → ISSUE handled → STOP | Request Refresh Token privately; do not substitute Tenant ID | PASS |
| REG-08 | Unsupported mixed provider credentials | INPUT invalid → ISSUE handled → STOP | Resolve the selected provider and required input group | PASS |
| REG-09 | Unknown or read-only field rejected by verified metadata | INPUT invalid → ISSUE handled → STOP | Correct mapping and start a fresh preflight; do not guess attribute names | PASS |
| REG-10 | No profile definition, SITE child, or populated SITE value | INPUT valid → SITE missing_or_invalid → ISSUE handled → STOP | Route to profile-options for Site-level correction; no default date | PASS |
| REG-11 | SITE date 2026-02-30 or 20261001 | INPUT valid → SITE missing_or_invalid → ISSUE handled → STOP | Require a real calendar date in yyyy-MM-dd format | PASS |
| REG-12 | Effective session/user-level value exists but SITE is blank | INPUT valid → SITE missing_or_invalid → ISSUE handled → STOP | Effective or non-Site value is insufficient | PASS |
| REG-13 | Multiple SITE records | INPUT valid → SITE missing_or_invalid → ISSUE handled → STOP | Resolve ambiguous profile evidence | PASS |
| REG-14 | Feature EnabledFlag N | INPUT valid → SITE valid → FEATURE disabled → ISSUE handled → STOP | Route exact feature to its opt-in workflow; approval, refresh, and reread precede a new preflight | PASS |
| REG-15 | Zero/multiple exact feature matches, missing flag, or uncertain offering | INPUT valid → SITE valid → FEATURE ambiguous_or_failed → ISSUE handled → STOP | Resolve feature identity; existence/choices do not prove enablement | PASS |
| REG-16 | Unknown current registration count | INPUT valid → SITE valid → FEATURE enabled → DESIGN blocked → ISSUE handled → STOP | Obtain authorized current-state evidence; do not assume zero | PASS |
| REG-17 | Two existing registrations | INPUT valid → SITE valid → FEATURE enabled → DESIGN blocked → ISSUE handled → STOP | Resolve singleton conflict; never add a third registration | PASS |
| REG-18 | One existing registration with verified key and update support | INPUT valid → SITE valid → FEATURE enabled → DESIGN import_ready → IMPORT | Preview update through Task Hook; create is not the intended operation | PASS |
| REG-19 | One existing registration lacks server key or update capability | INPUT valid → SITE valid → FEATURE enabled → DESIGN blocked → ISSUE handled → STOP | Resolve key/support; never synthesize a key or add another record | PASS |
| REG-20 | Zero existing registrations but create support unverified | INPUT valid → SITE valid → FEATURE enabled → DESIGN blocked → ISSUE handled → STOP | Obtain target metadata before preview | PASS |
| REG-21 | Terms not accepted | INPUT invalid → ISSUE handled → STOP | Required input group fails; do not continue to design or a write | PASS |
| REG-22 | Mail uniqueness unconfirmed or address reused across pods | INPUT valid → SITE valid → FEATURE enabled → DESIGN blocked → ISSUE handled → STOP | Require distinct pod mail registration; preserve clone warning | PASS |
| REG-23 | Environment identity missing/mismatched | Pre-execution gate stops; if mismatch arises during a lookup, SITE lookup_failed or FEATURE ambiguous_or_failed → ISSUE handled → STOP | Discard cross-pod evidence and resolve target; no exploratory substitute call | PASS |
| REG-24 | Explicit credential validation with identity but no verified path/method/payload/privilege/side effects | INPUT valid → SITE valid → FEATURE enabled → DESIGN blocked → ISSUE handled → STOP | Report missing contract; no Data Loader import or UI substitution | PASS |
| REG-25 | Credential validation request lacks existing identity | INPUT invalid → ISSUE handled → STOP | Ask for existing registration identity; no validation call | PASS |
| REG-26 | Credential source resides in tracked files or project artifacts | INPUT invalid → ISSUE handled → STOP | Require private source; disclose field names only | PASS |
| REG-27 | Sanitized failure/result contains a credential-related server message | ISSUE disclosure rule applies; validation success cannot be claimed without a verified operation | Report failure class, missing field/contract, and sanitized message; omit client secret, refresh/access token, and full payload | PASS, guidance review |

## Immutable-artifact lifecycle review

These are assisted guidance/graph review cases, not claims that a new pillar runtime evaluator exists. The public core interfaces and current tests listed below provide the executable evidence.

| Case | Synthetic event | Expected behavior | Review |
|---|---|---|---|
| ARTIFACT-01 | XLSX source requires conversion | Data Loader prepares and persists the exact archive before Task Hook preview and approval | PASS, current provider contract |
| ARTIFACT-02 | Original source edited or removed after an intact artifact is approved | Submit the verified retained bytes without source rereads, metadata refresh or conversion | PASS, current provider test |
| ARTIFACT-03 | Intended data, mapping, target or rules change | New preflight, prepared archive, ordered task-rule results and approval; no silent overwrite | PASS, guidance review |
| ARTIFACT-04 | Process restarts, retained preflight/archive/envelope remain intact | Use the supported approved-preflight path and verify context/digest; no live-process handle is required | PASS, current provider contract |
| ARTIFACT-05 | Retained archive or bound environment/Run Book/task digest changes | Block submission before upload; fresh validation and approval required | PASS, current provider tests |
| ARTIFACT-06 | A required rule is blocked, omitted, duplicated or returned out of order | Task Hook cannot build an eligible preview | PASS, current Task Validator tests |
| ARTIFACT-07 | Synthetic credential is proposed inside finalData, ruleResults or project evidence | Assisted caller rejects it before the core command; core accepts arbitrary finalData and is not assumed to redact it | PASS, guidance review |
| ARTIFACT-08 | Populated source or generated archive would land in project storage | Block before preparation; require approved private staging with verified ownership, permissions, no links and no destination collision | PASS, guidance review |
| ARTIFACT-09 | Provider disclosure contract for credential-bearing source is unverified | Block before credential-bearing processing; never assume OAuth-token redaction covers registration fields | PASS, guidance review |
| ARTIFACT-10 | Actual target family is unknown, or ApplCore has no applicable nested Apps Common workflow | Block before import preparation; do not infer a target from the business-object name or bypass with a direct client | PASS, guidance review |
| ARTIFACT-11 | Source has a traversing/symlink archive member, executable object, macro or unsafe output path | Reject before processing; do not extract, launch Office or substitute another helper | PASS, guidance review |
| ARTIFACT-12 | Valid private source and sanitized finalData are ready | Complete Task Hook build, authorized approval, archive verification and Data Loader submission with unchanged envelopes | PASS, current public interfaces |

## Reproducible verification

Run these from the repository root. All automated checks use synthetic fixtures or mocked integrations. They do not authenticate or submit a live registration.

```bash
python3 -B -m unittest discover -s core/data-loader/task-hook/tests -p 'test_task_hook.py'
PYTHONPATH=core/data-loader/task-validator/scripts python3 -B -m unittest discover -s core/data-loader/task-validator/scripts/noship -p 'test_task_rule_execution.py'
PYTHONPATH=core/data-loader/tests:core/data-loader:core/data-loader/scripts python3 -B -m unittest \
  test_upload_and_initiate.FusionDataLoadTests.test_approved_generated_artifacts_skip_sources_metadata_and_rebuilds \
  test_upload_and_initiate.FusionDataLoadTests.test_approved_preflight_blocks_integrity_environment_run_and_task_changes \
  test_upload_and_initiate.FusionDataLoadTests.test_approved_task_preflight_rejects_task_digest_mismatch_before_upload \
  test_upload_and_initiate.FusionDataLoadTests.test_preflight_envelope_is_restrictive_and_detects_metadata_changes \
  test_upload_and_initiate.FusionDataLoadTests.test_cli_preflight_output_persists_generated_artifact_and_envelope \
  test_upload_and_initiate.FusionDataLoadTests.test_cli_approved_preflight_uploads_without_selecting_sources_and_removes_envelope
```

Relevant assertions in the current sources:

- Task Hook: ready plans require caller execution; unknown statuses stop; preview requires the supplied task context, digest and supported approval/envelope interfaces.
- Task Validator: `test_preview_requires_all_rules_to_pass_in_exact_order`, `test_preview_requires_explicit_override_for_overridden_rule`, and `test_loader_receives_only_data_covered_by_exact_approval` verify ordered results and approved data.
- Data Loader: `test_approved_generated_artifacts_skip_sources_metadata_and_rebuilds`, `test_approved_preflight_blocks_integrity_environment_run_and_task_changes`, `test_approved_task_preflight_rejects_task_digest_mismatch_before_upload`, and `test_preflight_envelope_is_restrictive_and_detects_metadata_changes` verify retained bytes and bindings.

Current-run results on 2026-11-10: Task Hook 10/10 and Task Validator 22/22 passed. The six focused Data Loader cases above are the required provider checks for this lifecycle; all six passed in the current run. The broader, unchanged Data Loader suite was also run with its local test server: 181/192 passed, with ten old filename expectations and one validation-order/error-message expectation failing. These broader dependency-suite failures are recorded separately rather than represented as successful registration evidence. They do not exercise the authored domain checks or change the supported retained-artifact contract. The audit report records commands, scope and limitations. Historical live-session tests are not current evidence. The lifecycle guidance follows [Data Loader](../../../../../../core/data-loader/SKILL.md), [Task Hook](../../../../../../core/data-loader/task-hook/SKILL.md) and the task's [execution-safety gates](execution-safety.md). The graph is recompiled from the authored Markdown and checked for eight ready nodes and valid terminal paths.

No live endpoint, server-side registration validation, UI parity, runtime registration-payload redaction or human merge approval is certified by these offline checks. Each live operation must pass its selected workflow's metadata, privilege, storage, disclosure, routing and approval gates. The undocumented validateCredentials operation remains blocked.
