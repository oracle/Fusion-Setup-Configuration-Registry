#!/usr/bin/env python3
"""Portable, data-driven FSM task adapter runtime.

This file is copied into a generated Nested task skill.  Task semantics live in
the production task contract and ora-resource rule plan.  The
runtime performs offline package work only; it never connects to Fusion.
"""

from __future__ import annotations

import argparse
import importlib.util
import csv
import hashlib
import io
import json
import re
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree


SCHEMA_VERSION = "fscr-fsm-task-adapter-v1"
MAX_MEMBER_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100
SUCCESS_STATUS = re.compile(r"COMPLETE|SUCCESS|SUCCEED", re.IGNORECASE)


class AdapterError(ValueError):
    """A safe, user-correctable adapter failure."""


# Load the adjacent task-owned policy without relying on cwd or sys.path.
_policy_spec = importlib.util.spec_from_file_location("mtc_sensitive_policy", Path(__file__).with_name("sensitive_policy.py"))
_sensitive = importlib.util.module_from_spec(_policy_spec)
_policy_spec.loader.exec_module(_sensitive)


def _mtc_policy():
    try:
        return _sensitive.load()
    except (ValueError, OSError, KeyError) as exc:
        raise AdapterError("MTC-POLICY: Missing or invalid sensitive-field policy.") from exc


