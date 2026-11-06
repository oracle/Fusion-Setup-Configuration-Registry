#!/usr/bin/env python3
"""Validate an Item Import ZIP against a current-template-derived contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath


def validate_contract(contract: object) -> dict:
    """Require the template dimensions needed by every archive check."""
    if not isinstance(contract, dict):
        raise ValueError("contract must be an object")
    members = contract.get("members")
    if not isinstance(members, list) or not members:
        raise ValueError("contract.members must be a non-empty list")
    for entry in members:
        if not isinstance(entry, dict):
            raise ValueError("each contract member must be an object")
        field_count = entry.get("field_count")
        if type(field_count) is not int or field_count <= 0:
            raise ValueError("each contract member requires a positive integer field_count")
        batch_index = entry.get("batch_id_index")
        if type(batch_index) is not int or not 0 <= batch_index < field_count:
            raise ValueError("each contract member requires batch_id_index within its field_count")
        if "header_fields" in entry:
            header = entry["header_fields"]
            if (
                not isinstance(header, list)
                or len(header) != field_count
                or any(not isinstance(value, str) or not value.strip() for value in header)
            ):
                raise ValueError("header_fields must contain one nonblank string per field")
    names = [entry.get("name") for entry in members]
    if any(not isinstance(name, str) or not name.strip() for name in names):
        raise ValueError("each contract member requires a name")
    if len(names) != len(set(names)):
        raise ValueError("contract member names must be unique")
    return contract


def load_contract(path: Path) -> dict:
    return validate_contract(json.loads(path.read_text(encoding="utf-8")))


def validate_archive(archive: Path, contract: dict) -> dict:
    contract = validate_contract(contract)
    issues: list[dict[str, str]] = []
    expected = {entry["name"]: entry for entry in contract["members"]}
    expected_order = list(expected)
    batch_ids: set[str] = set()

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        if not names:
            issues.append({"code": "empty_archive", "message": "archive has no members"})
        if len(names) != len(set(names)):
            issues.append({"code": "duplicate_member", "message": "archive contains duplicate members"})

        for name in names:
            pure = PurePosixPath(name)
            if pure.name != name or pure.is_absolute() or ".." in pure.parts:
                issues.append({"code": "unsafe_member", "message": f"unsafe member: {name}"})
            if name not in expected:
                issues.append({"code": "unexpected_member", "message": f"unexpected member: {name}"})

        for name in expected_order:
            if name not in names:
                issues.append({"code": "missing_member", "message": f"required CSV member is missing: {name}"})
        if names != expected_order:
            issues.append({"code": "member_order", "message": "members do not follow the current template order"})

        for name in names:
            rule = expected.get(name)
            if rule is None:
                continue
            try:
                text = bundle.read(name).decode(contract.get("encoding", "utf-8-sig"))
            except UnicodeDecodeError:
                issues.append({"code": "encoding", "message": f"invalid encoding: {name}"})
                continue
            try:
                rows = list(csv.reader(io.StringIO(text, newline=""), strict=True))
            except csv.Error:
                issues.append({
                    "code": "csv_format",
                    "message": (
                        f"invalid CSV syntax or field exceeds parser limit "
                        f"({csv.field_size_limit()} characters): {name}"
                    ),
                })
                continue
            if not any(any(value.strip() for value in row) for row in rows):
                issues.append({"code": "empty_member", "message": f"CSV member has no records: {name}"})
                continue
            for row_number, row in enumerate(rows, 1):
                field_count = rule["field_count"]
                if len(row) != field_count:
                    issues.append({"code": "field_count", "message": f"{name} row {row_number}: expected {field_count}, found {len(row)}"})
                header = rule.get("header_fields")
                if row_number == 1 and isinstance(header, list) and row == header:
                    issues.append({"code": "header_row", "message": f"header row found in {name}"})
                batch_index = rule["batch_id_index"]
                if batch_index >= len(row) or not row[batch_index].isdigit():
                    issues.append({"code": "batch_id", "message": f"invalid Batch ID in {name} row {row_number}"})
                else:
                    batch_ids.add(row[batch_index])

    if len(batch_ids) != 1:
        issues.append({"code": "batch_id_consistency", "message": "archive must contain one numeric Batch ID"})
    return {
        "status": "ready" if not issues else "failed",
        "archive": archive.name,
        "sha256": digest,
        "member_count": len(names),
        "batch_id": next(iter(batch_ids)) if len(batch_ids) == 1 else None,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = validate_archive(args.archive.resolve(), load_contract(args.contract.resolve()))
    except (OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        result = {"status": "failed", "issues": [{"code": "input_validation", "message": str(exc)}]}
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if result["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
