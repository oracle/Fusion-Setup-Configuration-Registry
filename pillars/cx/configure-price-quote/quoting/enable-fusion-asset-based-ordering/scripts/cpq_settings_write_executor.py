#!/usr/bin/env python3
"""Execute the task-local, narrowly approved CPQ Settings sequence for Fusion ABO.

This is deliberately *not* a generic CPQ REST client. It consumes the
task-local canonical plan and permits only the fixed CPQ v19 operations that
plan contains. The task coordinator owns project persistence and invokes this
module only after it has recreated a fresh preflight and obtained an exact,
target-bound approval.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence
from urllib.parse import urlsplit


def _find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "core" / "data-loader" / "scripts").is_dir():
            return candidate
    raise RuntimeError("Could not locate the FSCR repository root.")


REPO_ROOT = _find_repo_root(Path(__file__).resolve())
CPQ_WRITE_PLAN_SCRIPTS = Path(__file__).resolve().parent
for script_path in (CPQ_WRITE_PLAN_SCRIPTS,):
    sys.path.insert(0, str(script_path))

from cpq_rest_transport import (  # noqa: E402
    CpqClientError,
    CpqConfigurationError,
    CpqHttpError,
    CpqOAuthTransport,
    CpqResponse,
    CpqResponseError,
    CpqTransportError,
    OAuthOptions,
    build_cpq_oauth_properties,
    read_properties,
    validate_cpq_base_url,
)
from cpq_settings_write_plan import (  # noqa: E402
    CPQ_COMMERCE_SETTINGS_PATH,
    CPQ_COMMERCE_SETTINGS_BUSINESS_OBJECT,
    CPQ_COMMERCE_SETTINGS_TYPE,
    CPQ_FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_PATH,
    FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_KEY,
    FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_VALUE,
    FUSION_ABO_ENABLED_KEY,
    FUSION_ABO_PROCESS_KEY,
    PLAN_VERSION,
    CpqSettingsWritePlanError,
    build_fusion_abo_cpq_settings_write_plan,
)
from fusion_abo_prerequisites import FUSION_ABO_PREREQUISITE_FEATURE_CODES  # noqa: E402


DATA_LOADER_HANDOFF_VERSION = "26.10.1"
_SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$", re.IGNORECASE)
_DATA_LOADER_OPERATIONS = frozenset({
    "configure_fusion_abo_settings",
    "save_fusion_abo_process",
    "enable_fusion_abo",
    "configure_abo_delta_action_library_function",
})
CommandRunner = Callable[[Sequence[str], Optional[str]], subprocess.CompletedProcess[str]]


SKILL_ID = "cx.configure-price-quote.quoting.enable-fusion-asset-based-ordering"
TASK_CODE = "CUSTOM_ENABLE_FUSION_ASSET_BASED_ORDERING"
TASK_SKILL_ID = "cx.configure-price-quote.quoting.enable-fusion-asset-based-ordering"
PREVIEW_VERSION = "1.4"
# The CPQ approval binds this one Data Loader import. Adaptive Search and ESS
# require their own later approvals. Keep this lifetime in sync with the
# coordinator's CPQ approval window.
APPROVAL_TTL_SECONDS = 7200

_STAGE_LABELS = {
    "configure_fusion_abo_settings": "Configure CPQ Fusion ABO Settings",
    "save_fusion_abo_process": "Save CPQ Fusion ABO Standard Process",
    "enable_fusion_abo": "Enable CPQ Fusion ABO",
    "verify_fusion_abo_enabled": "Verify final CPQ Commerce Settings",
    "configure_abo_delta_action_library_function": (
        "Configure CPQ Fusion ABO Delta Action Library Function"
    ),
    "verify_abo_delta_action_library_function": (
        "Verify CPQ Fusion ABO Delta Action Library Function"
    ),
}

class CpqSettingsWriteExecutorError(CpqClientError):
    """Raised before a CPQ write when plan, target, or approval is unsafe."""


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _repo_resolved_path(path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else REPO_ROOT / path


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CpqSettingsWriteExecutorError(f"{field_name} must be an object.")
    return value


def _require_nonblank_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CpqSettingsWriteExecutorError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: str) -> datetime:
    rendered = _require_nonblank_string(value, "approval_issued_at")
    normalized = rendered[:-1] + "+00:00" if rendered.endswith("Z") else rendered
    try:
        timestamp = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise CpqSettingsWriteExecutorError("approval_issued_at must be an RFC 3339 timestamp.") from exc
    if timestamp.tzinfo is None:
        raise CpqSettingsWriteExecutorError("approval_issued_at must include a timezone.")
    return timestamp.astimezone(timezone.utc).replace(microsecond=0)


def _safe_environment_value(value: Any) -> str:
    environment = _require_nonblank_string(value, "environment")
    if len(environment) > 255 or any(character in environment for character in "\x00\r\n"):
        raise CpqSettingsWriteExecutorError("environment identity is malformed.")
    parsed = urlsplit(environment)
    if parsed.hostname:
        return parsed.hostname.lower()
    if any(character in environment for character in "/\\?#@"):
        raise CpqSettingsWriteExecutorError("environment identity is malformed.")
    return environment.lower()


def _safe_https_host(value: Any, field_name: str) -> str:
    """Return an HTTPS host identity without retaining a URL or credentials."""

    raw = _require_nonblank_string(value, field_name)
    parsed = urlsplit(raw)
    try:
        port = parsed.port
    except ValueError as exc:
        raise CpqSettingsWriteExecutorError(f"{field_name} has an invalid port.") from exc
    if parsed.scheme != "https" or not parsed.hostname:
        raise CpqSettingsWriteExecutorError(f"{field_name} must be an HTTPS URL with a host.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise CpqSettingsWriteExecutorError(
            f"{field_name} must not contain credentials, a query, or a fragment."
        )
    if port not in {None, 443}:
        raise CpqSettingsWriteExecutorError(f"{field_name} must use the default HTTPS port.")
    return parsed.hostname.lower()


def _safe_host_value(value: Any, field_name: str) -> str:
    """Validate a host stored in a sanitized preflight target record."""

    host = _require_nonblank_string(value, field_name).lower()
    if len(host) > 255 or any(character in host for character in "\x00\r\n/\\?#@:"):
        raise CpqSettingsWriteExecutorError(f"{field_name} is malformed.")
    return host


def build_target_identity(oauth_properties: Mapping[str, str]) -> dict[str, str]:
    """Return only non-secret Fusion/CPQ target identity for approval binding.

    Fusion feature-state evidence and CPQ settings changes are meaningful only
    when they refer to the same integrated site. The canonical ``restBaseUrl``
    is therefore the single target root; the CPQ ``/cpq`` context is derived
    from it by the shared transport.
    """

    scoped = build_cpq_oauth_properties(oauth_properties)
    cpq_base_url = validate_cpq_base_url(scoped["restBaseUrl"])
    cpq_host = urlsplit(cpq_base_url).hostname
    if not cpq_host:
        raise CpqSettingsWriteExecutorError("CPQ target host is unavailable.")
    fusion_host = _safe_https_host(scoped.get("restBaseUrl"), "restBaseUrl")
    return {
        "environment": _safe_environment_value(scoped.get("environment")),
        "fusion_host": fusion_host,
        "cpq_host": cpq_host.lower(),
    }


def _validate_preflight_target(
    preflight: Mapping[str, Any], expected_target: Mapping[str, str]
) -> None:
    """Require fresh Fusion evidence to be bound to the approved CPQ site."""

    target = _require_mapping(preflight.get("target"), "fusion_abo_preflight_result.target")
    actual = {
        "environment": _safe_environment_value(target.get("environment")),
        "fusion_host": _safe_host_value(target.get("fusion_host"), "preflight.target.fusion_host"),
        "cpq_host": _safe_host_value(target.get("cpq_host"), "preflight.target.cpq_host"),
    }
    if actual != dict(expected_target):
        raise CpqSettingsWriteExecutorError(
            "Fresh Fusion ABO preflight target does not match the CPQ target selected for this write."
        )


def _expected_library_function_readback() -> dict[str, str]:
    return {
        "type": CPQ_COMMERCE_SETTINGS_TYPE,
        "key": FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_KEY,
        "value": FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_VALUE,
    }


def _validate_exact_plan(
    plan: Mapping[str, Any],
    fusion_abo_preflight_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Require the supplied plan to exactly equal the canonical fresh plan."""

    try:
        expected_plan = build_fusion_abo_cpq_settings_write_plan(fusion_abo_preflight_result)
        legacy_plan = build_fusion_abo_cpq_settings_write_plan(
            fusion_abo_preflight_result, legacy_failure_guidance=True
        )
    except CpqSettingsWritePlanError as exc:
        raise CpqSettingsWriteExecutorError(str(exc)) from exc
    supplied_json = _canonical_json(plan)
    if supplied_json not in {
        _canonical_json(expected_plan), _canonical_json(legacy_plan)
    }:
        raise CpqSettingsWriteExecutorError(
            "CPQ Settings write plan is not the exact canonical plan for the supplied fresh preflight."
        )

    operations = plan.get("operations")
    if not isinstance(operations, list):
        raise CpqSettingsWriteExecutorError("CPQ Settings write plan must contain an ordered operation list.")
    for operation in operations:
        if not isinstance(operation, Mapping):
            raise CpqSettingsWriteExecutorError("CPQ Settings write plan contains an invalid operation.")
        if operation.get("operation_type") == "mutation":
            if (
                operation.get("execution_route") != "core.data-loader"
                or operation.get("business_object") != CPQ_COMMERCE_SETTINGS_BUSINESS_OBJECT
                or operation.get("rest_action") != "PATCH"
                or not (
                    isinstance(operation.get("setting"), Mapping)
                    or isinstance(operation.get("settings"), list)
                )
            ):
                raise CpqSettingsWriteExecutorError("CPQ Settings plan has an unsupported Data Loader mutation.")
    return expected_plan if supplied_json == _canonical_json(expected_plan) else legacy_plan


