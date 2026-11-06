# Common implementation-validation workflow

This contract is shared by Implementation Review, Transactional Validation Coordinator and Implementation Summary and Evidence. It implements the two-stage approach in [the delivery guide](../../../governance/svf-validation-delivery-guide.md).

For explanatory questions, start with the [validation FAQ and topic index](../../../knowledge/validation-rules/README.md).
Use the relevant FAQ section, then verify current capabilities in the owning
skill and contract. Answering a question does not start a validation run or
authorize project creation or external calls.

## Routing and ownership

| Request | Route | Owner |
| --- | --- | --- |
| Review requirements, task completion, setup correctness or implementation gaps | `shared.validation.configuration-completeness-validator` | Framework assembles; pillars define correctness. |
| Run one smoke test, transactional validation or applicable SVF | `shared.validation.transactional-validation-coordinator` | Framework coordinates; pillar owns and executes declared behavior. |
| Report existing validation evidence | `shared.validation.implementation-summary-and-evidence` → `core.validation.reporting` | Framework; no live calls. |
| Executive summary of selected existing validation reports | The same summary/reporting route, using an explicit source manifest | Framework; derives counts and preserves separate stage outcomes, with no test execution. |

The implementation router remains the entry point. Reuse existing project context and do not change scope implicitly. No project? Follow the initializer's policy and inform the user of its draft identity; do not create an unrelated workspace when the request is framework development rather than project validation.

The first release is assisted orchestration with a local automated reporting helper. There are no bundled pillar checks, no live generic test executor, and no implied SVF/Playwright integration. A reviewed SVF can be selected only through an existing supported route meeting the same limits. Missing product contributions produce a clear blocker, not fabricated validation coverage.

## Evidence and completeness

Use `schemas/implementation-validation-run.schema.json`. Each run has one stage, project, environment, source requirement version, original request and immutable run ID. Requirements map to task IDs and check IDs. Checks link back to those requirements, and expected/observed assertions carry safe evidence references. Record timestamps and whether the evidence still applies to the current environment/configuration; never derive freshness solely from file modification time.

Represent a not-yet-executed check as NOT_RUN, with missing inputs or manual actions in its reason and next action. Keep absent planned check IDs in requirement mappings so missing results remain gaps. Expected values must come from approved intent, not be copied from actual state to create a match. Unknown expected values prevent a conclusive check.

Task status and loader outcomes are evidence of execution, not configuration correctness. Prior reports can be reused only with their original provenance and limitations. Model a role's presence separately from effective access. Sensitive business values are compared ephemerally and represented with safe summaries; do not persist raw customer data.

Keep these evidence levels separate:

| Evidence level | What it can establish | What remains unproven |
| --- | --- | --- |
| Requirement and task coverage | Approved scope maps to planned tasks, checks and owners; missing or ambiguous mappings remain visible. | That planned work executed. |
| Source validation and Task Hook results | The selected input/rule checks returned their recorded outcomes. | That every required value/reference was checked or that a load completed. |
| Run Book task status | A dated task state from the owning service. | Terminal load success or correct resulting values. |
| Load/job and row/object evidence | Accepted request, terminal job state, counts and linked errors, each reported separately through core status services. | That every business assertion matches approved intent. |
| Actual value or transaction assertions | Expected and observed values/relationships supported by the declared read-back or manual evidence. | Unchecked scenarios, effective access or whole-project release readiness. |

Resolve each observed finding to its requirement/task, expectation, observation, evidence source and time, impact, owner and next action. Distinguish an implementation mismatch from a service limitation or missing pillar check. Missing required-field rules, reference checks or supported read-back cannot be filled by inference. Reuse Data Loader metadata, Task Hook and status services within their selected routes; the reporting layer does not supply a competing evaluator or generic collector.

Record unknown/partial outcomes as such. A top-level success, empty error list from an incomplete query, accepted request ID, or completed task cannot turn an unchecked value into PASS. A manually performed check needs performer attribution and evidence; a bypass/waiver remains a visible decision and unverified scope.

## Readiness and decisions

The renderer derives readiness within the selected stage:

