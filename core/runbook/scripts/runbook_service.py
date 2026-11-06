#!/usr/bin/env python3
"""Deterministic run-book models built from Oracle Fusion responses."""

from collections import Counter
import json
from typing import Any, Dict, Iterable, List, Optional, Sequence
from urllib.parse import urljoin

from runbook_client import ApiError, RunbookClient
from runbook_values import positive_int64
from status_catalog import (
    STATUS_DEFINITIONS,
    display_status,
    is_complete,
    normalize_status,
    safe_unknown_label,
)


VIDEO_SUBTYPES = {
    "ORA_CHK_VIDEO_EMBEDDED",
    "ORA_CHK_VIDEO_MEDIA",
}
CREATE_DATA_LOADER_TASK_TYPE = "ORA_CHK_DATA_LOADER"


class CreatePayloadValidationError(ValueError):
    """No create payload can be posted; task-level warnings remain available."""

    def __init__(self, message: str, skipped_tasks: List[Dict[str, Any]]) -> None:
        super().__init__(message)
        self.skipped_tasks = skipped_tasks


def _verb(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural


def task_items(payload: Any) -> List[Dict[str, Any]]:
    """Validate and return task objects from an allStepTasks response."""

    items = payload.get("items") if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        raise ValueError("Expected an allStepTasks response with an items array.")
    if not all(isinstance(item, dict) for item in items):
        raise ValueError("Expected every allStepTasks item to be a JSON object.")
    return items


def _planning_text(payload: Dict[str, Any], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Planning payload is missing {field}.")
    return value


def _task_group_name(item: Dict[str, Any]) -> Optional[str]:
    offering = item.get("offering")
    functional_area = item.get("functional_area")
    if not (
        isinstance(offering, str)
        and offering.strip()
        and isinstance(functional_area, str)
        and functional_area.strip()
    ):
        return None
    return f"{offering.strip()} - {functional_area.strip()}"


def _skipped_task(index: int, item: Any, reasons: List[str]) -> Dict[str, Any]:
    name = item.get("name") if isinstance(item, dict) else None
    return {
        "index": index,
        "name": name if isinstance(name, str) and name.strip() else None,
        "reason": "; ".join(reasons),
    }


def build_create_payload(
    planning_payload: Any,
    task_notes: Any,
) -> Dict[str, Any]:
    """Build the allowlisted assigned-run-book POST body and skip invalid tasks."""

    if not isinstance(planning_payload, dict):
        raise ValueError("Expected plan to be a JSON object.")
    project_id = planning_payload.get("project_id")
    if project_id is not None and not (
        isinstance(project_id, str) and not project_id.strip()
    ):
        runbook_name = project_id.strip() if isinstance(project_id, str) else project_id
    else:
        offering = planning_payload.get("offering")
        functional_area = planning_payload.get("functional_area")
        if (
            isinstance(offering, str)
            and offering.strip()
            and isinstance(functional_area, str)
            and functional_area.strip()
        ):
            runbook_name = f"{offering.strip()} - {functional_area.strip()}"
        else:
            runbook_name = "Implementation Run Book"
    tasks = planning_payload.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("Planning payload must include a non-empty tasks array.")
    if not isinstance(task_notes, list) or len(task_notes) != len(tasks):
        raise ValueError(
            "taskNotes must contain exactly one entry for every source task."
        )
    valid_tasks: List[tuple[int, int, Dict[str, Any], Optional[str]]] = []
    skipped_tasks: List[Dict[str, Any]] = []
    for index, (item, notes_text) in enumerate(zip(tasks, task_notes)):
        reasons: List[str] = []
        if not isinstance(item, dict):
            reasons.append("task must be an object")
            name = None
            sequence = None
        else:
            name = item.get("name")
            sequence = item.get("sequence")
            task_action_code = item.get("task_id")
            task_type = item.get("taskType", CREATE_DATA_LOADER_TASK_TYPE)
            business_objects = item.get("business_objects", [])
            if not isinstance(name, str) or not name.strip():
                reasons.append("name must be non-empty text")
            if (
                isinstance(sequence, bool)
                or not isinstance(sequence, int)
                or sequence < 1
            ):
                reasons.append("sequence must be a positive integer")
            if (
                not isinstance(task_action_code, str)
                or not task_action_code.strip()
            ):
                reasons.append("task_id must be non-empty text")
            if task_type is not None and (
                not isinstance(task_type, str) or not task_type.strip()
            ):
                reasons.append("taskType must be non-empty text or null")
            if not isinstance(business_objects, list) or any(
                not isinstance(value, str) or not value.strip()
                for value in business_objects
            ):
                reasons.append("business_objects must be an array of non-empty strings")
        if not isinstance(notes_text, str):
            reasons.append("taskNotes entry must be text")

        if reasons:
            skipped_tasks.append(_skipped_task(index, item, reasons))
            continue

        task = {
            "name": name,
            "actionCode": task_action_code,
            "notes": notes_text,
            "taskType": task_type.strip() if isinstance(task_type, str) else None,
            "businessObjects": list(dict.fromkeys(value.strip() for value in business_objects)),
            "dependencyIds": (
                item["depends_on"]
                if isinstance(item.get("depends_on"), list)
                and all(
                    isinstance(dependency_id, str) and dependency_id.strip()
                    for dependency_id in item["depends_on"]
                )
                else []
            ),
        }
        group_name = _task_group_name(item)
        valid_tasks.append(
            (
                index,
                sequence,
                task,
                group_name,
            )
        )

    if not valid_tasks:
        raise CreatePayloadValidationError(
            "No valid tasks remain after validation.",
            skipped_tasks,
        )
    resolved_tasks = valid_tasks
    while resolved_tasks:
        task_names_by_action_code: Dict[str, List[str]] = {}
        for _, _, task, _ in resolved_tasks:
            task_names_by_action_code.setdefault(task["actionCode"], []).append(
                task["name"]
            )

        next_resolved_tasks: List[tuple[int, int, Dict[str, Any], Optional[str]]] = []
        for index, sequence, task, group_name in resolved_tasks:
            dependency_ids = task["dependencyIds"]
            unknown_dependency_ids = [
                dependency_id
                for dependency_id in dependency_ids
                if dependency_id not in task_names_by_action_code
            ]
            if unknown_dependency_ids:
                skipped_tasks.append(
                    _skipped_task(
                        index,
                        tasks[index],
                        [
                            "depends_on references unknown task_id: "
                            + ", ".join(unknown_dependency_ids)
                        ],
                    )
                )
                continue
            next_resolved_tasks.append((index, sequence, task, group_name))
        if len(next_resolved_tasks) == len(resolved_tasks):
            resolved_tasks = next_resolved_tasks
            break
        resolved_tasks = next_resolved_tasks

    if not resolved_tasks:
        raise CreatePayloadValidationError(
            "No valid tasks remain after validation.",
            skipped_tasks,
        )
    task_names_by_action_code = {}
    for _, _, task, _ in resolved_tasks:
        task_names_by_action_code.setdefault(task["actionCode"], []).append(
            task["name"]
        )
    for _, _, task, _ in resolved_tasks:
        task["dependentOn"] = (
            "|".join(
                task_name
                for dependency_id in task["dependencyIds"]
                for task_name in task_names_by_action_code[dependency_id]
            )
            or None
        )
    resolved_tasks.sort(key=lambda entry: (entry[1], entry[0]))
    group_sequences: Dict[str, int] = {}
    task_details: List[Dict[str, Any]] = []
    for task_index, entry in enumerate(resolved_tasks, start=1):
        task = entry[2]
        group_name = entry[3]
        task_detail = {
            "taskName": task["name"],
            "taskType": task["taskType"],
            "taskActionCode": task["actionCode"],
            "description": task["notes"],
            "sequence": task_index * 100,
            "notes": task["notes"],
            "required": "N",
            "allowComments": "Y",
            "AllowMultipleCommentsFlag": "Y",
            "allowAttachments": "Y",
            "dependentOn": task["dependentOn"],
            "embeddedApplicationTaskCode": ",".join(task["businessObjects"]),
        }
        if group_name is not None:
            if group_name not in group_sequences:
                group_sequences[group_name] = (len(group_sequences) + 1) * 10
            task_detail["groupName"] = group_name
            task_detail["groupSequence"] = group_sequences[group_name]
        task_details.append(task_detail)

    return {
        "payload": {
            "journeyDetails": {
                "name": runbook_name,
                "completionCriteria": "ORA_CHK_ALLTASKS_COMPLETE",
                "archiveOffset": 12,
                "purgeOffset": 12,
            },
            "taskDetails": task_details,
        },
        "skippedTasks": skipped_tasks,
    }


def status_counts(items: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Count task statuses using the agreed Oracle Fusion mappings."""

    task_list = list(items)
    statuses = Counter(normalize_status(item.get("Status")) for item in task_list)
    unknown = {
        safe_unknown_label(status): count
        for status, count in sorted(statuses.items())
        if status not in STATUS_DEFINITIONS
    }
    result = {
        "total": len(task_list),
        "inProgress": statuses["INP"],
        "readyForReview": statuses["RFR"],
        "open": statuses["INI"],
        "dependent": statuses["DEP"],
        "completed": statuses["COM"] + statuses["CWE"] + statuses["REJ"],
        "unknown": unknown,
    }
    if statuses["TOH"]:
        result["error"] = statuses["TOH"]
    if statuses["CWE"]:
        result["completedWithExceptions"] = statuses["CWE"]
    return result


def summary_sentence(counts: Dict[str, Any]) -> str:
    """Format the agreed concise user-facing task summary."""

    total = counts["total"]
    status_clauses = [
        f"{counts['open']} {_verb(counts['open'], 'has', 'have')} not started",
        f"{counts['inProgress']} {_verb(counts['inProgress'], 'is', 'are')} in progress",
        f"{counts['completed']} {_verb(counts['completed'], 'is', 'are')} completed",
    ]
    prefix = f"There {_verb(total, 'is', 'are')} {total} task{'' if total == 1 else 's'} in total"
    sentence = f"{prefix}: {', '.join(status_clauses[:-1])}, and {status_clauses[-1]}."
    unknown = counts.get("unknown") or {}
    if unknown:
        details = ", ".join(f"{status}={count}" for status, count in unknown.items())
        sentence += f" Other statuses: {details}."
    return sentence


def summarize_payload(payload: Any) -> Dict[str, Any]:
    """Return both structured counts and the concise summary sentence."""

    counts = status_counts(task_items(payload))
    result = {"counts": counts, "summary": summary_sentence(counts)}
    if isinstance(payload, dict) and "hasMore" in payload:
        result["pagination"] = {k: v for k, v in payload.items() if k != "items"}
    return result


def _required(value: Any) -> bool:
    return value is True or str(value or "").strip().upper() == "Y"


def _required_text(item: Dict[str, Any], field: str) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Task response is missing {field}.")
    return value


def _optional_stage_name(item: Dict[str, Any]) -> Optional[str]:
    value = item.get("StageName")
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Task StageName must be text or null.")
    return value if value.strip() else None


def _stage_sequence(item: Dict[str, Any]) -> Optional[int]:
    """Return a usable stage sequence, if Fusion supplied one."""

    try:
        return positive_int64(item.get("StageSequence"), "StageSequence")
    except ValueError:
        return None


def _subsequence_order(entry: tuple[int, Dict[str, Any]]) -> tuple[Any, ...]:
    """Order tasks within one stage by SubSequence, preserving response ties."""

    original_index, item = entry
    subsequence = item.get("SubSequence")
    return (
        subsequence is not None,
        0 if subsequence is None else subsequence,
        original_index,
    )


def _identifier(item: Dict[str, Any], field: str) -> str:
    value = item.get(field)
    if value is None or str(value).strip() == "":
        raise ValueError(f"Task response is missing {field}.")
    return str(value)


def _selected_indexes(
    items: Sequence[Dict[str, Any]],
    include_indexes: Optional[Sequence[int]],
) -> Optional[set[int]]:
    if include_indexes is None:
        return None
    if not all(
        isinstance(index, int) and not isinstance(index, bool)
        for index in include_indexes
    ):
        raise ValueError("Every requested task index must be an integer.")
    selected = set(include_indexes)
    if any(index < 0 or index >= len(items) for index in selected):
        raise ValueError("A requested task index is outside the task list.")
    return selected


def build_dashboard_result(
    journey: Optional[Dict[str, Any]],
    tasks_payload: Any,
    *,
    include_indexes: Optional[Sequence[int]] = None,
) -> Dict[str, Any]:
    """Build a field-allowlisted dashboard and an internal task index."""

    all_items = task_items(tasks_payload)
    selected_indexes = _selected_indexes(all_items, include_indexes)
    selected_entries = [
        (index, item)
        for index, item in enumerate(all_items)
        if selected_indexes is None or index in selected_indexes
    ]
    stage_groups: Dict[str, Dict[str, Any]] = {}
    unstaged_entries: List[tuple[int, Dict[str, Any]]] = []
    task_index: List[Dict[str, Any]] = []

    for original_index, item in selected_entries:
        name = _required_text(item, "Name")
        stage_name = _optional_stage_name(item)
        if stage_name is None:
            unstaged_entries.append((original_index, item))
            continue
        if stage_name not in stage_groups:
            stage_groups[stage_name] = {
                "name": stage_name,
                "stageSequence": _stage_sequence(item),
                "firstIndex": original_index,
                "entries": [],
            }
        stage_groups[stage_name]["entries"].append((original_index, item))

    stages: List[Dict[str, Any]] = []
    ordered_stage_groups = sorted(
        stage_groups.values(),
        key=lambda group: (
            group["stageSequence"] is None,
            0 if group["stageSequence"] is None else group["stageSequence"],
            group["firstIndex"],
        ),
    )
    display_groups = [
        (group["name"], sorted(group["entries"], key=_subsequence_order))
        for group in ordered_stage_groups
    ]
    if unstaged_entries:
        display_groups.append((None, sorted(unstaged_entries, key=_subsequence_order)))

    for stage_name, entries in display_groups:
        stage = {"name": stage_name, "tasks": []}
        for original_index, item in entries:
            name = _required_text(item, "Name")
            stage["tasks"].append(
                {
                    "sequence": item.get("Sequence"),
                    "name": name,
                    "required": _required(item.get("RequiredFlag")),
                    "status": display_status(item.get("Status")),
                    "complete": is_complete(item.get("Status")),
                    "percentage": item.get("TaskPercentageComplete"),
                }
            )
            task_index.append(
                {
                    "index": original_index,
                    "name": name,
                    "parentWorkerJourneyId": _identifier(item, "ParentWorkerJourneyId"),
                    "workerJourneyTaskId": _identifier(item, "WorkerJourneyTaskId"),
                    "type": str(item.get("Type") or ""),
                }
            )
        stages.append(stage)

    counts = status_counts(item for _, item in selected_entries)
    journey_title = ""
    if journey and isinstance(journey.get("JourneyTitle"), str):
        journey_title = journey["JourneyTitle"]

    return {
        "summary": summary_sentence(counts),
        "counts": counts,
        "runbook": {
            "journeyTitle": journey_title,
            "completedCount": counts["completed"],
            "totalCount": counts["total"],
            "stages": stages,
        },
        "taskIndex": task_index,
    }


def notes_html(value: Any) -> str:
    """Return the remote Notes string unchanged for safe browser rendering."""

    if value in (None, ""):
        return ""
    if not isinstance(value, str):
        raise ValueError("Task Notes must be text.")
    return value


def _optional_text(value: Any, field: str) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"Task {field} must be text when present.")
    if not value.strip():
        return None
    return value


def build_task_comments(payload: Any) -> List[Dict[str, str]]:
    """Allowlist Object Notes comments for task-detail rendering."""

    if not isinstance(payload, dict):
        raise ValueError("Expected a task comments response object.")
    items = payload.get("items")
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        raise ValueError("Expected task comments to contain object items.")

    comments: List[Dict[str, str]] = []
    for index, item in enumerate(items):
        note_text = item.get("NoteText")
        last_updated = item.get("LastUpdateDate")
        if not isinstance(note_text, str):
            raise ValueError(f"Task comment {index} NoteText must be text.")
        if not isinstance(last_updated, str) or not last_updated.strip():
            raise ValueError(
                f"Task comment {index} LastUpdateDate must be non-empty text."
            )
        author = next(
            (
                value.strip()
                for value in (
                    item.get("AuthorName"),
                    item.get("AuthorKnownAs"),
                    item.get("CreatedBy"),
                )
                if isinstance(value, str) and value.strip()
            ),
            "Unknown author",
        )
        comments.append(
            {
                "lastUpdated": last_updated,
                "author": author,
                "textHtml": note_text,
            }
        )
    return comments


def _nonnegative_count(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"Run Book {field} must be a nonnegative integer.")
    return value


def build_runbook_list_result(
    payload: Any,
    *,
    offset: int,
    page_size: int,
) -> Dict[str, Any]:
    """Build an allowlisted, chat-sized Run Book search result."""

    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a nonnegative integer.")
    if isinstance(page_size, bool) or not isinstance(page_size, int) or page_size < 1:
        raise ValueError("page_size must be a positive integer.")
    if not isinstance(payload, dict):
        raise ValueError("Expected a workerJourneySearches response object.")
    items = payload.get("items")
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        raise ValueError("Expected workerJourneySearches to contain object items.")
    has_more = payload.get("hasMore")
    if not isinstance(has_more, bool):
        raise ValueError("Expected workerJourneySearches hasMore to be a boolean.")
    if has_more and not items:
        raise ValueError(
            "Oracle Fusion reported more Run Books but returned no items."
        )

    visible_items = items[:page_size]
    runbooks: List[Dict[str, Any]] = []
    runbook_index: List[Dict[str, Any]] = []
    for item_index, item in enumerate(visible_items):
        name = _required_text(item, "JourneyDisplayName")
        worker_journey_id = str(
            positive_int64(item.get("WorkerJourneyId"), "WorkerJourneyId")
        )
        task_counts = item.get("taskCounts")
        if not isinstance(task_counts, dict):
            raise ValueError("Run Book response is missing taskCounts.")
        total_tasks = _nonnegative_count(task_counts.get("Tasks"), "Tasks")
        completed_tasks = _nonnegative_count(
            task_counts.get("CompletedTasks"), "CompletedTasks"
        )
        if completed_tasks > total_tasks:
            raise ValueError("Run Book CompletedTasks cannot exceed Tasks.")
        runbooks.append(
            {
                "name": name,
                "completedTasks": completed_tasks,
                "totalTasks": total_tasks,
                "status": _optional_text(
                    item.get("StatusCategoryMeaning"), "StatusCategoryMeaning"
                ),
                "assignedDate": _optional_text(
                    item.get("AssignedDate"), "AssignedDate"
                ),
                "category": _optional_text(
                    item.get("CategoryMeaning"), "CategoryMeaning"
                ),
            }
        )
        runbook_index.append(
            {
                "index": offset + item_index,
                "name": name,
                "workerJourneyId": worker_journey_id,
            }
        )

    more_available = has_more or len(items) > page_size
    next_offset = offset + len(visible_items) if more_available else None
    return {
        "runbooks": runbooks,
        "runbookIndex": runbook_index,
        "offset": offset,
        "count": len(runbooks),
        "hasMore": more_available,
        "nextOffset": next_offset,
    }


def _optional_task_percentage(value: Any) -> Optional[int]:
    if value is None:
        return None
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
        or value > 100
    ):
        raise ValueError(
            "Task TaskPercentageComplete must be an integer from 0 through 100."
        )
    return value


_DATA_LOAD_STATUS_TEXT_FIELDS = (
    ("DataSetName", "dataSetName"),
    ("BusinessObjectName", "businessObjectName"),
    ("DataSetStatus", "dataSetStatus"),
)
_DATA_LOAD_STATUS_COUNT_FIELDS = (
    ("LoadedCount", "loadedCount"),
    ("ErrorCount", "errorCount"),
    ("SkippedCount", "skippedCount"),
)

_ATTACHMENT_TEXT_FIELDS = (
    ("DatatypeCode", "type"),
    ("FileName", "fileName"),
    ("Title", "title"),
    ("DocumentPreviewURL", "previewUrl"),
    ("FileUrl", "fileUrl"),
    ("Url", "url"),
)


def _absolute_url(value: str, server_url: Optional[str]) -> str:
    if not server_url:
        return value
    return urljoin(f"{server_url.rstrip('/')}/", value)


def build_task_attachments(
    payload: Any,
    *,
    server_url: Optional[str] = None,
    base_url: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Allowlist task attachments for user-facing detail rendering."""

    if not isinstance(payload, dict):
        raise ValueError("Expected an attachments response object.")
    items = payload.get("items")
    if not isinstance(items, list):
        raise ValueError("Expected attachments to contain object items.")

    attachments: List[Dict[str, str]] = []
    resolved_server_url = server_url or base_url
    for item in items:
        if not isinstance(item, dict):
            continue
        attachment: Dict[str, str] = {}
        for source, target in _ATTACHMENT_TEXT_FIELDS:
            value = item.get(source)
            if isinstance(value, str) and value.strip():
                if target in {"previewUrl", "fileUrl", "url"}:
                    value = _absolute_url(value, resolved_server_url)
                attachment[target] = value
        attachments.append(attachment)
    return attachments


def build_data_load_status_rows(payload: Any) -> List[Dict[str, Any]]:
    """Decode and allowlist the generateRunbookSummary action result."""

    if not isinstance(payload, dict):
        raise ValueError("Expected a Data Load Status response object.")
    raw_result = payload.get("result")
    if raw_result is None:
        return []
    if not isinstance(raw_result, str):
        raise ValueError("Data Load Status result must be JSON text when present.")
    if not raw_result.strip():
        return []
    try:
        decoded = json.loads(raw_result)
    except json.JSONDecodeError as error:
        raise ValueError("Data Load Status result is not valid JSON.") from error
    if decoded is None:
        return []
    if not isinstance(decoded, list):
        raise ValueError("Data Load Status result must decode to an array.")

    rows: List[Dict[str, Any]] = []
    for index, item in enumerate(decoded):
        if not isinstance(item, dict):
            raise ValueError(
                f"Data Load Status row {index} must be a JSON object."
            )
        row: Dict[str, Any] = {}
        for source, target in _DATA_LOAD_STATUS_TEXT_FIELDS:
            value = item.get(source)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Data Load Status row {index} field {source} must be non-empty text."
                )
            row[target] = value
        for source, target in _DATA_LOAD_STATUS_COUNT_FIELDS:
            value = item.get(source)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"Data Load Status row {index} field {source} must be a nonnegative integer."
                )
            row[target] = value
        rows.append(row)
    return rows


def build_task_model(
    detail: Dict[str, Any],
    documents_payload: Optional[Dict[str, Any]] = None,
    data_load_status_rows: Optional[List[Dict[str, Any]]] = None,
    task_comments: Optional[List[Dict[str, str]]] = None,
    attachments: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Build the compact task-detail model without exposing task IDs."""

    if not isinstance(detail, dict):
        raise ValueError("Expected a task-detail JSON object.")
    name = _required_text(detail, "Name")
    task_type = str(detail.get("Type") or "")
    task_subtype = (
        _optional_text(detail.get("SubType"), "SubType")
        if task_type == "ORA_CHK_VIDEO"
        else None
    )
    external_url = None
    external_label = None
    video_url = None
    documents: List[Dict[str, str]] = []

    if task_type == "ORA_CHK_EXTERNAL_URL":
        external_url = _optional_text(detail.get("ActionURL"), "ActionURL")
        external_label = _optional_text(
            detail.get("ActivityAction1Label"), "ActivityAction1Label"
        )
    elif task_type == "ORA_CHK_DOC" and documents_payload is not None:
        raw_documents = documents_payload.get("items")
        if not isinstance(raw_documents, list) or not all(
            isinstance(item, dict) for item in raw_documents
        ):
            raise ValueError("Expected a documents response with object items.")
        for item in raw_documents:
            preview_url = _optional_text(
                item.get("DocumentPreviewURL"), "DocumentPreviewURL"
            )
            file_name = _optional_text(item.get("FileName"), "FileName")
            if not preview_url or not file_name:
                raise ValueError(
                    "Every document must include DocumentPreviewURL and FileName."
                )
            documents.append({"previewUrl": preview_url, "fileName": file_name})
    elif task_type == "ORA_CHK_VIDEO" and task_subtype in VIDEO_SUBTYPES:
        video_url = _optional_text(detail.get("ActionURL"), "ActionURL")

    return {
        "name": name,
        "sequence": detail.get("Sequence"),
        "status": display_status(detail.get("Status")),
        "percentage": _optional_task_percentage(
            detail.get("TaskPercentageComplete")
        ),
        "complete": is_complete(detail.get("Status")),
        "required": _required(detail.get("RequiredFlag")),
        "comments": list(task_comments or []),
        "attachments": list(attachments or []),
        "notesHtml": notes_html(detail.get("Notes")),
        "type": task_type,
        "subType": task_subtype,
        "videoUrl": video_url,
        "externalUrl": external_url,
        "externalLabel": external_label,
        "documents": documents,
        "dataLoadStatusRows": (
            list(data_load_status_rows or [])
            if task_type == CREATE_DATA_LOADER_TASK_TYPE
            else None
        ),
    }


class RunbookService:
    """Coordinate Oracle Fusion calls and deterministic run-book transformations."""

    def __init__(self, client: RunbookClient) -> None:
        self.client = client

    def get_dashboard(
        self,
        journey_id: str,
        *,
        include_indexes: Optional[Sequence[int]] = None,
        offset: int = 0,
    ) -> Dict[str, Any]:
        tasks_payload = self.client.list_tasks(journey_id, **({"offset": offset} if offset else {}))
        try:
            journey = self.client.get_journey(journey_id)
        except Exception:
            journey = None
        result = build_dashboard_result(
            journey,
            tasks_payload,
            include_indexes=include_indexes,
        )
        if "hasMore" in tasks_payload:
            result["pagination"] = {k: v for k, v in tasks_payload.items() if k != "items"}
        return result

    def get_summary(
        self,
        journey_id: str,
        *,
        offset: int = 0,
    ) -> Dict[str, Any]:
        return summarize_payload(self.client.list_tasks(journey_id, **({"offset": offset} if offset else {})))

    def get_task_model(
        self,
        parent_worker_journey_id: str,
        worker_journey_task_id: str,
        *,
        worker_journey_id: Optional[str] = None,
        attachments_offset: int = 0,
        comments_offset: int = 0,
        documents_offset: int = 0,
    ) -> Dict[str, Any]:
        """Retrieve one allowlisted task-detail model."""

        detail = self.client.get_task(
            parent_worker_journey_id,
            worker_journey_task_id,
        )
        pagination = {}
        attachments: List[Dict[str, str]] = []
        try:
            attachment_payload = self.client.get_attachments(
                parent_worker_journey_id, worker_journey_task_id,
                **({"offset": attachments_offset} if attachments_offset else {}))
            if "hasMore" in attachment_payload:
                pagination["attachments"] = {k: v for k, v in attachment_payload.items() if k != "items"}
            attachments = build_task_attachments(
                attachment_payload,
                server_url=getattr(
                    self.client,
                    "server_url",
                    getattr(self.client, "base_url", None),
                ),
            )
        except (ApiError, OSError, ValueError):
            attachments = []
        documents = None
        if detail.get("Type") == "ORA_CHK_DOC":
            documents = self.client.get_documents(
                parent_worker_journey_id,
                worker_journey_task_id,
                **({"offset": documents_offset} if documents_offset else {}),
            )
        data_load_status_rows = None
        if detail.get("Type") == CREATE_DATA_LOADER_TASK_TYPE:
            data_load_status_rows = []
            application_task_name = detail.get("ApplicationTaskName")
            if application_task_name not in (None, ""):
                if worker_journey_id is None or not str(worker_journey_id).strip():
                    data_load_status_rows = []
                else:
                    try:
                        data_load_status_rows = build_data_load_status_rows(
                            self.client.get_runbook_summary(
                                worker_journey_id,
                                application_task_name,
                            )
                        )
                    except (ApiError, OSError, ValueError):
                        data_load_status_rows = []
        task_comments: List[Dict[str, str]] = []
        try:
            comment_payload = self.client.get_task_comments(worker_journey_task_id, **({"offset": comments_offset} if comments_offset else {}))
            if "hasMore" in comment_payload:
                pagination["comments"] = {k: v for k, v in comment_payload.items() if k != "items"}
            task_comments = build_task_comments(comment_payload)
        except (ApiError, OSError, ValueError):
            task_comments = []
        if isinstance(documents, dict) and "hasMore" in documents:
            pagination["documents"] = {k: v for k, v in documents.items() if k != "items"}
        result = build_task_model(
            detail,
            documents_payload=documents,
            data_load_status_rows=data_load_status_rows,
            task_comments=task_comments,
            attachments=attachments,
        )
        if pagination:
            result["pagination"] = pagination
        return result
