"""Offline task checks and reconciliation; never authenticates or submits loads.


During a Data Loader session, evaluate its captured records in memory. Do not
reopen live inputs or persist records, approvals, previews or recovery envelopes.
The ZIP reader is for separately authorized baseline/export inspection only.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence
import xml.etree.ElementTree as ET
import zipfile

TASK = "IBY_MANAGE_DISBURSEMENT_SYSTEM_OPTIONS"
CSV_MEMBER = "IBY_INTERNAL_PAYER.csv"
XML_MEMBER = "ASM_SETUP_CSV_METADATA.xml"
# A bounded reader protects the host; this is not a Fusion volume capability.
MAX_EXPORT_BYTES = 64 * 1024 * 1024
HEADERS = (
    "BuName", "PaymentMethodAtPayeeFlag", "DocumentRejectionLevelCode",
    "PaymentRejectionLevelCode", "RequirePropPmtsReviewFlag",
    "AllowExtAcctOverrideFlag", "ExclusivePaymentFlag", "SavePaymentFileInDb",
    "CreatedBy", "CreationDate", "LastUpdatedBy", "LastUpdateDate",
    "LastUpdateLogin", "OrgType", "BankChargeBearer", "PprReportFormat",
    "AutomaticPprReportSubmit", "BusinessUnitId1", "ModuleId", "ModuleKey",
    "PaymentsApprovalFlag", "SraEmailSubject", "SraSendFrom",
)
AUDIT = frozenset({"CreatedBy", "CreationDate", "LastUpdatedBy", "LastUpdateDate", "LastUpdateLogin"})
REQUIRED_AUDIT = AUDIT - {"LastUpdateLogin"}  # EO leaves this service-owned field nullable.
UPDATE_AUDIT = frozenset({"LastUpdatedBy", "LastUpdateDate", "LastUpdateLogin"})
PROTECTED = AUDIT | {"BuName", "BusinessUnitId1", "ModuleId", "ModuleKey"}
BUSINESS = frozenset(HEADERS) - PROTECTED - {"OrgType"}
NONNULL = frozenset({"PaymentMethodAtPayeeFlag", "DocumentRejectionLevelCode",
    "PaymentRejectionLevelCode", "RequirePropPmtsReviewFlag", "AllowExtAcctOverrideFlag",
    "ExclusivePaymentFlag", "SavePaymentFileInDb"})
LENGTHS = {field: 1 for field in (
    "PaymentMethodAtPayeeFlag", "RequirePropPmtsReviewFlag", "AllowExtAcctOverrideFlag",
    "ExclusivePaymentFlag", "SavePaymentFileInDb", "AutomaticPprReportSubmit", "PaymentsApprovalFlag")}
LENGTHS.update({field: 30 for field in (
    "DocumentRejectionLevelCode", "PaymentRejectionLevelCode", "BankChargeBearer", "PprReportFormat")})
LENGTHS.update({"SraEmailSubject": 1024, "SraSendFrom": 1024})


class TaskError(ValueError):
    """A failed deterministic task check; no mutation was attempted."""


class EvidenceUnresolved(TaskError):
    """A missing evidence/decision contract, not a product prohibition."""


@dataclass(frozen=True)
class Snapshot:
    environment: str
    release: str
    source_sha256: str
    rows: tuple[tuple[str, ...], ...]

    def index(self) -> dict[str, tuple[str, ...]]:
        result: dict[str, tuple[str, ...]] = {}
        for row in self.rows:
            if len(row) != len(HEADERS) or any(not isinstance(v, str) for v in row):
                raise TaskError("Malformed captured record shape")
            key = row[0]
            if key and not key.strip():
                raise TaskError("Whitespace-only BU identity is not the blank enterprise identity")
            if key in result:
                raise TaskError("Duplicate record identity; clarify before processing")
            result[key] = row
        if "" not in result:
            raise TaskError("Exact-task baseline must establish its enterprise singleton")
        return result


def captured_snapshot(records: Sequence[Mapping[str, str]], *, environment: str,
                      release: str, source_sha256: str) -> Snapshot:
    """Inspect the current session's captured records without reopening sources."""
    if not environment or not release:
        raise TaskError("Explicit target environment and release are required")
    if (len(source_sha256) != 64
            or any(c not in "0123456789abcdef" for c in source_sha256)):
        raise TaskError("A captured-source SHA-256 is required")
    rows = []
    for record in records:
        if not isinstance(record, Mapping) or set(record) != set(HEADERS):
            raise TaskError("Captured fields must match the exact task's 23-column contract")
        rows.append(tuple(record[h] for h in HEADERS))
    snapshot = Snapshot(environment, release, source_sha256, tuple(rows))
    snapshot.index()
    return snapshot


