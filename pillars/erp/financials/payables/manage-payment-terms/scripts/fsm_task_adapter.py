#!/usr/bin/env python3
"""Portable, data-driven FSM task adapter runtime.

This file is copied into a generated Nested task skill.  Task semantics live in
the adjacent e2e-adapter.json descriptor and ora-resource rule plan.  The
runtime performs offline package work only; it never connects to Fusion.

Reading guide: the adapter verifies the package contract, applies only the two
source-proven header defaults, checks payment-term line and cross-line rules,
then builds and reconciles an offline candidate. It never calls Fusion.
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
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit
from xml.etree import ElementTree


SCHEMA_VERSION = "fscr-fsm-task-adapter-v1"
MAX_MEMBER_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100
SUCCESS_STATUSES = frozenset({"COMPLETED", "SUCCEEDED", "SUCCESS"})


class AdapterError(ValueError):
    """A safe, user-correctable adapter failure."""


# Reference receipts are corroborating observations, never proof of a live import.
REFERENCE_MAX_AGE = timedelta(hours=24)


def _https_origin(value: Any) -> str:
    if not isinstance(value, str) or not value or any(c.isspace() for c in value):
        raise AdapterError("INVALID_ORIGIN: baseUrl must be an HTTPS origin.")
    try:
        parsed = urlsplit(value)
        host, port = parsed.hostname, parsed.port
    except ValueError as exc:
        raise AdapterError("INVALID_ORIGIN: invalid HTTPS origin.") from exc
    if (parsed.scheme.lower() != "https" or not host
            or len(host) > 253 or any(re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?", label) is None for label in host.split("."))
            or parsed.netloc.endswith(":") or port == 0
            or parsed.username is not None or parsed.password is not None
            or parsed.path not in ("", "/") or parsed.query or parsed.fragment
            or "?" in value or "#" in value):
        raise AdapterError("INVALID_ORIGIN: baseUrl must contain only an HTTPS host and optional port.")
    return "https://" + host.lower() + (f":{port}" if port not in (None, 443) else "")



def _reference_origin(value: Any) -> str:
    try:
        return _https_origin(value)
    except AdapterError as exc:
        raise AdapterError(f"REFERENCE_PROVENANCE: {exc}") from exc


def _reference_target(context: Any, baseline: Any = None) -> dict[str, str]:
    if (not isinstance(context, dict) or not isinstance(context.get("environment"), str)
            or not context["environment"].strip()):
        raise AdapterError("REFERENCE_PROVENANCE: independently selected referenceContext with environment and baseUrl is required; rerun preflight.")
    target = {"environment": context["environment"].strip(),
              "baseUrl": _reference_origin(context.get("baseUrl"))}
    if baseline is not None and baseline.metadata.get("ProcessEnv") != target["environment"]:
        raise AdapterError("REFERENCE_PROVENANCE: selected environment differs from the baseline export.")
    return target


def _new_reference_provenance(context: Any, baseline: Any = None) -> dict[str, str]:
    return {**_reference_target(context, baseline),
            "checkedAt": datetime.now(timezone.utc).isoformat()}


def _validate_reference_provenance(
    receipt: Any, context: Any, baseline: Any = None, *, now: datetime | None = None,
) -> None:
    target = _reference_target(context, baseline)
    if not isinstance(receipt, dict) or _reference_target(receipt) != target:
        raise AdapterError("REFERENCE_PROVENANCE: lookup target differs from the selected environment/origin; rerun preflight.")
    stamp = receipt.get("checkedAt")
    if (not isinstance(stamp, str) or re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)", stamp) is None):
        raise AdapterError("REFERENCE_PROVENANCE: checkedAt must be a timezone-aware RFC 3339 timestamp; rerun preflight.")
    try:
        checked = datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, OverflowError) as exc:
        raise AdapterError("REFERENCE_PROVENANCE: invalid checkedAt timestamp; rerun preflight.") from exc
    age = (now or datetime.now(timezone.utc)) - checked
    if age < timedelta(0) or age > REFERENCE_MAX_AGE:
        raise AdapterError("REFERENCE_PROVENANCE: lookup timestamp is in the future or older than 24 hours; rerun preflight.")


def _validate_blueprint_reference_provenance(blueprint: dict[str, Any], baseline: Any = None) -> None:
    receipts = [item for item in blueprint.get("prerequisites", [])
                if isinstance(item, dict) and item.get("status") in ("satisfied", "validation_skipped", "unavailable")]
    scope = blueprint.get("resolvedScope", {})
    if isinstance(scope, dict) and isinstance(scope.get("businessUnits"), list):
        receipts += [item for item in scope["businessUnits"] if isinstance(item, dict)]
    receipts += [op["setResolution"] for op in blueprint.get("operations", [])
                 if isinstance(op, dict) and isinstance(op.get("setResolution"), dict)]
    for receipt in receipts:
        _validate_reference_provenance(receipt.get("provenance"), blueprint.get("referenceContext"), baseline)


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


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_new_json(path: Path, value: Any) -> None:
    """Publish a new CLI artifact without replacing an existing file or link."""
    rendered = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
    except OSError as exc:
        raise AdapterError(f"Cannot write new JSON output {path}: {exc}") from exc


def _preflight_cli_outputs(args: argparse.Namespace) -> None:
    """Check every declared CLI destination against all inputs before side effects."""
    output_names = {"report", "output", "blueprint_output", "preview_output", "requirements_output"}
    paths = {name: value for name, value in vars(args).items() if isinstance(value, Path)}
    outputs = [path for name, path in paths.items() if name in output_names]
    inputs = [path for name, path in paths.items() if name not in output_names]
    _validate_new_outputs(outputs, inputs)


def _default_contract_path() -> Path:
    return Path(__file__).resolve().parents[1] / "e2e-adapter.json"


# Validate the descriptor before using it so every later operation has a
# trustworthy task identity, entity list, and schema version.
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
            continue
        if name in result:
            raise AdapterError(f"Metadata contains duplicate business object {name}.")
        attributes = [
            value.strip()
            for value in _first_xml_text(node, "XmlAttributeList").split(",")
            if value.strip()
        ]
        types = [
            value.strip()
            for value in _first_xml_text(node, "XmlAttributeTypeList").split(",")
        ]
        if len(attributes) != len(types):
            raise AdapterError(
                f"Metadata object {name} has {len(attributes)} attributes and {len(types)} types."
            )
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
    if metadata["ProcessStatus"].upper() not in SUCCESS_STATUSES:
        raise AdapterError(
            f"Package process status is not successful: {metadata['ProcessStatus']!r}."
        )
    if not metadata["ProcessEnv"] or not metadata["ProcessRelease"]:
        raise AdapterError("Package metadata must declare ProcessEnv and ProcessRelease.")
    object_contracts = _metadata_object_contracts(root)
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
        actual_sequence = actual["nodeSequence"]
        if not actual_sequence.isdigit() or int(actual_sequence) <= 0:
            raise AdapterError(
                f"Metadata node sequence for {entity['name']} must be a positive integer; "
                f"found {actual_sequence!r}."
            )
        for field, actual_type in actual["types"].items():
            if field not in entity["headers"]:
                raise AdapterError(
                    f"Metadata object {entity['name']} contains non-CSV attribute {field}."
                )
            if entity["types"].get(field, "") != actual_type:
                raise AdapterError(
                    f"Metadata type for {entity['name']}.{field} is {actual_type!r}, expected {entity['types'].get(field, '')!r}."
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
    for path in outputs:
        if path.is_symlink():
            raise AdapterError(f"Refusing to overwrite existing output link: {path}.")
    try:
        resolved_outputs = [path.resolve() for path in outputs]
        resolved_inputs = {path.resolve() for path in inputs}
    except (OSError, RuntimeError) as exc:
        raise AdapterError(f"Cannot resolve artifact paths: {exc}") from exc
    if len(resolved_outputs) != len(set(resolved_outputs)):
        raise AdapterError("Output paths must be distinct.")
    for path in resolved_outputs:
        if path in resolved_inputs:
            raise AdapterError(f"Output path overlaps an input: {path}.")
        if path.exists():
            raise AdapterError(f"Refusing to overwrite existing output: {path}.")
        if any(other != path and other in path.parents for other in resolved_outputs):
            raise AdapterError("Output paths must not contain one another.")
        if any(parent.exists() and not parent.is_dir() for parent in path.parents):
            raise AdapterError(f"Output parent is not a directory: {path}.")


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


def _key_component(entity: dict[str, Any], field: str, value: Any) -> str:
    """Compare declared integer keys numerically without rewriting CSV cells."""
    datatype = (entity.get("types", {}).get(field) or "string").strip().lower()
    if datatype not in {"int", "integer", "long", "short"}:
        return str(value)
    valid = (isinstance(value, int) and not isinstance(value, bool)) or (
        isinstance(value, str) and re.fullmatch(r"[+-]?\d+", value.strip()) is not None
    )
    if valid:
        try:
            return str(int(str(value).strip()))
        except ValueError:
            # Oversized/malformed input must remain an actionable adapter error.
            pass
    raise AdapterError(
        f"Field {entity['name']}.{field} requires a valid {datatype} integer key; "
        f"received {type(value).__name__}."
    )


def _row_key(entity: dict[str, Any], row: dict[str, str]) -> tuple[str, ...]:
    return tuple(_key_component(entity, field, row.get(field, "")) for field in entity["keyFields"])


def _target_tuple(entity: dict[str, Any], target: dict[str, Any]) -> tuple[str, ...]:
    return tuple(_key_component(entity, field, target.get(field, "")) for field in entity["keyFields"])


def _same_preserved_value(entity: dict[str, Any], field: str, left: str, right: str) -> bool:
    """Key spelling may vary; every non-key preserved value stays exact."""
    if field in entity["keyFields"]:
        return _key_component(entity, field, left) == _key_component(entity, field, right)
    return left == right


def _validate_field_value(
    entity: dict[str, Any], field: str, value: Any, operation_id: str
) -> None:
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
            candidate = value.strip()
            for parser in (date.fromisoformat, lambda item: datetime.strptime(item, "%Y/%m/%d").date()):
                try:
                    parser(candidate)
                    valid = True
                    break
                except ValueError:
                    pass
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


def _row_index(
    package: PackageData, entity: dict[str, Any]
) -> dict[tuple[str, ...], dict[str, str]]:
    if not entity["keyFields"]:
        raise AdapterError(f"Entity {entity['name']} has no source-backed key.")
    result: dict[tuple[str, ...], dict[str, str]] = {}
    for number, row in enumerate(package.rows[entity["name"]], start=2):
        key = _row_key(entity, row)
        if any(value == "" for value in key):
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
) -> set[tuple[str, str, str]]:
    declared = {
        (entity["name"], blocker["field"]): blocker["resolver"]
        for entity in contract["package"]["entities"]
        for blocker in entity.get("conditionallyBlockedFields", [])
    }
    satisfied: set[tuple[str, str, str]] = set()
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
            satisfied.add((entity, field, resolver))
    return satisfied


def _validate_set_reference(operation: dict[str, Any]) -> None:
    """Do not let unresolved names enter normalization or package building."""
    reference = operation.get("setReference")
    if reference is not None:
        if (not isinstance(reference, dict)
                or reference.get("kind") not in {"code", "name", "unspecified"}
                or not isinstance(reference.get("value"), str)
                or not reference["value"].strip()
                or operation.get("entity") != "AP_TERM_SUBSCRIPTION"):
            raise AdapterError("Use a valid setReference on a payment-term subscription.")
        target = operation.get("targetKey")
        if not isinstance(target, dict):
            raise AdapterError("A set reference needs a subscription target key.")
        code = target.get("SetCode")
        resolution = operation.get("setResolution", {})
        if reference["kind"] == "code":
            if code != reference["value"]:
                raise AdapterError("Preserve the supplied Set Code in the subscription key.")
        elif (not isinstance(resolution, dict)
                or resolution.get("status") != "resolved"
                or resolution.get("kind") != reference["kind"]
                or resolution.get("suppliedValue") != reference["value"]
                or not code or resolution.get("SetCode") != code):
            raise AdapterError("Resolve the set name or unspecified set to one Set Code before normalization.")


def _normalized_blueprint(
    contract: dict[str, Any], design: dict[str, Any]
) -> dict[str, Any]:
    if not isinstance(design, dict):
        raise AdapterError("Normalized design input must be a JSON object.")
    operations = design.get("operations")
    if not isinstance(operations, list) or not operations:
        raise AdapterError("Design must contain at least one operation.")
    normalized_ops = []
    explicit_defaults = list(design.get("explicitDefaults", []))
    for index, raw in enumerate(operations, start=1):
        if not isinstance(raw, dict):
            raise AdapterError(f"Operation {index} must be an object.")
        operation = dict(raw)
        _validate_set_reference(operation)
        operation.setdefault("id", f"OP-{index:03d}")
        operation.setdefault("action", "update")
        operation.setdefault("preserveOtherValues", True)
        operation.setdefault("preserveUnspecifiedRows", True)
        _apply_payment_term_header_defaults(contract, operation, explicit_defaults)
        normalized_ops.append(operation)
    resolver_findings = design.get("resolverFindings", [])
    if not isinstance(resolver_findings, list) or not all(isinstance(item, dict) for item in resolver_findings):
        raise AdapterError("Design resolverFindings must be an array of objects.")
    blueprint = {
        "task": {
            "name": contract["task"]["name"],
            "code": contract["task"]["code"],
        },
        "operations": normalized_ops,
        "resolvedScope": design.get("resolvedScope", {}),
        "referenceContext": design.get("referenceContext"),
        "explicitDefaults": explicit_defaults,
        "preservedValues": design.get("preservedValues", []),
        "prerequisites": design.get("prerequisites", []),
        "warnings": design.get("warnings", []),
        "resolverFindings": resolver_findings,
    }
    return blueprint


def _apply_payment_term_header_defaults(
    contract: dict[str, Any], operation: dict[str, Any], explicit_defaults: list[Any]
) -> None:
    """Write task-owned, import-safe values for omitted new payment-term headers.

    FSM CSV represents omitted attributes as blank cells.  The Payment Terms FSM
    importer rejects or does not safely default blank required header cells, so
    the adapter serializes EnabledFlag, Type, and StartDateActive explicitly.
    This is intentionally task-local and applies only to new AP_TERM_HEADER rows.
    """
    if operation.get("action") != "create" or operation.get("entity") != "AP_TERM_HEADER":
        return
    values = operation.get("values")
    if not isinstance(values, dict):
        return
    operation["values"] = dict(values)
    values = operation["values"]
    defaults = {
        "EnabledFlag": ("Y", "Task-owned import-safe enabled-state default."),
        "Type": ("STD", "Task-owned standard payment-term type default."),
        "StartDateActive": (
            date.today().strftime("%Y/%m/%d"),
            "Task-owned import-safe package-builder system-date default.",
        ),
    }
    for field, (value, reason) in defaults.items():
        if str(values.get(field, "")).strip():
            continue
        values[field] = value
        explicit_defaults.append(
            {
                "operationId": operation["id"],
                "entity": "AP_TERM_HEADER",
                "field": field,
                "value": value,
                "reason": reason,
            }
        )


def _is_populated(row: dict[str, Any], field: str) -> bool:
    """Match the ADF BC rule's non-null/non-empty treatment for CSV cells."""
    value = row.get(field)
    return value is not None and str(value).strip() != ""


