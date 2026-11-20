"""Free-format XLSX intake for the Resource Types task."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import quote
import xml.etree.ElementTree as ElementTree
import zipfile

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from guarded_xlsx import GuardedWorkbook, column_index, shared_string


class WorkbookInputError(ValueError):
    pass


def _normal(value: object) -> str:
    # Templates may mark mandatory columns with an asterisk.  Treat the marker
    # as presentation only so the free-format reader accepts both forms.
    return " ".join(str(value or "").replace("*", "").strip().split()).casefold()


def _boolean(value: object, field: str) -> bool:
    normalized = _normal(value)
    if normalized in {"true", "yes", "y", "1", "active", "enabled"}:
        return True
    if normalized in {"false", "no", "n", "0", "inactive", "disabled"}:
        return False
    raise WorkbookInputError(f"{field} must be an unambiguous boolean.")


def _role(values: dict[str, object], label: str) -> str:
    value = _normal(values.get("role"))
    aliases = {
        "field resource": "field_resource",
        "field_resource": "field_resource",
        "vehicle": "vehicle",
        "tool": "tool",
        "bucket": "bucket",
        "organization unit": "organization_unit",
        "organization_unit": "organization_unit",
        "warehouse": "warehouse",
        "mnt resource": "mnt_resource",
        "mnt_resource": "mnt_resource",
    }
    if value in aliases:
        return aliases[value]
    # In the supplied comparison matrix, several clinical Resource Types omit
    # the repeated Role cell but declare an Associated Resource Role.
    if str(values.get("associated resource role") or "").strip():
        return "field_resource"
    raise WorkbookInputError(f"{label}: Role is required and must be a supported Resource Type role.")


_cell_column = column_index


def _read_xlsx(workbook: Path) -> dict[str, list[list[object]]]:
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    rel_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    package_ns = "{http://schemas.openxmlformats.org/package/2006/relationships}"
    try:
        with GuardedWorkbook(workbook) as archive:
            shared_root = archive.xml("xl/sharedStrings.xml") if "xl/sharedStrings.xml" in archive.namelist() else None
            shared = [] if shared_root is None else ["".join(node.itertext()) for node in shared_root.findall(f"{ns}si")]
            book = archive.xml("xl/workbook.xml")
            rels = archive.xml("xl/_rels/workbook.xml.rels")
            targets = {item.attrib["Id"]: item.attrib["Target"] for item in rels.findall(f"{package_ns}Relationship")}
            sheets: dict[str, list[list[object]]] = {}
            for sheet in book.findall(f"{ns}sheets/{ns}sheet"):
                target = targets.get(sheet.attrib.get(f"{rel_ns}id", ""))
                if not target:
                    raise WorkbookInputError("Workbook sheet relationship is missing.")
                path = target.lstrip("/") if target.startswith("/") else "xl/" + target
                data = archive.xml(path)
                rows: list[list[object]] = []
                for row in data.findall(f"{ns}sheetData/{ns}row"):
                    cells: dict[int, object] = {}
                    for cell in row.findall(f"{ns}c"):
                        index = _cell_column(cell.attrib.get("r", ""))
                        raw = cell.find(f"{ns}v")
                        if cell.attrib.get("t") == "inlineStr": value = "".join(cell.itertext())
                        elif raw is None: value = None
                        elif cell.attrib.get("t") == "s": value = shared_string(shared, raw.text)
                        elif cell.attrib.get("t") == "b": value = raw.text == "1"
                        else: value = raw.text
                        cells[index] = value
                    rows.append([cells.get(index) for index in range(1, max(cells, default=0) + 1)])
                sheets[sheet.attrib.get("name", "")] = rows
            return sheets
    except (OSError, KeyError, IndexError, ValueError, ElementTree.ParseError, zipfile.BadZipFile) as error:
        raise WorkbookInputError(f"Workbook could not be read: {error}") from error


def _resource_types_rows(workbook: Path) -> list[dict[str, object]]:
    if not workbook.is_file() or workbook.suffix.casefold() != ".xlsx":
        raise WorkbookInputError("workbook must be an existing .xlsx file.")
    sheets = _read_xlsx(workbook)
    target = next((rows for title, rows in sheets.items() if _normal(title) == "resource types"), None)
    if not target:
        raise WorkbookInputError("No Resource Types worksheet was found.")
    matrix_header_index = next(
        (index for index, row in enumerate(target) if len(row) > 1 and _normal(row[0]) == "rt info" and _normal(row[1]) == "label"),
        None,
    )
    if matrix_header_index is not None:
        headers = target[matrix_header_index]
        active_row = target[matrix_header_index + 1] if len(target) > matrix_header_index + 1 else []
        if len(active_row) < 2 or _normal(active_row[1]) != "active":
            raise WorkbookInputError("Resource Types matrix must contain an Active row immediately after Label.")
        records = []
        for column, value in enumerate(headers[3:], start=3):
            label = str(value or "").strip()
            if not label:
                continue
            values = {
                _normal(row[1]): row[column] if column < len(row) else None
                for row in target[matrix_header_index + 2:]
                if len(row) > 1 and _normal(row[1])
            }
            records.append({"label": label, "active": _boolean(active_row[column] if column < len(active_row) else None, "Active"), "values": values})
        if not records:
            raise WorkbookInputError("Resource Types matrix has no proposed Resource Types.")
        labels = [record["label"] for record in records]
        if len({label.casefold() for label in labels}) != len(labels):
            raise WorkbookInputError("Resource Type Label values must be unique.")
        return records
    headers = next((row for row in target if any(_normal(cell) in {"resource type label", "label", "resource type"} for cell in row)), None)
    if not headers:
        raise WorkbookInputError("Resource Types worksheet must contain a Resource Type Label column.")
    header_index = target.index(headers)
    names = [_normal(cell) for cell in headers]
    label_index = next(index for index, name in enumerate(names) if name in {"resource type label", "label", "resource type"})
    active_index = next((index for index, name in enumerate(names) if name in {"active", "status", "enabled"}), None)
    if active_index is None:
        raise WorkbookInputError("Resource Types worksheet must contain an Active column.")
    records = []
    for row in target[header_index + 1:]:
        if not any(value not in (None, "") for value in row):
            continue
        label = str(row[label_index] if label_index < len(row) else "").strip()
        if not label:
            raise WorkbookInputError("Resource Type Label is required.")
        values = {name: row[index] if index < len(row) else None for index, name in enumerate(names) if name}
        records.append({"label": label, "active": _boolean(row[active_index] if active_index < len(row) else None, "Active"), "values": values})
    if not records:
        raise WorkbookInputError("Resource Types worksheet has no proposed Resource Types.")
    labels = [record["label"] for record in records]
    if len({label.casefold() for label in labels}) != len(labels):
        raise WorkbookInputError("Resource Type Label values must be unique.")
    return records


def build_payload(
    workbook: Path,
    base_path: str,
    capabilities: tuple[str, ...],
    sources: dict[str, str] | None = None,
    rationales: dict[str, dict[str, str]] | None = None,
    english_names: dict[str, str] | None = None,
) -> dict[str, Any]:
    requests = []
    for record in _resource_types_rows(workbook):
        label = str(record["label"])
        values = record["values"]
        role = _role(values, label)
        english_name = (
            (english_names or {}).get(label.casefold(), "")
            or str(values.get("english display name") or "").strip()
        )
        if not english_name:
            raise WorkbookInputError(f"{label}: English display name is required.")
        configured = {name: False for name in capabilities}
        for capability in capabilities:
            source_name = (sources or {}).get(capability, capability)
            source = values.get(_normal(source_name))
            if source not in (None, ""):
                requested = _boolean(source, capability)
                rationale = (rationales or {}).get(label.casefold(), {}).get(_normal(source_name)) or str(values.get(f"{_normal(source_name)} rationale") or "").strip()
                if requested and not rationale:
                    raise WorkbookInputError(f"{record['label']}: {capability} requires documented business rationale.")
                configured[capability] = requested
        requests.append({"operationId": "put-resource-type", "method": "PUT", "path": f"{base_path}/{quote(label, safe='')}", "expectedStatuses": [200, 201], "body": {"label": label, "active": record["active"], "role": role, "capabilities": configured, "translations": [{"language": "en", "name": english_name}]}})
    return {"operation": "upsert", "requests": requests, "capabilityPolicy": "all optional capabilities disabled unless explicitly enabled with business rationale"}
