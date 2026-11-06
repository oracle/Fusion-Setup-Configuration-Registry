#!/usr/bin/env python3
"""Command-line entry point for the Run Book skill."""

import argparse
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, IO, Optional, Sequence

from data_loader_handoff import read_run_id, stamp_run_id
from runbook_client import (
    ApiError,
    RunbookClient,
)
from runbook_service import (
    CreatePayloadValidationError,
    RunbookService,
    build_runbook_list_result,
)
from runbook_values import positive_int64
from runbook_workflows import (
    PartialCreationError,
    PartialMergeError,
    PartialTaskAddError,
    PartialTaskAttachmentError,
    PartialTaskUpdateError,
    TaskAttachmentFailureError,
    add_task,
    attach_task_files,
    create_runbook,
    merge_runbook as runbook_merge_runbook,
    prepare_attachment_input,
    update_task as runbook_update_task,
)
from status_catalog import UPDATE_STATUS_CODES
from markdown_renderer import dashboard_markdown, runbook_list_markdown, task_markdown


SKILL_ROOT = Path(__file__).resolve().parent.parent
SHARED_ROOT = SKILL_ROOT.parent
DATA_LOADER_CONFIG = SHARED_ROOT / "data-loader" / "config" / "env.properties"
REPOSITORY_ROOT = SHARED_ROOT.parent
FUSION_PROPERTIES = REPOSITORY_ROOT / "core" / "auth" / "fusionEnv.properties"
DEFAULT_TOKEN_CACHE = Path("auto")
FUSION_AUTH_SCRIPTS = (
    REPOSITORY_ROOT
    / "core"
    / "auth"
    / "fusion-oauth-authentication"
    / "scripts"
)
DEFAULT_RUNBOOK_LIST_PAGE_SIZE = 10
PROJECT_RUNBOOK_PLAN = Path("artifacts/shared/runbook/current/runbook-plan.json")
REMOTE_COMMANDS = frozenset(
    {
        "list-tasks",
        "list-runbooks",
        "get-journey",
        "get-task",
        "get-documents",
        "summary",
        "dashboard",
        "task-detail",
        "add-task",
        "attach-task-files",
        "create-runbook",
        "merge-runbook",
        "update-task",
        "force-complete-runbook",
    }
)
ACTIVE_JOURNEY_COMMANDS = frozenset(
    {
        "list-tasks",
        "get-journey",
        "summary",
        "dashboard",
        "merge-runbook",
    }
)


def build_authenticated_client(
    *,
    properties_path: Path = FUSION_PROPERTIES,
    token_cache_path: Optional[Path] = None,
    access_token: Optional[str] = None,
    auth_code: Optional[str] = None,
    code_verifier: Optional[str] = None,
    redirect_url: Optional[str] = None,
    callback_timeout: Optional[int] = None,
    force_login: bool = False,
    open_browser: bool = True,
    total_record_fetch_limit: int = 2500,
    pagination_record_limit: int = 500,
    pagination_limit: int = 50,
    auth_module: Any = None,
) -> RunbookClient:
    """Build a Run Book client by delegating authentication to core auth."""

    if auth_module is None:
        if not FUSION_AUTH_SCRIPTS.is_dir():
            raise ValueError(
                "Fusion OAuth scripts are unavailable under core/auth."
            )
        auth_scripts = str(FUSION_AUTH_SCRIPTS)
        if auth_scripts not in sys.path:
            sys.path.insert(0, auth_scripts)
        try:
            import fusion_auth as auth_module
        except ImportError as error:
            raise ValueError("Fusion OAuth support could not be loaded.") from error

    try:
        properties = auth_module.read_properties(Path(properties_path))
        auth_module.require_props(properties, ["environment", "restBaseUrl"])
    except (OSError, ValueError) as error:
        raise ValueError(
            "Fusion authentication properties could not be loaded."
        ) from error

    explicit_access_token = access_token
    if explicit_access_token is not None and not explicit_access_token.strip():
        raise ValueError("Fusion access token must be non-empty text when supplied.")

    def authorization(*, refresh: bool) -> str:
        if explicit_access_token is not None:
            return f"Bearer {explicit_access_token}"
        token_options: dict[str, Any] = {
            "redirect_url": redirect_url,
            "auth_code": auth_code,
            "code_verifier": code_verifier,
            "open_browser": open_browser,
            "force_login": force_login or refresh,
        }
        if token_cache_path is not None:
            token_options["token_cache"] = str(token_cache_path)
        if callback_timeout is not None:
            token_options["callback_timeout"] = callback_timeout
        try:
            access_token = auth_module.get_access_token(
                properties,
                **token_options,
            )
        except Exception as error:
            raise ApiError(
                "Fusion OAuth authentication failed before the REST request."
            ) from error
        if not isinstance(access_token, str) or not access_token.strip():
            raise ApiError("Fusion OAuth authentication returned no access token.")
        return f"Bearer {access_token}"

    return RunbookClient(
        total_record_fetch_limit=total_record_fetch_limit,
        pagination_record_limit=pagination_record_limit,
        pagination_limit=pagination_limit,
        base_url=properties["restBaseUrl"].rstrip("/"),
        authorization=authorization(refresh=False),
        refresh_authorization=(
            None
            if explicit_access_token is not None
            else lambda: authorization(refresh=True)
        ),
    )