def _decimal_value(row: dict[str, Any], field: str) -> Decimal:
    try:
        return Decimal(str(row[field]).strip())
    except (KeyError, InvalidOperation) as exc:  # field typing runs before this helper
        raise AdapterError(f"Payment Term Line has an invalid {field} value.") from exc


def _date_value(row: dict[str, Any], field: str) -> date:
    """Parse one already type-validated FSM date cell."""
    candidate = str(row[field]).strip()
    for parser in (date.fromisoformat, lambda item: datetime.strptime(item, "%Y/%m/%d").date()):
        try:
            return parser(candidate)
        except ValueError:
            pass
    raise AdapterError(f"Payment Term Header has an invalid {field} value.")


def _validate_payment_term_header_semantics(
    row: dict[str, Any], operation_id: str
) -> None:
    """Apply Payment Terms header rules to one effective header."""
    if _is_populated(row, "Type") and str(row["Type"]).strip() != "STD":
        raise AdapterError(
            f"Operation {operation_id} AP_TERM_HEADER.Type must be STD."
        )
    if _is_populated(row, "StartDateActive") and _is_populated(row, "EndDateActive"):
        if _date_value(row, "EndDateActive") < _date_value(row, "StartDateActive"):
            raise AdapterError(
                f"Operation {operation_id} AP_TERM_HEADER.EndDateActive must be on or after "
                "StartDateActive."
            )
    if _is_populated(row, "Rank"):
        candidate = str(row["Rank"]).strip()
        digits = candidate[1:] if candidate[:1] in {"+", "-"} else candidate
        if re.fullmatch(r"\d+", digits) is None or len(digits) > 18:
            raise AdapterError(
                f"Operation {operation_id} AP_TERM_HEADER.Rank must be a whole numeric value "
                "with at most 18 digits."
            )


