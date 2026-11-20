#!/usr/bin/env python3
"""Run Work Skills through the shared Field Service task workflow."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from time import time


SHARED = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SHARED))
from task_orchestration import REST_SERVICE, add_service_argument, WorkflowBlocked, run
from task_adapter import WorkSkillsAdapter, WorkSkillsInputError


ROOT = Path(__file__).resolve().parents[6]
PROJECT_MGMT = ROOT / "core" / "project-mgmt" / "scripts"
sys.path.insert(0, str(PROJECT_MGMT))
from token_usage_logger import append_token_usage_log, utc_now


def _is_under_project(path: Path) -> bool:
    try:
        path.resolve().relative_to((ROOT / "project").resolve())
    except ValueError:
        return False
    return True


def _project_workspace(project_id: str) -> Path:
    if not project_id or Path(project_id).name != project_id:
        raise WorkflowBlocked("project_id must be a single project workspace name.")
    workspace = ROOT / "project" / project_id
    required = (workspace / "state" / "project-state.json", workspace / "artifacts" / "artifact-index.json")
    if not workspace.is_dir() or any(not path.is_file() for path in required):
        raise WorkflowBlocked(
            "project_id must reference an initialized project workspace with state/project-state.json "
            "and artifacts/artifact-index.json."
        )
    return workspace


def _project_evidence(
    project_id: str,
    result: dict[str, object] | None = None,
    *,
    failure_class: str | None = None,
) -> Path:
    folder = _project_workspace(project_id) / "state" / "runs"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"run-{int(time())}-work-skills.json"
    evidence = {
        "taskCode": WorkSkillsAdapter.task_code,
        "status": result.get("status") if result else "blocked",
        "failureClass": failure_class,
        "sha256": result.get("sha256") if result else None,
        "requestCount": result.get("requestCount", len(result.get("verified", []))) if result else 0,
        "verifiedCount": len(result.get("verified", [])) if result else 0,
        "redacted": True,
    }
    path.write_text(json.dumps(evidence, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return path


def _record_run(project_id: str, evidence: Path, status: str) -> None:
    append_token_usage_log(
        project_id=project_id,
        skill_id="cx.field-service.scheduling-and-dispatch.work-skills",
        task=WorkSkillsAdapter.task_code,
        trigger="task runner",
        activity_start_time=utc_now(),
        artifact_paths=[evidence],
        files_read=1,
        notes=f"Redacted {status} workflow evidence only; no customer payload retained.",
        root=ROOT,
    )


def _implementation_result(
    result: dict[str, object], preview_source: Path | dict[str, object], evidence: Path
) -> dict[str, object]:
    """Return a human-readable summary without echoing request bodies or baselines."""
    if isinstance(preview_source, dict):
        preview = preview_source
    else:
        try:
            preview = json.loads(preview_source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise WorkflowBlocked("The generated immutable preview could not be read for the implementation summary.") from error
    requests = preview.get("requests") if isinstance(preview, dict) else None
    if not isinstance(requests, list):
        raise WorkflowBlocked("The generated immutable preview has no request list for the implementation summary.")
    resource_counts = {"workSkills": 0, "workSkillGroups": 0}
    items = []
    configuration_details = []
    verified_by_sequence = {
        item.get("sequence"): item
        for item in result.get("verified", [])
        if isinstance(item, dict) and isinstance(item.get("sequence"), int)
    }
    for sequence, request in enumerate(requests, 1):
        if not isinstance(request, dict):
            continue
        is_group = request.get("operationId") == "put-work-skill-group"
        resource_type = "Work Skill Group" if is_group else "Work Skill"
        resource_counts["workSkillGroups" if is_group else "workSkills"] += 1
        item = {
            "sequence": sequence,
            "resourceType": resource_type,
            "label": request.get("label"),
            "path": request.get("path"),
        }
        if result.get("status") == "completed":
            item["status"] = "verified" if verified_by_sequence.get(sequence, {}).get("verified") else "not_verified"
        else:
            item["status"] = "pending_approval"
        items.append(item)
        body = request.get("body") if isinstance(request.get("body"), dict) else {}
        configuration_details.append(
            {
                "configuration": (
                    f"{request.get('label')} (Work Skill Group)"
                    if is_group
                    else request.get("label")
                ),
                "active": body.get("active"),
                "status": item["status"],
            }
        )
    status = result.get("status")
    summary: dict[str, object] = {
        "task": "Work Skills",
        "taskCode": WorkSkillsAdapter.task_code,
        "status": status,
        "environment": preview.get("environment"),
        "executionDirection": preview.get("executionDirection"),
        "configurationSummary": {**resource_counts, "total": len(items)},
        "configurationDetails": configuration_details,
        "checksum": result.get("sha256"),
        "redactedEvidence": str(evidence),
    }
    if status == "approval_required":
        summary["items"] = items
        summary["message"] = "Preview is ready. No changes have been sent. Approve the displayed checksum to execute the ordered requests."
        summary["nextActions"] = [
            "Review the target environment and ordered items.",
            "Approve the exact checksum immediately before execution.",
        ]
    elif status == "completed":
        summary["message"] = "All requested Work Skills and Work Skill Groups were updated and GET-verified."
        summary["nextActions"] = [
            "Confirm routing eligibility with the complete required-skill set.",
            "Confirm group capacity and resource-assignment behavior in the target environment.",
        ]
    summary["service"] = REST_SERVICE
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_service_argument(parser)
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--execution-direction", choices=("ora_rest_execution", "core.data-loader.task-rest"))
    parser.add_argument("--mode", choices=("preview", "execute"), default="preview")
    parser.add_argument("--approve-checksum")
    parser.add_argument("--include-exact-preview", action="store_true", help="Return the exact preview to the caller in preview mode; durable evidence remains redacted.")
    parser.add_argument("--properties", type=Path, default=ROOT / "core/auth/fusionEnv.properties")
    parser.add_argument("--output", type=Path, required=True, help="Ephemeral immutable preview output; do not place it under project/.")
    args = parser.parse_args()
    try:
        if args.include_exact_preview and args.mode != "preview":
            raise WorkflowBlocked("--include-exact-preview is available only in preview mode.")
        _project_workspace(args.project_id)
        if _is_under_project(args.output):
            raise WorkflowBlocked("Immutable preview output must not be stored under project/ because it contains request bodies.")
        result = run(
            WorkSkillsAdapter(),
            args.workbook,
            args.execution_direction,
            args.mode,
            args.approve_checksum,
            args.properties,
            args.output,
            include_exact_preview=True,
        )
        result["service"] = REST_SERVICE
        preview = result.pop("exactPreview", None)
        if result.get("status") == "approval_required" and not isinstance(preview, dict):
            raise WorkflowBlocked("The task runner did not retain the transient immutable preview for its summary.")
        evidence = _project_evidence(args.project_id, result)
        _record_run(args.project_id, evidence, "completed")
        if isinstance(preview, dict):
            summary = _implementation_result(result, preview, evidence)
            if args.include_exact_preview:
                summary["exactPreview"] = preview
        else:
            summary = {**result, "service": REST_SERVICE, "redactedEvidence": str(evidence)}
        print(json.dumps(summary, sort_keys=True))
        return 0
    except Exception as error:
        failure_class = (
            "input_validation"
            if isinstance(error, (ValueError, WorkSkillsInputError))
            else "approval_or_workflow_blocker"
            if isinstance(error, WorkflowBlocked)
            else "unexpected_runner_error"
        )
        try:
            evidence = _project_evidence(args.project_id, failure_class=failure_class)
            _record_run(args.project_id, evidence, "blocked")
        except (OSError, ValueError, WorkflowBlocked):
            pass
        print(f"Work Skills workflow blocked: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
