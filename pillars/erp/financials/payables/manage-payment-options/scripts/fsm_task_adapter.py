#!/usr/bin/env python3
"""Portable, data-driven FSM task adapter runtime.

This file is copied into a generated Nested task skill.  Task semantics live in
the adjacent e2e-adapter.json descriptor and ora-resource rule plan.  The
runtime performs offline package work only; it never connects to Fusion.

Reading guide: this adapter verifies the task contract and package, checks its
Payment-owned fields with the shared Invoice Options row contract, then
normalizes, validates, builds, and reconciles an offline candidate.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
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


def _load_invoice_options_shared_contract() -> tuple[Any, dict[str, Any]]:
    """Load the sibling AP_SYSTEM_PARAMETER contract used for shared-row checks.

    Manage Payment Options owns its payment-field semantics.  Manage Invoice
    Options owns the broader AP_SYSTEM_PARAMETER create/update contract.  Keep
    this dependency explicit and fail closed if a portable checkout does not
    contain the pinned sibling task.
    """
    invoice_root = Path(__file__).resolve().parents[2] / "manage-invoice-options"
    descriptor_path = invoice_root / "e2e-adapter.json"
    runtime_path = invoice_root / "scripts" / "fsm_task_adapter.py"
    if not descriptor_path.is_file() or not runtime_path.is_file():
        raise AdapterError(
            "Shared AP_SYSTEM_PARAMETER validation requires the sibling Manage "
            "Invoice Options adapter and runtime at pillars/erp/financials/payables/"
            "manage-invoice-options/."
        )
    spec = importlib.util.spec_from_file_location(
        "fscr_manage_invoice_options_shared_adapter", runtime_path
    )
    if spec is None or spec.loader is None:
        raise AdapterError("Cannot load the sibling Manage Invoice Options runtime.")
    module = importlib.util.module_from_spec(spec)
    # Dataclass resolution requires dynamically loaded modules to be registered
    # before their class decorators execute.
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(spec.name, None)
        raise
    shared_contract = module._load_contract(descriptor_path)
    return module, shared_contract


def _shared_create_defaults() -> dict[str, str]:
    """Reuse the shared row owner's documented defaults without copying them."""
    module, shared_contract = _load_invoice_options_shared_contract()
    defaults: dict[str, str] = {}
    for name in ("CREATE_FLAG_DEFAULTS", "CREATE_UI_DEFAULTS"):
        values = getattr(module, name, None)
        if not isinstance(values, dict) or not values:
            raise AdapterError(f"Shared Invoice Options {name} is missing or invalid.")
        defaults.update(values)
    entity = module._entity_map(shared_contract)["AP_SYSTEM_PARAMETER"]
    prohibited = set(entity["keyFields"]) | set(entity["auditFields"])
    if any(
        not isinstance(field, str) or field not in entity["headers"]
        or field in prohibited or not isinstance(value, str) or not value
        for field, value in defaults.items()
    ):
        raise AdapterError("Shared Invoice Options create defaults do not match the row contract.")
    return defaults


def _shared_invoice_blueprint(
    blueprint: dict[str, Any], shared_contract: dict[str, Any]
) -> dict[str, Any]:
    """Bind the same operations to the sibling adapter without changing inputs."""
    shared = json.loads(json.dumps(blueprint))
    shared["task"] = {
        "name": shared_contract["task"]["name"],
        "code": shared_contract["task"]["code"],
    }
    return shared


