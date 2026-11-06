#!/usr/bin/env python3
"""Coordinate the governed Enable Fusion Asset-Based Ordering workflow.

The script intentionally owns task ordering only.  It reuses:

* task-local CPQ settings validation over the local CPQ REST client;
* the task-local ``feature_states_reader`` for the authoritative Fusion state read;
* ``shared...fsm-set-optin-features`` for a separately approved Fusion opt-in
  update; and
* the task-local, fixed CPQ Settings plan and executor;
* ``cx.sales.sales-foundation.configure-adaptive-search`` for its own approved
  selective publish and exact-job status evidence; and
* ``core.fusion-api.ess-job-submitter`` for the conditional Unified Asset Read
  Model Sync submission after that skill returns successful final evidence.

The coordinator never constructs a raw CPQ REST request.  It owns the task
ordering, fresh preflight, exact approval gate, and durable sanitized project
record; the task-local executor owns the allowlisted CPQ mutation sequence and
reuses the canonical core transport.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Sequence
from urllib.parse import urlsplit

try:
    import fcntl
except ImportError:  # pragma: no cover - this governed local runtime requires POSIX file locks.
    fcntl = None


TASK_CODE = "CUSTOM_ENABLE_FUSION_ASSET_BASED_ORDERING"
TASK_NAME = "Enable Fusion Asset-Based Ordering"
SHARED_OPTIN_SKILL_ID = "shared.implementation-planning.fsm-set-optin.fsm-set-optin-features"
DEFAULT_FUSION_TOKEN_CACHE = "auto"
DEFAULT_BOSS_TOKEN_CACHE = "auto"
DEFAULT_FUSION_COMMON_TOKEN_CACHE = "auto"
DEFAULT_CPQ_TOKEN_CACHE = "auto"

ADAPTIVE_SEARCH_SKILL_ID = "cx.sales.sales-foundation.configure-adaptive-search"
ADAPTIVE_SEARCH_TASK_CODE = "ORA_CONFIGURE_ELASTIC_SEARCHES"
ADAPTIVE_SEARCH_REQUIRED_ENTITIES = ("ConsolidatedAsset", "SerializedAsset")
ADAPTIVE_SEARCH_WORKFLOW_SCOPE = "fusion_abo_adaptive_search_v1"
ADAPTIVE_SEARCH_DEFAULT_WAIT_SECONDS = 75 * 60
ADAPTIVE_SEARCH_DEFAULT_POLL_INTERVAL_SECONDS = 15
ADAPTIVE_SEARCH_MAX_CONSECUTIVE_READ_FAILURES = 3
ADAPTIVE_SEARCH_AUTH_FAILURE_CLASSES = frozenset({
    "auth_expired_or_invalid", "authorization_or_privilege",
})
ADAPTIVE_SEARCH_STATUS_READ_FAILURE_STAGES = frozenset({
    "adaptive_publish_status_readback", "adaptive_search_status_readback",
})
ESS_DEFAULT_WAIT_SECONDS = 15 * 60
ESS_DEFAULT_POLL_INTERVAL_SECONDS = 15
ESS_SYNC_TASK_CODE = "FUSION_ABO_UNIFIED_ASSET_READ_MODEL_SYNC"
ESS_SYNC_TASK_NAME = "Unified Asset Read Model Sync"


def find_repo_root(start: Path) -> Path:
    """Locate the repository root without depending on the working directory."""

    for candidate in (start, *start.parents):
        if (candidate / "core" / "fusion-api" / "rest-api-client" / "scripts").is_dir():
            return candidate
        if (
            candidate / "fdos" / "core" / "fusion-api" / "rest-api-client" / "scripts"
        ).is_dir():
            return candidate / "fdos"
    raise RuntimeError("Could not locate the FSCR repository root.")


REPO_ROOT = find_repo_root(Path(__file__).resolve())
TASK_SCRIPTS = Path(__file__).resolve().parent
CPQ_REST_SCRIPTS = TASK_SCRIPTS
PROJECT_MGMT_SCRIPTS = REPO_ROOT / "core" / "project-mgmt" / "scripts"
SHARED_OPTIN_WRAPPER = (
    REPO_ROOT
    / "shared"
    / "implementation-planning"
    / "fsm-set-optin"
    / "fsm-set-optin-features"
    / "scripts"
    / "set_optin_feature.py"
)
ADAPTIVE_SEARCH_EXECUTOR = (
    REPO_ROOT
    / "pillars"
    / "cx"
    / "sales"
    / "sales-foundation"
    / "configure-adaptive-search"
    / "scripts"
    / "adaptive_publish_executor.py"
)
ESS_ABO_ADAPTER = TASK_SCRIPTS / "fusion_abo_ess_adapter.py"
for script_path in (
    TASK_SCRIPTS,
    CPQ_REST_SCRIPTS,
    PROJECT_MGMT_SCRIPTS,
):
    sys.path.insert(0, str(script_path))

from cpq_rest_service import (  # noqa: E402
    CpqClientError,
    CpqRestClient,
    OAuthOptions as CpqReadOAuthOptions,
)
from cpq_settings_client import (  # noqa: E402
    CpqSettingsClient,
    CpqSettingsError,
    build_prerequisite_update_handoff,
    classify_fusion_abo_preflight,
    normalize_fusion_abo_feature_states,
)
from cpq_settings_write_executor import (  # noqa: E402
    CpqSettingsWriteExecutorError,
    OAuthOptions as CpqOAuthOptions,
    build_cpq_settings_write_preview,
    execute_approved_cpq_settings_write,
    prepare_cpq_settings_data_loader_loads,
    prepare_cpq_task_hook_previews,
)
from cpq_settings_write_plan import (  # noqa: E402
    CPQ_COMMERCE_SETTINGS_BUSINESS_OBJECT,
    CpqSettingsWritePlanError,
    build_fusion_abo_cpq_settings_write_plan,
)
from fusion_abo_prerequisites import (  # noqa: E402
    CPQ_ABO_PREREQUISITE_FEATURE_CODES,
    FUSION_ABO_PREREQUISITE_FEATURE_CODES,
    SUBSCRIPTION_COVERAGE_PREREQUISITE_FEATURE_CODES,
)
from feature_states_reader import (  # noqa: E402
    FeatureStatesError,
    FeatureStatesReader,
    OAuthOptions as FusionOAuthOptions,
    rest_client_common,
)
from token_usage_logger import append_token_usage_log, estimate_path_tokens  # noqa: E402


class FusionAboWorkflowError(RuntimeError):
    """Raised when a task-local workflow precondition is missing or unsafe."""


TASK_SKILL_ID = "cx.configure-price-quote.quoting.enable-fusion-asset-based-ordering"
PROJECT_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
TASK_ARTIFACT_DIRECTORY = Path(
    "artifacts/pillars/cx/configure-price-quote/quoting/enable-fusion-asset-based-ordering/current"
)
TOKEN_ESTIMATION_METHOD = "chars/4 estimate"
SENSITIVE_FIELD_NAMES = frozenset(
    {
        "access_token",
        "authorization",
        "authorization_header",
        "auth_code",
        "client_secret",
        "code_verifier",
        "password",
        "properties",
        "properties_path",
        "refresh_token",
        "secret",
        "token_cache",
        "token_cache_path",
    }
)
SAFE_PROVIDER_MESSAGE_MAX_LENGTH = 512
SAFE_PROVIDER_CODE_PATTERN = re.compile(
    r"^(?:[A-Za-z][A-Za-z0-9_.:-]{1,95}|[0-9]{1,96})$"
)
SAFE_PROVIDER_CORRELATION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{1,256}$")
ORACLE_ERROR_DETAIL_LIMIT = 5
ORACLE_ERROR_PRIMARY_MESSAGE_FIELDS = ("message", "detail", "Error")
ORACLE_ERROR_FALLBACK_MESSAGE_FIELDS = ("title",)
ORACLE_ERROR_CODE_FIELDS = ("o:errorCode", "errorCode", "code")
SAFE_PROVIDER_CORRELATION_ID_NAMES = frozenset(
    {
        "ecid",
        "opc-request-id",
        "request-id",
        "x-request-id",
        "x-oracle-request-id",
        "x-oracle-dms-ecid",
    }
)
_SENSITIVE_PROVIDER_TEXT_PATTERN = re.compile(
    r"(?i)\b(authorization|access[_-]?token|refresh[_-]?token|client[_-]?secret|password)"
    r"\s*[:=]\s*[^,;\s]+"
)
_BEARER_PROVIDER_TEXT_PATTERN = re.compile(r"(?i)\b(bearer|basic)\s+[A-Za-z0-9._~+/=-]+")


def _safe_provider_text(value: Any) -> str | None:
    """Return one bounded, presentation-safe Oracle business message.

    Core adapters must already parse an allowlisted provider field before this
    coordinator sees it.  This second small guard protects the durable task
    artifact boundary from accidental tokens, markup, line-oriented payloads,
    or arbitrary provider fields.
    """

    if not isinstance(value, str):
        return None
    rendered = " ".join(value.split())
    if not rendered or "<" in rendered or ">" in rendered:
        return None
    rendered = _SENSITIVE_PROVIDER_TEXT_PATTERN.sub(r"\1=[REDACTED]", rendered)
    rendered = _BEARER_PROVIDER_TEXT_PATTERN.sub(r"\1 [REDACTED]", rendered)
    return rendered[:SAFE_PROVIDER_MESSAGE_MAX_LENGTH]


def _safe_provider_code(value: Any) -> str | None:
    """Return one bounded symbolic or numeric Oracle provider code."""

    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not SAFE_PROVIDER_CODE_PATTERN.fullmatch(normalized):
        return None
    return normalized


def _safe_oracle_error_context(payload: Mapping[str, Any]) -> dict[str, str]:
    """Extract allowlisted Oracle business-error fields without retaining a body.

    Oracle services can use either a top-level ``Error`` field or an
    ``o:errorDetails`` array rather than the ordinary REST error shape. Only
    named scalar message/code fields from at most a few detail entries are
    eligible for durable diagnostics; arbitrary nested data is ignored.
    """

    def first_message(
        source: Mapping[str, Any], *, include_fallback_fields: bool = False
    ) -> str | None:
        fields = ORACLE_ERROR_PRIMARY_MESSAGE_FIELDS
        if include_fallback_fields:
            fields = (*fields, *ORACLE_ERROR_FALLBACK_MESSAGE_FIELDS)
        for field in fields:
            message = _safe_provider_text(source.get(field))
            if message:
                return message
        return None

    def first_code(source: Mapping[str, Any]) -> str | None:
        for field in ORACLE_ERROR_CODE_FIELDS:
            code = _safe_provider_code(source.get(field))
            if code:
                return code
        return None

    # ``title`` is commonly a generic HTTP label such as "Bad Request". It
    # must not hide a more actionable, nested Oracle business detail.
    message = first_message(payload)
    code = first_code(payload)
    raw_details = payload.get("o:errorDetails")
    details: list[Mapping[str, Any]] = []
    if isinstance(raw_details, list):
        details = [
            detail
            for detail in raw_details[:ORACLE_ERROR_DETAIL_LIMIT]
            if isinstance(detail, Mapping)
        ]
    for detail in details:
        if message is None:
            message = first_message(detail)
        if code is None:
            code = first_code(detail)
        if message is not None and code is not None:
            break
    if message is None:
        for detail in details:
            message = first_message(detail, include_fallback_fields=True)
            if message is not None:
                break
    if message is None:
        message = first_message(payload, include_fallback_fields=True)

    context: dict[str, str] = {}
    if message is not None:
        context["message"] = message
    if code is not None:
        context["code"] = code
    return context


def _safe_provider_error_context(error: BaseException) -> dict[str, Any]:
    """Extract only structured, bounded provider facts from an owned adapter.

    Never fall back to ``str(error)`` here.  Exception text is not a safe
    transport contract: an upstream adapter could include an HTML page,
    credential, or request payload.  A provider message is shown only when an
    owned adapter supplied it under an explicit safe field.
    """

    raw_context = getattr(error, "provider_error", None)
    if not isinstance(raw_context, Mapping):
        raw_context = {}

    message = _safe_provider_text(
        raw_context.get("message")
        or raw_context.get("business_message")
        or getattr(error, "provider_message", None)
    )
    raw_code = (
        raw_context.get("code")
        or raw_context.get("error_code")
        or getattr(error, "provider_code", None)
    )
    code = _safe_provider_code(raw_code)

    raw_ids = raw_context.get("correlation_ids")
    if not isinstance(raw_ids, Mapping):
        raw_ids = getattr(error, "diagnostic_ids", {})
    correlation_ids: dict[str, str] = {}
    if isinstance(raw_ids, Mapping):
        for raw_name, raw_value in raw_ids.items():
            name = str(raw_name).strip().casefold()
            if name not in SAFE_PROVIDER_CORRELATION_ID_NAMES or not isinstance(raw_value, str):
                continue
            value = raw_value.strip()
            if SAFE_PROVIDER_CORRELATION_ID_PATTERN.fullmatch(value):
                correlation_ids[name] = value

    raw_http_status = raw_context.get("http_status") or getattr(error, "http_status", None)
    http_status = (
        raw_http_status
        if isinstance(raw_http_status, int)
        and not isinstance(raw_http_status, bool)
        and 100 <= raw_http_status <= 599
        else None
    )

    result: dict[str, Any] = {}
    if message:
        result["message"] = message
    if code:
        result["code"] = code
    if correlation_ids:
        result["correlation_ids"] = correlation_ids
    if http_status is not None:
        result["http_status"] = http_status
    return result


def _with_safe_provider_detail(base_message: str, error: BaseException) -> tuple[str, dict[str, Any]]:
    """Append a provider-approved business detail without exposing raw text."""

    provider_error = _safe_provider_error_context(error)
    message = provider_error.get("message")
    code = provider_error.get("code")
    http_status = provider_error.get("http_status")
    suffix = f" HTTP {http_status}." if isinstance(http_status, int) else ""
    if not isinstance(message, str):
        return f"{base_message}{suffix}", provider_error
    suffix += f" Oracle reported: {message}"
    if isinstance(code, str):
        suffix += f" (code {code})"
    return f"{base_message}{suffix}", provider_error


def _safe_provider_status_context(status: Mapping[str, Any]) -> dict[str, Any]:
    """Extract a provider-safe diagnostic from an owned status projection.

    ESS and Adaptive Search core skills already reduce their responses to
    allowlisted scalar fields.  The coordinator nevertheless applies the same
    second boundary as it does for exceptions: it accepts only named fields,
    bounds their values, and never treats an arbitrary status mapping as a
    provider error payload.
    """

    nested_context = status.get("provider_error")
    if not isinstance(nested_context, Mapping):
        nested_context = {}
    oracle_context = _safe_oracle_error_context(status)
    nested_oracle_context = _safe_oracle_error_context(nested_context)

    message: str | None = None
    message_candidates = (
        nested_context.get("message"),
        nested_context.get("business_message"),
        nested_oracle_context.get("message"),
        status.get("message"),
        status.get("detail"),
        status.get("errorMessage"),
        status.get("provider_message"),
        status.get("providerMessage"),
        status.get("errorWarningMessage"),
        status.get("errorTypeDescription"),
        status.get("causeDescription"),
        oracle_context.get("message"),
    )
    for value in message_candidates:
        candidate = _safe_provider_text(value)
        if candidate:
            message = candidate
            break

    code: str | None = None
    for candidate in (
        nested_context.get("code"),
        nested_context.get("error_code"),
        nested_oracle_context.get("code"),
        status.get("code"),
        status.get("errorCode"),
        status.get("provider_code"),
        status.get("providerCode"),
        status.get("errorType"),
        oracle_context.get("code"),
    ):
        candidate_code = _safe_provider_code(candidate)
        if candidate_code:
            code = candidate_code
            break

    correlation_ids: dict[str, str] = {}
    raw_ids = (
        nested_context.get("correlation_ids")
        or nested_context.get("correlationIds")
        or status.get("correlation_ids")
        or status.get("correlationIds")
    )
    if isinstance(raw_ids, Mapping):
        for raw_name, raw_value in raw_ids.items():
            name = str(raw_name).strip().casefold()
            if (
                name in SAFE_PROVIDER_CORRELATION_ID_NAMES
                and isinstance(raw_value, str)
                and SAFE_PROVIDER_CORRELATION_ID_PATTERN.fullmatch(raw_value.strip())
            ):
                correlation_ids[name] = raw_value.strip()
    for key in (
        "correlation_id",
        "correlationId",
        "ecid",
        "requestId",
        "request_id",
        "opcRequestId",
        "opc-request-id",
    ):
        raw_value = status.get(key)
        if (
            isinstance(raw_value, str)
            and SAFE_PROVIDER_CORRELATION_ID_PATTERN.fullmatch(raw_value.strip())
        ):
            normalized_name = "ecid" if key == "ecid" else "request-id"
            correlation_ids.setdefault(normalized_name, raw_value.strip())

    raw_http_status = nested_context.get("http_status") or status.get("http_status")
    http_status = (
        raw_http_status
        if isinstance(raw_http_status, int)
        and not isinstance(raw_http_status, bool)
        and 100 <= raw_http_status <= 599
        else None
    )

    context: dict[str, Any] = {}
    if message:
        context["message"] = message
    if code:
        context["code"] = code
    if correlation_ids:
        context["correlation_ids"] = correlation_ids
    if http_status is not None:
        context["http_status"] = http_status
    return context


def _normalized_safe_provider_error(value: Mapping[str, Any] | None) -> dict[str, Any]:
    """Revalidate a previously safe provider diagnostic before persistence.

    Callers normally pass a result from one of the helpers above.  Rechecking
    it here keeps the project-artifact boundary safe if a future caller passes
    a broader adapter mapping by mistake.
    """

    if not isinstance(value, Mapping):
        return {}
    return _safe_provider_status_context({"provider_error": value})


def _with_safe_provider_status_detail(
    base_message: str, status: Mapping[str, Any]
) -> tuple[str, dict[str, Any]]:
    """Append a safe Oracle status diagnostic to a consultant-facing message."""

    provider_error = _safe_provider_status_context(status)
    message = provider_error.get("message")
    code = provider_error.get("code")
    if not isinstance(message, str):
        return base_message, provider_error
    suffix = f" Oracle reported: {message}"
    if isinstance(code, str):
        suffix += f" (code {code})"
    return f"{base_message}{suffix}", provider_error


def _read_properties(path_value: str) -> dict[str, str]:
    try:
        return rest_client_common.read_properties(Path(path_value))
    except (OSError, ValueError) as exc:
        raise FusionAboWorkflowError("Unable to read the local Fusion/CPQ connection profile.") from exc


def _environment_identity(properties: Mapping[str, str]) -> str:
    """Return an unambiguous, safe target identity for a preview fingerprint."""

    raw = properties.get("environment") or properties.get("restBaseUrl")
    if not isinstance(raw, str) or not raw.strip():
        raise FusionAboWorkflowError("The local connection profile is missing environment identity.")
    parsed = urlsplit(raw.strip())
    if parsed.hostname:
        return parsed.hostname.lower()
    return raw.strip().rstrip("/").lower()


def _https_host(properties: Mapping[str, str], field_name: str) -> str:
    """Return one safe HTTPS host from the exact profile used by a client."""

    raw = properties.get(field_name)
    if not isinstance(raw, str) or not raw.strip():
        raise FusionAboWorkflowError(
            f"The local connection profile is missing {field_name} target identity."
        )
    parsed = urlsplit(raw.strip())
    try:
        port = parsed.port
    except ValueError as exc:
        raise FusionAboWorkflowError(
            f"The local connection profile has an invalid {field_name} target port."
        ) from exc
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or port not in {None, 443}
    ):
        raise FusionAboWorkflowError(
            f"The local connection profile has an invalid {field_name} HTTPS target."
        )
    return parsed.hostname.lower()


def _target_evidence_from_properties(properties: Mapping[str, str]) -> dict[str, str]:
    """Bind Fusion and CPQ preflight to one safe, host-level target identity.

    The feature-state reader and canonical CPQ client share ``restBaseUrl``.
    The CPQ client derives the fixed ``/cpq`` context from that single target,
    preventing a second property from creating a cross-environment plan.
    """

    environment = _environment_identity(properties)
    fusion_host = _https_host(properties, "restBaseUrl")
    return {
        "environment": environment,
        "fusion_host": fusion_host,
        "cpq_host": fusion_host,
    }


def _cpq_client_from_args(
    args: argparse.Namespace, *, properties: Mapping[str, str] | None = None
) -> CpqSettingsClient:
    """Build the approved CPQ reader from the exact profile used for preflight.

    The coordinator reads a private profile once per preflight.  Passing that
    same in-memory mapping to both the Fusion and CPQ readers prevents a local
    profile edit between those reads from creating cross-target evidence.
    """

    options = CpqReadOAuthOptions(
        redirect_url=args.redirect_url,
        auth_code=args.auth_code,
        code_verifier=args.code_verifier,
        open_browser=not args.no_open_browser,
        callback_timeout=args.callback_timeout,
    )
    if properties is None:
        properties = _read_properties(args.properties)
    client = CpqRestClient(
        properties,
        token_cache=args.cpq_token_cache,
        timeout=args.timeout,
        oauth_options=options,
    )
    if args.force_cpq_login:
        client._access_token(force_login=True)  # noqa: SLF001 - explicit CLI request
    return CpqSettingsClient(client)


def _feature_states_reader_from_args(
    args: argparse.Namespace, *, properties: Mapping[str, str] | None = None
) -> FeatureStatesReader:
    options = FusionOAuthOptions(
        redirect_url=args.redirect_url,
        auth_code=args.auth_code,
        open_browser=not args.no_open_browser,
        callback_timeout=args.callback_timeout,
        force_login=args.force_fusion_login,
    )
    if properties is None:
        return FeatureStatesReader.from_properties_file(
            Path(args.properties),
            token_cache=args.fusion_token_cache,
            timeout=args.timeout,
            oauth_options=options,
        )
    return FeatureStatesReader(
        properties,
        token_cache=args.fusion_token_cache,
        timeout=args.timeout,
        oauth_options=options,
    )


def run_read_only_preflight(
    settings_client: CpqSettingsClient,
    feature_states_reader: FeatureStatesReader,
    process_variable_name: str | None,
    *,
    target: Mapping[str, str],
    use_default_process: bool = False,
) -> dict[str, Any]:
    """Run CPQ, then ordered CPQ/ABO and Subscription/Coverage checks.

    A CPQ blocker deliberately prevents the Fusion lookup because the task
    cannot safely continue to a prerequisite update until its CPQ target and
    selected process are known to be valid.
    """

    if not isinstance(process_variable_name, str) or not process_variable_name.strip():
        if not use_default_process:
            return {
                "status": "requires_process_selection",
                "task_code": TASK_CODE,
                "task_name": TASK_NAME,
                "prompt": (
                    "Please provide the CPQ Standard Process variable name. If you want to use "
                    "the default, reply 'use default' and I will use 'oraclecpqo'."
                ),
                "next_action": (
                    "Provide --process-variable-name with the exact Standard Process variable name, "
                    "or explicitly select --use-default-process."
                ),
                "side_effects": "No CPQ or Fusion request was made.",
            }

    safe_target = {
        "environment": _require_nonblank_string(target.get("environment"), "target.environment"),
        "fusion_host": _require_nonblank_string(target.get("fusion_host"), "target.fusion_host"),
        "cpq_host": _require_nonblank_string(target.get("cpq_host"), "target.cpq_host"),
    }
    if safe_target["fusion_host"] != safe_target["cpq_host"]:
        raise FusionAboWorkflowError(
            "Fusion ABO preflight requires matching Fusion and CPQ target hosts."
        )

    cpq_plan = settings_client.plan_fusion_abo_write(process_variable_name)
    if cpq_plan.get("status") == "blocked":
        result = classify_fusion_abo_preflight(cpq_plan, {"items": []})
        result.update(
            {
                "task_code": TASK_CODE,
                "task_name": TASK_NAME,
                "environment": safe_target["environment"],
                "target": safe_target,
                "feature_state_read": {
                    "status": "skipped",
                    "reason": "CPQ preflight was blocked before Fusion prerequisite lookup.",
                },
                "side_effects": "Read-only CPQ preflight attempted. No Fusion opt-in or CPQ setting was changed.",
            }
        )
        return result

    cpq_abo_states_result = feature_states_reader.read(
        CPQ_ABO_PREREQUISITE_FEATURE_CODES,
        feature_mode="COMBO",
    )
    cpq_abo_states = normalize_fusion_abo_feature_states(
        cpq_abo_states_result.as_evidence(),
        feature_codes=CPQ_ABO_PREREQUISITE_FEATURE_CODES,
    )
    cpq_status = cpq_plan.get("status")
    if any(not enabled for enabled in cpq_abo_states.values()):
        if cpq_status in {
            "already_enabled",
            "requires_abo_delta_action_library_function_recovery",
        }:
            result = {
                "status": "blocked",
                "stage": "preflight_reconciliation",
                "feature_states": cpq_abo_states,
                "prerequisite_feature_codes": list(CPQ_ABO_PREREQUISITE_FEATURE_CODES),
                "cpq_preflight": cpq_plan,
                "blockers": [
                    "Fusion ABO is already enabled in CPQ but CPQ/ABO prerequisite evidence is not "
                    "fully enabled. Reconcile the target environment; do not change either system automatically."
                ],
                "next_action": "Investigate the inconsistent environment state and rerun the read-only preflight.",
            }
        else:
            result = build_prerequisite_update_handoff(
                cpq_plan,
                cpq_abo_states,
                prerequisite_feature_codes=CPQ_ABO_PREREQUISITE_FEATURE_CODES,
                status="requires_cpq_abo_prerequisite_update",
                stage="cpq_abo_optin_handoff",
                readiness_label="CPQ/ABO prerequisite",
            )
        result.update(
            {
                "task_code": TASK_CODE,
                "task_name": TASK_NAME,
                "environment": safe_target["environment"],
                "target": safe_target,
                "feature_state_read": {
                    "cpq_abo": cpq_abo_states_result.as_dict(),
                    "subscription_coverage": {
                        "status": "skipped",
                        "reason": "CPQ/ABO prerequisites are not fully enabled.",
                    },
                },
                "side_effects": "Read-only CPQ and CPQ/ABO Fusion feature-state requests completed. No Fusion opt-in or CPQ setting was changed.",
            }
        )
        return result

    subscription_coverage_states_result = feature_states_reader.read(
        SUBSCRIPTION_COVERAGE_PREREQUISITE_FEATURE_CODES,
        feature_mode="COMBO",
    )
    subscription_coverage_states = normalize_fusion_abo_feature_states(
        subscription_coverage_states_result.as_evidence(),
        feature_codes=SUBSCRIPTION_COVERAGE_PREREQUISITE_FEATURE_CODES,
    )
    all_feature_states = {**cpq_abo_states, **subscription_coverage_states}
    if any(not enabled for enabled in subscription_coverage_states.values()):
        result = build_prerequisite_update_handoff(
            cpq_plan,
            all_feature_states,
            prerequisite_feature_codes=SUBSCRIPTION_COVERAGE_PREREQUISITE_FEATURE_CODES,
            status="requires_subscription_coverage_prerequisite_update",
            stage="subscription_coverage_optin_handoff",
            readiness_label="Subscription/Coverage prerequisite",
        )
    else:
        combined_evidence = {
            "items": [
                *cpq_abo_states_result.as_evidence()["items"],
                *subscription_coverage_states_result.as_evidence()["items"],
            ]
        }
        result = classify_fusion_abo_preflight(cpq_plan, combined_evidence)
    result.update(
        {
            "task_code": TASK_CODE,
            "task_name": TASK_NAME,
            "environment": safe_target["environment"],
            "target": safe_target,
            "feature_state_read": {
                "cpq_abo": cpq_abo_states_result.as_dict(),
                "subscription_coverage": subscription_coverage_states_result.as_dict(),
            },
            "side_effects": "Read-only CPQ and Fusion feature-state requests completed. No Fusion opt-in or CPQ setting was changed.",
        }
    )
    return result


def _require_nonblank_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FusionAboWorkflowError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _validate_feature_choice(value: str) -> str:
    choice = _require_nonblank_string(value, "feature_choice")
    if "," in choice or "\x00" in choice or "\n" in choice or "\r" in choice:
        raise FusionAboWorkflowError(
            "feature_choice must be one exact shared-workflow choice short name, not a list."
        )
    return choice


def _require_false_prerequisite(
    preflight_result: Mapping[str, Any], feature_code: str
) -> dict[str, Any]:
    if preflight_result.get("status") not in {
        "requires_cpq_abo_prerequisite_update",
        "requires_subscription_coverage_prerequisite_update",
        "requires_prerequisite_update",
    }:
        raise FusionAboWorkflowError(
            "A prerequisite-update preview can be created only from a current requires_prerequisite_update result."
        )
    states = preflight_result.get("feature_states")
    if not isinstance(states, Mapping):
        raise FusionAboWorkflowError("Preflight result does not contain validated Fusion feature states.")
    stage_codes = preflight_result.get("prerequisite_feature_codes")
    if not isinstance(stage_codes, list) or set(stage_codes) - set(FUSION_ABO_PREREQUISITE_FEATURE_CODES):
        raise FusionAboWorkflowError("Preflight result does not identify a valid prerequisite stage.")
    if feature_code not in stage_codes or states.get(feature_code) is not False:
        raise FusionAboWorkflowError(
            "The requested feature is not a currently false Fusion ABO prerequisite."
        )
    handoffs = preflight_result.get("prerequisite_handoffs")
    if not isinstance(handoffs, list) or not any(
        isinstance(handoff, Mapping)
        and handoff.get("feature_code") == feature_code
        and handoff.get("skill_id") == SHARED_OPTIN_SKILL_ID
        and handoff.get("approval_required") is True
        for handoff in handoffs
    ):
        raise FusionAboWorkflowError(
            "Preflight result does not contain the required governed shared-workflow handoff."
        )
    return {str(code): bool(states[code]) for code in states}


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _required_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise FusionAboWorkflowError(f"{field_name} must be an object.")
    return value


def build_prerequisite_update_preview(
    preflight_result: Mapping[str, Any],
    *,
    feature_code: str,
    feature_choice: str,
) -> dict[str, Any]:
    """Build the exact, approval-bound plan for one missing Fusion opt-in."""

    states = _require_false_prerequisite(preflight_result, feature_code)
    choice = _validate_feature_choice(feature_choice)
    environment = _require_nonblank_string(preflight_result.get("environment"), "environment")
    target = _required_mapping(preflight_result.get("target"), "Preflight target evidence")
    safe_target = {
        "environment": _require_nonblank_string(target.get("environment"), "target.environment"),
        "fusion_host": _require_nonblank_string(target.get("fusion_host"), "target.fusion_host"),
        "cpq_host": _require_nonblank_string(target.get("cpq_host"), "target.cpq_host"),
    }
    if safe_target["environment"] != environment or safe_target["fusion_host"] != safe_target["cpq_host"]:
        raise FusionAboWorkflowError("Preflight target evidence is inconsistent.")
    cpq_preflight = _required_mapping(
        preflight_result.get("cpq_preflight"), "Preflight CPQ evidence"
    )
    process_selection = cpq_preflight.get("process_selection")
    if not isinstance(process_selection, Mapping):
        raise FusionAboWorkflowError("Preflight result is missing CPQ process-selection evidence.")
    approval_context = {
        "task_code": TASK_CODE,
        "environment": environment,
        "target": safe_target,
        "feature_states": states,
        "feature_code": feature_code,
        "feature_choice": choice,
        "process_selection": {
            "resolved_process_variable_name": process_selection.get(
                "resolved_process_variable_name"
            ),
            "selection_source": process_selection.get("selection_source"),
        },
        "writer_skill_id": SHARED_OPTIN_SKILL_ID,
        "writer_action": "set-choices",
    }
    approval_fingerprint = hashlib.sha256(
        _canonical_json(approval_context).encode("utf-8")
    ).hexdigest()
    return {
        "status": "approval_required",
        "task_code": TASK_CODE,
        "task_name": TASK_NAME,
        "approval_fingerprint": approval_fingerprint,
        "approval_context": approval_context,
        "operation": {
            "skill_id": SHARED_OPTIN_SKILL_ID,
            "feature_code": feature_code,
            "action": "set-choices",
            "feature_choice": choice,
            "effect": "Set the selected Fusion feature choice for this one currently false prerequisite only.",
        },
        "approval_required": {
            "timing": "immediately_before_execution",
            "instruction": "Obtain current explicit approval for this exact target, feature code, and choice before invoking the shared writer.",
        },
        "post_write_requirement": "Reread the approved prerequisite stage, then rerun the full ordered preflight. CPQ work remains blocked until all four prerequisites are true.",
    }


def _read_json_object(path_value: str, field_name: str) -> dict[str, Any]:
    path = Path(path_value)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise FusionAboWorkflowError(f"Unable to read {field_name} file.") from exc
    except json.JSONDecodeError as exc:
        raise FusionAboWorkflowError(f"{field_name} file is not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise FusionAboWorkflowError(f"{field_name} file must contain a JSON object.")
    return payload


def _write_json(path_value: str | None, payload: Mapping[str, Any]) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if path_value:
        path = Path(path_value)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {path}")
    print(rendered)


def _workflow_presentation_context(record_ref: Any) -> dict[str, Any]:
    """Read only the safe display context from an exact local workflow record."""

    if not isinstance(record_ref, str):
        return {}
    parts = Path(record_ref).parts
    expected_parts = TASK_ARTIFACT_DIRECTORY.parts
    if (
        len(parts) != len(expected_parts) + 3
        or parts[0] != "project"
        or tuple(parts[2:-1]) != expected_parts
    ):
        return {}
    match = re.fullmatch(r"automatic-workflow-([a-f0-9]{64})\.json", parts[-1])
    if not match:
        return {}
    try:
        project_id = _safe_project_id(parts[1])
        path = _workflow_record_path(REPO_ROOT / "project" / project_id, match.group(1))
        if record_ref != _relative_to_repo(path):
            return {}
        record = _read_json_mapping(path, "Fusion ABO presentation checkpoint")
        if record.get("project_id") != project_id:
            return {}
        context = record.get("presentation_context")
        if isinstance(context, Mapping):
            states = context.get("feature_states")
            if (
                isinstance(states, Mapping)
                and set(states) == set(FUSION_ABO_PREREQUISITE_FEATURE_CODES)
                and all(states[code] is True for code in FUSION_ABO_PREREQUISITE_FEATURE_CODES)
            ):
                return dict(context)
        # Older checkpoints lack the display snapshot. A completed CPQ gate
        # still proves that all four prerequisites passed before its import.
        cpq = record.get("cpq_verification")
        if isinstance(cpq, Mapping) and cpq.get("status") == "completed":
            return {
                "target": cpq.get("target"),
                "validated_process_variable_name": cpq.get("validated_process_variable_name"),
                "prerequisites_verified_before_cpq": True,
            }
    except (FusionAboWorkflowError, OSError, ValueError):
        return {}
    return {}


def _with_customer_presentation(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Attach deterministic user-facing Markdown after workflow logic completes.

    The presentation is deliberately added only at the command boundary. It is
    never used to construct a payload, approval fingerprint, or durable
    execution decision.
    """

    from abo_presentation import render_abo_presentation

    result = dict(payload)
    if result.get("data_loader_markdown") and result.get("status") in {"approval_required", "submitted"}:
        result["customer_presentation"] = str(result.get("workbook_access", "")) + result["data_loader_markdown"]
        next_action = result.get("next_action")
        if result.get("status") == "submitted" and isinstance(next_action, str) and next_action.strip():
            result["customer_presentation"] += "\n\n## Next Action\n\n" + next_action
        return result
    if "presentation_context" not in result:
        context = _workflow_presentation_context(result.get("workflow_record_ref"))
        if context:
            result["presentation_context"] = context
            if isinstance(context.get("target"), Mapping):
                result.setdefault("target", context["target"])
            if isinstance(context.get("validated_process_variable_name"), str):
                result.setdefault(
                    "validated_process_variable_name",
                    context["validated_process_variable_name"],
                )
    result["customer_presentation"] = render_abo_presentation(result)
    return result


