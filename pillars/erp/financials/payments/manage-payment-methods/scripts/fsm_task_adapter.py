#!/usr/bin/env python3
"""Portable, data-driven FSM task adapter runtime.

This file is copied into a generated Nested task skill.  Task semantics live in
the adjacent e2e-adapter.json descriptor and ora-resource rule plan.  The
runtime performs offline package work only; it never connects to Fusion.
"""

from __future__ import annotations

import argparse
import csv
from copy import deepcopy
import hashlib
import io
import json
import re
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field, replace
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
    if not isinstance(package, dict) or not package.get("entities"):
        raise AdapterError("Adapter contract lacks package entities.")
    if contract.get("semanticModel", {}).get("mode") != "task-specific-extension":
        raise AdapterError("Payment Methods requires its registered task-specific semantic extension.")
    if task.get("code") != "IBY_MANAGE_PAYMENT_METHODS":
        raise AdapterError("Payment Methods extension cannot execute another task.")
    # Private executable rules are deliberately outside the generic descriptor.
    # The registered task-specific validator enforces them for every operation.
    extension_rules = {'IBY_FD_PAYMENT_METHOD': {'ignoredValueTypes': {'field': 'ApplicableValueTo', 'otherAllowedValues': ['PAYER_LE', 'PAYER_ORG', 'PAYEE', 'PAY_PROC_TRXN_TYPE'], 'whenField': 'ApplicableTypeCode', 'whenValues': ['CROSS_BORDER_FLAG', 'FOREIGN_CURRENCY_FLAG']}}, 'ORA_PAYMENT_METHOD_VALIDATION_VALUE': {'parentKeyResolver': {'fieldMap': {'ORA_IBY_FD_PARENT_PAY_MET.PaymentMethodCode': 'ORA_IBY_FD_PARENT_PAY_MET.PaymentMethodCode', 'ORA_PMT_METHOD_VALIDATION_ASSIGNMENT.AssignmentEntityId': 'AssignmentEntityId', 'ORA_PMT_METHOD_VALIDATION_ASSIGNMENT.ValAssignmentEntityType': 'ValAssignmentEntityType', 'ORA_PMT_METHOD_VALIDATION_ASSIGNMENT.ValidationSetCode': 'ValidationSetCode'}, 'matchPolicy': 'exactly-one', 'parentEntity': 'ORA_PMT_METHOD_VALIDATION_ASSIGNMENT', 'sourceEvidence': ['Same-task metadata XmlNodePath and exact ancestor-qualified CSV headers.', 'ValidationValueEO.xml 151-180 and ValidationAssignmentEO.xml 268-285; recover the complete portable parent key only after exactly one package match.']}}}
    for entity in package["entities"]:
        entity.update(extension_rules.get(entity["name"], {}))
    return contract


