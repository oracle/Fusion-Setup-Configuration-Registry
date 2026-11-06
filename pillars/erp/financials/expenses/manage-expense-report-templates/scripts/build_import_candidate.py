#!/usr/bin/env python3
"""Build a Manage Expense Report Templates FSM import ZIP from a fresh export."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from copy import deepcopy
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any
import reference_values


TASK_CODE = "EXM_MANAGE_EXPENSE_REPORT_TEMPLATES"
TEMPLATE_MEMBER = "EXM_EXPENSE_TEMPLATE.csv"
TYPE_MEMBER = "EXM_EXPENSE_TYPE.csv"
ITEMIZATION_MEMBER = "EXM_EXPENSE_TYPE_ITEMIZATION.csv"
PROJECT_MEMBER = "EXM_PROJECT_EXP_TYPE_MAP.csv"
METADATA_MEMBER = "ASM_SETUP_CSV_METADATA.xml"
REQUIRED_MEMBERS = {TEMPLATE_MEMBER, TYPE_MEMBER, METADATA_MEMBER}
WHO_COLUMNS = {
    "CreatedBy",
    "CreationDate",
    "LastUpdatedBy",
    "LastUpdateDate",
    "LastUpdateLogin",
}
TEMPLATE_FIELDS = {
    "description": "Description",
    "start_date": "StartDate",
    "inactive_date": "InactiveDate",
}
TYPE_FIELDS = {
    "description": "Description",
    "start_date": "StartDate",
    "end_date": "EndDate",
    "tax_classification_code": "TaxClassificationCode",
    "category_code": "CategoryCode",
    "ledger_name": "LedgerName",
    "expenditure_type_name": "ExpenditureTypeName",
    "tax_product_category_code": "TaxProductCategoryCode",
}
TEMPLATE_RECEIPT_FIELDS = {
    "cash_receipt_required": "CashReceiptReqFlag",
    "cash_receipt_threshold": "CashReceiptReqLimit",
    "allow_missing_receipt": "AllowRcptMissingFlag",
    "negative_line_receipt_required": "NegativeRcptReqFlag",
    "receipt_warning": "DispRcptViolationFlag",
}
TYPE_RECEIPT_FIELDS = {
    "cash_receipt_required": "ReceiptRequiredFlag",
    "cash_receipt_threshold": "ReceiptThreshold",
    "negative_line_receipt_required": "NegativeRcptReqCode",
    "project_receipt_required": "RcptRequiredProjFlag",
    "receipt_warning": "DispRcptViolationFlag",
}
TEMPLATE_BEHAVIOR_FIELDS = {
    "description": "DescriptionBehaviourCode",
    "expense_location": "LocationBehaviourCode",
    "merchant_name": "MerchantBehaviourCode",
    "number_of_days": "NumOfDaysBehaviourCode",
}
TYPE_BEHAVIOR_FIELDS = TEMPLATE_BEHAVIOR_FIELDS
BEHAVIOR_CODES = {
    "required": "REQUIRED",
    "optional": "ENABLED",
    "enabled": "ENABLED",
    "hidden": "DISABLED",
    "disabled": "DISABLED",
    "no override": "",
    "none": "",
    "blank": "",
}
ITEMIZATION_CODES = {
    "required": "REQUIRED",
    "optional": "ENABLED",
    "enabled": "ENABLED",
    "not required": "DISABLED",
    "disabled": "DISABLED",
}
DATE_KEYS = {"start_date", "inactive_date", "end_date"}
NUMBER_KEYS = {"cash_receipt_threshold"}
SIMPLE_FIELD_LIMITS = {
    "description": 240,
    "tax_classification_code": 30,
    "category_code": 30,
    "tax_product_category_code": 240,
}


class CandidateBuildError(ValueError):
    """The baseline or normalized design cannot produce a safe candidate."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256_bytes(encoded)


def require_text(value: Any, label: str, *, maximum: int | None = None) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CandidateBuildError(f"{label} must be a nonblank string.")
    result = value.strip()
    if maximum is not None and len(result) > maximum:
        raise CandidateBuildError(f"{label} exceeds the {maximum}-character limit.")
    return result


def optional_text(value: Any, label: str, *, maximum: int | None = None) -> str:
    if value is None or value == "":
        return ""
    if not isinstance(value, str):
        raise CandidateBuildError(f"{label} must be a string or null.")
    result = value.strip()
    if maximum is not None and len(result) > maximum:
        raise CandidateBuildError(f"{label} exceeds the {maximum}-character limit.")
    return result


def require_keys(value: dict[str, Any], required: set[str], label: str) -> None:
    missing = sorted(required - set(value))
    if missing:
        raise CandidateBuildError(f"{label} is missing normalized fields: {', '.join(missing)}")


