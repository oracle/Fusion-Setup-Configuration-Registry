#!/usr/bin/env python3
"""Render Data Loader helper results as user-friendly Markdown reports."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Iterable, TextIO


_FAILED_MARKERS = ("ERROR", "FAILED", "FAILURE", "REJECTED")
_SUCCESS_MARKERS = ("SUCCESS", "SUCCEEDED", "COMPLETE", "COMPLETED")
_WARNING_MARKERS = ("WARNING", "WARN")
_TECHNICAL_PREVIEW_FIELDS = {
    "restaction",
    "parentidentifier",
    "sourcereftablename",
}
_FSM_BUSINESS_OBJECT_FAILURE_RE = re.compile(
    r"Business object:\s*(?P<business_object>.+?)\.\s*"
    r"Status:\s*Completed with errors\.\s*"
    r"Status details:\s*(?P<details>.*?)(?=\r?\n\r?\nBusiness object:|\r?\n\r?\nTotal Objects|\Z)",
    re.DOTALL,
)
_FSM_DETAIL_OBJECT_RE = re.compile(
    r"Detail Object:\s*(?P<detail_object>.+?)\.\s*"
    r"Status:\s*Completed with errors\.\s*"
    r"Status Details:\s*(?P<details>.*?)(?=\r?\n(?:java\.|\. Started:)|\Z)",
    re.DOTALL,
)
_FSM_TOTALS_RE = re.compile(
    r"Total Objects Processed:\s*(?P<processed>\d+).*?"
    r"Total Objects Failed:\s*(?P<failed>\d+)",
    re.DOTALL,
)
_FSM_EXCEPTION_RE = re.compile(r"\bjava\.[A-Za-z0-9_$.]+(?:Exception|Error)\b")
_FSM_DECIMAL_PRECISION_RE = re.compile(
    r"Value\s+[^.\r\n]+?\s+for field\s+(?P<field>[A-Za-z][A-Za-z0-9_]*)\s+"
    r"exceeds the number of decimal places allowed\.",
    re.IGNORECASE,
)
_FBDI_ERROR_SECTION_RE = re.compile(
    r"Import completed with error or warning\.\s*Import errors or warnings are\.?",
    re.IGNORECASE,
)
_FBDI_ACTIONABLE_MESSAGE_RE = re.compile(
    r"\b(?:already exists|invalid|required|must|cannot|can't|does not exist|"
    r"not found|not allowed|duplicate|rejected|failed to|unable to)\b",
    re.IGNORECASE,
)
_FBDI_EXPLICIT_ERROR_RE = re.compile(
    r"^(?:(?:ERROR|FAILURE|FAILED|REJECTED|SEVERE)|(?:ORA|JBO|FND)-\d+)"
    r"\s*[:=\-]\s*(?P<message>.+)$",
    re.IGNORECASE,
)
_FBDI_LOG_PREFIX_RE = re.compile(
    r"^(?:####\[[^\]]+\]\s*\[[^\]]+\]\s*)?"
    r"(?:\d{1,2}/\d{1,2}/\d{2,4}\s+\d{1,2}:\d{2}:\d{2}\s+(?:AM|PM)\s+)?",
    re.IGNORECASE,
)
_FBDI_TECHNICAL_CODE_RE = re.compile(
    r"\b(?:FBDI_ERROR|ORA-\d+|JBO-\d+|FND-\d+)\b\s*[:=\-]?\s*",
    re.IGNORECASE,
)
_FBDI_EXCEPTION_CLASS_RE = re.compile(
    r"^(?:[A-Za-z_$][A-Za-z0-9_$]*\.)+"
    r"[A-Za-z_$][A-Za-z0-9_$]*(?:Exception|Error)\s*[:=\-]?\s*"
)


def _text(value: Any, default: str = "—") -> str:
    if value in (None, ""):
        return default
    return str(value)


def _cell(value: Any) -> str:
    return (
        _text(value)
        .replace("|", "\\|")
        .replace("\r\n", "<br>")
        .replace("\n", "<br>")
        .replace("\r", "<br>")
    )


def _label(value: str) -> str:
    if value == "journey-task-authorization":
        return "Run Book Task Authorization"
    spaced = (
        re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", value)
        .replace("_", " ")
        .replace("-", " ")
    )
    return " ".join(word.capitalize() for word in spaced.split())


def _fbdi_process_label(value: Any) -> str:
    rendered = _text(value, "ESS process")
    return {
        "ORA_FBDI_IMPORT": "FBDI Import",
        "ORA_FBDI_LOAD": "FBDI Load",
    }.get(rendered, rendered)


def _link(name: str, raw_path: str) -> str:
    path = str(Path(raw_path).expanduser().resolve())
    target = f"<{path}>" if any(character.isspace() for character in path) else path
    safe_name = name.replace("[", "\\[").replace("]", "\\]")
    return f"[{safe_name}]({target})"


def _table(
    headers: Iterable[str],
    rows: Iterable[Iterable[Any]],
    align: Iterable[str] | None = None,
) -> str:
    header_values = tuple(headers)
    alignments = tuple(align or ("---",) * len(header_values))
    lines = [
        "| " + " | ".join(_cell(value) for value in header_values) + " |",
        "|" + "|".join(alignments) + "|",
    ]
    lines.extend("| " + " | ".join(_cell(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def _preview_fields(headers: Iterable[Any], values: Iterable[Any] | None) -> str:
    if values is None:
        return "Headers only; no sample row generated."
    pairs: list[str] = []
    for raw_name, raw_value in zip(headers, values):
        name = str(raw_name)
        lowered = name.lower()
        if (
            lowered in _TECHNICAL_PREVIEW_FIELDS
            or lowered.startswith("sourceref")
            or lowered.endswith("id")
            or raw_value in (None, "")
        ):
            continue
        pairs.append(f"{_label(name)}: {_text(raw_value)}")
        if len(pairs) == 4:
            break
    return "; ".join(pairs) if pairs else "Sample row generated."


def render_sample_report(result: dict[str, Any]) -> str:
    output_name = _text(result.get("fileName"), "sample")
    output_path = _text(result.get("outputPath"), "")
    attribute_file = result.get("attributeDetailsFile") or {}
    key_file = result.get("keyFieldsFile") or {}
    is_xlsx = output_name.lower().endswith(".xlsx")

    intro = (
        "This is the generated sample files:"
        if is_xlsx and (attribute_file or key_file)
        else "This is the generated sample file:"
    )
    file_rows: list[tuple[str, str]] = [
        ("Editable sample" if is_xlsx else "DAT sample", _link(output_name, output_path))
    ]
    if attribute_file:
        file_rows.append(
            (
                "Attribute details",
                _link(
                    _text(attribute_file.get("fileName"), "attribute-details.xlsx"),
                    _text(attribute_file.get("outputPath"), ""),
                ),
            )
        )
    if key_file:
        file_rows.append(
            (
                "Key fields",
                _link(
                    _text(key_file.get("fileName"), "key-fields.xlsx"),
                    _text(key_file.get("outputPath"), ""),
                ),
            )
        )

    sections = result.get("sections") or []
    section_names = [
        _text(section.get("discriminator"), "Section")
        if isinstance(section, dict)
        else _text(section)
        for section in sections
    ]
    section_rows = [(index, section) for index, section in enumerate(section_names, start=1)]
    preview_rows = result.get("previewRows") or []
    previews = [
        (
            _text(item.get("section"), "Section"),
            _preview_fields(item.get("headers") or (), item.get("values")),
        )
        for item in preview_rows
        if isinstance(item, dict)
    ]
    if not previews:
        previews = [(section, "Section included in the generated sample.") for section in section_names]

    discriminator = _text(
        result.get("BusObjTopDiscriminator"), output_name.rsplit(".", 1)[0]
    )
    parts = [intro, _table(("File", "Link"), file_rows)]
    if section_rows:
        parts.extend(("Sections:", _table(("#", "Section"), section_rows, ("---:", "---"))))
    if previews:
        parts.extend((f"Preview — {discriminator}", _table(("Section", "Details"), previews)))
    return "\n\n".join(parts)


def render_sample_batch_report(result: dict[str, Any]) -> str:
    """Render an ordered multi-RESTBO sample-generation result."""
    intro = "These are the generated sample files:"
    file_rows: list[tuple[str, str, str]] = []
    for item in result.get("files") or []:
        if not isinstance(item, dict):
            continue
        file_rows.append(
            (
                _text(item.get("businessObject"), "Business object"),
                _text(item.get("type"), "Sample"),
                _link(
                    _text(item.get("fileName"), "sample"),
                    _text(item.get("outputPath"), ""),
                ),
            )
        )

    object_rows: list[tuple[int, str, str]] = []
    for index, item in enumerate(result.get("businessObjects") or [], start=1):
        if not isinstance(item, dict):
            continue
        discriminator = _text(item.get("BusObjTopDiscriminator"), "Business object")
        sections = ", ".join(_text(section) for section in item.get("sections") or [])
        object_rows.append((index, discriminator, sections or "—"))

    parts = [intro]
    if file_rows:
        parts.append(_table(("Business Object", "File", "Link"), file_rows))
    if object_rows:
        parts.extend(
            (
                "Business objects and sections:",
                _table(("#", "Business Object", "Sections"), object_rows, ("---:", "---", "---")),
            )
        )
    return "\n\n".join(parts)


def render_mandatory_attributes_report(result: dict[str, Any]) -> str:
    """Render the live required root attributes for a registered business object."""
    return _table(
        ("Attribute",),
        ((attribute,) for attribute in result.get("attributes") or ()),
    )


def render_key_attributes_report(result: dict[str, Any]) -> str:
    """Render live mandatory and foreign-key attributes by loader section."""
    return _table(
        ("Section", "Attribute", "Classification"),
        (
            (
                _text(row.get("section"), "Business object"),
                _text(row.get("attribute"), "Attribute"),
                _text(row.get("classification"), "Key attribute"),
            )
            for row in result.get("rows") or ()
            if isinstance(row, dict)
        ),
    )


def render_attribute_details_report(result: dict[str, Any]) -> str:
    output_name = _text(result.get("fileName"), "attribute-details.xlsx")
    output_path = _text(result.get("outputPath"), "")
    business_object = _text(
        result.get("UIName") or result.get("BusObjTopDiscriminator"),
        "Business object",
    )
    discriminator = _text(result.get("BusObjTopDiscriminator"))
    section_count = result.get("sectionCount")
    return "\n\n".join(
        (
            f"Attribute details for {business_object}:",
            _table(
                ("Item", "Value"),
                (
                    ("Business Object", business_object),
                    ("Discriminator", discriminator),
                    ("Sections", section_count),
                ),
            ),
            _table(
                ("File", "Link"),
                (("Attribute details", _link(output_name, output_path)),),
            ),
        )
    )


def render_initiation_report(result: dict[str, Any]) -> str:
    loads = [item for item in result.get("loads") or [] if isinstance(item, dict)]
    def friendly_load_type(item: dict[str, Any]) -> str:
        return {
            "ORA_CX_IMPORT": "Data Loader - CX Import",
            "FBDI": "Data Loader - FBDI",
            "FSM": "Data Loader - FSM",
        }.get(item.get("sourceType"), "Data Loader")

    def mapping_rows(item: dict[str, Any]) -> tuple[tuple[Any, ...], ...]:
        rows = []
        for mapping in item.get("columnMappings") or ():
            if not isinstance(mapping, dict):
                continue
            source = mapping.get("source_column")
            target = mapping.get("target_attribute")
            rule = mapping.get("match_rule")
            if not source or not target or rule == "Exact attribute":
                continue
            rows.append((source, target, rule or "Automatic mapping", "✅ Verified"))
        return tuple(rows)

    def details(item: dict[str, Any]) -> tuple[tuple[str, Any], ...]:
        rows: tuple[tuple[str, Any], ...] = (
            ("Data Set Name", item.get("dataSetName") or item.get("fileName")),
            ("Content ID(Request ID)", f"{_text(item.get('ContentId'))} ({_text(item.get('RequestId'))})"),
        )
        if item.get("sourceType") in {"ORA_CX_IMPORT", "FBDI"}:
            return (
                ("Data Set Name", item.get("dataSetName") or item.get("fileName")),
                ("Business Object Name", item.get("businessObject") or item.get("cxImportObjectName") or item.get("fbdiBusinessObject")),
                ("UCM Account", item.get("ucmAccount")),
                *rows[1:],
            )
        return rows

    if loads:
        parts = ["## Data Load In Progress", "The data loads were initiated successfully."]
        for index, item in enumerate(loads, start=1):
            parts.append(f"### Load {index} — {friendly_load_type(item)}")
            verified = mapping_rows(item)
            if verified:
                parts.extend((
                    "### Mapping verification",
                    _table(
                        ("Source Header", "Fusion Attribute", "Match Rule", "Verification"),
                        verified,
                    ),
                ))
            parts.append(_table(("Item", "Value"), details(item)))
        return "\n\n".join(parts)
    parts = [
        "## Data Load In Progress",
        f"The data load for {friendly_load_type(result)} Load Type was initiated successfully.",
    ]
    verified = mapping_rows(result)
    if verified:
        parts.extend((
            "### Mapping verification",
            _table(
                ("Source Header", "Fusion Attribute", "Match Rule", "Verification"),
                verified,
            ),
        ))
    parts.append(_table(("Item", "Value"), details(result)))
    return "\n\n".join(parts)


def render_validation_report(result: dict[str, Any]) -> str:
    """Render a successful pre-upload validation without implying submission."""
    rows = [
        ("Source file", result.get("fileName")),
        ("Business object", result.get("UIName") or result.get("BusObjTopDiscriminator")),
        ("Workbook structure", "Valid"),
        ("Live schema validation", "Valid"),
        ("Prepared archive", result.get("archiveName")),
    ]
    return "\n\n".join(
        (
            "The data-load file was validated successfully. Nothing was uploaded.",
            _table(("Check", "Result"), rows),
            _table(
                ("File", "Link"),
                ((
                    "Validated ZIP",
                    _link(result.get("archiveName"), result.get("outputPath")),
                ),),
            ) if result.get("outputPath") else "",
            _table(
                ("Next action", "Details"),
                (("When ready", "Submit a data-load request to upload and initiate this file."),),
            ),
        )
    )


def _status(value: Any) -> str:
    rendered = _text(value, "").upper()
    if any(marker in rendered for marker in _FAILED_MARKERS):
        return "❌ Failed"
    if any(marker in rendered for marker in _SUCCESS_MARKERS):
        return "✅ Succeeded"
    if any(marker in rendered for marker in _WARNING_MARKERS):
        return "⚠️ Warning"
    if rendered:
        return "🟡 In progress"
    return "❔ Not available yet"


def _overall_status(data_sets: list[dict[str, Any]]) -> str:
    if not data_sets:
        return "❔ Not available yet"
    statuses = [
        _status(item.get("DataSetStatus") or item.get("DataSetStatusMeaning"))
        for item in data_sets
    ]
    if any("Failed" in status for status in statuses):
        return "❌ Failed"
    if all("Succeeded" in status for status in statuses):
        return "✅ Succeeded"
    if any("Warning" in status for status in statuses):
        return "⚠️ Warning"
    return "🟡 In progress"


def render_status_report(result: dict[str, Any], *, status_only: bool = False) -> str:
    data_sets = [
        item for item in (result.get("dataSets") or []) if isinstance(item, dict)
    ]
    errors = [
        item
        for item in (result.get("dataSetErrors") or [])
        if isinstance(item, dict)
    ]
    log_diagnostics = _fsm_process_log_diagnostics(result)
    log_diagnostics.extend(_fbdi_process_log_diagnostics(result))
    error_parts = _status_error_parts(errors, data_sets, log_diagnostics)
    process_log_parts = _fsm_process_log_parts(result)
    fbdi_process_log_parts = _fbdi_process_log_parts(result)
    non_fsm_log_parts = _non_fsm_error_log_parts(result)
    cx_import_log_parts = _cx_import_error_log_parts(result)
    overall = _overall_status(data_sets)
    if not data_sets:
        if status_only and not error_parts and not process_log_parts and not fbdi_process_log_parts and not non_fsm_log_parts and not cx_import_log_parts:
            return _table(("Data load", "Status"), (("Current status", overall),))
        parts = [_table(("Data load", "Status"), (("Object status", overall),))]
        if error_parts:
            parts.extend(error_parts)
        if process_log_parts:
            parts.extend(process_log_parts)
        if fbdi_process_log_parts:
            parts.extend(fbdi_process_log_parts)
        if non_fsm_log_parts:
            parts.extend(non_fsm_log_parts)
        if cx_import_log_parts:
            parts.extend(cx_import_log_parts)
        elif not error_parts:
            parts.append(
                _table(
                    ("Next action", "Details"),
                    (("Check again shortly", "Errors can be queried after Fusion returns a data set."),),
                )
            )
        return "\n\n".join(parts)

    object_rows: list[tuple[Any, ...]] = []
    for item in data_sets:
        name = (
            item.get("DataSetName")
            or item.get("UIName")
            or item.get("BusinessObject")
            or "Unknown data set"
        )
        object_rows.append(
            (
                name,
                _status(item.get("DataSetStatus") or item.get("DataSetStatusMeaning")),
                item.get("ObjectTotalCount"),
                item.get("ObjectLoadedCount"),
                item.get("ObjectErrorCount"),
            )
        )
    parts = [
        _table(
            ("Data Set", "Status", "Total", "Loaded", "Failed"),
            object_rows,
            ("---", "---", "---:", "---:", "---:"),
        )
    ]

    if status_only and not error_parts and not process_log_parts and not fbdi_process_log_parts and not non_fsm_log_parts and not cx_import_log_parts:
        return "\n\n".join(parts)
    if error_parts:
        parts.extend(error_parts)
    elif not errors and not any(
        str(item.get("SourceType") or "").strip() == "FSM" for item in data_sets
    ):
        parts.extend(
            (
                "Errors:",
                _table(
                    ("Result", "Details"),
                    (("✅ None returned", "Fusion returned no data-set errors."),),
                ),
            )
        )
    if process_log_parts:
        parts.extend(process_log_parts)
    if fbdi_process_log_parts:
        parts.extend(fbdi_process_log_parts)
    if non_fsm_log_parts:
        parts.extend(non_fsm_log_parts)
    if cx_import_log_parts:
        parts.extend(cx_import_log_parts)
    return "\n\n".join(parts)


def _fsm_process_log_parts(result: dict[str, Any]) -> list[str]:
    logs = [item for item in result.get("fsmProcessLogs") or [] if isinstance(item, dict)]
    files = [item for item in logs if item.get("outputPath") and item.get("fileName")]
    failures = [
        item
        for item in result.get("fsmProcessLogErrors") or []
        if isinstance(item, dict) and item.get("error")
    ]
    parts: list[str] = []
    if files:
        parts.extend(
            (
                "FSM Process Logs:",
                _table(
                    ("Data Set", "File"),
                    (
                        (
                            item.get("dataSetName") or "FSM data set",
                            _link(str(item["fileName"]), str(item["outputPath"])),
                        )
                        for item in files
                    ),
                ),
            )
        )
    if failures:
        parts.extend(
            (
                "FSM Process Log:",
                _table(
                    ("Data Set", "Result", "Details"),
                    (
                        (
                            item.get("dataSetName") or "FSM data set",
                            "❌ Not downloaded",
                            item["error"],
                        )
                        for item in failures
                    ),
                ),
            )
        )
    return parts


def _fbdi_process_log_warning_rows(result: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in result.get("fbdiProcessLogErrors") or []:
        if not isinstance(item, dict) or not item.get("error"):
            continue
        rows.append(
            {
                "dataSetName": _text(item.get("dataSetName"), "FBDI data set"),
                "processName": _fbdi_process_label(item.get("processName")),
                "stage": _text(item.get("stage"), "ESS log retrieval"),
                "message": _text(item.get("error")),
            }
        )
    return rows


def _fbdi_process_log_parts(result: dict[str, Any]) -> list[str]:
    logs = [item for item in result.get("fbdiProcessLogs") or [] if isinstance(item, dict)]
    files = [item for item in logs if item.get("outputPath") and item.get("fileName")]
    warnings = _fbdi_process_log_warning_rows(result)
    parts: list[str] = []
    if files:
        parts.extend(
            (
                "FBDI ESS Process Logs:",
                _table(
                    ("Data Set", "Process", "Status", "File"),
                    (
                        (
                            item.get("dataSetName") or "FBDI data set",
                            item.get("processLabel")
                            or _fbdi_process_label(item.get("processName")),
                            _status(item.get("processStatus")),
                            _link(str(item["fileName"]), str(item["outputPath"])),
                        )
                        for item in files
                    ),
                ),
            )
        )
    if warnings:
        parts.extend(
            (
                "FBDI ESS Log Warnings:",
                _table(
                    ("Data Set", "Process", "Stage", "Details"),
                    (
                        (
                            item["dataSetName"],
                            item["processName"],
                            item["stage"],
                            item["message"],
                        )
                        for item in warnings
                    ),
                ),
            )
        )
    return parts


def _non_fsm_error_log_parts(result: dict[str, Any]) -> list[str]:
    logs = [item for item in result.get("nonFsmErrorLogs") or [] if isinstance(item, dict)]
    files = [item for item in logs if item.get("outputPath") and item.get("fileName")]
    warnings = _non_fsm_error_log_warning_rows(result)
    parts: list[str] = []
    if files:
        parts.extend(
            (
                "Data Loader Error Logs:",
                _table(
                    ("Data Set", "File"),
                    (
                        (
                            item.get("dataSetName") or "Data set",
                            _link(str(item["fileName"]), str(item["outputPath"])),
                        )
                        for item in files
                    ),
                ),
            )
        )
    if warnings:
        parts.extend(
            (
                "Data Loader Error Log Warnings:",
                _table(
                    ("Data Set", "Stage", "Details"),
                    (
                        (item["businessObject"], item["stage"], item["message"])
                        for item in warnings
                    ),
                ),
            )
        )
    return parts


def _non_fsm_error_log_warning_rows(result: dict[str, Any]) -> list[dict[str, str]]:
    labels = {
        "failedLines": "Failed Lines",
        "dataSetAllObjects": "Data Set Object Errors",
    }
    rows: list[dict[str, str]] = []
    for log in result.get("nonFsmErrorLogs") or []:
        if not isinstance(log, dict):
            continue
        data_set_name = _text(log.get("dataSetName"), "Data set")
        for item in log.get("sectionErrors") or []:
            if not isinstance(item, dict) or not item.get("error"):
                continue
            section = labels.get(str(item.get("section")), "Error details")
            rows.append(
                {
                    "businessObject": data_set_name,
                    "stage": "Diagnostic log",
                    "message": f"{section} were unavailable: {_text(item.get('error'))}",
                }
            )
    for item in result.get("nonFsmErrorLogErrors") or []:
        if isinstance(item, dict) and item.get("error"):
            rows.append(
                {
                    "businessObject": _text(item.get("dataSetName"), "Data set"),
                    "stage": "Diagnostic log",
                    "message": _text(item.get("error")),
                }
            )
    return rows


def _cx_import_error_log_parts(result: dict[str, Any]) -> list[str]:
    logs = [item for item in result.get("cxImportErrorLogs") or [] if isinstance(item, dict)]
    files = [item for item in logs if item.get("outputPath") and item.get("fileName")]
    warnings: list[dict[str, str]] = []
    for log in logs:
        data_set_name = _text(log.get("dataSetName"), "CX Import data set")
        for item in log.get("sectionErrors") or []:
            if isinstance(item, dict) and item.get("error"):
                warnings.append(
                    {
                        "dataSetName": data_set_name,
                        "stage": _text(item.get("section"), "CX Import errors"),
                        "message": _text(item.get("error")),
                    }
                )
    for item in result.get("cxImportErrorLogErrors") or []:
        if isinstance(item, dict) and item.get("error"):
            warnings.append(
                {
                    "dataSetName": _text(item.get("dataSetName"), "CX Import data set"),
                    "stage": "Diagnostic log",
                    "message": _text(item.get("error")),
                }
            )
    parts: list[str] = []
    if files:
        parts.extend(
            (
                "CX Import Error Logs:",
                _table(
                    ("Data Set", "File"),
                    (
                        (
                            item.get("dataSetName") or "CX Import data set",
                            _link(str(item["fileName"]), str(item["outputPath"])),
                        )
                        for item in files
                    ),
                ),
            )
        )
    if warnings:
        parts.extend(
            (
                "CX Import Error Log Warnings:",
                _table(
                    ("Data Set", "Stage", "Details"),
                    ((item["dataSetName"], item["stage"], item["message"]) for item in warnings),
                ),
            )
        )
    return parts


def _error_business_object_name(
    item: dict[str, Any], data_sets: list[dict[str, Any]]
) -> str:
    if item.get("UIName"):
        return str(item["UIName"])
    if item.get("BusinessObject"):
        return str(item["BusinessObject"])
    error_data_set_id = item.get("DataSetId")
    if error_data_set_id not in (None, ""):
        for data_set in data_sets:
            if str(data_set.get("DataSetId")) == str(error_data_set_id):
                return str(
                    data_set.get("UIName")
                    or data_set.get("BusinessObject")
                    or "Unknown business object"
                )
    if len(data_sets) == 1:
        data_set = data_sets[0]
        return str(
            data_set.get("UIName")
            or data_set.get("BusinessObject")
            or "Unknown business object"
        )
    return "Unknown business object"


def _status_error_parts(
    errors: list[dict[str, Any]],
    data_sets: list[dict[str, Any]],
    fsm_diagnostics: list[dict[str, str]] = [],
) -> list[str]:
    error_rows: list[tuple[Any, ...]] = []
    for item in errors:
        message = _data_set_error_message(item)
        if message is not None:
            error_rows.append(
                (
                    len(error_rows) + 1,
                    _error_business_object_name(item, data_sets),
                    item.get("OriginatingProcessName")
                    or item.get("OriginatingProcess")
                    or "Processing",
                    message,
                )
            )
    diagnostic_start = len(error_rows)
    error_rows.extend(
        (
            diagnostic_start + index,
            diagnostic["businessObject"],
            diagnostic["stage"],
            diagnostic["message"],
        )
        for index, diagnostic in enumerate(fsm_diagnostics, start=1)
    )
    if not error_rows:
        return []
    return [
        "Errors:",
        _table(
            ("#", "Business Object", "Stage", "Error"),
            error_rows,
            ("---:", "---", "---", "---"),
        ),
        _table(
            ("Next action", "Details"),
            (
                (
                    "Correct the source data",
                    "Address the listed diagnostics, validate the corrected source, and resubmit it.",
                ),
            ),
        ),
    ]


def _data_set_error_message(item: dict[str, Any]) -> str | None:
    """Return a nonblank dataSetErrors MsgText without transforming it."""
    value = item.get("MsgText")
    if value is None:
        return None
    message = str(value)
    return message if message.strip() else None


def _fsm_process_log_diagnostics(result: dict[str, Any]) -> list[dict[str, str]]:
    """Summarize FSM ProcessLog failures without changing the downloaded bytes."""
    diagnostics: list[dict[str, str]] = []
    for log in result.get("fsmProcessLogs") or []:
        if not isinstance(log, dict) or not isinstance(log.get("content"), bytes):
            continue
        text = log["content"].decode("utf-8", errors="replace")
        log_diagnostics = _parse_fsm_process_log(text)
        diagnostics.extend(log_diagnostics)
    return diagnostics


def _parse_fbdi_process_log(text: str) -> list[str]:
    """Summarize actionable FBDI errors while ignoring operational log noise."""
    normalized = (
        text.replace("\\r\\n", "\n")
        .replace("\\n", "\n")
        .replace("\\r", "\n")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )
    candidates: list[str] = []
    in_error_section = False
    for raw_line in normalized.split("\n"):
        line = " ".join(raw_line.strip().split())
        if not line:
            continue
        line = _FBDI_LOG_PREFIX_RE.sub("", line).strip()
        if _FBDI_ERROR_SECTION_RE.search(line):
            in_error_section = True
            continue
        if in_error_section and (
            line.startswith("---") or line.casefold().startswith("refer to ")
        ):
            in_error_section = False
            continue

        message = ""
        if in_error_section:
            if line.endswith(":"):
                continue
            if " - " in line:
                message = line.split(" - ", 1)[1].strip()
            elif _FBDI_ACTIONABLE_MESSAGE_RE.search(line):
                message = line
        else:
            explicit = _FBDI_EXPLICIT_ERROR_RE.match(line)
            if explicit:
                message = explicit.group("message").strip()
        if not message:
            continue
        message = _FBDI_EXCEPTION_CLASS_RE.sub("", message)
        message = _FBDI_TECHNICAL_CODE_RE.sub("", message).strip(" :-")
        if not message:
            continue
        message = message[:500].rstrip()
        candidates.append(message)

    ordered: list[str] = []
    counts: dict[str, int] = {}
    originals: dict[str, str] = {}
    for message in candidates:
        key = message.casefold()
        if key not in counts:
            ordered.append(key)
            originals[key] = message
            counts[key] = 0
        counts[key] += 1
    return [
        originals[key]
        if counts[key] == 1
        else f"{originals[key]} ({counts[key]} occurrences)"
        for key in ordered[:10]
    ]


def _fbdi_process_log_diagnostics(result: dict[str, Any]) -> list[dict[str, str]]:
    diagnostics: list[dict[str, str]] = []
    for log in result.get("fbdiProcessLogs") or []:
        if not isinstance(log, dict) or not isinstance(log.get("content"), bytes):
            continue
        messages = _parse_fbdi_process_log(
            log["content"].decode("utf-8", errors="replace")
        )
        diagnostics.extend(
            {
                "businessObject": _text(log.get("businessObject"), "FBDI import"),
                "stage": _text(
                    log.get("processLabel")
                    or _fbdi_process_label(log.get("processName")),
                    "ESS process",
                ),
                "message": message,
            }
            for message in messages
        )
    return diagnostics


def _parse_fsm_process_log(text: str) -> list[dict[str, str]]:
    # ProcessLog sometimes serializes line breaks as literal escape sequences.
    # Normalize those before applying the block patterns so a single failure
    # cannot absorb the remaining log into the dashboard diagnostic.
    text = text.replace("\\r\\n", "\n").replace("\\n", "\n")
    diagnostics: list[dict[str, str]] = []
    for match in _FSM_BUSINESS_OBJECT_FAILURE_RE.finditer(text):
        business_object = _fsm_text(match.group("business_object"))
        details = match.group("details")
        if "already processed" in details.casefold():
            # Fusion reports these dependent objects under the primary failed
            # object. They do not add an independent corrective action.
            continue
        detail_match = _FSM_DETAIL_OBJECT_RE.search(details)
        summary = _fsm_text(details.split("Detail Object:", 1)[0])
        if detail_match:
            detail_object = _fsm_text(detail_match.group("detail_object"))
            detail_summary = _fsm_text(detail_match.group("details"))
            summary = f"{detail_object}: {detail_summary}" if detail_summary else detail_object
        precision_fields = _FSM_DECIMAL_PRECISION_RE.findall(details)
        if precision_fields:
            field = _label(precision_fields[0])
            count = len(precision_fields)
            row_label = "row" if count == 1 else "rows"
            prefix = f"{detail_object}: " if detail_match and detail_object else ""
            summary = (
                f"{prefix}{field} has more decimal places than allowed in {count} "
                f"{row_label}. Use a value with the allowed precision, then reimport."
            )
        elif _FSM_EXCEPTION_RE.search(details):
            summary = (
                f"{detail_object}: The FSM import rejected an invalid value."
                if detail_match and detail_object
                else "The FSM import rejected an invalid value."
            )
        if summary:
            diagnostics.append(
                {
                    "businessObject": business_object or "FSM import",
                    "stage": "FSM Import",
                    "message": summary,
                }
            )
    if diagnostics:
        return diagnostics

    totals = _FSM_TOTALS_RE.search(text)
    failed = int(totals.group("failed")) if totals else 0
    if failed or "Status: Completed with errors" in text:
        if totals:
            message = (
                f"FSM import completed with errors: {failed} failed of "
                f"{totals.group('processed')} processed objects."
            )
        else:
            message = "FSM import completed with errors."
        return [
            {
                "businessObject": "FSM import",
                "stage": "FSM Import",
                "message": message,
            }
        ]
    return []


def _fsm_text(value: str) -> str:
    return " ".join(value.split())


def _join_fsm_summary(*parts: str) -> str:
    return " ".join(part for part in parts if part)


def _response_messages(value: Any) -> list[str]:
    messages: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            lowered = str(key).lower()
            if lowered in {
                "detail",
                "message",
                "msgtext",
                "title",
                "o:errorcode",
                "errorcode",
                "errormessage",
                "status",
                "requestid",
            } and nested not in (None, ""):
                messages.append(f"{_label(str(key))}: {_text(nested)}")
            elif isinstance(nested, (dict, list)):
                messages.extend(_response_messages(nested))
    elif isinstance(value, list):
        for item in value:
            messages.extend(_response_messages(item))
    return messages


def _next_action(stage: str, error: str = "") -> str:
    if stage == "partial-business-object-validation":
        return "Confirm whether to continue with the eligible business objects only."
    if stage == "journey-task-authorization":
        match = re.search(r"Run Book Task for (.+?) not defined", error)
        if match:
            return (
                f"Configure the {match.group(1)} Task in runbook and retry the operation."
            )
        return "Configure the required Run Book task and retry the operation."
    if stage == "business-object-validation" and "did not contain a UcmContentId" in error:
        return "Perform the Business Object Attribute Update, then retry the request."
    actions = {
        "approval": "Reply with an approval to upload and initiate this exact validated load.",
        "configuration": "Correct the environment properties and retry.",
        "source-selection": "Supply one supported source file and retry.",
        "file-validation": "Correct the source file, validate it again, and retry.",
        "business-object-validation": "Align the source with the live business-object metadata and retry.",
        "sample-generation": "Correct the sample request or output location and retry.",
        "ucm-upload": "Correct the upload or access issue and retry the approved source.",
        "data-load-initiation": "Correct the initiation error and retry without reusing an unverified payload.",
        "status-input": "Provide a positive numeric request ID and retry.",
        "data-loader-data-sets": "Verify access to dataLoaderDataSets and retry the status lookup.",
        "data-set-errors": "Verify access to dataSetErrors and retry the status lookup.",
    }
    return actions.get(stage, "Correct the reported issue and retry the operation.")


def _requires_mapping_attention(item: dict[str, Any]) -> bool:
    if item.get("status") == "unmapped":
        return True
    return (
        item.get("status") == "fuzzy"
        and (item.get("confidence") is None or float(item["confidence"]) < 1.0)
    )


def _is_safe_header_correction(item: dict[str, Any]) -> bool:
    source = item.get("source_column")
    target = item.get("target_attribute")
    if not isinstance(source, str) or not isinstance(target, str) or source == target:
        return False
    compact_source = re.sub(r"[\s/]+", "", source).casefold()
    compact_target = re.sub(r"[\s/]+", "", target).casefold()
    return compact_source == compact_target


def render_error_report(error: Any) -> str:
    payload = error.as_dict() if hasattr(error, "as_dict") else dict(error)
    if payload.get("stage") == "input-required":
        return _text(payload.get("error"), "Additional input is required.")
    response = payload.get("response")
    if isinstance(response, dict) and response.get("fbdiSelectionRequired") is True:
        candidates = [
            (item.get("businessObject"), str(item.get("matchCount")))
            for item in response.get("candidates", [])
            if isinstance(item, dict) and _text(item.get("businessObject"))
        ]
        if candidates:
            return "\n\n".join((
                "## FBDI Business Object selection required",
                "Multiple Business Objects match the same number of CSV files.",
                _table(("Business Object", "Matching CSVs"), candidates),
                "Choose one listed Business Object and retry preflight with `--business-object <exact-name>`.",
            ))
    if (
        payload.get("stage") == "business-object-validation"
        and isinstance(response, dict)
        and response.get("selectionRequired") is True
    ):
        candidates = [
            _text(item.get("discriminator"))
            for item in response.get("candidates", [])
            if isinstance(item, dict) and _text(item.get("discriminator"))
        ]
        if candidates:
            return "\n\n".join((
                "## Business Object selection required",
                _table(
                    ("Worksheet", "Result"),
                    ((response.get("rootWorksheet"), "Multiple registered Business Objects match this 30-character prefix."),),
                ),
                _table(
                    ("Candidate Business Object",),
                    ((candidate,) for candidate in candidates),
                ),
                "Choose one exact Business Object discriminator and retry with `--business-object <exact-discriminator>`.",
            ))
    preflight = _preflight_validation(payload)
    if preflight is not None:
        if not preflight["mappingComplete"]:
            review_rows = [
                item
                for item in preflight["columnMappings"]
                if _requires_mapping_attention(item)
                or item.get("match_rule") not in (None, "Exact attribute")
            ]
            return "\n\n".join((
                "## Mapping stage",
                _table(("Source", "Type"), ((item["sourceName"], item["businessObject"]) for item in preflight["eligible"])),
                "### Attribute Review",
                _table(
                    ("Source Header", "Fusion Attribute", "Match Rule", "Mapping confidence"),
                    (
                        (
                            f"🟥 {item.get('source_column')}",
                            "—",
                            "Unresolved",
                            "0%",
                        )
                        if item.get("status") == "unmapped"
                        else (
                            f"🟨 {item.get('source_column')}",
                            item.get("target_attribute") or "—",
                            item.get("match_rule") or "Automatic mapping",
                            f"{float(item.get('confidence') or 0) * 100:.0f}%",
                        )
                        for item in review_rows
                    ),
                ),
                "### Action required",
                "Provide mappings, exclusions, or corrected attributes for every unresolved header. After validation succeeds, approval is still required unless the original request included auto-approval wording.",
            ))
        passed = ", ".join(item["sourceName"] for item in preflight["eligible"])
        parts = [
            "## Business Object Validation",
            _table(("Source", "Type"), (
                (item["sourceName"], item["businessObject"])
                for item in preflight["eligible"]
            )),
        ]
        if preflight["cxFiles"]:
            parts.extend((
                "### CX Import files",
                _table(
                    ("CSV file", "ZIP member", "Role"),
                    (
                        (item["fileName"], item["memberName"], item["role"])
                        for item in preflight["cxFiles"]
                    ),
                ),
            ))
        cx_import_details = []
        if preflight["cxImportObjectCode"]:
            cx_import_details.append(("Object Name", preflight["cxImportObjectCode"]))
        if preflight["cxUcmAccount"]:
            cx_import_details.append(("UCM Account", preflight["cxUcmAccount"]))
        if cx_import_details:
            parts.extend((
                "### CX Import details",
                _table(("Item", "Value"), cx_import_details),
            ))
        fbdi_details = []
        if preflight["fbdiBusinessObject"]:
            fbdi_details.append(("Business Object", preflight["fbdiBusinessObject"]))
        if preflight["fbdiUcmAccount"]:
            fbdi_details.append(("UCM Account", preflight["fbdiUcmAccount"]))
        if preflight["fbdiFiles"]:
            fbdi_details.append(("Matched Files", ", ".join(preflight["fbdiFiles"])))
        if fbdi_details:
            parts.extend((
                "### FBDI routing",
                _table(("Item", "Value"), fbdi_details),
            ))
        mapped_columns = [
            item
            for item in preflight["columnMappings"]
            if item.get("target_attribute")
        ]
        user_approved_columns = [
            item
            for item in mapped_columns
            if item.get("status") in {"manual", "approved-fuzzy"}
        ]
        corrected_columns = [
            item
            for item in mapped_columns
            if item not in user_approved_columns
            and item.get("source_column") != item.get("target_attribute")
        ]
        ignored_columns = [item for item in preflight["columnMappings"] if not item.get("target_attribute")]
        displayed_columns = user_approved_columns or corrected_columns
        if displayed_columns:
            heading = (
                "### User-approved attributes"
                if user_approved_columns
                else "### Automatic header corrections"
            )
            parts.extend((
                heading,
                _table(
                    ("Source Header", "Fusion Attribute"),
                    (
                        (
                            item.get("source_column"),
                            item.get("target_attribute"),
                        )
                        for item in displayed_columns
                    ),
                ),
            ))
        if ignored_columns:
            if not displayed_columns:
                parts.append("### Column handling")
            parts.extend((
                f"#### Ignored columns ({len(ignored_columns)})",
                _table(
                    ("Section", "Source column", "Reason"),
                    ((item.get("section"), item.get("source_column"), item.get("reason")) for item in ignored_columns),
                ),
            ))
        if preflight["archiveName"]:
            validated_label = (
                "Validated CSV group"
                if preflight["sourceType"] == "ORA_CX_IMPORT" and not preflight["archivePath"]
                else "Validated ZIP"
            )
            archive_name = (
                _link(preflight["archiveName"], preflight["archivePath"])
                if preflight["archivePath"]
                else preflight["archiveName"]
            )
            parts.extend(("### Validated upload", _table(
                ("Item", "Value"),
                (
                    (validated_label, archive_name),
                ),
            )))
        parts.extend((
            "### Validation complete",
            f"{passed} passed validation. No data was uploaded.",
            "### Approval required",
            "Reply with an approval to upload and initiate this exact validated load.",
        ))
        return "\n\n".join(parts)
    partial = _partial_business_object_validation(payload)
    if partial is not None:
        failed = partial["failed"]
        eligible = partial["eligible"]
        required = partial["required"]
        failed_names = ", ".join(_label(item) for item in required)
        eligible_names = ", ".join(
            _label(str(item.get("businessObject") or "Business object"))
            for item in eligible
        )
        return "\n\n".join(
            (
                "Some business objects failed validation. No data was uploaded.",
                _table(
                    ("Business Object", "Source file", "Validation issue"),
                    (
                        (
                            item.get("businessObject"),
                            item.get("sourceName"),
                            _partial_validation_issue(item),
                        )
                        for item in failed
                    ),
                ),
                _table(
                    ("Eligible business object", "Source file"),
                    (
                        (item.get("businessObject"), item.get("sourceName"))
                        for item in eligible
                    ),
                ),
                _table(
                    ("Next action", "Details"),
                    (
                        (
                            "Confirmation required",
                            f"{failed_names} couldn't be included. {eligible_names} "
                            "are ready to load. Would you like to continue with only the ready business objects?",
                        ),
                    ),
                ),
            )
        )
    stage = _text(payload.get("stage"), "operation")
    ucm_access_denied = _ucm_upload_access_denied(payload, stage)
    if ucm_access_denied is not None:
        parts = [
                _table(
                    ("Stage", "Result", "Details"),
                    (("UCM upload", "❌ Failed", ucm_access_denied),),
                ),
        ]
        uploaded_documents = _uploaded_ucm_documents(payload)
        if uploaded_documents:
            parts.extend((
                "Already created UCM documents:",
                _table(
                    ("CSV file", "Content ID"),
                    ((item["fileName"], item["contentId"]) for item in uploaded_documents),
                ),
            ))
        parts.append(
                _table(
                    ("Next action", "Details"),
                    ((
                        "Required",
                        "Ask a Fusion security administrator to grant the authenticated user "
                        f"access to the UCM account `{_ucm_upload_account(payload)}` and retry the approved source.",
                    ),),
                )
        )
        return "\n\n".join(parts)
    details = [_text(payload.get("error"), "The operation failed.")]
    if payload.get("httpStatus") not in (None, ""):
        details.append(f"HTTP {payload['httpStatus']}")
    if payload.get("RequestId") not in (None, ""):
        details.append(f"Request ID: {payload['RequestId']}")
    for message in _response_messages(payload.get("response")):
        if message not in details:
            details.append(message)
    parts = [
            _table(
                ("Stage", "Result", "Details"),
                ((_label(stage), "❌ Failed", "<br>".join(details)),),
            ),
    ]
    uploaded_documents = _uploaded_ucm_documents(payload)
    if uploaded_documents:
        parts.extend((
            "Already created UCM documents; no data load was initiated:",
            _table(
                ("CSV file", "Content ID"),
                ((item["fileName"], item["contentId"]) for item in uploaded_documents),
            ),
        ))
    parts.append(
        _table(("Next action", "Details"), (("Required", _next_action(stage, details[0])),))
    )
    return "\n\n".join(parts)


def _ucm_upload_access_denied(payload: dict[str, Any], stage: str) -> str | None:
    """Render UCM check-in authorization errors without exposing raw server fields."""
    response = payload.get("response")
    if stage != "ucm-upload" or payload.get("httpStatus") != 403 or not isinstance(response, dict):
        return None
    if isinstance(response.get("uploadError"), dict):
        response = response["uploadError"]
    error_key = _text(response.get("errorKey"))
    if response.get("errorCode") != "-18" and "csUserInsufficientAccess" not in error_key:
        return None
    account = _text(response.get("dDocAccount"))
    if not account:
        return None
    return (
        "The authenticated Fusion user does not have permission to upload files "
        f"to the UCM account `{account}`. No data load was initiated."
    )


def _ucm_upload_account(payload: dict[str, Any]) -> str:
    response = payload.get("response")
    if not isinstance(response, dict):
        return "UCM"
    if isinstance(response.get("uploadError"), dict):
        response = response["uploadError"]
    return _text(response.get("dDocAccount"), "UCM")


def _uploaded_ucm_documents(payload: dict[str, Any]) -> list[dict[str, str]]:
    response = payload.get("response")
    if not isinstance(response, dict):
        return []
    return [
        {"fileName": _text(item.get("fileName")), "contentId": _text(item.get("contentId"))}
        for item in response.get("uploadedFiles") or []
        if isinstance(item, dict) and item.get("fileName") and item.get("contentId")
    ]


def _partial_business_object_validation(
    payload: dict[str, Any],
) -> dict[str, list[dict[str, str]]] | None:
    response = payload.get("response")
    if not isinstance(response, dict):
        return None
    raw = response.get("partialBusinessObjectValidation")
    if not isinstance(raw, dict):
        return None
    failed = [item for item in raw.get("failed") or [] if isinstance(item, dict)]
    eligible = [item for item in raw.get("eligible") or [] if isinstance(item, dict)]
    required = [str(item) for item in raw.get("requiredSkipBusinessObjects") or [] if str(item)]
    if not failed or not eligible or not required:
        return None
    return {"failed": failed, "eligible": eligible, "required": required}


def _partial_validation_issue(item: dict[str, Any]) -> str:
    details = item.get("mismatchDetails")
    if isinstance(details, list):
        readable = [str(detail) for detail in details if str(detail)]
        if readable:
            return " ".join(readable)
    return _text(item.get("message"), "Validation failed.")


def _preflight_validation(payload: dict[str, Any]) -> dict[str, Any] | None:
    response = payload.get("response")
    if not isinstance(response, dict):
        return None
    raw = response.get("preflight")
    if not isinstance(raw, dict):
        return None
    eligible = [
        {"sourceName": _text(item.get("sourceName")), "businessObject": _text(item.get("businessObject"))}
        for item in raw.get("eligible") or []
        if isinstance(item, dict)
    ]
    if not eligible:
        return None
    archive_path = raw.get("archivePath")
    cx_import_object_code = raw.get("cxImportObjectCode")
    cx_ucm_account = raw.get("cxUcmAccount")
    fbdi_business_object = raw.get("fbdiBusinessObject")
    fbdi_ucm_account = raw.get("fbdiUcmAccount")
    return {
        "eligible": eligible,
        "archiveName": _text(raw.get("archiveName")),
        "archivePath": archive_path.strip() if isinstance(archive_path, str) else "",
        "archiveSha256": _text(raw.get("archiveSha256")),
        "sourceType": _text(raw.get("sourceType")),
        "cxImportObjectCode": (
            cx_import_object_code.strip()
            if isinstance(cx_import_object_code, str)
            else ""
        ),
        "cxUcmAccount": (
            cx_ucm_account.strip()
            if isinstance(cx_ucm_account, str)
            else ""
        ),
        "fbdiBusinessObject": (
            fbdi_business_object.strip()
            if isinstance(fbdi_business_object, str)
            else ""
        ),
        "fbdiUcmAccount": (
            fbdi_ucm_account.strip()
            if isinstance(fbdi_ucm_account, str)
            else ""
        ),
        "fbdiFiles": [
            item.strip()
            for item in raw.get("fbdiFiles") or []
            if isinstance(item, str) and item.strip()
        ],
        "cxFiles": [
            {
                "fileName": _text(item.get("fileName")),
                "memberName": _text(item.get("memberName")),
                "role": _text(item.get("role")),
            }
            for item in raw.get("cxFiles") or []
            if isinstance(item, dict)
        ],
        "columnMappings": [item for item in raw.get("columnMappings") or [] if isinstance(item, dict)],
        "mappingComplete": raw.get("mappingComplete") is not False,
    }


def _visual_error_rows(
    errors: list[dict[str, Any]],
    data_sets: list[dict[str, Any]],
    fsm_diagnostics: list[dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in errors:
        message = _data_set_error_message(item)
        if message is not None:
            rows.append(
                {
                    "businessObject": _error_business_object_name(item, data_sets),
                    "stage": _text(
                        item.get("OriginatingProcessName")
                        or item.get("OriginatingProcess"),
                        "Processing",
                    ),
                    "message": message,
                }
            )
    rows.extend(fsm_diagnostics)
    return rows


def build_visual_model(
    result: dict[str, Any] | Any,
    report_type: str,
    *,
    status_only: bool = False,
) -> dict[str, Any]:
    """Create the allow-listed data model used by the inline Loader dashboard."""
    if report_type == "error":
        payload = result.as_dict() if hasattr(result, "as_dict") else dict(result)
        if payload.get("stage") == "input-required":
            return {
                "kind": "input-required",
                "title": "Additional input required",
                "tone": "progress",
                "summary": _text(payload.get("error"), "Additional input is required."),
            }
        preflight = _preflight_validation(payload)
        if preflight is not None:
            passed = ", ".join(item["sourceName"] for item in preflight["eligible"])
            facts = [("Passed validation", passed)]
            if preflight["sourceType"]:
                facts.append(("Source type", preflight["sourceType"]))
            if preflight["cxFiles"]:
                facts.append((
                    "CX Import files",
                    ", ".join(
                        f"{item['fileName']} ({item['role']})"
                        for item in preflight["cxFiles"]
                    ),
                ))
            if preflight["cxImportObjectCode"]:
                facts.append(("Object Name", preflight["cxImportObjectCode"]))
            if preflight["cxUcmAccount"]:
                facts.append(("UCM Account", preflight["cxUcmAccount"]))
            if preflight["archiveName"]:
                facts.append(("Validated ZIP", preflight["archiveName"]))
            return {
                "kind": "validation",
                "title": "Business Object Validation",
                "tone": "progress",
                "summary": (
                    f"{len(preflight['eligible'])} source(s) passed source validation. "
                ),
                "facts": facts,
                "nextAction": "Reply with an approval to upload and initiate this exact validated load.",
            }
        partial = _partial_business_object_validation(payload)
        if partial is not None:
            return {
                "kind": "error",
                "title": "Business objects need attention",
                "tone": "failed",
                "summary": "No data was uploaded.",
                "facts": [
                    (
                        "Eligible business objects",
                        ", ".join(
                            item.get("businessObject", "Business object")
                            for item in partial["eligible"]
                        ),
                    )
                ],
                "errors": [
                    {
                        "businessObject": item.get("businessObject", "Business object"),
                        "stage": "Validation",
                        "message": _partial_validation_issue(item),
                    }
                    for item in partial["failed"]
                ],
                "nextAction": ", ".join(_label(item) for item in partial["required"])
                + " couldn't be included. "
                + ", ".join(
                    _label(str(item.get("businessObject") or "Business object"))
                    for item in partial["eligible"]
                )
                + " are ready to load. Would you like to continue with only the ready business objects?",
            }
        stage = _text(payload.get("stage"), "operation")
        details = [_text(payload.get("error"), "The operation failed.")]
        if payload.get("httpStatus") not in (None, ""):
            details.append(f"HTTP {payload['httpStatus']}")
        if payload.get("RequestId") not in (None, ""):
            details.append(f"Request ID: {payload['RequestId']}")
        details.extend(_response_messages(payload.get("response")))
        return {
            "kind": "error",
            "title": "Data load needs attention",
            "tone": "failed",
            "summary": "The requested operation did not complete.",
            "failure": {"stage": _label(stage), "details": details},
            "nextAction": _next_action(stage, _text(payload.get("error"))),
        }

    payload = dict(result)
    if report_type == "validation":
        sections = [
            _text(section, "Business object")
            for section in payload.get("sections") or []
        ]
        return {
            "kind": "validation",
            "title": "Business Object Validation",
            "tone": "success",
            "summary": "The source file is ready for upload.",
            "facts": [
                ("Source file", _text(payload.get("fileName"))),
                ("Business object", _text(payload.get("UIName") or payload.get("BusObjTopDiscriminator"))),
                ("Workbook structure", "Valid"),
                ("Live schema validation", "Valid"),
                ("Prepared archive", _text(payload.get("archiveName"))),
            ],
            "sections": sections,
            "nextAction": "Submit a data-load request to upload and initiate this file.",
        }
    if report_type == "mandatory-attributes":
        attributes = [_text(item, "Attribute") for item in payload.get("attributes") or []]
        return {
            "kind": "sample",
            "title": f"{_text(payload.get('UIName') or payload.get('BusObjTopDiscriminator'), 'Business object')} mandatory attributes",
            "tone": "success",
            "summary": "",
            "sections": [_text(payload.get("BusObjTopDiscriminator"), "Business object")],
            "previews": [{"section": attribute, "details": "Mandatory"} for attribute in attributes],
        }
    if report_type == "key-attributes":
        rows = [row for row in payload.get("rows") or [] if isinstance(row, dict)]
        sections = list(dict.fromkeys(_text(row.get("section"), "Business object") for row in rows))
        return {
            "kind": "sample",
            "title": f"{_text(payload.get('UIName') or payload.get('BusObjTopDiscriminator'), 'Business object')} mandatory and foreign-key attributes",
            "tone": "success",
            "summary": "",
            "sections": sections,
            "previews": [
                {
                    "section": _text(row.get("attribute"), "Attribute"),
                    "details": f"{_text(row.get('classification'), 'Key attribute')} · {_text(row.get('section'), 'Business object')}",
                }
                for row in rows
            ],
        }
    if report_type == "sample":
        previews = []
        for item in payload.get("previewRows") or []:
            if isinstance(item, dict):
                previews.append(
                    {
                        "section": _text(item.get("section"), "Section"),
                        "details": _preview_fields(item.get("headers") or (), item.get("values")),
                    }
                )
        sections = [
            _text(item.get("discriminator"), "Section") if isinstance(item, dict) else _text(item, "Section")
            for item in payload.get("sections") or []
        ]
        if not previews:
            previews = [{"section": section, "details": "Section included in the generated sample."} for section in sections]
        return {
            "kind": "sample",
            "title": "Sample files generated",
            "tone": "success",
            "summary": "Your editable Data Loader sample is ready.",
            "sections": sections,
            "previews": previews,
        }

    if report_type == "attribute-details":
        section_summaries = [
            item for item in payload.get("sectionSummaries") or [] if isinstance(item, dict)
        ]
        sections = [
            _text(item.get("section"), "Section") for item in section_summaries
        ] or [_text(item, "Section") for item in payload.get("sections") or []]
        previews = [
            {
                "section": _text(item.get("section"), "Section"),
                "details": f"{_text(item.get('attributeCount'), '0')} attributes",
            }
            for item in section_summaries
        ]
        return {
            "kind": "attribute-details",
            "title": f"{_text(payload.get('UIName') or payload.get('BusObjTopDiscriminator'), 'Business object')} Attribute details",
            "tone": "success",
            "summary": f"Schema details for {_text(payload.get('UIName') or payload.get('BusObjTopDiscriminator'), 'Business object')}.",
            "facts": [
                ("Business Object", _text(payload.get("UIName") or payload.get("BusObjTopDiscriminator"))),
                ("Discriminator", _text(payload.get("BusObjTopDiscriminator"))),
                ("Sections", _text(payload.get("sectionCount"))),
            ],
            "sections": sections,
            "previews": previews,
        }

    if report_type == "initiation":
        loads = [item for item in payload.get("loads") or [] if isinstance(item, dict)]
        if loads:
            return {
                "kind": "initiation",
                "title": "Data loads initiated",
                "tone": "success",
                "summary": "Fusion accepted each data load for asynchronous processing.",
                "facts": [
                    (
                        f"Load {index}",
                        " · ".join(
                            (
                                _text(item.get("dataSetName") or item.get("fileName")),
                                f"Content ID {_text(item.get('ContentId'))}",
                                f"Request ID {_text(item.get('RequestId'))}",
                            )
                        ),
                    )
                    for index, item in enumerate(loads, start=1)
                ],
                "errors": [],
                "nextAction": "",
            }
        return {
            "kind": "initiation",
            "title": "Data load initiated",
            "tone": "success",
            "summary": "Fusion accepted the data load for asynchronous processing.",
            "facts": [
                ("Data Set Name", _text(payload.get("dataSetName") or payload.get("fileName"))),
                ("UCM Content ID", _text(payload.get("ContentId"))),
                ("Request ID", _text(payload.get("RequestId"))),
            ],
            "errors": [],
            "nextAction": "",
        }

    data_sets = [item for item in payload.get("dataSets") or [] if isinstance(item, dict)]
    errors = [item for item in payload.get("dataSetErrors") or [] if isinstance(item, dict)]
    rows = [
        {
            "name": _text(item.get("DataSetName") or item.get("UIName") or item.get("BusinessObject"), "Unknown data set"),
            "status": _status(item.get("DataSetStatus") or item.get("DataSetStatusMeaning")),
            "total": _text(item.get("ObjectTotalCount")),
            "loaded": _text(item.get("ObjectLoadedCount")),
            "failed": _text(item.get("ObjectErrorCount")),
        }
        for item in data_sets
    ]
    process_diagnostics = _fsm_process_log_diagnostics(payload)
    process_diagnostics.extend(_fbdi_process_log_diagnostics(payload))
    business_errors = _visual_error_rows(errors, data_sets, process_diagnostics)
    log_warnings = _non_fsm_error_log_warning_rows(payload)
    fbdi_log_warnings = [
        {
            "businessObject": item["dataSetName"],
            "stage": item["stage"],
            "message": f"{item['processName']}: {item['message']}",
        }
        for item in _fbdi_process_log_warning_rows(payload)
    ]
    log_warnings.extend(fbdi_log_warnings)
    visual_errors = business_errors + log_warnings
    process_log_errors = [
        item
        for item in payload.get("fsmProcessLogErrors") or []
        if isinstance(item, dict) and item.get("error")
    ]
    fbdi_process_log_errors = [
        item
        for item in payload.get("fbdiProcessLogErrors") or []
        if isinstance(item, dict) and item.get("error")
    ]
    return {
        "kind": "status",
        "title": "Data load status",
        "tone": "failed" if any("Failed" in row["status"] for row in rows) else ("success" if rows and all("Succeeded" in row["status"] for row in rows) else "progress"),
        "summary": _overall_status(data_sets),
        "statusOnly": status_only,
        "statusRows": rows,
        "errors": visual_errors,
        "nextAction": (
            (
                "Address the source diagnostics, then retry the status lookup for the unavailable log sections."
                if log_warnings
                else "Address the listed diagnostics, validate the corrected source, and resubmit it."
            )
            if business_errors
            else (
                "Retry the status lookup to complete the Data Loader error log."
                if log_warnings
                else (
                    "FSM ProcessLog could not be downloaded. Retry the status lookup."
                    if process_log_errors
                    else (
                        "FBDI ESS log could not be downloaded. Retry the status lookup."
                        if fbdi_process_log_errors
                        else ("Check again shortly; errors can be queried after Fusion returns a data set." if not rows else "")
                    )
                )
            )
        ),
    }


def write_inline_visual(
    result: dict[str, Any] | Any,
    report_type: str,
    output_path: str | Path,
    *,
    status_only: bool = False,
) -> Path:
    """Write a populated dashboard to an explicitly selected visualization path."""
    try:
        import data_loader_visual
    except ModuleNotFoundError:  # Imported from the skill root by tests.
        from scripts import data_loader_visual
    return data_loader_visual.write_dashboard(
        build_visual_model(result, report_type, status_only=status_only), Path(output_path)
    )


def verify_inline_visual(output_path: str | Path) -> bool:
    """Verify that the dashboard path can safely be handed to the inline renderer."""
    try:
        import data_loader_visual
    except ModuleNotFoundError:  # Imported from the skill root by tests.
        from scripts import data_loader_visual
    return data_loader_visual.verify_dashboard(Path(output_path))


def emit_inline_or_markdown(
    result: dict[str, Any] | Any,
    report_type: str,
    inline_output: str | Path | None,
    render_markdown: Callable[[Any], str],
    *,
    status_only: bool = False,
    stream: TextIO,
) -> bool:
    """Emit the user-friendly Markdown report.

    ``inline_output`` is retained as a no-op compatibility argument while
    inline dashboard rendering is disabled.  No HTML artifact is written.
    """
    del report_type, inline_output, status_only
    print(render_markdown(result), file=stream)
    return False
