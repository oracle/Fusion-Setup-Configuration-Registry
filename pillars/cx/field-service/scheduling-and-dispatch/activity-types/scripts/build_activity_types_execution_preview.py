#!/usr/bin/env python3
"""Create an immutable, preview-only Activity Types REST execution record."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any


TASK_CODE = "ORA_FFS_TS_ACTIVITY_TYPES"
LIVE_DIRECTION = "ora_rest_execution"


class ImmutablePreviewError(ValueError):
    """Raised when a preview cannot bind the planned write to its baseline."""


def _load_json(path: Path, description: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ImmutablePreviewError(f"{description} could not be read.") from error


def _parse_baseline(argument: str) -> tuple[str, Path]:
    label, separator, raw_path = argument.partition("=")
    if not separator or not label.strip() or not raw_path.strip():
        raise ImmutablePreviewError("baseline must use LABEL=PATH.")
    return label.strip(), Path(raw_path.strip())


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def build_execution_preview(
    payload_preview: dict[str, Any],
    execution_direction: str,
    environment: str,
    baselines: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if execution_direction != LIVE_DIRECTION:
        raise ImmutablePreviewError("immutable Activity Types REST preview requires ora_rest_execution.")
    if not environment.strip():
        raise ImmutablePreviewError("environment is required.")
    requests = payload_preview.get("requests")
    if not isinstance(requests, list) or not requests:
        raise ImmutablePreviewError("payload preview has no requests.")

    preview_requests: list[dict[str, Any]] = []
    for request in requests:
        if not isinstance(request, dict) or request.get("method") != "PUT":
            raise ImmutablePreviewError("payload preview contains a non-PUT request.")
        body = request.get("body")
        if not isinstance(body, dict) or not isinstance(body.get("label"), str):
            raise ImmutablePreviewError("payload preview request has no label.")
        label = body["label"]
        baseline = baselines.get(label)
        if not isinstance(baseline, dict) or baseline.get("label") != label:
            raise ImmutablePreviewError(f"{label}: matching current-state baseline is required.")
        preview_requests.append(
            {
                "operationId": request.get("operationId"),
                "method": "PUT",
                "path": request.get("path"),
                "body": body,
                "baseline": baseline,
            }
        )

    draft = {
        "schemaVersion": "1.0",
        "taskCode": TASK_CODE,
        "executionDirection": execution_direction,
        "environment": environment.strip(),
        "requests": preview_requests,
    }
    digest = hashlib.sha256(_canonical_json(draft)).hexdigest()
    return {**draft, "sha256": digest, "approvalRequired": True, "retryPolicy": "never"}


def _write_private_preview(output: Path, result: dict[str, Any]) -> None:
    """Create a private approval artifact without replacing files or symlinks."""
    content = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        with os.fdopen(os.open(output, flags, 0o600), "w", encoding="utf-8") as stream:
            stream.write(content)
    except FileExistsError as error:
        raise ImmutablePreviewError("output already exists; choose a fresh destination.") from error
    except OSError as error:
        raise ImmutablePreviewError("private preview output could not be created.") from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload-preview", type=Path, required=True)
    parser.add_argument("--execution-direction", required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--baseline", action="append", required=True, metavar="LABEL=PATH")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload_preview = _load_json(args.payload_preview, "payload preview")
        if not isinstance(payload_preview, dict):
            raise ImmutablePreviewError("payload preview must be an object.")
        baselines = {label: _load_json(path, f"{label} baseline") for label, path in map(_parse_baseline, args.baseline)}
        result = build_execution_preview(payload_preview, args.execution_direction, args.environment, baselines)
        _write_private_preview(args.output, result)
    except ImmutablePreviewError as error:
        print(f"Immutable preview blocked: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
