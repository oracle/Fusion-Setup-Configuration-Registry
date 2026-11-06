#!/usr/bin/env python3
"""Portable, data-driven FSM task adapter runtime.

This file is copied into a generated Nested task skill.  Task semantics live in
the adjacent e2e-adapter.json descriptor and ora-resource rule plan.  The
runtime performs offline package work only; it never connects to Fusion.

Reading guide: the helpers verify the task contract and FSM ZIP, normalize a
requested calendar design, enforce parent/period date rules, build a candidate,
and reconcile a later export. The CLI orchestrates only these offline steps.
"""

from __future__ import annotations

import argparse
import calendar
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
from urllib.parse import urlsplit
from xml.etree import ElementTree


SCHEMA_VERSION = "fscr-fsm-task-adapter-v1"
MAX_MEMBER_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100
SUCCESS_STATUSES = frozenset({"COMPLETED", "SUCCEEDED", "SUCCESS"})


class AdapterError(ValueError):
    """A safe, user-correctable adapter failure."""


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
        # Fusion exports can vary sequence numbering. Identify each object
        # by its name and validated node path, as Payment Terms does.
        actual_node_sequence = str(actual["nodeSequence"]).strip()
        if not re.fullmatch(r"[1-9][0-9]*", actual_node_sequence):
            raise AdapterError(
                f"Metadata node sequence for {entity['name']} must be a positive integer; "
                f"found {actual_node_sequence!r}."
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
    numeric_constraint = entity.get("numericConstraints", {}).get(field)
    if numeric_constraint:
        try:
            numeric_value = Decimal(str(value).strip())
        except (InvalidOperation, ValueError):
            numeric_value = Decimal("NaN")
        if not numeric_value.is_finite():
            raise AdapterError(
                f"Operation {operation_id} field {entity['name']}.{field} must be a "
                "finite numeric value."
            )
        minimum = numeric_constraint.get("minimum")
        maximum = numeric_constraint.get("maximum")
        if minimum is not None and numeric_value < Decimal(str(minimum)):
            raise AdapterError(
                f"Operation {operation_id} field {entity['name']}.{field} must be "
                f"at least {minimum}."
            )
        if maximum is not None and numeric_value > Decimal(str(maximum)):
            raise AdapterError(
                f"Operation {operation_id} field {entity['name']}.{field} must be "
                f"at most {maximum}."
            )
        exclusive_minimum = numeric_constraint.get("exclusiveMinimum")
        if (
            exclusive_minimum is not None
            and numeric_value <= Decimal(str(exclusive_minimum))
        ):
            raise AdapterError(
                f"Operation {operation_id} field {entity['name']}.{field} must be "
                f"greater than {exclusive_minimum}."
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


# Calendar-specific checks compare real dates and explicit parent-child keys;
# they never infer those rules from row names or display labels.
def _source_calendar_date(value: Any, operation_id: str, field: str) -> date:
    """Parse the two date encodings evidenced by FSM request/export packages."""
    text = str(value).strip()
    for pattern in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    raise AdapterError(
        f"Operation {operation_id} field {field} must use YYYY-MM-DD or the "
        "FSM-exported YYYY/MM/DD date form."
    )


_GENERATED_PERIOD_COUNTS = {
    "4-4-5": 12, "4-5-4": 12, "5-4-4": 12,
    "MONTHLY": 12, "QUARTERLY": 4, "WEEKLY": 52,
}


def _month_period_end(start: date, months: int) -> date:
    """Match CalendarUtil's month increment and inclusive end-date rule."""
    ordinal = start.year * 12 + start.month - 1 + months
    year, month_index = divmod(ordinal, 12)
    month = month_index + 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(start.day, last_day)) - (
        timedelta(days=1) if start.day <= last_day else timedelta()
    )


def _generated_periods(parent: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand the one-year Generate Periods action into explicit child creates."""
    operation_id = parent["id"]
    if parent["action"] != "create" or parent["entity"] != "AP_OTHER_PERIOD_TYPE":
        raise AdapterError(f"Operation {operation_id} can generate periods only for a calendar create.")
    values = parent["values"]
    frequency = str(values.get("PeriodFrequency", "")).strip()
    if frequency not in _GENERATED_PERIOD_COUNTS:
        raise AdapterError(
            f"Operation {operation_id} cannot generate periods for {frequency!r}; "
            "OTHER requires manually defined period rows."
        )
    count = _GENERATED_PERIOD_COUNTS[frequency]
    try:
        supplied_count = int(str(values.get("PeriodsPerYear", "")))
    except ValueError as exc:
        raise AdapterError(f"Operation {operation_id} must supply PeriodsPerYear={count}.") from exc
    if supplied_count != count:
        raise AdapterError(f"Operation {operation_id} requires PeriodsPerYear={count} for {frequency}.")
    start = _source_calendar_date(values.get("StartDate", ""), operation_id, "StartDate")
    year = start.year
    if not 1960 <= year <= 2060:
        raise AdapterError(f"Operation {operation_id} generated PeriodYear must be from 1960 to 2060.")
    name_format = str(values.get("PeriodNameFormat", "")).strip()
    if frequency in {"MONTHLY", "4-4-5", "4-5-4", "5-4-4"} and name_format not in {"MM", "MMM"}:
        raise AdapterError(f"Operation {operation_id} requires PeriodNameFormat MM or MMM for {frequency} generation.")
    if frequency == "QUARTERLY" and name_format != "QUARTER":
        raise AdapterError(f"Operation {operation_id} requires PeriodNameFormat QUARTER for quarterly generation.")
    if frequency == "WEEKLY" and name_format != "WEEK":
        raise AdapterError(f"Operation {operation_id} requires PeriodNameFormat WEEK for weekly generation.")
    calendar_name = str(parent["targetKey"]["CalendarName"])
    calendar_type = str(parent["targetKey"]["CalendarType"])
    rows = []
    current = start
    for number in range(1, count + 1):
        if frequency in {"4-4-5", "4-5-4", "5-4-4"}:
            weeks = int(frequency.split("-")[(number - 1) % 3])
            end = current + timedelta(days=weeks * 7 - 1)
        elif frequency == "WEEKLY":
            end = current + timedelta(days=6)
        else:
            end = _month_period_end(current, 3 if frequency == "QUARTERLY" else 1)
        if frequency == "QUARTERLY":
            prefix = f"Quarter{number}"
        elif frequency == "WEEKLY":
            prefix = f"Week{number}"
        elif name_format == "MM":
            prefix = f"{number:02d}"
        else:
            month = (start.month - 1 + number - 1 + (start.day > 15)) % 12 + 1
            prefix = calendar.month_abbr[month]
        period_name = f"{prefix}-{year % 100:02d}"
        row_values: dict[str, Any] = {
            "AP_OTHER_PERIOD_TYPE.CalendarName": calendar_name,
            "AP_OTHER_PERIOD_TYPE.CalendarType": calendar_type,
            "ApplicationId": 200,
            "PeriodYear": year,
            "EnteredPeriodName": prefix,
            "StartDate": current.isoformat(),
            "EndDate": end.isoformat(),
            "PeriodNum": number,
        }
        if calendar_type == "PAYMENT TERMS":
            row_values["DueDate"] = end.isoformat()
        rows.append({
            "id": f"{operation_id}-PERIOD-{number:02d}",
            "action": "create", "entity": "AP_OTHER_PERIOD_PERIOD",
            "targetKey": {"CalendarName": calendar_name, "CalendarType": calendar_type,
                          "PeriodName": period_name},
            "values": row_values,
            "preserveOtherValues": True, "preserveUnspecifiedRows": True,
        })
        current = end + timedelta(days=1)
    if frequency in {"MONTHLY", "QUARTERLY"}:
        # GL MonthlyYear/QuarterlyYear trims a final excess day for late-month starts.
        last = date.fromisoformat(rows[-1]["values"]["EndDate"])
        if last.month == start.month and last.day >= start.day:
            last -= timedelta(days=last.day - start.day + 1)
            rows[-1]["values"]["EndDate"] = last.isoformat()
            if calendar_type == "PAYMENT TERMS":
                rows[-1]["values"]["DueDate"] = last.isoformat()
    return rows


def _field_values_equal(
    entity: dict[str, Any], field: str, left: Any, right: Any
) -> bool:
    """Compare date fields semantically across export and import encodings."""
    left_text, right_text = str(left).strip(), str(right).strip()
    if str(entity.get("types", {}).get(field, "")).casefold() != "date":
        return left_text == right_text
    if not left_text or not right_text:
        return left_text == right_text
    try:
        return _source_calendar_date(left_text, "field comparison", field) == _source_calendar_date(
            right_text, "field comparison", field
        )
    except AdapterError:
        return left_text == right_text


def _validate_period_semantics(
    entity: dict[str, Any],
    operation: dict[str, Any],
    baseline: PackageData | None,
) -> None:
    """Apply source-backed date and sequence rules to period creates and updates."""
    if entity["name"] != "AP_OTHER_PERIOD_PERIOD" or operation["action"] not in {"create", "update"}:
        return
    operation_id = operation["id"]
    target = _target_tuple(entity, operation["targetKey"])
    baseline_rows = _row_index(baseline, entity) if baseline is not None else {}
    if operation["action"] == "update":
        if baseline is None:
            return
        merged = dict(baseline_rows[target])
    else:
        merged = {
            field: str(operation["targetKey"].get(field, ""))
            for field in entity["headers"]
        }
    merged.update({field: str(value) for field, value in operation["values"].items()})
    if operation["action"] == "create" and any(
        not str(merged.get(field, "")).strip()
        for field in ("StartDate", "EndDate", "PeriodYear", "PeriodNum")
    ):
        return
    start = _source_calendar_date(merged["StartDate"], operation_id, "StartDate")
    end = _source_calendar_date(merged["EndDate"], operation_id, "EndDate")
    if end < start:
        raise AdapterError(
            f"Operation {operation_id} EndDate must be on or after StartDate."
        )
    due_text = str(merged.get("DueDate", "")).strip()
    if merged["CalendarType"] == "PAYMENT TERMS" and not due_text:
        raise AdapterError(
            f"Operation {operation_id} requires DueDate for a PAYMENT TERMS calendar."
        )
    if due_text and _source_calendar_date(due_text, operation_id, "DueDate") < end:
        raise AdapterError(
            f"Operation {operation_id} DueDate must be on or after EndDate."
        )
    # Before import, check for duplicate period numbers and overlapping dates
    # using the final values from all requested creates and updates in memory.


def _validate_calendar_type_semantics(
    entity: dict[str, Any],
    operation: dict[str, Any],
    baseline: PackageData | None,
) -> None:
    """Apply source-backed start/effective-date rules to creates and updates."""
    if entity["name"] != "AP_OTHER_PERIOD_TYPE" or operation["action"] not in {"create", "update"}:
        return
    if operation["action"] == "update" and baseline is None:
        return
    operation_id = operation["id"]
    if operation["action"] == "update":
        before = _row_index(baseline, entity)[_target_tuple(entity, operation["targetKey"])]
        merged = dict(before)
    else:
        merged = {
            field: str(operation["targetKey"].get(field, ""))
            for field in entity["headers"]
        }
    merged.update({field: str(value) for field, value in operation["values"].items()})
    start_text = str(merged.get("StartDate", "")).strip()
    effective_from_text = str(merged.get("EffectiveFrom", "")).strip()
    effective_to_text = str(merged.get("EffectiveTo", "")).strip()
    if operation["action"] == "create" and not (start_text and effective_from_text):
        return
    if start_text and effective_from_text and (
        _source_calendar_date(effective_from_text, operation_id, "EffectiveFrom")
        < _source_calendar_date(start_text, operation_id, "StartDate")
    ):
        raise AdapterError(
            f"Operation {operation_id} EffectiveFrom must be on or after StartDate."
        )
    if effective_from_text and effective_to_text and (
        _source_calendar_date(effective_to_text, operation_id, "EffectiveTo")
        < _source_calendar_date(effective_from_text, operation_id, "EffectiveFrom")
    ):
        raise AdapterError(
            f"Operation {operation_id} EffectiveTo must be on or after EffectiveFrom."
        )


def _validate_period_parent_context(
    entity: dict[str, Any], operation: dict[str, Any]
) -> None:
    """Require child CSV parent references for create and period-value updates."""
    if entity["name"] != "AP_OTHER_PERIOD_PERIOD":
        return
    values = operation["values"]
    if operation["action"] not in {"create", "update"}:
        return
    expected = {
        "AP_OTHER_PERIOD_TYPE.CalendarName": str(operation["targetKey"]["CalendarName"]),
        "AP_OTHER_PERIOD_TYPE.CalendarType": str(operation["targetKey"]["CalendarType"]),
    }
    for field, target_value in expected.items():
        if field not in values:
            raise AdapterError(
                f"Operation {operation['id']} must serialize {field} as immutable "
                "parent-reference context for the child CSV row."
            )
        if str(values[field]) != target_value:
            raise AdapterError(
                f"Operation {operation['id']} parent-reference {field} must equal "
                f"the child target value {target_value!r}."
            )


def _validate_period_parent_row_operations(
    operations: list[dict[str, Any]], baseline: PackageData | None = None
) -> None:
    """Require an explicit parent or a fresh-baseline parent the builder can carry.

    Fusion FSM skips a period row when its CSV parent reference cannot be
    resolved to an AP_OTHER_PERIOD_TYPE row in that same archive.  The dotted
    fields alone are therefore insufficient.
    """
    parent_targets = {
        (
            str(operation["targetKey"]["CalendarName"]),
            str(operation["targetKey"]["CalendarType"]),
        )
        for operation in operations
        if operation["entity"] == "AP_OTHER_PERIOD_TYPE"
        and operation["action"] in {"create", "update"}
    }
    if baseline is not None:
        parent_targets.update(
            (row["CalendarName"], row["CalendarType"])
            for row in baseline.rows["AP_OTHER_PERIOD_TYPE"]
        )
    for operation in operations:
        if (
            operation["entity"] != "AP_OTHER_PERIOD_PERIOD"
            or operation["action"] not in {"create", "update"}
        ):
            continue
        target = operation["targetKey"]
        parent = (str(target["CalendarName"]), str(target["CalendarType"]))
        if parent not in parent_targets:
            raise AdapterError(
                f"Operation {operation['id']} requires a same-archive "
                "AP_OTHER_PERIOD_TYPE create/update row for its exact parent "
                f"{parent!r}; Fusion otherwise skips the child row."
            )


def _validate_period_number_uniqueness(
    contract: dict[str, Any], operations: list[dict[str, Any]], baseline: PackageData | None,
) -> None:
    """Check year/number pairs across retained periods and the requested batch."""
    entity = _entity_map(contract)["AP_OTHER_PERIOD_PERIOD"]
    effective = {
        key: (row, None) for key, row in
        (_row_index(baseline, entity).items() if baseline is not None else [])
    }
    for operation in operations:
        if operation["entity"] != entity["name"]:
            continue
        key = _target_tuple(entity, operation["targetKey"])
        row = dict(effective.get(key, ({}, None))[0])
        row.update(operation["targetKey"])
        row.update(operation["values"])
        effective[key] = (row, operation["id"])
    seen = {}
    for row, operation_id in effective.values():
        if any(str(row.get(field, "")).strip() == "" for field in ("PeriodYear", "PeriodNum")):
            continue  # Required-field validation reports incomplete creates.
        pair = (str(row["CalendarName"]), str(row["CalendarType"]),
                int(row["PeriodYear"]), int(row["PeriodNum"]))
        if pair in seen and (operation_id is not None or seen[pair] is not None):
            owner = operation_id if operation_id is not None else seen[pair]
            raise AdapterError(
                f"Operation {owner} PeriodNum must remain unique within PeriodYear "
                f"{pair[2]} for calendar {pair[0]!r} and type {pair[1]!r}; "
                f"period number {pair[3]} is used more than once."
            )
        seen[pair] = operation_id


def _validate_period_batch_overlaps(
    operations: list[dict[str, Any]], baseline: PackageData | None = None,
) -> None:
    """Check final period ranges after applying every create and update."""
    key_fields = ("CalendarName", "CalendarType", "PeriodName")
    effective = {
        tuple(str(row[field]) for field in key_fields): (dict(row), None)
        for row in (baseline.rows.get("AP_OTHER_PERIOD_PERIOD", [])
                    if baseline is not None else [])
    }
    for operation in operations:
        if operation["entity"] != "AP_OTHER_PERIOD_PERIOD":
            continue
        key = tuple(str(operation["targetKey"][field]) for field in key_fields)
        row = dict(effective.get(key, ({}, None))[0])
        row.update(operation["targetKey"])
        row.update(operation["values"])
        effective[key] = (row, operation["id"])
    periods = []
    for key, (row, operation_id) in effective.items():
        if not str(row.get("StartDate", "")).strip() or not str(row.get("EndDate", "")).strip():
            continue  # Required-field validation reports incomplete rows.
        owner = operation_id or repr(key)
        periods.append((key, operation_id,
                        _source_calendar_date(str(row["StartDate"]), owner, "StartDate"),
                        _source_calendar_date(str(row["EndDate"]), owner, "EndDate")))
    for index, (key, operation_id, start, end) in enumerate(periods):
        for other_key, other_id, other_start, other_end in periods[index + 1:]:
            if key[:2] != other_key[:2] or (operation_id is None and other_id is None):
                continue
            if start <= other_end and other_start <= end:
                owner = operation_id or other_id
                other = (f"requested period {other_id}" if operation_id and other_id
                         else f"retained period {other_key if operation_id else key!r}")
                raise AdapterError(f"Operation {owner} period range overlaps {other}.")


def _validate_requested_period_create_overlaps(operations: list[dict[str, Any]]) -> None:
    """Check create-only batches without a baseline."""
    _validate_period_batch_overlaps([
        operation for operation in operations
        if operation["entity"] == "AP_OTHER_PERIOD_PERIOD" and operation["action"] == "create"
    ])


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
    if "evidenceUnresolvedUpdateOverrides" in design:
        raise AdapterError("Payables Calendars does not support governed update overrides.")
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
        generate_periods = operation.pop("generatePeriods", False)
        if not isinstance(generate_periods, bool):
            raise AdapterError(f"Operation {index} generatePeriods must be true or false.")
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
        if generate_periods:
            generated = _generated_periods(operation)
            parent_key = operation["targetKey"]
            if any(
                item.get("entity") == "AP_OTHER_PERIOD_PERIOD"
                and item.get("targetKey", {}).get("CalendarName") == parent_key["CalendarName"]
                and item.get("targetKey", {}).get("CalendarType") == parent_key["CalendarType"]
                for item in operations
                if isinstance(item, dict)
            ):
                raise AdapterError(
                    f"Operation {operation['id']} cannot combine generated and manually supplied periods for the same calendar."
                )
            normalized_ops.extend(generated)
    warnings = list(design.get("warnings", []))
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
    }
    return blueprint


def _validate_blueprint(
    contract: dict[str, Any],
    blueprint: dict[str, Any],
    baseline: PackageData | None = None,
    *, validate_period_batch: bool = True,
) -> None:
    if "evidenceUnresolvedUpdateOverrides" in blueprint:
        raise AdapterError("Payables Calendars does not support governed update overrides.")
    task = blueprint.get("task")
    if task != {"name": contract["task"]["name"], "code": contract["task"]["code"]}:
        raise AdapterError("Blueprint task identity differs from the adapter contract.")
    operations = blueprint.get("operations")
    if not isinstance(operations, list) or not operations:
        raise AdapterError("Blueprint must contain at least one operation.")
    entities = _entity_map(contract)
    allowed = set(contract["normalization"]["supportedOperations"])
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
        supporting_parent = (
            entity_name == "AP_OTHER_PERIOD_TYPE" and action == "update"
            and baseline is not None
            and any(
                child["entity"] == "AP_OTHER_PERIOD_PERIOD"
                and child["action"] in {"create", "update"}
                and (str(child["targetKey"]["CalendarName"]),
                     str(child["targetKey"]["CalendarType"])) == target_tuple
                for child in operations
            )
        )
        if not isinstance(values, dict) or (not values and not supporting_parent):
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
        # Apply every concrete source-backed deterministic field rule.
        for field in values:
            _validate_field_value(entity, field, values[field], operation_id)
        _validate_period_parent_context(entity, operation)
        if action == "create":
            create_fields = set(entity.get("createFields", {}))
            unproven = (set(target) | set(values)) - create_fields
            if unproven:
                raise AdapterError(
                    f"Operation {operation_id} has no source-backed create contract for "
                    f"fields: {sorted(unproven)}."
                )
        if action in {"update", "end-date"}:
            update_field_contracts = entity.get("updateFields", {})
            update_fields = set(update_field_contracts)
            unproven = set(values) - update_fields
            if unproven:
                raise AdapterError(
                    f"Operation {operation_id} has no source-backed update contract for "
                    f"fields: {sorted(unproven)}."
                )
            validated_update_contracts = [
                update_field_contracts[field]
                for field in values
                if field in update_fields
            ]
            if any(
                item.get("requiresPreserveOtherValues") is True
                for item in validated_update_contracts
            ) and operation.get("preserveOtherValues", True) is not True:
                raise AdapterError(
                    f"Operation {operation_id} requires preserveOtherValues=true for its "
                    "source-backed update contract."
                )
            if any(
                item.get("requiresPreserveUnspecifiedRows") is True
                for item in validated_update_contracts
            ) and operation.get("preserveUnspecifiedRows", True) is not True:
                raise AdapterError(
                    f"Operation {operation_id} requires preserveUnspecifiedRows=true for its "
                    "source-backed update contract."
                )
        for field in values:
            if field in blocked and (
                entity_name, field, blocked[field]["resolver"]
            ) not in satisfied:
                raise AdapterError(
                    f"Operation {operation_id} changes conditionally blocked field "
                    f"{entity_name}.{field}: {blocked[field]['reason']}"
                )
        _validate_period_semantics(entity, operation, baseline)
        _validate_calendar_type_semantics(entity, operation, baseline)
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
    if validate_period_batch:
        _validate_period_number_uniqueness(contract, operations, baseline)
        _validate_period_batch_overlaps(operations, baseline)
    _validate_period_parent_row_operations(operations, baseline)


def _uploaded_operation_values(
    entity: dict[str, Any],
    row: dict[str, str],
    baseline_row: dict[str, str] | None,
    action: str,
) -> dict[str, str]:
    """Keep immutable child-parent context in an uploaded period update.

    The dotted parent fields are package context, rather than fields that a
    customer is changing.  They can therefore be unchanged from the baseline,
    but must remain present when the operation is validated and reserialized.
    """
    preserved_context = (
        {
            "AP_OTHER_PERIOD_TYPE.CalendarName",
            "AP_OTHER_PERIOD_TYPE.CalendarType",
        }
        if entity["name"] == "AP_OTHER_PERIOD_PERIOD"
        else set()
    )
    excluded = set(entity["keyFields"]) | set(entity["auditFields"])
    return {
        field: row[field]
        for field in entity["headers"]
        if field not in excluded
        and (
            (row[field] != "" if action == "create" or baseline_row is None
             else not _field_values_equal(entity, field, row[field], baseline_row[field]))
            or (field in preserved_context and row[field] != "")
        )
    }


def _uploaded_validation_operations(
    operations: list[dict[str, Any]], operation: dict[str, Any]
) -> list[dict[str, Any]]:
    """Include the same-archive parent when validating an uploaded period row."""
    if operation["entity"] != "AP_OTHER_PERIOD_PERIOD":
        if operation["entity"] == "AP_OTHER_PERIOD_TYPE" and not operation.get("values"):
            target = operation["targetKey"]
            children = [child for child in operations
                        if child["entity"] == "AP_OTHER_PERIOD_PERIOD"
                        and child["targetKey"]["CalendarName"] == target["CalendarName"]
                        and child["targetKey"]["CalendarType"] == target["CalendarType"]]
            return [operation, *children]
        return [operation]
    target = operation["targetKey"]
    parents = [
        candidate
        for candidate in operations
        if candidate["entity"] == "AP_OTHER_PERIOD_TYPE"
        and candidate["targetKey"]
        == {
            "CalendarName": target["CalendarName"],
            "CalendarType": target["CalendarType"],
        }
    ]
    return [*parents, operation]


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
    target_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate an exact-task uploaded FSM ZIP without creating or importing it."""
    baseline = _read_package(baseline_path, contract)
    uploaded = _read_package(package_path, contract)
    _validate_uploaded_compatibility(baseline, uploaded, target_context)
    if _schema_fingerprint(contract, baseline) != _schema_fingerprint(contract, uploaded):
        raise AdapterError("Uploaded package schema fingerprint differs from the fresh baseline.")
    operations, descriptions, raw_errors = [], [], []
    for entity in contract["package"]["entities"]:
        baseline_rows, keys = _row_index(baseline, entity), {}
        for number, row in enumerate(uploaded.rows[entity["name"]], start=1):
            target = {field: row[field] for field in entity["keyFields"]}
            key = _target_tuple(entity, target)
            action = "update" if key in baseline_rows else "create"
            values = _uploaded_operation_values(
                entity,
                row,
                baseline_rows.get(key),
                action,
            )
            operation_id = f"UPLOAD-{entity['name']}-{number:03d}"
            if entity["name"] == "AP_OTHER_PERIOD_TYPE" and action == "update" and not values:
                # Only an unchanged header is supporting data. Explicit clears
                # are included in values and follow normal update validation.
                changed = [field for field in entity["headers"]
                           if field not in entity["auditFields"]
                           and not _field_values_equal(entity, field, row[field], baseline_rows[key][field])]
                if changed:
                    raw_errors.append(f"Operation {operation_id} changed supporting parent fields: {changed}.")
            keys.setdefault(key, []).append((number, operation_id))
            audits = [field for field in entity["auditFields"] if row.get(field, "").strip()]
            if audits: raw_errors.append(f"Operation {operation_id} uploaded row must leave audit fields blank: {audits}.")
            operations.append({"id": operation_id, "action": action, "entity": entity["name"], "targetKey": target, "values": values, "preserveOtherValues": True, "preserveUnspecifiedRows": True})
            descriptions.append({"row": number, "operationId": operation_id, "entity": entity["name"], "action": action, "targetKey": target})
        for key, occurrences in keys.items():
            if len(occurrences) > 1:
                rows = [number for number, _ in occurrences]
                raw_errors.extend(f"Operation {operation_id} uploaded row has duplicate target key {key!r} in rows {rows}." for _, operation_id in occurrences)
    if not operations: raise AdapterError("Uploaded package contains no task rows to validate.")
    blueprint = _normalized_blueprint(contract, {"operations": operations, "resolvedScope": {}, "prerequisites": [], "warnings": []})
    errors = list(raw_errors)
    for operation in blueprint["operations"]:
        isolated = dict(blueprint)
        isolated["operations"] = _uploaded_validation_operations(
            blueprint["operations"], operation
        )
        try:
            # An uploaded ZIP is immutable: baseline presence cannot repair it.
            _validate_period_parent_row_operations(isolated["operations"])
            # Validate each row's own fields here; cross-period checks below
            # use the full batch rather than a row with stale sibling dates.
            _validate_blueprint(contract, isolated, baseline, validate_period_batch=False)
        except AdapterError as exc:
            if str(exc) not in errors: errors.append(str(exc))
    # Per-row checks cannot see conflicts between separately valid child rows.
    # Validate the complete immutable upload as well as each row's context.
    try:
        _validate_period_parent_row_operations(blueprint["operations"])
        _validate_blueprint(contract, blueprint, baseline)
    except AdapterError as exc:
        if str(exc) not in errors:
            errors.append(str(exc))
    for item in descriptions:
        item["errors"] = [error for error in errors if item["operationId"] in error]
        item["status"] = "FAIL" if item["errors"] else "PASS"
    return {"schemaVersion": SCHEMA_VERSION, "status": "PASS" if not errors else "FAIL", "task": contract["task"], "uploadedPackageSha256": uploaded.archive_sha256, "baselineSha256": baseline.archive_sha256, "notImported": True, "candidateCreated": False, "rowResults": descriptions, "errors": errors}


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
        "requirementCount": len(requirements),
    }
    return blueprint, preview, requirements


def _supporting_parent_keys(
    contract: dict[str, Any], blueprint: dict[str, Any]
) -> set[tuple[str, ...]]:
    """Parents needed by children but not supplied by explicit header operations."""
    parent = _entity_map(contract)['AP_OTHER_PERIOD_TYPE']
    explicit = {
        _target_tuple(parent, operation["targetKey"])
        for operation in blueprint["operations"]
        if operation["entity"] == parent["name"]
        and operation["action"] in {"create", "update"}
    }
    required = {
        tuple(str(operation["targetKey"][field]) for field in ('CalendarName', 'CalendarType'))
        for operation in blueprint["operations"]
        if operation["entity"] == 'AP_OTHER_PERIOD_PERIOD'
        and operation["action"] in {"create", "update"}
    }
    return required - explicit


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
        # The setup export represents dates as YYYY/MM/DD, while Fusion's
        # import endpoint requires ISO YYYY-MM-DD values.  Update rows retain
        # their untouched baseline values, so normalize every nonblank date
        # field before serializing the complete target row.
        for field in entity["headers"]:
            if str(entity.get("types", {}).get(field, "")).casefold() != "date":
                continue
            if not str(row.get(field, "")).strip():
                continue
            row[field] = _source_calendar_date(
                row[field], "candidate serialization", field
            ).isoformat()
        for field in entity["auditFields"]:
            row[field] = ""
        output[entity["name"]].append(row)
    # Carry same-archive parent context without changing its business values.
    parent_entity = entities['AP_OTHER_PERIOD_TYPE']
    baseline_parents = _row_index(baseline, parent_entity)
    for key in sorted(_supporting_parent_keys(contract, blueprint)):
        if key not in baseline_parents:
            raise AdapterError(
                f"Child create/update parent {parent_entity['name']} {key!r} "
                "does not exist in the fresh current export."
            )
        row = dict(baseline_parents[key])
        # Preserve dates while converting the export encoding to import ISO dates.
        for field in parent_entity["headers"]:
            if (str(parent_entity.get("types", {}).get(field, "")).casefold() == "date"
                    and str(row.get(field, "")).strip()):
                row[field] = _source_calendar_date(
                    row[field], "supporting parent serialization", field
                ).isoformat()
        for field in parent_entity["auditFields"]:
            row[field] = ""
        output[parent_entity["name"]].append(row)
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
    supporting_parents = _supporting_parent_keys(contract, blueprint)
    parent_entity = entities['AP_OTHER_PERIOD_TYPE']
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
            if not _field_values_equal(entity, field, row[field], value):
                issues.append(
                    {"code": "VALUE_MISMATCH", "message": f"{entity['name']} {key!r} {field} is {row[field]!r}, expected {str(value)!r}."}
                )
        if operation.get("preserveOtherValues", True) and operation["action"] == "update":
            allowed = set(operation["values"]) | set(entity["auditFields"])
            for field in entity["headers"]:
                if field not in allowed and not _field_values_equal(entity, field, row[field], before[field]):
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
            if identity not in expected_targets and not (
                entity["name"] == parent_entity["name"]
                and identity[1] in supporting_parents
            ):
                issues.append(
                    {"code": "UNEXPECTED_ROW", "message": f"Candidate contains unrequested {entity['name']} row {identity[1]!r}."}
                )
    candidate_parents = _row_index(candidate, parent_entity)
    baseline_parents = _row_index(baseline, parent_entity)
    for key in sorted(supporting_parents):
        row, before = candidate_parents.get(key), baseline_parents.get(key)
        if row is None:
            issues.append({"code": "MISSING_PARENT", "message":
                           f"Candidate lacks required parent {parent_entity['name']} {key!r}."})
            continue
        if before is None:
            issues.append({"code": "MISSING_PARENT_BASELINE", "message":
                           f"Fresh baseline lacks parent {parent_entity['name']} {key!r}."})
            continue
        for field in parent_entity["headers"]:
            if field in parent_entity["auditFields"]:
                if row[field] != "":
                    issues.append({"code": "AUDIT_FIELD_POPULATED", "message":
                                   f"Supporting parent {key!r} audit field {field} is not blank."})
            elif not _field_values_equal(parent_entity, field, row[field], before[field]):
                issues.append({"code": "PARENT_ROW_CHANGED", "message":
                               f"Supporting parent {key!r} changed {field}."})
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
                        not _field_values_equal(entity, field, candidate_row[field], before[field])
                        or not _field_values_equal(entity, field, persisted_row[field], before[field])
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