def _utc_timestamp(value: datetime | None = None) -> str:
    """Return a stable RFC 3339 timestamp for durable project records."""

    timestamp = value or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise FusionAboWorkflowError("A project-record timestamp must include a timezone.")
    return timestamp.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _parse_rfc3339_timestamp(value: str, field_name: str) -> datetime:
    """Parse an approval timestamp without accepting a local/ambiguous time."""

    rendered = _require_nonblank_string(value, field_name)
    normalized = rendered[:-1] + "+00:00" if rendered.endswith("Z") else rendered
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise FusionAboWorkflowError(f"{field_name} must be an RFC 3339 timestamp.") from exc
    if parsed.tzinfo is None:
        raise FusionAboWorkflowError(f"{field_name} must include a timezone.")
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def _read_json_mapping(path: Path, field_name: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise FusionAboWorkflowError(f"Unable to read {field_name}.") from exc
    except json.JSONDecodeError as exc:
        raise FusionAboWorkflowError(f"{field_name} is not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise FusionAboWorkflowError(f"{field_name} must contain a JSON object.")
    return payload


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    """Write a JSON record atomically so a stopped run never leaves partial JSON."""

    _assert_safe_for_persistence(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _assert_safe_for_persistence(value: Any, *, field_path: str = "record") -> None:
    """Reject accidental credential/token persistence instead of silently redacting it."""

    if isinstance(value, Mapping):
        for key, nested_value in value.items():
            key_text = str(key).strip().casefold()
            if key_text in SENSITIVE_FIELD_NAMES:
                raise FusionAboWorkflowError(
                    f"Refusing to persist sensitive field {field_path}.{key}."
                )
            _assert_safe_for_persistence(nested_value, field_path=f"{field_path}.{key}")
    elif isinstance(value, list):
        for index, nested_value in enumerate(value):
            _assert_safe_for_persistence(nested_value, field_path=f"{field_path}[{index}]")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_project_id(value: str) -> str:
    project_id = _require_nonblank_string(value, "project_id")
    if not PROJECT_ID_PATTERN.fullmatch(project_id):
        raise FusionAboWorkflowError(
            "project_id must use lowercase letters, digits, and internal hyphens only."
        )
    return project_id


def _project_workspace(project_id_value: str) -> tuple[str, Path, Path, Path, dict[str, Any], dict[str, Any]]:
    """Resolve one initialized project workspace and reject traversal or stale roots."""

    project_id = _safe_project_id(project_id_value)
    project_container = (REPO_ROOT / "project").resolve()
    project_root = (project_container / project_id).resolve()
    try:
        project_root.relative_to(project_container)
    except ValueError as exc:
        raise FusionAboWorkflowError("project_id resolves outside the FDOS project workspace.") from exc
    if not project_root.is_dir():
        raise FusionAboWorkflowError(
            "A CPQ Settings preview or execution requires an existing initialized project workspace."
        )
    state_path = project_root / "state" / "project-state.json"
    index_path = project_root / "artifacts" / "artifact-index.json"
    if not state_path.is_file() or not index_path.is_file():
        raise FusionAboWorkflowError(
            "The selected project workspace is not initialized with project state and artifact index files."
        )
    state = _read_json_mapping(state_path, "project state")
    artifact_index = _read_json_mapping(index_path, "artifact index")
    if state.get("project_id") != project_id or artifact_index.get("project_id") != project_id:
        raise FusionAboWorkflowError(
            "The selected project workspace has inconsistent project identity metadata."
        )
    if not isinstance(artifact_index.get("artifacts"), list):
        raise FusionAboWorkflowError("The project artifact index does not contain an artifacts array.")
    if not isinstance(state.get("active_skill_path"), list):
        raise FusionAboWorkflowError("The project state does not contain an active_skill_path array.")
    return project_id, project_root, state_path, index_path, state, artifact_index


def _relative_to_repo(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve()))
    except ValueError as exc:
        raise FusionAboWorkflowError("A project record path resolves outside the FDOS repository.") from exc


def _new_run_id(stage: str, timestamp: str) -> str:
    safe_stage = re.sub(r"[^a-z0-9-]+", "-", stage.casefold()).strip("-")
    return f"{timestamp.replace('-', '').replace(':', '').replace('Z', 'Z')}-fusion-abo-{safe_stage}-{uuid.uuid4().hex[:12]}"


def _artifact_record(
    *,
    artifact_id: str,
    name: str,
    artifact_type: str,
    location: str,
    timestamp: str,
    checksum: str | None,
) -> dict[str, Any]:
    """Return a schema-compatible artifact-index record for one safe record."""

    return {
        "artifact_id": artifact_id,
        "name": name,
        "artifact_type": artifact_type,
        "skill_id": TASK_SKILL_ID,
        "location": location,
        "version": "1.0.0",
        "status": "draft",
        "change_type": "initial",
        "supersedes": None,
        "checksum": checksum,
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def _append_artifact_records(
    artifact_index: dict[str, Any],
    *,
    timestamp: str,
    records: list[dict[str, Any]],
) -> None:
    existing = artifact_index.get("artifacts")
    if not isinstance(existing, list):
        raise FusionAboWorkflowError("The project artifact index does not contain an artifacts array.")
    existing_ids = {
        record.get("artifact_id")
        for record in existing
        if isinstance(record, Mapping) and isinstance(record.get("artifact_id"), str)
    }
    for record in records:
        artifact_id = record["artifact_id"]
        if artifact_id in existing_ids:
            raise FusionAboWorkflowError(
                "A generated CPQ Settings record conflicts with an existing artifact id."
            )
        existing.append(record)
        existing_ids.add(artifact_id)
    artifact_index["updated_at"] = timestamp


def _update_project_state(
    state: dict[str, Any],
    *,
    latest_run_ref: str,
    status: str,
    timestamp: str,
) -> None:
    if status not in {"in_progress", "blocked", "ready_for_review"}:
        raise FusionAboWorkflowError("The requested project-state status is unsupported.")
    active_skill_path = state["active_skill_path"]
    if TASK_SKILL_ID not in active_skill_path:
        active_skill_path.append(TASK_SKILL_ID)
    state["latest_run_ref"] = latest_run_ref
    state["status"] = status
    state["updated_at"] = timestamp


def _token_usage(
    *,
    project_id: str,
    project_root: Path,
    timestamp: str,
    trigger: str,
    artifact_paths: list[Path],
    files_read: int,
    notes: str,
) -> tuple[Path, dict[str, Any]]:
    """Append the required token-use log without persisting connection material."""

    output_tokens = sum(estimate_path_tokens(path) for path in artifact_paths)
    token_log = append_token_usage_log(
        project_id=project_id,
        skill_id=TASK_SKILL_ID,
        task=TASK_NAME,
        trigger=trigger,
        activity_start_time=timestamp,
        artifact_paths=artifact_paths,
        files_read=files_read,
        estimated_input_tokens=0,
        estimated_output_tokens=output_tokens,
        estimation_method=TOKEN_ESTIMATION_METHOD,
        notes=notes,
        root=REPO_ROOT,
    )
    return token_log, {
        "estimation_method": TOKEN_ESTIMATION_METHOD,
        "estimated_input_tokens": 0,
        "estimated_output_tokens": output_tokens,
        "estimated_total_tokens": output_tokens,
        "artifacts_written": len(artifact_paths),
        "files_read": files_read,
        "log_ref": _relative_to_repo(token_log),
        "notes": notes,
    }


def _write_workspace_preview_record(
    *,
    project_id_value: str,
    preview: Mapping[str, Any],
    trigger: str,
    preview_stage: str = "cpq_settings_write_preview",
    run_kind: str = "cpq-settings-write-preview",
    artifact_prefix: str = "cpq-settings-write-preview",
    artifact_name: str = "Fusion ABO CPQ Settings Write Preview",
    inputs: list[str] | None = None,
    notes: str = "Read-only CPQ Settings write preview completed; explicit current approval is still required.",
    token_notes: str = "Token estimate for the sanitized Fusion ABO CPQ Settings write preview.",
    files_read: int = 3,
    record_status: str = "approval_required",
    record_field: str = "preview",
    project_status: str = "ready_for_review",
) -> dict[str, str]:
    """Persist a completed, read-only approval preview and its safe artifact.

    Defaults preserve the existing CPQ preview records.
    """

    _assert_safe_for_persistence(preview)
    safe_stage = _require_nonblank_string(preview_stage, "preview_stage")
    safe_run_kind = _require_nonblank_string(run_kind, "run_kind")
    safe_artifact_prefix = _require_nonblank_string(artifact_prefix, "artifact_prefix")
    safe_artifact_name = _require_nonblank_string(artifact_name, "artifact_name")
    safe_notes = _require_nonblank_string(notes, "preview notes")
    safe_token_notes = _require_nonblank_string(token_notes, "preview token notes")
    safe_record_status = _require_nonblank_string(record_status, "preview record status")
    safe_record_field = _require_nonblank_string(record_field, "preview record field")
    if safe_record_field != "preview":
        raise FusionAboWorkflowError("Preview record field is unsupported.")
    if project_status not in {"in_progress", "blocked", "ready_for_review"}:
        raise FusionAboWorkflowError("Preview project status is unsupported.")
    if not re.fullmatch(r"[a-z0-9-]+", safe_run_kind) or not re.fullmatch(
        r"[a-z0-9-]+", safe_artifact_prefix
    ):
        raise FusionAboWorkflowError("Preview record names must use lowercase kebab-case.")
    if files_read < 1:
        raise FusionAboWorkflowError("Preview record files_read must be positive.")
    safe_inputs = list(inputs or ["fresh_cpq_and_fusion_preflight", "canonical_cpq_settings_write_plan"])
    if not all(isinstance(value, str) and value.strip() for value in safe_inputs):
        raise FusionAboWorkflowError("Preview record inputs must be non-empty strings.")
    project_id, project_root, state_path, index_path, state, artifact_index = _project_workspace(
        project_id_value
    )
    timestamp = _utc_timestamp()
    run_id = _new_run_id(safe_run_kind, timestamp)
    artifact_path = project_root / TASK_ARTIFACT_DIRECTORY / f"{safe_artifact_prefix}-{run_id}.json"
    run_path = project_root / "state" / "runs" / f"{run_id}.json"
    artifact_payload: dict[str, Any] = {
        "status": safe_record_status,
        "stage": safe_stage,
        "recorded_at": timestamp,
        "task_code": TASK_CODE,
        "task_name": TASK_NAME,
        "skill_id": TASK_SKILL_ID,
    }
    artifact_payload[safe_record_field] = dict(preview)
    _write_json_atomic(artifact_path, artifact_payload)
    artifact_ref = _relative_to_repo(artifact_path)
    run_ref = _relative_to_repo(run_path)
    run = {
        "run_id": run_id,
        "skill_id": TASK_SKILL_ID,
        "started_at": timestamp,
        "completed_at": timestamp,
        "status": "completed",
        "inputs": safe_inputs,
        "outputs": [artifact_ref],
        "artifact_refs": [artifact_ref],
        "notes": safe_notes,
    }
    _write_json_atomic(run_path, run)
    token_log, token_usage = _token_usage(
        project_id=project_id,
        project_root=project_root,
        timestamp=timestamp,
        trigger=trigger,
        artifact_paths=[artifact_path, run_path],
        files_read=files_read,
        notes=safe_token_notes,
    )
    run["token_usage"] = token_usage
    _write_json_atomic(run_path, run)

    token_log_ref = _relative_to_repo(token_log)
    _append_artifact_records(
        artifact_index,
        timestamp=timestamp,
        records=[
            _artifact_record(
                artifact_id=f"{safe_artifact_prefix}-{run_id}",
                name=safe_artifact_name,
                artifact_type="configuration_blueprint",
                location=artifact_ref,
                timestamp=timestamp,
                checksum=_sha256_file(artifact_path),
            ),
            _artifact_record(
                artifact_id=f"skill-run-{run_id}",
                name=f"{safe_artifact_name} Run",
                artifact_type="skill_run",
                location=run_ref,
                timestamp=timestamp,
                checksum=_sha256_file(run_path),
            ),
            _artifact_record(
                artifact_id=f"token-usage-{run_id}",
                name=f"{safe_artifact_name} Token Usage",
                artifact_type="token_usage_record",
                location=token_log_ref,
                timestamp=timestamp,
                checksum=_sha256_file(token_log),
            ),
        ],
    )
    _update_project_state(
        state,
        latest_run_ref=run_ref,
        status=project_status,
        timestamp=timestamp,
    )
    _write_json_atomic(index_path, artifact_index)
    _write_json_atomic(state_path, state)
    return {"artifact_ref": artifact_ref, "run_ref": run_ref}


def _start_cpq_settings_write_record(
    *,
    project_id_value: str,
    preview: Mapping[str, Any],
) -> dict[str, Any]:
    """Persist the approved preview and an append-only started run before submission."""

    _assert_safe_for_persistence(preview)
    project_id, project_root, state_path, index_path, state, artifact_index = _project_workspace(
        project_id_value
    )
    timestamp = _utc_timestamp()
    run_id = _new_run_id("cpq-settings-write-execution", timestamp)
    artifact_path = project_root / TASK_ARTIFACT_DIRECTORY / f"cpq-settings-write-approved-preview-{run_id}.json"
    run_path = project_root / "state" / "runs" / f"{run_id}.json"
    artifact_payload = {
        "status": "execution_started",
        "stage": "cpq_settings_write_execution",
        "recorded_at": timestamp,
        "task_code": TASK_CODE,
        "task_name": TASK_NAME,
        "skill_id": TASK_SKILL_ID,
        "preview": dict(preview),
        "side_effects": "No CPQ Settings Data Loader import had been submitted when this approved execution record was created.",
    }
    _write_json_atomic(artifact_path, artifact_payload)
    artifact_ref = _relative_to_repo(artifact_path)
    run_ref = _relative_to_repo(run_path)
    run = {
        "run_id": run_id,
        "skill_id": TASK_SKILL_ID,
        "started_at": timestamp,
        "completed_at": None,
        "status": "started",
        "inputs": [
            "fresh_cpq_and_fusion_preflight",
            "canonical_cpq_settings_write_plan",
            "exact_current_approval",
        ],
        "outputs": [artifact_ref],
        "artifact_refs": [artifact_ref],
        "notes": "Approved Fusion ABO CPQ Settings Data Loader sequence started; no automatic retry or rollback is allowed.",
    }
    _write_json_atomic(run_path, run)
    token_log, token_usage = _token_usage(
        project_id=project_id,
        project_root=project_root,
        timestamp=timestamp,
        trigger="approved CPQ Settings write started",
        artifact_paths=[artifact_path, run_path],
        files_read=3,
        notes="Token estimate recorded before the one approved CPQ Settings mutation sequence.",
    )
    run["token_usage"] = token_usage
    _write_json_atomic(run_path, run)

    token_log_ref = _relative_to_repo(token_log)
    _append_artifact_records(
        artifact_index,
        timestamp=timestamp,
        records=[
            _artifact_record(
                artifact_id=f"cpq-settings-write-approved-preview-{run_id}",
                name="Fusion ABO Approved CPQ Settings Write Preview",
                artifact_type="configuration_blueprint",
                location=artifact_ref,
                timestamp=timestamp,
                checksum=_sha256_file(artifact_path),
            ),
            _artifact_record(
                artifact_id=f"skill-run-{run_id}",
                name="Fusion ABO CPQ Settings Write Run",
                artifact_type="skill_run",
                location=run_ref,
                timestamp=timestamp,
                checksum=_sha256_file(run_path),
            ),
            _artifact_record(
                artifact_id=f"token-usage-started-{run_id}",
                name="Fusion ABO CPQ Settings Write Start Token Usage",
                artifact_type="token_usage_record",
                location=token_log_ref,
                timestamp=timestamp,
                checksum=_sha256_file(token_log),
            ),
        ],
    )
    _update_project_state(
        state,
        latest_run_ref=run_ref,
        status="in_progress",
        timestamp=timestamp,
    )
    _write_json_atomic(index_path, artifact_index)
    _write_json_atomic(state_path, state)
    return {
        "project_id": project_id,
        "project_root": project_root,
        "state_path": state_path,
        "index_path": index_path,
        "run_id": run_id,
        "run_path": run_path,
        "run_ref": run_ref,
        "preview_artifact_ref": artifact_ref,
    }


def _complete_cpq_settings_write_record(
    *,
    context: Mapping[str, Any],
    execution_result: Mapping[str, Any],
) -> dict[str, str]:
    """Record terminal core-executor output without replaying a CPQ request."""

    _assert_safe_for_persistence(execution_result)
    project_id = _require_nonblank_string(context.get("project_id"), "execution context project_id")
    project_root = context.get("project_root")
    state_path = context.get("state_path")
    index_path = context.get("index_path")
    run_path = context.get("run_path")
    run_id = _require_nonblank_string(context.get("run_id"), "execution context run_id")
    run_ref = _require_nonblank_string(context.get("run_ref"), "execution context run_ref")
    preview_artifact_ref = _require_nonblank_string(
        context.get("preview_artifact_ref"), "execution context preview_artifact_ref"
    )
    if not all(isinstance(path, Path) for path in (project_root, state_path, index_path, run_path)):
        raise FusionAboWorkflowError("CPQ Settings execution context has unsafe project paths.")

    state = _read_json_mapping(state_path, "project state")
    artifact_index = _read_json_mapping(index_path, "artifact index")
    timestamp = _utc_timestamp()
    result_status = execution_result.get("status")
    completed = result_status == "completed"
    artifact_path = project_root / TASK_ARTIFACT_DIRECTORY / f"cpq-settings-write-result-{run_id}.json"
    result_payload = {
        "status": "completed" if completed else "blocked",
        "stage": "cpq_settings_write_execution",
        "recorded_at": timestamp,
        "task_code": TASK_CODE,
        "task_name": TASK_NAME,
        "skill_id": TASK_SKILL_ID,
        "execution_result": dict(execution_result),
    }
    _write_json_atomic(artifact_path, result_payload)
    artifact_ref = _relative_to_repo(artifact_path)

    run = _read_json_mapping(run_path, "started CPQ Settings run")
    run["completed_at"] = timestamp
    run["status"] = "completed" if completed else "failed"
    run["outputs"] = [preview_artifact_ref, artifact_ref]
    run["artifact_refs"] = [preview_artifact_ref, artifact_ref]
    run["notes"] = (
        "CPQ Settings sequence completed and final Commerce Settings readback verified Fusion ABO."
        if completed
        else "CPQ Settings sequence stopped without retry or rollback; reconcile current CPQ state before another approval."
    )
    _write_json_atomic(run_path, run)

    token_log, token_usage = _token_usage(
        project_id=project_id,
        project_root=project_root,
        timestamp=timestamp,
        trigger="approved CPQ Settings write completed" if completed else "CPQ Settings write stopped",
        artifact_paths=[artifact_path, run_path],
        files_read=2,
        notes=(
            "Token estimate for the completed Fusion ABO CPQ Settings write verification."
            if completed
            else "Token estimate for the stopped/indeterminate Fusion ABO CPQ Settings write reconciliation record."
        ),
    )
    run["token_usage"] = token_usage
    _write_json_atomic(run_path, run)

    token_log_ref = _relative_to_repo(token_log)
    _append_artifact_records(
        artifact_index,
        timestamp=timestamp,
        records=[
            _artifact_record(
                artifact_id=f"cpq-settings-write-result-{run_id}",
                name="Fusion ABO CPQ Settings Write Result",
                artifact_type="validation_result",
                location=artifact_ref,
                timestamp=timestamp,
                checksum=_sha256_file(artifact_path),
            ),
            _artifact_record(
                artifact_id=f"token-usage-result-{run_id}",
                name="Fusion ABO CPQ Settings Write Result Token Usage",
                artifact_type="token_usage_record",
                location=token_log_ref,
                timestamp=timestamp,
                checksum=_sha256_file(token_log),
            ),
        ],
    )
    _update_project_state(
        state,
        latest_run_ref=run_ref,
        status="ready_for_review" if completed else "blocked",
        timestamp=timestamp,
    )
    _write_json_atomic(index_path, artifact_index)
    _write_json_atomic(state_path, state)
    return {"artifact_ref": artifact_ref, "run_ref": run_ref}


def _complete_cpq_settings_write_result(
    *,
    context: Mapping[str, Any],
    execution_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Complete the CPQ audit record without hiding a possible mutation.

    The append-only ``_start_cpq_settings_write_record`` checkpoint is durable
    before the first CPQ Settings Data Loader submission.  The core writer uses ``failed`` only before a
    submission is attempted; ``completed`` and ``indeterminate`` both cross the
    mutation boundary.  If local completion persistence then fails, report
    an indeterminate result and require read-only reconciliation instead of
    allowing the caller to repeat a potentially completed CPQ change.
    """

    status = execution_result.get("status")
    mutation_may_have_been_attempted = status in {"completed", "indeterminate"}
    try:
        persistence = _complete_cpq_settings_write_record(
            context=context,
            execution_result=execution_result,
        )
    except Exception:
        if not mutation_may_have_been_attempted:
            # The core writer guarantees that a failed result stopped before
            # the first submission, so normal pre-mutation persistence handling is
            # still accurate.
            raise

        result = {
            **dict(execution_result),
            "status": "indeterminate",
            "failure_class": "artifact_persistence",
            "message": (
                "The CPQ Settings sequence may already have changed the target, but FDOS could not persist "
                "its completed local audit record. Treat the CPQ state as possibly changed; do not retry the "
                "CPQ write or submit ESS automatically."
            ),
            "side_effects": (
                "One or more CPQ Settings Data Loader imports may have reached the target. No automatic retry, "
                "rollback, or ESS POST was attempted."
            ),
            "next_action": (
                "Reconcile CPQ Commerce Settings through approved read-only checks before any new approval, "
                "CPQ write, or ESS submission."
            ),
        }
        # The pre-submission checkpoint is durable by definition. Preserve its
        # safe references when available so reconciliation has an immutable
        # starting point even when the terminal record could not be written.
        run_ref = context.get("run_ref")
        preview_ref = context.get("preview_artifact_ref")
        if isinstance(run_ref, str) and run_ref.strip():
            result["project_run_ref"] = run_ref.strip()
        if isinstance(preview_ref, str) and preview_ref.strip():
            result["project_approved_preview_ref"] = preview_ref.strip()
        return result

    return {
        **dict(execution_result),
        "project_artifact_ref": persistence["artifact_ref"],
        "project_run_ref": persistence["run_ref"],
    }


# The CPQ preview has a bounded approval window. Adaptive Search and ESS use
# their own explicit approvals at their later execution stages.
WORKFLOW_APPROVAL_TTL_SECONDS = 7200
CPQ_SETTINGS_APPROVAL_TTL_SECONDS = WORKFLOW_APPROVAL_TTL_SECONDS


def _adaptive_search_target(target: Mapping[str, Any]) -> dict[str, str]:
    """Convert the parent host evidence into the child contract's HTTPS origin."""

    safe_target = _safe_target(target, "workflow target")
    raw_host = safe_target["fusion_host"].rstrip("/")
    parsed = urlsplit(raw_host)
    if parsed.scheme:
        try:
            port = parsed.port
        except ValueError as exc:
            raise FusionAboWorkflowError("The approved Fusion host has an invalid port.") from exc
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/"}
            or port not in {None, 443}
        ):
            raise FusionAboWorkflowError("The approved Fusion host cannot be used by Configure Adaptive Search.")
        origin = f"https://{parsed.hostname.lower()}"
    else:
        if "/" in raw_host or not raw_host:
            raise FusionAboWorkflowError("The approved Fusion host is not a safe HTTPS origin.")
        origin = f"https://{raw_host.lower()}"
    return {"environment": safe_target["environment"], "fusion_host": origin}


def _safe_adaptive_preparation(
    value: Mapping[str, Any], *, project_id: str, target: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate the read-only child preparation before it enters one approval."""

    preparation = _required_mapping(value.get("preparation"), "Adaptive Search preparation")
    if preparation.get("schema_version") != "1.0" or preparation.get("state") != "PREPARED":
        raise FusionAboWorkflowError("Configure Adaptive Search did not return a valid prepared operation.")
    preparation_id = _require_nonblank_string(
        preparation.get("preparation_id"), "Adaptive Search preparation_id"
    )
    if not re.fullmatch(r"app_[a-f0-9]{32}", preparation_id):
        raise FusionAboWorkflowError("Configure Adaptive Search returned an invalid preparation identifier.")
    if preparation.get("project_id") != project_id:
        raise FusionAboWorkflowError("Configure Adaptive Search preparation belongs to another project.")
    expected_target = _adaptive_search_target(target)
    if preparation.get("target") != expected_target:
        raise FusionAboWorkflowError("Configure Adaptive Search preparation targets a different Fusion environment.")
    if list(preparation.get("entities", [])) != list(ADAPTIVE_SEARCH_REQUIRED_ENTITIES):
        raise FusionAboWorkflowError("Configure Adaptive Search preparation does not cover the required entity pair.")
    if preparation.get("publish_type") != "selective":
        raise FusionAboWorkflowError("Configure Adaptive Search preparation is not a selective publish.")
    immutable_source = _required_mapping(
        preparation.get("immutable_source"), "Adaptive Search immutable source"
    )
    archive_sha256 = _require_nonblank_string(
        immutable_source.get("archive_sha256"), "Adaptive Search archive SHA-256"
    ).casefold()
    source_sha256 = _require_nonblank_string(
        immutable_source.get("source_sha256"), "Adaptive Search source SHA-256"
    ).casefold()
    if not re.fullmatch(r"[a-f0-9]{64}", archive_sha256) or not re.fullmatch(
        r"[a-f0-9]{64}", source_sha256
    ):
        raise FusionAboWorkflowError("Configure Adaptive Search preparation has invalid immutable-source digests.")
    prepared_record_ref = _require_nonblank_string(
        value.get("prepared_record_ref"), "Adaptive Search prepared record reference"
    )
    record_path = (REPO_ROOT / prepared_record_ref).resolve()
    try:
        record_path.relative_to((REPO_ROOT / "project" / project_id).resolve())
    except ValueError as exc:
        raise FusionAboWorkflowError("Configure Adaptive Search preparation record is outside the approved project.") from exc
    if not record_path.is_file():
        raise FusionAboWorkflowError("Configure Adaptive Search preparation record is unavailable.")
    return {
        "preparation_id": preparation_id,
        "prepared_record_ref": prepared_record_ref,
        "immutable_source": {
            "archive_sha256": archive_sha256,
            "source_sha256": source_sha256,
        },
        "target": expected_target,
    }


def _safe_cpq_data_loader_preparation(
    value: Mapping[str, Any],
    *,
    project_id: str,
    target: Mapping[str, str],
    require_preflight_envelopes: bool = True,
) -> dict[str, dict[str, Any]]:
    """Keep only immutable, project-local CPQ Data Loader preparation evidence."""

    allowed = {
        "configure_fusion_abo_settings",
        "save_fusion_abo_process",
        "enable_fusion_abo",
        "configure_abo_delta_action_library_function",
    }
    result: dict[str, dict[str, Any]] = {}
    for operation_id, raw in value.items():
        if operation_id not in allowed or not isinstance(raw, Mapping):
            raise FusionAboWorkflowError("CPQ Settings Data Loader preparation contains an unsupported operation.")
        immutable = _required_mapping(raw.get("immutable_source"), "CPQ Settings immutable source")
        archive_sha = _require_nonblank_string(immutable.get("archive_sha256"), "CPQ Settings archive SHA-256").casefold()
        source_sha = _require_nonblank_string(immutable.get("source_sha256"), "CPQ Settings source SHA-256").casefold()
        if not re.fullmatch(r"[a-f0-9]{64}", archive_sha) or not re.fullmatch(r"[a-f0-9]{64}", source_sha):
            raise FusionAboWorkflowError("CPQ Settings Data Loader preparation has invalid immutable-source digests.")
        if _safe_target(raw.get("target"), "CPQ Settings Data Loader target") != dict(target):
            raise FusionAboWorkflowError("CPQ Settings Data Loader preparation targets a different environment.")
        subject = _required_mapping(raw.get("approved_subject"), "CPQ Settings approved subject")
        if subject.get("operation_id") != operation_id or subject.get("business_object") != CPQ_COMMERCE_SETTINGS_BUSINESS_OBJECT:
            raise FusionAboWorkflowError("CPQ Settings Data Loader preparation has an invalid registered business object.")
        task_hook_preview_ref = _project_relative_path(
            raw.get("task_hook_preview_path"), project_id=project_id,
            field_name="CPQ Task Hook preview", require_exists=require_preflight_envelopes,
        )
        task_hook_preview_sha = _require_nonblank_string(
            raw.get("task_hook_preview_sha256"), "CPQ Task Hook preview SHA-256"
        ).casefold()
        if not re.fullmatch(r"[a-f0-9]{64}", task_hook_preview_sha):
            raise FusionAboWorkflowError("CPQ Task Hook preview has an invalid digest.")
        if require_preflight_envelopes and _sha256_file(REPO_ROOT / task_hook_preview_ref) != task_hook_preview_sha:
            raise FusionAboWorkflowError("CPQ Task Hook preview changed after preparation.")
        task_hook_preview = _read_json_mapping(
            REPO_ROOT / task_hook_preview_ref, "CPQ Task Hook preview"
        )
        final_data = _required_mapping(task_hook_preview.get("finalData"), "CPQ Task Hook finalData")
        if final_data.get("archiveSha256") != archive_sha or final_data.get("sourceSha256") != source_sha or final_data.get("target") != dict(target) or final_data.get("approvedSubject") != dict(subject):
            raise FusionAboWorkflowError("CPQ Task Hook preview does not cover the prepared setting and target.")
        result[operation_id] = {
            "target": dict(target),
            "approved_subject": dict(subject),
            "approved_subject_sha256": _require_nonblank_string(raw.get("approved_subject_sha256"), "CPQ Settings approved subject SHA-256").casefold(),
            "immutable_source": {"archive_sha256": archive_sha, "source_sha256": source_sha},
            "source_path": _project_relative_path(raw.get("source_path"), project_id=project_id, field_name="CPQ Settings source"),
            "archive_path": _project_relative_path(raw.get("archive_path"), project_id=project_id, field_name="CPQ Settings archive"),
            "preflight_envelope_path": _project_relative_path(
                raw.get("preflight_envelope_path"),
                project_id=project_id,
                field_name="CPQ Settings preflight envelope",
                require_exists=require_preflight_envelopes,
            ),
            "task_hook_preview_path": task_hook_preview_ref,
            "task_hook_preview_sha256": task_hook_preview_sha,
            "task_hook_preview": task_hook_preview,
        }
    if not result:
        raise FusionAboWorkflowError("CPQ Settings Data Loader preparation is empty.")
    return result


def _workflow_approval_components(
    cpq_preview: Mapping[str, Any], *, project_id: str, adaptive_preparation: Mapping[str, Any],
    cpq_data_loader_preparation: Mapping[str, Any],
    require_preflight_envelopes: bool = True,
) -> dict[str, Any]:
    """Return the fixed downstream plan bound to the CPQ approval record.

    This is deliberately a scope declaration, not a child-skill payload or
    callback. Configure Adaptive Search still creates and validates its own
    immutable Data Loader source through core.data-loader before it can use
    this authorization.
    """

    target = _safe_target(cpq_preview.get("target"), "cpq_settings_preview.target")
    process_name = _require_nonblank_string(
        cpq_preview.get("validated_process_variable_name"),
        "cpq_settings_preview.validated_process_variable_name",
    )
    return {
        "cpq_settings": {
            "approval_fingerprint": _require_nonblank_string(
                cpq_preview.get("approval_fingerprint"),
                "cpq_settings_preview.approval_fingerprint",
            ),
            "plan_fingerprint": _require_nonblank_string(
                cpq_preview.get("plan_fingerprint"),
                "cpq_settings_preview.plan_fingerprint",
            ),
            "operations": list(cpq_preview.get("operations", [])),
            "data_loader_loads": _safe_cpq_data_loader_preparation(
                cpq_data_loader_preparation,
                project_id=project_id,
                target=target,
                require_preflight_envelopes=require_preflight_envelopes,
            ),
        },
        "adaptive_search": {
            "skill_id": ADAPTIVE_SEARCH_SKILL_ID,
            "task_code": ADAPTIVE_SEARCH_TASK_CODE,
            "publish_type": "selective",
            "entities": list(ADAPTIVE_SEARCH_REQUIRED_ENTITIES),
            "target": dict(adaptive_preparation["target"]),
            "preparation_id": adaptive_preparation["preparation_id"],
            "prepared_record_ref": adaptive_preparation["prepared_record_ref"],
            "immutable_source": dict(adaptive_preparation["immutable_source"]),
            "preparation_operation": "prepare_partial_publish",
            "submission_operation": "submit_partial_publish",
            "status_operation": "get_partial_publish_status",
            "submission_route": "core.data-loader",
            "status_route": "cx.sales.sales-foundation.configure-adaptive-search",
            "submission_limit": 1,
        },
        "ess_sync": {
            "submission_route": "core.fusion-api.ess-job-submitter",
            "submission_limit": 1,
            "job_definition_id": (
                "JobDefinition://oracle/apps/ess/configPriceQuote/assets/"
                "UnifiedAssetReadModelSyncMasterJob"
            ),
            "application": "CrmEss",
            "product": "CPQ",
            "request_parameters": [],
            "description": (
                "FDOS Fusion ABO Unified Asset Read Model Sync | "
                f"project={project_id} | process={process_name}"
            ),
            "precondition": {
                "adaptive_search_status": "SUCCEEDED",
                "required_entities_enabled": list(ADAPTIVE_SEARCH_REQUIRED_ENTITIES),
            },
        },
        "target": target,
    }


def build_fusion_abo_workflow_preview(
    *,
    project_id: str,
    cpq_settings_preview: Mapping[str, Any],
    adaptive_preparation: Mapping[str, Any],
    cpq_data_loader_preparation: Mapping[str, Any],
    require_preflight_envelopes: bool = True,
) -> dict[str, Any]:
    """Build the durable plan; this approval authorizes only the CPQ import."""

    safe_project_id = _require_nonblank_string(project_id, "project_id")
    issued_at = _require_nonblank_string(
        cpq_settings_preview.get("issued_at"), "cpq_settings_preview.issued_at"
    )
    issued = _parse_rfc3339_timestamp(issued_at, "cpq_settings_preview.issued_at")
    expected_cpq_expiry = issued + timedelta(seconds=WORKFLOW_APPROVAL_TTL_SECONDS)
    cpq_expires_at = _parse_rfc3339_timestamp(
        _require_nonblank_string(
            cpq_settings_preview.get("expires_at"), "cpq_settings_preview.expires_at"
        ),
        "cpq_settings_preview.expires_at",
    )
    if _utc_timestamp(cpq_expires_at) != _utc_timestamp(expected_cpq_expiry):
        raise FusionAboWorkflowError(
            "The CPQ Settings preview does not use the required workflow approval lifetime."
        )
    components = _workflow_approval_components(
        cpq_settings_preview,
        project_id=safe_project_id,
        adaptive_preparation=_safe_adaptive_preparation(
            adaptive_preparation,
            project_id=safe_project_id,
            target=_safe_target(cpq_settings_preview.get("target"), "cpq_settings_preview.target"),
        ),
        cpq_data_loader_preparation=cpq_data_loader_preparation,
        require_preflight_envelopes=require_preflight_envelopes,
    )
    approval_context = {
        "approval_version": "1.0",
        "task_code": TASK_CODE,
        "task_skill_id": TASK_SKILL_ID,
        "project_id": safe_project_id,
        "target": components["target"],
        "components": components,
        "issued_at": issued_at,
        "expires_at": _utc_timestamp(expected_cpq_expiry),
    }
    approval_fingerprint = hashlib.sha256(
        _canonical_json(approval_context).encode("utf-8")
    ).hexdigest()
    return {
        "status": "approval_required",
        "approval_version": "1.0",
        "task_code": TASK_CODE,
        "task_skill_id": TASK_SKILL_ID,
        "project_id": safe_project_id,
        "target": components["target"],
        "validated_process_variable_name": cpq_settings_preview[
            "validated_process_variable_name"
        ],
        "components": components,
        "approval_fingerprint": approval_fingerprint,
        "issued_at": issued_at,
        "expires_at": _utc_timestamp(expected_cpq_expiry),
        "approval_required": {
            "timing": "immediately_before_cpq_data_loader_upload",
            "instruction": (
                "Approve only this exact CPQ Settings Data Loader import containing the selected "
                "process, enableFusionABO=Yes, and the fixed ABO delta-action Library Function. "
                "Adaptive Search and ESS each require a later, separate approval."
            ),
        },
        "failure_policy": {
            "automatic_cpq_data_loader_retry": False,
            "automatic_adaptive_search_republish": False,
            "automatic_ess_resubmission": False,
            "expired_approval_action": "Rerun read-only validation and request a new CPQ approval.",
        },
    }


def _safe_target(value: Any, field_name: str) -> dict[str, str]:
    target = _required_mapping(value, field_name)
    return {
        "environment": _require_nonblank_string(target.get("environment"), f"{field_name}.environment"),
        "fusion_host": _require_nonblank_string(target.get("fusion_host"), f"{field_name}.fusion_host"),
        "cpq_host": _require_nonblank_string(target.get("cpq_host"), f"{field_name}.cpq_host"),
    }


def _assert_cpq_settings_approval_is_current(preview: Mapping[str, Any]) -> None:
    """Fail closed unless the immutable workflow approval is current."""

    issued_at = _parse_rfc3339_timestamp(
        _require_nonblank_string(preview.get("issued_at"), "CPQ Settings approval issued_at"),
        "CPQ Settings approval issued_at",
    )
    expires_at = _parse_rfc3339_timestamp(
        _require_nonblank_string(preview.get("expires_at"), "CPQ Settings approval expires_at"),
        "CPQ Settings approval expires_at",
    )
    expected_expires_at = issued_at + timedelta(seconds=CPQ_SETTINGS_APPROVAL_TTL_SECONDS)
    if _utc_timestamp(expires_at) != _utc_timestamp(expected_expires_at):
        raise FusionAboWorkflowError(
            "The Fusion ABO workflow approval has an invalid expiration window. Create a new preview."
        )
    now = datetime.now(timezone.utc).replace(microsecond=0)
    if issued_at > now or now > expires_at:
        raise FusionAboWorkflowError(
            "The Fusion ABO workflow approval is not current. Create and approve a fresh preview."
        )


def _validate_cpq_settings_approval(
    args: argparse.Namespace,
    preview: Mapping[str, Any],
) -> None:
    """Validate the current CPQ approval used by this command."""

    if preview.get("approval_fingerprint") != args.approval_fingerprint:
        raise FusionAboWorkflowError(
            "The CPQ Settings approval is stale or does not match the current target and preflight. "
            "Create and approve a new preview."
        )
    issued_at = _parse_rfc3339_timestamp(args.approval_issued_at, "approval_issued_at")
    if _utc_timestamp(issued_at) != preview.get("issued_at"):
        raise FusionAboWorkflowError(
            "The CPQ Settings approval timestamp does not match the approved preview."
        )
    _assert_cpq_settings_approval_is_current(preview)


def build_shared_optin_command(
    args: argparse.Namespace,
    *,
    feature_code: str,
    feature_choice: str,
) -> list[str]:
    """Return the one-feature delegated writer command without any secret values."""

    if not SHARED_OPTIN_WRAPPER.is_file():
        raise FusionAboWorkflowError("The existing shared FSM Set Optin Features writer is unavailable.")
    command = [
        sys.executable,
        str(SHARED_OPTIN_WRAPPER),
        "--properties",
        args.properties,
        "--feature-code",
        feature_code,
        "--action",
        "set-choices",
        "--feature-choices",
        feature_choice,
        "--project-id",
        args.project_id,
        "--token-cache",
        args.fusion_token_cache,
        "--boss-token-cache",
        args.boss_token_cache,
        "--fusion-common-token-cache",
        args.fusion_common_token_cache,
    ]
    if args.redirect_url:
        command.extend(["--redirect-url", args.redirect_url])
    if args.auth_code:
        command.extend(["--auth-code", args.auth_code])
    if args.no_open_browser:
        command.append("--no-open-browser")
    if args.force_fusion_login:
        command.append("--force-login")
    return command


def run_shared_optin_writer(
    command: list[str],
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    """Delegate one approved write without replaying or exposing its output."""

    completed = runner(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise FusionAboWorkflowError(
            "The shared FSM Set Optin Features workflow failed. No CPQ setting was changed; inspect its sanitized project report before any new approval."
        )
    # The shared OAuth helper may print safe login progress before its final
    # machine-readable result.  Locate the one JSON object that consumes the
    # end of stdout instead of assuming stdout contains JSON only.
    payload: Any | None = None
    decoder = json.JSONDecoder()
    for start, character in enumerate(completed.stdout):
        if character != "{":
            continue
        try:
            candidate, end = decoder.raw_decode(completed.stdout[start:])
        except json.JSONDecodeError:
            continue
        if not completed.stdout[start + end :].strip():
            payload = candidate
            break
    if payload is None:
        raise FusionAboWorkflowError(
            "The shared FSM Set Optin Features workflow returned an unreadable result. Treat the feature update as indeterminate and reread feature state before retrying."
        )
    if not isinstance(payload, Mapping) or payload.get("ok") is not True:
        raise FusionAboWorkflowError(
            "The shared FSM Set Optin Features workflow did not confirm a completed operation. Treat the feature update as indeterminate."
        )
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise FusionAboWorkflowError(
            "The shared FSM Set Optin Features workflow did not return its required summary."
        )
    if summary.get("dryRun") is not False or not isinstance(summary.get("patchResult"), Mapping):
        raise FusionAboWorkflowError(
            "The shared FSM Set Optin Features workflow did not confirm one live Fusion Common PATCH. Treat the feature update as indeterminate."
        )
    return {
        "status": "submitted",
        "process_output_path": summary.get("processOutputPath"),
        "standard_report_path": summary.get("standardReportPath"),
        "token_usage_log_path": summary.get("tokenUsageLogPath"),
        "patch_status_present": True,
        "refresh_status_present": "refreshResult" in summary,
    }


def _run_preflight_from_args(
    args: argparse.Namespace, *, properties: Mapping[str, str] | None = None
) -> tuple[dict[str, Any], CpqSettingsClient, FeatureStatesReader]:
    """Run preflight with a single immutable local profile snapshot."""

    profile = dict(properties) if properties is not None else _read_properties(args.properties)
    target = _target_evidence_from_properties(profile)
    settings_client = _cpq_client_from_args(args, properties=profile)
    feature_states_reader = _feature_states_reader_from_args(args, properties=profile)
    result = run_read_only_preflight(
        settings_client,
        feature_states_reader,
        args.process_variable_name,
        target=target,
        use_default_process=getattr(args, "use_default_process", False),
    )
    return result, settings_client, feature_states_reader


def execute_approved_prerequisite_update(args: argparse.Namespace) -> dict[str, Any]:
    """Perform one explicit, approved Fusion prerequisite update then reread state.

    The caller must supply the fingerprint from ``preview-prerequisite-update``
    and a current ``--approve-prerequisite-update`` confirmation.  A mismatch
    means the preview is stale and no writer command is executed.
    """

    if not args.approve_prerequisite_update:
        raise FusionAboWorkflowError(
            "--execute-approved-prerequisite-update requires --approve-prerequisite-update after current explicit approval."
        )
    if not args.project_id:
        raise FusionAboWorkflowError(
            "--execute-approved-prerequisite-update requires --project-id so the shared writer can persist its governed records."
        )
    current_preflight, settings_client, feature_states_reader = _run_preflight_from_args(args)
    current_preview = build_prerequisite_update_preview(
        current_preflight,
        feature_code=args.feature_code,
        feature_choice=args.feature_choice,
    )
    if current_preview["approval_fingerprint"] != args.approval_fingerprint:
        raise FusionAboWorkflowError(
            "The approval preview is stale or targets different state. No Fusion update was sent; create and approve a new preview."
        )

    # This is the one approved mutation in this command.  A writer error is
    # deliberately indeterminate instead of retryable: the external PATCH may
    # have reached Fusion even when FDOS did not receive a usable result.
    safe_target = _safe_target(
        current_preflight.get("target"), "Current preflight target evidence"
    )
    try:
        writer_result = run_shared_optin_writer(
            build_shared_optin_command(
                args,
                feature_code=args.feature_code,
                feature_choice=args.feature_choice,
            )
        )
    except Exception as exc:
        message, provider_error = _with_safe_provider_detail(
            "The approved Fusion prerequisite update could not be confirmed. "
            "Its state may have changed; no automatic retry was attempted. "
            "No CPQ setting was changed.",
            exc,
        )
        result: dict[str, Any] = {
            "status": "prerequisite_update_indeterminate",
            "stage": "fusion_prerequisite_update",
            "failure_class": "fusion_prerequisite_update_indeterminate",
            "task_code": TASK_CODE,
            "task_name": TASK_NAME,
            "environment": safe_target["environment"],
            "target": safe_target,
            "message": message,
            "side_effects": (
                "One approved Fusion prerequisite update may have been attempted through the shared "
                "writer. No CPQ setting was changed and no automatic retry was attempted."
            ),
            "next_action": (
                "Reread all required Fusion feature states through the approved read-only route before "
                "deciding on recovery or requesting a new approval."
            ),
        }
        if provider_error:
            result["provider_error"] = provider_error
        return result

    # Do not retry a mutation. One fresh state read decides whether the update
    # is complete; if it is not, the caller must reconcile before a new approval.
    try:
        stage_codes = current_preflight.get("prerequisite_feature_codes")
        if not isinstance(stage_codes, list) or not stage_codes:
            raise FusionAboWorkflowError("Current preflight does not identify the approved prerequisite stage.")
        post_update_states = feature_states_reader.read(
            tuple(stage_codes),
            feature_mode="COMBO",
        )
    except Exception as exc:
        message, provider_error = _with_safe_provider_detail(
            "A fresh Fusion prerequisite read could not confirm the approved update. "
            "No CPQ setting was changed and no automatic retry was attempted.",
            exc,
        )
        result = {
            "status": "prerequisite_update_verification_blocked",
            "stage": "fusion_prerequisite_update_verification",
            "failure_class": "fusion_prerequisite_update_verification",
            "task_code": TASK_CODE,
            "task_name": TASK_NAME,
            "environment": safe_target["environment"],
            "target": safe_target,
            "message": message,
            "shared_writer": writer_result,
            "side_effects": (
                "One approved Fusion prerequisite update was submitted through the shared writer, but "
                "its fresh verification could not complete. No CPQ setting was changed and no automatic "
                "retry was attempted."
            ),
            "next_action": (
                "Reread all required Fusion feature states through the approved read-only route before "
                "deciding on recovery or requesting a new approval."
            ),
        }
        if provider_error:
            result["provider_error"] = provider_error
        return result
    if not all(post_update_states.feature_states.values()):
        return {
            "status": "prerequisite_update_verification_failed",
            "stage": "fusion_prerequisite_update_verification",
            "failure_class": "fusion_prerequisite_update_verification",
            "task_code": TASK_CODE,
            "task_name": TASK_NAME,
            "environment": safe_target["environment"],
            "target": safe_target,
            "message": (
                "The approved Fusion prerequisite update completed, but a fresh read shows that one or "
                "more required prerequisites are still not enabled. No CPQ setting was changed."
            ),
            "shared_writer": writer_result,
            "feature_state_read": post_update_states.as_dict(),
            "side_effects": "One approved Fusion prerequisite update was submitted through the shared writer. No CPQ setting was changed.",
            "next_action": "Stop. Reconcile the exact current feature states and obtain a new approval before any additional opt-in update. Do not retry automatically.",
        }

    # Fresh CPQ and Fusion reads are required before this task can advance.
    try:
        final_preflight = run_read_only_preflight(
            settings_client,
            feature_states_reader,
            args.process_variable_name,
            target=safe_target,
            use_default_process=getattr(args, "use_default_process", False),
        )
    except Exception as exc:
        message, provider_error = _with_safe_provider_detail(
            "The approved Fusion prerequisite update completed, but the required fresh CPQ and Fusion "
            "verification could not finish safely. No CPQ setting was changed and no automatic retry was "
            "attempted.",
            exc,
        )
        result = {
            "status": "prerequisite_update_final_preflight_blocked",
            "stage": "fusion_prerequisite_final_preflight",
            "failure_class": "post_update_preflight",
            "task_code": TASK_CODE,
            "task_name": TASK_NAME,
            "environment": safe_target["environment"],
            "target": safe_target,
            "message": message,
            "shared_writer": writer_result,
            "side_effects": (
                "One approved Fusion prerequisite update was submitted through the shared writer. No CPQ "
                "setting was changed and no automatic retry was attempted."
            ),
            "next_action": (
                "Reread the required CPQ and Fusion state through approved read-only routes before "
                "deciding on recovery or requesting a new approval."
            ),
        }
        if provider_error:
            result["provider_error"] = provider_error
        return result
    final_preflight["shared_writer"] = writer_result
    final_preflight["side_effects"] = (
        "One approved Fusion prerequisite update was submitted through the shared writer. "
        "Fresh CPQ and Fusion reads completed afterward. No CPQ setting was changed."
    )
    return final_preflight


def _cpq_oauth_options_from_args(args: argparse.Namespace) -> CpqOAuthOptions:
    """Pass only existing local OAuth options to the narrowly-scoped core writer."""

    return CpqOAuthOptions(
        redirect_url=args.redirect_url,
        auth_code=args.auth_code,
        code_verifier=args.code_verifier,
        open_browser=not args.no_open_browser,
        callback_timeout=args.callback_timeout,
    )


def _prepare_cpq_settings_write(
    args: argparse.Namespace,
    *,
    preview_issued_at: datetime | None = None,
    approved_plan_fingerprint: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    """Recreate authoritative state, canonical plan, and a target-bound preview.

    This helper deliberately accepts no cached preflight or caller-provided
    plan.  Both commands use it so a prior read cannot become a write input.
    """

    properties = _read_properties(args.properties)
    preflight, _, _ = _run_preflight_from_args(args, properties=properties)
    try:
        plan = build_fusion_abo_cpq_settings_write_plan(preflight)
        if approved_plan_fingerprint and hashlib.sha256(
            _canonical_json(plan).encode("utf-8")
        ).hexdigest() != approved_plan_fingerprint:
            # Existing approvals retain their exact original wording and digest.
            # Only this stored, target-bound approval can select the legacy plan.
            legacy_plan = build_fusion_abo_cpq_settings_write_plan(
                preflight, legacy_failure_guidance=True
            )
            if hashlib.sha256(_canonical_json(legacy_plan).encode("utf-8")).hexdigest() == approved_plan_fingerprint:
                plan = legacy_plan
        preview = build_cpq_settings_write_preview(
            oauth_properties=properties,
            fusion_abo_preflight_result=preflight,
            plan=plan,
            now=preview_issued_at,
        )
    except (CpqSettingsWritePlanError, CpqSettingsWriteExecutorError) as exc:
        message, provider_error = _with_safe_provider_detail(
            "The CPQ Settings write plan could not be prepared safely before any CPQ Settings Data Loader import was attempted.",
            exc,
        )
        wrapped = FusionAboWorkflowError(message)
        if provider_error:
            wrapped.provider_error = provider_error
        raise wrapped from exc
    return preflight, plan, preview, properties


def _run_json_command(
    command: Sequence[str],
    *,
    stage: str,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    """Run a selected child/core route and accept only its JSON result.

    The controller deliberately does not surface a child stderr payload.  Core
    adapters own their diagnostic redaction, while this parent retains only
    the structured, non-secret operation result required for orchestration.
    """

    completed = runner(list(command), check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise FusionAboWorkflowError(f"{stage} could not continue safely.")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise FusionAboWorkflowError(f"{stage} did not return its required structured result.") from exc
    if not isinstance(payload, dict):
        raise FusionAboWorkflowError(f"{stage} did not return a JSON object.")
    return payload


def _project_relative_path(
    path_value: Any, *, project_id: str, field_name: str, require_exists: bool = True
) -> str:
    """Canonicalize a child artifact path without accepting outside locations."""

    raw = _require_nonblank_string(path_value, field_name)
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    resolved = candidate.resolve()
    project_root = (REPO_ROOT / "project" / _safe_project_id(project_id)).resolve()
    try:
        resolved.relative_to(project_root)
    except ValueError as exc:
        raise FusionAboWorkflowError(f"{field_name} resolves outside the approved project workspace.") from exc
    if require_exists and not resolved.is_file():
        raise FusionAboWorkflowError(f"{field_name} is unavailable.")
    return _relative_to_repo(resolved)


def _prepare_adaptive_search_publish(
    args: argparse.Namespace,
    *,
    project_root: Path,
    cpq_preview: Mapping[str, Any],
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    """Call only the child read-only preparation route before the one approval."""

    request = {
        "schema_version": "1.0",
        "operation": "prepare_partial_publish",
        "project_id": _safe_project_id(args.project_id),
        "target": _adaptive_search_target(
            _safe_target(cpq_preview.get("target"), "cpq_settings_preview.target")
        ),
        "entities": list(ADAPTIVE_SEARCH_REQUIRED_ENTITIES),
        "publish_type": "selective",
    }
    request_path = (
        project_root
        / TASK_ARTIFACT_DIRECTORY
        / f"adaptive-search-preparation-request-{uuid.uuid4().hex}.json"
    )
    internal_output_path = request_path.with_name(
        request_path.name.replace("-request-", "-internal-")
    )
    _write_json_atomic(request_path, request)
    result = _run_json_command(
        [
            sys.executable,
            str(ADAPTIVE_SEARCH_EXECUTOR),
            "--prepare-request",
            str(request_path),
            "--project-root",
            str(project_root),
            "--properties",
            args.properties,
            "--token-cache",
            args.fusion_token_cache,
            "--internal-output",
            str(internal_output_path),
        ],
        stage="Configure Adaptive Search preparation",
        runner=runner,
    )
    internal_result = _read_json_mapping(
        internal_output_path, "Configure Adaptive Search preparation descriptor"
    )
    prepared_record_ref = _project_relative_path(
        internal_result.get("prepared_record_path"),
        project_id=args.project_id,
        field_name="Configure Adaptive Search prepared record",
    )
    return {
        "preparation": _required_mapping(result.get("preparation"), "Configure Adaptive Search preparation"),
        "prepared_record_ref": prepared_record_ref,
    }


def _prepare_cpq_settings_data_loader(
    args: argparse.Namespace,
    *, project_root: Path, plan: Mapping[str, Any], cpq_preview: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    """Prepare the CPQ setting archive before its Task Hook approval."""

    try:
        loads = prepare_cpq_settings_data_loader_loads(
            plan=plan,
            target=_safe_target(cpq_preview.get("target"), "cpq_settings_preview.target"),
            project_root=project_root,
            properties=Path(args.properties),
            token_cache=args.fusion_token_cache,
        )
        return prepare_cpq_task_hook_previews(loads=loads, project_root=project_root)
    except CpqSettingsWriteExecutorError as exc:
        raise FusionAboWorkflowError(str(exc)) from exc


def preview_cpq_settings_write(args: argparse.Namespace) -> dict[str, Any]:
    """Create the immutable CPQ approval preview and downstream plan."""

    if not args.project_id:
        raise FusionAboWorkflowError(
            "--preview-cpq-settings-write requires --project-id for its sanitized project record."
        )
    # Validate the workspace before selected read-only routes start OAuth or
    # make external GET calls. A preview must have somewhere safe to persist.
    _, project_root, _, _, _, _ = _project_workspace(args.project_id)
    preflight, plan, cpq_preview, _ = _prepare_cpq_settings_write(args)
    cpq_data_loader_preparation = _prepare_cpq_settings_data_loader(
        args, project_root=project_root, plan=plan, cpq_preview=cpq_preview
    )
    adaptive_preparation = _prepare_adaptive_search_publish(
        args,
        project_root=project_root,
        cpq_preview=cpq_preview,
    )
    preview = build_fusion_abo_workflow_preview(
        project_id=args.project_id,
        cpq_settings_preview=cpq_preview,
        adaptive_preparation=adaptive_preparation,
        cpq_data_loader_preparation=cpq_data_loader_preparation,
    )
    presentation_context: dict[str, Any] = {
        "feature_states": dict(
            _required_mapping(preflight.get("feature_states"), "Fresh preflight feature states")
        ),
        "validated_process_variable_name": preview["validated_process_variable_name"],
    }
    if preflight.get("status") == "requires_abo_delta_action_library_function_recovery":
        cpq_state = _required_mapping(preflight.get("cpq_preflight"), "Recovery CPQ preflight")
        function_state = _required_mapping(
            cpq_state.get("abo_delta_action_library_function"), "Current Library Function"
        )
        current_function = function_state.get("configured_function")
        if current_function is not None and not isinstance(current_function, str):
            raise FusionAboWorkflowError("Current Library Function is not a valid display value.")
        presentation_context["cpq_function_recovery_current_value"] = current_function
    persistence = _write_workspace_preview_record(
        project_id_value=args.project_id,
        preview=preview,
        trigger="Fusion ABO complete enablement workflow preview",
        preview_stage="fusion_abo_workflow_preview",
        run_kind="fusion-abo-workflow-preview",
        artifact_prefix="fusion-abo-workflow-preview",
        artifact_name="Fusion ABO Complete Enablement Workflow Preview",
        inputs=[
            "fresh_cpq_and_fusion_preflight",
            "canonical_cpq_settings_write_plan",
            "validated_immutable_cpq_settings_data_loader_sources",
            "validated_immutable_adaptive_search_source",
            "fixed_conditional_ess_scope",
        ],
        notes=(
            "Read-only Fusion ABO plan completed; the first explicit approval covers only the "
            "exact prepared CPQ Settings Data Loader source. Publish and ESS have later gates."
        ),
        token_notes="Token estimate for the sanitized complete Fusion ABO workflow preview.",
    )
    result = dict(preview)
    # The current readback is for presentation only; the immutable approval
    # preview and every execution payload retain their existing shape.
    result["presentation_context"] = presentation_context
    result["project_artifact_ref"] = persistence["artifact_ref"]
    result["project_run_ref"] = persistence["run_ref"]
    result["side_effects"] = (
        "Fresh CPQ and Fusion preflight plus CPQ Settings and Adaptive Search source preparation completed. No CPQ Settings Data Loader import, Adaptive Search publish request, or ESS POST was attempted."
    )
    return result


def _adaptive_preparation_from_preview(preview: Mapping[str, Any]) -> dict[str, Any]:
    """Recreate the child preparation input from an immutable parent preview."""

    components = _required_mapping(preview.get("components"), "workflow preview components")
    adaptive = _required_mapping(components.get("adaptive_search"), "workflow preview adaptive_search")
    return {
        "preparation": {
            "schema_version": "1.0",
            "preparation_id": adaptive.get("preparation_id"),
            "state": "PREPARED",
            "project_id": preview.get("project_id"),
            "target": adaptive.get("target"),
            "entities": adaptive.get("entities"),
            "publish_type": adaptive.get("publish_type"),
            "immutable_source": adaptive.get("immutable_source"),
        },
        "prepared_record_ref": adaptive.get("prepared_record_ref"),
    }


def _verify_stored_workflow_preview(
    preview: Mapping[str, Any], *, require_current: bool = True
) -> dict[str, Any]:
    """Recompute the stored approval fingerprint and validate its source record."""

    components = _required_mapping(preview.get("components"), "workflow preview components")
    cpq_component = _required_mapping(
        components.get("cpq_settings"), "workflow preview CPQ component"
    )
    reconstructed = build_fusion_abo_workflow_preview(
        project_id=_require_nonblank_string(preview.get("project_id"), "workflow preview project_id"),
        cpq_settings_preview=_required_mapping(
            {
                "target": preview.get("target"),
                "validated_process_variable_name": preview.get("validated_process_variable_name"),
                "issued_at": preview.get("issued_at"),
                "expires_at": preview.get("expires_at"),
                "approval_fingerprint": cpq_component.get("approval_fingerprint"),
                "plan_fingerprint": cpq_component.get("plan_fingerprint"),
                "operations": cpq_component.get("operations", []),
            },
            "workflow preview CPQ component",
        ),
        adaptive_preparation=_adaptive_preparation_from_preview(preview),
        cpq_data_loader_preparation=_required_mapping(
            cpq_component.get("data_loader_loads"), "workflow preview CPQ Data Loader preparation"
        ),
        require_preflight_envelopes=require_current,
    )
    if reconstructed.get("approval_fingerprint") != preview.get("approval_fingerprint"):
        raise FusionAboWorkflowError("The persisted Fusion ABO approval record is internally inconsistent.")
    if require_current:
        _assert_cpq_settings_approval_is_current(reconstructed)
    return reconstructed


def _load_approved_workflow_preview(
    args: argparse.Namespace,
    *,
    require_current: bool = True,
) -> tuple[dict[str, Any], str, str]:
    """Resolve exactly one durable, current parent approval record.

    Execution never uses a caller-supplied preview path.  That prevents a
    command line from substituting a new target, source, or child preparation
    after the user approved the persisted preview.
    """

    _, project_root, _, _, _, _ = _project_workspace(args.project_id)
    approval_issued_at = _parse_rfc3339_timestamp(args.approval_issued_at, "approval_issued_at")
    candidates: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted((project_root / TASK_ARTIFACT_DIRECTORY).glob("fusion-abo-workflow-preview-*.json")):
        try:
            record = _read_json_mapping(path, "Fusion ABO workflow preview record")
        except FusionAboWorkflowError:
            continue
        preview = record.get("preview")
        if not isinstance(preview, Mapping):
            continue
        if (
            record.get("status") == "approval_required"
            and record.get("stage") == "fusion_abo_workflow_preview"
            and preview.get("project_id") == args.project_id
            and preview.get("approval_fingerprint") == args.approval_fingerprint
            and preview.get("issued_at") == _utc_timestamp(approval_issued_at)
        ):
            candidates.append((path, dict(preview)))
    if len(candidates) != 1:
        raise FusionAboWorkflowError(
            "The approved Fusion ABO workflow record is missing or ambiguous; create and approve one fresh preview."
        )
    path, stored = candidates[0]
    preview = _verify_stored_workflow_preview(stored, require_current=require_current)
    if require_current:
        _validate_cpq_settings_approval(args, preview)
    return preview, _relative_to_repo(path), _sha256_file(path)


def _load_workflow_preview_by_fingerprint(
    args: argparse.Namespace,
    *,
    approval_fingerprint: str,
    require_current: bool = False,
) -> tuple[dict[str, Any], str, str]:
    """Resolve one parent workflow by its durable approval fingerprint."""

    fingerprint = _require_nonblank_string(
        approval_fingerprint, "workflow approval fingerprint"
    ).casefold()
    if not re.fullmatch(r"[a-f0-9]{64}", fingerprint):
        raise FusionAboWorkflowError("Workflow approval fingerprint is invalid.")
    _, project_root, _, _, _, _ = _project_workspace(args.project_id)
    candidates: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted((project_root / TASK_ARTIFACT_DIRECTORY).glob("fusion-abo-workflow-preview-*.json")):
        try:
            record = _read_json_mapping(path, "Fusion ABO workflow preview record")
        except FusionAboWorkflowError:
            continue
        preview = record.get("preview")
        if not isinstance(preview, Mapping):
            continue
        if (
            record.get("status") == "approval_required"
            and record.get("stage") == "fusion_abo_workflow_preview"
            and preview.get("project_id") == args.project_id
            and str(preview.get("approval_fingerprint") or "").casefold() == fingerprint
        ):
            candidates.append((path, dict(preview)))
    if len(candidates) != 1:
        raise FusionAboWorkflowError(
            "The approved Fusion ABO workflow record is missing or ambiguous for the supplied fingerprint."
        )
    path, stored = candidates[0]
    preview = _verify_stored_workflow_preview(stored, require_current=require_current)
    if require_current:
        _validate_cpq_settings_approval(args, preview)
    return preview, _relative_to_repo(path), _sha256_file(path)


def _adaptive_approval_preview_values(
    path_value: str, *, project_id: str
) -> tuple[str, str]:
    """Read the child approval preview and return its bound parent and digest."""

    preview_ref = _project_relative_path(
        path_value,
        project_id=project_id,
        field_name="Adaptive Search approval preview",
    )
    payload = _read_json_mapping(REPO_ROOT / preview_ref, "Adaptive Search approval preview")
    approval = _required_mapping(
        payload.get("approval_required"), "Adaptive Search approval_required"
    )
    preview_sha = _require_nonblank_string(
        approval.get("preview_sha256"), "Adaptive Search preview SHA-256"
    ).casefold()
    if not re.fullmatch(r"[a-f0-9]{64}", preview_sha):
        raise FusionAboWorkflowError("Adaptive Search approval preview digest is invalid.")
    task_hook_preview = _required_mapping(
        approval.get("preview"), "Adaptive Search Task Hook preview"
    )
    final_data = _required_mapping(
        task_hook_preview.get("finalData"), "Adaptive Search Task Hook finalData"
    )
    workflow_fingerprint = _require_nonblank_string(
        final_data.get("workflowApprovalFingerprint"),
        "Adaptive Search workflow approval fingerprint",
    ).casefold()
    if not re.fullmatch(r"[a-f0-9]{64}", workflow_fingerprint):
        raise FusionAboWorkflowError(
            "Adaptive Search approval preview has an invalid workflow approval fingerprint."
        )
    return workflow_fingerprint, preview_sha


def _validate_fresh_cpq_preview_against_approval(
    *, approved_preview: Mapping[str, Any], fresh_cpq_preview: Mapping[str, Any]
) -> None:
    """Ensure current CPQ reads still produce the exact approved write plan."""

    components = _required_mapping(approved_preview.get("components"), "approved workflow components")
    approved_cpq = _required_mapping(components.get("cpq_settings"), "approved CPQ component")
    for field in ("approval_fingerprint", "plan_fingerprint", "operations"):
        if fresh_cpq_preview.get(field) != approved_cpq.get(field):
            raise FusionAboWorkflowError(
                "Fresh CPQ validation no longer matches the approved Fusion ABO workflow; no CPQ Settings Data Loader import was attempted."
            )
    if _safe_target(fresh_cpq_preview.get("target"), "fresh CPQ target") != _safe_target(
        approved_preview.get("target"), "approved workflow target"
    ):
        raise FusionAboWorkflowError(
            "Fresh CPQ validation targets a different environment than the approved Fusion ABO workflow."
        )
    if fresh_cpq_preview.get("issued_at") != approved_preview.get("issued_at") or fresh_cpq_preview.get(
        "expires_at"
    ) != approved_preview.get("expires_at"):
        raise FusionAboWorkflowError("Fresh CPQ validation did not preserve the exact approved time window.")


def _adaptive_target_from_workflow_preview(workflow_preview: Mapping[str, Any]) -> dict[str, Any]:
    components = _required_mapping(workflow_preview.get("components"), "workflow preview components")
    adaptive = _required_mapping(components.get("adaptive_search"), "workflow preview adaptive_search")
    return dict(_required_mapping(adaptive.get("target"), "workflow preview adaptive target"))


def _cpq_operations_from_reconciliation(
    *,
    preflight: Mapping[str, Any],
    operation_id: str,
    data_set_name: str,
    data_load_status: str,
    loaded: int,
    errors: int,
    skipped: int,
) -> list[dict[str, Any]]:
    """Build the exact CPQ predecessor contract from read-only reconciliation evidence."""

    normalized_status = data_load_status.strip().casefold()
    if normalized_status not in {"success", "succeeded"}:
        raise FusionAboWorkflowError("CPQ Data Load Status must be Success before Adaptive Search preview.")
    if loaded < 1 or errors != 0 or skipped != 0:
        raise FusionAboWorkflowError("CPQ Data Load Status must show at least one loaded row and zero errors/skips.")
    cpq = _required_mapping(preflight.get("cpq_preflight"), "reconciliation CPQ preflight")
    settings = _required_mapping(cpq.get("commerce_settings"), "reconciliation commerce settings")
    function_read = _required_mapping(
        cpq.get("abo_delta_action_library_function"),
        "reconciliation ABO delta-action library function",
    )
    settings_audit = _required_mapping(settings.get("audit_summary"), "Commerce Settings readback audit")
    function_audit = _required_mapping(function_read.get("audit_summary"), "Library Function readback audit")
    if settings.get("enable_fusion_abo") != "Yes":
        raise FusionAboWorkflowError("CPQ readback does not prove enableFusionABO = Yes.")
    if not function_read.get("is_expected"):
        raise FusionAboWorkflowError("CPQ readback does not prove the fixed ABO delta-action Library Function.")
    completed = [
        {
            "id": operation_id,
            "status": "completed",
            "data_loader_status": "SUCCEEDED",
            "data_set_name": data_set_name,
            "loaded": loaded,
            "errors": errors,
            "skipped": skipped,
        },
    ]
    if operation_id == "configure_fusion_abo_settings":
        completed.append({
            "id": "verify_fusion_abo_enabled",
            "status": "completed",
            "method": settings_audit.get("method"),
            "http_status": settings_audit.get("http_status"),
            "endpoint_path": settings_audit.get("endpoint_path"),
        })
    completed.append({
        "id": "verify_abo_delta_action_library_function",
        "status": "completed",
        "method": function_audit.get("method"),
        "http_status": function_audit.get("http_status"),
        "endpoint_path": function_audit.get("endpoint_path"),
    })
    return completed


def _recovery_preexisting_cpq_readback(
    preflight: Mapping[str, Any], process_name: str,
) -> dict[str, Any]:
    """Preserve the GET evidence that recovery starts with Fusion ABO enabled."""

    cpq = _required_mapping(preflight.get("cpq_preflight"), "recovery CPQ preflight")
    settings = _required_mapping(cpq.get("commerce_settings"), "recovery Commerce Settings")
    audit = _required_mapping(settings.get("audit_summary"), "recovery Commerce Settings GET audit")
    if (
        settings.get("enable_fusion_abo") != "Yes"
        or settings.get("fusion_abo_process_variable_name") != process_name
        or audit.get("method") != "GET"
        or audit.get("http_status") != 200
    ):
        raise FusionAboWorkflowError("Recovery lacks verified preexisting Fusion ABO Commerce Settings.")
    return {
        "status": "verified",
        "method": "GET",
        "http_status": 200,
        "enable_fusion_abo": "Yes",
        "process_variable_name": process_name,
    }


def reconcile_cpq_settings_write_from_args(args: argparse.Namespace) -> dict[str, Any]:
    """Promote a prior indeterminate CPQ write only from read-only reconciliation evidence."""

    preview, approval_record_ref, approval_record_fingerprint = _load_approved_workflow_preview(
        args, require_current=False
    )
    _, project_root, _, _, _, _ = _project_workspace(args.project_id)
    workflow_record_path = _workflow_record_path(project_root, preview["approval_fingerprint"])
    preflight = _read_json_mapping(Path(args.preflight_result), "CPQ reconciliation preflight result")
    if preflight.get("status") != "already_configured":
        raise FusionAboWorkflowError("CPQ reconciliation requires a fresh already_configured preflight result.")
    if _safe_target(preflight.get("target"), "reconciliation preflight target") != _safe_target(
        preview.get("target"), "approved workflow target"
    ):
        raise FusionAboWorkflowError("CPQ reconciliation target differs from the approved Fusion ABO workflow.")
    cpq = _required_mapping(preflight.get("cpq_preflight"), "reconciliation CPQ preflight")
    process_validation = _required_mapping(cpq.get("process_validation"), "reconciliation process validation")
    process_name = _require_nonblank_string(
        process_validation.get("process_variable_name"), "reconciliation process variable name"
    )
    if process_name != preview.get("validated_process_variable_name") or process_validation.get("process_type") != 0:
        raise FusionAboWorkflowError("CPQ reconciliation does not prove the approved Standard Process.")
    components = _required_mapping(preview.get("components"), "approved workflow components")
    cpq_component = _required_mapping(components.get("cpq_settings"), "approved CPQ component")
    loads = _required_mapping(cpq_component.get("data_loader_loads"), "approved CPQ Data Loader loads")
    if len(loads) != 1 or next(iter(loads)) not in {
        "configure_fusion_abo_settings", "configure_abo_delta_action_library_function"
    }:
        raise FusionAboWorkflowError("Reconciliation requires one exact approved CPQ Settings load.")
    operation_id = next(iter(loads))
    load = _required_mapping(loads[operation_id], "approved CPQ settings load")
    approved_operations = cpq_component.get("operations")
    if not isinstance(approved_operations, list) or [
        item.get("id") for item in approved_operations
        if isinstance(item, Mapping) and item.get("id") in {
            "configure_fusion_abo_settings", "configure_abo_delta_action_library_function"
        }
    ] != [operation_id]:
        raise FusionAboWorkflowError("Reconciliation load differs from the approved CPQ operation.")
    operations = _cpq_operations_from_reconciliation(
        preflight=preflight,
        operation_id=operation_id,
        data_set_name=_require_nonblank_string(args.data_set_name, "data_set_name"),
        data_load_status=_require_nonblank_string(args.data_load_status, "data_load_status"),
        loaded=args.loaded,
        errors=args.errors,
        skipped=args.skipped,
    )
    preexisting = (
        _recovery_preexisting_cpq_readback(preflight, process_name)
        if operation_id == "configure_abo_delta_action_library_function" else None
    )
    archive_name = Path(_require_nonblank_string(load.get("archive_path"), "approved CPQ archive path")).name
    if archive_name != args.data_set_name:
        raise FusionAboWorkflowError("CPQ Data Load Status does not match the approved CPQ Settings archive.")
    with _workflow_lock(project_root, preview["approval_fingerprint"]):
        if not workflow_record_path.is_file():
            raise FusionAboWorkflowError("No persisted CPQ workflow checkpoint exists to reconcile.")
        workflow_record = _read_json_mapping(workflow_record_path, "automatic Fusion ABO workflow record")
        if (
            workflow_record.get("approval_record_ref") != approval_record_ref
            or workflow_record.get("approval_record_fingerprint") != approval_record_fingerprint
        ):
            raise FusionAboWorkflowError("The persisted automatic workflow does not match the approved provenance record.")
        if workflow_record.get("state") not in {"cpq_not_completed", "cpq_completed"}:
            raise FusionAboWorkflowError("Only a prior CPQ-not-completed checkpoint may be reconciled.")
        workflow_record.update(
            {
                "state": "cpq_completed",
                "cpq_verification": {
                    "status": "completed",
                    "target": _safe_target(preview.get("target"), "approved workflow target"),
                    "validated_process_variable_name": process_name,
                    "completed_operations": operations,
                    **({"preexisting_cpq_readback": preexisting} if preexisting else {}),
                    "reconciliation_evidence": {
                        "cpq_readback_ref": _relative_to_repo(Path(args.preflight_result)),
                        "data_load_status": {
                            "data_set_name": args.data_set_name,
                            "business_object": "CpqCommerceSettings",
                            "status": "Success",
                            "loaded": args.loaded,
                            "errors": args.errors,
                            "skipped": args.skipped,
                        },
                    },
                },
                "updated_at": _utc_timestamp(),
            }
        )
        _write_json_atomic(workflow_record_path, workflow_record)
    return {
        "status": "completed",
        "stage": "cpq_settings_write_reconciliation",
        "workflow_status": "awaiting_adaptive_search_approval",
        "workflow_record_ref": _relative_to_repo(workflow_record_path),
        "next_action": "Prepare the exact Adaptive Search Task Hook preview and obtain its separate approval.",
    }


def _safe_cpq_write_exception_result(
    *,
    error: Exception,
    preview: Mapping[str, Any],
) -> dict[str, Any]:
    """Convert a pre-write core rejection into a project-safe terminal result."""

    target = preview.get("target")
    if not isinstance(target, Mapping):
        target = {}
    if isinstance(error, CpqSettingsWriteExecutorError):
        failure_class = "approval_blocker"
        message = (
            "The approved CPQ Settings executor rejected this write before any CPQ Settings Data Loader import "
            "was attempted."
        )
    elif isinstance(error, CpqSettingsWritePlanError):
        failure_class = "input_validation"
        message = "The current CPQ Settings write plan was invalid before any CPQ Settings Data Loader import was attempted."
    else:
        failure_class = "input_validation"
        message = "The CPQ Settings write could not be prepared safely before any CPQ Settings Data Loader import was attempted."
    message, provider_error = _with_safe_provider_detail(message, error)
    components = preview.get("components")
    cpq_component = components.get("cpq_settings") if isinstance(components, Mapping) else {}
    result = {
        "status": "failed",
        "stage": "cpq_settings_write_gate",
        "failure_class": failure_class,
        "message": message,
        "target": {
            "environment": target.get("environment"),
            "fusion_host": target.get("fusion_host"),
            "cpq_host": target.get("cpq_host"),
        },
        "approval_fingerprint": preview.get("approval_fingerprint"),
        "plan_fingerprint": cpq_component.get("plan_fingerprint"),
        "completed_operations": [],
        "side_effects": "No CPQ Settings Data Loader import was attempted.",
        "next_action": "Create a fresh exact preview and obtain a current approval before any CPQ Settings execution.",
    }
    if provider_error:
        result["provider_error"] = provider_error
    return result


def execute_approved_cpq_settings_write_from_args(args: argparse.Namespace) -> dict[str, Any]:
    """Execute only the explicitly approved CPQ stage, then pause for publish."""

    if not args.approve_cpq_settings_write:
        raise FusionAboWorkflowError(
            "--execute-approved-cpq-settings-write requires explicit approval of the exact CPQ Data Loader preview."
        )
    if not args.project_id:
        raise FusionAboWorkflowError(
            "--execute-approved-cpq-settings-write requires --project-id for its governed audit record."
        )
    preview, approval_record_ref, approval_record_fingerprint = _load_approved_workflow_preview(args)
    _, project_root, _, _, _, _ = _project_workspace(args.project_id)
    workflow_record_path = _workflow_record_path(project_root, preview["approval_fingerprint"])
    with _workflow_lock(project_root, preview["approval_fingerprint"]):
        if workflow_record_path.is_file():
            persisted = _read_json_mapping(workflow_record_path, "automatic Fusion ABO workflow record")
            if (
                persisted.get("approval_record_ref") != approval_record_ref
                or persisted.get("approval_record_fingerprint") != approval_record_fingerprint
            ):
                raise FusionAboWorkflowError(
                    "The persisted automatic workflow does not match the approved provenance record."
                )
            state = _validate_downstream_resume_state(
                persisted, workflow_record_path=workflow_record_path
            )
            if state == "completed":
                return _completed_workflow_result(
                    persisted, workflow_record_path=workflow_record_path
                )
            return {
                "status": "approval_required", "stage": "adaptive_search",
                "workflow_record_ref": _relative_to_repo(workflow_record_path),
                "next_action": "Prepare the exact Adaptive Search Task Hook preview and obtain its separate approval.",
            }

        # This approval-keyed reservation is deliberately before preflight and
        # before the CPQ executor. A crash after any CPQ Settings Data Loader import can therefore
        # never be turned into another automatic CPQ attempt on rerun.
        workflow_record = {
            "schema_version": "1.0",
            "state": "reserved_before_cpq_execution",
            "project_id": preview["project_id"],
            "workflow_approval_fingerprint": preview["approval_fingerprint"],
            "approval_record_ref": approval_record_ref,
            "approval_record_fingerprint": approval_record_fingerprint,
            "created_at": _utc_timestamp(),
            "updated_at": _utc_timestamp(),
        }
        if not _write_json_exclusive(workflow_record_path, workflow_record):
            raise FusionAboWorkflowError(
                "A prior run already reserved this approval; do not repeat CPQ or downstream submission automatically."
            )
        approval_issued_at = _parse_rfc3339_timestamp(args.approval_issued_at, "approval_issued_at")
        try:
            preflight, plan, cpq_preview, properties = _prepare_cpq_settings_write(
                args,
                preview_issued_at=approval_issued_at,
                approved_plan_fingerprint=_required_mapping(
                    _required_mapping(preview.get("components"), "approved workflow components").get("cpq_settings"),
                    "approved CPQ Settings component",
                ).get("plan_fingerprint"),
            )
            _validate_fresh_cpq_preview_against_approval(
                approved_preview=preview, fresh_cpq_preview=cpq_preview
            )
            recovery_readback = (
                _recovery_preexisting_cpq_readback(
                    preflight, preview["validated_process_variable_name"]
                )
                if plan.get("write_scope") == "abo_delta_action_library_function_recovery_only"
                else None
            )
            feature_states = preflight.get("feature_states")
            if (
                isinstance(feature_states, Mapping)
                and set(feature_states) == set(FUSION_ABO_PREREQUISITE_FEATURE_CODES)
                and all(
                    feature_states[code] is True
                    for code in FUSION_ABO_PREREQUISITE_FEATURE_CODES
                )
            ):
                workflow_record["presentation_context"] = {
                    "target": dict(preview["target"]),
                    "validated_process_variable_name": preview["validated_process_variable_name"],
                    "feature_states": dict(feature_states),
                    "feature_states_verified_at": _utc_timestamp(),
                }
        except Exception:
            workflow_record.update({"state": "cpq_preflight_failed", "updated_at": _utc_timestamp()})
            _write_json_atomic(workflow_record_path, workflow_record)
            raise

        # Durable evidence must exist immediately before the first CPQ Settings Data Loader import.
        context = _start_cpq_settings_write_record(
            project_id_value=args.project_id,
            preview=preview,
        )
        try:
            execution_result = execute_approved_cpq_settings_write(
                oauth_properties=properties,
                fusion_abo_preflight_result=preflight,
                plan=plan,
                approval_fingerprint=cpq_preview["approval_fingerprint"],
                approval_issued_at=args.approval_issued_at,
                approval_confirmed=True,
                prepared_loads=_required_mapping(
                    _required_mapping(preview.get("components"), "approved workflow components").get("cpq_settings"),
                    "approved CPQ Settings component",
                ).get("data_loader_loads", {}),
                workflow_preview=preview,
                approval_record_ref=approval_record_ref,
                approval_record_fingerprint=approval_record_fingerprint,
                project_root=project_root,
                properties=Path(args.properties),
                token_cache=args.cpq_token_cache,
                fusion_token_cache=args.fusion_token_cache,
                timeout=args.timeout,
                oauth_options=_cpq_oauth_options_from_args(args),
            )
        except (CpqSettingsWriteExecutorError, CpqSettingsWritePlanError, CpqClientError) as exc:
            execution_result = _safe_cpq_write_exception_result(error=exc, preview=preview)

        cpq_result = _complete_cpq_settings_write_result(
            context=context,
            execution_result=execution_result,
        )
        cpq_result["workflow_approval_fingerprint"] = preview["approval_fingerprint"]
        cpq_result["cpq_settings_approval_fingerprint"] = cpq_preview["approval_fingerprint"]
        if cpq_result.get("status") != "completed":
            workflow_record.update(
                {
                    "state": "cpq_not_completed",
                    "cpq_run_ref": cpq_result.get("project_run_ref"),
                    "updated_at": _utc_timestamp(),
                }
            )
            _write_json_atomic(workflow_record_path, workflow_record)
            cpq_result["workflow_status"] = "blocked_before_adaptive_search_publish"
            cpq_result["ess_sync"] = {
                "status": "not_started",
                "side_effects": "No Adaptive Search or ESS POST was attempted.",
            }
            return cpq_result

        workflow_record.update(
            {
                "state": "cpq_completed",
                "cpq_run_ref": cpq_result.get("project_run_ref"),
                "cpq_verification": {
                    "status": cpq_result.get("status"),
                    "target": cpq_result.get("target"),
                    "validated_process_variable_name": cpq_result.get("validated_process_variable_name"),
                    "completed_operations": cpq_result.get("completed_operations"),
                    **({"preexisting_cpq_readback": recovery_readback} if recovery_readback else {}),
                },
                "updated_at": _utc_timestamp(),
            }
        )
        _write_json_atomic(workflow_record_path, workflow_record)
        return {
            **cpq_result,
            "workflow_status": "awaiting_adaptive_search_approval",
            "approval_required": {
                "stage": "adaptive_search",
                "next_action": "Prepare the exact Adaptive Search Task Hook preview, then request a separate publish approval.",
            },
            "workflow_record_ref": _relative_to_repo(workflow_record_path),
        }


def preview_adaptive_search_from_args(args: argparse.Namespace) -> dict[str, Any]:
    """Return the separate publish approval preview after verified CPQ success."""
    preview, record_ref, record_sha = _load_approved_workflow_preview(args, require_current=False)
    _, project_root, _, _, _, _ = _project_workspace(args.project_id)
    workflow_path = _workflow_record_path(project_root, preview["approval_fingerprint"])
    with _workflow_lock(project_root, preview["approval_fingerprint"]):
        record = _read_json_mapping(workflow_path, "Fusion ABO workflow record")
        if record.get("approval_record_ref") != record_ref or record.get("approval_record_fingerprint") != record_sha:
            raise FusionAboWorkflowError("The CPQ predecessor record differs from the approved plan.")
        return _preview_adaptive_submission(
            args, project_root=project_root, workflow_preview=preview,
            workflow_record_path=workflow_path, workflow_record=record,
            approval_record_ref=record_ref, approval_record_fingerprint=record_sha,
        )


def execute_approved_adaptive_search_from_args(args: argparse.Namespace) -> dict[str, Any]:
    """Submit the separately approved publish once and monitor its exact job."""
    if getattr(args, "adaptive_approval_preview", None):
        workflow_fingerprint, preview_sha = _adaptive_approval_preview_values(
            args.adaptive_approval_preview,
            project_id=args.project_id,
        )
        args.adaptive_preview_sha256 = preview_sha
        preview, record_ref, record_sha = _load_workflow_preview_by_fingerprint(
            args,
            approval_fingerprint=workflow_fingerprint,
            require_current=False,
        )
    else:
        if not args.approval_fingerprint or not args.approval_issued_at:
            raise FusionAboWorkflowError(
                "Supply --adaptive-approval-preview or the exact workflow approval fingerprint and issued_at."
            )
        preview, record_ref, record_sha = _load_approved_workflow_preview(args, require_current=False)
    if not args.approve_adaptive_search or not re.fullmatch(r"[a-f0-9]{64}", args.adaptive_preview_sha256 or ""):
        raise FusionAboWorkflowError("Explicit approval of the exact Adaptive Search preview is required.")
    _, project_root, _, _, _, _ = _project_workspace(args.project_id)
    workflow_path = _workflow_record_path(project_root, preview["approval_fingerprint"])
    with _workflow_lock(project_root, preview["approval_fingerprint"]):
        record = _read_json_mapping(workflow_path, "Fusion ABO workflow record")
        if record.get("state") != "awaiting_adaptive_search_approval" or record.get("adaptive_preview_sha256") != args.adaptive_preview_sha256:
            raise FusionAboWorkflowError("This workflow is not awaiting approval of that exact Adaptive Search preview.")
        if record.get("approval_record_ref") != record_ref or record.get("approval_record_fingerprint") != record_sha:
            raise FusionAboWorkflowError("The Adaptive Search predecessor record differs from the approved plan.")
        return _run_automatic_downstream_controller(
            args, workflow_preview=preview, approval_record_ref=record_ref,
            approval_record_fingerprint=record_sha, workflow_record_path=workflow_path,
            workflow_record=record,
        )


def submit_approved_ess_from_args(args: argparse.Namespace) -> dict[str, Any]:
    """Submit ESS only after a fresh, separate approval of its exact payload."""
    if not args.approve_ess or not re.fullmatch(r"[a-f0-9]{64}", args.ess_approval_sha256 or ""):
        raise FusionAboWorkflowError("Explicit approval of the exact ESS payload is required.")
    preview, record_ref, record_sha = _load_approved_workflow_preview(args, require_current=False)
    _, project_root, _, _, _, _ = _project_workspace(args.project_id)
    workflow_path = _workflow_record_path(project_root, preview["approval_fingerprint"])
    with _workflow_lock(project_root, preview["approval_fingerprint"]):
        record = _read_json_mapping(workflow_path, "Fusion ABO workflow record")
        if record.get("state") != "awaiting_ess_approval" or record.get("ess_preview_payload_sha256") != args.ess_approval_sha256:
            raise FusionAboWorkflowError("This workflow is not awaiting approval of that exact ESS payload.")
        if record.get("approval_record_ref") != record_ref or record.get("approval_record_fingerprint") != record_sha:
            raise FusionAboWorkflowError("The ESS predecessor record differs from the approved plan.")
        adaptive = _required_mapping(record.get("last_adaptive_search_status"), "final Adaptive Search status")
        _validate_adaptive_status_for_ess(preview, record, adaptive)
        ess = _submit_or_monitor_ess(
            args, workflow_preview=preview, workflow_record_path=workflow_path,
            workflow_record=record, adaptive_status=adaptive,
        )
        completed = ess.get("terminal") is True and ess.get("success") is True
        record.update({"state": "completed" if completed else "ess_pending_or_failed", "ess_sync": ess,
                       "updated_at": _utc_timestamp()})
        _write_json_atomic(workflow_path, record)
        return {"status": "completed" if completed else "incomplete",
                "workflow_status": record["state"], "adaptive_search": adaptive, "ess_sync": ess,
                "workflow_record_ref": _relative_to_repo(workflow_path)}


def resume_approved_fusion_abo_workflow_from_args(args: argparse.Namespace) -> dict[str, Any]:
    """Resume only persisted status checks; never replay a completed mutation."""

    if not args.project_id:
        raise FusionAboWorkflowError("--resume-approved-fusion-abo-workflow requires --project-id.")
    preview, approval_record_ref, approval_record_fingerprint = _load_approved_workflow_preview(
        args, require_current=False
    )
    _, project_root, _, _, _, _ = _project_workspace(args.project_id)
    workflow_record_path = _workflow_record_path(project_root, preview["approval_fingerprint"])
    if not workflow_record_path.is_file():
        raise FusionAboWorkflowError(
            "No persisted automatic Fusion ABO workflow exists for this approval; do not rerun CPQ automatically."
        )
    with _workflow_lock(project_root, preview["approval_fingerprint"]):
        workflow_record = _read_json_mapping(workflow_record_path, "automatic Fusion ABO workflow record")
        if (
            workflow_record.get("approval_record_ref") != approval_record_ref
            or workflow_record.get("approval_record_fingerprint") != approval_record_fingerprint
        ):
            raise FusionAboWorkflowError(
                "The persisted automatic workflow does not match the approved provenance record."
            )
        if workflow_record.get("state") == "awaiting_adaptive_search_approval":
            raise FusionAboWorkflowError("Legacy pending approvals cannot be resumed; prepare a fresh load.")
        if workflow_record.get("state") == "awaiting_ess_approval":
            adaptive = _required_mapping(workflow_record.get("last_adaptive_search_status"), "final Adaptive Search status")
            _validate_adaptive_status_for_ess(preview, workflow_record, adaptive)
            _, payload = _ess_payload(preview, adaptive_status=adaptive)
            payload_sha = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
            if payload_sha != workflow_record.get("ess_preview_payload_sha256") or workflow_record.get("ess_preview_target") != preview.get("target"):
                raise FusionAboWorkflowError("The saved ESS approval preview differs from the verified result.")
            return {
                "status": "approval_required", "workflow_status": "awaiting_ess_approval",
                "adaptive_search": adaptive,
                "approval_required": {"stage": "ess", "target": preview["target"],
                                      "operation": "Unified Asset Read Model Sync", "payload": payload,
                                      "payload_sha256": payload_sha},
                "workflow_record_ref": _relative_to_repo(workflow_record_path),
            }
        state = _validate_downstream_resume_state(
            workflow_record, workflow_record_path=workflow_record_path
        )
        if state == "completed":
            return _completed_workflow_result(
                workflow_record, workflow_record_path=workflow_record_path
            )
        if state == "ess_pending_or_failed":
            adaptive = _required_mapping(workflow_record.get("last_adaptive_search_status"), "final Adaptive Search status")
            ess = _submit_or_monitor_ess(
                args, workflow_preview=preview, workflow_record_path=workflow_record_path,
                workflow_record=workflow_record, adaptive_status=adaptive,
            )
            complete = ess.get("terminal") is True and ess.get("success") is True
            workflow_record.update({"state": "completed" if complete else "ess_pending_or_failed",
                                    "ess_sync": ess, "updated_at": _utc_timestamp()})
            _write_json_atomic(workflow_record_path, workflow_record)
            return {"status": "completed" if complete else "incomplete",
                    "workflow_status": workflow_record["state"], "adaptive_search": adaptive,
                    "ess_sync": ess, "workflow_record_ref": _relative_to_repo(workflow_record_path)}
        return _run_automatic_downstream_controller(
            args,
            workflow_preview=preview,
            approval_record_ref=approval_record_ref,
            approval_record_fingerprint=approval_record_fingerprint,
            workflow_record_path=workflow_record_path,
            workflow_record=workflow_record,
        )


def build_adaptive_search_companion_request(
    workflow_preview: Mapping[str, Any],
    *,
    approval_record_ref: str,
    approval_record_fingerprint: str,
) -> dict[str, Any]:
    """Build the exact approved primary-to-companion request.

    This is intentionally an opaque orchestration boundary: Configure Adaptive
    Search owns its Data Loader source and internal correlation identifiers.
    """

    preview = _required_mapping(workflow_preview, "workflow_preview")
    components = _required_mapping(preview.get("components"), "workflow_preview.components")
    adaptive = _required_mapping(components.get("adaptive_search"), "workflow_preview.components.adaptive_search")
    target = _required_mapping(adaptive.get("target"), "workflow_preview.components.adaptive_search.target")
    immutable_source = _required_mapping(
        adaptive.get("immutable_source"), "workflow_preview.components.adaptive_search.immutable_source"
    )
    fingerprint = _require_nonblank_string(
        preview.get("approval_fingerprint"), "workflow_preview.approval_fingerprint"
    ).casefold()
    record_fingerprint = _require_nonblank_string(
        approval_record_fingerprint, "workflow approval record fingerprint"
    ).casefold()
    if not re.fullmatch(r"[a-f0-9]{64}", fingerprint) or not re.fullmatch(
        r"[a-f0-9]{64}", record_fingerprint
    ):
        raise FusionAboWorkflowError("The approved workflow fingerprints are invalid.")
    authorization = {
        "scope": ADAPTIVE_SEARCH_WORKFLOW_SCOPE,
        "approval_fingerprint": fingerprint,
        "project_id": _require_nonblank_string(preview.get("project_id"), "workflow_preview.project_id"),
        "target": dict(target),
        "entities": list(adaptive.get("entities", [])),
        "publish_type": _require_nonblank_string(adaptive.get("publish_type"), "adaptive_search.publish_type"),
        "archive_sha256": _require_nonblank_string(immutable_source.get("archive_sha256"), "adaptive_search.archive_sha256").casefold(),
        "source_sha256": _require_nonblank_string(immutable_source.get("source_sha256"), "adaptive_search.source_sha256").casefold(),
        "issued_at": _require_nonblank_string(preview.get("issued_at"), "workflow_preview.issued_at"),
        "expires_at": _require_nonblank_string(preview.get("expires_at"), "workflow_preview.expires_at"),
        "submission_limit": 1,
        "approval_record_ref": _require_nonblank_string(approval_record_ref, "workflow approval record reference"),
        "approval_record_fingerprint": record_fingerprint,
    }
    return {
        "schema_version": "1.0",
        "operation": "submit_partial_publish",
        "project_id": authorization["project_id"],
        "target": authorization["target"],
        "entities": list(adaptive.get("entities", [])),
        "publish_type": authorization["publish_type"],
        "preparation_id": _require_nonblank_string(adaptive.get("preparation_id"), "adaptive_search.preparation_id"),
        "workflow_authorization": authorization,
    }


def evaluate_adaptive_search_publish_result(
    workflow_preview: Mapping[str, Any], adaptive_result: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate a companion status result and create the one ESS request gate.

    The function does not submit ESS.  It produces an immutable request for
    ``core.fusion-api.ess-job-submitter`` only when the companion has returned
    final success for the exact approved target and entity pair.
    """

    preview = _required_mapping(workflow_preview, "workflow_preview")
    components = _required_mapping(preview.get("components"), "workflow_preview.components")
    adaptive = _required_mapping(components.get("adaptive_search"), "workflow_preview.components.adaptive_search")
    request = {
        "project_id": preview.get("project_id"),
        "target": adaptive.get("target"),
        "entities": list(adaptive.get("entities", [])),
        "workflow_approval_fingerprint": preview.get("approval_fingerprint"),
    }
    result = _required_mapping(adaptive_result, "adaptive_search_result")
    if _require_nonblank_string(result.get("schema_version"), "adaptive_search_result.schema_version") != "1.0":
        raise FusionAboWorkflowError("Adaptive Search result has an unsupported schema version.")
    if _require_nonblank_string(result.get("project_id"), "adaptive_search_result.project_id") != request["project_id"]:
        raise FusionAboWorkflowError("Adaptive Search result belongs to a different project.")
    result_target = _required_mapping(result.get("target"), "adaptive_search_result.target")
    if result_target != request["target"]:
        raise FusionAboWorkflowError("Adaptive Search result belongs to a different target.")
    if list(result.get("entities", [])) != request["entities"]:
        raise FusionAboWorkflowError("Adaptive Search result does not cover the exact approved entity pair.")
    if result.get("publish_type") != adaptive.get("publish_type"):
        raise FusionAboWorkflowError("Adaptive Search result does not match the approved selective publish type.")
    operation_id = _require_nonblank_string(result.get("publish_operation_id"), "adaptive_search_result.publish_operation_id")
    state = _require_nonblank_string(result.get("state"), "adaptive_search_result.state")
    base = {
        "workflow_approval_fingerprint": request["workflow_approval_fingerprint"],
        "publish_operation_id": operation_id,
        "adaptive_search_status": state,
    }
    if state != "SUCCEEDED" or result.get("eligible_for_ess") is not True:
        return {
            **base,
            "workflow_status": (
                "adaptive_search_not_eligible_for_ess"
                if result.get("terminal") is True
                else "waiting_for_adaptive_search_publish"
            ),
            "ess_sync": {
                "status": "not_started",
                "stage": "ess_sync_auto_submission",
                "failure_class": "adaptive_search_predecessor_not_completed",
                "message": "ESS is not eligible until Configure Adaptive Search returns final SUCCEEDED evidence for both required entities.",
                "side_effects": "No ESS POST was attempted.",
            },
            "next_action": (
                "Reconcile the same Adaptive Search publish operation; do not submit ESS or republish automatically."
                if result.get("terminal") is True
                else "Continue GET-only monitoring of the same Adaptive Search publish operation."
            ),
        }
    if result.get("terminal") is not True or list(result.get("final_entity_readiness", [])) != list(ADAPTIVE_SEARCH_REQUIRED_ENTITIES):
        raise FusionAboWorkflowError(
            "Adaptive Search success lacks terminal enabled-entity readiness evidence; ESS is blocked."
        )
    job_id = _require_nonblank_string(result.get("adaptive_search_job_id"), "adaptive_search_result.adaptive_search_job_id")
    ess = _required_mapping(_required_mapping(workflow_preview, "workflow_preview").get("components"), "workflow_preview.components").get("ess_sync")
    return {
        **base,
        "workflow_status": "adaptive_search_succeeded_ess_submission_required",
        "next_action": "Use the governed controller to prepare the exact ESS payload and obtain its separate approval before submission.",
        "ess_submission_request": {
            "skill_id": "core.fusion-api.ess-job-submitter",
            "idempotency_key": f"{request['project_id']}:{operation_id}:{job_id}",
            "job_definition_id": ess["job_definition_id"],
            "application": ess["application"],
            "product": ess["product"],
            "request_parameters": ess["request_parameters"],
            "description": ess["description"],
            "adaptive_search_job_id": job_id,
        },
    }


def evaluate_adaptive_search_status_from_args(args: argparse.Namespace) -> dict[str, Any]:
    """CLI adapter for a persisted, redacted companion result."""

    return evaluate_adaptive_search_publish_result(
        _read_json_object(args.workflow_preview, "workflow preview"),
        _read_json_object(args.adaptive_search_status_result, "Adaptive Search status result"),
    )


def _workflow_record_path(project_root: Path, approval_fingerprint: str) -> Path:
    if not re.fullmatch(r"[a-f0-9]{64}", approval_fingerprint):
        raise FusionAboWorkflowError("Workflow approval fingerprint is invalid for a durable controller record.")
    return project_root / TASK_ARTIFACT_DIRECTORY / f"automatic-workflow-{approval_fingerprint}.json"


def _workflow_work_directory(workflow_record_path: Path) -> Path:
    """Return an approval-specific local work directory, never a shared current folder."""

    name = workflow_record_path.stem
    if not re.fullmatch(r"automatic-workflow-[a-f0-9]{64}", name):
        raise FusionAboWorkflowError("Automatic workflow record path is invalid.")
    return workflow_record_path.parent / name


def _write_json_exclusive(path: Path, payload: Mapping[str, Any]) -> bool:
    """Create a durable before-POST reservation without overwriting a prior run."""

    _assert_safe_for_persistence(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise
    return True


@contextmanager
def _workflow_lock(project_root: Path, approval_fingerprint: str) -> Iterator[None]:
    """Prevent two local controllers from issuing the approved mutations twice."""

    if fcntl is None:
        raise FusionAboWorkflowError("The automatic Fusion ABO controller requires POSIX file locking.")
    lock_path = project_root / TASK_ARTIFACT_DIRECTORY / f".automatic-workflow-{approval_fingerprint}.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise FusionAboWorkflowError(
                "This approved Fusion ABO workflow is already being controlled by another local process."
            ) from exc
        yield
    finally:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


def _completed_workflow_result(
    workflow_record: Mapping[str, Any], *, workflow_record_path: Path
) -> dict[str, Any]:
    """Return an already durable terminal success without restarting work."""

    ess_sync = _required_mapping(workflow_record.get("ess_sync"), "completed workflow ESS result")
    if ess_sync.get("terminal") is not True or ess_sync.get("success") is not True:
        raise FusionAboWorkflowError(
            "The workflow is marked completed without a durable successful ESS result; reconcile it instead of restarting automatically."
        )
    adaptive = workflow_record.get("last_adaptive_search_status")
    return {
        "status": "completed",
        "workflow_status": "completed",
        "adaptive_search": dict(adaptive) if isinstance(adaptive, Mapping) else None,
        "ess_sync": dict(ess_sync),
        "workflow_record_ref": _relative_to_repo(workflow_record_path),
    }


def _validate_downstream_resume_state(
    workflow_record: Mapping[str, Any], *, workflow_record_path: Path
) -> str:
    """Fail closed before a resume can cross any previously incomplete gate.

    A durable controller record is an at-most-once boundary.  In particular,
    a record created before CPQ execution must never be reinterpreted as
    permission to submit a child Data Loader import later.
    """

    state = _require_nonblank_string(workflow_record.get("state"), "automatic workflow state")
    if state == "completed":
        _completed_workflow_result(workflow_record, workflow_record_path=workflow_record_path)
        return state
    permitted = {
        "cpq_completed",
        "monitoring_timeout",
        "approval_expired_before_ess",
        "ess_pending_or_failed",
    }
    if state not in permitted:
        raise FusionAboWorkflowError(
            "The persisted workflow did not reach a safely resumable downstream state; reconcile the prior CPQ or child result instead of submitting anything automatically."
        )
    if state == "cpq_completed" and not isinstance(workflow_record.get("adaptive_operation_record_ref"), str):
        raise FusionAboWorkflowError("The publish has not been separately approved and submitted; prepare its approval preview.")
    if state != "cpq_completed":
        if not isinstance(workflow_record.get("adaptive_operation_record_ref"), str) or not isinstance(
            workflow_record.get("adaptive_submission"), Mapping
        ):
            raise FusionAboWorkflowError(
                "The persisted workflow state requires an exact prior Adaptive Search operation record; do not create a replacement submission automatically."
            )
    if state == "ess_pending_or_failed":
        ess_record = _workflow_work_directory(workflow_record_path) / "ess-submission.json"
        if not ess_record.is_file():
            raise FusionAboWorkflowError(
                "The workflow has an ESS pending/failed state without its durable ESS request record; do not submit another ESS request automatically."
            )
        ess_request_id = _read_json_mapping(ess_record, "ESS submission record").get("request_id")
        if isinstance(ess_request_id, bool) or not isinstance(ess_request_id, int) or ess_request_id < 1:
            raise FusionAboWorkflowError(
                "GET-only ESS resume requires a durable request id; reconcile the earlier submission before any new approval."
            )
    return state


def _safe_public_adaptive_status(value: Mapping[str, Any]) -> dict[str, Any]:
    """Keep only the child contract's public status fields in the parent record."""

    keys = (
        "schema_version",
        "publish_operation_id",
        "project_id",
        "target",
        "entities",
        "publish_type",
        "state",
        "terminal",
        "eligible_for_ess",
        "adaptive_search_job_id",
        "adaptive_search_status",
        "final_entity_readiness",
        "retryable",
        "message",
        "monitoring",
        "provider_error",
        "status_read_error",
    )
    return {key: value[key] for key in keys if key in value}


def _adaptive_operation_record_path(
    value: Any, *, project_id: str, field_name: str = "Adaptive Search operation record"
) -> Path:
    ref = _project_relative_path(value, project_id=project_id, field_name=field_name)
    return (REPO_ROOT / ref).resolve()


def _preview_adaptive_submission(
    args: argparse.Namespace, *, project_root: Path, workflow_preview: Mapping[str, Any],
    workflow_record_path: Path, workflow_record: dict[str, Any],
    approval_record_ref: str, approval_record_fingerprint: str,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    """Persist the exact child Task Hook preview without reserving a POST."""
    if workflow_record.get("state") not in {"cpq_completed", "awaiting_adaptive_search_approval"} or workflow_record.get("adaptive_submission_state"):
        raise FusionAboWorkflowError("Adaptive Search approval can be prepared only after verified CPQ completion and before publish submission.")
    request = build_adaptive_search_companion_request(
        workflow_preview, approval_record_ref=approval_record_ref,
        approval_record_fingerprint=approval_record_fingerprint,
    )
    adaptive = _required_mapping(
        _required_mapping(workflow_preview.get("components"), "workflow components").get("adaptive_search"),
        "Adaptive Search component",
    )
    prepared_path = _adaptive_operation_record_path(
        adaptive.get("prepared_record_ref"), project_id=args.project_id,
        field_name="Adaptive Search prepared record",
    )
    work = _workflow_work_directory(workflow_record_path)
    work.mkdir(parents=True, exist_ok=True)
    request_path = work / "adaptive-search-submission-request.json"
    predecessor_path = work / "cpq-settings-predecessor.json"
    internal_output_path = work / "adaptive-search-preview-internal.json"
    _write_json_atomic(request_path, request)
    _write_json_atomic(predecessor_path, {
        "status": "completed",
        "workflow_approval_fingerprint": workflow_preview["approval_fingerprint"],
        "project_id": workflow_preview["project_id"],
        "target": _adaptive_target_from_workflow_preview(workflow_preview),
        "cpq_verification": workflow_record.get("cpq_verification"),
    })
    result = _run_json_command([
        sys.executable, str(ADAPTIVE_SEARCH_EXECUTOR), "--request", str(request_path),
        "--preview-submit", "--predecessor-result", str(predecessor_path),
        "--prepared-record", str(prepared_path), "--project-root", str(project_root),
        "--properties", args.properties, "--token-cache", args.fusion_token_cache,
        "--internal-output", str(internal_output_path),
    ], stage="Configure Adaptive Search approval preview", runner=runner)
    approval = _required_mapping(result.get("approval_required"), "Adaptive Search approval preview")
    preview_sha = _require_nonblank_string(approval.get("preview_sha256"), "Adaptive Search preview digest")
    internal = _read_json_mapping(internal_output_path, "Adaptive Search preview descriptor")
    preview_path = _adaptive_operation_record_path(
        internal.get("preview_record_path"), project_id=args.project_id,
        field_name="Adaptive Search Task Hook preview",
    )
    if _sha256_file(preview_path) != preview_sha:
        raise FusionAboWorkflowError("Adaptive Search preview digest does not match its durable record.")
    workflow_record.update({
        "state": "awaiting_adaptive_search_approval",
        "adaptive_preview_sha256": preview_sha,
        "adaptive_preview_request_sha256": _sha256_file(request_path),
        "updated_at": _utc_timestamp(),
    })
    _write_json_atomic(workflow_record_path, workflow_record)
    return {"status": "approval_required", "stage": "adaptive_search", "approval_required": dict(approval),
            "workflow_record_ref": _relative_to_repo(workflow_record_path)}


def _adaptive_submission(
    args: argparse.Namespace,
    *,
    project_root: Path,
    workflow_preview: Mapping[str, Any],
    workflow_record_path: Path,
    workflow_record: dict[str, Any],
    approval_record_ref: str,
    approval_record_fingerprint: str,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> tuple[dict[str, Any], Path]:
    """Submit the immutable child source once, with a parent durable checkpoint."""

    existing_ref = workflow_record.get("adaptive_operation_record_ref")
    if isinstance(existing_ref, str) and existing_ref.strip():
        operation_path = _adaptive_operation_record_path(existing_ref, project_id=args.project_id)
        submission = _required_mapping(
            workflow_record.get("adaptive_submission"), "persisted Adaptive Search submission"
        )
        return dict(submission), operation_path
    if workflow_record.get("adaptive_submission_state") == "reserved_before_data_loader_submission":
        raise FusionAboWorkflowError(
            "Adaptive Search submission may already have been attempted but no durable operation id was recorded; do not submit again automatically."
        )
    approved_sha = getattr(args, "adaptive_preview_sha256", None)
    if not getattr(args, "approve_adaptive_search", False) or not isinstance(approved_sha, str) or approved_sha != workflow_record.get("adaptive_preview_sha256"):
        raise FusionAboWorkflowError("The exact Adaptive Search preview requires its own explicit approval before submission.")
    request = build_adaptive_search_companion_request(
        workflow_preview,
        approval_record_ref=approval_record_ref,
        approval_record_fingerprint=approval_record_fingerprint,
    )
    components = _required_mapping(workflow_preview.get("components"), "workflow preview components")
    adaptive = _required_mapping(components.get("adaptive_search"), "workflow preview adaptive component")
    prepared_path = _adaptive_operation_record_path(
        adaptive.get("prepared_record_ref"),
        project_id=args.project_id,
        field_name="Adaptive Search prepared record",
    )
    work = _workflow_work_directory(workflow_record_path)
    work.mkdir(parents=True, exist_ok=True)
    request_path = work / "adaptive-search-submission-request.json"
    predecessor_path = work / "cpq-settings-predecessor.json"
    internal_output_path = work / "adaptive-search-submission-internal.json"
    _write_json_atomic(request_path, request)
    _write_json_atomic(
        predecessor_path,
        {
            "status": "completed",
            "workflow_approval_fingerprint": workflow_preview["approval_fingerprint"],
            "project_id": workflow_preview["project_id"],
            "target": _adaptive_target_from_workflow_preview(workflow_preview),
            "cpq_verification": workflow_record.get("cpq_verification"),
        },
    )
    if workflow_record.get("adaptive_preview_request_sha256") != _sha256_file(request_path):
        raise FusionAboWorkflowError("The Adaptive Search request changed after its approval preview.")
    workflow_record["adaptive_submission_state"] = "reserved_before_data_loader_submission"
    workflow_record["updated_at"] = _utc_timestamp()
    _write_json_atomic(workflow_record_path, workflow_record)
    result = _run_json_command(
        [
            sys.executable,
            str(ADAPTIVE_SEARCH_EXECUTOR),
            "--request",
            str(request_path),
            "--approve-publish",
            "--approval-preview-sha256",
            approved_sha,
            "--predecessor-result",
            str(predecessor_path),
            "--prepared-record",
            str(prepared_path),
            "--project-root",
            str(project_root),
            "--properties",
            args.properties,
            "--token-cache",
            args.fusion_token_cache,
            "--internal-output",
            str(internal_output_path),
        ],
        stage="Configure Adaptive Search submission",
        runner=runner,
    )
    submission = _required_mapping(result.get("submission"), "Configure Adaptive Search submission")
    internal_result = _read_json_mapping(
        internal_output_path, "Configure Adaptive Search submission descriptor"
    )
    operation_path = _adaptive_operation_record_path(
        internal_result.get("operation_record"), project_id=args.project_id
    )
    if submission.get("state") != "SUBMITTED" or not re.fullmatch(
        r"apo_[a-f0-9]{32}", str(submission.get("publish_operation_id", ""))
    ):
        raise FusionAboWorkflowError("Configure Adaptive Search did not return a valid submitted operation.")
    workflow_record.update(
        {
            "adaptive_submission_state": "submitted",
            "adaptive_submission": dict(submission),
            "adaptive_operation_record_ref": _relative_to_repo(operation_path),
            "updated_at": _utc_timestamp(),
        }
    )
    _write_json_atomic(workflow_record_path, workflow_record)
    return dict(submission), operation_path


def _adaptive_status_once(
    args: argparse.Namespace,
    *,
    project_root: Path,
    operation_record_path: Path,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    result = _run_json_command(
        [
            sys.executable,
            str(ADAPTIVE_SEARCH_EXECUTOR),
            "--resume-operation-record",
            str(operation_record_path),
            "--project-root",
            str(project_root),
            "--properties",
            args.properties,
            "--token-cache",
            args.fusion_token_cache,
        ],
        stage="Configure Adaptive Search status",
        runner=runner,
    )
    return dict(_required_mapping(result.get("status"), "Configure Adaptive Search status"))


def _ess_payload(
    workflow_preview: Mapping[str, Any], *, adaptive_status: Mapping[str, Any]
) -> tuple[str, dict[str, Any]]:
    components = _required_mapping(workflow_preview.get("components"), "workflow preview components")
    ess = _required_mapping(components.get("ess_sync"), "workflow preview ESS component")
    operation_id = _require_nonblank_string(
        adaptive_status.get("publish_operation_id"), "Adaptive Search publish operation id"
    )
    job_id = _require_nonblank_string(
        adaptive_status.get("adaptive_search_job_id"), "Adaptive Search job id"
    )
    payload = {
        "jobDefinitionId": _require_nonblank_string(ess.get("job_definition_id"), "ESS job definition"),
        "application": _require_nonblank_string(ess.get("application"), "ESS application"),
        "product": _require_nonblank_string(ess.get("product"), "ESS product"),
        "requestParameters": list(ess.get("request_parameters", [])),
        "description": _require_nonblank_string(ess.get("description"), "ESS description"),
    }
    return f"{workflow_preview['project_id']}:{operation_id}:{job_id}", payload


def _ess_delegation_contract(
    args: argparse.Namespace,
    *,
    workflow_preview: Mapping[str, Any],
    adaptive_status: Mapping[str, Any],
    idempotency_key: str,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind the separately approved ESS payload to the fixed adapter contract."""

    target = _safe_target(workflow_preview.get("target"), "workflow preview target")
    properties = _read_properties(args.properties)
    configured_environment = _require_nonblank_string(
        properties.get("environment"), "configured Fusion environment"
    )
    configured_environment_identity = _environment_identity(properties)
    configured_fusion_host = _https_host(properties, "restBaseUrl")
    approved_environment_identity = _environment_identity(
        {"environment": target["environment"]}
    )
    approved_fusion_host = _environment_identity(
        {"environment": target["fusion_host"]}
    )
    if configured_environment_identity != approved_environment_identity:
        raise FusionAboWorkflowError(
            "The configured Fusion environment does not match the approved workflow target."
        )
    if configured_fusion_host != approved_fusion_host:
        raise FusionAboWorkflowError(
            "The configured Fusion REST host does not match the approved workflow target."
        )
    components = _required_mapping(workflow_preview.get("components"), "workflow preview components")
    ess = _required_mapping(components.get("ess_sync"), "workflow preview ESS component")
    job_definition_id = _require_nonblank_string(
        ess.get("job_definition_id"), "ESS job definition"
    )
    application = _require_nonblank_string(ess.get("application"), "ESS application")
    if payload.get("jobDefinitionId") != job_definition_id or payload.get("application") != application:
        raise FusionAboWorkflowError(
            "The ESS payload does not match the approved workflow job contract."
        )
    approval_fingerprint = _require_nonblank_string(
        workflow_preview.get("approval_fingerprint"), "workflow approval fingerprint"
    ).casefold()
    if not re.fullmatch(r"[a-f0-9]{64}", approval_fingerprint):
        raise FusionAboWorkflowError("The workflow approval fingerprint is invalid.")
    canonical_payload = dict(payload)
    return {
        "contract_version": "1.0",
        "stage": "approved_submission",
        "task": {
            "task_name": ESS_SYNC_TASK_NAME,
            "task_code": ESS_SYNC_TASK_CODE,
        },
        "fusion_environment_context": {
            "environment": configured_environment,
            "fusion_host": f"https://{configured_fusion_host}",
        },
        "requested_payload_overrides": {},
        "execution_options": {
            "wait_seconds": _validated_wait(args.ess_wait_seconds, "ess_wait_seconds"),
            "poll_interval_seconds": _validated_wait(
                args.ess_poll_interval_seconds, "ess_poll_interval_seconds"
            ),
        },
        "approval": {
            "explicit_submission_approval": True,
            "approved_payload_sha256": hashlib.sha256(
                _canonical_json(canonical_payload).encode("utf-8")
            ).hexdigest(),
        },
        "job_contract": {
            "job_definition_id": job_definition_id,
            "application": application,
        },
        "request_payload": canonical_payload,
        "audit_context": {
            "workflow_approval_fingerprint": approval_fingerprint,
            "ess_idempotency_key": idempotency_key,
            "adaptive_search_publish_operation_id": _require_nonblank_string(
                adaptive_status.get("publish_operation_id"),
                "Adaptive Search publish operation id",
            ),
            "adaptive_search_job_id": _require_nonblank_string(
                adaptive_status.get("adaptive_search_job_id"),
                "Adaptive Search job id",
            ),
        },
    }


def _safe_ess_result(value: Mapping[str, Any], *, request_id: int) -> dict[str, Any]:
    execution = _required_mapping(value.get("execution_result"), "ESS execution result")
    reported_request_id = execution.get("requestId")
    if (
        isinstance(reported_request_id, bool)
        or not isinstance(reported_request_id, int)
        or reported_request_id != request_id
    ):
        raise FusionAboWorkflowError(
            "ESS status does not belong to the persisted ESS request."
        )
    return {
        "request_id": request_id,
        "terminal": execution.get("terminal") is True,
        "success": execution.get("success"),
        "state": _required_mapping(execution.get("status"), "ESS status").get("state")
        if isinstance(execution.get("status"), Mapping)
        else None,
    }


def _run_ess_monitor_json_command(
    command: Sequence[str],
    *,
    request_id: int,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    """Read the ABO ESS adapter's structured terminal/timeout results.

    The selected adapter route deliberately uses exit code 3 for a bounded
    nonterminal wait and 4 for a terminal failed job.  Both outcomes still
    carry a normal JSON result and are GET-only once a persisted request id is
    supplied.  Accept only those documented result codes; every other nonzero
    result remains an unsafe adapter failure.
    """

    completed = runner(list(command), check=False, capture_output=True, text=True)
    if completed.returncode not in {0, 3, 4}:
        raise FusionAboWorkflowError("ESS status could not continue safely.")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise FusionAboWorkflowError(
            "ESS status did not return its required structured result."
        ) from exc
    if not isinstance(payload, dict):
        raise FusionAboWorkflowError("ESS status did not return a JSON object.")

    safe = _safe_ess_result(payload, request_id=request_id)
    if completed.returncode == 3:
        diagnostics = _required_mapping(payload.get("diagnostics"), "ESS timeout diagnostics")
        if (
            diagnostics.get("timed_out_waiting") is not True
            or safe["terminal"]
            or safe["success"] is not None
        ):
            raise FusionAboWorkflowError(
                "ESS status returned an inconsistent timeout result."
            )
    elif completed.returncode == 4 and not (
        safe["terminal"] and safe["success"] is False
    ):
        raise FusionAboWorkflowError(
            "ESS status returned an inconsistent terminal failure result."
        )
    return payload


def _run_ess_contract_validation_command(
    command: Sequence[str],
    *,
    expected_payload_sha256: str,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> tuple[bool, dict[str, Any]]:
    """Run task-local validation and prove that it cannot dispatch a POST."""

    completed = runner(list(command), check=False, capture_output=True, text=True)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise FusionAboWorkflowError(
            "ESS contract validation did not return its required structured result."
        ) from exc
    if not isinstance(payload, dict):
        raise FusionAboWorkflowError("ESS contract validation did not return a JSON object.")
    diagnostics = _required_mapping(
        payload.get("diagnostics"), "ESS contract validation diagnostics"
    )
    if diagnostics.get("dispatch_attempted") is not False:
        raise FusionAboWorkflowError(
            "ESS contract validation did not prove that no submission was attempted."
        )
    if completed.returncode == 0:
        validation = _required_mapping(
            payload.get("validation_result"), "ESS contract validation result"
        )
        if (
            validation.get("valid") is not True
            or validation.get("dispatch_attempted") is not False
            or validation.get("approved_payload_sha256") != expected_payload_sha256
        ):
            raise FusionAboWorkflowError(
                "ESS contract validation returned an inconsistent success result."
            )
        return True, payload
    if completed.returncode == 1:
        execution = _required_mapping(
            payload.get("execution_result"), "ESS contract validation failure result"
        )
        if (
            diagnostics.get("failure_stage") != "pre_dispatch_validation"
            or execution.get("submitted") is not False
            or execution.get("requestId") is not None
        ):
            raise FusionAboWorkflowError(
                "ESS contract validation failure was not proven to be pre-dispatch."
            )
        return False, payload
    raise FusionAboWorkflowError("ESS contract validation returned an unsupported result code.")


def _run_ess_submit_json_command(
    command: Sequence[str],
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> tuple[bool, dict[str, Any]]:
    """Preserve adapter dispatch evidence for successful and failed submissions."""

    completed = runner(list(command), check=False, capture_output=True, text=True)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise FusionAboWorkflowError(
            "ESS submission did not return its required structured result."
        ) from exc
    if not isinstance(payload, dict):
        raise FusionAboWorkflowError("ESS submission did not return a JSON object.")
    if completed.returncode == 0:
        return True, payload
    if completed.returncode == 1:
        diagnostics = _required_mapping(payload.get("diagnostics"), "ESS failure diagnostics")
        execution = _required_mapping(payload.get("execution_result"), "ESS failure result")
        dispatch_attempted = diagnostics.get("dispatch_attempted")
        if (
            not isinstance(dispatch_attempted, bool)
            or execution.get("submitted") is not False
            or execution.get("requestId") is not None
        ):
            raise FusionAboWorkflowError(
                "ESS submission failure did not return safe dispatch evidence."
            )
        return False, payload
    raise FusionAboWorkflowError("ESS submission returned an unsupported result code.")


def _run_ess_recent_lookup_json_command(
    command: Sequence[str],
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> list[dict[str, Any]]:
    """Return read-only recent ESS request summaries from the core submitter."""

    completed = runner(list(command), check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise FusionAboWorkflowError("ESS request-id reconciliation lookup could not continue safely.")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise FusionAboWorkflowError(
            "ESS request-id reconciliation did not return its required structured result."
        ) from exc
    if not isinstance(payload, dict):
        raise FusionAboWorkflowError("ESS request-id reconciliation did not return a JSON object.")
    diagnostics = _required_mapping(
        payload.get("diagnostics"), "ESS request-id reconciliation diagnostics"
    )
    if diagnostics.get("read_only") is not True:
        raise FusionAboWorkflowError("ESS request-id reconciliation did not prove read-only execution.")
    execution = _required_mapping(
        payload.get("execution_result"), "ESS request-id reconciliation result"
    )
    recent = execution.get("recent_requests")
    if not isinstance(recent, list):
        raise FusionAboWorkflowError("ESS request-id reconciliation did not return recent requests.")
    return [dict(item) for item in recent if isinstance(item, Mapping)]


def _ess_reconciliation_window_minutes(ess_record: Mapping[str, Any]) -> int:
    started = _parse_rfc3339_timestamp(
        _require_nonblank_string(
            ess_record.get("dispatch_started_at"), "ESS dispatch_started_at"
        ),
        "ESS dispatch_started_at",
    )
    elapsed = datetime.now(timezone.utc) - started
    minutes = int(elapsed.total_seconds() // 60) + 10
    return max(15, min(minutes, 24 * 60))


def _request_id_from_recent_ess_request(item: Mapping[str, Any]) -> int | None:
    raw = item.get("requestId")
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int) and raw > 0:
        return raw
    if isinstance(raw, str) and raw.isdigit() and int(raw) > 0:
        return int(raw)
    return None


def _reconcile_ess_dispatch_started_request_id(
    args: argparse.Namespace,
    *,
    ess_record: Mapping[str, Any],
    payload: Mapping[str, Any],
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> int:
    """Find one already-submitted ESS request without issuing another POST."""

    job_definition_id = _require_nonblank_string(
        payload.get("jobDefinitionId"), "ESS reconciliation job definition"
    )
    application = _require_nonblank_string(
        payload.get("application"), "ESS reconciliation application"
    )
    description = _require_nonblank_string(
        payload.get("description"), "ESS reconciliation description"
    )
    recent = _run_ess_recent_lookup_json_command(
        [
            sys.executable,
            str(ESS_ABO_ADAPTER),
            "--properties",
            args.properties,
            "--token-cache",
            args.fusion_token_cache,
            "--find-recent-job-definition",
            job_definition_id,
            "--since-minutes",
            str(_ess_reconciliation_window_minutes(ess_record)),
            "--no-open-browser",
            "--timeout",
            str(args.timeout),
        ],
        runner=runner,
    )
    matches: list[int] = []
    for item in recent:
        if (
            item.get("jobDefinitionId") == job_definition_id
            and item.get("application") == application
            and item.get("description") == description
        ):
            request_id = _request_id_from_recent_ess_request(item)
            if request_id is not None:
                matches.append(request_id)
    unique_matches = sorted(set(matches))
    if len(unique_matches) != 1:
        raise FusionAboWorkflowError(
            "ESS dispatch request id could not be reconciled unambiguously; do not submit again automatically."
        )
    return unique_matches[0]


def _submit_or_monitor_ess(
    args: argparse.Namespace,
    *,
    workflow_preview: Mapping[str, Any],
    workflow_record_path: Path,
    workflow_record: dict[str, Any],
    adaptive_status: Mapping[str, Any],
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    """Use one local reservation to guarantee at-most-once ESS POST behavior."""

    idempotency_key, payload = _ess_payload(workflow_preview, adaptive_status=adaptive_status)
    current_payload_sha = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    existing_ess_record = _workflow_work_directory(workflow_record_path) / "ess-submission.json"
    if not existing_ess_record.is_file():
        if workflow_record.get("state") != "awaiting_ess_approval" or not getattr(args, "approve_ess", False):
            raise FusionAboWorkflowError("Explicit approval is required immediately before the ESS submission.")
        if getattr(args, "ess_approval_sha256", None) != workflow_record.get("ess_preview_payload_sha256") or current_payload_sha != workflow_record.get("ess_preview_payload_sha256"):
            raise FusionAboWorkflowError("The ESS payload differs from the separately approved preview.")
        if workflow_record.get("ess_preview_target") != workflow_preview.get("target"):
            raise FusionAboWorkflowError("The ESS target differs from the separately approved preview.")
    delegation_contract = _ess_delegation_contract(
        args,
        workflow_preview=workflow_preview,
        adaptive_status=adaptive_status,
        idempotency_key=idempotency_key,
        payload=payload,
    )
    payload_sha256 = delegation_contract["approval"]["approved_payload_sha256"]
    contract_sha256 = hashlib.sha256(
        _canonical_json(delegation_contract).encode("utf-8")
    ).hexdigest()
    work = _workflow_work_directory(workflow_record_path)
    work.mkdir(parents=True, exist_ok=True)
    ess_record_path = work / "ess-submission.json"
    contract_path = work / "ess-delegation-contract.json"
    corrected_contract_path = work / "ess-delegation-contract.corrected.json"
    failed_contract_path = work / "ess-delegation-contract.pre-dispatch-failed.json"
    validation_command = [
        sys.executable,
        str(ESS_ABO_ADAPTER),
        "--delegation-contract-file",
        str(contract_path),
        "--validate-only",
        "--properties",
        args.properties,
    ]
    contract_validated_for_dispatch = False
    if not ess_record_path.exists():
        _write_json_atomic(contract_path, delegation_contract)
        valid, _ = _run_ess_contract_validation_command(
            validation_command,
            expected_payload_sha256=payload_sha256,
            runner=runner,
        )
        if not valid:
            raise FusionAboWorkflowError(
                "The corrected ESS delegation contract failed local validation before reservation."
            )
        contract_validated_for_dispatch = True
        created = _write_json_exclusive(
            ess_record_path,
            {
                "state": "validated_ready_to_dispatch",
                "idempotency_key": idempotency_key,
                "approved_payload_sha256": payload_sha256,
                "delegation_contract_sha256": contract_sha256,
                "created_at": _utc_timestamp(),
            },
        )
        if not created:
            raise FusionAboWorkflowError("Concurrent ESS submission reservation detected; do not submit again automatically.")
    ess_record = _read_json_mapping(ess_record_path, "ESS submission record")
    if ess_record.get("idempotency_key") != idempotency_key:
        raise FusionAboWorkflowError("The persisted ESS submission does not belong to this Adaptive Search operation.")
    request_id = ess_record.get("request_id")
    if request_id is None:
        state = ess_record.get("state")
        if state == "reserved_before_ess_submission":
            if not contract_path.exists():
                raise FusionAboWorkflowError(
                    "The legacy ESS reservation has no contract evidence; do not submit again automatically."
                )
            legacy_contract = _read_json_mapping(contract_path, "legacy ESS delegation contract")
            legacy_contract_sha256 = hashlib.sha256(
                _canonical_json(legacy_contract).encode("utf-8")
            ).hexdigest()
            legacy_payload = _required_mapping(
                legacy_contract.get("request_payload"), "legacy ESS request payload"
            )
            legacy_payload_sha256 = hashlib.sha256(
                _canonical_json(legacy_payload).encode("utf-8")
            ).hexdigest()
            if (
                legacy_contract_sha256 != ess_record.get("delegation_contract_sha256")
                or legacy_payload_sha256 != ess_record.get("approved_payload_sha256")
                or legacy_payload_sha256 != payload_sha256
            ):
                raise FusionAboWorkflowError(
                    "The legacy ESS reservation evidence does not match its immutable contract and payload."
                )
            # Only the historical missing-scheme defect proves the old core
            # validation could not have reached POST. The legacy environment
            # value could also be the bare hostname. A newly stricter local
            # validator rejecting any other old contract is not such proof.
            corrected_host = delegation_contract["fusion_environment_context"]["fusion_host"]
            corrected_environment = delegation_contract["fusion_environment_context"]["environment"]
            expected_legacy_contracts = []
            for legacy_environment in {
                corrected_environment,
                urlsplit(corrected_environment).netloc or corrected_environment,
            }:
                expected_legacy_contract = dict(delegation_contract)
                expected_legacy_contract["fusion_environment_context"] = {
                    "environment": legacy_environment,
                    "fusion_host": urlsplit(corrected_host).netloc,
                }
                expected_legacy_contracts.append(_canonical_json(expected_legacy_contract))
            if _canonical_json(legacy_contract) not in expected_legacy_contracts:
                raise FusionAboWorkflowError(
                    "The legacy ESS contract is not the proven pre-dispatch missing-scheme case; do not submit again automatically."
                )
            legacy_valid, _ = _run_ess_contract_validation_command(
                validation_command,
                expected_payload_sha256=legacy_payload_sha256,
                runner=runner,
            )
            if legacy_valid:
                raise FusionAboWorkflowError(
                    "The legacy ESS contract is valid, so its prior dispatch remains indeterminate; do not submit again automatically."
                )
            _write_json_atomic(corrected_contract_path, delegation_contract)
            corrected_validation_command = list(validation_command)
            corrected_validation_command[
                corrected_validation_command.index(str(contract_path))
            ] = str(corrected_contract_path)
            corrected_valid, _ = _run_ess_contract_validation_command(
                corrected_validation_command,
                expected_payload_sha256=payload_sha256,
                runner=runner,
            )
            if not corrected_valid:
                raise FusionAboWorkflowError(
                    "The corrected ESS contract did not pass local validation."
                )
            contract_validated_for_dispatch = True
            _write_json_atomic(failed_contract_path, legacy_contract)
            _write_json_atomic(contract_path, delegation_contract)
            ess_record.update(
                {
                    "state": "validated_ready_to_dispatch",
                    "delegation_contract_sha256": contract_sha256,
                    "recovery": {
                        "reason": "legacy_pre_dispatch_validation_failure",
                        "previous_delegation_contract_sha256": legacy_contract_sha256,
                        "previous_delegation_contract_evidence": failed_contract_path.name,
                        "dispatch_attempted": False,
                        "recovered_at": _utc_timestamp(),
                    },
                }
            )
            _write_json_atomic(ess_record_path, ess_record)
            state = "validated_ready_to_dispatch"
        elif state == "pre_dispatch_failed_retryable":
            valid, _ = _run_ess_contract_validation_command(
                validation_command,
                expected_payload_sha256=payload_sha256,
                runner=runner,
            )
            if not valid or ess_record.get("delegation_contract_sha256") != contract_sha256:
                raise FusionAboWorkflowError(
                    "The retryable ESS reservation no longer matches its validated contract."
                )
            contract_validated_for_dispatch = True
            ess_record.update({"state": "validated_ready_to_dispatch", "updated_at": _utc_timestamp()})
            _write_json_atomic(ess_record_path, ess_record)
            state = "validated_ready_to_dispatch"
        elif state == "dispatch_started":
            request_id = _reconcile_ess_dispatch_started_request_id(
                args,
                ess_record=ess_record,
                payload=payload,
                runner=runner,
            )
            ess_record.update(
                {
                    "state": "submitted",
                    "request_id": request_id,
                    "reconciled_at": _utc_timestamp(),
                    "reconciliation": {
                        "method": "read_only_recent_ess_request_lookup",
                        "dispatch_started_at": ess_record.get("dispatch_started_at"),
                    },
                }
            )
            _write_json_atomic(ess_record_path, ess_record)
            state = "submitted"
        if state == "validated_ready_to_dispatch":
            if not contract_path.exists():
                raise FusionAboWorkflowError(
                    "The validated ESS reservation has no delegation contract."
                )
            ready_contract = _read_json_mapping(
                contract_path, "validated ESS delegation contract"
            )
            ready_contract_sha256 = hashlib.sha256(
                _canonical_json(ready_contract).encode("utf-8")
            ).hexdigest()
            ready_valid = contract_validated_for_dispatch
            if not ready_valid:
                ready_valid, _ = _run_ess_contract_validation_command(
                    validation_command,
                    expected_payload_sha256=payload_sha256,
                    runner=runner,
                )
            if (
                not ready_valid
                or ready_contract_sha256 != contract_sha256
                or ready_contract_sha256 != ess_record.get("delegation_contract_sha256")
                or ess_record.get("approved_payload_sha256") != payload_sha256
            ):
                raise FusionAboWorkflowError(
                    "The validated ESS reservation no longer matches the corrected contract."
                )
        if state not in {"validated_ready_to_dispatch", "submitted"}:
            raise FusionAboWorkflowError(
                "ESS submission may already have been attempted but no durable request id was recorded; do not submit again automatically."
            )
        if state == "validated_ready_to_dispatch":
            if (
                workflow_record.get("state") != "awaiting_ess_approval"
                or not getattr(args, "approve_ess", False)
                or getattr(args, "ess_approval_sha256", None) != workflow_record.get("ess_preview_payload_sha256")
                or current_payload_sha != workflow_record.get("ess_preview_payload_sha256")
            ):
                raise FusionAboWorkflowError(
                    "A separate current approval is required before every new ESS POST, including a pre-dispatch retry."
                )
            ess_record.update({"state": "dispatch_started", "dispatch_started_at": _utc_timestamp()})
            _write_json_atomic(ess_record_path, ess_record)
            submit_succeeded, submit_result = _run_ess_submit_json_command(
                [
                    sys.executable,
                    str(ESS_ABO_ADAPTER),
                    "--delegation-contract-file",
                    str(contract_path),
                    "--submit-only",
                    "--properties",
                    args.properties,
                    "--token-cache",
                    args.fusion_token_cache,
                ] + (["--no-open-browser"] if args.no_open_browser else []),
                runner=runner,
            )
            if not submit_succeeded:
                diagnostics = _required_mapping(
                    submit_result.get("diagnostics"), "ESS failure diagnostics"
                )
                dispatch_attempted = diagnostics.get("dispatch_attempted") is True
                ess_record.update(
                    {
                        "state": (
                            "dispatch_indeterminate"
                            if dispatch_attempted
                            else "pre_dispatch_failed_retryable"
                        ),
                        "last_failure": {
                            "failure_class": diagnostics.get("failure_class"),
                            "failure_stage": diagnostics.get("failure_stage"),
                            "dispatch_attempted": dispatch_attempted,
                        },
                        "updated_at": _utc_timestamp(),
                    }
                )
                _write_json_atomic(ess_record_path, ess_record)
                if dispatch_attempted:
                    raise FusionAboWorkflowError(
                        "ESS submission became indeterminate after dispatch began; do not submit again automatically."
                    )
                raise FusionAboWorkflowError(
                    "ESS submission failed before dispatch and is safely retryable with current approval."
                )
            execution = _required_mapping(submit_result.get("execution_result"), "ESS submission result")
            raw_request_id = execution.get("requestId")
            if isinstance(raw_request_id, bool) or not isinstance(raw_request_id, int) or raw_request_id < 1:
                raise FusionAboWorkflowError("ESS submission did not return a valid request id; do not resubmit automatically.")
            request_id = raw_request_id
            ess_record.update(
                {"state": "submitted", "request_id": request_id, "submitted_at": _utc_timestamp()}
            )
            _write_json_atomic(ess_record_path, ess_record)
    if isinstance(request_id, bool) or not isinstance(request_id, int) or request_id < 1:
        raise FusionAboWorkflowError("The persisted ESS request id is invalid.")
    monitor_result = _run_ess_monitor_json_command(
        [
            sys.executable,
            str(ESS_ABO_ADAPTER),
            "--request-id",
            str(request_id),
            "--wait-seconds",
            str(args.ess_wait_seconds),
            "--poll-interval",
            str(args.ess_poll_interval_seconds),
            "--properties",
            args.properties,
            "--token-cache",
            args.fusion_token_cache,
        ] + (["--no-open-browser"] if args.no_open_browser else []),
        request_id=request_id,
        runner=runner,
    )
    safe_result = _safe_ess_result(monitor_result, request_id=request_id)
    ess_record.update({"state": "terminal" if safe_result["terminal"] else "monitoring", "last_result": safe_result, "updated_at": _utc_timestamp()})
    _write_json_atomic(ess_record_path, ess_record)
    workflow_record.update(
        {"ess_submission_record_ref": _relative_to_repo(ess_record_path), "ess_sync": safe_result, "updated_at": _utc_timestamp()}
    )
    _write_json_atomic(workflow_record_path, workflow_record)
    return safe_result


def _validated_wait(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise FusionAboWorkflowError(f"{field_name} must be a positive integer.")
    return value


def _validate_adaptive_status_for_ess(
    workflow_preview: Mapping[str, Any],
    workflow_record: Mapping[str, Any],
    status: Mapping[str, Any],
) -> None:
    """Prove the final child result belongs to this exact approved operation."""

    components = _required_mapping(workflow_preview.get("components"), "workflow preview components")
    adaptive = _required_mapping(components.get("adaptive_search"), "workflow preview adaptive component")
    submission = _required_mapping(
        workflow_record.get("adaptive_submission"), "persisted Adaptive Search submission"
    )
    if status.get("schema_version") != "1.0":
        raise FusionAboWorkflowError("Adaptive Search final status has an unsupported schema version.")
    expected = {
        "publish_operation_id": submission.get("publish_operation_id"),
        "project_id": workflow_preview.get("project_id"),
        "target": adaptive.get("target"),
        "entities": list(adaptive.get("entities", [])),
        "publish_type": adaptive.get("publish_type"),
    }
    for field, expected_value in expected.items():
        if status.get(field) != expected_value:
            raise FusionAboWorkflowError(
                "Adaptive Search final status does not match the persisted approved operation; ESS is blocked."
            )
    if status.get("state") != "SUCCEEDED" or status.get("eligible_for_ess") is not True:
        raise FusionAboWorkflowError("Adaptive Search final status is not eligible for ESS.")
    _require_nonblank_string(status.get("adaptive_search_job_id"), "Adaptive Search final job id")
    if list(status.get("final_entity_readiness", [])) != list(ADAPTIVE_SEARCH_REQUIRED_ENTITIES):
        raise FusionAboWorkflowError(
            "Adaptive Search final status lacks exact enabled-entity readiness evidence; ESS is blocked."
        )


def _run_automatic_downstream_controller(
    args: argparse.Namespace,
    *,
    workflow_preview: Mapping[str, Any],
    approval_record_ref: str,
    approval_record_fingerprint: str,
    workflow_record_path: Path,
    workflow_record: dict[str, Any],
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    sleeper: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
    continuous: bool = False,
    initial_status: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Monitor the separately approved child and stop at the ESS approval gate."""

    _, project_root, _, _, _, _ = _project_workspace(args.project_id)
    wait_seconds = _validated_wait(args.adaptive_search_wait_seconds, "adaptive_search_wait_seconds")
    poll_seconds = _validated_wait(args.adaptive_search_poll_interval_seconds, "adaptive_search_poll_interval_seconds")
    _validated_wait(args.ess_wait_seconds, "ess_wait_seconds")
    _validated_wait(args.ess_poll_interval_seconds, "ess_poll_interval_seconds")
    live = workflow_record.get("schema_version") == "2.0"
    if live:
        operation_path, _ = _bound_live_adaptive_operation(
            project_root, workflow_record_path, workflow_record, workflow_preview)
        _require_verified_adaptive_load(operation_path)
        if continuous:
            expected = _adaptive_monitoring_binding(workflow_record, mode="continuous")
            if workflow_record.get("adaptive_monitoring_choice") != expected:
                raise FusionAboWorkflowError("Explicit monitoring choice for this exact operation is required.")
            if poll_seconds != 15:
                raise FusionAboWorkflowError("The current monitoring choice requires 15-second intervals.")
    else:
        _, operation_path = _adaptive_submission(
            args,
            project_root=project_root,
            workflow_preview=workflow_preview,
            workflow_record_path=workflow_record_path,
            workflow_record=workflow_record,
            approval_record_ref=approval_record_ref,
            approval_record_fingerprint=approval_record_fingerprint,
            runner=runner,
        )
    deadline = monotonic() + float(wait_seconds)
    while True:
        try:
            adaptive_status = _safe_public_adaptive_status(
                initial_status if initial_status is not None else _adaptive_status_once(
                    args,
                    project_root=project_root,
                    operation_record_path=operation_path,
                    runner=runner,
                )
            )
            initial_status = None
        except (Exception, KeyboardInterrupt):
            if live:
                workflow_record["state"] = "awaiting_adaptive_monitoring_choice"
                _persist_live_checkpoint(args, workflow_record_path, workflow_record)
            raise
        read_error = adaptive_status.get("status_read_error")
        is_status_read_failure = (
            isinstance(read_error, Mapping)
            and read_error.get("failure_stage") in ADAPTIVE_SEARCH_STATUS_READ_FAILURE_STAGES
        )
        if is_status_read_failure:
            failure_count = workflow_record.get("adaptive_search_read_failure_count", 0)
            if isinstance(failure_count, bool) or not isinstance(failure_count, int) or failure_count < 0:
                failure_count = 0
            failure_count += 1
            workflow_record["adaptive_search_read_failure_count"] = failure_count
            workflow_record["adaptive_search_last_read_error"] = dict(read_error)
        else:
            failure_count = 0
            workflow_record["adaptive_search_read_failure_count"] = 0
            workflow_record.pop("adaptive_search_last_read_error", None)
        workflow_record.update(
            {"last_adaptive_search_status": adaptive_status,
             "last_adaptive_search_checked_at": _utc_timestamp(), "updated_at": _utc_timestamp()}
        )
        _write_json_atomic(workflow_record_path, workflow_record)
        if adaptive_status.get("monitoring", {}).get("stage") == "data_loader":
            return {
                "handover_version": "2.0", "status": "pending", "stage": "adaptive_data_loader",
                "workflow_status": "adaptive_load_submitted", "target": workflow_preview["target"],
                "adaptive_search": adaptive_status, "workflow_record_ref": _relative_to_repo(workflow_record_path),
                "next_action": "Check the Adaptive Search load status and continue.",
            }
        if is_status_read_failure:
            failure_class = read_error.get("failure_class")
            auth_failure = failure_class in ADAPTIVE_SEARCH_AUTH_FAILURE_CLASSES
            if auth_failure or failure_count >= ADAPTIVE_SEARCH_MAX_CONSECUTIVE_READ_FAILURES:
                workflow_record["state"] = "awaiting_adaptive_monitoring_choice"
                workflow_record["updated_at"] = _utc_timestamp()
                _persist_live_checkpoint(args, workflow_record_path, workflow_record)
                reason = (
                    "Adaptive Search status reads are blocked by authentication or authorization. "
                    "Restore access, then check the same publish job again."
                    if auth_failure else
                    "Adaptive Search status could not be read after three consecutive attempts. "
                    "Check connectivity or the recorded read error, then resume the same publish job."
                )
                return {
                    "status": "incomplete",
                    "workflow_status": "adaptive_search_status_read_failed",
                    "adaptive_search": adaptive_status,
                    "status_read_error": dict(read_error),
                    "consecutive_read_failures": failure_count,
                    "ess_sync": {"status": "not_started", "side_effects": "No ESS POST was attempted."},
                    "workflow_record_ref": _relative_to_repo(workflow_record_path),
                    "next_action": reason,
                }
        if adaptive_status.get("state") == "SUCCEEDED" and adaptive_status.get("eligible_for_ess") is True:
            try:
                _validate_adaptive_status_for_ess(
                    workflow_preview, workflow_record, adaptive_status
                )
            except FusionAboWorkflowError:
                workflow_record.update(
                    {"state": "adaptive_search_indeterminate", "updated_at": _utc_timestamp()}
                )
                _write_json_atomic(workflow_record_path, workflow_record)
                if live:
                    _persist_live_checkpoint(args, workflow_record_path, workflow_record)
                return {
                    "status": "failed",
                    "workflow_status": "adaptive_search_indeterminate",
                    "adaptive_search": adaptive_status,
                    "ess_sync": {"status": "not_started", "side_effects": "No ESS POST was attempted."},
                    "workflow_record_ref": _relative_to_repo(workflow_record_path),
                }
            _, payload = _ess_payload(workflow_preview, adaptive_status=adaptive_status)
            payload_sha = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
            workflow_record.update({
                "state": "awaiting_ess_approval", "ess_preview_payload_sha256": payload_sha,
                "ess_preview_target": workflow_preview["target"], "updated_at": _utc_timestamp(),
            })
            _write_json_atomic(workflow_record_path, workflow_record)
            if live:
                _persist_live_checkpoint(args, workflow_record_path, workflow_record)
            return {
                "status": "approval_required", "workflow_status": "awaiting_ess_approval",
                "adaptive_search": adaptive_status,
                "approval_required": {"stage": "ess", "target": workflow_preview["target"],
                                      "operation": "Unified Asset Read Model Sync", "payload": payload,
                                      "payload_sha256": payload_sha},
                "workflow_record_ref": _relative_to_repo(workflow_record_path),
            }
        if adaptive_status.get("terminal") is True:
            workflow_record.update({"state": "adaptive_search_failed", "updated_at": _utc_timestamp()})
            _write_json_atomic(workflow_record_path, workflow_record)
            if live:
                _persist_live_checkpoint(args, workflow_record_path, workflow_record)
            return {
                "status": "failed",
                "workflow_status": "adaptive_search_failed",
                "adaptive_search": adaptive_status,
                "ess_sync": {"status": "not_started", "side_effects": "No ESS POST was attempted."},
                "workflow_record_ref": _relative_to_repo(workflow_record_path),
            }
        if live and not continuous:
            workflow_record["state"] = "awaiting_adaptive_monitoring_choice"
            _persist_live_checkpoint(args, workflow_record_path, workflow_record)
            return _adaptive_monitoring_result(workflow_record, workflow_record_path)
        remaining = deadline - monotonic()
        if remaining <= 0:
            workflow_record.update({"state": "monitoring_timeout", "updated_at": _utc_timestamp()})
            workflow_record["adaptive_monitoring_elapsed_seconds"] = float(wait_seconds) - remaining
            _write_json_atomic(workflow_record_path, workflow_record)
            if live:
                _persist_live_checkpoint(args, workflow_record_path, workflow_record)
            return {
                "status": "incomplete",
                "workflow_status": "adaptive_search_monitoring_timeout",
                "adaptive_search": adaptive_status,
                "ess_sync": {"status": "not_started", "side_effects": "No ESS POST was attempted."},
                "workflow_record_ref": _relative_to_repo(workflow_record_path),
                "elapsed_wait_seconds": float(wait_seconds) - remaining,
                "next_action": "Monitoring stopped at its time limit. Check the Adaptive Search publish status later, or explicitly choose to keep checking again. Never resubmit the load or publish.",
            }
        if live:
            workflow_record["state"] = "adaptive_search_monitoring"
            progress = _adaptive_monitoring_result(workflow_record, workflow_record_path)
            print(json.dumps({"state": "workflow_progress", **_with_customer_presentation(progress)},
                             ensure_ascii=False), flush=True)
        try:
            sleeper(min(float(poll_seconds), remaining))
        except KeyboardInterrupt:
            if live:
                workflow_record["state"] = "awaiting_adaptive_monitoring_choice"
                _persist_live_checkpoint(args, workflow_record_path, workflow_record)
            raise


def _add_runtime_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--properties",
        default=str(REPO_ROOT / "core" / "auth" / "fusionEnv.properties"),
        help="Private local profile containing approved Fusion and CPQ OAuth fields. Keep it gitignored.",
    )
    parser.add_argument(
        "--process-variable-name",
        help="Exact CPQ Standard Process variable name. Omit only when --use-default-process is selected.",
    )
    parser.add_argument(
        "--use-default-process",
        action="store_true",
        help="Explicitly select the CPQ Dev default process variable name, oraclecpqo, for verification.",
    )
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--fusion-token-cache", default=DEFAULT_FUSION_TOKEN_CACHE)
    parser.add_argument("--cpq-token-cache", default=DEFAULT_CPQ_TOKEN_CACHE)
    parser.add_argument("--boss-token-cache", default=DEFAULT_BOSS_TOKEN_CACHE)
    parser.add_argument("--fusion-common-token-cache", default=DEFAULT_FUSION_COMMON_TOKEN_CACHE)
    parser.add_argument("--auth-code")
    parser.add_argument("--code-verifier")
    parser.add_argument("--redirect-url")
    parser.add_argument(
        "--callback-timeout",
        type=int,
        default=rest_client_common.DEFAULT_CALLBACK_TIMEOUT_SECONDS,
    )
    parser.add_argument("--no-open-browser", action="store_true")
    parser.add_argument("--force-fusion-login", action="store_true")
    parser.add_argument("--force-cpq-login", action="store_true")


def _add_automatic_controller_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--adaptive-search-wait-seconds",
        type=int,
        default=ADAPTIVE_SEARCH_DEFAULT_WAIT_SECONDS,
        help="Bounded automatic Adaptive Search monitoring time; status reads remain GET-only.",
    )
    parser.add_argument(
        "--adaptive-search-poll-interval-seconds",
        type=int,
        default=ADAPTIVE_SEARCH_DEFAULT_POLL_INTERVAL_SECONDS,
        help="Seconds between automatic Adaptive Search GET-only status reads.",
    )
    parser.add_argument(
        "--ess-wait-seconds",
        type=int,
        default=ESS_DEFAULT_WAIT_SECONDS,
        help="Bounded core ESS monitoring time after the single conditional ESS submission.",
    )
    parser.add_argument(
        "--ess-poll-interval-seconds",
        type=int,
        default=ESS_DEFAULT_POLL_INTERVAL_SECONDS,
        help="Seconds between core ESS GET-only status reads.",
    )


def _live_context(args, plan, target, workflow_id):
    """Business scope/provenance only; never a Core execution or approval record."""
    project_id = _safe_project_id(args.project_id)
    process = plan["validated_process_variable_name"]
    return {"schema_version": "2.0", "approval_fingerprint": workflow_id,
            "project_id": project_id, "target": dict(target),
            "validated_process_variable_name": process,
            "components": {
                "adaptive_search": {"target": _adaptive_search_target(target),
                    "entities": list(ADAPTIVE_SEARCH_REQUIRED_ENTITIES), "publish_type": "selective"},
                "ess_sync": {"job_definition_id": "JobDefinition://oracle/apps/ess/configPriceQuote/assets/UnifiedAssetReadModelSyncMasterJob",
                    "application": "CrmEss", "product": "CPQ", "request_parameters": [],
                    "description": f"FDOS Fusion ABO Unified Asset Read Model Sync | project={project_id} | process={process}"}}}


def _persist_live_checkpoint(args, path, record):
    """Persist non-executable state and register a sanitized durable skill run."""
    _write_json_atomic(path, record)
    project_id, root, state_path, index_path, state, index = _project_workspace(args.project_id)
    timestamp = _utc_timestamp()
    run_id = _new_run_id("live-checkpoint", timestamp)
    run_path = root / "state" / "runs" / f"{run_id}.json"
    run = {"run_id": run_id, "skill_id": TASK_SKILL_ID, "started_at": timestamp,
           "completed_at": timestamp, "status": "completed",
           "inputs": ["workflow_identity"], "outputs": [_relative_to_repo(path)],
           "artifact_refs": [_relative_to_repo(path)],
           "notes": f"Checkpoint state: {record['state']}. Core preflight and Task Hook preview use the persisted 26.10 protocol."}
    _write_json_atomic(run_path, run)
    _, usage = _token_usage(project_id=project_id, project_root=root, timestamp=timestamp,
        trigger=args.command, artifact_paths=[path, run_path], files_read=3,
        notes="Checkpoint estimate excludes live Core source/preview data and private configuration.")
    run["token_usage"] = usage
    _write_json_atomic(run_path, run)
    _append_artifact_records(index, timestamp=timestamp, records=[
        _artifact_record(artifact_id=f"live-checkpoint-{run_id}", name="Fusion ABO Live Checkpoint",
            artifact_type="validation_result", location=_relative_to_repo(path), timestamp=timestamp,
            checksum=_sha256_file(path)),
        _artifact_record(artifact_id=f"skill-run-{run_id}", name="Fusion ABO Live Stage Run",
            artifact_type="skill_run", location=_relative_to_repo(run_path), timestamp=timestamp,
            checksum=_sha256_file(run_path))])
    project_status = ("ready_for_review" if record["state"] == "completed" else "blocked"
                      if record["state"] in {"cpq_indeterminate", "cpq_verification_failed", "adaptive_search_indeterminate", "preparation_failed"}
                      else "in_progress")
    _update_project_state(state, latest_run_ref=_relative_to_repo(run_path), status=project_status, timestamp=timestamp)
    _write_json_atomic(index_path, index)
    _write_json_atomic(state_path, state)


def _load_live_workflow(args):
    _, root, _, _, _, _ = _project_workspace(args.project_id)
    path = _workflow_record_path(root, args.workflow_id)
    record = _read_json_mapping(path, "live workflow checkpoint")
    if (record.get("schema_version") != "2.0" or record.get("project_id") != args.project_id
            or record.get("workflow_approval_fingerprint") != args.workflow_id):
        raise FusionAboWorkflowError("The exact v2 workflow identity is required.")
    context = _required_mapping(record.get("workflow_context"), "workflow business context")
    if (context.get("approval_fingerprint") != args.workflow_id
            or context.get("project_id") != args.project_id
            or context.get("target") != record.get("target")):
        raise FusionAboWorkflowError("Workflow business identity is inconsistent.")
    properties = _read_properties(args.properties)
    if (_environment_identity(properties) != _environment_identity({"environment": record["target"]["environment"]})
            or _https_host(properties, "restBaseUrl") != _environment_identity({"environment": record["target"]["fusion_host"]})):
        raise FusionAboWorkflowError("Configured target differs from the submitted workflow.")
    return root, path, record, context, properties


def _live_stage_result(record, path, *, stage, status=None, next_action=None):
    return {"handover_version": "2.0", "status": status or record["state"],
            "workflow_status": record["state"], "stage": stage, "target": record["target"],
            "validated_process_variable_name": record["workflow_context"]["validated_process_variable_name"],
            "presentation_context": record.get("presentation_context", {}),
            "workflow_id": record["workflow_approval_fingerprint"],
            "workflow_record_ref": _relative_to_repo(path),
            "next_action": next_action or "Resume the exact workflow; never replay a submission."}


def _cpq_preparation_scope(args, plan, semantic):
    fingerprint = semantic.get("preflight_fingerprint")
    if not isinstance(fingerprint, str) or not re.fullmatch(r"[a-f0-9]{64}", fingerprint):
        raise FusionAboWorkflowError("A validated semantic CPQ preflight fingerprint is required.")
    return {"project_id": args.project_id, "target": _safe_target(semantic["target"], "CPQ target"),
            "business_plan": plan, "preflight_fingerprint": fingerprint}


def _cpq_preparation_result(record, path):
    proposal = record["cpq_preparation_proposal"]
    return {**_live_stage_result(record, path, stage="cpq_preparation", status="approval_required"),
            "project_id": record["project_id"],
            "components": {"cpq_settings": {"operations": record["business_plan"]["operations"]}},
            "approval_required": {"stage": "cpq_preparation", "target": record["target"],
                                  "proposal": proposal, "proposal_sha256": record["cpq_preparation_sha256"]}}


def preview_cpq_preparation_from_args(args):
    """Read current business state and stop before workbook/Core preparation."""
    root = _project_workspace(args.project_id)[1]
    preflight, plan, semantic, properties = _prepare_cpq_settings_write(args)
    scope = _cpq_preparation_scope(args, plan, semantic)
    target = scope["target"]
    # Serialize equivalent preparation attempts across the project/target/scope.
    scope_key = hashlib.sha256(_canonical_json({"target": target, "project_id": args.project_id,
                                                "process": plan["validated_process_variable_name"]}).encode()).hexdigest()
    workflow_id = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
    with _workflow_lock(root, scope_key), _workflow_lock(root, workflow_id):
        for existing in (root / TASK_ARTIFACT_DIRECTORY).glob("automatic-workflow-*.json"):
            prior = _read_json_mapping(existing, "prior workflow checkpoint")
            if prior.get("schema_version") == "1.0" and prior.get("state") in {
                "reserved_before_cpq_execution", "cpq_not_completed", "cpq_indeterminate",
            }:
                raise FusionAboWorkflowError("A legacy CPQ outcome is unresolved; reconcile it before preparing a new load.")
            if (prior.get("schema_version") == "2.0" and prior.get("target") == target
                    and prior.get("state") not in {"cancelled", "expired", "preparation_failed", "completed"}
                    and prior.get("workflow_context", {}).get("validated_process_variable_name") == plan["validated_process_variable_name"]):
                raise FusionAboWorkflowError("A matching workflow already exists; resume/status-check it instead of preparing another load.")
        path = _workflow_record_path(root, workflow_id)
        issued = datetime.now(timezone.utc).replace(microsecond=0)
        proposal = {"schema_version": "1.0", "purpose": "cpq_preparation_only", **scope,
                    "workflow_id": workflow_id, "issued_at": _utc_timestamp(issued),
                    "expires_at": _utc_timestamp(issued + timedelta(seconds=CPQ_SETTINGS_APPROVAL_TTL_SECONDS))}
        record = {"schema_version": "2.0", "state": "awaiting_cpq_preparation_approval", "project_id": args.project_id,
                  "workflow_approval_fingerprint": workflow_id, "target": target,
                  "workflow_context": _live_context(args, plan, target, workflow_id),
                  "business_plan": plan, "created_at": _utc_timestamp(),
                  "cpq_preparation_proposal": proposal,
                  "cpq_preparation_sha256": hashlib.sha256(_canonical_json(proposal).encode()).hexdigest(),
                  "presentation_context": {"target": target, "feature_states": preflight.get("feature_states", {})}}
        if preflight.get("status") == "requires_abo_delta_action_library_function_recovery":
            record["presentation_context"]["cpq_function_recovery_current_value"] = (
                preflight["cpq_preflight"]["abo_delta_action_library_function"]["configured_function"])
        _persist_live_checkpoint(args, path, record)
        return _cpq_preparation_result(record, path)


def prepare_cpq_load_from_args(args, *, load_runner=None):
    """Consume preparation permission and return a Core workbook handoff."""
    if (getattr(args, "approve_cpq_preparation", False) is not True
            or not getattr(args, "workflow_id", None) or not getattr(args, "cpq_preparation_sha256", None)):
        raise FusionAboWorkflowError("Approve the current CPQ preparation proposal before preparing a load.")
    root, path, record, context, properties = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, properties = _load_live_workflow(args)
        if record["state"] != "awaiting_cpq_preparation_approval":
            raise FusionAboWorkflowError("This preparation approval is already consumed or unavailable; never restart its prepared load.")
        proposal = _required_mapping(record.get("cpq_preparation_proposal"), "CPQ preparation proposal")
        digest = hashlib.sha256(_canonical_json(proposal).encode()).hexdigest()
        if (record.get("cpq_preparation_sha256") != digest or args.cpq_preparation_sha256 != digest
                or proposal.get("purpose") != "cpq_preparation_only"
                or proposal.get("workflow_id") != args.workflow_id
                or proposal.get("project_id") != args.project_id
                or proposal.get("target") != record["target"]
                or proposal.get("business_plan") != record.get("business_plan")):
            raise FusionAboWorkflowError("Preparation approval differs from the exact current business proposal.")
        issued = _parse_rfc3339_timestamp(proposal["issued_at"], "preparation issued_at")
        expires = _parse_rfc3339_timestamp(proposal["expires_at"], "preparation expires_at")
        now = datetime.now(timezone.utc)
        if expires != issued + timedelta(seconds=CPQ_SETTINGS_APPROVAL_TTL_SECONDS) or not issued <= now <= expires:
            record["state"] = "expired"
            _persist_live_checkpoint(args, path, record)
            raise FusionAboWorkflowError("Preparation proposal expired; create and approve a fresh proposal.")
        fresh_args = argparse.Namespace(**vars(args))
        selection = record["business_plan"].get("process_selection", {})
        default_selected = selection.get("selection_source") == "cpq_default"
        fresh_args.process_variable_name = None if default_selected else context["validated_process_variable_name"]
        fresh_args.use_default_process = default_selected
        if args.process_variable_name and args.process_variable_name != context["validated_process_variable_name"]:
            raise FusionAboWorkflowError("Process differs from the approved preparation proposal.")
        if args.use_default_process and not default_selected:
            raise FusionAboWorkflowError("Default selection differs from the approved preparation proposal.")
        try:
            preflight, plan, semantic, properties = _prepare_cpq_settings_write(fresh_args)
            expected = {key: proposal[key] for key in ("project_id", "target", "business_plan", "preflight_fingerprint")}
            if _cpq_preparation_scope(args, plan, semantic) != expected:
                raise FusionAboWorkflowError("CPQ scope or prerequisites changed; create and approve a fresh proposal.")
        except Exception:
            record["state"] = "preparation_failed"
            _persist_live_checkpoint(args, path, record)
            raise
        # One-use intent is saved BEFORE generation/Core preflight. It is not
        # a Core approval, and is never forwarded as load approval.
        record.update({"state": "preparing_cpq", "cpq_preparation_approved_at": _utc_timestamp(),
                       "cpq_preparation_approval_consumed": True})
        _persist_live_checkpoint(args, path, record)
        target = record["target"]
        workflow_id = args.workflow_id
        try:
            loads = prepare_cpq_settings_data_loader_loads(plan=plan, target=target, project_root=root,
                properties=Path(args.properties), token_cache=args.fusion_token_cache)
            if len(loads) != 1:
                raise FusionAboWorkflowError("The fixed CPQ stage requires exactly one workbook.")
            _, load = next(iter(loads.items()))
            stored = json.loads(json.dumps(load))
            stored["workbook_handoff"].pop("authentication_reference", None)
            record.update({"state": "cpq_workbook_handoff", "cpq_loader": stored})
        except BaseException:
            record["state"] = "preparation_failed"
            _persist_live_checkpoint(args, path, record)
            raise
        _persist_live_checkpoint(args, path, record)
        return {**_live_stage_result(record, path, stage="cpq_data_loader", status="handoff_required"),
            "core_data_loader_handoff": load["workbook_handoff"]}


def accept_cpq_workbook_from_args(args):
    from cpq_settings_write_executor import accept_workbook_result
    root, path, record, _, _ = _load_live_workflow(args)
    result = _read_json_object(args.core_handoff_result, "Core workbook result")
    with _workflow_lock(root, args.workflow_id):
        root, path, record, _, _ = _load_live_workflow(args)
        if record["state"] != "cpq_workbook_handoff":
            raise FusionAboWorkflowError("This workflow is not awaiting a CPQ workbook.")
        load = json.loads(json.dumps(record["cpq_loader"]))
        load["workbook_handoff"]["authentication_reference"] = {
            "properties": str(args.properties),
            **({"token_cache": args.fusion_token_cache} if args.fusion_token_cache else {})}
        accepted = accept_workbook_result(load, result, project_root=root,
            properties=Path(args.properties), token_cache=args.fusion_token_cache)
        stored = json.loads(json.dumps(accepted))
        stored["workbook_handoff"].pop("authentication_reference", None)
        stored["preflight_handoff"].pop("authentication_reference", None)
        record.update({"state": "cpq_core_handoff", "cpq_loader": stored})
        _persist_live_checkpoint(args, path, record)
        from abo_presentation import render_workbook_access
        return {**_live_stage_result(record, path, stage="cpq_data_loader", status="handoff_required"),
            "workbook_access": render_workbook_access(Path(accepted["source_path"]), project_root=root),
            "core_data_loader_handoff": accepted["preflight_handoff"]}


def cancel_cpq_preparation_from_args(args):
    """Decline only an unconsumed business proposal, never a submitted Core load."""
    root, path, record, _, _ = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, _, _ = _load_live_workflow(args)
        if record["state"] != "awaiting_cpq_preparation_approval":
            raise FusionAboWorkflowError("Only an unconsumed preparation proposal can be cancelled here.")
        record["state"] = "cancelled"
        _persist_live_checkpoint(args, path, record)
        return _live_stage_result(record, path, stage="cpq_preparation",
            next_action="Preparation was declined; no workbook or load was started. Create a fresh proposal if needed.")


def check_cpq_load_from_args(args, *, runner=None, start_adaptive=True):
    from cpq_settings_write_executor import (
        data_loader_status_handoff, validate_data_loader_status_result,
        verify_cpq_settings_after_load,
    )
    root, path, record, context, properties = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, properties = _load_live_workflow(args)
        if record["state"] not in {"cpq_submitted", "cpq_verification_failed", "cpq_completed"}:
            raise FusionAboWorkflowError("This checkpoint does not contain a confirmed CPQ submission.")
        submission = dict(_required_mapping(record.get("cpq_submission"), "CPQ submission"))
        if (submission.get("target") != record["target"]
                or not re.fullmatch(r"UCMFA[0-9]+", str(submission.get("content_id", "")))
                or not re.fullmatch(r"[1-9][0-9]*", str(submission.get("request_id", "")))):
            raise FusionAboWorkflowError("CPQ receipt identity is invalid.")
        if not getattr(args, "core_handoff_result", None):
            handoff = data_loader_status_handoff(
                request_id=submission["request_id"], target=record["target"],
                output_directory=path.parent / path.stem / "cpq-status",
                properties=Path(args.properties), token_cache=args.fusion_token_cache)
            record["cpq_status_handoff"] = {key: value for key, value in handoff.items()
                                            if key != "authentication_reference"}
            _persist_live_checkpoint(args, path, record)
            return {**_live_stage_result(record, path, stage="cpq_data_loader", status="handoff_required"),
                "core_data_loader_handoff": handoff}
        handoff = _required_mapping(record.get("cpq_status_handoff"), "CPQ status handoff")
        checked = validate_data_loader_status_result(
            _read_json_object(args.core_handoff_result, "Core status result"), handoff)
        load_state = checked["status"]
        if load_state != "SUCCEEDED":
            record["last_cpq_load_status"] = load_state
            _persist_live_checkpoint(args, path, record)
            return {**_live_stage_result(record, path, stage="cpq_data_loader",
                status="pending" if load_state == "PENDING" else "blocked",
                next_action="Check the CPQ load status and continue." if load_state == "PENDING"
                else "Inspect the exact submitted load; no Adaptive Search or retry was attempted."),
                "data_loader_markdown": checked["markdown"]}
        if checked["markdown"]:
            print(json.dumps({"state": "data_loader_status", "markdown": checked["markdown"]}), flush=True)
        submission.update({"status": "completed", "data_loader_status": "SUCCEEDED"})
        try:
            fresh_args = argparse.Namespace(**vars(args))
            fresh_args.process_variable_name = context["validated_process_variable_name"]
            fresh_args.use_default_process = False
            fresh, _, _ = _run_preflight_from_args(fresh_args, properties=properties)
            if fresh.get("status") != "already_configured" or fresh.get("target") != record["target"]:
                raise FusionAboWorkflowError("Fresh CPQ process/enablement and Fusion prerequisites do not confirm completion.")
            verification = verify_cpq_settings_after_load(plan=record["business_plan"], oauth_properties=properties,
                submission=submission, token_cache=args.cpq_token_cache, timeout=args.timeout,
                oauth_options=_cpq_oauth_options_from_args(args))
        except Exception:
            record["state"] = "cpq_verification_failed"
            _persist_live_checkpoint(args, path, record)
            raise
        verification["target"] = record["target"]
        record["presentation_context"]["feature_states"] = fresh.get("feature_states", {})
        record.update({"state": "cpq_completed", "cpq_verification": verification})
        _persist_live_checkpoint(args, path, record)
    # Verified completion permits a proposal, not workbook generation or Core preflight.
    return preview_adaptive_preparation_from_args(args) if start_adaptive else _live_stage_result(
        record, path, stage="cpq_verification", next_action="Present the Adaptive Search preparation proposal.")


def _adaptive_preparation_scope(record, context):
    """Fixed business provenance only; no workbook, Core preview or source hash."""
    verification = _required_mapping(record.get("cpq_verification"), "verified CPQ completion")
    submission = _required_mapping(record.get("cpq_submission"), "CPQ receipt")
    operations = verification.get("completed_operations")
    expected_ids = [record["business_plan"]["operations"][0]["id"],
                    "verify_fusion_abo_enabled", "verify_abo_delta_action_library_function"]
    if (expected_ids[0] not in {"configure_fusion_abo_settings", "configure_abo_delta_action_library_function"}
            or verification.get("write_scope") != record["business_plan"].get("write_scope")
            or verification.get("status") != "completed" or verification.get("target") != record["target"]
            or verification.get("validated_process_variable_name") != context["validated_process_variable_name"]
            or not isinstance(operations, list) or len(operations) != 3
            or any(not isinstance(item, Mapping) for item in operations)
            or [item.get("id") for item in operations] != expected_ids
            or any(item.get("status") != "completed" for item in operations)
            or operations[0].get("data_loader_status") != "SUCCEEDED"
            or any(item.get("method") != "GET" or item.get("http_status") != 200 for item in operations[1:])
            or submission.get("target") != record["target"]
            or not re.fullmatch(r"UCMFA[0-9]+", str(submission.get("content_id", "")))
            or not re.fullmatch(r"[1-9][0-9]*", str(submission.get("request_id", "")))
            or any(operations[0].get(key) != submission.get(key) for key in ("request_id", "content_id", "target"))):
        raise FusionAboWorkflowError("Exact successful CPQ receipt and business readbacks are required before Adaptive Search preparation.")
    adaptive = context["components"]["adaptive_search"]
    if (adaptive.get("target") != _adaptive_search_target(record["target"])
            or adaptive.get("entities") != list(ADAPTIVE_SEARCH_REQUIRED_ENTITIES)
            or adaptive.get("publish_type") != "selective"):
        raise FusionAboWorkflowError("Adaptive Search preparation must retain the exact fixed selective scope.")
    return {"project_id": record["project_id"], "workflow_id": record["workflow_approval_fingerprint"],
            "target": record["target"], "cpq_process": context["validated_process_variable_name"],
            "adaptive_target": adaptive["target"], "entities": list(ADAPTIVE_SEARCH_REQUIRED_ENTITIES),
            "publish_type": "selective", "cpq_completion": {
                "request_id": submission["request_id"], "content_id": submission["content_id"],
                "write_scope": record["business_plan"].get("write_scope")}}


def _require_unsubmitted_adaptive(record, path):
    child_root = path.parent / path.stem / "adaptive-live"
    if any((child_root / name).exists() for name in ("submission-intent.json", "operation.json")):
        raise FusionAboWorkflowError("Adaptive Search may already be submitted; reconcile the exact operation without preparing another load.")
    if record.get("adaptive_initialization_blocker"):
        raise FusionAboWorkflowError("Initial Full Publish is required; Partial Publish preparation is blocked.")
    if record["state"] != "cpq_completed":
        raise FusionAboWorkflowError("Verified CPQ completion is required; running/submitted stages cannot be restarted.")


def _adaptive_preparation_result(record, path):
    permission = record["adaptive_preparation"]
    status = permission["status"]
    result = {**_live_stage_result(record, path, stage="adaptive_preparation"),
              "project_id": record["project_id"],
              "workflow_status": "awaiting_adaptive_preparation_approval" if status == "awaiting_approval"
                                 else "adaptive_preparation_" + status,
              "status": "approval_required" if status == "awaiting_approval" else "stopped",
              "next_action": "Request a fresh Adaptive Search preparation proposal; do not reload CPQ or reuse a Core preview."}
    if status == "awaiting_approval":
        result["approval_required"] = {"stage": "adaptive_preparation", "target": record["target"],
            "proposal": permission["proposal"], "proposal_sha256": permission["proposal_sha256"]}
    return result


def _validate_adaptive_preparation(record, context):
    permission = _required_mapping(record.get("adaptive_preparation"), "Adaptive Search preparation permission")
    proposal = _required_mapping(permission.get("proposal"), "Adaptive Search preparation proposal")
    digest = hashlib.sha256(_canonical_json(proposal).encode()).hexdigest()
    scope = _adaptive_preparation_scope(record, context)
    if (permission.get("proposal_sha256") != digest or proposal.get("purpose") != "adaptive_preparation_only"
            or {key: proposal.get(key) for key in scope} != scope):
        raise FusionAboWorkflowError("Adaptive Search proposal differs from the exact verified business scope.")
    issued = _parse_rfc3339_timestamp(proposal.get("issued_at"), "Adaptive preparation issued_at")
    expires = _parse_rfc3339_timestamp(proposal.get("expires_at"), "Adaptive preparation expires_at")
    if expires != issued + timedelta(seconds=CPQ_SETTINGS_APPROVAL_TTL_SECONDS) or issued > datetime.now(timezone.utc):
        raise FusionAboWorkflowError("Adaptive Search preparation validity is inconsistent.")
    return permission, digest, expires


def _initialization_module():
    if str(ADAPTIVE_SEARCH_EXECUTOR.parent) not in sys.path:
        sys.path.insert(0, str(ADAPTIVE_SEARCH_EXECUTOR.parent))
    import adaptive_publish_executor
    return adaptive_publish_executor


def _initialization_scope(record, context):
    scope = _adaptive_preparation_scope(record, context)
    return {**scope, "entities": list(_initialization_module().INITIALIZATION_ENTITIES), "publish_type": "full"}


def _initialization_work(path):
    return path.parent / path.stem / "adaptive-initialization"


def _require_unsubmitted_initialization(record, path):
    for work in (_initialization_work(path), path.parent / path.stem / "adaptive-live"):
        if any((work / name).exists() for name in ("submission-intent.json", "operation.json")):
            raise FusionAboWorkflowError("A publish may already be submitted; reconcile its exact receipt without restarting preparation.")
    blocker = record.get("adaptive_initialization_blocker", {})
    if (record["state"] != "cpq_completed" or blocker.get("reason") not in {"missing_metamodel", "empty_catalog"}
            or (blocker.get("reason") == "missing_metamodel" and blocker.get("http_status") != 400)):
        raise FusionAboWorkflowError("Initialization requires verified CPQ completion and an unresolved catalog blocker.")


def _validate_initialization_permission(record, context):
    permission = _required_mapping(record.get("adaptive_initialization"), "initialization permission")
    proposal = _required_mapping(permission.get("proposal"), "initialization proposal")
    digest = hashlib.sha256(_canonical_json(proposal).encode()).hexdigest()
    scope = _initialization_scope(record, context)
    if (proposal.get("purpose") != "adaptive_initialization_preparation_only"
            or permission.get("proposal_sha256") != digest
            or {key: proposal.get(key) for key in scope} != scope
            or not re.fullmatch(r"[a-f0-9]{32}", str(proposal.get("proposal_id", "")))):
        raise FusionAboWorkflowError("Initialization permission differs from the exact Full Publish scope.")
    issued = _parse_rfc3339_timestamp(proposal.get("issued_at"), "initialization issued_at")
    expires = _parse_rfc3339_timestamp(proposal.get("expires_at"), "initialization expires_at")
    if issued > datetime.now(timezone.utc) or expires != issued + timedelta(seconds=CPQ_SETTINGS_APPROVAL_TTL_SECONDS):
        raise FusionAboWorkflowError("Initialization permission validity is inconsistent.")
    return permission, digest, expires


def _initialization_result(record, path):
    permission = record.get("adaptive_initialization", {})
    phase = permission.get("status", "required")
    result = {**_live_stage_result(record, path, stage="adaptive_initialization"), "project_id": record["project_id"],
        "workflow_status": "awaiting_adaptive_initialization_approval" if phase == "awaiting_approval" else "adaptive_initialization_" + phase,
        "initialization_blocker": record.get("adaptive_initialization_blocker", {}),
        "initialization_status": record.get("last_initialization_status", {}),
        "next_action": "Full Publish can take 10 minutes or longer. Please wait about 8–10 minutes, then request: Check the Full Publish initialization status and continue." if phase == "submitted" else
                       "Review the Full Publish initialization proposal; do not reload CPQ or retry Partial Publish."}
    if phase == "awaiting_approval":
        result["status"] = "approval_required"
        result["approval_required"] = {"stage": "adaptive_initialization", "target": record["target"],
            "proposal": permission["proposal"], "proposal_sha256": permission["proposal_sha256"]}
    elif phase in {"failed", "indeterminate"}:
        result["next_action"] = "Initialization failed or its outcome is uncertain. Reconcile the exact recorded load/job; do not resubmit or retry Partial Publish."
    elif phase in {"cancelled", "expired", "preparation_failed", "consumed"}:
        result["next_action"] = "Initialization preparation stopped. Diagnose the blocker, then explicitly request a fresh Full Publish preparation proposal. Do not retry Partial Publish."
    return result


def _offer_initialization(args, path, record, context, *, refresh=False):
    _require_unsubmitted_initialization(record, path)
    if record.get("adaptive_initialization"):
        permission, _, expires = _validate_initialization_permission(record, context)
        if permission["status"] == "awaiting_approval" and datetime.now(timezone.utc) > expires:
            permission["status"] = "expired"
            _persist_live_checkpoint(args, path, record)
        if permission["status"] == "awaiting_approval" or not refresh:
            return _initialization_result(record, path)
    issued = datetime.now(timezone.utc).replace(microsecond=0)
    proposal = {"schema_version": "1.0", "purpose": "adaptive_initialization_preparation_only",
        **_initialization_scope(record, context), "proposal_id": uuid.uuid4().hex,
        "issued_at": _utc_timestamp(issued),
        "expires_at": _utc_timestamp(issued + timedelta(seconds=CPQ_SETTINGS_APPROVAL_TTL_SECONDS))}
    record["adaptive_initialization"] = {"status": "awaiting_approval", "proposal": proposal,
        "proposal_sha256": hashlib.sha256(_canonical_json(proposal).encode()).hexdigest()}
    _persist_live_checkpoint(args, path, record)
    return _initialization_result(record, path)


def _bound_initialization_receipt(root, path, record, context):
    receipt = _initialization_work(path) / "operation.json"
    receipt.resolve().relative_to(root.resolve())
    operation = _read_json_mapping(receipt, "initialization receipt")
    module = _initialization_module()
    module.validate_initialization_operation(operation)
    proposal = _required_mapping(record.get("adaptive_initialization", {}).get("proposal"), "initialization proposal")
    _validate_initialization_permission(record, context)
    if (operation.get("workflow_approval_fingerprint") != record["workflow_approval_fingerprint"]
            or operation.get("project_id") != record["project_id"]
            or operation.get("target") != context["components"]["adaptive_search"]["target"]
            or operation.get("publish_operation_id") != "afi_" + str(proposal.get("proposal_id"))):
        raise FusionAboWorkflowError("Initialization receipt does not belong to this exact workflow/scope.")
    loader = operation.get("internal_data_loader", {})
    if (not re.fullmatch(r"UCMFA[0-9]+", str(loader.get("content_id", "")))
            or not re.fullmatch(r"[1-9][0-9]*", str(loader.get("request_id", "")))):
        raise FusionAboWorkflowError("Initialization load correlation is invalid.")
    return operation, receipt


def _recover_initialization_receipt(args, root, path, record, context):
    if not (_initialization_work(path) / "operation.json").exists():
        if (_initialization_work(path) / "submission-intent.json").exists():
            record["adaptive_initialization"]["status"] = "indeterminate"
            _persist_live_checkpoint(args, path, record)
            return True
        return False
    operation, receipt = _bound_initialization_receipt(root, path, record, context)
    if record.get("adaptive_initialization", {}).get("status") != "verified":
        if record["adaptive_initialization"].get("status") not in {"failed", "indeterminate"}:
            record["adaptive_initialization"]["status"] = "submitted"
        record["state"] = "adaptive_initialization_submitted"
        record["initialization_operation_record_ref"] = _relative_to_repo(receipt)
        _persist_live_checkpoint(args, path, record)
        return True
    proof = operation.get("initialization_verified", {})
    verified = operation.get("verified_data_loader", {})
    expected = {"publish_operation_id": operation["publish_operation_id"], "project_id": record["project_id"],
                "target": operation["target"], "job_id": operation.get("adaptive_search_job_id"),
                "entities": list(ADAPTIVE_SEARCH_REQUIRED_ENTITIES)}
    if (not expected["job_id"] or proof != expected or verified.get("status") != "SUCCEEDED"
            or verified.get("request_id") != operation["internal_data_loader"]["request_id"]
            or verified.get("publish_operation_id") != operation["publish_operation_id"]
            or verified.get("target") != operation["target"] or verified.get("project_id") != record["project_id"]):
        raise FusionAboWorkflowError("Saved initialization completion is not bound to the exact successful load/job/catalog.")
    return False


def preview_initialization_from_args(args):
    root, path, record, context, _ = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, _ = _load_live_workflow(args)
        if _recover_initialization_receipt(args, root, path, record, context):
            return _initialization_result(record, path)
        return _offer_initialization(args, path, record, context,
                                    refresh=getattr(args, "refresh_initialization", False))


def cancel_initialization_from_args(args):
    root, path, record, context, _ = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, _ = _load_live_workflow(args)
        _require_unsubmitted_initialization(record, path)
        permission, _, _ = _validate_initialization_permission(record, context)
        if permission["status"] != "awaiting_approval":
            raise FusionAboWorkflowError("Only an unconsumed initialization proposal can be declined.")
        permission["status"] = "cancelled"
        _persist_live_checkpoint(args, path, record)
        return _initialization_result(record, path)


def _revalidate_adaptive_readiness(args, record, context, properties):
    expected_scope = _adaptive_preparation_scope(record, context)
    if args.process_variable_name and args.process_variable_name != context["validated_process_variable_name"]:
        raise FusionAboWorkflowError("Process differs from the approved workflow.")
    fresh_args = argparse.Namespace(**vars(args))
    default_selected = record["business_plan"].get("process_selection", {}).get("selection_source") == "cpq_default"
    if args.use_default_process and not default_selected:
        raise FusionAboWorkflowError("Default selection differs from the approved workflow.")
    fresh_args.process_variable_name = None if default_selected else context["validated_process_variable_name"]
    fresh_args.use_default_process = default_selected
    fresh, _, _ = _run_preflight_from_args(fresh_args, properties=properties)
    if fresh.get("status") != "already_configured" or fresh.get("target") != record["target"]:
        raise FusionAboWorkflowError("Fresh CPQ and Fusion reads do not confirm readiness for Adaptive Search.")
    from cpq_settings_write_executor import verify_cpq_settings_after_load
    verification = verify_cpq_settings_after_load(plan=record["business_plan"], oauth_properties=properties,
        submission=record["cpq_verification"]["completed_operations"][0], token_cache=args.cpq_token_cache,
        timeout=args.timeout, oauth_options=_cpq_oauth_options_from_args(args))
    verification["target"] = record["target"]
    record["cpq_verification"] = verification
    if _adaptive_preparation_scope(record, context) != expected_scope:
        raise FusionAboWorkflowError("Verified CPQ predecessor changed after the proposal.")
    record["presentation_context"]["feature_states"] = fresh.get("feature_states", {})


def prepare_initialization_load_from_args(args, *, load_runner=None):
    root, path, record, context, _ = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, properties = _load_live_workflow(args)
        if _recover_initialization_receipt(args, root, path, record, context):
            return _initialization_result(record, path)
        _require_unsubmitted_initialization(record, path)
        permission, digest, expires = _validate_initialization_permission(record, context)
        if (getattr(args, "approve_initialization_preparation", False) is not True
                or permission["status"] != "awaiting_approval" or args.initialization_preparation_sha256 != digest):
            raise FusionAboWorkflowError("Separate current Full Publish preparation approval is required.")
        if datetime.now(timezone.utc) > expires:
            permission["status"] = "expired"
            _persist_live_checkpoint(args, path, record)
            raise FusionAboWorkflowError("Initialization proposal expired; request a fresh proposal and approval.")
        module = _initialization_module()
        try:
            _revalidate_adaptive_readiness(args, record, context, properties)
            permission.update({"status": "consumed", "approved_at": _utc_timestamp()})
            _persist_live_checkpoint(args, path, record)
            request = {"schema_version": "1.0", "handover_version": "2.0", "operation": "submit_initial_full_publish",
                "project_id": args.project_id, "target": context["components"]["adaptive_search"]["target"],
                "entities": list(module.INITIALIZATION_ENTITIES), "publish_type": "full",
                "initialization_id": "afi_" + permission["proposal"]["proposal_id"]}
            result = module.prepare_initialization_load(request, record["cpq_verification"], project_root=root,
                properties=Path(args.properties), workflow_record_path=path,
                token_cache=args.fusion_token_cache, load_runner=load_runner)
        except BaseException:
            permission["status"] = "indeterminate" if (_initialization_work(path) / "submission-intent.json").exists() else "preparation_failed"
            _persist_live_checkpoint(args, path, record)
            raise
        if result.get("status") == "validation_required":
            record.update({"state": "initialization_load_validation_required",
                "initialization_prepared_load_ref": _relative_to_repo(Path(result["prepared_load_record"])),
                "initialization_preparation_record_ref": _relative_to_repo(Path(result["preparation_record"]))})
            _persist_live_checkpoint(args, path, record)
            return {**_live_stage_result(record, path, stage="adaptive_initialization", status="validation_required"), **result}
        if result.get("status") == "handoff_required":
            record.update({"state": "initialization_workbook_handoff",
                "initialization_preparation_record_ref": _relative_to_repo(Path(result["preparation_record"]))})
            _persist_live_checkpoint(args, path, record)
            return {**_live_stage_result(record, path, stage="adaptive_initialization", status="handoff_required"),
                "core_data_loader_handoff": result["core_data_loader_handoff"]}
        if result.get("status") == "submitted":
            _recover_initialization_receipt(args, root, path, record, context)
        elif result.get("status") == "not_required":
            permission["status"] = "resolved_externally"
            record.pop("adaptive_initialization_blocker", None)
            record.pop("adaptive_preparation", None)
        else:
            permission["status"] = "indeterminate" if result.get("submission_started") else "preparation_failed"
        _persist_live_checkpoint(args, path, record)
    return preview_adaptive_preparation_from_args(args) if result.get("status") == "not_required" else _initialization_result(record, path)


def check_initialization_from_args(args):
    root, path, record, context, _ = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, _ = _load_live_workflow(args)
        _recover_initialization_receipt(args, root, path, record, context)
        already_verified = record.get("adaptive_initialization", {}).get("status") == "verified"
    if already_verified:
        # A late initialization check must not rewind an active Partial Publish
        # or ESS checkpoint. Completion proof was checked under the lock above.
        return resume_live_workflow_from_args(args)
    return _check_pending_initialization_from_args(args)


def _check_pending_initialization_from_args(args):
    root, path, record, context, _ = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, _ = _load_live_workflow(args)
        _recover_initialization_receipt(args, root, path, record, context)
        if record.get("adaptive_initialization", {}).get("status") == "verified":
            raise FusionAboWorkflowError("Initialization checkpoint advanced; resume the current workflow without rechecking initialization.")
        operation, receipt = _bound_initialization_receipt(root, path, record, context)
        core_result = (_read_json_object(args.core_handoff_result, "Core status result")
                       if getattr(args, "core_handoff_result", None) else None)
        observed = _initialization_module().initialization_status(receipt, project_root=root,
            properties=Path(args.properties), token_cache=args.fusion_token_cache,
            explicit_load_status=operation.get("verified_data_loader") is None,
            data_loader_result=core_result)
        if observed.get("state") == "HANDOFF_REQUIRED":
            return {**_live_stage_result(record, path, stage="adaptive_initialization", status="handoff_required"),
                    "core_data_loader_handoff": observed["core_data_loader_handoff"]}
        markdown = observed.pop("data_loader_markdown", "")
        record["last_initialization_status"] = observed
        if (observed.get("state") == "SUCCEEDED" and observed.get("catalog_ready") is True
                and observed.get("final_entity_readiness") == list(ADAPTIVE_SEARCH_REQUIRED_ENTITIES)
                and observed.get("publish_operation_id") == operation["publish_operation_id"]
                and observed.get("target") == operation["target"] and observed.get("project_id") == record["project_id"]):
            record["adaptive_initialization"]["status"] = "verified"
            _recover_initialization_receipt(args, root, path, record, context)
            record.pop("adaptive_initialization_blocker", None)
            record.pop("adaptive_preparation", None)
            record["state"] = "cpq_completed"
        elif observed.get("terminal") is True:
            record["adaptive_initialization"]["status"] = "indeterminate" if observed.get("state") == "INDETERMINATE" else "failed"
        _persist_live_checkpoint(args, path, record)
    if markdown:
        print(json.dumps({"state": "data_loader_status", "markdown": markdown}), flush=True)
    return preview_adaptive_preparation_from_args(args) if record["adaptive_initialization"]["status"] == "verified" else _initialization_result(record, path)


def preview_adaptive_preparation_from_args(args):
    root, path, record, context, _ = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, _ = _load_live_workflow(args)
        if _recover_initialization_receipt(args, root, path, record, context):
            return _initialization_result(record, path)
        if record.get("adaptive_initialization_blocker"):
            return _offer_initialization(args, path, record, context)
        if _recover_live_adaptive_receipt(args, root, path, record, context):
            return _live_stage_result(record, path, stage="adaptive_data_loader",
                                     next_action="Check the Adaptive Search load status and continue.")
        _require_unsubmitted_adaptive(record, path)
        scope = _adaptive_preparation_scope(record, context)
        permission = record.get("adaptive_preparation")
        if permission:
            permission, _, expires = _validate_adaptive_preparation(record, context)
            if permission["status"] == "awaiting_approval" and datetime.now(timezone.utc) > expires:
                permission["status"] = "expired"
                _persist_live_checkpoint(args, path, record)
            if permission["status"] == "awaiting_approval" or not getattr(args, "refresh_adaptive_preparation", False):
                return _adaptive_preparation_result(record, path)
        issued = datetime.now(timezone.utc).replace(microsecond=0)
        proposal = {"schema_version": "1.0", "purpose": "adaptive_preparation_only", **scope,
                    "proposal_id": uuid.uuid4().hex, "issued_at": _utc_timestamp(issued),
                    "expires_at": _utc_timestamp(issued + timedelta(seconds=CPQ_SETTINGS_APPROVAL_TTL_SECONDS))}
        record["adaptive_preparation"] = {"status": "awaiting_approval", "proposal": proposal,
            "proposal_sha256": hashlib.sha256(_canonical_json(proposal).encode()).hexdigest()}
        _persist_live_checkpoint(args, path, record)
        return _adaptive_preparation_result(record, path)


def cancel_adaptive_preparation_from_args(args):
    root, path, record, context, _ = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, _ = _load_live_workflow(args)
        _require_unsubmitted_adaptive(record, path)
        permission, _, _ = _validate_adaptive_preparation(record, context)
        if permission["status"] != "awaiting_approval":
            raise FusionAboWorkflowError("Only an unconsumed Adaptive Search preparation proposal can be declined.")
        permission["status"] = "cancelled"
        _persist_live_checkpoint(args, path, record)
        return _adaptive_preparation_result(record, path)


def prepare_adaptive_load_from_args(args, *, load_runner=None):
    root, path, record, context, _ = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, properties = _load_live_workflow(args)
        if _recover_initialization_receipt(args, root, path, record, context):
            return _initialization_result(record, path)
        if record.get("adaptive_initialization_blocker"):
            return _offer_initialization(args, path, record, context)
        if _recover_live_adaptive_receipt(args, root, path, record, context):
            return _live_stage_result(record, path, stage="adaptive_data_loader",
                                     next_action="Check the Adaptive Search load status and continue.")
        _require_unsubmitted_adaptive(record, path)
        if getattr(args, "approve_adaptive_preparation", False) is not True:
            raise FusionAboWorkflowError("Approve the current Adaptive Search preparation proposal before preparing its load.")
        permission, digest, expires = _validate_adaptive_preparation(record, context)
        if permission["status"] != "awaiting_approval" or getattr(args, "adaptive_preparation_sha256", None) != digest:
            raise FusionAboWorkflowError("Adaptive Search preparation approval is mismatched, consumed or unavailable.")
        if datetime.now(timezone.utc) > expires:
            permission["status"] = "expired"
            _persist_live_checkpoint(args, path, record)
            raise FusionAboWorkflowError("Adaptive Search preparation expired; obtain a fresh proposal and approval.")
        if args.process_variable_name and args.process_variable_name != context["validated_process_variable_name"]:
            raise FusionAboWorkflowError("Process differs from the approved Adaptive Search preparation.")
        try:
            _revalidate_adaptive_readiness(args, record, context, properties)
        except Exception:
            permission["status"] = "preparation_failed"
            _persist_live_checkpoint(args, path, record)
            raise
        permission.update({"status": "consumed", "approved_at": _utc_timestamp()})
        # Retain cpq_completed: the unchanged companion requires this state.
        # This permission never becomes a Core 'approve' command.
        _persist_live_checkpoint(args, path, record)
        if str(ADAPTIVE_SEARCH_EXECUTOR.parent) not in sys.path:
            sys.path.insert(0, str(ADAPTIVE_SEARCH_EXECUTOR.parent))
        from adaptive_publish_executor import AdaptiveInitializationRequired, prepare_publish_load
        request = {"schema_version": "1.0", "handover_version": "2.0", "operation": "submit_partial_publish",
                   "project_id": args.project_id, **context["components"]["adaptive_search"]}
        try:
            result = prepare_publish_load(request, record["cpq_verification"], project_root=root,
                properties=Path(args.properties), workflow_record_path=path,
                token_cache=args.fusion_token_cache, load_runner=load_runner)
        except AdaptiveInitializationRequired as exc:
            intent = path.parent / path.stem / "adaptive-live" / "submission-intent.json"
            if intent.exists():
                record["state"] = "adaptive_search_indeterminate"
                _persist_live_checkpoint(args, path, record)
                raise
            permission["status"] = "preparation_failed"
            record["adaptive_initialization_blocker"] = {
                "reason": "missing_metamodel" if exc.http_status == 400 else "empty_catalog",
                "http_status": exc.http_status, "message": str(exc), "stage": "adaptive_entity_readback",
                "failure_class": "Fusion API", "observed_at": _utc_timestamp()}
            return _offer_initialization(args, path, record, context)
        except BaseException:
            intent = path.parent / path.stem / "adaptive-live" / "submission-intent.json"
            if intent.exists():
                record["state"] = "adaptive_search_indeterminate"
            else:
                permission["status"] = "preparation_failed"
            _persist_live_checkpoint(args, path, record)
            raise
        if result.get("status") == "validation_required":
            record.update({"state": "adaptive_load_validation_required",
                "adaptive_prepared_load_ref": _relative_to_repo(Path(result["prepared_load_record"])),
                "adaptive_preparation_record_ref": _relative_to_repo(Path(result["preparation_record"]))})
            _persist_live_checkpoint(args, path, record)
            return {**_live_stage_result(record, path, stage="adaptive_data_loader", status="validation_required"), **result}
        if result.get("status") == "handoff_required":
            record.update({"state": "adaptive_workbook_handoff",
                "adaptive_preparation_record_ref": _relative_to_repo(Path(result["preparation_record"]))})
            _persist_live_checkpoint(args, path, record)
            return {**_live_stage_result(record, path, stage="adaptive_data_loader", status="handoff_required"),
                "core_data_loader_handoff": result["core_data_loader_handoff"]}
        if result.get("status") == "submitted":
            record.update({"state": "adaptive_load_submitted", "adaptive_submission": result["submission"],
                           "adaptive_operation_record_ref": _relative_to_repo(Path(result["operation_record"]))})
        elif result.get("submission_started"):
            record["state"] = "adaptive_search_indeterminate"
        else:
            permission["status"] = "preparation_failed"
        _persist_live_checkpoint(args, path, record)
        return _live_stage_result(record, path, stage="adaptive_data_loader",
            status=result["status"], next_action=result["next_action"])


def _bound_live_adaptive_operation(root, path, record, context, *, recovering=False):
    """Validate the fixed child receipt before any external status request."""
    expected_path = path.parent / path.stem / "adaptive-live" / "operation.json"
    try:
        expected_path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise FusionAboWorkflowError("Adaptive Search receipt is outside the project.") from exc
    if not recovering:
        supplied = REPO_ROOT / _project_relative_path(record.get("adaptive_operation_record_ref"),
            project_id=record["project_id"], field_name="Adaptive Search operation")
        if supplied.resolve() != expected_path.resolve():
            raise FusionAboWorkflowError("Adaptive Search receipt is not the exact workflow child.")
    operation = _read_json_mapping(expected_path, "confirmed Adaptive Search receipt")
    adaptive = context["components"]["adaptive_search"]
    if (operation.get("handover_version") != "2.0"
            or operation.get("workflow_approval_fingerprint") != record["workflow_approval_fingerprint"]
            or operation.get("schema_version") != "1.0"
            or operation.get("project_id") != record["project_id"]
            or operation.get("target") != adaptive["target"]
            or operation.get("entities") != adaptive["entities"]
            or operation.get("publish_type") != "selective"
            or operation.get("state") != "SUBMITTED"
            or not re.fullmatch(r"apo_[a-f0-9]{32}", str(operation.get("publish_operation_id", "")))
            or operation.get("status_check_operation") != "get_partial_publish_status"):
        raise FusionAboWorkflowError("Adaptive Search receipt differs from the exact workflow identity.")
    loader = _required_mapping(operation.get("internal_data_loader"), "Adaptive Search load receipt")
    if (not re.fullmatch(r"[1-9][0-9]*", str(loader.get("request_id", "")))
            or not re.fullmatch(r"UCMFA[0-9]+", str(loader.get("content_id", "")))):
        raise FusionAboWorkflowError("Adaptive Search receipt has no safe load correlation.")
    public = {key: operation[key] for key in (
        "schema_version", "publish_operation_id", "state", "project_id", "target",
        "entities", "publish_type", "status_check_operation")}
    if not recovering and record.get("adaptive_submission") != public:
        raise FusionAboWorkflowError("Parent and child Adaptive Search receipts do not match.")
    return expected_path, public


def _recover_live_adaptive_receipt(args, root, path, record, context):
    """Adopt an already saved confirmed receipt; never start or retry a load."""
    if record["state"] not in {"cpq_completed", "adaptive_search_indeterminate"}:
        return False
    receipt = path.parent / path.stem / "adaptive-live" / "operation.json"
    if not receipt.exists():
        return False
    operation, public = _bound_live_adaptive_operation(root, path, record, context, recovering=True)
    record.update({"state": "adaptive_load_submitted", "adaptive_submission": public,
                   "adaptive_operation_record_ref": _relative_to_repo(operation)})
    _persist_live_checkpoint(args, path, record)
    return True


ADAPTIVE_JOB_CHECKPOINT_STATES = frozenset({
    "awaiting_adaptive_monitoring_choice", "adaptive_search_manual",
    "adaptive_search_monitoring", "monitoring_timeout",
})
ADAPTIVE_MONITORING_PROMPT = (
    "Would you like me to keep checking every 15 seconds, "
    "or would you prefer to check the status later?"
)


def _require_verified_adaptive_load(operation_path):
    """Reject stale/foreign loader evidence before any job-only read."""
    operation = _read_json_mapping(operation_path, "Adaptive Search receipt")
    verified = operation.get("verified_data_loader")
    binding = {"request_id": operation["internal_data_loader"]["request_id"],
               "publish_operation_id": operation["publish_operation_id"],
               "project_id": operation["project_id"], "target": operation["target"],
               "status": "SUCCEEDED"}
    if (not isinstance(verified, Mapping)
            or any(verified.get(key) != value for key, value in binding.items())):
        raise FusionAboWorkflowError("Exact verified Data Loader success is required before job monitoring.")


def _adaptive_monitoring_binding(record, *, mode):
    return {"mode": mode, "workflow_id": record["workflow_approval_fingerprint"],
            "project_id": record["project_id"], "target": record["target"],
            "publish_operation_id": record["adaptive_submission"]["publish_operation_id"]}


def _adaptive_monitoring_result(record, path):
    state = record["state"]
    next_action = ("Monitoring this same publish every 15 seconds within the configured time limit."
                   if state == "adaptive_search_monitoring" else
                   "Checkpoint saved; monitoring is stopped. Say: Check the Adaptive Search publish status and continue."
                   if state == "adaptive_search_manual" else ADAPTIVE_MONITORING_PROMPT)
    return {**_live_stage_result(record, path, stage="adaptive_search", status="pending",
                                next_action=next_action),
            "adaptive_search": record.get("last_adaptive_search_status", {}),
            "last_checked_at": record.get("last_adaptive_search_checked_at"),
            "monitoring_choice_required": state == "awaiting_adaptive_monitoring_choice"}


def _check_adaptive_job(args, path, record, context, *, continuous=False, initial_status=None):
    result = _run_automatic_downstream_controller(args, workflow_preview=context,
        approval_record_ref=_relative_to_repo(path), approval_record_fingerprint=args.workflow_id,
        workflow_record_path=path, workflow_record=record, continuous=continuous, initial_status=initial_status)
    return {**_live_stage_result(record, path,
                                stage="ess" if record["state"] == "awaiting_ess_approval" else "adaptive_search"),
            "last_checked_at": record.get("last_adaptive_search_checked_at"), **result}


def choose_adaptive_monitoring_from_args(args):
    root, path, record, context, _ = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, _ = _load_live_workflow(args)
        if record["state"] not in ADAPTIVE_JOB_CHECKPOINT_STATES:
            raise FusionAboWorkflowError("No pending verified-load publish is awaiting a monitoring choice.")
        operation, _ = _bound_live_adaptive_operation(root, path, record, context)
        _require_verified_adaptive_load(operation)
        mode = args.monitoring_mode
        if mode not in {"continuous", "manual"}:
            raise FusionAboWorkflowError("Monitoring mode must be continuous or manual.")
        if mode == "continuous" and args.adaptive_search_poll_interval_seconds != 15:
            raise FusionAboWorkflowError("The approved monitoring choice checks every 15 seconds.")
        record["adaptive_monitoring_choice"] = _adaptive_monitoring_binding(record, mode=mode)
        record["state"] = "adaptive_search_monitoring" if mode == "continuous" else "adaptive_search_manual"
        _persist_live_checkpoint(args, path, record)
        if mode == "manual":
            return _adaptive_monitoring_result(record, path)
        return _check_adaptive_job(args, path, record, context, continuous=True)


def check_adaptive_publish_from_args(args):
    root, path, record, context, _ = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, _ = _load_live_workflow(args)
        if record["state"] not in ADAPTIVE_JOB_CHECKPOINT_STATES:
            raise FusionAboWorkflowError("This workflow is not awaiting a publish status check.")
        # An ordinary status request always checks once, even after prior polling consent.
        return _check_adaptive_job(args, path, record, context)


def check_adaptive_load_from_args(args):
    root, path, record, context, _ = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, _ = _load_live_workflow(args)
        _recover_live_adaptive_receipt(args, root, path, record, context)
        if record["state"] in ADAPTIVE_JOB_CHECKPOINT_STATES:
            return _check_adaptive_job(args, path, record, context)
        if record["state"] != "adaptive_load_submitted":
            raise FusionAboWorkflowError("This workflow is not awaiting an Adaptive Search load status check.")
        operation, _ = _bound_live_adaptive_operation(root, path, record, context)
        if str(ADAPTIVE_SEARCH_EXECUTOR.parent) not in sys.path:
            sys.path.insert(0, str(ADAPTIVE_SEARCH_EXECUTOR.parent))
        from adaptive_publish_executor import status
        core_result = (_read_json_object(args.core_handoff_result, "Core status result")
                       if getattr(args, "core_handoff_result", None) else None)
        observed = status(operation, project_root=root, properties=Path(args.properties),
                          token_cache=args.fusion_token_cache, explicit_load_status=True,
                          data_loader_result=core_result)
        if observed.get("state") == "HANDOFF_REQUIRED":
            return {**_live_stage_result(record, path, stage="adaptive_data_loader", status="handoff_required"),
                    "core_data_loader_handoff": observed["core_data_loader_handoff"]}
        load_markdown = observed.pop("data_loader_markdown", "")
        record["last_adaptive_search_status"] = _safe_public_adaptive_status(observed)
        if observed.get("monitoring", {}).get("stage") == "data_loader":
            _persist_live_checkpoint(args, path, record)
            return {**_live_stage_result(record, path, stage="adaptive_data_loader",
                status="blocked" if observed.get("terminal") else "pending",
                next_action=observed.get("next_action")),
                "data_loader_markdown": load_markdown}
        if load_markdown:
            print(json.dumps({"state": "data_loader_status", "markdown": load_markdown}), flush=True)
        record["state"] = "awaiting_adaptive_monitoring_choice"
        _persist_live_checkpoint(args, path, record)
        # Discovery may have already returned terminal failure/readiness; do not
        # issue another read to turn that terminal evidence into a retry.
        return _check_adaptive_job(args, path, record, context,
                                   initial_status=observed if observed.get("terminal") is True else None)


def submit_live_ess_from_args(args):
    root, path, record, context, _ = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        if record["state"] != "awaiting_ess_approval" or not args.approve_ess:
            raise FusionAboWorkflowError("Separate approval of the current ESS payload is required.")
        adaptive = _required_mapping(record.get("last_adaptive_search_status"), "Adaptive Search readiness")
        _validate_adaptive_status_for_ess(context, record, adaptive)
        ess = _submit_or_monitor_ess(args, workflow_preview=context, workflow_record_path=path,
                                   workflow_record=record, adaptive_status=adaptive)
        record.update({"state": "completed" if ess.get("terminal") and ess.get("success") else "ess_pending_or_failed",
                       "ess_sync": ess})
        _persist_live_checkpoint(args, path, record)
        return {**_live_stage_result(record, path, stage="ess"), "ess_sync": ess}


def resume_live_workflow_from_args(args):
    root, path, record, context, _ = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, _ = _load_live_workflow(args)
        _recover_orphaned_preparation(args, root, path, record, context)
        if record["state"] in {"cpq_workbook_handoff", "cpq_core_handoff"}:
            key = "workbook_handoff" if record["state"] == "cpq_workbook_handoff" else "preflight_handoff"
            handoff = dict(record["cpq_loader"][key])
            handoff["authentication_reference"] = {"properties": str(args.properties),
                **({"token_cache": args.fusion_token_cache} if args.fusion_token_cache else {})}
            return {**_live_stage_result(record, path, stage="cpq_data_loader", status="handoff_required"),
                    "core_data_loader_handoff": handoff}
        if record["state"] in {"adaptive_workbook_handoff", "initialization_workbook_handoff",
                               "adaptive_core_handoff", "initialization_core_handoff"}:
            stage = "initialization" if record["state"].startswith("initialization") else "adaptive"
            preparation_path = REPO_ROOT / record[stage + "_preparation_record_ref"]
            preparation = _read_json_object(str(preparation_path), "Adaptive Search preparation")
            if record["state"].endswith("_core_handoff"):
                handoff = dict(preparation["preflight_handoff"])
                handoff["authentication_reference"] = {"properties": str(args.properties),
                    **({"token_cache": args.fusion_token_cache} if args.fusion_token_cache else {})}
            else:
                handoff = {"handoff_version": "26.10.1", "handoff_id": preparation["handoff_id"],
                           "kind": "generate_populated_workbook", "business_object": "publish",
                           "values_json_path": preparation["values_json_path"],
                           "output_directory": str(preparation_path.parent),
                           "authentication_reference": {"properties": str(args.properties),
                               **({"token_cache": args.fusion_token_cache} if args.fusion_token_cache else {})}}
            return {**_live_stage_result(record, path, stage="adaptive_data_loader", status="handoff_required"),
                    "core_data_loader_handoff": handoff}
        if record["state"].endswith(("_load_validation_required", "_load_approval_required")):
            stage = record["state"].split("_load_", 1)[0]
            _, saved_load, _ = _persisted_load_binding(record, root, stage)
            if (record["state"] == stage + "_load_validation_required"
                    and saved_load["state"] == "awaiting_approval"):
                # Core saved the preview before the parent checkpoint advanced.
                record["state"] = stage + "_load_approval_required"
                _persist_live_checkpoint(args, path, record)
            return persisted_load_stage_result(record, path, root)
        if record["state"] == "cpq_possibly_submitted" and record.get("cpq_prepared_load_ref"):
            from cpq_settings_write_executor import load_persisted_load
            load = load_persisted_load(REPO_ROOT / record["cpq_prepared_load_ref"], project_root=root,
                workflow_id=args.workflow_id, target=record["target"])
            if load["state"] == "submitted":
                record.update({"state": "cpq_submitted", "cpq_submission": {
                    "id": load["scope"]["operation_id"], "status": "submitted", **load["submission"],
                    "target": record["target"], "submitted_at": _utc_timestamp()}})
                _persist_live_checkpoint(args, path, record)
        if record["state"] in {"adaptive_possibly_submitted", "initialization_possibly_submitted"}:
            if str(ADAPTIVE_SEARCH_EXECUTOR.parent) not in sys.path:
                sys.path.insert(0, str(ADAPTIVE_SEARCH_EXECUTOR.parent))
            from adaptive_publish_executor import recover_prepared_publish
            stage = "initialization" if record["state"].startswith("initialization") else "adaptive"
            recover_prepared_publish(REPO_ROOT / record[stage + "_preparation_record_ref"], project_root=root,
                                     workflow_id=args.workflow_id)
        if _recover_initialization_receipt(args, root, path, record, context):
            return _initialization_result(record, path)
        if record.get("adaptive_initialization_blocker"):
            return _offer_initialization(args, path, record, context)
        _recover_live_adaptive_receipt(args, root, path, record, context)
        if record["state"] == "preparing_cpq":
            # The lock proves the foreground stage is gone. No approval intent
            # was persisted, so this dead preparation cannot have submitted.
            record["state"] = "cancelled"
            _persist_live_checkpoint(args, path, record)
        if record["state"] == "awaiting_cpq_preparation_approval":
            proposal = _required_mapping(record.get("cpq_preparation_proposal"), "CPQ preparation proposal")
            if datetime.now(timezone.utc) > _parse_rfc3339_timestamp(proposal["expires_at"], "preparation expires_at"):
                record["state"] = "expired"
                _persist_live_checkpoint(args, path, record)
    if record["state"] in {"cpq_submitted", "cpq_verification_failed"}:
        return _live_stage_result(record, path, stage="cpq_data_loader",
                                 next_action="Check the CPQ load status and continue.")
    if record["state"] == "awaiting_cpq_preparation_approval":
        return _cpq_preparation_result(record, path)
    if record["state"] in {"expired", "cancelled", "preparation_failed"} and record.get("cpq_preparation_proposal"):
        return _live_stage_result(record, path, stage="cpq_preparation",
            next_action="No submission is confirmed. Create and approve a fresh preparation proposal; never reuse a lost Core preview.")
    if record["state"] == "adaptive_load_submitted":
        return _live_stage_result(record, path, stage="adaptive_data_loader",
                                 next_action="Check the Adaptive Search load status and continue.")
    if record["state"] == "cpq_completed":
        return preview_adaptive_preparation_from_args(args)
    if record["state"] in ADAPTIVE_JOB_CHECKPOINT_STATES:
        with _workflow_lock(root, args.workflow_id):
            root, path, record, context, _ = _load_live_workflow(args)
            if record["state"] not in ADAPTIVE_JOB_CHECKPOINT_STATES:
                raise FusionAboWorkflowError("The workflow checkpoint advanced; resume its current stage.")
            operation, _ = _bound_live_adaptive_operation(root, path, record, context)
            _require_verified_adaptive_load(operation)
            # A saved choice does not authorize restarting a foreground polling loop.
            if record["state"] != "adaptive_search_manual":
                record["state"] = "awaiting_adaptive_monitoring_choice"
                _persist_live_checkpoint(args, path, record)
            return _adaptive_monitoring_result(record, path)
    if record["state"] == "ess_pending_or_failed":
        with _workflow_lock(root, args.workflow_id):
            adaptive = record["last_adaptive_search_status"]
            _validate_adaptive_status_for_ess(context, record, adaptive)
            ess = _submit_or_monitor_ess(args, workflow_preview=context, workflow_record_path=path,
                                        workflow_record=record, adaptive_status=adaptive)
            record.update({"state": "completed" if ess.get("terminal") and ess.get("success") else "ess_pending_or_failed",
                           "ess_sync": ess})
            _persist_live_checkpoint(args, path, record)
            return {**_live_stage_result(record, path, stage="ess"), "ess_sync": ess}
    if record["state"] == "awaiting_ess_approval":
        _, payload = _ess_payload(context, adaptive_status=record["last_adaptive_search_status"])
        return {**_live_stage_result(record, path, stage="ess", status="approval_required"),
                "approval_required": {"stage": "ess", "target": record["target"],
                                     "payload": payload, "payload_sha256": record["ess_preview_payload_sha256"]}}
    if record["state"] == "completed":
        return _completed_workflow_result(record, workflow_record_path=path)
    return _live_stage_result(record, path, stage="recovery",
                             next_action="The pending prepared load is unavailable or submission is uncertain; never replay an approval.")



def _recover_orphaned_preparation(args, root, path, record, context):
    """Adopt only an exact prepared load saved before its parent checkpoint."""
    from cpq_settings_write_executor import load_persisted_load
    if (record["state"] in {"preparing_cpq", "preparation_failed"}
            and record.get("cpq_preparation_approval_consumed")
            and not record.get("cpq_prepared_load_ref")):
        base = (root / "artifacts/pillars/cx/configure-price-quote/quoting/enable-fusion-asset-based-ordering"
                / "current/cpq-settings-data-loader")
        candidates = []
        for candidate in base.glob("sample-*/*/prepared-load.json"):
            try:
                saved = json.loads(candidate.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(saved, Mapping) and saved.get("workflow_id") == args.workflow_id:
                candidates.append(candidate)
        if len(candidates) > 1:
            raise FusionAboWorkflowError("More than one CPQ preparation matches this workflow; reconcile before continuing.")
        if not candidates:
            return False
        load = load_persisted_load(candidates[0], project_root=root,
            workflow_id=args.workflow_id, target=record["target"])
        from cpq_settings_write_executor import _data_loader_mutations, _data_loader_subject
        mutations = _data_loader_mutations(record["business_plan"])
        if (len(mutations) != 1 or load["scope"] !=
                _data_loader_subject(mutations[0]["id"], mutations[0]["settings"])):
            raise FusionAboWorkflowError("Saved CPQ preparation differs from the approved business plan.")
        stage = "cpq"
        record["cpq_prepared_load_ref"] = _relative_to_repo(candidates[0])
    elif (record["state"] == "cpq_completed" and not record.get("adaptive_initialization_blocker")
          and record.get("adaptive_preparation", {}).get("status") in {"consumed", "preparation_failed"}
          and not record.get("adaptive_prepared_load_ref")):
        stage = "adaptive"
    elif (record.get("adaptive_initialization_blocker")
          and record.get("adaptive_initialization", {}).get("status") in {"consumed", "preparation_failed"}
          and not record.get("initialization_prepared_load_ref")):
        stage = "initialization"
    else:
        return False
    if stage != "cpq":
        work = path.parent / path.stem / ("adaptive-live" if stage == "adaptive" else "adaptive-initialization")
        preparation_path = work / "companion-preparation.json"
        if not preparation_path.exists():
            return False
        if str(ADAPTIVE_SEARCH_EXECUTOR.parent) not in sys.path:
            sys.path.insert(0, str(ADAPTIVE_SEARCH_EXECUTOR.parent))
        from adaptive_publish_executor import _prepared_publish_binding
        preparation, load_path, load = _prepared_publish_binding(preparation_path, root, args.workflow_id)
        if bool(preparation["initialization"]) != (stage == "initialization"):
            raise FusionAboWorkflowError("Saved companion preparation has the wrong stage.")
        record[stage + "_prepared_load_ref"] = _relative_to_repo(load_path)
        record[stage + "_preparation_record_ref"] = _relative_to_repo(preparation_path)
    if load["state"] not in {"awaiting_task_rules", "awaiting_approval"}:
        raise FusionAboWorkflowError("Saved preparation may have submitted; reconcile its receipt before continuing.")
    record["state"] = stage + ("_load_validation_required" if load["state"] == "awaiting_task_rules"
                             else "_load_approval_required")
    _persist_live_checkpoint(args, path, record)
    return True


def _persisted_load_binding(record, root, stage):
    if stage not in {"cpq", "adaptive", "initialization"}:
        raise FusionAboWorkflowError("Select the exact pending load stage.")
    reference = record.get(stage + "_prepared_load_ref")
    if not isinstance(reference, str):
        raise FusionAboWorkflowError("This stage has no prepared load.")
    target = record["target"] if stage == "cpq" else record["workflow_context"]["components"]["adaptive_search"]["target"]
    from cpq_settings_write_executor import load_persisted_load
    path = REPO_ROOT / reference
    load = load_persisted_load(path, project_root=root,
        workflow_id=record["workflow_approval_fingerprint"], target=target)
    return path, load, target


def accept_adaptive_workbook_from_args(args):
    root, path, record, _, _ = _load_live_workflow(args)
    result = _read_json_object(args.core_handoff_result, "Core workbook result")
    with _workflow_lock(root, args.workflow_id):
        root, path, record, _, _ = _load_live_workflow(args)
        stage = args.load_stage
        if stage not in {"adaptive", "initialization"} or record["state"] != stage + "_workbook_handoff":
            raise FusionAboWorkflowError("This workflow is not awaiting that Adaptive Search workbook.")
        preparation_path = REPO_ROOT / _project_relative_path(
            record[stage + "_preparation_record_ref"], project_id=record["project_id"],
            field_name="Adaptive Search preparation")
        accepted = _initialization_module().accept_publish_workbook_result(
            preparation_path, result, project_root=root, properties=Path(args.properties),
            token_cache=args.fusion_token_cache)
        record["state"] = stage + "_core_handoff"
        _persist_live_checkpoint(args, path, record)
        from abo_presentation import render_workbook_access
        return {**_live_stage_result(record, path, stage="adaptive_data_loader", status="handoff_required"),
            "workbook_access": render_workbook_access(Path(accepted["workbook_path"]), project_root=root),
            "core_data_loader_handoff": accepted["core_data_loader_handoff"]}


def persisted_load_stage_result(record, path, root):
    stage = record["state"].split("_load_", 1)[0]
    load_path, load, target = _persisted_load_binding(record, root, stage)
    result = _live_stage_result(record, path, stage="cpq_data_loader" if stage == "cpq" else "adaptive_data_loader")
    if load["state"] == "awaiting_task_rules":
        return {**result, "status": "validation_required", "task_validation": load["task_validation"],
                "validated_scope": load["scope"], "prepared_source_ref": _relative_to_repo(Path(load["source_path"])),
                "execution_guide": "core/data-loader/references/task-rule-registry-execution.md",
                "next_action": "Evaluate every ordered Core task rule against the prepared source and current-stage evidence, then build the load preview."}
    if load["state"] == "awaiting_approval":
        from abo_presentation import render_workbook_access
        try:
            workbook_access = render_workbook_access(Path(load["source_path"]), project_root=root)
        except (ValueError, OSError, RuntimeError):
            workbook_access = "The generated workbook link is unavailable. The validated load is unchanged.\n"
        return {**result, "status": "approval_required", "load_preview_sha256": load["preview_sha256"],
                "data_loader_markdown": load["core_approval_markdown"],
                "workbook_access": workbook_access,
                "next_action": "Obtain approval for this exact Core preview before submit-data-load."}
    raise FusionAboWorkflowError("The saved load is submitted or uncertain; reconcile without repeating preparation.")


def build_persisted_preview_from_args(args):
    """Accept the 26.10 Core preflight and Task Hook preview for one stage."""
    root, path, record, _, _ = _load_live_workflow(args)
    core_result = _read_json_object(args.core_handoff_result, "Core preflight result")
    with _workflow_lock(root, args.workflow_id):
        root, path, record, _, _ = _load_live_workflow(args)
        stage = args.load_stage
        if record["state"] != stage + "_core_handoff":
            raise FusionAboWorkflowError("Only the current Core handoff can complete load validation.")
        if stage == "cpq":
            from cpq_settings_write_executor import prepare_persisted_load
            load = _required_mapping(record.get("cpq_loader"), "CPQ Core handoff")
            result = prepare_persisted_load(core_result, handoff=load["preflight_handoff"],
                workbook_source=Path(load["source_path"]), workbook_project_root=root,
                target=record["target"], scope=load["approved_subject"], workflow_id=args.workflow_id)
        elif stage in {"adaptive", "initialization"}:
            preparation_path = REPO_ROOT / _project_relative_path(
                record[stage + "_preparation_record_ref"], project_id=record["project_id"],
                field_name="Adaptive Search preparation")
            result = _initialization_module().accept_publish_core_preflight(
                preparation_path, core_result, project_root=root)
        else:
            raise FusionAboWorkflowError("Select the current load stage.")
        record[stage + "_prepared_load_ref"] = _relative_to_repo(Path(result["prepared_load_record"]))
        record["state"] = stage + "_load_approval_required"
        _persist_live_checkpoint(args, path, record)
        return {**_live_stage_result(record, path, stage="cpq_data_loader" if stage == "cpq" else "adaptive_data_loader",
                                    status="approval_required"),
                **result, "load_preview_sha256": result["preview_sha256"],
                "next_action": "Obtain approval of Core's exact load preview, then submit-data-load."}


def submit_persisted_load_from_args(args):
    if getattr(args, "approve_load", False) is not True:
        raise FusionAboWorkflowError("Separate explicit approval of this Core load preview is required.")
    root, path, record, context, properties = _load_live_workflow(args)
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, properties = _load_live_workflow(args)
        stage = args.load_stage
        if record["state"] != stage + "_load_approval_required":
            raise FusionAboWorkflowError("This load is not awaiting approval; never repeat a submitted load.")
        load_path, load, target = _persisted_load_binding(record, root, stage)
        if stage == "cpq":
            fresh_args = argparse.Namespace(**vars(args))
            selection = record["business_plan"].get("process_selection", {})
            default_selected = selection.get("selection_source") == "cpq_default"
            fresh_args.process_variable_name = None if default_selected else context["validated_process_variable_name"]
            fresh_args.use_default_process = default_selected
            _, plan, semantic, _ = _prepare_cpq_settings_write(fresh_args)
            proposal = record["cpq_preparation_proposal"]
            if _cpq_preparation_scope(args, plan, semantic) != {key: proposal[key] for key in
                    ("project_id", "target", "business_plan", "preflight_fingerprint")}:
                raise FusionAboWorkflowError("CPQ readiness or scope changed; obtain fresh preparation and load approval.")
            from cpq_settings_write_executor import _data_loader_mutations, _data_loader_subject
            mutations = _data_loader_mutations(plan)
            if len(mutations) != 1 or load["scope"] != _data_loader_subject(mutations[0]["id"], mutations[0]["settings"]):
                raise FusionAboWorkflowError("The prepared CPQ load differs from the fixed approved business plan.")
        else:
            _revalidate_adaptive_readiness(args, record, context, properties)
        def reserve():
            record["state"] = stage + "_possibly_submitted"
            _persist_live_checkpoint(args, path, record)
        try:
            if stage == "cpq":
                from cpq_settings_write_executor import submit_persisted_load
                result = submit_persisted_load(load_path, project_root=root, workflow_id=args.workflow_id,
                    target=target, explicit_approval=True, preview_sha256=args.load_preview_sha256,
                    before_submit=reserve, properties=Path(args.properties), token_cache=args.fusion_token_cache)
            else:
                result = _initialization_module().submit_prepared_publish(REPO_ROOT / record[stage + "_preparation_record_ref"],
                    project_root=root, workflow_id=args.workflow_id, properties=Path(args.properties),
                    explicit_approval=True, preview_sha256=args.load_preview_sha256,
                    before_submit=reserve, token_cache=args.fusion_token_cache)
        except BaseException:
            # The exclusive Core intent can survive failure before the parent checkpoint.
            from cpq_settings_write_executor import _data_loader_read_json
            persisted = _data_loader_read_json(load_path, "prepared load")
            if persisted.get("state") in {"possibly_submitted", "submitted"}:
                record["state"] = stage + "_possibly_submitted"
                _persist_live_checkpoint(args, path, record)
            raise
        _persist_live_checkpoint(args, path, record)
        return {**_live_stage_result(record, path, stage="cpq_data_loader" if stage == "cpq" else "adaptive_data_loader",
                                    status="handoff_required"),
                "core_data_loader_handoff": result["core_data_loader_handoff"]}


def complete_persisted_load_from_args(args):
    root, path, record, context, _ = _load_live_workflow(args)
    core_result = _read_json_object(args.core_handoff_result, "Core submission result")
    with _workflow_lock(root, args.workflow_id):
        root, path, record, context, _ = _load_live_workflow(args)
        stage = args.load_stage
        if record["state"] != stage + "_possibly_submitted":
            raise FusionAboWorkflowError("This workflow has no reserved Core submission for that stage.")
        load_path, load, target = _persisted_load_binding(record, root, stage)
        if stage == "cpq":
            from cpq_settings_write_executor import complete_persisted_load
            result = complete_persisted_load(load_path, core_result, project_root=root,
                workflow_id=args.workflow_id, target=target)
            record.update({"state": "cpq_submitted", "cpq_submission": {
                "id": load["scope"]["operation_id"], "status": "submitted",
                "content_id": result["content_id"], "request_id": result["request_id"],
                "target": target, "submitted_at": _utc_timestamp()}})
        else:
            result = _initialization_module().complete_prepared_publish(REPO_ROOT / record[stage + "_preparation_record_ref"],
                core_result, project_root=root, workflow_id=args.workflow_id)
            if stage == "initialization":
                _recover_initialization_receipt(args, root, path, record, context)
            else:
                record.update({"state": "adaptive_load_submitted", "adaptive_submission": result["submission"],
                    "adaptive_operation_record_ref": _relative_to_repo(Path(result["operation_record"]))})
        _persist_live_checkpoint(args, path, record)
        prompt = {"cpq": "Check the CPQ load status and continue.",
                  "adaptive": "Check the Adaptive Search load status and continue.",
                  "initialization": "Full Publish can take 10 minutes or longer. Please wait about 8–10 minutes, then request the initialization status."}[stage]
        return {**_live_stage_result(record, path, stage="cpq_data_loader" if stage == "cpq" else "adaptive_data_loader",
                                    status="submitted", next_action=prompt),
                "data_loader_markdown": result["markdown"]}

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Coordinate governed Enable Fusion Asset-Based Ordering preflight, one approved "
            "Fusion prerequisite update, one approved fixed CPQ Settings sequence, separate "
            "Configure Adaptive Search routing, and Unified Asset Read Model Sync only after the "
            "Adaptive Search skill returns successful final evidence."
        )
    )
    commands = parser.add_subparsers(dest="command", required=True)

    for name in ("preview-cpq-preparation", "cancel-cpq-preparation", "prepare-cpq-load",
                 "accept-cpq-workbook", "accept-adaptive-workbook", "complete-data-load",
                 "preview-adaptive-preparation",
                 "cancel-adaptive-preparation", "prepare-adaptive-load", "check-cpq-load-status",
                 "check-adaptive-load-status", "check-adaptive-publish-status", "choose-adaptive-monitoring",
                 "preview-adaptive-initialization", "cancel-adaptive-initialization",
                 "prepare-adaptive-initialization", "check-adaptive-initialization-status",
                 "build-load-preview", "submit-data-load", "submit-live-ess-sync", "resume-live-workflow"):
        stage = commands.add_parser(name, help="V2 persisted Core load workflow; status commands require an explicit user request.")
        _add_runtime_arguments(stage)
        _add_automatic_controller_arguments(stage)
        stage.add_argument("--project-id", required=True)
        if name != "preview-cpq-preparation":
            stage.add_argument("--workflow-id", required=True)
        if name == "prepare-cpq-load":
            stage.add_argument("--approve-cpq-preparation", action="store_true")
            stage.add_argument("--cpq-preparation-sha256", required=True)
        if name == "preview-adaptive-preparation":
            stage.add_argument("--refresh-adaptive-preparation", action="store_true",
                               help="Create a fresh proposal only after a stopped unsubmitted preparation; never restart a running/submitted load.")
        if name == "prepare-adaptive-load":
            stage.add_argument("--approve-adaptive-preparation", action="store_true")
            stage.add_argument("--adaptive-preparation-sha256", required=True)
        if name == "preview-adaptive-initialization":
            stage.add_argument("--refresh-initialization", action="store_true")
        if name == "prepare-adaptive-initialization":
            stage.add_argument("--approve-initialization-preparation", action="store_true")
            stage.add_argument("--initialization-preparation-sha256", required=True)
        if name == "submit-live-ess-sync":
            stage.add_argument("--approve-ess", action="store_true")
            stage.add_argument("--ess-approval-sha256", required=True)
        if name in {"build-load-preview", "submit-data-load", "complete-data-load", "accept-adaptive-workbook"}:
            stage.add_argument("--load-stage", choices=("cpq", "adaptive", "initialization"), required=True)
        if name == "build-load-preview":
            stage.add_argument("--core-handoff-result", required=True,
                               help="Bound 26.10 Core preflight and Task Hook result JSON.")
        if name in {"accept-cpq-workbook", "accept-adaptive-workbook", "complete-data-load",
                    "check-cpq-load-status", "check-adaptive-load-status", "check-adaptive-initialization-status"}:
            stage.add_argument("--core-handoff-result",
                               required=name in {"accept-cpq-workbook", "accept-adaptive-workbook", "complete-data-load"},
                               help="Structured result of the current core.data-loader handoff.")
        if name == "submit-data-load":
            stage.add_argument("--approve-load", action="store_true")
            stage.add_argument("--load-preview-sha256", required=True)
        if name == "choose-adaptive-monitoring":
            stage.add_argument("--monitoring-mode", choices=("continuous", "manual"), required=True,
                               help="Explicit current user choice: keep checking every 15 seconds, or check later.")

    presentation = commands.add_parser(
        "render-presentation",
        help="Render a structured ABO result using the fixed user-facing Markdown template.",
    )
    presentation.add_argument("input", help="Path to a structured ABO result JSON file.")
    presentation.add_argument("--output", help="Optional Markdown output path.")

    preflight = commands.add_parser("preflight", help="Run CPQ and exact two-feature read-only checks.")
    _add_runtime_arguments(preflight)
    preflight.add_argument("--output", help="Optional path for the sanitized preflight JSON.")

    preview = commands.add_parser(
        "preview-prerequisite-update",
        help="Create the exact approval preview for one currently false Fusion prerequisite.",
    )
    preview.add_argument("--preflight-result", required=True)
    preview.add_argument("--feature-code", required=True)
    preview.add_argument("--feature-choice", required=True)
    preview.add_argument("--output", help="Optional path for the sanitized approval preview JSON.")

    execute = commands.add_parser(
        "execute-approved-prerequisite-update",
        help="Run one approved shared Fusion opt-in update, then reread all required prerequisites and CPQ state.",
    )
    _add_runtime_arguments(execute)
    execute.add_argument("--feature-code", required=True)
    execute.add_argument("--feature-choice", required=True)
    execute.add_argument("--approval-fingerprint", required=True)
    execute.add_argument("--project-id", required=True)
    execute.add_argument("--approve-prerequisite-update", action="store_true")
    execute.add_argument("--output", help="Optional path for the sanitized result JSON.")

    cpq_preview = commands.add_parser(
        "preview-cpq-settings-write",
        help=(
            "Rerun fresh preflight and persist the exact CPQ Data Loader approval preview."
        ),
    )
    _add_runtime_arguments(cpq_preview)
    cpq_preview.add_argument(
        "--project-id",
        required=True,
        help="Existing initialized project workspace used for sanitized preview and token-use records.",
    )
    cpq_preview.add_argument("--output", help="Optional path for the sanitized approval preview JSON.")

    cpq_execute = commands.add_parser(
        "execute-approved-cpq-settings-write",
        help=(
            "Execute the explicitly approved CPQ import once and pause before Adaptive Search."
        ),
    )
    _add_runtime_arguments(cpq_execute)
    _add_automatic_controller_arguments(cpq_execute)
    cpq_execute.add_argument(
        "--project-id",
        required=True,
        help="Existing initialized project workspace used for required durable audit records.",
    )
    cpq_execute.add_argument(
        "--approval-fingerprint",
        required=True,
        help="Exact CPQ-stage fingerprint from the current preview-cpq-settings-write output.",
    )
    cpq_execute.add_argument(
        "--approval-issued-at",
        required=True,
        help="Exact issued_at timestamp from the current CPQ preview output.",
    )
    cpq_execute.add_argument(
        "--approve-cpq-settings-write",
        action="store_true",
        help=(
            "Confirm explicit approval for this exact CPQ Data Loader import."
        ),
    )
    cpq_execute.add_argument("--output", help="Optional path for the sanitized terminal result JSON.")

    cpq_reconcile = commands.add_parser(
        "reconcile-cpq-settings-write",
        help=(
            "Promote a prior indeterminate CPQ write only from Run Book Data Load Status "
            "and fresh CPQ readback evidence."
        ),
    )
    cpq_reconcile.add_argument("--project-id", required=True)
    cpq_reconcile.add_argument("--approval-fingerprint", required=True)
    cpq_reconcile.add_argument("--approval-issued-at", required=True)
    cpq_reconcile.add_argument("--preflight-result", required=True)
    cpq_reconcile.add_argument("--data-set-name", required=True)
    cpq_reconcile.add_argument("--data-load-status", required=True)
    cpq_reconcile.add_argument("--loaded", type=int, required=True)
    cpq_reconcile.add_argument("--errors", type=int, required=True)
    cpq_reconcile.add_argument("--skipped", type=int, required=True)
    cpq_reconcile.add_argument("--output", help="Optional path for the sanitized reconciliation result JSON.")

    for command_name, description in (
        ("preview-adaptive-search-publish", "Build the separate Adaptive Search Task Hook approval preview after CPQ verification."),
        ("execute-approved-adaptive-search-publish", "Submit the separately approved partial publish once and monitor it."),
        ("submit-approved-ess-sync", "Submit Unified Asset Read Model Sync after its separate exact-payload approval."),
    ):
        stage = commands.add_parser(command_name, help=description)
        _add_runtime_arguments(stage)
        _add_automatic_controller_arguments(stage)
        stage.add_argument("--project-id", required=True)
        stage.add_argument(
            "--approval-fingerprint",
            required=command_name != "execute-approved-adaptive-search-publish",
            help="CPQ plan fingerprint used to locate the persisted workflow.",
        )
        stage.add_argument(
            "--approval-issued-at",
            required=command_name != "execute-approved-adaptive-search-publish",
        )
        stage.add_argument("--output", help="Optional path for the sanitized stage result JSON.")
        if command_name == "execute-approved-adaptive-search-publish":
            stage.add_argument("--approve-adaptive-search", action="store_true")
            stage.add_argument("--adaptive-preview-sha256")
            stage.add_argument(
                "--adaptive-approval-preview",
                help="Project-local Adaptive Search approval preview JSON used to resolve the bound parent workflow.",
            )
        if command_name == "submit-approved-ess-sync":
            stage.add_argument("--approve-ess", action="store_true")
            stage.add_argument("--ess-approval-sha256", required=True)

    resume = commands.add_parser(
        "resume-approved-fusion-abo-workflow",
        help="Resume only the exact persisted Adaptive Search/ESS status path; it never repeats CPQ, Data Loader, or Adaptive Search submission.",
    )
    _add_runtime_arguments(resume)
    _add_automatic_controller_arguments(resume)
    resume.add_argument("--project-id", required=True)
    resume.add_argument("--approval-fingerprint", required=True)
    resume.add_argument("--approval-issued-at", required=True)
    resume.add_argument("--output", help="Optional path for the sanitized resumed workflow result JSON.")

    adaptive_status = commands.add_parser(
        "evaluate-adaptive-search-status",
        help="Validate an opaque Configure Adaptive Search status result and, only on final success, create the fixed ESS submission request.",
    )
    adaptive_status.add_argument("--workflow-preview", required=True)
    adaptive_status.add_argument("--adaptive-search-status-result", required=True)
    adaptive_status.add_argument("--output", help="Optional path for the sanitized result JSON.")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    live_commands = {"build-load-preview": build_persisted_preview_from_args,
                     "submit-data-load": submit_persisted_load_from_args,
                     "complete-data-load": complete_persisted_load_from_args,
                     "accept-cpq-workbook": accept_cpq_workbook_from_args,
                     "accept-adaptive-workbook": accept_adaptive_workbook_from_args,
                     "preview-cpq-preparation": preview_cpq_preparation_from_args,
                     "cancel-cpq-preparation": cancel_cpq_preparation_from_args,
                     "prepare-cpq-load": prepare_cpq_load_from_args,
                     "preview-adaptive-preparation": preview_adaptive_preparation_from_args,
                     "cancel-adaptive-preparation": cancel_adaptive_preparation_from_args,
                     "prepare-adaptive-load": prepare_adaptive_load_from_args,
                     "preview-adaptive-initialization": preview_initialization_from_args,
                     "cancel-adaptive-initialization": cancel_initialization_from_args,
                     "prepare-adaptive-initialization": prepare_initialization_load_from_args,
                     "check-adaptive-initialization-status": check_initialization_from_args,
                     "check-cpq-load-status": check_cpq_load_from_args,
                     "check-adaptive-load-status": check_adaptive_load_from_args,
                     "check-adaptive-publish-status": check_adaptive_publish_from_args,
                     "choose-adaptive-monitoring": choose_adaptive_monitoring_from_args,
                     "submit-live-ess-sync": submit_live_ess_from_args,
                     "resume-live-workflow": resume_live_workflow_from_args}
    if args.command in live_commands:
        result = live_commands[args.command](args)
        print(json.dumps(_with_customer_presentation(result), ensure_ascii=False), flush=True)
        return 0
    if args.command in {"preview-cpq-settings-write", "execute-approved-cpq-settings-write",
                        "reconcile-cpq-settings-write", "preview-adaptive-search-publish",
                        "execute-approved-adaptive-search-publish"}:
        raise FusionAboWorkflowError("Saved Data Loader approval routes are retired; use the v2 persisted Core load workflow.")
    if args.command == "render-presentation":
        from abo_presentation import render_abo_presentation

        payload = _read_json_object(args.input, "ABO presentation input")
        rendered = render_abo_presentation(payload)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    if args.command == "preflight":
        result, _, _ = _run_preflight_from_args(args)
        _write_json(args.output, _with_customer_presentation(result))
        return 0
    if args.command == "preview-prerequisite-update":
        result = build_prerequisite_update_preview(
            _read_json_object(args.preflight_result, "preflight result"),
            feature_code=args.feature_code,
            feature_choice=args.feature_choice,
        )
        _write_json(args.output, _with_customer_presentation(result))
        return 0
    if args.command == "execute-approved-prerequisite-update":
        result = execute_approved_prerequisite_update(args)
        _write_json(args.output, _with_customer_presentation(result))
        return 0
    if args.command == "preview-cpq-settings-write":
        result = preview_cpq_settings_write(args)
        _write_json(args.output, _with_customer_presentation(result))
        return 0
    if args.command == "execute-approved-cpq-settings-write":
        result = execute_approved_cpq_settings_write_from_args(args)
        _write_json(args.output, _with_customer_presentation(result))
        return 0
    if args.command == "reconcile-cpq-settings-write":
        result = reconcile_cpq_settings_write_from_args(args)
        _write_json(args.output, _with_customer_presentation(result))
        return 0
    if args.command == "preview-adaptive-search-publish":
        result = preview_adaptive_search_from_args(args)
        _write_json(args.output, _with_customer_presentation(result))
        return 0
    if args.command == "execute-approved-adaptive-search-publish":
        result = execute_approved_adaptive_search_from_args(args)
        _write_json(args.output, _with_customer_presentation(result))
        return 0
    if args.command == "submit-approved-ess-sync":
        result = submit_approved_ess_from_args(args)
        _write_json(args.output, _with_customer_presentation(result))
        return 0
    if args.command == "resume-approved-fusion-abo-workflow":
        result = resume_approved_fusion_abo_workflow_from_args(args)
        _write_json(args.output, _with_customer_presentation(result))
        return 0
    if args.command == "evaluate-adaptive-search-status":
        result = evaluate_adaptive_search_status_from_args(args)
        _write_json(args.output, _with_customer_presentation(result))
        return 0
    raise AssertionError(f"Unhandled command: {args.command}")


def _safe_cli_failure_result(error: BaseException) -> dict[str, Any]:
    """Render an expected workflow failure without ever echoing raw exception text.

    The task may be invoked directly from a terminal as well as through an AI
    assistant.  This final boundary mirrors the durable-artifact boundary: a
    stage message is always safe, while an Oracle business detail is included
    only if an owned adapter supplied it through an allowlisted field.
    """

    if isinstance(error, FeatureStatesError):
        base_message = "Fusion prerequisite state could not be read safely."
    elif isinstance(error, (CpqSettingsError, CpqClientError)):
        base_message = "CPQ state could not be read safely."
    elif isinstance(error, (CpqSettingsWritePlanError, CpqSettingsWriteExecutorError)):
        base_message = "CPQ Settings write preparation could not continue safely."
    else:
        base_message = "The Fusion ABO workflow could not continue safely."

    message, provider_error = _with_safe_provider_detail(base_message, error)
    result: dict[str, Any] = {
        "status": "failed",
        "task_code": TASK_CODE,
        "message": message,
    }
    if provider_error:
        result["provider_error"] = provider_error
    return result


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        failure = _safe_cli_failure_result(exc)
        try:
            failure = _with_customer_presentation(failure)
        except Exception:
            # The safe structured failure remains authoritative if presentation
            # construction itself is unavailable.
            pass
        print(json.dumps(failure), file=sys.stderr)
        raise SystemExit(1)
