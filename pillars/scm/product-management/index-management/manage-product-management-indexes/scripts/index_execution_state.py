#!/usr/bin/env python3
"""Persist one Product Management index execution continuation state."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import re
from pathlib import Path
import sys
import tempfile
from uuid import uuid4


REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
PROJECTS_ROOT = REPOSITORY_ROOT / "project"
STATE_RELATIVE_PATH = Path(
    "artifacts/pillars/scm/product-management/index-management/"
    "manage-product-management-indexes/current/index-execution-state.json"
)

STATES = frozenset(
    {
        "data_load_submitted",
        "data_load_pending",
        "data_load_succeeded",
        "data_load_failed",
        "readback_verified",
        "ess_approval_pending",
        "ess_submitting",
        "ess_submitted",
        "ess_skipped",
        "blocked",
    }
)

TRANSITIONS = {
    None: {"data_load_submitted", "ess_approval_pending", "blocked"},
    "data_load_submitted": {"data_load_pending", "data_load_succeeded", "data_load_failed", "blocked"},
    "data_load_pending": {"data_load_pending", "data_load_succeeded", "data_load_failed", "blocked"},
    "data_load_failed": {"ess_approval_pending", "blocked"},
    "data_load_succeeded": {"readback_verified", "blocked"},
    "readback_verified": {"ess_approval_pending", "blocked"},
    "ess_approval_pending": {"ess_submitting", "ess_skipped", "blocked"},
    "ess_submitting": {"ess_submitted", "blocked"},
    "ess_submitted": set(),
    "ess_skipped": set(),
    "blocked": {"data_load_failed", "data_load_pending", "data_load_succeeded", "readback_verified", "ess_submitted"},
}
TERMINAL_STATES = frozenset({"ess_submitted", "ess_skipped", "blocked"})


class StateError(ValueError):
    """Raised when an execution state or transition is unsafe."""


class ArtifactPersistenceError(RuntimeError):
    """Raised when durable state cannot be safely persisted."""


def _validate_live_load_evidence(current: dict | None, evidence: dict | None,
                                 event: str) -> None:
    """Validate fresh host-normalized status facts without saving a core report."""
    if (not current or not isinstance(evidence, dict)
            or evidence.get("confirmed") is not True
            or evidence.get("user_requested_status_check") is not True):
        raise StateError("A fresh user-requested core status check is required without a saved report.")
    for key in ("environment", "request_sha256", "canonical_index_name", "data_loader_request_id"):
        if not current.get(key) or evidence.get(key) != current[key]:
            raise StateError(f"Live status {key} must match the saved invocation binding.")
    if evidence.get("outcome") != event:
        raise StateError("Live status outcome differs from the requested checkpoint.")
    if current.get("ess_dispatch_status") != "not_attempted":
        raise StateError("Load status cannot erase an ESS dispatch attempt.")


def _nonblank(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StateError(f"{field} must be one nonblank string.")
    return value.strip()


def _request_id(value: object, field: str = "data_loader_request_id") -> str:
    text = _nonblank(value, field)
    if not text.isdecimal() or int(text) <= 0:
        raise StateError(f"{field} must be a positive integer.")
    return text


def _load(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ArtifactPersistenceError("unable to read index execution state") from error
    if not isinstance(value, dict) or value.get("schema_version") != "1.0":
        raise StateError("index execution state must be a schema_version 1.0 object.")
    state = value.get("state")
    if state not in STATES:
        raise StateError("index execution state has an unsupported state.")
    _nonblank(value.get("canonical_index_name"), "canonical_index_name")
    return value


def state_path_for_project(project_root: Path) -> Path:
    """Return the sole registered continuation-state path for one project."""
    try:
        root = project_root.resolve()
        if root.parent != PROJECTS_ROOT.resolve() or not root.name:
            raise StateError("project_root must be an existing project/{project_id} workspace.")
        if not root.is_dir():
            raise StateError("project_root must be an existing directory.")

        current = root
        for component in STATE_RELATIVE_PATH.parts[:-1]:
            current = current / component
            if current.exists():
                if current.is_symlink() or not current.is_dir():
                    raise ArtifactPersistenceError("index execution state directory is unsafe")
            else:
                current.mkdir()
            if not current.resolve().is_relative_to(root):
                raise ArtifactPersistenceError(
                    "index execution state directory is outside the project workspace"
                )

        target = current / STATE_RELATIVE_PATH.name
        if target.is_symlink() or not target.parent.resolve().is_relative_to(root):
            raise ArtifactPersistenceError("index execution state path is unsafe")
        return target
    except OSError as error:
        raise ArtifactPersistenceError("unable to prepare index execution state path") from error


def transition(
    current: dict[str, object] | None,
    *,
    event: str,
    canonical_index_name: str | None,
    data_loader_request_id: str | None,
    artifact_refs: list[str],
    data_loader_terminal_status: str | None = None,
    failed_load_rebuild_choice: str | None = None,
    ess_request_id: str | None = None,
    ess_dispatch_uncertain: bool = False,
    data_loader_dispatch_uncertain: bool = False,
    environment: str | None = None,
    request_sha256: str | None = None,
    approved_payload_sha256: str | None = None,
    reconciliation: dict | None = None,
) -> dict[str, object]:
    if event not in STATES:
        raise StateError("event must name a supported execution state.")
    previous = current.get("state") if current else None
    if event not in TRANSITIONS[previous]:
        raise StateError(f"Cannot transition from {previous or 'new'} to {event}.")

    # A legacy checkpoint can be inspected, but missing original bindings
    # cannot be supplied later as if they had been recorded before dispatch.
    if current is not None:
        for key in ("environment", "request_sha256"):
            if not current.get(key):
                raise StateError(f"Legacy checkpoint lacks {key}; recover original evidence before continuation.")
    bindings = {}
    for key, supplied in (("environment", environment), ("request_sha256", request_sha256),
                          ("approved_payload_sha256", approved_payload_sha256)):
        saved = (current or {}).get(key)
        if supplied is not None:
            supplied = _nonblank(supplied, key)
            if key.endswith("sha256") and not re.fullmatch(r"[0-9a-f]{64}", supplied):
                raise StateError(f"{key} must be a lowercase SHA-256 fingerprint.")
            if saved is not None and supplied != saved:
                raise StateError(f"{key} cannot change during an invocation.")
        if supplied is not None or saved is not None:
            bindings[key] = supplied if supplied is not None else saved
    _nonblank(bindings.get("environment"), "environment")
    if not re.fullmatch(r"[0-9a-f]{64}", _nonblank(bindings.get("request_sha256"), "request_sha256")):
        raise StateError("request_sha256 must be a lowercase SHA-256 fingerprint.")
    if event == "ess_submitting":
        if not re.fullmatch(r"[0-9a-f]{64}", _nonblank(
            bindings.get("approved_payload_sha256"), "approved_payload_sha256"
        )):
            raise StateError("approved_payload_sha256 must be a lowercase SHA-256 fingerprint.")

    recovering = previous == "blocked" and event != "data_load_failed"
    if recovering:
        # Evidence is normalized by the host from the declared core result.
        # This guard validates bindings; it cannot authenticate caller assertions.
        if not isinstance(reconciliation, dict) or reconciliation.get("confirmed") is not True:
            raise StateError("Reconciliation requires confirmed core evidence.")
        if not artifact_refs:
            if event == "ess_submitted":
                raise StateError("ESS reconciliation requires an authorized artifact reference.")
            _validate_live_load_evidence(current, reconciliation, event)
        for key in ("environment", "request_sha256"):
            if not (current or {}).get(key) or reconciliation.get(key) != current[key]:
                raise StateError(f"Reconciliation {key} must match the saved invocation binding.")
        if reconciliation.get("canonical_index_name") != current.get("canonical_index_name"):
            raise StateError("Reconciliation canonical index differs from the invocation.")
        if reconciliation.get("outcome") != event:
            raise StateError("Reconciliation outcome differs from the requested checkpoint.")
        if event == "ess_submitted":
            if current.get("ess_dispatch_status") not in {"submitting", "unknown"}:
                raise StateError("ESS reconciliation requires an existing dispatch attempt.")
            saved_hash = current.get("approved_payload_sha256")
            if not saved_hash or reconciliation.get("approved_payload_sha256") != saved_hash:
                raise StateError("ESS reconciliation must bind the original approved payload.")
            if reconciliation.get("ess_request_id") != ess_request_id:
                raise StateError("ESS reconciliation must bind the confirmed accepted request ID.")
        else:
            if current.get("ess_dispatch_status") != "not_attempted":
                raise StateError("Load reconciliation cannot erase an ESS dispatch attempt.")
            saved_id = current.get("data_loader_request_id")
            if not saved_id or reconciliation.get("data_loader_request_id") != saved_id:
                raise StateError("Load reconciliation must bind the original accepted request ID.")
            if current.get("data_loader_terminal_status") == "Failed":
                raise StateError("A confirmed failed load cannot be relabeled successful or pending.")
            if event == "readback_verified" and reconciliation.get("load_succeeded") is not True:
                raise StateError("Readback reconciliation requires confirmed load success.")
    elif reconciliation is not None and event != "data_load_failed":
        raise StateError("Reconciliation evidence is used only to recover a blocked checkpoint.")

    canonical = (
        _nonblank(canonical_index_name, "canonical_index_name")
        if canonical_index_name is not None
        else _nonblank(current.get("canonical_index_name") if current else None, "canonical_index_name")
    )
    if current is not None and canonical != current["canonical_index_name"]:
        raise StateError("canonical_index_name cannot change during an invocation.")
    request_id = data_loader_request_id or (current or {}).get("data_loader_request_id")
    if event in {"data_load_submitted", "data_load_pending", "data_load_succeeded", "readback_verified"}:
        request_id = _request_id(request_id)
    elif request_id is not None:
        request_id = _request_id(request_id)
    if current is not None and request_id != current.get("data_loader_request_id"):
        raise StateError("data_loader_request_id cannot change during an invocation.")

    terminal_status = (current or {}).get("data_loader_terminal_status")
    choice = (current or {}).get("failed_load_rebuild_choice")
    if event == "data_load_failed":
        _request_id(request_id)
        if data_loader_terminal_status != "Failed":
            raise StateError("data_load_failed requires terminal Failed status.")
        if reconciliation is not None or not artifact_refs:
            _validate_live_load_evidence(current, reconciliation, event)
        terminal_status = "Failed"
        choice = None
    elif data_loader_terminal_status is not None:
        raise StateError("Terminal failure status is supplied only for data_load_failed.")
    if failed_load_rebuild_choice is not None:
        expected = {"proceed": "ess_approval_pending", "decline": "blocked"}
        if (
            previous != "data_load_failed"
            or expected.get(failed_load_rebuild_choice) != event
            or not artifact_refs
        ):
            raise StateError("Failed-load rebuild choice requires the failed state, matching event and decision artifact.")
        choice = failed_load_rebuild_choice
    if previous == "data_load_failed" and event == "ess_approval_pending" and choice != "proceed":
        raise StateError("Rebuild after a failed load requires an explicit proceed choice.")

    ess_id = (current or {}).get("ess_request_id")
    if ess_request_id is not None:
        supplied_id = _request_id(ess_request_id, "ess_request_id")
        if event != "ess_submitted" or (ess_id is not None and ess_id != supplied_id):
            raise StateError("ess_request_id must bind the accepted ESS submission and cannot change.")
        ess_id = supplied_id
    dispatch = (current or {}).get("ess_dispatch_status", "unknown" if previous == "blocked" else "not_attempted")
    loader_uncertain = (current or {}).get("data_loader_dispatch_uncertain", False)
    if ess_dispatch_uncertain or data_loader_dispatch_uncertain:
        if event != "blocked" or not artifact_refs:
            raise StateError("Uncertain dispatch requires blocked state and diagnostic evidence.")
        if ess_dispatch_uncertain:
            dispatch = "unknown"
        loader_uncertain = loader_uncertain or data_loader_dispatch_uncertain
    if event == "ess_submitting":
        if dispatch != "not_attempted" or ess_id is not None or not artifact_refs:
            raise StateError("ESS dispatch requires no previous attempt and an approved payload reference.")
        dispatch = "submitting"
    elif event == "ess_submitted":
        ess_id = _request_id(ess_id, "ess_request_id")
        dispatch = "submitted"
    elif event == "blocked" and dispatch == "submitting":
        dispatch = "unknown"
    elif event == "ess_skipped" and dispatch != "not_attempted":
        raise StateError("An attempted ESS submission cannot be recorded as skipped.")

    history = list((current or {}).get("reconciliation_history") or [])
    if recovering or (previous == "blocked" and event == "data_load_failed" and reconciliation is not None):
        history.append({"from": previous, "to": event, "artifact_refs": list(artifact_refs),
                        "prior_ess_dispatch_status": (current or {}).get("ess_dispatch_status"),
                        "prior_data_loader_dispatch_uncertain": (current or {}).get("data_loader_dispatch_uncertain")})
        if event != "ess_submitted":
            loader_uncertain = False
    refs = list((current or {}).get("artifact_refs") or [])
    for ref in artifact_refs:
        if not isinstance(ref, str) or not ref.strip():
            raise StateError("artifact references must be nonblank strings.")
        if ref not in refs:
            refs.append(ref)
    return {
        "schema_version": "1.0",
        "canonical_index_name": canonical,
        "state": event,
        "data_loader_request_id": request_id,
        "data_loader_dispatch_uncertain": loader_uncertain,
        "ess_dispatch_status": dispatch,
        "ess_request_id": ess_id,
        "artifact_refs": refs,
        **bindings,
        **({"reconciliation_history": history} if history else {}),
        **({
            "data_loader_terminal_status": terminal_status,
            "failed_load_rebuild_choice": choice,
        } if terminal_status else {}),
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def _write(path: Path, state: dict[str, object]) -> None:
    temporary: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as handle:
            temporary = Path(handle.name)
            json.dump(state, handle, indent=2, sort_keys=True)
            handle.write("\n")
        temporary.replace(path)
    except OSError as error:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
        raise ArtifactPersistenceError("unable to persist index execution state") from error


def _archive_terminal(path: Path, current: dict[str, object]) -> Path:
    """Snapshot a terminal invocation while retaining its current checkpoint."""
    if current["state"] not in TERMINAL_STATES:
        raise StateError("A new invocation requires a terminal prior state.")
    if current["state"] == "blocked" and (
        current.get("data_loader_request_id") not in (None, "")
        or current.get("data_loader_dispatch_uncertain") is not False
        or current.get("ess_dispatch_status") != "not_attempted"
        or current.get("ess_request_id") not in (None, "")
        or not current.get("environment")
        or not current.get("request_sha256")
    ):
        raise StateError(
            "Cannot restart blocked external work; reconcile the existing Data Loader or ESS request first. "
            "Legacy blocked states without dispatch evidence also require reconciliation."
        )
    history = path.parent / "history"
    try:
        if history.is_symlink():
            raise ArtifactPersistenceError("index execution history path is unsafe")
        history.mkdir(exist_ok=True)
        if not history.is_dir() or not history.resolve().is_relative_to(path.parent.resolve()):
            raise ArtifactPersistenceError("index execution history path is unsafe")
        archived = history / f"index-execution-state-{uuid4().hex}.json"
        _write(archived, current)
        return archived
    except OSError as error:
        raise ArtifactPersistenceError("unable to archive index execution state") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        required=True,
        type=Path,
        help="Existing project/{project_id} workspace; the state path is derived from it.",
    )
    parser.add_argument("--event", required=True, choices=sorted(STATES))
    parser.add_argument("--canonical-index-name")
    parser.add_argument("--data-loader-request-id")
    parser.add_argument("--artifact-ref", action="append", default=[])
    parser.add_argument("--data-loader-terminal-status", choices=["Failed"])
    parser.add_argument("--failed-load-rebuild-choice", choices=["proceed", "decline"])
    parser.add_argument("--ess-request-id", help="Positive request ID returned by the accepted ESS submission.")
    parser.add_argument("--ess-dispatch-uncertain", action="store_true")
    parser.add_argument("--data-loader-dispatch-uncertain", action="store_true")
    parser.add_argument("--environment", help="Required for a new invocation; inherited unchanged on continuation.")
    parser.add_argument("--request-sha256", help="Required original request fingerprint for a new invocation.")
    parser.add_argument("--approved-payload-sha256", help="Required approved ESS payload fingerprint before ess_submitting.")
    parser.add_argument("--reconcile-stdin", action="store_true", help="Read normalized confirmed core reconciliation evidence from stdin; never submit external work.")
    parser.add_argument(
        "--start-new",
        action="store_true",
        help="Archive a terminal prior invocation and start a fresh invocation, including a same-index restart after validation.",
    )
    args = parser.parse_args(argv)
    stage = "checkpoint_read"
    archived = None
    state_path = None
    try:
        state_path = state_path_for_project(args.project_root)
        current = _load(state_path)
        if args.start_new and args.event not in TRANSITIONS[None]:
            raise StateError("--start-new requires an initial invocation event.")
        if args.start_new and current is None:
            raise StateError("--start-new requires a terminal prior invocation.")
        result = transition(
            None if args.start_new else current,
            event=args.event,
            canonical_index_name=args.canonical_index_name,
            data_loader_request_id=args.data_loader_request_id,
            artifact_refs=args.artifact_ref,
            data_loader_terminal_status=args.data_loader_terminal_status,
            failed_load_rebuild_choice=args.failed_load_rebuild_choice,
            ess_request_id=args.ess_request_id,
            ess_dispatch_uncertain=args.ess_dispatch_uncertain,
            data_loader_dispatch_uncertain=args.data_loader_dispatch_uncertain,
            environment=args.environment,
            request_sha256=args.request_sha256,
            approved_payload_sha256=args.approved_payload_sha256,
            reconciliation=json.load(sys.stdin) if args.reconcile_stdin else None,
        )
        stage = "checkpoint_archive"
        archived = _archive_terminal(state_path, current) if args.start_new else None
        stage = "checkpoint_write"
        # Both writes are atomic. The previous checkpoint remains current if
        # either write fails, so no fallible restoration step is necessary.
        _write(state_path, result)
    except (StateError, json.JSONDecodeError) as error:
        parser.error(str(error))
    except ArtifactPersistenceError:
        refs = []
        if state_path is not None and state_path.is_file():
            refs.append(str(STATE_RELATIVE_PATH))
        if archived is not None:
            refs.append(str(STATE_RELATIVE_PATH.parent / "history" / archived.name))
        print(
            json.dumps(
                {
                    "status": "failed",
                    "failure_class": "artifact_persistence",
                    "stage": stage,
                    "message": "Unable to persist index execution state.",
                    "artifact_refs": refs,
                    "recommended_action": "Stop continuation; inspect the retained checkpoint evidence and resolve storage before retrying the local checkpoint operation. Do not repeat a Fusion operation.",
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
