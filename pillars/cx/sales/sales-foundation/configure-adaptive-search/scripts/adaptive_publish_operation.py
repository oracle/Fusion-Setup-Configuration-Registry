#!/usr/bin/env python3
"""Public contract normalizer for an Adaptive Search partial-publish operation.

This module intentionally has no Fusion, Data Loader, or polling client.  The
Configure Adaptive Search execution route calls the real adapters and gives
their redacted results to this module.  The module then:

* exposes an immutable-source preparation suitable for one parent approval;
* creates an opaque publish-operation identifier after one Data Loader submit;
* validates every status request against that exact operation identity; and
* converts adapter results into a small, stable public state vocabulary.

Data Loader content and request identifiers are retained only in the private
operation record.  They must never cross the Fusion ABO companion boundary.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit


SCHEMA_VERSION = "1.0"
WORKFLOW_AUTHORIZATION_SCOPE = "fusion_abo_adaptive_search_v1"
REQUIRED_ENTITIES = ("ConsolidatedAsset", "SerializedAsset")
INITIALIZATION_ENTITIES = ("Account", "Contact", "Lead", "Opportunity", "Revenue",
                           "Activity", "Asset", "Product", "CRMProductGroup")
INITIALIZATION_ID = re.compile(r"^afi_[a-f0-9]{32}$")
PUBLISH_SOURCE_ENTITIES_METADATA_TYPE = "string"

OPAQUE_OPERATION_ID = re.compile(r"^apo_[a-f0-9]{32}$")
OPAQUE_PREPARATION_ID = re.compile(r"^app_[a-f0-9]{32}$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")

SUCCESSFUL_DATA_LOADER_STATES = frozenset({"ORA_SUCCESS", "SUCCESS", "SUCCEEDED"})
FAILED_DATA_LOADER_STATES = frozenset(
    {"ORA_ERROR", "ERROR", "FAILED", "CANCELLED", "CANCELED"}
)
PENDING_DATA_LOADER_STATES = frozenset(
    {
        "WAIT",
        "WAITING",
        "PENDING",
        "QUEUED",
        "RUNNING",
        "IN_PROGRESS",
        "SUBMITTED",
        "ORA_WAIT",
        "ORA_PENDING",
        "ORA_RUNNING",
        "ORA_IN_PROGRESS",
    }
)
PENDING_PUBLISH_STATES = frozenset({"WAIT", "WAITING", "READY", "PENDING", "QUEUED", "SUBMITTED"})
RUNNING_PUBLISH_STATES = frozenset({"RUNNING", "PAUSED", "IN_PROGRESS"})
FAILED_PUBLISH_STATES = frozenset({"ERROR", "FAILED"})
TIMED_OUT_PUBLISH_STATES = frozenset({"TIMEOUT", "TIMED_OUT"})

NORMALIZED_STATES = frozenset(
    {
        "PREPARED",
        "SUBMITTED",
        "DATA_LOADER_PENDING",
        "DATA_LOADER_FAILED",
        "PUBLISH_PENDING",
        "PUBLISH_RUNNING",
        "SUCCEEDED",
        "PUBLISH_FAILED",
        "CANCELLED",
        "TIMED_OUT",
        "BLOCKED",
        "INDETERMINATE",
    }
)


class AdaptivePublishOperationError(ValueError):
    """Raised when a companion request cannot be proven safe and compatible."""


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AdaptivePublishOperationError(f"{name} must be an object.")
    return value


def _strict_mapping(
    value: Any,
    name: str,
    *,
    required: frozenset[str],
    allowed: frozenset[str] | None = None,
) -> Mapping[str, Any]:
    raw = _mapping(value, name)
    keys = set(raw)
    missing = required - keys
    if missing:
        raise AdaptivePublishOperationError(
            f"{name} is missing required field(s): {', '.join(sorted(missing))}."
        )
    if allowed is not None:
        unexpected = keys - allowed
        if unexpected:
            raise AdaptivePublishOperationError(
                f"{name} contains unsupported field(s): {', '.join(sorted(map(str, unexpected)))}."
            )
    return raw


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AdaptivePublishOperationError(f"{name} must be a nonblank string.")
    return value.strip()


def _sha256(value: Any, name: str) -> str:
    digest = _text(value, name).casefold()
    if not SHA256.fullmatch(digest):
        raise AdaptivePublishOperationError(f"{name} must be a SHA-256 hex digest.")
    return digest


def _timestamp(value: Any, name: str) -> str:
    timestamp = _text(value, name)
    try:
        parsed = datetime.fromisoformat(
            timestamp[:-1] + "+00:00" if timestamp.endswith("Z") else timestamp
        )
    except ValueError as exc:
        raise AdaptivePublishOperationError(f"{name} must be an RFC 3339 timestamp.") from exc
    if parsed.tzinfo is None:
        raise AdaptivePublishOperationError(f"{name} must include a UTC offset.")
    return timestamp


def _target(value: Any) -> dict[str, str]:
    raw = _strict_mapping(
        value,
        "target",
        required=frozenset({"environment", "fusion_host"}),
        allowed=frozenset({"environment", "fusion_host"}),
    )
    host = _text(raw.get("fusion_host"), "target.fusion_host")
    parsed = urlsplit(host)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
    ):
        raise AdaptivePublishOperationError(
            "target.fusion_host must be an HTTPS origin without credentials, path, query, or fragment."
        )
    return {
        "environment": _text(raw.get("environment"), "target.environment"),
        "fusion_host": host.rstrip("/"),
    }


def _entities(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise AdaptivePublishOperationError("entities must be a nonempty array.")
    normalized = [_text(item, "entities[]") for item in value]
    if len(set(normalized)) != len(normalized):
        raise AdaptivePublishOperationError("entities must not contain duplicates.")
    return normalized


def _publish_type(value: Any) -> str:
    publish_type = _text(value, "publish_type")
    if publish_type != "selective":
        raise AdaptivePublishOperationError("publish_type must be selective.")
    return publish_type


def _operation_id(value: Any) -> str:
    operation_id = _text(value, "publish_operation_id")
    if not OPAQUE_OPERATION_ID.fullmatch(operation_id):
        raise AdaptivePublishOperationError("publish_operation_id is invalid.")
    return operation_id


def _preparation_id(value: Any) -> str:
    preparation_id = _text(value, "preparation_id")
    if not OPAQUE_PREPARATION_ID.fullmatch(preparation_id):
        raise AdaptivePublishOperationError("preparation_id is invalid.")
    return preparation_id


def _identity(
    value: Mapping[str, Any],
    *,
    name: str,
    operation: str,
    require_preparation_id: bool = False,
) -> dict[str, Any]:
    required = {
        "schema_version",
        "operation",
        "project_id",
        "target",
        "entities",
        "publish_type",
    }
    if require_preparation_id:
        required.add("preparation_id")
    allowed = set(required)
    if operation == "submit_partial_publish":
        allowed.add("workflow_authorization")
    raw = _strict_mapping(
        value,
        name,
        required=frozenset(required),
        allowed=frozenset(allowed),
    )
    if _text(raw.get("schema_version"), f"{name}.schema_version") != SCHEMA_VERSION:
        raise AdaptivePublishOperationError("Unsupported schema_version.")
    if _text(raw.get("operation"), f"{name}.operation") != operation:
        raise AdaptivePublishOperationError(f"operation must be {operation}.")
    identity: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "project_id": _text(raw.get("project_id"), f"{name}.project_id"),
        "target": _target(raw.get("target")),
        "entities": _entities(raw.get("entities")),
        "publish_type": _publish_type(raw.get("publish_type")),
    }
    if require_preparation_id:
        identity["preparation_id"] = _preparation_id(raw.get("preparation_id"))
    return identity


def _identity_matches(
    expected: Mapping[str, Any],
    actual: Mapping[str, Any],
    *,
    name: str,
    include_preparation: bool = False,
) -> None:
    keys = ("project_id", "target", "entities", "publish_type")
    if include_preparation:
        keys += ("preparation_id",)
    for key in keys:
        if actual.get(key) != expected.get(key):
            raise AdaptivePublishOperationError(
                f"{name} does not match the exact prepared operation identity ({key})."
            )


def _immutable_source(value: Any, name: str) -> dict[str, str]:
    raw = _strict_mapping(
        value,
        name,
        required=frozenset({"archive_sha256", "source_sha256"}),
        allowed=frozenset({"archive_sha256", "source_sha256"}),
    )
    return {
        "archive_sha256": _sha256(raw.get("archive_sha256"), f"{name}.archive_sha256"),
        "source_sha256": _sha256(raw.get("source_sha256"), f"{name}.source_sha256"),
    }


def _prepared_source(value: Any) -> tuple[dict[str, str], dict[str, Any]]:
    raw = _strict_mapping(
        value,
        "internal_prepared_source",
        required=frozenset({"archive_sha256", "source_sha256"}),
        allowed=frozenset(
            {"archive_sha256", "source_sha256", "prepared_record_path", "task_validation_ref"}
        ),
    )
    source = {
        "archive_sha256": _sha256(
            raw.get("archive_sha256"), "internal_prepared_source.archive_sha256"
        ),
        "source_sha256": _sha256(
            raw.get("source_sha256"), "internal_prepared_source.source_sha256"
        ),
    }
    private: dict[str, Any] = dict(source)
    for key in ("prepared_record_path", "task_validation_ref"):
        if raw.get(key) is not None:
            private[key] = _text(raw.get(key), f"internal_prepared_source.{key}")
    return source, private


def _workflow_authorization(
    value: Any,
    *,
    identity: Mapping[str, Any],
    immutable_source: Mapping[str, str],
) -> dict[str, Any]:
    raw = _strict_mapping(
        value,
        "workflow_authorization",
        required=frozenset(
            {
                "scope",
                "approval_fingerprint",
                "project_id",
                "target",
                "entities",
                "publish_type",
                "archive_sha256",
                "source_sha256",
                "issued_at",
                "expires_at",
                "submission_limit",
                "approval_record_ref",
                "approval_record_fingerprint",
            }
        ),
        allowed=frozenset(
            {
                "scope",
                "approval_fingerprint",
                "project_id",
                "target",
                "entities",
                "publish_type",
                "archive_sha256",
                "source_sha256",
                "issued_at",
                "expires_at",
                "submission_limit",
                "approval_record_ref",
                "approval_record_fingerprint",
            }
        ),
    )
    if _text(raw.get("scope"), "workflow_authorization.scope") != WORKFLOW_AUTHORIZATION_SCOPE:
        raise AdaptivePublishOperationError(
            "workflow_authorization.scope does not authorize the Fusion ABO companion operation."
        )
    authorization_identity = {
        "project_id": _text(
            raw.get("project_id"), "workflow_authorization.project_id"
        ),
        "target": _target(raw.get("target")),
        "entities": _entities(raw.get("entities")),
        "publish_type": _publish_type(raw.get("publish_type")),
    }
    _identity_matches(identity, authorization_identity, name="workflow_authorization")
    source = {
        "archive_sha256": _sha256(
            raw.get("archive_sha256"), "workflow_authorization.archive_sha256"
        ),
        "source_sha256": _sha256(
            raw.get("source_sha256"), "workflow_authorization.source_sha256"
        ),
    }
    if source != dict(immutable_source):
        raise AdaptivePublishOperationError(
            "workflow_authorization does not bind the exact immutable prepared source."
        )
    issued_at = _timestamp(raw.get("issued_at"), "workflow_authorization.issued_at")
    expires_at = _timestamp(raw.get("expires_at"), "workflow_authorization.expires_at")
    try:
        issued = datetime.fromisoformat(
            issued_at[:-1] + "+00:00" if issued_at.endswith("Z") else issued_at
        )
        expires = datetime.fromisoformat(
            expires_at[:-1] + "+00:00" if expires_at.endswith("Z") else expires_at
        )
    except ValueError as exc:  # Already checked above; keeps type checkers happy.
        raise AdaptivePublishOperationError("workflow_authorization timestamps are invalid.") from exc
    if expires <= issued:
        raise AdaptivePublishOperationError(
            "workflow_authorization.expires_at must be later than issued_at."
        )
    submission_limit = raw.get("submission_limit")
    if (
        isinstance(submission_limit, bool)
        or not isinstance(submission_limit, int)
        or submission_limit != 1
    ):
        raise AdaptivePublishOperationError(
            "workflow_authorization.submission_limit must be exactly 1."
        )
    return {
        "scope": WORKFLOW_AUTHORIZATION_SCOPE,
        "approval_fingerprint": _sha256(
            raw.get("approval_fingerprint"),
            "workflow_authorization.approval_fingerprint",
        ),
        **authorization_identity,
        **source,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "submission_limit": 1,
        "approval_record_ref": _text(
            raw.get("approval_record_ref"),
            "workflow_authorization.approval_record_ref",
        ),
        "approval_record_fingerprint": _sha256(
            raw.get("approval_record_fingerprint"),
            "workflow_authorization.approval_record_fingerprint",
        ),
    }


def _private_preparation(value: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    raw = _strict_mapping(
        value,
        "prepared_operation",
        required=frozenset(
            {
                "schema_version",
                "preparation_id",
                "state",
                "project_id",
                "target",
                "entities",
                "publish_type",
                "immutable_source",
                "internal_prepared_source",
            }
        ),
        allowed=frozenset(
            {
                "schema_version",
                "preparation_id",
                "state",
                "project_id",
                "target",
                "entities",
                "publish_type",
                "immutable_source",
                "internal_prepared_source",
                "prepare_operation",
                "submission_operation",
            }
        ),
    )
    if _text(raw.get("schema_version"), "prepared_operation.schema_version") != SCHEMA_VERSION:
        raise AdaptivePublishOperationError("prepared_operation has an unsupported schema_version.")
    if _preparation_id(raw.get("preparation_id")) != raw.get("preparation_id"):
        raise AdaptivePublishOperationError("prepared_operation.preparation_id is invalid.")
    if _text(raw.get("state"), "prepared_operation.state") != "PREPARED":
        raise AdaptivePublishOperationError("prepared_operation must be in PREPARED state.")
    identity = {
        "project_id": _text(raw.get("project_id"), "prepared_operation.project_id"),
        "target": _target(raw.get("target")),
        "entities": _entities(raw.get("entities")),
        "publish_type": _publish_type(raw.get("publish_type")),
        "preparation_id": _preparation_id(raw.get("preparation_id")),
    }
    immutable_source = _immutable_source(
        raw.get("immutable_source"), "prepared_operation.immutable_source"
    )
    private_source, _ = _prepared_source(raw.get("internal_prepared_source"))
    if private_source != immutable_source:
        raise AdaptivePublishOperationError(
            "prepared_operation immutable source does not match its private prepared source."
        )
    return identity, immutable_source


def _internal_data_loader(value: Mapping[str, Any]) -> dict[str, str]:
    raw = _strict_mapping(
        value,
        "internal_data_loader",
        required=frozenset({"request_id", "content_id"}),
        allowed=frozenset({"request_id", "content_id"}),
    )
    return {
        "request_id": _text(raw.get("request_id"), "internal_data_loader.request_id"),
        "content_id": _text(raw.get("content_id"), "internal_data_loader.content_id"),
    }


def serialize_entities_for_publish_source(
    entities: Any, *, metadata_type: str
) -> str:
    """Serialize REST entities for the registered string source field."""

    if (
        not isinstance(metadata_type, str)
        or metadata_type.strip().casefold() != PUBLISH_SOURCE_ENTITIES_METADATA_TYPE
    ):
        raise AdaptivePublishOperationError(
            "Live publish metadata does not expose entities as the required string field."
        )
    return json.dumps(_entities(entities), separators=(",", ":"), ensure_ascii=False)


def validate_publish_source_metadata(metadata: Mapping[str, Any]) -> str:
    """Extract the sole permitted entities-source type from live metadata."""

    metadata = _mapping(metadata, "publish_metadata")
    descriptor = _mapping(metadata.get("entities"), "publish_metadata.entities")
    return _text(descriptor.get("type"), "publish_metadata.entities.type")


def build_publish_data_loader_source(
    payload: Mapping[str, Any], *, entities_metadata_type: str
) -> dict[str, str]:
    """Build and self-validate the task-local immutable Data Loader source."""

    payload = _mapping(payload, "payload")
    allowed = {"entities", "publishType"}
    if set(payload) - allowed or "entities" not in payload:
        raise AdaptivePublishOperationError("Publish payload contains unsupported source fields.")
    entities = _entities(payload.get("entities"))
    source = {
        "entities": serialize_entities_for_publish_source(
            entities, metadata_type=entities_metadata_type
        )
    }
    try:
        decoded = json.loads(source["entities"])
    except json.JSONDecodeError as exc:  # Serializer output is deterministic.
        raise AdaptivePublishOperationError(
            "Publish entities source serialization is invalid JSON."
        ) from exc
    if decoded != entities:
        raise AdaptivePublishOperationError(
            "Publish entities source serialization does not round-trip exactly."
        )
    publish_type = payload.get("publishType")
    if publish_type is not None:
        source["publishType"] = _text(publish_type, "payload.publishType")
    return source


def create_preparation(
    request: Mapping[str, Any], *, internal_prepared_source: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Create a public preparation and a private prepared-source record.

    The caller has already run read-only lookup and immutable-source creation.
    This function simply makes the source digest and exact identity available
    for the one parent approval; it never sends data to Fusion.
    """

    identity = _identity(
        request, name="request", operation="prepare_partial_publish"
    )
    immutable_source, private_source = _prepared_source(internal_prepared_source)
    preparation_id = "app_" + uuid.uuid4().hex
    public = {
        "schema_version": SCHEMA_VERSION,
        "preparation_id": preparation_id,
        "state": "PREPARED",
        "project_id": identity["project_id"],
        "target": identity["target"],
        "entities": identity["entities"],
        "publish_type": identity["publish_type"],
        "immutable_source": immutable_source,
        "submission_operation": "submit_partial_publish",
    }
    private = {
        **public,
        "prepare_operation": "prepare_partial_publish",
        "internal_prepared_source": private_source,
    }
    return public, private


