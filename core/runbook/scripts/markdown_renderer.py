#!/usr/bin/env python3
"""Render allowlisted run-book models as Markdown."""

from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from html.parser import HTMLParser
import re
from typing import Any, Dict
from urllib.parse import urlparse


class _VisibleTextParser(HTMLParser):
    """Extract visible text from the small Notes HTML allowlist."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.suppressed_depth = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag in {"script", "style", "iframe", "object", "embed", "form"}:
            self.suppressed_depth += 1
            return
        if self.suppressed_depth:
            return
        if tag in {"p", "li", "br"} and self.parts:
            self.parts.append("\n")
        if tag == "li":
            self.parts.append("- ")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "iframe", "object", "embed", "form"}:
            self.suppressed_depth = max(0, self.suppressed_depth - 1)
            return
        if self.suppressed_depth:
            return
        if tag in {"p", "li"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.suppressed_depth:
            self.parts.append(data)


class _CommentMarkdownParser(HTMLParser):
    """Convert the supported Object Notes HTML subset to safe Markdown."""

    _SUPPRESSED_TAGS = {"script", "style", "iframe", "object", "embed", "form"}
    _SUPPORTED_TAGS = {
        "p", "div", "blockquote", "br", "ul", "ol", "li", "strong", "b",
        "em", "i", "code", "a",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.suppressed_depth = 0
        self.list_stack: list[str] = []
        self.link_urls: list[str | None] = []
        self.has_unsupported_markup = False

    def _break(self) -> None:
        if self.parts and not self.parts[-1].endswith("\n"):
            self.parts.append("\n")

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag not in self._SUPPORTED_TAGS and tag not in self._SUPPRESSED_TAGS:
            self.has_unsupported_markup = True
            return
        if tag in self._SUPPRESSED_TAGS:
            self.suppressed_depth += 1
            return
        if self.suppressed_depth:
            return
        if tag in {"p", "div", "blockquote"}:
            self._break()
        elif tag == "br":
            self.parts.append("\n")
        elif tag in {"ul", "ol"}:
            self._break()
            self.list_stack.append(tag)
        elif tag == "li":
            self._break()
            self.parts.append("- " if not self.list_stack or self.list_stack[-1] == "ul" else "1. ")
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")
        elif tag == "code":
            self.parts.append("`")
        elif tag == "a":
            href = dict(attrs).get("href")
            parsed = urlparse(href) if isinstance(href, str) else None
            safe_url = href if parsed and parsed.scheme in {"http", "https", "mailto"} else None
            self.link_urls.append(safe_url)
            if safe_url:
                self.parts.append("[")

    def handle_endtag(self, tag: str) -> None:
        if tag not in self._SUPPORTED_TAGS and tag not in self._SUPPRESSED_TAGS:
            self.has_unsupported_markup = True
            return
        if tag in self._SUPPRESSED_TAGS:
            self.suppressed_depth = max(0, self.suppressed_depth - 1)
            return
        if self.suppressed_depth:
            return
        if tag in {"p", "div", "blockquote", "li"}:
            self._break()
        elif tag in {"ul", "ol"}:
            if self.list_stack:
                self.list_stack.pop()
            self._break()
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")
        elif tag == "code":
            self.parts.append("`")
        elif tag == "a" and self.link_urls:
            href = self.link_urls.pop()
            if href:
                self.parts.append("](<" + href.replace("\\", "\\\\").replace(")", "\\)") + ">)")

    def handle_data(self, data: str) -> None:
        if self.suppressed_depth:
            return
        self.parts.append(
            escape(data, quote=False)
            .replace("\\", "\\\\")
            .replace("`", "\\`")
            .replace("*", "\\*")
            .replace("_", "\\_")
            .replace("[", "\\[")
            .replace("]", "\\]")
        )


def _cell(value: Any, fallback: str = "—") -> str:
    text = str(value).strip() if value not in (None, "") else fallback
    return (
        escape(text, quote=False)
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\n", " / ")
    )


def _visible_notes(value: Any) -> str:
    if value in (None, ""):
        return ""
    parser = _VisibleTextParser()
    parser.feed(str(value))
    parser.close()
    lines = [" ".join(line.split()) for line in "".join(parser.parts).splitlines()]
    return "\n".join(line for line in lines if line)


def _comment_markdown(value: Any) -> str:
    if not isinstance(value, str):
        return str(value) if value is not None else ""
    if not value:
        return ""
    try:
        parser = _CommentMarkdownParser()
        parser.feed(value)
        parser.close()
        if parser.has_unsupported_markup:
            # Preserve unsupported HTML as literal code so it stays visible
            # without being interpreted by the chat renderer.
            return "```html\n" + value.replace("```", "``\\`") + "\n```"
        lines = [" ".join(line.split()) for line in "".join(parser.parts).splitlines()]
        rendered = "\n".join(line for line in lines if line)
    except (ValueError, TypeError):
        rendered = ""
    if rendered:
        return rendered
    # This also covers supported-but-nontext markup such as a script-only
    # comment. Keep it visible as code rather than returning active HTML.
    return "```html\n" + value.replace("```", "``\\`") + "\n```"


def _utc_comment_timestamp(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Comment LastUpdateDate must be non-empty text.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("Comment LastUpdateDate must be ISO-8601 text.") from error
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    timestamp = parsed.astimezone(timezone.utc)
    hour = timestamp.hour % 12 or 12
    meridiem = "AM" if timestamp.hour < 12 else "PM"
    return (
        f"{timestamp.strftime('%b')} {timestamp.day}, {timestamp.year}, "
        f"{hour}:{timestamp.strftime('%M')} {meridiem} UTC"
    )


def _link(label: Any, url: Any) -> str:
    safe_label = (
        escape(str(label or "Open link"), quote=False)
        .replace("[", "\\[")
        .replace("]", "\\]")
    )
    return f"[{safe_label}](<{str(url)}>)"


_TRAILING_URL_LABEL_PATTERN = re.compile(
    r"\s*\(<?(?:[a-z][a-z0-9+.-]*://|www\.|/|#)[^)\s>]+>?\)\s*$",
    re.IGNORECASE,
)


def _attachment_label(label: Any) -> str:
    text = str(label or "Attachment").strip() or "Attachment"
    cleaned = _TRAILING_URL_LABEL_PATTERN.sub("", text).strip()
    return cleaned or "Attachment"


_DASHBOARD_TABLE_HEADER = "| Sequence | Task | Status |"
_DASHBOARD_TABLE_DIVIDER = "|---:|---|---|"

_TASK_TABLE_HEADER = "| Sequence | Task | Status | % Completed | Required |"
_TASK_TABLE_DIVIDER = "|---:|---|---|---:|---|"


def _task_table_row(task: Dict[str, Any], *, include_details: bool = True) -> str:
    percentage = task.get("percentage")
    progress = f"{percentage}%" if isinstance(percentage, int) else "—"
    sequence = task.get("sequence")
    sequence_display = (
        f"{sequence}."
        if sequence is not None and str(sequence).strip()
        else "—"
    )
    return (
        "| "
        + " | ".join(
            (
                _cell(sequence_display),
                _cell(task.get("name"), "Unnamed task"),
                _cell(task.get("status"), "Unknown"),
            )
            + ((_cell(progress), "Yes" if task.get("required") else "No") if include_details else ())
        )
        + " |"
    )


def dashboard_markdown(model: Dict[str, Any], summary: str) -> str:
    """Render a complete user-facing Run Book dashboard."""

    lines: list[str] = []
    title = str(model.get("journeyTitle") or "").strip()
    if title:
        lines.extend((f"# {escape(title, quote=False)}", ""))
    lines.extend((summary, ""))
    task_count = 0
    for stage in model.get("stages") or []:
        if not isinstance(stage, dict):
            continue
        lines.extend(
            (
                f"## {_cell(stage.get('name'), 'Tasks')}",
                "",
                _DASHBOARD_TABLE_HEADER,
                _DASHBOARD_TABLE_DIVIDER,
            )
        )
        stage_task_count = 0
        for task in stage.get("tasks") or []:
            if not isinstance(task, dict):
                continue
            task_count += 1
            stage_task_count += 1
            lines.append(_task_table_row(task, include_details=False))
        if not stage_task_count:
            lines.append("| — | No tasks | — |")
        lines.append("")
    if not task_count:
        if not any(isinstance(stage, dict) for stage in model.get("stages") or []):
            lines.extend(
                (
                    "## Tasks",
                    "",
                    _DASHBOARD_TABLE_HEADER,
                    _DASHBOARD_TABLE_DIVIDER,
                    "| — | No tasks | — |",
                )
            )
    return "\n".join(lines).rstrip()


def runbook_list_markdown(model: Dict[str, Any]) -> str:
    """Render the current page of Run Books without exposing IDs."""

    lines = [
        "# Run Books",
        "",
        "| Runbook | Status | My tasks |",
        "|---|---|---:|",
    ]
    runbooks = model.get("runbooks") or []
    for runbook in runbooks:
        if not isinstance(runbook, dict):
            continue
        lines.append(
            f"| {_cell(runbook.get('name'), 'Unnamed Run Book')} | "
            f"{_cell(runbook.get('status'), 'Unknown')} | "
            f"{_cell(runbook.get('completedTasks'), '0')} of "
            f"{_cell(runbook.get('totalTasks'), '0')} Completed |"
        )
    if not runbooks:
        lines.append("| No Run Books | — | — |")
    if model.get("hasMore"):
        lines.extend(("", "More Run Books are available. Say `load more` to continue."))
    return "\n".join(lines)


def task_markdown(model: Dict[str, Any]) -> str:
    """Render a complete user-facing Run Book task."""

    lines = [
        f"# {_cell(model.get('name'), 'Task')}",
        "",
        _TASK_TABLE_HEADER,
        _TASK_TABLE_DIVIDER,
        _task_table_row(model),
    ]
    notes = _visible_notes(model.get("notesHtml"))
    if notes:
        lines.extend(("", "## Notes", "", escape(notes, quote=False)))
    comments = model.get("comments")
    if isinstance(comments, list) and comments:
        rendered_comments: list[tuple[str, str, str]] = []
        for comment in comments:
            if not isinstance(comment, dict):
                continue
            try:
                timestamp = _utc_comment_timestamp(comment.get("lastUpdated"))
            except ValueError:
                timestamp = "Unknown date"
            author = str(comment.get("author") or "Unknown author").strip()
            text = _comment_markdown(comment.get("textHtml"))
            if text:
                rendered_comments.append((timestamp, author, text))
        if rendered_comments:
            lines.extend(("", "## Comments", ""))
            for index, (timestamp, author, text) in enumerate(rendered_comments):
                lines.extend(
                    (
                        f"**{escape(author, quote=False)}** — {escape(timestamp, quote=False)}  ",
                        text,
                    )
                )
                if index < len(rendered_comments) - 1:
                    lines.append("")

    attachments = model.get("attachments")
    if isinstance(attachments, list) and attachments:
        lines.extend(("", "## Attachments", ""))
        for attachment in attachments:
            if not isinstance(attachment, dict):
                continue
            label = _attachment_label(
                attachment.get("fileName") or attachment.get("title")
            )
            url = (
                attachment.get("previewUrl")
                or attachment.get("fileUrl")
                or attachment.get("url")
            )
            lines.append(
                f"- {_link(label, url)}" if url else f"- {escape(str(label), quote=False)}"
            )

    status_rows = model.get("dataLoadStatusRows")
    if (
        model.get("type") == "ORA_CHK_DATA_LOADER"
        and isinstance(status_rows, list)
        and status_rows
    ):
        lines.extend(
            (
                "",
                "## Data Load Status",
                "",
                "| Data Set Name | Business Object | Status | Loaded | Errors | Skipped |",
                "|---|---|---|---:|---:|---:|",
            )
        )
        for row in status_rows:
            if not isinstance(row, dict):
                continue
            lines.append(
                "| "
                + " | ".join(
                    _cell(row.get(key))
                    for key in (
                        "dataSetName",
                        "businessObjectName",
                        "dataSetStatus",
                        "loadedCount",
                        "errorCount",
                        "skippedCount",
                    )
                )
                + " |"
            )

    external_url = model.get("externalUrl")
    if model.get("type") == "ORA_CHK_EXTERNAL_URL" and external_url:
        lines.extend(
            (
                "",
                "## External action",
                "",
                _link(model.get("externalLabel") or "Open link", external_url),
            )
        )
    documents = model.get("documents")
    if (
        model.get("type") == "ORA_CHK_DOC"
        and isinstance(documents, list)
        and documents
    ):
        lines.extend(("", "## Documents", ""))
        for document in documents:
            if isinstance(document, dict) and document.get("previewUrl"):
                lines.append(
                    f"- {_link(document.get('fileName') or 'Document', document['previewUrl'])}"
                )
    return "\n".join(lines)
