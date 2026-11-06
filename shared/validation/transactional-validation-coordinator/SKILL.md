---
skill_id: "shared.validation.transactional-validation-coordinator"
name: "Transactional Validation Coordinator"
description: "Select one offering-owned transactional check or applicable Starter Validation Flow; coordinate its supported API or manual route, prerequisite evidence, approval, assertions and separate cleanup outcome for detailed and executive reports."
layer: "shared"
pillar: "Common"
type: "orchestration"
execution_mode: "assisted"
owner_team: "FSCR framework team"
version: "0.2.0"
inputs:
  - "project_context"
  - "user_request"
  - "offering_scope"
  - "pillar_check_definition"
  - "selected_test_inputs"
  - "prior_attempt_evidence"
outputs:
  - "selected_check"
  - "transactional_validation_result"
  - "next_actions"
  - "token_usage_record"
depends_on:
  - "shared.validation.implementation-summary-and-evidence"
uses_core:
  - "core.project-mgmt.project-state-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.validation.reporting"
token_usage_tracking:
  enabled: true
  granularity: "per_skill_run"
  artifact_type: "token_usage_record"
  default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
  estimation_method: "chars/4 estimate unless exact accounting is available"
  required_fields:
    - "activity_start_time"
    - "skill_id"
    - "task"
    - "trigger"
    - "artifacts_written"
    - "files_read"
    - "estimated_input_tokens"
    - "estimated_output_tokens"
    - "estimated_total_tokens"
    - "estimation_method"
    - "notes"
persists_project_state: true
state_updates:
  - "validation_results"
  - "reports"
  - "token_usage_records"
workspace_outputs:
  -
    artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/shared/validation/{run_id}/"
    versioning_policy: "append-only"
  -
    artifact_type: "report"
    default_location: "project/{project_id}/artifacts/shared/validation/{run_id}/"
    versioning_policy: "append-only"
  -
    artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "As declared by the selected pillar check"
side_effects:
  - "Writes sanitized local validation results, reports, run records, and token estimates."
required_privileges:
  - "Local project workspace access; delegated live checks require the selected workflow privileges."
---

# Transactional Validation Coordinator

## Purpose

Coordinate one explicitly selected pillar-owned transaction check through its supported route, preserving prerequisites, bounded execution, evidence, user decisions and separate cleanup.

**Reviewers:** framework architecture owner, affected pillar lead and QA. Framework owns common controls; the pillar owns the transaction, API, assertions and cleanup.

## Discovery and contract

Read [the common workflow](../references/validation-workflow.md) and [check contract](../references/pillar-check-contract.md). Search only the resolved offering's `implementation-validation/` content and explicitly referenced reviewed SVFs. Keep checks manually authored; do not generate setup-task catalog metadata. Markdown and SKILL.md contributions may be normalized into `schemas/implementation-validation-check.schema.json` for this invocation. Do not invent missing fields or automatically register arbitrary files.

This skill provides assisted orchestration. It has no generic HTTP execution facility, no bundled pillar check, and no Playwright/SVF adapter. Missing or incomplete declared execution paths remain blocked.

## Single-check workflow

1. Require an explicit transactional-validation request. Run Book completion may offer checks, never execute them. Bind project/environment and scope using the implementation router. Standalone requests do not require a prior implementation report; existing project Run Book mutation gates still apply.
2. Present exact check IDs/versions, applicable SVF source, narrow outcomes, side effects and why each is relevant. Resolve ambiguity with the user. Select one check; never run all candidates or automatically chain prerequisite tests.
3. If the user skips, record SKIPPED and reason without preflight or mutation. If the required supported route is absent, record BLOCKED and next action. A pillar-authored manual alternative can be separately offered and selected; no silent fallback.
4. Confirm prerequisites, existing reference records, release, environment, identity, privileges, minimum inputs and supported client/operation. An earlier blocked review cannot be bypassed for a prerequisite this check needs: require current evidence that the relevant issue is resolved, preserving the prior report. Reuse prerequisites; if another independent record must first be created, stop. Do not require unrelated tasks to be complete or claim their verification from this check.
5. Resolve the stable test key and prior attempt. Reconcile any unknown outcome before creation. Reuse is allowed only when the check permits it, and proves read-back rather than new creation. Do not use fresh timestamps to conceal duplicate attempts.
6. Inspect the actual request through the declared route's payload validator: at most one new primary transaction; mandatory child collections within declared bounds. Reject batch input, loops, parallel creates, chained checks and unattended repeats. If no enforceable payload bound exists, block automated execution.
7. Preview exact environment, operation, sanitized user-visible payload, inputs/lineage, record marker, assertions, limits, side effects and cleanup. Keep any sensitive execution inputs ephemeral. The owning route must bind approval to the exact plan; changed inputs/environment invalidate it. Obtain explicit approval immediately before mutation under repository policy. This skill's persisted result is not an approval token.
8. Execute once through the selected supported pillar/core workflow. Transactions do not use setup Data Loader. For guided manual execution, have the implementer follow the authored bounded procedure and supply outcome, performer and evidence; do not control the application unless a separate declared route authorizes it.
9. Read back or inspect the result using the selected route. Record each expected/observed assertion, evidence source and observation time, safe record/request IDs, actual creation count, owner and next action. Confirm the narrow business result and required references, not only acceptance or a terminal job status. Record count as null with INDETERMINATE if unknown; do not infer zero after timeout. HTTP success alone is insufficient. Attributed manual evidence may support PASS; an unsupported assertion or attestation alone must retain its weaker evidence classification.
10. Capture evidence before cleanup. Delete/cancel only through the pillar-declared supported route, for the exact identified test record, after the required immediate approval. An initial plan's cleanup recommendation alone is not deletion approval. Otherwise record explicit retention or pending manual cleanup with owner. Keep test and cleanup outcomes separate.
11. Produce one `transactional-validation` run envelope with exactly one check result. Include skipped/blocked outcomes too. Call the summary skill to publish it; report remaining effects and what was not tested. Later invocations use new run IDs. An executive index may list the separate historical reports and derive counts from them; it never dispatches tests, converts cleanup success into transaction success, or closes implementation-review gaps.

## Preflight, failures and recovery

Use [common failure handling](../references/validation-workflow.md#failure-handling). Never perform an external exploratory call to discover a missing route. No generic retries: an unknown or timed-out mutation stops, records INDETERMINATE, environment, operation, request identity, elapsed wait and next reconciliation action. Delegated routes must declare polling bounds; absent bounds block execution. After a confirmed failure retrieve safe diagnostics through that route where available. No automatic repeat-until-pass. Fresh approval is required for a new live attempt after reconciliation.

## Persistence

Keep credentials, cookies, tokens and customer payloads out of project artifacts. Store safe approval references only, not reusable credentials or executable approval envelopes. The report helper enforces result consistency but does not verify live privileges, payloads or approval; those remain execution-route responsibilities. Record durable runs/token usage under the selected project and preserve partial success.

A report-only request reads selected existing sanitized artifacts. It does not authorize live refresh, transaction execution, automatic post-load monitoring or persistence of core service session internals. Preserve skipped tests, user decisions, uncertain outcomes and cleanup failures in both detailed reports and any executive index.
