"""Validate reference evidence captured through the shared read-only REST client.

This module performs no network, authentication, or mutation operation.
"""

from datetime import date, datetime, timezone


ROOT = "/fscmRestApi/resources/11.13.18.05/"
CATEGORY_PATH = ROOT + "standardLookups/EXM_EXPENSE_TYPE_CATEGORY/child/lookupCodes"
BU_PATH = ROOT + "finBusinessUnitsLOV"
LEDGER_PATH = ROOT + "ledgersLOV"


def batch(evidence, name, environment, baseline_sha256, path):
    entry = evidence.get(name, {})
    if (entry.get("environment") != environment
            or entry.get("baseline_sha256") != baseline_sha256
            or entry.get("path") != path or entry.get("http_status") != 200
            or entry.get("complete") is not True or not isinstance(entry.get("items"), list)):
        raise ValueError(f"{name}: complete same-environment REST evidence bound to this baseline is required")
    try:
        captured = datetime.fromisoformat(entry["captured_at"].replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - captured).total_seconds()
        if captured.tzinfo is None or not 0 <= age <= 86400:
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"{name}: capture time must be offset-aware and within 24 hours") from None
    if any(not isinstance(row, dict) for row in entry["items"]):
        raise ValueError(f"{name}: invalid REST item")
    return entry["items"]


def unique(rows, field, value, label):
    matches = [row for row in rows if str(row.get(field, "")) == str(value)]
    if len(matches) != 1:
        raise ValueError(f"{label}: expected one exact REST match; found {len(matches)}")
    return matches[0]


def effective_date(value, field):
    if value is None:
        return None
    try:
        parsed = date.fromisoformat(value) if isinstance(value, str) else None
        if parsed is None or parsed.isoformat() != value:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValueError(f"categories: {field} must be null or a valid YYYY-MM-DD date") from None
    return parsed


def categories(evidence, environment, baseline_sha256):
    rows = batch(evidence, "categories", environment, baseline_sha256, CATEGORY_PATH)
    today = datetime.now(timezone.utc).date()
    codes, labels = set(), {}
    for row in rows:
        code = row.get("LookupCode")
        if not isinstance(code, str) or not code or code in codes:
            raise ValueError("categories: missing or duplicate LookupCode")
        if "StartDateActive" not in row or "EndDateActive" not in row or row.get("EnabledFlag") not in {"Y", "N"}:
            raise ValueError("categories: missing enabled flag or effective-date attributes")
        start = effective_date(row["StartDateActive"], "StartDateActive")
        end = effective_date(row["EndDateActive"], "EndDateActive")
        if start is not None and end is not None and end < start:
            raise ValueError("categories: EndDateActive precedes StartDateActive")
        if row["EnabledFlag"] != "Y":
            continue
        if start is not None and start > today:
            continue
        if end is not None and end < today:
            continue
        codes.add(code)
        for label in (code, row.get("Meaning")):
            if label:
                key = str(label).casefold()
                if key in labels and labels[key] != code:
                    raise ValueError("categories: ambiguous business label")
                labels[key] = code
    return codes, labels


def business_unit(evidence, environment, baseline_sha256, name):
    row = unique(batch(evidence, "business_units", environment, baseline_sha256, BU_PATH),
                 "BusinessUnitName", name, "business unit")
    if not row.get("BusinessUnitId") or row.get("ActiveFlag") is not True:
        raise ValueError("business unit: an active destination business unit is required")
    return row


def ledger_name(evidence, environment, baseline_sha256, bu):
    ledger_id = bu.get("PrimaryLedgerId")
    if not ledger_id:
        raise ValueError("business unit: PrimaryLedgerId is required to resolve the expense account")
    row = unique(batch(evidence, "ledgers", environment, baseline_sha256, LEDGER_PATH),
                 "LedgerId", ledger_id, "primary ledger")
    if not isinstance(row.get("Name"), str) or not row["Name"].strip():
        raise ValueError("primary ledger: Name is required")
    return row["Name"]