def _mtc_policy_check(contract, blueprint, baseline):
    if _sensitive.enabled(contract) and baseline is not None:
        try:
            _sensitive.check_blueprint(blueprint, baseline)
        except ValueError as exc:
            raise AdapterError(str(exc)) from exc


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
    if (task["code"] != "IBY_MANAGE_TRANSMISSION_CONFIGURATIONS"
            or contract.get("semanticModel", {}).get("mode") != "task-specific-extension"):
        raise AdapterError("MTC-POLICY: This task runtime requires its production identity and policy-enabled semantic mode.")
    if not isinstance(package, dict) or not package.get("entities"):
        raise AdapterError("Adapter contract lacks package entities.")
    for entity in package["entities"]:
        _nullable_key_fields(entity)
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
        archive_bytes = path if isinstance(path, bytes) else path.read_bytes()
        if isinstance(path, bytes):
            path = Path("in-memory-export.zip")
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
                f"{entity['member']} header order differs from the task contract."
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
    if not SUCCESS_STATUS.search(metadata["ProcessStatus"]):
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
        # Successful same-task exports can assign different positive ordinals.
        # Keep exact node paths/types and preserve baseline metadata in candidates.
        # Generic generated-contract fixtures retain their stricter sequence gate.
        if (actual_node_sequence != expected_node_sequence
                and contract.get("semanticModel", {}).get("mode") != "task-specific-extension"):
            raise AdapterError(
                f"Metadata node sequence for {entity['name']} is {actual_node_sequence!r}, "
                f"expected {expected_node_sequence!r} from the task contract."
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
    resolved_outputs = [path.resolve() for path in outputs]
    resolved_inputs = {path.resolve() for path in inputs}
    if len(resolved_outputs) != len(set(resolved_outputs)):
        raise AdapterError("Output paths must be distinct.")
    for path in resolved_outputs:
        if path in resolved_inputs:
            raise AdapterError(f"Output path overlaps an input: {path}.")
        if path.exists():
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


def _nullable_key_fields(entity: dict[str, Any]) -> set[str]:
    """Opt-in blank strings only; missing components and null values stay invalid."""
    rules = entity.get("nullableKeyFields", {})
    if not isinstance(rules, dict):
        raise AdapterError("nullableKeyFields must be a source-backed mapping.")
    keys = set(entity.get("keyFields", []))
    if rules and (not set(rules) < keys or set(rules) & set(entity.get("auditFields", []))):
        raise AdapterError("Nullable keys must be a proper subset of non-audit keyFields.")
    for field, rule in rules.items():
        if (str(entity.get("types", {}).get(field) or "string") != "string"
                or not isinstance(rule, dict) or set(rule) != {"sourceIds", "boundary"}
                or not isinstance(rule.get("sourceIds"), list) or not rule["sourceIds"]
                or any(not isinstance(s, str) or not s.strip() for s in rule["sourceIds"])
                or not isinstance(rule.get("boundary"), str) or not rule["boundary"].strip()
                or field in entity.get("requiredFields", [])
                or field in entity.get("createDefaults", {})):
            raise AdapterError("Invalid source-backed nullable key contract for " + field)
        domain = entity.get("valueContracts", {}).get(field, {})
        if (domain.get("constraintKind") in {"fixed-enumeration", "seeded-enumeration"}
                and domain.get("extensible") is False
                and "" not in {str(item.get("code")) for item in domain.get("allowedValues", [])}):
            raise AdapterError("Nullable key conflicts with closed value domain for " + field)

    return set(rules)


def _row_key(entity: dict[str, Any], row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row.get(field, "") for field in entity["keyFields"])


def _target_tuple(entity: dict[str, Any], target: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(target.get(field, "")) for field in entity["keyFields"])


def _validate_field_value(
    entity: dict[str, Any], field: str, value: Any, operation_id: str
) -> None:
    # Source-backed nullable serialization: helper/null typed values are
    # checked against parameter mandatory metadata by the task extension.
    if value == "" and ((entity.get("name") == "IBY_TRANSMISSION_CONFIGURATION" and field in {"EndDateDsp", "InactiveDate"}) or (entity.get("name") == "ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL" and field in {"TransmitDateValue", "TransmitNumberValue", "TransmitVarchar2Value"})):
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
    nullable = _nullable_key_fields(entity)
    result: dict[tuple[str, ...], dict[str, str]] = {}
    for number, row in enumerate(package.rows[entity["name"]], start=2):
        key = _row_key(entity, row)
        if any(field not in row or row[field] is None or (value == "" and field not in nullable)
               for field, value in zip(entity["keyFields"], key)):
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
    if not isinstance(operations, list) or (not operations and design.get("status") != "MANUAL_ONLY"):
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
        "explicitDefaults": applied_defaults,
        "preservedValues": design.get("preservedValues", []),
        "prerequisites": design.get("prerequisites", []),
        "warnings": warnings,
        "evidenceUnresolvedUpdateOverrides": evidence_overrides,
    }
    if _sensitive.enabled(contract):
        blueprint["sensitivePolicySha256"] = design.get("sensitivePolicySha256")
        blueprint["manualSteps"] = design.get("manualSteps", [])
        if design.get("status") == "MANUAL_ONLY":
            blueprint["status"] = "MANUAL_ONLY"
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
            if field not in unresolved or unresolved[field].get("overrideEligible") is not True
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
    _mtc_policy_check(contract, blueprint, baseline)
    task = blueprint.get("task")
    if task != {"name": contract["task"]["name"], "code": contract["task"]["code"]}:
        raise AdapterError("Blueprint task identity differs from the adapter contract.")
    operations = blueprint.get("operations")
    if not isinstance(operations, list) or (not operations and blueprint.get("status") != "MANUAL_ONLY"):
        raise AdapterError("Blueprint must contain at least one operation.")
    entities = _entity_map(contract)
    allowed = set(contract["normalization"]["supportedOperations"])
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
        nullable = _nullable_key_fields(entity)
        if any(value == "" and field not in nullable
               for field, value in zip(entity["keyFields"], target_tuple)):
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
            create_fields = set(entity.get("createFields", {}))
            unproven = (set(target) | set(values)) - create_fields
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
    if baseline is not None:
        _mtc_check(contract, blueprint, baseline, AdapterError)


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
    if _sensitive.enabled(contract):
        try:
            design = _sensitive.prepare(design, baseline)
        except ValueError as exc:
            # Policy errors use fixed messages and never include input values.
            raise AdapterError(str(exc)) from exc
        except (KeyError, TypeError) as exc:
            raise AdapterError("MTC-SENSITIVE-INPUT: Invalid input or embedded credentials; review the input without logging its contents.") from exc
    blueprint = _normalized_blueprint(contract, design)
    _mtc_check(contract, blueprint, baseline, AdapterError, prepare=True)
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
        "prerequisites": blueprint["prerequisites"],
        "warnings": blueprint["warnings"],
        "evidenceUnresolvedUpdateOverrides": blueprint.get(
            "evidenceUnresolvedUpdateOverrides", []
        ),
        "requirementCount": len(requirements),
    }
    if _sensitive.enabled(contract):
        preview.update(status=blueprint.get("status", "READY"),
                       sensitivePolicySha256=blueprint["sensitivePolicySha256"],
                       manualSteps=blueprint["manualSteps"])
    return blueprint, _mtc_redact_preview(blueprint, preview), requirements


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
    for entity_name, rows in output.items():
        entity = entities[entity_name]
        rows.sort(key=lambda row: _row_key(entity, row))
    return _mtc_close_ancestors(contract, baseline, output)


