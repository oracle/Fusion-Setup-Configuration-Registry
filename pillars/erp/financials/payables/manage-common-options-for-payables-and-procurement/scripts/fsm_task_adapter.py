#!/usr/bin/env python3
"""Portable, data-driven FSM task adapter runtime.

This file is copied into a generated Nested task skill.  Task semantics live in
the adjacent e2e-adapter.json descriptor and ora-resource rule plan.  The
runtime performs offline package work only; it never connects to Fusion.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree


SCHEMA_VERSION = "fscr-fsm-task-adapter-v1"
TASK_SPECIFIC_RULES_VERSION = "ap-financials-option-validation-v1"
TASK_SPECIFIC_RULES_FILE = "financials_option_extension.json"
MAX_MEMBER_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100
SUCCESS_STATUSES = frozenset({"COMPLETE", "COMPLETED", "SUCCESS", "SUCCEEDED"})


class AdapterError(ValueError):
    """A safe, user-correctable adapter failure."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AdapterError(f"Cannot read valid JSON from {path}: {exc}") from exc


def _write_json(path: Path, value: Any, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def _default_contract_path() -> Path:
    return Path(__file__).resolve().parents[1] / "e2e-adapter.json"


def _load_contract(path: Path) -> dict[str, Any]:
    contract = _read_json(path)
    if not isinstance(contract, dict):
        raise AdapterError("Adapter contract must be a JSON object.")
    if contract.get("schemaVersion") not in (SCHEMA_VERSION, "fscr-fsm-task-adapter-v2"):
        raise AdapterError(
            f"Unsupported adapter schema: {contract.get('schemaVersion')!r}."
        )
    task = contract.get("task")
    package = contract.get("package")
    if not isinstance(task, dict) or not task.get("name") or not task.get("code"):
        raise AdapterError("Adapter contract lacks exact task identity.")
    if not isinstance(package, dict) or not package.get("entities"):
        raise AdapterError("Adapter contract lacks package entities.")
    return contract


def _entity_map(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entity["name"]: entity for entity in contract["package"]["entities"]}


def _task_specific_entity_rules(entity: dict[str, Any]) -> dict[str, Any]:
    """Load the task-owned validation extension for one generated entity.

    The generic adapter descriptor deliberately remains within the published
    adapter schema. Rules that require Payables-specific source semantics are
    kept beside this runtime and registered through ``semanticModel`` as a
    task-specific extension.
    """

    path = Path(__file__).resolve().with_name(TASK_SPECIFIC_RULES_FILE)
    document = _read_json(path)
    if (
        not isinstance(document, dict)
        or document.get("schemaVersion") != TASK_SPECIFIC_RULES_VERSION
    ):
        raise AdapterError(
            f"Task-specific validation rules at {path} have an unsupported schema."
        )
    entities = document.get("entities")
    if not isinstance(entities, dict):
        raise AdapterError("Task-specific validation rules lack an entities object.")
    rules = entities.get(entity["name"])
    if not isinstance(rules, dict):
        raise AdapterError(
            f"Task-specific validation rules lack {entity['name']!r}."
        )
    return rules


def _safe_member_name(name: str) -> None:
    normalized = name.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if pure.is_absolute() or ".." in pure.parts or normalized.startswith("/"):
        raise AdapterError(f"Unsafe ZIP member name: {name!r}.")


def _decode_csv(raw: bytes, member: str) -> tuple[list[str], list[dict[str, str]]]:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise AdapterError(f"{member} is not UTF-8 CSV: {exc}") from exc
    try:
        reader = csv.reader(io.StringIO(text, newline=""))
        headers = next(reader, [])
        if (
            not headers
            or any(not str(header).strip() for header in headers)
            or len(set(headers)) != len(headers)
        ):
            raise AdapterError(f"{member} has blank or duplicate headers.")
        rows = []
        for number, values in enumerate(reader, start=2):
            if len(values) != len(headers):
                raise AdapterError(
                    f"{member} row {number} has {len(values)} CSV fields but the "
                    f"template header has {len(headers)}. Every row must serialize "
                    "one field per exact template header; trailing blanks require "
                    "explicit empty CSV fields."
                )
            rows.append(dict(zip(headers, values)))
    except csv.Error as exc:
        raise AdapterError(f"{member} is not valid CSV: {exc}") from exc
    return headers, rows


def _csv_bytes(headers: list[str], rows: list[dict[str, str]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=headers,
        extrasaction="raise",
        quoting=csv.QUOTE_ALL,
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                header: "" if row.get(header, "") is None else str(row.get(header, ""))
                for header in headers
            }
        )
    return stream.getvalue().encode("utf-8")


def _first_xml_text(root: ElementTree.Element, local_name: str) -> str:
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] == local_name:
            return "" if node.text is None else node.text.strip()
    return ""


@dataclass
class PackageData:
    path: Path
    archive_sha256: str
    member_names: list[str]
    member_bytes: dict[str, bytes]
    member_infos: dict[str, zipfile.ZipInfo]
    headers: dict[str, list[str]]
    rows: dict[str, list[dict[str, str]]]
    metadata: dict[str, str]
    object_contracts: dict[str, dict[str, Any]]


def _metadata_object_contracts(root: ElementTree.Element) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] != "MigrationProcessBusinessObjectCSVMetadataVORow":
            continue
        name = _first_xml_text(node, "BusinessObjectShortName")
        if not name:
            raise AdapterError("Metadata contains an unnamed business object.")
        if name in result:
            raise AdapterError(f"Metadata contains duplicate business object {name}.")
        attributes = [
            value.strip()
            for value in _first_xml_text(node, "XmlAttributeList").split(",")
        ]
        types = [
            value.strip()
            for value in _first_xml_text(node, "XmlAttributeTypeList").split(",")
        ]
        if len(attributes) != len(types):
            raise AdapterError(
                f"Metadata object {name} has {len(attributes)} attributes and {len(types)} types."
            )
        if not all(attributes) or len(attributes) != len(set(attributes)):
            raise AdapterError(f"Metadata object {name} has blank or duplicate attributes.")
        result[name] = {
            "nodePath": _first_xml_text(node, "XmlNodePath"),
            "nodeSequence": _first_xml_text(node, "NodeSequence"),
            "types": dict(zip(attributes, types)),
        }
    return result


def _read_package(path: Path, contract: dict[str, Any]) -> PackageData:
    try:
        archive_bytes = path.read_bytes()
        with zipfile.ZipFile(io.BytesIO(archive_bytes), "r") as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            total_size = 0
            for info in infos:
                _safe_member_name(info.filename)
                if info.is_dir():
                    raise AdapterError(f"Directory ZIP members are not allowed: {info.filename!r}.")
                if info.flag_bits & 0x1:
                    raise AdapterError(f"Encrypted ZIP members are not allowed: {info.filename!r}.")
                if info.file_size > MAX_MEMBER_BYTES:
                    raise AdapterError(f"ZIP member is too large: {info.filename!r}.")
                total_size += info.file_size
                if total_size > MAX_TOTAL_BYTES:
                    raise AdapterError("FSM ZIP expands beyond the allowed total size.")
                if info.file_size and info.file_size / max(info.compress_size, 1) > MAX_COMPRESSION_RATIO:
                    raise AdapterError(f"ZIP member compression ratio is unsafe: {info.filename!r}.")
            if len(names) != len(set(names)):
                raise AdapterError(f"{path.name} contains duplicate ZIP members.")
            member_bytes = {name: archive.read(name) for name in names}
            member_infos = {info.filename: info for info in infos}
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        if isinstance(exc, AdapterError):
            raise
        raise AdapterError(f"Cannot read FSM ZIP {path}: {exc}") from exc

    expected = [contract["package"]["metadataMember"]] + [
        entity["member"] for entity in contract["package"]["entities"]
    ]
    if sorted(names) != sorted(expected):
        raise AdapterError(
            f"{path.name} members differ from the exact task contract; "
            f"expected {sorted(expected)}, found {sorted(names)}."
        )

    headers: dict[str, list[str]] = {}
    rows: dict[str, list[dict[str, str]]] = {}
    for entity in contract["package"]["entities"]:
        actual_headers, actual_rows = _decode_csv(
            member_bytes[entity["member"]], entity["member"]
        )
        if actual_headers != entity["headers"]:
            raise AdapterError(
                f"{entity['member']} header order differs from e2e-adapter.json."
            )
        headers[entity["name"]] = actual_headers
        rows[entity["name"]] = actual_rows

    metadata_member = contract["package"]["metadataMember"]
    try:
        root = ElementTree.fromstring(member_bytes[metadata_member])
    except ElementTree.ParseError as exc:
        raise AdapterError(f"Invalid {metadata_member}: {exc}") from exc
    metadata = {
        name: _first_xml_text(root, name)
        for name in (
            "ProcessName",
            "ProcessStatus",
            "ProcessEnv",
            "ProcessRelease",
            "ESSRequestId",
            "ObjectShortName",
        )
    }
    if metadata["ObjectShortName"] != contract["package"]["objectShortName"]:
        raise AdapterError(
            "Package ObjectShortName does not match the adapter task identity: "
            f"{metadata['ObjectShortName']!r}."
        )
    if metadata["ProcessStatus"].strip().upper() not in SUCCESS_STATUSES:
        raise AdapterError(
            f"Package process status is not successful: {metadata['ProcessStatus']!r}."
        )
    if not metadata["ProcessEnv"] or not metadata["ProcessRelease"]:
        raise AdapterError("Package metadata must declare ProcessEnv and ProcessRelease.")
    object_contracts = _metadata_object_contracts(root)
    if set(object_contracts) != {entity["name"] for entity in contract["package"]["entities"]}:
        raise AdapterError("Metadata business objects differ from the exact task contract.")
    observed_node_sequences: list[str] = []
    for entity in contract["package"]["entities"]:
        actual = object_contracts.get(entity["name"])
        if actual is None:
            raise AdapterError(
                f"Metadata lacks business object contract for {entity['name']}."
            )
        if actual["nodePath"] != entity["nodePath"]:
            raise AdapterError(
                f"Metadata node path for {entity['name']} is {actual['nodePath']!r}, expected {entity['nodePath']!r}."
            )
        observed_node_sequences.append(actual["nodeSequence"])
        native_fields = {field for field in entity["headers"] if "." not in field}
        if set(actual["types"]) != native_fields:
            raise AdapterError(f"Metadata attributes for {entity['name']} differ from its native CSV fields.")
        for field, actual_type in actual["types"].items():
            if field not in entity["headers"]:
                raise AdapterError(
                    f"Metadata object {entity['name']} contains non-CSV attribute {field}."
                )
            if entity["types"].get(field, "") != actual_type:
                raise AdapterError(
                    f"Metadata type for {entity['name']}.{field} is {actual_type!r}, expected {entity['types'].get(field, '')!r}."
                )
    expected_node_sequences = {
        str(index) for index in range(1, len(contract["package"]["entities"]) + 1)
    }
    if set(observed_node_sequences) != expected_node_sequences:
        raise AdapterError(
            "Metadata node sequences must be unique contiguous positive values; "
            f"observed {observed_node_sequences!r}."
        )

    return PackageData(
        path=path,
        archive_sha256=_sha256_bytes(archive_bytes),
        member_names=names,
        member_bytes=member_bytes,
        member_infos=member_infos,
        headers=headers,
        rows=rows,
        metadata=metadata,
        object_contracts=object_contracts,
    )