def _validate_payment_term_rank_uniqueness(
    contract: dict[str, Any], blueprint: dict[str, Any], baseline: PackageData | None
) -> None:
    """Reject duplicate nonblank Rank values across the global header collection."""
    header_entity = _entity_map(contract).get("AP_TERM_HEADER")
    if header_entity is None:
        return
    rows: dict[tuple[str, ...], dict[str, Any]] = {}
    if baseline is not None:
        rows = {key: dict(value) for key, value in _row_index(baseline, header_entity).items()}
    for operation in blueprint["operations"]:
        if operation["entity"] != "AP_TERM_HEADER":
            continue
        target_tuple = _target_tuple(header_entity, operation["targetKey"])
        if baseline is None and operation["action"] == "update":
            continue
        row = rows.get(target_tuple, {field: "" for field in header_entity["headers"]})
        row.update(operation["targetKey"])
        row.update({field: str(value) for field, value in operation["values"].items()})
        rows[target_tuple] = row
    owners: dict[int, tuple[str, ...]] = {}
    for key, row in rows.items():
        if not _is_populated(row, "Rank"):
            continue
        candidate = str(row["Rank"]).strip()
        digits = candidate[1:] if candidate[:1] in {"+", "-"} else candidate
        if re.fullmatch(r"\d+", digits) is None or len(digits) > 18:
            raise AdapterError(
                f"AP_TERM_HEADER.Rank for {key!r} must be a whole numeric value with at most 18 digits."
            )
        rank = int(candidate)
        prior = owners.get(rank)
        if prior is not None and prior != key:
            raise AdapterError(
                f"AP_TERM_HEADER.Rank {row['Rank']!r} duplicates the global Payment Terms "
                f"rank used by {prior!r}."
            )
        owners[rank] = key


def _validate_payment_term_line_semantics(
    row: dict[str, Any], operation_id: str
) -> None:
    """Apply the AP_TERMS_LINES ADF BC rules to one effective line.

    Evidence: PaymentTermLineEO.xml, rules 0-19, in the reviewed Fusion
    CodeSearch branch.  This is intentionally task-local: it models Payment
    Terms business semantics, not a generic CSV rule.
    """
    due_percent = _is_populated(row, "DuePercent")
    due_amount = _is_populated(row, "DueAmount")
    if due_percent == due_amount:
        raise AdapterError(
            f"Operation {operation_id} AP_TERM_LINE must provide exactly one of "
            "DuePercent or DueAmount."
        )
    if due_percent and not (Decimal("0") <= _decimal_value(row, "DuePercent") <= Decimal("100")):
        raise AdapterError(f"Operation {operation_id} AP_TERM_LINE.DuePercent must be between 0 and 100.")
    if due_amount and _decimal_value(row, "DueAmount") < 0:
        raise AdapterError(f"Operation {operation_id} AP_TERM_LINE.DueAmount must be zero or greater.")

    due_days = _is_populated(row, "DueDays")
    due_dom = _is_populated(row, "DueDayOfMonth")
    due_months = _is_populated(row, "DueMonthsForward")
    fixed_date = _is_populated(row, "FixedDate")
    calendar = _is_populated(row, "Calendar")
    if due_days and _decimal_value(row, "DueDays") < 0:
        raise AdapterError(f"Operation {operation_id} AP_TERM_LINE.DueDays must be zero or greater.")
    if due_dom and not (Decimal("1") <= _decimal_value(row, "DueDayOfMonth") <= Decimal("31")):
        raise AdapterError(f"Operation {operation_id} AP_TERM_LINE.DueDayOfMonth must be between 1 and 31.")
    if due_months and _decimal_value(row, "DueMonthsForward") < 0:
        raise AdapterError(f"Operation {operation_id} AP_TERM_LINE.DueMonthsForward must be zero or greater.")
    if due_dom and not due_months:
        raise AdapterError(
            f"Operation {operation_id} AP_TERM_LINE.DueDayOfMonth requires DueMonthsForward."
        )
    if due_months and not due_dom:
        raise AdapterError(
            f"Operation {operation_id} AP_TERM_LINE.DueMonthsForward requires DueDayOfMonth."
        )
    due_methods = sum((due_days, due_dom and due_months, fixed_date, calendar))
    if due_methods != 1:
        raise AdapterError(
            f"Operation {operation_id} AP_TERM_LINE must use exactly one due-date method: "
            "DueDays, DueDayOfMonth with DueMonthsForward, FixedDate, or Calendar."
        )

    discount_fields = (
        ("DiscountPercent", "DiscountDays", "DiscountDayOfMonth", "DiscountMonthsForward"),
        ("DiscountPercent2", "DiscountDays2", "DiscountDayOfMonth2", "DiscountMonthsForward2"),
        ("DiscountPercent3", "DiscountDays3", "DiscountDayOfMonth3", "DiscountMonthsForward3"),
    )
    for percent, days, day_of_month, months_forward in discount_fields:
        has_percent = _is_populated(row, percent)
        has_days = _is_populated(row, days)
        has_dom = _is_populated(row, day_of_month)
        has_months = _is_populated(row, months_forward)
        if has_percent and not (Decimal("0") < _decimal_value(row, percent) <= Decimal("100")):
            raise AdapterError(f"Operation {operation_id} AP_TERM_LINE.{percent} must be greater than 0 and at most 100.")
        if has_days and _decimal_value(row, days) < 0:
            raise AdapterError(f"Operation {operation_id} AP_TERM_LINE.{days} must be zero or greater.")
        if has_dom and not (Decimal("1") <= _decimal_value(row, day_of_month) <= Decimal("31")):
            raise AdapterError(f"Operation {operation_id} AP_TERM_LINE.{day_of_month} must be between 1 and 31.")
        if has_months and _decimal_value(row, months_forward) < 0:
            raise AdapterError(f"Operation {operation_id} AP_TERM_LINE.{months_forward} must be zero or greater.")
        if has_dom and not has_months:
            raise AdapterError(f"Operation {operation_id} AP_TERM_LINE.{day_of_month} requires {months_forward}.")
        if has_months and not has_dom:
            raise AdapterError(f"Operation {operation_id} AP_TERM_LINE.{months_forward} requires {day_of_month}.")
        if has_percent and not (has_days or (has_dom and has_months)):
            raise AdapterError(
                f"Operation {operation_id} AP_TERM_LINE.{percent} requires a discount due-date method."
            )
        if (has_days or has_dom or has_months) and not has_percent:
            raise AdapterError(
                f"Operation {operation_id} AP_TERM_LINE.{percent} is required when its discount date fields are supplied."
            )
        if has_days and (has_dom or has_months):
            raise AdapterError(
                f"Operation {operation_id} AP_TERM_LINE.{days} cannot be combined with "
                f"{day_of_month} or {months_forward}."
            )
    if _is_populated(row, "DiscountPercent2") and not _is_populated(row, "DiscountPercent"):
        raise AdapterError(f"Operation {operation_id} AP_TERM_LINE.DiscountPercent2 requires DiscountPercent.")
    if _is_populated(row, "DiscountPercent3") and (
        not _is_populated(row, "DiscountPercent") or not _is_populated(row, "DiscountPercent2")
    ):
        raise AdapterError(
            f"Operation {operation_id} AP_TERM_LINE.DiscountPercent3 requires DiscountPercent and DiscountPercent2."
        )
    for earlier, later in (("DiscountDays", "DiscountDays2"), ("DiscountDays2", "DiscountDays3")):
        if _is_populated(row, earlier) and _is_populated(row, later) and _decimal_value(row, earlier) >= _decimal_value(row, later):
            raise AdapterError(f"Operation {operation_id} AP_TERM_LINE.{earlier} must be earlier than {later}.")
    for earlier, later in (("DiscountPercent", "DiscountPercent2"), ("DiscountPercent2", "DiscountPercent3")):
        if _is_populated(row, earlier) and _is_populated(row, later) and _decimal_value(row, later) >= _decimal_value(row, earlier):
            raise AdapterError(f"Operation {operation_id} AP_TERM_LINE.{later} must be less than {earlier}.")