def _all_updates_already_satisfied(
    contract: dict[str, Any],
    baseline: PackageData,
    blueprint: dict[str, Any],
) -> bool:
    """Suppress a whole request only when every requested value already persists."""
    entities = _entity_map(contract)
    for operation in blueprint["operations"]:
        if operation["action"] != "update":
            return False
        entity = entities[operation["entity"]]
        key = _target_tuple(entity, operation["targetKey"])
        before = _row_index(baseline, entity).get(key)
        if before is None or any(
            before[field] != str(value)
            for field, value in operation["values"].items()
        ):
            return False
    return True


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
    with zipfile.ZipFile(output_path, "w") as archive:
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
                    {"code": "VALUE_MISMATCH", "message": f"{entity['name']} {key!r} {field} differs from the approved value; values withheld."}
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
    issues.extend(_mtc_validate_ancestors(contract, candidate, baseline, blueprint, expected_targets))
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
    sensitive_issues = (_sensitive.candidate_issues(candidate, baseline, blueprint)
                        if _sensitive.enabled(contract) else [])
    # Do not let ordinary mismatch diagnostics echo a blocked candidate value.
    issues = sensitive_issues or _semantic_issues(contract, candidate, baseline, blueprint, requirements)
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
    if _sensitive.enabled(contract) and blueprint.get("status") == "MANUAL_ONLY":
        return {"status": "MANUAL_ONLY", "notImported": True,
                "manualSteps": blueprint.get("manualSteps", []),
                "reason": "All supplied parameter changes require Payments UI; no candidate ZIP was written."}
    if _all_updates_already_satisfied(contract, baseline, blueprint):
        return {
            "schemaVersion": SCHEMA_VERSION,
            "status": "NO_OP",
            "task": contract["task"],
            "baselineSha256": baseline.archive_sha256,
            "designSha256": _sha256_bytes(_canonical_bytes(blueprint)),
            "reason": "All requested update values already match the current-data baseline; no candidate ZIP was written.",
            "manualSteps": blueprint.get("manualSteps", []),
        }
    rows = _candidate_rows(contract, baseline, blueprint)
    if _sensitive.enabled(contract):
        from types import SimpleNamespace
        if _sensitive.candidate_issues(SimpleNamespace(rows=rows), baseline, blueprint):
            raise AdapterError("MTC-SENSITIVE-IMPORT: Prohibited rows rejected before ZIP creation.")
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
    if _sensitive.enabled(contract):
        result["manualSteps"] = blueprint.get("manualSteps", [])
        result["sensitivePolicySha256"] = blueprint["sensitivePolicySha256"]
    for operation in result.get("businessSummary", []):
        if operation.get("entity") == "ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL":
            operation["values"] = {field: ("[protected parameter value; inspect governed design]" if field in {"TransmitVarchar2Value", "TransmitNumberValue", "TransmitDateValue"} and value not in ("", None) else value) for field, value in operation["values"].items()}
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
            f"task contract package.entities[{entity['name']}].types[{field}]=date",
            "Exact ASM_SETUP_CSV_METADATA.xml XmlAttributeTypeList date contract",
        ],
    }