def read_export(data: bytes, *, environment: str, release: str) -> Snapshot:
    """Strictly inspect a read-only exact-task export; never extract ZIP paths."""
    if not isinstance(data, bytes) or len(data) > MAX_EXPORT_BYTES:
        raise TaskError("Export exceeds this reader's memory bound")
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = archive.infolist()
            if len(members) != 2 or {m.filename for m in members} != {CSV_MEMBER, XML_MEMBER}:
                raise TaskError("Unexpected, missing or duplicate ZIP members")
            if any(m.flag_bits & 1 or m.file_size > MAX_EXPORT_BYTES
                   or PurePosixPath(m.filename).is_absolute() for m in members):
                raise TaskError("Encrypted, oversized or unsafe ZIP member")
            if sum(m.file_size for m in members) > MAX_EXPORT_BYTES:
                raise TaskError("Expanded export exceeds this reader's memory bound")
            csv_data = archive.read(CSV_MEMBER).decode("utf-8-sig")
            xml_data = archive.read(XML_MEMBER)
    except (zipfile.BadZipFile, UnicodeError, RuntimeError, NotImplementedError) as exc:
        raise TaskError("Unreadable export package") from exc
    try:
        xml_text = xml_data.decode("utf-8-sig")
    except UnicodeError as exc:
        raise TaskError("Metadata must use the inspected UTF-8 export encoding") from exc
    if "\x00" in xml_text or "<!DOCTYPE" in xml_text.upper() or "<!ENTITY" in xml_text.upper():
        raise TaskError("XML declarations/entities are not permitted")
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise TaskError("Malformed export metadata") from exc
    processes = root.findall("MigrationProcessCSVMetadataVORow")
    if root.tag != "MigrationProcessCSVMetadataVO" or len(processes) != 1:
        raise TaskError("Ambiguous export process metadata")
    process = processes[0]
    checks = {"ObjectShortName": TASK, "ObjectType": "TASK", "ProcessType": "EXPORT",
              "ProcessStatus": "COMPLETED", "ProcessEnv": environment, "ProcessRelease": release}
    for tag, expected in checks.items():
        if not expected or len(process.findall(tag)) != 1 or process.findtext(tag) != expected:
            raise TaskError("Task/environment/release/export metadata mismatch: " + tag)
    objects = process.findall("MigrationProcessBusinessObjectCSVMetadata1/MigrationProcessBusinessObjectCSVMetadataVORow")
    if len(objects) != 1:
        raise TaskError("Expected one exact business object")
    obj = objects[0]
    for tag, value in {"BusinessObjectShortName": "IBY_INTERNAL_PAYER",
                       "XmlNodePath": "/InternalPayerVO/InternalPayerVORow",
                       "NodeSequence": "1"}.items():
        if len(obj.findall(tag)) != 1 or obj.findtext(tag) != value:
            raise TaskError("Business-object topology mismatch: " + tag)
    attributes = (obj.findtext("XmlAttributeList") or "").split(",")
    types = (obj.findtext("XmlAttributeTypeList") or "").split(",")
    expected_types = {h: "dateTime" if h in {"CreationDate", "LastUpdateDate"}
                      else "long" if h in {"BusinessUnitId1", "ModuleId"} else "string" for h in HEADERS}
    if (len(obj.findall("XmlAttributeList")) != 1 or len(obj.findall("XmlAttributeTypeList")) != 1
            or len(attributes) != len(HEADERS) or len(types) != len(attributes)
            or len(set(attributes)) != len(attributes)
            or dict(zip(attributes, types)) != expected_types):
        raise TaskError("Metadata field/type contract mismatch")
    reader = csv.reader(io.StringIO(csv_data, newline=""), strict=True)
    try:
        if tuple(next(reader)) != HEADERS:
            raise TaskError("CSV ordered headers do not match the task contract")
        rows = tuple(tuple(row) for row in reader)
    except (StopIteration, csv.Error) as exc:
        raise TaskError("Malformed or empty CSV") from exc
    snapshot = Snapshot(environment, release, hashlib.sha256(data).hexdigest(), rows)
    snapshot.index()
    return snapshot