def _validate_payment_term_cross_line_semantics(
    contract: dict[str, Any], blueprint: dict[str, Any], baseline: PackageData | None
) -> None:
    """Apply PaymentTermHeaderEO's due-basis and percentage-total rules.

    The effective collection is calculated from the fresh export plus requested
    operations.  Without a baseline, an update cannot safely establish the
    full collection, so it is left to the later fresh-export validation.
    """
    line_entity = _entity_map(contract).get("AP_TERM_LINE")
    if line_entity is None:
        return
    rows: dict[tuple[str, ...], dict[str, Any]] = {}
    if baseline is not None:
        rows = {key: dict(value) for key, value in _row_index(baseline, line_entity).items()}
    affected: set[str] = set()
    incomplete_update_terms: set[str] = set()
    for operation in blueprint["operations"]:
        if operation["entity"] != "AP_TERM_LINE":
            continue
        target = operation["targetKey"]
        name = str(target["AP_TERM_HEADER.Name"])
        affected.add(name)
        target_tuple = _target_tuple(line_entity, target)
        if baseline is None and operation["action"] == "update":
            incomplete_update_terms.add(name)
            continue
        row = rows.get(target_tuple, {field: "" for field in line_entity["headers"]})
        row.update(target)
        row.update({field: str(value) for field, value in operation["values"].items()})
        rows[target_tuple] = row
    for name in affected - incomplete_update_terms:
        term_rows = [row for row in rows.values() if str(row.get("AP_TERM_HEADER.Name", "")) == name]
        if not term_rows:
            continue
        has_percent = any(_is_populated(row, "DuePercent") for row in term_rows)
        has_amount = any(_is_populated(row, "DueAmount") for row in term_rows)
        if has_percent and has_amount:
            raise AdapterError(
                f"Payment term {name!r} cannot mix AP_TERM_LINE DuePercent and DueAmount rows."
            )
        if has_percent:
            total = sum((_decimal_value(row, "DuePercent") for row in term_rows), Decimal("0"))
            if total != Decimal("100"):
                raise AdapterError(
                    f"Payment term {name!r} AP_TERM_LINE.DuePercent values must total exactly 100; got {total}."
                )
        if has_amount:
            minimum = min(_decimal_value(row, "DueAmount") for row in term_rows)
            if minimum != Decimal("0"):
                raise AdapterError(
                    f"Payment term {name!r} amount-based lines must include a DueAmount of 0; "
                    f"the source-backed minimum is {minimum}."
                )


def _validate_new_header_installments(blueprint: dict[str, Any]) -> None:
    """A new payment term needs an explicitly requested installment in its ZIP.

    AP_AT_LEAST_ONE_CHILD was verified for new enabled and disabled headers;
    subscriptions and translations do not satisfy this dependency. Existing
    headers and their child-only changes do not need another installment.
    """
    line_parents = {
        operation["targetKey"]["AP_TERM_HEADER.Name"]
        for operation in blueprint["operations"]
        if operation["action"] == "create" and operation["entity"] == "AP_TERM_LINE"
    }
    for operation in blueprint["operations"]:
        if operation["action"] != "create" or operation["entity"] != "AP_TERM_HEADER":
            continue
        name = operation["targetKey"]["Name"]
        if name not in line_parents:
            raise AdapterError(
                f"Operation {operation['id']} AP_AT_LEAST_ONE_CHILD: new payment term "
                f"{name!r} requires at least one AP_TERM_LINE installment in the same package. "
                "Set assignments and translations do not satisfy this requirement. "
                "Ask the user for installment details; do not invent a line."
            )


def _validate_blueprint(
    contract: dict[str, Any],
    blueprint: dict[str, Any],
    baseline: PackageData | None = None,
) -> None:
    task = blueprint.get("task")
    if task != {"name": contract["task"]["name"], "code": contract["task"]["code"]}:
        raise AdapterError("Blueprint task identity differs from the adapter contract.")
    operations = blueprint.get("operations")
    if not isinstance(operations, list) or not operations:
        raise AdapterError("Blueprint must contain at least one operation.")
    entities = _entity_map(contract)
    allowed = set(contract["normalization"]["supportedOperations"])
    _validate_blueprint_reference_provenance(blueprint, baseline)
    satisfied = _satisfied_prerequisites(blueprint, contract)
    seen_ids: set[str] = set()
    seen_targets: set[tuple[str, tuple[str, ...]]] = set()
    for position, operation in enumerate(operations, start=1):
        if not isinstance(operation, dict):
            raise AdapterError(f"Operation {position} must be an object.")
        operation_id = operation.get("id")
        if not isinstance(operation_id, str) or not operation_id:
            raise AdapterError(f"Operation {position} has no stable id.")
        if operation_id in seen_ids:
            raise AdapterError(f"Duplicate operation id {operation_id!r}.")
        seen_ids.add(operation_id)
        action = operation.get("action")
        if action not in allowed:
            raise AdapterError(f"Operation {operation_id} uses unsupported action {action!r}.")
        if action in {"update", "end-date"} and operation.get("preserveOtherValues", True) is not True:
            raise AdapterError(
                f"Operation {operation_id} requires preserveOtherValues=true for updates; "
                "unrequested fields must retain their baseline values."
            )
        entity_name = operation.get("entity")
        if entity_name not in entities:
            raise AdapterError(f"Operation {operation_id} names unknown entity {entity_name!r}.")
        entity = entities[entity_name]
        _validate_set_reference(operation)
        blocked = {
            item["field"]: item
            for item in entity.get("conditionallyBlockedFields", [])
        }
        target = operation.get("targetKey")
        if not isinstance(target, dict) or set(target) != set(entity["keyFields"]):
            raise AdapterError(
                f"Operation {operation_id} targetKey must contain exactly "
                f"{entity['keyFields']}."
            )
        for field in entity["keyFields"]:
            _validate_field_value(entity, field, target[field], operation_id)
            if (
                action == "create"
                and field in blocked
                and (entity_name, field, blocked[field]["resolver"]) not in satisfied
            ):
                raise AdapterError(
                    f"Operation {operation_id} creates conditionally blocked key field "
                    f"{entity_name}.{field}: {blocked[field]['reason']}"
                )
        target_tuple = _target_tuple(entity, target)
        if any(value == "" for value in target_tuple):
            raise AdapterError(f"Operation {operation_id} has a blank target key.")
        target_identity = (entity_name, target_tuple)
        if target_identity in seen_targets:
            raise AdapterError(
                f"More than one operation targets {entity_name} {target_tuple!r}."
            )
        seen_targets.add(target_identity)
        values = operation.get("values")
        if not isinstance(values, dict):
            raise AdapterError(f"Operation {operation_id} must supply values.")
        if not values:
            non_key_business_fields = set(entity["headers"]) - set(entity["keyFields"]) - set(entity["auditFields"])
            if action != "create" or non_key_business_fields:
                raise AdapterError(f"Operation {operation_id} must supply values.")
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
            if field in blocked and (
                entity_name, field, blocked[field]["resolver"]
            ) not in satisfied:
                raise AdapterError(
                    f"Operation {operation_id} changes conditionally blocked field "
                    f"{entity_name}.{field}: {blocked[field]['reason']}"
                )
            _validate_field_value(entity, field, values[field], operation_id)
        effective_row = {field: "" for field in entity["headers"]}
        if baseline is not None:
            matches = _row_index(baseline, entity)
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
            if action == "update":
                effective_row.update(matches[target_tuple])
        effective_row.update(target)
        effective_row.update({field: str(value) for field, value in values.items()})
        if entity_name == "AP_TERM_HEADER":
            _validate_payment_term_header_semantics(effective_row, operation_id)
        elif entity_name == "AP_TERM_LINE":
            _validate_payment_term_line_semantics(effective_row, operation_id)
    _validate_payment_term_rank_uniqueness(contract, blueprint, baseline)
    _validate_payment_term_cross_line_semantics(contract, blueprint, baseline)
    _validate_new_header_installments(blueprint)