def _derived_date_aliases(entity: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Accept only explicit same-entity date aliases, never name heuristics."""
    # Source-backed task-specific extension, declared in semanticModel.extension.
    # Customer-v2 rejects the generic Builder entity property; do not alter its schema.
    aliases = ({"EndDateDisp": {"sourceField": "EndDate", "blankWhenSourceEquals": "4712-12-31",
                "sourceIds": ["SRC-REVIEW-ASSIGN-DATE-SETTER"]}}
               if entity.get("name") == "ORA_PMT_METHOD_VALIDATION_ASSIGNMENT" else {})
    if not isinstance(aliases, dict):
        raise AdapterError("derivedDateAliases must be an object.")
    protected = set(entity.get("keyFields", [])) | set(entity.get("auditFields", []))
    for field, rule in aliases.items():
        if not isinstance(rule, dict):
            raise AdapterError("Derived date alias requires a source-backed rule.")
        source = rule.get("sourceField")
        evidence = rule.get("sourceIds")
        sentinel = rule.get("blankWhenSourceEquals")
        if (field == source or field not in entity["headers"] or source not in entity["headers"]
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
    entity_contracts: dict[str, dict[str, Any]] = field(default_factory=dict)


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



# Only the two exact observed task shapes are accepted. This is a task-local
# semantic extension, not a generic schema relaxation or field support removal.
CURRENT_87_FINGERPRINT = "c6f3413be5d3f5288369c8820bb9d731286abe436a0588ca891dd7e71538a22b"
VARIANT_ABSENT_FIELDS = {"DueDayOfMonth", "DueMonthsForward"}


def _variant_contract(contract, parent_headers):
    parent = _entity_map(contract)["ORA_IBY_FD_PARENT_PAY_MET"]
    full = parent["headers"]
    reduced = [field for field in full if field not in VARIANT_ABSENT_FIELDS]
    if parent_headers == full:
        return contract
    if parent_headers != reduced or len(full) != 89 or len(reduced) != 87:
        raise AdapterError("Unknown Payment Methods parent package variant; exact observed 89/87-column contract required.")
    selected = deepcopy(contract)
    entity = _entity_map(selected)[parent["name"]]
    entity["headers"] = reduced
    # Remove fields only from this selected package view, never the canonical
    # descriptor. Legacy packages retain their complete operation allowlists.
    for name, values in entity.items():
        if isinstance(values, dict):
            for field in VARIANT_ABSENT_FIELDS:
                values.pop(field, None)
        elif isinstance(values, list) and name != "headers":
            values[:] = [item for item in values if item not in VARIANT_ABSENT_FIELDS] if all(isinstance(item,str) for item in values) else values
    for item in selected["package"]["entities"]:
        item["_calendarCSVDateFormat"] = "yyyy/MM/dd"
    selected["package"]["schemaFingerprint"] = CURRENT_87_FINGERPRINT
    return selected


def _contract_for_package(contract, package):
    return _variant_contract(contract, package.headers["ORA_IBY_FD_PARENT_PAY_MET"])


def _require_same_variant(contract, *packages):
    fingerprints = {_schema_fingerprint(contract, package) for package in packages}
    if len(fingerprints) != 1:
        raise AdapterError("Mixed package variants are not allowed; obtain matching template/current/export sources.")

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

    parent = _entity_map(contract)["ORA_IBY_FD_PARENT_PAY_MET"]
    parent_headers, _ = _decode_csv(member_bytes[parent["member"]], parent["member"])
    contract = _variant_contract(contract, parent_headers)

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
    if not SUCCESS_STATUS.search(metadata["ProcessStatus"]):
        raise AdapterError(
            f"Package process status is not successful: {metadata['ProcessStatus']!r}."
        )
    if not metadata["ProcessEnv"] or not metadata["ProcessRelease"]:
        raise AdapterError("Package metadata must declare ProcessEnv and ProcessRelease.")
    object_contracts = _metadata_object_contracts(root)
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
            # XmlCSVAMImpl scopes its TreeMap by XML file and hierarchy level.
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
    result = PackageData(
        path=path,
        archive_sha256=_sha256_bytes(archive_bytes),
        member_names=names,
        member_bytes=member_bytes,
        member_infos=member_infos,
        headers=headers,
        rows=rows,
        metadata=metadata,
        object_contracts=object_contracts,
        entity_contracts=_entity_map(contract),
    )
    if len(parent_headers) == 87 and _schema_fingerprint(contract, result) != CURRENT_87_FINGERPRINT:
        raise AdapterError("Observed 87-column package metadata/type fingerprint differs from its exact qualified contract.")
    return result


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
    _require_same_variant(contract, template, baseline)
    # evidenceRelease records authoring provenance. Runtime compatibility is
    # established by the exact task identity, matching live source releases,
    # and the stable member/path/header/type fingerprint below. A compatible
    # environment release must not require regenerating an otherwise identical
    # task adapter.


def _row_key(
    entity: dict[str, Any], row: dict[str, str],
    package: PackageData | None = None, parent_context: PackageData | None = None,
) -> tuple[str, ...]:
    return _resolved_key(entity, row, package, parent_context)


def _target_tuple(
    entity: dict[str, Any], target: dict[str, Any],
    package: PackageData | None = None, parent_context: PackageData | None = None,
) -> tuple[str, ...]:
    return _resolved_key(entity, target, package, parent_context)


def _resolved_key(
    entity: dict[str, Any], values: dict[str, Any],
    package: PackageData | None, parent_context: PackageData | None = None,
) -> tuple[str, ...]:
    """Resolve identity from package evidence, never from database identifiers."""
    raw = _canonical_key(entity, values)
    resolver = entity.get("parentKeyResolver")
    if not resolver:
        return raw
    if package is None:
        raise AdapterError(f"Entity {entity['name']} requires package parent context for identity.")
    parent_name = resolver["parentEntity"]
    parent = package.entity_contracts.get(parent_name)
    if not parent or parent.get("parentKeyResolver"):
        raise AdapterError(f"Entity {entity['name']} has an invalid parent identity contract.")
    # Candidates are deltas. Their explicit parent rows overlay the baseline;
    # full baseline/persisted exports never receive a fallback context.
    parents = {}
    if parent_context is not None:
        parents.update(_row_index(parent_context, parent))
    parents.update(_row_index(package, parent))
    mapping = resolver["fieldMap"]
    reference = {child: str(values.get(child, "")) for child in mapping}
    if any(value == "" for value in reference.values()):
        raise AdapterError(f"Entity {entity['name']} has a blank parent reference: {reference!r}.")
    matches = [
        key for key, row in parents.items()
        if all(str(row.get(parent_field, "")) == reference[child]
               for child, parent_field in mapping.items())
    ]
    if len(matches) != 1:
        raise AdapterError(
            f"Entity {entity['name']} parent reference {reference!r} matched "
            f"{len(matches)} rows in {parent_name}; exactly one is required."
        )
    own = _canonical_key(entity, values)
    return matches[0] + own


def _canonical_key(entity: dict[str, Any], values: dict[str, Any]) -> tuple[str, ...]:
    ignored = entity.get("ignoredValueTypes", {})
    if ignored:
        kind = str(values.get(ignored["whenField"], ""))
        if kind not in ignored["whenValues"] + ignored["otherAllowedValues"]:
            raise AdapterError(
                f"Entity {entity['name']} field {ignored['whenField']} has no source-backed identity rule for {kind!r}."
            )
    return tuple(
        "" if field == ignored.get("field")
        and str(values.get(ignored.get("whenField", ""), "")) in ignored.get("whenValues", [])
        else str(values.get(field, ""))
        for field in entity["keyFields"]
    )


def _validate_field_value(
    entity: dict[str, Any], field: str, value: Any, operation_id: str
) -> None:
    # Source EO152-169 and setter568-569: optional nonnegative Long.
    # Only the exact empty CSV value represents this attribute's null.
    if entity["name"] == "ORA_IBY_FD_PARENT_PAY_MET" and field == "AnticipatedFloat":
        if value == "":
            return
        if (isinstance(value, bool) or not isinstance(value, (int, str))
                or re.fullmatch(r"[+-]?\d+", str(value).strip()) is None
                or not 0 <= int(value) <= 9223372036854775807):
            raise AdapterError("AnticipatedFloat expects a source-compatible long value: blank or an integer from 0 to 9223372036854775807.")
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
    package: PackageData, entity: dict[str, Any],
    parent_context: PackageData | None = None,
) -> dict[tuple[str, ...], dict[str, str]]:
    if not entity["keyFields"]:
        raise AdapterError(f"Entity {entity['name']} has no source-backed key.")
    result: dict[tuple[str, ...], dict[str, str]] = {}
    for number, row in enumerate(package.rows[entity["name"]], start=2):
        raw_key = _canonical_key(entity, row)
        nullable = set(entity.get("nullableKeyFields", []))
        if any(value == "" and field not in nullable for field, value in zip(entity["keyFields"], raw_key)):
            raise AdapterError(
                f"{entity['member']} row {number} has a blank key component."
            )
        key = _row_key(entity, row, package, parent_context)
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
            operation["values"] = values
        if entity is not None:
            values = dict(operation.get("values") or {})
            for alias, rule in _derived_date_aliases(entity).items():
                source = rule["sourceField"]
                if alias in values:
                    raw = values[alias]
                    if not isinstance(raw, str):
                        raise AdapterError("Display date must be a strict date string or empty string.")
                    implied = raw or rule["blankWhenSourceEquals"]
                    if source in values and values[source] != implied:
                        raise AdapterError("Contradictory source and derived dates.")
                    values[source] = implied
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



def _validate_task_import_effects(operations, baseline):
    """SRC-DEBUG-IMPORT: reject source-proven deletion of preserved usage rows.

    This task supports create/update with row preservation, not an implicit
    deletion campaign. Requires the same fresh package used by build/validate.
    No flags, IDs or missing defaults are synthesized.
    """
    if baseline is None:
        return  # normalization is not fresh-baseline qualification
    parents = baseline.rows["ORA_IBY_FD_PARENT_PAY_MET"]
    usages = baseline.rows["IBY_FD_PAYMENT_METHOD"]
    for operation in operations:
        entity = operation["entity"]
        target = operation["targetKey"]
        values = operation["values"]
        method = str(target.get("PaymentMethodCode", ""))
        if entity == "ORA_IBY_FD_PARENT_PAY_MET":
            current = next((row for row in parents if row.get("PaymentMethodCode") == method), {})
            if current.get("SeededFlag") == "Y":
                raise AdapterError("Seeded payment-method parent is suppressed by FSM import; this create/update request cannot be qualified.")
            flags = {name: values.get(name, current.get(name)) for name in ("PmtEnableAp", "PmtEnableAr", "PmtEnableCe")}
            if all(value == "N" for value in flags.values()):
                raise AdapterError("At least one payment application must be enabled (AP, AR or CE).")
            for field, app in (("PmtEnableAp", "AP"), ("PmtEnableAr", "AR"), ("PmtEnableCe", "CE")):
                # Candidate parent rows serialize retained flags too. An existing
                # N can trigger the hook even when the user changes another field.
                if flags[field] == "N" and any(row.get("PaymentMethodCode") == method and
                        (row.get("ApplicationShortName") == app or row.get("ApplicationShortName") not in {"AP", "AR", "CE"}) for row in usages):
                    raise AdapterError(f"FSM_IMPORT_SIDE_EFFECT: {field}=N can remove existing usage rows for {method}/{app}; preserved-row create/update cannot proceed.")
        if entity == "ORA_IBY_FD_PARENT_PAY_MET":
            for field, app in (("PmtEnableAp", "AP"), ("PmtEnableAr", "AR"), ("PmtEnableCe", "CE")):
                if values.get(field) == "Y" and (operation["action"] == "create" or current.get(field) != "Y"):
                    has_usage = any(row.get("PaymentMethodCode") == method and row.get("ApplicationShortName") == app for row in usages)
                    has_usage = has_usage or any(op["entity"] == "IBY_FD_PAYMENT_METHOD" and op["action"] == "create" and op["targetKey"].get("PaymentMethodCode") == method and op["targetKey"].get("ApplicationShortName") == app for op in operations)
                    if not has_usage:
                        raise AdapterError(f"FSM_USAGE_REQUIRED: {field}=Y needs explicit {app} Usage rows; parent-only enablement does not persist. Include the requested Usage operations.")
        if entity == "IBY_FD_PAYMENT_METHOD" and operation["action"] == "update":
            current_usage = next((row for row in usages if all(str(row.get(k, "")) == str(value) for k, value in target.items())), None)
            changed = {field for field, value in values.items() if current_usage is not None and str(value) != current_usage.get(field, "")}
            if changed & {"BuName", "LEName"}:
                raise AdapterError("FSM_SCOPE_REPLACEMENT: changing BU/LE can select a new Usage identity; prepare an explicit scope-change plan preserving existing rows.")
            if changed and target.get("ApplicableTypeCode") not in {"CROSS_BORDER_FLAG", "FOREIGN_CURRENCY_FLAG"}:
                raise AdapterError("FSM_IGNORED_USAGE_UPDATE: import discards matched incoming Usage of this type; a successful process cannot qualify this scalar update.")
        if entity == "IBY_FD_PAYMENT_METHOD" and target.get("ApplicableTypeCode") == "PAYER_ORG" and str(target.get("ApplicableValueTo", "")) == "":
            app = str(target.get("ApplicationShortName", ""))
            if any(row.get("PaymentMethodCode") == method and row.get("ApplicationShortName") == app and
                    row.get("ApplicableTypeCode") == "PAYER_ORG" and str(row.get("ApplicableValueTo", "")) != "" for row in usages):
                raise AdapterError("FSM_IMPORT_SIDE_EFFECT: all-BU scope can consolidate/remove existing specific-BU usage rows; preserved-row create/update cannot proceed.")

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
    if baseline is not None:
        for entity in entities.values():
            if entity.get("parentKeyResolver"):
                _row_index(baseline, entity)
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
        reference_fields = set(entity.get("parentKeyResolver", {}).get("fieldMap", {}))
        target_fields = set(entity["keyFields"]) | reference_fields
        if not isinstance(target, dict) or set(target) != target_fields:
            raise AdapterError(
                f"Operation {operation_id} targetKey must contain exactly "
                f"{sorted(target_fields)}."
            )
        for field in sorted(target_fields):
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
        raw_target = _canonical_key(entity, target)
        nullable = set(entity.get("nullableKeyFields", []))
        if any(value == "" and field not in nullable for field, value in zip(entity["keyFields"], raw_target)):
            raise AdapterError(f"Operation {operation_id} has a blank target key.")
        target_tuple = (
            _target_tuple(entity, target, baseline)
            if baseline is not None or not reference_fields
            else raw_target + tuple(str(target[field]) for field in sorted(reference_fields))
        )
        target_identity = (entity_name, target_tuple)
        if target_identity in seen_targets:
            raise AdapterError(
                f"More than one operation targets {entity_name} {target_tuple!r}."
            )
        seen_targets.add(target_identity)
        values = operation.get("values")
        if not isinstance(values, dict) or (not values and action != "create"):
            raise AdapterError(f"Operation {operation_id} must supply values.")
        for alias, rule in _derived_date_aliases(entity).items():
            source = rule["sourceField"]
            if alias in values:
                if source not in values:
                    raise AdapterError("Display date must be normalized to canonical source date before build.")
                if values[alias] != _derived_date_value(rule, values):
                    raise AdapterError("Contradictory source and derived dates.")
        if entity_name == "ORA_IBY_FD_PARENT_PAY_MET" and "SeededFlag" in values:
            raise AdapterError("SeededFlag is product-owned seed metadata and cannot be requested.")
        if entity_name == "ORA_PAYMENT_METHOD_VALIDATION_VALUE" and "LevelCode" in values:
            raise AdapterError(f"Operation {operation_id} has no source-backed {action} contract for LevelCode: derived display field; change the typed parameter value instead.")
        prohibited = set(entity["keyFields"]) | reference_fields | set(entity["auditFields"])
        unknown = set(values) - set(entity["headers"])
        if unknown & VARIANT_ABSENT_FIELDS:
            raise AdapterError(f"Operation {operation_id} requests fields absent from the selected export variant: {sorted(unknown & VARIANT_ABSENT_FIELDS)}. Obtain a compatible export; these fields remain supported by the historical 89-column contract.")
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
            # Ancestor references select an existing parent; they are neither
            # child business inputs nor writable values. Exact-one resolution
            # above validates them before the child create-field allowlist.
            unproven = ((set(target) - reference_fields) | set(values)) - create_fields
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
            if entity_name == "ORA_IBY_FD_PARENT_PAY_MET" and field == "PaymentModeCode" and values[field] == "":
                continue  # source-backed optional mode: no code to resolve
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


    _validate_task_import_effects(operations, baseline)


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


def _package_dependencies(contract):
    """Only explicitly reviewed relationships opt into package closure."""
    entities = _entity_map(contract)
    result = []
    for rule in contract.get("semanticModel", {}).get("relationships", []):
        if not rule.get("includeInPackage", False):
            continue
        parent = entities.get(rule.get("parentEntity"))
        child = entities.get(rule.get("childEntity"))
        pf, cf = rule.get("parentFields", []), rule.get("childFields", [])
        if (rule.get("status") != "confirmed" or not rule.get("evidence")
                or parent is None or child is None or parent is child
                or not pf or len(pf) != len(cf)
                or len(set(pf)) != len(pf) or len(set(cf)) != len(cf)
                or not set(pf) <= set(parent["headers"])
                or not set(cf) <= set(child["headers"])):
            raise AdapterError("Invalid confirmed package dependency relationship.")
        result.append(rule)
    edges = {}
    for rule in result:
        edges.setdefault(rule["childEntity"], []).append(rule["parentEntity"])
    def visit(name, trail):
        if name in trail:
            raise AdapterError("Cyclic package dependency relationship.")
        for parent in edges.get(name, []):
            visit(parent, trail | {name})
    for name in edges:
        visit(name, set())
    return result


def _add_package_dependencies(contract, baseline, output):
    """Carry exact baseline ancestors, preserving business fields and blanking audit."""
    entities = _entity_map(contract)
    rules = _package_dependencies(contract)
    changed = True
    while changed:
        changed = False
        for rule in rules:
            parent = entities[rule["parentEntity"]]
            parent_rows = output[parent["name"]]
            fields = parent["keyFields"]
            # Requested parent rows overlay their baseline identities.
            key = lambda row: tuple(row.get(field, "") for field in fields)
            available = {key(row): row for row in baseline.rows[parent["name"]]}
            if len(available) != len(baseline.rows[parent["name"]]):
                raise AdapterError("Package dependency parent identity is ambiguous.")
            available.update({key(row): row for row in parent_rows})
            for child in list(output[rule["childEntity"]]):
                matches = [row for row in available.values() if all(
                    row.get(p, "") == child.get(c, "")
                    for p, c in zip(rule["parentFields"], rule["childFields"]))]
                if len(matches) != 1:
                    raise AdapterError("Package dependency must resolve exactly one parent: "
                                       + rule["childEntity"] + " -> " + parent["name"])
                selected = matches[0]
                if not any(key(row) == key(selected) for row in parent_rows):
                    copy = dict(selected)
                    for field in parent["auditFields"]:
                        copy[field] = ""
                    parent_rows.append(copy)
                    changed = True


def _candidate_rows(
    contract: dict[str, Any],
    baseline: PackageData,
    blueprint: dict[str, Any],
) -> dict[str, list[dict[str, str]]]:
    entities = _entity_map(contract)
    output: dict[str, list[dict[str, str]]] = {name: [] for name in entities}
    for operation in blueprint["operations"]:
        entity = entities[operation["entity"]]
        key = _target_tuple(entity, operation["targetKey"], baseline)
        if operation["action"] == "update":
            row = dict(_row_index(baseline, entity)[key])
        elif operation["action"] == "create":
            row = {header: "" for header in entity["headers"]}
            row.update({field: str(value) for field, value in operation["targetKey"].items()})
        else:
            raise AdapterError(f"Unsupported action {operation['action']!r}.")
        row.update({field: str(value) for field, value in operation["values"].items()})
        for alias, rule in _derived_date_aliases(entity).items():
            if rule["sourceField"] in operation["values"]:
                # Keep both XML setters consistent, independent of import order.
                row[alias] = _derived_date_value(rule, row)
        if entity.get("_calendarCSVDateFormat") == "yyyy/MM/dd":
            for field in operation["values"]:
                if entity["types"].get(field) == "date" and re.fullmatch(r"\d{4}-\d{2}-\d{2}", row[field]):
                    row[field] = date.fromisoformat(row[field]).strftime("%Y/%m/%d")
        if entity["name"] in {"IBY_FD_PAYMENT_METHOD", "ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION"}:
            ancestor = "ORA_IBY_FD_PARENT_PAY_MET.PaymentMethodCode"
            code = row["PaymentMethodCode"]
            if row.get(ancestor) not in {"", code}:
                raise AdapterError("Child payment-method ancestor conflicts with its portable code.")
            if operation["action"] == "create":
                row[ancestor] = code  # exact source-export addressing, not a new business input
        if entity["name"] == "ORA_PMT_METHOD_VALIDATION_ASSIGNMENT" and operation["action"] == "create":
            # METHOD AssignmentEntityId is the portable owning PaymentMethodCode.
            # Serialize the ancestor address; it is not a separate business input.
            if row["ValAssignmentEntityType"] != "METHOD":
                raise AdapterError("Payment-method assignment creation requires METHOD parent context.")
            row["ORA_IBY_FD_PARENT_PAY_MET.PaymentMethodCode"] = row["AssignmentEntityId"]
        for field in entity["auditFields"]:
            row[field] = ""
        output[entity["name"]].append(row)
    _add_package_dependencies(contract, baseline, output)
    # Dependency parents execute the same Fusion import hooks as explicit parents.
    parent_checks = [{"entity": "ORA_IBY_FD_PARENT_PAY_MET", "action": "update",
                      "targetKey": {"PaymentMethodCode": row["PaymentMethodCode"]}, "values": {}}
                     for row in output["ORA_IBY_FD_PARENT_PAY_MET"]
                     if any(old["PaymentMethodCode"] == row["PaymentMethodCode"]
                            for old in baseline.rows["ORA_IBY_FD_PARENT_PAY_MET"])]
    _validate_task_import_effects(parent_checks, baseline)
    context = replace(baseline, rows=output)
    for entity_name, rows in output.items():
        entity = entities[entity_name]
        rows.sort(key=lambda row: _row_key(entity, row, context, baseline))
    return output


def _candidate_bytes(
    template: PackageData,
    baseline: PackageData,
    contract: dict[str, Any],
    rows: dict[str, list[dict[str, str]]],
) -> bytes:
    entity_by_member = {
        entity["member"]: entity for entity in contract["package"]["entities"]
    }
    metadata_member = contract["package"]["metadataMember"]
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
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

    return buffer.getvalue()


def _write_candidate(
    template: PackageData,
    baseline: PackageData,
    contract: dict[str, Any],
    rows: dict[str, list[dict[str, str]]],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(_candidate_bytes(template, baseline, contract, rows))


@dataclass(frozen=True)
class MemorySource:
    """Read interface for task bytes; never materializes payloads on disk."""
    name: str
    content: bytes = field(repr=False)

    def read_bytes(self) -> bytes:
        return self.content

    def read_text(self, encoding: str = "utf-8") -> str:
        return self.content.decode(encoding)

    def __str__(self) -> str:
        return self.name


def _update_values_match(entity, existing, values):
    """Reuse declared calendar equivalence without broadening other scalars."""
    return all(
        existing.get(field, "") == str(value)
        or _requested_value_equivalence(
            entity, field, str(value), str(value), existing.get(field, "")
        ) is not None
        for field, value in values.items()
    )


def build_candidate_bytes(
    contract: dict[str, Any], template_bytes: bytes, baseline_bytes: bytes,
    design: dict[str, Any],
) -> tuple[bytes | None, dict[str, Any], list[dict[str, Any]]]:
    """Prepare validated bytes for core's memory-only session; grants no execution authority.

    Reuses normalization, source/identity/side-effect gates, serializer and exact
    candidate validator used by the CLI. The caller keeps all returned state in
    session memory, obtains core approval and never persists an approval envelope.
    None means every requested update is already present: do not submit a load.
    """
    template_source = MemorySource("template-in-memory.zip", template_bytes)
    baseline_source = MemorySource("baseline-in-memory.zip", baseline_bytes)
    template = _read_package(template_source, contract)
    baseline = _read_package(baseline_source, contract)
    effective = _contract_for_package(contract, baseline)
    _validate_source_pair(effective, template, baseline)
    blueprint = _normalized_blueprint(effective, design)
    _validate_blueprint(effective, blueprint, baseline)
    requirements = _requirements(effective, blueprint)
    entities = _entity_map(effective)
    unchanged = all(op["action"] == "update" and _update_values_match(
        entities[op["entity"]],
        _row_index(baseline, entities[op["entity"]])[
            _target_tuple(entities[op["entity"]], op["targetKey"], baseline)
        ], op["values"]
    ) for op in blueprint["operations"])
    if unchanged:
        return None, blueprint, requirements
    content = _candidate_bytes(template, baseline, effective,
                               _candidate_rows(effective, baseline, blueprint))
    result = validate_candidate(
        effective, template_source, baseline_source,
        MemorySource("blueprint-in-memory.json", _canonical_bytes(blueprint)),
        MemorySource("requirements-in-memory.json", _canonical_bytes(requirements)),
        MemorySource("candidate-in-memory.zip", content),
    )
    if result["status"] != "PASS":
        raise AdapterError("In-memory candidate failed exact-package validation: " +
                           "; ".join(item["message"] for item in result["errors"]))
    return content, blueprint, requirements


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
    for entity in entities.values():
        if entity.get("parentKeyResolver"):
            _row_index(candidate, entity, baseline)
    for operation in blueprint["operations"]:
        entity = entities[operation["entity"]]
        key = _target_tuple(entity, operation["targetKey"], candidate, baseline)
        expected_targets.add((entity["name"], key))
        candidate_rows = _row_index(candidate, entity, baseline)
        baseline_rows = _row_index(baseline, entity)
        row = candidate_rows.get(key)
        if row is None:
            issues.append(
                {"code": "MISSING_TARGET", "message": f"Candidate lacks {entity['name']} {key!r}."}
            )
            continue
        before = baseline_rows.get(key, {header: "" for header in entity["headers"]})
        for field, value in operation["values"].items():
            equal = row[field] == str(value)
            if not equal and entity.get("_calendarCSVDateFormat"):
                equal = _requested_value_equivalence(entity, field, str(value), row[field], row[field]) is not None
            if not equal:
                issues.append(
                    {"code": "VALUE_MISMATCH", "message": f"{entity['name']} {key!r} {field} is {row[field]!r}, expected {str(value)!r}."}
                )
        if operation.get("preserveOtherValues", True) and operation["action"] == "update":
            allowed = set(operation["values"]) | set(entity["auditFields"])
            for alias, rule in _derived_date_aliases(entity).items():
                if rule["sourceField"] in operation["values"]:
                    expected = _derived_date_value(rule, row)
                    if row[alias] != expected and not (expected and _requested_value_equivalence(entity, alias, expected, expected, row[alias])):
                        issues.append({"code": "DERIVED_DATE_MISMATCH", "message": f"{alias} must agree with its canonical source date."})
                    allowed.add(alias)
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
    expected_rows = _candidate_rows(contract, baseline, blueprint)
    for entity in contract["package"]["entities"]:
        actual = _row_index(candidate, entity, baseline)
        for expected in expected_rows[entity["name"]]:
            key = _row_key(entity, expected, candidate, baseline)
            identity = (entity["name"], key)
            if identity in expected_targets:
                continue
            expected_targets.add(identity)
            if actual.get(key) != expected:
                issues.append({"code": "PACKAGE_DEPENDENCY_MISMATCH", "message":
                    f"Required parent {entity['name']} {key!r} is missing or changed."})
    for entity in contract["package"]["entities"]:
        for row in candidate.rows[entity["name"]]:
            if entity["name"] in {"IBY_FD_PAYMENT_METHOD", "ORA_IBY_FD_PARENT_PAY_MET_TRANSLATION"} and row.get("ORA_IBY_FD_PARENT_PAY_MET.PaymentMethodCode") != row.get("PaymentMethodCode"):
                issues.append({"code":"PARENT_ADDRESSING", "message":"Child ancestor must equal its exact portable payment-method code."})
            identity = (entity["name"], _row_key(entity, row, candidate, baseline))
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
    contract = _contract_for_package(contract, baseline)
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
    # Input exports remain BOM-tolerant; the exact import bytes must be BOM-free.
    for entity in contract["package"]["entities"]:
        member = entity["member"]
        if candidate.member_bytes[member].startswith(b"\xef\xbb\xbf"):
            issues.append({
                "code": "CSV_UTF8_BOM",
                "member": member,
                "message": (
                    f"{member} has a leading UTF-8 BOM that can prevent Fusion "
                    "from matching its first key header. Rebuild the import ZIP "
                    "as BOM-free UTF-8; preserve metadata and approved values."
                ),
            })
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
    contract = _contract_for_package(contract, baseline)
    _validate_source_pair(contract, template, baseline)
    blueprint = _read_json(blueprint_path)
    requirements = _read_json(requirements_path)
    _validate_blueprint(contract, blueprint, baseline)
    if not isinstance(requirements, list):
        raise AdapterError("Requirements file must contain a JSON array.")
    _requirement_contract(contract, blueprint, requirements)
    entities = _entity_map(contract)
    unchanged = True
    for operation in blueprint['operations']:
        if operation['action'] != 'update':
            unchanged = False
            break
        entity = entities[operation['entity']]
        existing = _row_index(baseline, entity)[_target_tuple(entity, operation['targetKey'], baseline)]
        if not _update_values_match(entity, existing, operation['values']):
            unchanged = False
            break
    if unchanged:
        return {
            'schemaVersion': SCHEMA_VERSION, 'status': 'NO_OP',
            'task': contract['task'], 'baselineSha256': _sha256_path(baseline_path),
            'designSha256': _sha256_bytes(_canonical_bytes(blueprint)),
            'requirementIds': [requirement['id'] for requirement in requirements],
            'candidateCreated': False, 'notImported': True,
            'errors': [], 'warnings': [],
            'detail': 'Every requested update value is already present in the validated baseline; no candidate ZIP was created.',
        }
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
        first_result = build_candidate(
            contract, template_path, baseline_path, blueprint_path, requirements_path, first
        )
        second_result = build_candidate(
            contract, template_path, baseline_path, blueprint_path, requirements_path, second
        )
        if first_result.get('status') == second_result.get('status') == 'NO_OP':
            return {'schemaVersion': SCHEMA_VERSION, 'status': 'PASS',
                    'buildDisposition': 'NO_OP', 'candidateCreated': False, 'identicalBytes': True,
                    'firstSha256': None, 'secondSha256': None}
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
    if entity.get("_calendarCSVDateFormat") == "yyyy/MM/dd":
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", requested):
                return None
            dates = []
            for value in (requested, candidate, persisted):
                fmt = "%Y/%m/%d" if re.fullmatch(r"\d{4}/\d{2}/\d{2}", value) else "%Y-%m-%d" if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) else None
                if fmt is None:
                    return None
                dates.append(datetime.strptime(value, fmt).date())
            if len(set(dates)) != 1:
                return None
        except ValueError:
            return None
        return {"ruleId":"FSCR.TYPE.DATE.OBSERVED_87_CSV", "entity":entity["name"], "field":field,
                "declaredType":declared_type, "rawValues":{"requested":requested,"candidate":candidate,"persisted":persisted},
                "canonicalValue":dates[0].isoformat(), "semanticValue":"same Gregorian calendar date",
                "contractEvidence":["Exact observed87-column task fingerprint and metadata date type; ordinary export/source yyyy/MM/dd representation"]}
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
    contract = _contract_for_package(contract, baseline)
    _require_same_variant(contract, baseline, candidate, persisted)
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
            "candidate": _row_index(candidate, entity, baseline),
            "persisted": _row_index(persisted, entity),
        }
        for name, entity in entities.items()
    }
    matrix = []
    for requirement in requirements:
        entity = entities[requirement["entity"]]
        key = _target_tuple(entity, requirement["targetKey"], candidate, baseline)
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
            if not passed and (candidate_value == requested or entity.get("_calendarCSVDateFormat")):
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
                    _target_tuple(entities[op["entity"]], op["targetKey"], candidate, baseline),
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
    contract = _contract_for_package(contract, before)
    template = _read_package(template_path, contract)
    _require_same_variant(contract, before, current, template)
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
        key = _target_tuple(entity, operation["targetKey"], before)
        original_row = _row_index(before, entity).get(key)
        current_row = _row_index(current, entity).get(key)
        if original_row is None or current_row is None:
            raise AdapterError(f"Rollback target {entity['name']} {key!r} is missing.")
        values = {field: original_row[field] for field in operation["values"]}
        for field in values:
            if entity["types"].get(field) == "date" and re.fullmatch(r"\d{4}/\d{2}/\d{2}", values[field]):
                values[field] = datetime.strptime(values[field], "%Y/%m/%d").date().isoformat()
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
    contract = _contract_for_package(contract, package)
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
    if command == 'build' and result.get('status') == 'NO_OP':
        return result.get('candidateCreated') is False and result.get('notImported') is True
    if command == "manifest":
        return result.get("status") == "COMPLETED"
    return result.get("status", "PASS") == "PASS"


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


if __name__ == "__main__":
    raise SystemExit(main())
