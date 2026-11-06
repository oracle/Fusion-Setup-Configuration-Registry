#!/usr/bin/env python3
"""Resolve index attributes and validate captured loader rows, entirely in memory."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

BUSINESS_OBJECT = "productManagementESIndexedAttributes"
CODE_FIELDS = ("IndexName", "AttributeCode", "GroupCode", "ObjectCode")
NAME_FIELDS = ("AttributeName", "GroupName", "ObjectName")


class AttributeContractError(ValueError):
    pass


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def selectors(request: dict, dimension: str) -> list[tuple[str, str]]:
    """Generic selectors accept either; explicit name/code pairs must agree."""
    result = []
    for suffix, kind in (("", "either"), ("_name", "name"), ("_code", "code")):
        snake = dimension + suffix
        pascal = "".join(part.title() for part in dimension.split("_")) + (suffix[1:].title() if suffix else "")
        for key in (snake, pascal):
            if key in request and request[key] not in (None, ""):
                if not text(request[key]):
                    raise AttributeContractError(f"{key} must be nonblank text.")
                result.append((kind, text(request[key]).casefold()))
    return result


def matches_selectors(request: dict, record: dict) -> bool:
    for dimension in ("attribute", "group", "object", "object_sub_type"):
        prefix = "".join(part.title() for part in dimension.split("_"))
        for kind, value in selectors(request, dimension):
            fields = ([prefix + "Name"] if kind == "name" else
                      [prefix + "Code"] if kind == "code" else
                      [prefix + "Name", prefix + "Code"])
            if value not in {text(record.get(field)).casefold() for field in fields}:
                return False
    return True


def resolve_attribute(request: dict, canonical_index: str, available: dict,
                      *, scope_confirmed: bool = False) -> dict:
    if not text(canonical_index) or not isinstance(request, dict):
        raise AttributeContractError("A canonical index and attribute request are required.")
    if not selectors(request, "attribute"):
        raise AttributeContractError("Supply an attribute name or code.")
    if not isinstance(available, dict) or not isinstance(available.get("items"), list):
        raise AttributeContractError("Available-attribute metadata must contain items.")
    if available.get("hasMore") is True:
        raise AttributeContractError("Available-attribute metadata is incomplete.")
    # All supplied fields are AND constraints, including explicit name/code pairs.
    candidates = [r for r in available["items"] if isinstance(r, dict)
                  and text(r.get("IndexName")).casefold() == canonical_index.casefold()
                  and matches_selectors(request, r)]
    if len(candidates) != 1:
        raise AttributeContractError("Attribute scope must resolve to exactly one metadata record.")
    candidate = candidates[0]
    if any(not text(candidate.get(k)) for k in CODE_FIELDS + NAME_FIELDS):
        raise AttributeContractError("Resolved metadata has an incomplete identity.")
    if candidate["IndexName"] != canonical_index:
        raise AttributeContractError("Resolved metadata does not preserve the canonical index.")
    incomplete = any(not selectors(request, d) for d in ("group", "object"))
    if incomplete and not scope_confirmed:
        return {"status": "candidate_confirmation_required", "candidate": candidate}
    row = {k: candidate[k] for k in CODE_FIELDS + NAME_FIELDS}
    subtype = candidate.get("ObjectSubTypeCode")
    if selectors(request, "object_sub_type") and not text(subtype):
        raise AttributeContractError("Supplied object subtype requires a resolved ObjectSubTypeCode.")
    if subtype not in (None, ""):
        if not text(subtype):
            raise AttributeContractError("Resolved ObjectSubTypeCode must be nonblank text.")
        row["ObjectSubTypeCode"] = candidate["ObjectSubTypeCode"]
    row["RestAction"] = "POST"
    return {"status": "verified", "candidate": candidate, "post_row": row}


def resolve_requested_addition(request: dict, canonical_index: str,
                               existing: dict, available: dict | None = None,
                               *, scope_confirmed: bool = False) -> dict:
    """Satisfy existing identities before resolving prospective create rows."""
    if not text(canonical_index) or not isinstance(request, dict):
        raise AttributeContractError("A canonical index and attribute request are required.")
    if not selectors(request, "attribute"):
        raise AttributeContractError("Supply an attribute name or code.")
    if (not isinstance(existing, dict) or not isinstance(existing.get("items"), list)
            or existing.get("hasMore") is True):
        raise AttributeContractError("Existing indexed-attribute metadata must be complete.")
    for record in existing["items"]:
        if not isinstance(record, dict) or record.get("IndexName") != canonical_index:
            raise AttributeContractError("Existing metadata contains an invalid or wrong-index row.")
        if any(not text(record.get(k)) for k in CODE_FIELDS):
            raise AttributeContractError("Existing metadata has an incomplete identity.")
        if "ObjectSubTypeCode" not in record:
            raise AttributeContractError("Existing ObjectSubTypeCode evidence is missing.")
        subtype = record["ObjectSubTypeCode"]
        if subtype not in (None, "") and not text(subtype):
            raise AttributeContractError("Existing ObjectSubTypeCode must be nonblank text.")

    matches = [record for record in existing["items"]
               if matches_selectors(request, record)]
    if len(matches) > 1:
        raise AttributeContractError("Existing attribute scope is ambiguous.")
    if matches:
        # Reuse selector, identity and partial-scope checks; discard the
        # tentative row so an existing identity never becomes a create input.
        result = resolve_attribute(request, canonical_index, existing,
                                   scope_confirmed=scope_confirmed)
        if result["status"] == "candidate_confirmation_required":
            return result
        return {"status": "already_indexed", "candidate": result["candidate"],
                "resolution_source": "existing_indexed_attributes"}
    return resolve_attribute(request, canonical_index, available,
                             scope_confirmed=scope_confirmed)


def backend_id(value: Any) -> str:
    """Normalize a backend ID without accepting booleans or lossy numbers."""
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise AttributeContractError("AttributeId must be a nonblank backend ID.")
    result = str(value).strip()
    if not result:
        raise AttributeContractError("AttributeId must be a nonblank backend ID.")
    return result


def resolve_requested_removal(request: dict, canonical_index: str,
                              existing: dict, *, scope_confirmed: bool = False) -> dict:
    """Resolve DELETE only from complete existing metadata, using every selector."""
    if not text(canonical_index) or not isinstance(request, dict):
        raise AttributeContractError("A canonical index and attribute request are required.")
    if not selectors(request, "attribute"):
        raise AttributeContractError("Supply an attribute name or code.")
    if (not isinstance(existing, dict) or not isinstance(existing.get("items"), list)
            or ("hasMore" in existing and existing["hasMore"] is not False)):
        raise AttributeContractError("Existing indexed-attribute metadata must be complete.")
    for record in existing["items"]:
        if not isinstance(record, dict) or record.get("IndexName") != canonical_index:
            raise AttributeContractError("Existing metadata contains an invalid or wrong-index row.")
        if any(not text(record.get(k)) for k in CODE_FIELDS):
            raise AttributeContractError("Existing metadata has an incomplete identity.")
        if "ObjectSubTypeCode" not in record:
            raise AttributeContractError("Existing ObjectSubTypeCode evidence is missing.")
        if record["ObjectSubTypeCode"] not in (None, "") and not text(record["ObjectSubTypeCode"]):
            raise AttributeContractError("Existing ObjectSubTypeCode must be nonblank text.")
    supplied_ids = [backend_id(request[k]) for k in ("attribute_id", "AttributeId")
                    if k in request and request[k] not in (None, "")]
    if len(set(supplied_ids)) > 1:
        raise AttributeContractError("Supplied AttributeId aliases conflict.")
    matches = [r for r in existing["items"] if matches_selectors(request, r)]
    if not matches:
        raise AttributeContractError("Removal selectors match no existing record; check names, codes and their agreement.")
    if supplied_ids:
        matches = [r for r in matches if backend_id(r.get("AttributeId")) == supplied_ids[0]]
        if not matches:
            raise AttributeContractError("Supplied AttributeId does not match the removal selectors.")
    if len(matches) != 1:
        raise AttributeContractError("Removal scope is ambiguous; provide group, object, subtype or AttributeId.")
    candidate = matches[0]
    if any(not text(candidate.get(k)) for k in NAME_FIELDS):
        raise AttributeContractError("Resolved removal metadata has an incomplete identity.")
    if selectors(request, "object_sub_type") and not text(candidate.get("ObjectSubTypeCode")):
        raise AttributeContractError("Supplied object subtype requires a resolved ObjectSubTypeCode.")
    identifier = backend_id(candidate.get("AttributeId"))
    if sum(backend_id(r.get("AttributeId")) == identifier for r in existing["items"]) != 1:
        raise AttributeContractError("Existing metadata has a duplicate backend AttributeId.")
    if any(not selectors(request, d) for d in ("group", "object")) and not scope_confirmed:
        return {"status": "candidate_confirmation_required", "candidate": candidate}
    row = {k: candidate[k] for k in CODE_FIELDS + NAME_FIELDS}
    row.update(RestAction="DELETE", AttributeId=identifier)
    for key in ("ObjectSubTypeCode", "ObjectSubTypeName"):
        if candidate.get(key) not in (None, ""):
            row[key] = candidate[key]
    return {"status": "removal_resolved", "candidate": candidate, "delete_row": row,
            "resolution_source": "existing_indexed_attributes"}


def create_attributes(describe: dict) -> dict:
    try:
        resource = describe["Resources"][BUSINESS_OBJECT]
        actions = resource["collection"]["actions"]
        attributes = resource["attributes"]
    except (KeyError, TypeError) as error:
        raise AttributeContractError("Create describe metadata is unavailable or malformed.") from error
    if not isinstance(actions, list) or not any(
        isinstance(a, dict) and a.get("name") == "create" and a.get("method") == "POST"
        for a in actions
    ):
        raise AttributeContractError("Live metadata does not advertise create POST.")
    if not isinstance(attributes, list) or any(not isinstance(a, dict) or not text(a.get("name")) for a in attributes):
        raise AttributeContractError("Create attribute metadata is malformed.")
    fields = {a["name"]: a for a in attributes}
    if len(fields) != len(attributes) or any(k not in fields for k in CODE_FIELDS):
        raise AttributeContractError("Create metadata has duplicate or missing identity fields.")
    for name in CODE_FIELDS:
        if fields[name].get("allowChanges") not in ("inCreate", "always"):
            raise AttributeContractError(f"{name} is not writable during create.")
    return fields


def validate_post(row: dict, resolved: dict, describe: dict) -> None:
    fields = create_attributes(describe)
    if row.get("RestAction") != "POST" or row.get("AttributeId") not in (None, ""):
        raise AttributeContractError("POST must omit the generated AttributeId.")
    for name in CODE_FIELDS:
        if not text(row.get(name)) or row[name] != resolved.get(name):
            raise AttributeContractError(f"POST {name} must equal validated metadata.")
    for name in NAME_FIELDS:
        if row.get(name) not in (None, "") and row[name] != resolved.get(name):
            raise AttributeContractError(f"POST {name} differs from validated metadata.")
    if (row.get("ObjectSubTypeCode") or "") != (resolved.get("ObjectSubTypeCode") or ""):
        raise AttributeContractError("POST ObjectSubTypeCode must preserve validated metadata.")
    if row.get("ObjectSubTypeCode") not in (None, ""):
        if not text(row["ObjectSubTypeCode"]) or row["ObjectSubTypeCode"] != resolved.get("ObjectSubTypeCode"):
            raise AttributeContractError("POST ObjectSubTypeCode must equal validated metadata.")
        if fields.get("ObjectSubTypeCode", {}).get("allowChanges") not in ("inCreate", "always"):
            raise AttributeContractError("ObjectSubTypeCode is not writable during create.")
    for name, definition in fields.items():
        writable = definition.get("allowChanges") in ("inCreate", "always")
        required = definition.get("inputRequired") is True or (
            writable and definition.get("mandatory") is True
            and definition.get("hasDefaultValueExpression") is not True
            and "defaultValue" not in definition)
        if required and (row.get(name) in (None, "") or
                         isinstance(row.get(name), str) and not row[name].strip()):
            raise AttributeContractError(f"Create requires {name}.")
        if row.get(name) not in (None, "") and not writable:
            raise AttributeContractError(f"{name} is not writable during create.")


def captured_rows(records: list) -> list[dict]:
    """Read normalized artifact records; never reopen source workbooks."""
    if not isinstance(records, list) or not records:
        raise AttributeContractError("Normalized artifact records are required.")
    rows = []
    for source in records:
        if not isinstance(source, dict) or not isinstance(source.get("sections"), list):
            raise AttributeContractError("Captured source sections are malformed.")
        for section in source["sections"]:
            if not isinstance(section, dict) or section.get("discriminator") != BUSINESS_OBJECT:
                raise AttributeContractError("Captured section targets another business object.")
            headers, values = section.get("headers"), section.get("rows")
            if (not isinstance(headers, list) or not headers or
                any(not text(h) for h in headers) or len(set(headers)) != len(headers) or
                not isinstance(values, list)):
                raise AttributeContractError("Captured columns or rows are malformed.")
            for value in values:
                if not isinstance(value, list) or len(value) != len(headers):
                    raise AttributeContractError("Captured row width differs from its headers.")
                rows.append(dict(zip(headers, value)))
    if not rows:
        raise AttributeContractError("Normalized artifact records have no data rows.")
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdin", action="store_true", required=True,
                        help="Read one JSON envelope from stdin; no files or network calls.")
    args = parser.parse_args(argv)
    try:
        envelope = json.load(sys.stdin)
        if not isinstance(envelope, dict):
            raise AttributeContractError("Input envelope must be an object.")
        operation = envelope.get("operation", "add")
        if operation not in ("add", "remove"):
            raise AttributeContractError("operation must be add or remove.")
        if operation == "remove":
            result = resolve_requested_removal(
                envelope["request"], envelope["canonical_index_name"],
                envelope["existing_attributes"],
                scope_confirmed=envelope.get("scope_confirmed") is True)
        elif "existing_attributes" in envelope:
            result = resolve_requested_addition(
                envelope["request"], envelope["canonical_index_name"],
                envelope["existing_attributes"], envelope.get("available_attributes"),
                scope_confirmed=envelope.get("scope_confirmed") is True)
        else:
            # Preserve the prospective-POST interface for missing seeded repairs.
            result = resolve_attribute(envelope["request"], envelope["canonical_index_name"],
                                       envelope["available_attributes"],
                                       scope_confirmed=envelope.get("scope_confirmed") is True)
        if result["status"] == "verified":
            validate_post(result["post_row"], result["candidate"], envelope["create_contract"])
        print(json.dumps(result))
        return 0
    except (AttributeContractError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"Index attribute contract blocked: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
