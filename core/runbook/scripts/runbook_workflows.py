"""Write workflows used by the Run Book command-line entry point."""

import base64
import hashlib
from html import escape
import json
import mimetypes
from pathlib import Path
import re
from typing import Any, Callable, IO, Optional

from data_loader_handoff import stamp_run_id
from runbook_client import (
    ApiError,
    IndeterminateWriteError,
    RunbookClient,
    SuccessResponseError,
)
from runbook_service import (
    RunbookService,
    build_create_payload,
)
from runbook_values import MAX_INT64, positive_int64
from status_catalog import update_code
from markdown_renderer import dashboard_markdown, task_markdown


AD_HOC_TASK_INPUT_FIELDS = frozenset(
    {
        "name",
        "sequence",
        "required",
        "notes",
        "allow_comments",
        "allow_attachments",
        "performer_type",
    }
)
DEFAULT_AD_HOC_TASK = {
    "required": False,
    "allow_comments": True,
    "allow_attachments": True,
    "performer_type": "ORA_INITIATOR",
}
ATTACHMENT_INPUT_FIELDS = frozenset({"files"})
ATTACHMENT_FILE_FIELDS = frozenset(
    {"path", "approved_sha256", "title", "description", "content_type"}
)
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


class PartialCreationError(RuntimeError):
    """Creation succeeded or may have succeeded, but completion is unavailable."""

    def __init__(self, message: str, result: dict[str, Any]) -> None:
        super().__init__(message)
        self.result = result


class PartialMergeError(RuntimeError):
    """A merge succeeded or may have succeeded, but completion is unavailable."""

    def __init__(self, message: str, result: dict[str, Any]) -> None:
        super().__init__(message)
        self.result = result


class PartialTaskAddError(RuntimeError):
    """Task creation succeeded or may have succeeded, but retrieval is unavailable."""

    def __init__(self, message: str, result: dict[str, Any]) -> None:
        super().__init__(message)
        self.result = result


class PartialTaskUpdateError(RuntimeError):
    """Task update succeeded, but refreshed task details are unavailable."""

    def __init__(self, message: str, result: dict[str, Any]) -> None:
        super().__init__(message)
        self.result = result


class PartialTaskAttachmentError(RuntimeError):
    """One or more task attachments succeeded or may have succeeded."""

    def __init__(self, message: str, result: dict[str, Any]) -> None:
        super().__init__(message)
        self.result = result


class TaskAttachmentFailureError(RuntimeError):
    """No task attachment succeeded, and the failure outcome is known."""

    def __init__(self, message: str, result: dict[str, Any]) -> None:
        super().__init__(message)
        self.result = result


def _read_creation_input(stdin: IO[str]) -> tuple[Any, Any]:
    try:
        envelope = json.load(stdin)
    except json.JSONDecodeError as error:
        raise ValueError(f"Creation input is not valid JSON: {error.msg}.") from error
    if not isinstance(envelope, dict):
        raise ValueError("Creation input must be a JSON object.")
    if "plan" in envelope:
        return envelope.get("plan"), envelope.get("taskNotes")
    tasks = envelope.get("tasks")
    task_notes = [""] * len(tasks) if isinstance(tasks, list) else None
    return envelope, task_notes


def _read_merge_input(stdin: IO[str]) -> tuple[Any, Any]:
    """Read the original merge envelope without enabling raw-plan input."""

    try:
        envelope = json.load(stdin)
    except json.JSONDecodeError as error:
        raise ValueError(f"Creation input is not valid JSON: {error.msg}.") from error
    if not isinstance(envelope, dict):
        raise ValueError("Creation input must be a JSON object.")
    return envelope.get("plan"), envelope.get("taskNotes")


def _read_json_object(stdin: IO[str], description: str) -> dict[str, Any]:
    try:
        value = json.load(stdin)
    except json.JSONDecodeError as error:
        raise ValueError(f"{description} is not valid JSON: {error.msg}.") from error
    if not isinstance(value, dict):
        raise ValueError(f"{description} must be a JSON object.")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _markdown_text(value: str) -> str:
    return (
        escape(value, quote=False)
        .replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("*", "\\*")
        .replace("_", "\\_")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("\r", " ")
        .replace("\n", " ")
    )


