"""Shared Field Service task workflow: preview, approval, write, verify."""
from __future__ import annotations

import argparse
import json
import hashlib
import hmac
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Protocol


ROOT = Path(__file__).resolve().parents[4]
REST_CLIENT = ROOT / "core/fusion-api/rest-api-client/scripts/fusion_rest_client.py"
READ_CLIENT = Path(__file__).with_name("rest_client_status.py")
REST_SERVICE = "field-service"
CONTRACT_BLOCK = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)
VERIFICATION_ATTEMPTS = 8
VERIFICATION_INTERVAL_SECONDS = 3


def add_service_argument(parser: argparse.ArgumentParser) -> None:
    """Expose the fixed task transport without allowing scope substitution."""
    parser.add_argument(
        "--service", choices=(REST_SERVICE,), default=REST_SERVICE,
        help="Task API service (default and only option: field-service); uses "
        "fs_restBaseUrl and fs_scope. Project prevalidation is a separate workflow.",
    )


class WorkflowBlocked(RuntimeError):
    def __init__(self, message: str, *, failure_class: str = "input_validation") -> None:
        super().__init__(message)
        self.failure_class = failure_class


class PartialExecutionBlocked(WorkflowBlocked):
    """A write may have applied; no later request may be attempted."""

    def __init__(self, message: str, *, sha256: str, completed_count: int, safe_summary: str = "", failure_class: str = "fusion_api_error") -> None:
        super().__init__(message, failure_class=failure_class)
        self.sha256 = sha256
        self.completed_count = completed_count
        self.safe_summary = safe_summary


class TaskAdapter(Protocol):
    task_code: str

    def resolve_route(self, direction: str | None) -> dict[str, str]: ...

    def preflight(
        self, workbook: Path, get: Any, temp: Path
    ) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]: ...

    def build_preview(
        self,
        payload: dict[str, Any],
        environment: str,
        baselines: dict[str, dict[str, Any]],
    ) -> dict[str, Any]: ...

    def mismatches(self, expected: dict[str, Any], actual: dict[str, Any]) -> list[str]: ...