def identity(scope: str, bu_name: str | None) -> str:
    if scope == "enterprise":
        if bu_name not in (None, ""):
            raise TaskError("Enterprise scope cannot also name a BU")
        return ""
    if scope == "business_unit" and isinstance(bu_name, str) and bu_name.strip():
        return bu_name  # exact; never trim, case-fold or substitute the CSV value
    raise TaskError("Provide explicit enterprise scope or business_unit scope with an exact BuName")


@dataclass(frozen=True)
class Change:
    bu_name: str
    field: str
    before: str
    after: str


@dataclass(frozen=True)
class Creation:
    bu_name: str
    org_type: str
    values: tuple[tuple[str, str], ...]
    reference_id: str


@dataclass(frozen=True)
class ReviewedUpdates:
    baseline: Snapshot
    rows: tuple[tuple[str, ...], ...]
    changes: tuple[Change, ...]
    # Records business decisions only; never denotes mutation/candidate approval.
    uncertainty_decisions: tuple[tuple[str, str, str], ...]
    creations: tuple[Creation, ...] = ()


def review_updates(baseline: Snapshot, requests: Sequence[Mapping], *,
                   expected_baseline_sha256: str,
                   application_validation_decisions: frozenset[tuple[str, str, str]] = frozenset()
                   ) -> ReviewedUpdates:
    """Atomically review explicit existing-row changes, in memory only.

    Every unresolved field operation needs a separately obtained human decision
    to rely on application validation, identified by exact (BuName, field, value)
    in this baseline/target context. These are findings from the trusted host,
    not an approval protocol or reusable authorization token.
    Passing that decision does not qualify the field or approve an import.
    No task defaults, approvals, payload files or API calls are created here.
    """
    if baseline.source_sha256 != expected_baseline_sha256:
        raise TaskError("Stale or mismatched baseline hash")
    index = baseline.index()
    if not requests:
        raise TaskError("No requested business changes")
    changes: list[Change] = []
    updates = dict(index)
    seen: set[str] = set()
    used_decisions: set[tuple[str, str, str]] = set()
    for request in requests:
        if not isinstance(request, Mapping) or set(request) - {"scope", "buName", "operation", "changes"}:
            raise TaskError("Unknown request attributes")
        operation = request.get("operation")
        if operation == "create":
            raise EvidenceUnresolved("Create eligibility, required inputs and serialization need qualification; not a product prohibition")
        if operation != "update":
            raise EvidenceUnresolved("No task CSV lifecycle/delete contract is established")
        key = identity(request.get("scope"), request.get("buName"))
        if key in seen:
            raise TaskError("Conflicting operations for one identity; combine or clarify")
        seen.add(key)
        if key not in index:
            raise TaskError("Exact update target is absent; no create or enterprise fallback")
        values = request.get("changes")
        if not isinstance(values, Mapping) or not values:
            raise TaskError("Provide at least one explicit changed business value")
        row = dict(zip(HEADERS, index[key]))
        row_changes = []
        for field, value in values.items():
            if field in PROTECTED:
                raise TaskError("Identity/audit/derived metadata cannot be supplied as a business change")
            if field == "OrgType":
                raise EvidenceUnresolved("OrgType context/mutability is unproven; preserve the baseline")
            if field not in BUSINESS or not isinstance(value, str):
                raise TaskError("Unknown business field or non-string canonical value")
            if field in NONNULL and not value:
                raise TaskError("Source-required value cannot be cleared: " + field)
            if len(value) > LENGTHS[field]:
                raise TaskError("Source-backed field length exceeded: " + field)
            if value != row[field]:
                decision = (key, field, value)
                if decision not in application_validation_decisions:
                    raise EvidenceUnresolved("Field update remains evidence_unresolved; obtain exact-field application-validation decision: " + field)
                used_decisions.add(decision)
                row_changes.append(Change(key, field, row[field], value))
                row[field] = value
        if not row_changes:
            raise TaskError("No-op update; no candidate is needed")
        if row["AutomaticPprReportSubmit"] == "Y" and not row["PprReportFormat"].strip():
            raise TaskError("Automatic PPR report submission requires a nonblank format")
        updates[key] = tuple(row[h] for h in HEADERS)
        changes.extend(row_changes)
    if used_decisions != set(application_validation_decisions):
        raise TaskError("Uncertainty decision does not match the exact changed fields")
    ordered = tuple(updates[row[0]] for row in baseline.rows)
    return ReviewedUpdates(baseline, ordered,
        tuple(sorted(changes, key=lambda c: (c.bu_name, HEADERS.index(c.field)))),
        tuple(sorted(used_decisions)))


