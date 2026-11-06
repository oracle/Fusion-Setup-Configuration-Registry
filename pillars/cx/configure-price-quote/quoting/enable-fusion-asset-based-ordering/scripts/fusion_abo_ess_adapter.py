#!/usr/bin/env python3
"""ABO-specific approval and at-most-once boundary over the shared ESS client.

The shared ESS submitter owns the Fusion HTTP calls. This adapter owns only the
ABO contract, safe result projection, and the rule that a POST is never retried.
The workflow controller persists its dispatch reservation before invoking this
script; a caller must not invoke submission without that reservation.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


REPO_ROOT = Path(__file__).resolve().parents[6]
CORE_ESS_SCRIPTS = REPO_ROOT / "core" / "fusion-api" / "ess-job-submitter" / "scripts"
sys.path.insert(0, str(CORE_ESS_SCRIPTS))
import ess_job_submitter as core_ess  # noqa: E402


TASK_CODE = "FUSION_ABO_UNIFIED_ASSET_READ_MODEL_SYNC"
TASK_NAME = "Unified Asset Read Model Sync"
JOB_DEFINITION_ID = (
    "JobDefinition://oracle/apps/ess/configPriceQuote/assets/"
    "UnifiedAssetReadModelSyncMasterJob"
)
SAFE_STATE = re.compile(r"[A-Za-z0-9_ -]{1,80}\Z")
SHA256 = re.compile(r"[a-f0-9]{64}\Z")
RECENT_LOOKUP_FIELDS = (
    "requestId",
    "jobDefinitionId",
    "jobDisplayName",
    "description",
    "application",
    "state",
    "stateDescription",
    "processPhase",
    "processPhaseDescription",
    "cause",
    "causeDescription",
    "errorType",
    "errorWarningMessage",
    "submissionTime",
    "completedTime",
    "elapsedTime",
    "ecid",
)


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _exact_keys(value: dict[str, Any], keys: set[str], field: str) -> None:
    if set(value) != keys:
        raise ValueError(f"{field} has missing or unsupported fields")


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def _nonblank(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonblank string")
    return value.strip()


def _authority(value: Any, field: str) -> tuple[str, int]:
    parsed = urlsplit(_nonblank(value, field))
    if (
        parsed.scheme.lower() != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise ValueError(f"{field} must be a credential-free HTTPS host")
    try:
        port = parsed.port or 443
    except ValueError as exc:
        raise ValueError(f"{field} has an invalid port") from exc
    return parsed.hostname.casefold(), port


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{field} must be a positive integer")
    return value


def load_delegation_contract(
    contract_path: str | Path, props: dict[str, str]
) -> tuple[dict[str, Any], int, int]:
    """Validate the immutable, approved ABO envelope before any side effect."""

    contract = _mapping(json.loads(Path(contract_path).read_text(encoding="utf-8")), "ESS contract")
    _exact_keys(
        contract,
        {
            "contract_version", "stage", "task", "fusion_environment_context",
            "requested_payload_overrides", "execution_options", "approval",
            "job_contract", "request_payload", "audit_context",
        },
        "ESS contract",
    )
    if contract["contract_version"] != "1.0" or contract["stage"] != "approved_submission":
        raise ValueError("ESS contract is not an approved v1.0 submission")
    task = _mapping(contract["task"], "ESS task")
    _exact_keys(task, {"task_name", "task_code"}, "ESS task")
    if task["task_name"] != TASK_NAME or task["task_code"] != TASK_CODE:
        raise ValueError("ESS contract does not identify the ABO sync task")
    target = _mapping(contract["fusion_environment_context"], "ESS target")
    _exact_keys(target, {"environment", "fusion_host"}, "ESS target")
    if _nonblank(target["environment"], "ESS environment") != _nonblank(
        props.get("environment"), "configured environment"
    ):
        raise ValueError("ESS contract targets a different environment")
    if _authority(target["fusion_host"], "ESS Fusion host") != _authority(
        props.get("restBaseUrl"), "configured REST host"
    ):
        raise ValueError("ESS contract targets a different Fusion host")
    options = _mapping(contract["execution_options"], "ESS execution options")
    _exact_keys(options, {"wait_seconds", "poll_interval_seconds"}, "ESS execution options")
    wait_seconds = _positive_int(options["wait_seconds"], "ESS wait_seconds")
    poll_interval = _positive_int(options["poll_interval_seconds"], "ESS poll_interval_seconds")
    approval = _mapping(contract["approval"], "ESS approval")
    _exact_keys(approval, {"explicit_submission_approval", "approved_payload_sha256"}, "ESS approval")
    if approval["explicit_submission_approval"] is not True:
        raise ValueError("ESS submission lacks explicit approval")
    payload = _mapping(contract["request_payload"], "ESS request payload")
    if not payload:
        raise ValueError("ESS request payload is empty")
    approved_hash = approval["approved_payload_sha256"]
    actual_hash = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    if not isinstance(approved_hash, str) or not SHA256.fullmatch(approved_hash) or approved_hash != actual_hash:
        raise ValueError("ESS payload differs from the approved payload")
    job = _mapping(contract["job_contract"], "ESS job contract")
    _exact_keys(job, {"job_definition_id", "application"}, "ESS job contract")
    if (
        job["job_definition_id"] != JOB_DEFINITION_ID
        or job["application"] != "CrmEss"
        or payload.get("jobDefinitionId") != job["job_definition_id"]
        or payload.get("application") != job["application"]
        or payload.get("product") != "CPQ"
        or payload.get("requestParameters") != []
        or set(payload) != {"jobDefinitionId", "application", "product", "requestParameters", "description"}
    ):
        raise ValueError("ESS payload differs from the fixed ABO sync job")
    if not _nonblank(payload["description"], "ESS description").startswith(
        "FDOS Fusion ABO Unified Asset Read Model Sync | project="
    ):
        raise ValueError("ESS description does not identify the ABO workflow")
    if contract["requested_payload_overrides"] != {}:
        raise ValueError("ESS payload overrides are not permitted")
    audit = _mapping(contract["audit_context"], "ESS audit context")
    _exact_keys(
        audit,
        {
            "workflow_approval_fingerprint", "ess_idempotency_key",
            "adaptive_search_publish_operation_id", "adaptive_search_job_id",
        },
        "ESS audit context",
    )
    fingerprint = audit["workflow_approval_fingerprint"]
    if not isinstance(fingerprint, str) or not SHA256.fullmatch(fingerprint):
        raise ValueError("ESS parent approval fingerprint is invalid")
    for field in (
        "ess_idempotency_key", "adaptive_search_publish_operation_id", "adaptive_search_job_id"
    ):
        _nonblank(audit[field], field)
    core_ess.validate_request_payload(payload)
    return payload, wait_seconds, poll_interval


def _auth_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        access_token=None,
        redirect_url=None,
        auth_code=None,
        open_browser=not args.no_open_browser,
        callback_timeout=core_ess.DEFAULT_CALLBACK_TIMEOUT_SECONDS,
        token_cache=args.token_cache,
        force_login=False,
    )


def _failure(*, stage: str, dispatched: bool, exc: Exception) -> dict[str, Any]:
    if isinstance(exc, core_ess.FusionHttpError):
        failure_class = "auth_or_authorization" if exc.status_code in {401, 403} else "fusion_api"
    elif isinstance(exc, (TimeoutError, ConnectionError, OSError)):
        failure_class = "transport_or_environment"
    elif isinstance(exc, (ValueError, KeyError, TypeError, json.JSONDecodeError)):
        failure_class = "input_validation"
    else:
        failure_class = "execution"
    return {
        "execution_result": {"submitted": False, "requestId": None},
        "diagnostics": {
            "dispatch_attempted": dispatched,
            "failure_stage": stage,
            "failure_class": failure_class,
            "error_type": type(exc).__name__,
        },
    }


def _safe_status(status: dict[str, Any], request_id: int) -> dict[str, Any]:
    reported_id = status.get("requestId")
    if reported_id is not None and (
        isinstance(reported_id, bool) or str(reported_id) != str(request_id)
    ):
        raise ValueError("ESS status belongs to a different request")
    raw_state = status.get("state")
    state = raw_state.strip() if isinstance(raw_state, str) else None
    if state is not None and not SAFE_STATE.fullmatch(state):
        state = None
    terminal = core_ess.is_terminal_status(status)
    success = core_ess.is_success_status(status) if terminal else None
    cause = str(status.get("cause") or "").strip().upper()
    has_error = any(
        status.get(key) for key in ("errorType", "errorWarningMessage", "errorWarningDetail")
    )
    if (
        state and state.upper() == "COMPLETED"
        and terminal and success is False
        and cause in core_ess.NON_TERMINAL_CAUSES
        and not has_error
    ):
        # Fusion can expose COMPLETED before it exposes a final success cause.
        # Keep reading this request instead of recording an unsupported failure.
        terminal, success = False, None
    if terminal and not success and (status.get("cause") in {None, "", "NON_TERMINAL"}):
        if state and state.upper() in {"SUCCESS", "SUCCEEDED"} and not any(
            status.get(key) for key in ("errorType", "errorWarningMessage", "errorWarningDetail")
        ):
            success = True
    return {
        "execution_result": {
            "submitted": False,
            "requestId": request_id,
            "terminal": terminal,
            "success": success,
            "status": {"state": state},
        },
        "diagnostics": {"read_only": True, "timed_out_waiting": False},
    }


def _safe_recent_request(status: dict[str, Any]) -> dict[str, Any]:
    return {
        "requestId": status.get("requestId"),
        "jobDefinitionId": status.get("jobDefinitionId"),
        "jobDisplayName": status.get("jobDisplayName"),
        "description": status.get("description"),
        "application": status.get("application"),
        "state": status.get("state"),
        "stateDescription": status.get("stateDescription"),
        "processPhase": status.get("processPhase"),
        "cause": status.get("cause"),
        "causeDescription": status.get("causeDescription"),
        "submissionTime": status.get("submissionTime"),
        "completedTime": status.get("completedTime"),
        "elapsedTime": status.get("elapsedTime"),
        "errorType": status.get("errorType"),
        "errorWarningMessage": status.get("errorWarningMessage"),
        "ecid": status.get("ecid"),
    }


def _find_recent(
    props: dict[str, str],
    args: argparse.Namespace,
    job_definition_id: str,
) -> tuple[int, dict[str, Any]]:
    since_minutes = _positive_int(args.since_minutes, "since_minutes")
    token = core_ess.get_token(props, _auth_args(args))
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=since_minutes)).isoformat()
    query = f'jobDefinitionId eq "{job_definition_id}" and submissionTime ge "{since}"'
    response = core_ess.request_json(
        props,
        core_ess.build_url(
            props,
            core_ess.ESS_REQUESTS_RESOURCE,
            {
                "q": query,
                "orderBy": "submissionTime:desc",
                "fields": ",".join(RECENT_LOOKUP_FIELDS),
            },
        ),
        method="GET",
        access_token=token,
        timeout=args.timeout,
    )
    items = response.body.get("items", [])
    if not isinstance(items, list):
        raise ValueError("recent ESS request lookup did not return an items array")
    return 0, {
        "execution_result": {
            "submitted": False,
            "requestId": None,
            "recent_requests": [
                _safe_recent_request(item) for item in items if isinstance(item, dict)
            ],
        },
        "diagnostics": {
            "read_only": True,
            "lookup_window_minutes": since_minutes,
            "timed_out_waiting": False,
        },
    }


def _monitor(
    props: dict[str, str], args: argparse.Namespace, request_id: int
) -> tuple[int, dict[str, Any]]:
    wait_seconds = _positive_int(args.wait_seconds, "wait_seconds")
    poll_interval = _positive_int(args.poll_interval, "poll_interval")
    token = core_ess.get_token(props, _auth_args(args))
    deadline = time.monotonic() + wait_seconds
    refreshed = False
    while True:
        try:
            response = core_ess.get_job_request(
                props, token, request_id, fields=list(core_ess.DEFAULT_STATUS_FIELDS), timeout=args.timeout
            )
        except core_ess.FusionHttpError as exc:
            if exc.status_code not in {401, 403} or refreshed:
                raise
            token = core_ess.get_token(props, _auth_args(args), force_login=True)
            refreshed = True
            continue
        status = _mapping(response.body, "ESS status")
        result = _safe_status(status, request_id)
        execution = result["execution_result"]
        if execution["terminal"]:
            return (0 if execution["success"] else 4), result
        if time.monotonic() >= deadline:
            result["diagnostics"]["timed_out_waiting"] = True
            return 3, result
        time.sleep(min(poll_interval, max(0.0, deadline - time.monotonic())))


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ABO-approved ESS delegation over the shared submitter")
    parser.add_argument("--delegation-contract-file")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--submit-only", action="store_true")
    parser.add_argument("--request-id", type=int)
    parser.add_argument("--find-recent-job-definition")
    parser.add_argument("--since-minutes", type=int)
    parser.add_argument("--properties", default=str(core_ess.DEFAULT_PROPERTIES_PATH))
    parser.add_argument("--token-cache", default="auto")
    parser.add_argument("--no-open-browser", action="store_true")
    parser.add_argument("--wait-seconds", type=int, default=300)
    parser.add_argument("--poll-interval", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args(argv)
    selected = sum(
        bool(value)
        for value in (args.validate_only, args.submit_only, args.request_id, args.find_recent_job_definition)
    )
    if selected != 1:
        parser.error("choose exactly one validation, submission, monitoring, or recent-lookup mode")
    if args.validate_only or args.submit_only:
        if not args.delegation_contract_file or args.request_id is not None:
            parser.error("contract validation/submission requires only --delegation-contract-file")
        if args.find_recent_job_definition or args.since_minutes:
            parser.error("contract validation/submission does not accept recent lookup options")
    elif args.request_id is not None:
        if args.delegation_contract_file or args.find_recent_job_definition or args.since_minutes:
            parser.error("monitoring requires only --request-id")
    elif args.find_recent_job_definition:
        if args.delegation_contract_file or args.request_id is not None:
            parser.error("recent lookup does not accept contract or request-id options")
        if not args.since_minutes or args.since_minutes <= 0:
            parser.error("recent lookup requires --since-minutes")
    else:
        parser.error("monitoring requires only --request-id")
    return args


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    dispatch_attempted = False
    stage = "pre_dispatch_validation" if args.delegation_contract_file else "status_tracking"
    try:
        _positive_int(args.timeout, "timeout")
        props = core_ess.read_properties(Path(args.properties))
        core_ess.require_props(props, ["environment", "restBaseUrl"])
        _authority(props["restBaseUrl"], "configured REST host")
        if args.find_recent_job_definition:
            code, result = _find_recent(
                props, args, _nonblank(args.find_recent_job_definition, "job definition")
            )
        elif args.request_id is not None:
            request_id = _positive_int(args.request_id, "request_id")
            code, result = _monitor(props, args, request_id)
        else:
            payload, wait_seconds, poll_interval = load_delegation_contract(
                args.delegation_contract_file, props
            )
            if args.validate_only:
                code = 0
                result = {
                    "validation_result": {
                        "valid": True,
                        "dispatch_attempted": False,
                        "approved_payload_sha256": hashlib.sha256(
                            _canonical_json(payload).encode("utf-8")
                        ).hexdigest(),
                    },
                    "diagnostics": {"dispatch_attempted": False, "read_only": True},
                }
            else:
                # Token acquisition is pre-dispatch. The controller already
                # persisted dispatch_started before calling this process.
                token = core_ess.get_token(props, _auth_args(args))
                stage = "submission_dispatch"
                dispatch_attempted = True
                response = core_ess.submit_job_request(props, token, payload, timeout=args.timeout)
                request_id = core_ess.extract_request_id(response.body, response.headers)
                request_id = _positive_int(request_id, "ESS request id")
                result = {
                    "execution_result": {"submitted": True, "requestId": request_id},
                    "diagnostics": {"dispatch_attempted": True, "failure_stage": None},
                }
                code = 0
                # The controller uses --submit-only to persist the ID before
                # it issues any GET. No implicit poll or second POST here.
                assert args.submit_only and wait_seconds > 0 and poll_interval > 0
    except Exception as exc:
        result = _failure(stage=stage, dispatched=dispatch_attempted, exc=exc)
        code = 1
    print(json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
