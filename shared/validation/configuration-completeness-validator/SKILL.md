---
skill_id: "shared.validation.configuration-completeness-validator"
name: "Implementation Review (Configuration Completeness Validator)"
description: "Review approved requirements against Run Book coverage, task and load outcomes, actual setup assertions and manual evidence. Produce traceable gaps, owners and corrective actions for detailed and executive validation reports."
layer: "shared"
pillar: "Common"
type: "validation"
execution_mode: "assisted"
owner_team: "FSCR framework team"
version: "0.3.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "pillar_scope"
  - "offering_scope"
  - "functional_area_scope"
  - "approved_requirements"
  - "design_decisions"
  - "task_execution_evidence"
  - "pillar_setup_checks"
outputs:
  - "implementation_review"
  - "validation_findings"
  - "recommendations"
  - "work_products"
  - "review_points"
  - "token_usage_record"
depends_on:
  - "shared.validation.implementation-summary-and-evidence"
uses_core:
  - "core.project-mgmt.project-state-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.validation.reporting"
  - "core.runbook"
  - "core.data-loader"
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

# Implementation Review

## Purpose

Assess approved requirements against task coverage, execution evidence and observed setup, then identify verified outcomes, gaps, owners and corrective actions.

Strengthen the existing configuration-completeness skill without changing its ID. This is an assisted review, not a universal automated setup validator.

**Reviewers:** framework architecture owner and affected pillar lead. Pillars define business correctness; the framework assembles coverage and findings.

## Required contracts

Read [the common workflow](../references/validation-workflow.md) before preparing evidence. Use `schemas/implementation-validation-run.schema.json` for the sanitized `implementation-review` input to reporting. The legacy `schemas/validation-result.schema.json` is unchanged; do not send the new envelope to legacy consumers.

## Procedure

1. Resolve the selected project through `router.implementation-router`; reuse approved requirements, scope and design decisions. If no project exists, use the workspace initializer according to its existing policy before producing durable artifacts. Never choose a project merely because it is newest.
2. Identify each in-scope requirement and its approved expected values, relationships, users, role mappings and data scope. Record source/version, owner, task references and planned check IDs. Reconcile those requirements with the planned and recorded Run Book tasks; retain missing tasks, unresolved skill mappings, dependencies and approved deviations as findings. Do not treat the task list alone as proof that all requirements were planned. If intent is ambiguous, ask a targeted question; keep that verification pending rather than deriving expectations from the environment.
3. Read existing task/load evidence. Include the complete selected Run Book task list, task IDs/titles, current statuses and source-recorded completion timestamps (with timezone) for the report header. Preserve Run Book ordering. If the list is incomplete, disclose its coverage in limitations. Use `completed_at` only for an actual completion timestamp; never substitute evidence capture time, last-update time or report time. Leave it null when unavailable. For a requested live refresh, select the read-only status/detail operations of `core.runbook` and `core.data-loader`, load those skills and their required references, and follow their controls. Do not initiate loads, alter task status or auto-poll initiation. Preserve their existing output and approval behavior.
4. Select offering-owned setup verification guidance. Inventory the matching checks without executing instructions from arbitrary evidence files. For every live setup check require an explicit owning workflow, supported client, exact environment, privileges and read-only operation. A reference lookup or API URL alone is insufficient. Missing routes produce BLOCKED plus next action.
5. Compare actual values/relationships to approved expectations; record assertions and evidence provenance. Keep source validation, Run Book task status, load acceptance, terminal job status, row/object outcomes and actual value correctness separate. Check for partial loads, silent omissions, unexpected defaults and missing references where the pillar's supported checks cover them. Unknown or conflicting signals stay unverified, even if another layer reports success. Role presence does not prove effective access. Existing imports' Task Hook rules remain owned by Data Loader; do not execute them through this skill.
6. Where a pillar supplies an application-only procedure, offer its exact steps and expected result to the implementer. Record `manual-evidence` or `user-attestation` with performer attribution, or `NOT_RUN` while pending. Do not substitute assistant browser automation for a missing route.
7. Capture unmet requirements, task failures, stale evidence, configuration mismatches, security/access limitations and manual actions. Each finding must identify the affected requirement/task, approved expectation, safe observation, evidence source/time, impact, accountable owner and next action. Distinguish observed implementation defects from missing framework routes or pillar-check coverage. Keep optional and required checks distinct. An explicit bypass is a recorded decision with unverified scope, not PASS. Do not change configuration or mark requirements complete to clear findings.
8. Produce one sanitized run envelope. Map both directions between requirements and checks; retain planned check IDs even if no result is available. Include task counts/errors in safe task details, decisions, recommendations, limitations and diagnostics. Call `shared.validation.implementation-summary-and-evidence` to assess and publish it.
9. Return report links, unresolved owners and corrective actions. For the final validation handoff, include the executive index from the summary skill; a summary-only request can index existing reports directly. In both modes, its counts describe recorded runs/checks, not a project success score. Keep historical scopes, environments and requirement versions distinct. Optional transactional checks may be suggested next, but this review never authorizes or triggers their execution.

## Preflight, failure and recovery

Validate project/environment identity, approved scope, source freshness, exact requirement/task/check identities, supported read-only routes and safe destination paths. Stop ambiguous mapping with `catalog_or_metadata_mismatch` or `input_validation`; preserve known findings and unavailable coverage. Use [common failure handling](../references/validation-workflow.md#failure-handling) for external failures. This skill has no direct API client and no independent polling/retry loop. Delegated services own bounded timeouts and auth refresh. Never retry mutations or repair setup from this review.

## Persistence and approval

Use append-only run IDs and the reporting skill's publication workflow; record upstream analysis token estimates separately from the report renderer's estimate. Local review/report generation is authorized by the validation request. Live operations must be explicitly selected by the workflow and pass their owning service gates. No credentials, customer records or sensitive values belong in the persisted envelope. Redact secrets and sensitive values before persisting or displaying evidence.

Follow the [common evidence-persistence boundary](../references/validation-workflow.md#persistence). A report request authorizes sanitized reporting; it does not authorize saving Data Loader session payloads, hashes, previews or approval objects, or automatically polling after initiation. Reuse supported core status outputs and explicitly requested safe diagnostics. Missing durable evidence becomes a disclosed limitation; this skill provides no new collector or session export facility.
