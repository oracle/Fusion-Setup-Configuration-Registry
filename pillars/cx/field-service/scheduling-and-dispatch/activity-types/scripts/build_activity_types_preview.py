#!/usr/bin/env python3
"""Build a preview-only OFSC Activity Types create payload from a free-format XLSX workbook."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any
from urllib.parse import quote
import xml.etree.ElementTree as ElementTree
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from guarded_xlsx import GuardedWorkbook, column_index, shared_string


FEATURE_KEYS = (
    "isTeamworkAvailable",
    "isSegmentingEnabled",
    "allowMoveBetweenResources",
    "allowCreationInBuckets",
    "allowReschedule",
    "supportOfNotOrderedActivities",
    "allowNonScheduled",
    "supportOfWorkZones",
    "supportOfWorkSkills",
    "supportOfTimeSlots",
    "supportOfInventory",
    "supportOfLinks",
    "supportOfPreferredResources",
    "allowMassActivities",
    "allowRepeatingActivities",
    "calculateTravel",
    "calculateActivityDurationUsingStatistics",
    "allowToSearch",
    "allowToCreateFromIncomingInterface",
    "enableDayBeforeTrigger",
    "enableReminderAndChangeTriggers",
    "enableNotStartedTrigger",
    "enableSwWarningTrigger",
    "calculateDeliveryWindow",
    "slaAndServiceWindowUseCustomerTimeZone",
    "supportOfRequiredInventory",
    "disableLocationTracking",
)

FIELD_ALIASES = {
    "name": ("activity type name", "english name", "name"),
    "label": ("activity type label",),
    "active": ("status", "active", "enabled"),
    "group": ("group", "activity type group"),
    "duration": ("default duration (minutes)", "default duration", "duration"),
}


class PreviewInputError(ValueError):
    """Raised when the workbook cannot produce a safe immutable preview."""


class _Worksheet:
    def __init__(self, title: str, rows: list[tuple[Any, Any]]) -> None:
        self.title = title
        self._rows = rows

    def iter_rows(self, *, values_only: bool) -> list[tuple[Any, Any]]:
        if not values_only:
            raise ValueError("Only values_only worksheet iteration is supported.")
        return self._rows


def _normalized(value: Any) -> str:
    return " ".join(str(value or "").strip().split()).casefold()


def _as_text(value: Any, field: str, sheet: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise PreviewInputError(f"{sheet}: {field} is required.")
    return text


def _as_boolean(value: Any, field: str, sheet: str) -> bool:
    text = _normalized(value)
    if text in {"true", "yes", "y", "1", "active", "enabled"}:
        return True
    if text in {"false", "no", "n", "0", "inactive", "disabled"}:
        return False
    raise PreviewInputError(f"{sheet}: {field} must be an unambiguous boolean.")


def _as_duration(value: Any, sheet: str) -> int:
    try:
        duration = int(str(value).strip())
    except (TypeError, ValueError) as error:
        raise PreviewInputError(f"{sheet}: Default Duration must be an integer.") from error
    if not 1 <= duration <= 1440:
        raise PreviewInputError(f"{sheet}: Default Duration must be between 1 and 1440.")
    return duration


def _worksheet_values(worksheet: Any) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for row in worksheet.iter_rows(values_only=True):
        if not row:
            continue
        key = _normalized(row[0] if len(row) > 0 else None)
        if key and len(row) > 1 and row[1] is not None:
            values[key] = row[1]
    return values


_column_index = column_index


def _read_shared_strings(archive: GuardedWorkbook) -> list[str]:
    try:
        root = archive.xml("xl/sharedStrings.xml")
    except KeyError:
        return []
    namespace = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    return ["".join(node.itertext()) for node in root.findall(f"{namespace}si")]


def _read_xlsx_worksheets(workbook_path: Path) -> list[_Worksheet]:
    spreadsheet = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    relationship = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    package_relationship = "{http://schemas.openxmlformats.org/package/2006/relationships}"
    try:
        with GuardedWorkbook(workbook_path) as archive:
            workbook = archive.xml("xl/workbook.xml")
            relationships = archive.xml("xl/_rels/workbook.xml.rels")
            targets = {
                item.attrib["Id"]: item.attrib["Target"]
                for item in relationships.findall(f"{package_relationship}Relationship")
            }
            shared_strings = _read_shared_strings(archive)
            result: list[_Worksheet] = []
            for sheet in workbook.findall(f"{spreadsheet}sheets/{spreadsheet}sheet"):
                relationship_id = sheet.attrib.get(f"{relationship}id")
                target = targets.get(relationship_id or "")
                if not target:
                    raise PreviewInputError("Workbook sheet relationship is missing.")
                sheet_path = target.lstrip("/") if target.startswith("/") else "xl/" + target
                root = archive.xml(sheet_path)
                rows: list[tuple[Any, Any]] = []
                for row in root.findall(f"{spreadsheet}sheetData/{spreadsheet}row"):
                    values: dict[int, Any] = {}
                    for cell in row.findall(f"{spreadsheet}c"):
                        column = _column_index(cell.attrib.get("r", ""))
                        if column not in {1, 2}:
                            continue
                        cell_type = cell.attrib.get("t")
                        value_node = cell.find(f"{spreadsheet}v")
                        if cell_type == "inlineStr":
                            value = "".join(cell.itertext())
                        elif value_node is None:
                            value = None
                        elif cell_type == "s":
                            value = shared_string(shared_strings, value_node.text)
                        elif cell_type == "b":
                            value = (value_node.text == "1")
                        else:
                            value = value_node.text
                        values[column] = value
                    rows.append((values.get(1), values.get(2)))
                result.append(_Worksheet(sheet.attrib.get("name", ""), rows))
            return result
    except (KeyError, IndexError, OSError, ValueError, ElementTree.ParseError, zipfile.BadZipFile) as error:
        raise PreviewInputError(f"Workbook could not be read: {error}") from error


def _find_field(values: dict[str, Any], aliases: tuple[str, ...], field: str, sheet: str) -> Any:
    for alias in aliases:
        if alias in values:
            return values[alias]
    raise PreviewInputError(f"{sheet}: {field} is required.")


def _record_from_worksheet(worksheet: Any, group_label: str) -> dict[str, Any]:
    values = _worksheet_values(worksheet)
    sheet = str(worksheet.title)
    label = _as_text(_find_field(values, FIELD_ALIASES["label"], "Activity Type Label", sheet), "Activity Type Label", sheet)
    if len(label) > 32:
        raise PreviewInputError(f"{sheet}: Activity Type Label must be at most 32 characters.")
    name = _as_text(_find_field(values, FIELD_ALIASES["name"], "Activity Type Name", sheet), "Activity Type Name", sheet)
    if len(name) > 32:
        raise PreviewInputError(f"{sheet}: Activity Type Name must be at most 32 characters.")
    active = _as_boolean(_find_field(values, FIELD_ALIASES["active"], "Status", sheet), "Status", sheet)
    supplied_group = _as_text(_find_field(values, FIELD_ALIASES["group"], "Group", sheet), "Group", sheet)
    if supplied_group.casefold() != "customer":
        raise PreviewInputError(f"{sheet}: Group must be the confirmed Customer display name.")
    duration = _as_duration(_find_field(values, FIELD_ALIASES["duration"], "Default Duration", sheet), sheet)
    body = {
        "label": label,
        "active": active,
        "groupLabel": group_label,
        "defaultDuration": duration,
        "features": {key: False for key in FEATURE_KEYS},
        "translations": [{"language": "en", "name": name}],
    }
    return {
        "operationId": "put-activity-type",
        "method": "PUT",
        "path": f"/rest/ofscMetadata/v1/activityTypes/{quote(label, safe='')}",
        "expectedStatuses": [200, 201],
        "body": body,
    }


def build_preview_data(workbook_path: Path, group_label: str) -> dict[str, Any]:
    if not workbook_path.is_file() or workbook_path.suffix.casefold() != ".xlsx":
        raise PreviewInputError("workbook must be an existing .xlsx file.")
    canonical_group = _as_text(group_label, "canonical group label", "arguments")
    worksheets = [sheet for sheet in _read_xlsx_worksheets(workbook_path) if _normalized(sheet.title).startswith("activity types")]
    if not worksheets:
        raise PreviewInputError("No Activity Types worksheet was found.")
    requests = [_record_from_worksheet(sheet, canonical_group) for sheet in worksheets]
    labels = [request["body"]["label"] for request in requests]
    if len(set(labels)) != len(labels):
        raise PreviewInputError("Activity Type Label values must be unique.")
    return {
        "operation": "create",
        "requests": requests,
        "capabilityPolicy": "all optional capabilities explicitly disabled",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", required=True, type=Path, help="Free-format Activity Types .xlsx workbook.")
    parser.add_argument("--group-label", required=True, help="Canonical environment Activity Type Group label.")
    parser.add_argument("--output", required=True, type=Path, help="Preview JSON output path.")
    args = parser.parse_args()
    try:
        payload = build_preview_data(args.workbook, args.group_label)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except PreviewInputError as error:
        print(f"Input validation: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