def create_submission(
    request: Mapping[str, Any],
    *,
    internal_data_loader: Mapping[str, Any],
    prepared_operation: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Create public submission output and private persisted operation state.

    A standalone Adaptive Search request remains compatible with its own
    approval route.  A Fusion ABO request must include a fully bound
    workflow_authorization and the exact private preparation record.
    """

    raw_request = _mapping(request, "request")
    is_abo_companion = raw_request.get("workflow_authorization") is not None
    identity = _identity(
        raw_request,
        name="request",
        operation="submit_partial_publish",
        require_preparation_id=is_abo_companion,
    )
    loader = _internal_data_loader(internal_data_loader)
    authorization: dict[str, Any] | None = None
    immutable_source: dict[str, str] | None = None

    if is_abo_companion:
        if prepared_operation is None:
            raise AdaptivePublishOperationError(
                "Fusion ABO submission requires the exact private prepared operation."
            )
        prepared_identity, immutable_source = _private_preparation(prepared_operation)
        _identity_matches(
            prepared_identity,
            identity,
            name="submission request",
            include_preparation=True,
        )
        authorization = _workflow_authorization(
            raw_request.get("workflow_authorization"),
            identity=identity,
            immutable_source=immutable_source,
        )
    elif prepared_operation is not None:
        # A standalone caller may retain a preparation record, but it must
        # still have an identity matching its submit request.
        prepared_identity, immutable_source = _private_preparation(prepared_operation)
        _identity_matches(prepared_identity, identity, name="submission request")

    operation_id = "apo_" + uuid.uuid4().hex
    public = {
        "schema_version": SCHEMA_VERSION,
        "publish_operation_id": operation_id,
        "state": "SUBMITTED",
        "project_id": identity["project_id"],
        "target": identity["target"],
        "entities": identity["entities"],
        "publish_type": identity["publish_type"],
        "status_check_operation": "get_partial_publish_status",
    }
    private: dict[str, Any] = {
        **public,
        "internal_data_loader": loader,
    }
    if "preparation_id" in identity:
        private["preparation_id"] = identity["preparation_id"]
    if immutable_source is not None:
        private["immutable_source"] = immutable_source
    if authorization is not None:
        private["workflow_authorization"] = authorization
    return public, private


def validate_initialization_request(request: Mapping[str, Any]) -> dict[str, Any]:
    """Separate fixed Full Publish boundary; never relax the selective API."""
    required = {"schema_version", "handover_version", "operation", "project_id", "target",
                "entities", "publish_type", "initialization_id"}
    raw = _strict_mapping(request, "initialization request", required=frozenset(required),
                          allowed=frozenset(required))
    if (raw.get("schema_version") != "1.0" or raw.get("handover_version") != "2.0"
            or raw.get("operation") != "submit_initial_full_publish"
            or raw.get("publish_type") != "full" or raw.get("entities") != list(INITIALIZATION_ENTITIES)
            or not INITIALIZATION_ID.fullmatch(str(raw.get("initialization_id", "")))):
        raise AdaptivePublishOperationError("Initialization requires its own identity and exact OOTB Full Publish scope.")
    return {**dict(raw), "project_id": _text(raw["project_id"], "project_id"), "target": _target(raw["target"])}


def create_initialization_submission(request: Mapping[str, Any], *, internal_data_loader: Mapping[str, Any],
                                     workflow_fingerprint: str) -> tuple[dict[str, Any], dict[str, Any]]:
    request = validate_initialization_request(request)
    internal_data_loader = _internal_data_loader(internal_data_loader)
    content, request_id = internal_data_loader.get("content_id"), internal_data_loader.get("request_id")
    if not re.fullmatch(r"UCMFA[0-9]+", str(content)) or not re.fullmatch(r"[1-9][0-9]*", str(request_id)):
        raise AdaptivePublishOperationError("Initialization receipt has invalid private load correlation.")
    public = {"schema_version": "1.0", "publish_operation_id": request["initialization_id"],
              "state": "SUBMITTED", "project_id": request["project_id"], "target": request["target"],
              "entities": request["entities"], "publish_type": "full",
              "status_check_operation": "get_initial_full_publish_status"}
    private = {**public, "handover_version": "2.0", "purpose": "adaptive_search_initialization",
               "workflow_approval_fingerprint": _sha256(workflow_fingerprint, "workflow fingerprint"),
               "internal_data_loader": dict(internal_data_loader)}
    return public, private


def validate_initialization_operation(operation: Mapping[str, Any]) -> None:
    raw = _mapping(operation, "initialization operation")
    validate_initialization_request({"schema_version": raw.get("schema_version"),
        "handover_version": raw.get("handover_version"), "operation": "submit_initial_full_publish",
        "project_id": raw.get("project_id"), "target": raw.get("target"), "entities": raw.get("entities"),
        "publish_type": raw.get("publish_type"), "initialization_id": raw.get("publish_operation_id")})
    _sha256(raw.get("workflow_approval_fingerprint"), "workflow fingerprint")
    correlation = _internal_data_loader(raw.get("internal_data_loader"))
    if (not re.fullmatch(r"UCMFA[0-9]+", correlation["content_id"])
            or not re.fullmatch(r"[1-9][0-9]*", correlation["request_id"])):
        raise AdaptivePublishOperationError("Initialization private load correlation is invalid.")
    if (raw.get("purpose") != "adaptive_search_initialization" or raw.get("state") != "SUBMITTED"
            or raw.get("status_check_operation") != "get_initial_full_publish_status"):
        raise AdaptivePublishOperationError("Receipt is not an initial Full Publish operation.")


def evaluate_initialization_status(operation: Mapping[str, Any], *, data_loader_status: Mapping[str, Any],
                                   publish_status: Mapping[str, Any] | None = None, status_request=None) -> dict[str, Any]:
    validate_initialization_operation(operation)
    base = {key: operation[key] for key in ("schema_version", "publish_operation_id", "project_id", "target", "entities", "publish_type")}
    loader = str(data_loader_status.get("status", "")).upper()
    if loader in FAILED_DATA_LOADER_STATES:
        state, terminal = "DATA_LOADER_FAILED", True
    elif loader in PENDING_DATA_LOADER_STATES:
        state, terminal = "DATA_LOADER_PENDING", False
    elif loader not in SUCCESSFUL_DATA_LOADER_STATES:
        state, terminal = "INDETERMINATE", True
    elif publish_status is None:
        state, terminal = "PUBLISH_PENDING", False
    else:
        raw = str(publish_status.get("status", "")).upper()
        if raw in PENDING_PUBLISH_STATES:
            state, terminal = "PUBLISH_PENDING", False
        elif raw in RUNNING_PUBLISH_STATES:
            state, terminal = "PUBLISH_RUNNING", False
        elif raw == "SUCCEEDED":
            ready = publish_status.get("entities_ready") == list(REQUIRED_ENTITIES)
            state, terminal = ("SUCCEEDED" if ready and publish_status.get("jobId") else "BLOCKED"), True
        elif raw in FAILED_PUBLISH_STATES | TIMED_OUT_PUBLISH_STATES | {"CANCELLED", "CANCELED"}:
            state, terminal = "PUBLISH_FAILED", True
        else:
            state, terminal = "INDETERMINATE", True
    result = {**base, "state": state, "terminal": terminal, "eligible_for_ess": False}
    if publish_status:
        result["adaptive_search_status"] = publish_status.get("status")
        _publish_fields(publish_status, result)
    if state == "SUCCEEDED":
        result["catalog_ready"] = True
        result["final_entity_readiness"] = list(REQUIRED_ENTITIES)
    return result


def validate_companion_request(request: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the v2 companion boundary before any external preparation."""
    if request.get("handover_version") != "2.0":
        raise AdaptivePublishOperationError("A live v2 handover is required.")
    allowed = {"schema_version", "handover_version", "operation", "project_id",
               "target", "entities", "publish_type"}
    if set(request) - allowed:
        raise AdaptivePublishOperationError("Saved approval/source fields are not accepted.")
    plain = {key: value for key, value in request.items() if key != "handover_version"}
    _identity(plain, name="live request", operation="submit_partial_publish")
    if plain.get("entities") != ["ConsolidatedAsset", "SerializedAsset"]:
        raise AdaptivePublishOperationError("Only the fixed ordered ABO entity pair is allowed.")
    return plain


def create_companion_submission(request: Mapping[str, Any], *, internal_data_loader: Mapping[str, Any],
                           workflow_fingerprint: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """V2 live approval has already been consumed by Core, not by this record.

    Status identity remains v1-compatible; the private handover is versioned
    separately and never contains source hashes or a replayable approval.
    """
    plain = validate_companion_request(request)
    fingerprint = _sha256(workflow_fingerprint, "workflow fingerprint")
    public, private = create_submission(plain, internal_data_loader=internal_data_loader)
    private.update({"handover_version": "2.0", "workflow_approval_fingerprint": fingerprint})
    return public, private


def build_status_request(submission: Mapping[str, Any]) -> dict[str, Any]:
    """Build a status request that carries the operation's exact public identity."""

    raw = _strict_mapping(
        submission,
        "submission",
        required=frozenset(
            {
                "schema_version",
                "publish_operation_id",
                "state",
                "project_id",
                "target",
                "entities",
                "publish_type",
            }
        ),
        allowed=frozenset(
            {
                "schema_version",
                "publish_operation_id",
                "state",
                "project_id",
                "target",
                "entities",
                "publish_type",
                "status_check_operation",
            }
        ),
    )
    if _text(raw.get("schema_version"), "submission.schema_version") != SCHEMA_VERSION:
        raise AdaptivePublishOperationError("submission has an unsupported schema_version.")
    if _text(raw.get("state"), "submission.state") != "SUBMITTED":
        raise AdaptivePublishOperationError("submission must be in SUBMITTED state.")
    return {
        "schema_version": SCHEMA_VERSION,
        "operation": "get_partial_publish_status",
        "project_id": _text(raw.get("project_id"), "submission.project_id"),
        "target": _target(raw.get("target")),
        "entities": _entities(raw.get("entities")),
        "publish_type": _publish_type(raw.get("publish_type")),
        "publish_operation_id": _operation_id(raw.get("publish_operation_id")),
    }


def validate_status_request(
    request: Mapping[str, Any], *, operation: Mapping[str, Any]
) -> dict[str, Any]:
    """Fail closed unless a status request names the exact private operation."""

    raw = _strict_mapping(
        request,
        "status_request",
        required=frozenset(
            {
                "schema_version",
                "operation",
                "project_id",
                "target",
                "entities",
                "publish_type",
                "publish_operation_id",
            }
        ),
        allowed=frozenset(
            {
                "schema_version",
                "operation",
                "project_id",
                "target",
                "entities",
                "publish_type",
                "publish_operation_id",
            }
        ),
    )
    if _text(raw.get("schema_version"), "status_request.schema_version") != SCHEMA_VERSION:
        raise AdaptivePublishOperationError("status_request has an unsupported schema_version.")
    if _text(raw.get("operation"), "status_request.operation") != "get_partial_publish_status":
        raise AdaptivePublishOperationError(
            "status_request.operation must be get_partial_publish_status."
        )
    request_identity = {
        "project_id": _text(raw.get("project_id"), "status_request.project_id"),
        "target": _target(raw.get("target")),
        "entities": _entities(raw.get("entities")),
        "publish_type": _publish_type(raw.get("publish_type")),
    }
    operation_identity = {
        "project_id": _text(operation.get("project_id"), "operation.project_id"),
        "target": _target(operation.get("target")),
        "entities": _entities(operation.get("entities")),
        "publish_type": _publish_type(operation.get("publish_type")),
    }
    _identity_matches(operation_identity, request_identity, name="status_request")
    operation_id = _operation_id(operation.get("publish_operation_id"))
    if _operation_id(raw.get("publish_operation_id")) != operation_id:
        raise AdaptivePublishOperationError(
            "status_request does not name the exact submitted publish operation."
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "operation": "get_partial_publish_status",
        **request_identity,
        "publish_operation_id": operation_id,
    }


def _public_status_base(operation: Mapping[str, Any]) -> dict[str, Any]:
    raw = _strict_mapping(
        operation,
        "operation",
        required=frozenset(
            {
                "schema_version",
                "publish_operation_id",
                "state",
                "project_id",
                "target",
                "entities",
                "publish_type",
                "internal_data_loader",
            }
        ),
    )
    if _text(raw.get("schema_version"), "operation.schema_version") != SCHEMA_VERSION:
        raise AdaptivePublishOperationError("operation has an unsupported schema_version.")
    if _text(raw.get("state"), "operation.state") != "SUBMITTED":
        raise AdaptivePublishOperationError("operation must be in SUBMITTED state.")
    _internal_data_loader(_mapping(raw.get("internal_data_loader"), "operation.internal_data_loader"))
    return {
        "schema_version": SCHEMA_VERSION,
        "publish_operation_id": _operation_id(raw.get("publish_operation_id")),
        "project_id": _text(raw.get("project_id"), "operation.project_id"),
        "target": _target(raw.get("target")),
        "entities": _entities(raw.get("entities")),
        "publish_type": _publish_type(raw.get("publish_type")),
        "eligible_for_ess": False,
    }


def _result(base: Mapping[str, Any], state: str, *, terminal: bool) -> dict[str, Any]:
    if state not in NORMALIZED_STATES:
        raise AdaptivePublishOperationError(f"{state} is not a normalized companion state.")
    return {**base, "state": state, "terminal": terminal}


def _publish_fields(publish: Mapping[str, Any], response: dict[str, Any]) -> None:
    job_id = publish.get("jobId")
    if job_id is not None:
        if isinstance(job_id, bool) or not isinstance(job_id, (str, int)):
            raise AdaptivePublishOperationError("publish_status.jobId must be a string or integer.")
        normalized_job_id = str(job_id).strip()
        if not normalized_job_id:
            raise AdaptivePublishOperationError("publish_status.jobId must be nonblank.")
        response["adaptive_search_job_id"] = normalized_job_id
    optional_fields = {
        "mmuuid": "mmuuid",
        "publishSource": "publish_source",
    }
    for input_key, output_key in optional_fields.items():
        if publish.get(input_key) is not None:
            response[output_key] = _text(
                publish.get(input_key), f"publish_status.{input_key}"
            )


def _same_entities(expected: list[str], observed: list[str]) -> bool:
    return len(expected) == len(observed) and set(expected) == set(observed)


def evaluate_status(
    operation: Mapping[str, Any],
    *,
    data_loader_status: Mapping[str, Any],
    publish_status: Mapping[str, Any] | None = None,
    status_request: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize one status read without submitting, polling, or retrying work.

    New one-approval callers must pass status_request.  Its exact identity is
    checked before the execution route performs a Data Loader or Fusion GET.
    The optional form remains only for existing standalone compatibility.
    """

    operation = _mapping(operation, "operation")
    if status_request is not None:
        validate_status_request(status_request, operation=operation)
    base = _public_status_base(operation)
    loader = _strict_mapping(
        data_loader_status,
        "data_loader_status",
        required=frozenset({"status"}),
    )
    loader_state = _text(loader.get("status"), "data_loader_status.status").upper()
    if loader_state in FAILED_DATA_LOADER_STATES:
        return _result(base, "DATA_LOADER_FAILED", terminal=True)
    if loader_state in PENDING_DATA_LOADER_STATES:
        return _result(base, "DATA_LOADER_PENDING", terminal=False)
    if loader_state not in SUCCESSFUL_DATA_LOADER_STATES:
        return _result(base, "INDETERMINATE", terminal=True)
    if publish_status is None:
        return _result(base, "PUBLISH_PENDING", terminal=False)

    publish = _strict_mapping(
        publish_status,
        "publish_status",
        required=frozenset({"status"}),
    )
    publish_state = _text(publish.get("status"), "publish_status.status").upper()
    if publish_state in PENDING_PUBLISH_STATES:
        response = _result(base, "PUBLISH_PENDING", terminal=False)
    elif publish_state in RUNNING_PUBLISH_STATES:
        response = _result(base, "PUBLISH_RUNNING", terminal=False)
    elif publish_state == "SUCCEEDED":
        ready = _entities(publish.get("entities_ready"))
        if not _same_entities(base["entities"], ready):
            return _result(base, "BLOCKED", terminal=True)
        job_id = publish.get("jobId")
        if job_id is None or (isinstance(job_id, str) and not job_id.strip()):
            return _result(base, "INDETERMINATE", terminal=True)
        response = _result(base, "SUCCEEDED", terminal=True)
        response["eligible_for_ess"] = tuple(base["entities"]) == REQUIRED_ENTITIES
        response["final_entity_readiness"] = list(base["entities"])
    elif publish_state in {"CANCELLED", "CANCELED"}:
        response = _result(base, "CANCELLED", terminal=True)
    elif publish_state in TIMED_OUT_PUBLISH_STATES:
        response = _result(base, "TIMED_OUT", terminal=True)
    elif publish_state in FAILED_PUBLISH_STATES:
        response = _result(base, "PUBLISH_FAILED", terminal=True)
    else:
        response = _result(base, "INDETERMINATE", terminal=True)
    response["adaptive_search_status"] = publish_state
    _publish_fields(publish, response)
    return response


def _read(path: str) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        return _mapping(json.load(handle), path)  # type: ignore[arg-type]


def _write(path: str, value: Mapping[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=destination.parent, delete=False
    ) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = handle.name
    os.replace(temporary, destination)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Normalize a redacted Adaptive Search publish operation."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--request", required=True)
    prepare.add_argument("--internal-prepared-source", required=True)
    prepare.add_argument("--preparation-record", required=True)
    submit = commands.add_parser("submit")
    submit.add_argument("--request", required=True)
    submit.add_argument("--internal-data-loader-result", required=True)
    submit.add_argument("--operation-record", required=True)
    submit.add_argument("--prepared-record")
    status = commands.add_parser("status")
    status.add_argument("--operation-record", required=True)
    status.add_argument("--data-loader-status", required=True)
    status.add_argument("--publish-status")
    status.add_argument("--request")
    args = parser.parse_args(argv)

    if args.command == "prepare":
        public, private = create_preparation(
            _read(args.request),
            internal_prepared_source=_read(args.internal_prepared_source),
        )
        _write(args.preparation_record, private)
        print(json.dumps(public, sort_keys=True))
        return 0
    if args.command == "submit":
        prepared = _read(args.prepared_record) if args.prepared_record else None
        public, private = create_submission(
            _read(args.request),
            internal_data_loader=_read(args.internal_data_loader_result),
            prepared_operation=prepared,
        )
        _write(args.operation_record, private)
        print(json.dumps(public, sort_keys=True))
        return 0
    publish = _read(args.publish_status) if args.publish_status else None
    request = _read(args.request) if args.request else None
    print(
        json.dumps(
            evaluate_status(
                _read(args.operation_record),
                data_loader_status=_read(args.data_loader_status),
                publish_status=publish,
                status_request=request,
            ),
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
