"""Deterministic customer-facing presentation for the Fusion ABO workflow.

The presentation contract is task-local. It is validated here instead of in
the repository schemas, and it never participates in an execution fingerprint
or mutation payload.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


PRESENTATION_SCHEMA_VERSION = "1.0"
OPT_INS = (
    ("ORA_FOM_ASSET_BASED_ORDERING", "Asset-Based Ordering"),
    ("ORA_ENABLE_UNIFIED_ORACLE_CPQ_IN_FUSION", "Unified Oracle CPQ in Fusion"),
    ("ORA_FOM_OSS_INTEGRATION_SUBSCRIPTIONS", "Order Management Subscription Integration"),
    ("ORA_FOM_OSS_INTEGRATION_COVERAGES", "Order Management Coverage Integration"),
)
OPT_IN_NAMES = dict(OPT_INS)
OPT_IN_STATUS_VALUES = {
    "enabled", "disabled", "not_checked", "verification_failed", "inconsistent",
    "previously_verified",
}
PREREQUISITE_STATUSES = {
    "requires_cpq_abo_prerequisite_update",
    "requires_subscription_coverage_prerequisite_update",
    "requires_prerequisite_update",
}
PREREQUISITE_STAGES = {
    "cpq_abo_optin_handoff",
    "subscription_coverage_optin_handoff",
    "requires_cpq_abo_prerequisite_update",
    "requires_subscription_coverage_prerequisite_update",
}
SAFE_CPQ_SETTING_LABELS = {
    "commerceProcessVarNameForEnabledFusionABO": "Fusion ABO process",
    "enableFusionABO": "Enable Fusion ABO",
    "defineFieldsForModifyActionFunction": "ABO delta-action Library Function",
}
INITIALIZATION_ENTITIES = ["Account", "Contact", "Lead", "Opportunity", "Revenue", "Activity", "Asset", "Product", "CRMProductGroup"]


class AboPresentationError(ValueError):
    """Raised when a customer presentation cannot be built safely."""


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    return value if isinstance(value, list) else ()


def _value(payload: Mapping[str, Any], *keys: str, default: str = "Not available") -> str:
    for key in keys:
        value = payload.get(key)
        if value is not None and str(value).strip():
            return str(value)
    return default


def _status_and_stage(payload: Mapping[str, Any]) -> tuple[str, str]:
    return (
        _value(payload, "workflow_status", "status", default=""),
        _value(payload, "stage", default=""),
    )


def _feature_states(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    for candidate in (
        payload,
        _mapping(payload.get("presentation_context")),
        _mapping(payload.get("approval_context")),
        _mapping(payload.get("preflight")),
        _mapping(payload.get("fusion_abo_preflight")),
        _mapping(payload.get("result")),
    ):
        states = candidate.get("feature_states")
        if isinstance(states, Mapping):
            return states
    return {}


def _target(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    for candidate in (
        payload,
        _mapping(payload.get("workflow_preview")),
        _mapping(payload.get("presentation_context")),
        _mapping(payload.get("preflight")),
        _mapping(payload.get("approval_context")),
        _mapping(payload.get("approval_required")),
    ):
        target = candidate.get("target")
        if isinstance(target, Mapping):
            return target
    return {}


def _process(payload: Mapping[str, Any]) -> str:
    for candidate in (
        payload,
        _mapping(payload.get("presentation_context")),
        _mapping(payload.get("approval_context")),
        _mapping(payload.get("cpq_preflight")),
        _mapping(payload.get("preflight")),
        _mapping(payload.get("workflow_preview")),
    ):
        value = candidate.get("validated_process_variable_name")
        if value:
            return str(value)
        selection = _mapping(candidate.get("process_selection"))
        if selection.get("resolved_process_variable_name"):
            return str(selection["resolved_process_variable_name"])
    return "Not available"


def _handoffs(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [
        item
        for item in _sequence(payload.get("prerequisite_handoffs"))
        if isinstance(item, Mapping)
    ]


def _eligible_handoff(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    by_code = {
        str(item.get("feature_code")): item
        for item in _handoffs(payload)
        if item.get("feature_code")
    }
    for code, _ in OPT_INS:
        if code in by_code:
            return by_code[code]
    return {}


def _operation(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(payload.get("operation"))


def _is_prerequisite_handoff(payload: Mapping[str, Any]) -> bool:
    status, stage = _status_and_stage(payload)
    return status in PREREQUISITE_STATUSES or stage in PREREQUISITE_STAGES


def _is_prerequisite_approval(payload: Mapping[str, Any]) -> bool:
    operation = _operation(payload)
    return (
        _value(payload, "status", default="") == "approval_required"
        and bool(operation.get("feature_code"))
        and bool(operation.get("feature_choice"))
    )


def _opt_in_rows(payload: Mapping[str, Any]) -> list[dict[str, str]]:
    states = _feature_states(payload)
    prior_verification = (
        _mapping(payload.get("presentation_context")).get("prerequisites_verified_before_cpq")
        is True
    )
    status, _ = _status_and_stage(payload)
    failed_without_evidence = (
        status in {
            "failed",
            "prerequisite_update_verification_blocked",
            "prerequisite_update_final_preflight_blocked",
        }
        and not states
    )
    rows: list[dict[str, str]] = []
    for code, name in OPT_INS:
        value = states.get(code)
        if value is True:
            state = "enabled"
            detail = "Verified enabled by the current feature-state evidence."
        elif value is False:
            state = "disabled"
            detail = "Must be enabled before the workflow can continue."
        elif prior_verification:
            state = "previously_verified"
            detail = "Verified before CPQ execution; the earlier individual readings are unavailable."
        elif failed_without_evidence:
            state = "verification_failed"
            detail = "The current status could not be verified safely."
        else:
            state = "not_checked"
            detail = "Not checked yet because the current prerequisite stage must complete first."
        rows.append({"code": code, "name": name, "status": state, "detail": detail})
    return rows


def _cpq_settings(payload: Mapping[str, Any]) -> list[dict[str, str]]:
    cpq = _mapping(_mapping(payload.get("components")).get("cpq_settings"))
    for operation in _sequence(cpq.get("operations")):
        if not isinstance(operation, Mapping) or operation.get("id") not in {
            "configure_fusion_abo_settings", "configure_abo_delta_action_library_function"
        }:
            continue
        safe = []
        settings = (
            [operation.get("setting")]
            if operation.get("id") == "configure_abo_delta_action_library_function"
            else _sequence(operation.get("settings"))
        )
        for setting in settings:
            if not isinstance(setting, Mapping):
                continue
            key = setting.get("key")
            if key in SAFE_CPQ_SETTING_LABELS and setting.get("value") is not None:
                safe.append(
                    {"name": SAFE_CPQ_SETTING_LABELS[str(key)], "value": str(setting["value"])}
                )
        return safe
    return []


def _sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def _cpq_recovery_current_value(payload: Mapping[str, Any]) -> str | None:
    context = _mapping(payload.get("presentation_context"))
    if "cpq_function_recovery_current_value" in context:
        value = context["cpq_function_recovery_current_value"]
    else:
        preflight = _mapping(payload.get("cpq_preflight"))
        function = _mapping(preflight.get("abo_delta_action_library_function"))
        if "configured_function" not in function:
            return None
        value = function["configured_function"]
    return "Not configured" if value is None or value == "" else str(value)


def _has_adaptive_preview(payload: Mapping[str, Any]) -> bool:
    approval = _mapping(payload.get("approval_required"))
    preview = _mapping(approval.get("preview"))
    final_data = _mapping(preview.get("finalData"))
    target = _mapping(approval.get("target"))
    return (
        approval.get("stage") == "adaptive_search"
        and bool(target.get("environment"))
        and _sha256(approval.get("preview_sha256"))
        and _sha256(final_data.get("archiveSha256"))
        and _sha256(final_data.get("sourceSha256"))
        and final_data.get("target") == target
        and final_data.get("entities") == ["ConsolidatedAsset", "SerializedAsset"]
        and final_data.get("publishType") == "selective"
        and approval.get("entities") == ["ConsolidatedAsset", "SerializedAsset"]
        and approval.get("publish_type") == "selective"
    )


def _has_ess_payload(payload: Mapping[str, Any]) -> bool:
    approval = _mapping(payload.get("approval_required"))
    ess = _mapping(approval.get("payload"))
    target = _mapping(approval.get("target"))
    return (
        approval.get("stage") == "ess"
        and bool(target.get("environment"))
        and _sha256(approval.get("payload_sha256"))
        and ess.get("jobDefinitionId") == "JobDefinition://oracle/apps/ess/configPriceQuote/assets/UnifiedAssetReadModelSyncMasterJob"
        and ess.get("application") == "CrmEss"
        and ess.get("product") == "CPQ"
        and ess.get("requestParameters") == []
        and isinstance(ess.get("description"), str)
        and bool(ess["description"].strip())
    )


def _has_cpq_preview(payload: Mapping[str, Any]) -> bool:
    cpq = _mapping(_mapping(payload.get("components")).get("cpq_settings"))
    loads = _mapping(cpq.get("data_loader_loads"))
    target = _mapping(payload.get("target"))
    mutations = [
        operation for operation in _sequence(cpq.get("operations"))
        if isinstance(operation, Mapping) and operation.get("id") in {
            "configure_fusion_abo_settings", "configure_abo_delta_action_library_function"
        }
    ]
    if len(mutations) != 1 or not target.get("environment"):
        return False
    mutation = mutations[0]
    recovery = mutation["id"] == "configure_abo_delta_action_library_function"
    settings = _cpq_settings(payload)
    expected = (
        [{"name": SAFE_CPQ_SETTING_LABELS["defineFieldsForModifyActionFunction"],
          "value": "_s_getAttributesForABODeltaActionCalculation"}]
        if recovery else [
            {"name": SAFE_CPQ_SETTING_LABELS["commerceProcessVarNameForEnabledFusionABO"],
             "value": _process(payload)},
            {"name": SAFE_CPQ_SETTING_LABELS["enableFusionABO"], "value": "Yes"},
            {"name": SAFE_CPQ_SETTING_LABELS["defineFieldsForModifyActionFunction"],
             "value": "_s_getAttributesForABODeltaActionCalculation"},
        ]
    )
    if settings != expected or (recovery and _cpq_recovery_current_value(payload) is None):
        return False
    if set(loads) != {mutation["id"]}:
        return False
    load = _mapping(loads[mutation["id"]])
    final_data = _mapping(_mapping(load.get("task_hook_preview")).get("finalData"))
    immutable = _mapping(load.get("immutable_source"))
    subject = _mapping(load.get("approved_subject"))
    return (
        _sha256(load.get("task_hook_preview_sha256"))
        and _sha256(final_data.get("archiveSha256"))
        and _sha256(final_data.get("sourceSha256"))
        and final_data.get("archiveSha256") == immutable.get("archive_sha256")
        and final_data.get("sourceSha256") == immutable.get("source_sha256")
        and final_data.get("target") == target
        and final_data.get("approvedSubject") == subject
        and subject.get("business_object") == "CpqCommerceSettings"
    )


def _has_cpq_preparation_proposal(payload: Mapping[str, Any]) -> bool:
    """Business-plan approval only; never require a generated Core source."""
    approval = _mapping(payload.get("approval_required"))
    proposal = _mapping(approval.get("proposal"))
    target = _target(payload)
    plan = _mapping(proposal.get("business_plan"))
    operations = _sequence(plan.get("operations"))
    cpq = _mapping(_mapping(payload.get("components")).get("cpq_settings"))
    if (approval.get("stage") != "cpq_preparation" or proposal.get("purpose") != "cpq_preparation_only"
            or proposal.get("target") != target or approval.get("target") != target
            or not target.get("environment") or not _sha256(approval.get("proposal_sha256"))
            or any(_feature_states(payload).get(code) is not True for code, _ in OPT_INS)
            or not proposal.get("project_id") or proposal.get("project_id") != payload.get("project_id")
            or proposal.get("workflow_id") != payload.get("workflow_id")
            or operations != _sequence(cpq.get("operations"))
            or plan.get("validated_process_variable_name") != _process(payload)):
        return False
    digest = hashlib.sha256(json.dumps(dict(proposal), sort_keys=True, separators=(",", ":"),
                                       ensure_ascii=True).encode()).hexdigest()
    if digest != approval["proposal_sha256"]:
        return False
    mutations = [item for item in operations if isinstance(item, Mapping) and item.get("id") in {
        "configure_fusion_abo_settings", "configure_abo_delta_action_library_function"}]
    if len(mutations) != 1:
        return False
    expected = [{"name": SAFE_CPQ_SETTING_LABELS["defineFieldsForModifyActionFunction"],
                 "value": "_s_getAttributesForABODeltaActionCalculation"}]
    if mutations[0]["id"] == "configure_fusion_abo_settings":
        expected = [{"name": SAFE_CPQ_SETTING_LABELS["commerceProcessVarNameForEnabledFusionABO"],
                     "value": _process(payload)},
                    {"name": SAFE_CPQ_SETTING_LABELS["enableFusionABO"], "value": "Yes"}, *expected]
    elif _cpq_recovery_current_value(payload) is None:
        return False
    return _cpq_settings(payload) == expected


def _approval_scope(payload: Mapping[str, Any], stage: str) -> list[dict[str, str]]:
    approval = _mapping(payload.get("approval_required"))
    if stage == "adaptive_initialization" and _has_initialization_proposal(payload):
        return [{"name": "Operation", "value": "Prepare initial Adaptive Search Full Publish"},
                {"name": "Publish type", "value": "Full"},
                {"name": "Entities", "value": ", ".join(INITIALIZATION_ENTITIES)}]
    if stage == "adaptive_preparation" and _has_adaptive_preparation_proposal(payload):
        return [{"name": "Operation", "value": "Prepare Adaptive Search Partial Publish"},
                {"name": "Publish type", "value": "Selective"},
                {"name": "Entities", "value": "ConsolidatedAsset, SerializedAsset"}]
    if stage == "cpq":
        return ([{"name": "Prepared import", "value": "CpqCommerceSettings Task Hook preview"}]
                if _has_cpq_preview(payload) else [])
    if stage == "adaptive_search" and _has_adaptive_preview(payload):
        return [
            {"name": "Prepared publish", "value": "Adaptive Search Task Hook preview"},
            {"name": "Publish type", "value": "Selective"},
            {"name": "Entities", "value": "ConsolidatedAsset, SerializedAsset"},
        ]
    if stage == "ess" and _has_ess_payload(payload):
        ess = _mapping(approval.get("payload"))
        fields = (
            ("Job definition", "jobDefinitionId"),
            ("Application", "application"),
            ("Product", "product"),
            ("Description", "description"),
        )
        rows = [{"name": label, "value": str(ess[key])} for label, key in fields
                if isinstance(ess.get(key), str) and ess[key]]
        if ess.get("requestParameters") == []:
            rows.append({"name": "Request parameters", "value": "None"})
        return rows
    return []


def _has_initialization_proposal(payload: Mapping[str, Any]) -> bool:
    blocker = _mapping(payload.get("initialization_blocker"))
    return (blocker.get("reason") in {"missing_metamodel", "empty_catalog"}
            and _has_adaptive_preparation_proposal(payload, initialization=True))


def _has_adaptive_preparation_proposal(payload: Mapping[str, Any], *, initialization=False) -> bool:
    approval = _mapping(payload.get("approval_required"))
    proposal = _mapping(approval.get("proposal"))
    if (approval.get("stage") != ("adaptive_initialization" if initialization else "adaptive_preparation")
            or proposal.get("purpose") != ("adaptive_initialization_preparation_only" if initialization else "adaptive_preparation_only")
            or not _mapping(payload.get("target"))
            or proposal.get("target") != payload.get("target") or approval.get("target") != payload.get("target")
            or not proposal.get("project_id") or proposal.get("project_id") != payload.get("project_id")
            or proposal.get("workflow_id") != payload.get("workflow_id")
            or proposal.get("cpq_process") != _process(payload)
            or proposal.get("entities") != (INITIALIZATION_ENTITIES if initialization else ["ConsolidatedAsset", "SerializedAsset"])
            or proposal.get("publish_type") != ("full" if initialization else "selective") or not _mapping(proposal.get("cpq_completion"))
            or not _sha256(approval.get("proposal_sha256"))):
        return False
    return hashlib.sha256(json.dumps(dict(proposal), sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=True).encode()).hexdigest() == approval["proposal_sha256"]


def _stage_rows(
    payload: Mapping[str, Any], opt_ins: Sequence[Mapping[str, str]]
) -> list[dict[str, str]]:
    status, stage = _status_and_stage(payload)
    all_enabled = all(item["status"] == "enabled" for item in opt_ins)
    any_disabled = any(item["status"] == "disabled" for item in opt_ins)
    if stage == "adaptive_initialization":
        return [
            {"name": "Fusion prerequisite opt-ins", "status": "Previously verified" if all_enabled else "See prerequisite evidence"},
            {"name": "CPQ Commerce Settings", "status": "Verified before preparation"},
            {"name": "Adaptive Search partial publish", "status": "Waiting for initial Full Publish: ready for preparation approval" if _has_initialization_proposal(payload) else "Waiting for initial Full Publish completion"},
            {"name": "Unified Asset Read Model Sync", "status": "Waiting for final Partial Publish readiness"},
        ]
    if stage == "adaptive_preparation":
        return [
            {"name": "Fusion prerequisite opt-ins", "status": "Previously verified" if all_enabled else "See prerequisite evidence"},
            {"name": "CPQ Commerce Settings", "status": "Verified before preparation"},
            {"name": "Adaptive Search partial publish", "status": "Ready for preparation approval" if _has_adaptive_preparation_proposal(payload) else "Preparation stopped"},
            {"name": "Unified Asset Read Model Sync", "status": "Waiting for final Adaptive Search readiness"},
        ]
    if payload.get("handover_version") == "2.0" and stage in {"cpq_data_loader", "adaptive_data_loader", "cpq_verification", "recovery"}:
        cpq_pending = stage == "cpq_data_loader"
        uncertain = status in {"cpq_indeterminate", "adaptive_search_indeterminate"} or stage == "recovery"
        return [
            {"name": "Fusion prerequisite opt-ins", "status": "Previously verified" if all_enabled else "See prerequisite evidence"},
            {"name": "CPQ Commerce Settings", "status": "Completion not verified" if cpq_pending else "Verified" if not uncertain else "Reconciliation required"},
            {"name": "Adaptive Search partial publish", "status": "Completion not verified" if stage == "adaptive_data_loader" else "Waiting for verified CPQ completion" if cpq_pending else "Not yet completed"},
            {"name": "Unified Asset Read Model Sync", "status": "Waiting for final Adaptive Search readiness"},
        ]
    if status == "awaiting_cpq_preparation_approval":
        return [
            {"name": "Fusion prerequisite opt-ins", "status": "Verified" if all_enabled else "Verification incomplete"},
            {"name": "CPQ Commerce Settings", "status": "Ready for preparation approval" if _has_cpq_preparation_proposal(payload) else "Proposal needs correction"},
            {"name": "Adaptive Search partial publish", "status": "Waiting for verified CPQ completion"},
            {"name": "Unified Asset Read Model Sync", "status": "Waiting for final Adaptive Search readiness"},
        ]
    if status in {"completed", "COMPLETED"}:
        return [
            {"name": "Fusion prerequisite opt-ins", "status": "Completed"},
            {"name": "CPQ Commerce Settings", "status": "Completed"},
            {"name": "Adaptive Search partial publish", "status": "Completed"},
            {"name": "Unified Asset Read Model Sync", "status": "Completed"},
        ]
    if _is_prerequisite_handoff(payload) or _is_prerequisite_approval(payload) or any_disabled:
        fusion_status = "Ready for approval" if _is_prerequisite_approval(payload) else "Action required"
        return [
            {"name": "Fusion prerequisite opt-ins", "status": fusion_status},
            {"name": "CPQ Commerce Settings", "status": "Blocked by Fusion prerequisites"},
            {"name": "Adaptive Search partial publish", "status": "Waiting for CPQ completion"},
            {"name": "Unified Asset Read Model Sync", "status": "Waiting for Adaptive Search completion"},
        ]
    fusion_status = "Completed" if all_enabled else "Verification pending"
    if status == "requires_process_selection":
        cpq_status, adaptive_status, ess_status = (
            "Awaiting process selection", "Waiting for CPQ completion", "Waiting for Adaptive Search completion"
        )
    elif status == "already_configured":
        cpq_status, adaptive_status, ess_status = "Already configured", "Not evaluated", "Not evaluated"
    elif status == "requires_abo_delta_action_library_function_recovery":
        cpq_status, adaptive_status, ess_status = (
            "Function recovery preview needed", "Waiting for CPQ recovery", "Waiting for Adaptive Search completion"
        )
    elif status in {
        "awaiting_adaptive_monitoring_choice", "adaptive_search_manual", "adaptive_search_monitoring",
        "ess_pending_or_failed", "adaptive_search_monitoring_timeout", "monitoring_timeout",
        "adaptive_search_failed", "adaptive_search_indeterminate",
        "waiting_for_adaptive_search_publish", "adaptive_search_not_eligible_for_ess",
        "adaptive_search_succeeded_ess_submission_required",
    }:
        cpq_status = "Completed"
        adaptive_status = (
            "Completed" if status in {"ess_pending_or_failed", "adaptive_search_succeeded_ess_submission_required"} else
            "Failed or indeterminate" if status in {"adaptive_search_failed", "adaptive_search_indeterminate", "adaptive_search_not_eligible_for_ess"}
            else "Monitoring pending"
        )
        ess_status = (
            "Pending or failed" if status == "ess_pending_or_failed" else
            "Approval preparation required" if status == "adaptive_search_succeeded_ess_submission_required"
            else "Waiting for Adaptive Search completion"
        )
    elif status == "blocked_before_adaptive_search_publish":
        cpq_status, adaptive_status, ess_status = (
            "Reconciliation required", "Blocked by CPQ result", "Waiting for Adaptive Search completion"
        )
    elif status == "indeterminate" and stage == "cpq_settings_write_execution":
        cpq_status, adaptive_status, ess_status = (
            "Reconciliation required", "Blocked by CPQ result", "Waiting for Adaptive Search completion"
        )
    elif stage == "adaptive_search" or status == "awaiting_adaptive_search_approval":
        cpq_status, adaptive_status, ess_status = (
            "Completed", "Ready for approval" if _has_adaptive_preview(payload) else "Preview needed",
            "Waiting for Adaptive Search completion"
        )
    elif stage == "ess" or status == "awaiting_ess_approval":
        cpq_status, adaptive_status, ess_status = (
            "Completed", "Completed", "Ready for approval" if _has_ess_payload(payload) else "Preview needed"
        )
    elif status == "approval_required" and _mapping(payload.get("components")).get("cpq_settings"):
        cpq_status, adaptive_status, ess_status = (
            "Ready for approval" if _has_cpq_preview(payload) else "Preview needed",
            "Waiting for CPQ completion", "Waiting for Adaptive Search completion"
        )
    elif status == "ready_for_cpq_write_route":
        cpq_status, adaptive_status, ess_status = (
            "Ready to prepare approval", "Waiting for CPQ completion", "Waiting for Adaptive Search completion"
        )
    else:
        cpq_status, adaptive_status, ess_status = (
            "Not started", "Waiting for CPQ completion", "Waiting for Adaptive Search completion"
        )
    return [
        {"name": "Fusion prerequisite opt-ins", "status": fusion_status},
        {"name": "CPQ Commerce Settings", "status": cpq_status},
        {"name": "Adaptive Search partial publish", "status": adaptive_status},
        {"name": "Unified Asset Read Model Sync", "status": ess_status},
    ]


def _action_and_approval(
    payload: Mapping[str, Any], opt_ins: Sequence[Mapping[str, str]]
) -> tuple[str, dict[str, Any], str]:
    status, stage = _status_and_stage(payload)
    operation = _operation(payload)
    if stage == "adaptive_initialization":
        blocker = _mapping(payload.get("initialization_blocker"))
        reason = ("Fusion returned HTTP 400: Could not find active meta model."
                  if blocker.get("reason") == "missing_metamodel" else
                  "Fusion returned an empty entity catalog." if blocker.get("reason") == "empty_catalog" else
                  "Adaptive Search initialization completion is not verified.")
        if status == "awaiting_adaptive_initialization_approval" and _has_initialization_proposal(payload):
            prompt = ("Approve preparing the initial Adaptive Search Full Publish? "
                      "Upload and submission will require a separate Data Loader approval.")
            return (reason + " CPQ remains verified. Initial Full Publish is required before Partial Publish. "
                    "No Full Publish workbook or submission has started for this proposal.",
                    {"required": True, "stage": stage, "prompt": prompt}, prompt)
        observed = _mapping(payload.get("initialization_status"))
        progress = {"DATA_LOADER_PENDING": " The Full Publish data load is still processing.",
                    "DATA_LOADER_FAILED": " The Full Publish data load failed.",
                    "PUBLISH_PENDING": " Full Publish completion is not yet verified.",
                    "PUBLISH_RUNNING": " The Full Publish job is running.",
                    "PUBLISH_FAILED": " The Full Publish job failed.",
                    "BLOCKED": " Full Publish completed, but catalog readiness could not be verified.",
                    "INDETERMINATE": " The initialization outcome is uncertain."}.get(observed.get("state"), "")
        return (reason + " CPQ completion is retained." + progress,
                {"required": False, "stage": stage, "prompt": "No new preparation or load approval is actionable."},
                _value(payload, "next_action"))
    if status == "awaiting_adaptive_preparation_approval":
        if not _has_adaptive_preparation_proposal(payload):
            return ("The Adaptive Search preparation proposal is incomplete or inconsistent.",
                    {"required": False, "stage": "adaptive_preparation", "prompt": "No preparation approval is actionable."},
                    "Request a fresh validated Adaptive Search preparation proposal.")
        prompt = ("Approve preparing the Adaptive Search Partial Publish? "
                  "Upload and submission will require a separate Data Loader approval.")
        return ("The CPQ load succeeded and its settings were verified. Next, prepare a selective publish for "
                "Consolidated Asset and Serialized Asset. Workbook generation and load submission "
                "have not started for this proposal.",
                {"required": True, "stage": "adaptive_preparation", "prompt": prompt}, prompt)
    if stage == "adaptive_preparation":
        return ("Adaptive Search preparation is stopped. The previous CPQ completion is retained; no publish submission is authorized.",
                {"required": False, "stage": "adaptive_preparation", "prompt": "No preparation or load approval is actionable."},
                _value(payload, "next_action"))
    if status == "awaiting_cpq_preparation_approval":
        if not _has_cpq_preparation_proposal(payload):
            return ("The CPQ preparation proposal is incomplete or inconsistent.",
                    {"required": False, "stage": "cpq_preparation", "prompt": "No preparation approval is actionable."},
                    "Create a fresh validated CPQ preparation proposal.")
        prompt = ("Approve proceeding with preparation of these CPQ settings changes? "
                  "Upload and submission will require a separate Data Loader approval.")
        return ("Review the planned CPQ settings. No workbook has been generated and no CPQ change has been submitted.",
                {"required": True, "stage": "cpq_preparation", "prompt": prompt}, prompt)
    if stage == "cpq_preparation":
        return ("CPQ preparation is stopped; no new submission is authorized.",
                {"required": False, "stage": "cpq_preparation", "prompt": "No preparation or load approval is actionable."},
                _value(payload, "next_action", default="Create and approve a fresh preparation proposal if needed."))
    # Completion wins over the most recent execution stage (including live ESS).
    if status in {"completed", "COMPLETED"}:
        return ("The Fusion Asset-Based Ordering workflow is complete.",
                {"required": False, "stage": "completed", "prompt": "No approval is required."},
                "No further workflow action is required.")
    if status in {"awaiting_adaptive_monitoring_choice", "adaptive_search_manual", "adaptive_search_monitoring"}:
        adaptive = _mapping(payload.get("adaptive_search"))
        actual = str(adaptive.get("adaptive_search_status", "")).strip().upper()
        allowed = {"WAIT", "READY", "RUNNING", "PAUSED", "SUCCEEDED", "FAILED", "ERROR", "CANCELLED"}
        publish = (f"Last checked Partial Publish status: {actual}." if actual in allowed else
                   "Partial Publish completion has not yet been verified.")
        action = "Adaptive Search data load succeeded. " + publish
        if status == "adaptive_search_manual":
            action += " Monitoring is stopped; the checkpoint is saved."
        elif status == "adaptive_search_monitoring":
            action += " Checking this same publish every 15 seconds within the time limit."
        return (action, {"required": False, "stage": "adaptive_search",
                        "prompt": "No mutation approval is requested; ESS still requires separate approval."},
                _value(payload, "next_action"))
    if status in {"adaptive_search_monitoring_timeout", "monitoring_timeout"}:
        return ("Adaptive Search monitoring stopped at its time limit; completion is not verified.",
                {"required": False, "stage": "adaptive_search", "prompt": "No ESS approval is actionable."},
                _value(payload, "next_action", default="Check the Adaptive Search publish status and continue, or explicitly choose to keep checking again."))
    if status == "ess_pending_or_failed":
        return ("The approved ESS request has not reached verified success.",
                {"required": False, "stage": "ess", "prompt": "No new ESS submission approval is currently actionable."},
                "Resume GET-only monitoring of the persisted ESS request; reconcile a terminal failure without resubmitting automatically.")
    if status in {"adaptive_search_not_eligible_for_ess", "adaptive_search_failed", "adaptive_search_indeterminate"}:
        return ("Adaptive Search did not provide the exact final evidence required for ESS.",
                {"required": False, "stage": "adaptive_search", "prompt": "No ESS approval is actionable."},
                _value(payload, "next_action", default="Reconcile the same publish operation without republishing or submitting ESS automatically."))
    if payload.get("handover_version") == "2.0" and stage in {"cpq_data_loader", "adaptive_data_loader", "cpq_verification", "recovery"}:
        label = "CPQ settings" if stage == "cpq_data_loader" else "Adaptive Search"
        submitted = status in {"cpq_submitted", "adaptive_load_submitted"} and payload.get("status") != "blocked"
        action = (f"{label} load submitted. Completion has not yet been verified."
                  if submitted else "Completion is not verified; continue only from the exact workflow checkpoint.")
        next_action = _value(payload, "next_action")
        return action, {"required": False, "stage": "none", "prompt": "No new mutation approval is requested."}, next_action
    if status == "requires_process_selection":
        prompt = _value(payload, "prompt", default="Provide the CPQ Standard Process variable name, or explicitly choose the default oraclecpqo.")
        return prompt, {"required": False, "stage": "process_selection", "prompt": "No approval is currently actionable."}, prompt
    if _is_prerequisite_approval(payload):
        code = str(operation["feature_code"])
        name = OPT_IN_NAMES.get(code, code)
        choice = str(operation["feature_choice"])
        action = f"Enable the required Fusion opt-in: {name}, using the resolved choice {choice}."
        prompt = (
            f"Please approve enabling {name} using the resolved choice {choice}. "
            "Only this opt-in will be changed."
        )
        return action, {"required": True, "stage": "fusion_prerequisite", "prompt": prompt}, prompt
    if _is_prerequisite_handoff(payload):
        disabled = [item["name"] for item in opt_ins if item["status"] == "disabled"]
        eligible = _eligible_handoff(payload)
        eligible_name = OPT_IN_NAMES.get(
            str(eligible.get("feature_code")), "the first disabled Fusion opt-in"
        )
        names = ", ".join(disabled) if disabled else "one or more required Fusion opt-ins"
        action = (
            f"The following Fusion opt-ins must be enabled: {names}. "
            f"Resolve the exact choice for {eligible_name} first."
        )
        next_action = (
            f"Resolve and validate the exact enablement choice for {eligible_name}; "
            "then present its one-feature approval preview."
        )
        return action, {
            "required": False,
            "stage": "fusion_prerequisite",
            "prompt": "No approval is actionable until the exact choice is resolved.",
        }, next_action
    if stage == "adaptive_search" or status == "awaiting_adaptive_search_approval":
        if not _has_adaptive_preview(payload):
            next_action = "Prepare the exact Adaptive Search Task Hook preview, then request its separate publish approval."
            return (next_action,
                    {"required": False, "stage": "adaptive_search", "prompt": "No publish approval is actionable until its preview is prepared."},
                    next_action)
        prompt = (
            "Please approve the exact Adaptive Search partial publish for "
            "ConsolidatedAsset and SerializedAsset."
        )
        return prompt, {"required": True, "stage": "adaptive_search", "prompt": prompt}, prompt
    if stage == "ess" or status == "awaiting_ess_approval":
        if not _has_ess_payload(payload):
            next_action = "Prepare the exact ESS payload before requesting separate approval."
            return (next_action,
                    {"required": False, "stage": "ess", "prompt": "No ESS approval is actionable until its payload is prepared."},
                    next_action)
        prompt = "Please approve the exact Unified Asset Read Model Sync ESS submission."
        return prompt, {"required": True, "stage": "ess", "prompt": prompt}, prompt
    if status == "approval_required" and _mapping(payload.get("components")).get("cpq_settings"):
        if not _has_cpq_preview(payload):
            next_action = "Complete the exact CPQ Task Hook preview before requesting approval."
            return (next_action,
                    {"required": False, "stage": "cpq", "prompt": "No CPQ approval is actionable until its preview is complete."},
                    next_action)
        settings = _cpq_settings(payload)
        recovery_only = len(settings) == 1 and settings[0]["name"] == SAFE_CPQ_SETTING_LABELS["defineFieldsForModifyActionFunction"]
        prompt = (
            ("Please approve only the ABO delta-action Library Function recovery import. "
             if recovery_only else "Please approve this exact CPQ Commerce Settings operation. ")
            + "Adaptive Search and ESS require later separate approvals."
        )
        return (
            ("Apply only the fixed ABO delta-action Library Function setting. "
             "The process and Fusion ABO enablement settings are not part of this recovery import."
             if recovery_only else "Apply the CPQ Commerce Settings required to enable Fusion Asset-Based Ordering."),
            {"required": True, "stage": "cpq", "prompt": prompt},
            prompt,
        )
    if status == "ready_for_cpq_write_route":
        next_action = (
            "Prepare the exact CPQ Commerce Settings preview, then request approval "
            "for that immutable operation."
        )
        return (
            "All four Fusion opt-ins are enabled. CPQ approval preparation can begin.",
            {"required": False, "stage": "cpq", "prompt": "No approval is currently actionable."},
            next_action,
        )
    if status == "requires_abo_delta_action_library_function_recovery":
        next_action = "Prepare the fixed function-only CPQ Settings recovery preview, then request its exact approval."
        return ("Only the ABO delta-action Library Function requires CPQ recovery.",
                {"required": False, "stage": "cpq", "prompt": "No approval is currently actionable."}, next_action)
    if status == "already_configured":
        return ("The selected CPQ process and Fusion ABO settings are already configured.",
                {"required": False, "stage": "cpq", "prompt": "No CPQ change requires approval."},
                _value(payload, "next_action", default="Record the verified CPQ state in the project workspace."))
    if status == "waiting_for_adaptive_search_publish":
        return ("The approved Adaptive Search publish has not reached verified success.",
                {"required": False, "stage": "adaptive_search", "prompt": "No ESS approval is currently actionable."},
                _value(payload, "next_action", default="Continue GET-only monitoring of the same publish operation."))
    if status == "adaptive_search_succeeded_ess_submission_required":
        return ("Adaptive Search succeeded; the ESS approval payload must be prepared next.",
                {"required": False, "stage": "ess", "prompt": "No ESS approval is actionable until the exact payload is prepared."},
                _value(payload, "next_action", default="Prepare the governed ESS preview and request its separate approval."))
    if status == "blocked_before_adaptive_search_publish" or (
        status == "indeterminate" and stage == "cpq_settings_write_execution"
    ):
        return ("The CPQ Settings import or readback is incomplete or uncertain.",
                {"required": False, "stage": "cpq", "prompt": "No publish approval is actionable."},
                _value(payload, "next_action", default="Reconcile CPQ Commerce Settings through approved read-only checks; do not replay the import automatically."))
    if status == "prerequisite_update_indeterminate":
        return ("The approved Fusion opt-in update could not be confirmed.",
                {"required": False, "stage": "fusion_prerequisite", "prompt": "No further opt-in approval is actionable yet."},
                _value(payload, "next_action", default="Reread the required Fusion feature states before deciding on recovery; do not retry automatically."))
    if status == "failed" or "failed" in status or "blocked" in status:
        return (
            _value(payload, "message", default="The current workflow state could not be verified safely."),
            {"required": False, "stage": "blocked", "prompt": "No approval is currently actionable."},
            _value(payload, "next_action", default="Resolve the reported blocker and rerun the approved read-only verification."),
        )
    return (
        "Review the current Fusion Asset-Based Ordering workflow state.",
        {"required": False, "stage": "none", "prompt": "No approval is currently required."},
        "Continue only through the next eligible governed workflow stage.",
    )


def _validate_presentation_model(model: Mapping[str, Any]) -> None:
    """Validate the embedded task-local presentation contract."""

    if model.get("schema_version") != PRESENTATION_SCHEMA_VERSION:
        raise AboPresentationError("Unsupported ABO presentation contract version.")
    target = model.get("target")
    if not isinstance(target, Mapping):
        raise AboPresentationError("ABO presentation target must be an object.")
    for field in ("environment", "cpq_process"):
        if not isinstance(target.get(field), str) or not str(target[field]).strip():
            raise AboPresentationError(
                f"ABO presentation target.{field} must be a non-empty string."
            )
    opt_ins = model.get("opt_ins")
    if (
        not isinstance(opt_ins, list)
        or [item.get("code") for item in opt_ins if isinstance(item, Mapping)]
        != [code for code, _ in OPT_INS]
    ):
        raise AboPresentationError(
            "ABO presentation must contain the four ordered prerequisite opt-ins."
        )
    for item in opt_ins:
        if not isinstance(item, Mapping) or item.get("status") not in OPT_IN_STATUS_VALUES:
            raise AboPresentationError("ABO presentation contains an invalid opt-in status.")
    approval = model.get("approval")
    if not isinstance(approval, Mapping) or not isinstance(approval.get("required"), bool):
        raise AboPresentationError(
            "ABO presentation approval must declare whether approval is required."
        )
    if not isinstance(approval.get("prompt"), str) or not str(approval["prompt"]).strip():
        raise AboPresentationError("ABO presentation approval prompt is required.")
    stages = model.get("workflow_stages")
    if not isinstance(stages, list) or len(stages) != 4:
        raise AboPresentationError(
            "ABO presentation must contain the four ordered workflow stages."
        )
    for stage in stages:
        if (
            not isinstance(stage, Mapping)
            or not isinstance(stage.get("name"), str)
            or not isinstance(stage.get("status"), str)
        ):
            raise AboPresentationError("ABO presentation contains an invalid workflow stage.")
    required_changes = model.get("required_changes")
    if not isinstance(required_changes, list) or not all(
        isinstance(item, str) and item.strip() for item in required_changes
    ):
        raise AboPresentationError("ABO presentation required_changes must be a string list.")
    for field in ("current_operation", "next_action", "side_effects"):
        if not isinstance(model.get(field), str) or not str(model[field]).strip():
            raise AboPresentationError(f"ABO presentation {field} must be a non-empty string.")
    cpq_settings = model.get("cpq_settings")
    if not isinstance(cpq_settings, list) or not all(
        isinstance(item, Mapping)
        and isinstance(item.get("name"), str)
        and isinstance(item.get("value"), str)
        for item in cpq_settings
    ):
        raise AboPresentationError("ABO presentation CPQ settings are invalid.")
    recovery_current = model.get("cpq_recovery_current_value")
    if recovery_current is not None and not isinstance(recovery_current, str):
        raise AboPresentationError("ABO presentation recovery current value is invalid.")
    approval_scope = model.get("approval_scope", [])
    if not isinstance(approval_scope, list) or not all(
        isinstance(item, Mapping)
        and isinstance(item.get("name"), str)
        and isinstance(item.get("value"), str)
        for item in approval_scope
    ):
        raise AboPresentationError("ABO presentation approval scope is invalid.")


def build_abo_presentation_model(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize any public ABO result into the embedded presentation contract."""

    if payload.get("schema_version") == PRESENTATION_SCHEMA_VERSION and isinstance(
        payload.get("opt_ins"), list
    ):
        model = dict(payload)
        _validate_presentation_model(model)
        return model
    target = _target(payload)
    opt_ins = _opt_in_rows(payload)
    action, approval, next_action = _action_and_approval(payload, opt_ins)
    model = {
        "schema_version": PRESENTATION_SCHEMA_VERSION,
        "target": {
            "environment": _value(target, "environment", "name", "fusion_host"),
            "cpq_process": _process(payload),
        },
        "opt_ins": opt_ins,
        "required_changes": [
            item["name"] for item in opt_ins if item["status"] == "disabled"
        ],
        "workflow_stages": _stage_rows(payload, opt_ins),
        "current_operation": action,
        "cpq_settings": _cpq_settings(payload),
        "cpq_recovery_current_value": _cpq_recovery_current_value(payload),
        "approval": approval,
        "approval_scope": _approval_scope(payload, str(approval["stage"])) if approval["required"] else [],
        "next_action": next_action,
        "side_effects": _value(
            payload, "side_effects", default="No side effects were reported."
        ),
    }
    _validate_presentation_model(model)
    return model