def reconcile(
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
    if _sensitive.enabled(contract) and _sensitive.candidate_issues(candidate, baseline, blueprint):
        raise AdapterError("MTC-SENSITIVE-IMPORT: Reconciliation candidate contains prohibited rows.")
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
                # campaign's baseline. Requested targets remain covered by the
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
                        if (_sensitive.enabled(contract) and entity_name == VALUES and field in COLS.values()
                                and _sensitive.redact_value(_mtc_policy(),
                                    _sensitive.configs_for(baseline).get(left.get(PARENT)), left.get("TransmitParameterCode"))):
                            continue  # Never infer credential preservation from masked equality.
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
    result = {
        "schemaVersion": SCHEMA_VERSION,
        "status": "PASS" if all(row["passed"] for row in matrix) else "FAIL",
        "task": contract["task"],
        "baselineSha256": baseline.archive_sha256,
        "candidateSha256": candidate.archive_sha256,
        "exportSha256": persisted.archive_sha256,
        "requirementMatrix": matrix,
        "mismatchCount": sum(not row["passed"] for row in matrix),
    }

    if _sensitive.enabled(contract):
        result = _sensitive.safe_report(result, {
            r["id"] for r in requirements if r.get("entity") == VALUES
        })
        result["sensitiveImportCheck"] = "PASS: prohibited rows absent; only approved create placeholders permitted"
        result["credentialPreservation"] = "NOT_VERIFIED: sanitized exports do not prove secret equality"
        result["manualSteps"] = blueprint.get("manualSteps", [])
    return result


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
        # FSM date exports use YYYY/MM/DD; serialize equal calendar dates in
        # the canonical design syntax, retaining the raw before-export evidence.
        for field, value in list(values.items()):
            if entity.get("types", {}).get(field) == "date" and value:
                values[field] = date.fromisoformat(value.replace("/", "-")).isoformat()
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
        "prerequisites": forward.get("prerequisites", []),
        "warnings": [],
    }
    if _sensitive.enabled(contract):
        design["sensitivePolicySha256"] = _sensitive.digest()
        design["manualSteps"] = []
    rollback = _normalized_blueprint(contract, design)
    _validate_blueprint(contract, rollback, current)
    requirements = _requirements(contract, rollback)
    _write_json(rollback_blueprint_path, rollback)
    _write_json(rollback_requirements_path, requirements)
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
    populated = [
        entity["member"]
        for entity in contract["package"]["entities"]
        if package.rows[entity["name"]]
    ]
    return {
        "environment": environment,
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
    return parser.parse_args(argv)


def _command_succeeded(command: str, result: dict[str, Any]) -> bool:
    if command == "manifest":
        return result.get("status") == "COMPLETED"
    return result.get("status", "PASS") in {"PASS", "READY", "MANUAL_ONLY", "NO_OP"}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
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
            _write_json(args.blueprint_output, blueprint)
            _write_json(args.preview_output, preview)
            _write_json(args.requirements_output, requirements)
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
            )
        elif args.command == "reconcile":
            result = reconcile(
                contract,
                args.baseline,
                args.candidate,
                args.blueprint,
                args.requirements,
                args.export,
            )
        else:
            raise AdapterError(f"Unknown command {args.command!r}.")
        if args.report:
            _write_json(args.report, result)
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if _command_succeeded(args.command, result) else 2
    except AdapterError as exc:
        failure = {
            "schemaVersion": SCHEMA_VERSION,
            "status": "FAIL",
            "errors": [{"code": "ADAPTER_ERROR", "message": str(exc)}],
        }
        if getattr(args, "report", None):
            _write_json(args.report, failure)
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        return 2


"""Task-owned offline transmission semantics.

Uses exact target FSM export metadata, never a credential service or SQL.
MTC-OAUTH-01 deliberately blocks new/changed OAuth assignments.
"""
import copy
import json
import re
from datetime import date
from pathlib import Path

CONFIG='IBY_TRANSMISSION_CONFIGURATION'
VALUES='ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL'
TL=CONFIG+'_TRANSLATION'
PROTOCOL='ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL'
PARAM='ORA_IBY_TRANSMISSION_CONFIG_PARA'
PARENT=CONFIG+'.TransmitConfigurationName'
COLS={'VARCHAR2':'TransmitVarchar2Value','NUMBER':'TransmitNumberValue','DATE':'TransmitDateValue'}
KEYS={'PGP_PUBLIC_KEY':'PGP','PGP_PRIVATE_KEY':'PGP','PRIVATE_KEY_FILE':'SSH',
      'XML_SIGNATURE_KEY':'P12','CLIENT_AUTH_PRIVATE_KEY_FILE':'P12'}

def _fail(error, code, message):
    raise error(code+': '+message)

def _day(value, error):
    if not value: return None
    try: return date.fromisoformat(str(value).replace('/','-'))
    except ValueError: _fail(error,'MTC-DATE','Invalid calendar date.')