def _schema_fingerprint(contract: dict[str, Any], package: PackageData) -> str:
    normalized = {
        "taskCode": contract["task"]["code"],
        "objectShortName": contract["package"]["objectShortName"],
        "metadataMember": contract["package"]["metadataMember"],
        "entities": [
            {
                "name": entity["name"],
                "member": entity["member"],
                "nodePath": package.object_contracts[entity["name"]]["nodePath"],
                "headers": package.headers[entity["name"]],
                "types": [
                    package.object_contracts[entity["name"]]["types"].get(field, "")
                    for field in package.headers[entity["name"]]
                ],
            }
            for entity in sorted(
                contract["package"]["entities"], key=lambda item: item["member"]
            )
        ],
    }
    return _sha256_bytes(_canonical_bytes(normalized))


def _validate_new_outputs(outputs: list[Path], inputs: list[Path]) -> None:
    resolved_outputs = [path.resolve() for path in outputs]
    resolved_inputs = {path.resolve() for path in inputs}
    if len(resolved_outputs) != len(set(resolved_outputs)):
        raise AdapterError("Output paths must be distinct.")
    for original, path in zip(outputs, resolved_outputs):
        if path in resolved_inputs:
            raise AdapterError(f"Output path overlaps an input: {path}.")
        if original.is_symlink() or path.exists():
            raise AdapterError(f"Refusing to overwrite existing output: {path}.")


def _validate_source_pair(
    contract: dict[str, Any], template: PackageData, baseline: PackageData
) -> None:
    if any(template.rows[entity["name"]] for entity in contract["package"]["entities"]):
        raise AdapterError("Build template must be template-only and contain no data rows.")
    for field in ("ProcessEnv", "ProcessRelease"):
        if template.metadata[field] != baseline.metadata[field]:
            raise AdapterError(
                f"Template and baseline {field} differ: {template.metadata[field]!r} versus {baseline.metadata[field]!r}."
            )
    # evidenceRelease records authoring provenance. Runtime compatibility is
    # established by the exact task identity, matching live source releases,
    # and the stable member/path/header/type fingerprint below. A compatible
    # environment release must not require regenerating an otherwise identical
    # task adapter.


def _row_key(entity: dict[str, Any], row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row.get(field, "") for field in entity["keyFields"])


def _target_tuple(entity: dict[str, Any], target: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(target.get(field, "")) for field in entity["keyFields"])


def _validate_field_value(
    entity: dict[str, Any], field: str, value: Any, operation_id: str
) -> None:
    value_contract = entity.get("valueContracts", {}).get(field)
    # An empty optional CSV cell is a supported clear/default request.  Its
    # field-specific semantics are not invented here; required-create, key,
    # dependency, and closed-enumeration checks run elsewhere.  In particular,
    # fixed Y/N UI flags still flow through their value contract below.
    if value == "" and value_contract is None:
        return
    expected = entity["types"].get(field, "string") or "string"
    lowered = expected.lower()
    if lowered in {"datetime", "timestamp"} or "timestamp" in lowered:
        normalized_type = "dateTime"
    elif lowered == "date" or ("date" in lowered and "time" not in lowered):
        normalized_type = "date"
    elif lowered in {"integer", "short"}:
        normalized_type = "int"
    elif lowered in {"number", "float", "double", "bigdecimal"}:
        normalized_type = "decimal"
    else:
        normalized_type = expected
    valid = False
    if normalized_type == "string":
        valid = isinstance(value, str)
    elif normalized_type in {"int", "long"}:
        valid = (
            isinstance(value, int)
            and not isinstance(value, bool)
        ) or (
            isinstance(value, str)
            and re.fullmatch(r"[+-]?\d+", value.strip()) is not None
        )
    elif normalized_type == "decimal":
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            candidate = str(value)
        elif isinstance(value, str):
            candidate = value.strip()
        else:
            candidate = ""
        if candidate:
            try:
                valid = Decimal(candidate).is_finite()
            except InvalidOperation:
                valid = False
    elif normalized_type == "date":
        if isinstance(value, str) and value.strip():
            try:
                date.fromisoformat(value.strip())
                valid = True
            except ValueError:
                valid = False
    elif normalized_type == "dateTime":
        if isinstance(value, str) and value.strip():
            candidate = value.strip()
            if candidate.endswith("Z"):
                candidate = candidate[:-1] + "+00:00"
            try:
                datetime.fromisoformat(candidate)
                valid = True
            except ValueError:
                valid = False
    else:
        valid = isinstance(value, str)
    if not valid:
        raise AdapterError(
            f"Operation {operation_id} field {entity['name']}.{field} expects "
            f"a source-compatible {expected} value; received {type(value).__name__}."
        )
    if (
        value_contract
        and value_contract.get("constraintKind")
        in {"fixed-enumeration", "seeded-enumeration"}
        and value_contract.get("extensible") is False
    ):
        allowed = {
            str(item.get("code", ""))
            for item in value_contract.get("allowedValues", [])
        }
        if str(value) not in allowed:
            choices = ", ".join(
                str(item.get("label", ""))
                for item in value_contract.get("allowedValues", [])
                if str(item.get("label", ""))
            )
            raise AdapterError(
                f"Operation {operation_id} field {entity['name']}.{field} has an "
                f"unsupported business value; choose one of: {choices}."
            )


def _normalize_field_value(
    entity: dict[str, Any], field: str, value: Any, operation_id: str
) -> Any:
    """Map a declared business label or synonym to its package code."""

    value_contract = entity.get("valueContracts", {}).get(field)
    if not value_contract or not isinstance(value, str):
        return value
    stripped = value.strip()
    folded = stripped.casefold()
    exact_code = field in _task_specific_entity_rules(entity).get(
        "fieldValidation", {}
    ).get("exactCodeFields", [])
    matches: list[str] = []
    for item in value_contract.get("allowedValues", []):
        code = str(item.get("code", "")).strip()
        labels = [
            str(item.get("label", "")).strip(),
            *[
                str(candidate).strip()
                for candidate in item.get("synonyms", [])
                if str(candidate).strip()
            ],
        ]
        code_matches = stripped == code if exact_code else folded == code.casefold()
        if code_matches or folded in {
            label.casefold() for label in labels if label
        }:
            matches.append(code)
    matches = list(dict.fromkeys(matches))
    if len(matches) == 1:
        return matches[0]
    closed = (
        value_contract.get("constraintKind")
        in {"fixed-enumeration", "seeded-enumeration"}
        and value_contract.get("extensible") is False
    )
    if not matches and not closed:
        return stripped
    choices = ", ".join(
        str(item.get("label", ""))
        for item in value_contract.get("allowedValues", [])
        if str(item.get("label", ""))
    )
    if not matches:
        raise AdapterError(
            f"Operation {operation_id} field {entity['name']}.{field} has an "
            f"unsupported business value; choose one of: {choices}."
        )
    raise AdapterError(
        f"Operation {operation_id} field {entity['name']}.{field} is ambiguous; "
        f"choose one of: {choices}."
    )


def _omit_create_blank_values(
    entity: dict[str, Any], values: dict[str, Any], action: str, operation_id: str
) -> dict[str, Any]:
    """Omit only source-proven null defaults from a new-row change request.

    An FSM CSV must retain every header and therefore serializes an empty cell for
    omitted values.  That is not equivalent to accepting an explicit empty value
    during an update, which may be a request to clear existing target data.  The
    task extension can therefore declare the small set of fields whose server-side
    new-row procedure initializes to NULL; only those blank create inputs are
    removed before validation and candidate-row construction.
    """

    rules = _task_specific_entity_rules(entity).get("fieldValidation", {})
    if not isinstance(rules, dict):
        raise AdapterError(
            f"Adapter contract has invalid fieldValidation for {entity['name']}."
        )
    null_on_create = rules.get("omitBlankOnCreate", {})
    if not isinstance(null_on_create, dict):
        raise AdapterError(
            f"Adapter contract has invalid omitBlankOnCreate for {entity['name']}."
        )
    for field, reason in null_on_create.items():
        if (
            not isinstance(field, str)
            or field not in entity.get("headers", [])
            or not isinstance(reason, str)
            or not reason
        ):
            raise AdapterError(
                f"Adapter contract has invalid create-null default for {entity['name']}."
            )
    if action != "create":
        return values
    return {
        field: value
        for field, value in values.items()
        if not (field in null_on_create and value in (None, ""))
    }


def _row_index(
    package: PackageData, entity: dict[str, Any], *, allow_blank_enterprise: bool = False
) -> dict[tuple[str, ...], dict[str, str]]:
    """Index all rows, preserving unrelated export rows with blank enterprise IDs.

    Only baseline/persisted exports permit that blank component; candidate keys
    remain complete, and duplicate keys or any other blank key still fail.
    """

    if not entity["keyFields"]:
        raise AdapterError(f"Entity {entity['name']} has no source-backed key.")
    enterprise_field = _bu_context_rules(entity).get("enterpriseIdField")
    result: dict[tuple[str, ...], dict[str, str]] = {}
    for number, row in enumerate(package.rows[entity["name"]], start=2):
        key = _row_key(entity, row)
        if any(
            value == "" and not (allow_blank_enterprise and field == enterprise_field)
            for field, value in zip(entity["keyFields"], key)
        ):
            raise AdapterError(
                f"{entity['member']} row {number} has a blank key component."
            )
        if key in result:
            raise AdapterError(
                f"{entity['member']} contains duplicate key {key!r}."
            )
        result[key] = row
    return result


def _satisfied_prerequisites(
    blueprint: dict[str, Any], contract: dict[str, Any]
) -> list[dict[str, Any]]:
    """Return declared, successful receipts without weakening their bindings.

    A receipt is intentionally not reduced to an entity/field/resolver tuple.
    The caller must additionally bind it to one operation and the exact requested
    value (and any resolver-specific source context) before treating it as proof.
    """
    declared = {
        (entity["name"], blocker["field"]): blocker["resolver"]
        for entity in contract["package"]["entities"]
        for blocker in entity.get("conditionallyBlockedFields", [])
    }
    satisfied: list[dict[str, Any]] = []
    for item in blueprint.get("prerequisites", []):
        if not isinstance(item, dict) or item.get("status") != "satisfied":
            continue
        entity = str(item.get("entity", ""))
        field = str(item.get("field", ""))
        resolver = str(item.get("resolver", ""))
        if (
            entity
            and field
            and resolver
            and item.get("evidence")
            and declared.get((entity, field)) == resolver
        ):
            satisfied.append(item)
    return satisfied