def resolve_journey_id(
    value: Any,
    config_path: Optional[Path] = None,
) -> str:
    """Resolve an explicit or configured WorkerJourneyId."""

    candidate = value
    if candidate is None:
        candidate = read_run_id(config_path or DATA_LOADER_CONFIG)
    if candidate is None:
        raise ValueError(
            "No Run Book is available to show. Create or select a Run Book, "
            "then try again."
        )
    return str(positive_int64(candidate, "WorkerJourneyId"))


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def task_percentage_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0 or parsed > 100:
        raise argparse.ArgumentTypeError("must be an integer from 0 through 100")
    return parsed


def add_journey_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--journey-id")
    parser.add_argument("--offset", type=nonnegative_int, default=0)


def add_task_id_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--parent-worker-journey-id", required=True)
    parser.add_argument("--worker-journey-task-id", required=True)


def add_oauth_arguments(parser: argparse.ArgumentParser) -> None:
    """Add authentication and collection limits used by remote commands."""
    parser.add_argument("--total-record-fetch-limit", type=positive_int, default=2500)
    parser.add_argument("--pagination-record-limit", type=positive_int, default=500)
    parser.add_argument("--pagination-limit", type=positive_int, default=50)

    parser.add_argument(
        "--properties",
        type=Path,
        default=FUSION_PROPERTIES,
        help="Fusion OAuth properties file.",
    )
    parser.add_argument(
        "--token-cache",
        type=Path,
        default=DEFAULT_TOKEN_CACHE,
        help=(
            "External private cache override; defaults to ~/.fusionaim/<profile-fingerprint>_token.json."
        ),
    )
    parser.add_argument(
        "--access-token",
        help="Existing Fusion bearer token; never written to output.",
    )
    parser.add_argument("--auth-code", help="OAuth authorization code.")
    parser.add_argument(
        "--code-verifier",
        help="PKCE verifier matching a supplied OAuth authorization code.",
    )
    parser.add_argument("--redirect-url", help="OAuth redirect URL override.")
    parser.add_argument(
        "--callback-timeout",
        type=positive_int,
        help="Seconds to wait for the shared OAuth callback.",
    )
    parser.add_argument(
        "--force-login",
        action="store_true",
        help="Ignore a cached token and invoke shared Fusion OAuth login.",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        default=True,
        help="Open the shared OAuth login URL when login is required.",
    )
    parser.add_argument(
        "--no-open-browser",
        action="store_false",
        dest="open_browser",
        help="Print the shared OAuth login URL without opening a browser.",
    )


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create, retrieve, format, and update Oracle Fusion run books.",
        allow_abbrev=False,
    )
    commands = parser.add_subparsers(dest="command", required=True)

    list_command = commands.add_parser(
        "list-tasks", help="Retrieve all run-book tasks.", allow_abbrev=False
    )
    add_journey_arguments(list_command)

    runbook_list_command = commands.add_parser(
        "list-runbooks",
        help="Retrieve and format a page of Run Books.",
        allow_abbrev=False,
    )
    runbook_list_command.add_argument("--offset", type=nonnegative_int, default=0)
    runbook_list_command.add_argument(
        "--page-size",
        type=positive_int,
        default=DEFAULT_RUNBOOK_LIST_PAGE_SIZE,
    )
    runbook_list_command.add_argument(
        "--query-stdin",
        action="store_true",
        help="Read the exact Run Book name query from standard input.",
    )
    runbook_list_command.add_argument(
        "--status",
        action="append",
        default=[],
        help="Run Book status filter; repeat for multiple statuses.",
    )

    journey_command = commands.add_parser(
        "get-journey", help="Retrieve run-book details.", allow_abbrev=False
    )
    journey_command.add_argument("--journey-id")

    task_command = commands.add_parser(
        "get-task", help="Retrieve raw task details.", allow_abbrev=False
    )
    add_task_id_arguments(task_command)

    documents_command = commands.add_parser(
        "get-documents", help="Retrieve raw task documents.", allow_abbrev=False
    )
    documents_command.add_argument("--offset", type=nonnegative_int, default=0)
    add_task_id_arguments(documents_command)

    summary_command = commands.add_parser(
        "summary", help="Retrieve and summarize all task statuses.", allow_abbrev=False
    )
    add_journey_arguments(summary_command)

    dashboard_command = commands.add_parser(
        "dashboard",
        help="Retrieve and format the run-book dashboard as Markdown.",
        allow_abbrev=False,
    )
    add_journey_arguments(dashboard_command)
    dashboard_command.add_argument(
        "--include-task-index",
        action="append",
        type=nonnegative_int,
        help=(
            "Show only a selected zero-based task index; repeat for multiple tasks."
        ),
    )

    detail_command = commands.add_parser(
        "task-detail", help="Retrieve and format one task as Markdown.", allow_abbrev=False
    )
    detail_command.add_argument("--journey-id", required=True)
    add_task_id_arguments(detail_command)
    for collection in ("attachments", "comments", "documents"):
        detail_command.add_argument(f"--{collection}-offset", type=nonnegative_int, default=0)
    add_task_command = commands.add_parser(
        "add-task",
        help="Add one ad hoc task and format its details as Markdown.",
        allow_abbrev=False,
    )
    add_task_command.add_argument("--journey-id", required=True)
    add_task_command.add_argument("--input-stdin", action="store_true", required=True)

    attachment_command = commands.add_parser(
        "attach-task-files",
        help="Attach one or more files to a Run Book task.",
        allow_abbrev=False,
    )
    add_task_id_arguments(attachment_command)
    attachment_command.add_argument("--input-stdin", action="store_true", required=True)

    create_command = commands.add_parser(
        "create-runbook",
        help="Create an assigned run book and format its dashboard as Markdown.",
        allow_abbrev=False,
    )
    create_command.add_argument(
        "--project-root",
        type=Path,
        required=True,
        help=(
            "Initialized project workspace whose runbook_control is updated "
            "for this creation attempt."
        ),
    )

    merge_command = commands.add_parser(
        "merge-runbook",
        help="Merge an implementation plan into an assigned Run Book.",
        allow_abbrev=False,
    )
    merge_command.add_argument("--journey-id")
    merge_command.add_argument("--input-stdin", action="store_true", required=True)

    update_command = commands.add_parser(
        "update-task", help="Patch one task.", allow_abbrev=False
    )
    add_task_id_arguments(update_command)
    update_command.add_argument("--journey-id")
    update_command.add_argument("--input-stdin", action="store_true")
    update_command.add_argument("--status", choices=tuple(UPDATE_STATUS_CODES))
    update_command.add_argument("--task-percentage", type=task_percentage_int)
    update_command.add_argument("--reopen", action="store_true")
    comment_source = update_command.add_mutually_exclusive_group()
    comment_source.add_argument(
        "--comments",
        help="Create one short, single-line task comment.",
    )
    comment_source.add_argument(
        "--comments-stdin",
        action="store_true",
        help="Create one task comment from the exact standard-input text.",
    )

    force_complete_command = commands.add_parser(
        "force-complete-runbook",
        help="Force-complete one selected Run Book.",
        allow_abbrev=False,
    )
    force_complete_command.add_argument("--journey-id", required=True)

    for remote_parser in (
        list_command,
        runbook_list_command,
        journey_command,
        task_command,
        documents_command,
        summary_command,
        dashboard_command,
        detail_command,
        add_task_command,
        attachment_command,
        create_command,
        merge_command,
        update_command,
        force_complete_command,
    ):
        add_oauth_arguments(remote_parser)

    return parser.parse_args(argv)