def _mtc_check(contract, blueprint, baseline, error, *, prepare=False):
    """Prepare only explicit derivations during normalize; recheck on every build.

    Persist only sanitized baselines and non-sensitive derived values.
    Diagnostics never include parameter values, credentials, URLs, or secrets.
    """
    if contract.get('semanticModel',{}).get('mode')!='task-specific-extension': return
    facts=_mtc_policy()['sourceFacts']
    b=baseline.rows
    configs={r['TransmitConfigurationName']:dict(r) for r in b[CONFIG]}
    protocols={r['TransmitProtocolCode']:r for r in b[PROTOCOL]}
    params={(r['TransmitProtocolCode'],r['TransmitParameterCode']):r for r in b[PARAM]}
    vals={(r[PARENT],r['TransmitParameterCode']):dict(r) for r in b[VALUES]}
    before_configs=copy.deepcopy(configs)
    before_vals=copy.deepcopy(vals)
    ops=blueprint['operations']
    touched=set(); created=set()
    def derive(op, field, value):
        values=op['values']
        if field in values:
            if str(values[field])!=str(value): _fail(error,'MTC-PARENT','Contradictory derived '+field+'.')
        elif prepare:
            values[field]=value
            blueprint.setdefault('explicitDefaults',[]).append({'operationId':op['id'],'entity':op['entity'],
                'field':field,'value':value,'sourceIds':['SRC-FSM-PACKAGE','SRC-CODE-FSM-AM'],
                'reason':'Exact parent serialization or effective-date display derivation.'})
        else: _fail(error,'MTC-SERIALIZATION','Missing normalized derivation '+field+'.')
    # Resolve all configuration creates first; operation order is not identity.
    for op in ops:
        if op.get('entity')!=CONFIG: continue
        name=op.get('targetKey',{}).get('TransmitConfigurationName')
        if not name: _fail(error,'MTC-PARENT','Missing configuration key.')
        if op['action']=='create': created.add(name)
        prior=configs.get(name,{})
        values=op.get('values',{})
        if op['action']=='update' and any(f in values and str(values[f])!=str(prior.get(f,'')) for f in ('TransmitProtocolCode','TransmitProtocolName')):
            _fail(error,'MTC-PROTOCOL-CONVERSION','Protocol conversion is outside this task contract; create a separately reviewed configuration.')
        configs[name]={**prior,**op['targetKey'],**values}
        touched.add(name)
    for op in ops:
        entity=op.get('entity'); values=op.get('values',{})
        if entity not in (CONFIG,VALUES,TL): continue # Generic ownership gate rejects other entities.
        name=op['targetKey'].get('TransmitConfigurationName') if entity==CONFIG else op['targetKey'].get(PARENT)
        config=configs.get(name)
        if not config: _fail(error,'MTC-PARENT','Owning configuration is absent from target baseline and design.')
        touched.add(name)
        protocol=config.get('TransmitProtocolCode')
        meta=protocols.get(protocol)
        if not meta: _fail(error,'MTC-PROTOCOL','Exact target protocol is missing.')
        if entity==CONFIG and op['action']=='create':
            derive(op,'TransmitProtocolName',meta['TransmitProtocolName'])
        if op['action']=='create':
            for field in ('TransmitProtocolCode','TransmitProtocolName','TransmitCodeLanguage'):
                derive(op,PROTOCOL+'.'+field,meta[field])
        else:
            prior=config if entity==CONFIG else (before_vals.get((name,op['targetKey'].get('TransmitParameterCode')),{}) if entity==VALUES else {})
            for field in ('TransmitProtocolCode','TransmitProtocolName','TransmitCodeLanguage'):
                inherited=PROTOCOL+'.'+field
                if inherited in prior and prior[inherited]!=meta[field]:
                    _fail(error,'MTC-PARENT','Target inherited protocol context is inconsistent.')
        if entity==CONFIG:
            if 'EndDate' in values or op['action']=='create':
                end=_day(values.get('EndDate',config.get('EndDate')),error)
                if end: derive(op,'EndDateDsp','' if end==date(4712,12,31) else end.isoformat())
            elif 'EndDateDsp' in values:
                end=_day(config.get('EndDate'),error)
                expected='' if end==date(4712,12,31) else (end.isoformat() if end else '')
                if values['EndDateDsp']!=expected: _fail(error,'MTC-DATE','EndDateDsp must agree with EndDate.')
            configs[name].update(values)
            if op['action']=='create' or {'StartDate','EndDate'} & set(values):
                start=_day(configs[name].get('StartDate'),error); end=_day(configs[name].get('EndDate'),error)
                if not start or not end or start>end: _fail(error,'MTC-DATE','Explicit start/end dates are required and start must not follow end.')
            tunnel=values.get('TunnelTransmitConfigurationName')
            if tunnel:
                target=configs.get(tunnel)
                if not target: _fail(error,'MTC-TUNNEL','Tunnel name is absent from target baseline/design.')
                if tunnel==name: _fail(error,'MTC-TUNNEL','Configuration cannot tunnel through itself.')
                if target.get('TunnelTransmitConfigurationName'): _fail(error,'MTC-TUNNEL','A tunnel target must not itself reference another tunnel.')
            continue
        if entity==TL:
            for f in ('Language','SourceLang'):
                v=op['targetKey'].get(f,values.get(f,''))
                if (op['action']=='create' or f in values) and not re.fullmatch(r'[A-Za-z0-9_]{1,4}',str(v)):
                    _fail(error,'MTC-LANGUAGE','Language code must be explicit and at most four characters; FSM validates installed language.')
            continue
        parameter=op['targetKey'].get('TransmitParameterCode')
        pm=params.get((protocol,parameter))
        if not pm: _fail(error,'MTC-PARAMETER','Parameter does not belong to the owning target protocol.')
        if protocol=='HTTP_MPART' and parameter=='NO_ACK':
            _fail(error,'MTC-SEED-DRIFT','HTTP_MPART.NO_ACK differs from reviewed seed metadata; preserve it unchanged.')
        prior=before_vals.get((name,parameter),{})
        if parameter=='OAUTH_TRANSMIT_CONFIG':
            if op['action']=='create' or any(str(v)!=str(prior.get(f,'')) for f,v in values.items() if f in COLS.values()):
                _fail(error,'MTC-OAUTH-01','New or changed OAuth assignment is deferred pending a governed target name-to-ID product enhancement.')
        selected=COLS.get(pm.get('TransmitParameterType','').upper())
        if not selected: _fail(error,'MTC-PARAMETER-TYPE','Unknown parameter type in target export.')
        row={**prior,**op['targetKey'],**values}
        for col in COLS.values():
            if col!=selected and row.get(col) not in ('',None):
                _fail(error,'MTC-PARAMETER-TYPE','Only the metadata-selected typed value column may be populated.')
        seed=facts['protocols'].get(protocol)
        if seed is None: _fail(error,'MTC-PARAMETER-METADATA','Required/protected metadata is not reviewed for this protocol.')
        if parameter in seed['required'] and not row.get(selected):
            _fail(error,'MTC-REQUIRED','Mandatory protocol parameter has no value.')
        if parameter in seed['secured'] and row.get(selected) and set(str(row[selected]))<={'*'}:
            _fail(error,'MTC-SECRET','Masked text cannot be supplied as a credential value.')
        vals[(name,parameter)]=row
    for name in created:
        protocol=configs[name]['TransmitProtocolCode']; seed=facts['protocols'].get(protocol)
        if seed is None: _fail(error,'MTC-PARAMETER-METADATA','Create requires reviewed mandatory parameter metadata.')
        for parameter in seed['required']:
            pm=params.get((protocol,parameter),{}); col=COLS.get(pm.get('TransmitParameterType','').upper())
            if not col or not vals.get((name,parameter),{}).get(col):
                if _sensitive.blocked(_mtc_policy(),protocol,parameter):
                    _fail(error,'MTC-MANUAL-REQUIRED','Complete the required sensitive parameter through Payments UI before this configuration can be imported; no placeholder is approved for it.')
                _fail(error,'MTC-REQUIRED','Configuration create omits a mandatory protocol parameter.')
    # DML scans every crypto parameter, including untouched values.
    for name in touched:
        for (owner,parameter),row in vals.items():
            if owner!=name or parameter not in KEYS or not row.get('TransmitVarchar2Value'): continue
            alias=row['TransmitVarchar2Value']
            if '/' in alias or '\\' in alias: _fail(error,'MTC-CREDENTIAL-PATH','Exported physical credential paths are not portable aliases.')
            matching=[p for p in blueprint.get('prerequisites',[]) if isinstance(p,dict)
                and p.get('resolverId')=='MTC-CREDENTIAL-DML' and p.get('configurationName')==name
                and p.get('parameterCode')==parameter and p.get('credentialType')==KEYS[parameter]
                and (p.get('alias')==alias if alias != _sensitive.WITHHELD else p.get('noRegistrationVerifiedInUI') is True) and p.get('baselineSha256')==baseline.archive_sha256
                and p.get('evidence') and p.get('status')=='satisfied']
            if len(matching)!=1: _fail(error,'MTC-CREDENTIAL-DML','Every crypto reference needs exact baseline-bound credential review, including unchanged references.')
            gate=matching[0]
            if gate.get('resolution')=='existing-type-and-alias': continue
            # Credential registration is manual until the core secure framework exists.
            _fail(error,'MTC-CREDENTIAL-DML','Credential registration side effects are not explicitly covered by the design.')