def reject_unknown(value: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise CandidateBuildError(f"{label} contains unsupported fields: {', '.join(unknown)}")


def validate_resulting_row(row: dict[str, str], *, template: bool, label: str) -> None:
    """Validate final values, including values retained from an edit baseline."""
    start = row.get("StartDate", "")
    if not start:
        raise CandidateBuildError(f"{label}.start_date is required; select an explicit date.")
    start = date_value(start, f"{label}.start_date")
    end = row.get("InactiveDate" if template else "EndDate", "")
    if end and date_value(end, f"{label}.end_date") < start:
        raise CandidateBuildError(f"{label} end date cannot precede start date.")
    required = row.get("CashReceiptReqFlag" if template else "ReceiptRequiredFlag")
    threshold = row.get("CashReceiptReqLimit" if template else "ReceiptThreshold")
    if required == "Y" and not threshold:
        raise CandidateBuildError(f"{label}.cash_receipt_threshold is required when the resulting receipt flag is Yes.")
    if threshold:
        number(threshold, f"{label}.cash_receipt_threshold")
    if not template and row.get("EnableProjectsFlag") == "Y" and not row.get("ExpenditureTypeName"):
        raise CandidateBuildError(f"{label} requires a resolved default project expenditure type when Projects is Enabled.")


def flag(value: Any, label: str) -> str:
    if isinstance(value, bool):
        return "Y" if value else "N"
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized in {"yes", "y", "true"}:
            return "Y"
        if normalized in {"no", "n", "false"}:
            return "N"
    raise CandidateBuildError(f"{label} must be Yes/No or a Boolean.")


def number(value: Any, label: str) -> str:
    if value is None or value == "":
        return ""
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise CandidateBuildError(f"{label} must be a valid number or null.") from error
    if not parsed.is_finite():
        raise CandidateBuildError(f"{label} must be a finite number.")
    return format(parsed, "f")


def date_value(value: Any, label: str) -> str:
    if value is None or value == "":
        return ""
    text = require_text(value, label)
    match = re.fullmatch(r"(\d{4})[-/](\d{2})[-/](\d{2})", text)
    if not match:
        raise CandidateBuildError(f"{label} must use YYYY-MM-DD.")
    year, month, day = (int(part) for part in match.groups())
    try:
        from datetime import date

        date(year, month, day)
    except ValueError as error:
        raise CandidateBuildError(f"{label} is not a valid calendar date.") from error
    return f"{year:04d}/{month:02d}/{day:02d}"


def behavior(value: Any, label: str) -> str:
    text = require_text(value, label).casefold()
    if text not in BEHAVIOR_CODES:
        raise CandidateBuildError(f"{label} must be Required, Optional, Hidden, No override, or Blank.")
    return BEHAVIOR_CODES[text]


def omit_blank_behavior_values(values: dict[str, Any]) -> dict[str, Any]:
    """Normalize the workbook's Blank dropdown choice to an omitted input."""
    return {
        key: value
        for key, value in values.items()
        if not (isinstance(value, str) and value.strip().casefold() == "blank")
    }


def itemization(value: Any, label: str) -> str:
    text = require_text(value, label).casefold()
    if text not in ITEMIZATION_CODES:
        raise CandidateBuildError(f"{label} must be Disabled, Enabled, or Required.")
    return ITEMIZATION_CODES[text]


def read_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CandidateBuildError(f"{label} is unreadable JSON: {path}") from error
    if not isinstance(value, dict):
        raise CandidateBuildError(f"{label} must contain a JSON object.")
    return value


def validate_member_name(name: str) -> None:
    member = PurePosixPath(name)
    if member.is_absolute() or ".." in member.parts or name.endswith("/"):
        raise CandidateBuildError(f"Unsafe or unsupported ZIP member path: {name}")
    if len(member.parts) != 1:
        raise CandidateBuildError(f"FSM ZIP members must be at the archive root: {name}")


def read_baseline(path: Path) -> tuple[list[zipfile.ZipInfo], dict[str, bytes]]:
    if not path.is_file():
        raise CandidateBuildError(f"Baseline ZIP does not exist: {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise CandidateBuildError("Baseline ZIP contains duplicate member names.")
            for name in names:
                validate_member_name(name)
            missing = sorted(REQUIRED_MEMBERS - set(names))
            if missing:
                raise CandidateBuildError(f"Baseline ZIP is missing required members: {', '.join(missing)}")
            bad = archive.testzip()
            if bad:
                raise CandidateBuildError(f"Baseline ZIP integrity failed for member: {bad}")
            return infos, {name: archive.read(name) for name in names}
    except zipfile.BadZipFile as error:
        raise CandidateBuildError(f"Baseline is not a valid ZIP archive: {path}") from error


def read_csv_member(content: bytes, name: str) -> tuple[list[str], list[dict[str, str]]]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise CandidateBuildError(f"{name} must use UTF-8 encoding.") from error
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise CandidateBuildError(f"{name} has a missing or duplicate CSV header.")
    rows: list[dict[str, str]] = []
    for row_number, row in enumerate(reader, start=2):
        if None in row:
            raise CandidateBuildError(f"{name} row {row_number} has more values than the header.")
        rows.append({field: row.get(field, "") or "" for field in reader.fieldnames})
    return list(reader.fieldnames), rows


def write_csv_member(fields: list[str], rows: list[dict[str, str]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="raise", lineterminator="\r\n", quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def require_columns(fields: list[str], required: set[str], member: str) -> None:
    missing = sorted(required - set(fields))
    if missing:
        raise CandidateBuildError(f"{member} is missing required columns: {', '.join(missing)}")


def blank_row(fields: list[str]) -> dict[str, str]:
    return {field: "" for field in fields}


def matching_indexes(rows: list[dict[str, str]], **criteria: str) -> list[int]:
    return [
        index
        for index, row in enumerate(rows)
        if all((row.get(field) or "").strip().casefold() == value.strip().casefold() for field, value in criteria.items())
    ]


def apply_simple_fields(row: dict[str, str], source: dict[str, Any], mapping: dict[str, str], prefix: str) -> None:
    for key, column in mapping.items():
        if key not in source:
            continue
        value = source[key]
        if key in DATE_KEYS:
            row[column] = date_value(value, f"{prefix}.{key}")
        else:
            row[column] = optional_text(
                value,
                f"{prefix}.{key}",
                maximum=SIMPLE_FIELD_LIMITS.get(key),
            )


def apply_receipt_fields(
    row: dict[str, str], source: dict[str, Any], mapping: dict[str, str], prefix: str
) -> None:
    for key, column in mapping.items():
        if key not in source:
            continue
        row[column] = (
            number(source[key], f"{prefix}.{key}")
            if key in NUMBER_KEYS
            else ("" if source[key] is None else flag(source[key], f"{prefix}.{key}"))
        )
    # Validate the resulting row below: an Edit may retain an existing threshold.


def apply_behavior_fields(
    row: dict[str, str], source: dict[str, Any], mapping: dict[str, str], prefix: str
) -> None:
    for key, column in mapping.items():
        if key in source:
            row[column] = "" if source[key] is None else behavior(source[key], f"{prefix}.{key}")


def require_cash_only(row: dict[str, str], label: str) -> None:
    """Do not silently convert selected card-enabled records into cash-only ones."""
    flags = ("EnableCcMappingFlag", "CcReceiptReqFlag", "CcReceiptRequiredFlag")
    refs = ("CcReceiptReqLimit", "CcReceiptThreshold", "ExpenseTypeName", "VirtualCardProgramId", "VirtualCardProgramName")
    if any(row.get(k, "").upper() not in {"", "N"} for k in flags) or any(row.get(k, "") for k in refs):
        raise CandidateBuildError(f"{label} has corporate-card configuration and is outside this cash-only edit workflow.")


def seed_category_map(seed_reference_path: Path) -> dict[str, str]:
    """Read category-code hints from the task-local Markdown seed table."""
    try:
        source = seed_reference_path.read_text(encoding="utf-8")
    except OSError as error:
        raise CandidateBuildError(
            f"Unable to read expense template seed reference {seed_reference_path}: {error}"
        ) from error

    section_match = re.search(
        r"^### Category Type Seed Data\s*$([\s\S]*?)(?=^## |\Z)",
        source,
        flags=re.MULTILINE,
    )
    if section_match is None:
        raise CandidateBuildError(
            "Expense template seed reference lacks the Category Type Seed Data section."
        )

    expected_columns = ["Seed ID", "Display Name", "Category Value", "Category Code"]
    header_found = False
    result: dict[str, str] = {}
    for line in section_match.group(1).splitlines():
        if not line.startswith("|"):
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if columns[:4] == expected_columns:
            header_found = True
            continue
        if not header_found or not columns or all(re.fullmatch(r":?-{3,}:?", column) for column in columns):
            continue
        if len(columns) < 4:
            raise CandidateBuildError(
                "Expense template seed reference has an incomplete Category Type Seed Data row."
            )
        display_name, category_value, category_code = columns[1:4]
        category_code = category_code.strip("`").strip().upper()
        if not display_name or not category_value or not category_code:
            raise CandidateBuildError(
                "Expense template seed reference has a Category Type Seed Data row with a missing display name, category value, or category code."
            )
        for key in (display_name, category_value):
            result[key.casefold()] = category_code

    if not header_found:
        raise CandidateBuildError(
            "Expense template seed reference lacks the Category Type Seed Data table header."
        )
    if not result:
        raise CandidateBuildError(
            "Expense template seed reference has no Category Type Seed Data rows."
        )
    return result


def resolve_category_code(
    value: dict[str, Any], available: set[str], seed_map: dict[str, str], label: str,
    *, require_explicit: bool = False,
) -> str:
    explicit = value.get("category_code")
    category_value = value.get("category_value")
    if explicit is None and (category_value is None or category_value == ""):
        return ""
    if explicit is not None:
        code = require_text(explicit, f"{label}.category_code", maximum=30)
    else:
        if require_explicit:
            raise CandidateBuildError(f"{label} requires an explicitly resolved category_code; a category label is not an import code.")
        submitted = require_text(category_value, f"{label}.category_value", maximum=80)
        normalized = re.sub(r"[^A-Z0-9]+", "_", submitted.upper()).strip("_")
        if normalized in available:
            code = normalized
        else:
            code = seed_map.get(submitted.casefold(), "")
    if not code or code not in available:
        choices = ", ".join(sorted(available)) or "(none)"
        raise CandidateBuildError(
            f"{label} category does not resolve to an active destination lookup code. Available codes: {choices}."
        )
    return code


def changed_fields(before: dict[str, str] | None, after: dict[str, str]) -> dict[str, dict[str, str]]:
    if before is None:
        return {key: {"before": "", "after": value} for key, value in after.items() if value}
    return {
        key: {"before": before.get(key, ""), "after": value}
        for key, value in after.items()
        if before.get(key, "") != value
    }


def row_hash(row: dict[str, str], fields: list[str]) -> str:
    return canonical_json_sha256([row.get(field, "") for field in fields])


def build_template_row(
    fields: list[str], rows: list[dict[str, str]], business_unit: str, template: dict[str, Any],
    operation: str, label: str, *, cash_only: bool = False,
) -> tuple[dict[str, str], dict[str, str] | None, int | None]:
    reject_unknown(template, {
        "operation", "business_unit", "name", "match_name", "expense_types",
        "default_template_intent", "receipt_rules", "field_behaviors", *TEMPLATE_FIELDS,
    }, label)
    name = require_text(template.get("name"), f"{label}.name", maximum=80)
    match_name = require_text(template.get("match_name", name), f"{label}.match_name", maximum=80)
    matches = matching_indexes(rows, BuName=business_unit, Name=match_name)
    if operation == "create":
        if matches:
            raise CandidateBuildError(f"Template {name!r} already exists for business unit {business_unit!r}.")
        row = blank_row(fields)
        before = None
        index = None
        require_keys(
            template,
            {
                "description",
                "start_date",
                "inactive_date",
                "default_template_intent",
                "receipt_rules",
                "field_behaviors",
            },
            f"Create {label}",
        )
    else:
        if len(matches) != 1:
            raise CandidateBuildError(
                f"Edit requires exactly one template match for {match_name!r} in {business_unit!r}; found {len(matches)}."
            )
        if name.casefold() != match_name.casefold():
            raise CandidateBuildError("Template rename is unsupported because related mapping identities must remain preserved.")
        index = matches[0]
        before = deepcopy(rows[index])
        row = deepcopy(before)
        if cash_only:
            require_cash_only(before, label)
    row["BuName"] = business_unit
    row["Name"] = name
    apply_simple_fields(row, template, TEMPLATE_FIELDS, label)
    receipt_rules = template.get("receipt_rules", {})
    field_behaviors = template.get("field_behaviors", {})
    if not isinstance(receipt_rules, dict) or not isinstance(field_behaviors, dict):
        raise CandidateBuildError(f"{label} receipt_rules and field_behaviors must be JSON objects.")
    reject_unknown(receipt_rules, set(TEMPLATE_RECEIPT_FIELDS), f"{label}.receipt_rules")
    reject_unknown(field_behaviors, set(TEMPLATE_BEHAVIOR_FIELDS), f"{label}.field_behaviors")
    field_behaviors = omit_blank_behavior_values(field_behaviors)
    if cash_only and operation == "edit":
        if any(v is None for k, v in receipt_rules.items() if k not in NUMBER_KEYS) or any(v is None for v in field_behaviors.values()):
            raise CandidateBuildError("Edit controls are not nullable; omit unchanged controls instead of clearing them.")
    if operation == "create":
        require_keys(receipt_rules, set(TEMPLATE_RECEIPT_FIELDS), f"Create {label} receipt_rules")
        require_keys(field_behaviors, set(TEMPLATE_BEHAVIOR_FIELDS), f"Create {label} field_behaviors")
    apply_receipt_fields(row, receipt_rules, TEMPLATE_RECEIPT_FIELDS, f"{label}.receipt_rules")
    apply_behavior_fields(row, field_behaviors, TEMPLATE_BEHAVIOR_FIELDS, f"{label}.field_behaviors")
    if cash_only and any(str(v).strip().casefold() in {"no override", "none"} for v in field_behaviors.values()):
        raise CandidateBuildError("Template field behaviors do not accept No override.")
    default_intent = template.get("default_template_intent")
    if default_intent not in (None, "", False, "No", "no", "N", "n"):
        raise CandidateBuildError("Creating or changing a default template is not supported by this cash-only candidate builder.")
    if operation == "create":
        row.update(
            {
                "CcReceiptReqLimit": "",
                "CcReceiptReqFlag": "N",
                "EnableCcMappingFlag": "N",
                "ExpenseTypeName": "",
                **{column: "" for column in WHO_COLUMNS if column in row},
            }
        )
    validate_resulting_row(row, template=True, label=label)
    return row, before, index


def build_type_row(
    fields: list[str], rows: list[dict[str, str]], business_unit: str, template: dict[str, Any],
    template_operation: str, item: dict[str, Any], seed_map: dict[str, str],
    available_categories: set[str], label: str, *, require_explicit_category: bool = False,
    cash_only_no_account_or_projects: bool = False,
    tax_fields_empty: bool = False,
) -> tuple[str, dict[str, str], dict[str, str] | None, int | None]:
    allowed = {
        "operation", "name", "match_name", "category_value", "account_number", "itemization", "project_use",
        "prepaid", "itemization_only", "flexfield_segments", "receipt_rules", "field_behaviors", *TYPE_FIELDS,
    }
    reject_unknown(item, allowed, f"{label}.expense_type")
    restricted_inputs = {"project_use", "ledger_name", "expenditure_type_name", "flexfield_segments"}
    if tax_fields_empty:
        restricted_inputs |= {"tax_classification_code", "tax_product_category_code"}
    supplied_restricted = sorted(restricted_inputs & set(item))
    if (cash_only_no_account_or_projects or tax_fields_empty) and supplied_restricted:
        fixed_values = "null account and tax values" if tax_fields_empty else "a null account"
        raise CandidateBuildError(
            f"{label}.expense_type cannot supply {', '.join(supplied_restricted)}; "
            f"this workbook format imports {fixed_values} with Projects disabled."
        )
    template_name = require_text(template.get("name"), f"{label}.name", maximum=80)
    operation = str(item.get("operation", "create" if template_operation == "create" else "edit")).strip().casefold()
    if operation not in {"create", "edit", "preserve"}:
        raise CandidateBuildError("Expense type operation must be create, edit, or preserve.")
    name = require_text(item.get("name"), f"{label}.expense_types[].name", maximum=80)
    match_name = require_text(item.get("match_name", name), f"{label}.expense_types[].match_name", maximum=80)
    matches = matching_indexes(
        rows,
        **{
            "EXM_EXPENSE_TEMPLATE.BuName": business_unit,
            "EXM_EXPENSE_TEMPLATE.Name": template_name,
            "Name": match_name,
        },
    )
    if operation == "create":
        if matches:
            raise CandidateBuildError(f"Expense type {name!r} already exists under template {template_name!r}.")
        row = blank_row(fields)
        before = None
        index = None
        required_create = {
            "description",
            "start_date",
            "end_date",
            "tax_classification_code",
            "itemization",
            "project_use",
            "ledger_name",
            "expenditure_type_name",
            "prepaid",
            "tax_product_category_code",
            "flexfield_segments",
            "receipt_rules",
            "field_behaviors",
        }
        if cash_only_no_account_or_projects:
            required_create -= {"project_use", "ledger_name", "expenditure_type_name", "flexfield_segments"}
        if tax_fields_empty:
            required_create -= {"tax_classification_code", "tax_product_category_code"}
        if "category_code" not in item:
            required_create.add("category_value")
        require_keys(item, required_create, f"Create expense type {name!r}")
    else:
        if len(matches) != 1:
            raise CandidateBuildError(
                f"{operation.title()} requires exactly one expense type match for {match_name!r}; found {len(matches)}."
            )
        if name.casefold() != match_name.casefold():
            raise CandidateBuildError("Expense type rename is unsupported because related mapping identities must remain preserved.")
        index = matches[0]
        before = deepcopy(rows[index])
        row = deepcopy(before)
        if require_explicit_category:
            require_cash_only(before, label)
        if operation == "preserve":
            if set(item) - {"operation", "name", "match_name"}:
                raise CandidateBuildError("A preserved expense type cannot also contain requested changes.")
            return operation, row, before, index
    row.update(
        {
            "EXM_EXPENSE_TEMPLATE.BuName": business_unit,
            "EXM_EXPENSE_TEMPLATE.Name": template_name,
            "BuName": business_unit,
            "TemplateName": template_name,
            "Name": name,
        }
    )
    type_label = f"{label}.expense_types[{name}]"
    if require_explicit_category and operation == "edit" and any(k in item and item[k] is None for k in ("itemization", "project_use", "prepaid", "itemization_only")):
        raise CandidateBuildError("Edit controls are not nullable; omit unchanged controls instead of clearing them.")
    apply_simple_fields(row, item, TYPE_FIELDS, type_label)
    if "category_code" in item or "category_value" in item:
        row["CategoryCode"] = resolve_category_code(item, available_categories, seed_map, type_label,
                                                   require_explicit=require_explicit_category)
    if "itemization" in item:
        row["ItemizationBehaviourCode"] = "" if item["itemization"] is None else itemization(item["itemization"], f"{type_label}.itemization")
    if "project_use" in item:
        row["EnableProjectsFlag"] = "" if item["project_use"] is None else flag(item["project_use"], f"{type_label}.project_use")
    if "prepaid" in item:
        row["PrepaidFlag"] = "" if item["prepaid"] is None else flag(item["prepaid"], f"{type_label}.prepaid")
    receipt_rules = item.get("receipt_rules", {})
    field_behaviors = item.get("field_behaviors", {})
    if not isinstance(receipt_rules, dict) or not isinstance(field_behaviors, dict):
        raise CandidateBuildError(f"{type_label} receipt_rules and field_behaviors must be JSON objects.")
    reject_unknown(receipt_rules, set(TYPE_RECEIPT_FIELDS), f"{type_label}.receipt_rules")
    if cash_only_no_account_or_projects and "project_receipt_required" in receipt_rules:
        raise CandidateBuildError(
            f"{type_label}.receipt_rules.project_receipt_required is not collected; "
            "Projects is disabled for this workbook format."
        )
    if require_explicit_category and operation == "edit" and any(v is None for k, v in receipt_rules.items() if k not in NUMBER_KEYS):
        raise CandidateBuildError("Edit receipt flags are not nullable; omit unchanged flags instead of clearing them.")
    reject_unknown(field_behaviors, set(TYPE_BEHAVIOR_FIELDS), f"{type_label}.field_behaviors")
    field_behaviors = omit_blank_behavior_values(field_behaviors)
    if operation == "create":
        required_receipt_rules = set(TYPE_RECEIPT_FIELDS)
        if cash_only_no_account_or_projects:
            required_receipt_rules.discard("project_receipt_required")
        require_keys(receipt_rules, required_receipt_rules, f"Create expense type {name!r} receipt_rules")
        require_keys(field_behaviors, set(TYPE_BEHAVIOR_FIELDS), f"Create expense type {name!r} field_behaviors")
    apply_receipt_fields(row, receipt_rules, TYPE_RECEIPT_FIELDS, f"{type_label}.receipt_rules")
    apply_behavior_fields(row, field_behaviors, TYPE_BEHAVIOR_FIELDS, f"{type_label}.field_behaviors")
    segments = item.get("flexfield_segments", {})
    if not isinstance(segments, dict):
        raise CandidateBuildError(f"{type_label}.flexfield_segments must be a JSON object.")
    for key, value in segments.items():
        match = re.fullmatch(r"segment(\d+)", key, re.IGNORECASE)
        if not match:
            raise CandidateBuildError(f"Unsupported flexfield segment key: {key}")
        column = f"Segment{int(match.group(1))}"
        if column not in fields:
            raise CandidateBuildError(f"Fresh task CSV schema does not support {column}.")
        row[column] = optional_text(value, f"{type_label}.{key}", maximum=25)
    if operation == "create":
        row.update(
            {
                "CcReceiptRequiredFlag": "N",
                "CcReceiptThreshold": "",
                "ItemizationOnlyFlag": "N",
                **{column: "" for column in WHO_COLUMNS if column in row},
            }
        )
    if "itemization_only" in item:
        row["ItemizationOnlyFlag"] = "" if item["itemization_only"] is None else flag(item["itemization_only"], f"{type_label}.itemization_only")
    if cash_only_no_account_or_projects:
        # Account fields preserve the baseline on edits. New accounts are
        # resolved by the caller from the BU's primary ledger, never user input.
        for column in fields:
            if column == "ExpenditureTypeName":
                row[column] = ""
        row["EnableProjectsFlag"] = "N"
        if "RcptRequiredProjFlag" in row:
            row["RcptRequiredProjFlag"] = "N"
    if tax_fields_empty:
        # Current workbook intake deliberately has no tax inputs.
        for column in ("TaxClassificationCode", "TaxProductCategoryCode"):
            if column in row:
                row[column] = ""
    validate_resulting_row(row, template=False, label=type_label)
    return operation, row, before, index


def normalized_templates(design: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the multi-template shape, accepting legacy v1.0 and v1.1 designs."""
    schema_version = design.get("schema_version")
    if schema_version == "1.0":
        legacy_template = design.get("template")
        legacy_types = design.get("expense_types", [])
        legacy_operation = str(design.get("operation", "")).strip().casefold()
        if not isinstance(legacy_template, dict) or not isinstance(legacy_types, list):
            raise CandidateBuildError("v1.0 designs require template and expense_types values.")
        if legacy_operation not in {"create", "edit"}:
            raise CandidateBuildError("v1.0 design.operation must be create or edit.")
        template = deepcopy(legacy_template)
        template["operation"] = legacy_operation
        template["expense_types"] = legacy_types
        return [template]
    if schema_version not in {"1.1", "1.2", "1.3", "1.4", "1.5"}:
        raise CandidateBuildError("design.schema_version must be 1.0, 1.1, 1.2, 1.3, 1.4, or 1.5.")
    templates = design.get("templates")
    if not isinstance(templates, list) or not templates:
        raise CandidateBuildError(f"v{schema_version} designs require a nonempty templates array.")
    if "template" in design or "expense_types" in design or "operation" in design:
        raise CandidateBuildError(f"v{schema_version} designs store operation and expense_types inside each templates item.")
    result: list[dict[str, Any]] = []
    seen_template_keys: set[tuple[str, str]] = set()
    batch_operation: str | None = None
    for index, value in enumerate(templates, start=1):
        if not isinstance(value, dict):
            raise CandidateBuildError(f"templates[{index}] must be a JSON object.")
        template = deepcopy(value)
        if schema_version == "1.5":
            if "operation" in template:
                raise CandidateBuildError("v1.5 operation-free designs must not include a template operation.")
        else:
            operation = str(template.get("operation", "")).strip().casefold()
            if operation not in {"create", "edit"}:
                raise CandidateBuildError(f"templates[{index}].operation must be create or edit.")
            if batch_operation is not None and operation != batch_operation:
                raise CandidateBuildError(f"v{schema_version} batches cannot mix create and edit template operations.")
            batch_operation = operation
            template["operation"] = operation
        name = require_text(template.get("name"), f"templates[{index}].name", maximum=80)
        if schema_version in {"1.2", "1.3", "1.4", "1.5"}:
            business_unit = require_text(
                template.get("business_unit"), f"templates[{index}].business_unit", maximum=240
            )
        else:
            business_unit = require_text(design.get("business_unit"), "business_unit", maximum=240)
        identity = (business_unit.casefold(), name.casefold())
        if identity in seen_template_keys:
            raise CandidateBuildError(
                f"Duplicate template in normalized design for business unit {business_unit!r}: {name}"
            )
        seen_template_keys.add(identity)
        expense_types = template.get("expense_types", [])
        if not isinstance(expense_types, list):
            raise CandidateBuildError(f"templates[{index}].expense_types must be a JSON array.")
        result.append(template)
    return result


def validate_design(design: dict[str, Any], baseline_sha256: str) -> list[dict[str, Any]]:
    if design.get("task_code") != TASK_CODE:
        raise CandidateBuildError(f"design.task_code must be {TASK_CODE}.")
    expected = require_text(design.get("baseline_sha256"), "baseline_sha256")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
        raise CandidateBuildError("baseline_sha256 must be a SHA-256 hexadecimal value.")
    if expected.casefold() != baseline_sha256.casefold():
        raise CandidateBuildError("The baseline ZIP checksum does not match the normalized design.")
    process_id = require_text(design.get("baseline_process_id"), "baseline_process_id")
    if not process_id.isdigit() or int(process_id) <= 0:
        raise CandidateBuildError("baseline_process_id must be a positive integer string.")
    require_text(design.get("environment"), "environment")
    schema_version = design.get("schema_version")
    if schema_version in {"1.0", "1.1"}:
        require_text(design.get("business_unit"), "business_unit", maximum=240)
    elif schema_version in {"1.2", "1.3", "1.4", "1.5"} and "business_unit" in design:
        raise CandidateBuildError(f"v{schema_version} designs store business_unit inside every templates item.")
    if schema_version in {"1.2", "1.3", "1.4", "1.5"}:
        reject_unknown(design, {"schema_version", "environment", "task_code", "baseline_process_id",
                               "baseline_sha256", "templates", "itemizations", "project_mappings"}, "design")
        if schema_version in {"1.3", "1.4", "1.5"} and "project_mappings" in design:
            raise CandidateBuildError(
                f"project_mappings is not supported by v{schema_version}: Projects is disabled for every import."
            )
    for key in ("itemizations", "project_mappings"):
        if key in design and (schema_version not in {"1.2", "1.3", "1.4", "1.5"} or not isinstance(design[key], list)):
            raise CandidateBuildError(f"{key} requires a v1.2, v1.3, v1.4, or v1.5 array.")
    return normalized_templates(design)


def infer_target_operation(matches: list[int], label: str) -> str:
    """Classify one source identity from the fresh target-export matches."""
    if not matches:
        return "create"
    if len(matches) == 1:
        return "edit"
    raise CandidateBuildError(f"{label} matched {len(matches)} target records; resolve the duplicate identity before packaging.")


def resolve_operation_free_design(
    design: dict[str, Any], templates: list[dict[str, Any]], template_rows: list[dict[str, str]],
    type_rows: list[dict[str, str]], members: dict[str, bytes],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Resolve V3 intake operations only from the fresh target baseline."""
    if design.get("schema_version") != "1.5":
        return design, templates

    resolved_design = deepcopy(design)
    resolved_templates = deepcopy(templates)
    template_operations: set[str] = set()
    for index, template in enumerate(resolved_templates, start=1):
        label = f"templates[{index}]"
        business_unit = require_text(template.get("business_unit"), f"{label}.business_unit", maximum=240)
        name = require_text(template.get("name"), f"{label}.name", maximum=80)
        template["operation"] = infer_target_operation(
            matching_indexes(template_rows, BuName=business_unit, Name=name), label
        )
        template_operations.add(template["operation"])
        expense_types = template.get("expense_types", [])
        if not isinstance(expense_types, list):
            raise CandidateBuildError(f"{label}.expense_types must be a JSON array.")
        for type_index, item in enumerate(expense_types, start=1):
            if not isinstance(item, dict):
                raise CandidateBuildError(f"{label}.expense_types[{type_index}] must be a JSON object.")
            if "operation" in item:
                raise CandidateBuildError("v1.5 operation-free designs must not include an expense type operation.")
            type_name = require_text(item.get("name"), f"{label}.expense_types[{type_index}].name", maximum=80)
            item["operation"] = infer_target_operation(
                matching_indexes(
                    type_rows,
                    **{
                        "EXM_EXPENSE_TEMPLATE.BuName": business_unit,
                        "EXM_EXPENSE_TEMPLATE.Name": name,
                        "Name": type_name,
                    },
                ),
                f"{label}.expense_types[{type_index}]",
            )
    if len(template_operations) > 1:
        raise CandidateBuildError(
            "The operation-free worksheet contains both new and existing templates; split the target-resolved create and edit templates into separate candidates."
        )

    itemizations = resolved_design.get("itemizations", [])
    if not isinstance(itemizations, list):
        return resolved_design, resolved_templates
    if ITEMIZATION_MEMBER not in members:
        return resolved_design, resolved_templates
    _, mapping_rows = read_csv_member(members[ITEMIZATION_MEMBER], ITEMIZATION_MEMBER)
    for index, item in enumerate(itemizations, start=1):
        label = f"itemizations[{index}]"
        if not isinstance(item, dict):
            raise CandidateBuildError(f"{label} must be an object.")
        if "operation" in item:
            raise CandidateBuildError("v1.5 operation-free designs must not include an itemization operation.")
        business_unit = require_text(item.get("business_unit"), f"{label}.business_unit", maximum=240)
        template_name = require_text(item.get("template_name"), f"{label}.template_name", maximum=80)
        parent_type = require_text(item.get("parent_type_name"), f"{label}.parent_type_name", maximum=80)
        child_type = require_text(item.get("child_type_name"), f"{label}.child_type_name", maximum=80)
        criteria = {
            **mapping_parent(business_unit, template_name, parent_type),
            "BuName": business_unit,
            "ExpTemplateName": template_name,
            "Name": child_type,
        }
        item["operation"] = infer_target_operation(matching_indexes(mapping_rows, **criteria), label)
    return resolved_design, resolved_templates


def mapping_parent(bu: str, template: str, owner: str) -> dict[str, str]:
    return {"EXM_EXPENSE_TEMPLATE.BuName": bu, "EXM_EXPENSE_TEMPLATE.Name": template,
            "EXM_EXPENSE_TYPE.BuName": bu, "EXM_EXPENSE_TYPE.TemplateName": template,
            "EXM_EXPENSE_TYPE.Name": owner}


def build_mapping_changes(design, templates, type_rows, members, baseline_zip, enabled_types):
    """Apply explicit child changes using final type rows and fresh-export references."""
    requested = {"itemizations": design.get("itemizations", []),
                 "project_mappings": design.get("project_mappings", [])}
    if not any(requested.values()) and not enabled_types:
        return {}, []
    if ITEMIZATION_MEMBER not in members or (requested["project_mappings"] and PROJECT_MEMBER not in members):
        raise CandidateBuildError("Requested child mappings require their child CSVs in the fresh task export.")
    from inspect_fsm_schema import inspect_schema
    try:
        inspect_schema(baseline_zip)
    except (ValueError, KeyError, OSError, ET.ParseError, zipfile.BadZipFile) as error:
        raise CandidateBuildError(f"Child mapping schema verification failed: {error}") from error
    selected = {(t.get("business_unit", design.get("business_unit", "")).strip().casefold(),
                 t["name"].strip().casefold()) for t in templates}
    changed, deltas = {}, []
    item_rows_after = []
    for section, member in (("itemizations", ITEMIZATION_MEMBER), ("project_mappings", PROJECT_MEMBER)):
        fields, original = read_csv_member(members[member], member)
        rows = deepcopy(original)
        is_item = section == "itemizations"
        required = {*mapping_parent("", "", ""), "BuName", "ExpTemplateName", "Name"}
        if not is_item:
            required |= {"ProjectUnitName", "ExpenditureTypeName", "ClassificationCode",
                         "EffectiveStartDate", "EffectiveEndDate", "SysEffectiveDate"}
        require_columns(fields, required, member)
        if set(fields) - required - WHO_COLUMNS:
            raise CandidateBuildError(f"Unmapped child CSV columns in {member}; review the current schema before writing rows.")
        seen = set()
        for number_, item in enumerate(requested[section], 1):
            label = f"{section}[{number_}]"
            if not isinstance(item, dict):
                raise CandidateBuildError(f"{label} must be an object.")
            allowed = {"operation", "business_unit", "template_name"}
            allowed |= ({"parent_type_name", "child_type_name", "include", "end_date"} if is_item else
                        {"type_name", "project_unit", "expenditure_type_name", "match_row_sha256", "reference_row_sha256"})
            reject_unknown(item, allowed, label)
            op = require_text(item.get("operation"), f"{label}.operation").casefold()
            if op not in {"create", "edit"}:
                raise CandidateBuildError(f"{label}.operation must be create or edit.")
            bu = require_text(item.get("business_unit"), f"{label}.business_unit", maximum=240)
            template = require_text(item.get("template_name"), f"{label}.template_name", maximum=80)
            owner = require_text(item.get("parent_type_name" if is_item else "type_name"), f"{label}.owner", maximum=80)
            if (bu.casefold(), template.casefold()) not in selected:
                raise CandidateBuildError(f"{label} parent must be included in templates (identity-only edit is sufficient).")
            owner_matches = matching_indexes(type_rows, **{"EXM_EXPENSE_TEMPLATE.BuName": bu,
                "EXM_EXPENSE_TEMPLATE.Name": template, "BuName": bu, "TemplateName": template, "Name": owner})
            if len(owner_matches) != 1:
                raise CandidateBuildError(f"{label} requires exactly one owning expense type.")
            owner_row = type_rows[owner_matches[0]]
            require_cash_only(owner_row, label)
            bu, template, owner = owner_row['BuName'], owner_row['TemplateName'], owner_row['Name']
            control = owner_row.get("ItemizationBehaviourCode" if is_item else "EnableProjectsFlag")
            if control not in ({"ENABLED", "REQUIRED"} if is_item else {"Y"}):
                raise CandidateBuildError(f"{label} conflicts with the owning type's disabled control.")
            parent = mapping_parent(bu, template, owner)
            if is_item:
                child = require_text(item.get("child_type_name"), f"{label}.child_type_name", maximum=80)
                if child.casefold() == owner.casefold():
                    raise CandidateBuildError(f"{label} cannot itemize itself.")
                child_matches = matching_indexes(type_rows, **{"EXM_EXPENSE_TEMPLATE.BuName": bu,
                    "EXM_EXPENSE_TEMPLATE.Name": template, "BuName": bu, "TemplateName": template, "Name": child})
                if len(child_matches) != 1:
                    raise CandidateBuildError(f"{label} requires exactly one child expense type in the same template and Business Unit.")
                require_cash_only(type_rows[child_matches[0]], label)
                child = type_rows[child_matches[0]]['Name']
                criteria = {**parent, "BuName": bu, "ExpTemplateName": template, "Name": child}
                if "end_date" in item and (item["end_date"] is not None or op == "edit"):
                    raise CandidateBuildError(f"{label}.end_date has no itemization mapping CSV column; end-dating/Clear is unsupported.")
                if op == "create" and "include" not in item:
                    raise CandidateBuildError(f"{label}.include is required for Create.")
                if "include" in item and flag(item["include"], f"{label}.include") != "Y":
                    raise CandidateBuildError(f"{label}: Include No/removal has no verified FSM deletion contract.")
            else:
                unit = require_text(item.get("project_unit"), f"{label}.project_unit", maximum=240)
                expenditure = require_text(item.get("expenditure_type_name"), f"{label}.expenditure_type_name", maximum=240)
                # All three FK identities form EXM_PROJECT_EXP_TYPE_MAPS_PK.
                criteria = {**parent, "BuName": bu, "ExpTemplateName": template, "Name": owner,
                            "ProjectUnitName": unit, "ExpenditureTypeName": expenditure}
            identity = tuple(v.casefold() for v in criteria.values())
            if identity in seen:
                raise CandidateBuildError(f"Duplicate requested mapping identity in {section}.")
            seen.add(identity)
            matches = matching_indexes(original, **criteria)
            if not is_item and "match_row_sha256" in item:
                if op != "edit":
                    raise CandidateBuildError(f"{label}.match_row_sha256 is only valid for Edit.")
                matches = [i for i in matches if row_hash(original[i], fields) == item["match_row_sha256"]]
            if (op == "create" and matches) or (op == "edit" and len(matches) != 1):
                raise CandidateBuildError(f"{label}: {op} mapping identity matched {len(matches)} existing rows; expected {'zero' if op == 'create' else 'exactly one'}.")
            before = original[matches[0]] if matches else None
            after = deepcopy(before) if before else blank_row(fields)
            if before is None:
                after.update(criteria)
            evidence = None
            if not is_item:
                if before is not None and "reference_row_sha256" in item:
                    raise CandidateBuildError(f"{label}: Edit preserves the existing reference attributes; reference_row_sha256 is Create-only.")
                if before is None:
                    # Expenditure attributes belong to the exact selected exported reference.
                    # Never copy a code/date from a different project unit or expenditure type.
                    refs = [r for r in original if r["ProjectUnitName"].casefold() == unit.casefold()
                            and r["ExpenditureTypeName"].casefold() == expenditure.casefold()]
                    if "reference_row_sha256" in item:
                        refs = [r for r in refs if row_hash(r, fields) == item["reference_row_sha256"]]
                    technical = {"ClassificationCode", "EffectiveStartDate", "EffectiveEndDate", "SysEffectiveDate"}
                    signatures = {tuple(r[k] for k in sorted(technical)) for r in refs}
                    if not refs or len(signatures) != 1:
                        raise CandidateBuildError(f"{label}: missing or ambiguous exported project reference; resolve the exact Project Unit/expenditure type and reference_row_sha256 from the fresh baseline.")
                    reference = refs[0]
                    for key in technical:
                        after[key] = reference[key]
                    after['ProjectUnitName'] = reference['ProjectUnitName']
                    after['ExpenditureTypeName'] = reference['ExpenditureTypeName']
                    evidence = row_hash(reference, fields)
                for key in ("EffectiveStartDate", "EffectiveEndDate", "SysEffectiveDate"):
                    if after[key]:
                        date_value(after[key], f"{label}.{key}")
                if after["EffectiveStartDate"] and after["EffectiveEndDate"] and date_value(after["EffectiveEndDate"], label) < date_value(after["EffectiveStartDate"], label):
                    raise CandidateBuildError(f"{label} exported project end date precedes start date.")
            delta = changed_fields(before, after)
            if delta:
                if matches:
                    rows[matches[0]] = after
                else:
                    rows.append(after)
                deltas.append({"member": member, "operation": op, "key": criteria,
                               "row_before_sha256": row_hash(before, fields) if before else None,
                               "row_after_sha256": row_hash(after, fields), "fields": delta,
                               "reference_row_sha256": evidence})
        if rows != original:
            changed[member] = write_csv_member(fields, rows)
        if is_item:
            item_rows_after = rows
    for bu, template, owner in enabled_types:
        included = matching_indexes(item_rows_after, **mapping_parent(bu, template, owner))
        if not included:
            raise CandidateBuildError(f"Enabled/Required type {owner!r} needs included child mappings.")
        for index in included:
            child = item_rows_after[index]
            if len(matching_indexes(type_rows, **{"BuName": child["BuName"],
                    "TemplateName": child["ExpTemplateName"], "Name": child["Name"]})) != 1:
                raise CandidateBuildError(f"Included child mapping for {owner!r} has no unique child expense type.")
    return changed, deltas


def build_candidate(
    baseline_zip: Path, design_path: Path, output_zip: Path, preview_path: Path, seed_reference_path: Path,
    reference_evidence_path: Path | None = None,
) -> dict[str, Any]:
    if output_zip.resolve() == preview_path.resolve():
        raise CandidateBuildError("Candidate ZIP and preview output must use different paths.")
    for output in (output_zip, preview_path):
        if output.exists():
            raise CandidateBuildError(f"Refusing to overwrite existing output: {output}")
    infos, members = read_baseline(baseline_zip)
    baseline_sha256 = sha256_file(baseline_zip)
    template_fields, template_rows = read_csv_member(members[TEMPLATE_MEMBER], TEMPLATE_MEMBER)
    type_fields, type_rows = read_csv_member(members[TYPE_MEMBER], TYPE_MEMBER)
    require_columns(
        template_fields,
        {"BuName", "Name", *TEMPLATE_FIELDS.values(), *TEMPLATE_RECEIPT_FIELDS.values(), *TEMPLATE_BEHAVIOR_FIELDS.values()},
        TEMPLATE_MEMBER,
    )
    require_columns(
        type_fields,
        {
            "EXM_EXPENSE_TEMPLATE.BuName", "EXM_EXPENSE_TEMPLATE.Name", "BuName", "TemplateName", "Name",
            *TYPE_FIELDS.values(), *TYPE_RECEIPT_FIELDS.values(), *TYPE_BEHAVIOR_FIELDS.values(),
            "EnableProjectsFlag", "ItemizationBehaviourCode", "ItemizationOnlyFlag", "PrepaidFlag",
        },
        TYPE_MEMBER,
    )
    design = read_json_object(design_path, "Normalized candidate design")
    templates = validate_design(design, baseline_sha256)
    design, templates = resolve_operation_free_design(design, templates, template_rows, type_rows, members)
    references = read_json_object(reference_evidence_path, "Destination reference evidence") if reference_evidence_path else {}
    category_requested = any("category_code" in item or "category_value" in item
                             for template in templates for item in template.get("expense_types", []))
    try:
        available_categories, seed_map = reference_values.categories(references, design["environment"], baseline_sha256) if category_requested else (set(), {})
    except ValueError as error:
        raise CandidateBuildError(str(error)) from error

    default_business_unit = design.get("business_unit")
    template_deltas: list[dict[str, Any]] = []
    enabled_types = []
    for template_index, template in enumerate(templates, start=1):
        label = f"templates[{template_index}]"
        business_unit = require_text(
            template.get("business_unit", default_business_unit), f"{label}.business_unit", maximum=240
        )
        try:
            resolved_bu = reference_values.business_unit(references, design["environment"], baseline_sha256, business_unit)
        except ValueError as error:
            raise CandidateBuildError(str(error)) from error
        operation = template["operation"]
        template_after, template_before, existing_template_index = build_template_row(
            template_fields, template_rows, business_unit, template, operation, label,
            cash_only=design.get("schema_version") in {"1.2", "1.3", "1.4", "1.5"},
        )
        if existing_template_index is None:
            template_rows.append(template_after)
        else:
            template_rows[existing_template_index] = template_after

        type_changes: list[dict[str, Any]] = []
        expense_types = template.get("expense_types", [])
        if not isinstance(expense_types, list):
            raise CandidateBuildError(f"{label}.expense_types must be a JSON array.")
        seen_types: set[str] = set()
        for item in expense_types:
            if not isinstance(item, dict):
                raise CandidateBuildError(f"Every {label}.expense_types item must be a JSON object.")
            type_name = require_text(item.get("name"), f"{label}.expense_types[].name", maximum=80)
            normalized_name = type_name.casefold()
            if normalized_name in seen_types:
                raise CandidateBuildError(f"Duplicate expense type in {label}: {type_name}")
            seen_types.add(normalized_name)
            item = deepcopy(item)
            if "category_value" in item and "category_code" not in item:
                submitted = require_text(item["category_value"], f"{label}.category_value", maximum=80)
                item["category_code"] = seed_map.get(submitted.casefold(), "")
            account = item.pop("account_number", ...)
            type_operation, type_after, type_before, existing_type_index = build_type_row(
                type_fields, type_rows, business_unit, template, operation, item, seed_map,
                available_categories, label, require_explicit_category=design.get("schema_version") in {"1.2", "1.3", "1.4", "1.5"},
                cash_only_no_account_or_projects=design.get("schema_version") in {"1.3", "1.4", "1.5"},
                tax_fields_empty=design.get("schema_version") in {"1.4", "1.5"},
            )
            if account is not ...:
                if "Segment1" not in type_fields or "LedgerName" not in type_fields:
                    raise CandidateBuildError("Fresh schema must expose Segment1 and LedgerName for an expense account.")
                if account is None:
                    raise CandidateBuildError("Expense Type Account clearing is not established; omit unchanged accounts.")
                type_after["Segment1"] = require_text(account, f"{label}.account_number", maximum=25)
                try:
                    type_after["LedgerName"] = reference_values.ledger_name(references, design["environment"], baseline_sha256, resolved_bu)
                except ValueError as error:
                    raise CandidateBuildError(str(error)) from error
            if type_operation == "create":
                type_rows.append(type_after)
            elif type_operation == "edit" and existing_type_index is not None:
                type_rows[existing_type_index] = type_after
            if type_after.get("ItemizationBehaviourCode") in {"ENABLED", "REQUIRED"} and (
                type_before is None or type_before.get("ItemizationBehaviourCode") not in {"ENABLED", "REQUIRED"}
            ):
                enabled_types.append((business_unit, template["name"], type_name))
            fields_changed = changed_fields(type_before, type_after)
            if fields_changed:
                type_changes.append(
                    {
                        "operation": type_operation,
                        "key": {"business_unit": business_unit, "template": template["name"], "name": type_name},
                        "row_before_sha256": row_hash(type_before, type_fields) if type_before else None,
                        "row_after_sha256": row_hash(type_after, type_fields),
                        "fields": fields_changed,
                    }
                )

        template_changes = changed_fields(template_before, template_after)
        if template_changes or type_changes:
            template_deltas.append(
                {
                    "operation": operation,
                    "key": {"business_unit": business_unit, "name": template["name"]},
                    "row_before_sha256": row_hash(template_before, template_fields) if template_before else None,
                    "row_after_sha256": row_hash(template_after, template_fields),
                    "fields": template_changes,
                    "expense_types": type_changes,
                }
            )

    mapping_members, mapping_deltas = build_mapping_changes(
        design, templates, type_rows, members, baseline_zip, enabled_types
    )
    if not template_deltas and not mapping_deltas:
        raise CandidateBuildError("The normalized design produces no delta from the fresh baseline.")

    changed_members = {
        TEMPLATE_MEMBER: write_csv_member(template_fields, template_rows),
        TYPE_MEMBER: write_csv_member(type_fields, type_rows),
    }
    changed_members.update(mapping_members)
    # Do not reserialize a parent CSV for a mapping-only request.
    if not any(delta["fields"] for delta in template_deltas):
        changed_members.pop(TEMPLATE_MEMBER)
    if not any(delta["expense_types"] for delta in template_deltas):
        changed_members.pop(TYPE_MEMBER)
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix=f".{output_zip.name}.", suffix=".tmp", dir=output_zip.parent, delete=False) as temp:
            temp_path = Path(temp.name)
        with zipfile.ZipFile(temp_path, "w") as archive:
            for info in infos:
                archive.writestr(info, changed_members.get(info.filename, members[info.filename]))
        with zipfile.ZipFile(temp_path) as archive:
            if archive.testzip() is not None or set(archive.namelist()) != set(members):
                raise CandidateBuildError("Candidate ZIP verification failed after construction.")
            for name, content in members.items():
                if name not in changed_members and archive.read(name) != content:
                    raise CandidateBuildError(f"Protected baseline member changed unexpectedly: {name}")
        os.replace(temp_path, output_zip)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    candidate_sha256 = sha256_file(output_zip)
    preview = {
        "schema_version": design.get("schema_version") if design.get("schema_version") in {"1.2", "1.3", "1.4", "1.5"} else "1.1",
        "status": "candidate_built",
        "environment": design["environment"],
        "task_code": TASK_CODE,
        "operations": [template["operation"] for template in templates],
        "baseline": {
            "process_id": design["baseline_process_id"],
            "zip": str(baseline_zip),
            "sha256": baseline_sha256,
            "inventory": [info.filename for info in infos],
        },
        "normalized_design": {"path": str(design_path), "sha256": canonical_json_sha256(design)},
        "candidate": {"zip": str(output_zip), "sha256": candidate_sha256},
        "delta": {
            "templates": template_deltas,
            "mappings": mapping_deltas,
            "changed_members": sorted(changed_members),
            "protected_members": sorted(set(members) - set(changed_members)),
        },
        "validation": {
            "archive_integrity": "passed",
            "inventory_preserved": True,
            "protected_members_byte_identical": True,
            "baseline_checksum_matched": True,
            "task_schema_headers_matched": True,
            "duplicate_identity_checks": "passed",
            "cash_only_create_defaults": "applied" if any(template["operation"] == "create" for template in templates) else "preserved",
            "next_gate": "core.data-loader Task Hook validation and immutable-preview approval",
        },
    }
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    preview_path.write_text(json.dumps(preview, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return preview


def default_seed_reference() -> Path:
    repository_root = Path(__file__).resolve().parents[6]
    return (
        repository_root
        / "pillars"
        / "erp"
        / "financials"
        / "expenses"
        / "manage-expense-report-templates"
        / "ora-resource"
        / "ora_reference_lookups.md"
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-zip", required=True, type=Path)
    parser.add_argument("--design-json", required=True, type=Path)
    parser.add_argument("--output-zip", required=True, type=Path)
    parser.add_argument("--preview-output", required=True, type=Path)
    parser.add_argument("--seed-reference", type=Path, default=default_seed_reference())
    parser.add_argument("--reference-evidence", required=True, type=Path,
                        help="Fresh core-captured category, BU, and optional primary-ledger REST evidence")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        preview = build_candidate(
            args.baseline_zip,
            args.design_json,
            args.output_zip,
            args.preview_output,
            args.seed_reference,
            args.reference_evidence,
        )
    except CandidateBuildError as error:
        print(f"Candidate build failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(preview, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
