#!/usr/bin/env python3
"""Run Activity Types through the shared Field Service task workflow."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile

SHARED = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SHARED))
from task_orchestration import REST_SERVICE, add_service_argument, PartialExecutionBlocked, WorkflowBlocked, run
from task_adapter import ActivityTypesAdapter

ROOT = Path(__file__).resolve().parents[6]
PROJECT_MGMT = ROOT / "core" / "project-mgmt" / "scripts"
sys.path.insert(0, str(PROJECT_MGMT))
from token_usage_logger import append_token_usage_log, utc_now

SKILL_ID = "cx.field-service.scheduling-and-dispatch.activity-types"
TASK_CODE = "ORA_FFS_TS_ACTIVITY_TYPES"


def _under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _transient_output(path: Path) -> bool:
    """Exact previews contain customer configuration and may only live in OS temp."""
    roots = {Path(tempfile.gettempdir()).resolve(), Path("/tmp").resolve(), Path("/private/tmp").resolve()}
    return any(_under(path, root) for root in roots)


def _project_workspace(project_id: str) -> Path:
    if not project_id or Path(project_id).name != project_id:
        raise WorkflowBlocked("project_id must be a single initialized project workspace name.")
    workspace = ROOT / "project" / project_id
    required = (workspace / "state" / "project-state.json", workspace / "artifacts" / "artifact-index.json")
    if not workspace.is_dir() or any(not item.is_file() for item in required):
        raise WorkflowBlocked(
            "project_id must reference an initialized project workspace with state/project-state.json "
            "and artifacts/artifact-index.json."
        )
    return workspace


def _environment(properties: Path) -> str:
    try:
        values = dict(
            line.split("=", 1)
            for line in properties.read_text(encoding="utf-8").splitlines()
            if "=" in line
        )
    except OSError:
        return "unavailable"
    return values.get("environment", "unavailable").strip() or "unavailable"


def _persist_redacted_evidence(project_id: str, result: dict[str, object], properties: Path) -> Path:
    workspace = _project_workspace(project_id)
    run_root = workspace / "state" / "runs"
    run_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    evidence = {
        "taskCode": TASK_CODE,
        "skillId": SKILL_ID,
        "status": result.get("status", "blocked"),
        "stage": result.get("stage", "completed"),
        "environment": _environment(properties),
        "executionDirection": result.get("executionDirection"),
        "sha256": result.get("sha256"),
        "requestCount": result.get("requestCount", len(result.get("verified", []))),
        "completedCount": result.get("completedCount", len(result.get("verified", []))),
        "checksRun": result.get(
            "checksRun",
            ["workbook_validation", "design_enforcement", "preflight", "preview", "approval", "put", "get_verification"],
        ),
        "artifactRefs": [],
        "redaction": "No credentials, tokens, request bodies, baselines, labels, response bodies, or customer values persisted.",
    }
    for key in ("failureClass", "recommendedAction", "message", "errors"):
        if key in result:
            evidence[key] = result[key]
    path = run_root / f"activity-types-{timestamp}.json"
    path.write_text(json.dumps(evidence, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return path


def _update_project_state(project_id: str, evidence: Path, status: str) -> None:
    """Record only the safe run reference in durable project state."""
    workspace = _project_workspace(project_id)
    path = workspace / "state" / "project-state.json"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise WorkflowBlocked("Project state could not be read for redacted run recording.") from error
    if not isinstance(state, dict):
        raise WorkflowBlocked("Project state is not a JSON object for redacted run recording.")
    state["latest_run_ref"] = str(evidence.relative_to(ROOT))
    active = state.get("active_skill_path")
    if isinstance(active, list) and SKILL_ID not in active:
        state["active_skill_path"] = [*active, SKILL_ID]
    state["updated_at"] = utc_now()
    state["status"] = "blocked" if status in {"blocked", "partial_failure"} else "in_progress"
    path.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _record_token_usage(project_id: str, evidence: Path, status: str) -> None:
    append_token_usage_log(
        project_id=project_id,
        skill_id=SKILL_ID,
        task=TASK_CODE,
        trigger="task runner",
        activity_start_time=utc_now(),
        artifact_paths=[evidence],
        files_read=1,
        notes=f"Redacted {status} workflow evidence only; no customer payload retained.",
        root=ROOT,
    )


def _blocked_result(error: Exception) -> dict[str, object]:
    message = str(error)
    if "checksum" in message:
        failure_class, action = "approval_blocker", "Create and approve a fresh immutable preview checksum."
    elif "cannot execute" in message:
        failure_class, action = "catalog_mismatch", "Select ora_rest_execution; Core Task REST does not support this task's PUT operation."
    elif message.startswith(("GET ", "PUT ", "POST ")):
        failure_class, action = "fusion_api", "Correct the environment or API issue, then create a fresh preview."
    elif "environment" in message.lower():
        failure_class, action = "transport_or_environment", "Select a valid FSCR environment profile and rerun preview."
    else:
        failure_class, action = "input_validation", "Correct the reported validation issue and rerun preview."
    return {
        "status": "blocked",
        "stage": "validation_or_preflight",
        "failureClass": failure_class,
        "message": "Activity Types workflow blocked before a write was attempted.",
        "recommendedAction": action,
        "errors": [{"stage": "validation_or_preflight", "entity_id": "workflow", "failure_class": failure_class, "recommended_action": action}],
    }


def _safe_result(result: dict[str, object], evidence: Path) -> dict[str, object]:
    """Return the exact preview only to the active caller; durable evidence stays redacted."""
    summary = {
        key: result[key]
        for key in ("status", "taskCode", "sha256", "requestCount", "executionDirection", "stage")
        if key in result
    }
    if isinstance(result.get("verified"), list):
        summary["verifiedCount"] = len(result["verified"])
    if isinstance(result.get("failures"), list):
        summary["failureCount"] = len(result["failures"])
    if result.get("status") == "approval_required" and isinstance(result.get("exactPreview"), dict):
        summary["exactPreview"] = result["exactPreview"]
    summary["service"] = REST_SERVICE
    summary["redactedEvidence"] = str(evidence)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_service_argument(parser)
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--execution-direction", choices=("ora_rest_execution", "core.data-loader.task-rest"))
    parser.add_argument("--mode", choices=("preview", "execute"), default="preview")
    parser.add_argument("--approve-checksum")
    parser.add_argument("--properties", type=Path, default=ROOT / "core/auth/fusionEnv.properties")
    parser.add_argument("--output", type=Path, required=True, help="Ephemeral exact preview under the OS temporary directory; never under project/.")
    args = parser.parse_args()
    try:
        _project_workspace(args.project_id)
        if not _transient_output(args.output):
            raise WorkflowBlocked("Immutable preview output must be under the OS temporary directory because it contains customer configuration.")
        result = run(
            ActivityTypesAdapter(), args.workbook, args.execution_direction, args.mode,
            args.approve_checksum, args.properties, args.output,
            include_exact_preview=args.mode == "preview",
        )
        result["service"] = REST_SERVICE
        result["executionDirection"] = args.execution_direction or "ora_rest_execution"
        result["stage"] = "preview" if result.get("status") == "approval_required" else "completed"
        evidence = _persist_redacted_evidence(args.project_id, result, args.properties)
        _update_project_state(args.project_id, evidence, str(result["status"]))
        _record_token_usage(args.project_id, evidence, str(result["status"]))
        print(json.dumps(_safe_result(result, evidence), sort_keys=True))
        return 0
    except PartialExecutionBlocked as error:
        try:
            evidence = _persist_redacted_evidence(args.project_id, {
                "status": "partial_failure", "stage": "put_or_verification", "failureClass": "partial_execution",
                "sha256": error.sha256, "completedCount": error.completed_count,
                "message": "A write or verification did not complete; remaining requests were not attempted.",
                "recommendedAction": "Read back the affected Activity Type and create a new approved continuation preview.",
                "errors": [{"stage": "put_or_verification", "entity_id": f"request-{error.completed_count + 1}", "failure_class": "partial_execution", "recommended_action": "Read back the affected Activity Type before continuation."}],
            }, args.properties)
            _update_project_state(args.project_id, evidence, "partial_failure")
            _record_token_usage(args.project_id, evidence, "partial_failure")
        except (OSError, ValueError, WorkflowBlocked):
            pass
        print(f"Activity Types workflow blocked: {error}", file=sys.stderr)
        return 2
    except (OSError, ValueError, WorkflowBlocked, RuntimeError) as error:
        try:
            evidence = _persist_redacted_evidence(args.project_id, _blocked_result(error), args.properties)
            _update_project_state(args.project_id, evidence, "blocked")
            _record_token_usage(args.project_id, evidence, "blocked")
        except (OSError, ValueError, WorkflowBlocked):
            pass
        print(f"Activity Types workflow blocked: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
