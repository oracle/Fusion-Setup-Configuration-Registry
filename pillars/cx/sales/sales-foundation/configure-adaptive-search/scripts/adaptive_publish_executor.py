#!/usr/bin/env python3
"""Execute the separately approved Fusion ABO Adaptive Search companion safely.

This is deliberately the runtime counterpart to ``adaptive_publish_operation``.
The operation module defines the redacted public contract; this executor owns
the private Data Loader correlation and returns versioned Core handoffs. It
never accepts a raw URL, request body, or credential from a caller.

The parent follows Core's persisted preflight, evaluates ordered task rules,
and later approves its exact saved preview. Status checks Data Loader only on an explicit user request; after
confirmed load success, controller ticks monitor the discovered publish job.
No status or recovery route submits another load.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid
from typing import Any, Callable, Iterator, Mapping, Optional, Sequence
from urllib.parse import urlsplit


def _find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "core" / "data-loader" / "scripts").is_dir():
            return candidate
        if (candidate / "fdos" / "core" / "data-loader" / "scripts").is_dir():
            return candidate / "fdos"
    raise RuntimeError("Could not locate the FSCR repository root.")


REPO_ROOT = _find_repo_root(Path(__file__).resolve())
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))
ABO_SCRIPT_DIRECTORY = REPO_ROOT / "pillars/cx/configure-price-quote/quoting/enable-fusion-asset-based-ordering/scripts"
if str(ABO_SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ABO_SCRIPT_DIRECTORY))

from adaptive_publish_operation import (  # noqa: E402
    AdaptivePublishOperationError,
    build_publish_data_loader_source,
    build_status_request,
    create_preparation,
    create_submission,
    create_companion_submission,
    validate_companion_request,
    evaluate_status,
    validate_status_request,
    INITIALIZATION_ENTITIES,
    validate_initialization_request,
    create_initialization_submission,
    validate_initialization_operation,
    evaluate_initialization_status,
)
from validate_publish_contract import DEFAULT_CONTRACT, validate as validate_publish_contract  # noqa: E402


DATA_LOADER_HANDOFF_VERSION = "26.10.1"
FUSION_REST = REPO_ROOT / "core" / "fusion-api" / "rest-api-client" / "scripts" / "fusion_rest_client.py"

REQUIRED_ENTITIES = ("ConsolidatedAsset", "SerializedAsset")
PUBLISH_LOADER_FIELDS = {
    "RestAction": "POST",
    "Content-Type": "application/json",
    "REST-Framework-Version": "9",
    "Preference": "transient",
}
AUTHORIZATION_SCOPE = "fusion_abo_adaptive_search_v1"
PREPARATION_ID_PATTERN = re.compile(r"^app_[a-f0-9]{32}$")
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$", re.IGNORECASE)
# The Data Loader initiation/status reports return private Content and Request
# IDs, not an Adaptive Search publish job ID.  For the approved Fusion ABO
# companion route, the child discovers that job only after its own Data Loader
# request succeeds, then pins every later status read to the discovered ID.
ADAPTIVE_SEARCH_JOB_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$")
NONTERMINAL_PUBLISH_STATES = frozenset({"WAIT", "READY", "RUNNING", "PAUSED", "SUBMITTED"})
TERMINAL_PUBLISH_STATES = frozenset({"SUCCEEDED", "ERROR", "FAILED", "CANCELLED"})


class AdaptivePublishExecutorError(RuntimeError):
    """Raised for an unsafe companion execution condition."""


class AdaptivePublishReadError(AdaptivePublishExecutorError):
    """A redacted read failure with just enough classification for safe routing."""

    def __init__(
        self,
        message: str,
        *,
        not_found: bool = False,
        http_status: int | None = None,
        provider_message: str | None = None,
        provider_code: str | None = None,
        failure_stage: str = "adaptive_search_readback",
        failure_class: str = "fusion_api_error",
    ) -> None:
        super().__init__(message)
        self.not_found = not_found
        self.http_status = http_status
        self.provider_message = provider_message
        self.provider_code = provider_code
        self.failure_stage = failure_stage
        self.failure_class = failure_class
        self.provider_error = {
            key: value for key, value in {
                "http_status": http_status,
                "message": provider_message,
                "code": provider_code,
            }.items() if value is not None
        }


class AdaptiveInitializationRequired(AdaptivePublishReadError):
    """Only an allowlisted entity-catalog condition may select initialization."""
    def __init__(self, *, http_status=None):
        super().__init__(
            "Could not find active meta model" if http_status == 400
            else "Adaptive Search entity catalog is null or empty.",
            http_status=http_status,
            failure_stage="adaptive_entity_readback",
        )


# ``Callable[...]`` is evaluated at import time on Python 3.9 even with
# postponed function annotations, so keep this alias PEP-604-free.
CommandRunner = Callable[[Sequence[str], Optional[str]], subprocess.CompletedProcess[str]]


def _run(command: Sequence[str], stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, input=stdin, text=True, capture_output=True, check=False)


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AdaptivePublishExecutorError(f"{name} must be an object.")
    return value


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AdaptivePublishExecutorError(f"{name} must be a nonblank string.")
    return value.strip()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise AdaptivePublishExecutorError(f"Required local artifact is unavailable: {path.name}.") from exc
    return digest.hexdigest()


def _read_json(path: Path, name: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AdaptivePublishExecutorError(f"{name} is unavailable or invalid JSON.") from exc
    return dict(_mapping(value, name))


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    """Atomically write a private, credential-free workflow record."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: Any, name: str) -> datetime:
    rendered = _text(value, name)
    normalized = rendered[:-1] + "+00:00" if rendered.endswith("Z") else rendered
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise AdaptivePublishExecutorError(f"{name} must be an RFC 3339 timestamp.") from exc
    if parsed.tzinfo is None:
        raise AdaptivePublishExecutorError(f"{name} must include a timezone.")
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def _host(value: str) -> str:
    parsed = urlsplit(value)
    return (parsed.netloc or parsed.path.split("/", 1)[0]).casefold()


def _target(value: Any) -> dict[str, str]:
    source = _mapping(value, "target")
    return {
        "environment": _text(source.get("environment"), "target.environment"),
        "fusion_host": _text(source.get("fusion_host"), "target.fusion_host"),
    }