def review_operations(baseline: Snapshot, requests: Sequence[Mapping], *,
                      expected_baseline_sha256: str,
                      application_validation_decisions: frozenset[tuple[str, str, str]] = frozenset(),
                      creation_reference_ids: Mapping[str, str] | None = None) -> ReviewedUpdates:
    """Atomically prepare explicit updates and new BU rows; no implicit upsert.

    Reference authenticity/current-task eligibility belong to the trusted caller.
    Every create business field, including an intentional blank, is explicit.
    Service-owned columns are left blank, never copied from historical rows.
    This controlled preparation contract does not establish import success.
    """
    if baseline.source_sha256 != expected_baseline_sha256:
        raise TaskError("Stale or mismatched baseline hash")
    if not requests:
        raise TaskError("No requested business operations")
    index, seen, updates, creations = baseline.index(), set(), [], []
    used = set()
    references = dict(creation_reference_ids or {})
    for item in requests:
        if not isinstance(item, Mapping):
            raise TaskError("Malformed operation")
        key = identity(item.get("scope"), item.get("buName"))
        if key in seen:
            raise TaskError("Conflicting operations for one identity; combine or clarify")
        seen.add(key)
        if item.get("operation") != "create":
            updates.append(item)
            continue
        if set(item) != {"operation", "scope", "buName", "values", "orgType"}:
            raise TaskError("Create needs explicit values/context; no protected overrides")
        if not key or key in index:
            raise TaskError("Create target already exists; no implicit update or enterprise creation")
        if item["orgType"] != "OPERATING_UNIT":
            raise EvidenceUnresolved("BU create context needs its own authoritative contract")
        values = item["values"]
        if not isinstance(values, Mapping) or set(values) != BUSINESS:
            raise TaskError("Provide every create business field explicitly; no defaults or protected inputs")
        for field, value in values.items():
            if not isinstance(value, str) or len(value) > LENGTHS[field]:
                raise TaskError("Create needs canonical strings within source-backed lengths")
            if field in NONNULL and not value:
                raise TaskError("Source-required create value is missing: " + field)
            decision = (key, field, value)
            if decision not in application_validation_decisions:
                raise EvidenceUnresolved("Create field needs exact application-validation decision: " + field)
            used.add(decision)
        if values["AutomaticPprReportSubmit"] == "Y" and not values["PprReportFormat"].strip():
            raise TaskError("Automatic PPR report submission requires a nonblank format")
        reference_id = references.get(key)
        if (not isinstance(reference_id, str) or not 1 <= len(reference_id) <= 18
                or not reference_id.isascii() or not reference_id.isdigit() or int(reference_id) <= 0):
            raise TaskError("Create requires an exact current active/eligible BU reference")
        creations.append(Creation(key, item["orgType"],
            tuple((h, values[h]) for h in HEADERS if h in BUSINESS), reference_id))
    create_keys = {c.bu_name for c in creations}
    if set(references) != create_keys:
        raise TaskError("Creation references must match exactly the new BU identities")
    if len(set(references.values())) != len(references):
        raise TaskError("Distinct create identities cannot resolve to the same BU ID")
    update_decisions = frozenset(d for d in application_validation_decisions if d[0] not in create_keys)
    update_review = (review_updates(baseline, updates, expected_baseline_sha256=expected_baseline_sha256,
        application_validation_decisions=update_decisions) if updates else
        ReviewedUpdates(baseline, baseline.rows, (), ()))
    used.update(update_review.uncertainty_decisions)
    if used != set(application_validation_decisions):
        raise TaskError("Uncertainty decisions must match every exact requested field")
    rows = list(update_review.rows)
    for creation in sorted(creations, key=lambda c: c.bu_name):
        row = dict.fromkeys(HEADERS, "")
        row.update(dict(creation.values))
        row.update(BuName=creation.bu_name, OrgType=creation.org_type)
        rows.append(tuple(row[h] for h in HEADERS))
    return ReviewedUpdates(baseline, tuple(rows), update_review.changes, tuple(sorted(used)),
                           tuple(sorted(creations, key=lambda c: c.bu_name)))


