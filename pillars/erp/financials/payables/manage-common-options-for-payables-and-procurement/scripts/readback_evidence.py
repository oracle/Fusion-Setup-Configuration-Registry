#!/usr/bin/env python3
"""Bind content comparison to a recorded Core import and Shared export observation.

Receipts are local workflow evidence, not cryptographic proof against a person
who can rewrite the workspace. Only the producer below may create live receipts.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import json
from pathlib import Path
import re
import sys
import tempfile
import time
from types import SimpleNamespace
from urllib.error import URLError
from urllib.parse import urlsplit

SCHEMA = "payables.readback-observation.v1"
PRODUCER = "payables.shared-export-observer"
MAX_AGE = timedelta(hours=24)
TASK_CODES = {
    "ORA_AP_MANAGE_BANK_CHARGES",
    "AP_MANAGE_COMMON_OPTIONS_FOR_PAYABLES_AND_PROCUREMENT",
}


def _sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _fingerprint(value: dict) -> str:
    unsigned = {key: item for key, item in value.items() if key != "observationSha256"}
    return _sha(json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode())


def _host(value: str) -> str:
    if (not isinstance(value, str) or any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in value)
            or "?" in value or "#" in value):
        raise ValueError("A complete HTTPS target origin is required.")
    parsed = urlsplit(value)
    port, hostname = parsed.port, parsed.hostname
    if (parsed.scheme != "https" or not hostname or "@" in parsed.netloc
            or parsed.netloc.endswith(":") or port == 0 or "%" in hostname
            or parsed.path not in {"", "/"}):
        raise ValueError("A complete HTTPS target origin is required.")
    if ":" in hostname:
        if not parsed.netloc.startswith("["):
            raise ValueError("An IPv6 target origin must use brackets.")
        authority = "[" + hostname + "]"
    else:
        if len(hostname) > 253 or not all(
            re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label)
            for label in hostname.removesuffix(".").split(".")
        ):
            raise ValueError("A valid HTTPS target hostname is required.")
        authority = hostname
    return "https://" + authority + (f":{port}" if port not in (None, 443) else "")


def _instant(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("Observation times must be strings.")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Observation times must include a timezone.")
    return result.astimezone(timezone.utc)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _positive_id(value) -> bool:
    return isinstance(value, (str, int)) and not isinstance(value, bool) and str(value).isdigit() and int(value) > 0


def _zero(value) -> bool:
    return not isinstance(value, bool) and value in (0, "0")


def _reject_status_mutation(*args, **kwargs):
    raise ValueError("Only FSM status reads are allowed during read-back observation.")


def read_observation(path: Path | None) -> dict | None:
    if path is None:
        return None
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(value, dict):
            return value
    except (OSError, ValueError):
        pass
    return {"_readError": "Read-back observation is missing, unreadable, or not an object."}


def bind_readback_result(
    comparison: dict, evidence: dict | None, *, task_code: str, environment: str,
    baseline_sha256: str, candidate_sha256: str, export_sha256: str,
    import_request_id: str | None = None, target_url: str | None = None,
    now: datetime | None = None,
) -> dict:
    """Keep offline matches pending until the exact current load has read-back evidence."""
    result = dict(comparison)
    comparison_status = comparison.get("comparisonStatus", comparison.get("status"))
    result.update(comparisonStatus=comparison_status, persistenceVerified=False)
    if comparison_status != "PASS":
        result["status"] = "FAIL"
        return result
    if evidence is None:
        result.update(status="PENDING", persistenceReason="Fresh governed export observation required.")
        return result
    try:
        if not isinstance(evidence, dict) or evidence.get("_readError"):
            raise ValueError("Read-back observation is unreadable.")
        if evidence.get("schemaVersion") != SCHEMA or evidence.get("producer") != PRODUCER:
            raise ValueError("Unsupported read-back observation.")
        if evidence.get("observationSha256") != _fingerprint(evidence):
            raise ValueError("Read-back observation integrity mismatch.")
        if not _positive_id(import_request_id) or not target_url:
            raise ValueError("The current import request and target URL are required.")
        expected = {
            "taskCode": task_code, "baselineSha256": baseline_sha256,
            "candidateSha256": candidate_sha256, "exportSha256": export_sha256,
        }
        if any(evidence.get(key) != value for key, value in expected.items()):
            raise ValueError("Task or package digest differs from this comparison.")
        if any(not re.fullmatch(r"[0-9a-f]{64}", value)
               for value in (baseline_sha256, candidate_sha256, export_sha256)):
            raise ValueError("Actual baseline, candidate, and export digests are required.")
        if export_sha256 in {candidate_sha256, baseline_sha256}:
            raise ValueError("A candidate or baseline archive cannot serve as post-import proof.")
        context = evidence["environment"]
        if context["name"] != environment or _host(context["host"]) != _host(target_url):
            raise ValueError("Read-back observation belongs to a different environment.")
        imported, exported = evidence["import"], evidence["export"]
        if (str(imported["requestId"]) != str(import_request_id)
                or imported["status"] != "ORA_SUCCESS"
                or not _positive_id(imported["processId"])
                or not re.fullmatch(r"UCMFA[0-9]+", imported["contentId"])
                or any(not re.fullmatch(r"[0-9a-f]{64}", imported[key])
                       for key in ("initiationSha256", "preflightSha256"))):
            raise ValueError("Successful current import evidence is missing or mismatched.")
        if (exported["status"] not in {"COMPLETED", "COMPLETED_WARNINGS"}
                or not _positive_id(exported["processId"])
                or str(exported["processId"]) == str(imported["processId"])
                or exported["enclosure"] != "FileContent"):
            raise ValueError("A completed task-data export is required.")
        imported_at = _instant(imported["observedAt"])
        started_at = _instant(exported["startedAt"])
        observed_at = _instant(exported["observedAt"])
        current = now or _utc_now()
        if not imported_at <= started_at <= observed_at <= current:
            raise ValueError("Export evidence is out of order or dated in the future.")
        if current - observed_at > MAX_AGE:
            raise ValueError("Export observation is stale; obtain a new governed export.")
    except (KeyError, TypeError, ValueError, OverflowError):
        result.update(status="BLOCKED", persistenceReason=(
            "Read-back evidence is invalid, stale, or not bound to this task, target, "
            "current import request, and exact package digests."
        ))
        return result
    result.update(status="PASS", persistenceVerified=True,
                  persistenceReason="Requested values match a bound post-import export observation.",
                  readbackObservationSha256=evidence["observationSha256"])
    return result


def _services() -> SimpleNamespace:
    root = next((path for path in Path(__file__).resolve().parents
                 if (path / "core/data-loader/scripts/upload_and_initiate.py").is_file()), None)
    if root is None:
        raise ValueError("The repository Core/Shared services are unavailable.")
    for relative in ("shared/setup-export/fsm-csv-export/scripts",
                     "core/auth/fusion-oauth-authentication/scripts", "core/data-loader/scripts"):
        sys.path.insert(0, str(root / relative))
    auth = importlib.import_module("fusion_auth")
    loader = importlib.import_module("upload_and_initiate")
    status = importlib.import_module("get_data_load_info")
    exporter = importlib.import_module("fsm_csv_export_engine")
    return SimpleNamespace(auth=auth, loader=loader, status=status, exporter=exporter)


class ObservationFailure(ValueError):
    def __init__(self, failure_class: str, message: str):
        super().__init__(message)
        self.failure_class = failure_class


def _run_fingerprint(state: dict) -> str:
    return _sha(json.dumps({key: value for key, value in state.items() if key != "runSha256"},
                           sort_keys=True, separators=(",", ":")).encode())


def _resume_state(run_path: Path, plan: dict, initiated: dict, now: datetime) -> dict:
    """Validate the original attempt locally before any status/authentication call."""
    try:
        state = json.loads(run_path.read_text(encoding="utf-8"))
        if not isinstance(state, dict) or state.get("runSha256") != _run_fingerprint(state):
            raise ValueError("Run integrity differs.")
        for key in ("taskCode", "environment", "importRequestId", "candidateSha256",
                    "baselineSha256", "preflightSha256", "initiationSha256", "outputDirectory"):
            if state.get(key) != plan[key]:
                raise ValueError("Run input differs.")
        imported = state["importObservation"]
        if (state["status"] not in {"BLOCKED", "IN_PROGRESS"}
                or state["stage"] not in {"export-status", "export-download"}
                or state.get("failureClass") == "process_failed"
                or not _positive_id(state["exportProcessId"])
                or str(state["exportProcessId"]) == str(imported["processId"])
                or str(imported["requestId"]) != plan["importRequestId"]
                or imported["contentId"] != initiated["ContentId"]
                or imported["status"] != "ORA_SUCCESS"
                or not _positive_id(imported["processId"])
                or any(imported[key] != plan[key] for key in ("preflightSha256", "initiationSha256"))):
            raise ValueError("Run has no resumable export.")
        started = _instant(state["exportStartedAt"])
        if not _instant(imported["observedAt"]) <= started <= now or now - started > MAX_AGE:
            raise ValueError("Run timestamps are stale or inconsistent.")
        return state
    except (OSError, KeyError, TypeError, ValueError, OverflowError):
        raise ValueError("Recorded run is invalid, stale, or not bound to these inputs; cannot resume.") from None


def _diagnostic_codes(content: bytes) -> list[str]:
    # Retain product identifiers only; free text can contain credentials/customer data.
    return sorted(set(re.findall(r"\b(?:ORA-\d{5}|JBO-\d{5}|(?:AP|FND)_[A-Z][A-Z0-9_]{2,63})\b",
                                 content.decode("utf-8", errors="replace"))))[:50]


def _exception_chain(exc: Exception) -> list[BaseException]:
    chain = []
    while exc is not None and exc not in chain and len(chain) < 8:
        chain.append(exc)
        exc = exc.__cause__ or exc.__context__
    return chain


def _http_status(exc: Exception):
    for cause in _exception_chain(exc):
        status = getattr(cause, "http_status", None) or getattr(cause, "status_code", None)
        if isinstance(status, int) and not isinstance(status, bool):
            return status
    return None


def _failure_details(exc: Exception, stage: str) -> tuple[str, str]:
    if isinstance(exc, ObservationFailure):
        return exc.failure_class, str(exc)
    http_status = _http_status(exc)
    if http_status in (401, 403):
        return ("auth_expired_or_invalid" if http_status == 401 else "authorization_or_privilege",
                "The delegated service rejected authentication or access; use its owning authentication workflow.")
    if http_status:
        return "fusion_api_error", "The delegated Fusion request failed; inspect its recorded HTTP status."
    if stage == "artifact-write":
        return "artifact_persistence", "The downloaded evidence could not be saved; preserve this run."
    if any(isinstance(cause, (OSError, URLError)) for cause in _exception_chain(exc)):
        return "transport_or_environment", "The delegated service was unreachable or interrupted."
    if stage == "authentication":
        return "auth_expired_or_invalid", "Authentication could not complete; use the owning authentication workflow."
    return "input_validation", "The response or evidence did not satisfy this operation's binding checks."


def _validate_output_paths(output_dir: Path, inputs: tuple[Path, ...], *, resume: bool) -> None:
    """Reject unusable destinations locally, including before displaying a preview."""
    if output_dir.is_symlink() or (output_dir.exists() and not output_dir.is_dir()):
        raise ValueError("Read-back output directory must be an unlinked directory.")
    resolved_inputs = {path.resolve() for path in inputs}
    for name in ("readback-run.json", "readback.zip", "readback-observation.json"):
        path = output_dir / name
        if path.is_symlink():
            raise ValueError("Read-back outputs must not be symbolic links.")
        if path.resolve() in resolved_inputs or (path.exists() and any(
                source.exists() and path.samefile(source) for source in inputs)):
            raise ValueError("Read-back outputs must be distinct from all input files.")
        if resume and name == "readback-run.json":
            if not path.is_file():
                raise ValueError("Resume requires an existing regular read-back checkpoint.")
        elif path.exists():
            raise ValueError("Read-back outputs already exist; inspect them without overwriting.")


def produce_observation(
    *, task_code: str, baseline: Path, candidate: Path, preflight: Path,
    initiation: Path, properties: Path, output_dir: Path, execute: bool = False,
    wait_seconds: int = 60, resume: bool = False, services=None, clock=_utc_now,
) -> dict:
    """Preview locally; execute only at the approved Shared task-data export step."""
    if task_code not in TASK_CODES or not 0 <= wait_seconds <= 60:
        raise ValueError("Unsupported task or wait duration.")
    _validate_output_paths(output_dir, (baseline, candidate, preflight, initiation, properties), resume=resume)
    services = services or _services()
    props = services.auth.read_properties(properties)
    environment = {"name": props["environment"].strip(), "host": _host(props["restBaseUrl"])}
    preflight_bytes, initiation_bytes = preflight.read_bytes(), initiation.read_bytes()
    approved = services.loader.load_preflight_envelope(preflight)
    if preflight.read_bytes() != preflight_bytes:
        raise ValueError("Core preflight changed while being read.")
    initiated = json.loads(initiation_bytes)
    candidate_hash, baseline_hash = _sha(candidate.read_bytes()), _sha(baseline.read_bytes())
    if (approved.get("archiveSha256") != candidate_hash
            or approved.get("environment") != environment["name"]
            or _host(approved.get("host", "")) != environment["host"]
            or approved.get("sourceType") != "FSM"
            or initiated.get("archiveSha256") != candidate_hash
            or initiated.get("uploadStatus") != "SUCCESS"
            or initiated.get("initiationStatus") != "SUCCESS"
            or initiated.get("sourceType") != "FSM"
            or not _positive_id(initiated.get("RequestId"))
            or not re.fullmatch(r"UCMFA[0-9]+", str(initiated.get("ContentId", "")))):
        raise ValueError("Core preflight/initiation evidence does not match this candidate and target.")
    request_id = str(initiated["RequestId"])
    plan = {
        "status": "PREVIEW", "taskCode": task_code, "environment": environment,
        "importRequestId": request_id, "candidateSha256": candidate_hash,
        "baselineSha256": baseline_hash,
        "preflightSha256": _sha(preflight_bytes), "initiationSha256": _sha(initiation_bytes),
        "operation": "Observe Core import success; create, poll, and download one Shared task-data export.",
        "exportPayload": {"TaskCode": task_code, "SetupTaskCSVExportProcess": [{"TaskCode": task_code}]},
        "outputDirectory": str(output_dir.resolve()),
    }
    run_path, archive_path, evidence_path = (
        output_dir / name for name in ("readback-run.json", "readback.zip", "readback-observation.json")
    )
    state = _resume_state(run_path, plan, initiated, clock()) if resume else None
    if resume:
        plan.update(resume=True, exportProcessId=state["exportProcessId"],
                    operation="Poll and download the recorded Shared export; no new export.",
                    exportStartedAt=state["exportStartedAt"])
        plan.pop("exportPayload")
    if not execute:
        return plan
    _validate_output_paths(output_dir, (baseline, candidate, preflight, initiation, properties), resume=resume)
    output_dir.mkdir(parents=True, exist_ok=True)
    if not resume:
        state = {**plan, "status": "IN_PROGRESS", "stage": "import-status"}

    def save_state():
        state["runSha256"] = _run_fingerprint(state)
        # Atomic replacement keeps the original process checkpoint usable after interruption.
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output_dir, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(state, stream, indent=2)
            stream.write("\n")
        try:
            temporary.replace(run_path)
        finally:
            temporary.unlink(missing_ok=True)

    if not resume:
        with run_path.open("x", encoding="utf-8") as stream:
            state["runSha256"] = _run_fingerprint(state)
            json.dump(state, stream, indent=2)
    else:
        for key in ("failureClass", "message", "nextAction"):
            state.pop(key, None)
        state.update(status="IN_PROGRESS", stage="export-status")
        save_state()
    wait_started = None
    try:
        if resume:
            imported = state["importObservation"]
        else:
            load = services.status.get_data_load_info(
                request_id, config_path=properties, auth_options={"open_browser": False},
                poster=_reject_status_mutation,
            )
            rows = load.get("dataSets", [])
            if str(load.get("RequestId")) != request_id or not _zero(load.get("errorCount")) or len(rows) != 1:
                raise ValueError("Import status is incomplete or ambiguous.")
            row = rows[0]
            if (str(row.get("DataSetRequestId")) != request_id
                    or row.get("UcmContentId") != initiated["ContentId"]
                    or row.get("SourceType") != "FSM" or row.get("FsmTaskCode") != task_code
                    or row.get("DataSetStatus") != "ORA_SUCCESS" or not _zero(row.get("ObjectErrorCount"))
                    or not _positive_id(row.get("FsmMigRequestId"))):
                raise ValueError("The matching FSM import has not completed successfully.")
            imported = {
                "requestId": request_id, "contentId": initiated["ContentId"],
                "processId": str(row["FsmMigRequestId"]), "status": "ORA_SUCCESS",
                "observedAt": _time(clock()), "preflightSha256": _sha(preflight_bytes),
                "initiationSha256": _sha(initiation_bytes),
            }
        current_props = services.auth.read_properties(properties)
        if (current_props["environment"].strip() != environment["name"]
                or _host(current_props["restBaseUrl"]) != environment["host"]):
            raise ValueError("Target configuration changed during observation.")
        previous_stage = state["stage"]
        state["stage"] = "authentication"
        token = services.auth.get_access_token(current_props, open_browser=False)
        state["stage"] = previous_stage
        engine = services.exporter
        scope = engine.ExportScope(kind="task", primary_code=task_code, template_only=False)
        if resume:
            process_id, started = state["exportProcessId"], state["exportStartedAt"]
        else:
            state.update(stage="export-create", importObservation=imported)
            save_state()
            started = _time(clock())
            response = engine.create_export_process(current_props, token, scope)
            process_id = engine.extract_process_id(response, scope.process_child)
            if not _positive_id(process_id):
                raise ValueError("Shared export did not return a process identity; do not retry automatically.")
            state.update(stage="export-status", exportProcessId=str(process_id), exportStartedAt=started)
        save_state()
        state.setdefault("lastStatus", ["UNKNOWN"])
        wait_started = time.monotonic()
        process, items = engine.wait_for_result(
            current_props, token, scope, str(process_id), wait_seconds, 10
        )
        state["elapsedWaitSeconds"] = round(time.monotonic() - wait_started, 3)
        wait_started = None
        for record in [process, *items]:
            if (record.get("ProcessId", process_id) != process_id
                    and str(record.get("ProcessId")) != str(process_id)):
                raise ValueError("Export response process identity differs.")
            if record.get("TaskCode", task_code) != task_code:
                raise ValueError("Export response task differs.")
        statuses = {item.get("StatusCode") for item in items}
        safe_statuses = {"COMPLETED", "COMPLETED_WARNINGS", "COMPLETED_ERRORS",
                         "IN_PROGRESS", "NOT_STARTED", "PENDING", "RUNNING", "ERROR", "FAILED"}
        state["lastStatus"] = sorted({code if code in safe_statuses else "UNKNOWN" for code in statuses})
        completed = engine.process_completed(process.get("ProcessCompletedFlag"))
        state["processCompleted"] = completed
        if statuses & {"COMPLETED_ERRORS", "ERROR", "FAILED"}:
            try:
                log, enclosure = engine.download_result(
                    current_props, token, scope, str(process_id), download_log=True)
                if enclosure != "ProcessLog":
                    raise ValueError("The delegated enclosure is not a process log.")
                state["processLog"] = {"status": "RETRIEVED", "sha256": _sha(log),
                                       "byteCount": len(log), "diagnosticCodes": _diagnostic_codes(log)}
            except Exception as log_error:
                state["processLog"] = {"status": "UNAVAILABLE",
                                       "failureClass": _failure_details(log_error, "export-status")[0]}
            raise ObservationFailure("process_failed", "The recorded export completed with errors; inspect its status and sanitized log summary.")
        if not completed:
            raise ObservationFailure("process_timeout", "The recorded export did not complete within this polling window.")
        if len(statuses) != 1 or not statuses <= {"COMPLETED", "COMPLETED_WARNINGS"}:
            raise ObservationFailure("fusion_api_error", "The completed export has no unambiguous successful result.")
        state["stage"] = "export-download"
        save_state()
        content, enclosure = engine.download_result(current_props, token, scope, str(process_id))
        exported = {
            "processId": str(process_id), "status": next(iter(statuses)),
            "startedAt": started, "observedAt": _time(clock()), "enclosure": enclosure,
        }
        receipt = {
            "schemaVersion": SCHEMA, "producer": PRODUCER, "taskCode": task_code,
            "environment": environment, "baselineSha256": baseline_hash,
            "candidateSha256": candidate_hash, "exportSha256": _sha(content),
            "import": imported, "export": exported,
        }
        receipt["observationSha256"] = _fingerprint(receipt)
        check = bind_readback_result(
            {"status": "PASS"}, receipt, task_code=task_code, environment=environment["name"],
            baseline_sha256=baseline_hash, candidate_sha256=candidate_hash,
            export_sha256=receipt["exportSha256"], import_request_id=request_id,
            target_url=environment["host"], now=clock(),
        )
        if not check["persistenceVerified"]:
            raise ValueError("Downloaded evidence failed observation binding.")
        state["stage"] = "artifact-write"
        with archive_path.open("xb") as stream:
            stream.write(content)
        with evidence_path.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, indent=2)
        state.update(status="OBSERVED_NOT_RECONCILED", stage="complete",
                     archive=str(archive_path.resolve()), observation=str(evidence_path.resolve()))
        save_state()
        return state
    except Exception as exc:
        if wait_started is not None:
            state["elapsedWaitSeconds"] = round(time.monotonic() - wait_started, 3)
        failure_class, message = _failure_details(exc, state["stage"])
        # A failed authentication while resuming must retain the resumable process stage.
        if resume and state["stage"] == "authentication":
            state["stage"] = "export-status"
        state.update(status="BLOCKED", failureClass=failure_class, message=message,
                     nextAction=("After an explicit request to continue, preview --resume and execute "
                                 "status/download for this same process. Do not create a new export."
                                 if state.get("exportProcessId") and failure_class != "process_failed"
                                 and state["stage"] in {"export-status", "export-download"}
                                 else "Inspect this recorded attempt and diagnostics; any new export needs a fresh preview and approval."))
        http_status = _http_status(exc)
        if isinstance(http_status, int):
            state["httpStatus"] = http_status
        save_state()
        raise ValueError(f"Read-back observation blocked at {state['stage']}; see {run_path}.") from None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-code", required=True, choices=sorted(TASK_CODES))
    for name in ("baseline", "candidate", "preflight", "initiation", "properties", "output-dir"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--execute", action="store_true",
                        help="Run only after the active workflow approves the displayed export plan.")
    parser.add_argument("--wait-seconds", type=int, default=60)
    parser.add_argument("--resume", action="store_true",
                        help="Preview or explicitly continue status/download for the recorded export; never create another.")
    args = vars(parser.parse_args())
    try:
        print(json.dumps(produce_observation(**args), indent=2))
        return 0
    except Exception:
        print("Read-back observation blocked; inspect the inputs or recorded run. No persistence claim.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
