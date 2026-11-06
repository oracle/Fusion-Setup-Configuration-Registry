---
skill_id: "core.validation.reporting"
name: "Validation Reporting"
description: "Validate sanitized implementation-validation evidence and generate HTML/JSON with conservative readiness. Publish new runs into an existing project with artifact registration and token estimates. Build a calculated executive index from explicit prior report sources; entirely local and does not execute tests."
layer: "core"
pillar: "Core"
type: "validation"
execution_mode: "assisted"
owner_team: "FSCR framework team"
version: "0.2.0"
inputs:
  - "sanitized_validation_run_when_publishing_a_stage"
  - "existing_project_workspace"
  - "explicit_summary_source_manifest_when_consolidating"
outputs:
  - "html_report"
  - "structured_results"
  - "executive_index_html_and_json_when_consolidating"
  - "skill_run"
  - "artifact_records"
  - "token_usage_record"
depends_on: []
uses_core:
  - "core.project-mgmt.project-state-manager"
  - "core.project-mgmt.artifact-registry-manager"
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

# Validation Reporting

## Purpose

Generate local stage reports and an executive index from sanitized evidence, preserving scope, provenance and unresolved findings without executing validation checks.

**Reviewers:** framework architecture owner and QA. This helper performs local report generation only; it does not certify the truth of evidence, inspect customer payloads, enforce a live approval, or contact Fusion.

## Prerequisites

Use Python 3.10+; runtime dependencies are standard-library only. The helper validates the supported contract subset and rejects unknown schema keywords. Read [report contract](references/report-contract.md) for fields, readiness and exit codes. Input must satisfy `schemas/implementation-validation-run.schema.json`; the old validation-result schema remains supported by its existing consumers and is not modified.

## Request modes

Use `validation_report.py` for a sanitized new stage run. Use `executive_summary.py` for an index of existing reports; this mode requires a source manifest, not a new run envelope. The input fields above are conditional. A summary-only request goes directly to the [executive summary contract](references/executive-summary-contract.md) and does not recollect evidence or publish an invented stage run.

## Workflow — new stage report

1. Receive a sanitized, redaction-reviewed run from a shared validation skill. Preserve evidence/source identities and recorded business outcomes.
2. Run local validation without writes:

   ```bash
   python3 core/validation/reporting/scripts/validation_report.py --input /path/to/sanitized-run.json --dry-run
   ```

3. Explain derived gaps, blockers and readiness. The script rejects inconsistent PASS records, mixed environments, broken traceability and multi-check transactional invocations. It cannot determine whether a claimed supported API actually exists or whether an approval was obtained; the execution workflow owns those checks.
4. On an authorized report request, publish a new run:

   ```bash
   python3 core/validation/reporting/scripts/validation_report.py --input /path/to/sanitized-run.json --publish
   ```

   The `project_id` must identify an existing initialized repository project. Publication writes append-only HTML/JSON under `artifacts/shared/validation/<run_id>`, registers draft artifacts, records a reporting skill run, updates the project's latest-run reference and appends the standard token log. It never creates a Fusion project/Run Book. If no workspace exists, route to the workspace initializer rather than inventing one in this helper.
5. For a project summary or final handoff, follow [executive summary contract](references/executive-summary-contract.md) and publish a fresh `index.html` / `index.json` from explicitly selected source report pairs. Include the new stage report and the relevant earlier reports; do not silently omit an earlier failure or assume absent stages passed. No project-wide readiness score is calculated.
6. Return the paths, readiness and estimated tokens. A completed reporting run does not mean the business checks passed. Do not discard reports because their exit code indicates a failure or incomplete verification.

## Preflight and approvals

Input schema/semantic validation precedes writes. Require exact project identity, canonical artifact index, safe non-symlink output paths and unused run ID. A validation/report request authorizes new local artifacts and metadata registration; existing run outputs are never overwritten. No live-operation approvals are performed here.

## Error handling and recovery

- `input_validation`: invalid/mixed/missing data; fail before publication and identify the field without echoing its value.
- `artifact_persistence`: unsafe path, existing run, lock contention or write failure; stop. Handled write errors restore prior metadata and remove the new report folder. Reconcile after a process crash before retrying; do not automatically remove a lock whose owner may still be active.
- Business/route diagnostics in `errors` are preserved, not retried. There is no network or polling timeout.
- Use one project writer at a time. The report lock serializes this helper only; other project writers must be idle during publication. No cross-service transaction guarantee is claimed.
- Never retry Fusion actions to recover a local publication. No automatic overwrite or cleanup of historical evidence.
- Input must already be sanitized. All report text is HTML-escaped, evidence references display as text, and no input scripts/remote content execute. HTML escaping does not redact confidential data.

The helper's chars/4 estimate covers sanitized input and report bodies only. It excludes upstream reasoning, external calls, credentials and metadata serialization; owning skills must log their own activity estimates.

## Presentation contract

Per-run HTML starts with Run Book task ID, title, recorded status and source completion time, followed by calculated scope/status cards, readiness, gaps/blockers, owners and next actions, requirement mappings, expected/observed assertions, evidence provenance and limitations. An absent completion timestamp is **Not recorded**, never the capture timestamp. Planned prevalidation tasks are not execution outcomes. Transactions show the new primary-record count, reuse and cleanup disposition separately; unknown counts remain unknown. Evidence references remain escaped text, not arbitrary executable links.

Executive summaries link only validated local stage-report paths and count all selected historical check results with their denominator and stage. They do not close old findings, prove that all Run Book tasks were supplied, or certify stored values. The caller owns source selection, redaction and environment identity. Preserve allowed core status observations only; never persist Data Loader session payloads, previews, hashes, approval objects or encoded artifacts as report evidence. Source SHA-256 values in the summary identify sanitized report files only.
