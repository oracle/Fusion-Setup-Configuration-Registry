---
skill_id: "shared.validation.implementation-summary-and-evidence"
name: "Implementation Summary and Evidence"
description: "Consolidate sanitized implementation-review or transactional-validation evidence into project HTML and JSON reports with decisions, gaps, manual results, cleanup and coverage limits. Generate a calculated executive index with historical stage outcomes. Does not run checks or infer success from task status."
layer: "shared"
pillar: "Common"
type: "assessment"
execution_mode: "assisted"
owner_team: "FSCR framework team"
version: "0.2.0"
inputs:
  - "project_context"
  - "validation_run_when_publishing_a_new_stage"
  - "prior_run_refs"
  - "explicit_summary_source_manifest_when_consolidating"
  - "approved_decisions"
outputs:
  - "html_report"
  - "structured_results"
  - "executive_index_html"
  - "executive_index_json"
  - "readiness_assessment"
  - "follow_up_actions"
  - "token_usage_record"
depends_on: []
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

# Implementation Summary and Evidence

## Purpose

Prepare and explain sanitized validation evidence for stage reports and a historical executive index while keeping readiness, business outcomes and cleanup distinct.

**Reviewers:** framework owner and QA; affected pillars review business assertions and explanations.

## Inputs and responsibility

Read [the common workflow](../references/validation-workflow.md). Consume sanitized run envelopes conforming to `schemas/implementation-validation-run.schema.json`. This skill assembles and explains evidence; `core.validation.reporting` validates consistency, derives conservative readiness, renders and publishes. No Fusion calls, check execution, or cleanup are performed by reporting.

## Request modes

- **New stage report:** receive a sanitized `validation_run`; follow the procedure below, then create the final executive index from selected existing reports and the newly published report.
- **Summary of existing reports:** no new `validation_run` is required. Go directly to **Historical project summary**, resolve existing report pairs and assemble the summary manifest. Skip per-stage collection/publication; do not fabricate a new check run, request re-execution or contact Fusion to create an index.

The manifest and run-envelope inputs are conditional on the selected mode; neither mode implicitly authorizes the other mode's live work.

## Procedure — new stage report

1. Confirm project, environment, requested stage and source requirement version. Consume prior approved project artifacts before requesting repeated context. Preserve exact run/source/check identities; do not mix environments or old/new requirement baselines silently.
2. Place the supplied Run Book task list immediately after the report title/project metadata, before scope and readiness, showing task ID, title, status and source completion time. Display missing completion timestamps as “Not recorded”; incomplete tasks as “Not completed”. Collect required mappings, task outcomes, assertions, manual attribution, decisions, recommendation authority, exceptions, limitations, open actions and diagnostics. Add incomplete coverage explicitly. A task marked complete does not manufacture a passing assertion.
3. For transaction reports include stable test key, created/reused ID, actual count, safe approval reference, side effects and cleanup outcome. Include pre-cleanup evidence and pending retention owner. Skipped/not-run checks cannot become passing results.
4. Review every text value and evidence reference for redaction before saving input. Raw customer records, credentials and sensitive screenshots are prohibited even if a directory is gitignored. Set `redaction_reviewed: true` only after review; this field is an attestation, not an automatic sanitizer.
5. Invoke `core.validation.reporting` with `--dry-run`. Resolve structural and consistency errors; never alter evidence merely to make readiness green. Nonzero business-readiness exit codes are valid reportable outcomes.
6. Publish to a new run ID using the core helper. Its project publication registers HTML/JSON, updates `latest_run_ref`, records a reporting skill run and logs a limited token estimate. It deliberately does not mark the project complete or change its active execution route. Record this assisted skill's own upstream activity/token estimate through project state/registry services as applicable; avoid counting renderer estimates twice.
7. Build the executive index for the final validation handoff using the procedure below. Return its link first, followed by the stage report/result links, readiness within each verified stage, unresolved owners and next actions. Readiness is advisory; a release/progression decision remains with the project owner. Any acceptance of gaps is a separate referenced decision, not a rewrite of findings.

## Historical project summary

For a project-level summary, use `core.validation.reporting` and its [executive summary contract](../../../core/validation/reporting/references/executive-summary-contract.md). For summary-only requests, use existing reports directly. For a new stage report, first publish it and include it alongside the relevant prior immutable prevalidation, implementation-review and transaction reports for the same project/environment and requirement baseline. Review source selection explicitly; include unresolved earlier findings. Show missing stages as **no supplied report**, never PASS or SKIPPED. A project summary is local indexing, not batch execution.

1. Assemble the documented summary manifest with a new summary ID, target identity, current timestamp, redaction review, project-relative JSON/HTML source paths and SHA-256 hashes of those sanitized report files. Do not hash or archive Data Loader payloads or session approval objects. Prevalidation input is its existing `readiness.json`; implementation/transaction inputs are the published `{run, assessment}` JSON wrappers.
2. Run `python3 core/validation/reporting/scripts/executive_summary.py --input /path/to/summary-manifest.json --dry-run`. Resolve changed/missing source files, wrong identities or mixed baselines before publication. Do not hand-edit stored assessment counts to get a green report.
3. Run the same command with `--publish` to create `project/{project_id}/artifacts/shared/validation/{summary_id}/index.html` and `index.json`. The common publisher registers both, records the reporting run and token estimate, and preserves earlier artifacts. Use a fresh summary ID after subsequent tests or corrections; never overwrite the previous index.
4. Return the new index link. Explain that its counts represent recorded results across selected reports, including repeated checks. A later successful transactional check does not close a previous implementation failure. Scope, observation time, source baseline and per-stage readiness remain visible. Current project readiness requires a separately requested reassessment against complete current evidence.

The index places the latest **supplied** task observation per task at the top, with source completion time, capture time and originating run; it does not pretend this is one complete live Run Book snapshot. It then shows executive numbers, missing stages, stage cards/links, findings with expected/observed evidence and owners/actions, and transaction/cleanup metrics. Transaction record counts are per-run observations, not unique records or a current retained-record inventory. Unknown creation counts are counted separately.

Do not concatenate several transactional check runs into one invocation envelope: each underlying transactional run still accepts one selected check. Repeated historical runs can be indexed without rerunning them. Overall project readiness in the summary JSON is `NOT_ASSESSED`; a zero exit code confirms successful indexing only.

Example human prompt: **“Summarize this project's validation results, including earlier gaps, in an executive report with counts and links to the stage reports.”** Resolve the project and existing report references from the durable workspace; ask only for genuinely ambiguous identity or scope, not permission to make the requested local report.

## Failure and recovery

Preflight schema, bidirectional traceability, environment, evidence timestamps, safe project paths and new run identity. Follow [common failure handling](../references/validation-workflow.md#failure-handling). Rendering/persistence failures must be disclosed separately from business failures. Preserve safe input for recovery; do not repeat any Fusion action to repair a report. No polling or automatic overwrite. A failed publication must be reconciled locally before using a new run ID.
