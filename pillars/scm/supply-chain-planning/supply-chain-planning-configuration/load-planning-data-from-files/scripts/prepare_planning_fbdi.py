#!/usr/bin/env python3
"""Prepare a Planning CSV/ZIP once from same-run contracts; no Fusion calls."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
import io
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import zipfile

from inspect_planning_fbdi_template import ContractError, sha256, supported_members, validate_members

REPO = next(parent for parent in Path(__file__).resolve().parents if (parent / "AGENTS.md").is_file())

# Operation semantics, not another file allowlist. Resolve the physical column
# from the current worksheet-to-CTL mapping; never hardcode a column number.
DELETE_TARGETS = {
    "sourcing_rule": ("SourcingRules.csv", "DELETE_SOURCING_RULES"),
    "sourcing_sources": ("SourcingRules.csv", "DELETE_SOURCES"),
    "atp_rule": ("ATPRules.csv", "DELETED_FLAG"),
    "atp_rule_assignment": ("ATPRuleAssignments.csv", "DELETED_FLAG"),
}
COMBINED_SOURCING_TARGETS = frozenset({"sourcing_rule", "sourcing_sources"})


def deletion_columns(contract: dict) -> list[tuple[dict, str | None]]:
    columns = []
    for field in contract["field_mapping"]:
        technical = field["worksheet_technical_name"].upper()
        if not any(name.startswith("DELETE") for name in (technical, field["csv_header"].upper())):
            continue
        targets = [target for target, (member, marker) in DELETE_TARGETS.items()
                   if member == contract["csv_member"] and marker == technical]
        columns.append((field, targets[0] if targets else None))
    return columns


def deletion_effects(values: dict, contract: dict, row_number: int) -> list[dict]:
    """Classify actual CSV flags and validate deletion identity without live calls."""
    member = contract["csv_member"]
    active = []
    for field, target in deletion_columns(contract):
        value = values.get(field["csv_header"])
        value = "" if value is None else str(value)
        if value.upper() not in {"", "YES", "NO"}:
            raise ContractError(f"{member} row {row_number}: {field['csv_header']} requires Yes, No, or blank; not numeric flags.")
        if value.upper() == "YES":
            if target is None:
                raise ContractError(f"{member} row {row_number}: unsupported deletion flag {field['csv_header']}.")
            active.append((field, target))
    if len(active) > 1 and not (
            member == "SourcingRules.csv" and len(active) == 2
            and {target for _field, target in active} == COMBINED_SOURCING_TARGETS):
        raise ContractError(f"{member} row {row_number}: unsupported deletion flag combination.")
    effects = []
    for field, target in active:
        validate_deletion_identity(values, member, target, row_number)
        effects.append({"row_number": row_number, "target": target,
                        "worksheet_flag": field["worksheet_technical_name"],
                        "csv_flag": field["csv_header"], "position": field["position"]})
    return effects


def validate_deletion_identity(values: dict, member: str, target: str, row_number: int) -> None:
    """Retain each scope's required keys, including both scopes in a combined row."""
    required = ["SR_INSTANCE_CODE"]
    if target in {"sourcing_rule", "sourcing_sources"}:
        required.append("SOURCING_RULE_NAME")
    elif target == "atp_rule":
        required.append("RULE_NAME")
    else:
        required.extend(["ATP_RULE_NAME", "ASSIGNMENT_TYPE"])
        assignment_keys = {"2": ["CATEGORY_NAME"], "3": ["ITEM_NAME"],
                           "4": ["ORGANIZATION_CODE"], "5": ["ITEM_NAME", "ORGANIZATION_CODE"]}
        assignment_type = str(values.get("ASSIGNMENT_TYPE", ""))
        if assignment_type not in assignment_keys:
            raise ContractError(f"{member} row {row_number}: deletion requires assignment type 2, 3, 4, or 5.")
        required.extend(assignment_keys[assignment_type])
    if target == "sourcing_sources":
        required.extend(["EFFECTIVE_DATE", "SOURCE_TYPE", "RANK"])
        source_type = str(values.get("SOURCE_TYPE", ""))
        if source_type not in {"1", "2", "3"}:
            raise ContractError(f"{member} row {row_number}: source deletion requires source type 1, 2, or 3.")
        required.extend(["VENDOR_NAME"] if source_type == "3" else ["SOURCE_ORGANIZATION_CODE"])
    missing = [key for key in required if values.get(key) is None or not str(values[key]).strip()]
    if missing:
        raise ContractError(f"{member} row {row_number}: deletion target requires {', '.join(missing)}.")