def write_json(value: Any, output: IO[str] = sys.stdout) -> None:
    json.dump(value, output, ensure_ascii=False)
    output.write("\n")


def load_project_state(project_root: Path) -> tuple[Path, dict[str, Any]]:
    """Read a direct project workspace without changing its state."""

    root = project_root.resolve()
    projects_root = (REPOSITORY_ROOT / "project").resolve()
    if root.parent != projects_root:
        raise ValueError(
            "--project-root must be a direct workspace under project/."
        )
    state_path = root / "state" / "project-state.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            "Project Run Book state must be a readable JSON object."
        ) from error
    if not isinstance(state, dict):
        raise ValueError("Project Run Book state must be a JSON object.")
    return state_path, state


def load_project_plan_stdin(project_root: Path) -> IO[str]:
    """Return the persisted plan with catalog descriptions as task notes."""

    plan_path = project_root.resolve() / PROJECT_RUNBOOK_PLAN
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ValueError(f"Persisted Run Book plan is unavailable: {plan_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Persisted Run Book plan is not valid JSON: {error.msg}.") from error
    if not isinstance(plan, dict):
        raise ValueError("Persisted Run Book plan must be a JSON object.")
    tasks = plan.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("Persisted Run Book plan must contain a tasks array.")
    task_notes = []
    for task in tasks:
        description = task.get("task_description") if isinstance(task, dict) else None
        if description is not None and not isinstance(description, str):
            raise ValueError("Persisted Run Book task_description must be text or null.")
        task_notes.append(description or "")
    return io.StringIO(json.dumps({"plan": plan, "taskNotes": task_notes}))