def _validate_shared_invoice_contract(
    contract: dict[str, Any], blueprint: dict[str, Any], baseline: PackageData
) -> None:
    """Apply Invoice Options shared-row validation to every Payment operation.

    The sibling adapter validates the complete resulting AP_SYSTEM_PARAMETER
    record.  This covers create prerequisites/defaults and update preservation
    in addition to the Payment-specific field contract.
    """
    module, shared_contract = _load_invoice_options_shared_contract()
    local = _entity_map(contract).get("AP_SYSTEM_PARAMETER")
    shared = module._entity_map(shared_contract).get("AP_SYSTEM_PARAMETER")
    if local is None or shared is None:
        raise AdapterError("AP_SYSTEM_PARAMETER is absent from a shared-row contract.")
    for key in ("headers", "keyFields", "auditFields", "nodePath", "nodeSequence"):
        if local.get(key) != shared.get(key):
            raise AdapterError(
                "Payment Options and Invoice Options AP_SYSTEM_PARAMETER contracts "
                f"differ at {key}; refresh task evidence before building a candidate."
            )
    try:
        # The sibling contract owns the row semantics, not this FSM archive's
        # task identity. Bind its reader to the exact Payment export identity
        # after structural compatibility has been established above.
        shared_contract = json.loads(json.dumps(shared_contract))
        shared_contract["package"]["objectShortName"] = contract["package"][
            "objectShortName"
        ]
        shared_baseline = module._read_package(baseline.path, shared_contract)
        module._validate_blueprint(
            shared_contract,
            _shared_invoice_blueprint(blueprint, shared_contract),
            shared_baseline,
        )
    except Exception as exc:
        raise AdapterError(
            "Shared Invoice Options AP_SYSTEM_PARAMETER validation failed: "
            f"{exc}"
        ) from exc


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
        expected_node_sequence = str(entity["nodeSequence"]).strip()
        actual_node_sequence = str(actual["nodeSequence"]).strip()
        if not re.fullmatch(r"[1-9][0-9]*", expected_node_sequence):
            raise AdapterError(
                f"Adapter node sequence for {entity['name']} must be a positive integer; "
                f"found {expected_node_sequence!r}."
            )
        if not re.fullmatch(r"[1-9][0-9]*", actual_node_sequence):
            raise AdapterError(
                f"Metadata node sequence for {entity['name']} must be a positive integer; "
                f"found {actual_node_sequence!r}."
            )
        if actual_node_sequence != expected_node_sequence:
            raise AdapterError(
                f"Metadata node sequence for {entity['name']} is {actual_node_sequence!r}, "
                f"expected {expected_node_sequence!r} from e2e-adapter.json."
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


def _row_key(entity: dict[str, Any], row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row.get(field, "") for field in entity["keyFields"])


def _target_tuple(entity: dict[str, Any], target: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(target.get(field, "")) for field in entity["keyFields"])


def _validate_field_value(
    entity: dict[str, Any], field: str, value: Any, operation_id: str
) -> None:
    # Preserve BankChargeBearer as supplied. FSM Import owns value validation.
    if entity["name"] == "AP_SYSTEM_PARAMETER" and field == "BankChargeBearer":
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
    length_constraint = entity.get("fieldConstraints", {}).get(field)
    if length_constraint and isinstance(value, str):
        maximum = int(length_constraint["maxLength"])
        unit = str(length_constraint["lengthUnit"])
        actual = len(value) if unit == "characters" else len(value.encode("utf-8"))
        if actual > maximum:
            raise AdapterError(
                f"Operation {operation_id} field {entity['name']}.{field} exceeds "
                f"the source-backed maximum length of {maximum} {unit}; received "
                f"{actual}. Shorten the business value and regenerate the preview."
            )
    value_contract = entity.get("valueContracts", {}).get(field)
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


# These rules are deliberately kept task-local.  They are derived from the
# observable Manage Payment Options UI, rather than being inferred from the
# shared AP_SYSTEM_PARAMETER package structure.  They validate business input
# before the separate lifecycle/write-evidence gate is evaluated below.
_UI_BOOLEAN_FIELDS = {
    "PostDatedPaymentsFlag",
    "AllowSupplierBankOverride",
    "PayDocCategoryOverride",
    "AllowPymtThirdPartyOvrd",
}
_UI_NONNEGATIVE_INTEGER_FIELDS = {"EscheatmentEligibilityPeriod"}
_UI_FIXED_ENUMERATIONS = {
    "BankChargeDeductionTypeDes": {"Standard", "Negotiated", "None"},
    "WhenToAccountPmt": {"PAYMENT ONLY", "CLEARING ONLY", "BOTH"},
}
PAYMENT_OWNED_FIELDS = {
    "PostDatedPaymentsFlag",
    "AllowSupplierBankOverride",
    "PayDocCategoryOverride",
    "AllowPymtThirdPartyOvrd",
    "WhenToAccountPmt",
    "BankChargeDeductionTypeDes",
    "EscheatmentEligibilityPeriod",
}


def validate_payment_owned_row(
    entity: dict[str, Any], values: dict[str, Any], operation_id: str
) -> None:
    """Validate the Payment Options portion of a shared system-options row.

    This is intentionally a field-contract entry point, rather than a call to
    this adapter's full blueprint validator: the Invoice Options adapter uses
    it while validating the same AP_SYSTEM_PARAMETER row and a reciprocal full
    adapter call would recurse.  Empty exported values remain valid for
    optional controls; supplied nonblank Payment values receive both their
    package type/value validation and the task-local UI validation.  Fusion
    stores the conversion-rate controls in Financials System Parameters rather
    than the AP system-parameter record, but a supplied checkbox value is
    still constrained to Y or N; an unspecified exported value is preserved.
    """
    for field in sorted(PAYMENT_OWNED_FIELDS & set(values)):
        value = values[field]
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        _validate_field_value(entity, field, value, operation_id)
        _validate_ui_observed_payment_options_value(entity, field, value, operation_id)


def _validate_ui_observed_payment_options_value(
    entity: dict[str, Any], field: str, value: Any, operation_id: str
) -> None:
    """Validate task UI rules whose CSV write contract may still be unresolved."""
    if entity["name"] != "AP_SYSTEM_PARAMETER":
        return
    if field in _UI_BOOLEAN_FIELDS:
        if not isinstance(value, str) or value.strip().upper() not in {"Y", "N"}:
            raise AdapterError(
                f"Operation {operation_id} field {entity['name']}.{field} must be Y or N "
                "for its Manage Payment Options checkbox."
            )
    elif field in _UI_NONNEGATIVE_INTEGER_FIELDS:
        try:
            number = int(str(value).strip())
        except (TypeError, ValueError):
            number = -1
        if number < 0:
            raise AdapterError(
                f"Operation {operation_id} field {entity['name']}.{field} must be a "
                "nonnegative integer."
            )
    elif field in _UI_FIXED_ENUMERATIONS:
        allowed = _UI_FIXED_ENUMERATIONS[field]
        if not isinstance(value, str) or value.strip().casefold() not in {item.casefold() for item in allowed}:
            raise AdapterError(
                f"Operation {operation_id} field {entity['name']}.{field} must be one "
                f"of: {', '.join(sorted(allowed))}."
            )


def _normalize_field_value(
    entity: dict[str, Any], field: str, value: Any, operation_id: str
) -> Any:
    """Map a business label/synonym to its source-backed package value."""
    value_contract = entity.get("valueContracts", {}).get(field)
    if not value_contract or not isinstance(value, str):
        return value
    stripped = value.strip()
    folded = stripped.casefold()
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
        if folded == code.casefold() or folded in {
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
        if not isinstance(item, dict) or item.get("status") not in {
            "satisfied",
            "developer_override",
            "implementor_override",
        }:
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
    applied_defaults = list(design.get("explicitDefaults", []))
    for index, raw in enumerate(operations, start=1):
        if not isinstance(raw, dict):
            raise AdapterError(f"Operation {index} must be an object.")
        operation = dict(raw)
        operation.setdefault("id", f"OP-{index:03d}")
        operation.setdefault("action", "update")
        operation.setdefault("preserveOtherValues", True)
        operation.setdefault("preserveUnspecifiedRows", True)
        entity = entities.get(operation.get("entity"))
        if entity is not None:
            target = dict(operation.get("targetKey") or {})
            operation["targetKey"] = {
                field: _normalize_field_value(
                    entity, field, value, operation["id"]
                )
                for field, value in target.items()
            }
            values = dict(operation.get("values") or {})
            operation["values"] = {
                field: _normalize_field_value(
                    entity, field, value, operation["id"]
                )
                for field, value in values.items()
            }
        if operation["action"] == "create" and operation.get("entity") in entities:
            entity = entities[operation["entity"]]
            values = dict(operation.get("values") or {})
            for field, default in entity.get("createDefaults", {}).items():
                if field in values:
                    continue
                values[field] = default["value"]
                applied_defaults.append(
                    {
                        "operationId": operation["id"],
                        "entity": entity["name"],
                        "field": field,
                        "value": default["value"],
                        "sourceIds": default["sourceIds"],
                    }
                )
            if entity["name"] == "AP_SYSTEM_PARAMETER":
                for field, value in _shared_create_defaults().items():
                    if field in values:
                        continue
                    values[field] = value
                    applied_defaults.append({
                        "operationId": operation["id"], "entity": entity["name"],
                        "field": field, "value": value,
                        "source": "Manage Invoice Options create defaults",
                    })
            operation["values"] = values
        normalized_ops.append(operation)
    raw_evidence_overrides = design.get("evidenceUnresolvedUpdateOverrides", [])
    if not isinstance(raw_evidence_overrides, list):
        raise AdapterError("evidenceUnresolvedUpdateOverrides must be an array.")
    evidence_overrides = [
        dict(item) if isinstance(item, dict) else item
        for item in raw_evidence_overrides
    ]
    warnings = list(design.get("warnings", []))
    for item in evidence_overrides:
        if not isinstance(item, dict):
            continue
        operation_id = str(item.get("operationId", ""))
        if any(
            isinstance(warning, dict)
            and warning.get("code") == "EVIDENCE_UNRESOLVED_UPDATE_OVERRIDE"
            and warning.get("operationId") == operation_id
            for warning in warnings
        ):
            continue
        warnings.append(
            {
                "code": "EVIDENCE_UNRESOLVED_UPDATE_OVERRIDE",
                "operationId": operation_id,
                "entity": str(item.get("entity", "")),
                "fields": list(item.get("fields", []))
                if isinstance(item.get("fields"), list)
                else [],
                "message": str(item.get("uncertaintyAcknowledgement", "")),
            }
        )
    blueprint = {
        "task": {
            "name": contract["task"]["name"],
            "code": contract["task"]["code"],
        },
        "operations": normalized_ops,
        "resolvedScope": design.get("resolvedScope", {}),
        "referenceContext": design.get("referenceContext"),
        "explicitDefaults": applied_defaults,
        "preservedValues": design.get("preservedValues", []),
        "prerequisites": design.get("prerequisites", []),
        "warnings": warnings,
        "evidenceUnresolvedUpdateOverrides": evidence_overrides,
    }
    return blueprint


def _evidence_unresolved_update_override_map(
    contract: dict[str, Any], blueprint: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Validate and index narrowly scoped governed implementor overrides."""
    raw_overrides = blueprint.get("evidenceUnresolvedUpdateOverrides", [])
    if not isinstance(raw_overrides, list):
        raise AdapterError("evidenceUnresolvedUpdateOverrides must be an array.")
    if not raw_overrides:
        return {}
    policy = contract.get("normalization", {}).get(
        "evidenceUnresolvedUpdateOverridePolicy", {}
    )
    expected_policy = {
        "mode": "governed-application-validation",
        "operation": "update",
        "requiresExplicitImplementorApproval": True,
        "requiresEnvironmentAuthorization": True,
        "requiresExactOperationBinding": True,
        "requiresExactFieldBinding": True,
        "requiresImmutablePreview": True,
        "requiresCandidateSpecificApproval": True,
        "requiresPreserveOtherValues": True,
        "requiresPreserveUnspecifiedRows": True,
        "singleSubmissionOnly": True,
        "automaticRetryAllowed": False,
        "authoritativeValidator": "FSM",
        "executionOwner": "runbook-and-core.data-loader",
    }
    if policy != expected_policy:
        raise AdapterError(
            "Adapter does not declare the complete governed evidence-unresolved update override policy."
        )
    operations = {
        str(item.get("id", "")): item
        for item in blueprint.get("operations", [])
        if isinstance(item, dict) and str(item.get("id", ""))
    }
    entities = _entity_map(contract)
    indexed: dict[str, dict[str, Any]] = {}
    seen_ids: set[str] = set()
    for position, item in enumerate(raw_overrides, start=1):
        if not isinstance(item, dict):
            raise AdapterError(
                f"Evidence-unresolved update override {position} must be an object."
            )
        override_id = item.get("id")
        operation_id = item.get("operationId")
        entity_name = item.get("entity")
        fields = item.get("fields")
        if not isinstance(override_id, str) or not override_id:
            raise AdapterError(
                f"Evidence-unresolved update override {position} requires a stable id."
            )
        if override_id in seen_ids:
            raise AdapterError(f"Duplicate evidence override id {override_id!r}.")
        seen_ids.add(override_id)
        if not isinstance(operation_id, str) or operation_id not in operations:
            raise AdapterError(
                f"Evidence override {override_id} must bind to one exact operation id."
            )
        if operation_id in indexed:
            raise AdapterError(
                f"Operation {operation_id} has more than one evidence-unresolved override."
            )
        operation = operations[operation_id]
        if operation.get("action") != "update":
            raise AdapterError(
                f"Evidence override {override_id} may apply only to an update operation."
            )
        if entity_name != operation.get("entity") or entity_name not in entities:
            raise AdapterError(
                f"Evidence override {override_id} must bind to the operation's exact entity."
            )
        ownership = entities[entity_name].get("operationOwnership", {}).get(
            "update"
        )
        if ownership is not None and ownership.get("implementorTarget") is not True:
            raise AdapterError(
                f"Evidence override {override_id} cannot bypass entity-operation ownership; "
                f"{entity_name!r} is not an implementor target for update."
            )
        if (
            not isinstance(fields, list)
            or not fields
            or any(not isinstance(field, str) or not field for field in fields)
            or len(fields) != len(set(fields))
        ):
            raise AdapterError(
                f"Evidence override {override_id} requires unique exact field names."
            )
        unresolved = entities[entity_name].get("unresolvedUpdateFields", {})
        ineligible = [
            field
            for field in fields
            if field not in PAYMENT_OWNED_FIELDS
            or field not in unresolved
            or unresolved[field].get("overrideEligible") is not True
        ]
        if ineligible:
            raise AdapterError(
                f"Evidence override {override_id} includes ineligible fields: {sorted(ineligible)}."
            )
        if item.get("implementorApproval") != "accept-evidence-uncertainty":
            raise AdapterError(
                f"Evidence override {override_id} requires explicit informed implementor approval."
            )
        acknowledgement = item.get("uncertaintyAcknowledgement")
        if not isinstance(acknowledgement, str) or not acknowledgement.strip():
            raise AdapterError(
                f"Evidence override {override_id} requires an uncertainty acknowledgement."
            )
        if item.get("singleSubmissionOnly") is not True:
            raise AdapterError(
                f"Evidence override {override_id} must be limited to one submission."
            )
        if item.get("automaticRetryAllowed") is not False:
            raise AdapterError(
                f"Evidence override {override_id} must prohibit automatic retry."
            )
        if operation.get("preserveOtherValues", True) is not True or operation.get(
            "preserveUnspecifiedRows", True
        ) is not True:
            raise AdapterError(
                f"Evidence override {override_id} requires full value and row preservation."
            )
        warning_matches = [
            warning
            for warning in blueprint.get("warnings", [])
            if isinstance(warning, dict)
            and warning.get("code") == "EVIDENCE_UNRESOLVED_UPDATE_OVERRIDE"
            and warning.get("operationId") == operation_id
            and warning.get("entity") == entity_name
            and set(warning.get("fields", [])) == set(fields)
            and str(warning.get("message", "")).strip()
        ]
        if len(warning_matches) != 1:
            raise AdapterError(
                f"Evidence override {override_id} requires one matching immutable-preview warning."
            )
        indexed[operation_id] = item
    return indexed


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
    evidence_overrides = _evidence_unresolved_update_override_map(
        contract, blueprint
    )
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
        ownership_operation = "update" if action == "end-date" else action
        ownership = entity.get("operationOwnership", {}).get(ownership_operation)
        if ownership is not None and ownership.get("implementorTarget") is not True:
            raise AdapterError(
                f"Operation {operation_id} cannot target {entity_name!r} for {action}; "
                "the evidence-backed entity-operation ownership contract classifies it "
                "as a package dependency or reconciliation target, not an implementor target."
            )
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
        if not isinstance(values, dict) or not values:
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
        # Apply every concrete source-backed deterministic field rule before
        # evaluating whether unresolved operation evidence needs an override.
        for field in values:
            _validate_field_value(entity, field, values[field], operation_id)
        if action == "create":
            shared_defaults = (
                _shared_create_defaults() if entity_name == "AP_SYSTEM_PARAMETER" else {}
            )
            invalid_defaults = [
                field for field, value in shared_defaults.items()
                if values.get(field) != value
            ]
            if invalid_defaults:
                raise AdapterError(
                    f"Operation {operation_id} must include shared create defaults "
                    f"at their documented values: {sorted(invalid_defaults)}. "
                    "Use Invoice Options to request different Invoice-owned settings."
                )
            create_fields = set(entity.get("createFields", {}))
            unproven = (set(target) | set(values)) - create_fields
            # These shared AP-system-option controls are governed by the
            # sibling Invoice Options create contract, which is invoked below
            # for the complete proposed row.  They are required there and
            # must not be reclassified as unproven merely because Payment
            # Options does not independently own their UI labels.
            unproven -= {
                "InvoiceCurrencyCode",
                "PaymentCurrencyCode",
                "PaymentPriority",
                "TermName",
                "WhenToAccountPmt",
            }
            # Permit only the exact shared defaults checked above, rather
            # than expanding Payment Options ownership of Invoice fields.
            unproven -= set(shared_defaults)
            if unproven:
                raise AdapterError(
                    f"Operation {operation_id} has no source-backed create contract for "
                    f"fields: {sorted(unproven)}."
                )
        if action in {"update", "end-date"}:
            update_fields = set(entity.get("updateFields", {}))
            unproven = set(values) - update_fields
            if unproven:
                override = evidence_overrides.get(operation_id)
                if override is None or set(override.get("fields", [])) != unproven:
                    raise AdapterError(
                        f"Operation {operation_id} has no source-backed update contract for "
                        f"fields: {sorted(unproven)}. A governed implementor "
                        "application-validation override must bind exactly to every "
                        "evidence-unresolved field."
                    )
            elif operation_id in evidence_overrides:
                raise AdapterError(
                    f"Operation {operation_id} declares an evidence override but has no "
                    "evidence-unresolved update field."
                )
        for field in values:
            if field in blocked and (
                entity_name, field, blocked[field]["resolver"]
            ) not in satisfied and not (
                operation_id in evidence_overrides
                and field in set(evidence_overrides[operation_id].get("fields", []))
            ):
                raise AdapterError(
                    f"Operation {operation_id} changes conditionally blocked field "
                    f"{entity_name}.{field}: {blocked[field]['reason']}"
                )
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


def _uploaded_validation_context(
    contract: dict[str, Any], baseline: PackageData, uploaded: PackageData,
    supplied: dict[str, Any] | None, reference_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Use saved lookup evidence only for the exact task, ZIP and baseline."""
    if supplied is None:
        return {}
    if not isinstance(supplied, dict):
        raise AdapterError("UPLOAD_CONTEXT_MISMATCH: validation context must be an object.")
    context = supplied.get("uploadValidationContext", supplied)
    if (not isinstance(context, dict)
            or context.get("schemaVersion") != "payment-options-upload-context-v1"
            or context.get("task") != contract["task"]
            or context.get("uploadedPackageSha256") != uploaded.archive_sha256
            or context.get("baselineSha256") != baseline.archive_sha256
            or not isinstance(context.get("resolvedScope"), dict)
            or not isinstance(context.get("prerequisites"), list)
            or not isinstance(context.get("warnings"), list)):
        raise AdapterError(
            "UPLOAD_CONTEXT_MISMATCH: use the saved build report for this exact task, ZIP and baseline."
        )
    has_receipts = bool(context.get("prerequisites") or context.get("resolvedScope", {}).get("businessUnits"))
    if has_receipts:
        selected = _reference_target(reference_context, baseline)
        if _reference_target(context.get("referenceContext"), baseline) != selected:
            raise AdapterError("REFERENCE_PROVENANCE: saved build target differs from the independently selected upload target.")
        _validate_blueprint_reference_provenance({**context, "referenceContext": selected}, baseline)
    return context


def _validate_uploaded_create_context(
    contract: dict[str, Any], blueprint: dict[str, Any], operation: dict[str, Any],
    row: dict[str, str],
) -> None:
    """Check physical ledger/currency cells against the sibling's BU receipts."""
    module, shared_contract = _load_invoice_options_shared_contract()
    entity = module._entity_map(shared_contract)[operation["entity"]]
    shared_blueprint = _shared_invoice_blueprint(blueprint, shared_contract)
    try:
        expected = {
            "SOBName": module._resolved_sob_name(shared_blueprint, entity, operation["targetKey"], operation["id"]),
            "BaseCurrencyCode": module._resolved_base_currency_code(shared_blueprint, entity, operation["targetKey"], operation["id"]),
        }
    except Exception as exc:
        raise AdapterError(f"Operation {operation['id']} uploaded create context is invalid: {exc}") from exc
    for field, value in expected.items():
        if row[field] != value:
            raise AdapterError(
                f"Operation {operation['id']} uploaded {field} does not match the resolved business-unit primary ledger."
            )


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
    validation_context: dict[str, Any] | None = None,
    reference_context: dict[str, Any] | None = None,
    target_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate an exact-task uploaded FSM ZIP without creating or importing it."""
    baseline = _read_package(baseline_path, contract)
    uploaded = _read_package(package_path, contract)
    _validate_uploaded_compatibility(baseline, uploaded, target_context)
    if _schema_fingerprint(contract, baseline) != _schema_fingerprint(contract, uploaded):
        raise AdapterError("Uploaded package schema fingerprint differs from the fresh baseline.")
    context_errors = []
    try:
        context = _uploaded_validation_context(contract, baseline, uploaded, validation_context, reference_context)
    except AdapterError as exc:
        context, context_errors = {}, [str(exc)]
    operations, descriptions, raw_errors = [], [], list(context_errors)
    uploaded_rows = {}
    for entity in contract["package"]["entities"]:
        baseline_rows, keys = _row_index(baseline, entity), {}
        for number, row in enumerate(uploaded.rows[entity["name"]], start=1):
            target = {field: row[field] for field in entity["keyFields"]}
            key = _target_tuple(entity, target)
            action = "update" if key in baseline_rows else "create"
            values = {
                field: row[field] for field in entity["headers"]
                if field not in set(entity["keyFields"]) | set(entity["auditFields"])
                # A changed blank cell on an existing row is an explicit clear.
                # Blank optional create cells remain omitted.
                and (row[field] != "" if action == "create"
                     else row[field] != baseline_rows[key][field])
            }
            # These two CSV cells are resolved BU context, not requested create
            # fields. Validate their physical values against the saved receipts.
            if action == "create" and entity["name"] == "AP_SYSTEM_PARAMETER":
                for field in ("SOBName", "BaseCurrencyCode"):
                    values.pop(field, None)
            operation_id = f"UPLOAD-{entity['name']}-{number:03d}"
            uploaded_rows[operation_id] = row
            keys.setdefault(key, []).append((number, operation_id))
            audits = [field for field in entity["auditFields"] if row.get(field, "").strip()]
            if audits:
                raw_errors.append(f"Operation {operation_id} uploaded row must leave audit fields blank: {audits}.")
            operations.append({"id": operation_id, "action": action, "entity": entity["name"], "targetKey": target, "values": values, "preserveOtherValues": True, "preserveUnspecifiedRows": True})
            descriptions.append({"row": number, "operationId": operation_id, "entity": entity["name"], "action": action, "targetKey": target})
        for key, occurrences in keys.items():
            if len(occurrences) > 1:
                rows = [number for number, _ in occurrences]
                raw_errors.extend(f"Operation {operation_id} uploaded row has duplicate target key {key!r} in rows {rows}." for _, operation_id in occurrences)
    if not operations:
        raise AdapterError("Uploaded package contains no task rows to validate.")
    blueprint = _normalized_blueprint(contract, {
        "operations": operations, "resolvedScope": context.get("resolvedScope", {}), "referenceContext": reference_context,
        "prerequisites": context.get("prerequisites", []), "warnings": context.get("warnings", []),
    })
    errors = list(raw_errors)
    for operation in blueprint["operations"]:
        isolated = dict(blueprint)
        isolated["operations"] = [operation]
        try:
            _validate_blueprint(contract, isolated, baseline)
            _validate_shared_invoice_contract(contract, isolated, baseline)
            if operation["action"] == "create":
                physical = uploaded_rows[operation["id"]]
                _validate_uploaded_create_context(contract, isolated, operation, physical)
                invalid_defaults = [
                    field for field, value in _shared_create_defaults().items()
                    if physical.get(field) != value
                ]
                if invalid_defaults:
                    raise AdapterError(
                        f"Operation {operation['id']} uploaded create must contain "
                        f"the shared create defaults in the CSV: {sorted(invalid_defaults)}. "
                        "Regenerate the ZIP; validation does not fill blank cells."
                    )
        except AdapterError as exc:
            message = str(exc)
            if operation["id"] not in message:
                message = f"Operation {operation['id']}: {message}"
            if message not in errors:
                errors.append(message)
    for item in descriptions:
        item["errors"] = [error for error in errors if item["operationId"] in error]
        item["errors"].extend(context_errors)
        item["status"] = "FAIL" if item["errors"] else "PASS"
    return {"schemaVersion": SCHEMA_VERSION, "status": "PASS" if not errors else "FAIL", "task": contract["task"], "uploadedPackageSha256": uploaded.archive_sha256, "baselineSha256": baseline.archive_sha256, "notImported": True, "candidateCreated": False, "rowResults": descriptions, "errors": errors, "warnings": context.get("warnings", [])}


def _requirements(
    contract: dict[str, Any], blueprint: dict[str, Any]
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    number = 1
    entities = _entity_map(contract) if contract.get("package") else {}
    for operation in blueprint["operations"]:
        entity = entities.get(operation["entity"], {})
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
            non_persisted = entity.get("nonPersistedFields", {}).get(field)
            result.append(
                {
                    "id": f"REQ-{number:03d}",
                    "kind": (
                        "candidate_context"
                        if operation["action"] == "create" and non_persisted
                        else "value"
                    ),
                    "requirement": (
                        f"Serialize {operation['entity']}.{field}={value} as derived create context; "
                        "the fresh export may leave it blank"
                        if operation["action"] == "create" and non_persisted
                        else f"Persist {operation['entity']}.{field}={value}"
                    ),
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
    _validate_shared_invoice_contract(contract, blueprint, baseline)
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
        "prerequisites": blueprint["prerequisites"],
        "warnings": blueprint["warnings"],
        "evidenceUnresolvedUpdateOverrides": blueprint.get(
            "evidenceUnresolvedUpdateOverrides", []
        ),
        "requirementCount": len(requirements),
    }
    return blueprint, preview, requirements


def _candidate_rows(
    contract: dict[str, Any],
    baseline: PackageData,
    blueprint: dict[str, Any],
) -> dict[str, list[dict[str, str]]]:
    """Build shared AP system-options rows through the sibling create contract.

    Payment Options owns its page-field validation, while Invoice Options owns
    the complete shared-row create mechanics: deterministic EnterpriseId
    selection and the ledger-derived SOBName/BaseCurrencyCode values.  Using
    that task-local implementation prevents a sparse Payment Options create
    from emitting an invalid all-blank shared row.
    """
    module, shared_contract = _load_invoice_options_shared_contract()
    shared_contract = json.loads(json.dumps(shared_contract))
    shared_contract["package"]["objectShortName"] = contract["package"]["objectShortName"]
    shared_baseline = module._read_package(baseline.path, shared_contract)
    return module._candidate_rows(
        shared_contract,
        shared_baseline,
        _shared_invoice_blueprint(blueprint, shared_contract),
    )


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
                if field not in allowed and row[field] != before[field]:
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
    _validate_shared_invoice_contract(contract, blueprint, baseline)
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
    result["uploadValidationContext"] = {
        "schemaVersion": "payment-options-upload-context-v1", "task": contract["task"],
        "uploadedPackageSha256": _sha256_path(output_path), "baselineSha256": baseline.archive_sha256,
        "resolvedScope": blueprint.get("resolvedScope", {}),
        "prerequisites": blueprint.get("prerequisites", []), "warnings": blueprint.get("warnings", []),
        "referenceContext": blueprint.get("referenceContext"),
    }
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


def _requested_value_equivalence(
    entity: dict[str, Any],
    field: str,
    requested: str,
    candidate: str,
    persisted: str,
) -> dict[str, Any] | None:
    """Return strict type-driven equivalence for a declared calendar date."""
    declared_type = str(entity.get("types", {}).get(field, "")).strip()
    if declared_type.lower() != "date":
        return None
    if candidate != requested:
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", requested) is None:
        return None
    if re.fullmatch(r"\d{4}/\d{2}/\d{2}", persisted) is None:
        return None
    try:
        requested_date = datetime.strptime(requested, "%Y-%m-%d").date()
        persisted_date = datetime.strptime(persisted, "%Y/%m/%d").date()
    except ValueError:
        return None
    if requested_date != persisted_date:
        return None
    return {
        "ruleId": "FSCR.TYPE.DATE.STRICT_ISO_TO_SLASH",
        "entity": entity["name"],
        "field": field,
        "declaredType": declared_type,
        "rawValues": {
            "requested": requested,
            "candidate": candidate,
            "persisted": persisted,
        },
        "canonicalValue": requested_date.isoformat(),
        "semanticValue": "same Gregorian calendar date",
        "contractEvidence": [
            f"e2e-adapter.json package.entities[{entity['name']}].types[{field}]=date",
            "Exact ASM_SETUP_CSV_METADATA.xml XmlAttributeTypeList date contract",
        ],
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
        raw_differences: list[dict[str, Any]] = []
        semantic_equivalences: list[dict[str, Any]] = []
        if kind == "target":
            passed = candidate_row is not None and persisted_row is not None
        elif kind == "value":
            field = requirement["field"]
            requested = str(requirement["requestedValue"])
            candidate_value = "" if candidate_row is None else candidate_row[field]
            persisted_value = "" if persisted_row is None else persisted_row[field]
            passed = candidate_value == requested and persisted_value == requested
            if not passed and candidate_value == requested:
                equivalence = _requested_value_equivalence(
                    entity, field, requested, candidate_value, persisted_value
                )
                if equivalence is not None:
                    passed = True
                    raw_differences.append(
                        {
                            "field": field,
                            "requested": requested,
                            "candidate": candidate_value,
                            "persisted": persisted_value,
                        }
                    )
                    semantic_equivalences.append(equivalence)
                    detail = (
                        "Retained the raw declared-date format difference under "
                        f"{equivalence['ruleId']}."
                    )
        elif kind == "candidate_context":
            field = requirement["field"]
            requested = str(requirement["requestedValue"])
            candidate_value = "" if candidate_row is None else candidate_row[field]
            persisted_value = "" if persisted_row is None else persisted_row[field]
            field_contract = entity.get("nonPersistedFields", {}).get(field, {})
            passed = (
                candidate_value == requested
                and persisted_row is not None
                and (
                    persisted_value == requested
                    or (
                        field_contract.get("classification") == "derived-transient"
                        and field_contract.get("persistedExpectation") == "blank-or-omitted"
                        and persisted_value == ""
                    )
                )
            )
            detail = (
                "Candidate carried source-backed derived context; the fresh export omitted "
                "the transient value as allowed by the field contract."
                if passed and persisted_value == ""
                else "Derived create context did not satisfy the candidate/export contract."
            )
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
                # Protect every confirmed baseline row, but do not fail solely
                # because another actor created an unrelated row after this
                # candidate's captured baseline. Requested targets remain covered by the
                # target/value requirements above and duplicate keys are
                # rejected while indexing the package.
                for row_key in sorted(baseline_rows):
                    if (entity_name, row_key) in touched:
                        continue
                    left = baseline_rows.get(row_key)
                    right = persisted_rows.get(row_key)
                    if right is None:
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
        matrix_row = {
                "requirementId": requirement["id"],
                "requirement": requirement["requirement"],
                "requested": requested,
                "candidate": candidate_value,
                "persisted": persisted_value,
                "passed": passed,
                "detail": detail,
            }
        if raw_differences:
            matrix_row["rawDifferences"] = raw_differences
        if semantic_equivalences:
            matrix_row["semanticEquivalences"] = semantic_equivalences
        matrix.append(matrix_row)
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
    validate_upload.add_argument("--reference-context", type=Path, help="Independently selected environment and HTTPS origin JSON; required when reusing reference evidence.")
    validate_upload.add_argument("--validation-context", type=Path, help="Saved build report with lookup evidence for this exact ZIP and baseline; needed for creates.")

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
                _read_json(args.validation_context) if args.validation_context else None,
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