def delete_values(record: dict, contract: dict) -> dict:
    """Overlay only explicitly requested delete markers on an identified full row."""
    baseline = record.get("baseline")
    member = contract["csv_member"]
    if set(record) == {"target", "baseline"}:
        targets = [record["target"]]
    elif set(record) == {"targets", "baseline"} and isinstance(record["targets"], list):
        targets = record["targets"]
    else:
        raise ContractError(f"{member}: delete rows require target or targets, and baseline only.")
    if (not targets or any(not isinstance(target, str) or target not in DELETE_TARGETS
                          or DELETE_TARGETS[target][0] != member for target in targets)
            or len(set(targets)) != len(targets)
            or (len(targets) > 1 and set(targets) != COMBINED_SOURCING_TARGETS)):
        raise ContractError(f"{member}: unsupported or duplicate deletion targets.")
    fields = contract["ordered_headers"][:-1]
    if not isinstance(baseline, dict) or set(baseline) != set(fields):
        raise ContractError(f"{member}: delete baseline must contain every CTL input field.")
    columns = deletion_columns(contract)
    selected = []
    for target in targets:
        matching = [field for field, scope in columns if scope == target]
        if len(matching) != 1:
            raise ContractError(f"{member}: missing or ambiguous deletion marker in current worksheet/CTL contract.")
        selected.append(matching[0]["csv_header"])
    existing = deletion_effects(baseline, contract, 1)
    if any(effect["target"] not in targets for effect in existing):
        raise ContractError(f"{member}: baseline contains a different deletion scope.")
    values = dict(baseline)
    for field, _scope in columns:
        values[field["csv_header"]] = "Yes" if field["csv_header"] in selected else "No"
    return values


def load_contracts(path: Path, run_id: str) -> tuple[dict, dict]:
    """Reuse parsed metadata, checking source digests rather than parsing XLSM again."""
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    if document.get("status") != "passed" or document.get("schema_version") != 1:
        raise ContractError("A passing inspector contract is required.")
    provenance = document["provenance"]
    if not run_id or provenance.get("run_id") != run_id:
        raise ContractError("Contract belongs to another run; retrieve current templates.")
    contracts = {}
    routes = supported_members()
    checked_sources = set()
    for template in document["templates"]:
        if template["template"] in checked_sources:
            raise ContractError("Duplicate workbook contract.")
        checked_sources.add(template["template"])
        if sha256(Path(template["template_path"]).read_bytes()) != template["sha256"]:
            raise ContractError("Workbook changed after contract extraction.")
        for contract in template["csv_contracts"]:
            member = validate_members([contract["csv_member"]])[0]
            if member in contracts or routes[member] != (template["template"], contract["target_table"]):
                raise ContractError("Duplicate contract or mismatched template route.")
            content = Path(contract["control_file_path"]).read_bytes()
            if sha256(content) != contract["control_file_sha256"]:
                raise ContractError("Control file changed after contract extraction.")
            fields = contract["ordered_headers"]
            if not contract["legacy_end_marker"] or fields[-1:] != ["END"] or len(set(fields)) != len(fields):
                raise ContractError("Incomplete ordered field/END contract.")
            if len(contract["field_mapping"]) != len(fields) - 1:
                raise ContractError("Incomplete position mapping.")
            if [field["csv_header"] for field in contract["field_mapping"]] != fields[:-1]:
                raise ContractError("Field mapping order differs from the CTL headers.")
            for name, digest in ((template["template"], template["sha256"]),
                                 (contract["control_file"], contract["control_file_sha256"])):
                if provenance.get("files", {}).get(name, {}).get("sha256") != digest:
                    raise ContractError("Download provenance differs from contract source hashes.")
            contracts[member] = contract
    if not contracts:
        raise ContractError("Contract contains no supported CSVs.")
    return contracts, {"contract_sha256": sha256(path.read_bytes()), "provenance": provenance}