def _mtc_redact_preview(blueprint, preview):
    """Hide parameter content in display reports; blocked values were excluded."""
    preview = copy.deepcopy(preview)
    for op in preview.get('operations',[]):
        if op.get('entity')==VALUES:
            for field in COLS.values():
                if field in op.get('requestedValues',{}) and op['requestedValues'][field] not in ('',None):
                    op['requestedValues'][field]='[protected parameter value; inspect governed design]'
    return preview


def _mtc_close_ancestors(contract, baseline, rows):
    """Include only unchanged XML ancestors required to materialize task rows.

    Source: ASM_SETUP_CSV_METADATA.XmlNodePath and the captured FSM skipped-row
    diagnostic. Dependency serialization does not authorize metadata edits.
    """
    if contract.get('semanticModel', {}).get('mode') != 'task-specific-extension':
        return rows
    entities = _entity_map(contract)
    output = {name: [dict(row) for row in values] for name, values in rows.items()}
    parents = {
        CONFIG: (PROTOCOL, { 'TransmitProtocolCode': PROTOCOL + '.TransmitProtocolCode'}),
        VALUES: (CONFIG, {'TransmitConfigurationName': PARENT}),
        TL: (CONFIG, {'TransmitConfigurationName': PARENT}),
        PARAM: (PROTOCOL, {'TransmitProtocolCode': PROTOCOL + '.TransmitProtocolCode'}),
        PROTOCOL + '_TRANSLATION': (PROTOCOL, {'TransmitProtocolCode': 'TransmitProtocolCode'}),
        PARAM + '_TRANSLATION': (PARAM, {'TransmitProtocolCode': 'TransmitProtocolCode', 'TransmitParameterCode': 'TransmitParameterCode'}),
    }
    pending = [(name, row) for name, values in output.items() for row in values]
    while pending:
        child, row = pending.pop()
        if child not in parents:
            continue
        parent, mapping = parents[child]
        meta = entities[parent]
        key = tuple(row.get(mapping[field], '') for field in meta['keyFields'])
        if any(not part for part in key):
            raise AdapterError('MTC-ANCESTOR: Required parent identity is missing.')
        if any(_row_key(meta, existing) == key for existing in output[parent]):
            continue
        original = _row_index(baseline, meta).get(key)
        if original is None:
            raise AdapterError('MTC-ANCESTOR: Required parent row is absent from the exact baseline and design.')
        copied = dict(original)
        for field in meta['auditFields']:
            copied[field] = ''
        output[parent].append(copied)
        pending.append((parent, copied))
    for name, values in output.items():
        values.sort(key=lambda row: _row_key(entities[name], row))
    return output