def prepare_attachment_input(stdin: IO[str]) -> list[dict[str, Any]]:
    """Validate attachment input before authentication or side effects."""

    value = _read_json_object(stdin, "Task attachment input")
    unknown_fields = sorted(set(value) - ATTACHMENT_INPUT_FIELDS)
    if unknown_fields:
        raise ValueError(
            "Task attachment input contains unsupported fields: "
            f"{', '.join(unknown_fields)}."
        )
    files = value.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("Task attachment input requires a non-empty files array.")

    prepared: list[dict[str, Any]] = []
    for index, item in enumerate(files):
        label = f"Task attachment file {index}"
        if not isinstance(item, dict):
            raise ValueError(f"{label} must be a JSON object.")
        unknown_item_fields = sorted(set(item) - ATTACHMENT_FILE_FIELDS)
        if unknown_item_fields:
            raise ValueError(
                f"{label} contains unsupported fields: "
                f"{', '.join(unknown_item_fields)}."
            )

        raw_path = item.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ValueError(f"{label} requires a non-empty absolute path.")
        source_path = Path(raw_path)
        if not source_path.is_absolute():
            raise ValueError(f"{label} path must be absolute.")
        try:
            resolved_path = source_path.resolve(strict=True)
        except OSError as error:
            raise ValueError(f"{label} path does not exist or cannot be resolved.") from error
        if not resolved_path.is_file():
            raise ValueError(f"{label} path must identify a regular file.")
        file_name = source_path.name
        if not file_name or len(file_name) > 2048:
            raise ValueError(f"{label} filename must contain 1 through 2048 characters.")
        try:
            file_size = resolved_path.stat().st_size
        except OSError as error:
            raise ValueError(f"{label} could not be read.") from error
        if file_size < 1:
            raise ValueError(f"{label} must not be empty.")

        approved_sha256 = item.get("approved_sha256")
        if (
            not isinstance(approved_sha256, str)
            or SHA256_PATTERN.fullmatch(approved_sha256) is None
        ):
            raise ValueError(
                f"{label} approved_sha256 must be 64 lowercase hexadecimal characters."
            )
        try:
            actual_sha256 = _sha256(resolved_path)
        except OSError as error:
            raise ValueError(f"{label} could not be read.") from error
        if actual_sha256 != approved_sha256:
            raise ValueError(
                f"{label} no longer matches its approved SHA-256 digest."
            )

        title = item.get("title", file_name)
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"{label} title must be non-empty text when supplied.")
        description = item.get("description")
        if description is not None and (
            not isinstance(description, str) or len(description) > 255
        ):
            raise ValueError(
                f"{label} description must be text no longer than 255 characters."
            )
        content_type = item.get("content_type")
        if content_type is None:
            content_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
        elif not isinstance(content_type, str) or not content_type.strip():
            raise ValueError(
                f"{label} content_type must be non-empty text when supplied."
            )

        prepared.append(
            {
                "path": resolved_path,
                "fileName": file_name,
                "title": title,
                "description": description,
                "contentType": content_type,
                "sha256": approved_sha256,
            }
        )
    return prepared


def _attachment_result(
    *, task_name: str, file_results: list[dict[str, str]], attached: Any
) -> dict[str, Any]:
    confirmed = [item for item in file_results if item["status"] == "attached"]
    count = len(confirmed)
    count_text = f"{count} file{'s' if count != 1 else ''}"
    escaped_task_name = _markdown_text(task_name)
    if attached is True:
        summary = f"Attached {count_text} to **{escaped_task_name}**."
    elif attached == "unknown":
        summary = (
            f"Attachment outcome is unknown for **{escaped_task_name}**. "
            f"Confirmed {count_text} attached."
        )
    elif attached == "partial":
        summary = (
            f"Attachment upload did not finish for **{escaped_task_name}**. "
            f"Confirmed {count_text} attached."
        )
    else:
        summary = f"No files were attached to **{escaped_task_name}**."
    lines = [summary]
    if confirmed:
        lines.extend(
            ("", *(f"- {_markdown_text(item['fileName'])}" for item in confirmed))
        )
    return {
        "attached": attached,
        "taskName": task_name,
        "files": file_results,
        "markdown": "\n".join(lines),
    }