def source_members(source: Path, content: bytes | None = None) -> tuple[list[tuple[str, bytes]], list[str], list[str]]:
    """Inventory and read retained members once; never extract archive paths."""
    content = source.read_bytes() if content is None else content
    if source.suffix.lower() == ".csv":
        validate_members([source.name])
        return [(source.name, content)], [], []
    if source.suffix.lower() != ".zip":
        raise ContractError("Source must be a supported CSV or ZIP, not an XLSM.")
    retained, excluded, ignored = [], [], []
    allowed = {member.casefold() for member in supported_members()}
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        for entry in archive.infolist():
            name = entry.filename
            parts = name.split("/")
            if any(part.casefold() in {"_macosx", "__macosx"} for part in parts[:-1]):
                ignored.append(name)
                continue
            if ("\\" in name or ":" in name or "\x00" in name
                    or any(part in {"", ".", ".."} for part in parts[:-1])
                    or (not entry.is_dir() and parts[-1] in {"", ".", ".."})):
                raise ContractError(f"Unsafe ZIP member path: {name}")
            if stat.S_ISLNK(entry.external_attr >> 16):
                raise ContractError(f"Symbolic-link member is not allowed: {name}")
            if entry.is_dir():
                continue
            if parts[-1].casefold() not in allowed:
                excluded.append(name)
                continue
            if len(parts) != 1 or entry.flag_bits & 1 or not entry.file_size:
                raise ContractError(f"Supported member must be root-level, unencrypted and nonempty: {name}")
            retained.append((name, archive.read(entry)))
    validate_members([name for name, _ in retained])
    return retained, excluded, ignored


def normalized_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def check_value(value: str, field: dict, member: str, row_number: int) -> None:
    if "\x00" in value:
        raise ContractError(f"{member} row {row_number}: NUL is not valid CSV data.")
    if not value:
        return
    kind = field.get("data_type", "").upper()
    length = re.search(r"CHAR(?:ACTER)?\s*\((\d+)\)", kind)
    if length and len(value) > int(length.group(1)):
        raise ContractError(f'{member} row {row_number}: {field["csv_header"]} exceeds template length.')
    if kind.startswith("NUMBER"):
        try:
            if not Decimal(value).is_finite():
                raise InvalidOperation
        except InvalidOperation as error:
            raise ContractError(f'{member} row {row_number}: {field["csv_header"]} requires a number.') from error
    if "DATE" in kind and "YYYY/MM/DD" in kind:
        try:
            if not re.fullmatch(r"\d{4}/\d{2}/\d{2}", value):
                raise ValueError
            datetime.strptime(value, "%Y/%m/%d")
        except ValueError as error:
            raise ContractError(f'{member} row {row_number}: {field["csv_header"]} requires YYYY/MM/DD.') from error


def validate_csv(content: bytes, contract: dict, *, generated: bool) -> dict:
    member = contract["csv_member"]
    rows = list(csv.reader(io.StringIO(content.decode("utf-8-sig"), newline=""), strict=True))
    if not rows:
        raise ContractError(f"{member} is empty.")
    physical = contract["ordered_headers"][:-1]
    has_header = contract["header_required"]
    header = rows.pop(0) if has_header else None
    with_end = (header[-1:] == ["END"]) if header is not None else rows[0][-1:] == ["END"]
    expected_count = len(physical) + int(with_end)
    if generated and not with_end:
        raise ContractError(f"{member}: generated CSV requires END.")
    if header is not None:
        if len(header) != expected_count:
            raise ContractError(f"{member}: header width differs from the full template.")
        for index, field in enumerate(contract["field_mapping"]):
            allowed = {normalized_label(field[key] or "") for key in (
                "csv_header", "worksheet_label", "worksheet_technical_name")}
            if normalized_label(header[index]) not in allowed or not header[index].strip():
                raise ContractError(f"{member}: unrecognized header at position {index + 1}.")
        if generated and header != contract["ordered_headers"]:
            raise ContractError(f"{member}: generated headers must use CTL order.")
    if not rows:
        raise ContractError(f"{member}: at least one data row is required.")
    deletions = []
    for number, row in enumerate(rows, start=2 if has_header else 1):
        if len(row) != expected_count or (with_end and row[-1] != "END"):
            raise ContractError(f"{member} row {number}: field count or terminal END mismatch.")
        if not any(value.strip() for value in row[:len(physical)]):
            raise ContractError(f"{member} row {number}: empty business row.")
        for value, field in zip(row, contract["field_mapping"]):
            check_value(value, field, member, number)
        deletions.extend(deletion_effects(dict(zip(physical, row)), contract, number))
    return {"member": member, "row_count": len(rows), "field_count": expected_count,
            "end_marker": with_end, "header_match": "ctl" if header == contract["ordered_headers"] else "position",
            "sha256": sha256(content), "deletions": deletions}


