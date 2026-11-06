#!/usr/bin/env python3
"""Portable, data-driven FSM task adapter runtime.

This file is copied into a generated Nested task skill.  Task semantics live in
the adjacent e2e-adapter.json descriptor and ora-resource rule plan.  The
runtime performs offline package work only; it never connects to Fusion.
"""

from __future__ import annotations

import argparse
from collections import Counter
import copy
import csv
import hashlib
import io
import json
import os
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

from readback_evidence import bind_readback_result, read_observation, _host as _target_origin


SCHEMA_VERSION = "fscr-fsm-task-adapter-v1"
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


def _write_json(path: Path, value: Any) -> None:
    _validate_new_outputs([path], [])
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".bank-charge-json-", dir=path.parent) as temporary:
        staged = Path(temporary) / "report.json"
        staged.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        os.link(staged, path)


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
    if any(path.is_symlink() for path in outputs):
        raise AdapterError("Output paths must not be symbolic links.")
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


def _row_key(entity: dict[str, Any], row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row.get(field, "") for field in entity["keyFields"])


def _target_tuple(entity: dict[str, Any], target: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(target.get(field, "")) for field in entity["keyFields"])


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
            candidate = value
        else:
            candidate = ""
        if re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", candidate):
            try:
                valid = Decimal(candidate).is_finite()
            except InvalidOperation:
                valid = False
    elif normalized_type == "date":
        if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            try:
                date.fromisoformat(value)
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


def _validate_option_names(entity: dict[str, Any], row: dict[str, Any], operation_id: str) -> None:
    """User-approved input rules, independent of Oracle's value-clearing UI."""
    prefix = "ORA_AP_BANK_CHARGE." if entity["name"] == "ORA_AP_BANK_CHARGE_LINE" else ""
    for side in ("Transferring", "Receiving"):
        for kind, all_label, one_label in (
            ("Bank", "All banks", "Specific bank"),
            ("Branch", "All branches", "Specific branch"),
        ):
            option, name = prefix + side + kind + "Option", prefix + side + kind + "Name"
            if option not in row and name not in row:
                continue
            supplied_name = row.get(name)
            if supplied_name is not None and not isinstance(supplied_name, str):
                raise AdapterError(f"Operation {operation_id} field {name} must be text or blank.")
            has_name = bool(supplied_name and supplied_name.strip())
            supplied_option = row.get(option)
            if supplied_option is None or not str(supplied_option).strip():
                raise AdapterError(
                    f"Operation {operation_id} must supply {option}; the All default "
                    f"is not applicable when {name} is supplied."
                )
            selected = _normalize_field_value(entity, option, supplied_option, operation_id)
            _validate_field_value(entity, option, selected, operation_id)
            if selected == one_label and not has_name:
                raise AdapterError(f"Operation {operation_id}: {option} is {one_label}; {name} is required.")
            if selected == all_label and has_name:
                raise AdapterError(f"Operation {operation_id}: {option} is {all_label}; {name} must be blank.")


def _is_omitted(value: Any) -> bool:
    """Treat absent, null, empty, and whitespace-only customer input as omitted."""
    return value is None or (isinstance(value, str) and not value.strip())


def _applicable_reference_checks(header):
    checks = {("resolve_currency", "")}
    if header.get("LegalEntityName") != "All":
        checks.add(("resolve_legal_entity", ""))
    for side in ("Transferring", "Receiving"):
        if header.get(side + "BankOption") == "Specific bank":
            checks.add(("resolve_bank", side))
        if header.get(side + "BranchOption") == "Specific branch":
            checks.add(("resolve_bank_branch", side))
        if header.get(side + "BankCountry"):
            checks.add(("resolve_bank_country", side))
    return checks


