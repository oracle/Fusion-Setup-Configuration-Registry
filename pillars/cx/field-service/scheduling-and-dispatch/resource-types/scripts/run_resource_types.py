#!/usr/bin/env python3
"""Only entry point for Resource Types task execution."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

SHARED = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SHARED))
from task_orchestration import REST_SERVICE, add_service_argument, PartialExecutionBlocked, WorkflowBlocked, run
from task_adapter import ResourceTypesAdapter

ROOT = Path(__file__).resolve().parents[6]


def _under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _environment(properties: Path) -> str:
    try:
        values = dict(
            line.split("=", 1) for line in properties.read_text(encoding="utf-8").splitlines()
            if "=" in line
        )
    except OSError:
        return "unavailable"
    return values.get("environment", "unavailable").strip() or "unavailable"


def _persist_redacted_evidence(project_id: str, result: dict[str, object], properties: Path) -> Path:
    project_root = ROOT / "project" / project_id
    if not project_root.is_dir():
        raise WorkflowBlocked(f"Project workspace does not exist: project/{project_id}")
    run_root = project_root / "state" / "runs"
    run_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence = {
        "taskCode": "ORA_FFS_TS_RESOURCE_TYPES",
        "skillId": "cx.field-service.scheduling-and-dispatch.resource-types",
        "status": result["status"],
        "stage": result.get("stage", "completed"),
        "environment": _environment(properties),
        "sha256": result.get("sha256"),
        "requestCount": result.get("requestCount", len(result.get("verified", []))),
        "checksRun": result.get("checksRun", ["workbook_validation", "design_enforcement", "preflight", "preview", "approval", "put", "get_verification"]),
        "artifactRefs": [],
        "redaction": "No credentials, tokens, request bodies, baselines, labels, or payload values persisted.",
    }
    if "failureClass" in result:
        evidence["failureClass"] = result["failureClass"]
    if "completedCount" in result:
        evidence["completedCount"] = result["completedCount"]
    if "message" in result:
        evidence["message"] = result["message"]
    if "recommendedAction" in result:
        evidence["recommendedAction"] = result["recommendedAction"]
    if "safeFailureSummary" in result:
        evidence["safeFailureSummary"] = result["safeFailureSummary"]
    if "errors" in result:
        evidence["errors"] = result["errors"]
    path = run_root / f"resource-types-{timestamp}.json"
    path.write_text(json.dumps(evidence, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _partial_failure_summary(error: PartialExecutionBlocked) -> str:
    """Persist only the shared workflow's safe diagnostic summary."""
    if isinstance(error.safe_summary, str) and error.safe_summary:
        return error.safe_summary
    status = re.search(r"\bHTTP\s+(\d{3})\b", str(error))
    return f"HTTP {status.group(1)}" if status else "Fusion REST client error"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_service_argument(parser)
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--execution-direction", choices=("core.data-loader.task-rest", "ora_rest_execution"))
    parser.add_argument("--mode", choices=("preview", "execute"), default="preview")
    parser.add_argument("--approve-checksum")
    parser.add_argument("--include-exact-preview", action="store_true", help="Return the exact preview to the caller in preview mode; durable evidence remains redacted.")
    parser.add_argument("--properties", type=Path, default=ROOT / "core/auth/fusionEnv.properties")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--rationale-file", type=Path, help="Optional task-local rationale JSON; never store it in project evidence.")
    parser.add_argument("--english-names-file", type=Path, help="Required for future workbook mapping; never store it in project evidence.")
    parser.add_argument("--test-payload-file", type=Path, help="Restricted synthetic fscr_test_ fixture using the documented OFSC body; never use customer data.")
    parser.add_argument("--output", type=Path, required=True, help="Immutable preview output; do not place customer data in project evidence.")
    args = parser.parse_args()
    try:
        if args.include_exact_preview and args.mode != "preview":
            raise WorkflowBlocked("--include-exact-preview is available only in preview mode.")
        if not (ROOT / "project" / args.project_id).is_dir():
            raise WorkflowBlocked(f"Project workspace does not exist: project/{args.project_id}")
        if _under(args.output, ROOT / "project" / args.project_id):
            raise WorkflowBlocked("Immutable preview output must not be persisted inside project evidence.")
        adapter = ResourceTypesAdapter(args.rationale_file, args.english_names_file, args.test_payload_file)
        adapter.validate_design_rules(args.workbook)
        result = run(adapter, args.workbook, args.execution_direction, args.mode, args.approve_checksum, args.properties, args.output, include_exact_preview=args.include_exact_preview)
        result["service"] = REST_SERVICE
        _persist_redacted_evidence(args.project_id, result, args.properties)
        print(json.dumps(result, sort_keys=True))
        return 0
    except PartialExecutionBlocked as error:
        if (ROOT / "project" / args.project_id).is_dir():
            safe_summary = _partial_failure_summary(error)
            _persist_redacted_evidence(args.project_id, {
                "status": "partial_failure", "stage": "put_or_verification", "failureClass": "partial_execution",
                "sha256": error.sha256, "completedCount": error.completed_count,
                "message": "A Resource Type write or verification did not complete; remaining requests were not attempted.",
                "recommendedAction": "Read back the affected Resource Type and create a new approved continuation preview.",
                "safeFailureSummary": safe_summary,
                "errors": [{"stage": "put_or_verification", "entity_id": f"request-{error.completed_count + 1}", "message": safe_summary, "failure_class": error.failure_class, "recommended_action": "Read back the affected Resource Type before continuation."}],
            }, args.properties)
        print(f"Resource Types workflow blocked: {error}", file=sys.stderr)
        return 2
    except (OSError, ValueError, WorkflowBlocked) as error:
        if (ROOT / "project" / args.project_id).is_dir():
            failure_class = "fusion_api" if str(error).startswith(("GET ", "PUT ")) else "input_validation"
            _persist_redacted_evidence(args.project_id, {
                "status": "blocked", "stage": "validation_or_preflight", "failureClass": failure_class,
                "message": "Resource Types workflow blocked before a write was attempted.",
                "recommendedAction": "Correct the workbook or preflight issue, then create a fresh preview.",
                "errors": [{"stage": "validation_or_preflight", "entity_id": "workflow", "message": "Workflow blocked before a write was attempted.", "failure_class": "input_validation", "recommended_action": "Correct the reported issue and rerun preview."}],
            }, args.properties)
        print(f"Resource Types workflow blocked: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