def _reference_time(value: Any, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("Timezone required")
        return parsed.astimezone(timezone.utc)
    except (AttributeError, TypeError, ValueError) as exc:
        raise AdapterError(f"Reference evidence {field} must be a timezone-qualified ISO timestamp.") from exc


def _validate_reference_provenance(
    blueprint: dict[str, Any], baseline: PackageData,
    satisfied: list[dict[str, Any]], *, require_fresh: bool,
) -> None:
    """Bind successful resolver evidence to the selected run and actual export.

    The workflow supplies referenceContext before acquiring receipts. This
    local check never invents provenance or rebinds an earlier receipt. Offline
    structural checks without a baseline do not constitute preparation.
    """
    if not satisfied:
        return
    context = blueprint.get("referenceContext")
    fields = {"environment", "baseUrl", "baselineSha256", "runId", "startedAt"}
    if not isinstance(context, dict) or set(context) != fields:
        raise AdapterError("Successful reference receipts require a complete referenceContext for the selected run.")
    from readback_evidence import _host

    try:
        origin = _host(context["baseUrl"])
    except (TypeError, ValueError) as exc:
        raise AdapterError("Reference context baseUrl must be a complete HTTPS origin.") from exc
    if (context["baseUrl"] != origin
            or not baseline.metadata.get("ProcessEnv")
            or context["environment"] != baseline.metadata["ProcessEnv"]
            or context["baselineSha256"] != baseline.archive_sha256
            or not isinstance(context["runId"], str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", context["runId"])):
        raise AdapterError("Reference context must bind the current environment, HTTPS origin, export SHA and run ID.")
    now = datetime.now(timezone.utc)
    started = _reference_time(context["startedAt"], "startedAt")
    if started > now or (require_fresh and now - started > timedelta(hours=24)):
        raise AdapterError("Reference run must have started within the last 24 hours and not in the future.")
    for receipt in satisfied:
        if receipt.get("requestContext") != context:
            raise AdapterError("Successful reference receipt must bind the exact current referenceContext; never reuse or rebind earlier evidence.")
        if any(name in receipt and receipt[name] != context[name]
               for name in ("environment", "baseUrl", "baselineSha256")):
            raise AdapterError("Reference receipt contains conflicting environment, origin or export provenance.")
        observed = _reference_time(receipt.get("observedAt"), "observedAt")
        if observed < started or observed > now:
            raise AdapterError("Reference receipt observedAt must be within the selected run and not in the future.")


def _effective_operation_value(
    values: dict[str, Any], baseline_row: dict[str, str] | None, field: str
) -> Any:
    """Return an explicitly changed value or its exact current-export value."""

    if field in values:
        return values[field]
    if baseline_row is not None:
        return baseline_row.get(field)
    return None


def _receipt_context(
    entity: dict[str, Any],
    blocker: dict[str, Any],
    values: dict[str, Any],
    baseline_row: dict[str, str] | None,
    operation_id: str,
) -> dict[str, str]:
    """Build the exact source context a resolver receipt must carry."""

    bindings = _task_specific_entity_rules(entity).get("receiptBindings", {}).get(
        blocker["resolver"], {}
    )
    if not isinstance(bindings, dict):
        raise AdapterError(
            f"Adapter contract has invalid receipt bindings for "
            f"{entity['name']}.{blocker['field']}."
        )
    context: dict[str, str] = {}
    for receipt_field, binding in bindings.items():
        if not isinstance(receipt_field, str):
            raise AdapterError(
                f"Adapter contract has invalid receipt binding for "
                f"{entity['name']}.{blocker['field']}."
            )
        if isinstance(binding, str):
            binding = {"field": binding}
        if not isinstance(binding, dict):
            raise AdapterError(
                f"Adapter contract has invalid receipt binding for "
                f"{entity['name']}.{blocker['field']}."
            )
        if set(binding) == {"constant"} and isinstance(binding["constant"], str):
            context[receipt_field] = binding["constant"]
            continue
        if set(binding) != {"field"} or not isinstance(binding["field"], str):
            raise AdapterError(
                f"Adapter contract has invalid receipt binding for "
                f"{entity['name']}.{blocker['field']}."
            )
        candidate_field = binding["field"]
        if candidate_field == "$blocked":
            candidate_field = blocker["field"]
        value = _effective_operation_value(values, baseline_row, candidate_field)
        if value in (None, ""):
            raise AdapterError(
                f"Operation {operation_id} changes conditionally blocked field "
                f"{entity['name']}.{blocker['field']} but lacks required "
                f"{candidate_field} context for {blocker['resolver']}."
            )
        context[receipt_field] = str(value)
    return context


def _has_satisfied_prerequisite(
    satisfied: list[dict[str, Any]],
    *,
    operation_id: str,
    entity_name: str,
    field: str,
    resolver: str,
    requested_value: Any,
    context: dict[str, str],
    required_values: list[str],
) -> bool:
    """Require operation-, value-, and context-bound evidence for a resolver."""

    expected_value = str(requested_value)
    for item in satisfied:
        if (
            item.get("operationId") != operation_id
            or item.get("entity") != entity_name
            or item.get("field") != field
            or item.get("resolver") != resolver
            or "requestedValue" not in item
            or str(item["requestedValue"]) != expected_value
        ):
            continue
        if any(
            not isinstance(item.get(name), (str, int))
            or isinstance(item.get(name), bool)
            or not str(item[name]).strip()
            for name in required_values
        ):
            continue
        if all(str(item.get(name, "")) == value for name, value in context.items()):
            return True
    return False


def _required_receipt_values(entity: dict[str, Any], resolver: str) -> list[str]:
    """Require declared resolver outputs even when no CSV value binds them."""

    fields = _task_specific_entity_rules(entity).get(
        "receiptRequiredValues", {}
    ).get(resolver, [])
    if not isinstance(fields, list) or any(
        not isinstance(field, str) or not field for field in fields
    ):
        raise AdapterError(f"Invalid required receipt values for {resolver}.")
    return fields


def _additional_rest_check_warnings(contract, blueprint, baseline):
    """Defer unavailable supplemental REST checks without claiming resolution."""
    operations = {op["id"]: op for op in blueprint["operations"]
                  if isinstance(op, dict) and isinstance(op.get("id"), str)}
    entities = _entity_map(contract)
    warnings = []
    seen = set()
    availability = {
        "auth_authz": {401, 403},
        "endpoint_unavailable": {404, 405, 410, 501},
        "transport_environment": {None, 408, 429, 500, 502, 503, 504},
    }
    for item in blueprint.get("prerequisites", []):
        if isinstance(item, dict) and item.get("status") in ("invalid", "ambiguous", "no_match"):
            raise AdapterError("A completed reference check found an invalid or ambiguous value; correct the input.")
        if not isinstance(item, dict) or item.get("status") != "unavailable":
            continue
        if any(not isinstance(item.get(name), str)
               for name in ("operationId", "entity", "field", "resolver", "failureClass")):
            raise AdapterError("Unavailable REST check identifiers and failure class must be strings.")
        operation = operations.get(item.get("operationId"))
        entity = entities.get(item.get("entity"))
        field = item.get("field")
        resolver = item.get("resolver")
        if (baseline is None or operation is None or entity is None
                or operation.get("entity") != entity["name"]
                or resolver not in _task_specific_entity_rules(entity).get("additionalRestResolvers", [])
                or not any(b["field"] == field and b["resolver"] == resolver
                           for b in entity.get("conditionallyBlockedFields", []))
                or field not in operation.get("values", {})):
            raise AdapterError("Unavailable REST check is not an applicable additional reference check.")
        status = item.get("httpStatus")
        allowed_fields = {"operationId", "entity", "field", "resolver", "requestedValue",
                          "status", "failureClass", "httpStatus", "evidence", "requestContext",
                          "method", "endpointPath"}
        if (set(item) != allowed_fields or item.get("method") != "GET"
                or not isinstance(item.get("endpointPath"), str)
                or not item["endpointPath"].startswith(("/fscmRestApi/", "/hcmRestApi/"))
                or any(c in item["endpointPath"] for c in ("?", "#", "\n", "\r"))
                or "httpStatus" not in item or (status is not None and type(status) is not int)
                or item.get("failureClass") not in availability
                or status not in availability[item["failureClass"]]
                or not isinstance(item.get("evidence"), str) or not item["evidence"].strip()):
            raise AdapterError("Additional REST check must record an API availability failure, not an invalid result.")
        key = (operation["id"], entity["name"], field)
        if key in seen:
            raise AdapterError("Duplicate unavailable REST check.")
        if any(isinstance(other, dict) and other.get("status") == "satisfied"
               and (other.get("operationId"), other.get("entity"), other.get("field")) == key
               for other in blueprint.get("prerequisites", [])):
            raise AdapterError("Unavailable REST check conflicts with a completed reference receipt.")
        seen.add(key)
        expected = {
            "environment": baseline.metadata.get("ProcessEnv"),
            "baselineSha256": baseline.archive_sha256,
            "targetKey": operation["targetKey"],
            "requestedValues": operation["values"],
        }
        if (not expected["environment"] or item.get("requestContext") != expected
                or str(item.get("requestedValue")) != str(operation["values"][field])):
            raise AdapterError("Unavailable REST check must bind the current environment, export, target and requested values.")
        warnings.append({
            "status": "UNVERIFIED_API_UNAVAILABLE", "operationId": operation["id"],
            "entity": entity["name"], "field": field, "resolver": resolver,
            "failureClass": item["failureClass"], "httpStatus": status,
            "evidence": item["evidence"],
            "message": "Additional REST validation unavailable; supplied value preserved for governed Fusion validation.",
        })
    return warnings


def _bu_context_rules(entity: dict[str, Any]) -> dict[str, Any]:
    """Return the task-specific ERP-only BU-context contract, if declared."""

    rules = _task_specific_entity_rules(entity).get("buContext")
    if rules is None:
        return {}
    if not isinstance(rules, dict):
        raise AdapterError(
            f"Adapter contract has invalid BU-context rules for {entity['name']}."
        )
    return rules


def _bu_context_field(
    entity: dict[str, Any], rules: dict[str, Any], name: str
) -> str:
    """Read one declared CSV field name from the BU-context extension."""

    value = rules.get(name)
    if not isinstance(value, str) or not value:
        raise AdapterError(
            f"Adapter contract has invalid BU-context {name} for {entity['name']}."
        )
    if value not in entity["headers"]:
        raise AdapterError(
            f"Adapter contract BU-context {name} is not a CSV field for {entity['name']}."
        )
    return value


def _receipt_value(
    receipt: dict[str, Any], name: str, *, expected: str | None = None
) -> str:
    """Read a nonblank sanitized receipt value and, when supplied, match it exactly."""

    value = receipt.get(name)
    if value in (None, ""):
        raise AdapterError(
            f"ERP-only BU-context receipt is missing required {name}."
        )
    actual = str(value)
    if expected is not None and actual != expected:
        raise AdapterError(
            f"ERP-only BU-context receipt {name} {actual!r} does not match "
            f"the expected value {expected!r}."
        )
    return actual


def _derive_and_verify_erp_bu_context(
    contract: dict[str, Any],
    blueprint: dict[str, Any],
    baseline: PackageData,
    satisfied: list[dict[str, Any]],
) -> dict[str, dict[str, str]]:
    """Select EnterpriseId and derive SOBName with recorded ERP-only receipts.

    Explicit row input wins, then a uniquely matched update row, then the one
    distinct nonblank export value. Overrides never seed or invalidate the
    export default. ``finBusinessUnitsLOV`` does not validate EnterpriseId;
    Fusion performs its applicable validation during import. The two ERP reads
    still establish the BU's primary ledger/name. This adapter is offline.
    """

    entities = _entity_map(contract)
    operations = blueprint.get("operations")
    if not isinstance(operations, list):
        return {}
    contexts: dict[str, dict[str, str]] = {}
    enterprise_defaults: dict[str, dict[str, Any]] = {}
    for operation in operations:
        if not isinstance(operation, dict):
            continue
        operation_id = operation.get("id")
        entity_name = operation.get("entity")
        action = operation.get("action")
        if (
            not isinstance(operation_id, str)
            or not operation_id
            or not isinstance(entity_name, str)
            or entity_name not in entities
            or action not in {"create", "update"}
        ):
            continue
        entity = entities[entity_name]
        rules = _bu_context_rules(entity)
        if not rules:
            continue
        resolver = rules.get("resolver")
        if not isinstance(resolver, str) or not resolver:
            raise AdapterError(
                f"Adapter contract has invalid BU-context resolver for {entity_name}."
            )
        business_unit_field = _bu_context_field(entity, rules, "businessUnitField")
        enterprise_id_field = _bu_context_field(entity, rules, "enterpriseIdField")
        ledger_name_field = _bu_context_field(entity, rules, "ledgerNameField")

        target = operation.get("targetKey")
        if not isinstance(target, dict):
            continue
        unexpected_target_fields = set(target) - {
            business_unit_field,
            enterprise_id_field,
        }
        if unexpected_target_fields:
            raise AdapterError(
                f"Operation {operation_id} targetKey has unsupported BU-context "
                f"fields: {sorted(unexpected_target_fields)}."
            )
        business_unit_name = target.get(business_unit_field)
        if not isinstance(business_unit_name, str) or not business_unit_name:
            raise AdapterError(
                f"Operation {operation_id} must provide a nonblank "
                f"{entity_name}.{business_unit_field} before ERP-only context "
                "derivation."
            )

        baseline_rows = baseline.rows.get(entity_name, [])
        distinct_enterprise_ids = sorted({
            str(row.get(enterprise_id_field) or "").strip()
            for row in baseline_rows
            if str(row.get(enterprise_id_field) or "").strip()
        })
        export_default = (
            distinct_enterprise_ids[0] if len(distinct_enterprise_ids) == 1 else None
        )
        enterprise_defaults[entity_name] = {
            "value": export_default,
            "source": "fresh_exact_task_export",
            "status": "usable" if export_default is not None else "unavailable",
            "baselineSha256": baseline.archive_sha256,
            "distinctNonblankValues": distinct_enterprise_ids,
        }
        supplied = target.get(enterprise_id_field)
        if supplied is not None and not (isinstance(supplied, str) and not supplied.strip()):
            # Validate before string conversion so booleans/objects cannot be
            # mistaken for an omitted value or a valid long-integer identifier.
            _validate_field_value(entity, enterprise_id_field, supplied, operation_id)
            enterprise_id = str(supplied).strip()
        else:
            update_matches = [
                row for row in baseline_rows
                if action == "update" and row.get(business_unit_field) == business_unit_name
            ]
            matched_id = (
                str(update_matches[0].get(enterprise_id_field) or "").strip()
                if len(update_matches) == 1 else ""
            )
            enterprise_id = matched_id or export_default
            if enterprise_id is None:
                raise AdapterError(
                    f"Operation {operation_id} is missing {enterprise_id_field}: "
                    "no usable uniquely matched update-row value or single distinct "
                    "nonblank export value is available "
                    f"(export values: {distinct_enterprise_ids!r}). "
                    "Ask the user which Enterprise ID to use for this row."
                )
        matches = [
            item
            for item in satisfied
            if item.get("operationId") == operation_id
            and item.get("entity") == entity_name
            and item.get("field") == enterprise_id_field
            and item.get("resolver") == resolver
            and str(item.get("requestedValue", "")) == enterprise_id
        ]
        if len(matches) != 1:
            raise AdapterError(
                f"Operation {operation_id} requires exactly one satisfied "
                "ERP-only BU-context receipt bound to the selected "
                f"{enterprise_id_field}."
            )
        receipt = matches[0]
        _receipt_value(receipt, "baselineSha256", expected=baseline.archive_sha256)
        _receipt_value(receipt, "baselineRowCount", expected=str(len(baseline_rows)))
        _receipt_value(
            receipt, "distinctEnterpriseIdCount", expected=str(len(distinct_enterprise_ids))
        )
        _receipt_value(receipt, "enterpriseId", expected=enterprise_id)
        _receipt_value(receipt, "businessUnitHttpStatus", expected="200")
        _receipt_value(receipt, "businessUnitName", expected=business_unit_name)
        _receipt_value(receipt, "businessUnitCount", expected="1")
        _receipt_value(receipt, "businessUnitItemCount", expected="1")
        _receipt_value(receipt, "businessUnitHasMore", expected="False")
        _receipt_value(
            receipt, "returnedBusinessUnitName", expected=business_unit_name
        )
        _receipt_value(receipt, "businessUnitId")
        primary_ledger_id = _receipt_value(receipt, "primaryLedgerId")
        _receipt_value(receipt, "ledgerHttpStatus", expected="200")
        _receipt_value(receipt, "ledgerId", expected=primary_ledger_id)
        ledger_name = _receipt_value(receipt, "ledgerName")

        values = operation.get("values")
        if not isinstance(values, dict):
            continue
        if ledger_name_field in values and str(values[ledger_name_field]) != ledger_name:
            raise AdapterError(
                f"Operation {operation_id} supplies {ledger_name_field} "
                f"{values[ledger_name_field]!r}, but ERP primary-ledger resolution "
                f"returned {ledger_name!r}. Do not override the derived value."
            )
        if action == "create":
            values[ledger_name_field] = ledger_name
        operation["values"] = values
        contexts[operation_id] = {
            "enterpriseId": enterprise_id,
            "ledgerName": ledger_name,
            "ledgerNameField": ledger_name_field,
        }
        target[enterprise_id_field] = enterprise_id
        operation["targetKey"] = target

    # Persist only in this run's design/preflight. Recompute from the supplied
    # baseline each time; a previous run or explicit row override is not a default.
    blueprint["enterpriseIdDefaults"] = enterprise_defaults
    return contexts


def _validate_field_rules(
    entity: dict[str, Any],
    operation: dict[str, Any],
    values: dict[str, Any],
    baseline_row: dict[str, str] | None,
) -> None:
    """Apply product-backed entity rules and documented transport sanity."""

    rules = _task_specific_entity_rules(entity).get("fieldValidation", {})
    if not isinstance(rules, dict):
        raise AdapterError(f"Adapter contract has invalid fieldValidation for {entity['name']}.")
    operation_id = str(operation["id"])

    max_lengths = rules.get("maxLengths", {})
    if not isinstance(max_lengths, dict):
        raise AdapterError(f"Adapter contract has invalid maxLengths for {entity['name']}.")
    max_length_prefixes = rules.get("maxLengthPrefixes", {})
    if not isinstance(max_length_prefixes, dict):
        raise AdapterError(
            f"Adapter contract has invalid maxLengthPrefixes for {entity['name']}."
        )
    length_limits: dict[str, Any] = {
        field: maximum for field, maximum in max_lengths.items() if field in values
    }
    for prefix, maximum in max_length_prefixes.items():
        if not isinstance(prefix, str) or not prefix:
            raise AdapterError(
                f"Adapter contract has invalid maximum-length prefix for {entity['name']}."
            )
        for field in values:
            if field.startswith(prefix):
                length_limits.setdefault(field, maximum)
    for field, maximum in length_limits.items():
        if not isinstance(maximum, int) or maximum < 1:
            raise AdapterError(
                f"Adapter contract has invalid maximum length for {entity['name']}.{field}."
            )
        value = values[field]
        if isinstance(value, str) and len(value) > maximum:
            raise AdapterError(
                f"Operation {operation_id} field {entity['name']}.{field} exceeds "
                f"the source-proven maximum length of {maximum}."
            )

    integer_max_digits = rules.get("integerMaxDigits", {})
    if not isinstance(integer_max_digits, dict):
        raise AdapterError(
            f"Adapter contract has invalid integerMaxDigits for {entity['name']}."
        )
    for field, maximum in integer_max_digits.items():
        if field not in values:
            continue
        if not isinstance(field, str) or field not in entity.get("types", {}):
            raise AdapterError(
                f"Adapter contract has an unknown integer precision field "
                f"for {entity['name']}."
            )
        if entity["types"][field] not in {"int", "long"}:
            raise AdapterError(
                f"Adapter contract has non-integer precision field "
                f"{entity['name']}.{field}."
            )
        if not isinstance(maximum, int) or maximum < 1:
            raise AdapterError(
                f"Adapter contract has invalid integer precision for "
                f"{entity['name']}.{field}."
            )
        digits = str(values[field]).strip().lstrip("+-").lstrip("0") or "0"
        if len(digits) > maximum:
            raise AdapterError(
                f"Operation {operation_id} field {entity['name']}.{field} exceeds "
                f"the source-proven numeric precision of {maximum} digits."
            )

    derived_fields = rules.get("derivedFields", {})
    if not isinstance(derived_fields, dict):
        raise AdapterError(f"Adapter contract has invalid derivedFields for {entity['name']}.")
    for field, reason in derived_fields.items():
        if field in values:
            raise AdapterError(
                f"Operation {operation_id} cannot supply derived field "
                f"{entity['name']}.{field}: {reason}"
            )

    conditional_rules = rules.get("conditionalBlankRules", [])
    if not isinstance(conditional_rules, list):
        raise AdapterError(
            f"Adapter contract has invalid conditionalBlankRules for {entity['name']}."
        )
    for rule in conditional_rules:
        if not isinstance(rule, dict):
            raise AdapterError(
                f"Adapter contract has invalid conditional blank rule for {entity['name']}."
            )
        condition_field = rule.get("conditionField")
        dependent_field = rule.get("dependentField")
        expected_value = rule.get("conditionValue")
        if not all(
            isinstance(value, str)
            for value in (condition_field, dependent_field, expected_value)
        ):
            raise AdapterError(
                f"Adapter contract has invalid conditional blank rule for {entity['name']}."
            )
        if (
            operation["action"] == "update"
            and condition_field not in values
            and dependent_field not in values
        ):
            continue
        condition_value = _effective_operation_value(
            values, baseline_row, condition_field
        )
        if operation["action"] == "create" and condition_value in (None, ""):
            condition_value = rule.get("defaultConditionValueForCreate")
        if condition_value != expected_value:
            required_value = rule.get("requiredConditionValueForNonblank")
            if required_value is not None:
                if not isinstance(required_value, str) or not required_value:
                    raise AdapterError(
                        f"Adapter contract has invalid required condition value "
                        f"for {entity['name']}.{dependent_field}."
                    )
                dependent_value = _effective_operation_value(
                    values, baseline_row, dependent_field
                )
                if (
                    (condition_field in values or dependent_field in values)
                    and dependent_value not in (None, "")
                    and condition_value != required_value
                ):
                    raise AdapterError(
                        f"Operation {operation_id} may supply or retain nonblank "
                        f"{entity['name']}.{dependent_field} only when "
                        f"{condition_field} is confirmed as {required_value} in "
                        "the requested values or fresh current export. "
                        "A blank, missing, or unknown flag is not confirmation."
                    )
            continue
        dependent_value = values.get(dependent_field)
        if dependent_field in values:
            if dependent_value not in (None, ""):
                raise AdapterError(
                    f"Operation {operation_id} must leave {entity['name']}."
                    f"{dependent_field} blank when {condition_field}={expected_value}."
                )
            continue
        if operation["action"] == "create":
            continue
        if not rule.get("requireExplicitClearOnUpdate"):
            continue
        baseline_value = (
            baseline_row.get(dependent_field) if baseline_row is not None else None
        )
        if baseline_value not in (None, ""):
            raise AdapterError(
                f"Operation {operation_id} sets {condition_field}={expected_value} "
                f"but must explicitly clear {entity['name']}.{dependent_field}."
            )
        if baseline_row is None:
            raise AdapterError(
                f"Operation {operation_id} needs a fresh current export proving "
                f"{entity['name']}.{dependent_field} is blank, or must explicitly "
                f"clear it when {condition_field}={expected_value}."
            )


def _require_preservation(operation: dict[str, Any]) -> None:
    for field in ("preserveOtherValues", "preserveUnspecifiedRows"):
        if operation.get(field, True) is not True:
            raise AdapterError(f"{field} must be true; unrequested changes are not supported.")


def _normalized_blueprint(
    contract: dict[str, Any], design: dict[str, Any]
) -> dict[str, Any]:
    if not isinstance(design, dict):
        raise AdapterError("Normalized design input must be a JSON object.")
    operations = design.get("operations")
    if not isinstance(operations, list) or not operations:
        raise AdapterError("Design must contain at least one operation.")
    entities = _entity_map(contract)
    normalized_ops = []
    for index, raw in enumerate(operations, start=1):
        if not isinstance(raw, dict):
            raise AdapterError(f"Operation {index} must be an object.")
        operation = dict(raw)
        operation.setdefault("id", f"OP-{index:03d}")
        operation.setdefault("action", "update")
        operation.setdefault("preserveOtherValues", True)
        operation.setdefault("preserveUnspecifiedRows", True)
        _require_preservation(operation)
        entity = entities.get(operation.get("entity"))
        if entity is not None:
            target = dict(operation.get("targetKey") or {})
            operation["targetKey"] = {
                field: _normalize_field_value(entity, field, value, operation["id"])
                for field, value in target.items()
            }
            values = dict(operation.get("values") or {})
            normalized_values = {
                field: _normalize_field_value(entity, field, value, operation["id"])
                for field, value in values.items()
            }
            operation["values"] = _omit_create_blank_values(
                entity,
                normalized_values,
                operation["action"],
                operation["id"],
            )
        normalized_ops.append(operation)
    blueprint = {
        "task": {
            "name": contract["task"]["name"],
            "code": contract["task"]["code"],
        },
        "operations": normalized_ops,
        "resolvedScope": design.get("resolvedScope", {}),
        "explicitDefaults": design.get("explicitDefaults", []),
        "preservedValues": design.get("preservedValues", []),
        "prerequisites": design.get("prerequisites", []),
        "warnings": design.get("warnings", []),
    }
    if "referenceContext" in design:
        blueprint["referenceContext"] = design["referenceContext"]
    blueprint["firstTimeUiDefaulting"] = _first_time_ui_defaulting(
        contract, normalized_ops
    )
    return blueprint


def _first_time_ui_defaulting(
    contract: dict[str, Any], operations: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Return a report-only summary of the UI's first-time-row behavior.

    The plan deliberately does not add values to ``operation["values"]``. The
    FSM import service does not invoke the UI's Reference Integration defaulting
    method, and two entity defaults do not have direct CSV headers.
    """

    entities = _entity_map(contract)
    notices: list[dict[str, Any]] = []
    for operation in operations:
        if operation.get("action") != "create":
            continue
        entity_name = operation.get("entity")
        entity = entities.get(entity_name)
        if entity is None:
            continue
        plan = _task_specific_entity_rules(entity).get("firstTimeUiDefaultPlan")
        if not isinstance(plan, dict):
            continue
        values = operation.get("values")
        values = values if isinstance(values, dict) else {}

        fixed_defaults = []
        for raw_default in plan.get("fixedEntityDefaults", []):
            if not isinstance(raw_default, dict):
                continue
            default = dict(raw_default)
            csv_field = default.get("csvField")
            user_supplied = (
                isinstance(csv_field, str)
                and values.get(csv_field) not in (None, "")
            )
            default["effectiveUiValue"] = (
                str(values[csv_field])
                if user_supplied
                else str(default.get("defaultValue", ""))
            )
            default["valueSource"] = (
                "user_supplied" if user_supplied else "entity_default"
            )
            fixed_defaults.append(default)

        reference_accounts = []
        for raw_account in plan.get("referenceIntegrationAccounts", []):
            if not isinstance(raw_account, dict):
                continue
            account = dict(raw_account)
            csv_field = account.get("csvField")
            account["candidateInputState"] = (
                "user_supplied"
                if isinstance(csv_field, str) and values.get(csv_field) not in (None, "")
                else "not_supplied"
            )
            reference_accounts.append(account)

        notices.append(
            {
                "operationId": operation["id"],
                "entity": entity_name,
                "mode": plan.get("mode", "report_only"),
                "candidatePolicy": plan.get("candidatePolicy", "report_only"),
                "preconditions": list(plan.get("preconditions", [])),
                "fixedEntityDefaults": fixed_defaults,
                "referenceIntegrationAccounts": reference_accounts,
                "lookupOutcome": plan.get("lookupOutcome", ""),
            }
        )
    return notices


def _validate_blueprint(
    contract: dict[str, Any],
    blueprint: dict[str, Any],
    baseline: PackageData | None = None,
    *, require_fresh_references: bool = True,
) -> None:
    task = blueprint.get("task")
    if task != {"name": contract["task"]["name"], "code": contract["task"]["code"]}:
        raise AdapterError("Blueprint task identity differs from the adapter contract.")
    operations = blueprint.get("operations")
    if not isinstance(operations, list) or not operations:
        raise AdapterError("Blueprint must contain at least one operation.")
    entities = _entity_map(contract)
    allowed = set(contract["normalization"]["supportedOperations"])
    satisfied = _satisfied_prerequisites(blueprint, contract)
    if baseline is not None:
        _validate_reference_provenance(
            blueprint, baseline, satisfied, require_fresh=require_fresh_references
        )
    resolved_bu_contexts = (
        _derive_and_verify_erp_bu_context(contract, blueprint, baseline, satisfied)
        if baseline is not None
        else {}
    )
    rest_warnings = _additional_rest_check_warnings(contract, blueprint, baseline)
    deferred = {(w["operationId"], w["entity"], w["field"]) for w in rest_warnings}
    if rest_warnings:
        blueprint["referenceValidationWarnings"] = rest_warnings
    else:
        blueprint.pop("referenceValidationWarnings", None)
    baseline_indexes = (
        {
            name: _row_index(baseline, entity, allow_blank_enterprise=True)
            for name, entity in entities.items()
        }
        if baseline is not None
        else {}
    )
    seen_ids: set[str] = set()
    seen_targets: set[tuple[str, tuple[str, ...]]] = set()
    for position, operation in enumerate(operations, start=1):
        if not isinstance(operation, dict):
            raise AdapterError(f"Operation {position} must be an object.")
        _require_preservation(operation)
        operation_id = operation.get("id")
        if not isinstance(operation_id, str) or not operation_id:
            raise AdapterError(f"Operation {position} has no stable id.")
        if operation_id in seen_ids:
            raise AdapterError(f"Duplicate operation id {operation_id!r}.")
        seen_ids.add(operation_id)
        action = operation.get("action")
        if action not in allowed:
            raise AdapterError(f"Operation {operation_id} uses unsupported action {action!r}.")
        entity_name = operation.get("entity")
        if entity_name not in entities:
            raise AdapterError(f"Operation {operation_id} names unknown entity {entity_name!r}.")
        entity = entities[entity_name]
        blocked = {
            item["field"]: item
            for item in entity.get("conditionallyBlockedFields", [])
        }
        values = operation.get("values")
        if not isinstance(values, dict) or not values:
            raise AdapterError(f"Operation {operation_id} must supply values.")
        target = operation.get("targetKey")
        if not isinstance(target, dict) or set(target) != set(entity["keyFields"]):
            raise AdapterError(
                f"Operation {operation_id} targetKey must contain exactly "
                f"{entity['keyFields']}."
            )
        for field in entity["keyFields"]:
            _validate_field_value(entity, field, target[field], operation_id)
        target_tuple = _target_tuple(entity, target)
        if any(value == "" for value in target_tuple):
            raise AdapterError(f"Operation {operation_id} has a blank target key.")
        target_identity = (entity_name, target_tuple)
        if target_identity in seen_targets:
            raise AdapterError(
                f"More than one operation targets {entity_name} {target_tuple!r}."
            )
        seen_targets.add(target_identity)
        baseline_row: dict[str, str] | None = None
        if baseline is not None:
            matches = baseline_indexes[entity_name]
            if action == "update" and target_tuple not in matches:
                raise AdapterError(
                    f"Operation {operation_id} target {target_tuple!r} does not exist "
                    "exactly once in the fresh current export."
                )
            if action == "create" and target_tuple in matches:
                raise AdapterError(
                    f"Operation {operation_id} create target {target_tuple!r} already "
                    "exists in the fresh current export."
                )
            baseline_row = matches.get(target_tuple)

        resolved_bu_context = resolved_bu_contexts.get(operation_id)
        if (
            action == "update"
            and baseline_row is not None
            and resolved_bu_context is not None
            and baseline_row.get(resolved_bu_context["ledgerNameField"], "")
            != resolved_bu_context["ledgerName"]
        ):
            raise AdapterError(
                f"Operation {operation_id} target row has "
                f"{resolved_bu_context['ledgerNameField']} "
                f"{baseline_row.get(resolved_bu_context['ledgerNameField'], '')!r}, "
                "which does not match the ERP primary-ledger receipt."
            )

        for field in entity["keyFields"]:
            if action != "create" or field not in blocked:
                continue
            blocker = blocked[field]
            if blocker.get("status") == "blocked":
                raise AdapterError(
                    f"Operation {operation_id} cannot create blocked key field "
                    f"{entity_name}.{field}: {blocker['reason']}"
                )
            context = _receipt_context(
                entity, blocker, values, baseline_row, operation_id
            )
            if not _has_satisfied_prerequisite(
                satisfied,
                operation_id=operation_id,
                entity_name=entity_name,
                field=field,
                resolver=blocker["resolver"],
                requested_value=target[field],
                context=context,
                required_values=_required_receipt_values(entity, blocker["resolver"]),
            ):
                raise AdapterError(
                    f"Operation {operation_id} creates conditionally blocked key field "
                    f"{entity_name}.{field}: {blocker['reason']}. A satisfied receipt "
                    "must bind the operation, exact requested value, and required context."
                )
        if action == "create":
            create_inputs = {**target, **values}
            missing = [
                field
                for field in entity.get("requiredFields", [])
                if field not in create_inputs or create_inputs[field] in (None, "")
            ]
            if missing:
                raise AdapterError(
                    f"Operation {operation_id} creates {entity['name']} without "
                    f"required fields: {missing}."
                )
        prohibited = set(entity["keyFields"]) | set(entity["auditFields"])
        unknown = set(values) - set(entity["headers"])
        if unknown:
            raise AdapterError(
                f"Operation {operation_id} supplies unknown fields: {sorted(unknown)}."
            )
        invalid = set(values) & prohibited
        if invalid:
            raise AdapterError(
                f"Operation {operation_id} cannot change key/audit fields: {sorted(invalid)}."
            )
        for field in values:
            _validate_field_value(entity, field, values[field], operation_id)
        _validate_field_rules(entity, operation, values, baseline_row)
        # Declarations govern requested inputs, not the unchanged baseline row.
        # Keys enter create through targetKey; they never become mutable values.
        contract_name = "createFields" if action == "create" else "updateFields"
        field_contract = entity.get(contract_name)
        if not isinstance(field_contract, dict) or not field_contract:
            raise AdapterError(
                f"Operation {operation_id} has no declared {contract_name} contract."
            )
        requested_fields = set(values)
        if action == "create":
            requested_fields.update(target)
        unsupported = requested_fields - set(field_contract)
        if unsupported:
            raise AdapterError(
                f"Operation {operation_id} supplies fields outside {contract_name}: "
                f"{sorted(unsupported)}."
            )
        for field, value in values.items():
            if field not in blocked:
                continue
            if (operation_id, entity_name, field) in deferred:
                continue
            blocker = blocked[field]
            if blocker.get("status") == "blocked":
                raise AdapterError(
                    f"Operation {operation_id} cannot change blocked field "
                    f"{entity_name}.{field}: {blocker['reason']}"
                )
            context = _receipt_context(
                entity, blocker, values, baseline_row, operation_id
            )
            if _has_satisfied_prerequisite(
                satisfied,
                operation_id=operation_id,
                entity_name=entity_name,
                field=field,
                resolver=blocker["resolver"],
                requested_value=value,
                context=context,
                required_values=_required_receipt_values(entity, blocker["resolver"]),
            ):
                continue
            raise AdapterError(
                f"Operation {operation_id} changes conditionally blocked field "
                f"{entity_name}.{field}: {blocker['reason']}. A satisfied receipt "
                "must bind the operation, exact requested value, and required context."
            )
    if "firstTimeUiDefaulting" in blueprint:
        expected_defaulting = _first_time_ui_defaulting(contract, operations)
        if blueprint["firstTimeUiDefaulting"] != expected_defaulting:
            raise AdapterError(
                "Blueprint firstTimeUiDefaulting differs from the task's "
                "declarative report-only UI default plan."
            )


def _requirements(
    contract: dict[str, Any], blueprint: dict[str, Any]
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    number = 1
    for operation in blueprint["operations"]:
        target_key_text = json.dumps(
            operation["targetKey"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        base = {
            "operationId": operation["id"],
            "entity": operation["entity"],
            "targetKey": operation["targetKey"],
        }
        result.append(
            {
                "id": f"REQ-{number:03d}",
                "kind": "target",
                "requirement": (
                    f"{operation['action']} exactly one {operation['entity']} record "
                    f"identified by {target_key_text}"
                ),
                **base,
            }
        )
        number += 1
        for field in sorted(operation["values"]):
            value = str(operation["values"][field])
            result.append(
                {
                    "id": f"REQ-{number:03d}",
                    "kind": "value",
                    "requirement": f"Persist {operation['entity']}.{field}={value}",
                    "field": field,
                    "requestedValue": value,
                    **base,
                }
            )
            number += 1
        # A create has no pre-existing target row whose values can be preserved.
        # Unspecified fields are governed by the explicit create values and the
        # package schema; only updates need a target-level preservation check.
        if operation["action"] == "update":
            result.append(
                {
                    "id": f"REQ-{number:03d}",
                    "kind": "preserve_target",
                    "requirement": "Preserve every other non-audit value on the target record",
                    **base,
                }
            )
            number += 1
        result.append(
            {
                "id": f"REQ-{number:03d}",
                "kind": "preserve_rows",
                "requirement": "Preserve every unspecified record and non-audit value",
                **base,
            }
        )
        number += 1
    return result


def _requirement_contract(
    contract: dict[str, Any], blueprint: dict[str, Any], requirements: list[Any]
) -> list[dict[str, Any]]:
    expected = _requirements(contract, blueprint)
    if requirements != expected:
        raise AdapterError(
            "Requirements JSON is stale or differs from the deterministic blueprint requirements."
        )
    return expected


def normalize_design(
    contract: dict[str, Any],
    baseline_path: Path,
    request_path: Path,
    design_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    baseline = _read_package(baseline_path, contract)
    design = _read_json(design_path)
    blueprint = _normalized_blueprint(contract, design)
    _validate_blueprint(contract, blueprint, baseline)
    requirements = _requirements(contract, blueprint)
    design_sha = _sha256_bytes(_canonical_bytes(blueprint))
    preview = {
        "schemaVersion": SCHEMA_VERSION,
        "task": blueprint["task"],
        "requestSha256": _sha256_path(request_path),
        "designSha256": design_sha,
        "baselineSha256": baseline.archive_sha256,
        "operations": [
            {
                "id": operation["id"],
                "action": operation["action"],
                "entity": operation["entity"],
                "targetKey": operation["targetKey"],
                "requestedValues": operation["values"],
                "preserveOtherValues": operation.get("preserveOtherValues", True),
                "preserveUnspecifiedRows": operation.get("preserveUnspecifiedRows", True),
            }
            for operation in blueprint["operations"]
        ],
        "explicitDefaults": blueprint["explicitDefaults"],
        "enterpriseIdDefaults": blueprint.get("enterpriseIdDefaults", {}),
        "firstTimeUiDefaulting": blueprint["firstTimeUiDefaulting"],
        "preservedValues": blueprint["preservedValues"],
        "prerequisites": blueprint["prerequisites"],
        "referenceContext": blueprint.get("referenceContext"),
        "warnings": blueprint["warnings"],
        "referenceValidationWarnings": blueprint.get("referenceValidationWarnings", []),
        "requirementCount": len(requirements),
    }
    return blueprint, preview, requirements


def _candidate_rows(
    contract: dict[str, Any],
    baseline: PackageData,
    blueprint: dict[str, Any],
) -> dict[str, list[dict[str, str]]]:
    entities = _entity_map(contract)
    output: dict[str, list[dict[str, str]]] = {name: [] for name in entities}
    for operation in blueprint["operations"]:
        entity = entities[operation["entity"]]
        key = _target_tuple(entity, operation["targetKey"])
        if operation["action"] == "update":
            row = dict(_row_index(baseline, entity, allow_blank_enterprise=True)[key])
        elif operation["action"] == "create":
            row = {header: "" for header in entity["headers"]}
            row.update({field: str(value) for field, value in operation["targetKey"].items()})
        else:
            raise AdapterError(f"Unsupported action {operation['action']!r}.")
        row.update({field: str(value) for field, value in operation["values"].items()})
        for field in entity["auditFields"]:
            row[field] = ""
        output[entity["name"]].append(row)
    for entity_name, rows in output.items():
        entity = entities[entity_name]
        rows.sort(key=lambda row: _row_key(entity, row))
    return output


def _write_candidate(
    template: PackageData,
    baseline: PackageData,
    contract: dict[str, Any],
    rows: dict[str, list[dict[str, str]]],
    output_path: Path,
) -> None:
    entity_by_member = {
        entity["member"]: entity for entity in contract["package"]["entities"]
    }
    metadata_member = contract["package"]["metadataMember"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "x") as archive:
        for member in template.member_names:
            if member in entity_by_member:
                entity = entity_by_member[member]
                content = _csv_bytes(entity["headers"], rows[entity["name"]])
                member_info = template.member_infos[member]
            elif member == metadata_member:
                content = baseline.member_bytes[member]
                member_info = baseline.member_infos[member]
            else:
                content = template.member_bytes[member]
                member_info = template.member_infos[member]
            archive.writestr(member_info, content)


def _semantic_issues(
    contract: dict[str, Any],
    candidate: PackageData,
    baseline: PackageData,
    blueprint: dict[str, Any],
    requirements: list[dict[str, Any]],
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    entities = _entity_map(contract)
    expected_targets: set[tuple[str, tuple[str, ...]]] = set()
    for operation in blueprint["operations"]:
        entity = entities[operation["entity"]]
        key = _target_tuple(entity, operation["targetKey"])
        expected_targets.add((entity["name"], key))
        candidate_rows = _row_index(candidate, entity)
        baseline_rows = _row_index(baseline, entity, allow_blank_enterprise=True)
        row = candidate_rows.get(key)
        if row is None:
            issues.append(
                {"code": "MISSING_TARGET", "message": f"Candidate lacks {entity['name']} {key!r}."}
            )
            continue
        before = baseline_rows.get(key, {header: "" for header in entity["headers"]})
        for field, value in operation["values"].items():
            if row[field] != str(value):
                issues.append(
                    {"code": "VALUE_MISMATCH", "message": f"{entity['name']} {key!r} {field} is {row[field]!r}, expected {str(value)!r}."}
                )
        if operation["action"] == "update":
            allowed = set(operation["values"]) | set(entity["auditFields"])
            for field in entity["headers"]:
                if field not in allowed and row[field] != before[field]:
                    issues.append(
                        {"code": "UNEXPECTED_CHANGE", "message": f"{entity['name']} {key!r} changed preserved field {field}."}
                    )
        elif operation["action"] == "create":
            expected = _candidate_rows(contract, baseline, {"operations": [operation]})[entity["name"]][0]
            checked = set(operation["values"]) | set(entity["auditFields"])
            for field in entity["headers"]:
                if field not in checked and row[field] != expected[field]:
                    issues.append(
                        {"code": "UNEXPECTED_CHANGE", "message": f"{entity['name']} {key!r} populated unrequested create field {field}."}
                    )
        for field in entity["auditFields"]:
            if row[field] != "":
                issues.append(
                    {"code": "AUDIT_FIELD_POPULATED", "message": f"{entity['name']} {key!r} audit field {field} is not blank."}
                )
    for entity in contract["package"]["entities"]:
        for row in candidate.rows[entity["name"]]:
            identity = (entity["name"], _row_key(entity, row))
            if identity not in expected_targets:
                issues.append(
                    {"code": "UNEXPECTED_ROW", "message": f"Candidate contains unrequested {entity['name']} row {identity[1]!r}."}
                )
    if {item["id"] for item in requirements} != {
        item["id"] for item in _requirements(contract, blueprint)
    }:
        issues.append(
            {"code": "REQUIREMENT_COVERAGE", "message": "Requirement IDs do not cover the normalized blueprint."}
        )
    return issues


def validate_candidate(
    contract: dict[str, Any],
    template_path: Path,
    baseline_path: Path,
    blueprint_path: Path,
    requirements_path: Path,
    candidate_path: Path,
) -> dict[str, Any]:
    template = _read_package(template_path, contract)
    baseline = _read_package(baseline_path, contract)
    candidate = _read_package(candidate_path, contract)
    _validate_source_pair(contract, template, baseline)
    blueprint = _read_json(blueprint_path)
    requirements = _read_json(requirements_path)
    _validate_blueprint(contract, blueprint, baseline)
    if not isinstance(requirements, list):
        raise AdapterError("Requirements file must contain a JSON array.")
    _requirement_contract(contract, blueprint, requirements)
    expected_fingerprint = contract["package"]["schemaFingerprint"]
    fingerprints = {
        "template": _schema_fingerprint(contract, template),
        "baseline": _schema_fingerprint(contract, baseline),
        "candidate": _schema_fingerprint(contract, candidate),
    }
    issues = _semantic_issues(contract, candidate, baseline, blueprint, requirements)
    metadata_member = contract["package"]["metadataMember"]
    if candidate.member_bytes[metadata_member] != baseline.member_bytes[metadata_member]:
        issues.append(
            {
                "code": "METADATA_PROVENANCE",
                "message": (
                    f"{metadata_member} must be preserved byte-for-byte from the fresh "
                    "current-data baseline, not the template-only export."
                ),
            }
        )
    for label, fingerprint in fingerprints.items():
        if fingerprint != expected_fingerprint:
            issues.append(
                {"code": "SCHEMA_FINGERPRINT", "message": f"{label} schema fingerprint {fingerprint} differs from {expected_fingerprint}."}
            )
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS" if not issues else "FAIL",
        "task": contract["task"],
        "candidateSha256": candidate.archive_sha256,
        "templateSha256": template.archive_sha256,
        "baselineSha256": baseline.archive_sha256,
        "designSha256": _sha256_bytes(_canonical_bytes(blueprint)),
        "schemaFingerprint": expected_fingerprint,
        "memberInventory": candidate.member_names,
        "rowCounts": {
            entity["member"]: len(candidate.rows[entity["name"]])
            for entity in contract["package"]["entities"]
        },
        "requirementIds": [item["id"] for item in requirements],
        "errors": issues,
        "warnings": blueprint.get("warnings", []),
        "unresolvedWarnings": blueprint.get("warnings", []),
        "referenceValidationWarnings": blueprint.get("referenceValidationWarnings", []),
    }


def build_candidate(
    contract: dict[str, Any],
    template_path: Path,
    baseline_path: Path,
    blueprint_path: Path,
    requirements_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    _validate_new_outputs(
        [output_path],
        [template_path, baseline_path, blueprint_path, requirements_path],
    )
    template = _read_package(template_path, contract)
    baseline = _read_package(baseline_path, contract)
    _validate_source_pair(contract, template, baseline)
    blueprint = _read_json(blueprint_path)
    requirements = _read_json(requirements_path)
    _validate_blueprint(contract, blueprint, baseline)
    if not isinstance(requirements, list):
        raise AdapterError("Requirements file must contain a JSON array.")
    _requirement_contract(contract, blueprint, requirements)
    rows = _candidate_rows(contract, baseline, blueprint)
    _write_candidate(template, baseline, contract, rows, output_path)
    result = validate_candidate(
        contract,
        template_path,
        baseline_path,
        blueprint_path,
        requirements_path,
        output_path,
    )
    if result["status"] != "PASS":
        raise AdapterError(
            "Generated candidate failed semantic validation: "
            + "; ".join(issue["message"] for issue in result["errors"])
        )
    first_time_defaulting = blueprint.get("firstTimeUiDefaulting")
    if first_time_defaulting is None:
        first_time_defaulting = _first_time_ui_defaulting(
            contract, blueprint["operations"]
        )
    defaulting_by_operation = {
        notice["operationId"]: notice
        for notice in first_time_defaulting
    }
    result["businessSummary"] = [
        {
            "operationId": operation["id"],
            "action": operation["action"],
            "entity": operation["entity"],
            "targetKey": operation["targetKey"],
            "values": operation["values"],
            "firstTimeUiDefaulting": defaulting_by_operation.get(operation["id"]),
        }
        for operation in blueprint["operations"]
    ]
    result["firstTimeUiDefaulting"] = list(defaulting_by_operation.values())
    result["structuralValidator"] = "fsm_task_adapter.py exact-task package reader"
    result["semanticValidator"] = "fsm_task_adapter.py blueprint/baseline validator"
    result["notImported"] = True
    return result


def determinism_check(
    contract: dict[str, Any],
    template_path: Path,
    baseline_path: Path,
    blueprint_path: Path,
    requirements_path: Path,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="fscr-adapter-") as directory:
        first = Path(directory) / "candidate-a.zip"
        second = Path(directory) / "candidate-b.zip"
        build_candidate(
            contract, template_path, baseline_path, blueprint_path, requirements_path, first
        )
        build_candidate(
            contract, template_path, baseline_path, blueprint_path, requirements_path, second
        )
        first_sha = _sha256_path(first)
        second_sha = _sha256_path(second)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS" if first_sha == second_sha else "FAIL",
        "firstSha256": first_sha,
        "secondSha256": second_sha,
        "identicalBytes": first_sha == second_sha,
    }


def reconcile(
    contract: dict[str, Any],
    baseline_path: Path,
    candidate_path: Path,
    blueprint_path: Path,
    requirements_path: Path,
    export_path: Path,
    *,
    readback_evidence: dict[str, Any] | None = None,
    import_request_id: str | None = None,
    target_url: str | None = None,
) -> dict[str, Any]:
    from readback_evidence import bind_readback_result

    baseline = _read_package(baseline_path, contract)
    candidate = _read_package(candidate_path, contract)
    persisted = _read_package(export_path, contract)
    for label, package in (("Candidate", candidate), ("Persisted export", persisted)):
        for field in ("ProcessEnv", "ProcessRelease"):
            if package.metadata[field] != baseline.metadata[field]:
                raise AdapterError(
                    f"{label} {field} differs from baseline: "
                    f"{package.metadata[field]!r} versus {baseline.metadata[field]!r}."
                )
    blueprint = _read_json(blueprint_path)
    requirements = _read_json(requirements_path)
    _validate_blueprint(contract, blueprint, baseline, require_fresh_references=False)
    if not isinstance(requirements, list):
        raise AdapterError("Requirements file must contain a JSON array.")
    _requirement_contract(contract, blueprint, requirements)
    entities = _entity_map(contract)
    operation_map = {operation["id"]: operation for operation in blueprint["operations"]}
    indexes = {
        name: {
            "baseline": _row_index(baseline, entity, allow_blank_enterprise=True),
            "candidate": _row_index(candidate, entity),
            "persisted": _row_index(persisted, entity, allow_blank_enterprise=True),
        }
        for name, entity in entities.items()
    }
    matrix = []
    for requirement in requirements:
        entity = entities[requirement["entity"]]
        key = _target_tuple(entity, requirement["targetKey"])
        rows = indexes[entity["name"]]
        before = rows["baseline"].get(key)
        candidate_row = rows["candidate"].get(key)
        persisted_row = rows["persisted"].get(key)
        kind = requirement["kind"]
        passed = True
        requested: Any = requirement.get("requestedValue", "record present")
        candidate_value: Any = "present" if candidate_row is not None else "missing"
        persisted_value: Any = "present" if persisted_row is not None else "missing"
        detail = ""
        if kind == "target":
            passed = candidate_row is not None and persisted_row is not None
        elif kind == "value":
            field = requirement["field"]
            requested = str(requirement["requestedValue"])
            candidate_value = "" if candidate_row is None else candidate_row[field]
            persisted_value = "" if persisted_row is None else persisted_row[field]
            passed = candidate_value == requested and persisted_value == requested
        elif kind == "preserve_target":
            operation = operation_map[requirement["operationId"]]
            allowed = set(operation["values"]) | set(entity["auditFields"])
            differences = []
            if before is None or candidate_row is None or persisted_row is None:
                differences.append("target row unavailable")
            else:
                for field in entity["headers"]:
                    if field not in allowed and (
                        candidate_row[field] != before[field]
                        or persisted_row[field] != before[field]
                    ):
                        differences.append(field)
            requested = "unchanged"
            candidate_value = "unchanged" if not differences else differences
            persisted_value = "unchanged" if not differences else differences
            passed = not differences
            detail = "Preserved all non-requested, non-audit target fields."
        elif kind == "preserve_rows":
            touched = {
                (
                    op["entity"],
                    _target_tuple(entities[op["entity"]], op["targetKey"]),
                )
                for op in blueprint["operations"]
            }
            differences = []
            for entity_name, current_entity in entities.items():
                baseline_rows = indexes[entity_name]["baseline"]
                persisted_rows = indexes[entity_name]["persisted"]
                for row_key in sorted(set(baseline_rows) | set(persisted_rows)):
                    if (entity_name, row_key) in touched:
                        continue
                    left = baseline_rows.get(row_key)
                    right = persisted_rows.get(row_key)
                    if left is None or right is None:
                        differences.append(f"{entity_name}:{row_key}:row")
                        continue
                    for field in current_entity["headers"]:
                        if field not in current_entity["auditFields"] and left[field] != right[field]:
                            differences.append(f"{entity_name}:{row_key}:{field}")
            requested = "unchanged"
            candidate_value = "not populated by design"
            persisted_value = "unchanged" if not differences else differences[:25]
            passed = not differences
            detail = f"Unexpected difference count: {len(differences)}."
        matrix.append(
            {
                "requirementId": requirement["id"],
                "requirement": requirement["requirement"],
                "requested": requested,
                "candidate": candidate_value,
                "persisted": persisted_value,
                "passed": passed,
                "detail": detail,
            }
        )
    comparison = {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS" if all(row["passed"] for row in matrix) else "FAIL",
        "task": contract["task"],
        "baselineSha256": baseline.archive_sha256,
        "candidateSha256": candidate.archive_sha256,
        "exportSha256": persisted.archive_sha256,
        "requirementMatrix": matrix,
        "mismatchCount": sum(not row["passed"] for row in matrix),
    }
    return bind_readback_result(
        comparison, readback_evidence,
        task_code=contract["task"]["code"],
        environment=baseline.metadata["ProcessEnv"],
        baseline_sha256=baseline.archive_sha256,
        candidate_sha256=candidate.archive_sha256,
        export_sha256=persisted.archive_sha256,
        import_request_id=import_request_id,
        target_url=target_url,
    )


def make_rollback(
    contract: dict[str, Any],
    template_path: Path,
    before_path: Path,
    current_path: Path,
    forward_blueprint_path: Path,
    rollback_blueprint_path: Path,
    rollback_requirements_path: Path,
    output_path: Path,
    prerequisites_path: Path | None = None,
    reference_context_path: Path | None = None,
) -> dict[str, Any]:
    _validate_new_outputs(
        [rollback_blueprint_path, rollback_requirements_path, output_path],
        [template_path, before_path, current_path, forward_blueprint_path]
        + ([prerequisites_path] if prerequisites_path is not None else [])
        + ([reference_context_path] if reference_context_path is not None else []),
    )
    before = _read_package(before_path, contract)
    current = _read_package(current_path, contract)
    if before.metadata["ProcessEnv"] != current.metadata["ProcessEnv"]:
        raise AdapterError("Before and current rollback exports come from different environments.")
    if before.metadata["ProcessRelease"] != current.metadata["ProcessRelease"]:
        raise AdapterError("Before and current rollback exports come from different releases.")
    forward = _read_json(forward_blueprint_path)
    _validate_blueprint(contract, forward, before, require_fresh_references=False)
    if prerequisites_path is None:
        raise AdapterError(
            "Rollback requires --prerequisites: fresh validation receipts for the "
            "RB-OP operation IDs, restored values, and current-export BU context. "
            "Forward receipts cannot be reused or automatically rebound."
        )
    rollback_prerequisites = _read_json(prerequisites_path)
    if not isinstance(rollback_prerequisites, list):
        raise AdapterError("Rollback prerequisites must be a JSON array of bound receipts.")
    if reference_context_path is None:
        raise AdapterError("Rollback requires --reference-context for a fresh run bound to the current export.")
    rollback_context = _read_json(reference_context_path)
    if (isinstance(rollback_context, dict)
            and rollback_context.get("runId") == forward.get("referenceContext", {}).get("runId")):
        raise AdapterError("Rollback must use a new reference run; forward context cannot be reused.")
    entities = _entity_map(contract)
    operations = []
    for index, operation in enumerate(forward["operations"], start=1):
        if operation["action"] != "update":
            raise AdapterError("Automatic rollback currently supports update operations only.")
        entity = entities[operation["entity"]]
        key = _target_tuple(entity, operation["targetKey"])
        original_row = _row_index(before, entity, allow_blank_enterprise=True).get(key)
        current_row = _row_index(current, entity, allow_blank_enterprise=True).get(key)
        if original_row is None or current_row is None:
            raise AdapterError(f"Rollback target {entity['name']} {key!r} is missing.")
        for field, forward_value in operation["values"].items():
            if current_row[field] != str(forward_value):
                raise AdapterError(
                    f"Rollback target {entity['name']}.{field} no longer matches "
                    "the forward requested value; review concurrent changes first."
                )
        values = {field: original_row[field] for field in operation["values"]}
        operations.append(
            {
                "id": f"RB-OP-{index:03d}",
                "action": "update",
                "entity": entity["name"],
                "targetKey": operation["targetKey"],
                "values": values,
                "preserveOtherValues": True,
                "preserveUnspecifiedRows": True,
            }
        )
    design = {
        "operations": operations,
        "resolvedScope": forward.get("resolvedScope", {}),
        "explicitDefaults": [],
        "preservedValues": [],
        "prerequisites": rollback_prerequisites,
        "referenceContext": rollback_context,
        "warnings": [],
    }
    rollback = _normalized_blueprint(contract, design)
    _validate_blueprint(contract, rollback, current)
    requirements = _requirements(contract, rollback)
    _write_json(rollback_blueprint_path, rollback, exclusive=True)
    _write_json(rollback_requirements_path, requirements, exclusive=True)
    report = build_candidate(
        contract,
        template_path,
        current_path,
        rollback_blueprint_path,
        rollback_requirements_path,
        output_path,
    )
    report["rollbackOfDesignSha256"] = _sha256_bytes(_canonical_bytes(forward))
    report["rollbackScope"] = "Restore only fields changed by the forward blueprint."
    return report


def normalized_manifest(
    contract: dict[str, Any],
    package_path: Path,
    environment: str,
    base_url: str,
    template_only: bool,
) -> dict[str, Any]:
    package = _read_package(package_path, contract)
    if not isinstance(environment, str) or environment.strip() != package.metadata["ProcessEnv"]:
        raise AdapterError("Manifest environment must match the package ProcessEnv.")
    from readback_evidence import _host

    try:
        origin = _host(base_url)
    except ValueError as exc:
        raise AdapterError("Manifest base URL must be a complete HTTPS origin without a path.") from exc
    populated = [
        entity["member"]
        for entity in contract["package"]["entities"]
        if package.rows[entity["name"]]
    ]
    return {
        "environment": environment.strip(),
        "baseUrl": origin,
        "taskName": contract["task"]["name"],
        "taskCode": contract["task"]["code"],
        "status": package.metadata["ProcessStatus"],
        "templateOnly": template_only,
        "release": package.metadata["ProcessRelease"],
        "processId": package.metadata["ESSRequestId"],
        "schemaFingerprint": _schema_fingerprint(contract, package),
        "selectedTaskCodes": [contract["task"]["code"]],
        "definedTaskCodes": [contract["task"]["code"]],
        "members": package.member_names,
        "headers": {
            entity["member"]: package.headers[entity["name"]]
            for entity in contract["package"]["entities"]
        },
        "populatedMembers": populated,
        "unrelatedPopulatedMembers": [],
    }


def _bool_arg(value: str) -> bool:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise argparse.ArgumentTypeError("Expected true or false.")


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--contract", type=Path, default=_default_contract_path())
    parser.add_argument("--report", type=Path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    manifest = sub.add_parser("manifest", help="Normalize one exact-task source ZIP.")
    _add_common(manifest)
    manifest.add_argument("--package", type=Path, required=True)
    manifest.add_argument("--environment", required=True)
    manifest.add_argument("--base-url", required=True)
    manifest.add_argument("--template-only", type=_bool_arg, required=True)

    normalize = sub.add_parser("normalize", help="Validate a Codex-normalized business design.")
    _add_common(normalize)
    normalize.add_argument("--baseline", type=Path, required=True)
    normalize.add_argument("--request", type=Path, required=True)
    normalize.add_argument("--design", type=Path, required=True)
    normalize.add_argument("--blueprint-output", type=Path, required=True)
    normalize.add_argument("--preview-output", type=Path, required=True)
    normalize.add_argument("--requirements-output", type=Path, required=True)

    for name in ("build", "validate", "determinism"):
        command = sub.add_parser(name)
        _add_common(command)
        command.add_argument("--template", type=Path, required=True)
        command.add_argument("--baseline", type=Path, required=True)
        command.add_argument("--blueprint", type=Path, required=True)
        command.add_argument("--requirements", type=Path, required=True)
        if name == "build":
            command.add_argument("--output", type=Path, required=True)
        elif name == "validate":
            command.add_argument("--package", type=Path, required=True)

    rollback = sub.add_parser("rollback", help="Build a narrow rollback for a validated update.")
    _add_common(rollback)
    rollback.add_argument("--template", type=Path, required=True)
    rollback.add_argument("--before", type=Path, required=True)
    rollback.add_argument("--current", type=Path, required=True)
    rollback.add_argument("--forward-blueprint", type=Path, required=True)
    rollback.add_argument("--prerequisites", type=Path, required=True, help="JSON array of fresh RB-OP/value/current-export-bound receipts.")
    rollback.add_argument("--reference-context", type=Path, required=True, help="JSON context for the fresh rollback reference run and current export.")
    rollback.add_argument("--blueprint-output", type=Path, required=True)
    rollback.add_argument("--requirements-output", type=Path, required=True)
    rollback.add_argument("--output", type=Path, required=True)

    reconcile_parser = sub.add_parser("reconcile")
    _add_common(reconcile_parser)
    reconcile_parser.add_argument("--baseline", type=Path, required=True)
    reconcile_parser.add_argument("--candidate", type=Path, required=True)
    reconcile_parser.add_argument("--blueprint", type=Path, required=True)
    reconcile_parser.add_argument("--requirements", type=Path, required=True)
    reconcile_parser.add_argument("--export", type=Path, required=True)
    reconcile_parser.add_argument("--readback-evidence", type=Path,
                                  help="Observation from the governed post-import export.")
    reconcile_parser.add_argument("--import-request-id",
                                  help="Current Core Data Loader initiation request ID.")
    reconcile_parser.add_argument("--target-url",
                                  help="Explicit target Fusion URL for persisted verification.")
    return parser.parse_args(argv)


def _command_succeeded(command: str, result: dict[str, Any]) -> bool:
    if command == "manifest":
        return str(result.get("status", "")).strip().upper() in SUCCESS_STATUSES
    return result.get("status", "PASS") == "PASS"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    outputs_checked = False
    try:
        output_names = {"report", "output", "blueprint_output", "preview_output", "requirements_output"}
        path_arguments = {name: value for name, value in vars(args).items() if isinstance(value, Path)}
        _validate_new_outputs(
            [path for name, path in path_arguments.items() if name in output_names],
            [path for name, path in path_arguments.items() if name not in output_names],
        )
        outputs_checked = True
        contract = _load_contract(args.contract)
        if args.command == "manifest":
            result = normalized_manifest(
                contract,
                args.package,
                args.environment,
                args.base_url,
                args.template_only,
            )
        elif args.command == "normalize":
            blueprint, preview, requirements = normalize_design(
                contract, args.baseline, args.request, args.design
            )
            _write_json(args.blueprint_output, blueprint, exclusive=True)
            _write_json(args.preview_output, preview, exclusive=True)
            _write_json(args.requirements_output, requirements, exclusive=True)
            result = preview
        elif args.command == "build":
            result = build_candidate(
                contract,
                args.template,
                args.baseline,
                args.blueprint,
                args.requirements,
                args.output,
            )
        elif args.command == "validate":
            result = validate_candidate(
                contract,
                args.template,
                args.baseline,
                args.blueprint,
                args.requirements,
                args.package,
            )
        elif args.command == "determinism":
            result = determinism_check(
                contract,
                args.template,
                args.baseline,
                args.blueprint,
                args.requirements,
            )
        elif args.command == "rollback":
            result = make_rollback(
                contract,
                args.template,
                args.before,
                args.current,
                args.forward_blueprint,
                args.blueprint_output,
                args.requirements_output,
                args.output,
                args.prerequisites,
                args.reference_context,
            )
        elif args.command == "reconcile":
            from readback_evidence import read_observation

            result = reconcile(
                contract,
                args.baseline,
                args.candidate,
                args.blueprint,
                args.requirements,
                args.export,
                readback_evidence=read_observation(args.readback_evidence),
                import_request_id=args.import_request_id,
                target_url=args.target_url,
            )
        else:
            raise AdapterError(f"Unknown command {args.command!r}.")
        if args.report:
            _write_json(args.report, result, exclusive=True)
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if _command_succeeded(args.command, result) else 2
    except (AdapterError, OSError, ValueError) as exc:
        failure = {
            "schemaVersion": SCHEMA_VERSION,
            "status": "FAIL",
            "errors": [{"code": "ADAPTER_ERROR", "message": str(exc)}],
        }
        if outputs_checked and getattr(args, "report", None):
            try:
                _write_json(args.report, failure, exclusive=True)
            except OSError as report_exc:
                failure["errors"].append({"code": "REPORT_WRITE_ERROR", "message": str(report_exc)})
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