def _display_opt_in_status(item: Mapping[str, str]) -> str:
    labels = {
        "enabled": "Enabled",
        "disabled": "Disabled — must be enabled",
        "not_checked": "Not checked yet — blocked by the current prerequisite stage",
        "verification_failed": "Unable to verify — no change attempted",
        "inconsistent": "Inconsistent — reconciliation required",
        "previously_verified": "Verified before CPQ execution — individual readings unavailable",
    }
    return labels[item["status"]]


def _table_cell(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def render_workbook_access(source: Path, *, project_root: Path) -> str:
    """Link the generated input without reading or changing the validated archive."""
    root = project_root.resolve(strict=True)
    workbook = source.resolve(strict=True)
    workbook.relative_to(root)
    if (not workbook.is_file() or workbook.suffix.lower() != ".xlsx"
            or any(ord(character) < 32 or character in "<>" for character in str(workbook))):
        raise AboPresentationError("Workbook access requires a generated XLSX file.")
    label = re.sub(r"([\\`*\[\]<>|])", r"\\\1", workbook.name)
    target = f"<{workbook}>"
    return (f"Generated workbook: [{label}]({target})\n\n"
            "You can open it to view the contents. The pending load uses the validated immutable archive; "
            "editing this file does not update that load.\n")


def render_abo_presentation(payload: Mapping[str, Any]) -> str:
    """Render a validated customer presentation without implementation metadata."""

    if payload.get("state") in {"workbook_access", "awaiting_approval", "data_loader_status"} and isinstance(payload.get("markdown"), str):
        # Workbook access is separate; Core's preview/status remains verbatim.
        return payload["markdown"]
    model = build_abo_presentation_model(payload)
    if _status_and_stage(payload)[0] == "requires_process_selection":
        # Process selection is a correction prompt, not a setup status report.
        # Do not infer Run Book creation from the fact that preflight ran.
        message = str(model["next_action"])
        if _mapping(payload.get("cpq_preflight")).get("process_selection_required") is True:
            message += " No ABO configuration changes were made."
        return message + "\n"
    target = _mapping(model["target"])
    lines = [
        "# Enable Fusion Asset-Based Ordering",
        "",
        "## Target",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Environment | {_table_cell(target['environment'])} |",
        f"| CPQ Process | {_table_cell(target['cpq_process'])} |",
        "",
        "## Required Fusion Opt-In Status",
        "",
        "| Opt-In | Status |",
        "|---|---|",
    ]
    lines.extend(
        f"| {item['name']} | {_display_opt_in_status(item)} |"
        for item in model["opt_ins"]
    )
    if _mapping(payload.get("presentation_context")).get("feature_states_verified_at"):
        lines.extend([
            "",
            "These opt-ins were verified before CPQ execution; this status message does not recheck them.",
        ])
    lines.extend(["", "## Required Changes", ""])
    if model["required_changes"]:
        lines.extend(f"- Enable {name}." for name in model["required_changes"])
    else:
        lines.append(
            "No disabled Fusion opt-ins were found in the available verified evidence."
        )
    lines.extend(
        ["", "## Planned Workflow", "", "| Stage | Operation | Status |", "|---|---|---|"]
    )
    for index, stage in enumerate(model["workflow_stages"], start=1):
        lines.append(f"| {index} | {stage['name']} | {stage['status']} |")
    lines.extend(["", "## Current Operation", "", str(model["current_operation"])])
    is_initialization = _status_and_stage(payload)[1] == "adaptive_initialization"
    adaptive = _mapping(payload.get("initialization_status" if is_initialization else "adaptive_search"))
    job_id = adaptive.get("adaptive_search_job_id")
    if isinstance(job_id, (str, int)) and not isinstance(job_id, bool) and re.fullmatch(r"[1-9][0-9]*", str(job_id)):
        lines.extend(["", "### Full Publish Initialization Status" if is_initialization else "### Partial Publish Status", "", "| Field | Value |", "|---|---|",
                      f"| Publish Job | {job_id} |"])
        last_status = str(adaptive.get("adaptive_search_status", "")).strip().upper()
        if last_status in {"WAIT", "READY", "RUNNING", "PAUSED", "SUCCEEDED", "FAILED", "ERROR", "CANCELLED"}:
            lines.append(f"| Last checked status | {last_status} |")
        elapsed = payload.get("elapsed_wait_seconds")
        if isinstance(elapsed, (int, float)) and not isinstance(elapsed, bool) and elapsed >= 0:
            lines.append(f"| Elapsed monitoring wait | {elapsed:.0f} seconds |")
    if _status_and_stage(payload)[0] in {"completed", "COMPLETED", "ess_pending_or_failed"}:
        ess = _mapping(payload.get("ess_sync"))
        request_id = ess.get("request_id")
        if isinstance(request_id, int) and not isinstance(request_id, bool) and request_id > 0:
            lines.extend(["", "### Asset Sync Result", "", "| Field | Value |", "|---|---|",
                          f"| Request | {request_id} |",
                          "| Result | " + ("Succeeded" if ess.get("terminal") is True and ess.get("success") is True
                                           else "Completion not verified") + " |"])
    if model["cpq_settings"] and model["cpq_recovery_current_value"] is not None:
        lines.extend([
            "", "### ABO Delta-Action Library Function Recovery", "",
            "| State | Value |", "|---|---|",
            f"| Current | {_table_cell(model['cpq_recovery_current_value'])} |",
            f"| Required | {_table_cell(model['cpq_settings'][0]['value'])} |",
        ])
    elif model["cpq_settings"]:
        cpq_approval_ready = (
            model["approval"]["required"] and model["approval"]["stage"] == "cpq"
        )
        lines.extend(
            [
                "",
                "### CPQ Settings in This Approval" if cpq_approval_ready else "### Planned CPQ Settings",
                "",
                "| Setting | Value |",
                "|---|---|",
            ]
        )
        lines.extend(
            f"| {_table_cell(item['name'])} | {_table_cell(item['value'])} |" for item in model["cpq_settings"]
        )
    if model["approval_scope"]:
        lines.extend(["", "### Exact Operation in This Approval", "", "| Field | Value |", "|---|---|"])
        lines.extend(
            f"| {_table_cell(item['name'])} | {_table_cell(item['value'])} |" for item in model["approval_scope"]
        )
    lines.extend(
        [
            "",
            "## Approval Required" if _mapping(model["approval"])["required"] else "## Approval Status",
            "",
            str(_mapping(model["approval"])["prompt"]),
        ]
    )
    if not _mapping(model["approval"])["required"]:
        lines.extend(["", "## Next Action", "", str(model["next_action"])])
    status_report = payload.get("data_loader_markdown", "")
    prefix = status_report + "\n\n" if isinstance(status_report, str) and status_report else ""
    return prefix + "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render the fixed Fusion ABO user-facing presentation."
    )
    parser.add_argument("input", help="Path to a structured ABO result JSON file.")
    parser.add_argument("--output", help="Optional Markdown output path.")
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise SystemExit("ABO presentation input must be a JSON object.")
    rendered = render_abo_presentation(payload)
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