def _entities(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise AdaptivePublishExecutorError("entities must be an array.")
    result = [_text(item, "entities[]") for item in value]
    if result != list(REQUIRED_ENTITIES):
        raise AdaptivePublishExecutorError(
            "Fusion ABO Adaptive Search requires exactly ConsolidatedAsset and SerializedAsset in order."
        )
    return result


def _properties_match_target(properties: Path, request: Mapping[str, Any]) -> None:
    try:
        entries = dict(
            line.split("=", 1)
            for line in properties.read_text(encoding="utf-8").splitlines()
            if "=" in line and not line.lstrip().startswith(("#", "!"))
        )
    except OSError as exc:
        raise AdaptivePublishExecutorError("Approved Fusion properties are unavailable.") from exc
    target = _target(request.get("target"))
    environment = _text(entries.get("environment"), "Fusion properties environment")
    rest_base_url = _text(entries.get("restBaseUrl"), "Fusion properties restBaseUrl")
    if environment != target["environment"] and _host(environment) != _host(target["fusion_host"]):
        raise AdaptivePublishExecutorError("Approved Fusion properties target a different environment.")
    if _host(rest_base_url) != _host(target["fusion_host"]):
        raise AdaptivePublishExecutorError("Approved Fusion properties target a different Fusion host.")


def _fusion_auth_options(properties: Path, token_cache: str | None) -> list[str]:
    result = ["--properties", str(properties)]
    if token_cache:
        result.extend(["--token-cache", token_cache])
    return result


def _authorization(request: Mapping[str, Any], prepared: Mapping[str, Any]) -> dict[str, Any]:
    authorization = _mapping(request.get("workflow_authorization"), "workflow_authorization")
    if _text(authorization.get("scope"), "workflow_authorization.scope") != AUTHORIZATION_SCOPE:
        raise AdaptivePublishExecutorError("Workflow authorization has an unsupported scope.")
    for field in ("project_id", "publish_type"):
        if _text(authorization.get(field), f"workflow_authorization.{field}") != _text(request.get(field), field):
            raise AdaptivePublishExecutorError("Workflow authorization does not match the submitted request.")
    if _target(authorization.get("target")) != _target(request.get("target")):
        raise AdaptivePublishExecutorError("Workflow authorization targets a different Fusion environment.")
    if _entities(authorization.get("entities")) != _entities(request.get("entities")):
        raise AdaptivePublishExecutorError("Workflow authorization does not cover the requested entity pair.")
    if authorization.get("submission_limit") != 1:
        raise AdaptivePublishExecutorError("Workflow authorization must allow exactly one Data Loader submission.")
    if _text(authorization.get("publish_type"), "workflow_authorization.publish_type") != "selective":
        raise AdaptivePublishExecutorError("Workflow authorization does not permit selective publish.")
    now = datetime.now(timezone.utc).replace(microsecond=0)
    issued_at = _parse_timestamp(authorization.get("issued_at"), "workflow_authorization.issued_at")
    expires_at = _parse_timestamp(authorization.get("expires_at"), "workflow_authorization.expires_at")
    if issued_at > now or expires_at <= issued_at:
        raise AdaptivePublishExecutorError("Workflow plan has an invalid time window.")
    archive_sha = _text(authorization.get("archive_sha256"), "workflow_authorization.archive_sha256")
    source_sha = _text(authorization.get("source_sha256"), "workflow_authorization.source_sha256")
    if not SHA256_PATTERN.fullmatch(archive_sha) or not SHA256_PATTERN.fullmatch(source_sha):
        raise AdaptivePublishExecutorError("Workflow authorization has invalid immutable-source digests.")
    prepared_contract = _mapping(
        prepared.get("prepared_operation"), "prepared Adaptive Search contract"
    )
    immutable_source = _mapping(
        prepared_contract.get("immutable_source"), "prepared immutable source"
    )
    if archive_sha.casefold() != _text(immutable_source.get("archive_sha256"), "prepared archive_sha256").casefold():
        raise AdaptivePublishExecutorError("Workflow authorization does not cover the prepared Data Loader archive.")
    if source_sha.casefold() != _text(immutable_source.get("source_sha256"), "prepared source_sha256").casefold():
        raise AdaptivePublishExecutorError("Workflow authorization does not cover the prepared source.")
    record_ref = _text(authorization.get("approval_record_ref"), "workflow_authorization.approval_record_ref")
    record_fingerprint = _text(
        authorization.get("approval_record_fingerprint"), "workflow_authorization.approval_record_fingerprint"
    )
    approval_fingerprint = _text(
        authorization.get("approval_fingerprint"), "workflow_authorization.approval_fingerprint"
    )
    if not SHA256_PATTERN.fullmatch(approval_fingerprint) or not SHA256_PATTERN.fullmatch(record_fingerprint):
        raise AdaptivePublishExecutorError("Workflow authorization has invalid approval provenance fingerprints.")
    record_path = (REPO_ROOT / record_ref).resolve()
    try:
        record_path.relative_to((REPO_ROOT / "project" / _text(authorization.get("project_id"), "workflow_authorization.project_id")).resolve())
    except ValueError as exc:
        raise AdaptivePublishExecutorError("Workflow authorization record resolves outside the approved project workspace.") from exc
    if not record_path.is_file() or _sha256_file(record_path).casefold() != record_fingerprint.casefold():
        raise AdaptivePublishExecutorError("Workflow authorization provenance record is unavailable or changed.")
    # A path and checksum alone are insufficient authorization evidence.  The
    # persisted parent preview must also contain the exact one-time approval
    # and immutable source that this child is about to consume.
    record = _read_json(record_path, "workflow authorization provenance record")
    preview = _mapping(record.get("preview"), "workflow authorization provenance preview")
    if _text(preview.get("approval_fingerprint"), "provenance approval_fingerprint").casefold() != _text(
        authorization.get("approval_fingerprint"), "workflow_authorization.approval_fingerprint"
    ).casefold():
        raise AdaptivePublishExecutorError("Workflow authorization does not match its durable parent approval record.")
    if _text(preview.get("project_id"), "provenance project_id") != _text(
        authorization.get("project_id"), "workflow_authorization.project_id"
    ):
        raise AdaptivePublishExecutorError("Workflow authorization project does not match its durable parent approval record.")
    components = _mapping(preview.get("components"), "provenance components")
    adaptive = _mapping(components.get("adaptive_search"), "provenance adaptive_search")
    if _target(adaptive.get("target")) != _target(authorization.get("target")):
        raise AdaptivePublishExecutorError("Workflow authorization target does not match its durable parent approval record.")
    if _entities(adaptive.get("entities")) != _entities(authorization.get("entities")):
        raise AdaptivePublishExecutorError("Workflow authorization entities do not match its durable parent approval record.")
    if _text(adaptive.get("publish_type"), "provenance publish_type") != _text(
        authorization.get("publish_type"), "workflow_authorization.publish_type"
    ):
        raise AdaptivePublishExecutorError("Workflow authorization publish type does not match its durable parent approval record.")
    immutable = _mapping(adaptive.get("immutable_source"), "provenance immutable source")
    if _text(immutable.get("archive_sha256"), "provenance archive_sha256").casefold() != archive_sha.casefold() or _text(
        immutable.get("source_sha256"), "provenance source_sha256"
    ).casefold() != source_sha.casefold():
        raise AdaptivePublishExecutorError("Workflow authorization immutable source does not match its durable parent approval record.")
    return dict(authorization)


def _require_success(result: subprocess.CompletedProcess[str], stage: str) -> None:
    if result.returncode:
        raise AdaptivePublishExecutorError(f"{stage} failed before a downstream side effect was allowed.")


def _task_context(project_root: Path) -> tuple[Path, str, int]:
    path = project_root / "artifacts" / "shared" / "runbook" / "current" / "task-context.json"
    context = _read_json(path, "Run Book task context")
    tasks = context.get("tasks")
    if not isinstance(tasks, list):
        raise AdaptivePublishExecutorError("Run Book task context has no tasks.")
    matches = [
        value for value in tasks
        if isinstance(value, Mapping) and value.get("task_name") == "Enable Fusion Asset-Based Ordering"
    ]
    if len(matches) != 1:
        raise AdaptivePublishExecutorError("Run Book task context must contain exactly one Enable Fusion Asset-Based Ordering task.")
    sequence = matches[0].get("sequence")
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
        raise AdaptivePublishExecutorError("Run Book task context has an invalid Enable Fusion Asset-Based Ordering sequence.")
    return path, "Enable Fusion Asset-Based Ordering", sequence


def _json_from_output(result: subprocess.CompletedProcess[str], stage: str) -> dict[str, Any]:
    _require_success(result, stage)
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AdaptivePublishExecutorError(f"{stage} did not return JSON.") from exc
    return dict(_mapping(value, stage))


FUSION_HTTP_ERROR_PATTERN = re.compile(
    r"(?:^|\r?\n)Error: HTTP (?P<status>[1-5][0-9]{2})"
    r"(?: calling [^\r\n]+?)?:[ \t]*(?P<body>\{.*\})[ \t]*(?:\r?\n)?\Z",
    re.DOTALL,
)
SAFE_PROVIDER_MESSAGE_MAX_LENGTH = 512
SAFE_PROVIDER_CODE_PATTERN = re.compile(r"^(?:[A-Za-z][A-Za-z0-9_.:-]{1,95}|[0-9]{1,96})$")
SENSITIVE_PROVIDER_TEXT_PATTERN = re.compile(
    r"(?i)\b(authorization|access[_-]?token|refresh[_-]?token|client[_-]?secret|password)"
    r"\s*[:=]\s*[^,;\s]+"
)
BEARER_PROVIDER_TEXT_PATTERN = re.compile(r"(?i)\b(bearer|basic)\s+[A-Za-z0-9._~+/=-]+")


def _safe_provider_text(value: Any) -> str | None:
    """Return one bounded Oracle message without retaining an arbitrary body."""

    if not isinstance(value, str):
        return None
    rendered = " ".join(value.split())
    if not rendered or "<" in rendered or ">" in rendered:
        return None
    rendered = SENSITIVE_PROVIDER_TEXT_PATTERN.sub(r"\1=[REDACTED]", rendered)
    rendered = BEARER_PROVIDER_TEXT_PATTERN.sub(r"\1 [REDACTED]", rendered)
    return rendered[:SAFE_PROVIDER_MESSAGE_MAX_LENGTH]


def _safe_provider_code(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    rendered = value.strip()
    return rendered if SAFE_PROVIDER_CODE_PATTERN.fullmatch(rendered) else None


def _safe_fusion_error_context(body: Any) -> dict[str, str]:
    """Extract only allowlisted scalar fields from a parsed Fusion error body."""

    if not isinstance(body, Mapping):
        return {}
    sources: list[Mapping[str, Any]] = [body]
    details = body.get("o:errorDetails")
    if isinstance(details, list):
        sources.extend(item for item in details[:5] if isinstance(item, Mapping))
    message = next((candidate for source in sources for field in ("message", "detail", "Error")
                    if (candidate := _safe_provider_text(source.get(field)))), None)
    if message is None:
        message = next((candidate for source in sources
                        if (candidate := _safe_provider_text(source.get("title")))), None)
    code = next((candidate for source in sources for field in ("o:errorCode", "errorCode", "code")
                 if (candidate := _safe_provider_code(source.get(field)))), None)
    return {key: value for key, value in {"message": message, "code": code}.items() if value is not None}


def _fusion_http_error(stderr: str) -> tuple[int, Any] | None:
    """Return the final Fusion HTTP status/body independently of prior diagnostics."""
    match = FUSION_HTTP_ERROR_PATTERN.search(stderr)
    if not match:
        return None
    try:
        body = json.loads(match.group("body"))
    except json.JSONDecodeError:
        body = None
    return int(match.group("status")), body


def _run_rest_json(
    runner: CommandRunner,
    endpoint: str,
    output_path: Path,
    *,
    properties: Path,
    token_cache: str | None,
    query: Sequence[str] = (),
) -> dict[str, Any]:
    command: list[str] = [sys.executable, str(FUSION_REST), endpoint, "--output", str(output_path)]
    for item in query:
        command.extend(["--query", item])
    command.extend(_fusion_auth_options(properties, token_cache))
    result = runner(command, None)
    if result.returncode:
        # Current and earlier Fusion releases use different exact bodies for
        # "no previous publish".  Do not collapse other 404s or failures into
        # that condition.
        error = _fusion_http_error(result.stderr or "")
        if (endpoint == "/crmRestApi/searchResources/latest/entities"
                and error == (400, {"Error": "Could not find active meta model"})):
            raise AdaptiveInitializationRequired(http_status=400)
        not_found = bool(error and error[0] == 404 and error[1] in (
                {"Error": "Cannot parse null string"},
                {"Error": "No prior publish job was found."},
            ))
        http_status = error[0] if error else None
        provider = _safe_fusion_error_context(error[1]) if error else {}
        failure_stage = ("adaptive_entity_readback" if endpoint.endswith("/entities")
                         else "adaptive_publish_status_readback")
        failure_class = ("auth_expired_or_invalid" if http_status == 401 else
                         "authorization_or_privilege" if http_status == 403 else
                         "fusion_api_error" if http_status is not None else
                         "transport_or_environment")
        message = (f"Adaptive Search read failed (HTTP {http_status})."
                   if http_status is not None else "Adaptive Search read failed.")
        if provider.get("message"):
            message += f" Oracle reported: {provider['message']}"
            if provider.get("code"):
                message += f" (code {provider['code']})"
        raise AdaptivePublishReadError(
            message,
            not_found=not_found,
            http_status=http_status,
            provider_message=provider.get("message"),
            provider_code=provider.get("code"),
            failure_stage=failure_stage,
            failure_class=failure_class,
        )
    if endpoint == "/crmRestApi/searchResources/latest/entities":
        try:
            if json.loads(output_path.read_text(encoding="utf-8")) is None:
                return {"items": None}
        except (OSError, json.JSONDecodeError) as exc:
            raise AdaptivePublishReadError("Adaptive Search catalog response is unavailable or malformed.") from exc
    return _read_json(output_path, "Adaptive Search response")


def _safe_baseline_publish_status(
    runner: CommandRunner, *, work: Path, properties: Path, token_cache: str | None
) -> dict[str, Any] | None:
    """Return a terminal/no-prior baseline; a nonterminal baseline blocks submit."""
    output = work / "preflight-publish-status.json"
    try:
        status = _run_rest_json(
            runner, "/crmRestApi/searchResources/latest/publishStatus", output,
            properties=properties, token_cache=token_cache,
        )
    except AdaptivePublishReadError as exc:
        if not exc.not_found:
            raise
        # The public endpoint reports no prior publish differently by release.
        # A missing response cannot be used as a positive correlation signal;
        # retain it as an explicit no-baseline marker and require a new job ID
        # after successful Data Loader processing.
        return None
    state = status.get("status")
    if not isinstance(state, str) or not state.strip():
        raise AdaptivePublishExecutorError(
            "Adaptive Search publish-status response has no usable state; do not submit a concurrent publish."
        )
    normalized_state = state.strip().upper()
    if normalized_state in NONTERMINAL_PUBLISH_STATES:
        raise AdaptivePublishExecutorError("Adaptive Search already has a nonterminal publish; do not submit another publish.")
    if normalized_state not in TERMINAL_PUBLISH_STATES:
        raise AdaptivePublishExecutorError(
            "Adaptive Search publish-status response has an unrecognized state; do not submit a concurrent publish."
        )
    return status


def _validate_entities(
    runner: CommandRunner, *, work: Path, properties: Path, token_cache: str | None
) -> dict[str, Any]:
    entities = _run_rest_json(
        runner,
        "/crmRestApi/searchResources/latest/entities",
        work / "entities.json",
        properties=properties,
        token_cache=token_cache,
        query=("language=en", "limit=-1", "isDocument=true"),
    )
    items = entities.get("items")
    if ("items" in entities and items is None) or items == []:
        raise AdaptiveInitializationRequired()
    if not isinstance(items, list):
        raise AdaptivePublishExecutorError("Adaptive Search entity catalog is unavailable for the required selective publish.")
    names = {
        item.get("entityName") for item in items
        if isinstance(item, Mapping) and isinstance(item.get("entityName"), str)
    }
    missing = [name for name in REQUIRED_ENTITIES if name not in names]
    if missing:
        raise AdaptivePublishExecutorError("Adaptive Search entity catalog is missing the required Fusion ABO entities.")
    return {"entity_count": len(items), "required_entities": list(REQUIRED_ENTITIES)}


def prepare(*args, **kwargs):
    raise AdaptivePublishExecutorError("Saved preparation is retired; use the Fusion ABO prepare-adaptive-load.")


def _prepared_record(path: Path, request: Mapping[str, Any]) -> dict[str, Any]:
    prepared = _read_json(path, "prepared Adaptive Search record")
    if prepared.get("operation") != "prepared_partial_publish":
        raise AdaptivePublishExecutorError("Prepared Adaptive Search record has an invalid operation.")
    contract = _mapping(prepared.get("prepared_operation"), "prepared Adaptive Search contract")
    for field in ("project_id", "target", "entities", "publish_type"):
        if contract.get(field) != request.get(field):
            raise AdaptivePublishExecutorError(f"Prepared Adaptive Search record does not match approved {field}.")
    expected_preparation_id = request.get("preparation_id")
    if expected_preparation_id is not None and contract.get("preparation_id") != expected_preparation_id:
        raise AdaptivePublishExecutorError("Prepared Adaptive Search record does not match approved preparation_id.")
    immutable_source = _mapping(contract.get("immutable_source"), "prepared immutable source")
    archive = Path(_text(prepared.get("archive_path"), "prepared archive path"))
    expected = _text(immutable_source.get("archive_sha256"), "prepared archive SHA-256")
    if not archive.is_file() or _sha256_file(archive).casefold() != expected.casefold():
        raise AdaptivePublishExecutorError("Prepared Adaptive Search archive is missing or changed after approval.")
    if not Path(_text(prepared.get("preflight_envelope_path"), "prepared preflight envelope path")).is_file():
        raise AdaptivePublishExecutorError("Prepared Data Loader preflight envelope is unavailable.")
    return prepared


def _rule_results(plan: Mapping[str, Any], prepared: Mapping[str, Any], predecessor: Mapping[str, Any]) -> list[dict[str, Any]]:
    if plan.get("taskValidationStatus") not in {"ready", "skipped"}:
        raise AdaptivePublishExecutorError("Task Hook validation is not ready for an Adaptive Search preview.")
    resources = plan.get("ruleResources")
    if not isinstance(resources, list):
        raise AdaptivePublishExecutorError("Task Hook plan has no ordered rule resources.")
    contract = _mapping(prepared.get("prepared_operation"), "prepared Adaptive Search contract")
    immutable_source = _mapping(contract.get("immutable_source"), "prepared immutable source")
    archive = Path(_text(prepared.get("archive_path"), "prepared archive"))
    source = Path(_text(prepared.get("preflight_envelope_path"), "prepared preflight")).parent / "publish.xlsx"
    if not archive.is_file() or _sha256_file(archive) != immutable_source.get("archive_sha256"):
        raise AdaptivePublishExecutorError("Prepared publish archive changed before Task Hook validation.")
    if not source.is_file() or _sha256_file(source) != immutable_source.get("source_sha256"):
        raise AdaptivePublishExecutorError("Prepared publish source changed before Task Hook validation.")
    evidence = _mapping(prepared.get("entity_evidence"), "Adaptive Search entity evidence")
    if evidence.get("required_entities") != list(REQUIRED_ENTITIES):
        raise AdaptivePublishExecutorError("Prepared publish entity validation is incomplete.")
    if predecessor.get("status") != "completed":
        raise AdaptivePublishExecutorError("Verified CPQ predecessor evidence is missing.")
    if predecessor.get("project_id") != contract.get("project_id") or predecessor.get("target") != contract.get("target"):
        raise AdaptivePublishExecutorError("CPQ predecessor project or target differs from the prepared publish.")
    verification = _mapping(predecessor.get("cpq_verification"), "CPQ readback evidence")
    if verification.get("status") != "completed" or not isinstance(verification.get("validated_process_variable_name"), str) or not verification["validated_process_variable_name"].strip():
        raise AdaptivePublishExecutorError("CPQ predecessor lacks completed process verification.")
    operations = verification.get("completed_operations")
    normal = ["configure_fusion_abo_settings", "verify_fusion_abo_enabled", "verify_abo_delta_action_library_function"]
    recovery = ["configure_abo_delta_action_library_function", "verify_abo_delta_action_library_function"]
    operation_ids = [item.get("id") for item in operations if isinstance(item, Mapping)] if isinstance(operations, list) else []
    if not isinstance(operations, list) or operation_ids not in (normal, recovery) or len(operations) != len(operation_ids):
        raise AdaptivePublishExecutorError("CPQ predecessor lacks the exact Data Loader and readback sequence.")
    if operation_ids == recovery:
        prior = verification.get("preexisting_cpq_readback")
        if not isinstance(prior, Mapping) or (
            prior.get("status") != "verified"
            or prior.get("method") != "GET"
            or prior.get("http_status") != 200
            or prior.get("enable_fusion_abo") != "Yes"
            or prior.get("process_variable_name") != verification["validated_process_variable_name"]
        ):
            raise AdaptivePublishExecutorError("CPQ recovery predecessor lacks verified preexisting Fusion ABO settings.")
    if any(not isinstance(item, Mapping) or item.get("status") != "completed" for item in operations) or operations[0].get("data_loader_status") != "SUCCEEDED":
        raise AdaptivePublishExecutorError("CPQ predecessor Data Loader or readback did not complete successfully.")
    if any(item.get("method") != "GET" or item.get("http_status") != 200 for item in operations[1:]):
        raise AdaptivePublishExecutorError("CPQ predecessor lacks successful GET readback evidence.")
    results: list[dict[str, Any]] = []
    seen_nodes: set[str] = set()
    for resource in resources:
        filename = resource.get("file") if isinstance(resource, Mapping) else None
        if not isinstance(filename, str) or not filename:
            raise AdaptivePublishExecutorError("Task Hook plan has an invalid rule resource.")
        nodes = resource.get("nodes")
        if not isinstance(nodes, list) or not nodes:
            raise AdaptivePublishExecutorError("Task Hook resource has no planned nodes.")
        ids = {_text(_mapping(node, "Task Hook node").get("id"), "Task Hook node id") for node in nodes}
        seen_nodes.update(ids)
        checked = sorted(ids & {"ABO.PREPARE_ADAPTIVE_SEARCH", "ABO.CPQ_VERIFICATION"})
        deferred = sorted(ids - set(checked))
        results.append({
            "source": filename,
            "status": "passed" if checked and not deferred else "not_applicable",
            "issues": [{"severity": "info", "message": f"Prepared publish source, archive, entity evidence, and completed CPQ predecessor were verified for current-stage nodes {', '.join(checked) or 'none'}; this resource also contains deferred or unrelated nodes: {', '.join(deferred) or 'none'}. A resource is passed only when all its nodes have current-stage evidence."}],
            "changes": [],
        })
    if not {"ABO.PREPARE_ADAPTIVE_SEARCH", "ABO.CPQ_VERIFICATION"} <= seen_nodes:
        raise AdaptivePublishExecutorError("Task Hook omitted required Fusion ABO predecessor nodes.")
    return results


def _reserve_submission(work: Path, request: Mapping[str, Any]) -> tuple[Path, bool]:
    authorization = _mapping(request.get("workflow_authorization"), "workflow_authorization")
    fingerprint = _text(authorization.get("approval_fingerprint"), "workflow_authorization.approval_fingerprint").casefold()
    if not SHA256_PATTERN.fullmatch(fingerprint):
        raise AdaptivePublishExecutorError("workflow_approval_fingerprint must be a SHA-256 value.")
    path = work / f"workflow-authorization-{fingerprint}.json"
    payload = {
        "state": "reserved_before_data_loader_submission",
        "approval_fingerprint": fingerprint,
        "project_id": _text(request.get("project_id"), "project_id"),
        "target": _target(request.get("target")),
        "entities": _entities(request.get("entities")),
    }
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return path, False
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path, True


def submit(*args, **kwargs):
    raise AdaptivePublishExecutorError("The legacy direct approval route is retired; use the prepared Core load approval route.")


def validate_companion_loader_row(row: Mapping[str, Any], entities: Sequence[str]) -> None:
    """Validate our complete input row, not a reread of Core's captured source."""
    expected = {**PUBLISH_LOADER_FIELDS, **build_publish_data_loader_source(
        {"entities": list(entities), "publishType": "selective"}, entities_metadata_type="string")}
    row = _mapping(row, "companion loader row")
    if set(row) != set(expected):
        raise AdaptivePublishExecutorError("Companion loader row must contain exactly the six mapped publish fields.")
    for field, value in expected.items():
        if row[field] != value:
            raise AdaptivePublishExecutorError(f"Companion loader row has an invalid {field} value.")


def build_companion_loader_row(entities: Sequence[str]) -> dict[str, str]:
    """Add the loader operation/headers around the existing body serializer."""
    errors, binding = validate_publish_contract(_read_json(DEFAULT_CONTRACT, "publish API contract"))
    if errors or binding is None:
        raise AdaptivePublishExecutorError("The embedded publish API contract is invalid; preparation stopped.")
    row = {
        "RestAction": binding["method"],
        **build_publish_data_loader_source(
            {"entities": list(entities), "publishType": "selective"}, entities_metadata_type="string"),
        "Content-Type": binding["contentType"],
        "REST-Framework-Version": PUBLISH_LOADER_FIELDS["REST-Framework-Version"],
        "Preference": binding["requiredHeaders"]["Preference"],
    }
    validate_companion_loader_row(row, entities)
    return row


def prepare_publish_load(request: Mapping[str, Any], predecessor: Mapping[str, Any], *,
                         project_root: Path, properties: Path, workflow_record_path: Path,
                         token_cache=None, runner: CommandRunner = _run,
                         load_runner=None, emit=None) -> dict[str, Any]:
    return _prepare_publish_load(request, predecessor, project_root=project_root, properties=properties,
        workflow_record_path=workflow_record_path, token_cache=token_cache, runner=runner,
        load_runner=load_runner, emit=emit, initialization=False)


def prepare_initialization_load(request, predecessor, *, project_root, properties, workflow_record_path,
                                token_cache=None, runner=_run, load_runner=None, emit=None):
    return _prepare_publish_load(request, predecessor, project_root=project_root, properties=properties,
        workflow_record_path=workflow_record_path, token_cache=token_cache, runner=runner,
        load_runner=load_runner, emit=emit, initialization=True)


def _prepare_publish_load(request, predecessor, *, project_root, properties, workflow_record_path,
                          token_cache, runner, load_runner, emit, initialization):
    """Own one ABO companion workbook and live Core approval connection."""
    abo_scripts = REPO_ROOT / "pillars" / "cx" / "configure-price-quote" / "quoting" / "enable-fusion-asset-based-ordering" / "scripts"
    if str(abo_scripts) not in sys.path:
        sys.path.insert(0, str(abo_scripts))
    (validate_initialization_request if initialization else validate_companion_request)(request)
    if not initialization and (request.get("handover_version") != "2.0" or request.get("operation") != "submit_partial_publish"):
        raise AdaptivePublishExecutorError("The companion requires a v2 live handover.")
    target = _target(request.get("target"))
    entities = list(request["entities"]) if initialization else _entities(request.get("entities"))
    if not initialization and (entities != list(REQUIRED_ENTITIES) or request.get("publish_type") != "selective"):
        raise AdaptivePublishExecutorError("Only the fixed ABO selective entity pair is allowed.")
    _properties_match_target(properties, request)
    root = project_root.resolve()
    try:
        workflow_record_path.resolve().relative_to(root)
    except ValueError as exc:
        raise AdaptivePublishExecutorError("Parent workflow is outside the selected project.") from exc
    parent = _read_json(workflow_record_path, "parent workflow")
    fingerprint = _text(parent.get("workflow_approval_fingerprint"), "workflow fingerprint")
    if not SHA256_PATTERN.fullmatch(fingerprint):
        raise AdaptivePublishExecutorError("Parent workflow identity is malformed.")
    if (parent.get("schema_version") != "2.0" or parent.get("state") != "cpq_completed"
            or parent.get("project_id") != request.get("project_id")
            or parent.get("cpq_verification") != dict(predecessor)):
        raise AdaptivePublishExecutorError("Exact verified CPQ predecessor is required.")
    parent_target = _target(parent.get("target"))
    if (parent_target["environment"] != target["environment"]
            or _host(parent_target["fusion_host"]) != _host(target["fusion_host"])
            or predecessor.get("status") != "completed"):
        raise AdaptivePublishExecutorError("CPQ predecessor belongs to a different target or is incomplete.")
    context = _mapping(parent.get("workflow_context"), "parent business context")
    adaptive_scope = _mapping(_mapping(context.get("components"), "parent components").get("adaptive_search"), "parent selective scope")
    if (context.get("approval_fingerprint") != fingerprint
            or context.get("project_id") != request.get("project_id")
            or _target(adaptive_scope.get("target")) != target
            or adaptive_scope.get("entities") != list(REQUIRED_ENTITIES)
            or adaptive_scope.get("publish_type") != "selective"):
        raise AdaptivePublishExecutorError("Companion scope differs from exact parent business provenance.")
    operations = predecessor.get("completed_operations")
    if (not isinstance(operations, list) or len(operations) != 3
            or any(not isinstance(item, Mapping) for item in operations)
            or [item.get("id") for item in operations] not in (
                ["configure_fusion_abo_settings", "verify_fusion_abo_enabled", "verify_abo_delta_action_library_function"],
                ["configure_abo_delta_action_library_function", "verify_fusion_abo_enabled", "verify_abo_delta_action_library_function"])
            or any(item.get("status") != "completed" for item in operations)
            or operations[0].get("data_loader_status") != "SUCCEEDED"
            or any(item.get("method") != "GET" or item.get("http_status") != 200 for item in operations[1:])):
        raise AdaptivePublishExecutorError("CPQ predecessor lacks load success and exact business readbacks.")
    if initialization:
        permission = _mapping(parent.get("adaptive_initialization"), "initialization preparation permission")
        proposal = _mapping(permission.get("proposal"), "initialization proposal")
        blocker = _mapping(parent.get("adaptive_initialization_blocker"), "initialization blocker")
        digest = hashlib.sha256(json.dumps(dict(proposal), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
        issued = _parse_timestamp(proposal.get("issued_at"), "initialization issued_at")
        expires = _parse_timestamp(proposal.get("expires_at"), "initialization expires_at")
        if (permission.get("status") != "consumed" or blocker.get("reason") not in {"missing_metamodel", "empty_catalog"}
                or (blocker.get("reason") == "missing_metamodel" and blocker.get("http_status") != 400)
                or permission.get("proposal_sha256") != digest
                or issued > datetime.now(timezone.utc) or datetime.now(timezone.utc) > expires
                or expires != issued + timedelta(hours=2)
                or proposal.get("purpose") != "adaptive_initialization_preparation_only"
                or proposal.get("project_id") != request["project_id"]
                or proposal.get("workflow_id") != fingerprint
                or proposal.get("target") != parent.get("target")
                or proposal.get("adaptive_target") != target
                or proposal.get("entities") != entities or proposal.get("publish_type") != "full"
                or "afi_" + str(proposal.get("proposal_id")) != request["initialization_id"]):
            raise AdaptivePublishExecutorError("Exact consumed initialization preparation permission is required.")
        other = workflow_record_path.parent / workflow_record_path.stem / "adaptive-live"
        if any((other / name).exists() for name in ("submission-intent.json", "operation.json")):
            raise AdaptivePublishExecutorError("A Partial Publish may be submitted; initialization is not permitted.")
    work = workflow_record_path.parent / workflow_record_path.stem / ("adaptive-initialization" if initialization else "adaptive-live")
    work.mkdir(parents=True, exist_ok=True)
    operation_path = work / "operation.json"
    intent_path = work / "submission-intent.json"
    if intent_path.exists() or operation_path.exists():
        raise AdaptivePublishExecutorError("A companion submission was already reserved; status/reconciliation only.")
    if (work / "companion-preparation.json").exists():
        raise AdaptivePublishExecutorError("This companion load is already prepared; resume its saved rules or approval.")
    if initialization:
        try:
            _validate_entities(runner, work=work, properties=properties, token_cache=token_cache)
        except AdaptiveInitializationRequired:
            pass
        else:
            return {"status": "not_required", "submission_started": False,
                    "next_action": "Catalog is now ready; prepare a fresh Partial Publish proposal."}
        # Explicitly clear the workbook cell; its REST body value is omitted.
        source_row = {**PUBLISH_LOADER_FIELDS, **build_publish_data_loader_source(
            {"entities": entities}, entities_metadata_type="string"), "publishType": ""}
        errors, binding = validate_publish_contract(_read_json(DEFAULT_CONTRACT, "publish API contract"))
        if errors or binding is None:
            raise AdaptivePublishExecutorError("The initialization publish contract is invalid.")
    else:
        source_row = build_companion_loader_row(entities)
        _validate_entities(runner, work=work, properties=properties, token_cache=token_cache)
    baseline = _safe_baseline_publish_status(runner, work=work, properties=properties, token_cache=token_cache)
    values_path = work / f"publish-values-{uuid.uuid4().hex}.json"
    _write_json(values_path, {"publish": [source_row]})
    handoff_id = "dlh_" + uuid.uuid4().hex
    preparation_path = work / "companion-preparation.json"
    _write_json(preparation_path, {"request": dict(request), "workflow_fingerprint": fingerprint,
        "initialization": initialization, "baseline_publish_status": baseline,
        "state": "awaiting_workbook", "handoff_id": handoff_id,
        "values_json_path": str(values_path), "source_row": source_row})
    handoff = {"handoff_version": DATA_LOADER_HANDOFF_VERSION, "handoff_id": handoff_id,
        "kind": "generate_populated_workbook", "business_object": "publish",
        "values_json_path": str(values_path), "output_directory": str(work),
        "authentication_reference": {"properties": str(properties),
            **({"token_cache": token_cache} if token_cache else {})}}
    return {"status": "handoff_required", "submission_started": False,
        "preparation_record": str(preparation_path), "core_data_loader_handoff": handoff}


def accept_publish_workbook_result(preparation_path: Path, result: Mapping[str, Any], *,
                                   project_root: Path, properties: Path,
                                   token_cache: str | None = None) -> dict[str, Any]:
    from cpq_settings_write_executor import data_loader_preflight_handoff, _artifact_inside
    preparation = _read_json(preparation_path, "companion preparation")
    if (preparation.get("state") != "awaiting_workbook"
            or result.get("handoff_version") != DATA_LOADER_HANDOFF_VERSION
            or result.get("handoff_id") != preparation.get("handoff_id")
            or result.get("status") != "generated"):
        raise AdaptivePublishExecutorError("Workbook result does not match the current companion handoff.")
    source = _artifact_inside(result.get("workbook_path"), project_root)
    if source != (preparation_path.parent / "publish.xlsx").resolve():
        raise AdaptivePublishExecutorError("Core did not return the expected publish.xlsx workbook.")
    handoff = data_loader_preflight_handoff(source, "publish", project_root, properties,
        token_cache, handoff_id=preparation["handoff_id"])
    stored_handoff = dict(handoff)
    stored_handoff.pop("authentication_reference", None)
    preparation.update({"state": "awaiting_core_preflight", "source_path": str(source),
                        "preflight_handoff": stored_handoff})
    _write_json(preparation_path, preparation)
    return {"status": "handoff_required", "preparation_record": str(preparation_path),
            "workbook_path": str(source), "core_data_loader_handoff": handoff}


def accept_publish_core_preflight(preparation_path: Path, result: Mapping[str, Any], *,
                                  project_root: Path) -> dict[str, Any]:
    from cpq_settings_write_executor import prepare_persisted_load
    preparation = _read_json(preparation_path, "companion preparation")
    if preparation.get("state") != "awaiting_core_preflight":
        raise AdaptivePublishExecutorError("Companion is not awaiting a Core preflight result.")
    request = _mapping(preparation.get("request"), "companion request")
    terminal = prepare_persisted_load(result, handoff=preparation["preflight_handoff"],
        workbook_source=Path(preparation["source_path"]), workbook_project_root=project_root,
        target=request["target"], scope={"business_object": "publish", "row": preparation["source_row"]},
        workflow_id=preparation["workflow_fingerprint"])
    preparation.update({"state": "awaiting_approval",
                        "prepared_load_record": terminal["prepared_load_record"]})
    _write_json(preparation_path, preparation)
    return {"status": "approval_required", "prepared_load_record": terminal["prepared_load_record"],
            "workbook_access": terminal["workbook_access"],
            "preview_sha256": terminal["preview_sha256"],
            "data_loader_markdown": terminal["data_loader_markdown"]}


def _loader_state(markdown: str) -> str:
    """Classify Core's status cells, not names/headings or diagnostic prose."""
    def cell_state(text):
        normalized = text.upper()
        if "❌ FAILED" in normalized or "ORA_ERROR" in normalized:
            return "FAILED"
        if any(token in normalized for token in (
                "❔ NOT AVAILABLE YET", "🟡 IN PROGRESS", "IN PROGRESS",
                "ORA_WAIT", "ORA_PENDING", "ORA_RUNNING", "QUEUED", "RUNNING")):
            return "PENDING"
        if "✅ SUCCEEDED" in normalized or "ORA_SUCCESS" in normalized:
            return "SUCCEEDED"
        return "INDETERMINATE"

    rows = [line.split("|")[1:-1] for line in markdown.splitlines() if line.startswith("|")]
    for index, cells in enumerate(rows):
        headings = [cell.strip().casefold() for cell in cells]
        if not all(name in headings for name in ("data set", "status", "total", "loaded", "failed")):
            continue
        states = []
        for values in rows[index + 1:]:
            if all(set(cell.strip()) <= {"-", ":"} for cell in values):
                continue
            if len(values) != len(headings):
                break  # A later, unrelated diagnostics table.
            state = cell_state(values[headings.index("status")])
            try:
                counts = [int(values[headings.index(name)].strip().replace(",", ""))
                          for name in ("total", "loaded", "failed")]
            except ValueError:
                counts = None
            if counts is not None:
                total, loaded, failed = counts
                if min(counts) < 0:
                    state = "INDETERMINATE"
                elif failed > 0:
                    state = "FAILED"
                elif state == "SUCCEEDED" and loaded != total:
                    state = "INDETERMINATE"
            elif state == "SUCCEEDED":
                state = "INDETERMINATE"
            states.append(state)
        if not states or "INDETERMINATE" in states:
            return "FAILED" if "FAILED" in states else "INDETERMINATE"
        return "FAILED" if "FAILED" in states else "PENDING" if "PENDING" in states else "SUCCEEDED"
    return cell_state(markdown)


def _adaptive_search_job_id_from_publish_status(publish: Mapping[str, Any]) -> str | None:
    """Read the job ID returned by Adaptive Search's post-loader status GET.

    The unfiltered status GET is used once, and only after this operation's
    exact Data Loader request has succeeded.  Its job ID is immediately
    persisted; every later GET is pinned with ``jobId``.  A response without a
    job ID means the asynchronous Adaptive publish is not observable yet, not
    that another publish should be submitted.
    """

    value = publish.get("jobId")
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise AdaptivePublishExecutorError("Adaptive Search status returned an invalid publish job ID.")
    job_id = str(value).strip()
    if not ADAPTIVE_SEARCH_JOB_ID_PATTERN.fullmatch(job_id):
        raise AdaptivePublishExecutorError("Adaptive Search status returned an invalid publish job ID.")
    return job_id


def _validated_publish_status(publish: Mapping[str, Any]) -> str:
    """Require a known Adaptive Search status before pinning a discovered ID."""

    value = publish.get("status")
    if not isinstance(value, str) or not value.strip():
        raise AdaptivePublishExecutorError("Adaptive Search status returned no usable publish state.")
    state = value.strip().upper()
    if state not in NONTERMINAL_PUBLISH_STATES | TERMINAL_PUBLISH_STATES:
        raise AdaptivePublishExecutorError("Adaptive Search status returned an unrecognized publish state.")
    return state


def _pre_submission_publish_job_id(operation: Mapping[str, Any]) -> str | None:
    """Return the terminal pre-submit job ID, when one was available.

    This is a stale-result fence for the one unfiltered post-loader lookup.
    The child must not pin the terminal job that the pre-submit concurrency
    check already observed; it waits until Adaptive Search reports a new job.
    """

    if "pre_submission_publish_status" not in operation:
        raise AdaptivePublishExecutorError("Persisted pre-submission Adaptive Search status is unavailable.")
    baseline = operation.get("pre_submission_publish_status")
    if baseline is None:
        return None
    if not isinstance(baseline, Mapping):
        raise AdaptivePublishExecutorError("Persisted pre-submission Adaptive Search status is invalid.")
    return _adaptive_search_job_id_from_publish_status(baseline)


def _persisted_adaptive_search_job_id(operation: Mapping[str, Any]) -> str | None:
    """Validate a private persisted job ID before it is used as a query value."""

    value = operation.get("adaptive_search_job_id")
    if value is None:
        return None
    if not isinstance(value, str) or not ADAPTIVE_SEARCH_JOB_ID_PATTERN.fullmatch(value.strip()):
        raise AdaptivePublishExecutorError("Persisted Adaptive Search job correlation is invalid.")
    return value.strip()


def _indeterminate_status(operation: Mapping[str, Any], *, stage: str, message: str) -> dict[str, Any]:
    """Return a durable terminal result when exact attribution cannot be proven."""

    return {
        "schema_version": operation["schema_version"],
        "publish_operation_id": operation["publish_operation_id"],
        "project_id": operation["project_id"],
        "target": operation["target"],
        "entities": operation["entities"],
        "publish_type": operation["publish_type"],
        "eligible_for_ess": False,
        "state": "INDETERMINATE",
        "terminal": True,
        "message": message,
        "monitoring": {"stage": stage, "terminal": True},
    }


def _public_submission_from_operation(operation: Mapping[str, Any]) -> dict[str, Any]:
    """Project the persisted private record into the contract's public shape."""

    try:
        return {
            key: operation[key]
            for key in (
                "schema_version",
                "publish_operation_id",
                "state",
                "project_id",
                "target",
                "entities",
                "publish_type",
                "status_check_operation",
            )
        }
    except KeyError as exc:
        raise AdaptivePublishExecutorError("Persisted Adaptive Search operation is missing its public identity.") from exc


def _retry_status(operation: Mapping[str, Any], *, stage: str, message: str) -> dict[str, Any]:
    """Return a redacted retryable result without treating a read failure as success."""

    return {
        "schema_version": operation["schema_version"],
        "publish_operation_id": operation["publish_operation_id"],
        "project_id": operation["project_id"],
        "target": operation["target"],
        "entities": operation["entities"],
        "publish_type": operation["publish_type"],
        "eligible_for_ess": False,
        "state": "PUBLISH_PENDING",
        "terminal": False,
        "retryable": True,
        "message": message,
        "monitoring": {"stage": stage, "terminal": False},
    }


def _with_read_error(result: Mapping[str, Any], error: AdaptivePublishReadError) -> dict[str, Any]:
    enriched = dict(result)
    read_error = {
        "failure_stage": error.failure_stage,
        "failure_class": error.failure_class,
        "observed_at": _utc_now(),
    }
    if error.http_status is not None:
        read_error["http_status"] = error.http_status
    if error.provider_error:
        enriched["provider_error"] = dict(error.provider_error)
        read_error["provider_error"] = dict(error.provider_error)
    enriched["status_read_error"] = read_error
    suffix = f" HTTP {error.http_status}." if error.http_status is not None else ""
    if error.provider_message:
        suffix += f" Oracle reported: {error.provider_message}"
        if error.provider_code:
            suffix += f" (code {error.provider_code})"
    enriched["message"] = f"{enriched['message']}{suffix}"
    return enriched


def _entity_readiness(
    runner: CommandRunner, *, work: Path, properties: Path, token_cache: str | None
) -> list[str]:
    payload = _run_rest_json(
        runner, "/crmRestApi/searchResources/latest/entities", work / "final-entities.json",
        properties=properties, token_cache=token_cache,
        query=("language=en", "limit=-1", "isDocument=true"),
    )
    items = payload.get("items")
    if not isinstance(items, list):
        raise AdaptivePublishExecutorError("Adaptive Search final entity readiness response is invalid.")
    ready = {
        item.get("entityName") for item in items
        if isinstance(item, Mapping) and item.get("isEnabled") is True
    }
    return [name for name in REQUIRED_ENTITIES if name in ready]


@contextmanager
def _status_lock(work: Path) -> Iterator[None]:
    """Keep concurrent controllers from issuing competing status discovery reads."""
    lock_path = work / ".publish-status.lock"
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        if hasattr(os, "O_NONBLOCK"):
            # fcntl is unavailable on non-POSIX platforms; this repository's
            # production runtime is POSIX, and a plain lock is safer than a
            # second status controller there.
            import fcntl
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise AdaptivePublishExecutorError("Adaptive Search status monitoring is already active for this operation.") from exc
        yield
    finally:
        try:
            import fcntl
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        except (ImportError, OSError):
            pass
        os.close(descriptor)


def status(
    operation_record: Path, *, project_root: Path, properties: Path,
    token_cache: str | None = None, runner: CommandRunner = _run,
    explicit_load_status: bool = False, data_loader_result: Mapping[str, Any] | None = None,
    _initialization: bool = False,
) -> dict[str, Any]:
    """Perform one GET-only status tick for exactly one persisted operation."""
    if not project_root.is_dir():
        raise AdaptivePublishExecutorError("The approved project workspace does not exist.")
    load_markdown = ""
    try:
        operation_record.resolve().relative_to(project_root.resolve())
    except ValueError as exc:
        raise AdaptivePublishExecutorError("Operation receipt is outside the selected project.") from exc
    work = operation_record.parent
    with _status_lock(work):
        operation = _read_json(operation_record, "persisted Adaptive Search operation")
        _properties_match_target(properties, operation)
        try:
            status_request = None if _initialization else build_status_request(_public_submission_from_operation(operation))
            # Validate before any GET.  A caller cannot repoint a persisted
            # operation record through a generic status route.
            if _initialization:
                validate_initialization_operation(operation)
            else:
                validate_status_request(status_request, operation=operation)
        except AdaptivePublishOperationError as exc:
            raise AdaptivePublishExecutorError(str(exc)) from exc
        evaluate = evaluate_initialization_status if _initialization else evaluate_status
        loader = _mapping(operation.get("internal_data_loader"), "private Data Loader correlation")
        request_id = _text(loader.get("request_id"), "private Data Loader request ID")
        if not re.fullmatch(r"[1-9][0-9]*", request_id) or not re.fullmatch(r"UCMFA[0-9]+", str(loader.get("content_id", ""))):
            raise AdaptivePublishExecutorError("Persisted Data Loader correlation is malformed.")
        binding = {"request_id": request_id, "publish_operation_id": operation["publish_operation_id"],
                   "project_id": operation["project_id"], "target": operation["target"]}
        verified = operation.get("verified_data_loader")
        if verified is not None and (not isinstance(verified, Mapping)
                or any(verified.get(key) != value for key, value in binding.items())
                or verified.get("status") != "SUCCEEDED"):
            raise AdaptivePublishExecutorError("Stored load-success evidence is not bound to this operation.")
        if explicit_load_status:
            if data_loader_result is None:
                handoff = {"handoff_version": DATA_LOADER_HANDOFF_VERSION,
                    "handoff_id": "dls_" + uuid.uuid4().hex, "kind": "data_load_status",
                    "request_id": request_id, "target": operation["target"],
                    "diagnostic_output_directory": str(work / "data-loader-diagnostics"),
                    "authentication_reference": {"properties": str(properties),
                        **({"token_cache": token_cache} if token_cache else {})}}
                operation["data_loader_status_handoff"] = {
                    key: value for key, value in handoff.items() if key != "authentication_reference"}
                _write_json(operation_record, operation)
                return {"state": "HANDOFF_REQUIRED", "terminal": False,
                    "publish_operation_id": operation["publish_operation_id"],
                    "core_data_loader_handoff": handoff}
            from cpq_settings_write_executor import (
                CpqSettingsWriteExecutorError, validate_data_loader_status_result)
            handoff = _mapping(operation.get("data_loader_status_handoff"), "Data Loader status handoff")
            try:
                checked = validate_data_loader_status_result(data_loader_result, handoff)
            except CpqSettingsWriteExecutorError as exc:
                raise AdaptivePublishExecutorError(str(exc)) from exc
            loader_state, load_markdown = checked["status"], checked["markdown"]
            if loader_state != "SUCCEEDED":
                if loader_state == "INDETERMINATE":
                    result = _indeterminate_status(operation, stage="data_loader_status",
                        message="Load status is unavailable or unknown; no automatic retry or publish was attempted.")
                else:
                    result = evaluate(operation, data_loader_status={"status": loader_state},
                                             status_request=status_request)
                result["monitoring"] = {"stage": "data_loader", "terminal": bool(result.get("terminal"))}
                result["next_action"] = ("Check the Adaptive Search load status and continue."
                    if loader_state == "PENDING" else
                    "Inspect the exact submitted load and its diagnostics; no automatic retry or ESS was attempted.")
                operation["monitoring"] = {"state": "WAITING_FOR_USER_STATUS",
                                          "last_status": result["state"], "checkpointed_at": _utc_now()}
                _write_json(operation_record, operation)
                return {**result, **({"data_loader_markdown": load_markdown} if load_markdown else {})}
            operation["verified_data_loader"] = {**binding, "status": "SUCCEEDED", "verified_at": _utc_now()}
            _write_json(operation_record, operation)
        elif verified is None:
            result = evaluate(operation, data_loader_status={"status": "PENDING"}, status_request=status_request)
            result["monitoring"] = {"stage": "data_loader", "terminal": False}
            result["next_action"] = "Check the Adaptive Search load status and continue."
            return {**result, **({"data_loader_markdown": load_markdown} if load_markdown else {})}
        try:
            job_id = _persisted_adaptive_search_job_id(operation)
        except AdaptivePublishExecutorError:
            result = _indeterminate_status(
                operation,
                stage="adaptive_search_job_correlation",
                message="The persisted Adaptive Search job correlation is invalid; no ESS request was submitted.",
            )
            operation["monitoring"] = {
                "state": "TERMINAL",
                "last_status": result["state"],
                "checkpointed_at": _utc_now(),
            }
            _write_json(operation_record, operation)
            return {**result, **({"data_loader_markdown": load_markdown} if load_markdown else {})}
        if job_id is None:
            try:
                discovery = _run_rest_json(
                    runner,
                    "/crmRestApi/searchResources/latest/publishStatus",
                    work / "publish-status-discovery.json",
                    properties=properties,
                    token_cache=token_cache,
                )
                _validated_publish_status(discovery)
                job_id = _adaptive_search_job_id_from_publish_status(discovery)
                baseline_job_id = _pre_submission_publish_job_id(operation)
            except AdaptivePublishReadError as exc:
                result = _with_read_error(_retry_status(
                    operation,
                    stage="adaptive_search_job_discovery",
                    message="Adaptive Search publish job discovery could not be read; retry the same GET-only status check.",
                ), exc)
                operation["monitoring"] = {
                    "state": "POLLING",
                    "last_status": result["state"],
                    "last_read_error": result["status_read_error"],
                    "checkpointed_at": _utc_now(),
                }
                _write_json(operation_record, operation)
                return {**result, **({"data_loader_markdown": load_markdown} if load_markdown else {})}
            except AdaptivePublishExecutorError:
                result = _indeterminate_status(
                    operation,
                    stage="adaptive_search_job_discovery",
                    message="Adaptive Search job discovery returned an unsafe response; no ESS request was submitted.",
                )
                operation["monitoring"] = {
                    "state": "TERMINAL",
                    "last_status": result["state"],
                    "checkpointed_at": _utc_now(),
                }
                _write_json(operation_record, operation)
                return {**result, **({"data_loader_markdown": load_markdown} if load_markdown else {})}
            if job_id is None:
                result = _retry_status(
                    operation,
                    stage="adaptive_search_job_discovery",
                    message="Adaptive Search has not returned a publish job ID yet; retry the same GET-only status check.",
                )
                operation["monitoring"] = {
                    "state": "POLLING",
                    "last_status": result["state"],
                    "checkpointed_at": _utc_now(),
                }
                _write_json(operation_record, operation)
                return {**result, **({"data_loader_markdown": load_markdown} if load_markdown else {})}
            if baseline_job_id == job_id:
                result = _retry_status(
                    operation,
                    stage="adaptive_search_job_discovery",
                    message="Adaptive Search still reports the pre-submission publish job; retry the same GET-only status check.",
                )
                operation["monitoring"] = {
                    "state": "POLLING",
                    "last_status": result["state"],
                    "checkpointed_at": _utc_now(),
                }
                _write_json(operation_record, operation)
                return {**result, **({"data_loader_markdown": load_markdown} if load_markdown else {})}
            operation["adaptive_search_job_id"] = job_id
            operation["adaptive_search_job_correlation"] = "post_data_loader_publish_status_discovery"
            operation.setdefault("monitoring", {}).pop("last_read_error", None)
            result = evaluate(
                operation,
                data_loader_status={"status": "SUCCEEDED"},
                status_request=status_request,
            )
            result["monitoring"] = {"stage": "adaptive_search_job_discovery", "terminal": False}
            operation["monitoring"] = {
                "state": "POLLING_ADAPTIVE_SEARCH_JOB",
                "adaptive_search_job_id": job_id,
                "last_status": result["state"],
                "checkpointed_at": _utc_now(),
            }
            _write_json(operation_record, operation)
            return {**result, **({"data_loader_markdown": load_markdown} if load_markdown else {})}

        # The initial status discovery above is deliberately nonterminal.  A
        # later tick must use the saved job ID and receive an echoed exact-job
        # response before entity readiness or ESS eligibility is evaluated.
        try:
            publish = _run_rest_json(
                runner, "/crmRestApi/searchResources/latest/publishStatus", work / "publish-status.json",
                properties=properties, token_cache=token_cache, query=(f"jobId={job_id}",),
            )
        except AdaptivePublishReadError as exc:
            result = _with_read_error(_retry_status(
                operation,
                stage="adaptive_search",
                message="Adaptive Search status could not be read; retry the same GET-only status check.",
            ), exc)
            operation["monitoring"] = {
                "state": "POLLING", "last_status": result["state"],
                "last_read_error": result["status_read_error"], "checkpointed_at": _utc_now()}
            _write_json(operation_record, operation)
            return {**result, **({"data_loader_markdown": load_markdown} if load_markdown else {})}
        except AdaptivePublishExecutorError:
            read_error = {
                "failure_stage": "adaptive_search_status_readback",
                "failure_class": "unusable_status_response",
                "observed_at": _utc_now(),
            }
            result = _retry_status(
                operation,
                stage="adaptive_search",
                message="Adaptive Search status could not be read; retry the same GET-only status check.",
            )
            result["status_read_error"] = read_error
            operation["monitoring"] = {
                "state": "POLLING",
                "last_status": result["state"],
                "last_read_error": read_error,
                "checkpointed_at": _utc_now(),
            }
            _write_json(operation_record, operation)
            return {**result, **({"data_loader_markdown": load_markdown} if load_markdown else {})}
        operation.setdefault("monitoring", {}).pop("last_read_error", None)
        raw_candidate = publish.get("jobId")
        candidate = (
            str(raw_candidate).strip()
            if isinstance(raw_candidate, (str, int)) and not isinstance(raw_candidate, bool)
            else None
        )
        if candidate != job_id:
            result = _indeterminate_status(
                operation,
                stage="adaptive_search",
                message="Adaptive Search status did not return the exact pinned job ID; no ESS request was submitted.",
            )
            operation["monitoring"] = {
                "state": "TERMINAL",
                "last_status": result["state"],
                "checkpointed_at": _utc_now(),
            }
            _write_json(operation_record, operation)
            return {**result, **({"data_loader_markdown": load_markdown} if load_markdown else {})}
        if isinstance(publish.get("status"), str) and publish["status"].strip().upper() == "SUCCEEDED":
            try:
                if _initialization:
                    _validate_entities(runner, work=work, properties=properties, token_cache=token_cache)
                    publish["entities_ready"] = list(REQUIRED_ENTITIES)
                else:
                    publish["entities_ready"] = _entity_readiness(
                        runner, work=work, properties=properties, token_cache=token_cache)
            except AdaptivePublishReadError as exc:
                result = _with_read_error({
                    "schema_version": "1.0", "publish_operation_id": operation["publish_operation_id"],
                    "project_id": operation["project_id"], "target": operation["target"],
                    "entities": operation["entities"], "publish_type": operation["publish_type"],
                    "eligible_for_ess": False, "state": "BLOCKED", "terminal": True,
                    "message": "Adaptive Search publish succeeded but final entity readiness could not be verified.",
                    "monitoring": {"stage": "adaptive_search", "terminal": True},
                }, exc)
                operation["monitoring"] = {
                    "state": "TERMINAL", "last_status": result["state"], "checkpointed_at": _utc_now()}
                _write_json(operation_record, operation)
                return {**result, **({"data_loader_markdown": load_markdown} if load_markdown else {})}
            except AdaptivePublishExecutorError:
                result = {
                    "schema_version": "1.0", "publish_operation_id": operation["publish_operation_id"],
                    "project_id": operation["project_id"], "target": operation["target"], "entities": operation["entities"], "publish_type": operation["publish_type"],
                    "eligible_for_ess": False, "state": "BLOCKED", "terminal": True,
                    "message": "Adaptive Search publish succeeded but final entity readiness could not be verified.",
                    "monitoring": {"stage": "adaptive_search", "terminal": True},
                }
                operation["monitoring"] = {
                    "state": "TERMINAL",
                    "last_status": result["state"],
                    "checkpointed_at": _utc_now(),
                }
                _write_json(operation_record, operation)
                return {**result, **({"data_loader_markdown": load_markdown} if load_markdown else {})}
        try:
            result = evaluate(
                operation,
                data_loader_status={"status": "SUCCEEDED"},
                publish_status=publish,
                status_request=status_request,
            )
        except AdaptivePublishOperationError:
            result = _indeterminate_status(
                operation,
                stage="adaptive_search",
                message="Adaptive Search status response was incompatible with the exact operation; no ESS request was submitted.",
            )
        result["monitoring"] = {"stage": "adaptive_search", "terminal": bool(result.get("terminal"))}
        if _initialization and result.get("state") == "SUCCEEDED":
            operation["initialization_verified"] = {
                "publish_operation_id": operation["publish_operation_id"], "project_id": operation["project_id"],
                "target": operation["target"], "job_id": job_id, "entities": list(REQUIRED_ENTITIES)}
        operation["monitoring"] = {"state": "TERMINAL" if result["monitoring"]["terminal"] else "POLLING", "last_status": result.get("state"), "checkpointed_at": _utc_now()}
        _write_json(operation_record, operation)
        return {**result, **({"data_loader_markdown": load_markdown} if load_markdown else {})}


def initialization_status(operation_record, *, project_root, properties, token_cache=None,
                          runner=_run, explicit_load_status=False, data_loader_result=None):
    result = status(operation_record, project_root=project_root, properties=properties,
                    token_cache=token_cache, runner=runner, explicit_load_status=explicit_load_status,
                    data_loader_result=data_loader_result,
                    _initialization=True)
    result["eligible_for_ess"] = False
    if not result.get("terminal"):
        result["next_action"] = "Check the Full Publish initialization status and continue."
    return result


def _read_input(path: str, name: str) -> dict[str, Any]:
    return _read_json(Path(path), name)


def _public_cli_result(result: Mapping[str, Any]) -> dict[str, Any]:
    """Remove machine-only artifact paths from every CLI-visible child result."""

    if "preparation" in result:
        return {"preparation": _mapping(result.get("preparation"), "preparation")}
    if "approval_required" in result:
        return {"approval_required": _mapping(result.get("approval_required"), "approval_required")}
    if "submission" in result:
        public: dict[str, Any] = {"submission": _mapping(result.get("submission"), "submission")}
        if result.get("reused") is True:
            public["reused"] = True
        return public
    if "status" in result:
        return {"status": _mapping(result.get("status"), "status")}
    raise AdaptivePublishExecutorError("Adaptive Search executor produced an unsupported result shape.")



def _prepared_publish_binding(preparation_path, project_root, workflow_id):
    from cpq_settings_write_executor import _artifact_inside, load_persisted_load
    preparation_path = _artifact_inside(preparation_path, project_root)
    preparation = _read_json(preparation_path, "companion preparation")
    request = preparation["request"]
    (validate_initialization_request if preparation["initialization"] else validate_companion_request)(request)
    if preparation["workflow_fingerprint"] != workflow_id or request["project_id"] != project_root.name:
        raise AdaptivePublishExecutorError("The preparation does not belong to this exact workflow/project.")
    load_path = _artifact_inside(preparation["prepared_load_record"], project_root)
    if load_path.parent != preparation_path.parent:
        raise AdaptivePublishExecutorError("Companion preparation and load artifacts are not colocated.")
    load = load_persisted_load(load_path, project_root=project_root, workflow_id=workflow_id, target=request["target"])
    row = ({**PUBLISH_LOADER_FIELDS, **build_publish_data_loader_source(
        {"entities": list(INITIALIZATION_ENTITIES)}, entities_metadata_type="string"), "publishType": ""}
        if preparation["initialization"] else build_companion_loader_row(REQUIRED_ENTITIES))
    if load["scope"] != {"business_object": "publish", "row": row}:
        raise AdaptivePublishExecutorError("The prepared load does not match the exact Full/Partial publish scope.")
    return preparation, load_path, load


def _complete_prepared_publish(preparation_path, preparation, correlation):
    public, private = (create_initialization_submission if preparation["initialization"] else create_companion_submission)(
        preparation["request"], internal_data_loader=correlation, workflow_fingerprint=preparation["workflow_fingerprint"])
    private.update({"baseline_publish_status": preparation["baseline_publish_status"],
        "pre_submission_publish_status": preparation["baseline_publish_status"],
        "monitoring": {"state": "SUBMITTED"}, "submitted_at": _utc_now()})
    operation_path = preparation_path.parent / "operation.json"
    _write_json(operation_path, private)
    return {"submission": public, "operation_record": str(operation_path)}


def recover_prepared_publish(preparation_path, *, project_root, workflow_id):
    preparation_path = Path(preparation_path)
    preparation, _, load = _prepared_publish_binding(preparation_path, project_root, workflow_id)
    if load["state"] == "submitted":
        operation_path = preparation_path.parent / "operation.json"
        if not operation_path.exists():
            return _complete_prepared_publish(preparation_path, preparation, load["submission"])
    return None


def submit_prepared_publish(preparation_path, *, project_root, workflow_id, properties,
                            explicit_approval, preview_sha256, before_submit,
                            token_cache=None, runner=_run):
    from cpq_settings_write_executor import submit_persisted_load
    preparation_path = Path(preparation_path)
    preparation, load_path, load = _prepared_publish_binding(preparation_path, project_root, workflow_id)
    _properties_match_target(properties, preparation["request"])
    current = _safe_baseline_publish_status(runner, work=preparation_path.parent,
        properties=properties, token_cache=token_cache)
    if current != preparation["baseline_publish_status"]:
        raise AdaptivePublishExecutorError("Publish concurrency changed; obtain fresh validation and approval.")
    result = submit_persisted_load(load_path, project_root=project_root, workflow_id=workflow_id,
        target=preparation["request"]["target"], explicit_approval=explicit_approval,
        preview_sha256=preview_sha256, before_submit=before_submit,
        properties=properties, token_cache=token_cache)
    return result


def complete_prepared_publish(preparation_path, core_result, *, project_root, workflow_id):
    from cpq_settings_write_executor import complete_persisted_load
    preparation_path = Path(preparation_path)
    preparation, load_path, _ = _prepared_publish_binding(preparation_path, project_root, workflow_id)
    result = complete_persisted_load(load_path, core_result, project_root=project_root,
        workflow_id=workflow_id, target=preparation["request"]["target"])
    return {**_complete_prepared_publish(preparation_path, preparation,
        {"content_id": result["content_id"], "request_id": result["request_id"]}),
        "markdown": result["markdown"]}

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-request")
    parser.add_argument("--request")
    parser.add_argument("--preview-submit", action="store_true")
    parser.add_argument("--approve-publish", action="store_true")
    parser.add_argument("--approval-preview-sha256")
    parser.add_argument("--predecessor-result")
    parser.add_argument("--prepared-record", type=Path)
    parser.add_argument("--resume-operation-record", type=Path)
    parser.add_argument("--check-load-status", action="store_true",
                        help="Use only for a user's explicit Data Loader status request.")
    parser.add_argument("--data-loader-result", type=Path,
                        help="Structured status returned by this operation's Core handoff.")
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--properties", type=Path, default=REPO_ROOT / "core" / "auth" / "fusionEnv.properties")
    parser.add_argument("--token-cache")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--internal-output",
        type=Path,
        help="Machine-only descriptor for the selected parent controller; never display this result to a consultant.",
    )
    args = parser.parse_args(argv)
    try:
        if args.check_load_status and not args.resume_operation_record:
            raise AdaptivePublishExecutorError("--check-load-status requires the exact persisted operation record.")
        if args.prepare_request:
            if any((args.request, args.predecessor_result, args.prepared_record, args.resume_operation_record, args.preview_submit, args.approve_publish, args.approval_preview_sha256)):
                raise AdaptivePublishExecutorError("Preparation accepts no execution or status inputs.")
            result = prepare(
                _read_input(args.prepare_request, "preparation request"), project_root=args.project_root,
                properties=args.properties, token_cache=args.token_cache,
            )
        elif args.resume_operation_record:
            if any((args.request, args.predecessor_result, args.prepared_record, args.preview_submit, args.approve_publish, args.approval_preview_sha256)):
                raise AdaptivePublishExecutorError("Status accepts only a persisted operation record.")
            result = {"status": status(args.resume_operation_record, project_root=args.project_root, properties=args.properties, token_cache=args.token_cache,
                                      explicit_load_status=args.check_load_status,
                                      data_loader_result=_read_json(args.data_loader_result, "Data Loader status result")
                                          if args.data_loader_result else None)}
        else:
            if not args.request or not args.predecessor_result or args.prepared_record is None:
                raise AdaptivePublishExecutorError("Submission requires request, CPQ predecessor result, and prepared record.")
            if args.preview_submit == args.approve_publish:
                raise AdaptivePublishExecutorError("Select exactly one of --preview-submit or --approve-publish.")
            result = submit(
                _read_input(args.request, "companion request"), _read_input(args.predecessor_result, "CPQ predecessor result"),
                project_root=args.project_root, properties=args.properties, prepared_record=args.prepared_record,
                token_cache=args.token_cache, preview_only=args.preview_submit,
                explicit_approval=args.approve_publish,
                approval_preview_sha256=args.approval_preview_sha256,
            )
        if args.internal_output:
            _write_json(args.internal_output, result)
        public_result = _public_cli_result(result)
        if args.output:
            _write_json(args.output, public_result)
        else:
            print(json.dumps(public_result, sort_keys=True))
        return 0
    except (AdaptivePublishExecutorError, AdaptivePublishOperationError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