def _additional_rest_check_warnings(results, environment, header):
    """Validate recorded reference outcomes; return only availability warnings."""
    if not isinstance(results, list):
        raise AdapterError("reference_check_results must be an array.")
    reference_fields = ["LegalEntityName", "LegalEntityIdentifier", "CurrencyCode"]
    reference_fields += [side + suffix for side in ("Transferring", "Receiving")
                         for suffix in ("BankOption", "BankName", "BankNumber", "BankCountry",
                                        "BranchOption", "BranchName", "BranchNumber")]
    context = {"environment": environment,
               "referenceValues": {field: str(header.get(field) or "") for field in reference_fields}}
    paths = {
        "resolve_legal_entity": "legalEntitiesLOV", "resolve_currency": "currenciesLOV",
        "resolve_bank": "cashBanksLOV", "resolve_bank_country": "territoriesLOV",
        "resolve_bank_branch": "cashBankBranchesLOV",
    }
    availability = {"auth_authz": {401, 403}, "endpoint_unavailable": {404, 405, 410, 501},
                    "transport_environment": {None, 408, 429, 500, 502, 503, 504}}
    warnings = []
    seen = set()
    allowed = {"resolver", "side", "status", "failureClass", "httpStatus",
               "method", "endpointPath", "requestContext", "evidence"}
    for item in results:
        if not isinstance(item, dict):
            raise AdapterError("Reference API outcome must be an object.")
        verified = item.get("status") == "verified"
        expected = allowed | {"matchCount", "hasMore"} if verified else allowed
        if set(item) != expected:
            raise AdapterError("Reference API outcome must contain only the declared sanitized fields.")
        resolver, side = item["resolver"], item["side"]
        if any(not isinstance(item[name], str) for name in ("resolver", "side", "failureClass")):
            raise AdapterError("Reference API resolver, side and failure class must be strings.")
        if item["status"] not in ("unavailable", "verified"):
            raise AdapterError("Reference checks must be verified or unavailable; invalid or ambiguous references require correction.")
        if resolver not in paths or (resolver in {"resolve_legal_entity", "resolve_currency"}
                                    and side != "") or (resolver not in {"resolve_legal_entity", "resolve_currency"}
                                                       and side not in {"Transferring", "Receiving"}):
            raise AdapterError("Reference API outcome names an unknown resolver or bank side.")
        if (resolver, side) not in _applicable_reference_checks(header):
            raise AdapterError("Reference API outcome is not applicable to this charge group.")
        status = item["httpStatus"]
        if (not environment or item["requestContext"] != context or item["method"] != "GET"
                or item["endpointPath"] != "/fscmRestApi/resources/11.13.18.05/" + paths[resolver]
                or (status is not None and type(status) is not int)
                or not isinstance(item["evidence"], str) or not item["evidence"].strip()):
            raise AdapterError("Reference outcome must bind this environment/group and declared GET endpoint.")
        if (resolver, side) in seen:
            raise AdapterError("Duplicate reference API check.")
        seen.add((resolver, side))
        if verified:
            if (status != 200 or item["failureClass"] != ""
                    or type(item["matchCount"]) is not int or item["matchCount"] != 1
                    or item["hasMore"] is not False):
                raise AdapterError("Verified reference requires HTTP 200, one exact match, no further pages and no failure class.")
            continue
        if (item["failureClass"] not in availability
                or status not in availability[item["failureClass"]]):
            raise AdapterError("Unavailable reference must record an API availability failure.")
        warnings.append({"status": "UNVERIFIED_API_UNAVAILABLE", "resolver": resolver, "side": side,
                         "failureClass": item["failureClass"], "httpStatus": status,
                         "evidence": item["evidence"],
                         "message": "Additional REST validation unavailable; supplied references preserved for governed Fusion validation."})
    return warnings


