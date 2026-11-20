"""Shift Item adapter for the shared Field Service execution workflow."""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import sys

TASK_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TASK_ROOT.parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from guarded_xlsx import GuardedWorkbook, column_index, shared_string
from task_orchestration import WorkflowBlocked, resolve_execution_route

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REQUIRED = {"work_schedule_label", "itemId", "type", "startDate"}
WORK_SCHEDULES_PATH = "/api/field-service/configuration/v1/workSchedules"
SHIFTS_PATH = "/api/field-service/configuration/v1/shifts"
ON_CALL_DECORATIONS = {"yellow", "orange", "red", "blue", "green", "purple"}


def _column_index(reference: str) -> int:
    return column_index(reference) - 1


def _workbook_rows(workbook: Path) -> list[dict[str, Any]]:
    """Read payload rows through bounded, DTD-rejecting OOXML parsing (F5)."""
    try:
        with GuardedWorkbook(workbook) as archive:
            shared: list[str] = []
            if "xl/sharedStrings.xml" in archive.namelist():
                root = archive.xml("xl/sharedStrings.xml")
                shared = ["".join(node.itertext()) for node in root.findall(f"{NS}si")]
            rels = archive.xml("xl/_rels/workbook.xml.rels")
            paths = {rel.attrib["Id"]: rel.attrib["Target"].lstrip("/") for rel in rels}
            book = archive.xml("xl/workbook.xml")
            sheet = next((s for s in book.findall(f".//{NS}sheet") if s.attrib.get("name") == "Shift Items REST Payload"), None)
            if sheet is None:
                raise WorkflowBlocked("Workbook has no 'Shift Items REST Payload' worksheet.")
            target = paths.get(sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", ""))
            if not target:
                raise WorkflowBlocked("Shift Items REST Payload worksheet relationship is unreadable.")
            if not target.startswith("xl/"):
                target = "xl/" + target
            root = archive.xml(target)
        rows: list[list[Any]] = []
        for row in root.findall(f".//{NS}sheetData/{NS}row"):
            archive.check_time()
            values: list[Any] = []
            for cell in row.findall(f"{NS}c"):
                index = _column_index(cell.attrib["r"])
                values.extend([None] * (index + 1 - len(values)))
                raw = cell.findtext(f"{NS}v")
                if cell.attrib.get("t") == "s" and raw is not None:
                    value: Any = shared_string(shared, raw)
                elif cell.attrib.get("t") == "inlineStr":
                    value = "".join(cell.itertext())
                else:
                    value = raw
                values[index] = value
            rows.append(values)
        header_at = next((i for i, row in enumerate(rows) if row and str(row[0]).strip().casefold() == "operation"), None)
        if header_at is None:
            raise WorkflowBlocked("Shift Items REST Payload table has no operation header.")
        headers = [str(x).strip() if x is not None else "" for x in rows[header_at]]
        return [{headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
                for row in rows[header_at + 1:] if any(value not in (None, "") for value in row)]

    except (OSError, zipfile.BadZipFile, KeyError, ET.ParseError, ValueError) as error:
        raise WorkflowBlocked(f"Filled workbook cannot be read: {error}") from error


def _named_rows(workbook: Path, sheet_name: str, first_header: str) -> list[dict[str, Any]]:
    """Read parent rows through the same guarded XML path as payload rows (F5)."""
    try:
        with GuardedWorkbook(workbook) as archive:
            shared: list[str] = []
            if "xl/sharedStrings.xml" in archive.namelist():
                root = archive.xml("xl/sharedStrings.xml")
                shared = ["".join(node.itertext()) for node in root.findall(f"{NS}si")]
            rels = archive.xml("xl/_rels/workbook.xml.rels")
            paths = {rel.attrib["Id"]: rel.attrib["Target"].lstrip("/") for rel in rels}
            book = archive.xml("xl/workbook.xml")
            sheet = next((s for s in book.findall(f".//{NS}sheet") if s.attrib.get("name") == sheet_name), None)
            if sheet is None:
                raise WorkflowBlocked(f"Workbook has no '{sheet_name}' worksheet.")
            target = paths.get(sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", ""))
            if not target:
                raise WorkflowBlocked(f"{sheet_name} worksheet relationship is unreadable.")
            root = archive.xml(target if target.startswith("xl/") else "xl/" + target)
        rows: list[list[Any]] = []
        for row in root.findall(f".//{NS}sheetData/{NS}row"):
            archive.check_time()
            values: list[Any] = []
            for cell in row.findall(f"{NS}c"):
                index = _column_index(cell.attrib["r"])
                values.extend([None] * (index + 1 - len(values)))
                raw = cell.findtext(f"{NS}v")
                values[index] = shared_string(shared, raw) if cell.attrib.get("t") == "s" and raw is not None else ("".join(cell.itertext()) if cell.attrib.get("t") == "inlineStr" else raw)
            rows.append(values)
        header_at = next((i for i, row in enumerate(rows) if row and str(row[0]).strip().rstrip("*").casefold() == first_header.casefold()), None)
        if header_at is None:
            raise WorkflowBlocked(f"{sheet_name} worksheet has no '{first_header}' header.")
        headers = [str(value).strip().rstrip("*").strip() if value is not None else "" for value in rows[header_at]]
        return [{headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
                for row in rows[header_at + 1:] if any(value not in (None, "") for value in row)]

    except (OSError, zipfile.BadZipFile, KeyError, ET.ParseError, ValueError) as error:
        raise WorkflowBlocked(f"Filled workbook cannot be read: {error}") from error


def _text(row: dict[str, Any], field: str) -> str:
    return str(row.get(field) or "").strip()


def _issue(rule_id: str, condition: str, correction: str) -> dict[str, str]:
    return {"ruleId": rule_id, "severity": "Error", "blockingCondition": condition, "recommendation": correction}


def _integer(value: Any, field: str, row: int) -> int:
    try:
        number = int(str(value))
    except (TypeError, ValueError) as error:
        raise WorkflowBlocked(f"Row {row}: {field} must be a positive integer.") from error
    if number <= 0:
        raise WorkflowBlocked(f"Row {row}: {field} must be a positive integer.")
    return number


def _date(value: Any, field: str, row: int) -> str:
    if not value:
        raise WorkflowBlocked(f"Row {row}: {field} is required.")
    text = str(value).strip()
    try:
        return datetime.strptime(text, "%Y-%m-%d").date().isoformat()
    except ValueError as error:
        raise WorkflowBlocked(f"Row {row}: {field} must use YYYY-MM-DD.") from error


def _boolean(value: Any, field: str, row: int) -> bool:
    text = str(value).strip().casefold()
    if text in {"true", "yes", "y", "1", "active"}:
        return True
    if text in {"false", "no", "n", "0", "inactive"}:
        return False
    raise WorkflowBlocked(f"Row {row}: {field} must be true or false.")


def _label(value: Any, field: str, row: int) -> str:
    label = str(value or "").strip()
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", label):
        raise WorkflowBlocked(f"Row {row}: {field} must be an API-safe label beginning with a letter.")
    return label


def _item_days(value: Any, row: int) -> list[str]:
    days = [day.strip().lower() for day in str(value or "").split(",") if day.strip()]
    if not days or any(day not in {"mon", "tue", "wed", "thu", "fri", "sat", "sun"} for day in days):
        raise WorkflowBlocked(f"Row {row}: repeatDays must be a comma-separated list of mon, tue, wed, thu, fri, sat, sun.")
    return days


def _ofsc_time(value: Any) -> str:
    """Canonicalize OFSC time-only values returned as HH:MM:SS."""
    text = str(value or "").strip()
    if re.fullmatch(r"\d{2}:\d{2}", text):
        return text + ":00"
    return text


class ShiftsAndSchedulesAdapter:
    task_code = "ORA_FFS_TS_SHIFTS_AND_SCHEDULES"

    def resolve_route(self, direction: str | None) -> dict[str, str]:
        return resolve_execution_route(TASK_ROOT / "ora-resource" / "ora_rest_execution.md", self.task_code, direction)

    def validate_design(self, workbook: Path) -> list[dict[str, str]]:
        """Execute every SS design rule locally before the REST baseline lookup."""
        schedules = _named_rows(workbook, "Work Schedules", "Runtime ID")
        shifts = _named_rows(workbook, "Shifts", "Work Schedule Label")
        items = _workbook_rows(workbook)
        issues: list[dict[str, str]] = []
        labels = [_text(row, "Label") for row in schedules + shifts]
        if any(not _text(row, "Hierarchy / Assignment Level") or "resource" in _text(row, "Hierarchy / Assignment Level").casefold() for row in schedules):
            issues.append(_issue("SS.HIERARCHY_AND_INHERITANCE", "A schedule lacks a parent hierarchy level or is configured directly on a resource.", "Define the common schedule at a bucket or organization-unit level and inherit it."))
        if any(not _text(row, "Holiday / Override Review") for row in schedules):
            issues.append(_issue("SS.AVAILABILITY_ACCURACY", "Availability or override review is missing for a changed schedule.", "Record current calendar availability and the override review before preview."))
        regular_keys: set[tuple[str, str, str]] = set()
        for row in shifts:
            if _text(row, "Type").casefold() == "regular":
                key = (_text(row, "Start Time"), _text(row, "End Time"), _text(row, "Work Schedule Label"))
                if key in regular_keys:
                    issues.append(_issue("SS.STANDARD_SHIFT", "A regular repeatable shift is duplicated in the same schedule.", "Keep one standard regular shift at the highest practical hierarchy level."))
                    break
                regular_keys.add(key)
        if len(schedules) > 1 and any(not _text(row, "Variation Reason") for row in schedules[1:]):
            issues.append(_issue("SS.SCHEDULE_VARIATION", "A separate schedule has no documented repeatable variation.", "Document a real rotation, region, season, weekend, or operating-hours difference."))
        if any(not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", label) for label in labels if label) or any(not _text(row, "Status") for row in schedules + shifts):
            issues.append(_issue("SS.NAMING_AND_STATUS", "A label is ambiguous or a schedule or shift has no lifecycle status.", "Use stable API-friendly labels and keep required future shifts active."))
        for row in shifts:
            coverage = _text(row, "Routing / On-Call Coverage").casefold()
            if _text(row, "Type").casefold() == "on call" and "manual" not in coverage:
                issues.append(_issue("SS.ROUTING_VS_ON_CALL", "An on-call shift lacks explicit manual-assignment coverage.", "Use on-call only for deliberate manual assignment beyond normal hours.")); break
            if _text(row, "Type").casefold() == "regular" and "automatic" not in coverage:
                issues.append(_issue("SS.ROUTING_VS_ON_CALL", "A regular shift lacks automatic-routing intent.", "Use regular shifts for normal automatic-routing availability.")); break
        if any(any(word in _text(row, "Recurring Internal Work").casefold() for word in ("lunch", "break", "meeting")) and "attach" not in _text(row, "Recurring Internal Work").casefold() for row in shifts):
            issues.append(_issue("SS.RECURRING_INTERNAL_WORK", "Recurring internal work is not associated with its shift.", "Associate the recurring activity with the relevant shift rather than recreating it per resource."))
        for row in items:
            if _text(row, "type").casefold() == "non-working" and not _text(row, "nonWorkingReasonLabel"):
                issues.append(_issue("SS.ABSENCE_MODEL", "A non-working item lacks a non-working reason.", "Use a non-working reason for full-day absence and dedicated calendars for partial-day or split shifts.")); break
        schedule_by_label = {_text(row, "Label"): row for row in schedules}
        for row in items:
            item_schedule_label = _text(row, "work_schedule_label")
            if item_schedule_label and "holiday" in _text(row, "comments").casefold() and not _text(schedule_by_label.get(item_schedule_label, {}), "Holiday / Override Review"):
                issues.append(_issue("SS.HOLIDAY_PRECEDENCE", "Holiday configuration lacks child-override review.", "Apply holidays centrally and verify child overrides before preview.")); break
        for row in shifts:
            unit, points, kind = _text(row, "Capacity Unit"), _text(row, "Points Limit"), _text(row, "Type").casefold()
            if unit == "Points" and kind != "on call" and (not points or not points.isdigit() or int(points) <= 0):
                issues.append(_issue("SS.CAPACITY_ALIGNMENT", "A points-based regular shift has no positive points limit.", "Set a sensible shift-level points limit that matches planned workload.")); break
        return issues

    def preflight(self, workbook: Path, get: Any, temp: Path) -> tuple[dict[str, Any], dict[str, Any]]:
        """Plan parent upserts first, then schedule items that depend on them.

        API Structure - Configuration documents v1 PUT upserts for work schedules
        and shifts, and v1 work-schedule item operations.  A shift item cannot
        be sent until its parent schedule and referenced shift are resolvable.
        """
        requests: list[dict[str, Any]] = []
        baselines: dict[str, Any] = {}
        schedules = _named_rows(workbook, "Work Schedules", "Runtime ID")
        shifts = _named_rows(workbook, "Shifts", "Work Schedule Label")
        item_rows = _workbook_rows(workbook)
        if not item_rows:
            raise WorkflowBlocked("Shift Items REST Payload table has no request rows.")
        missing_columns = REQUIRED - set(item_rows[0])
        if missing_columns:
            raise WorkflowBlocked(f"Shift Items REST Payload table is missing required columns: {', '.join(sorted(missing_columns))}.")
        # Resolve each concrete Configuration API parent. A structured label
        # GET 404 is the creation baseline for its subsequent conditional PUT;
        # collection GETs are deliberately not used because they are not
        # required by this parent-upsert contract.
        schedule_labels: set[str] = set()
        shift_labels: set[str] = set()
        shift_details: dict[str, dict[str, str]] = {}

        for row_number, row in enumerate(schedules, 2):
            label = _label(row.get("Label"), "Work Schedule Label", row_number)
            name = _text(row, "Name")
            if not name:
                raise WorkflowBlocked(f"Row {row_number}: Work Schedule Name is required.")
            if label in schedule_labels:
                raise WorkflowBlocked(f"Row {row_number}: duplicate work schedule label {label}.")
            schedule_labels.add(label)
            path = f"{WORK_SCHEDULES_PATH}/{label}"
            baseline_key = f"workSchedule:{label}"
            body = {"name": name, "active": _boolean(row.get("Active") or row.get("Status"), "Active", row_number)}
            requests.append({"method": "PUT", "path": path, "verifyPath": path, "identity": baseline_key,
                             "resourceType": "workSchedule", "body": body, "parentLabel": label})

        for row_number, row in enumerate(shifts, 2):
            label = _label(row.get("Label"), "Shift Label", row_number)
            schedule_label = _label(row.get("Work Schedule Label"), "Work Schedule Label", row_number)
            if schedule_label not in schedule_labels:
                raise WorkflowBlocked(f"Row {row_number}: shift {label} references unknown work schedule {schedule_label}.")
            name = _text(row, "Name")
            shift_type = _text(row, "Type").casefold().replace(" ", "-")
            if not name or shift_type not in {"regular", "on-call"}:
                raise WorkflowBlocked(f"Row {row_number}: shift Name and Type (regular or on-call) are required.")
            if label in shift_labels:
                raise WorkflowBlocked(f"Row {row_number}: duplicate shift label {label}.")
            shift_labels.add(label)
            shift_details[label] = {"type": shift_type, "decoration": _text(row, "Decoration").casefold()}
            path = f"{SHIFTS_PATH}/{label}"
            baseline_key = f"shift:{label}"
            body: dict[str, Any] = {"name": name, "active": _boolean(row.get("Active") or row.get("Status"), "Active", row_number),
                                    "type": shift_type, "workTimeStart": _text(row, "Start Time"), "workTimeEnd": _text(row, "End Time")}
            if not body["workTimeStart"] or not body["workTimeEnd"]:
                raise WorkflowBlocked(f"Row {row_number}: Start Time and End Time are required.")
            if _text(row, "Points Limit"):
                body["points"] = _integer(row.get("Points Limit"), "Points Limit", row_number)
            decoration = _text(row, "Decoration").casefold()
            if shift_type == "on-call":
                if decoration not in ON_CALL_DECORATIONS:
                    raise WorkflowBlocked(f"Row {row_number}: on-call shift Decoration must be one of {', '.join(sorted(ON_CALL_DECORATIONS))}.")
                body["decoration"] = decoration
            elif decoration:
                raise WorkflowBlocked(f"Row {row_number}: Decoration is allowed only for on-call shifts.")
            requests.append({"method": "PUT", "path": path, "verifyPath": path, "identity": baseline_key,
                             "resourceType": "shift", "body": body, "parentLabel": label})

        for row_number, row in enumerate(item_rows, 6):
            operation = str(row.get("operation") or "").upper()
            schedule_label = _label(row.get("work_schedule_label"), "work_schedule_label", row_number)
            if operation not in {"POST", "PUT", "DELETE"} or schedule_label not in schedule_labels:
                raise WorkflowBlocked(f"Row {row_number}: operation must be POST, PUT, or DELETE and work_schedule_label must identify a workbook schedule.")
            base = f"{WORK_SCHEDULES_PATH}/{schedule_label}/items"
            item_id = _integer(row.get("itemId"), "itemId", row_number) if operation in {"PUT", "DELETE"} else None
            if operation == "POST" and _text(row, "itemId"):
                raise WorkflowBlocked(f"Row {row_number}: itemId is OFSC-generated for POST and must be blank.")
            path = f"{base}/{item_id}" if operation in {"PUT", "DELETE"} else base
            request: dict[str, Any] = {"method": operation, "path": path, "verifyPath": base,
                                       "identity": f"{schedule_label}/{item_id}", "resourceType": "workScheduleItem",
                                       "workScheduleLabel": schedule_label, "itemId": item_id}
            if operation != "DELETE":
                item_type = str(row.get("type") or "").strip().lower()
                if item_type not in {"shift", "non-working"}:
                    raise WorkflowBlocked(f"Row {row_number}: type must be shift or non-working.")
                body: dict[str, Any] = {"type": item_type,
                                        "startDate": _date(row.get("startDate"), "startDate", row_number)}
                end_date = row.get("endDate")
                if end_date:
                    body["endDate"] = _date(end_date, "endDate", row_number)
                    if body["endDate"] < body["startDate"]:
                        raise WorkflowBlocked(f"Row {row_number}: endDate cannot precede startDate.")
                if item_type == "shift":
                    shift_label = _label(row.get("shiftLabel"), "shiftLabel", row_number)
                    if shift_label not in shift_labels:
                        raise WorkflowBlocked(f"Row {row_number}: shiftLabel {shift_label} must identify a workbook shift.")
                    body["label"] = shift_label
                    body["shiftType"] = shift_details[shift_label]["type"]
                    if body["shiftType"] == "on-call":
                        body["decoration"] = shift_details[shift_label]["decoration"]
                else:
                    reason = _text(row, "nonWorkingReasonLabel")
                    if not reason:
                        raise WorkflowBlocked(f"Row {row_number}: nonWorkingReasonLabel is required for non-working items.")
                    body["label"] = reason
                for field in ("comments",):
                    if row.get(field) not in (None, ""):
                        body[field] = row[field]
                repeat_type = _text(row, "repeatType").casefold()
                if repeat_type:
                    if repeat_type not in {"daily", "weekly", "yearly"}:
                        raise WorkflowBlocked(f"Row {row_number}: repeatType must be daily, weekly, or yearly.")
                    recurrence: dict[str, Any] = {"type": repeat_type, "every": 1, "startDate": body["startDate"], "endDate": body.get("endDate", "")}
                    if repeat_type == "weekly":
                        names = {"mon":"monday","tue":"tuesday","wed":"wednesday","thu":"thursday","fri":"friday","sat":"saturday","sun":"sunday"}
                        recurrence["weekdays"] = [names[day] for day in _item_days(row.get("repeatDays"), row_number)]
                    body["recurrence"] = recurrence
                request["body"] = body
            requests.append(request)
        for request in requests:
            if request["resourceType"] in {"workSchedule", "shift"}:
                baseline = get(request["path"], temp / f"baseline-{len(baselines) + 1}.json")
                baselines[request["identity"]] = baseline
                request["headers"] = {"If-None-Match": request["parentLabel"]} if baseline is None else {}
        # Preserve an actual parent change or a missing parent to be created.
        # Omit only a parent that already equals the workbook state.
        requests = [
            request for request in requests
            if request["resourceType"] not in {"workSchedule", "shift"}
            or baselines.get(request["identity"]) is None
            or self.verify(request, baselines[request["identity"]])
        ]
        for request in requests:
            if request["resourceType"] != "workScheduleItem":
                continue
            label = request["workScheduleLabel"]
            key = f"workScheduleItems:{label}"
            if key not in baselines:
                baselines[key] = get(request["verifyPath"], temp / f"baseline-{len(baselines) + 1}.json")
        reconciled = []
        planned_creations = set()
        for request in requests:
            if request["resourceType"] != "workScheduleItem" or request["method"] != "POST":
                reconciled.append(request)
                continue
            label = request["workScheduleLabel"]
            creation_key = (label, self._item_key(request["body"]))
            if creation_key in planned_creations:
                raise WorkflowBlocked("Duplicate schedule-item creation keys in workbook; resolve before preview.")
            planned_creations.add(creation_key)
            current = baselines[f"workScheduleItems:{label}"]
            if current is None and baselines.get(f"workSchedule:{label}") is None:
                items = []  # A missing parent has no existing item collection.
            elif not isinstance(current, dict) or not isinstance(current.get("items"), list):
                raise WorkflowBlocked("Schedule-item baseline is missing or invalid; reconcile before creation.")
            else:
                if current.get("hasMore") or any(link.get("rel") == "next" for link in current.get("links", []) if isinstance(link, dict)):
                    raise WorkflowBlocked("Schedule-item baseline is incomplete; resolve pagination before creation.")
                items = current["items"]
            if any(not isinstance(item, dict) for item in items):
                raise WorkflowBlocked("Schedule-item baseline contains invalid items.")
            candidates = [item for item in items if self._item_key(item) == creation_key[1]]
            if len(candidates) > 1:
                raise WorkflowBlocked("Multiple existing schedule items match the creation key; reconcile duplicates before preview.")
            if candidates:
                item = candidates[0]
                item_id = _integer(item.get("itemId"), "existing itemId", 0)
                if self.verify({**request, "itemId": item_id}, {"items": [item]}):
                    raise WorkflowBlocked("Existing schedule item conflicts with the proposed creation; use an explicit itemId update.")
                continue  # The exact item already exists; do not POST it again.
            request = {**request, "existingItemIds": [_integer(item.get("itemId"), "existing itemId", 0) for item in items]}
            reconciled.append(request)
        return {"requests": reconciled}, baselines

    @staticmethod
    def _item_key(item: dict[str, Any]) -> str:
        # Comments are editable content, not permission to create the same shift again.
        recurrence = item.get("recurrence") or {}
        if not isinstance(recurrence, dict):
            raise WorkflowBlocked("Schedule-item recurrence baseline is invalid.")
        identity = {key: item.get(key) for key in ("type", "label", "shiftType", "startDate")}
        identity["recurrence"] = {key: recurrence.get(key) for key in ("type", "every", "weekdays")}
        days = identity["recurrence"]["weekdays"]
        if days is not None:
            if not isinstance(days, list) or not all(isinstance(day, str) for day in days):
                raise WorkflowBlocked("Schedule-item weekday baseline is invalid.")
            identity["recurrence"]["weekdays"] = sorted(days)
        return json.dumps(identity, sort_keys=True, separators=(",", ":"))

    def verification_request(self, request: dict[str, Any], response_output: Path) -> dict[str, Any]:
        if request["resourceType"] != "workScheduleItem" or request["method"] != "POST":
            return request
        try:
            response = json.loads(response_output.read_text(encoding="utf-8"))
            item_id = _integer(response.get("itemId"), "created itemId", 0)
        except (OSError, ValueError, AttributeError, WorkflowBlocked) as error:
            raise WorkflowBlocked("Created schedule-item response has no valid itemId; reconcile the write before retry.", failure_class="fusion_api_error") from error
        if item_id in request.get("existingItemIds", []):
            raise WorkflowBlocked("Returned schedule itemId existed before POST; reconcile the write before retry.", failure_class="fusion_api_error")
        return {**request, "itemId": item_id}

    def build_preview(self, payload: dict[str, Any], environment: str, baselines: dict[str, Any]) -> dict[str, Any]:
        preview = {"taskCode": self.task_code, "executionDirection": "ora_rest_execution", "environment": environment,
                   "requests": payload["requests"], "currentState": baselines, "designValidation": payload.get("designValidation")}
        preview["sha256"] = hashlib.sha256(json.dumps(preview, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        return preview

    def verify(self, request: dict[str, Any], actual: dict[str, Any] | None) -> list[str]:
        if request["resourceType"] in {"workSchedule", "shift"}:
            if not isinstance(actual, dict):
                return ["parent resource was not found after PUT"]
            return [
                key for key, value in request["body"].items()
                if (_ofsc_time(actual.get(key)) if key in {"workTimeStart", "workTimeEnd"} else str(actual.get(key)))
                != (_ofsc_time(value) if key in {"workTimeStart", "workTimeEnd"} else str(value))
            ]
        items = actual.get("items", []) if isinstance(actual, dict) else []
        item_id = request.get("itemId")
        matched = next((item for item in items if item_id and str(item.get("itemId")) == str(item_id)), None)
        if request["method"] == "DELETE":
            return [] if matched is None else ["item_id still present"]
        if request["method"] == "POST" and not item_id:
            return ["created itemId is missing from write response"]
        if not isinstance(matched, dict):
            return ["created or updated item not found"]
        differences = []
        for key, value in request["body"].items():
            if key == "recurrence":
                actual_recurrence = matched.get("recurrence", {})
                if not isinstance(actual_recurrence, dict):
                    differences.append(key)
                    continue
                for part in ("type", "every", "weekdays"):
                    if part not in value:
                        continue
                    observed, expected = actual_recurrence.get(part), value[part]
                    if part == "weekdays" and isinstance(observed, list) and all(isinstance(day, str) for day in observed):
                        observed, expected = sorted(observed), sorted(expected)
                    if observed != expected:
                        differences.append(key)
                        break
            elif matched.get(key) != value:
                differences.append(key)
        return differences