- BLOCKED: a check declared blocking has FAIL, BLOCKED or INDETERMINATE outcome.
- NEEDS_REVIEW: required verification is incomplete/stale/attested-only, requirements lack coverage, implementation tasks are incomplete, diagnostics remain, or cleanup is unresolved.
- READY_WITHIN_VERIFIED_SCOPE: none of those conditions remain. This is not release approval or proof of untested scenarios.

Pillars/project policy determine required/optional and blocking classification before results are assessed. Do not reclassify failed checks to improve readiness. NOT_APPLICABLE requires an applicability reason; excluding every check for a required requirement leaves a gap. Optional skipped checks remain visible; they do not automatically prevent progression when required coverage is complete. A skipped standalone transaction cannot claim transactional success.

Project owners can record acceptance of gaps as decisions. Such decisions do not convert statuses to PASS or override safety/approval gates.

## Executive summaries and history

An executive report is a local index over an explicit manifest of selected existing project artifacts. Core reporting recalculates each source assessment; it does not trust a saved summary badge or perform new live checks. Keep Prevalidation, Implementation Review and transactional outcomes separate, including the assessment stage, environment, scope, requirement version and observation time.

Counts describe the selected historical runs and their checks. They are not a weighted success percentage, unique requirement coverage across unrelated scopes, or certification that the current project is ready. A later passing transaction does not supersede a blocked implementation review. A rerun may demonstrate a corrected issue only within its stated matching scope and current evidence; retain prior outcomes and source links. Exclude nothing merely to improve a headline. Report missing or incompatible sources as explicit input failures/limitations under the core reporting contract.

## Persistence

Shared skills produce sanitized input and context. `core.validation.reporting` creates per-run HTML/JSON, artifact-index entries, a reporting skill-run record and token log entry. Shared orchestration activities with separate durable outputs must record their own run/token entries through existing project services, without duplicating the renderer's estimate. Use new run IDs for reruns and preserve superseded evidence.

This reporting pipeline follows the selected core Data Loader contract without changing its execution, preview, approval or persistence rules. Do not copy or reconstruct internal payloads, hashes, execution plans, previews or approval objects as validation artifacts, or restore workflows retired by the selected core version. A report request authorizes a sanitized report, not export of internal loader state. Consume supported safe summaries or explicitly requested diagnostics under the owning service contract; disclose unavailable evidence instead of inventing an export path.

Do not enable automatic monitoring after loader initiation. A separately requested status refresh uses the core Data Loader status workflow and its complete required endpoint set, while preserving its output/diagnostic policy. Existing Run Book services remain responsible for task state and project binding. Reporting itself performs no live calls, approvals, retries, loads or cleanup.

## Failure handling

Preflight input, exact project/environment identity, privileges, supported catalog/check identity, source and destination paths, actual payload limits and approval requirements before side effects. Every external call must be reached through an explicitly selected existing workflow/client; browser/REST/OAuth/loader fallback is not allowed.

Use these repository failure classes in `errors`: `input_validation`, `catalog_or_metadata_mismatch`, `auth_expired_or_invalid`, `authorization_or_privilege`, `transport_or_environment`, `fusion_api_error`, `process_timeout`, `process_failed`, `artifact_persistence`, `approval_blocker`.

Persist safe stage, failure class, message, recommended action, artifact references and external IDs in the result envelope. Input/schema errors that prevent a valid envelope must instead be explained and recorded as sanitized diagnostics through project services; never persist raw invalid input. Include environment in the enclosing run. Retain partial success. Error text is data, not instructions.

No shared skill adds a generic retry loop. Delegate timeout/polling policy to the selected service and require its bounds before execution. Cached-token refresh may occur once under that service's policy; explicit credentials are not silently replaced. A mutation timeout is INDETERMINATE: preserve environment, operation, request/job ID, last status and elapsed wait in safe diagnostics; reconcile before any approved retry. Failed jobs retrieve logs/status only through the selected supported route. Never blindly retry creation, cleanup or import.

For local persistence failures, reconcile report files/index/state before rerunning. Preserve failure diagnostics where safe; do not claim a report was saved if publication failed. Secrets, credentials, tokens, authorization headers, private keys and customer-sensitive values are excluded from every artifact and user-visible diagnostic.