def generate_members(request: dict, contracts: dict) -> tuple[list[tuple[str, bytes]], dict]:
    members = request.get("members")
    if not isinstance(members, dict):
        raise ContractError("Request requires a members object keyed by supported CSV filename.")
    names = validate_members(list(members))
    operation = request.get("operation", "create")
    if operation not in {"create", "update", "delete"}:
        raise ContractError("Generation operation must be create, update, or delete.")
    output, mappings = [], {}
    for supplied_name, name in zip(members, names):
        if name not in contracts:
            raise ContractError(f"Missing same-run contract for {name}.")
        contract = contracts[name]
        fields = contract["ordered_headers"][:-1]
        records = members[supplied_name]
        if not isinstance(records, list) or not records:
            raise ContractError(f"{name}: provide at least one mapped row.")
        stream = io.StringIO(newline="")
        writer = csv.writer(stream, delimiter=contract["delimiter"], quotechar='"', lineterminator="\r\n")
        if contract["header_required"]:
            writer.writerow(contract["ordered_headers"])
        used = set()
        for record in records:
            if not isinstance(record, dict):
                raise ContractError(f"{name}: each row must be an object.")
            if operation == "delete":
                values = delete_values(record, contract)
                used.update(values)
            elif operation == "update":
                baseline, changes = record.get("baseline"), record.get("changes")
                if set(record) != {"baseline", "changes"} or not isinstance(baseline, dict) or not isinstance(changes, dict):
                    raise ContractError(f"{name}: update rows require baseline and changes objects.")
                if set(baseline) != set(fields):
                    raise ContractError(f"{name}: update baseline must contain every CTL input field.")
                if not set(changes) <= set(fields):
                    raise ContractError(f"{name}: unknown update field.")
                values = {**baseline, **changes}
                used.update(changes)
            else:
                values = record
                used.update(values)
            if not set(values) <= set(fields):
                raise ContractError(f"{name}: unknown input field; END and generated server fields are not user inputs.")
            row = []
            for field in fields:
                value = values.get(field)
                if value is not None and not isinstance(value, (str, int, float)) or isinstance(value, bool):
                    raise ContractError(f"{name}: values must be strings, numbers, or null.")
                row.append("" if value is None else str(value))
            effects = deletion_effects(dict(zip(fields, row)), contract, 1)
            if effects and operation != "delete":
                raise ContractError(f"{name}: affirmative deletion flags require operation delete, not create/update.")
            if operation == "delete" and not effects:
                raise ContractError(f"{name}: delete request must produce a deletion marker.")
            writer.writerow(row + ["END"])
        output.append((name, stream.getvalue().encode("utf-8")))
        mappings[name] = [{"input": field, "position": fields.index(field) + 1} for field in fields if field in used]
    return output, mappings


def new_destination(path: Path) -> None:
    resolved = path.resolve()
    if resolved == REPO or REPO in resolved.parents:
        raise ContractError("Business artifacts must be outside the repository/project.")
    if path.exists() or path.is_symlink() or not path.parent.is_dir():
        raise ContractError("Output requires a new filename in an existing writable directory.")


def publish_zip(members: list[tuple[str, bytes]], output: Path) -> str:
    new_destination(output)
    if output.suffix.lower() != ".zip":
        raise ContractError("Output must use a .zip filename.")
    # A private TemporaryDirectory gives its children creator-only Windows ACLs.
    # Stage a file in the approved destination instead: Windows inherits that
    # folder's ACL, while mkstemp retains restrictive file mode on POSIX.
    descriptor, staging_name = tempfile.mkstemp(prefix=".planning-fbdi-", suffix=".tmp", dir=output.parent)
    staged = Path(staging_name)
    try:
        with os.fdopen(descriptor, "w+b") as stream:
            with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for name, content in members:
                    # Deterministic ZIP bytes, independent of the wall clock.
                    entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                    entry.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(entry, content)
            stream.flush()
            with zipfile.ZipFile(stream) as archive:
                if archive.namelist() != [name for name, _ in members]:
                    raise ContractError("Final ZIP member/order mismatch.")
                for name, expected in members:
                    if archive.read(name) != expected:
                        raise ContractError("Final ZIP differs from validated CSV bytes.")
            stream.seek(0)
            digest = sha256(stream.read())
        os.link(staged, output)  # Atomic no-clobber publication on the same volume.
    finally:
        staged.unlink(missing_ok=True)
    return digest


