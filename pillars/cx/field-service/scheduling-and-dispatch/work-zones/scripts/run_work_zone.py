#!/usr/bin/env python3
"""Run Work Zones only through the shared Field Service task workflow."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


SHARED = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SHARED))
from task_orchestration import REST_SERVICE, add_service_argument, PartialExecutionBlocked, WorkflowBlocked, run
from task_adapter import WorkZonesAdapter


ROOT = Path(__file__).resolve().parents[6]


def _project_evidence(project_id: str, path: Path) -> Path:
    resolved = path.resolve()
    project_root = (ROOT / "project" / project_id).resolve()
    if not project_root.is_dir():
        raise WorkflowBlocked(f"Project workspace does not exist: project/{project_id}")
    if project_root not in resolved.parents:
        raise WorkflowBlocked("output must be a redacted evidence path under the selected project workspace.")
    return resolved


def _environment(properties: Path) -> str:
    try:
        values = dict(
            line.split("=", 1) for line in properties.read_text(encoding="utf-8").splitlines()
            if "=" in line
        )
    except OSError:
        return "unavailable"
    return values.get("environment", "unavailable").strip() or "unavailable"


def _persist_redacted_run(project_id: str, result: dict[str, object], properties: Path) -> Path:
    run_root = ROOT / "project" / project_id / "state" / "runs"
    run_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence = {
        "taskCode": "ORA_FFS_TS_WORK_ZONES",
        "skillId": "cx.field-service.scheduling-and-dispatch.work-zones",
        "status": result["status"],
        "stage": result.get("stage", "completed"),
        "environment": _environment(properties),
        "sha256": result.get("sha256"),
        "requestCount": result.get("requestCount", len(result.get("verified", []))),
        "checksRun": result.get("checksRun", ["workbook_validation", "design_enforcement", "environment_preflight", "rest_preflight", "preview", "approval", "put", "get_verification"]),
        "artifactRefs": [],
        "redaction": "No credentials, tokens, request bodies, baselines, labels, or payload values persisted.",
    }
    for key in ("failureClass", "completedCount", "safeSummary", "message", "recommendedAction", "errors"):
        if key in result:
            evidence[key] = result[key]
    path = run_root / f"work-zones-{timestamp}.json"
    path.write_text(json.dumps(evidence, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _append_token_usage(project_id: str, started_at: str, result: dict[str, object]) -> None:
    log = ROOT / "project" / project_id / "artifacts" / "shared" / "token-usage" / "current" / "token-usage-log.md"
    estimated_output = max(1, len(json.dumps(result, sort_keys=True)) // 4)
    row = (
        f"| {started_at} | cx.field-service.scheduling-and-dispatch.work-zones | Work Zones REST workflow | CLI | 2 | 3 | 0 | {estimated_output} | {estimated_output} | chars/4 estimate | "
        f"status={result.get('status', 'blocked')}; redacted evidence only. |\n"
    )
    with log.open("a", encoding="utf-8") as handle:
        handle.write(row)


def _failure_class(error: Exception) -> str:
    if isinstance(error, WorkflowBlocked):
        return error.failure_class
    if isinstance(error, OSError):
        return "artifact_persistence"
    return "input_validation"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_service_argument(parser)
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--execution-direction", choices=("ora_rest_execution",))
    parser.add_argument("--mode", choices=("preview", "execute"), default="preview")
    parser.add_argument("--approve-checksum")
    parser.add_argument("--include-exact-preview", action="store_true", help="Return the exact preview to the caller in preview mode; durable evidence remains redacted.")
    parser.add_argument("--properties", type=Path, default=ROOT / "core/auth/fusionEnv.properties")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    try:
        if arguments.include_exact_preview and arguments.mode != "preview":
            raise WorkflowBlocked("--include-exact-preview is available only in preview mode.")
        output = _project_evidence(arguments.project_id, arguments.output)
        result = run(WorkZonesAdapter(), arguments.workbook, arguments.execution_direction, arguments.mode, arguments.approve_checksum, arguments.properties, output, include_exact_preview=arguments.include_exact_preview)
        result["service"] = REST_SERVICE
        _persist_redacted_run(arguments.project_id, result, arguments.properties)
        _append_token_usage(arguments.project_id, started_at, result)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except PartialExecutionBlocked as error:
        if (ROOT / "project" / arguments.project_id).is_dir():
            result = {
                "status": "partial_failure", "stage": "put_or_verification", "failureClass": "partial_execution",
                "sha256": error.sha256, "completedCount": error.completed_count,
                "safeSummary": error.safe_summary or "verification_mismatch",
                "message": "A Work Zone write or verification did not complete; remaining requests were not attempted.",
                "recommendedAction": "Read back the affected Work Zone and create a new approved continuation preview.",
            }
            result["failureClass"] = error.failure_class
            _persist_redacted_run(arguments.project_id, result, arguments.properties)
            _append_token_usage(arguments.project_id, started_at, result)
        print(f"Work Zones workflow blocked: {error}", file=sys.stderr)
        return 2
    except (OSError, ValueError, WorkflowBlocked) as error:
        if (ROOT / "project" / arguments.project_id).is_dir():
            result = {
                "status": "blocked", "stage": "validation_or_preflight", "failureClass": _failure_class(error),
                "message": "Work Zones workflow blocked before a write was attempted.",
                "recommendedAction": "Correct the reported workbook, design, environment, or preflight issue, then create a fresh preview.",
            }
            _persist_redacted_run(arguments.project_id, result, arguments.properties)
            _append_token_usage(arguments.project_id, started_at, result)
        print(f"Work Zones workflow blocked: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
