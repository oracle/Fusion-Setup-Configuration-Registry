#!/usr/bin/env python3
"""Offline Payables FSM packages driven by an explicit task-owned contract.

The consuming Payables task owns fields, choices, references and source effects.
This helper never authenticates, contacts Fusion, or authorizes an import.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import ipaddress
import json
import os
import re
import stat
import sys
import tempfile
import zipfile
import zlib
from dataclasses import dataclass, replace
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any
from types import FunctionType
from urllib.parse import urlsplit
from copy import deepcopy
from xml.etree import ElementTree


SCHEMA_VERSION = "fscr-fsm-task-adapter-v1"
MAX_MEMBER_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100
SUCCESS_STATUSES = frozenset({"COMPLETED"})


class AdapterError(ValueError):
    """A safe, user-correctable adapter failure."""

    def __init__(
        self,
        message: str,
        failure_class: str = "input_validation",
        recommended_action: str = "Correct the reported input and rerun local validation before preparing an import.",
    ) -> None:
        super().__init__(message)
        self.failure_class = failure_class
        self.recommended_action = recommended_action


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
        value = json.loads(path.read_text(encoding="utf-8"))
        def check_encoding(item: Any) -> None:
            if isinstance(item, str):
                item.encode("utf-8")
            elif isinstance(item, dict):
                for key, child in item.items():
                    key.encode("utf-8")
                    check_encoding(child)
            elif isinstance(item, list):
                for child in item:
                    check_encoding(child)
        check_encoding(value)
        return value
    except FileNotFoundError as exc:
        raise AdapterError(f"Required JSON input does not exist: {path}.") from exc
    except OSError as exc:
        raise AdapterError(
            f"Cannot access JSON input: {path}.",
            "artifact_persistence",
            "Check the input path and filesystem access, preserve the source file, and rerun the local command.",
        ) from exc
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise AdapterError(f"Cannot read valid JSON from {path}.") from exc


def _write_json(path: Path, value: Any) -> None:
    _publish_outputs({path: _json_bytes(value)})


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def _publish_outputs(contents: dict[Path, bytes]) -> None:
    """Stage a validated output set, then publish without replacing any file.

    Each file appears atomically. If publication of a set fails, remove only
    files this invocation just linked; existing evidence is never overwritten.
    """
    _validate_new_outputs(list(contents), [])
    staged: dict[Path, Path] = {}
    published: list[Path] = []
    try:
        for destination, content in contents.items():
            destination.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary = tempfile.mkstemp(prefix=".fscr-stage-", dir=destination.parent)
            staged[destination] = Path(temporary)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
        _validate_new_outputs(list(contents), [])
        for destination, temporary in staged.items():
            os.link(temporary, destination)
            published.append(destination)
    except (AdapterError, OSError):
        for destination in reversed(published):
            # Do not remove a path replaced by another writer after linking.
            temporary = staged[destination]
            if destination.exists() and os.path.samefile(destination, temporary):
                destination.unlink()
        raise
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AdapterError(f"{label} must be a JSON object.")
    return value


def _array(value: Any, label: str, item_type: type | None = None) -> list[Any]:
    if not isinstance(value, list) or (item_type is not None and any(not isinstance(item, item_type) for item in value)):
        raise AdapterError(f"{label} must be a JSON array" + (f" of {item_type.__name__} values." if item_type else "."))
    return value


def _string(value: Any, label: str, *, nonempty: bool = False) -> str:
    if not isinstance(value, str) or (nonempty and not value.strip()):
        raise AdapterError(f"{label} must be a" + (" nonempty" if nonempty else "") + " string.")
    return value


def _validate_design_shape(design: Any, label: str) -> None:
    """Reject malformed envelopes before dictionary access or coercion."""
    _object(design, label)
    operations = _array(design.get("operations"), f"{label}.operations", dict)
    for index, operation in enumerate(operations, 1):
        prefix = f"{label}.operations[{index}]"
        for field in ("id", "entity", "action"):
            if field in operation:
                _string(operation[field], f"{prefix}.{field}", nonempty=True)
        for field in ("targetKey", "values"):
            if field in operation:
                _object(operation[field], f"{prefix}.{field}")
        for field in ("preserveOtherValues", "preserveUnspecifiedRows"):
            if field in operation and type(operation[field]) is not bool:
                raise AdapterError(f"{prefix}.{field} must be a boolean.")
    for field in ("explicitDefaults", "preservedValues", "prerequisites", "warnings", "evidenceUnresolvedUpdateOverrides"):
        if field in design:
            _array(design[field], f"{label}.{field}", dict)
    if "resolvedScope" in design:
        _object(design["resolvedScope"], f"{label}.resolvedScope")
    if "task" in design:
        _object(design["task"], f"{label}.task")
    for index, item in enumerate(design.get("warnings", []), 1):
        if "fields" in item:
            _array(item["fields"], f"{label}.warnings[{index}].fields", str)
    for index, item in enumerate(design.get("prerequisites", []), 1):
        for field in ("entity", "field", "resolver", "status"):
            if field in item:
                _string(item[field], f"{label}.prerequisites[{index}].{field}")


def _validate_contract_shape(contract: dict[str, Any]) -> None:
    task = _object(contract.get("task"), "Adapter task")
    for field in ("name", "code"):
        _string(task.get(field), f"Adapter task.{field}", nonempty=True)
    package = _object(contract.get("package"), "Adapter package")
    for field in ("metadataMember", "objectShortName", "schemaFingerprint"):
        _string(package.get(field), f"Adapter package.{field}", nonempty=True)
    entities = _array(package.get("entities"), "Adapter package.entities", dict)
    if not entities:
        raise AdapterError("Adapter contract lacks package entities.")
    seen_names: set[str] = set()
    seen_members: set[str] = set()
    for entity in entities:
        for field in ("name", "member", "nodePath"):
            _string(entity.get(field), f"Entity {field}", nonempty=True)
        if entity["name"] in seen_names or entity["member"] in seen_members:
            raise AdapterError("Adapter contains duplicate entity names or members.")
        seen_names.add(entity["name"])
        seen_members.add(entity["member"])
        sequence = entity.get("nodeSequence")
        if type(sequence) not in (str, int) or not re.fullmatch(r"[1-9][0-9]*", str(sequence)):
            raise AdapterError("Entity nodeSequence must be a positive integer.")
        for field in ("headers", "keyFields", "auditFields", "requiredFields"):
            values = _array(entity.get(field, [] if field == "requiredFields" else None), f"Entity {entity['name']}.{field}", str)
            if len(values) != len(set(values)) or any(not item for item in values):
                raise AdapterError(f"Entity {entity['name']}.{field} must contain unique nonempty field names.")
        if not entity.get("headers") or not entity.get("keyFields"):
            raise AdapterError("Every entity requires headers and keyFields.")
        headers = set(entity["headers"])
        if any(not set(entity.get(field, [])) <= headers for field in ("keyFields", "auditFields", "requiredFields")):
            raise AdapterError("Entity field lists refer to unknown CSV headers.")
        types = _object(entity.get("types"), f"Entity {entity['name']}.types")
        if set(types) != headers or any(not isinstance(value, str) for value in types.values()):
            raise AdapterError("Entity types must declare one string type for each exact CSV header.")
        for field in ("createFields", "updateFields", "unresolvedUpdateFields", "nonPersistedFields", "fieldConstraints", "valueContracts", "createDefaults", "operationOwnership"):
            mapping = _object(entity.get(field, {}), f"Entity {entity['name']}.{field}")
            if any(not isinstance(value, dict) for value in mapping.values()):
                raise AdapterError(f"Entity {entity['name']}.{field} entries must be objects.")
        for field, constraint in entity.get("fieldConstraints", {}).items():
            maximum = constraint.get("maxLength")
            if (field not in headers or type(maximum) is not int or maximum < 1
                    or constraint.get("lengthUnit") not in ("characters", "bytes")):
                raise AdapterError("Field length constraints require a positive maxLength and characters/bytes unit.")
        for field, domain in entity.get("valueContracts", {}).items():
            _string(domain.get("constraintKind", ""), "Value contract constraintKind")
            if "restFallback" in domain:
                fallback = _object(domain["restFallback"], "Value contract REST fallback")
                _string(fallback.get("resolver"), "REST fallback resolver", nonempty=True)
                _string(fallback.get("matchField"), "REST fallback matchField", nonempty=True)
                context = _object(fallback.get("context"), "REST fallback context")
                if not context or any(type(value) not in (str, int) for value in context.values()):
                    raise AdapterError("REST fallback requires a nonempty scalar lookup context.")
            for item in _array(domain.get("allowedValues", []), "Value contract allowedValues", dict):
                for name in ("code", "label"):
                    if name in item:
                        _string(item[name], f"Value contract {name}")
                _array(item.get("synonyms", []), "Value contract synonyms", str)
        for default in entity.get("createDefaults", {}).values():
            if "value" not in default:
                raise AdapterError("Create default must declare value.")
            _array(default.get("sourceIds"), "Create default sourceIds", str)
        for blocker in _array(entity.get("conditionallyBlockedFields", []), "conditionallyBlockedFields", dict):
            for field in ("field", "resolver", "reason"):
                _string(blocker.get(field), f"Conditional blocker {field}", nonempty=True)
            if "restMatchField" in blocker:
                _string(blocker["restMatchField"], "Conditional blocker REST match field", nonempty=True)
        _nullable_key_fields(entity)
        _nullable_fields(entity)
        _derived_date_aliases(entity)
    normalization = _object(contract.get("normalization"), "Adapter normalization")
    _array(normalization.get("supportedOperations"), "Adapter supportedOperations", str)
    for field in ("referenceValidationPolicy", "evidenceUnresolvedUpdateOverridePolicy"):
        if field in normalization:
            _object(normalization[field], f"Adapter normalization.{field}")
    semantic_model = _object(contract.get("semanticModel", {}), "Adapter semanticModel")
    _array(semantic_model.get("relationships", []), "Adapter relationships", dict)


def _load_contract(path: Path) -> dict[str, Any]:
    bound_contract = globals().get("_BOUND_CONTRACT_PATH")
    if bound_contract is not None and path.resolve() != bound_contract:
        raise AdapterError("A task-bound adapter must use its declared contract path.",
                           "catalog_or_metadata_mismatch",
                           "Invoke the owning Payables task adapter with its declared contract; use this helper directly only through an explicit task-owned workflow.")
    contract = _read_json(path)
    if not isinstance(contract, dict):
        raise AdapterError("Adapter contract must be a JSON object.")
    if contract.get("schemaVersion") not in (SCHEMA_VERSION, "fscr-fsm-task-adapter-v2"):
        raise AdapterError(
            f"Unsupported adapter schema: {contract.get('schemaVersion')!r}."
        )
    _validate_contract_shape(contract)
    _parent_relationships(contract)
    _related_value_rules(contract)
    _source_effects(contract, {"operations": []})
    return contract


def _derived_date_aliases(entity: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Accept only explicit same-entity date aliases, never name heuristics."""
    aliases = entity.get("derivedDateAliases", {})
    if not isinstance(aliases, dict):
        raise AdapterError("derivedDateAliases must be an object.")
    protected = set(entity.get("keyFields", [])) | set(entity.get("auditFields", []))
    for field, rule in aliases.items():
        if not isinstance(rule, dict):
            raise AdapterError("Derived date alias requires a source-backed rule.")
        source = rule.get("sourceField")
        evidence = rule.get("sourceIds")
        sentinel = rule.get("blankWhenSourceEquals")
        if (not isinstance(source, str) or field == source or field not in entity["headers"] or source not in entity["headers"]
                or field in protected or source in aliases
                or entity.get("types", {}).get(field) != "date"
                or entity.get("types", {}).get(source) != "date"
                or not isinstance(evidence, list) or not evidence
                or any(not isinstance(s, str) or not s.strip() for s in evidence)
                or not isinstance(sentinel, str)):
            raise AdapterError("Invalid source-backed derived date alias contract.")
        try:
            if date.fromisoformat(sentinel).isoformat() != sentinel:
                raise ValueError()
        except ValueError as exc:
            raise AdapterError("Derived date alias requires a strict ISO sentinel.") from exc
    return aliases


