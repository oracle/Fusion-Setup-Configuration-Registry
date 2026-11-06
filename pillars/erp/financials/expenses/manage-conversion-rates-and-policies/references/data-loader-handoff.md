# Maintenance Data Loader handoff

The task builds a review-only native FSM ZIP. It does not authenticate, submit,
approve, or establish live readiness. The compiled registry describes creates
with source-required fields and merged updates preserving nullable percentages.
Evaluate every runtime gate; ready authoring
is not passed preflight or mutation approval. Unsupported operations remain
blocked. Never import directly, select another executor or fabricate passed
Task Hook results.

Read `core/data-loader/SKILL.md` and `core/data-loader/task-hook/SKILL.md` from
the repository root before execution. The maintenance branch uses retained
preflight and Task Hook envelopes; it provides no `load_session.py` API.

1. Through the Router and active project Run Book, bind the exact task,
   environment, export provenance and intended changes. Compare the actual core
   OAuth target and Run Book server/run ID with the selected destination.
   Obtain fresh same-target template and baseline through the declared export
   workflow and its gates. Resolve task readiness, reference checks and semantic
   findings before live execution. Local review preparation may report blockers.
2. Use `build_fsm_from_workbook.py` to produce a new candidate in authorized
   protected local storage. Keep customer data outside tracked source and do not
   store it under `project/` contrary to repository policy. `--dry-run` writes
   no candidate. `build_in_memory` is an offline helper, not a live core route.
3. Run normal core validation without upload authorization, retaining preflight:

   ```text
   python3 core/data-loader/scripts/upload_and_initiate.py <candidate.zip> --task-routed --properties <core-environment.properties> --run-config <core-runbook.properties> --preflight-envelope-output <protected-local-directory/preflight.json>
   ```

   Only core's approval-stage exit with a produced preflight is expected. Other
   failures stop the workflow. Hold its provisional approval report internally.
4. Invoke Task Hook's `data-load` route with the selected task context, exact
   task name `Manage Conversion Rates and Policies` and positive sequence.
   Execute all returned read-only rules against the immutable artifact and
   retained evidence. Use `scripts/validate_references.py` to evaluate fresh complete core-fetched
   reference batches against the merged parent and child rows, selected environment
   and core-preflight digest. Record the real evidence in ordered ruleResults.
   Missing, blocked or incomplete task guidance is not a passing result. Then use `build-data-load-preview --input-stdin`
   with context, task, sequence, actual ordered `ruleResults` and `finalData`
   bound to the core-preflight `archiveSha256`.
5. Retain the returned preview unchanged. Present core's complete approval
   report only after validation passes. Core owns the single exact-artifact
   approval; do not require a magic keyword or add a second pillar approval.
   On contextual approval, call Task Hook's `approve-data-load-preview`, then
   `verify-approved-data-load-archive` for the exact candidate. Persist the
   returned `taskValidationEnvelope` unchanged; never construct one locally.
6. Submit only that retained artifact:

   ```text
   python3 core/data-loader/scripts/upload_and_initiate.py --approved-preflight-envelope <protected-local-directory/preflight.json> --task-validation-envelope <protected-local-directory/task-envelope.json> --confirm-upload --properties <core-environment.properties> --run-config <core-runbook.properties>
   ```

   For core's explicitly authorized same-request auto-approval policy, use
   `--approve-upload` instead of `--confirm-upload`. Never supply both flags.
   Keep the internal preflight and Task Hook records under core's retention
   policy and follow Task Hook's project-evidence registration requirements.

Core verifies retained bytes and environment/Run Book context before submission.
Do not rebuild or repeat source/reference checks after approval. A changed or
missing approved artifact or context requires fresh validation and approval;
changes to original workbook/export files alone do not replace an intact
approved artifact. Return core's complete Markdown report unchanged and stop
after accepted initiation. Later requested status and fresh-export reconciliation
use their declared core/shared workflows and the original request identity.
Never automatically resubmit a failed or uncertain mutation.