def _uploaded_reference_checks(
    uploaded: PackageData, evidence: dict[str, Any] | None, field: str,
    reference_context: dict[str, Any] | None = None, baseline: PackageData | None = None,
) -> tuple[list[str], list[str]]:
    """Require results for each reference of this kind in the exact uploaded ZIP."""
    entity = "AP_TERM_SUBSCRIPTION" if field == "SetCode" else "AP_TERM_LINE"
    references = {row[field] for row in uploaded.rows[entity] if row[field].strip()}
    if not references:
        return [], []
    prefix = "SET" if field == "SetCode" else "CALENDAR"
    endpoint = ("/fscmRestApi/resources/11.13.18.05/setIdSetsLOV" if field == "SetCode"
                else "/fscmRestApi/resources/11.13.18.05/payablesCalendarTypes")
    if (not isinstance(evidence, dict)
            or evidence.get("schemaVersion") != "payment-terms-upload-reference-v1"
            or evidence.get("uploadedPackageSha256") != uploaded.archive_sha256
            or not isinstance(evidence.get("baseUrl"), str) or not evidence["baseUrl"]
            or not isinstance(evidence.get("checks"), list)):
        return [f"{prefix}_LOOKUP_REQUIRED: run the reference helper for this exact uploaded ZIP and provide its results."], []
    try:
        selected = _reference_target(reference_context, baseline)
        if _reference_target(evidence) != selected:
            raise AdapterError("REFERENCE_PROVENANCE: uploaded lookup target differs from selected target.")
    except AdapterError as exc:
        return [f"{prefix}_LOOKUP_REQUIRED: {exc}"], []
    all_checks = evidence["checks"]
    if any(not isinstance(c, dict) or len({"SetCode", "Calendar"} & set(c)) != 1
           or any(not isinstance(c[key], str) or not c[key].strip()
                  for key in ("SetCode", "Calendar") if key in c) for c in all_checks):
        return [f"{prefix}_LOOKUP_REQUIRED: lookup results contain an invalid reference check."], []
    checks = [c for c in all_checks if field in c]
    if len(checks) != len(references) or {c[field] for c in checks} != references:
        return [f"{prefix}_LOOKUP_REQUIRED: lookup results must cover each uploaded {field} exactly once."], []
    errors, warnings = [], []
    for check in checks:
        value = check[field]
        try:
            _validate_reference_provenance({**selected, "checkedAt": check.get("checkedAt")}, selected, baseline)
        except AdapterError as exc:
            errors.append(f"{prefix}_LOOKUP_REQUIRED: {field} {value!r}: {exc}")
            continue
        if check.get("endpoint") != endpoint or not check.get("checkedAt"):
            errors.append(f"{prefix}_LOOKUP_REQUIRED: incomplete lookup details for {field} {value!r}.")
        elif check.get("status") == "validation_skipped":
            if not check.get("warnings") or not check.get("diagnostics"):
                errors.append(f"{prefix}_LOOKUP_REQUIRED: missing skipped-check diagnostic for {field} {value!r}.")
            else:
                warnings.append(f"validation_skipped: {field} {value!r} could not be checked; Fusion must check it during the approved import.")
        elif check.get("status") != "validated":
            errors.append(f"{prefix}_LOOKUP_FAILED: {field} {value!r}: {check.get('error', 'lookup did not pass')}")
    return errors, warnings


def _uploaded_set_checks(uploaded: PackageData, evidence: dict[str, Any] | None, reference_context: dict[str, Any] | None = None, baseline: PackageData | None = None) -> tuple[list[str], list[str]]:
    return _uploaded_reference_checks(uploaded, evidence, "SetCode", reference_context, baseline)


def _validate_uploaded_compatibility(
    baseline: PackageData, uploaded: PackageData, target_context: Any,
) -> None:
    """Require the workflow-selected target, not schema equality, to establish compatibility."""
    if not isinstance(target_context, dict):
        raise AdapterError("UPLOAD_TARGET_REQUIRED: supply independently selected environment and release in --target-context.")
    expected = {}
    for key, metadata_field in (("environment", "ProcessEnv"), ("release", "ProcessRelease")):
        value = target_context.get(key)
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            raise AdapterError(f"UPLOAD_TARGET_REQUIRED: target {key} must be a nonblank string without surrounding whitespace.")
        expected[metadata_field] = value
    for label, package in (("baseline", baseline), ("uploaded package", uploaded)):
        for field, value in expected.items():
            if package.metadata.get(field) != value:
                raise AdapterError(
                    f"UPLOAD_TARGET_MISMATCH: {label} {field} {package.metadata.get(field)!r} "
                    f"does not match selected target {value!r}. Cross-environment or cross-release "
                    "migration requires a governed compatibility check and is not accepted by this validator."
                )