def _safe_preview_operations(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Expose the immutable effect for approval without any connection data."""

    operations = plan["operations"]
    result: list[dict[str, Any]] = []
    for operation in operations:
        item = {"id": operation["id"], "sequence": operation["sequence"]}
        if operation["operation_type"] == "mutation":
            item.update({
                "execution_route": operation["execution_route"],
                "business_object": operation["business_object"],
                "rest_action": operation["rest_action"],
            })
            if "settings" in operation:
                item["settings"] = operation["settings"]
            else:
                item["setting"] = operation["setting"]
        else:
            item.update({"method": operation["method"], "endpoint_path": operation["endpoint_path"]})
        if operation.get("method") == "GET" and "expected_setting" in operation:
            item["expected_setting"] = operation["expected_setting"]
        if operation.get("method") == "GET" and "expected_commerce_settings" in operation:
            item["expected_commerce_settings"] = operation["expected_commerce_settings"]
        result.append(item)
    return result


def _safe_preflight_summary(preflight: Mapping[str, Any], plan: Mapping[str, Any]) -> dict[str, Any]:
    cpq = _require_mapping(preflight.get("cpq_preflight"), "cpq_preflight")
    settings = _require_mapping(cpq.get("commerce_settings"), "cpq_preflight.commerce_settings")
    validation = _require_mapping(cpq.get("process_validation"), "cpq_preflight.process_validation")
    selection = _require_mapping(cpq.get("process_selection"), "cpq_preflight.process_selection")
    states = _require_mapping(preflight.get("feature_states"), "feature_states")
    result = {
        "standard_abo": settings.get("enable_standard_abo"),
        "fusion_abo": settings.get("enable_fusion_abo"),
        "fusion_abo_process_variable_name": settings.get(
            "fusion_abo_process_variable_name"
        ),
        "feature_states": {
            feature_code: states.get(feature_code)
            for feature_code in FUSION_ABO_PREREQUISITE_FEATURE_CODES
        },
        "process_validation": {
            "process_variable_name": validation.get("process_variable_name"),
            "exists": validation.get("exists"),
            "is_standard_process": validation.get("is_standard_process"),
            "process_type": validation.get("process_type"),
        },
        "process_selection": {
            "requested_process_variable_name": selection.get("requested_process_variable_name"),
            "resolved_process_variable_name": selection.get("resolved_process_variable_name"),
            "selection_source": selection.get("selection_source"),
            "requires_default_disclosure": selection.get("requires_default_disclosure"),
            "default_disclosure": selection.get("default_disclosure"),
        },
        "plan_version": plan.get("plan_version"),
    }
    library_function = cpq.get("abo_delta_action_library_function")
    if isinstance(library_function, Mapping):
        result["abo_delta_action_library_function"] = {
            "configured_function": library_function.get("configured_function"),
            "is_expected": library_function.get("is_expected"),
        }
    return result


def _approval_bound_preflight_context(
    preflight: Mapping[str, Any], plan: Mapping[str, Any]
) -> dict[str, Any]:
    """Return only the semantic preflight state that an approval must bind.

    Every fresh CPQ/Fusion GET can receive new request IDs, ECIDs, timestamps,
    or other transport metadata while the actual configuration state remains
    unchanged.  Those correlation values are valuable in the durable audit
    record, but including them in the approval fingerprint would make a
    correct fresh preflight look stale on every execution attempt.

    This deliberately includes only the required feature states, the relevant
    Fusion-ABO Commerce values, the verified process result, and the selected
    process/default disclosure. The caller separately binds the same-site
    target identity and the canonical fixed-operation plan.
    """

    summary = _safe_preflight_summary(preflight, plan)
    return {
        "status": _require_nonblank_string(preflight.get("status"), "preflight.status"),
        "feature_states": summary["feature_states"],
        "commerce_settings": {
            "enable_standard_abo": summary["standard_abo"],
            "enable_fusion_abo": summary["fusion_abo"],
            "fusion_abo_process_variable_name": summary[
                "fusion_abo_process_variable_name"
            ],
        },
        "process_validation": summary["process_validation"],
        "process_selection": summary["process_selection"],
        "abo_delta_action_library_function": summary.get(
            "abo_delta_action_library_function"
        ),
    }


def build_cpq_settings_write_preview(
    *,
    oauth_properties: Mapping[str, str],
    fusion_abo_preflight_result: Mapping[str, Any],
    plan: Mapping[str, Any],
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build a target-bound, immutable CPQ write preview without a network call."""

    preflight = _require_mapping(fusion_abo_preflight_result, "fusion_abo_preflight_result")
    target = build_target_identity(oauth_properties)
    _validate_preflight_target(preflight, target)
    canonical_plan = _validate_exact_plan(_require_mapping(plan, "plan"), preflight)
    issued = now or _utc_now()
    if issued.tzinfo is None:
        raise CpqSettingsWriteExecutorError("Preview time must include a timezone.")
    issued = issued.astimezone(timezone.utc).replace(microsecond=0)
    operations = _safe_preview_operations(canonical_plan)
    issued_at = _format_timestamp(issued)
    approval_context = {
        "task_code": TASK_CODE,
        "task_skill_id": TASK_SKILL_ID,
        "writer_skill_id": SKILL_ID,
        "target": target,
        # Hash only semantic state.  Fresh reads necessarily receive new
        # request/ECID values, which must remain audit evidence rather than
        # cause a valid approval to become stale.
        "preflight_fingerprint": _sha256(
            _approval_bound_preflight_context(preflight, canonical_plan)
        ),
        "plan_fingerprint": _sha256(canonical_plan),
        "validated_process_variable_name": canonical_plan["validated_process_variable_name"],
        "process_selection": canonical_plan["process_selection"],
        "preflight_summary": _safe_preflight_summary(preflight, canonical_plan),
        "operations": operations,
        # Bind the approval lifetime into the signed context.  Otherwise an
        # old preview fingerprint could be paired with a fabricated current
        # timestamp at execution time.
        "issued_at": issued_at,
    }
    return {
        "status": "approval_required",
        "preview_version": PREVIEW_VERSION,
        "task_code": TASK_CODE,
        "task_skill_id": TASK_SKILL_ID,
        "writer_skill_id": SKILL_ID,
        "target": target,
        "validated_process_variable_name": canonical_plan["validated_process_variable_name"],
        "process_selection": canonical_plan["process_selection"],
        "operations": operations,
        "preflight_fingerprint": approval_context["preflight_fingerprint"],
        "plan_fingerprint": approval_context["plan_fingerprint"],
        "approval_fingerprint": _sha256(approval_context),
        "issued_at": issued_at,
        "expires_at": _format_timestamp(issued + timedelta(seconds=APPROVAL_TTL_SECONDS)),
        "approval_required": {
            "timing": "immediately_before_execution",
            "instruction": (
                "Approve this exact target and "
                f"{len(operations)}-operation CPQ sequence before it is executed once."
            ),
        },
        "failure_policy": {
            "automatic_data_loader_retry": False,
            "automatic_rollback": False,
            "partial_failure_action": "Stop, persist sanitized evidence, and reconcile through approved reads. Request a new CPQ preview and approval only if another CPQ write is required.",
        },
    }


def _validate_current_approval(
    *,
    preview: Mapping[str, Any],
    approval_fingerprint: str,
    approval_issued_at: str,
    approval_confirmed: bool,
    now: datetime | None = None,
) -> None:
    if approval_confirmed is not True:
        raise CpqSettingsWriteExecutorError(
            "CPQ Settings write requires an explicit current approval confirmation."
        )
    supplied_fingerprint = _require_nonblank_string(approval_fingerprint, "approval_fingerprint")
    if supplied_fingerprint != preview.get("approval_fingerprint"):
        raise CpqSettingsWriteExecutorError(
            "The CPQ Settings write approval is stale or targets different current state."
        )
    issued = _parse_timestamp(approval_issued_at)
    if _format_timestamp(issued) != preview.get("issued_at"):
        raise CpqSettingsWriteExecutorError(
            "The CPQ Settings write approval timestamp does not match the approved preview."
        )
    current_time = (now or _utc_now()).astimezone(timezone.utc).replace(microsecond=0)
    if issued > current_time:
        raise CpqSettingsWriteExecutorError("approval_issued_at cannot be in the future.")
    if current_time - issued > timedelta(seconds=APPROVAL_TTL_SECONDS):
        raise CpqSettingsWriteExecutorError(
            "The CPQ Settings write approval has expired. Create and approve a new preview."
        )


def _safe_failure_diagnostic(error: Exception) -> dict[str, Any]:
    """Return only correlation-safe details needed for reconciliation."""

    if isinstance(error, CpqHttpError):
        result: dict[str, Any] = {
            "http_status": error.status_code,
            "method": error.method,
            "endpoint_path": error.path,
            "diagnostic_ids": dict(error.diagnostic_ids),
        }
        if error.provider_code:
            result["provider_error_code"] = error.provider_code
        if error.provider_message:
            result["provider_message"] = error.provider_message
        return result
    return {}


def _operation_record(
    operation_id: str,
    response: CpqResponse | None = None,
    error: Exception | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {"id": operation_id, "status": "attempted"}
    if response is not None:
        record.update({"status": "completed", **response.audit_summary()})
    if error is not None:
        record.update({"status": "failed", **_safe_failure_diagnostic(error)})
    return record


def _normalise_yes_no(value: Any) -> str | None:
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized == "yes":
            return "Yes"
        if normalized == "no":
            return "No"
    return None


def _verify_final_commerce_settings(payload: Mapping[str, Any], expected_process_name: str) -> None:
    settings = payload.get("commerceSettings")
    if not isinstance(settings, Mapping):
        raise CpqResponseError("CPQ final Commerce Settings readback is missing commerceSettings.")
    if _normalise_yes_no(settings.get("enableFusionABO")) != "Yes":
        raise CpqResponseError("CPQ final Commerce Settings readback did not confirm Fusion ABO is Yes.")
    if settings.get(FUSION_ABO_PROCESS_KEY) != expected_process_name:
        raise CpqResponseError(
            "CPQ final Commerce Settings readback did not retain the selected Standard Process."
        )


def _verify_abo_delta_action_library_function(payload: Mapping[str, Any]) -> None:
    """Require the exact direct CPQ Settings readback for the fixed function."""

    if payload.get("type") != CPQ_COMMERCE_SETTINGS_TYPE:
        raise CpqResponseError(
            "CPQ ABO Delta Action Library Function readback did not return Commerce setting type."
        )
    if payload.get("key") != FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_KEY:
        raise CpqResponseError(
            "CPQ ABO Delta Action Library Function readback returned an unexpected setting key."
        )
    if payload.get("value") != FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_VALUE:
        raise CpqResponseError(
            "CPQ ABO Delta Action Library Function readback did not retain the required fixed value."
        )


def _failure_class(error: Exception) -> str:
    if isinstance(error, CpqHttpError):
        return "cpq_api"
    if isinstance(error, CpqTransportError):
        return "transport_environment"
    if isinstance(error, CpqResponseError):
        return "cpq_api"
    if isinstance(error, CpqConfigurationError):
        return "auth_authz_or_configuration"
    return "execution_failure"


def _safe_failure_message(error: Exception, *, stage: str) -> str:
    stage_label = _STAGE_LABELS.get(stage, "CPQ Settings operation")
    if isinstance(error, CpqClientError):
        return f"{stage_label} failed: {error}"
    return f"{stage_label} failed: An unexpected local execution error occurred. No further CPQ operation was attempted."


def _safe_target_from_preview(preview: Mapping[str, Any]) -> dict[str, str]:
    target = _require_mapping(preview.get("target"), "preview.target")
    return {
        "environment": _require_nonblank_string(target.get("environment"), "preview.target.environment"),
        "fusion_host": _require_nonblank_string(target.get("fusion_host"), "preview.target.fusion_host"),
        "cpq_host": _require_nonblank_string(target.get("cpq_host"), "preview.target.cpq_host"),
    }


def _run_command(command: Sequence[str], stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, input=stdin, text=True, capture_output=True, check=False)


def _data_loader_text(value: Any, name: str) -> str:
    return _require_nonblank_string(value, name)


def _data_loader_mapping(value: Any, name: str) -> dict[str, Any]:
    return dict(_require_mapping(value, name))


def _data_loader_sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise CpqSettingsWriteExecutorError(f"Required immutable artifact is unavailable: {path.name}.") from exc
    return digest.hexdigest()


def _data_loader_write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _data_loader_read_json(path: Path, name: str) -> dict[str, Any]:
    try:
        return _data_loader_mapping(json.loads(path.read_text(encoding="utf-8")), name)
    except (OSError, json.JSONDecodeError) as exc:
        raise CpqSettingsWriteExecutorError(f"{name} is unavailable or invalid JSON.") from exc


def _data_loader_mutations(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    operations = plan.get("operations")
    if not isinstance(operations, list):
        raise CpqSettingsWriteExecutorError("CPQ Settings plan has no ordered operations.")
    mutations: list[dict[str, Any]] = []
    for operation in operations:
        if not isinstance(operation, Mapping) or operation.get("operation_type") != "mutation":
            continue
        operation_id = _data_loader_text(operation.get("id"), "CPQ setting operation id")
        if operation_id not in _DATA_LOADER_OPERATIONS or operation.get("execution_route") != "core.data-loader":
            raise CpqSettingsWriteExecutorError("CPQ Settings plan contains an unsupported Data Loader mutation.")
        raw_settings = operation.get("settings")
        if raw_settings is None:
            settings = [_data_loader_mapping(operation.get("setting"), "CPQ setting")]
        elif isinstance(raw_settings, list) and raw_settings:
            settings = [
                _data_loader_mapping(setting, f"CPQ setting {index}")
                for index, setting in enumerate(raw_settings, start=1)
            ]
        else:
            raise CpqSettingsWriteExecutorError(
                "CPQ Settings Data Loader mutation must contain one or more settings."
            )
        keys: list[str] = []
        for setting in settings:
            if setting.get("type") != CPQ_COMMERCE_SETTINGS_TYPE:
                raise CpqSettingsWriteExecutorError(
                    "CPQ Settings Data Loader mutation has an unsupported setting type."
                )
            keys.append(_data_loader_text(setting.get("key"), "CPQ setting key"))
        if len(set(keys)) != len(keys):
            raise CpqSettingsWriteExecutorError(
                "CPQ Settings Data Loader mutation contains duplicate setting keys."
            )
        mutations.append({"id": operation_id, "settings": settings})
    if not mutations:
        raise CpqSettingsWriteExecutorError("CPQ Settings plan contains no Data Loader mutation.")
    return mutations


def _data_loader_subject(
    operation_id: str, settings: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    return {
        "business_object": CPQ_COMMERCE_SETTINGS_BUSINESS_OBJECT,
        "operation_id": operation_id,
        "rest_action": "PATCH",
        "items": [dict(setting) for setting in settings],
    }


def _data_loader_subject_sha256(subject: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(subject).encode("utf-8")).hexdigest()


def _mutation_contains_setting(mutation: Mapping[str, Any], key: str) -> bool:
    settings = mutation.get("settings")
    return isinstance(settings, list) and any(
        isinstance(setting, Mapping) and setting.get("key") == key
        for setting in settings
    )


def prepare_cpq_settings_data_loader_loads(
    *, plan: Mapping[str, Any], target: Mapping[str, Any], project_root: Path, properties: Path,
    token_cache: str | None = None, runner: CommandRunner = _run_command,
) -> dict[str, dict[str, Any]]:
    """Prepare exact workbook inputs; the core.data-loader skill generates XLSX."""
    if not project_root.is_dir():
        raise CpqSettingsWriteExecutorError("The selected project workspace does not exist.")
    loads = {}
    work_root = project_root / "artifacts" / "pillars" / "cx" / "configure-price-quote" / "quoting" / "enable-fusion-asset-based-ordering" / "current" / "cpq-settings-data-loader" / f"sample-{uuid.uuid4().hex}"
    for mutation in _data_loader_mutations(plan):
        operation_id, settings = mutation["id"], mutation["settings"]
        group_key = _data_loader_text(settings[0].get("key"), "CPQ setting key")
        work = work_root / operation_id
        work.mkdir(parents=True, exist_ok=True)
        values_path = work / "values.json"
        _data_loader_write_json(values_path, {
            CPQ_COMMERCE_SETTINGS_BUSINESS_OBJECT: [{"cpqCommerceSettingKey": group_key, "RestAction": "PATCH", "Accept": "application/json", "Content-Type": "application/json"}],
            "Items": [{"cpqCommerceSettingKey": group_key, "RestAction": "PATCH", **setting} for setting in settings],
        })
        handoff_id = "dlh_" + uuid.uuid4().hex
        loads[operation_id] = {
            "business_object": CPQ_COMMERCE_SETTINGS_BUSINESS_OBJECT,
            "target": dict(target),
            "approved_subject": _data_loader_subject(operation_id, settings),
            "workbook_handoff": {
                "handoff_version": DATA_LOADER_HANDOFF_VERSION, "handoff_id": handoff_id,
                "kind": "generate_populated_workbook",
                "business_object": CPQ_COMMERCE_SETTINGS_BUSINESS_OBJECT,
                "values_json_path": str(values_path), "output_directory": str(work),
                "authentication_reference": {"properties": str(properties),
                    **({"token_cache": token_cache} if token_cache else {})},
            },
        }
    return loads


def _data_loader_task_context(project_root: Path) -> tuple[Path, str, int]:
    path = project_root / "artifacts" / "shared" / "runbook" / "current" / "task-context.json"
    context = _data_loader_read_json(path, "Run Book task context")
    matches = [task for task in context.get("tasks", []) if isinstance(task, Mapping)
               and task.get("task_name") == "Enable Fusion Asset-Based Ordering"]
    if (len(matches) != 1 or isinstance(matches[0].get("sequence"), bool)
            or not isinstance(matches[0].get("sequence"), int) or matches[0]["sequence"] < 1):
        raise CpqSettingsWriteExecutorError("Run Book must contain one positive-sequenced Enable Fusion Asset-Based Ordering task.")
    return path, "Enable Fusion Asset-Based Ordering", matches[0]["sequence"]


def data_loader_preflight_handoff(source: Path, business_object: str, project_root: Path,
                                  properties: Path, token_cache: str | None = None,
                                  *, handoff_id: str) -> dict[str, Any]:
    """Describe the 26.10 Core preflight/Task Hook route without invoking it."""
    context, _, _ = _data_loader_task_context(project_root)
    guard_scripts = str(REPO_ROOT / "core/runbook/scripts")
    if guard_scripts not in sys.path:
        sys.path.insert(0, guard_scripts)
    from runbook_guard import runbook_from_task_context
    binding = runbook_from_task_context(context)
    run_config = source.parent / f"runbook-id-{uuid.uuid4().hex}.properties"
    descriptor = os.open(run_config, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        stream.write(f"runID={binding['workerJourneyId']}\n")
    return {
        "handoff_version": DATA_LOADER_HANDOFF_VERSION, "handoff_id": handoff_id,
        "kind": "prepare_persisted_load", "source_path": str(source),
        "business_object": business_object, "project_root": str(project_root),
        "task_context": str(context), "task_name": "Enable Fusion Asset-Based Ordering",
        "sequence": _data_loader_task_context(project_root)[2],
        "preflight_envelope_output": str(source.parent / "preflight-envelope.json"),
        "run_config": str(run_config),
        "authentication_reference": {"properties": str(properties),
            **({"token_cache": token_cache} if token_cache else {})},
    }


def accept_workbook_result(load: Mapping[str, Any], result: Mapping[str, Any], *,
                           project_root: Path, properties: Path,
                           token_cache: str | None = None) -> dict[str, Any]:
    handoff = _data_loader_mapping(load.get("workbook_handoff"), "workbook handoff")
    if (result.get("handoff_version") != DATA_LOADER_HANDOFF_VERSION
            or result.get("handoff_id") != handoff.get("handoff_id")
            or result.get("status") != "generated"):
        raise CpqSettingsWriteExecutorError("Workbook result does not match the current Core handoff.")
    output = Path(_data_loader_text(handoff.get("output_directory"), "workbook output directory")).resolve()
    source = Path(_data_loader_text(result.get("workbook_path"), "generated workbook path")).resolve()
    try:
        source.relative_to(output)
        source.relative_to(project_root.resolve())
    except ValueError as exc:
        raise CpqSettingsWriteExecutorError("Generated workbook is outside the approved project output directory.") from exc
    candidates = sorted(path.resolve() for path in output.glob("*.xlsx")
                        if not path.name.endswith(("_attribute-details.xlsx", "_key-fields.xlsx")))
    if source.suffix.lower() != ".xlsx" or not source.is_file() or candidates != [source]:
        raise CpqSettingsWriteExecutorError("Core must return exactly one available CPQ Settings workbook.")
    accepted = dict(load)
    accepted["source_path"] = str(source)
    accepted["preflight_handoff"] = data_loader_preflight_handoff(
        source, load["business_object"], project_root, properties, token_cache,
        handoff_id=handoff["handoff_id"])
    return accepted


def initiation_correlation(markdown: str) -> dict[str, str]:
    """Accept one canonical Core receipt; an exit code alone is not correlation."""
    matches = re.findall(r"\|\s*Content ID\s*\(Request ID\)\s*\|\s*(UCMFA[0-9]+)\s*\(([1-9][0-9]*)\)\s*\|", markdown)
    if len(matches) != 1:
        raise CpqSettingsWriteExecutorError("Submission correlation is missing or ambiguous; reconcile without resubmitting.")
    return {"content_id": matches[0][0], "request_id": matches[0][1]}


def prepare_persisted_load(
    core_result: Mapping[str, Any], *, handoff: Mapping[str, Any],
    workbook_source: Path, workbook_project_root: Path,
    target: Mapping[str, Any], scope: Mapping[str, Any], workflow_id: str,
) -> dict[str, Any]:
    """Accept a Core-owned 26.10 preflight and Task Hook preview."""
    root = workbook_project_root.resolve(strict=True)
    source = _artifact_inside(workbook_source, root)
    if (core_result.get("handoff_version") != DATA_LOADER_HANDOFF_VERSION
            or core_result.get("handoff_id") != handoff.get("handoff_id")
            or core_result.get("status") != "approval_required"
            or Path(str(core_result.get("source_path", ""))).resolve() != source
            or handoff.get("kind") != "prepare_persisted_load"):
        raise CpqSettingsWriteExecutorError("Core preflight result does not match this workbook handoff.")
    if not re.fullmatch(r"[a-f0-9]{64}", workflow_id):
        raise CpqSettingsWriteExecutorError("An exact workflow identity is required.")
    path = source.parent / "prepared-load.json"
    if path.exists():
        raise CpqSettingsWriteExecutorError("This load is already prepared; resume its saved approval.")
    expected_preflight = Path(_data_loader_text(handoff.get("preflight_envelope_output"), "Core preflight path"))
    preflight_path = _artifact_inside(core_result.get("preflight_path"), root)
    if preflight_path != expected_preflight.resolve():
        raise CpqSettingsWriteExecutorError("Core returned a preflight outside this handoff.")
    preflight = _data_loader_mapping(_data_loader_read_json(preflight_path, "Core preflight").get("preflight"), "Core preflight")
    archive = _artifact_inside(preflight.get("approvedArtifactPath", ""), root)
    if _data_loader_sha256_file(archive) != preflight.get("archiveSha256"):
        raise CpqSettingsWriteExecutorError("Core's immutable archive is missing or changed.")
    context, task_name, sequence = _data_loader_task_context(root)
    if (context.resolve() != Path(str(handoff.get("task_context", ""))).resolve()
            or task_name != handoff.get("task_name")
            or sequence != handoff.get("sequence")):
        raise CpqSettingsWriteExecutorError("Run Book context changed after the Core handoff.")
    validation = _data_loader_mapping(core_result.get("task_validation"), "Core Task Hook validation")
    if validation.get("taskValidationStatus") not in {"ready", "skipped"}:
        raise CpqSettingsWriteExecutorError("Core Task Hook validation is not ready.")
    final_data = {"archiveSha256": preflight["archiveSha256"],
        "sourceSha256": _data_loader_sha256_file(source),
        "projectId": root.name, "target": dict(target), "workflowId": workflow_id,
        "approvedSubject": dict(scope)}
    preview_path = _artifact_inside(core_result.get("task_preview_path"), root)
    preview = _data_loader_read_json(preview_path, "Core Task Hook preview")
    if preview.get("finalData") != final_data:
        raise CpqSettingsWriteExecutorError("Core Task Hook preview changed the validated approval scope.")
    markdown = _data_loader_text(core_result.get("core_approval_markdown"), "Core approval report")
    record = {"schema_version": DATA_LOADER_HANDOFF_VERSION, "state": "awaiting_approval",
        "handoff_id": handoff["handoff_id"], "project_root": str(root),
        "target": dict(target), "scope": dict(scope), "workflow_id": workflow_id,
        "source_path": str(source), "source_sha256": final_data["sourceSha256"],
        "archive_path": str(archive), "archive_sha256": preflight["archiveSha256"],
        "preflight_path": str(preflight_path), "preflight_sha256": _data_loader_sha256_file(preflight_path),
        "task_context": str(context), "task_context_sha256": _data_loader_sha256_file(context),
        "task_name": task_name, "sequence": sequence, "task_validation": validation,
        "preview_path": str(preview_path), "preview_sha256": _data_loader_sha256_file(preview_path),
        "final_data": final_data, "core_approval_markdown": markdown,
        "run_config": handoff["run_config"]}
    _data_loader_write_json(path, record)
    from abo_presentation import render_workbook_access
    try:
        access = render_workbook_access(source, project_root=root)
    except (ValueError, OSError, RuntimeError):
        access = "The generated workbook link is unavailable. The validated load is unchanged.\n"
    return {"state": "awaiting_approval", "submissionStarted": False,
            "prepared_load_record": str(path), "workbook_access": access,
            "preview_sha256": record["preview_sha256"],
            "data_loader_markdown": markdown}



def prepare_cpq_task_hook_previews(**kwargs):
    raise CpqSettingsWriteExecutorError("Saved Task Hook approvals are retired; use prepare-cpq-load.")


def _submit_data_loader_setting(**kwargs):
    raise CpqSettingsWriteExecutorError("The legacy direct submit route is retired; use the prepared Core load approval route.")


def verify_cpq_settings_after_load(*, plan: Mapping[str, Any], oauth_properties: Mapping[str, str],
                                   submission: Mapping[str, Any], token_cache=None, timeout=60,
                                   oauth_options=None, transport=None) -> dict[str, Any]:
    """Read back business state only after the exact request was checked successfully."""
    if submission.get("data_loader_status") != "SUCCEEDED":
        raise CpqSettingsWriteExecutorError("Exact CPQ load success is required before readback.")
    connection = transport or CpqOAuthTransport(oauth_properties, token_cache=token_cache,
                                                timeout=timeout, oauth_options=oauth_options)
    expected = validate_cpq_base_url(build_cpq_oauth_properties(oauth_properties)["restBaseUrl"])
    if connection.base_url != expected:
        raise CpqSettingsWriteExecutorError("CPQ readback target differs from the selected workflow.")
    process_name = plan["validated_process_variable_name"]
    connection.ensure_authenticated()
    # Always check process/enablement too, including function-only recovery.
    response = connection.get_json(CPQ_COMMERCE_SETTINGS_PATH)
    _verify_final_commerce_settings(response.payload, process_name)
    operations = [dict(submission), _operation_record("verify_fusion_abo_enabled", response)]
    response = connection.get_json(CPQ_FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_PATH)
    _verify_abo_delta_action_library_function(response.payload)
    operations.append(_operation_record("verify_abo_delta_action_library_function", response))
    return {"status": "completed", "validated_process_variable_name": process_name,
            "write_scope": plan.get("write_scope"), "completed_operations": operations}


def execute_approved_cpq_settings_write(
    *,
    oauth_properties: Mapping[str, str],
    fusion_abo_preflight_result: Mapping[str, Any],
    plan: Mapping[str, Any],
    approval_fingerprint: str,
    approval_issued_at: str,
    approval_confirmed: bool,
    token_cache: str | None = None,
    timeout: int = 60,
    oauth_options: OAuthOptions | None = None,
    transport: CpqOAuthTransport | None = None,
    now: datetime | None = None,
    prepared_loads: Mapping[str, Any] | None = None,
    workflow_preview: Mapping[str, Any] | None = None,
    approval_record_ref: str | None = None,
    approval_record_fingerprint: str | None = None,
    project_root: Path | None = None,
    properties: Path | None = None,
    fusion_token_cache: str | None = None,
    data_loader_wait_seconds: int = 15 * 60,
    data_loader_poll_seconds: int = 15,
    runner: CommandRunner = _run_command,
) -> dict[str, Any]:
    """Legacy saved approvals cannot authorize a new load."""
    raise CpqSettingsWriteExecutorError("Saved CPQ approvals are retired; use prepare-cpq-load.")


def _read_json_object(path_value: str, field_name: str) -> dict[str, Any]:
    path = Path(path_value)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CpqSettingsWriteExecutorError(f"Unable to read {field_name} file.") from exc
    except json.JSONDecodeError as exc:
        raise CpqSettingsWriteExecutorError(f"{field_name} file is not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise CpqSettingsWriteExecutorError(f"{field_name} file must contain a JSON object.")
    return payload


def _read_oauth_properties(path_value: str) -> dict[str, str]:
    """Read a local profile without surfacing malformed secret-bearing lines."""

    try:
        return read_properties(Path(path_value))
    except (OSError, ValueError) as exc:
        raise CpqSettingsWriteExecutorError("Unable to read the local CPQ OAuth properties file.") from exc


def _write_json(path_value: str | None, payload: Mapping[str, Any]) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if path_value:
        path = Path(path_value)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {path}")
    print(rendered)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a target-bound preview for the fixed Fusion ABO CPQ Settings write sequence. "
            "This core command never contacts CPQ; live execution is owned by the governed pillar coordinator."
        )
    )
    parser.add_argument("--preflight-result", required=True, help="Fresh sanitized Fusion ABO preflight JSON.")
    parser.add_argument("--properties", required=True, help="Private, gitignored CPQ OAuth properties file.")
    parser.add_argument("--output", help="Optional local path for the sanitized preview JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    preflight = _read_json_object(args.preflight_result, "preflight result")
    try:
        plan = build_fusion_abo_cpq_settings_write_plan(preflight)
    except CpqSettingsWritePlanError as exc:
        raise CpqSettingsWriteExecutorError(str(exc)) from exc
    preview = build_cpq_settings_write_preview(
        oauth_properties=_read_oauth_properties(args.properties),
        fusion_abo_preflight_result=preflight,
        plan=plan,
    )
    _write_json(args.output, preview)
    return 0



def _artifact_inside(path: Any, root: Path) -> Path:
    try:
        resolved = Path(path).resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
        if not resolved.is_file():
            raise ValueError()
        return resolved
    except (TypeError, ValueError, OSError) as exc:
        raise CpqSettingsWriteExecutorError("The selected project artifact is missing or outside the project.") from exc


def load_persisted_load(path: Path, *, project_root: Path, workflow_id: str, target: Mapping[str, Any]) -> dict[str, Any]:
    path = _artifact_inside(path, project_root)
    record = _data_loader_read_json(path, "prepared load")
    if (record.get("schema_version") != "26.10.1" or record.get("project_root") != str(project_root.resolve())
            or record.get("workflow_id") != workflow_id or record.get("target") != dict(target)):
        raise CpqSettingsWriteExecutorError("Prepared load does not match the exact project, workflow and target.")
    for key, hash_key in (("archive_path", "archive_sha256"), ("preflight_path", "preflight_sha256"),
                          ("task_context", "task_context_sha256")):
        # Core consumes the preflight envelope after a successful upload. Its
        # absence is then expected; it must exist for any pending approval.
        if (key == "preflight_path" and record.get("state") in {"possibly_submitted", "submitted"}
                and not Path(record[key]).exists()):
            continue
        if _data_loader_sha256_file(_artifact_inside(record[key], project_root)) != record[hash_key]:
            raise CpqSettingsWriteExecutorError("A validated artifact or Run Book context changed; obtain fresh validation and approval.")
    return record


def build_persisted_load_preview(*args, **kwargs):
    raise CpqSettingsWriteExecutorError(
        "Core owns Task Hook preview construction; return its bound preflight result.")


def submit_persisted_load(path: Path, *, project_root: Path, workflow_id: str,
                          target: Mapping[str, Any], explicit_approval: bool,
                          preview_sha256: str, before_submit: Callable[[], None],
                          properties: Path, token_cache: str | None = None) -> dict[str, Any]:
    """Reserve one approved 26.10 Core load and return its execution handoff."""
    record = load_persisted_load(path, project_root=project_root, workflow_id=workflow_id, target=target)
    if explicit_approval is not True or record["state"] != "awaiting_approval":
        raise CpqSettingsWriteExecutorError("A later explicit approval of this exact load is required.")
    preview_path = _artifact_inside(record["preview_path"], project_root)
    if preview_sha256 != record["preview_sha256"] or _data_loader_sha256_file(preview_path) != preview_sha256:
        raise CpqSettingsWriteExecutorError("The approved preview is missing or changed.")
    preview = _data_loader_read_json(preview_path, "approved Core preview")
    if preview.get("finalData") != record["final_data"]:
        raise CpqSettingsWriteExecutorError("The displayed scope differs from the approved load.")
    try:
        issued = datetime.fromisoformat(str(preview["generatedAt"]).replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - issued).total_seconds()
    except (KeyError, ValueError, TypeError) as exc:
        raise CpqSettingsWriteExecutorError("The load preview timestamp is invalid.") from exc
    if not 0 <= age <= 1800:
        raise CpqSettingsWriteExecutorError("The load preview expired; obtain fresh validation and approval.")
    intent = path.parent / "submission-intent.json"
    descriptor = os.open(intent, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        json.dump({"workflow_id": workflow_id, "state": "possibly_submitted",
                   "handoff_id": record["handoff_id"]}, stream)
        stream.flush()
        os.fsync(stream.fileno())
    record["state"] = "possibly_submitted"
    _data_loader_write_json(path, record)
    before_submit()
    return {"state": "handoff_required", "submissionStarted": False,
        "core_data_loader_handoff": {
            "handoff_version": DATA_LOADER_HANDOFF_VERSION,
            "handoff_id": record["handoff_id"], "kind": "submit_approved_persisted_load",
            "preflight_path": record["preflight_path"], "task_preview_path": record["preview_path"],
            "archive_path": record["archive_path"], "run_config": record["run_config"],
            "task_context": record["task_context"], "task_name": record["task_name"],
            "sequence": record["sequence"], "authentication_reference": {
                "properties": str(properties),
                **({"token_cache": token_cache} if token_cache else {})},
        }}


def complete_persisted_load(path: Path, core_result: Mapping[str, Any], *,
                            project_root: Path, workflow_id: str,
                            target: Mapping[str, Any]) -> dict[str, Any]:
    """Accept only a correlated Core submission receipt after local reservation."""
    record = load_persisted_load(path, project_root=project_root, workflow_id=workflow_id, target=target)
    if (record["state"] != "possibly_submitted"
            or core_result.get("handoff_version") != DATA_LOADER_HANDOFF_VERSION
            or core_result.get("handoff_id") != record.get("handoff_id")):
        raise CpqSettingsWriteExecutorError("Core submission result does not match the reserved load.")
    if core_result.get("state") != "success" or core_result.get("submission_started") is not True:
        raise CpqSettingsWriteExecutorError(
            "Submission failed or is uncertain; reconcile the reserved load without retrying.")
    content_id = _data_loader_text(core_result.get("content_id"), "Data Loader Content ID")
    request_id = _data_loader_text(core_result.get("request_id"), "Data Loader Request ID")
    if not re.fullmatch(r"UCMFA[0-9]+", content_id) or not re.fullmatch(r"[1-9][0-9]*", request_id):
        raise CpqSettingsWriteExecutorError("Confirmed Core submission correlation is malformed.")
    markdown = _data_loader_text(core_result.get("markdown"), "Core submission receipt")
    if initiation_correlation(markdown) != {"content_id": content_id, "request_id": request_id}:
        raise CpqSettingsWriteExecutorError("Core receipt and structured correlation differ.")
    correlation = {"content_id": content_id, "request_id": request_id}
    record.update({"state": "submitted", "submission": correlation})
    _data_loader_write_json(path, record)
    return {"state": "success", "submissionStarted": True, **correlation, "markdown": markdown}


def data_loader_status_handoff(*, request_id: str, target: Mapping[str, Any],
                               output_directory: Path, properties: Path,
                               token_cache: str | None = None) -> dict[str, Any]:
    if not re.fullmatch(r"[1-9][0-9]*", request_id):
        raise CpqSettingsWriteExecutorError("Data Loader Request ID is malformed.")
    return {"handoff_version": DATA_LOADER_HANDOFF_VERSION,
            "handoff_id": "dls_" + uuid.uuid4().hex, "kind": "data_load_status",
            "request_id": request_id, "target": dict(target),
            "diagnostic_output_directory": str(output_directory),
            "authentication_reference": {"properties": str(properties),
                **({"token_cache": token_cache} if token_cache else {})}}


def validate_data_loader_status_result(result: Mapping[str, Any],
                                       handoff: Mapping[str, Any]) -> dict[str, Any]:
    if (result.get("handoff_version") != DATA_LOADER_HANDOFF_VERSION
            or result.get("handoff_id") != handoff.get("handoff_id")
            or str(result.get("request_id")) != str(handoff.get("request_id"))):
        raise CpqSettingsWriteExecutorError("Data Loader status result does not match the current handoff.")
    state = _data_loader_text(result.get("status"), "Data Loader status").upper()
    if state not in {"SUCCEEDED", "PENDING", "FAILED", "INDETERMINATE"}:
        raise CpqSettingsWriteExecutorError("Data Loader status result is unsupported.")
    return {"status": state, "markdown": str(result.get("markdown") or ""),
            "counts": dict(result.get("counts") or {})}


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CpqSettingsWriteExecutorError, CpqSettingsWritePlanError, CpqClientError) as exc:
        print(json.dumps({"status": "failed", "message": str(exc)}), file=sys.stderr)
        raise SystemExit(1)