def reconcile(review: ReviewedUpdates, fresh: Snapshot) -> dict:
    """Compare all requested and unrequested values; never infer import success."""
    if (fresh.environment, fresh.release) != (review.baseline.environment, review.baseline.release):
        raise TaskError("Fresh export target/release differs from the baseline")
    if review.changes or review.creations:
        _checked_review(review.baseline, review)
    elif review.rows != review.baseline.rows or review.uncertainty_decisions:
        raise TaskError("Unchanged comparison must preserve the exact baseline design")
    observed = fresh.index()
    expected = {row[0]: row for row in review.rows}
    changed = {(c.bu_name, c.field) for c in review.changes}
    changed_rows = {c.bu_name for c in review.changes}
    creations = {c.bu_name: c for c in review.creations}
    requested_errors, preservation_errors, audit_deltas, assigned = [], [], [], []
    for key in expected.keys() & observed.keys():
        for position, field in enumerate(HEADERS):
            if key in creations and field in PROTECTED - {"BuName"}:
                value = observed[key][position]
                if (field in REQUIRED_AUDIT and not value.strip()
                        or field == "BusinessUnitId1" and value != creations[key].reference_id
                        or field == "ModuleKey" and value != "PAYABLES_PAYMENT_BF"
                        or field == "ModuleId" and (not 1 <= len(value) <= 18 or not value.isascii()
                                                    or not value.isdigit() or int(value) <= 0)):
                    preservation_errors.append({"scope": "business_unit", "buName": key, "field": field})
                else:
                    assigned.append({"scope": "business_unit", "buName": key, "field": field})
                continue
            if expected[key][position] == observed[key][position]:
                continue
            cell = {"scope": "enterprise" if key == "" else "business_unit", "buName": key, "field": field}
            if key in creations or (key, field) in changed:
                requested_errors.append(cell)
            elif key in changed_rows and field in UPDATE_AUDIT:
                audit_deltas.append(cell)
            else:
                preservation_errors.append(cell)
    added, removed = sorted(observed.keys() - expected.keys()), sorted(expected.keys() - observed.keys())
    result = {"comparisonMatch": not (requested_errors or preservation_errors or added or removed),
        "requestedMismatches": requested_errors, "preservationMismatches": preservation_errors,
        "serviceOwnedAuditDeltas": audit_deltas, "addedIdentities": added, "removedIdentities": removed,
        "importOutcome": "not_determined_by_export_comparison"}
    if creations:
        result["createdIdentities"] = sorted(creations)
        result["serviceOwnedCreateAssignments"] = assigned
    return result


