#!/usr/bin/env python3
"""Project Plan Types local ZIP gate; never uploads or mutates Fusion.

The task workflow must use build -> approve -> verify before handing the exact
archive and envelope to the shared loader. Shared loader code is unchanged;
calling it directly does not enforce this task-local gate.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
from typing import Any
import zipfile

TASK_DIRECTORY = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = TASK_DIRECTORY.parents[4]
TASK_CODE = "PJO_MANAGE_PROJECT_PLAN_TYPES"
TASK_NAME = "Manage Project Plan Types"
HOOK_SCRIPTS = REPOSITORY_ROOT / "core/data-loader/task-hook/scripts"
if str(HOOK_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(HOOK_SCRIPTS))
from task_hook import (  # noqa: E402
    approve_data_load_preview, build_data_load_preview,
    verify_approved_data_load_archive,
)

_spec = importlib.util.spec_from_file_location("_project_plan_type_import_contract", TASK_DIRECTORY / "scripts/validate_import.py")
assert _spec and _spec.loader
_contract = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _contract
_spec.loader.exec_module(_contract)


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def _validate(content: bytes, operation: str) -> dict[str, Any]:
    if operation not in {"create", "update"}:
        raise ValueError("UNRESOLVED_INPUT: operation must be create or update; separate mixed-operation packages.")
    result = _contract.validate_archive(content, operation=operation)
    if any(result[key]["status"] != "passed" for key in ("packageIntegrity", "taskContractValidation")):
        raise ValueError("Task archive validation blocked: " + json.dumps(result, sort_keys=True, ensure_ascii=False))
    return result


def _with_reference_warnings(value: dict[str, Any], content: bytes) -> dict[str, Any]:
    """Keep unsupported target checks visible even when a narrative omits them."""
    value = copy.deepcopy(value)
    results = value.get('ruleResults', [])
    reference = next((r for r in results if r.get('source', '').endswith('ora_reference_lookups.md')), None)
    if reference is None:
        return value  # The canonical rule engine reports missing rule resources.
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        if _contract.CHILD not in archive.namelist():
            return value  # Parent-only updates do not introduce option rows.
        rows = csv.DictReader(io.StringIO(archive.read(_contract.CHILD).decode('utf-8-sig')))
        for row in rows:
            for field, label in (('Name', 'Period Profile'), ('Name2', 'Budget Generation Financial Plan Type'),
                                 ('Name3', 'Forecast Financial Plan Type')):
                if not row.get(field):
                    continue
                path = _contract.CHILD+'.'+field
                issues = reference.setdefault('issues', [])
                if not any(i.get('code') == 'REFERENCE_UNRESOLVED' and i.get('path') == path
                           and i.get('value') == row[field] for i in issues):
                    issues.append({'code': 'REFERENCE_UNRESOLVED', 'severity': 'warning',
                        'blocking': False, 'path': path, 'value': row[field],
                        'message': label+' '+row[field]+': ZIP validation does not establish target membership or eligibility. Carry current target evidence separately; otherwise this value remains unverified.'})
    return value


def build_preview(archive: Path, operation: str, rule_results: list[dict[str, Any]], *, task_context: Path, sequence: int) -> dict[str, Any]:
    """Validate actual bytes before asking the shared engine to build a preview."""
    content = archive.read_bytes()
    final_data = {"archivePath": str(archive.resolve()), "archiveSha256": hashlib.sha256(content).hexdigest(), "operation": operation}
    return build_from_input({
        "taskContextPath": str(task_context), "taskName": TASK_NAME,
        "sequence": sequence, "finalData": final_data, "ruleResults": rule_results,
    })


def _route(value: dict[str, Any]) -> dict[str, Any]:
    if value.get("taskName") != TASK_NAME or value.get("allowReadinessOverride"):
        raise ValueError("Project Plan Types requires its exact task name and ready Task Hook route.")
    routed = build_data_load_preview(value)
    plan = routed["taskValidation"]
    expected = (TASK_DIRECTORY / "SKILL.md").resolve()
    skill_path = plan.get("skillPath")
    if plan.get("taskCode") != TASK_CODE or not isinstance(skill_path, str) or (REPOSITORY_ROOT / skill_path).resolve() != expected:
        raise ValueError("Task Hook must select the Project Plan Types skill and exact task code.")
    return routed["preview"]


def build_from_input(value: dict[str, Any]) -> dict[str, Any]:
    """Accept the existing Task Hook input and preserve target context verbatim."""
    if not isinstance(value, dict) or not isinstance(value.get("finalData"), dict):
        raise ValueError("Build requires Task Hook input with finalData.")
    final_data = value["finalData"]
    path = final_data.get("archivePath")
    if not isinstance(path, str) or not path:
        raise ValueError("finalData.archivePath is required.")
    content = Path(path).read_bytes()
    if final_data.get("archiveSha256") != hashlib.sha256(content).hexdigest():
        raise ValueError("Prepared archive bytes do not match finalData.archiveSha256.")
    result = _validate(content, final_data.get("operation"))
    _contract.validate_source_intent(content, final_data.get('sourceInput'))
    return {
        "preview": _route(_with_reference_warnings(value, content)),
        "archiveValidation": result,
        "taskRoutingContext": {"taskContextPath": value["taskContextPath"], "sequence": value["sequence"]},
    }


def _preview_fields(record: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    """Check retained task identity and shape without reading or replanning."""
    if not isinstance(record, dict):
        raise ValueError("Task preview record must be an object; rebuild legacy previews.")
    preview = record.get("preview")
    if not isinstance(preview, dict) or preview.get("taskCode") != TASK_CODE or preview.get("taskName") != TASK_NAME:
        raise ValueError("Preview must identify Manage Project Plan Types and its exact task code.")
    final_data = preview.get("finalData")
    if not isinstance(final_data, dict):
        raise ValueError("Preview requires finalData.")
    return preview, final_data


def _check_preview(record: Any) -> dict[str, Any]:
    """Recheck task validation and routing only before recording approval."""
    preview, final_data = _preview_fields(record)
    path = final_data.get("archivePath")
    if not isinstance(path, str) or not path:
        raise ValueError("Preview requires finalData.archivePath.")
    content = Path(path).read_bytes()
    if final_data.get("archiveSha256") != hashlib.sha256(content).hexdigest():
        raise ValueError("Prepared archive bytes do not match the preview SHA-256; rebuild and approve.")
    result = _validate(content, final_data.get("operation"))
    _contract.validate_source_intent(content, final_data.get('sourceInput'))
    if record.get("archiveValidation") != result:
        raise ValueError("Executable archive findings are missing or stale; rebuild the preview.")
    routing = record.get("taskRoutingContext")
    if not isinstance(routing, dict):
        raise ValueError("Preview must retain its Task Hook routing context.")
    route_input = {**routing, "taskName": TASK_NAME, "finalData": final_data, "ruleResults": preview.get("ruleResults")}
    checked = _with_reference_warnings(route_input, content)
    if checked['ruleResults'] != route_input['ruleResults']:
        raise ValueError('Reference warnings are missing or stale; rebuild the preview.')
    routed = _route(checked)
    if routed.get("runbookBinding") != preview.get("runbookBinding"):
        raise ValueError("Project Run Book binding changed; create a fresh preview and approval.")
    return result


def approve_preview(record: dict[str, Any]) -> dict[str, Any]:
    """Call only after explicit approval of the displayed preview and exact ZIP."""
    _check_preview(record)
    approved = approve_data_load_preview({"preview": record["preview"]})
    # Task evidence stays outside the authoritative core preview and approval.
    return {
        "preview": approved["preview"], "approval": approved["approval"],
        "taskEvidence": {
            "archiveValidation": record["archiveValidation"],
            "taskRoutingContext": record["taskRoutingContext"],
        },
        "previewSha256": _digest(record),
    }


def verify_archive(envelope: dict[str, Any], content: bytes) -> dict[str, Any]:
    """Verify retained approval and exact bytes without rerunning task planning."""
    if not isinstance(envelope, dict):
        raise ValueError("Approved envelope must be an object.")
    preview, approval = envelope.get("preview"), envelope.get("approval")
    evidence = envelope.get("taskEvidence")
    if not isinstance(evidence, dict) or set(evidence) != {"archiveValidation", "taskRoutingContext"}:
        raise ValueError("Task evidence is missing; rebuild and approve legacy envelopes.")
    record = {"preview": preview, **evidence}
    if not isinstance(approval, dict) or envelope.get("previewSha256") != _digest(record):
        raise ValueError("Approval does not cover the immutable preview; rebuild and approve.")
    _preview_fields(record)
    # Task findings and routing were evaluated before approval. Their retained
    # evidence is covered by the record digest above; do not reevaluate it or
    # depend on current rules, the planner, or the original source/context file.
    # Core checks the approved preview/approval, current Run Book binding and
    # the supplied archive's SHA-256 without rebuilding a task preview.
    # The core verifier accepts a path. Verify the supplied immutable bytes,
    # never reread the original source, which may have changed after approval.
    with tempfile.TemporaryDirectory(prefix="ppt-verify-") as directory:
        archive = Path(directory) / "prepared.zip"
        archive.write_bytes(content)
        verified = verify_approved_data_load_archive(
            {"preview": preview, "approval": approval}, archive,
        )
    return verified["taskValidationEnvelope"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("--input", type=Path, required=True, help="Existing Task Hook input JSON, including persisted context and finalData target details.")
    approve = commands.add_parser("approve")
    approve.add_argument("--input", type=Path, required=True, help="The explicitly user-approved preview JSON.")
    verify = commands.add_parser("verify")
    verify.add_argument("--input", type=Path, required=True, help="Approved envelope JSON.")
    verify.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "build":
            result = build_from_input(json.loads(args.input.read_text()))
        elif args.command == "approve":
            result = approve_preview(json.loads(args.input.read_text()))
        else:
            result = verify_archive(json.loads(args.input.read_text()), args.archive.read_bytes())
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
