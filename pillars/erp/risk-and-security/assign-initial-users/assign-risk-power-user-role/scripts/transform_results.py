#!/usr/bin/env python3
"""Evaluate Core REST results for Risk Power User role assignment.

This helper only joins and validates already-returned data.  The pillar skill
prepares every request and the Core REST client skill executes it.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROLE_CODE = "ORA_GTG_RISK_POWER_USER_JOB"
PROVIDED_PROCESS_CATALOG_ENDPOINT = "/api/boss/data/objects/ora/riskMgmtRisk/core/v1/referenceDataValues"
TERMINAL_AAR_STATES = {"APPROVED", "SYSTEM_APPROVED", "COMPLETED", "REJECTED", "FAILED", "WITHDRAWN", "CANCELED", "CANCELLED", "ERROR"}
SUCCESSFUL_AAR_STATES = {"APPROVED", "SYSTEM_APPROVED", "COMPLETED"}


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rows(payload: Any, response_id: str) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        raise ValueError(f"Core response {response_id!r} must be an object")
    for key in ("items", "Resources"):
        value = payload.get(key)
        if isinstance(value, list) and all(isinstance(item, dict) for item in value):
            return value
    if payload.get("id"):
        return [payload]
    raise ValueError(f"Core response {response_id!r} must contain items or Resources")


def exactly_one(payload: Any, response_id: str) -> dict[str, Any] | None:
    result = rows(payload, response_id)
    return result[0] if len(result) == 1 else None


def authenticated_identity(responses: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    current_user = responses.get("current_user")
    username = current_user.get("Username") if isinstance(current_user, dict) else None
    if not isinstance(username, str) or not username.strip():
        return None, {"classification": "authenticated_user_unresolved", "recommended_action": "Sign in again and retry the access review."}

    try:
        user = exactly_one(responses.get("authenticated_user"), "authenticated_user")
    except ValueError:
        user = None
    if user is None or not user.get("id") or user.get("active") is not True:
        return None, {"classification": "authenticated_user_unresolved", "recommended_action": "Sign in again and retry the access review."}
    scim_username = user.get("userName")
    if not isinstance(scim_username, str) or scim_username.casefold() != username.casefold():
        return None, {"classification": "authenticated_user_mismatch", "recommended_action": "Sign in again and retry the access review."}
    return str(user["id"]), {}


def role_members(payload: Any) -> set[str]:
    role = exactly_one(payload, "role_members")
    members = role.get("members", []) if role else None
    if not isinstance(members, list):
        raise ValueError("Risk Power User role membership response is missing or invalid")
    return {str(member["value"]) for member in members if isinstance(member, dict) and member.get("value")}


def is_process_root(item: dict[str, Any]) -> bool:
    """Recognize ordinary L2 roots and the provided Common/Risk Management root."""
    if item.get("levelOne") == item.get("levelTwo"):
        return True
    return item.get("levelOne") == "Common" and str(item.get("referenceCode") or "").endswith(".COMM.ORA")


def owner_links(responses: dict[str, Any]) -> tuple[dict[str, list[dict[str, str]]], list[dict[str, Any]]]:
    processes = rows(responses["process_catalog"], "process_catalog")
    properties = rows(responses["properties"], "properties")
    labels = {
        str(item["valueCode"]): str(item.get("levelTwo") or item["valueCode"])
        for item in processes
        if item.get("valueCode") and is_process_root(item)
    }
    links: dict[str, list[dict[str, str]]] = defaultdict(list)
    exceptions: list[dict[str, Any]] = []
    for item in processes:
        if item.get("levelOne") == "Common" and not is_process_root(item):
            exceptions.append({"classification": "unrecognized_process_root_pattern", "value_code": str(item.get("valueCode") or "Unknown"), "recommended_action": "Confirm the seeded Common process-root pattern before assigning a default owner."})
    for item in properties:
        value_code = str(item.get("valueCode") or "")
        if value_code not in labels:
            continue
        owner_type = str(item.get("defaultOwnerType") or "").upper()
        owner_code = item.get("defaultOwnerCode")
        if owner_type == "USER" and owner_code:
            links[str(owner_code)].append({"value_code": value_code, "process": labels[value_code]})
        elif owner_type:
            exceptions.append({"classification": "non_user_owner", "value_code": value_code, "owner_type": owner_type})
        else:
            exceptions.append({"classification": "missing_default_owner", "value_code": value_code})
    return links, exceptions


def discovery(source: dict[str, Any], responses: dict[str, Any]) -> dict[str, Any]:
    if source.get("process_catalog_endpoint") != PROVIDED_PROCESS_CATALOG_ENDPOINT:
        raise ValueError("Discovery requires the direct provided referenceDataValues process catalog")
    role = exactly_one(responses["role"], "role")
    requested_by_user_guid, identity_exception = authenticated_identity(responses)
    if requested_by_user_guid is None or role is None or not role.get("id"):
        exception = identity_exception if requested_by_user_guid is None else {"classification": "role_resolution_exception", "recommended_action": "Ask the security administrator to validate the Risk Power User role setup."}
        return {"stage": "discovery", "status": "blocked", "candidates": [], "exceptions": [exception]}
    links, exceptions = owner_links(responses)
    output: dict[str, Any] = {
        "stage": "discovery",
        "requested_by_user_guid": requested_by_user_guid,
        "role_id": str(role["id"]),
        "role_code": str(source.get("role_code") or ROLE_CODE),
        "owner_user_ids": sorted(links),
        "needs_role_membership": "role_members" not in responses,
        "exceptions": exceptions,
        "candidates_requiring_decision": [],
        "already_assigned": [],
        "ineligible": [],
    }
    unresolved = [user_id for user_id in links if f"user:{user_id}" not in responses]
    if unresolved or output["needs_role_membership"]:
        output["needs_user_lookups"] = sorted(unresolved)
        return output
    members = role_members(responses["role_members"])
    for user_id, processes in sorted(links.items()):
        user = exactly_one(responses[f"user:{user_id}"], f"user:{user_id}")
        if user is None or not user.get("id"):
            exceptions.append({"classification": "owner_identity_unresolved", "processes": processes})
            continue
        candidate = {
            "user_guid": str(user["id"]),
            "username": str(user.get("userName") or "Unknown user"),
            "display_name": str(user.get("displayName") or user.get("userName") or "Unknown user"),
            "active": user.get("active") is True,
            "already_member": str(user["id"]) in members,
            "processes": processes,
        }
        if not candidate["active"]:
            candidate["reason"] = "inactive"
            output["ineligible"].append(candidate)
        elif candidate["already_member"]:
            output["already_assigned"].append(candidate)
        else:
            output["candidates_requiring_decision"].append(candidate)
    output["needs_user_lookups"] = []
    output["needs_role_membership"] = False
    output["status"] = "needs_fresh_eligibility_check" if output["candidates_requiring_decision"] else "completed_no_change_required"
    return output


def preflight(source: dict[str, Any], responses: dict[str, Any]) -> dict[str, Any]:
    requested_by_user_guid, role_id = source.get("requested_by_user_guid"), source.get("role_id")
    candidates = source.get("candidates_requiring_decision")
    if not isinstance(requested_by_user_guid, str) or not requested_by_user_guid or not isinstance(role_id, str) or not role_id or not isinstance(candidates, list):
        raise ValueError("Preflight input requires a completed discovery result")
    if not candidates:
        return {"stage": "preflight", "status": "completed_no_change_required", "requested_by_user_guid": requested_by_user_guid, "role_id": role_id, "role_code": str(source.get("role_code") or ROLE_CODE), "assignments_ready_for_confirmation": [], "exceptions": []}
    missing = [str(candidate["user_guid"]) for candidate in candidates if isinstance(candidate, dict) and isinstance(candidate.get("user_guid"), str) and f"user:{candidate['user_guid']}" not in responses]
    output: dict[str, Any] = {"stage": "preflight", "requested_by_user_guid": requested_by_user_guid, "role_id": role_id, "role_code": str(source.get("role_code") or ROLE_CODE), "needs_role_membership": "role_members" not in responses, "needs_user_lookups": sorted(set(missing)), "exceptions": [], "assignments_ready_for_confirmation": []}
    if output["needs_role_membership"] or missing:
        output["status"] = "awaiting_core_results"
        return output
    members = role_members(responses["role_members"])
    assignments = []
    for candidate in candidates:
        if not isinstance(candidate, dict) or not isinstance(candidate.get("user_guid"), str):
            output["exceptions"].append({"classification": "invalid_candidate"})
            continue
        user_id = str(candidate["user_guid"])
        user = exactly_one(responses[f"user:{user_id}"], f"user:{user_id}")
        if user is None or user.get("active") is not True:
            output["exceptions"].append({"classification": "inactive_or_unresolved_target", "username": candidate.get("username", "Unknown user")})
        elif user_id in members:
            output["exceptions"].append({"classification": "already_risk_power_user", "username": candidate.get("username", "Unknown user")})
        else:
            assignments.append({"user_guid": user_id, "username": candidate.get("username", "Unknown user"), "display_name": candidate.get("display_name", candidate.get("username", "Unknown user")), "processes": candidate.get("processes", [])})
    output["needs_role_membership"] = False
    output["needs_user_lookups"] = []
    output["assignments_ready_for_confirmation"] = assignments
    output["status"] = "awaiting_final_approval" if assignments else "completed_no_change_required"
    return output


def state_name(item: dict[str, Any]) -> str | None:
    for key in ("status", "Status", "requestStatus", "RequestStatus", "approvalStatus", "ApprovalStatus"):
        if item.get(key) is not None:
            return str(item[key]).upper()
    return None


def utc_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"Polling input requires {field} as an ISO-8601 UTC timestamp")
    normalized = f"{value[:-1]}+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"Polling input requires {field} as an ISO-8601 UTC timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"Polling input requires {field} with an explicit UTC offset")
    return parsed.astimezone(timezone.utc)


def positive_seconds(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"Polling input requires {field} as a positive integer")
    return value


def poll(source: dict[str, Any], responses: dict[str, Any]) -> dict[str, Any]:
    executions = source.get("executions")
    if not isinstance(executions, list) or not isinstance(source.get("role_id"), str):
        raise ValueError("Polling input requires role_id and submitted executions with AAR IDs")
    started_at = utc_timestamp(source.get("poll_started_at"), "poll_started_at")
    observed_at = utc_timestamp(source.get("observed_at"), "observed_at")
    if observed_at < started_at:
        raise ValueError("Polling input observed_at cannot be earlier than poll_started_at")
    poll_interval = positive_seconds(source.get("poll_interval_seconds"), "poll_interval_seconds")
    max_wait = positive_seconds(source.get("max_poll_wait_seconds"), "max_poll_wait_seconds")
    if max_wait < poll_interval:
        raise ValueError("Polling input max_poll_wait_seconds must be at least poll_interval_seconds")
    elapsed_wait = int((observed_at - started_at).total_seconds())
    output: dict[str, Any] = {
        "stage": "poll",
        "role_id": source["role_id"],
        "executions": [],
        "pending_aar_ids": [],
        "timed_out_aar_ids": [],
        "elapsed_wait_seconds": elapsed_wait,
        "max_poll_wait_seconds": max_wait,
        "next_check_after_seconds": None,
        "timed_out": False,
        "needs_role_membership": False,
        "exceptions": list(source.get("exceptions", [])) if isinstance(source.get("exceptions"), list) else [],
    }
    for execution in executions:
        if not isinstance(execution, dict) or not execution.get("aar_id"):
            output["exceptions"].append({"classification": "missing_aar_id"})
            continue
        result = dict(execution)
        response_id = f"poll:{result['aar_id']}"
        if response_id not in responses:
            output["pending_aar_ids"].append(str(result["aar_id"]))
            output["executions"].append(result)
            continue
        matches = [item for item in rows(responses[response_id], response_id) if str(item.get("AccessRequestId")) == str(result["aar_id"])]
        if len(matches) != 1:
            output["exceptions"].append({"classification": "aar_status_unresolved", "aar_id": result["aar_id"]})
        else:
            result["aar_state"] = state_name(matches[0])
            if result["aar_state"] not in TERMINAL_AAR_STATES:
                output["pending_aar_ids"].append(str(result["aar_id"]))
        output["executions"].append(result)
    if output["pending_aar_ids"]:
        if elapsed_wait >= max_wait:
            output["timed_out"] = True
            output["timed_out_aar_ids"] = list(output["pending_aar_ids"])
            output["timeout"] = {
                "failure_class": "process_timeout",
                "operation": "Advanced Access Request status polling",
                "aar_ids": list(output["pending_aar_ids"]),
                "last_statuses": [
                    {
                        "aar_id": item.get("aar_id"),
                        "last_status": item.get("aar_state", "UNKNOWN"),
                    }
                    for item in output["executions"]
                    if item.get("aar_id") in output["pending_aar_ids"]
                ],
                "elapsed_wait_seconds": elapsed_wait,
                "max_poll_wait_seconds": max_wait,
                "recommended_action": "Persist the timeout diagnostic and obtain a fresh customer decision before another status check.",
            }
        else:
            output["next_check_after_seconds"] = poll_interval
    else:
        output["needs_role_membership"] = True
    return output


def verify(source: dict[str, Any], responses: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(source.get("role_id"), str) or not isinstance(source.get("executions"), list):
        raise ValueError("Verification input requires role_id and completed polling state")
    members = role_members(responses["role_members"])
    exceptions = list(source.get("exceptions", [])) if isinstance(source.get("exceptions"), list) else []
    outcomes = []
    for execution in source["executions"]:
        if not isinstance(execution, dict):
            continue
        status = str(execution.get("aar_state") or "UNKNOWN")
        outcome = "verified" if status in SUCCESSFUL_AAR_STATES and str(execution.get("user_guid")) in members else "membership_not_verified" if status in SUCCESSFUL_AAR_STATES else "access_request_not_approved"
        outcomes.append({"user_guid": execution.get("user_guid"), "username": execution.get("username", "Unknown user"), "display_name": execution.get("display_name", execution.get("username", "Unknown user")), "processes": execution.get("processes", []), "aar_state": status, "outcome": outcome})
        if outcome != "verified":
            exceptions.append({"classification": outcome, "username": execution.get("username", "Unknown user")})
    return {"stage": "verify", "role_code": str(source.get("role_code") or ROLE_CODE), "executions": outcomes, "exceptions": exceptions, "summary": {"verified": sum(outcome["outcome"] == "verified" for outcome in outcomes), "exceptions": len(exceptions)}}


def continuation(source: dict[str, Any], responses: dict[str, Any]) -> dict[str, Any]:
    """Recheck unfinished people after a verified approval batch.

    ``remaining_candidates`` holds people not selected in the prior approval.
    A person whose selected request was not verified is also returned to the
    decision set; a previous approval never authorizes a retry.
    """

    requested_by_user_guid, role_id = source.get("requested_by_user_guid"), source.get("role_id")
    remaining = source.get("remaining_candidates")
    executions = source.get("verification_executions")
    decision = source.get("consultant_decision")
    if not isinstance(requested_by_user_guid, str) or not requested_by_user_guid or not isinstance(role_id, str) or not role_id:
        raise ValueError("Continuation input requires requested_by_user_guid and role_id")
    if not isinstance(remaining, list) or not isinstance(executions, list):
        raise ValueError("Continuation input requires remaining_candidates and verification_executions")
    if decision not in (None, "SKIP_REMAINING_AND_PROCEED"):
        raise ValueError("Continuation consultant_decision must be SKIP_REMAINING_AND_PROCEED when supplied")

    candidates_by_user: dict[str, dict[str, Any]] = {}
    for candidate in remaining:
        if not isinstance(candidate, dict) or not isinstance(candidate.get("user_guid"), str) or not candidate["user_guid"]:
            continue
        candidates_by_user[str(candidate["user_guid"])] = dict(candidate)

    verified = []
    for execution in executions:
        if not isinstance(execution, dict):
            continue
        user_guid = execution.get("user_guid")
        if not isinstance(user_guid, str) or not user_guid:
            continue
        if execution.get("outcome") == "verified":
            verified.append(dict(execution))
            continue
        retry_candidate = {
            "user_guid": user_guid,
            "username": execution.get("username", "Unknown user"),
            "display_name": execution.get("display_name", execution.get("username", "Unknown user")),
            "processes": execution.get("processes", []),
            "requires_fresh_approval": True,
        }
        candidates_by_user[user_guid] = retry_candidate

    candidates = list(candidates_by_user.values())
    output: dict[str, Any] = {
        "stage": "continuation",
        "requested_by_user_guid": requested_by_user_guid,
        "role_id": role_id,
        "role_code": str(source.get("role_code") or ROLE_CODE),
        "verified": verified,
        "remaining_pending_decision": [],
        "resolved_without_change": [],
        "requires_explicit_skip": [],
        "skipped_by_explicit_consultant_decision": [],
        "exceptions": list(source.get("exceptions", [])) if isinstance(source.get("exceptions"), list) else [],
        "needs_role_membership": "role_members" not in responses,
        "needs_user_lookups": sorted(user_guid for user_guid in candidates_by_user if f"user:{user_guid}" not in responses),
    }
    if output["needs_role_membership"] or output["needs_user_lookups"]:
        output["status"] = "awaiting_core_results"
        return output

    members = role_members(responses["role_members"])
    for candidate in candidates:
        user_guid = str(candidate["user_guid"])
        user = exactly_one(responses[f"user:{user_guid}"], f"user:{user_guid}")
        if user is None or not user.get("id"):
            result = dict(candidate)
            result["current_result"] = "Access eligibility needs attention"
            output["requires_explicit_skip"].append(result)
            output["exceptions"].append({"classification": "owner_identity_unresolved", "username": candidate.get("username", "Unknown user")})
        elif user.get("active") is not True:
            result = dict(candidate)
            result["current_result"] = "Person is not eligible for access"
            output["requires_explicit_skip"].append(result)
            output["exceptions"].append({"classification": "inactive_or_unresolved_target", "username": candidate.get("username", "Unknown user")})
        elif user_guid in members:
            output["resolved_without_change"].append({
                "user_guid": user_guid,
                "username": candidate.get("username", user.get("userName", "Unknown user")),
                "display_name": candidate.get("display_name", user.get("displayName", user.get("userName", "Unknown user"))),
                "processes": candidate.get("processes", []),
            })
        else:
            result = dict(candidate)
            result["current_result"] = "A new approval is required" if candidate.get("requires_fresh_approval") else "Access not assigned"
            output["remaining_pending_decision"].append(result)

    if decision == "SKIP_REMAINING_AND_PROCEED":
        output["skipped_by_explicit_consultant_decision"] = [
            *output["remaining_pending_decision"],
            *output["requires_explicit_skip"],
        ]
        output["remaining_pending_decision"] = []
        output["requires_explicit_skip"] = []
        output["status"] = "partial_deferred_by_consultant"
    elif output["remaining_pending_decision"] or output["requires_explicit_skip"]:
        output["status"] = "awaiting_remaining_decision"
    else:
        output["status"] = "completed_all_resolved"
    return output


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    divider = ["---"] * len(headers)
    return "\n".join(
        ["| " + " | ".join(headers) + " |", "| " + " | ".join(divider) + " |"]
        + ["| " + " | ".join(row) + " |" for row in rows]
    )


def process_names(value: Any) -> str:
    if not isinstance(value, list) or not value:
        return "Not specified"
    names = [str(item.get("process") or "Not specified") for item in value if isinstance(item, dict)]
    return ", ".join(names) if names else "Not specified"


def consultant_status(stage: str, output: dict[str, Any]) -> str:
    """Return the table-first result intended for an implementation consultant."""

    if stage in {"discovery", "preflight"}:
        candidates = output.get("candidates_requiring_decision") if stage == "discovery" else output.get("assignments_ready_for_confirmation")
        if isinstance(candidates, list) and candidates:
            rows = [
                [str(candidate.get("display_name") or candidate.get("username") or "Unknown person"), process_names(candidate.get("processes")), "Ready for approval"]
                for candidate in candidates
                if isinstance(candidate, dict)
            ]
            return "\n".join(["Risk Power User access review", "", markdown_table(["Person", "Affected process", "Approval"], rows), "", "Next action: confirm the selected people to request access."])
        return "\n".join(["Risk Power User access review", "", markdown_table(["Current result", "Business impact", "Next action"], [["No additional access is needed", "Current eligible owners already have the required access or no eligible owner was found.", "No approval is required."]])])

    if stage == "poll":
        result = "Access is still being processed" if output.get("pending_aar_ids") else "Access processing is complete"
        action = "Wait for the next scheduled check." if output.get("pending_aar_ids") and not output.get("timed_out") else "Review the final access result." if not output.get("timed_out") else "Review the affected people before deciding whether to request access again."
        return "\n".join(["Risk Power User access status", "", markdown_table(["Current result", "Next action"], [[result, action]])])

    if stage == "continuation":
        verified = output.get("verified") if isinstance(output.get("verified"), list) else []
        pending = output.get("remaining_pending_decision") if isinstance(output.get("remaining_pending_decision"), list) else []
        attention = output.get("requires_explicit_skip") if isinstance(output.get("requires_explicit_skip"), list) else []
        skipped = output.get("skipped_by_explicit_consultant_decision") if isinstance(output.get("skipped_by_explicit_consultant_decision"), list) else []
        lines = ["Risk Power User access update", ""]
        if verified:
            lines.extend([markdown_table(
                ["Person", "Affected process", "Current result"],
                [[str(item.get("display_name") or item.get("username") or "Unknown person"), process_names(item.get("processes")), "Access confirmed"] for item in verified if isinstance(item, dict)],
            ), ""])
        if pending or attention:
            decision_rows = [
                [str(item.get("display_name") or item.get("username") or "Unknown person"), process_names(item.get("processes")), str(item.get("current_result") or "Access not assigned"), "Assign Risk Power User access"]
                for item in pending
                if isinstance(item, dict)
            ] + [
                [str(item.get("display_name") or item.get("username") or "Unknown person"), process_names(item.get("processes")), str(item.get("current_result") or "Access needs attention"), "Skip and proceed"]
                for item in attention
                if isinstance(item, dict)
            ]
            lines.extend([
                markdown_table(["Person", "Affected process", "Current result", "Approval or next action"], decision_rows),
                "",
                "Do you want to assign Risk Power User access to any of these remaining people, or skip the remaining assignments and proceed with the next task? If you proceed, this task will be recorded as complete with the listed assignments skipped.",
                "",
                "For example, reply with the people to assign, “assign all remaining,” or an unambiguous request to proceed with the next task.",
            ])
            return "\n".join(lines)
        if skipped:
            lines.extend([markdown_table(
                ["Person", "Affected process", "Current result"],
                [[str(item.get("display_name") or item.get("username") or "Unknown person"), process_names(item.get("processes")), "Not assigned by consultant decision"] for item in skipped if isinstance(item, dict)],
            ), "", "Next action: proceed with the next eligible task in the runbook."])
            return "\n".join(lines)
        lines.extend([markdown_table(["Current result", "Next action"], [["All eligible owners have the required access", "No further access decisions are required."]])])
        return "\n".join(lines)

    outcomes = output.get("executions")
    labels = {"verified": "Access confirmed", "access_request_not_approved": "Access not approved", "membership_not_verified": "Access needs attention"}
    rows = [
        [str(item.get("display_name") or item.get("username") or "Unknown person"), process_names(item.get("processes")), labels.get(str(item.get("outcome")), "Access needs attention")]
        for item in outcomes
        if isinstance(item, dict)
    ] if isinstance(outcomes, list) else []
    if not rows:
        rows = [["No affected person", "Not specified", "No access change was confirmed"]]
    return "\n".join(["Risk Power User access completion", "", markdown_table(["Person", "Affected process", "Current result"], rows), "", "Next action: review any item that needs attention before making another request."])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("discovery", "preflight", "poll", "verify", "continuation"), required=True)
    parser.add_argument("--input", required=True, help="JSON object containing only stage input")
    parser.add_argument("--response", action="append", default=[], help="Returned Core response as response_id=path; repeat as needed")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = read_json(Path(args.input))
    responses = payload.pop("responses", {})
    if not isinstance(responses, dict):
        raise ValueError("input responses must be an object when supplied")
    for specification in args.response:
        response_id, separator, response_path = specification.partition("=")
        if not separator or not response_id or not response_path or response_id in responses:
            raise ValueError("--response must be a unique response_id=path")
        responses[response_id] = read_json(Path(response_path))
    transforms = {"discovery": discovery, "preflight": preflight, "poll": poll, "verify": verify, "continuation": continuation}
    output = transforms[args.stage](payload, responses)
    write_json(Path(args.output), output)
    if args.stage in {"discovery", "preflight"} and output.get("status") not in {"blocked", "awaiting_core_results"} and "role_members" in responses:
        if not role_members(responses["role_members"]):
            print("No people are currently assigned to the Risk Power User role.\n")
    print(consultant_status(args.stage, output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