def attach_task_files(
    *,
    client: RunbookClient,
    prepared_files: list[dict[str, Any]],
    parent_worker_journey_id: str,
    worker_journey_task_id: str,
) -> dict[str, Any]:
    """Attach files sequentially and stop after the first failure."""

    try:
        detail = client.get_task(parent_worker_journey_id, worker_journey_task_id)
    except ApiError as error:
        raise ValueError(
            "The selected Run Book task and attachment permissions could not be verified."
        ) from error
    task_name = detail.get("Name")
    if not isinstance(task_name, str) or not task_name.strip():
        task_name = "Run Book task"

    file_results: list[dict[str, str]] = []
    for index, item in enumerate(prepared_files):
        public_item = {
            "fileName": item["fileName"],
            "sha256": item["sha256"],
            "status": "not-attempted",
        }
        try:
            try:
                contents = item["path"].read_bytes()
            except OSError as error:
                raise ValueError(
                    f"{item['fileName']} could not be read immediately before upload."
                ) from error
            if hashlib.sha256(contents).hexdigest() != item["sha256"]:
                raise ValueError(
                    f"{item['fileName']} changed after attachment approval."
                )
            payload = {
                "DatatypeCode": "FILE",
                "FileName": item["fileName"],
                "Title": item["title"],
                "UploadedFileContentType": item["contentType"],
                "FileContents": base64.b64encode(contents).decode("ascii"),
            }
            if item["description"] is not None:
                payload["Description"] = item["description"]
            client.add_task_attachment(
                parent_worker_journey_id,
                worker_journey_task_id,
                payload,
            )
            public_item["status"] = "attached"
            file_results.append(public_item)
        except IndeterminateWriteError as error:
            public_item["status"] = "unknown"
            file_results.append(public_item)
            file_results.extend(
                {
                    "fileName": remaining["fileName"],
                    "sha256": remaining["sha256"],
                    "status": "not-attempted",
                }
                for remaining in prepared_files[index + 1 :]
            )
            result = _attachment_result(
                task_name=task_name,
                file_results=file_results,
                attached="unknown",
            )
            result["error"] = str(error)
            raise PartialTaskAttachmentError(
                "Oracle Fusion may have received the task attachment POST; do not "
                "retry it automatically.",
                result,
            ) from error
        except SuccessResponseError as error:
            public_item["status"] = "attached-unverified"
            file_results.append(public_item)
            file_results.extend(
                {
                    "fileName": remaining["fileName"],
                    "sha256": remaining["sha256"],
                    "status": "not-attempted",
                }
                for remaining in prepared_files[index + 1 :]
            )
            result = _attachment_result(
                task_name=task_name,
                file_results=file_results,
                attached="partial",
            )
            result["error"] = str(error)
            raise PartialTaskAttachmentError(
                "Oracle Fusion accepted the task attachment POST but its response "
                "could not be verified; do not retry it automatically.",
                result,
            ) from error
        except ApiError as error:
            safe_error = ValueError(
                f"Oracle Fusion did not confirm attachment of {item['fileName']}."
            )
            had_confirmed_attachment = bool(file_results)
            public_item["status"] = "failed"
            file_results.append(public_item)
            file_results.extend(
                {
                    "fileName": remaining["fileName"],
                    "sha256": remaining["sha256"],
                    "status": "not-attempted",
                }
                for remaining in prepared_files[index + 1 :]
            )
            result = _attachment_result(
                task_name=task_name,
                file_results=file_results,
                attached="partial" if had_confirmed_attachment else False,
            )
            result["error"] = str(safe_error)
            if not had_confirmed_attachment:
                raise TaskAttachmentFailureError(
                    "The first task attachment failed; remaining files were not "
                    "attempted.",
                    result,
                ) from error
            raise PartialTaskAttachmentError(
                "A task attachment failed after an earlier file was attached; "
                "remaining files were not attempted.",
                result,
            ) from error
        except (OSError, ValueError) as error:
            had_confirmed_attachment = bool(file_results)
            public_item["status"] = "failed"
            file_results.append(public_item)
            file_results.extend(
                {
                    "fileName": remaining["fileName"],
                    "sha256": remaining["sha256"],
                    "status": "not-attempted",
                }
                for remaining in prepared_files[index + 1 :]
            )
            result = _attachment_result(
                task_name=task_name,
                file_results=file_results,
                attached="partial" if had_confirmed_attachment else False,
            )
            result["error"] = str(error)
            if not had_confirmed_attachment:
                raise TaskAttachmentFailureError(
                    "The first task attachment failed; remaining files were not "
                    "attempted.",
                    result,
                ) from error
            raise PartialTaskAttachmentError(
                "A task attachment failed after an earlier file was attached; "
                "remaining files were not attempted.",
                result,
            ) from error

    return _attachment_result(
        task_name=task_name,
        file_results=file_results,
        attached=True,
    )


