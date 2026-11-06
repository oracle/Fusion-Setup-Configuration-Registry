#!/usr/bin/env python3
"""Dispatch one Data Loader task-level route for an already selected task."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Sequence

DATA_LOADER_ROOT = Path(__file__).resolve().parents[2]
FSCR_ROOT = DATA_LOADER_ROOT.parents[1]
VALIDATOR_SCRIPTS = FSCR_ROOT / "core" / "data-loader" / "task-validator" / "scripts"
if str(VALIDATOR_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(VALIDATOR_SCRIPTS))
RUNBOOK_SCRIPTS = FSCR_ROOT / "core" / "runbook" / "scripts"
if str(RUNBOOK_SCRIPTS) not in sys.path:
    sys.path.append(str(RUNBOOK_SCRIPTS))

from runbook_guard import (  # noqa: E402
    require_approved_runbook,
    require_runbook_binding,
    runbook_from_task_context,
)

from task_rule_execution import (  # noqa: E402
    TaskRuleContractError,
    approve_task_preview,
    approved_loader_payload,
    build_task_preview,
    resolve_task_rules_from_context,
)


class TaskHookError(ValueError):
    """A requested Task Hook route is invalid or unsafe."""


def _positive_int(value: str) -> int:
    try:
        result = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a positive integer") from error
    if result < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return result

def data_load(path: Path, task_name: str, sequence: int, override: bool) -> dict[str, Any]:
    runbook_from_task_context(path)
    plan = resolve_task_rules_from_context(
        repository_root=FSCR_ROOT,
        task_context_path=path,
        task_name=task_name,
        sequence=sequence,
        allow_readiness_override=override,
    )
    status = plan.get("taskValidationStatus")
    execute_rules = (
        "The caller must now read executionGuide and the returned ruleResources, "
        "then execute applicable nodes following registry prerequisites and transitions. "
        "Perform declared read-only Fusion GETs through "
        "core/fusion-api/rest-api-client/scripts/fusion_rest_client.py. "
        "For Data Loader endpoints dataLoaderBusinessObjects, dataLoaderDataSets, "
        "or dataSetErrors, include --header REST-Framework-Version=9 on every "
        "delegated client invocation, including their Describe, finder, child-resource, "
        "action, and pagination requests, for both latest and versioned resource URLs "
        "and every permitted retry. This header requirement does not authorize "
        "additional operations or retries. "
        "Record evidence in ordered ruleResults and call build-data-load-preview only "
        "after applicable rules pass or are explicitly waived. Obtain user approval "
        "before approve-data-load-preview and archive verification. "
        "This is the supported assisted execution route; absence of a standalone "
        "rule-evaluator command is not an execution-route blocker."
    )
    if status == "ready":
        next_action = "The rule plan is ready to execute; checks have not yet run. " + execute_rules
    elif status == "overridden":
        if not override:
            raise TaskHookError("Task validation is overridden without an explicit readiness waiver.")
        next_action = (
            "Retain the explicit waiver and original failure evidence in ruleResults. "
            + execute_rules
        )
    elif status == "skipped":
        reason = plan.get("taskValidationSkipReason") or "No skip reason was supplied."
        next_action = (
            f"Task validation was skipped: {reason} "
            "Record the unavailable task guidance as not_applicable and continue to "
            "build-data-load-preview. Upload still requires user approval."
        )
    else:
        raise TaskHookError(f"Unsupported task validation status: {status!r}. Stop before preview or upload.")
    return {
        "route": "data-load",
        "taskValidation": plan,
        "executionGuide": "core/data-loader/references/task-rule-registry-execution.md",
        "nextAction": next_action,
    }


def _read_json_object(stream: Any, description: str) -> dict[str, Any]:
    try:
        value = json.load(stream)
    except json.JSONDecodeError as error:
        raise TaskHookError(f"{description} is not valid JSON: {error.msg}.") from error
    if not isinstance(value, dict):
        raise TaskHookError(f"{description} must be a JSON object.")
    return value


def _preview_input(value: dict[str, Any]) -> tuple[Path, str, int, Any, Any, bool]:
    context_path = value.get("taskContextPath")
    task_name = value.get("taskName")
    sequence = value.get("sequence")
    final_data = value.get("finalData")
    if not isinstance(context_path, str) or not context_path.strip():
        raise TaskHookError("Data Loader preview requires taskContextPath.")
    if not isinstance(task_name, str) or not task_name.strip():
        raise TaskHookError("Data Loader preview requires taskName.")
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
        raise TaskHookError("Data Loader preview requires a positive integer sequence.")
    if not isinstance(final_data, dict):
        raise TaskHookError("Data Loader preview requires finalData as a JSON object.")
    archive_sha256 = final_data.get("archiveSha256")
    if not isinstance(archive_sha256, str) or len(archive_sha256) != 64 or any(
        character not in "0123456789abcdefABCDEF" for character in archive_sha256
    ):
        raise TaskHookError("Data Loader preview requires finalData.archiveSha256 as a SHA-256 hex value.")
    override = value.get("allowReadinessOverride", False)
    if not isinstance(override, bool):
        raise TaskHookError("allowReadinessOverride must be a JSON boolean when supplied.")
    return (
        Path(context_path),
        task_name,
        sequence,
        final_data,
        value.get("ruleResults"),
        override,
    )


def build_data_load_preview(value: dict[str, Any]) -> dict[str, Any]:
    """Build the Task Validator preview through the required Task Hook route."""
    context_path, task_name, sequence, final_data, rule_results, override = _preview_input(value)
    binding = runbook_from_task_context(context_path)
    plan = resolve_task_rules_from_context(
        repository_root=FSCR_ROOT,
        task_context_path=context_path,
        task_name=task_name,
        sequence=sequence,
        allow_readiness_override=override,
    )
    skill_path = plan.get("skillPath")
    if plan.get("taskValidationStatus") == "skipped":
        skip_reason = str(plan.get("taskValidationSkipReason", "Task Validation guidance is unavailable."))
        preview = {
            "schemaVersion": "3.0",
            "taskCode": plan["taskCode"],
            "taskName": plan["taskName"],
            "executionRoute": "data-loader",
            "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "ruleResults": [
                {
                    "source": "task-hook-routing",
                    "status": "not_applicable",
                    "issues": [{"severity": "warning", "message": skip_reason}],
                    "changes": [],
                }
            ],
            "finalData": final_data,
        }
    elif not isinstance(skill_path, str) or not skill_path.strip():
        raise TaskHookError("The selected task has no skill-backed validation route.")
    else:
        preview = build_task_preview(
            repository_root=FSCR_ROOT,
            skill_path=skill_path,
            task_name=plan["taskName"],
            final_data=final_data,
            rule_results=rule_results,
            allow_readiness_override=override,
            task_code=plan["taskCode"],
        )
    preview["runbookBinding"] = binding
    return {"route": "data-load", "taskValidation": plan, "preview": preview}


def approve_data_load_preview(value: dict[str, Any]) -> dict[str, Any]:
    """Record an explicit caller-authorized approval for a Task Hook preview."""
    preview = value.get("preview")
    binding = require_runbook_binding(preview.get("runbookBinding") if isinstance(preview, dict) else None)
    approval = approve_task_preview(preview)
    approval["runbookBinding"] = binding
    return {
        "route": "data-load",
        "preview": preview,
        "approval": approval,
    }


def verify_approved_data_load_archive(value: dict[str, Any], archive: Path) -> dict[str, Any]:
    """Return an uploader-compatible envelope only when it covers exact archive bytes."""
    preview = value.get("preview")
    approval = value.get("approval")
    payload = approved_loader_payload(preview, approval)
    require_approved_runbook(preview, approval)
    final_data = payload.get("finalData")
    expected = final_data.get("archiveSha256") if isinstance(final_data, dict) else None
    if not isinstance(expected, str) or not expected.strip():
        raise TaskHookError("Approved Data Loader payload must include finalData.archiveSha256.")
    digest = hashlib.sha256()
    try:
        with archive.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as error:
        raise TaskHookError(f"Prepared archive could not be read: {archive}") from error
    actual = digest.hexdigest()
    if expected.casefold() != actual.casefold():
        raise TaskHookError("Approved Data Loader payload does not match the prepared archive SHA-256.")
    return {
        "route": "data-load",
        "archiveSha256": actual,
        "taskValidationEnvelope": {"preview": preview, "approval": approval},
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command_name in (
        "data-load",
        "build-data-load-preview",
        "approve-data-load-preview",
        "verify-approved-data-load-archive",
    ):
        command = commands.add_parser(command_name, allow_abbrev=False)
        if command_name in {
            "build-data-load-preview",
            "approve-data-load-preview",
        }:
            command.add_argument("--input-stdin", required=True, action="store_true")
            continue
        if command_name == "verify-approved-data-load-archive":
            command.add_argument("--input-stdin", required=True, action="store_true")
            command.add_argument("--archive", required=True, type=Path)
            continue
        command.add_argument("--task-context", required=True, type=Path)
        command.add_argument("--task-name", required=True)
        command.add_argument("--sequence", required=True, type=_positive_int)
        if command_name == "data-load":
            command.add_argument("--allow-readiness-override", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "build-data-load-preview":
            result = build_data_load_preview(_read_json_object(sys.stdin, "Data Loader preview input"))
        elif args.command == "approve-data-load-preview":
            result = approve_data_load_preview(_read_json_object(sys.stdin, "Data Loader approval input"))
        elif args.command == "verify-approved-data-load-archive":
            result = verify_approved_data_load_archive(
                _read_json_object(sys.stdin, "Approved Data Loader input"), args.archive
            )
        elif args.command == "data-load":
            result = data_load(args.task_context, args.task_name, args.sequence, args.allow_readiness_override)
        else:
            raise TaskHookError(f"Unsupported Task Hook command: {args.command}.")
        json.dump(result, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0
    except (TaskHookError, TaskRuleContractError, OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
