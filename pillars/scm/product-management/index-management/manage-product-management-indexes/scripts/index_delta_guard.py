#!/usr/bin/env python3
"""Validate an index delta and captured Data Loader rows before approval."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from index_attribute_contract import (AttributeContractError, captured_rows, matches_selectors,
                                      selectors, validate_post, resolve_requested_removal, backend_id)


class DeltaGuardError(ValueError):
    """Raised when a calculated index delta is missing or unsafe to use."""


def archive_records(path: Path, expected_sha256: str) -> list[dict]:
    """Read one snapshot of Core's immutable ZIP, bound to its preflight digest.

    This is task-specific row validation only. Core owns source conversion,
    preflight-envelope verification, approval and upload integrity checks.
    """
    if (not isinstance(expected_sha256, str) or len(expected_sha256) != 64
            or any(c not in "0123456789abcdef" for c in expected_sha256)):
        raise DeltaGuardError("The Core preflight archive SHA-256 is required.")
    try:
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != expected_sha256:
            raise DeltaGuardError("The prepared archive differs from Core's preflight digest.")
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            members = [m for m in archive.infolist()
                       if not any(p.casefold() in {"_macosx", "__macosx"}
                                  for p in m.filename.split("/"))]
            if (len(members) != 1 or members[0].filename !=
                    "productManagementESIndexedAttributes.dat"):
                raise DeltaGuardError("The prepared ZIP must contain one indexed-attributes DAT.")
            lines = archive.read(members[0]).decode("utf-8-sig").splitlines()
    except (OSError, zipfile.BadZipFile, UnicodeDecodeError, RuntimeError) as error:
        raise DeltaGuardError("Unable to read the prepared indexed-attributes ZIP.") from error
    headers = None
    values = []
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) < 3 or parts[1] != "productManagementESIndexedAttributes":
            raise DeltaGuardError("The prepared DAT targets another business object.")
        if parts[0] == "METADATA":
            if headers is not None:
                raise DeltaGuardError("The prepared DAT contains duplicate metadata sections.")
            headers = parts[2:]
            if (any(not h or h != h.strip() for h in headers)
                    or len(set(headers)) != len(headers) or "RestAction" not in headers):
                raise DeltaGuardError("The prepared DAT headers are malformed.")
            continue
        if (headers is None or parts[0] not in {"MERGE", "DELETE"}
                or len(parts) != len(headers) + 2):
            raise DeltaGuardError("The prepared DAT has a malformed data row.")
        action = parts[2:][headers.index("RestAction")]
        if (action not in {"POST", "DELETE"}
                or (parts[0] == "DELETE") != (action == "DELETE")):
            raise DeltaGuardError("The DAT directive differs from RestAction.")
        values.append(parts[2:])
    if headers is None or not values:
        raise DeltaGuardError("The prepared DAT has no data rows.")
    return [{"sections": [{"discriminator": "productManagementESIndexedAttributes",
                            "headers": headers, "rows": values}]}]


def _read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise DeltaGuardError(f"Unable to read {label}.") from error
    if not isinstance(value, dict):
        raise DeltaGuardError(f"{label} must be a JSON object.")
    return value


def _nonblank(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DeltaGuardError(f"{field} must be one nonblank string.")
    return value.strip()


def _rows(value: object, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise DeltaGuardError(f"{field} must be an array of objects.")
    return value


def _identity(row: dict[str, Any], label: str) -> tuple[str, str, str]:
    return tuple(_nonblank(row.get(field), f"{label} {field}") for field in
                 ("attribute_code", "group_code", "object_code"))


def _subtype(row: dict[str, Any]) -> str:
    value = row.get("object_sub_type_code")
    if value in (None, ""):
        return ""
    return _nonblank(value, "ObjectSubTypeCode")


def _present(identity, existing, subtype: str | None = None) -> bool:
    matches = [row for row in existing if _identity(row, "existing identity") == identity]
    if subtype is None:
        # A resolved record without a subtype uses the three-code comparison.
        return bool(matches)
    if any("object_sub_type_code" not in row for row in matches):
        raise DeltaGuardError("Existing ObjectSubTypeCode evidence is missing for a scoped addition.")
    return any(_subtype(row) == subtype for row in matches)


def validate_readback(canonical: str, additions: list, removals: list, response: dict) -> dict:
    """Verify submitted changes using a complete core-retrieved index response."""
    _nonblank(canonical, "canonical_index_name")
    if (not isinstance(response, dict) or not isinstance(response.get("items"), list)
            or response.get("hasMore") is True):
        raise DeltaGuardError("Readback must contain a complete items response.")
    existing = []
    for item in response["items"]:
        if not isinstance(item, dict) or item.get("IndexName") != canonical:
            raise DeltaGuardError("Readback contains another index or an invalid row.")
        row = {key: item.get(field) for key, field in (
            ("attribute_code", "AttributeCode"), ("group_code", "GroupCode"),
            ("object_code", "ObjectCode"), ("attribute_id", "AttributeId"))}
        if "ObjectSubTypeCode" in item:
            row["object_sub_type_code"] = item["ObjectSubTypeCode"]
        _identity(row, "readback identity")
        existing.append(row)
    for row in _rows(additions, "submitted additions"):
        if not _present(_identity(row, "submitted addition"), existing, _subtype(row) or None):
            raise DeltaGuardError("Readback is missing a submitted POST identity or ObjectSubTypeCode.")
    for row in _rows(removals, "submitted removals"):
        identifier = _nonblank(row.get("attribute_id"), "submitted DELETE AttributeId")
        if any(item["attribute_id"] in (None, "") for item in existing):
            raise DeltaGuardError("Readback is missing AttributeId evidence for DELETE verification.")
        if any(str(item["attribute_id"]) == identifier for item in existing):
            raise DeltaGuardError("Readback retains a submitted DELETE AttributeId.")
    return {"canonical_index_name": canonical, "readback_verified": True}


def _request_digest(request: dict[str, Any]) -> str:
    encoded = json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_delta(
    request: dict[str, Any], delta: dict[str, Any], *, require_data_loader: bool,
    records: list | None = None,
    create_contract: dict | None = None,
) -> dict[str, Any]:
    """Validate the delta evidence required before loader artifact preparation."""

    canonical = _nonblank(request.get("canonical_index_name"), "canonical_index_name")
    if delta.get("schema_version") != "1.0":
        raise DeltaGuardError("index_attribute_delta must be a schema_version 1.0 object.")
    if _nonblank(delta.get("canonical_index_name"), "delta canonical_index_name") != canonical:
        raise DeltaGuardError("The delta belongs to a different canonical index.")
    if delta.get("environment") != request.get("environment"):
        raise DeltaGuardError("The delta was calculated for a different environment.")
    if delta.get("request_sha256") != _request_digest(request):
        raise DeltaGuardError("The delta does not match the current single-index request.")

    additions = _rows(delta.get("attributes_to_add"), "attributes_to_add")
    removals = _rows(delta.get("attributes_to_remove"), "attributes_to_remove")
    resolved = _rows(delta.get("resolved_requested_additions"), "resolved_requested_additions")
    seeded = _rows(delta.get("seeded_identities"), "seeded_identities")
    existing = _rows(delta.get("existing_identities"), "existing_identities")
    validated_seeded = _rows(delta.get("validated_seeded_additions"), "validated_seeded_additions")
    requested_additions = _rows(request.get("attributes_to_add"), "request attributes_to_add")
    requested_removals = _rows(request.get("attributes_to_remove"), "request attributes_to_remove")
    resolved_removals = _rows(delta.get("resolved_requested_removals", []), "resolved_requested_removals")
    if len(resolved_removals) != len(requested_removals):
        raise DeltaGuardError("Every requested removal must have one resolved identity; refresh legacy removal evidence.")
    if len(resolved) != len(requested_additions):
        raise DeltaGuardError("Every requested addition must have one resolved identity.")
    resolved_ids: list[tuple[str, str, str]] = []
    resolved_subtypes = {}
    for index, (source, target) in enumerate(zip(requested_additions, resolved)):
        if target.get("request_index") != index:
            raise DeltaGuardError("Resolved addition order does not match the request.")
        record = {"".join(part.title() for part in key.split("_")): value
                  for key, value in target.items()}
        if not selectors(source, "attribute") or not matches_selectors(source, record):
            raise DeltaGuardError("Resolved addition identity differs from the request.")
        resolved_ids.append(_identity(target, "resolved addition"))
        if selectors(source, "object_sub_type"):
            _nonblank(target.get("object_sub_type_code"), "resolved ObjectSubTypeCode")
        code = _subtype(target)
        if code:
            identity = resolved_ids[-1]
            if identity in resolved_subtypes and resolved_subtypes[identity] != code:
                raise DeltaGuardError("Conflicting object subtypes for one addition identity.")
            resolved_subtypes[identity] = code
    seeded_ids = [_identity(row, "seeded identity") for row in seeded]
    existing_ids = [_identity(row, "existing identity") for row in existing]
    existing_keys = [(*_identity(row, "existing identity"), _subtype(row)) for row in existing]
    if len(set(seeded_ids)) != len(seeded_ids) or len(set(existing_keys)) != len(existing_keys):
        raise DeltaGuardError("Seeded or existing identities contain duplicates.")
    validated_seeded_ids = [_identity(row, "validated seeded addition") for row in validated_seeded]
    if len(set(validated_seeded_ids)) != len(validated_seeded_ids) or set(validated_seeded_ids) != (
        set(seeded_ids) - set(existing_ids)
    ):
        raise DeltaGuardError("Validated seeded additions do not match missing seeded identities.")
    expected_additions = (set(seeded_ids) - set(existing_ids)) | {
        identity for identity in resolved_ids
        if not _present(identity, existing, resolved_subtypes.get(identity))
    }
    actual_additions = [_identity(row, "addition") for row in additions]
    if len(set(actual_additions)) != len(actual_additions) or set(actual_additions) != expected_additions:
        raise DeltaGuardError("POST rows do not equal the calculated addition delta.")
    source_by_identity: dict[tuple[str, str, str], tuple[str, str, str]] = {}
    source_subtypes: dict[tuple[str, str, str], str] = {}
    for source_row in validated_seeded + resolved:
        identity = _identity(source_row, "validated addition source")
        names = tuple(_nonblank(source_row.get(field), f"validated source {field}") for field in
                      ("attribute_name", "group_name", "object_name"))
        if identity in source_by_identity and source_by_identity[identity] != names:
            raise DeltaGuardError("Validated sources disagree on one addition identity.")
        source_by_identity[identity] = names
        subtype = _subtype(source_row)
        if identity in source_subtypes and source_subtypes[identity] != subtype:
            raise DeltaGuardError("Validated sources disagree on ObjectSubTypeCode.")
        source_subtypes[identity] = subtype
    if len(removals) != len(requested_removals):
        raise DeltaGuardError("DELETE rows do not match the requested removals.")
    data_loader_required = delta.get("data_loader_required")
    if not isinstance(data_loader_required, bool):
        raise DeltaGuardError("data_loader_required must be boolean.")
    if data_loader_required != bool(additions or removals):
        raise DeltaGuardError("data_loader_required must match the persisted change rows.")
    if require_data_loader and not data_loader_required:
        raise DeltaGuardError("No calculated Data Loader change set is available for preparation.")

    for row in additions:
        subtype = source_subtypes[_identity(row, "addition")]
        if _subtype(row) != subtype:
            raise DeltaGuardError("POST ObjectSubTypeCode differs from validated metadata.")
        if row.get("rest_action") != "POST":
            raise DeltaGuardError("Every calculated addition must use RestAction POST.")
        for field in ("attribute_code", "group_code", "object_code"):
            _nonblank(row.get(field), f"addition {field}")
        if row.get("attribute_id") not in (None, ""):
            raise DeltaGuardError("A calculated addition must leave attribute_id blank.")
        _nonblank(row.get("attribute_name"), "addition attribute_name")
        _nonblank(row.get("group_name"), "addition group_name")
        _nonblank(row.get("object_name"), "addition object_name")
        names = tuple(row[field] for field in ("attribute_name", "group_name", "object_name"))
        if names != source_by_identity[_identity(row, "addition")]:
            raise DeltaGuardError("POST row names differ from the validated source.")
    removal_ids = set()
    existing_response = {"items": [
        {"IndexName": canonical} | {
            "".join(part.title() for part in key.split("_")): value
            for key, value in item.items()}
        for item in existing], "hasMore": False}
    for index, (source, row, resolved_removal) in enumerate(zip(requested_removals, removals, resolved_removals)):
        if row.get("rest_action") != "DELETE":
            raise DeltaGuardError("Every calculated removal must use RestAction DELETE.")
        _nonblank(row.get("attribute_id"), "removal attribute_id")
        if row.get("request_index") != index or resolved_removal.get("request_index") != index:
            raise DeltaGuardError("DELETE row order does not match the request.")
        resolution = resolve_requested_removal(
            source, canonical, existing_response,
            scope_confirmed=resolved_removal.get("scope_confirmed") is True)
        if resolution["status"] != "removal_resolved":
            raise DeltaGuardError("Removal scope requires candidate confirmation.")
        candidate = resolution["candidate"]
        for field in ("attribute_name", "group_name", "object_name", "attribute_code",
                      "group_code", "object_code", "object_sub_type_code", "object_sub_type_name"):
            key = "".join(part.title() for part in field.split("_"))
            expected = candidate.get(key) or ""
            if any((evidence.get(field) or "") != expected for evidence in (row, resolved_removal)):
                raise DeltaGuardError(f"DELETE {field} differs from the resolved backend record.")
        identifier = backend_id(candidate.get("AttributeId"))
        if any(backend_id(evidence.get("attribute_id")) != identifier for evidence in (row, resolved_removal)):
            raise DeltaGuardError("DELETE row does not match one existing backend record.")
        if identifier in removal_ids:
            raise DeltaGuardError("Duplicate DELETE backend AttributeId.")
        # Compare the original resolved addition requirements, including those
        # already satisfied by the pre-load snapshot, not only generated POSTs.
        # An unscoped addition uses triplet matching; a resolved subtype narrows
        # the requirement even when the user did not explicitly supply it.
        for addition in resolved:
            if (_identity(addition, "resolved addition") == _identity(row, "removal")
                    and (not _subtype(addition) or _subtype(addition) == _subtype(row))):
                raise DeltaGuardError(
                    f"Conflicting addition request {addition['request_index']} and removal request {index}: "
                    "the resolved attribute scopes overlap. Choose add or remove before preparing the load."
                )
        removal_ids.add(identifier)

    rows = None
    if records is not None:
        rows = captured_rows(records)
        if additions and create_contract is None:
            raise DeltaGuardError("Captured POST validation requires the live create contract.")
    if rows is not None:
        expected = additions + removals
        if len(rows) != len(expected):
            raise DeltaGuardError("Captured rows do not match the calculated delta.")
        for row, target in zip(rows, expected):
            if row.get("IndexName") != canonical:
                raise DeltaGuardError("The prepared row contains another index.")
            if row.get("RestAction") != target["rest_action"]:
                raise DeltaGuardError("Prepared row actions do not match the delta.")
            fields = ("AttributeName", "GroupName", "ObjectName", "AttributeId")
            keys = ("attribute_name", "group_name", "object_name", "attribute_id")
            for field, key in zip(fields, keys):
                if (row.get(field) or "") != (target.get(key) or ""):
                    raise DeltaGuardError("Prepared rows do not match the validated names or ID.")
            if row["RestAction"] == "DELETE":
                for field, key in (("AttributeCode", "attribute_code"),
                                   ("GroupCode", "group_code"), ("ObjectCode", "object_code"),
                                   ("ObjectSubTypeCode", "object_sub_type_code"),
                                   ("ObjectSubTypeName", "object_sub_type_name")):
                    # Some registered DELETE templates contain only names and ID.
                    # Any supplied optional identity value must still agree.
                    if row.get(field) not in (None, "") and row[field] != target.get(key):
                        raise DeltaGuardError(f"DELETE {field} differs from validated metadata.")
            if row["RestAction"] == "POST":
                if (row.get("ObjectSubTypeCode") or "") != (target.get("object_sub_type_code") or ""):
                    raise DeltaGuardError("POST ObjectSubTypeCode differs from validated metadata.")
                for field, key in (("AttributeCode", "attribute_code"),
                                   ("GroupCode", "group_code"), ("ObjectCode", "object_code")):
                    if row.get(field) != target[key]:
                        raise DeltaGuardError(f"POST {field} differs from validated metadata.")
                if create_contract is not None:
                    resolved_row = {"IndexName": canonical} | {
                        "".join(part.title() for part in key.split("_")): value
                        for key, value in target.items()}
                    validate_post(row, resolved_row, create_contract)

    return {
        "canonical_index_name": canonical,
        "addition_count": len(additions),
        "removal_count": len(removals),
        "data_loader_required": data_loader_required,
        "request_sha256": _request_digest(request),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdin", action="store_true", help="Read request, delta, records and create_contract from one in-memory JSON envelope.")
    parser.add_argument("--captured", action="store_true", help="Require normalized artifact records for an offline pre-approval check (with --stdin).")
    parser.add_argument("--archive", type=Path, help="Exact immutable ZIP prepared by Core Data Loader (with --stdin).")
    parser.add_argument("--archive-sha256", help="Exact archiveSha256 returned by Core preflight; required with --archive.")
    parser.add_argument("--readback", action="store_true", help="Verify submitted delta against a complete readback response (with --stdin).")
    parser.add_argument("--request", type=Path)
    parser.add_argument("--delta", type=Path)
    parser.add_argument(
        "--require-data-loader",
        action="store_true",
        help="Block unless the calculated delta has at least one Data Loader change row.",
    )
    args = parser.parse_args(argv)
    try:
        if bool(args.archive) != bool(args.archive_sha256):
            raise DeltaGuardError("--archive and --archive-sha256 must be supplied together.")
        if args.archive and (not args.stdin or args.captured or args.readback):
            raise DeltaGuardError("--archive requires --stdin and cannot be combined with --captured or --readback.")
        if (args.captured or args.readback) and not args.stdin:
            raise DeltaGuardError("--captured and --readback require --stdin.")
        if args.readback and (args.captured or args.require_data_loader):
            raise DeltaGuardError("Readback is separate from pre-approval validation.")
        if args.stdin:
            if args.request or args.delta:
                raise DeltaGuardError("--stdin cannot be combined with file inputs.")
            data = json.load(sys.stdin)
            if not isinstance(data, dict) or not isinstance(data.get("request"), dict) or not isinstance(data.get("delta"), dict):
                raise DeltaGuardError("Envelope requires request and delta objects.")
            if args.archive:
                if "records" in data:
                    raise DeltaGuardError("Archive validation cannot accept independent records.")
                data["records"] = archive_records(args.archive, args.archive_sha256)
            if args.readback:
                canonical = data["request"].get("canonical_index_name")
                submitted = data["delta"]
                if (submitted.get("canonical_index_name") != canonical
                        or submitted.get("environment") != data["request"].get("environment")
                        or submitted.get("request_sha256") != _request_digest(data["request"])):
                    raise DeltaGuardError("Readback delta differs from the submitted request context.")
                print(json.dumps(validate_readback(canonical, submitted.get("attributes_to_add"),
                                                  submitted.get("attributes_to_remove"), data.get("readback")),
                                 sort_keys=True))
                return 0
            if args.captured and not isinstance(data.get("records"), list):
                raise DeltaGuardError("Pre-approval check requires normalized artifact records.")
            result = validate_delta(data["request"], data["delta"],
                                    require_data_loader=args.require_data_loader,
                                    records=data.get("records"), create_contract=data.get("create_contract"))
            # Approval and preflight persistence remain owned by Core.
            result.pop("request_sha256", None)
            if args.archive:
                result["archive_sha256"] = args.archive_sha256
            print(json.dumps(result, sort_keys=True))
        else:
            if not args.request or not args.delta:
                raise DeltaGuardError("Use --stdin for live work, or --request and --delta for offline checks.")
            request = _read_object(args.request, "single-index request")
            delta = _read_object(args.delta, "index_attribute_delta")
            print(json.dumps(validate_delta(request, delta, require_data_loader=args.require_data_loader), sort_keys=True))
    except (DeltaGuardError, AttributeContractError, json.JSONDecodeError) as error:
        print(f"Index delta guard blocked: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