def _normalize_ad_hoc_task(value: dict[str, Any]) -> dict[str, Any]:
    """Validate one ad hoc manual task and apply its defaults."""

    unknown_fields = sorted(set(value) - AD_HOC_TASK_INPUT_FIELDS)
    if unknown_fields:
        raise ValueError(
            "Ad hoc task input contains unsupported fields: "
            f"{', '.join(unknown_fields)}."
        )

    name = value.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Ad hoc task input requires a non-empty name.")

    normalized = {"name": name.strip(), **DEFAULT_AD_HOC_TASK}
    for field in ("required", "allow_comments", "allow_attachments"):
        if field in value:
            if not isinstance(value[field], bool):
                raise ValueError(f"Ad hoc task {field} must be a boolean.")
            normalized[field] = value[field]

    if "performer_type" in value:
        performer_type = value["performer_type"]
        if not isinstance(performer_type, str) or not performer_type.strip():
            raise ValueError("Ad hoc task performer_type must be non-empty text.")
        normalized["performer_type"] = performer_type.strip()
    if "notes" in value:
        notes = value["notes"]
        if not isinstance(notes, str):
            raise ValueError("Ad hoc task notes must be text.")
        normalized["notes"] = notes
    if "sequence" in value:
        if isinstance(value["sequence"], bool) or not isinstance(
            value["sequence"], int
        ):
            raise ValueError("Ad hoc task sequence must be a positive integer.")
        normalized["sequence"] = positive_int64(
            value["sequence"], "Ad hoc task sequence"
        )
    return normalized


def _next_task_sequence(tasks_payload: Any) -> str:
    if not isinstance(tasks_payload, dict):
        raise ValueError("Expected the existing task list to be a JSON object.")
    items = tasks_payload.get("items")
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        raise ValueError("Expected the existing task list to contain object items.")

    largest = 0
    for index, item in enumerate(items):
        sequence = positive_int64(item.get("Sequence"), f"Task {index} Sequence")
        largest = max(largest, sequence)
    if largest > MAX_INT64 - 10:
        raise ValueError("The next task Sequence exceeds the 64-bit integer limit.")
    return str(largest + 10)


def _build_add_task_payload(
    journey_id: Any,
    task_input: dict[str, Any],
    sequence: Any,
) -> dict[str, Any]:
    normalized_journey_id = str(positive_int64(journey_id, "WorkerJourneyId"))
    normalized_sequence = str(positive_int64(sequence, "Sequence"))
    task = {
        "Name": task_input["name"],
        "Type": "ORA_CHK_MANUAL",
        "PerformerType": task_input["performer_type"],
        "RequiredFlag": task_input["required"],
        "Sequence": normalized_sequence,
        "AllowCommentFlag": task_input["allow_comments"],
        "AllowAttachmentFlag": task_input["allow_attachments"],
    }
    if "notes" in task_input:
        task["Notes"] = task_input["notes"]
    return {"WorkerJourneyId": normalized_journey_id, "tasks": [task]}


def _added_task_id(response: Any) -> str:
    """Return the task identifier from a successful single-task add response."""

    if not isinstance(response, dict):
        raise ValueError("Expected the ad hoc task response to be a JSON object.")
    tasks = response.get("tasks")
    if not isinstance(tasks, dict):
        raise ValueError("Ad hoc task response is missing tasks.")
    items = tasks.get("items")
    if (
        not isinstance(items, list)
        or len(items) != 1
        or not isinstance(items[0], dict)
    ):
        raise ValueError("Ad hoc task response must contain exactly one task.")
    return str(
        positive_int64(items[0].get("WorkerJourneyTaskId"), "WorkerJourneyTaskId")
    )


UPDATE_INPUT_FIELDS = frozenset(
    {
        "taskName", "description", "notes", "status", "sequence",
        "taskPercentage", "comments", "reopen",
    }
)


def _text_operation(value: Any, field: str) -> dict[str, str]:
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{field} must be a non-empty object.")
    unknown = sorted(set(value) - {"replace", "append"})
    if unknown:
        raise ValueError(f"{field} contains unsupported fields: {', '.join(unknown)}.")
    result: dict[str, str] = {}
    for key in ("replace", "append"):
        if key in value:
            if not isinstance(value[key], str):
                raise ValueError(f"{field}.{key} must be text.")
            result[key] = value[key]
    if not result:
        raise ValueError(f"{field} must include replace or append.")
    return result