def _derived_date_value(rule: dict[str, Any], row: dict[str, str]) -> str:
    raw = row[rule["sourceField"]]
    if raw == "":
        return ""
    for pattern in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            value = datetime.strptime(raw, pattern).date().isoformat()
            if datetime.strptime(raw, pattern).strftime(pattern) != raw:
                continue
            return "" if value == rule["blankWhenSourceEquals"] else value
        except ValueError:
            continue
    raise AdapterError("Derived date alias source is not a supported calendar date.")


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
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
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
        if len(attributes) != len(set(attributes)):
            raise AdapterError(f"Metadata object {name} contains duplicate attributes.")
        result[name] = {
            "nodePath": _first_xml_text(node, "XmlNodePath"),
            "nodeSequence": _first_xml_text(node, "NodeSequence"),
            "types": dict(zip(attributes, types)),
        }
    return result


def _node_sequence_policy(contract: dict[str, Any]) -> dict[str, str] | None:
    policy = contract["package"].get("nodeSequencePolicy")
    if policy is None:
        return None  # Legacy descriptors retain exact entity-bound checks.
    if not isinstance(policy, dict) or set(policy) != {"mode", "sourceEvidence", "xmlFileByEntity"}:
        raise AdapterError("Invalid nodeSequencePolicy contract.")
    evidence = policy["sourceEvidence"]
    groups = policy["xmlFileByEntity"]
    names = {entity["name"] for entity in contract["package"]["entities"]}
    if (policy["mode"] != "export-local"
            or not isinstance(evidence, list) or not evidence
            or any(not isinstance(item, str) or not item.strip() for item in evidence)
            or not isinstance(groups, dict) or set(groups) != names
            or any(not isinstance(value, str) or not value.strip() for value in groups.values())):
        raise AdapterError("Export-local sequencing requires source evidence and exact XML-file mapping for every entity.")
    return groups


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
                member_type = stat.S_IFMT(info.external_attr >> 16) if info.create_system == 3 else 0
                if member_type not in {0, stat.S_IFREG}:
                    raise AdapterError(f"Nonregular ZIP members are not allowed: {info.filename!r}.")
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
    except FileNotFoundError as exc:
        raise AdapterError(f"Required FSM ZIP input does not exist: {path}.") from exc
    except OSError as exc:
        raise AdapterError(
            f"Cannot access FSM ZIP input: {path}.",
            "artifact_persistence",
            "Check the input path and filesystem access, preserve the source file, and rerun the local command.",
        ) from exc
    except (zipfile.BadZipFile, RuntimeError, zlib.error) as exc:
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
    except (ElementTree.ParseError, LookupError, UnicodeError) as exc:
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
    if set(object_contracts) != {entity["name"] for entity in contract["package"]["entities"]}:
        raise AdapterError("Metadata business object inventory differs from the exact task contract.")
    sequence_groups = _node_sequence_policy(contract)
    sequence_slots: dict[tuple[str, int, int], str] = {}
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
        if sequence_groups is None and actual_node_sequence != expected_node_sequence:
            raise AdapterError(
                f"Metadata node sequence for {entity['name']} is {actual_node_sequence!r}, "
                f"expected {expected_node_sequence!r} from e2e-adapter.json."
            )
        if sequence_groups is not None:
            path_parts = actual["nodePath"].split("/")
            if not actual["nodePath"].startswith("/") or not all(path_parts[1:]) or len(path_parts) % 2 != 1:
                raise AdapterError(f"Invalid paired XML node path for {entity['name']}.")
            # Node sequence values must be unique within each XML file and hierarchy level.
            slot = (sequence_groups[entity["name"]], len(path_parts) // 2, int(actual_node_sequence))
            if slot in sequence_slots:
                raise AdapterError(f"NodeSequence collision in XML file/level: {sequence_slots[slot]} and {entity['name']}.")
            sequence_slots[slot] = entity["name"]
        for field, actual_type in actual["types"].items():
            if field not in entity["headers"]:
                raise AdapterError(
                    f"Metadata object {entity['name']} contains non-CSV attribute {field}."
                )
            if entity["types"].get(field, "") != actual_type:
                raise AdapterError(
                    f"Metadata type for {entity['name']}.{field} is {actual_type!r}, expected {entity['types'].get(field, '')!r}."
                )
    package = PackageData(
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
    fingerprint = _schema_fingerprint(contract, package)
    if fingerprint != contract["package"]["schemaFingerprint"]:
        raise AdapterError(
            f"Package schema fingerprint {fingerprint} differs from the exact task contract; "
            "require complete source metadata before normalizing, building or accepting a no-op."
        )
    return package


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


def _validate_new_outputs(outputs: list[Path], inputs: list[Path], workspace: Path | None = None) -> None:
    def refuse(message: str) -> None:
        raise AdapterError(
            message,
            "approval_blocker",
            "Choose new, distinct output files under the intended project workspace; preserve all input and existing evidence files.",
        )

    try:
        resolved_inputs = {path.resolve() for path in inputs}
    except RuntimeError:
        refuse("Input path cannot be safely resolved.")
    resolved_outputs = []
    for output in outputs:
        absolute = output.absolute()
        for part in (absolute, *absolute.parents):
            if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
                refuse(f"Linked output paths are not allowed: {output}.")
            if part != absolute and part.exists() and not part.is_dir():
                raise AdapterError(
                    f"Output parent is not a directory: {part}.",
                    "artifact_persistence",
                    "Choose an output whose parent can be created as a directory under the intended project workspace.",
                )
        resolved = output.resolve()
        if workspace is not None and not resolved.is_relative_to(workspace.resolve()):
            refuse(f"Output path is outside the selected workspace: {output}.")
        if resolved in resolved_inputs:
            refuse(f"Output path overlaps an input: {output}.")
        if output.exists():
            refuse(f"Refusing to overwrite existing output: {output}.")
        if any(str(resolved).casefold() == str(other).casefold()
               or resolved in other.parents or other in resolved.parents
               for other in resolved_outputs):
            refuse("Output paths must be distinct files and must not contain one another.")
        resolved_outputs.append(resolved)


def _preflight_command_outputs(args: argparse.Namespace) -> None:
    paths = {name: value for name, value in vars(args).items()
             if isinstance(value, Path) and name != "workspace"}
    output_names = {name for name in paths if name in {"output", "report"} or name.endswith("_output")}
    _validate_new_outputs(
        [path for name, path in paths.items() if name in output_names],
        [path for name, path in paths.items() if name not in output_names],
        getattr(args, "workspace", None),
    )


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


def _nullable_fields(entity: dict[str, Any]) -> set[str]:
    """Allow typed clears only for descriptor-declared source-supported fields."""
    rules = _object(entity.get("nullableFields", {}), "nullableFields")
    prohibited = set(entity.get("keyFields", [])) | set(entity.get("auditFields", [])) | set(entity.get("requiredFields", []))
    numeric_date_types = {"integer", "short", "int", "long", "number", "float", "double", "bigdecimal", "decimal", "date", "datetime", "timestamp"}
    for field, rule in rules.items():
        if (field not in entity["headers"] or field in prohibited
                or entity["types"].get(field, "").lower() not in numeric_date_types
                or not isinstance(rule, dict) or set(rule) != {"sourceIds", "when"}
                or not isinstance(rule["sourceIds"], list) or not rule["sourceIds"]
                or any(not isinstance(item, str) or not item.strip() for item in rule["sourceIds"])
                or not isinstance(rule["when"], dict) or not rule["when"]
                or any(name not in entity["headers"] or name == field or not isinstance(value, str)
                       for name, value in rule["when"].items())):
            raise AdapterError(f"Invalid source-backed nullable field contract for {field}.")
    return set(rules)


def _validate_nullable_context(
    entity: dict[str, Any], operation: dict[str, Any], current: dict[str, str] | None
) -> None:
    effective = {**(current or {}), **operation["targetKey"], **operation["values"]}
    for field in _nullable_fields(entity):
        if field not in operation["values"] or operation["values"][field] != "":
            continue
        condition = entity["nullableFields"][field]["when"]
        if any(effective.get(name) != value for name, value in condition.items()):
            raise AdapterError(
                f"Operation {operation['id']} may clear {entity['name']}.{field} only "
                f"under its source-backed effective-field condition {condition!r}."
            )


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
    if value == "" and field in _nullable_fields(entity):
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
    if value is None and field in _nullable_fields(entity):
        return ""
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
    package: PackageData,
    entity: dict[str, Any],
    cache: dict[str, dict[tuple[str, ...], dict[str, str]]] | None = None,
) -> dict[tuple[str, ...], dict[str, str]]:
    if not entity["keyFields"]:
        raise AdapterError(f"Entity {entity['name']} has no source-backed key.")
    if cache is not None and entity["name"] in cache:
        return cache[entity["name"]]
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
    if cache is not None:
        cache[entity["name"]] = result
    return result


def _rest_validation_unavailable(
    message: str,
    failure_class: str = "transport_or_environment",
    recommended_action: str = "Obtain a complete successful response through the declared read-only reference workflow; preserve the supplied business value.",
) -> AdapterError:
    return AdapterError(message, failure_class, recommended_action)


def _rest_reference_match(item: dict[str, Any]) -> bool:
    """Accept existence evidence, including multiple rows, without selecting an ID."""
    result = item["restResult"]
    label = f"{item.get('entity', '')}.{item.get('field', '')}"
    if not isinstance(result, dict):
        raise _rest_validation_unavailable(f"REST reference validation unavailable for {label}: malformed response.")
    status = result.get("httpStatus")
    if type(status) is not int or not 200 <= status < 300:
        failure_class, action = {
            401: ("auth_expired_or_invalid", "Return to the selected authentication workflow to renew access before the authorized read; preserve the supplied business value."),
            403: ("authorization_or_privilege", "Resolve access through the selected authentication and privilege workflow before the authorized read; preserve the supplied business value."),
        }.get(status, ("fusion_api_error", "Inspect the failed reference response through the declared Core workflow; preserve the supplied business value and follow its read-only retry policy.")) if type(status) is int else (
            "transport_or_environment", "Obtain a valid HTTP response through the declared read-only reference workflow; preserve the supplied business value."
        )
        raise _rest_validation_unavailable(f"REST reference validation unavailable for {label}: HTTP response was not successful.", failure_class, action)
    if "hasMore" in result and type(result["hasMore"]) is not bool:
        raise _rest_validation_unavailable(f"REST reference validation unavailable for {label}: malformed paging state.")
    rows = result.get("items")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise _rest_validation_unavailable(f"REST reference validation unavailable for {label}: malformed items array.")
    if not rows:
        if result.get("hasMore") is True:
            raise _rest_validation_unavailable(f"REST reference validation unavailable for {label}: additional pages remain.")
        raise AdapterError(f"REST reference {label} returned no matching row for the requested value.")
    return True


def _validate_reference_fallbacks(
    entity: dict[str, Any], operation: dict[str, Any], blueprint: dict[str, Any]
) -> None:
    """Require matching field-bound REST evidence only outside a listed domain."""
    for field, domain in entity.get("valueContracts", {}).items():
        fallback = domain.get("restFallback")
        if not fallback or field not in operation["values"]:
            continue
        value = operation["values"][field]
        if value in {item.get("code") for item in domain.get("allowedValues", [])}:
            continue
        matched = False
        for item in blueprint.get("prerequisites", []):
            if (item.get("operationId") != operation["id"]
                    or item.get("entity") != entity["name"] or item.get("field") != field
                    or item.get("resolver") != fallback["resolver"]
                    or not isinstance(item.get("evidence"), str) or not item["evidence"].strip()
                    or "restResult" not in item):
                continue
            context = item.get("lookupContext")
            if not isinstance(context, dict) or any(
                    key not in context or type(context[key]) is not type(expected)
                    or context[key] != expected for key, expected in fallback["context"].items()):
                continue
            _rest_reference_match(item)
            if any(row.get(fallback["matchField"]) == value for row in item["restResult"]["items"]):
                matched = True
                break
            if any(fallback["matchField"] not in row for row in item["restResult"]["items"]):
                raise _rest_validation_unavailable(f"REST reference validation unavailable for {entity['name']}.{field}: matching field is missing.")
            if item["restResult"].get("hasMore") is True:
                raise _rest_validation_unavailable(f"REST reference validation unavailable for {entity['name']}.{field}: additional pages remain.")
        if not matched:
            raise AdapterError(
                f"Operation {operation['id']} field {entity['name']}.{field} has an unlisted value; "
                f"require matching REST fallback evidence from {fallback['resolver']} before preparing a candidate."
            )


def _satisfied_prerequisites(
    blueprint: dict[str, Any], contract: dict[str, Any]
) -> set[tuple[str, ...]]:
    declared = {
        (entity["name"], blocker["field"]): blocker
        for entity in contract["package"]["entities"]
        for blocker in entity.get("conditionallyBlockedFields", [])
    }
    entities = _entity_map(contract)
    policy = contract.get("normalization", {}).get("referenceValidationPolicy", {})
    extra = policy.get("additionalReceiptContracts", [])
    if not isinstance(extra, list):
        raise AdapterError("Additional REST reference contracts must be an array.")
    additional = {}
    for rule in extra:
        if not isinstance(rule, dict) or any(not isinstance(rule.get(k), str) or not rule[k].strip() for k in ("entity", "field", "resolver", "matchField")):
            raise AdapterError("Additional REST reference contracts require entity, field, resolver and matchField.")
        key = (rule["entity"], rule["field"], rule["resolver"])
        if key in additional or rule["entity"] not in entities:
            raise AdapterError("Additional REST reference contracts must identify a unique known entity and resolver.")
        context = rule.get("lookupContext", {})
        if not isinstance(context, dict) or any(type(v) not in (str, int) for v in context.values()):
            raise AdapterError("Additional REST reference lookupContext must contain scalar values.")
        additional[key] = rule
    operations = blueprint.get("operations", [])
    satisfied: set[tuple[str, ...]] = set()
    for item in blueprint.get("prerequisites", []):
        if not isinstance(item, dict):
            continue
        if (
            contract.get("normalization", {}).get("referenceValidationPolicy", {}).get("mode")
            == "rest-at-least-one-row"
            and "restResult" in item
        ):
            entity = item.get("entity")
            field = item.get("field")
            resolver = item.get("resolver")
            if not all(isinstance(value, str) and value.strip() for value in (entity, field, resolver)):
                raise AdapterError("REST reference validation unavailable: entity, field and resolver are required.", "catalog_or_metadata_mismatch", "Obtain an operation-bound receipt through the declared reference workflow.")
            # The configured-label fallback has its own context-bound validator.
            domain = entities.get(entity, {}).get("valueContracts", {}).get(field, {})
            fallback = domain.get("restFallback", {})
            if fallback and resolver == fallback.get("resolver"):
                continue
            blocker = declared.get((entity, field))
            extra_rule = additional.get((entity, field, resolver))
            match_field = extra_rule.get("matchField") if extra_rule else blocker.get("restMatchField") if blocker and resolver == blocker.get("resolver") else None
            if not match_field:
                raise AdapterError("REST reference validation unavailable: no declared matching contract for this field and resolver.", "catalog_or_metadata_mismatch", "Use a declared reference contract or report unavailable validation.")
            expected_context = extra_rule.get("lookupContext", {}) if extra_rule else {}
            context = item.get("lookupContext")
            if expected_context and (not isinstance(context, dict) or any(k not in context or type(context[k]) is not type(v) or context[k] != v for k, v in expected_context.items())):
                raise AdapterError("REST reference validation unavailable: lookup context does not match the declared contract.", "catalog_or_metadata_mismatch", "Obtain an operation-bound receipt through the declared reference workflow.")
            operation_id = item.get("operationId")
            evidence = item.get("evidence")
            if not isinstance(operation_id, str) or not operation_id.strip() or not isinstance(evidence, str) or not evidence.strip():
                raise AdapterError("REST reference validation unavailable: operation identity and evidence are required.", "catalog_or_metadata_mismatch", "Obtain an operation-bound receipt through the declared reference workflow.")
            matches = [op for op in operations if isinstance(op, dict) and op.get("id") == operation_id and op.get("entity") == entity]
            if len(matches) != 1:
                raise AdapterError("REST reference validation unavailable: receipt does not identify exactly one matching operation.", "catalog_or_metadata_mismatch", "Obtain an operation-bound receipt through the declared reference workflow.")
            operation = matches[0]
            target, values = operation.get("targetKey"), operation.get("values")
            if not isinstance(target, dict) or not isinstance(values, dict):
                raise AdapterError("REST reference validation unavailable: operation fields are missing.", "catalog_or_metadata_mismatch", "Supply the exact operation and its reference evidence.")
            supplied = [part[field] for part in (target, values) if field in part]
            if not supplied or any(value != supplied[0] or type(value) is not type(supplied[0]) for value in supplied):
                raise AdapterError("REST reference validation unavailable: the requested field value is missing or ambiguous.", "catalog_or_metadata_mismatch", "Supply the exact operation and its reference evidence.")
            _rest_reference_match(item)
            if not any(match_field in row and type(row[match_field]) is type(supplied[0]) and row[match_field] == supplied[0] for row in item["restResult"]["items"]):
                if any(match_field not in row for row in item["restResult"]["items"]):
                    raise _rest_validation_unavailable(f"REST reference validation unavailable for {entity}.{field}: matching field is missing.")
                if item["restResult"].get("hasMore") is True:
                    raise _rest_validation_unavailable(f"REST reference validation unavailable for {entity}.{field}: additional pages remain.")
                raise AdapterError(f"REST reference {entity}.{field} returned no matching row for the requested value.")
            satisfied.add((operation_id, entity, field, resolver))
            continue
        if item.get("status") not in {
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
            and declared.get((entity, field), {}).get("resolver") == resolver
        ):
            satisfied.add((entity, field, resolver))
    return satisfied


def _normalized_blueprint(
    contract: dict[str, Any], design: dict[str, Any]
) -> dict[str, Any]:
    _validate_design_shape(design, "Normalized design")
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
        if "values" not in operation or not isinstance(operation["values"], dict):
            raise AdapterError(
                f"Operation {operation['id']} must supply a values object."
            )
        entity = entities.get(operation.get("entity"))
        if entity is not None:
            target = dict(operation.get("targetKey") or {})
            operation["targetKey"] = {
                field: _normalize_field_value(
                    entity, field, value, operation["id"]
                )
                for field, value in target.items()
            }
            values = dict(operation["values"])
            operation["values"] = {
                field: _normalize_field_value(
                    entity, field, value, operation["id"]
                )
                for field, value in values.items()
            }
        if operation["action"] == "create" and operation.get("entity") in entities:
            entity = entities[operation["entity"]]
            values = dict(operation["values"])
            # A declared setter effect takes precedence over an omitted field's
            # ordinary create default; explicit conflicting inputs still fail.
            effect_defaults = {effect["field"]: effect for effect in
                               _source_effects(contract, {"operations": [operation]})
                               if effect["kind"] in {"set-field", "clear-field"}}
            for field, default in entity.get("createDefaults", {}).items():
                if field in values:
                    continue
                effect = effect_defaults.get(field)
                values[field] = effect.get("value", "") if effect else default["value"]
                applied_defaults.append(
                    {
                        "operationId": operation["id"],
                        "entity": entity["name"],
                        "field": field,
                        "value": values[field],
                        "sourceIds": effect["sourceIds"] if effect else default["sourceIds"],
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
    blueprint["sourceEffects"] = _source_effects(contract, blueprint)
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


def _related_value_rules(contract: dict[str, Any]) -> list[dict[str, Any]]:
    """Read source-bound local field relationships without domain assumptions."""
    rules = contract.get("semanticModel", {}).get("relatedValueRules", [])
    if not isinstance(rules, list):
        raise AdapterError("relatedValueRules must be an array.")
    entities = _entity_map(contract)
    seen: set[str] = set()
    for rule in rules:
        if not isinstance(rule, dict):
            raise AdapterError("Each related-value rule must be an object.")
        rule_id = rule.get("id")
        entity_name = rule.get("entity")
        if (not isinstance(rule_id, str) or not rule_id.strip() or rule_id in seen
                or not isinstance(entity_name, str) or entity_name not in entities):
            raise AdapterError("Related-value rules require unique ids and an exact entity.")
        seen.add(rule_id)
        headers = set(entities[entity_name]["headers"])
        for key in ("triggerFields", "requireNonblank", "requireEmpty"):
            fields = rule.get(key, [])
            if (not isinstance(fields, list)
                    or any(not isinstance(field, str) or field not in headers for field in fields)
                    or len(set(fields)) != len(fields)
                    or (key == "triggerFields" and not fields)):
                raise AdapterError(f"Invalid {key} in related-value rule {rule_id}.")
        required = rule.get("requireNonblank", [])
        empty = rule.get("requireEmpty", [])
        condition = rule.get("when")
        evidence = rule.get("sourceIds")
        if (not required and not empty) or set(required) & set(empty):
            raise AdapterError(f"Conflicting or absent related-value assertions for {rule_id}.")
        if (not isinstance(condition, dict)
                or not isinstance(condition.get("field"), str)
                or condition["field"] not in headers
                or not isinstance(condition.get("operator"), str)
                or condition["operator"] not in {"equals", "not-equals", "blank"}
                or (condition.get("operator") != "blank"
                    and not isinstance(condition.get("value"), str))
                or not isinstance(evidence, list) or not evidence
                or any(not isinstance(item, str) or not item.strip() for item in evidence)):
            raise AdapterError(f"Invalid source-backed condition in related-value rule {rule_id}.")
        if not ({condition["field"]} | set(required) | set(empty)) <= set(rule["triggerFields"]):
            raise AdapterError(f"Related-value rule {rule_id} must trigger on every related field.")
        for fields, message_key in ((required, "requiredMessage"), (empty, "emptyMessage")):
            if fields and (not isinstance(rule.get(message_key), str)
                           or not rule[message_key].strip()):
                raise AdapterError(f"Related-value rule {rule_id} requires {message_key}.")
    return rules


def _validate_related_value_context(
    contract: dict[str, Any],
    entity: dict[str, Any],
    operation: dict[str, Any],
    current: dict[str, str] | None,
) -> None:
    """Check only changed relationships, with fresh retained state for updates."""
    values = operation["values"]
    for rule in _related_value_rules(contract):
        if rule["entity"] != entity["name"]:
            continue
        if operation["action"] != "create":
            if not set(rule["triggerFields"]).intersection(values) or current is None:
                continue
        effective = {**(current or {}), **operation["targetKey"], **values}
        condition = rule["when"]
        raw = effective.get(condition["field"])
        normalized = str(raw or "").strip().casefold()
        operator = condition["operator"]
        matches = (not normalized if operator == "blank" else
                   normalized == condition["value"].strip().casefold())
        if operator == "not-equals":
            matches = not matches
        if not matches:
            continue
        missing = [field for field in rule.get("requireNonblank", [])
                   if effective.get(field) is None or not str(effective[field]).strip()]
        if missing:
            raise AdapterError(
                f"Operation {operation['id']} {rule['requiredMessage']} "
                f"Missing fields: {', '.join(missing)}."
            )
        nonempty = [field for field in rule.get("requireEmpty", [])
                    if effective.get(field) not in (None, "")]
        if nonempty:
            raise AdapterError(f"Operation {operation['id']} {rule['emptyMessage']}")


def _parent_relationships(contract: dict[str, Any]) -> list[dict[str, Any]]:
    entities = _entity_map(contract)
    relationships = contract.get("semanticModel", {}).get("relationships", [])
    if not isinstance(relationships, list):
        raise AdapterError("Parent relationships must be a list.")
    seen = set()
    for relationship in relationships:
        if not isinstance(relationship, dict):
            raise AdapterError("Each parent relationship must be an object.")
        child_name = relationship.get("childEntity")
        parent_name = relationship.get("parentEntity")
        child_fields = relationship.get("childFields")
        parent_fields = relationship.get("parentFields")
        evidence = relationship.get("sourceIds")
        if (not isinstance(child_name, str) or not isinstance(parent_name, str)
                or child_name not in entities or parent_name not in entities
                or child_name == parent_name or child_name in seen
                or not isinstance(child_fields, list) or not child_fields
                or any(not isinstance(field, str) for field in child_fields)
                or len(set(child_fields)) != len(child_fields)
                or not isinstance(parent_fields, list)
                or parent_fields != entities[parent_name]["keyFields"]
                or len(child_fields) != len(parent_fields)
                or any(field not in entities[child_name]["headers"] for field in child_fields)
                or not isinstance(evidence, list) or not evidence
                or any(not isinstance(value, str) or not value.strip() for value in evidence)):
            raise AdapterError("Invalid source-backed child-to-parent relationship.")
        seen.add(child_name)
    policy = contract.get("semanticModel", {}).get("parentRelationshipPolicy")
    if policy is not None:
        if not isinstance(policy, dict):
            raise AdapterError("Parent relationship policy must be an object.")
        roots = policy.get("rootEntities")
        evidence = policy.get("sourceIds")
        if (not isinstance(roots, list) or not roots
                or any(not isinstance(name, str) or name not in entities for name in roots)
                or len(set(roots)) != len(roots)
                or policy.get("coverage") != "all-non-root-entities"
                or policy.get("childFieldBinding") != "qualified-parent-keys"
                or not isinstance(evidence, list) or not evidence
                or any(not isinstance(item, str) or not item.strip() for item in evidence)):
            raise AdapterError("Invalid source-backed parent relationship policy.")
        if seen != set(entities) - set(roots) or any(
            item["parentEntity"] not in roots
            or item["childFields"] != [item["parentEntity"] + "." + field
                                       for field in item["parentFields"]]
            for item in relationships
        ):
            raise AdapterError("Every non-root entity requires its exact parent relationship.")
    return relationships


def _validate_parent_targets(
    contract: dict[str, Any], blueprint: dict[str, Any], baseline: PackageData | None
) -> None:
    relationships = _parent_relationships(contract)
    if baseline is None:
        return  # Existing-parent membership is checked when a current baseline is supplied.
    entities = _entity_map(contract)
    indexes = {}
    created = {
        (operation["entity"], _target_tuple(entities[operation["entity"]], operation["targetKey"]))
        for operation in blueprint["operations"] if operation["action"] == "create"
    }
    for relationship in relationships:
        parent = entities[relationship["parentEntity"]]
        parents = _row_index(baseline, parent, indexes)
        for operation in blueprint["operations"]:
            if operation["entity"] != relationship["childEntity"]:
                continue
            effective = {**operation["targetKey"], **operation["values"]}
            key = tuple(str(effective[field]) for field in relationship["childFields"])
            if key not in parents and (parent["name"], key) not in created:
                raise AdapterError(
                    f"Operation {operation['id']} references a missing parent {key!r}; "
                    "select an existing parent or explicitly create that parent in the same request."
                )


def _validate_blueprint(
    contract: dict[str, Any],
    blueprint: dict[str, Any],
    baseline: PackageData | None = None,
) -> None:
    _validate_design_shape(blueprint, "Blueprint")
    task = blueprint.get("task")
    if task != {"name": contract["task"]["name"], "code": contract["task"]["code"]}:
        raise AdapterError("Blueprint task identity differs from the adapter contract.")
    operations = blueprint.get("operations")
    if not isinstance(operations, list) or not operations:
        raise AdapterError("Blueprint must contain at least one operation.")
    entities = _entity_map(contract)
    # Every row is carried into a candidate or preservation comparison, even
    # when the request targets a different entity or resolves to a no-op.
    # Qualify all keys before producing a preview, result, or package.
    if baseline is not None:
        for entity in entities.values():
            _row_index(baseline, entity)
    allowed = set(contract["normalization"]["supportedOperations"])
    satisfied = _satisfied_prerequisites(blueprint, contract)
    evidence_overrides = _evidence_unresolved_update_override_map(
        contract, blueprint
    )
    seen_ids: set[str] = set()
    seen_targets: set[tuple[str, tuple[str, ...]]] = set()
    baseline_indexes = {}
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
                and (operation_id, entity_name, field, blocked[field]["resolver"]) not in satisfied
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
        if not isinstance(values, dict) or (not values and action != "create"):
            raise AdapterError(f"Operation {operation_id} must supply values.")
        for field, rule in _derived_date_aliases(entity).items():
            if field in values and rule["sourceField"] in values:
                expected = _derived_date_value(rule, values)
                actual = values[field]
                if actual != expected and not (expected and _requested_value_equivalence(entity, field, expected, expected, actual)):
                    raise AdapterError(f"Operation {operation_id} supplies contradictory source and derived dates.")
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
        _validate_reference_fallbacks(entity, operation, blueprint)
        if action == "create":
            create_fields = set(entity.get("createFields", {}))
            unproven = (set(target) | set(values)) - create_fields
            if unproven:
                raise AdapterError(
                    f"Operation {operation_id} has no source-backed create contract for "
                    f"fields: {sorted(unproven)}."
                )
            proposed = {**target, **values}
            missing_required = [
                field
                for field in entity.get("requiredFields", [])
                if field not in proposed
                or proposed[field] is None
                or (isinstance(proposed[field], str) and not proposed[field].strip())
            ]
            if missing_required:
                raise AdapterError(
                    f"Operation {operation_id} is missing required create fields: "
                    f"{sorted(missing_required)}."
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
            ) not in satisfied and (
                operation_id, entity_name, field, blocked[field]["resolver"]
            ) not in satisfied and not (
                operation_id in evidence_overrides
                and field in set(evidence_overrides[operation_id].get("fields", []))
            ):
                raise AdapterError(
                    f"Operation {operation_id} changes conditionally blocked field "
                    f"{entity_name}.{field}: {blocked[field]['reason']}"
                )
        current = None
        if baseline is not None:
            matches = _row_index(baseline, entity, baseline_indexes)
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
            current = matches.get(target_tuple)
        _validate_related_value_context(contract, entity, operation, current)
        _validate_nullable_context(entity, operation, current)
    _validate_parent_targets(contract, blueprint, baseline)


def _source_effects(contract: dict[str, Any], blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    """Derive only declared effects of explicitly supplied setter values."""
    entities = _entity_map(contract) if contract.get("package") else {}
    rules = contract.get("package", {}).get("sourceEffects", [])
    if not isinstance(rules, list):
        raise AdapterError("sourceEffects must be an array of source-backed rules.")
    effects = []
    seen = set()
    for rule in rules:
        if not isinstance(rule, dict) or not isinstance(rule.get("id"), str) or not rule["id"] or rule["id"] in seen:
            raise AdapterError("Each source effect requires a unique nonblank id.")
        seen.add(rule["id"])
        if not isinstance(rule.get("entity"), str):
            raise AdapterError("Source effect entity must be a string.")
        entity = entities.get(rule["entity"])
        trigger = rule.get("trigger")
        sources = rule.get("sourceIds")
        if (entity is None or not isinstance(trigger, dict) or not {"field", "value"} <= set(trigger)
                or not set(trigger) <= {"field", "value", "comparison"} or not isinstance(trigger.get("comparison", "exact"), str)
                or trigger.get("comparison", "exact") not in {"exact", "trim-casefold"}
                or not isinstance(trigger["field"], str) or trigger["field"] not in entity.get("updateFields", {})
                or not isinstance(trigger["value"], str) or not isinstance(sources, list) or not sources
                or not all(isinstance(s, str) and s.strip() for s in sources)
                or not isinstance(rule.get("boundary"), str) or not rule["boundary"].strip()):
            raise AdapterError("Source effect needs an owned trigger, sourceIds and explicit boundary.")
        kind = rule.get("kind")
        if kind == "clear-field":
            if not isinstance(rule.get("field"), str) or rule["field"] not in entity.get("nullableFields", {}):
                raise AdapterError("A clear-field effect requires an explicitly declared nullable field.")
            if entity["nullableFields"][rule["field"]].get("when") != {trigger["field"]: trigger["value"]}:
                raise AdapterError("A clear-field effect must satisfy its exact declared nullable condition.")
        elif kind == "set-field":
            if not isinstance(rule.get("field"), str) or rule["field"] not in entity.get("updateFields", {}) or not isinstance(rule.get("value"), str):
                raise AdapterError("A set-field effect requires an owned field and an explicit string value.")
            _validate_field_value(entity, rule["field"], rule["value"], rule["id"])
        elif kind == "remove-child-rows":
            if not isinstance(rule.get("childEntity"), str):
                raise AdapterError("Source effect childEntity must be a string.")
            child = entities.get(rule["childEntity"])
            if (child is None or not isinstance(rule.get("parentFields"), list)
                    or not rule["parentFields"] or not isinstance(rule.get("childFields"), list)
                    or len(rule["parentFields"]) != len(rule["childFields"])
                    or not all(isinstance(f, str) for f in rule["parentFields"] + rule["childFields"])
                    or not set(rule["parentFields"]) <= set(entity["keyFields"])
                    or not set(rule["childFields"]) <= set(child["keyFields"])):
                raise AdapterError("A child-removal effect requires exact portable parent/child key bindings.")
            if not any(r["parentEntity"] == entity["name"] and r["childEntity"] == child["name"] and r["parentFields"] == rule["parentFields"] and r["childFields"] == rule["childFields"] for r in _parent_relationships(contract)):
                raise AdapterError("A child-removal effect must use an existing exact parent relationship.")
        else:
            raise AdapterError("Unsupported source-effect kind.")
        for operation in blueprint.get("operations", []):
            supplied = operation["values"].get(trigger["field"])
            matched = supplied == trigger["value"]
            if trigger.get("comparison") == "trim-casefold" and isinstance(supplied, str):
                matched = supplied.strip().casefold() == trigger["value"].strip().casefold()
            if operation.get("entity") != entity["name"] or not matched:
                continue
            effect = {**rule, "operationId": operation["id"], "targetKey": operation["targetKey"]}
            if kind in {"clear-field", "set-field"}:
                expected = rule.get("value", "")
                if rule["field"] in operation["values"] and operation["values"][rule["field"]] != expected:
                    raise AdapterError(f"Operation {operation['id']} explicitly conflicts with source effect {rule['id']}: {rule['field']} must be {expected!r}.")
            else:
                if not set(rule["parentFields"]) <= set(operation["targetKey"]):
                    raise AdapterError("Source effect requires the complete declared parent key.")
                for other in blueprint.get("operations", []):
                    if other.get("entity") == rule["childEntity"] and _effect_matches_row(effect, {**other["targetKey"], **other["values"]}):
                        raise AdapterError(f"Operation {other['id']} conflicts with source effect {rule['id']} removing this selection group.")
            effects.append(effect)
    return effects


def _effect_matches_row(effect: dict[str, Any], row: dict[str, str]) -> bool:
    return all(str(row.get(child, "")) == str(effect["targetKey"][parent])
               for parent, child in zip(effect["parentFields"], effect["childFields"]))


def _effect_clear_fields(contract: dict[str, Any], blueprint: dict[str, Any], operation_id: str) -> set[str]:
    return {effect["field"] for effect in _source_effects(contract, blueprint)
            if effect["operationId"] == operation_id and effect["kind"] in {"clear-field", "set-field"}}


def _preview_source_effects(contract: dict[str, Any], blueprint: dict[str, Any], baseline: PackageData) -> list[dict[str, Any]]:
    entities = _entity_map(contract)
    result = []
    for effect in _source_effects(contract, blueprint):
        item = dict(effect)
        if effect["kind"] == "remove-child-rows":
            child = entities[effect["childEntity"]]
            item["affectedRowKeys"] = [{field: row[field] for field in child["keyFields"]}
                for row in baseline.rows[child["name"]] if _effect_matches_row(effect, row)]
        else:
            entity = entities[effect["entity"]]
            before = _row_index(baseline, entity).get(_target_tuple(entity, effect["targetKey"]))
            item["beforeValue"] = None if before is None else before[effect["field"]]
            item["expectedValue"] = effect.get("value", "")
        result.append(item)
    return result


def _rollback_operations(
    contract: dict[str, Any], forward: dict[str, Any], before: PackageData, current: PackageData
) -> list[dict[str, Any]]:
    """Restore requested fields and changed setter effects, without redundant clears."""
    entities = _entity_map(contract)
    operations = []
    for index, operation in enumerate(forward["operations"], start=1):
        if operation["action"] != "update":
            raise AdapterError("Automatic rollback currently supports update operations only.")
        entity = entities[operation["entity"]]
        key = _target_tuple(entity, operation["targetKey"])
        original = _row_index(before, entity).get(key)
        observed = _row_index(current, entity).get(key)
        if original is None or observed is None:
            raise AdapterError(f"Rollback target {entity['name']} {key!r} is missing.")
        fields = set(operation["values"]) | {
            field for field in _effect_clear_fields(contract, forward, operation["id"])
            if original[field] != observed[field]
        }
        operations.append({
            "id": f"RB-OP-{index:03d}", "action": "update", "entity": entity["name"],
            "targetKey": operation["targetKey"],
            "values": {field: _rollback_field_value(entity, field, original[field]) for field in sorted(fields)},
            "preserveOtherValues": True, "preserveUnspecifiedRows": True,
        })
    return operations


def _rollback_blueprint(
    contract: dict[str, Any], forward: dict[str, Any], before: PackageData, current: PackageData
) -> dict[str, Any]:
    # Forward receipts and overrides are bound to forward operations. Never
    # relabel them as independent evidence or approval for a reverse request.
    return _normalized_blueprint(contract, {
        "operations": _rollback_operations(contract, forward, before, current),
        "resolvedScope": forward.get("resolvedScope", {}),
        "prerequisites": [], "explicitDefaults": [], "preservedValues": [], "warnings": [],
    })


def _rollback_limitations(contract: dict[str, Any], blueprint: dict[str, Any], baseline: PackageData) -> list[dict[str, str]]:
    """Do not advertise automatic recovery where the source clear contract is absent."""
    entities = _entity_map(contract)
    limits = []
    for operation in blueprint["operations"]:
        entity = entities[operation["entity"]]
        base = {"operationId": operation["id"], "entity": entity["name"]}
        if operation["action"] != "update":
            limits.append({**base, "reason": "Automatic rollback supports updates only; creation has no declared removal mechanism."})
            continue
        before = _row_index(baseline, entity).get(_target_tuple(entity, operation["targetKey"]))
        if before is None:
            continue
        for field, value in operation["values"].items():
            if before[field] != str(value) and any(
                receipt.get("operationId") == operation["id"]
                and receipt.get("entity") == entity["name"] and receipt.get("field") == field
                and "restResult" in receipt
                for receipt in blueprint.get("prerequisites", [])
            ):
                limits.append({**base, "field": field,
                               "reason": "Restoring this reference requires fresh evidence bound to the rollback operation and original value; forward REST evidence cannot be reused."})
            domain = entity.get("valueContracts", {}).get(field, {})
            if domain.get("restFallback") and before[field] != str(value):
                listed = {item.get("code") for item in domain.get("allowedValues", [])}
                if before[field] not in listed:
                    limits.append({**base, "field": field,
                                   "reason": "Restoring the original unlisted value requires fresh REST evidence bound to the rollback operation; automatic rollback is unsupported."})
            if before[field] == "" and str(value) != "":
                try:
                    _validate_field_value(entity, field, "", "rollback")
                except AdapterError:
                    limits.append({**base, "field": field, "reason": "The original typed cell is blank and no source-backed clearing contract is declared; automatic rollback is unsupported."})
    for effect in _source_effects(contract, blueprint):
        if effect["kind"] == "set-field":
            limits.append({"operationId": effect["operationId"], "entity": effect["entity"], "effectId": effect["id"],
                           "reason": "This branch forces a related value; automatic reversal requires a separately reviewed recovery design."})
        if effect["kind"] == "remove-child-rows" and any(_effect_matches_row(effect, row) for row in baseline.rows[effect["childEntity"]]):
            limits.append({"operationId": effect["operationId"], "entity": effect["entity"], "effectId": effect["id"],
                           "reason": "This setter removes selected rows; recreating them requires separately reviewed recovery and current reference validation."})
    if not limits:
        # Validate the actual reverse contract against the projected forward
        # state before advertising automatic recovery. This is local feasibility,
        # not an observation of saved Fusion data.
        rows = {name: [dict(row) for row in group] for name, group in baseline.rows.items()}
        for operation in blueprint["operations"]:
            entity = entities[operation["entity"]]
            key = _target_tuple(entity, operation["targetKey"])
            row = next(row for row in rows[entity["name"]] if _row_key(entity, row) == key)
            row.update(operation["values"])
        for effect in _source_effects(contract, blueprint):
            if effect["kind"] in {"clear-field", "set-field"}:
                entity = entities[effect["entity"]]
                key = _target_tuple(entity, effect["targetKey"])
                row = next(row for row in rows[entity["name"]] if _row_key(entity, row) == key)
                row[effect["field"]] = effect.get("value", "")
        projected = replace(baseline, rows=rows)
        try:
            reverse = _rollback_blueprint(contract, blueprint, baseline, projected)
            _validate_blueprint(contract, reverse, projected)
            for effect in _source_effects(contract, reverse):
                if effect["kind"] == "remove-child-rows":
                    conflict = any(_effect_matches_row(effect, row) for row in baseline.rows[effect["childEntity"]])
                else:
                    original = _row_index(baseline, entities[effect["entity"]])[_target_tuple(entities[effect["entity"]], effect["targetKey"])]
                    conflict = original[effect["field"]] != effect.get("value", "")
                if conflict:
                    limits.append({"operationId": effect["operationId"], "entity": effect["entity"], "effectId": effect["id"],
                                   "reason": "The reverse setter would alter original data; use a separately reviewed recovery design."})
        except AdapterError as exc:
            limits.append({"operationId": "rollback", "entity": "recovery",
                           "reason": "The reverse operation does not satisfy the task contract: " + str(exc)})
    return limits


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
        for effect in _source_effects(contract, blueprint):
            if effect["operationId"] == operation["id"]:
                result.append({"id": f"REQ-{number:03d}", "kind": "source_effect", **base,
                               "effect": effect, "requirement": f"Apply declared source effect {effect['id']} within its exact target scope"})
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
                "preserveOtherValues": operation.get("preserveOtherValues", True),
                "preserveUnspecifiedRows": operation.get("preserveUnspecifiedRows", True),
            }
            for operation in blueprint["operations"]
        ],
        "explicitDefaults": blueprint["explicitDefaults"],
        "preservedValues": blueprint["preservedValues"],
        "prerequisites": blueprint["prerequisites"],
        "warnings": blueprint["warnings"],
        "sourceEffects": _preview_source_effects(contract, blueprint, baseline),
        "automaticRollbackSupported": not _rollback_limitations(contract, blueprint, baseline),
        "rollbackLimitations": _rollback_limitations(contract, blueprint, baseline),
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
    entities = _entity_map(contract)
    output: dict[str, list[dict[str, str]]] = {name: [] for name in entities}
    baseline_indexes = {}
    for operation in blueprint["operations"]:
        entity = entities[operation["entity"]]
        key = _target_tuple(entity, operation["targetKey"])
        if operation["action"] == "update":
            row = dict(_row_index(baseline, entity, baseline_indexes)[key])
        elif operation["action"] == "create":
            row = {header: "" for header in entity["headers"]}
            row.update({field: str(value) for field, value in operation["targetKey"].items()})
        else:
            raise AdapterError(f"Unsupported action {operation['action']!r}.")
        row.update({field: str(value) for field, value in operation["values"].items()})
        for effect in _source_effects(contract, blueprint):
            if effect["operationId"] == operation["id"] and effect["kind"] in {"clear-field", "set-field"}:
                row[effect["field"]] = effect.get("value", "")
        for field in entity["auditFields"]:
            row[field] = ""
        output[entity["name"]].append(row)
    for entity_name, rows in output.items():
        entity = entities[entity_name]
        rows.sort(key=lambda row: _row_key(entity, row))
    return output


def _all_updates_already_satisfied(
    contract: dict[str, Any],
    baseline: PackageData,
    blueprint: dict[str, Any],
) -> bool:
    """Suppress a whole request only when every requested value already persists."""
    entities = _entity_map(contract)
    baseline_indexes = {}
    for operation in blueprint["operations"]:
        if operation["action"] != "update":
            return False
        entity = entities[operation["entity"]]
        key = _target_tuple(entity, operation["targetKey"])
        before = _row_index(baseline, entity, baseline_indexes).get(key)
        if before is None or any(
            before[field] != str(value)
            for field, value in operation["values"].items()
        ):
            return False
    for effect in _source_effects(contract, blueprint):
        if effect["kind"] in {"clear-field", "set-field"}:
            entity = entities[effect["entity"]]
            row = _row_index(baseline, entity).get(_target_tuple(entity, effect["targetKey"]))
            if row is not None and row[effect["field"]] != effect.get("value", ""):
                return False
        elif any(_effect_matches_row(effect, row) for row in baseline.rows[effect["childEntity"]]):
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
    _validate_new_outputs([output_path], [])
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
    candidate_indexes = {}
    baseline_indexes = {}
    for operation in blueprint["operations"]:
        entity = entities[operation["entity"]]
        key = _target_tuple(entity, operation["targetKey"])
        expected_targets.add((entity["name"], key))
        candidate_rows = _row_index(candidate, entity, candidate_indexes)
        baseline_rows = _row_index(baseline, entity, baseline_indexes)
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
        if operation["action"] == "create":
            declared = set(operation["targetKey"]) | set(operation["values"]) | set(entity["auditFields"]) | _effect_clear_fields(contract, blueprint, operation["id"])
            for field in entity["headers"]:
                if field not in declared and row[field] != "":
                    issues.append(
                        {"code": "UNEXPECTED_CREATE_VALUE", "message": f"{entity['name']} {key!r} contains an unrequested value in omitted create field {field}."}
                    )
        if operation.get("preserveOtherValues", True) and operation["action"] == "update":
            allowed = set(operation["values"]) | set(entity["auditFields"]) | _effect_clear_fields(contract, blueprint, operation["id"])
            for field in entity["headers"]:
                if field not in allowed and row[field] != before[field]:
                    issues.append(
                        {"code": "UNEXPECTED_CHANGE", "message": f"{entity['name']} {key!r} changed preserved field {field}."}
                    )
        for effect in _source_effects(contract, blueprint):
            if effect["operationId"] == operation["id"] and effect["kind"] in {"clear-field", "set-field"} and row[effect["field"]] != effect.get("value", ""):
                issues.append({"code": "SOURCE_EFFECT_MISMATCH", "message": f"Candidate must apply {effect['id']} to {entity['name']}.{effect['field']}."})
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
    if _all_updates_already_satisfied(contract, baseline, blueprint):
        return {
            "schemaVersion": SCHEMA_VERSION,
            "status": "NO_OP",
            "task": contract["task"],
            "baselineSha256": baseline.archive_sha256,
            "designSha256": _sha256_bytes(_canonical_bytes(blueprint)),
            "reason": "All requested update values already match the current-data baseline; no candidate ZIP was written.",
        }
    rows = _candidate_rows(contract, baseline, blueprint)
    with tempfile.TemporaryDirectory(prefix="fscr-build-") as temporary:
        staged_candidate = Path(temporary).resolve() / "candidate.zip"
        _write_candidate(template, baseline, contract, rows, staged_candidate)
        result = validate_candidate(
            contract,
            template_path,
            baseline_path,
            blueprint_path,
            requirements_path,
            staged_candidate,
        )
        if result["status"] != "PASS":
            raise AdapterError(
                "Generated candidate failed semantic validation: "
                + "; ".join(issue["message"] for issue in result["errors"])
            )
        _publish_outputs({output_path: staged_candidate.read_bytes()})
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
        first = Path(directory).resolve() / "candidate-a.zip"
        second = Path(directory).resolve() / "candidate-b.zip"
        first_result = build_candidate(
            contract, template_path, baseline_path, blueprint_path, requirements_path, first
        )
        second_result = build_candidate(
            contract, template_path, baseline_path, blueprint_path, requirements_path, second
        )
        if first_result["status"] == "NO_OP" or second_result["status"] == "NO_OP":
            identical = first_result == second_result
            return {
                "schemaVersion": SCHEMA_VERSION,
                "status": "NO_OP" if identical else "FAIL",
                "identicalResults": identical,
                "identicalBytes": None,
                "candidateWritten": first.exists() or second.exists(),
                "reason": "Repeated no-op builds have no candidate bytes to hash." if identical else "Repeated builds disagree on whether a candidate is needed.",
            }
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


def _validate_reconciliation_sources(
    baseline: PackageData, candidate: PackageData, exported: PackageData
) -> None:
    """Reject source reuse without claiming metadata authenticates a download."""
    sources = (baseline, candidate)
    if exported.path.resolve() in {source.path.resolve() for source in sources}:
        raise AdapterError("Reconciliation requires an independent export, not a baseline or candidate path.")
    if exported.archive_sha256 in {source.archive_sha256 for source in sources}:
        raise AdapterError("Reconciliation export reuses baseline or candidate bytes.")
    for field in ("ProcessEnv", "ProcessRelease"):
        if any(source.metadata[field] != baseline.metadata[field] for source in (candidate, exported)):
            raise AdapterError(f"Reconciliation source {field} differs from the baseline.")
    process_id = exported.metadata.get("ESSRequestId", "")
    if not re.fullmatch(r"[1-9][0-9]*", process_id):
        raise AdapterError("Reconciliation export requires a positive ESSRequestId.")
    if process_id in {source.metadata.get("ESSRequestId", "") for source in sources}:
        raise AdapterError("Reconciliation export reuses a baseline or candidate ESSRequestId.")


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
    _validate_reconciliation_sources(baseline, candidate, persisted)
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
        elif kind == "source_effect":
            effect = requirement["effect"]
            requested = effect["boundary"]
            if effect["kind"] in {"clear-field", "set-field"}:
                field = effect["field"]
                candidate_value = None if candidate_row is None else candidate_row[field]
                persisted_value = None if persisted_row is None else persisted_row[field]
                passed = candidate_value == effect.get("value", "") and persisted_value == effect.get("value", "")
            else:
                child_name = effect["childEntity"]
                child_entity = entities[child_name]
                candidate_value = [dict(zip(child_entity["keyFields"], key)) for key, row in indexes[child_name]["candidate"].items() if _effect_matches_row(effect, row)]
                persisted_value = [dict(zip(child_entity["keyFields"], key)) for key, row in indexes[child_name]["persisted"].items() if _effect_matches_row(effect, row)]
                passed = not candidate_value and not persisted_value
            detail = f"Checked explicit source effect {effect['id']}; sourceIds={effect['sourceIds']}."
        elif kind == "preserve_target":
            operation = operation_map[requirement["operationId"]]
            allowed = set(operation["values"]) | set(entity["auditFields"]) | _effect_clear_fields(contract, blueprint, operation["id"])
            aliases = {field: rule for field, rule in _derived_date_aliases(entity).items()
                       if rule["sourceField"] in operation["values"]}
            differences = []
            if before is None or candidate_row is None or persisted_row is None:
                differences.append("target row unavailable")
            else:
                for field in entity["headers"]:
                    if field in aliases and field not in operation["values"]:
                        expected = _derived_date_value(aliases[field], persisted_row)
                        actual = persisted_row[field]
                        candidate_display = candidate_row[field]
                        candidate_expected = _derived_date_value(aliases[field], candidate_row)
                        candidate_valid = candidate_display == before[field] or candidate_display == candidate_expected or (
                            candidate_expected and _requested_value_equivalence(entity, field, candidate_expected, candidate_expected, candidate_display))
                        persisted_valid = actual == expected or (
                            expected and _requested_value_equivalence(entity, field, expected, expected, actual))
                        if not candidate_valid or not persisted_valid:
                            differences.append(field)
                        semantic_equivalences.append({
                            "ruleId": "FSCR.DERIVED.DATE_ALIAS", "field": field,
                            "sourceField": aliases[field]["sourceField"],
                            "sourceIds": aliases[field]["sourceIds"],
                            "expected": expected, "persisted": actual,
                            "candidate": candidate_display, "passed": bool(candidate_valid and persisted_valid),
                        })
                    elif field not in allowed and (
                        candidate_row[field] != before[field]
                        or persisted_row[field] != before[field]
                    ):
                        differences.append(field)
            requested = "unchanged"
            candidate_value = "unchanged" if not differences else differences
            persisted_value = "unchanged" if not differences else differences
            passed = not differences
            detail = "Checked preservation and explicitly declared derived date relationships." if aliases else "Preserved all non-requested, non-audit target fields."
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
                    if any(effect["kind"] == "remove-child-rows" and effect["childEntity"] == entity_name and _effect_matches_row(effect, left)
                           for effect in _source_effects(contract, blueprint)):
                        continue  # Separately asserted by the exact source-effect requirement.
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
    comparison_passed = all(row["passed"] for row in matrix)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "COMPARISON_ONLY" if comparison_passed else "FAIL",
        "comparisonStatus": "PASS" if comparison_passed else "FAIL",
        "persistenceVerified": False,
        "exportProvenance": {
            "status": "UNVERIFIED",
            "processId": persisted.metadata["ESSRequestId"],
            "reason": "Offline metadata and value comparison do not authenticate export acquisition or prove freshness.",
            "workflowRequiredChecks": [
                "Verify the independent successful exact-task FileContent download through the active Run Book and shared task exporter.",
                "Bind its task, environment, base URL, process identity and downloaded archive digest to the approved load.",
                "Verify export acquisition timestamps are after the approved load submission; a caller-written manifest is not authenticated proof.",
            ],
        },
        "task": contract["task"],
        "baselineSha256": baseline.archive_sha256,
        "candidateSha256": candidate.archive_sha256,
        "exportSha256": persisted.archive_sha256,
        "requirementMatrix": matrix,
        "mismatchCount": sum(not row["passed"] for row in matrix),
    }


def _rollback_field_value(entity: dict[str, Any], field: str, raw: str) -> str:
    """Convert a declared exported date to the rollback blueprint's ISO form.

    This is an internal FSM export boundary, not customer-input or locale
    inference. Keep other field types and the original export evidence intact.
    """
    if raw == "":
        # Respect a bound task's source-backed field validator. The base
        # validator still rejects undeclared typed clears; reverse validation
        # separately checks their effective-field conditions.
        _validate_field_value(entity, field, raw, "rollback")
        return ""
    lowered = (entity.get("types", {}).get(field, "string") or "string").lower()
    if "time" in lowered or not (lowered == "date" or "date" in lowered):
        return raw
    for pattern, shape in (("%Y-%m-%d", r"\d{4}-\d{2}-\d{2}"),
                           ("%Y/%m/%d", r"\d{4}/\d{2}/\d{2}")):
        if not isinstance(raw, str) or re.fullmatch(shape, raw) is None:
            continue
        try:
            parsed = datetime.strptime(raw, pattern).date()
        except ValueError:
            break
        return parsed.isoformat()
    raise AdapterError(
        f"Rollback source field {entity['name']}.{field} has an invalid or "
        "unsupported exported date; require YYYY-MM-DD or YYYY/MM/DD. "
        "Do not infer a locale or ambiguous month/day order."
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
) -> dict[str, Any]:
    _validate_new_outputs(
        [rollback_blueprint_path, rollback_requirements_path, output_path],
        [template_path, before_path, current_path, forward_blueprint_path],
    )
    template = _read_package(template_path, contract)
    before = _read_package(before_path, contract)
    current = _read_package(current_path, contract)
    _validate_source_pair(contract, template, current)
    if before.metadata["ProcessEnv"] != current.metadata["ProcessEnv"]:
        raise AdapterError("Before and current rollback exports come from different environments.")
    if before.metadata["ProcessRelease"] != current.metadata["ProcessRelease"]:
        raise AdapterError("Before and current rollback exports come from different releases.")
    forward = _read_json(forward_blueprint_path)
    _validate_blueprint(contract, forward, before)
    limitations = _rollback_limitations(contract, forward, before)
    if limitations:
        raise AdapterError("Automatic rollback unsupported: " + "; ".join(item.get("field", item.get("effectId", item["entity"])) + ": " + item["reason"] for item in limitations))
    rollback = _rollback_blueprint(contract, forward, before, current)
    _validate_blueprint(contract, rollback, current)
    requirements = _requirements(contract, rollback)
    with tempfile.TemporaryDirectory(prefix="fscr-rollback-") as temporary:
        staging = Path(temporary).resolve()
        staged_blueprint = staging / "blueprint.json"
        staged_requirements = staging / "requirements.json"
        staged_candidate = staging / "candidate.zip"
        _publish_outputs({staged_blueprint: _json_bytes(rollback), staged_requirements: _json_bytes(requirements)})
        report = build_candidate(
            contract,
            template_path,
            current_path,
            staged_blueprint,
            staged_requirements,
            staged_candidate,
        )
        outputs = {rollback_blueprint_path: _json_bytes(rollback), rollback_requirements_path: _json_bytes(requirements)}
        if report["status"] != "NO_OP":
            outputs[output_path] = staged_candidate.read_bytes()
        _publish_outputs(outputs)
    report["rollbackOfDesignSha256"] = _sha256_bytes(_canonical_bytes(forward))
    report["rollbackScope"] = "Restore only fields changed by the forward blueprint."
    return report


def _validated_manifest_origin(value: str) -> str:
    """Validate an explicit origin without resolving hosts or inferring trust."""
    message = "Manifest base URL must be a credential-free HTTPS origin with a valid host and port, without a path, query or fragment."
    if (not isinstance(value, str) or not value
            or any(character.isspace() or ord(character) < 32 or ord(character) == 127 for character in value)
            or any(character in value for character in "\\?#")):
        raise AdapterError(message)
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        if (parsed.scheme != "https" or not host or parsed.path
                or parsed.username is not None or parsed.password is not None or "%" in host):
            raise ValueError("Invalid origin components")
        if parsed.netloc.startswith("["):
            suffix = parsed.netloc[parsed.netloc.index("]") + 1:]
            if suffix and not re.fullmatch(r":[0-9]+", suffix):
                raise ValueError("Invalid IPv6 authority")
            ipaddress.IPv6Address(host)
        else:
            if ":" in parsed.netloc and not re.fullmatch(r"[0-9]+", parsed.netloc.rsplit(":", 1)[1]):
                raise ValueError("Invalid port")
            try:
                ipaddress.IPv4Address(host)
            except ValueError:
                ascii_host = host.encode("idna").decode("ascii")
                label = r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
                if (len(ascii_host.rstrip(".")) > 253 or re.fullmatch(r"[0-9.]+", ascii_host)
                        or not re.fullmatch(label + r"(?:\." + label + r")*\.?", ascii_host)):
                    raise ValueError("Invalid DNS host")
        port = parsed.port
        if port is not None and not 1 <= port <= 65535:
            raise ValueError("Invalid port")
    except (ValueError, UnicodeError) as exc:
        raise AdapterError(message) from exc
    return value


def normalized_manifest(
    contract: dict[str, Any],
    package_path: Path,
    environment: str,
    base_url: str,
    template_only: bool,
) -> dict[str, Any]:
    package = _read_package(package_path, contract)
    if (not isinstance(environment, str) or not environment.strip()
            or environment != package.metadata["ProcessEnv"]):
        raise AdapterError("Manifest environment must be the explicitly selected Fusion environment and exactly match package ProcessEnv; do not substitute or derive an authentication-profile label.")
    origin = _validated_manifest_origin(base_url)
    if type(template_only) is not bool:
        raise AdapterError("Manifest template_only must be a Boolean.")
    populated = [
        entity["member"]
        for entity in contract["package"]["entities"]
        if package.rows[entity["name"]]
    ]
    if template_only and populated:
        raise AdapterError("A template-only manifest cannot describe a package containing data rows.")
    return {
        "environment": environment,
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
    bound_contract = globals().get("_BOUND_CONTRACT_PATH")
    parser.add_argument("--contract", type=Path, required=bound_contract is None,
                        default=bound_contract)
    parser.add_argument("--report", type=Path)
    if bound_contract is not None:
        parser.add_argument("--workspace", type=Path, default=Path.cwd(),
                            help="Allowed output directory (defaults to the current directory).")


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
    if command in {"build", "determinism", "rollback"} and result.get("status") == "NO_OP":
        return True
    if command == "manifest":
        return str(result.get("status", "")).upper() in SUCCESS_STATUSES
    if command == "reconcile":
        return result.get("status") == "COMPARISON_ONLY" and result.get("comparisonStatus") == "PASS"
    return result.get("status", "PASS") == "PASS"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    outputs_preflighted = False
    staging_context: tempfile.TemporaryDirectory[str] | None = None
    requested_outputs: dict[str, Path] = {}
    try:
        _preflight_command_outputs(args)
        outputs_preflighted = True
        contract = _load_contract(args.contract)
        # Public commands publish their complete validated output set together,
        # including an optional report. A failure leaves only its diagnostic.
        requested_outputs = {
            name: value for name, value in vars(args).items()
            if isinstance(value, Path) and name != "report"
            and (name == "output" or name.endswith("_output"))
        }
        staging_context = tempfile.TemporaryDirectory(prefix="fscr-command-")
        staging_directory = Path(staging_context.name).resolve()
        for index, (name, value) in enumerate(requested_outputs.items()):
            setattr(args, name, staging_directory / f"{index}-{value.name}")
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
        if result.get("status") == "FAIL":
            result["failure_class"] = "input_validation"
            result["stage"] = args.command
            result["recommended_action"] = "Correct the reported candidate or comparison differences before requesting import approval or claiming persistence."
            for issue in result.get("errors", []):
                issue.update(failure_class=result["failure_class"], stage=args.command,
                             recommended_action=result["recommended_action"])
        contents = {}
        if _command_succeeded(args.command, result):
            contents.update({destination: getattr(args, name).read_bytes()
                             for name, destination in requested_outputs.items()
                             if getattr(args, name).exists()})
        if args.report:
            contents[args.report] = _json_bytes(result)
        if contents:
            _publish_outputs(contents)
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if _command_succeeded(args.command, result) else 2
    except (AdapterError, OSError) as exc:
        if isinstance(exc, AdapterError):
            message = str(exc)
            failure_class = exc.failure_class
            recommended_action = exc.recommended_action
        elif isinstance(exc, FileExistsError):
            message = "An output was created or changed after preflight; existing files were not overwritten."
            failure_class = "approval_blocker"
            recommended_action = "Select new output paths and rerun local validation."
        else:
            message = "Local artifact access or persistence failed."
            failure_class = "artifact_persistence"
            recommended_action = "Check the intended project paths and filesystem permissions, preserve existing evidence, and rerun the local command."
        diagnostic = {
            "failure_class": failure_class,
            "stage": args.command,
            "recommended_action": recommended_action,
        }
        failure = {
            "schemaVersion": SCHEMA_VERSION,
            "status": "FAIL",
            **diagnostic,
            "errors": [{"code": "ADAPTER_ERROR", "message": message, **diagnostic}],
        }
        if outputs_preflighted and getattr(args, "report", None):
            try:
                _write_json(args.report, failure)
            except (AdapterError, OSError):
                failure["errors"].append({
                    "code": "REPORT_PERSISTENCE_FAILED",
                    "message": "The failure report could not be saved without changing existing files; retain this diagnostic output.",
                    "failure_class": "artifact_persistence",
                    "stage": "write_failure_report",
                    "recommended_action": "Choose a new accessible report path under the intended project workspace.",
                })
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        return 2
    finally:
        if staging_context is not None:
            staging_context.cleanup()


def bind_runtime(namespace: dict[str, Any], *, contract_path: Path) -> None:
    """Bind independent Payables functions for a task's domain-specific extensions.

    Calls resolve through the caller's namespace, allowing task-owned validators
    to extend the primitive without mutating the shared module or other callers.
    """
    exports = {name: value for name, value in globals().items()
               if not name.startswith("__") and name not in {"bind_runtime", "annotations"}}
    collisions = set(exports).intersection(namespace)
    if collisions:
        raise ValueError("Runtime bindings would replace existing names: " + ", ".join(sorted(collisions)))
    for name, value in exports.items():
        if isinstance(value, FunctionType) and value.__module__ == __name__:
            bound = FunctionType(value.__code__, namespace, value.__name__, value.__defaults__, value.__closure__)
            bound.__kwdefaults__ = deepcopy(value.__kwdefaults__)
            bound.__annotations__ = dict(value.__annotations__)
            namespace[name] = bound
        else:
            namespace[name] = deepcopy(value) if isinstance(value, (dict, list, set)) else value
    namespace["_BOUND_CONTRACT_PATH"] = Path(contract_path).resolve()


if __name__ == "__main__":
    raise SystemExit(main())