def _apply_create_defaults(
    entity: dict[str, Any], values: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Apply source-backed defaults without erasing specific reference intent."""
    normalized = dict(values)
    applied: list[dict[str, Any]] = []
    for field, default in entity.get("createDefaults", {}).items():
        if field in normalized and not _is_omitted(normalized[field]):
            continue
        if field.endswith("Option"):
            name = field.removesuffix("Option") + "Name"
            if not _is_omitted(normalized.get(name)):
                continue
        if field == "LegalEntityName" and not _is_omitted(
            normalized.get("LegalEntityIdentifier")
        ):
            continue
        normalized[field] = default["value"]
        applied.append(
            {
                "entity": entity["name"],
                "field": field,
                "value": default["value"],
                "sourceIds": default["sourceIds"],
            }
        )
    return normalized, applied


def assess_business_intake(contract: dict[str, Any], intake: dict[str, Any]) -> dict[str, Any]:
    """Offline consistency assessment; never an executable blueprint or readiness override."""
    if intake.get("task", {}).get("code") != contract["task"]["code"]:
        raise AdapterError("Intake task identity differs from the adapter.")
    header, line = contract["package"]["entities"]
    raw = intake.get("draft_field_mapping")
    lines = intake.get("draft_charge_lines")
    if not isinstance(raw, dict) or not isinstance(lines, list) or not lines:
        raise AdapterError("Supply a header and at least one charge line.")
    normalized: dict[str, Any] = {}
    for field in raw:
        if field not in header["headers"]:
            raise AdapterError(f"Unknown header field {field}.")
        normalized[field] = _normalize_field_value(header, field, raw[field], "intake")
        if normalized[field] is not None:
            _validate_field_value(header, field, normalized[field], "intake")
    normalized, applied_defaults = _apply_create_defaults(header, normalized)
    for item in applied_defaults:
        _validate_field_value(header, item["field"], item["value"], "intake-default")
    if normalized.get("LegalEntityName") == "All":
        if not _is_omitted(normalized.get("LegalEntityIdentifier")):
            raise AdapterError("All legal entities requires a blank LegalEntityIdentifier.")
        if "LegalEntityIdentifier" in normalized:
            normalized["LegalEntityIdentifier"] = ""
    _validate_option_names(header, normalized, "intake")
    for field in ("LegalEntityName", "CurrencyCode", "SettlementPriorityDisplay", "TransferringBankOption", "ReceivingBankOption", "TransferringBranchOption", "ReceivingBranchOption"):
        if not isinstance(normalized.get(field), str) or not normalized[field].strip():
            raise AdapterError(f"Supply business value {field}; the source-backed default is not applicable.")
    local_checks = ["source_backed_header_defaults", "local_choice_domains", "four_option_name_pairs"]
    for number, values in enumerate(lines, 1):
        if not isinstance(values, dict):
            raise AdapterError(f"Line {number} must be an object.")
        for field in ("StartDate", "TransAmountFrom", "BankChargeStandard", "BankChargeNegotiated"):
            if values.get(field) in (None, ""):
                raise AdapterError(f"Line {number} requires {field}.")
        for field in values:
            if field not in line["headers"] or field.startswith("ORA_AP_BANK_CHARGE."):
                raise AdapterError(f"Unknown or parent-owned line input {field}.")
            # Null records business intent only; this is not CSV serialization.
            if values[field] not in (None, ""):
                _validate_field_value(line, field, values[field], f"line-{number}")
        amounts = {}
        for field in ("TransAmountFrom", "TransAmountTo", "BankChargeStandard", "BankChargeNegotiated"):
            if values.get(field) not in (None, ""):
                amount = Decimal(str(values[field]))
                if not amount.is_finite() or amount < 0:
                    raise AdapterError(f"Line {number}: {field} must be finite and nonnegative.")
                amounts[field] = amount
        if "TransAmountTo" in amounts and amounts["TransAmountFrom"] > amounts["TransAmountTo"]:
            raise AdapterError(f"Line {number}: payment amount From exceeds To.")
        if values.get("EndDate") and date.fromisoformat(values["StartDate"]) > date.fromisoformat(values["EndDate"]):
            raise AdapterError(f"Line {number}: StartDate exceeds EndDate.")
    local_checks += ["required_line_scalars", "nonnegative_finite_amounts", "amount_and_date_order"]
    if len(lines) == 1:
        if Decimal(str(lines[0]["TransAmountFrom"])) != 0:
            raise AdapterError("The only payment range must start at zero.")
        if lines[0].get("TransAmountTo") not in (None, ""):
            raise AdapterError("The only payment range must have an open upper amount.")
        local_checks += ["single_range_starts_at_zero", "single_range_open_upper_amount"]
    all_scope = all(normalized[side + "BankOption"] == "All banks" and normalized[side + "BranchOption"] == "All branches" for side in ("Transferring", "Receiving"))
    applicable_checks = _applicable_reference_checks(normalized)
    country_lookup_required = any(resolver == "resolve_bank_country" for resolver, _ in applicable_checks)
    not_applicable = ["resolve_bank", "resolve_bank_country", "resolve_bank_branch"] if all_scope else []
    if country_lookup_required:
        not_applicable = [resolver for resolver in not_applicable if resolver != "resolve_bank_country"]
    unresolved = sorted(set(normalized) - set(header["createFields"]))
    reference_warnings = _additional_rest_check_warnings(
        intake.get("reference_check_results", []),
        (intake.get("environment") or {}).get("name"), normalized)
    verified_references = [copy.deepcopy(item) for item in intake.get("reference_check_results", [])
                           if item["status"] == "verified"]
    reference_verified = ({(item["resolver"], item["side"]) for item in verified_references}
                          == applicable_checks)
    assembly_review = None
    if all_scope and normalized["LegalEntityName"] == "All":
        header_row = {field: "" if normalized.get(field) is None else str(normalized[field]) for field in header["headers"]}
        line_rows = []
        for values in lines:
            row = {}
            for field in line["headers"]:
                if field.startswith("ORA_AP_BANK_CHARGE."):
                    row[field] = header_row[field.split(".", 1)[1]]
                else:
                    row[field] = "" if values.get(field) is None else str(values[field])
            line_rows.append(row)
        assembly_rows = {header["name"]: [header_row], line["name"]: line_rows}
        assembly_review = {"rows": assembly_rows, "validation": _validate_parent_assembly(contract, assembly_rows),
                           "purpose": "Offline field-mapping review only; not an import archive or runnable blueprint"}
        local_checks.append("csv_parent_assembly")
    return {
        "status": "LOCAL_INPUT_PASS_EXECUTION_BLOCKED",
        "task": intake["task"], "environment": intake.get("environment"),
        "normalized_header": normalized, "charge_lines": lines,
        "applied_defaults": applied_defaults,
        "local_checks_passed": local_checks,
        "not_applicable_resolvers": not_applicable,
        "local_choice_resolvers": ["resolve_bank_option", "resolve_branch_option", "resolve_settlement_priority"],
        "reference_validation_warnings": reference_warnings,
        "reference_validation_verified": reference_verified,
        "reference_validation_evidence": verified_references,
        "applicable_reference_contracts": (["resolve_legal_entity", "resolve_currency"]
                                           + ([] if all_scope else ["conditional_specific_bank_country_branch"])
                                           + (["resolve_bank_country"] if country_lookup_required else [])),
        "supplied_header_fields_without_create_contract": unresolved,
        "csv_assembly_review": assembly_review,
        "confirmed_execution_contracts": ["Create input consumption for all 94 package fields and 18-column CSV parent assembly."],
        "remaining_execution_requirements": [
            "Assess applicable references through the declared workflow; preserve bound additional REST availability warnings without treating them as blockers or passed checks.",
            "Check fresh exported groups for an existing definition and compare the complete expected state after import.",
            "Complete applicable task-rule contracts and obtain a successful execution plan before preparing an import candidate.",
        ] + (["Assess the complete multi-line range/date rules; this local assessor does not claim cross-row coverage."] if len(lines) > 1 else []),
        "recovery": "Monitor the original attempt, retrieve logs and fresh state, disclose partial effects; no automatic replay or rollback.",
        "candidate_generated": False, "runnable_blueprint": False, "fusion_calls": 0,
    }


def _validate_parent_assembly(contract: dict[str, Any], rows: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    """Validate CSV staging links, never persisted Fusion record identity.

    SRC-CODE-FSM-CSV-XML-TRANSFORM 734-739,817-830 and the reviewed
    CSVParser 422-428 concatenate raw cells, representing empty cells as
    Java's literal 'null'. Detect collisions before reproducing that lookup.
    """
    header, child = contract["package"]["entities"]
    prefix = header["name"] + "."
    parent_fields = [field[len(prefix):] for field in child["headers"] if field.startswith(prefix)]
    header_order = [field for field in header["headers"] if field in parent_fields]
    if len(parent_fields) != 18 or header_order != parent_fields:
        raise AdapterError("CSV parent-reference columns do not match the source-backed 18-field order.")

    def values(row, names):
        if any(name not in row for name in names):
            raise AdapterError("CSV staging context is missing a parent-reference column.")
        if any(not isinstance(row[name], str) for name in names):
            raise AdapterError("CSV staging comparison requires raw string cells, including explicit empty strings.")
        return tuple(row[name] for name in names)

    def signature(items):
        return "".join("null" if item == "" else item for item in items)

    parents = {}
    for index, row in enumerate(rows.get(header["name"], [])):
        context = values(row, parent_fields)
        key = signature(context)
        if key in parents:
            prior_context, _ = parents[key]
            reason = "duplicate header context" if prior_context == context else "ambiguous concatenated header context"
            raise AdapterError("CSV staging cannot safely resolve " + reason + ".")
        parents[key] = (context, index)
    links = []
    for index, row in enumerate(rows.get(child["name"], [])):
        context = values(row, [prefix + field for field in parent_fields])
        found = parents.get(signature(context))
        if found is None:
            raise AdapterError(f"CSV line {index + 1} has no matching parent header context.")
        if found[0] != context:
            raise AdapterError(f"CSV line {index + 1} has an ambiguous concatenated parent context.")
        links.append({"line_index": index, "header_index": found[1]})
    return {"status": "PASS", "parent_reference_fields": parent_fields, "links": links,
            "identity_scope": "CSV staging only; no saved-record matching assertion"}


def _row_index(
    package: PackageData, entity: dict[str, Any]
) -> dict[tuple[str, ...], dict[str, str]]:
    if not entity["keyFields"]:
        raise AdapterError(f"Entity {entity['name']} has no configured row-index fields.")
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
            values, operation_defaults = _apply_create_defaults(entity, values)
            for item in operation_defaults:
                applied_defaults.append(
                    {
                        "operationId": operation["id"],
                        **item,
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
    task = blueprint.get("task")
    if task != {"name": contract["task"]["name"], "code": contract["task"]["code"]}:
        raise AdapterError("Blueprint task identity differs from the adapter contract.")
    operations = blueprint.get("operations")
    if not isinstance(operations, list) or not operations:
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
        if action == "update" and not all(
            entity.get("keyFields") for entity in contract["package"]["entities"]
        ):
            raise AdapterError(
                "Bank Charges updates require the snapshot-bound update command; "
                "generic keyed normalize/build is unavailable without local row-index fields."
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
        effective = {**target, **values}
        if action != "create" and baseline is not None:
            before = _row_index(baseline, entity).get(target_tuple, {})
            effective = {**before, **effective}
        _validate_option_names(entity, effective, operation_id)
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
    try:
        _validate_parent_assembly(contract, candidate.rows)
    except AdapterError as exc:
        issues.append({"code": "PARENT_ASSEMBLY", "message": str(exc)})
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
        try:
            _validate_option_names(entity, row, operation["id"])
        except AdapterError as exc:
            issues.append({"code": "OPTION_NAME_CONSISTENCY", "message": str(exc)})
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
    _validate_parent_assembly(contract, rows)
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


def reconcile(
    contract: dict[str, Any],
    baseline_path: Path,
    candidate_path: Path,
    blueprint_path: Path,
    requirements_path: Path,
    export_path: Path,
    readback_evidence_path: Path | None = None,
    import_request_id: str | None = None,
    target_url: str | None = None,
) -> dict[str, Any]:
    baseline = _read_package(baseline_path, contract)
    candidate = _read_package(candidate_path, contract)
    persisted = _read_package(export_path, contract)
    for label, package in (("Candidate", candidate), ("Observed export", persisted)):
        for field in ("ProcessEnv", "ProcessRelease"):
            if package.metadata[field] != baseline.metadata[field]:
                raise AdapterError(
                    f"{label} {field} differs from baseline: "
                    f"{package.metadata[field]!r} versus {baseline.metadata[field]!r}."
                )
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
    return _bind_readback(
        comparison, contract, baseline, persisted, candidate_path,
        readback_evidence_path, import_request_id, target_url,
    )


def _bind_readback(comparison, contract, before, after, candidate_path=None,
                   readback_evidence_path=None, import_request_id=None, target_url=None,
                   candidate_error=None):
    """Keep package comparisons distinct from governed persistence evidence."""
    evidence = read_observation(readback_evidence_path)
    if candidate_error is not None:
        evidence = {"_readError": candidate_error}
    candidate_sha256 = ""
    if candidate_path is not None:
        try:
            candidate_sha256 = _sha256_path(Path(candidate_path))
        except OSError as exc:
            evidence = {"_readError": f"Cannot read the submitted candidate: {exc}"}
    return bind_readback_result(
        comparison, evidence,
        task_code=contract["task"]["code"],
        environment=before.metadata["ProcessEnv"],
        baseline_sha256=getattr(before, "archive_sha256", ""),
        candidate_sha256=candidate_sha256,
        export_sha256=getattr(after, "archive_sha256", ""),
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
    if not isinstance(environment, str) or environment.strip() != package.metadata["ProcessEnv"]:
        raise AdapterError("Manifest environment must match package ProcessEnv.")
    try:
        origin = _target_origin(base_url)
    except ValueError as exc:
        raise AdapterError("Manifest base URL must be a complete HTTPS origin.") from exc
    populated = [
        entity["member"]
        for entity in contract["package"]["entities"]
        if package.rows[entity["name"]]
    ]
    return {
        "environment": package.metadata["ProcessEnv"],
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


def _update_cell(entity, field, value):
    from inspect_bank_charge_group import _cell

    return _cell(entity, field, value)


def _update_row(entity, row):
    from inspect_bank_charge_group import _row

    return _row(entity, row)


def _read_update_package(path, contract):
    from prepare_charge_group_create import read_group_package

    return read_group_package(path, contract)


REVIEW_FIELDS = frozenset({
    'BankChargeStandard', 'BankChargeNegotiated', 'StartDate', 'EndDate',
    'TransAmountFrom', 'TransAmountTo',
})
CLEARABLE_REVIEW_FIELDS = frozenset({'EndDate', 'TransAmountTo'})


def _update_object(value, label):
    if not isinstance(value, dict):
        raise AdapterError(f'{label} must be an object.')
    return value


def _check_update_snapshot(contract, request, snapshot):
    environment = _update_object(request.get('environment'), 'environment').get('name')
    if not isinstance(environment, str) or not environment.strip():
        raise AdapterError('Supply the explicit environment name.')
    if snapshot.metadata['ProcessEnv'] != environment:
        raise AdapterError('Snapshot environment differs from the update request.')
    for entity in contract['package']['entities']:
        for row in snapshot.rows[entity['name']]:
            _update_row(entity, row)
    return _validate_parent_assembly(contract, snapshot.rows)['links']


def _proposed_update_value(entity, field, value):
    if value is None or value == '':
        if field not in CLEARABLE_REVIEW_FIELDS:
            raise AdapterError(f'{field} is required and cannot be cleared.')
        return ''
    if field in {'StartDate', 'EndDate'}:
        if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
            raise AdapterError(f'{field} must use YYYY-MM-DD.')
    elif isinstance(value, bool) or not isinstance(value, (str, int)):
        raise AdapterError(f'{field} must be an exact decimal string or integer; floating-point numbers are not accepted.')
    text = str(value)
    _update_cell(entity, field, text)
    return text


def _check_update_group(header, child, parent, lines):
    # Check effective saved header context without applying any create defaults.
    for field, rule in header.get('valueContracts', {}).items():
        if rule:
            _normalize_field_value(header, field, parent[field], 'update-review')
    _validate_option_names(header, parent, 'update-review')
    for field in ('LegalEntityName', 'CurrencyCode', 'SettlementPriorityDisplay'):
        if not parent[field].strip():
            raise AdapterError(f'The saved header is missing {field}.')
    if parent['LegalEntityName'] == 'All' and parent['LegalEntityIdentifier'].strip():
        raise AdapterError('All legal entities requires a blank LegalEntityIdentifier.')

    periods = set()
    ranges = []
    for line in lines:
        for field in ('StartDate', 'TransAmountFrom', 'BankChargeStandard', 'BankChargeNegotiated'):
            if not line[field]:
                raise AdapterError(f'The proposed group requires {field}.')
        start = _update_cell(child, 'StartDate', line['StartDate'])
        end = _update_cell(child, 'EndDate', line['EndDate'])
        if end[0] != 'blank' and start[1] > end[1]:
            raise AdapterError('StartDate exceeds EndDate in the proposed group.')
        periods.add((start, end))
        for field in ('TransAmountFrom', 'TransAmountTo', 'BankChargeStandard', 'BankChargeNegotiated'):
            if line[field] and Decimal(line[field]) < 0:
                raise AdapterError(f'{field} must be nonnegative in the proposed group.')
        lower = Decimal(line['TransAmountFrom'])
        upper = Decimal(line['TransAmountTo']) if line['TransAmountTo'] else None
        if upper is not None and upper <= lower:
            raise AdapterError('Finite payment ranges must have positive width.')
        ranges.append((lower, upper))
    if len(periods) != 1:
        raise AdapterError('This update review supports one common effective period for the complete group.')
    ranges.sort(key=lambda item: item[0])
    if ranges[0][0] != 0:
        raise AdapterError('The complete payment range set must start at zero.')
    for index, (_, upper) in enumerate(ranges):
        if index == len(ranges) - 1:
            if upper is not None:
                raise AdapterError('The final payment range must have an open upper amount.')
        elif upper is None or upper != ranges[index + 1][0]:
            raise AdapterError('Payment ranges must be contiguous without gaps or overlaps.')


def prepare_update(contract, request, snapshot):
    """Project explicit changes onto an exact exported row without inventing keys."""
    _update_object(request, 'request')
    required = {'task', 'environment', 'snapshot_sha256', 'target', 'changes'}
    if not required <= set(request) or set(request) - required - {'reference_check_results'}:
        raise AdapterError('Request requires task, environment, snapshot_sha256, target and changes; only reference_check_results is optional.')
    if _update_object(request['task'], 'task').get('code') != contract['task']['code']:
        raise AdapterError('Update request task differs from the adapter.')
    digest = request['snapshot_sha256']
    if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
        raise AdapterError('Bind the request to the exact snapshot SHA-256.')
    if snapshot.archive_sha256 != digest:
        raise AdapterError('Snapshot SHA-256 changed; reselect the target and review original values.')
    links = _check_update_snapshot(contract, request, snapshot)
    target = _update_object(request['target'], 'target')
    if set(target) != {'header', 'line'}:
        raise AdapterError('Target requires complete exported header and line rows.')
    header, child = contract['package']['entities']
    for label, entity in (('header', header), ('line', child)):
        _update_row(entity, _update_object(target[label], 'target.' + label))
    parents = [i for i, row in enumerate(snapshot.rows[header['name']]) if row == target['header']]
    if len(parents) != 1:
        raise AdapterError('Target header must match exactly one complete exported row.')
    group_indexes = [link['line_index'] for link in links if link['header_index'] == parents[0]]
    matches = [i for i in group_indexes if snapshot.rows[child['name']][i] == target['line']]
    if len(matches) != 1:
        raise AdapterError('Target line must match exactly one exported row belonging to the header.')
    changes = _update_object(request['changes'], 'changes')
    if not changes or set(changes) - REVIEW_FIELDS:
        raise AdapterError('Supply at least one supported line change: ' + ', '.join(sorted(REVIEW_FIELDS)) + '.')
    proposed = copy.deepcopy(target['line'])
    differences = []
    for field in child['headers']:
        if field not in changes:
            continue
        value = _proposed_update_value(child, field, changes[field])
        # Equivalent date/decimal spellings are not changes; preserve raw bytes.
        if _update_cell(child, field, proposed[field]) != _update_cell(child, field, value):
            differences.append({'field': field, 'before': proposed[field], 'after': value})
            proposed[field] = value
    expected = copy.deepcopy(snapshot.rows)
    expected[child['name']][matches[0]] = proposed
    _check_update_group(header, child, target['header'], [expected[child['name']][i] for i in group_indexes])
    _validate_parent_assembly(contract, expected)
    reference_warnings = _additional_rest_check_warnings(
        request.get('reference_check_results', []), request['environment']['name'], target['header'])

    return {
        'schema_version': 'bank-charge-update-review-v2',
        'status': 'UPDATE_REVIEW_PREPARED',
        'task': copy.deepcopy(request['task']), 'environment': copy.deepcopy(request['environment']),
        'request': copy.deepcopy(request), 'request_sha256': _sha256_bytes(_canonical_bytes(request)),
        'baseline_sha256': digest, 'snapshot_release': snapshot.metadata['ProcessRelease'],
        'target': {'header': copy.deepcopy(target['header']), 'before': copy.deepcopy(target['line']), 'after': proposed},
        'changes': differences, 'change_count': len(differences),
        'expected_rows': expected, 'row_counts': {name: len(rows) for name, rows in expected.items()},
        'applied_defaults': [], 'implementation_gaps': [],
        'reference_validation_warnings': reference_warnings,
        'local_checks': ['exact_snapshot_binding', 'unique_complete_target_rows', 'csv_parent_assembly',
                         'resulting_group_scalars_and_ranges', 'unspecified_values_and_rows_preserved'],
        'requires_before_import': [
            'Build and validate the update ZIP with --package; this review JSON is not an import source.',
            'Fresh authorized export and applicable reference/rule checks through the owning workflow.',
            'Data Loader and Task Hook validation, immutable preview and exact artifact approval.',
        ],
        'boundary': 'Full exported rows and the snapshot hash locate this local review only; they are not Oracle saved-record keys.',
        'freshness': 'A file hash binds bytes, not live freshness. Refresh and repeat preparation before future execution.',
        'import_ready': False, 'execution_ready': False, 'candidate_generated': False,
        'runnable_blueprint': False, 'fusion_calls': 0,
    }


def _update_package_rows(contract, review):
    """Limit import scope to the selected header and its complete charge lines."""
    header, child = contract['package']['entities']
    rows = review['expected_rows']
    parent_index = rows[header['name']].index(review['target']['header'])
    links = _validate_parent_assembly(contract, rows)['links']
    return {
        header['name']: [copy.deepcopy(review['target']['header'])],
        child['name']: [copy.deepcopy(rows[child['name']][link['line_index']])
                        for link in links if link['header_index'] == parent_index],
    }


def validate_update_package(contract, request, snapshot, candidate):
    """Check the actual ZIP against the request and original exported group."""
    review = prepare_update(contract, request, snapshot)
    if not review['change_count']:
        raise AdapterError('No effective changes; no update package is needed.')
    metadata = contract['package']['metadataMember']
    if candidate.member_bytes[metadata] != snapshot.member_bytes[metadata]:
        raise AdapterError('Update package metadata differs from the original export.')
    _check_update_snapshot(contract, request, candidate)
    expected = _update_package_rows(contract, review)
    if candidate.rows != expected:
        raise AdapterError('Update package rows differ from the requested complete charge group.')
    return {
        **review, 'status': 'UPDATE_PACKAGE_VALIDATED',
        'source_path': str(candidate.path.resolve()), 'sha256': candidate.archive_sha256,
        'package_scope': 'selected_charge_group',
        'package_row_counts': {name: len(rows) for name, rows in expected.items()},
        'local_package_validated': True,
        'local_checks': review['local_checks'] + ['original_metadata_preserved',
                         'exact_package_members_and_columns', 'exact_requested_group_rows'],
        'requires_before_import': review['requires_before_import'][1:],
    }


def build_update_package(contract, request, snapshot, output):
    """Stage, reopen and validate the ZIP before publishing without overwrite."""
    output = Path(output)
    if output.suffix.lower() != '.zip':
        raise AdapterError('Update package output must be a .zip file.')
    _validate_new_outputs([output], [snapshot.path])
    if output.is_symlink():
        raise AdapterError('Update package output must not be a symbolic link.')
    review = prepare_update(contract, request, snapshot)
    if not review['change_count']:
        raise AdapterError('No effective changes; no update package is needed.')
    rows = _update_package_rows(contract, review)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.bank-charge-update-', dir=output.parent) as temporary:
        staged = Path(temporary) / 'candidate.zip'
        source = copy.deepcopy(snapshot)
        _write_candidate(source, source, contract, rows, staged)
        checked = validate_update_package(contract, request, snapshot, _read_update_package(staged, contract))
        # Same-directory hard linking publishes complete bytes and refuses an
        # existing destination, including one created after the preflight.
        os.link(staged, output)
    return {**checked, 'status': 'UPDATE_PACKAGE_PREPARED_NOT_APPROVED',
            'source_path': str(output.resolve()), 'candidate_generated': True}


def compare_update_after(contract, request, before, after, *, candidate_path=None,
                         readback_evidence_path=None, import_request_id=None, target_url=None):
    """Require the exact proposed complete state, allowing only typed formatting changes."""
    review = prepare_update(contract, request, before)
    _check_update_snapshot(contract, request, after)
    if before.metadata['ProcessRelease'] != after.metadata['ProcessRelease']:
        raise AdapterError('Snapshot releases differ; re-establish a comparable baseline.')
    checks = {}
    for entity in contract['package']['entities']:
        wanted = Counter(_update_row(entity, row) for row in review['expected_rows'][entity['name']])
        observed = Counter(_update_row(entity, row) for row in after.rows[entity['name']])
        checks[entity['name']] = {
            'matches': wanted == observed,
            'missing_or_changed_rows': sum((wanted - observed).values()),
            'extra_or_changed_rows': sum((observed - wanted).values()),
        }
    comparison = {
        'status': 'PASS' if all(item['matches'] for item in checks.values()) else 'FAIL',
        'before_sha256': before.archive_sha256, 'after_sha256': after.archive_sha256,
        'request_sha256': review['request_sha256'], 'complete_state_checks': checks,
        'boundary': 'Observed state and preservation only; no assertion about process causation, importer keys or execution readiness.',
        'import_ready': False, 'execution_ready': False, 'fusion_calls': 0,
    }
    candidate_error = None
    if candidate_path is not None and readback_evidence_path is not None:
        try:
            validate_update_package(
                contract, request, before, _read_update_package(Path(candidate_path), contract)
            )
        except (AdapterError, OSError, ValueError) as exc:
            candidate_error = f"Submitted candidate does not match this update: {exc}"
    return _bind_readback(
        comparison, contract, before, after, candidate_path,
        readback_evidence_path, import_request_id, target_url, candidate_error,
    )



def _run_update_command(args):
    published_package = None
    try:
        if (args.candidate or args.readback_evidence or args.import_request_id or args.target_url) and not args.after:
            raise AdapterError('Read-back evidence options apply only with --after.')
        if args.package and not args.output:
            raise AdapterError('--package requires --output for the accompanying review JSON.')
        if args.output:
            if args.output.suffix.lower() != '.json':
                raise AdapterError('--output must be a review JSON file; use --package for a ZIP.')
            outputs = [args.output] + ([args.package] if args.package else [])
            inputs = ([args.request, args.snapshot] + ([args.after] if args.after else [])
                      + ([args.validate_package] if args.validate_package else [])
                      + ([args.candidate] if args.candidate else [])
                      + ([args.readback_evidence] if args.readback_evidence else []))
            _validate_new_outputs(outputs, inputs)
            if any(path.is_symlink() for path in outputs):
                raise AdapterError('Output paths must not be symbolic links.')
        contract = _load_contract(_default_contract_path())
        request = json.loads(args.request.read_text(encoding='utf-8'))
        before = _read_update_package(args.snapshot, contract)
        if args.package:
            result = build_update_package(contract, request, before, args.package)
            published_package = args.package
        elif args.validate_package:
            result = validate_update_package(contract, request, before, _read_update_package(args.validate_package, contract))
        elif args.after:
            result = compare_update_after(
                contract, request, before, _read_update_package(args.after, contract),
                candidate_path=args.candidate, readback_evidence_path=args.readback_evidence,
                import_request_id=args.import_request_id, target_url=args.target_url,
            )
        else:
            result = prepare_update(contract, request, before)
        encoded = json.dumps(result, indent=2, allow_nan=False) + '\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='.bank-charge-report-', dir=args.output.parent) as temporary:
                staged = Path(temporary) / 'report.json'
                staged.write_text(encoded, encoding='utf-8')
                os.link(staged, args.output)
    except (AdapterError, ValueError, KeyError, OSError) as exc:
        if published_package is not None:
            published_package.unlink()
        print(json.dumps({'status': 'UPDATE_REVIEW_REJECTED', 'message': str(exc),
                          'failure_class': 'artifact_persistence' if isinstance(exc, OSError) else 'input_validation',
                          'candidate_generated': False, 'fusion_calls': 0}))
        return 1
    print(encoded, end='')
    return int(result['status'] in {'FAIL', 'PENDING', 'BLOCKED'})


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

    intake = sub.add_parser("assess-intake", help="Check business input locally without building a package.")
    _add_common(intake)
    intake.add_argument("--intake", type=Path, required=True)

    update = sub.add_parser("update", help="Prepare or check one snapshot-bound charge-line update.")
    update.add_argument("--request", type=Path, required=True)
    update.add_argument("--snapshot", type=Path, required=True)
    update_mode = update.add_mutually_exclusive_group()
    update_mode.add_argument("--package", type=Path)
    update_mode.add_argument("--validate-package", type=Path)
    update_mode.add_argument("--after", type=Path)
    update.add_argument("--candidate", type=Path)
    update.add_argument("--readback-evidence", type=Path)
    update.add_argument("--import-request-id")
    update.add_argument("--target-url")
    update.add_argument("--output", type=Path)

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
    reconcile_parser.add_argument("--readback-evidence", type=Path)
    reconcile_parser.add_argument("--import-request-id")
    reconcile_parser.add_argument("--target-url")
    return parser.parse_args(argv)


def _command_succeeded(command: str, result: dict[str, Any]) -> bool:
    if command == "assess-intake":
        return result.get("status") == "LOCAL_INPUT_PASS_EXECUTION_BLOCKED"
    if command == "manifest":
        return str(result.get("status", "")).strip().upper() in SUCCESS_STATUSES
    return result.get("status", "PASS") == "PASS"


def _validate_cli_outputs(args: argparse.Namespace) -> None:
    output_names = {"report", "blueprint_output", "preview_output", "requirements_output", "output"}
    if args.command == "update":
        output_names.add("package")
    outputs = [value for key, value in vars(args).items()
               if key in output_names and isinstance(value, Path)]
    inputs = [value for key, value in vars(args).items()
              if key not in output_names and isinstance(value, Path)]
    if not hasattr(args, "contract"):
        inputs.append(_default_contract_path())
    _validate_new_outputs(outputs, inputs)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        # Validate every destination together before reading or writing any output,
        # including failure reports. Never write a failure to a rejected path.
        _validate_cli_outputs(args)
    except (AdapterError, OSError, ValueError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [{"code": "OUTPUT_PATH", "message": str(exc)}]}), file=sys.stderr)
        return 1 if args.command == "update" else 2
    if args.command == "update":
        return _run_update_command(args)
    if args.command == "assess-intake":
        try:
            contract = _load_contract(args.contract)
            intake = _read_json(args.intake)
            if not isinstance(intake, dict):
                raise AdapterError("Business intake must be a JSON object.")
            result = assess_business_intake(contract, intake)
        except (AdapterError, ValueError, OSError) as exc:
            failure = {"status": "INPUT_REJECTED", "message": str(exc), "fusion_calls": 0}
            if args.report:
                _write_json(args.report, failure)
            print(json.dumps(failure))
            return 1
        if args.report:
            _write_json(args.report, result)
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if _command_succeeded(args.command, result) else 1

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
                args.readback_evidence,
                args.import_request_id,
                args.target_url,
            )
        else:
            raise AdapterError(f"Unknown command {args.command!r}.")
        if args.report:
            _write_json(args.report, result)
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if _command_succeeded(args.command, result) else 2
    except (AdapterError, OSError, ValueError) as exc:
        failure = {
            "schemaVersion": SCHEMA_VERSION,
            "status": "FAIL",
            "errors": [{"code": "ADAPTER_ERROR", "message": str(exc)}],
        }
        if getattr(args, "report", None):
            try:
                _write_json(args.report, failure)
            except (AdapterError, OSError):
                # A destination created after preflight must also stay untouched.
                pass
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    # Shared charge-group readers import this module; preserve one runtime and
    # one AdapterError class when the adapter is invoked as a script.
    sys.modules.setdefault("fsm_task_adapter", sys.modules[__name__])
    raise SystemExit(main())