def normalize_update_input(value: dict[str, Any]) -> dict[str, Any]:
    unknown = sorted(set(value) - UPDATE_INPUT_FIELDS)
    if unknown:
        raise ValueError("Update input contains unsupported fields: " + ", ".join(unknown))
    normalized: dict[str, Any] = {}
    if "reopen" in value:
        if not isinstance(value["reopen"], bool):
            raise ValueError("reopen must be a boolean.")
        if value["reopen"]:
            normalized.update(
                {"Status": "INI", "TaskPercentageComplete": None}
            )
    for source, target in (("taskName", "Name"), ("description", "Description")):
        if source in value:
            if not isinstance(value[source], str):
                raise ValueError(f"{source} must be text.")
            normalized[target] = value[source]
    if "status" in value:
        if not isinstance(value["status"], str):
            raise ValueError("status must be text.")
        normalized["Status"] = update_code(value["status"])
    if "sequence" in value:
        normalized["Sequence"] = positive_int64(value["sequence"], "sequence")
    if "taskPercentage" in value:
        percentage = value["taskPercentage"]
        if isinstance(percentage, bool) or not isinstance(percentage, int) or not 0 <= percentage <= 100:
            raise ValueError("taskPercentage must be an integer from 0 through 100.")
        normalized["TaskPercentageComplete"] = percentage
    if "notes" in value:
        normalized["Notes"] = _text_operation(value["notes"], "notes")
    if "comments" in value:
        comment = value["comments"]
        if not isinstance(comment, str):
            raise ValueError("comments must be text; replace and append are not supported.")
        normalized["commentText"] = comment
    if not normalized:
        raise ValueError("Request at least one task update.")
    return normalized


def _compose_text(operation: dict[str, str], current: Any) -> str:
    base = operation.get("replace", current if isinstance(current, str) else "")
    addition = operation.get("append")
    if addition is None:
        return base
    return f"{base}\n{addition}" if base and addition else base or addition