def _checked_review(baseline: Snapshot, review: ReviewedUpdates) -> ReviewedUpdates:
    """Recompute a design from its exact changes; never trust a constructed rows tuple."""
    if baseline != review.baseline:
        raise TaskError("Design is not bound to this exact baseline")
    groups: dict[str, dict[str, str]] = {}
    cells = set()
    index = baseline.index()
    for change in review.changes:
        cell = (change.bu_name, change.field)
        if cell in cells or change.bu_name not in index or change.field not in HEADERS:
            raise TaskError("Duplicate or unknown design change")
        cells.add(cell)
        if index[change.bu_name][HEADERS.index(change.field)] != change.before:
            raise TaskError("Design before-value differs from its baseline")
        groups.setdefault(change.bu_name, {})[change.field] = change.after
    requests = [{"operation": "update", "scope": "enterprise" if key == "" else "business_unit",
                 "buName": key, "changes": values} for key, values in groups.items()]
    if review.creations:
        requests.extend({"operation": "create", "scope": "business_unit", "buName": c.bu_name,
                         "orgType": c.org_type, "values": dict(c.values)} for c in review.creations)
        checked = review_operations(baseline, requests, expected_baseline_sha256=baseline.source_sha256,
            application_validation_decisions=frozenset(review.uncertainty_decisions),
            creation_reference_ids={c.bu_name: c.reference_id for c in review.creations})
    else:
        checked = review_updates(baseline, requests, expected_baseline_sha256=baseline.source_sha256,
            application_validation_decisions=frozenset(review.uncertainty_decisions))
    if checked != review:
        raise TaskError("Design rows, changes or decisions differ from recomputed preflight")
    return checked


def build_candidate(baseline_bytes: bytes, review: ReviewedUpdates) -> bytes:
    """Prepare an offline native FSM source from a separately confirmed design.

    The trusted caller owns design confirmation and later Core approval. This
    pure function grants neither. Never call it to alter a pending Core session.
    It preserves metadata bytes and member order; CSV logical values are
    serialized deterministically with explicit trailing blanks.
    """
    baseline = read_export(baseline_bytes, environment=review.baseline.environment,
                           release=review.baseline.release)
    _checked_review(baseline, review)
    with zipfile.ZipFile(io.BytesIO(baseline_bytes)) as original:
        names = original.namelist()
        metadata = original.read(XML_MEMBER)
        bom = original.read(CSV_MEMBER).startswith(b"\xef\xbb\xbf")
    csv_text = io.StringIO(newline="")
    writer = csv.writer(csv_text, lineterminator="\r\n")
    writer.writerow(HEADERS)
    writer.writerows(review.rows)
    csv_bytes = (b"\xef\xbb\xbf" if bom else b"") + csv_text.getvalue().encode("utf-8")
    content = {CSV_MEMBER: csv_bytes, XML_MEMBER: metadata}
    output = io.BytesIO()
    # Stored entries avoid compressor-version variability in this local format.
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in names:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o600 << 16
            archive.writestr(info, content[name])
    candidate = output.getvalue()
    if len(candidate) > MAX_EXPORT_BYTES:
        raise TaskError("Candidate exceeds this helper's local memory bound")
    validate_candidate(candidate, baseline_bytes, review)
    return candidate


