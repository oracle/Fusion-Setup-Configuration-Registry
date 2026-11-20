"""Work Skills business rules for the shared Field Service task workflow."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import quote
import xml.etree.ElementTree as ElementTree
import zipfile

import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from guarded_xlsx import GuardedWorkbook, column_index, shared_string
from task_orchestration import WorkflowBlocked, resolve_execution_route


TASK_CODE = "ORA_FFS_TS_WORK_SKILLS"
MAX_WORKBOOK_RECORDS = 20000
LIVE_DIRECTION = "ora_rest_execution"
WORK_SKILLS_PATH = "/rest/ofscMetadata/v1/workSkills/"
WORK_SKILL_GROUPS_PATH = "/rest/ofscMetadata/v1/workSkillGroups/"
LANGUAGES_PATH = "/rest/ofscMetadata/v1/languages"
FIELD_ALIASES = {
    "label": ("work skill label", "label", "id", "work skill id"),
    "name": ("english name", "work skill name", "name"),
    "active": ("active", "status", "enabled"),
    "sharing": ("sharing of the skill in teamwork", "sharing", "teamwork sharing"),
}
GROUP_FIELD_ALIASES = {
    "label": ("work skill group label", "group label"),
    "name": ("english name", "work skill group name", "group name"),
    "active": ("active", "status", "enabled"),
    "assign_to_resource": ("assign to resource", "assign to resources"),
    "add_to_capacity_category": ("add to capacity category",),
    "purpose": ("business purpose / capacity rationale", "capacity rationale", "business purpose", "group purpose"),
}
MEMBER_FIELD_ALIASES = {
    "group_label": ("work skill group label", "group label"),
    "skill_label": ("work skill label", "skill label"),
    "ratio": ("ratio",),
}
DESIGN_FIELD_ALIASES = {
    "qualification_purpose": ("qualification difference / business purpose", "qualification difference", "business purpose"),
    "routing_evidence": ("routing / optimization validation evidence", "routing validation evidence", "optimization validation evidence"),
    "notes": ("notes / source reference", "notes", "source reference"),
}
RULE_REGISTRY = ROOT.parent / "ora-resource" / "ora_rule_registry.json"
DESIGN_RULE_IDS = (
    "WS.QUALIFICATION_MODEL",
    "WS.CONDITION_SOURCE",
    "WS.CONDITION_LOGIC",
    "WS.REQUIRED_AND_PREFERRED_LEVELS",
    "WS.ROUTING_ELIGIBILITY",
    "WS.ACTIVE_AND_ASSIGNED",
    "WS.TEAMWORK_SHARING",
    "WS.GROUPS_AND_CAPACITY",
    "WS.ADVANCED_VALIDATION",
)


class WorkSkillsInputError(ValueError):
    """Raised when a free-format workbook cannot safely produce a PUT preview."""


def _normalized(value: Any) -> str:
    # End-user templates mark mandatory headers with ``*``.  That marker is
    # presentation-only; it must not make an otherwise valid field unknown.
    return " ".join(str("" if value is None else value).strip().rstrip("*").strip().split()).casefold()


def _as_text(value: Any, field: str, sheet: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise WorkSkillsInputError(f"{sheet}: {field} is required.")
    return text


def _as_boolean(value: Any, field: str, sheet: str) -> bool:
    text = _normalized(value)
    if text in {"true", "yes", "y", "1", "active", "enabled"}:
        return True
    if text in {"false", "no", "n", "0", "inactive", "disabled"}:
        return False
    raise WorkSkillsInputError(f"{sheet}: {field} must be an unambiguous boolean.")


def _as_sharing(value: Any, sheet: str) -> str:
    sharing = _normalized(value)
    # The supplied Configuration API contract demonstrates ``maximal``.  Do
    # not translate UI display strings to undocumented API enum values.
    if sharing != "maximal":
        raise WorkSkillsInputError(
            f"{sheet}: Sharing must be Maximal until the API enum for other sharing modes is confirmed."
        )
    return sharing


def _as_optional_boolean(value: Any, field: str, sheet: str) -> bool:
    if value is None or not str(value).strip():
        return False
    return _as_boolean(value, field, sheet)


def _as_ratio(value: Any, sheet: str) -> int:
    text = _as_text(value, "Ratio", sheet)
    try:
        ratio = int(text)
    except ValueError as error:
        raise WorkSkillsInputError(f"{sheet}: Ratio must be a whole number.") from error
    if ratio < 0:
        raise WorkSkillsInputError(f"{sheet}: Ratio must not be negative.")
    return ratio


_column_index = column_index


def _read_workbook(workbook_path: Path) -> list[tuple[str, dict[str, Any]]]:
    spreadsheet = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    relationship = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    package_relationship = "{http://schemas.openxmlformats.org/package/2006/relationships}"
    if not workbook_path.is_file() or workbook_path.suffix.casefold() != ".xlsx":
        raise WorkSkillsInputError("workbook must be an existing .xlsx file.")
    try:
        with GuardedWorkbook(workbook_path) as archive:
            workbook = archive.xml("xl/workbook.xml")
            relationships = archive.xml("xl/_rels/workbook.xml.rels")
            try:
                shared_root = archive.xml("xl/sharedStrings.xml")
                shared_strings = ["".join(item.itertext()) for item in shared_root.findall(f"{spreadsheet}si")]
            except KeyError:
                shared_strings = []
            targets = {
                item.attrib["Id"]: item.attrib["Target"]
                for item in relationships.findall(f"{package_relationship}Relationship")
            }
            result = []

            def append_record(sheet_name: str, record: dict[str, Any]) -> None:
                archive.check_time()
                if len(result) >= MAX_WORKBOOK_RECORDS:
                    raise WorkSkillsInputError("Work Skills workbook record limit exceeded.")
                result.append((sheet_name, record))

            for sheet in workbook.findall(f"{spreadsheet}sheets/{spreadsheet}sheet"):
                target = targets.get(sheet.attrib.get(f"{relationship}id", ""))
                if not target:
                    raise WorkSkillsInputError("Workbook sheet relationship is missing.")
                path = target.lstrip("/") if target.startswith("/") else "xl/" + target
                root = archive.xml(path)
                archive.check_time()
                rows: list[dict[int, Any]] = []
                for row in root.findall(f"{spreadsheet}sheetData/{spreadsheet}row"):
                    archive.check_time()
                    cells: dict[int, Any] = {}
                    for cell in row.findall(f"{spreadsheet}c"):
                        column = _column_index(cell.attrib.get("r", ""))
                        value = cell.find(f"{spreadsheet}v")
                        if cell.attrib.get("t") == "inlineStr":
                            cells[column] = "".join(cell.itertext())
                        elif cell.attrib.get("t") == "s" and value is not None:
                            cells[column] = shared_string(shared_strings, value.text)
                        elif cell.attrib.get("t") == "b" and value is not None:
                            cells[column] = value.text == "1"
                        elif value is not None:
                            cells[column] = value.text
                    if cells:
                        rows.append(cells)
                sheet_name = sheet.attrib.get("name", "Unnamed worksheet")
                free_format: dict[str, Any] = {}
                for cells in rows:
                    archive.check_time()
                    key = _normalized(cells.get(1))
                    if key and cells.get(2) is not None:
                        free_format[key] = cells[2]
                table_detected = False
                active_labels: dict[int, str] = {}
                # A header starts a new section. Each following data row belongs
                # only to that section, never to all earlier headers.
                for values in rows:
                    archive.check_time()
                    labels = {}
                    for column, value in values.items():
                        label = _normalized(value)
                        if label:
                            labels[column] = label
                    has_skill = (
                        any(alias in labels.values() for alias in FIELD_ALIASES["label"])
                        and any(alias in labels.values() for alias in FIELD_ALIASES["name"])
                        and any(alias in labels.values() for alias in FIELD_ALIASES["active"])
                    )
                    has_group = (
                        any(alias in labels.values() for alias in GROUP_FIELD_ALIASES["label"])
                        and any(alias in labels.values() for alias in GROUP_FIELD_ALIASES["name"])
                        and any(alias in labels.values() for alias in GROUP_FIELD_ALIASES["active"])
                    )
                    has_member = all(any(alias in labels.values() for alias in aliases) for aliases in MEMBER_FIELD_ALIASES.values())
                    if has_skill or has_group or has_member:
                        table_detected = True
                        active_labels = labels
                        continue
                    if active_labels:
                        record = {
                            active_labels[column]: value
                            for column, value in values.items()
                            if column in active_labels
                        }
                        if (
                            any(alias in record for alias in FIELD_ALIASES["label"])
                            or any(alias in record for alias in GROUP_FIELD_ALIASES["label"])
                            or any(alias in record for alias in MEMBER_FIELD_ALIASES["group_label"])
                        ):
                            append_record(sheet_name, record)
                if free_format and not table_detected:
                    append_record(sheet_name, free_format)
                if "work skill condition" in _normalized(sheet_name):
                    condition_header_seen = False
                    for condition in rows:
                        archive.check_time()
                        if condition_header_seen:
                            if any(str(value or "").strip() for value in condition.values()):
                                append_record(sheet_name, {"__work_skill_conditions_configured": True})
                                break
                        elif {"model code/skill", "condition label", "work skill label"} & {
                            _normalized(value) for value in condition.values()
                        }:
                            condition_header_seen = True
            archive.check_time()
            return result
    except (KeyError, IndexError, OSError, ValueError, ElementTree.ParseError, zipfile.BadZipFile) as error:
        raise WorkSkillsInputError(f"Workbook could not be read: {error}") from error


def _field(values: dict[str, Any], field: str, sheet: str) -> Any:
    for alias in FIELD_ALIASES[field]:
        if alias in values:
            return values[alias]
    display = {
        "label": "Work Skill Label",
        "name": "English Name",
        "sharing": "Sharing of the skill in teamwork",
        "active": "Active",
    }[field]
    raise WorkSkillsInputError(f"{sheet}: {display} is required.")


def _group_field(values: dict[str, Any], field: str, sheet: str, required: bool = True) -> Any:
    for alias in GROUP_FIELD_ALIASES[field]:
        if alias in values:
            return values[alias]
    if required:
        raise WorkSkillsInputError(f"{sheet}: {field.replace('_', ' ').title()} is required.")
    return None


def _member_field(values: dict[str, Any], field: str, sheet: str) -> Any:
    for alias in MEMBER_FIELD_ALIASES[field]:
        if alias in values:
            return values[alias]
    raise WorkSkillsInputError(f"{sheet}: {field.replace('_', ' ').title()} is required.")


def _design_field(values: dict[str, Any], field: str, sheet: str) -> str:
    for alias in DESIGN_FIELD_ALIASES[field]:
        if alias in values:
            return str(values[alias] or "").strip()
    return ""


def _has_any(values: dict[str, Any], aliases: tuple[str, ...]) -> bool:
    return any(alias in values for alias in aliases)


def _is_group_record(values: dict[str, Any]) -> bool:
    return all(
        _has_any(values, GROUP_FIELD_ALIASES[field])
        for field in ("label", "name", "active")
    )


def _is_group_member_record(values: dict[str, Any]) -> bool:
    return all(_has_any(values, aliases) for aliases in MEMBER_FIELD_ALIASES.values())


def build_preview_data(workbook: Path) -> dict[str, Any]:
    skill_requests = []
    skill_design_records = []
    sources = _read_workbook(workbook)
    conditions_configured = any(values.get("__work_skill_conditions_configured") for _, values in sources)
    named_sources = [(sheet, values) for sheet, values in sources if _normalized(sheet) == "work skills"]
    generic_sources = [
        (sheet, values)
        for sheet, values in sources
        if not _is_group_record(values) and not _is_group_member_record(values)
    ]
    for sheet, values in named_sources or generic_sources:
        if not any(alias in values for alias in FIELD_ALIASES["label"]):
            continue
        label = _as_text(_field(values, "label", sheet), "Work Skill Label", sheet)
        name = _as_text(_field(values, "name", sheet), "English Name", sheet)
        active = _as_boolean(_field(values, "active", sheet), "Active", sheet)
        skill_design_records.append(
            {
                "label": label,
                "active": active,
                "sharing": _as_sharing(_field(values, "sharing", sheet), sheet),
                "qualificationPurpose": _design_field(values, "qualification_purpose", sheet),
                "routingEvidence": _design_field(values, "routing_evidence", sheet),
                "notes": _design_field(values, "notes", sheet),
            }
        )
        skill_requests.append(
            {
                "operationId": "put-work-skill",
                "method": "PUT",
                "path": f"{WORK_SKILLS_PATH}{quote(label, safe='')}",
                "expectedStatuses": [200],
                "body": {
                    "name": name,
                    "active": active,
                    "sharing": skill_design_records[-1]["sharing"],
                    "translations": [{"language": "en", "name": name}],
                },
                "label": label,
            }
        )
    labels = [request["label"] for request in skill_requests]
    if len(labels) != len(set(labels)):
        raise WorkSkillsInputError("Work Skill Label values must be unique.")
    group_sources = [(sheet, values) for sheet, values in sources if _is_group_record(values)]
    member_sources = [(sheet, values) for sheet, values in sources if _is_group_member_record(values)]
    groups: dict[str, dict[str, Any]] = {}
    group_design_records = []
    for sheet, values in group_sources:
        label = _as_text(_group_field(values, "label", sheet), "Work Skill Group Label", sheet)
        if label in groups:
            raise WorkSkillsInputError("Work Skill Group Label values must be unique.")
        name = _as_text(_group_field(values, "name", sheet), "English Name", sheet)
        purpose = _as_text(_group_field(values, "purpose", sheet), "Business Purpose / Capacity Rationale", sheet)
        add_to_capacity_category = _as_optional_boolean(
            _group_field(values, "add_to_capacity_category", sheet, required=False),
            "Add to Capacity Category",
            sheet,
        )
        group_design_records.append(
            {
                "label": label,
                "purpose": purpose,
                "addToCapacityCategory": add_to_capacity_category,
            }
        )
        groups[label] = {
            "active": _as_boolean(_group_field(values, "active", sheet), "Active", sheet),
            "assignToResource": _as_optional_boolean(_group_field(values, "assign_to_resource", sheet, required=False), "Assign to Resource", sheet),
            "addToCapacityCategory": add_to_capacity_category,
            "translations": [{"language": "en", "name": name}],
            "workSkills": [],
        }
    for sheet, values in member_sources:
        group_label = _as_text(_member_field(values, "group_label", sheet), "Work Skill Group Label", sheet)
        if group_label not in groups:
            raise WorkSkillsInputError(f"{sheet}: Work Skill Group Label {group_label} is not defined on Work Skill Groups.")
        skill_label = _as_text(_member_field(values, "skill_label", sheet), "Work Skill Label", sheet)
        groups[group_label]["workSkills"].append({"label": skill_label, "ratio": _as_ratio(_member_field(values, "ratio", sheet), sheet)})
    group_requests = []
    for label, body in groups.items():
        if not body["workSkills"]:
            raise WorkSkillsInputError(f"Work Skill Groups: {label} requires at least one Work Skill Group Member.")
        members = [item["label"] for item in body["workSkills"]]
        if len(members) != len(set(members)):
            raise WorkSkillsInputError(f"Work Skill Groups: {label} contains duplicate Work Skill Group Members.")
        group_requests.append({"operationId": "put-work-skill-group", "method": "PUT", "path": f"{WORK_SKILL_GROUPS_PATH}{quote(label, safe='')}", "expectedStatuses": [200], "body": body, "label": label, "memberLabels": members})
    requests = skill_requests + group_requests
    if not requests:
        raise WorkSkillsInputError("No worksheet supplied Work Skills or Work Skill Groups input.")
    return {
        "operation": "upsert",
        "requests": requests,
        "skillLabels": set(labels),
        "skillDesignRecords": skill_design_records,
        "groupDesignRecords": group_design_records,
        "conditionsConfigured": conditions_configured,
    }


def _design_rule_ids() -> set[str]:
    try:
        registry = json.loads(RULE_REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise WorkSkillsInputError(f"Work Skills rule registry could not be read: {error}") from error
    task = next(
        (
            item
            for item in registry.get("tasks", [])
            if isinstance(item, dict) and item.get("task_code") == TASK_CODE
        ),
        None,
    )
    if not isinstance(task, dict):
        raise WorkSkillsInputError("Work Skills rule registry has no task entry for ORA_FFS_TS_WORK_SKILLS.")
    return {
        node.get("id")
        for node in task.get("nodes", [])
        if isinstance(node, dict) and node.get("action_type") == "design_enforcement" and isinstance(node.get("id"), str)
    }


def enforce_design_rules(payload: dict[str, Any]) -> None:
    """Execute every registered Work Skills design gate before a live preview.

    The workbook is the available evidence source.  These checks therefore
    validate required evidence and configuration semantics, but never claim to
    prove real-world routing or optimization outcomes from free text alone.
    """
    registered = _design_rule_ids()
    if registered != set(DESIGN_RULE_IDS):
        missing = sorted(set(DESIGN_RULE_IDS) - registered)
        unexpected = sorted(registered - set(DESIGN_RULE_IDS))
        raise WorkSkillsInputError(
            "Work Skills rule registry and executable validators disagree "
            f"(missing={missing}, unexpected={unexpected})."
        )
    skills = payload.get("skillDesignRecords", [])
    groups = payload.get("groupDesignRecords", [])
    if not isinstance(skills, list) or not isinstance(groups, list):
        raise WorkSkillsInputError("Design-enforcement input is incomplete.")
    def condition_rules() -> list[str]:
        if not payload.get("conditionsConfigured"):
            return []
        return [
            "WS.CONDITION_SOURCE: Work Skill Conditions require a separately approved payload and reliable activity attributes.",
            "WS.CONDITION_LOGIC: Work Skill Conditions require explicit AND-logic eligibility validation.",
            "WS.REQUIRED_AND_PREFERRED_LEVELS: Work Skill Conditions require explicit required/preferred level mapping.",
        ]

    def qualification_model() -> list[str]:
        return [
            f"WS.QUALIFICATION_MODEL: {record.get('label', 'unknown')} lacks qualification evidence."
            for record in skills
            if not str(record.get("qualificationPurpose", "")).strip()
        ]

    def routing_eligibility() -> list[str]:
        return [
            f"WS.ROUTING_ELIGIBILITY: active skill {record.get('label', 'unknown')} lacks routing evidence."
            for record in skills
            if bool(record.get("active")) and not str(record.get("routingEvidence", "")).strip()
        ]

    def active_and_assigned() -> list[str]:
        return [
            f"WS.ACTIVE_AND_ASSIGNED: active skill {record.get('label', 'unknown')} lacks onboarding or dispatcher evidence."
            for record in skills
            if bool(record.get("active")) and not str(record.get("notes", "")).strip()
        ]

    def teamwork_sharing() -> list[str]:
        return [
            f"WS.TEAMWORK_SHARING: {record.get('label', 'unknown')} has unsupported sharing semantics."
            for record in skills
            if record.get("sharing") != "maximal"
        ]

    def groups_and_capacity() -> list[str]:
        return [
            f"WS.GROUPS_AND_CAPACITY: group {group.get('label', 'unknown')} lacks a purpose or capacity rationale."
            for group in groups
            if not str(group.get("purpose", "")).strip()
        ]

    def advanced_validation() -> list[str]:
        return [
            f"WS.ADVANCED_VALIDATION: active skill {record.get('label', 'unknown')} lacks routing or optimization evidence."
            for record in skills
            if bool(record.get("active")) and not str(record.get("routingEvidence", "")).strip()
        ]

    validators = {
        "WS.QUALIFICATION_MODEL": qualification_model,
        "WS.CONDITION_SOURCE": condition_rules,
        "WS.CONDITION_LOGIC": condition_rules,
        "WS.REQUIRED_AND_PREFERRED_LEVELS": condition_rules,
        "WS.ROUTING_ELIGIBILITY": routing_eligibility,
        "WS.ACTIVE_AND_ASSIGNED": active_and_assigned,
        "WS.TEAMWORK_SHARING": teamwork_sharing,
        "WS.GROUPS_AND_CAPACITY": groups_and_capacity,
        "WS.ADVANCED_VALIDATION": advanced_validation,
    }
    if set(validators) != registered:
        raise WorkSkillsInputError("Work Skills executable validator coverage is incomplete.")
    failures = [failure for rule_id in DESIGN_RULE_IDS for failure in validators[rule_id]() if failure.startswith(rule_id)]
    if failures:
        raise WorkSkillsInputError("Work Skills design enforcement blocked preview: " + " ".join(failures))


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _active_english_is_available(languages: object) -> bool:
    return isinstance(languages, dict) and isinstance(languages.get("items"), list) and any(
        isinstance(item, dict)
        and isinstance(item.get("label"), str)
        and (item["label"].casefold() == "en" or item["label"].casefold().startswith("en-"))
        and item.get("active") in (True, "true", "TRUE")
        for item in languages["items"]
    )


class WorkSkillsAdapter:
    task_code = TASK_CODE

    def resolve_route(self, direction: str | None) -> dict[str, str]:
        return resolve_execution_route(ROOT.parent / "ora-resource" / "ora_rest_execution.md", TASK_CODE, direction)

    def preflight(self, workbook: Path, get: Any, temp: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
        payload = build_preview_data(workbook)
        enforce_design_rules(payload)
        languages = get(LANGUAGES_PATH, temp / "languages.json")
        if not _active_english_is_available(languages):
            raise WorkflowBlocked("Target environment does not expose an active English language.")
        listed = get(WORK_SKILLS_PATH, temp / "work-skills.json")
        if not isinstance(listed, dict):
            raise WorkflowBlocked("Work Skills list could not be read from OFSC Metadata.")
        if any(request.get("operationId") == "put-work-skill-group" for request in payload["requests"]):
            listed_groups = get(WORK_SKILL_GROUPS_PATH, temp / "work-skill-groups.json")
            if not isinstance(listed_groups, dict):
                raise WorkflowBlocked("Work Skill Groups list could not be read from OFSC Metadata.")
        baselines = {}
        for sequence, request in enumerate(payload["requests"], 1):
            label = request["label"]
            baseline = get(request["path"], temp / f"baseline-{sequence}.json")
            if request.get("operationId", "put-work-skill") == "put-work-skill":
                baselines[label] = baseline
            else:
                baselines[request["path"]] = baseline
        for sequence, request in enumerate(payload["requests"], 1):
            if request.get("operationId") != "put-work-skill-group":
                continue
            for member_sequence, member in enumerate(request["memberLabels"], 1):
                if member in payload["skillLabels"]:
                    continue
                existing = get(f"{WORK_SKILLS_PATH}{quote(member, safe='')}", temp / f"member-baseline-{sequence}-{member_sequence}.json")
                if existing is None:
                    raise WorkflowBlocked(
                        f"Work Skill Group {request['label']} references Work Skill {member}, which is absent from the workbook and target environment."
                    )
        return payload, baselines

    def build_preview(self, payload: dict[str, Any], environment: str, baselines: dict[str, dict[str, Any]]) -> dict[str, Any]:
        if not environment.strip():
            raise WorkSkillsInputError("environment is required.")
        requests = []
        for request in payload.get("requests", []):
            label = request.get("label")
            baseline = baselines.get(request.get("path"), baselines.get(label))
            if request.get("method") != "PUT" or not isinstance(label, str) or baseline is not None and not isinstance(baseline, dict):
                raise WorkSkillsInputError("A valid PUT request and an object-or-absent baseline are required for every Work Skill.")
            requests.append({"operationId": request["operationId"], "method": "PUT", "path": request["path"], "body": request["body"], "baseline": baseline, "label": label})
        draft = {"schemaVersion": "1.0", "taskCode": TASK_CODE, "executionDirection": LIVE_DIRECTION, "environment": environment.strip(), "requests": requests}
        return {**draft, "sha256": hashlib.sha256(_canonical_json(draft)).hexdigest(), "approvalRequired": True, "retryPolicy": "never"}

    def mismatches(self, expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
        if "workSkills" in expected:
            differences = [key for key in ("active", "assignToResource", "addToCapacityCategory") if actual.get(key) != expected.get(key)]
            if actual.get("workSkills") != expected.get("workSkills"):
                differences.append("workSkills")
        else:
            differences = [key for key in ("name", "active", "sharing") if actual.get(key) != expected.get(key)]
        # OFSC enriches each translation returned by GET with optional metadata
        # such as ``languageISO``.  Verify the fields this task owns while
        # preserving the ordered translation set; metadata enrichment is not a
        # configuration mismatch.
        expected_translations = expected.get("translations")
        actual_translations = actual.get("translations")
        if not isinstance(expected_translations, list) or not isinstance(actual_translations, list):
            differences.append("translations")
        else:
            expected_owned = [
                {key: item.get(key) for key in ("language", "name")}
                for item in expected_translations
                if isinstance(item, dict)
            ]
            actual_owned = [
                {key: item.get(key) for key in ("language", "name")}
                for item in actual_translations
                if isinstance(item, dict)
            ]
            if len(expected_owned) != len(expected_translations) or len(actual_owned) != len(actual_translations) or actual_owned != expected_owned:
                differences.append("translations")
        return differences