def load_project_runbook_state(project_root: Path) -> tuple[Path, dict[str, Any]]:
    """Load an eligible project-backed initial Run Book state."""

    state_path, state = load_project_state(project_root)
    control = state.get("runbook_control")
    if (
        not isinstance(control, dict)
        or control.get("status") != "pending"
        or control.get("active_runbook_ref") not in (None, "")
    ):
        raise ValueError(
            "Project-backed Run Book creation requires runbook_control.status "
            "pending and an empty active_runbook_ref."
        )
    return state_path, state


def write_project_state(path: Path, state: dict[str, Any]) -> None:
    """Atomically replace project state while preserving its file mode."""

    mode = path.stat().st_mode
    temporary_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(state, handle, indent=2)
            handle.write("\n")
            temporary_path = Path(handle.name)
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def persist_project_runbook_outcome(
    state_path: Path,
    *,
    status: str,
    result: Optional[dict[str, Any]] = None,
    failure: Optional[str] = None,
) -> None:
    """Persist only the nested Run Book control after a creation attempt."""

    if status not in {"active", "failed", "unknown"}:
        raise ValueError("Run Book outcome status must be active, failed, or unknown.")
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            "Project Run Book state must remain a readable JSON object."
        ) from error
    if not isinstance(state, dict):
        raise ValueError("Project Run Book state must remain a JSON object.")
    control = state.get("runbook_control")
    if (
        not isinstance(control, dict)
        or control.get("status") != "pending"
        or control.get("active_runbook_ref") not in (None, "")
    ):
        raise ValueError(
            "Project Run Book state changed after creation preflight; refusing "
            "to overwrite it."
        )
    updated_state = dict(state)
    updated_control = dict(control)
    if status == "active":
        response = result or {}
        journey_id = response.get("workerJourneyId")
        if (
            isinstance(journey_id, bool)
            or not isinstance(journey_id, (int, str))
            or not str(journey_id).strip()
        ):
            raise ValueError(
                "Successful Run Book creation returned no valid workerJourneyId."
            )
        server_url = response.get("serverUrl")
        updated_control.update(
            {
                "status": "active",
                "active_runbook_ref": str(journey_id).strip(),
                "server_url": (
                    server_url.strip()
                    if isinstance(server_url, str) and server_url.strip()
                    else None
                ),
                "created_at": datetime.now(timezone.utc)
                .replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z"),
                "failure": None,
            }
        )
    else:
        updated_control.update({"status": status, "failure": failure})
    updated_state["runbook_control"] = updated_control
    write_project_state(state_path, updated_state)