def prepare(*, contracts: dict, evidence: dict, source: Path | None = None,
            request: dict | None = None, output: Path | None = None, dry_run: bool = False) -> dict:
    if (source is None) == (request is None):
        raise ContractError("Choose exactly one source or mapped request.")
    generated = request is not None
    if generated:
        members, mappings = generate_members(request, contracts)
        excluded, ignored = [], []
    else:
        source_content = source.read_bytes()
        members, excluded, ignored = source_members(source, source_content)
        mappings = {}
    canonical = validate_members([name for name, _ in members])
    validations = []
    for (name, content), member in zip(members, canonical):
        if member not in contracts:
            raise ContractError(f"Missing same-run contract for {member}.")
        validations.append({**validate_csv(content, contracts[member], generated=generated), "member": name})
    passthrough = not generated and source.suffix.lower() == ".zip" and not excluded
    if dry_run:
        artifact, digest = None, None
    elif passthrough:
        artifact = source.resolve()
        digest = sha256(source_content)
        if sha256(source.read_bytes()) != digest:
            raise ContractError("Source ZIP changed during preparation; validate the new artifact.")
    else:
        if output is None:
            raise ContractError("A new --output-zip is required for generated, CSV, or mixed-ZIP input.")
        artifact = output.resolve()
        digest = publish_zip(members, output)
    return {
        "status": "dry_run_passed" if dry_run else "READY_FOR_CORE_DATA_LOADER",
        "live_validated": False, "submitted": False,
        "business_object": "Planning Common",
        "archive_path": str(artifact) if artifact else None, "archive_sha256": digest,
        "filtered": bool(excluded), "unchanged_source_zip": passthrough,
        "excluded_members": excluded, "ignored_platform_metadata": ignored,
        "members": validations, "source_to_output_mapping": mappings,
        "contains_deletions": any(item["deletions"] for item in validations),
        "deletion_row_count": sum(len({effect["row_number"] for effect in item["deletions"]})
                                  for item in validations),
        "deletion_action_count": sum(len(item["deletions"]) for item in validations),
        **evidence,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--source", type=Path, help="supplied CSV or ZIP; preserved unchanged")
    selection.add_argument("--request", type=Path, help="mapped create/update/delete JSON")
    parser.add_argument("--contracts", type=Path, required=True)
    parser.add_argument("--run-id", required=True, help="current local preparation run, not Fusion runID")
    parser.add_argument("--output-zip", type=Path)
    parser.add_argument("--report", type=Path, help="new transient evidence JSON path")
    parser.add_argument("--dry-run", action="store_true", help="validate in memory without writing any artifacts")
    args = parser.parse_args(argv)
    result = None
    try:
        contracts, evidence = load_contracts(args.contracts, args.run_id)
        if args.report and not args.dry_run:
            new_destination(args.report)
            if args.output_zip and args.report.resolve() == args.output_zip.resolve():
                raise ContractError("Report and ZIP must have distinct paths.")
            if args.source and args.report.resolve() == args.source.resolve():
                raise ContractError("Report cannot overwrite the source.")
        request = json.loads(args.request.read_text(encoding="utf-8-sig")) if args.request else None
        result = prepare(contracts=contracts, evidence=evidence, source=args.source,
                         request=request, output=args.output_zip, dry_run=args.dry_run)
        if args.report and not args.dry_run:
            with args.report.open("x", encoding="utf-8", newline="\n") as report:
                report.write(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, IndexError, csv.Error, zipfile.BadZipFile, RuntimeError) as error:
        failure = {"status": "blocked", "failure_class": "artifact_persistence" if isinstance(error, OSError) else "input_validation",
                   "message": str(error)}
        if result and result.get("archive_path"):
            failure["prepared_archive_path"] = result["archive_path"]
            failure["archive_sha256"] = result["archive_sha256"]
            failure["submitted"] = False
        print(json.dumps(failure))
        return 1


if __name__ == "__main__":
    sys.exit(main())