def build_update_payload(
    update: dict[str, Any],
    current_task: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build the Run Book PATCH payload from normalized task updates."""
    payload: dict[str, Any] = {}
    for field, value in update.items():
        if field == "commentText":
            continue
        if field == "Notes" and isinstance(value, dict):
            if "append" in value and current_task is None and "replace" not in value:
                raise ValueError(f"{field} append requires current task details.")
            payload[field] = _compose_text(value, (current_task or {}).get(field))
        else:
            payload[field] = value
    return payload


def update_task(
    *, client: RunbookClient, service: RunbookService, update_input: dict[str, Any],
    parent_worker_journey_id: str, worker_journey_task_id: str, worker_journey_id: Optional[str] = None,
) -> dict[str, Any]:
    update = normalize_update_input(update_input)
    needs_current = any(
        isinstance(value, dict) and "append" in value and "replace" not in value
        for value in update.values()
    )
    current_task = client.get_task(parent_worker_journey_id, worker_journey_task_id) if needs_current else None
    payload = build_update_payload(update, current_task)
    comment_text = update.get("commentText")
    partial = {"updated": True}
    if payload:
        try:
            client.update_task(parent_worker_journey_id, worker_journey_task_id, payload)
        except IndeterminateWriteError as error:
            raise PartialTaskUpdateError("The Run Book service may have received the task PATCH; do not retry it automatically.", {"updated": "unknown", "error": str(error)}) from error
        except SuccessResponseError as error:
            raise PartialTaskUpdateError("The Run Book service accepted the task PATCH but returned an unusable response.", {**partial, "error": str(error)}) from error
    if comment_text is not None:
        try:
            client.add_task_comment(worker_journey_task_id, comment_text)
        except IndeterminateWriteError as error:
            raise PartialTaskUpdateError("The Run Book service may have received the task comment; do not retry it automatically.", {"updated": "unknown", "error": str(error)}) from error
        except SuccessResponseError as error:
            raise PartialTaskUpdateError("The Run Book service accepted the task comment but returned an unusable response.", {**partial, "error": str(error)}) from error
        except ApiError as error:
            if payload:
                raise PartialTaskUpdateError(
                    "The Run Book service updated the task, but could not create the comment.",
                    {**partial, "error": str(error)},
                ) from error
            raise
    try:
        task = service.get_task_model(parent_worker_journey_id, worker_journey_task_id, worker_journey_id=worker_journey_id)
    except (ApiError, OSError, ValueError) as error:
        raise PartialTaskUpdateError("The Run Book service updated the task, but its details could not be retrieved.", {**partial, "error": str(error)}) from error
    return {"updated": True, "name": task["name"], "status": task["status"], "type": task["type"], "markdown": "The task was updated successfully.\n\n" + task_markdown(task)}


def create_runbook(
    *,
    client: RunbookClient,
    service: RunbookService,
    stdin: IO[str],
    data_loader_config: Path,
    on_create_invoked: Optional[Callable[[], None]] = None,
) -> dict[str, Any]:
    plan, task_notes = _read_creation_input(stdin)
    creation = build_create_payload(plan, task_notes)
    partial_result: dict[str, Any] = {
        "created": True,
        "skippedTasks": creation["skippedTasks"],
    }
    try:
        if on_create_invoked is not None:
            on_create_invoked()
        response = client.create_runbook(creation["payload"])
    except IndeterminateWriteError as error:
        unknown_result = {
            **partial_result,
            "created": "unknown",
            "error": str(error),
        }
        raise PartialCreationError(
            "Oracle Fusion may have received the run-book POST; do not retry it "
            "automatically.",
            unknown_result,
        ) from error
    except SuccessResponseError as error:
        partial_result["error"] = str(error)
        raise PartialCreationError(
            "Oracle Fusion accepted the run-book POST but returned an unusable "
            "response.",
            partial_result,
        ) from error

    if not isinstance(response, dict):
        message = "Oracle Fusion created the run book but did not return a JSON object."
        partial_result["error"] = message
        raise PartialCreationError(message, partial_result)

    worker_journey_id = response.get("WorkerJourneyId")
    if (
        isinstance(worker_journey_id, bool)
        or not isinstance(worker_journey_id, (int, str))
        or not str(worker_journey_id).strip()
    ):
        message = (
            "Oracle Fusion created the run book but did not return WorkerJourneyId."
        )
        partial_result["error"] = message
        raise PartialCreationError(message, partial_result)

    journey_id = str(worker_journey_id).strip()
    partial_result["workerJourneyId"] = journey_id
    server_url = response.get("ServerUrl")
    if isinstance(server_url, str) and server_url.strip():
        partial_result["serverUrl"] = server_url.strip()
    try:
        stamp_run_id(data_loader_config, journey_id)
    except (OSError, ValueError) as error:
        partial_result["error"] = str(error)
        raise PartialCreationError(
            "Fusion Run Book service created the run book, but its ID could not be "
            "saved for Data Loader.",
            partial_result,
        ) from error

    try:
        dashboard = service.get_dashboard(journey_id)
    except (ApiError, OSError, ValueError) as error:
        partial_result["error"] = str(error)
        raise PartialCreationError(
            "Oracle Fusion created the run book, but its dashboard data could not "
            "be retrieved.",
            partial_result,
        ) from error

    dashboard_report = dashboard_markdown(
        dashboard["runbook"],
        dashboard["summary"],
    )
    warning_lines = [
        f"- Task {item.get('index', '?')}: {item.get('reason', 'Skipped')}"
        for item in creation["skippedTasks"]
    ]
    warnings = (
        "\n\n## Skipped tasks\n\n" + "\n".join(warning_lines)
        if warning_lines
        else ""
    )
    creation_markdown = (
        "The run book was created successfully.\n\n"
        + dashboard_report
        + warnings
    )

    result = {
        "created": True,
        "workerJourneyId": journey_id,
        "summary": dashboard["summary"],
        "counts": dashboard["counts"],
        "journeyTitle": dashboard["runbook"]["journeyTitle"],
        "taskIndex": dashboard["taskIndex"],
        "skippedTasks": creation["skippedTasks"],
        "markdown": creation_markdown,
    }
    if "serverUrl" in partial_result:
        result["serverUrl"] = partial_result["serverUrl"]
    return result


def merge_runbook(
    *,
    client: RunbookClient,
    service: RunbookService,
    stdin: IO[str],
    data_loader_config: Path,
    journey_id: str,
) -> dict[str, Any]:
    """Merge a validated implementation plan into an existing Run Book."""

    plan, task_notes = _read_merge_input(stdin)
    creation = build_create_payload(plan, task_notes)
    normalized_journey_id = str(positive_int64(journey_id, "WorkerJourneyId"))
    merge_payload = {"taskDetails": creation["payload"]["taskDetails"]}
    partial_result: dict[str, Any] = {
        "merged": True,
        "skippedTasks": creation["skippedTasks"],
    }
    try:
        client.merge_runbook(normalized_journey_id, merge_payload)
    except IndeterminateWriteError as error:
        raise PartialMergeError(
            "Oracle Fusion may have received the Run Book merge; do not retry it automatically.",
            {**partial_result, "merged": "unknown", "error": str(error)},
        ) from error
    except SuccessResponseError as error:
        raise PartialMergeError(
            "Oracle Fusion accepted the Run Book merge but returned an unusable response.",
            {**partial_result, "error": str(error)},
        ) from error

    try:
        dashboard = service.get_dashboard(normalized_journey_id)
    except (ApiError, OSError, ValueError) as error:
        raise PartialMergeError(
            "Oracle Fusion merged the Run Book tasks, but its dashboard data could not be retrieved.",
            {**partial_result, "error": str(error)},
        ) from error
    try:
        stamp_run_id(data_loader_config, normalized_journey_id)
    except (OSError, ValueError) as error:
        raise PartialMergeError(
            "Oracle Fusion merged the Run Book tasks, but the active Run Book could not be saved.",
            {**partial_result, "error": str(error)},
        ) from error

    warning_lines = [
        f"- Task {item.get('index', '?')}: {item.get('reason', 'Skipped')}"
        for item in creation["skippedTasks"]
    ]
    warnings = "\n\n## Skipped tasks\n\n" + "\n".join(warning_lines) if warning_lines else ""
    return {
        "merged": True,
        "workerJourneyId": normalized_journey_id,
        "summary": dashboard["summary"],
        "counts": dashboard["counts"],
        "journeyTitle": dashboard["runbook"]["journeyTitle"],
        "taskIndex": dashboard["taskIndex"],
        "skippedTasks": creation["skippedTasks"],
        "markdown": "The implementation plan was merged successfully.\n\n"
        + dashboard_markdown(dashboard["runbook"], dashboard["summary"])
        + warnings,
    }


def add_task(
    *,
    client: RunbookClient,
    service: RunbookService,
    stdin: IO[str],
    journey_id: str,
) -> dict[str, Any]:
    task_input = _normalize_ad_hoc_task(
        _read_json_object(stdin, "Ad hoc task input")
    )
    normalized_journey_id = str(positive_int64(journey_id, "WorkerJourneyId"))
    sequence = task_input.get("sequence")
    if sequence is None:
        current_tasks = client.list_tasks(normalized_journey_id)
        sequence = _next_task_sequence(current_tasks)
    payload = _build_add_task_payload(
        normalized_journey_id,
        task_input,
        sequence,
    )
    partial_result: dict[str, Any] = {
        "added": True,
        "name": task_input["name"],
    }
    try:
        add_response = client.add_task(payload)
    except IndeterminateWriteError as error:
        unknown_result = {
            **partial_result,
            "added": "unknown",
            "error": str(error),
        }
        raise PartialTaskAddError(
            "The Run Book service may have received the ad hoc task POST; do not "
            "retry it "
            "automatically.",
            unknown_result,
        ) from error
    except SuccessResponseError as error:
        partial_result["error"] = str(error)
        raise PartialTaskAddError(
            "The Run Book service accepted the ad hoc task POST but returned an unusable "
            "response.",
            partial_result,
        ) from error

    try:
        task_id = _added_task_id(add_response)
        task = service.get_task_model(
            normalized_journey_id,
            task_id,
            worker_journey_id=normalized_journey_id,
        )
    except (ApiError, OSError, ValueError) as error:
        partial_result["error"] = str(error)
        raise PartialTaskAddError(
            "The Run Book service added the ad hoc task, but its details could not be "
            "retrieved.",
            partial_result,
        ) from error

    task_report = task_markdown(task)
    add_markdown = (
        "The ad hoc task was added successfully.\n\n" + task_report
    )
    return {
        "added": True,
        "name": task["name"],
        "status": task["status"],
        "type": task["type"],
        "markdown": add_markdown,
    }