def preinvocation_create_failure_result(
    error: Exception,
    *,
    stage: str,
    project_state: Optional[dict[str, Any]],
) -> dict[str, Any]:
    """Return a safe, actionable error when no Oracle create call was made."""

    control = project_state.get("runbook_control") if project_state else None
    control_status = (
        control.get("status")
        if isinstance(control, dict) and isinstance(control.get("status"), str)
        else "not-assessed"
    )
    if stage == "authentication":
        failure_class = "auth/authz"
        recommended_action = (
            "Restore Fusion authentication configuration or access, then retry "
            "Run Book creation."
        )
    elif isinstance(error, OSError) or isinstance(error.__cause__, OSError):
        failure_class = "artifact persistence"
        recommended_action = (
            "Restore access to the required project artifacts, then retry Run "
            "Book creation."
        )
    else:
        failure_class = "input validation"
        recommended_action = (
            "Correct the Run Book preflight issue, then retry Run Book creation."
        )
    return {
        "created": False,
        "invoked": False,
        "stage": stage,
        "failureClass": failure_class,
        "runbookControlStatus": control_status,
        "error": str(error),
        "recommendedAction": recommended_action,
    }


def main(
    argv: Optional[Sequence[str]] = None,
    *,
    stdin: IO[str] = sys.stdin,
    stdout: IO[str] = sys.stdout,
    stderr: IO[str] = sys.stderr,
    client: Optional[RunbookClient] = None,
) -> int:
    args = parse_args(argv)
    oracle = client
    service: Optional[RunbookService] = None
    prepared_attachments: Optional[list[dict[str, Any]]] = None
    project_state_path: Optional[Path] = None
    project_state: Optional[dict[str, Any]] = None
    create_operation_started = False
    create_stage = "preflight"
    creation_input: IO[str] = stdin

    def mark_create_operation_started() -> None:
        """Record that the Oracle Run Book create call is about to be invoked."""

        nonlocal create_operation_started
        create_operation_started = True

    try:
        if args.command == "attach-task-files":
            prepared_attachments = prepare_attachment_input(stdin)
            args.parent_worker_journey_id = str(
                positive_int64(
                    args.parent_worker_journey_id,
                    "ParentWorkerJourneyId",
                )
            )
            args.worker_journey_task_id = str(
                positive_int64(
                    args.worker_journey_task_id,
                    "WorkerJourneyTaskId",
                )
            )
        if args.command == "create-runbook":
            project_state_path, project_state = load_project_runbook_state(
                args.project_root
            )
            creation_input = load_project_plan_stdin(args.project_root)
        if args.command in ACTIVE_JOURNEY_COMMANDS:
            args.journey_id = resolve_journey_id(args.journey_id)
        elif args.command == "force-complete-runbook":
            args.journey_id = str(
                positive_int64(args.journey_id, "WorkerJourneyId")
            )
        if args.command in REMOTE_COMMANDS:
            if args.command == "create-runbook":
                create_stage = "authentication"
            oracle = oracle or build_authenticated_client(
                total_record_fetch_limit=args.total_record_fetch_limit,
                pagination_record_limit=args.pagination_record_limit,
                pagination_limit=args.pagination_limit,
                properties_path=args.properties,
                token_cache_path=args.token_cache,
                access_token=args.access_token,
                auth_code=args.auth_code,
                code_verifier=args.code_verifier,
                redirect_url=args.redirect_url,
                callback_timeout=args.callback_timeout,
                force_login=args.force_login,
                open_browser=args.open_browser,
            )
            service = RunbookService(oracle)
            if args.command == "create-runbook":
                create_stage = "preflight"
        if args.command == "list-tasks":
            assert oracle is not None
            result = oracle.list_tasks(args.journey_id, **({"offset": args.offset} if args.offset else {}))
        elif args.command == "list-runbooks":
            assert oracle is not None
            query = stdin.read() if args.query_stdin else None
            runbooks = build_runbook_list_result(
                oracle.list_runbooks(args.offset, query, args.status),
                offset=args.offset,
                page_size=args.page_size,
            )
            result = {
                **runbooks,
                "markdown": runbook_list_markdown(runbooks),
            }
        elif args.command == "get-journey":
            assert oracle is not None
            result = oracle.get_journey(args.journey_id)
        elif args.command == "get-task":
            assert oracle is not None
            result = oracle.get_task(
                args.parent_worker_journey_id,
                args.worker_journey_task_id,
            )
        elif args.command == "get-documents":
            assert oracle is not None
            result = oracle.get_documents(
                args.parent_worker_journey_id,
                args.worker_journey_task_id,
                **({"offset": args.offset} if args.offset else {}),
            )
        elif args.command == "summary":
            assert service is not None
            result = service.get_summary(
                args.journey_id,
                **({"offset": args.offset} if args.offset else {}),
            )
        elif args.command == "dashboard":
            assert service is not None
            dashboard = service.get_dashboard(
                args.journey_id,
                include_indexes=args.include_task_index,
                **({"offset": args.offset} if args.offset else {}),
            )
            stamp_run_id(DATA_LOADER_CONFIG, args.journey_id)
            result = {
                **({"pagination": dashboard["pagination"]} if "pagination" in dashboard else {}),
                "summary": dashboard["summary"],
                "counts": dashboard["counts"],
                "journeyTitle": dashboard["runbook"]["journeyTitle"],
                "taskIndex": dashboard["taskIndex"],
                "markdown": dashboard_markdown(
                    dashboard["runbook"], dashboard["summary"]
                ),
            }
        elif args.command == "task-detail":
            assert service is not None
            task = service.get_task_model(
                args.parent_worker_journey_id,
                args.worker_journey_task_id,
                worker_journey_id=args.journey_id,
                **{f"{name}_offset": getattr(args, f"{name}_offset") for name in ("attachments", "comments", "documents") if getattr(args, f"{name}_offset")},
            )
            result = {
                **({"pagination": task["pagination"]} if "pagination" in task else {}),
                "name": task["name"],
                "status": task["status"],
                "type": task["type"],
                "markdown": task_markdown(task),
            }
        elif args.command == "add-task":
            assert oracle is not None and service is not None
            result = add_task(
                client=oracle,
                service=service,
                stdin=stdin,
                journey_id=args.journey_id,
            )
        elif args.command == "attach-task-files":
            assert oracle is not None and prepared_attachments is not None
            result = attach_task_files(
                client=oracle,
                prepared_files=prepared_attachments,
                parent_worker_journey_id=args.parent_worker_journey_id,
                worker_journey_task_id=args.worker_journey_task_id,
            )
        elif args.command == "create-runbook":
            assert oracle is not None and service is not None
            result = create_runbook(
                client=oracle,
                service=service,
                stdin=creation_input,
                data_loader_config=DATA_LOADER_CONFIG,
                on_create_invoked=mark_create_operation_started,
            )
            if project_state_path is not None and project_state is not None:
                try:
                    persist_project_runbook_outcome(
                        project_state_path,
                        status="active",
                        result=result,
                    )
                except (OSError, ValueError) as error:
                    partial_result = {
                        key: value
                        for key, value in result.items()
                        if key != "markdown"
                    }
                    partial_result["error"] = (
                        "Oracle Fusion created the Run Book, but project "
                        "Run Book state could not be persisted."
                    )
                    write_json(partial_result, stdout)
                    print(f"Run Book partial success: {error}", file=stderr)
                    return 3
        elif args.command == "merge-runbook":
            assert oracle is not None and service is not None
            result = runbook_merge_runbook(
                client=oracle,
                service=service,
                stdin=stdin,
                data_loader_config=DATA_LOADER_CONFIG,
                journey_id=args.journey_id,
            )
        elif args.command == "update-task":
            assert oracle is not None and service is not None
            legacy_requested = any(
                (args.status is not None, args.task_percentage is not None,
                 args.reopen, args.comments is not None, args.comments_stdin)
            )
            if args.input_stdin and legacy_requested:
                raise ValueError("Use --input-stdin or legacy update flags, not both.")
            if args.input_stdin:
                try:
                    update_input = json.load(stdin)
                except json.JSONDecodeError as error:
                    raise ValueError(f"Update input is not valid JSON: {error.msg}.") from error
                if not isinstance(update_input, dict):
                    raise ValueError("Update input must be a JSON object.")
            else:
                update_input: dict[str, Any] = {}
                if args.status is not None:
                    update_input["status"] = args.status
                if args.task_percentage is not None:
                    update_input["taskPercentage"] = args.task_percentage
                if args.reopen:
                    update_input["reopen"] = True
                if args.comments_stdin:
                    update_input["comments"] = stdin.read()
                elif args.comments is not None:
                    update_input["comments"] = args.comments
            result = runbook_update_task(
                client=oracle, service=service, update_input=update_input,
                parent_worker_journey_id=args.parent_worker_journey_id,
                worker_journey_task_id=args.worker_journey_task_id,
                worker_journey_id=args.journey_id,
            )
        elif args.command == "force-complete-runbook":
            assert oracle is not None
            oracle.force_complete_runbook(args.journey_id)
            result = {
                "completed": True,
                "markdown": "The Run Book was force-completed successfully.",
            }
        else:
            raise ValueError(f"Unsupported command: {args.command}")
    except PartialCreationError as error:
        partial_result = dict(error.result)
        if project_state_path is not None and project_state is not None:
            try:
                persist_project_runbook_outcome(
                    project_state_path,
                    status="unknown",
                    failure=str(error),
                )
            except (OSError, ValueError) as state_error:
                partial_result["projectStateError"] = (
                    "Run Book outcome was not persisted to project state."
                )
                print(f"Run Book project-state error: {state_error}", file=stderr)
        write_json(partial_result, stdout)
        print(f"Run Book partial success: {error}", file=stderr)
        return 3
    except PartialMergeError as error:
        write_json(error.result, stdout)
        print(f"Run Book partial success: {error}", file=stderr)
        return 3
    except PartialTaskAddError as error:
        write_json(error.result, stdout)
        print(f"Run Book partial success: {error}", file=stderr)
        return 3
    except PartialTaskAttachmentError as error:
        write_json(error.result, stdout)
        print(f"Run Book partial success: {error}", file=stderr)
        return 3
    except TaskAttachmentFailureError as error:
        write_json(error.result, stdout)
        print(f"Run Book error: {error}", file=stderr)
        return 2
    except PartialTaskUpdateError as error:
        write_json(error.result, stdout)
        print(f"Run Book partial success: {error}", file=stderr)
        return 3
    except CreatePayloadValidationError as error:
        failure_result = {
            "created": False,
            "skippedTasks": error.skipped_tasks,
            "error": str(error),
        }
        if (
            args.command == "create-runbook"
            and create_operation_started
            and project_state_path is not None
            and project_state is not None
        ):
            try:
                persist_project_runbook_outcome(
                    project_state_path,
                    status="failed",
                    failure=str(error),
                )
            except (OSError, ValueError) as state_error:
                failure_result["projectStateError"] = (
                    "Run Book failure was not persisted to project state."
                )
                print(f"Run Book project-state error: {state_error}", file=stderr)
        write_json(failure_result, stdout)
        print(f"Run Book error: {error}", file=stderr)
        return 2
    except (ApiError, OSError, ValueError) as error:
        if (
            args.command == "create-runbook"
            and create_operation_started
            and project_state_path is not None
            and project_state is not None
        ):
            failure_result = {"created": False, "error": str(error)}
            try:
                persist_project_runbook_outcome(
                    project_state_path,
                    status="failed",
                    failure=str(error),
                )
            except (OSError, ValueError) as state_error:
                failure_result["projectStateError"] = (
                    "Run Book failure was not persisted to project state."
                )
                print(f"Run Book project-state error: {state_error}", file=stderr)
            write_json(failure_result, stdout)
        elif args.command == "create-runbook":
            write_json(
                preinvocation_create_failure_result(
                    error,
                    stage=create_stage,
                    project_state=project_state,
                ),
                stdout,
            )
        print(f"Run Book error: {error}", file=stderr)
        return 2

    write_json(result, stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