def resolve_execution_route(
    contract_path: Path, task_code: str, execution_direction: str | None = None
) -> dict[str, str]:
    """Resolve a task-owned execution contract without task-specific code."""
    try:
        blocks = CONTRACT_BLOCK.findall(contract_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise WorkflowBlocked("Execution-direction contract could not be read.", failure_class="catalog_or_metadata_mismatch") from error
    if len(blocks) != 1:
        raise WorkflowBlocked("Execution-direction contract must contain exactly one JSON block.", failure_class="catalog_or_metadata_mismatch")
    try:
        contract = json.loads(blocks[0])
    except json.JSONDecodeError as error:
        raise WorkflowBlocked("Execution-direction contract is not valid JSON.", failure_class="catalog_or_metadata_mismatch") from error
    directions = contract.get("executionDirections") if isinstance(contract, dict) else None
    default = contract.get("defaultDirection") if isinstance(contract, dict) else None
    if (
        contract.get("taskCode") != task_code
        or not isinstance(directions, dict)
        or default not in directions
    ):
        raise WorkflowBlocked("Execution-direction contract is invalid.", failure_class="catalog_or_metadata_mismatch")
    direction = execution_direction or default
    selected = directions.get(direction)
    if (
        not isinstance(selected, dict)
        or not isinstance(selected.get("executorSkill"), str)
        or not isinstance(selected.get("orchestration"), str)
    ):
        raise WorkflowBlocked("Unsupported task execution direction.", failure_class="catalog_or_metadata_mismatch")
    return {
        "taskCode": task_code,
        "defaultDirection": default,
        "executionContract": str(contract_path),
        "requestedDirection": direction,
        "executorSkill": selected["executorSkill"],
        "orchestration": selected["orchestration"],
        "service": REST_SERVICE,
    }


def _props(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if separator and key.strip():
            values[key.strip()] = value.strip()
    if not values.get("environment"):
        raise WorkflowBlocked("Selected FDOS environment profile has no environment identity.", failure_class="transport_or_environment")
    return values


def _snapshot_properties(properties: Path, temporary: Path) -> Path:
    """Freeze the selected profile before target resolution or REST preflight."""
    try:
        contents = properties.read_bytes()
    except OSError as error:
        raise WorkflowBlocked(
            "Selected FDOS environment profile could not be read.",
            failure_class="transport_or_environment",
        ) from error
    snapshot = temporary / "selected-field-service.properties"
    try:
        descriptor = os.open(snapshot, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(contents)
    except OSError as error:
        raise WorkflowBlocked(
            "Selected FDOS environment profile could not be snapshotted.",
            failure_class="artifact_persistence",
        ) from error
    return snapshot


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _execution_target(properties: Path) -> dict[str, str]:
    """Return the non-secret Field Service target selected by a profile.

    The target is deliberately derived from the same properties file supplied
    to the REST client.  A display-only ``environment`` label is insufficient:
    it can be reused for a different tenant.
    """
    values = _props(properties)
    missing = [name for name in ("fs_restBaseUrl", "fs_scope") if not values.get(name)]
    if missing:
        raise WorkflowBlocked(
            f"Selected FDOS environment profile is missing: {', '.join(missing)}.",
            failure_class="transport_or_environment",
        )
    base_url = values["fs_restBaseUrl"].rstrip("/")
    if not re.fullmatch(r"https://[^/]+(?:/[^?#]*)?", base_url):
        raise WorkflowBlocked(
            "Selected FDOS environment profile has an invalid Field Service base URL.",
            failure_class="transport_or_environment",
        )
    # Keep the scope out of previews and durable evidence while still binding
    # the approval to the OAuth audience selected for the target.
    scope_fingerprint = hashlib.sha256(values["fs_scope"].encode("utf-8")).hexdigest()
    target = {
        "environment": values["environment"],
        "service": REST_SERVICE,
        "fsRestBaseUrl": base_url,
        "fsScopeSha256": scope_fingerprint,
    }
    return {
        **target,
        "fingerprint": hashlib.sha256(_canonical_json(target).encode("utf-8")).hexdigest(),
    }


def _bind_preview_target(preview: dict[str, Any], target: dict[str, str]) -> dict[str, Any]:
    """Bind the immutable approval digest to the selected REST target."""
    if preview.get("environment") != target["environment"]:
        raise WorkflowBlocked(
            "Preview environment does not match the selected FDOS environment profile.",
            failure_class="transport_or_environment",
        )
    bound = dict(preview)
    bound["targetFingerprint"] = target["fingerprint"]
    digest_input = dict(bound)
    digest_input.pop("sha256", None)
    bound["sha256"] = hashlib.sha256(_canonical_json(digest_input).encode("utf-8")).hexdigest()
    return bound


def _assert_approved_target(properties: Path, preview: dict[str, Any]) -> None:
    """Fail closed if the selected profile changed after approval was built."""
    approved = preview.get("targetFingerprint")
    actual = _execution_target(properties)["fingerprint"]
    if not isinstance(approved, str) or not hmac.compare_digest(approved, actual):
        error = WorkflowBlocked(
            "Selected Field Service execution target differs from the approved preview.",
            failure_class="transport_or_environment",
        )
        error.safe_summary = "approved_target_mismatch"
        raise error


def _assert_saved_approved_target(properties: Path, output: Path, approval: str | None) -> None:
    """Reject a changed profile before execute-mode preflight can read it."""
    if not approval:
        return
    try:
        evidence = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise WorkflowBlocked(
            "Execution requires the redacted evidence from the approved preview.",
            failure_class="approval_blocker",
        ) from error
    if not isinstance(evidence, dict) or evidence.get("sha256") != approval:
        raise WorkflowBlocked(
            "Approved checksum does not match the saved preview evidence.",
            failure_class="approval_blocker",
        )
    approved = evidence.get("targetFingerprint")
    actual = _execution_target(properties)["fingerprint"]
    if not isinstance(approved, str) or not hmac.compare_digest(approved, actual):
        raise WorkflowBlocked(
            "Selected Field Service execution target differs from the approved preview.",
            failure_class="transport_or_environment",
        )


def _call(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def _get(path: str, output: Path, properties: Path) -> dict[str, Any] | None:
    result = _call(
        [
            sys.executable,
            str(READ_CLIENT),
            path,
            "--method",
            "GET",
            "--service",
            REST_SERVICE,
            "--properties",
            str(properties),
            "--output",
            str(output),
        ]
    )
    if result.returncode == 0:
        return json.loads(output.read_text(encoding="utf-8"))
    try:
        failure = json.loads(result.stderr.strip().splitlines()[-1])
    except (ValueError, IndexError):
        failure = None
    status = failure.get("status") if isinstance(failure, dict) and failure.get("type") == "field_service_http_error" else None
    if type(status) is not int or not 100 <= status <= 599:
        status = None
    if status == 404:
        return None
    message = f"HTTP {status}" if status else "Core REST client failed without an authoritative HTTP status."
    failure_class = "fusion_api_error" if status else "transport_or_environment"
    raise WorkflowBlocked(f"GET {path} failed: {message}", failure_class=failure_class)


def _write(
    method: str,
    path: str,
    body: dict[str, Any],
    output: Path,
    properties: Path,
    headers: dict[str, str] | None = None,
) -> None:
    if method not in {"POST", "PUT"}:
        raise WorkflowBlocked(f"Unsupported write method: {method}")
    output.parent.mkdir(parents=True, exist_ok=True)
    request = output.with_suffix(".request.json")
    request.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
    args = [
            sys.executable,
            str(REST_CLIENT),
            path,
            "--method",
            method,
            "--service",
            REST_SERVICE,
            "--properties",
            str(properties),
            "--body-file",
            str(request),
            "--output",
            str(output),
        ]
    for name, value in (headers or {}).items():
        args.extend(["--header", f"{name}={value}"])
    result = _call(args)
    if result.returncode:
        message = (result.stderr or result.stdout).strip()
        failure_class = "fusion_api_error" if re.search(r"\bHTTP\s+\d{3}\b", message) else "transport_or_environment"
        diagnostic = output.with_suffix(".failure.json")
        diagnostic.write_text(
            json.dumps(
                {"status": "failed", "operation": "write", "method": method, "path": path, "requestArtifact": str(request), "response": message},
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        # Raw diagnostics stay in the temporary directory.  Attach an
        # allow-listed summary so callers can retain the actionable cause
        # without persisting a response body or customer payload.
        error = WorkflowBlocked(
            f"{method} request failed: {_safe_failure_summary_from_text(message)} (diagnostic: {diagnostic})",
            failure_class=failure_class,
        )
        error.safe_summary = _safe_failure_summary_from_text(message)
        raise error
    request.unlink(missing_ok=True)


def _put(
    path: str,
    body: dict[str, Any],
    output: Path,
    properties: Path,
    headers: dict[str, str] | None = None,
) -> None:
    """Compatibility entry point for PUT-only task adapters."""
    _write("PUT", path, body, output, properties, headers)


def _redacted_path_template(path: object, *, verify_path: object = None) -> str:
    if not isinstance(path, str) or not path.startswith("/"):
        return "redacted"
    schedule_item = re.fullmatch(r"(/api/field-service/configuration/v1/workSchedules/)[^/]+(/items)(/[^/]+)?", path)
    if schedule_item:
        return schedule_item[1] + "{identity}" + schedule_item[2] + ("/{itemId}" if schedule_item[3] else "")
    # A create request uses a collection path and a distinct singular read-back
    # path.  The collection path contains no customer identity, so retain it
    # verbatim in redacted evidence.  Singular read/write paths redact only the
    # final identity segment.
    if isinstance(verify_path, str) and verify_path.startswith("/") and verify_path != path:
        return path
    prefix, separator, _ = path.rstrip("/").rpartition("/")
    return f"{prefix}{separator}{{identity}}" if separator else "redacted"


def _write_redacted_evidence(output: Path, preview: dict[str, Any]) -> None:
    """Persist only immutable routing metadata; never customer request or baseline data."""
    output.parent.mkdir(parents=True, exist_ok=True)
    requests = preview.get("requests") if isinstance(preview.get("requests"), list) else []
    evidence = {
        "redacted": True,
        "taskCode": preview.get("taskCode"),
        "executionDirection": preview.get("executionDirection"),
        "environment": preview.get("environment"),
        "targetFingerprint": preview.get("targetFingerprint"),
        "sha256": preview.get("sha256"),
        "approvalRequired": preview.get("approvalRequired"),
        "retryPolicy": preview.get("retryPolicy"),
        "requestSequence": [
            {
                "sequence": index,
                "operationId": request.get("operationId"),
                "method": request.get("method"),
                "pathTemplate": _redacted_path_template(
                    request.get("path"), verify_path=request.get("verifyPath")
                ),
            }
            for index, request in enumerate(requests, 1)
            if isinstance(request, dict)
        ],
    }
    output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _request_identity(request: dict[str, Any]) -> str:
    identity = request.get("identity", request.get("label", request.get("body", {}).get("label")))
    if isinstance(identity, str) and identity:
        return identity
    path = request.get("path")
    if isinstance(path, str) and path:
        return path
    raise WorkflowBlocked("Each task request requires a non-empty identity.")


def _safe_failure_summary_from_text(text: str) -> str:
    """Return only allow-listed REST diagnostics from a client response."""
    match = re.search(r"\bHTTP\s+(\d{3})\b", text)
    status = f"HTTP {match.group(1)}" if match else "Fusion REST client error"
    # The response can be followed by internal diagnostic text, so it need not
    # be at the end of the exception string.
    payload = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if payload:
        try:
            response = json.loads(payload.group(1))
        except json.JSONDecodeError:
            response = None
        if isinstance(response, dict):
            code = response.get("errorCode") or response.get("code")
            field = response.get("field") or response.get("property")
            ecid = response.get("ecid") or response.get("ECID")
            details = []
            if isinstance(code, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", code):
                details.append(f"code={code}")
            if isinstance(field, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", field):
                details.append(f"field={field}")
            if isinstance(ecid, str) and re.fullmatch(r"[A-Za-z0-9_.:-]{1,200}", ecid):
                details.append(f"ecid={ecid}")
            if details:
                return f"{status} ({', '.join(details)})"
    return status


def _safe_failure_summary(error: Exception) -> str:
    """Retain actionable API status without leaking endpoint output or payloads."""
    saved = getattr(error, "safe_summary", None)
    if isinstance(saved, str) and saved:
        return saved
    return _safe_failure_summary_from_text(str(error))


def _verify_readback(adapter: TaskAdapter, request: dict[str, Any], output: Path, properties: Path) -> list[str]:
    """Confirm a successful write with bounded GET-only polling."""
    differences: list[str] = []
    for attempt in range(VERIFICATION_ATTEMPTS):
        actual = _get(
            request.get("verifyPath", request["path"]),
            output.with_name(f"{output.stem}-{attempt + 1}.json"),
            properties,
        )
        if hasattr(adapter, "verify"):
            differences = adapter.verify(request, actual)
        else:
            differences = adapter.mismatches(request["body"], actual or {})
        if not differences:
            return []
        if attempt + 1 < VERIFICATION_ATTEMPTS:
            time.sleep(VERIFICATION_INTERVAL_SECONDS)
    return differences


def run(
    adapter: TaskAdapter,
    workbook: Path,
    direction: str | None,
    mode: str,
    approval: str | None,
    properties: Path,
    output: Path,
    *,
    include_exact_preview: bool = False,
) -> dict[str, Any]:
    route = adapter.resolve_route(direction)
    if route["requestedDirection"] != "ora_rest_execution":
        raise WorkflowBlocked(
            f"{route['requestedDirection']} cannot execute {adapter.task_code}; "
            "select ora_rest_execution explicitly.",
            failure_class="catalog_or_metadata_mismatch",
        )
    with tempfile.TemporaryDirectory(prefix=f"{adapter.task_code.lower()}-") as folder:
        selected_properties = _snapshot_properties(properties, Path(folder))
        target = _execution_target(selected_properties)
        environment = target["environment"]
        if mode != "preview":
            _assert_saved_approved_target(selected_properties, output, approval)
        validate_design = getattr(adapter, "validate_design", None)
        if callable(validate_design):
            design_issues = validate_design(workbook)
            if design_issues:
                rule_ids = ", ".join(
                    str(issue.get("ruleId", "unknown"))
                    for issue in design_issues
                    if isinstance(issue, dict)
                ) or "unknown"
                raise WorkflowBlocked(
                    f"Design enforcement failed before REST lookup: {rule_ids}"
                )
        def selected_profile_get(path: str, response_output: Path) -> dict[str, Any] | None:
            if not response_output.resolve().is_relative_to(Path(folder).resolve()):
                raise WorkflowBlocked("Field Service baseline output must remain inside the run temporary directory.")
            return _get(path, response_output, selected_properties)

        payload, baselines = adapter.preflight(workbook, selected_profile_get, Path(folder))
        if callable(validate_design):
            payload["designValidation"] = {"status": "passed", "issues": []}
        requests = payload.get("requests") if isinstance(payload, dict) else None
        if isinstance(requests, list) and not requests:
            # A valid rerun that matches the authoritative GET baseline has no
            # external side effect to approve.  Record the outcome without
            # inventing an empty mutable preview or asking for a checksum.
            no_change_evidence = {
                "taskCode": adapter.task_code,
                "executionDirection": "ora_rest_execution",
                "environment": environment,
                "targetFingerprint": target["fingerprint"],
                "sha256": None,
                "approvalRequired": False,
                "retryPolicy": "not_applicable",
                "requests": [],
            }
            _write_redacted_evidence(output, no_change_evidence)
            return {
                "status": "no_changes",
                "taskCode": adapter.task_code,
                "requestCount": 0,
                "checksRun": ["workbook_validation", "design_enforcement", "preflight", "baseline_comparison"],
            }
        preview = _bind_preview_target(adapter.build_preview(payload, environment, baselines), target)
        _write_redacted_evidence(output, preview)
        if mode == "preview":
            result = {
                "status": "approval_required",
                "taskCode": adapter.task_code,
                "sha256": preview["sha256"],
                "requestCount": len(preview["requests"]),
            }
            if include_exact_preview:
                # The caller may present this transient value for human approval.
                # The persisted output above remains redacted.
                result["exactPreview"] = preview
            return result
        if approval != preview["sha256"]:
            raise WorkflowBlocked("Approval checksum is missing or does not match the fresh immutable preview.")
        verified = []
        failures = []
        for sequence, request in enumerate(preview["requests"], 1):
            identity = _request_identity(request)
            try:
                _assert_approved_target(selected_properties, preview)
                method = request.get("method", "PUT")
                write_output = Path(folder) / f"write-{sequence}.response.json"
                if method == "PUT" and not request.get("headers"):
                    _put(request["path"], request["body"], write_output, selected_properties)
                else:
                    _write(method, request["path"], request["body"], write_output, selected_properties, request.get("headers"))
                _assert_approved_target(selected_properties, preview)
                verification_request = getattr(adapter, "verification_request", None)
                readback_request = verification_request(request, write_output) if callable(verification_request) else request
                differences = _verify_readback(adapter, readback_request, Path(folder) / f"verify-{sequence}.json", selected_properties)
            except WorkflowBlocked as error:
                if getattr(adapter, "continue_independent_write_failures", False):
                    safe_summary = _safe_failure_summary(error)
                    failures.append({"sequence": sequence, "safeSummary": safe_summary})
                    diagnostics = output.parent / f"{output.stem}-diagnostics"
                    diagnostics.mkdir(parents=True, exist_ok=True)
                    (diagnostics / f"write-{sequence}.workflow.failure.json").write_text(
                        json.dumps(
                            {"status": "failed", "sequence": sequence, "safeSummary": safe_summary},
                            ensure_ascii=False,
                            indent=2,
                            sort_keys=True,
                        )
                        + "\n",
                        encoding="utf-8",
                    )
                    continue
                safe_summary = _safe_failure_summary(error)
                raise PartialExecutionBlocked(
                    f"Request {sequence} did not complete ({safe_summary}); remaining requests were not attempted.",
                    sha256=preview["sha256"],
                    completed_count=len(verified),
                    safe_summary=safe_summary,
                    failure_class=error.failure_class,
                ) from error
            if differences:
                raise PartialExecutionBlocked(
                    f"Verification failed at request {sequence}; remaining requests were not attempted.",
                    sha256=preview["sha256"],
                    completed_count=len(verified),
                    safe_summary="verification_mismatch",
                    failure_class="fusion_api_error",
                )
            verified.append({"sequence": sequence, "label": identity, "verified": True})
        result = {
            "status": "partial_failed" if failures else "completed",
            "taskCode": adapter.task_code,
            "sha256": preview["sha256"],
            "verified": verified,
            "failures": failures,
        }
        if include_exact_preview:
            # The task runner uses this only to render a redaction-safe
            # implementor summary.  Durable output remains the redacted
            # evidence written above.
            result["exactPreview"] = preview
        return result