def validate_uploaded_package(
    contract: dict[str, Any], baseline_path: Path, package_path: Path,
    reference_evidence: dict[str, Any] | None = None,
    reference_context: dict[str, Any] | None = None,
    target_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate an exact-task uploaded FSM ZIP without creating or importing it."""
    baseline = _read_package(baseline_path, contract)
    uploaded = _read_package(package_path, contract)
    _validate_uploaded_compatibility(baseline, uploaded, target_context)
    if _schema_fingerprint(contract, baseline) != _schema_fingerprint(contract, uploaded):
        raise AdapterError("Uploaded package schema fingerprint differs from the fresh baseline.")
    set_errors, set_warnings = _uploaded_set_checks(uploaded, reference_evidence, reference_context, baseline)
    calendar_errors, calendar_warnings = _uploaded_reference_checks(uploaded, reference_evidence, "Calendar", reference_context, baseline)
    reference_errors, reference_warnings = set_errors + calendar_errors, set_warnings + calendar_warnings
    operations, descriptions, raw_errors = [], [], list(reference_errors)
    for entity in contract["package"]["entities"]:
        baseline_rows, keys = _row_index(baseline, entity), {}
        for number, row in enumerate(uploaded.rows[entity["name"]], start=1):
            target = {field: row[field] for field in entity["keyFields"]}; key = _target_tuple(entity, target)
            action = "update" if key in baseline_rows else "create"
            # On updates, a populated baseline cell changed to blank is an
            # explicit clear. On creates, blank optional cells remain omitted.
            values = {
                field: row[field] for field in entity["headers"]
                if field not in set(entity["keyFields"]) | set(entity["auditFields"])
                and (row[field] != "" if action == "create"
                     else row[field] != baseline_rows[key][field])
            }
            operation_id = f"UPLOAD-{entity['name']}-{number:03d}"; keys.setdefault(key, []).append((number, operation_id))
            audits = [field for field in entity["auditFields"] if row.get(field, "").strip()]
            if audits: raw_errors.append(f"Operation {operation_id} uploaded row must leave audit fields blank: {audits}.")
            # An unchanged existing header is a transport dependency, not an
            # empty user update. Keep it in the ZIP and row results, but do not
            # invent an operation that would fail the nonempty-values check.
            supporting_header = (
                entity["name"] == "AP_TERM_HEADER" and action == "update"
                and all(row[field] == baseline_rows[key][field]
                        for field in entity["headers"] if field not in entity["auditFields"])
            )
            if not supporting_header:
                operations.append({"id": operation_id, "action": action, "entity": entity["name"], "targetKey": target, "values": values, "preserveOtherValues": True, "preserveUnspecifiedRows": True})
            descriptions.append({"row": number, "operationId": operation_id, "entity": entity["name"], "action": action, "targetKey": target})
        for key, occurrences in keys.items():
            if len(occurrences) > 1:
                rows = [number for number, _ in occurrences]
                raw_errors.extend(f"Operation {operation_id} uploaded row has duplicate target key {key!r} in rows {rows}." for _, operation_id in occurrences)
    parent_names = {row["Name"] for row in uploaded.rows.get("AP_TERM_HEADER", [])}
    for operation in operations:
        if operation["entity"] in {"AP_TERM_LINE", "AP_TERM_SUBSCRIPTION", "AP_TERM_HEADER_TRANSLATION"}:
            parent = operation["targetKey"]["AP_TERM_HEADER.Name"]
            if parent not in parent_names:
                raw_errors.append(
                    f"Operation {operation['id']} MISSING_PARENT: include the matching "
                    f"AP_TERM_HEADER row for {parent!r} in the same uploaded ZIP."
                )
    if not operations: raise AdapterError("Uploaded package contains no effective task changes to validate.")
    blueprint = _normalized_blueprint(contract, {"operations": operations, "resolvedScope": {}, "prerequisites": [], "warnings": []})
    errors = list(raw_errors)
    for operation in blueprint["operations"]:
        isolated = dict(blueprint); isolated["operations"] = [operation]
        if operation["action"] == "create" and operation["entity"] == "AP_TERM_HEADER":
            # Validate the new header with its actual companion installments,
            # not as a header-only request merely because rows are checked one
            # at a time. Other child types cannot satisfy the dependency.
            isolated["operations"] += [
                child for child in blueprint["operations"]
                if child["entity"] == "AP_TERM_LINE" and child["action"] == "create"
                and child["targetKey"]["AP_TERM_HEADER.Name"] == operation["targetKey"]["Name"]
            ]
        elif operation["entity"] == "AP_TERM_LINE":
            # Totals and due-basis rules apply to the complete effective line
            # collection, including other requested lines for this parent.
            isolated["operations"] = [
                child for child in blueprint["operations"]
                if child["entity"] == "AP_TERM_LINE"
                and child["targetKey"]["AP_TERM_HEADER.Name"] == operation["targetKey"]["AP_TERM_HEADER.Name"]
            ]
        try: _validate_blueprint(contract, isolated, baseline)
        except AdapterError as exc:
            if str(exc) not in errors: errors.append(str(exc))
    try: _validate_blueprint(contract, blueprint, baseline)
    except AdapterError as exc:
        if str(exc) not in errors: errors.append(str(exc))
    for item in descriptions:
        item["errors"] = [error for error in errors if item["operationId"] in error]
        if item["entity"] == "AP_TERM_SUBSCRIPTION":
            item["errors"].extend(set_errors)
        elif item["entity"] == "AP_TERM_LINE" and calendar_errors:
            item["errors"].extend(calendar_errors)
        item["status"] = "FAIL" if item["errors"] else "PASS"
    return {"schemaVersion": SCHEMA_VERSION, "status": "PASS" if not errors else "FAIL", "task": contract["task"], "uploadedPackageSha256": uploaded.archive_sha256, "baselineSha256": baseline.archive_sha256, "notImported": True, "candidateCreated": False, "rowResults": descriptions, "errors": errors, "warnings": reference_warnings, "referenceEvidence": reference_evidence}


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
        if (
            operation["action"] == "update"
            and operation.get("preserveOtherValues", True)
        ):
            result.append(
                {
                    "id": f"REQ-{number:03d}",
                    "kind": "preserve_target",
                    "requirement": "Preserve every other non-audit value on the target record",
                    **base,
                }
            )
            number += 1
        if operation.get("preserveUnspecifiedRows", True):
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
                **({"setReference": operation["setReference"],
                    "setResolution": operation.get("setResolution")}
                   if "setReference" in operation else {}),
                "preserveOtherValues": operation.get("preserveOtherValues", True),
                "preserveUnspecifiedRows": operation.get("preserveUnspecifiedRows", True),
            }
            for operation in blueprint["operations"]
        ],
        "explicitDefaults": blueprint["explicitDefaults"],
        "prerequisites": blueprint["prerequisites"],
        "warnings": blueprint["warnings"],
        "resolverFindings": blueprint["resolverFindings"],
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
            row = dict(_row_index(baseline, entity)[key])
        elif operation["action"] == "create":
            row = {header: "" for header in entity["headers"]}
            row.update({field: str(value) for field, value in operation["targetKey"].items()})
        else:
            raise AdapterError(f"Unsupported action {operation['action']!r}.")
        row.update({field: str(value) for field, value in operation["values"].items()})
        for field in entity["auditFields"]:
            row[field] = ""
        output[entity["name"]].append(row)

    # Fusion requires a parent Payment Term Header row in a narrow FSM package
    # whenever the package creates or updates one of its child records.
    # A child-only row is structurally valid CSV, but Fusion skips it because it cannot resolve
    # the parent in the package.  Carry the unchanged parent header from the
    # fresh baseline (with technical audit fields blank) unless an explicit
    # header operation already supplies that parent row.
    header_entity = entities.get("AP_TERM_HEADER")
    if header_entity is not None:
        existing_headers = {
            _row_key(header_entity, row) for row in output[header_entity["name"]]
        }
        baseline_headers = _row_index(baseline, header_entity)
        parent_names = {
            str(operation["targetKey"]["AP_TERM_HEADER.Name"])
            for operation in blueprint["operations"]
            if operation["action"] in {"create", "update"}
            and operation["entity"] != header_entity["name"]
            and "AP_TERM_HEADER.Name" in operation["targetKey"]
        }
        for parent_name in sorted(parent_names):
            key = (parent_name,)
            if key in existing_headers:
                continue
            if key not in baseline_headers:
                raise AdapterError(
                    "Child create/update parent AP_TERM_HEADER "
                    f"{parent_name!r} does not exist in the fresh current export."
                )
            row = dict(baseline_headers[key])
            for field in header_entity["auditFields"]:
                row[field] = ""
            output[header_entity["name"]].append(row)
            existing_headers.add(key)
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
    expected_support_headers: set[tuple[str, ...]] = set()
    header_entity = entities.get("AP_TERM_HEADER")
    if header_entity is not None:
        explicit_headers = {
            _target_tuple(header_entity, operation["targetKey"])
            for operation in blueprint["operations"]
            if operation["entity"] == header_entity["name"]
        }
        for operation in blueprint["operations"]:
            if (
                operation["action"] in {"create", "update"}
                and operation["entity"] != header_entity["name"]
                and "AP_TERM_HEADER.Name" in operation["targetKey"]
            ):
                key = (str(operation["targetKey"]["AP_TERM_HEADER.Name"]),)
                if key not in explicit_headers:
                    expected_support_headers.add(key)
    for operation in blueprint["operations"]:
        entity = entities[operation["entity"]]
        key = _target_tuple(entity, operation["targetKey"])
        expected_targets.add((entity["name"], key))
        candidate_rows = _row_index(candidate, entity)
        baseline_rows = _row_index(baseline, entity)
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
        if operation.get("preserveOtherValues", True) and operation["action"] == "update":
            allowed = set(operation["values"]) | set(entity["auditFields"])
            for field in entity["headers"]:
                if field not in allowed and not _same_preserved_value(entity, field, row[field], before[field]):
                    issues.append(
                        {"code": "UNEXPECTED_CHANGE", "message": f"{entity['name']} {key!r} changed preserved field {field}."}
                    )
        for field in entity["auditFields"]:
            if row[field] != "":
                issues.append(
                    {"code": "AUDIT_FIELD_POPULATED", "message": f"{entity['name']} {key!r} audit field {field} is not blank."}
                )
    for entity in contract["package"]["entities"]:
        for row in candidate.rows[entity["name"]]:
            identity = (entity["name"], _row_key(entity, row))
            if (
                identity not in expected_targets
                and not (
                    header_entity is not None
                    and entity["name"] == header_entity["name"]
                    and identity[1] in expected_support_headers
                )
            ):
                issues.append(
                    {"code": "UNEXPECTED_ROW", "message": f"Candidate contains unrequested {entity['name']} row {identity[1]!r}."}
                )
    if header_entity is not None:
        candidate_headers = _row_index(candidate, header_entity)
        baseline_headers = _row_index(baseline, header_entity)
        for key in sorted(expected_support_headers):
            row = candidate_headers.get(key)
            before = baseline_headers.get(key)
            if row is None:
                issues.append(
                    {"code": "MISSING_PARENT", "message": f"Candidate lacks required parent AP_TERM_HEADER {key!r}."}
                )
                continue
            if before is None:
                issues.append(
                    {"code": "MISSING_PARENT_BASELINE", "message": f"Fresh baseline lacks parent AP_TERM_HEADER {key!r}."}
                )
                continue
            for field in header_entity["headers"]:
                if field in header_entity["auditFields"]:
                    if row[field] != "":
                        issues.append(
                            {"code": "AUDIT_FIELD_POPULATED", "message": f"Parent AP_TERM_HEADER {key!r} audit field {field} is not blank."}
                        )
                elif not _same_preserved_value(header_entity, field, row[field], before[field]):
                    issues.append(
                        {"code": "PARENT_ROW_CHANGED", "message": f"Supporting parent AP_TERM_HEADER {key!r} changed {field}."}
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
        "resolverFindings": blueprint.get("resolverFindings", []),
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
    result["businessSummary"] = [
        {
            "operationId": operation["id"],
            "action": operation["action"],
            "entity": operation["entity"],
            "targetKey": operation["targetKey"],
            "values": operation["values"],
        }
        for operation in blueprint["operations"]
    ]
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


def _read_verification_evidence(path: Path | None) -> dict[str, Any] | None:
    """Unreadable workflow evidence cannot prove persistence."""
    if path is None:
        return None
    try:
        return _read_json(path)
    except (AdapterError, OSError):
        return None


def _readback_provenance(
    contract: dict[str, Any], baseline: PackageData, candidate: PackageData,
    blueprint_path: Path, readback: PackageData, context: Any, evidence: Any,
    requirements_path: Path,
) -> str | None:
    """Check the governed import/export observation before claiming persistence.

    The routed workflow supplies observations from Data Loader and Task Level
    Export, separately from its selected target and import request. ZIP contents
    alone cannot establish when or where an export was observed.
    """
    if readback.archive_sha256 in {baseline.archive_sha256, candidate.archive_sha256}:
        return "The baseline or candidate ZIP cannot serve as post-import proof."
    if readback.metadata.get("ProcessStatus", "").upper() not in SUCCESS_STATUSES:
        return "The supplied export metadata does not declare a completed process."
    if not isinstance(context, dict) or not isinstance(evidence, dict):
        return "Governed import/export evidence and the selected verification context are required."
    if evidence.get("schemaVersion") != "fsm-post-import-readback-v1":
        return "Unsupported post-import readback evidence."
    environment, base_url = context.get("environment"), context.get("baseUrl")
    request_id = context.get("importRequestId")
    if (not isinstance(environment, str) or not environment.strip()
            or environment != environment.strip()
            or any(ord(c) < 32 or ord(c) == 127 for c in environment)
            or not isinstance(request_id, str) or not re.fullmatch(r"[1-9][0-9]*", request_id)):
        return "Selected target environment and positive import request ID are required."
    try:
        base_url = _https_origin(base_url)
    except AdapterError as exc:
        return f"Selected target must provide a credential-free HTTPS origin: {exc}"
    imported, exported = evidence.get("importObservation"), evidence.get("exportObservation")
    if not isinstance(imported, dict) or not isinstance(exported, dict):
        return "Completed import and export observations are required."
    for observation in (imported, exported):
        try:
            observation_origin = _https_origin(observation.get("baseUrl"))
        except AdapterError as exc:
            return f"Import/export evidence must provide a credential-free HTTPS origin: {exc}"
        if (observation.get("environment") != environment
                or observation_origin != base_url
                or observation.get("taskCode") != contract["task"]["code"]):
            return "Import/export evidence does not match the selected environment, URL and task."
    if any(package.metadata.get("ProcessEnv") != environment for package in (baseline, candidate, readback)):
        return "A package environment does not match the selected verification environment."
    if (imported.get("source") != "core.data-loader"
            or imported.get("status") != "SUCCEEDED"
            or imported.get("requestId") != request_id
            or not re.fullmatch(r"UCMFA[0-9]+", str(imported.get("ucmContentId", "")))
            or type(imported.get("loadedObjects")) is not int or imported["loadedObjects"] < 1
            or type(imported.get("failedObjects")) is not int or imported["failedObjects"] != 0):
        return "A successful Data Loader observation for the selected import request is required."
    if (imported.get("candidateSha256") != candidate.archive_sha256
            or imported.get("baselineSha256") != baseline.archive_sha256
            or imported.get("blueprintSha256") != _sha256_path(blueprint_path)):
        return "Import evidence is not bound to this candidate, baseline and request blueprint."
    if imported.get("requirementsSha256") != _sha256_path(requirements_path):
        return "Import evidence is not bound to these verification requirements."
    if (exported.get("source") != "shared.setup-export.task-level-export"
            or exported.get("status") != "COMPLETED"
            or exported.get("processCompletedFlag") is not True
            or not isinstance(exported.get("processId"), str)
            or not re.fullmatch(r"[1-9][0-9]*", exported["processId"])
            or not isinstance(exported.get("requestId"), str)
            or not re.fullmatch(r"[1-9][0-9]*", exported["requestId"])
            or exported["requestId"] != readback.metadata.get("ESSRequestId")
            or exported.get("artifactSha256") != readback.archive_sha256):
        return "A completed Task Level Export observation bound to this export process, request and ZIP is required."

    def observed_time(observation: dict[str, Any], field: str) -> datetime:
        value = observation.get(field)
        if not isinstance(value, str):
            raise ValueError("Missing timestamp")
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.utcoffset() is None:
            raise ValueError("Timestamp needs a timezone")
        return parsed

    try:
        import_end = observed_time(imported, "completedAt")
        import_seen = observed_time(imported, "observedAt")
        export_start = observed_time(exported, "startedAt")
        export_end = observed_time(exported, "completedAt")
        export_seen = observed_time(exported, "observedAt")
        valid_order = (import_end <= import_seen <= export_start <= export_end <= export_seen
                       and import_end < export_start
                       and export_seen <= datetime.now(timezone.utc) + timedelta(seconds=60))
    except (ValueError, TypeError, OverflowError):
        return "Import/export observations need valid timestamps with timezones."
    if not valid_order:
        return "Export evidence is stale or its observation times do not follow this completed import."
    return None


def reconcile(
    contract: dict[str, Any], baseline_path: Path, candidate_path: Path,
    blueprint_path: Path, requirements_path: Path, export_path: Path,
    verification_evidence: dict[str, Any] | None = None,
    verification_context: dict[str, Any] | None = None,
    *, compare_only: bool = False,
) -> dict[str, Any]:
    """Compare files, or verify persistence using observed import/export evidence."""
    if compare_only:
        result = _compare_package_contents(contract, baseline_path, candidate_path,
                                          blueprint_path, requirements_path, export_path)
        result["status"] = "MATCH" if result["status"] == "PASS" else "DIFFERENT"
        result["persistenceVerification"] = "NOT_PERFORMED"
        result["reason"] = "Offline file comparison only; this does not prove changes were saved in Fusion."
        return result
    baseline = _read_package(baseline_path, contract)
    candidate = _read_package(candidate_path, contract)
    try:
        readback = _read_package(export_path, contract)
        reason = _readback_provenance(contract, baseline, candidate, blueprint_path,
                                     readback, verification_context, verification_evidence,
                                     requirements_path)
    except (AdapterError, OSError):
        reason = "Post-import export or evidence files could not be read."
    if reason:
        return {"schemaVersion": SCHEMA_VERSION, "task": contract["task"],
                "status": "PENDING", "persistenceVerification": "PENDING", "reason": reason,
                "baselineSha256": baseline.archive_sha256, "candidateSha256": candidate.archive_sha256,
                "exportSha256": _sha256_path(export_path) if export_path.is_file() else None,
                "requirementMatrix": [], "mismatchCount": None}
    result = _compare_package_contents(contract, baseline_path, candidate_path,
                                      blueprint_path, requirements_path, export_path)
    result["persistenceVerification"] = result["status"]
    return result


def _compare_package_contents(
    contract: dict[str, Any],
    baseline_path: Path,
    candidate_path: Path,
    blueprint_path: Path,
    requirements_path: Path,
    export_path: Path,
) -> dict[str, Any]:
    baseline = _read_package(baseline_path, contract)
    candidate = _read_package(candidate_path, contract)
    persisted = _read_package(export_path, contract)
    blueprint = _read_json(blueprint_path)
    requirements = _read_json(requirements_path)
    _validate_blueprint(contract, blueprint, baseline)
    if not isinstance(requirements, list):
        raise AdapterError("Requirements file must contain a JSON array.")
    _requirement_contract(contract, blueprint, requirements)
    entities = _entity_map(contract)
    operation_map = {operation["id"]: operation for operation in blueprint["operations"]}
    indexes = {
        name: {
            "baseline": _row_index(baseline, entity),
            "candidate": _row_index(candidate, entity),
            "persisted": _row_index(persisted, entity),
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
                        not _same_preserved_value(entity, field, candidate_row[field], before[field])
                        or not _same_preserved_value(entity, field, persisted_row[field], before[field])
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
            # Fusion creates language translation rows when a payment-term
            # header is created, even if the candidate intentionally contains
            # no AP_TERM_HEADER_TRANSLATION rows. Those rows are derived from
            # the new header rather than unrelated setup changes, so exclude
            # only translations belonging to headers created by this package.
            created_term_names = {
                str(op["targetKey"]["Name"])
                for op in blueprint["operations"]
                if op["action"] == "create" and op["entity"] == "AP_TERM_HEADER"
            }
            description_updated_term_names = {
                str(op["targetKey"]["Name"])
                for op in blueprint["operations"]
                if (
                    op["action"] == "update"
                    and op["entity"] == "AP_TERM_HEADER"
                    and "Description" in op["values"]
                )
            }
            differences = []
            for entity_name, current_entity in entities.items():
                baseline_rows = indexes[entity_name]["baseline"]
                persisted_rows = indexes[entity_name]["persisted"]
                for row_key in sorted(set(baseline_rows) | set(persisted_rows)):
                    if (entity_name, row_key) in touched:
                        continue
                    if (
                        entity_name == "AP_TERM_HEADER_TRANSLATION"
                        and row_key[0] in created_term_names
                    ):
                        continue
                    left = baseline_rows.get(row_key)
                    right = persisted_rows.get(row_key)
                    if left is None or right is None:
                        differences.append(f"{entity_name}:{row_key}:row")
                        continue
                    for field in current_entity["headers"]:
                        if (
                            entity_name == "AP_TERM_HEADER_TRANSLATION"
                            and row_key[0] in description_updated_term_names
                            and field == "Description"
                        ):
                            continue
                        if field not in current_entity["auditFields"] and not _same_preserved_value(current_entity, field, left[field], right[field]):
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
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS" if all(row["passed"] for row in matrix) else "FAIL",
        "task": contract["task"],
        "baselineSha256": baseline.archive_sha256,
        "candidateSha256": candidate.archive_sha256,
        "exportSha256": persisted.archive_sha256,
        "requirementMatrix": matrix,
        "mismatchCount": sum(not row["passed"] for row in matrix),
    }


def make_rollback(
    contract: dict[str, Any],
    template_path: Path,
    before_path: Path,
    current_path: Path,
    forward_blueprint_path: Path,
    rollback_blueprint_path: Path,
    rollback_requirements_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    _validate_new_outputs(
        [rollback_blueprint_path, rollback_requirements_path, output_path],
        [template_path, before_path, current_path, forward_blueprint_path],
    )
    before = _read_package(before_path, contract)
    current = _read_package(current_path, contract)
    if before.metadata["ProcessEnv"] != current.metadata["ProcessEnv"]:
        raise AdapterError("Before and current rollback exports come from different environments.")
    if before.metadata["ProcessRelease"] != current.metadata["ProcessRelease"]:
        raise AdapterError("Before and current rollback exports come from different releases.")
    forward = _read_json(forward_blueprint_path)
    _validate_blueprint(contract, forward, before)
    entities = _entity_map(contract)
    operations = []
    for index, operation in enumerate(forward["operations"], start=1):
        if operation["action"] != "update":
            raise AdapterError("Automatic rollback currently supports update operations only.")
        entity = entities[operation["entity"]]
        key = _target_tuple(entity, operation["targetKey"])
        original_row = _row_index(before, entity).get(key)
        current_row = _row_index(current, entity).get(key)
        if original_row is None or current_row is None:
            raise AdapterError(f"Rollback target {entity['name']} {key!r} is missing.")
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
        "referenceContext": forward.get("referenceContext"),
        "explicitDefaults": [],
        "preservedValues": [],
        "prerequisites": forward.get("prerequisites", []),
        "warnings": [],
    }
    rollback = _normalized_blueprint(contract, design)
    _validate_blueprint(contract, rollback, current)
    requirements = _requirements(contract, rollback)
    _write_new_json(rollback_blueprint_path, rollback)
    _write_new_json(rollback_requirements_path, requirements)
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
    if (not isinstance(environment, str) or not environment.strip()
            or any(ord(c) < 32 or ord(c) == 127 for c in environment)):
        raise AdapterError("MANIFEST_SOURCE_MISMATCH: a nonblank source environment label is required.")
    if environment.strip() != package.metadata["ProcessEnv"]:
        raise AdapterError("MANIFEST_SOURCE_MISMATCH: source environment label differs from package ProcessEnv; keep migration target metadata separate.")
    base_url = _https_origin(base_url)
    if type(template_only) is not bool:
        raise AdapterError("MANIFEST_TEMPLATE_MISMATCH: templateOnly must be a boolean.")
    populated = [
        entity["member"]
        for entity in contract["package"]["entities"]
        if package.rows[entity["name"]]
    ]
    if template_only and populated:
        raise AdapterError("MANIFEST_TEMPLATE_MISMATCH: template-only packages must contain no data rows.")
    return {
        "environment": package.metadata["ProcessEnv"],
        "baseUrl": base_url,
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

    validate_upload = sub.add_parser("validate-upload", help="Validate an uploaded FSM ZIP without import.")
    _add_common(validate_upload)
    validate_upload.add_argument("--baseline", type=Path, required=True)
    validate_upload.add_argument("--target-context", type=Path, help="Independently selected environment and release JSON; required for uploaded validation.")
    validate_upload.add_argument("--package", type=Path, required=True)
    validate_upload.add_argument("--reference-context", type=Path, help="Independently selected environment and HTTPS origin JSON; required for reference evidence.")
    validate_upload.add_argument("--reference-evidence", type=Path, help="Lookup helper results for the exact ZIP; required for set assignments or installment Calendars.")

    rollback = sub.add_parser("rollback", help="Build a narrow rollback for a validated update.")
    _add_common(rollback)
    rollback.add_argument("--template", type=Path, required=True)
    rollback.add_argument("--before", type=Path, required=True)
    rollback.add_argument("--current", type=Path, required=True)
    rollback.add_argument("--forward-blueprint", type=Path, required=True)
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
    reconcile_parser.add_argument("--compare-only", action="store_true",
                                  help="Compare file contents only; never claim Fusion persistence.")
    reconcile_parser.add_argument("--verification-evidence", type=Path,
                                  help="Governed successful import and later export observations.")
    reconcile_parser.add_argument("--environment", help="Selected target environment.")
    reconcile_parser.add_argument("--base-url", help="Selected target HTTPS origin.")
    reconcile_parser.add_argument("--import-request-id", help="Selected completed Data Loader request.")
    return parser.parse_args(argv)


def _command_succeeded(command: str, result: dict[str, Any]) -> bool:
    if command == "reconcile":
        return result.get("status") in {"PASS", "MATCH"}
    if command == "manifest":
        status = result.get("status")
        return isinstance(status, str) and status.strip().upper() in SUCCESS_STATUSES
    return result.get("status", "PASS") == "PASS"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report_safe = False
    try:
        _preflight_cli_outputs(args)
        report_safe = True
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
            _write_new_json(args.blueprint_output, blueprint)
            _write_new_json(args.preview_output, preview)
            _write_new_json(args.requirements_output, requirements)
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
        elif args.command == "validate-upload":
            result = validate_uploaded_package(
                contract, args.baseline, args.package,
                _read_json(args.reference_evidence) if args.reference_evidence else None,
                _read_json(args.reference_context) if args.reference_context else None,
                target_context=_read_json(args.target_context) if args.target_context else None,
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
            )
        elif args.command == "reconcile":
            result = reconcile(
                contract,
                args.baseline,
                args.candidate,
                args.blueprint,
                args.requirements,
                args.export,
                _read_verification_evidence(args.verification_evidence),
                {"environment": args.environment, "baseUrl": args.base_url,
                 "importRequestId": args.import_request_id},
                compare_only=args.compare_only,
            )
        else:
            raise AdapterError(f"Unknown command {args.command!r}.")
        if args.report:
            _write_new_json(args.report, result)
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if _command_succeeded(args.command, result) else 2
    except (AdapterError, OSError) as exc:
        failure = {
            "schemaVersion": SCHEMA_VERSION,
            "status": "FAIL",
            "errors": [{"code": "ADAPTER_ERROR", "message": str(exc)}],
        }
        if report_safe and getattr(args, "report", None):
            try:
                _write_new_json(args.report, failure)
            except AdapterError as report_error:
                failure["errors"].append({"code": "REPORT_ERROR", "message": str(report_error)})
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