def _mtc_validate_ancestors(contract, candidate, baseline, blueprint, expected_targets):
    """Allow only exact baseline ancestor rows and reject missing/altered ones."""
    if contract.get('semanticModel', {}).get('mode') != 'task-specific-extension':
        return []
    entities = _entity_map(contract)
    target_rows = {name: [] for name in entities}
    for op in blueprint['operations']:
        meta = entities[op['entity']]
        key = _target_tuple(meta, op['targetKey'])
        row = dict(_row_index(baseline, meta).get(key, {h: '' for h in meta['headers']}))
        row.update({k: str(v) for k, v in op['targetKey'].items()})
        row.update({k: str(v) for k, v in op['values'].items()})
        target_rows[op['entity']].append(row)
    closed = _mtc_close_ancestors(contract, baseline, target_rows)
    issues = []
    for name, rows in closed.items():
        meta = entities[name]
        actual = _row_index(candidate, meta)
        for expected in rows:
            key = _row_key(meta, expected)
            identity = (name, key)
            if identity in expected_targets:
                continue
            expected_targets.add(identity)
            found = actual.get(key)
            if found is None:
                issues.append({'code': 'MTC_ANCESTOR_MISSING', 'message': 'Candidate omits a required unchanged parent row in ' + name + '.'})
            elif any(found[field] != expected[field] for field in meta['headers']):
                issues.append({'code': 'MTC_ANCESTOR_CHANGED', 'message': 'Candidate changes a protected ancestor row in ' + name + '.'})
    return issues


if __name__ == "__main__":
    raise SystemExit(main())