def validate_candidate(candidate_bytes: bytes, baseline_bytes: bytes,
                       review: ReviewedUpdates) -> dict:
    """Independently inspect exact candidate values and all preservation rules."""
    baseline = read_export(baseline_bytes, environment=review.baseline.environment,
                           release=review.baseline.release)
    _checked_review(baseline, review)
    candidate = read_export(candidate_bytes, environment=baseline.environment, release=baseline.release)
    with zipfile.ZipFile(io.BytesIO(baseline_bytes)) as original, \
            zipfile.ZipFile(io.BytesIO(candidate_bytes)) as prepared:
        if (original.namelist() != prepared.namelist()
                or original.read(XML_MEMBER) != prepared.read(XML_MEMBER)):
            raise TaskError("Candidate metadata bytes or member order changed")
    if candidate.rows != review.rows:
        raise TaskError("Candidate differs from requested values or preservation requirements")
    result = {"valid": True, "taskCode": TASK, "rows": len(candidate.rows),
            "changedRows": len({c.bu_name for c in review.changes} | {c.bu_name for c in review.creations}),
            "changedFields": len(review.changes) + sum(len(c.values) + 1 for c in review.creations), "sha256": hashlib.sha256(candidate_bytes).hexdigest(),
            "applicationValidationDecisions": len(review.uncertainty_decisions),
            "importOutcome": "not_run", "approvalGranted": False}
    if review.creations:
        result.update(createdRows=len(review.creations), updatedRows=len({c.bu_name for c in review.changes}))
    return result


def determinism(baseline_bytes: bytes, review: ReviewedUpdates) -> dict:
    first, second = build_candidate(baseline_bytes, review), build_candidate(baseline_bytes, review)
    if first != second:
        raise TaskError("Repeated candidate preparation differs")
    return {"identical": True, "sha256": hashlib.sha256(first).hexdigest(), "builds": 2}


def reverse_review(forward: ReviewedUpdates, fresh_bytes: bytes, *,
                   application_validation_decisions: frozenset[tuple[str, str, str]] = frozenset()
                   ) -> ReviewedUpdates:
    """Prepare a narrow new reverse design; never authorize restoration or reuse approval."""
    _checked_review(forward.baseline, forward)
    if forward.creations:
        raise EvidenceUnresolved("Created rows have no before-values; no supported CSV deletion/absence restoration")
    fresh = read_export(fresh_bytes, environment=forward.baseline.environment,
                        release=forward.baseline.release)
    if not reconcile(forward, fresh)["comparisonMatch"]:
        raise TaskError("Fresh post-forward state drifted; investigate before reverse update")
    groups: dict[str, dict[str, str]] = {}
    for change in forward.changes:
        groups.setdefault(change.bu_name, {})[change.field] = change.before
    requests = [{"operation": "update", "scope": "enterprise" if key == "" else "business_unit",
                 "buName": key, "changes": fields} for key, fields in groups.items()]
    return review_updates(fresh, requests, expected_baseline_sha256=fresh.source_sha256,
                          application_validation_decisions=application_validation_decisions)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--release", required=True)
    args = parser.parse_args()
    try:
        if args.export.stat().st_size > MAX_EXPORT_BYTES:
            raise TaskError("Export exceeds this reader's memory bound")
        snapshot = read_export(args.export.read_bytes(), environment=args.environment, release=args.release)
        print(json.dumps({"task": TASK, "rows": len(snapshot.rows), "columns": len(HEADERS),
                          "enterpriseRows": 1, "sourceSHA256": snapshot.source_sha256,
                          "mutationAttempted": False}))
        return 0
    except (OSError, TaskError) as exc:
        print(json.dumps({"status": "FAILED", "error": str(exc), "mutationAttempted": False}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
