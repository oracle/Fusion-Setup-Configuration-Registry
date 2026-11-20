"""Work Zones adapter for the shared Field Service workflow."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any
from urllib.parse import quote
import xml.etree.ElementTree as ElementTree
import zipfile


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from guarded_xlsx import GuardedWorkbook, column_index, shared_string
from task_orchestration import WorkflowBlocked, resolve_execution_route


TASK_CODE = "ORA_FFS_TS_WORK_ZONES"
LIVE_DIRECTION = "ora_rest_execution"
FIELD_ALIASES = {
    "workZoneName": {"work zone name", "work_zone_name", "workzonename"},
    "workZoneLabel": {"work zone label", "work_zone_label", "workzonelabel"},
    "status": {"status"},
    "keys": {"work zone key", "work_zone_key", "workzone_key", "keys"},
    "shapes": {"shapes", "work zone shapes"},
    "translations": {"translations", "work zone translations"},
}
DESIGN_FIELDS = {
    "geographic_eligibility_boundary": "geographic eligibility boundary",
    "practical_routing_pool_evidence": "practical routing pool evidence",
    "key_definition_governance": "key definition governance controlled",
    "compound_key": "compound key",
    "compound_key_business_need": "compound key business need",
    "assignment_model": "assignment model",
    "temporary_coverage_view": "temporary coverage view prepared",
    "immediate_routing_override": "immediate routing override",
    "urgency_justification": "urgency justification",
    "new_territory": "new territory",
    "travel_learning_plan": "travel learning / seed plan",
    "post_change_validation_plan": "post-change validation plan",
}
EXPECTED_RULE_NODES = (
    "WZ.VALIDATE_WORKBOOK",
    "WZ.ENFORCE_DESIGN",
    "WZ.RETURN_ISSUES",
    "WZ.RETURN_SUCCESS",
)


class WorkbookInputError(ValueError):
    pass


def _normal(value: object) -> str:
    return " ".join(str(value or "").strip().replace("*", "").split()).casefold()


def _text(value: object, field: str, sheet: str) -> str:
    rendered = str(value or "").strip()
    if not rendered:
        raise WorkbookInputError(f"{sheet}: {field} is required.")
    if rendered != str(value):
        raise WorkbookInputError(f"{sheet}: {field} must not have leading or trailing whitespace.")
    return rendered


_column_index = column_index


def _xlsx_rows(path: Path) -> list[tuple[str, list[list[object]]]]:
    main = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    rel = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    package = "{http://schemas.openxmlformats.org/package/2006/relationships}"
    try:
        with GuardedWorkbook(path) as archive:
            workbook = archive.xml("xl/workbook.xml")
            relationships = archive.xml("xl/_rels/workbook.xml.rels")
            targets = {node.attrib["Id"]: node.attrib["Target"] for node in relationships.findall(f"{package}Relationship")}
            try:
                strings = ["".join(node.itertext()) for node in archive.xml("xl/sharedStrings.xml").findall(f"{main}si")]
            except KeyError:
                strings = []
            sheets: list[tuple[str, list[list[object]]]] = []
            for sheet in workbook.findall(f"{main}sheets/{main}sheet"):
                target = targets.get(sheet.attrib.get(f"{rel}id", ""))
                if not target:
                    raise WorkbookInputError("Workbook sheet relationship is missing.")
                sheet_path = target.lstrip("/") if target.startswith("/") else "xl/" + target
                document = archive.xml(sheet_path)
                rows: list[list[object]] = []
                for row in document.findall(f"{main}sheetData/{main}row"):
                    cells: dict[int, object] = {}
                    for cell in row.findall(f"{main}c"):
                        value_node = cell.find(f"{main}v")
                        cell_type = cell.attrib.get("t")
                        if cell_type == "inlineStr":
                            value: object = "".join(cell.itertext())
                        elif value_node is None:
                            value = None
                        elif cell_type == "s":
                            value = shared_string(strings, value_node.text)
                        elif cell_type == "b":
                            value = value_node.text == "1"
                        else:
                            value = value_node.text
                        cells[_column_index(cell.attrib.get("r", ""))] = value
                    rows.append([cells.get(index) for index in range(1, max(cells, default=0) + 1)])
                sheets.append((sheet.attrib.get("name", ""), rows))
            return sheets
    except (OSError, KeyError, IndexError, ValueError, ElementTree.ParseError, zipfile.BadZipFile) as error:
        raise WorkbookInputError(f"Workbook could not be read: {error}") from error


def _headers(row: list[object]) -> dict[str, int]:
    discovered = {_normal(value): index for index, value in enumerate(row) if _normal(value)}
    return {
        field: next((discovered[alias] for alias in aliases if alias in discovered), -1)
        for field, aliases in FIELD_ALIASES.items()
    }


def _cell(row: list[object], index: int) -> object:
    return row[index] if index >= 0 and index < len(row) else None


def _is_next_section_marker(row: list[object]) -> bool:
    """Recognize the workbook navigation row that starts the next configuration table."""
    values = {_normal(value) for value in row if _normal(value)}
    return "o contents" in values or "o_contents" in values


def _values(value: object, field: str, sheet: str) -> list[str]:
    text = _text(value, field, sheet)
    values = [item.strip() for item in text.split(",") if item.strip()]
    if not values or len(values) != len({_normal(item) for item in values}):
        raise WorkbookInputError(f"{sheet}: {field} values must be unique.")
    if any(len(item) > 50 for item in values):
        raise WorkbookInputError(f"{sheet}: {field} values must be at most 50 characters.")
    return values


def _design_headers(row: list[object]) -> dict[str, int]:
    discovered = {
        _normal(value).rstrip("?").strip(): index
        for index, value in enumerate(row)
        if _normal(value)
    }
    return {
        field: next(
            (index for header, index in discovered.items() if header == expected or header.startswith(expected + " ")),
            -1,
        )
        for field, expected in DESIGN_FIELDS.items()
    }


def _required_design_text(value: object, label: str, rule: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise WorkbookInputError(f"{label}: {rule} requires design evidence.")
    return text


def _design_boolean(value: object, label: str, rule: str) -> bool:
    text = _required_design_text(value, label, rule).casefold()
    if text == "yes":
        return True
    if text == "no":
        return False
    raise WorkbookInputError(f"{label}: {rule} requires Yes or No.")


def build_preview_data(workbook: Path) -> dict[str, Any]:
    if not workbook.is_file() or workbook.suffix.casefold() != ".xlsx":
        raise WorkbookInputError("workbook must be an existing .xlsx file.")
    work_sheets = [(name, rows) for name, rows in _xlsx_rows(workbook) if "work zone" in _normal(name)]
    if not work_sheets:
        raise WorkbookInputError("No Work Zones worksheet was found.")
    requests: list[dict[str, Any]] = []
    for sheet, rows in work_sheets:
        header_index, mapping = next(
            ((index, _headers(row)) for index, row in enumerate(rows) if all(_headers(row)[field] >= 0 for field in ("workZoneName", "workZoneLabel", "status", "keys"))),
            (-1, {}),
        )
        if header_index < 0:
            raise WorkbookInputError(f"{sheet}: required Work Zone header row was not found.")
        for row in rows[header_index + 1 :]:
            if _is_next_section_marker(row):
                break
            if not any(value not in (None, "") for value in row):
                continue
            label_value = _cell(row, mapping["workZoneLabel"])
            if label_value in (None, ""):
                continue
            label = _text(label_value, "Work Zone Label", sheet)
            name = _text(_cell(row, mapping["workZoneName"]), "Work Zone Name", sheet)
            status = _text(_cell(row, mapping["status"]), "Status", sheet).casefold()
            if status not in {"active", "inactive"}:
                raise WorkbookInputError(f"{sheet}: Status must be active or inactive.")
            body: dict[str, Any] = {"workZoneLabel": label, "workZoneName": name, "status": status, "keys": _values(_cell(row, mapping["keys"]), "Work Zone Key", sheet)}
            for field in ("shapes",):
                value = _cell(row, mapping.get(field, -1))
                if value not in (None, ""):
                    body[field] = _values(value, "Shapes", sheet)
            translations = _cell(row, mapping.get("translations", -1))
            if translations not in (None, ""):
                try:
                    parsed_translations = json.loads(_text(translations, "Translations", sheet))
                except json.JSONDecodeError as error:
                    raise WorkbookInputError(f"{sheet}: Translations must be a JSON array when supplied.") from error
                if not isinstance(parsed_translations, list):
                    raise WorkbookInputError(f"{sheet}: Translations must be a JSON array when supplied.")
                body["translations"] = parsed_translations
            requests.append(
                {
                    "operationId": "resolve-work-zone",
                    "path": f"/rest/ofscMetadata/v1/workZones/{quote(label, safe='')}",
                    "identity": label,
                    "body": body,
                }
            )
    if not requests:
        raise WorkbookInputError("No populated Work Zone rows were found.")
    labels = [request["identity"] for request in requests]
    if len(labels) != len({_normal(label) for label in labels}):
        raise WorkbookInputError("Work Zone Label values must be unique case-insensitively.")
    keys = [key for request in requests for key in request["body"]["keys"]]
    if len(keys) != len({_normal(key) for key in keys}):
        raise WorkbookInputError("Work Zone Key values must be unique case-insensitively.")
    return {"operation": "create-or-replace", "requests": requests, "optionalCapabilityPolicy": "Only documented shapes and translations fields may be sent when supplied."}


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


class WorkZonesAdapter:
    task_code = TASK_CODE

    def resolve_route(self, direction: str | None) -> dict[str, str]:
        return resolve_execution_route(ROOT.parent / "ora-resource" / "ora_rest_execution.md", self.task_code, direction)

    def validate_design_rules(self, workbook: Path) -> None:
        """Execute the task-local WZ gates before REST current-state reads."""
        registry_path = ROOT.parent / "ora-resource" / "ora_rule_registry.json"
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise WorkflowBlocked("Work Zones rule registry could not be read.") from error
        task = next(
            (item for item in registry.get("tasks", []) if item.get("task_code") == self.task_code),
            None,
        )
        nodes = task.get("nodes") if isinstance(task, dict) else None
        if not isinstance(nodes, list) or tuple(node.get("id") for node in nodes) != EXPECTED_RULE_NODES:
            raise WorkflowBlocked("Work Zones rule registry is incomplete or has an unsafe execution order.")

        sheets = [(name, rows) for name, rows in _xlsx_rows(workbook) if "work zone" in _normal(name)]
        if not sheets:
            raise WorkbookInputError("No Work Zones worksheet was found.")
        evaluated = 0
        for sheet, rows in sheets:
            header_index, api_headers = next(
                ((index, _headers(row)) for index, row in enumerate(rows) if all(_headers(row)[field] >= 0 for field in ("workZoneName", "workZoneLabel", "status", "keys"))),
                (-1, {}),
            )
            if header_index < 0:
                raise WorkbookInputError(f"{sheet}: required Work Zone header row was not found.")
            design_headers = _design_headers(rows[header_index])
            missing = [DESIGN_FIELDS[field] for field, index in design_headers.items() if index < 0]
            if missing:
                raise WorkbookInputError(f"{sheet}: WZ.ENFORCE_DESIGN requires columns: {', '.join(missing)}.")
            for row in rows[header_index + 1 :]:
                if _is_next_section_marker(row):
                    break
                label_value = _cell(row, api_headers["workZoneLabel"])
                if label_value in (None, ""):
                    continue
                label = _text(label_value, "Work Zone Label", sheet)
                values = {field: _cell(row, index) for field, index in design_headers.items()}
                _required_design_text(values["geographic_eligibility_boundary"], label, "WZ.GEOGRAPHIC_ELIGIBILITY")
                _required_design_text(values["practical_routing_pool_evidence"], label, "WZ.GEOGRAPHIC_ELIGIBILITY")
                if not _design_boolean(values["key_definition_governance"], label, "WZ.SUPPORT_AND_GOVERNANCE"):
                    raise WorkbookInputError(f"{label}: WZ.SUPPORT_AND_GOVERNANCE requires controlled key-definition evidence.")
                if _design_boolean(values["compound_key"], label, "WZ.COMPOUND_KEY"):
                    _required_design_text(values["compound_key_business_need"], label, "WZ.COMPOUND_KEY")
                assignment = _required_design_text(values["assignment_model"], label, "WZ.ASSIGNMENT_MODEL").casefold()
                if assignment not in {"organization", "direct override", "temporary"}:
                    raise WorkbookInputError(f"{label}: WZ.ASSIGNMENT_MODEL must be Organization, Direct Override, or Temporary.")
                temporary_view = _design_boolean(values["temporary_coverage_view"], label, "WZ.TEMPORARY_COVERAGE")
                if assignment == "temporary" and not temporary_view:
                    raise WorkbookInputError(f"{label}: WZ.TEMPORARY_COVERAGE requires dispatcher-view evidence for temporary coverage.")
                if _design_boolean(values["immediate_routing_override"], label, "WZ.IMMEDIATE_OVERRIDE"):
                    _required_design_text(values["urgency_justification"], label, "WZ.IMMEDIATE_OVERRIDE")
                if _design_boolean(values["new_territory"], label, "WZ.NEW_TERRITORY_LEARNING"):
                    _required_design_text(values["travel_learning_plan"], label, "WZ.NEW_TERRITORY_LEARNING")
                plan = _required_design_text(values["post_change_validation_plan"], label, "WZ.POST_CHANGE_VALIDATION").casefold()
                if not any(token in plan for token in ("key", "zip", "postal")) or "eligib" not in plan:
                    raise WorkbookInputError(f"{label}: WZ.POST_CHANGE_VALIDATION must cover key resolution and resource eligibility.")
                evaluated += 1
        if not evaluated:
            raise WorkbookInputError("No populated Work Zone rows were found for WZ.ENFORCE_DESIGN.")

    def validate_design(self, workbook: Path) -> list[dict[str, str]]:
        """Expose the task-local enforcement gate to the shared runner."""
        self.validate_design_rules(workbook)
        return []

    def preflight(self, workbook: Path, get: Any, temp: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
        payload = build_preview_data(workbook)
        baselines: dict[str, dict[str, Any]] = {}
        for sequence, request in enumerate(payload["requests"], 1):
            label = request["identity"]
            singular_path = request["path"]
            baseline = get(singular_path, temp / f"baseline-{sequence}.json")
            if baseline is not None:
                baselines[label] = baseline
                request.update(
                    {
                        "operationId": "replace-work-zone",
                        "method": "PUT",
                        "path": singular_path,
                        "verifyPath": singular_path,
                    }
                )
            else:
                request.update(
                    {
                        "operationId": "create-work-zone",
                        "method": "POST",
                        "path": "/rest/ofscMetadata/v1/workZones",
                        "verifyPath": singular_path,
                    }
                )
        return payload, baselines

    def build_preview(self, payload: dict[str, Any], environment: str, baselines: dict[str, dict[str, Any]]) -> dict[str, Any]:
        if not environment.strip():
            raise WorkflowBlocked("environment is required.")
        requests = []
        for request in payload["requests"]:
            label = request["identity"]
            baseline = baselines.get(label)
            requests.append(
                {
                    "operationId": request["operationId"],
                    "method": request["method"],
                    "path": request["path"],
                    "verifyPath": request["verifyPath"],
                    "identity": label,
                    "headers": request.get("headers", {}),
                    "body": request["body"],
                    "baseline": baseline,
                }
            )
        draft = {"schemaVersion": "1.0", "taskCode": self.task_code, "executionDirection": LIVE_DIRECTION, "environment": environment.strip(), "requests": requests}
        return {**draft, "sha256": hashlib.sha256(_canonical_json(draft)).hexdigest(), "approvalRequired": True, "retryPolicy": "never"}

    def mismatches(self, expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
        return [field for field, value in expected.items() if actual.get(field) != value]

    def request_identity(self, request: dict[str, Any]) -> str:
        return str(request["identity"])
