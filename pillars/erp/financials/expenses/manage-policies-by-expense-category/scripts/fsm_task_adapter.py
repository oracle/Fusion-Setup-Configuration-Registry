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

    def __init__(self, message, *, issues=None):
        super().__init__(message)
        self.issues = list(issues or [])


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


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
    for entity in package["entities"]:
        _nullable_key_fields(entity)
        _derived_date_aliases(entity)
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


def _metadata_fields(node):
    values = {}
    for child in node:
        if list(child):
            continue
        name = child.tag.rsplit('}', 1)[-1]
        if name in values:
            raise AdapterError('Duplicate metadata field: '+name)
        values[name] = child.text or ''
    return values


def _metadata_object_contracts(root: ElementTree.Element) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] != "MigrationProcessBusinessObjectCSVMetadataVORow":
            continue
        values = _metadata_fields(node)
        name = values.get('BusinessObjectShortName', '').strip()
        if not name:
            raise AdapterError('CSV metadata object requires BusinessObjectShortName.')
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
            raise AdapterError('Duplicate metadata attribute for '+name)
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


def _sequence_checked_objects(root, contract, object_contracts):
    """Scope collisions to this task's source-registered transform objects.

    The package also carries one metadata-only definition owned by a different
    task. Preserve and validate it, but do not invent a second transform object.
    """
    profile = _read_json(Path(__file__).resolve().parents[1]/'references/policy-package-metadata.json')
    registered = profile.get('taskBusinessObjects', [])
    aliases = profile.get('metadataOnlyAliases', {})
    names = {entity['name'] for entity in contract['package']['entities']}
    if (not isinstance(registered, list) or len(set(registered)) != len(registered)
            or not isinstance(aliases, dict) or set(registered) & set(aliases)
            or set(registered) | set(aliases) != names
            or profile.get('xmlFileByEntity') != _node_sequence_policy(contract)):
        raise AdapterError('Reviewed task transform-object/alias registration required.')
    selected = [_metadata_fields(node).get('BusinessObjectShortName', '').strip() for node in root.iter()
                if node.tag.rsplit('}', 1)[-1] == 'MigrationProcessMigrationObjectCSVMetadataVORow']
    if len(selected) != len(set(selected)) or set(selected) != set(registered):
        raise AdapterError('Task migration-object registrations differ from the reviewed source.')
    for alias, canonical in aliases.items():
        if (canonical not in registered
                or profile['xmlFileByEntity'][alias] != profile['xmlFileByEntity'][canonical]
                or object_contracts.get(alias) != object_contracts.get(canonical)):
            raise AdapterError('Metadata-only alias differs from its reviewed XML node: '+alias)
    return set(registered)


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
    if not SUCCESS_STATUS.search(metadata["ProcessStatus"]):
        raise AdapterError(
            f"Package process status is not successful: {metadata['ProcessStatus']!r}."
        )
    if not metadata["ProcessEnv"] or not metadata["ProcessRelease"]:
        raise AdapterError("Package metadata must declare ProcessEnv and ProcessRelease.")
    object_contracts = _metadata_object_contracts(root)
    if set(object_contracts) != {entity['name'] for entity in contract['package']['entities']}:
        raise AdapterError('CSV metadata object inventory must exactly match the task descriptor.')
    sequence_groups = _node_sequence_policy(contract)
    sequence_objects = (_sequence_checked_objects(root, contract, object_contracts)
                        if sequence_groups is not None else set())
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
        if sequence_groups is not None and entity['name'] in sequence_objects:
            path_parts = actual["nodePath"].split("/")
            if not actual["nodePath"].startswith("/") or not all(path_parts[1:]) or len(path_parts) % 2 != 1:
                raise AdapterError(f"Invalid paired XML node path for {entity['name']}.")
            # XmlCSVAMImpl scopes its TreeMap by XML file and hierarchy level.
            slot = (sequence_groups[entity["name"]], len(path_parts) // 2, int(actual_node_sequence))
            if slot in sequence_slots:
                raise AdapterError(f"NodeSequence collision in XML file/level: {sequence_slots[slot]} and {entity['name']}.")
            sequence_slots[slot] = entity["name"]
        expected_metadata_types = {field: entity['types'].get(field, '')
                                   for field in entity['headers'] if '.' not in field}
        if actual['types'] != expected_metadata_types:
            raise AdapterError('CSV metadata attribute/type inventory differs for '+entity['name'])
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
        if (str(entity.get("types", {}).get(field) or "string") not in {"string", "date", "decimal", "int"}
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


def _protocol_manifest(
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


def normalized_manifest(contract, path, environment, base_url, template_only):
    return _policy_call('manifest', contract, path, environment, base_url, template_only)


def _policy_call(name, contract, *args):
    import policy_adapter
    try:
        return getattr(policy_adapter, name)(globals(), contract, *args)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        raise AdapterError(str(exc), issues=getattr(exc, 'issues', None)) from exc


def normalize_design(contract, baseline, request, design):
    return _policy_call('normalize', contract, baseline, request, design)


def build_candidate(contract, template, baseline, blueprint, requirements, output):
    return _policy_call('build', contract, template, baseline, blueprint, requirements, output)


def validate_candidate(contract, template, baseline, blueprint, requirements, candidate):
    return _policy_call('validate', contract, template, baseline, blueprint, requirements, candidate)


def determinism_check(contract, template, baseline, blueprint, requirements):
    return _policy_call('determinism', contract, template, baseline, blueprint, requirements)


def reconcile(contract, baseline, candidate, blueprint, requirements, export, historical_proof=None):
    return _policy_call('reconcile', contract, baseline, candidate, blueprint, requirements, export, historical_proof)


def make_rollback(contract, *args):
    return _policy_call('rollback', contract, *args)


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
    reconcile_parser.add_argument("--historical-proof", type=Path,
                                  help="Read-only original validated-preparation proof; never usable for candidate generation or import.")
    return parser.parse_args(argv)


def _command_succeeded(command: str, result: dict[str, Any]) -> bool:
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
                args.historical_proof,
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
        if exc.issues:
            failure['issues'] = exc.issues
        if getattr(args, "report", None):
            _write_json(args.report, failure)
        print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
