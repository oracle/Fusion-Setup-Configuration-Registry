#!/usr/bin/env python3
"""Task-local CPQ Commerce Settings validation for Fusion ABO planning."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


TASK_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TASK_SCRIPTS))

from cpq_rest_service import (  # noqa: E402
    CpqClientError,
    CpqConfigurationError,
    CpqHttpError,
    CpqRestClient,
    add_connection_arguments,
    client_from_args,
)
from fusion_abo_prerequisites import (  # noqa: E402
    CPQ_ABO_PREREQUISITE_FEATURE_CODES,
    FUSION_ABO_PREREQUISITE_FEATURE_CODES,
    SUBSCRIPTION_COVERAGE_PREREQUISITE_FEATURE_CODES,
)


class CpqSettingsError(CpqClientError):
    """Raised when CPQ settings cannot safely support a Fusion ABO plan."""


FSM_SET_OPTIN_SKILL_ID = "shared.implementation-planning.fsm-set-optin.fsm-set-optin-features"
CPQ_DEFAULT_FUSION_ABO_PROCESS_VARIABLE_NAME = "oraclecpqo"
PROCESS_SELECTION_SOURCE_EXPLICIT = "explicit"
PROCESS_SELECTION_SOURCE_CPQ_DEFAULT = "cpq_default"
FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_KEY = "defineFieldsForModifyActionFunction"
FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_VALUE = "_s_getAttributesForABODeltaActionCalculation"
CPQ_COMMERCE_SETTINGS_PATH = "/rest/v19/commerceUISettings"
CPQ_COMMERCE_PROCESS_PATH_PREFIX = "/rest/v19/commerceProcesses/"
CPQ_FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_PATH = (
    "/rest/v19/settings/COMMERCE/defineFieldsForModifyActionFunction"
)


def validate_process_variable_name(value: str) -> str:
    """Validate a process variable before turning it into a CPQ URL segment."""

    process_name = value.strip()
    if not process_name:
        raise CpqConfigurationError("process_variable_name is required.")
    if len(process_name) > 255 or any(char in process_name for char in "\x00\r\n/\\"):
        raise CpqConfigurationError("process_variable_name is malformed.")
    return process_name


def _read_cpq_response(stage: str, operation: Any) -> Any:
    """Add a business stage label while preserving only safe CPQ failures."""

    try:
        return operation()
    except CpqClientError as exc:
        # Do not pass through arbitrary exception text: a non-HTTP transport
        # error can contain an unsafe low-level detail.  The task coordinator
        # presents only the structured fields copied below.
        status_code = getattr(exc, "status_code", None)
        if isinstance(status_code, int):
            message = f"{stage} failed: CPQ returned HTTP {status_code}."
        else:
            message = f"{stage} failed before a supported CPQ response was available."

        wrapped = CpqSettingsError(message)
        for attribute in ("provider_message", "provider_code", "diagnostic_ids"):
            value = getattr(exc, attribute, None)
            if value is not None:
                setattr(wrapped, attribute, value)
        raise wrapped from exc


def _normalise_value(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, int):
        return str(value)
    return None


def _commerce_settings_map(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return the map published by the Commerce-specific v19 read resource."""

    commerce_settings = payload.get("commerceSettings")
    if not isinstance(commerce_settings, Mapping):
        raise CpqSettingsError(
            "CPQ commerceUISettings response does not contain a commerceSettings object."
        )
    return commerce_settings


def _required_abo_state(commerce_settings: Mapping[str, Any], key: str) -> str:
    """Require an unambiguous Yes/No value for an ABO state setting."""

    value = _normalise_value(commerce_settings.get(key))
    if value is None:
        raise CpqSettingsError(
            f"CPQ commerceUISettings response is missing required Commerce setting {key}."
        )
    if value.casefold() == "yes":
        return "Yes"
    if value.casefold() == "no":
        return "No"
    raise CpqSettingsError(
        f"CPQ Commerce setting {key} must be Yes or No; received an unsupported value."
    )


def _optional_commerce_setting(commerce_settings: Mapping[str, Any], key: str) -> str | None:
    """Read a setting that CPQ may intentionally omit from the response."""

    return _normalise_value(commerce_settings.get(key))


def _abo_delta_action_library_function_value(payload: Mapping[str, Any]) -> str | None:
    """Validate the direct response from CPQ's one approved generic-setting GET.

    CPQ returns this endpoint as a single Settings object, not a Commerce
    settings map. Reject a malformed or mismatched response rather than
    guessing that another setting represents the required library function.
    """

    if payload.get("key") != FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_KEY:
        raise CpqSettingsError(
            "CPQ ABO Delta Action Library Function readback returned an unexpected setting key; "
            f"expected {FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_KEY}."
        )
    setting_type = payload.get("type")
    if not isinstance(setting_type, str) or setting_type.casefold() != "commerce":
        raise CpqSettingsError(
            "CPQ ABO Delta Action Library Function readback returned an unexpected setting type for "
            f"{FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_KEY}."
        )
    value = payload.get("value")
    if value is None:
        return None
    if not isinstance(value, str):
        raise CpqSettingsError(
            "CPQ ABO Delta Action Library Function readback returned an unsupported value for "
            f"{FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_KEY}."
        )
    return value.strip() or None


def _is_yes(value: str | None) -> bool:
    return isinstance(value, str) and value.casefold() == "yes"


@dataclass(frozen=True)
class CommerceSettingsSummary:
    """Only the three CPQ Commerce Settings relevant to Fusion ABO."""

    standard_abo: str | None
    fusion_abo: str | None
    fusion_abo_process: str | None
    audit_summary: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "enable_standard_abo": self.standard_abo,
            "enable_fusion_abo": self.fusion_abo,
            "fusion_abo_process_variable_name": self.fusion_abo_process,
            "audit_summary": self.audit_summary,
        }


@dataclass(frozen=True)
class AboDeltaActionLibraryFunctionSummary:
    """The exact CPQ Commerce Library Function required by Fusion ABO.

    This object represents one fixed settings resource. It is deliberately not
    a reusable generic-settings model, because the task must not read or
    disclose arbitrary CPQ settings.
    """

    configured_function: str | None
    is_expected: bool
    audit_summary: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "configured_function": self.configured_function,
            "is_expected": self.is_expected,
            "audit_summary": self.audit_summary,
        }


@dataclass(frozen=True)
class StandardProcessVerification:
    """Safe result for a CPQ Commerce Process type check."""

    process_variable_name: str
    exists: bool
    is_standard_process: bool
    process_type: int | None
    reason: str
    audit_summary: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "process_variable_name": self.process_variable_name,
            "exists": self.exists,
            "is_standard_process": self.is_standard_process,
            "process_type": self.process_type,
            "reason": self.reason,
            "audit_summary": self.audit_summary,
        }


@dataclass(frozen=True)
class FusionAboProcessSelection:
    """The resolved process and whether CPQ's documented default was used."""

    requested_process_variable_name: str | None
    resolved_process_variable_name: str
    selection_source: str
    requires_default_disclosure: bool

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "requested_process_variable_name": self.requested_process_variable_name,
            "resolved_process_variable_name": self.resolved_process_variable_name,
            "selection_source": self.selection_source,
            "requires_default_disclosure": self.requires_default_disclosure,
        }
        if self.requires_default_disclosure:
            result["default_disclosure"] = (
                "No CPQ process was supplied. CPQ default oraclecpqo was selected and will be used "
                "only if this target site verifies that it exists and is a Standard Process "
                "(processType = 0)."
            )
        return result


def resolve_fusion_abo_process_selection(
    process_variable_name: str | None,
) -> FusionAboProcessSelection:
    """Match CPQ Dev's explicit-process and blank-process behavior safely.

    A blank Fusion ABO process is not silently accepted.  It is resolved to
    CPQ Dev's documented default, then the caller must still verify that value
    through the normal CPQ Commerce Process lookup before a write can be
    planned.  A supplied value, including ``oraclecpqo``, remains explicit and
    follows the same verification path.
    """

    if process_variable_name is None:
        return FusionAboProcessSelection(
            requested_process_variable_name=None,
            resolved_process_variable_name=CPQ_DEFAULT_FUSION_ABO_PROCESS_VARIABLE_NAME,
            selection_source=PROCESS_SELECTION_SOURCE_CPQ_DEFAULT,
            requires_default_disclosure=True,
        )
    if not isinstance(process_variable_name, str):
        raise CpqSettingsError("process_variable_name must be text when supplied.")
    requested_name = process_variable_name.strip()
    if not requested_name:
        return FusionAboProcessSelection(
            requested_process_variable_name=None,
            resolved_process_variable_name=CPQ_DEFAULT_FUSION_ABO_PROCESS_VARIABLE_NAME,
            selection_source=PROCESS_SELECTION_SOURCE_CPQ_DEFAULT,
            requires_default_disclosure=True,
        )
    return FusionAboProcessSelection(
        requested_process_variable_name=validate_process_variable_name(requested_name),
        resolved_process_variable_name=validate_process_variable_name(requested_name),
        selection_source=PROCESS_SELECTION_SOURCE_EXPLICIT,
        requires_default_disclosure=False,
    )


class CpqSettingsClient:
    """Expose only read-only Fusion ABO readiness checks for CPQ Settings."""

    def __init__(self, rest_client: CpqRestClient) -> None:
        self._rest_client = rest_client

    def read_commerce_settings(self) -> CommerceSettingsSummary:
        response = _read_cpq_response(
            "Read CPQ Commerce Settings",
            lambda: self._rest_client.get_json(CPQ_COMMERCE_SETTINGS_PATH),
        )
        commerce_settings = _commerce_settings_map(response.payload)
        return CommerceSettingsSummary(
            standard_abo=_required_abo_state(commerce_settings, "enableStandardABO"),
            fusion_abo=_required_abo_state(commerce_settings, "enableFusionABO"),
            fusion_abo_process=_optional_commerce_setting(
                commerce_settings,
                "commerceProcessVarNameForEnabledFusionABO",
            ),
            audit_summary=response.audit_summary(),
        )

    def read_abo_delta_action_library_function(self) -> AboDeltaActionLibraryFunctionSummary:
        """Read and validate the fixed Commerce Library Function required by ABO.

        This task selects one fixed GET route; the shared CPQ transport has no
        knowledge of the Fusion ABO setting key.
        """

        response = _read_cpq_response(
            "Read CPQ Fusion ABO Delta Action Library Function",
            lambda: self._rest_client.get_json(
                CPQ_FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_PATH
            ),
        )
        configured_function = _abo_delta_action_library_function_value(response.payload)
        return AboDeltaActionLibraryFunctionSummary(
            configured_function=configured_function,
            is_expected=(
                configured_function == FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_VALUE
            ),
            audit_summary=response.audit_summary(),
        )

    def verify_standard_process(self, process_variable_name: str) -> StandardProcessVerification:
        requested_name = validate_process_variable_name(process_variable_name)
        encoded_name = urllib.parse.quote(requested_name, safe="")
        try:
            response = _read_cpq_response(
                "Verify CPQ Standard Process",
                lambda: self._rest_client.get_json(
                    f"{CPQ_COMMERCE_PROCESS_PATH_PREFIX}{encoded_name}"
                ),
            )
        except CpqSettingsError as exc:
            # Only this exact process lookup's HTTP 404 means missing.
            # Authentication, transport and other resource failures stay errors.
            cause = exc.__cause__
            if not isinstance(cause, CpqHttpError) or cause.status_code != 404:
                raise
            return StandardProcessVerification(
                process_variable_name=requested_name,
                exists=False,
                is_standard_process=False,
                process_type=None,
                reason="The requested CPQ process does not exist.",
                audit_summary={"method": "GET", "status_code": 404},
            )
        payload = response.payload
        returned_name = payload.get("variableName")
        exact_name_match = isinstance(returned_name, str) and returned_name == requested_name
        raw_process_type = payload.get("processType")
        process_type = raw_process_type if type(raw_process_type) is int else None
        if not exact_name_match:
            reason = "CPQ returned a process that does not exactly match the requested variable name."
        elif process_type is None:
            reason = "CPQ returned an invalid processType; a Standard Process must have numeric processType 0."
        elif process_type != 0:
            reason = "The requested CPQ process is not a Standard Process (processType must be 0)."
        else:
            reason = "The requested CPQ process exists and is a Standard Process."
        return StandardProcessVerification(
            process_variable_name=requested_name,
            exists=exact_name_match,
            is_standard_process=exact_name_match and process_type == 0,
            process_type=process_type,
            reason=reason,
            audit_summary=response.audit_summary(),
        )

    def plan_fusion_abo_write(self, process_variable_name: str | None) -> dict[str, Any]:
        """Return a non-executable readiness plan for a future CPQ write route."""

        process_selection = resolve_fusion_abo_process_selection(process_variable_name)
        requested_name = process_selection.resolved_process_variable_name

        # Read every fixed prerequisite before deciding which CPQ write plan
        # is safe.  A missing/different value is valid while Fusion ABO is
        # still off because the normal plan will configure it later; it is a
        # recovery condition only when Fusion ABO is already enabled for this
        # same Standard Process.  Keeping the read unconditional also gives
        # every preflight the exact read route that will be used for the final
        # post-write verification.
        settings = self.read_commerce_settings()
        library_function = self.read_abo_delta_action_library_function()
        process = self.verify_standard_process(requested_name)
        common_result = {
            "commerce_settings": settings.as_dict(),
            "process_selection": process_selection.as_dict(),
            "process_validation": process.as_dict(),
            "abo_delta_action_library_function": library_function.as_dict(),
        }
        blockers: list[str] = []
        if _is_yes(settings.standard_abo):
            blockers.append("Standard ABO is Yes. Do not disable it automatically.")
        if not process.is_standard_process:
            blockers.append(process.reason)
        if _is_yes(settings.fusion_abo):
            if not settings.fusion_abo_process:
                blockers.append(
                    "Fusion ABO is already Yes but CPQ did not return its current process; do not assume a match."
                )
            elif settings.fusion_abo_process != requested_name:
                blockers.append(
                    "Fusion ABO is already enabled for a different CPQ process; do not replace it automatically."
                )
            elif not blockers:
                if not library_function.is_expected:
                    return {
                        "status": "requires_abo_delta_action_library_function_recovery",
                        "message": (
                            "Fusion ABO is already enabled for the requested Standard Process, but the "
                            "required ABO Delta Action Commerce Library Function is missing or different."
                        ),
                        **common_result,
                        "required_before_write": [
                            "Verify all required Fusion opt-ins through the existing FSM Set Opt-in Features workflow.",
                            "Use the approved CPQ Settings executor to preview only the fixed ABO Delta Action Library Function PATCH and exact readback.",
                            "Obtain explicit approval immediately before the function-only CPQ recovery write.",
                        ],
                        "next_action": (
                            "Prepare a function-only recovery plan. Do not replay the saved process or "
                            "enableFusionABO PATCH."
                        ),
                    }
                return {
                    "status": "already_enabled",
                    "message": "Fusion ABO is already enabled for the requested Standard Process.",
                    **common_result,
                    "next_action": "Record the verified state; no CPQ write is required.",
                }
        if blockers:
            return {
                "status": "blocked",
                "blockers": blockers,
                "process_selection_required": (
                    process.audit_summary.get("status_code") == 404
                    or (process.exists and process.process_type is not None
                        and process.process_type != 0)
                ),
                **common_result,
                "next_action": "Resolve the listed CPQ condition before preparing any CPQ write execution.",
            }
        return {
            "status": "ready_for_cpq_write_design",
            "message": "CPQ preflight passed. This is not approval or execution readiness.",
            **common_result,
            "required_before_write": [
                *(
                    [
                        "Show the CPQ default-process disclosure in the exact later change preview before approval."
                    ]
                    if process_selection.requires_default_disclosure
                    else []
                ),
                "Verify all required Fusion opt-ins through the existing FSM Set Opt-in Features workflow.",
                "Prepare an approved CPQ Commerce Settings write executor for the selected target.",
                "Use that executor to preview the exact process-first then Fusion-ABO-enable sequence.",
                "Obtain explicit approval immediately before the CPQ write.",
            ],
        }


def normalize_fusion_abo_feature_states(
    evidence: Mapping[str, Any],
    *,
    feature_codes: Sequence[str] = FUSION_ABO_PREREQUISITE_FEATURE_CODES,
) -> dict[str, bool]:
    """Validate one exact, fresh Fusion ABO prerequisite state set.

    The CPQ Settings client deliberately does not call Fusion `featureStates`.
    The caller must obtain the evidence through the separately governed shared
    opt-in/read workflow, then pass the response object here for a deterministic
    read-only classification.
    """

    items = evidence.get("items")
    if not isinstance(items, list):
        raise CpqSettingsError("Fusion ABO feature-state evidence must contain an items array.")

    requested_codes = tuple(feature_codes)
    if not requested_codes or len(requested_codes) != len(set(requested_codes)):
        raise CpqSettingsError("Fusion ABO prerequisite feature codes must be a unique non-empty set.")

    states: dict[str, bool] = {}
    expected = set(requested_codes)
    for item in items:
        if not isinstance(item, Mapping):
            raise CpqSettingsError("Each Fusion ABO feature-state item must be an object.")
        feature_code = item.get("FeatureCode")
        feature_mode = item.get("FeatureMode")
        status_flag = item.get("StatusFlag")
        if feature_code not in expected:
            raise CpqSettingsError(
                "Fusion ABO feature-state evidence contains an unexpected feature code."
            )
        if feature_mode != "COMBO":
            raise CpqSettingsError(
                f"Fusion ABO prerequisite {feature_code} must have FeatureMode COMBO."
            )
        if not isinstance(status_flag, bool):
            raise CpqSettingsError(
                f"Fusion ABO prerequisite {feature_code} must have a boolean StatusFlag."
            )
        if feature_code in states:
            raise CpqSettingsError(
                f"Fusion ABO feature-state evidence contains duplicate feature code {feature_code}."
            )
        states[feature_code] = status_flag

    missing = [code for code in requested_codes if code not in states]
    if missing:
        raise CpqSettingsError(
            "Fusion ABO feature-state evidence is missing required feature code(s): "
            + ", ".join(missing)
            + "."
        )
    if len(items) != len(requested_codes):
        raise CpqSettingsError(
            "Fusion ABO feature-state evidence must contain exactly the required prerequisite records."
        )
    return states


def build_prerequisite_update_handoff(
    cpq_plan: Mapping[str, Any],
    feature_states: Mapping[str, bool],
    *,
    prerequisite_feature_codes: Sequence[str],
    status: str,
    stage: str,
    readiness_label: str,
) -> dict[str, Any]:
    """Return separate approval handoffs for one ordered prerequisite stage."""

    requested_codes = tuple(prerequisite_feature_codes)
    missing_features = [code for code in requested_codes if feature_states.get(code) is False]
    if not missing_features:
        raise CpqSettingsError("A prerequisite handoff requires at least one currently false feature.")
    return {
        "status": status,
        "stage": stage,
        "feature_states": dict(feature_states),
        "prerequisite_feature_codes": list(requested_codes),
        "cpq_preflight": cpq_plan,
        "prerequisite_handoffs": [
            {
                "skill_id": FSM_SET_OPTIN_SKILL_ID,
                "feature_code": code,
                "requested_action": "set-choices",
                "requested_intent": "enable",
                "choice_resolution_required": True,
                "execution_mode": "separate_governed_workflow",
                "approval_required": True,
                "fresh_readback_required": True,
            }
            for code in missing_features
        ],
        "next_action": (
            f"Stop this task. Run the existing shared opt-in workflow separately for each listed "
            f"{readiness_label} feature after explicit approval, then reread that stage and rerun "
            "the full read-only preflight."
        ),
    }


def build_fusion_abo_preflight(
    settings_client: CpqSettingsClient,
    process_variable_name: str | None,
    feature_state_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a non-executable, read-only Fusion ABO preflight result.

    This function never invokes the shared opt-in updater and never writes CPQ.
    It supplies explicit handoffs for false prerequisites and returns a ready
    CPQ write-route state only when every authoritative prerequisite passes.
    """

    cpq_plan = settings_client.plan_fusion_abo_write(process_variable_name)
    return classify_fusion_abo_preflight(cpq_plan, feature_state_evidence)


def classify_fusion_abo_preflight(
    cpq_plan: Mapping[str, Any],
    feature_state_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Classify fresh Fusion evidence after the CPQ read-only preflight.

    This function exists so a task-level orchestrator can preserve the declared
    read order: CPQ state and process first, then the authoritative Fusion
    ``featureStates`` lookup.  It never initiates an opt-in update or a CPQ
    mutation.  Callers must pass the complete, fresh CPQ plan and a feature
    response obtained through the approved Fusion read route.
    """

    status = cpq_plan.get("status")
    if status == "blocked":
        if cpq_plan.get("process_selection_required") is True:
            prompt = (
                "The selected process is not a valid CPQ Standard Process. "
                "Please enter another process variable name, or reply 'use default' "
                "to select oraclecpqo for verification."
            )
            return {
                "status": "requires_process_selection",
                "stage": "process_selection",
                "cpq_preflight": cpq_plan,
                "prompt": prompt,
                "next_action": prompt,
            }
        return {
            "status": "blocked",
            "stage": "cpq_preflight",
            "cpq_preflight": cpq_plan,
            "next_action": "Resolve the CPQ blocker before reading or changing Fusion prerequisite opt-ins, then rerun the full read-only preflight.",
        }

    feature_states = normalize_fusion_abo_feature_states(feature_state_evidence)
    supported_statuses = {
        "ready_for_cpq_write_design",
        "already_enabled",
        "requires_abo_delta_action_library_function_recovery",
    }
    if status not in supported_statuses:
        raise CpqSettingsError(f"CPQ preflight returned an unsupported status: {status!r}.")

    cpq_abo_disabled = [
        code for code in CPQ_ABO_PREREQUISITE_FEATURE_CODES if not feature_states[code]
    ]
    if status in {"already_enabled", "requires_abo_delta_action_library_function_recovery"}:
        if cpq_abo_disabled:
            return {
                "status": "blocked",
                "stage": "preflight_reconciliation",
                "feature_states": feature_states,
                "cpq_preflight": cpq_plan,
                "blockers": [
                    "Fusion ABO is already enabled in CPQ but prerequisite Fusion opt-in evidence is not fully enabled: "
                    + ", ".join(cpq_abo_disabled)
                    + ". Reconcile the target environment; do not change either system automatically."
                ],
                "next_action": "Investigate the inconsistent environment state and rerun the read-only preflight.",
            }
    if cpq_abo_disabled:
        return build_prerequisite_update_handoff(
            cpq_plan,
            feature_states,
            prerequisite_feature_codes=CPQ_ABO_PREREQUISITE_FEATURE_CODES,
            status="requires_cpq_abo_prerequisite_update",
            stage="cpq_abo_optin_handoff",
            readiness_label="CPQ/ABO prerequisite",
        )

    subscription_coverage_disabled = [
        code
        for code in SUBSCRIPTION_COVERAGE_PREREQUISITE_FEATURE_CODES
        if not feature_states[code]
    ]
    if subscription_coverage_disabled:
        return build_prerequisite_update_handoff(
            cpq_plan,
            feature_states,
            prerequisite_feature_codes=SUBSCRIPTION_COVERAGE_PREREQUISITE_FEATURE_CODES,
            status="requires_subscription_coverage_prerequisite_update",
            stage="subscription_coverage_optin_handoff",
            readiness_label="Subscription/Coverage prerequisite",
        )

    if status in {
        "already_enabled",
        "requires_abo_delta_action_library_function_recovery",
    }:
        if status == "requires_abo_delta_action_library_function_recovery":
            return {
                "status": "requires_abo_delta_action_library_function_recovery",
                "stage": "cpq_function_recovery",
                "feature_states": feature_states,
                "cpq_preflight": cpq_plan,
                "next_action": (
                    "Build the fixed function-only CPQ Settings recovery preview, obtain current exact "
                    "approval, then invoke the approved executor once. Do not replay the process-save or "
                    "Fusion ABO enable PATCH."
                ),
            }
        return {
            "status": "already_configured",
            "stage": "preflight_complete",
            "feature_states": feature_states,
            "cpq_preflight": cpq_plan,
            "next_action": "Record the verified state in the project workspace; no CPQ write is required.",
        }

    return {
        "status": "ready_for_cpq_write_route",
        "stage": "preflight_complete",
        "feature_states": feature_states,
        "cpq_preflight": cpq_plan,
        "next_action": "Build the fixed CPQ Settings write preview, obtain current exact approval, then invoke the approved CPQ Settings write executor once.",
    }


def _read_feature_state_evidence(path_value: str) -> dict[str, Any]:
    path = Path(path_value)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CpqSettingsError("Unable to read Fusion ABO feature-state evidence file.") from exc
    except json.JSONDecodeError as exc:
        raise CpqSettingsError("Fusion ABO feature-state evidence file is not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise CpqSettingsError("Fusion ABO feature-state evidence file must contain a JSON object.")
    return payload


def _client_from_args(args: argparse.Namespace) -> CpqSettingsClient:
    return CpqSettingsClient(client_from_args(args))


def _print_result(result: Mapping[str, Any]) -> None:
    print(json.dumps(result, indent=2, sort_keys=True))


def _process_selection_required_result(args: argparse.Namespace) -> dict[str, str] | None:
    """Require an explicit process choice before standalone CPQ reads begin."""

    if args.command not in {"plan", "preflight"} or args.use_default_process:
        return None
    process_variable_name = args.process_variable_name
    if isinstance(process_variable_name, str) and process_variable_name.strip():
        return None
    return {
        "status": "requires_process_selection",
        "prompt": (
            "Please provide the CPQ Standard Process variable name. If you want to use "
            "the default, reply 'use default' and I will use 'oraclecpqo'."
        ),
        "next_action": (
            "Provide --process-variable-name with the exact Standard Process variable name, "
            "or explicitly select --use-default-process."
        ),
        "side_effects": "No CPQ request was made.",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read and validate CPQ Commerce Settings for Fusion ABO. This command does not write CPQ settings."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    read = subparsers.add_parser("read", help="Read the safe Fusion ABO Commerce Settings summary.")
    add_connection_arguments(read)
    read_library_function = subparsers.add_parser(
        "read-abo-delta-action-library-function",
        help="Read the fixed CPQ Commerce Library Function required by Fusion ABO.",
    )
    add_connection_arguments(read_library_function)
    verify = subparsers.add_parser("verify-process", help="Verify that one CPQ process is a Standard Process.")
    verify.add_argument("--process-variable-name", required=True)
    add_connection_arguments(verify)
    plan = subparsers.add_parser("plan", help="Build a read-only CPQ readiness plan for a future CPQ write.")
    plan.add_argument(
        "--process-variable-name",
        help="Exact CPQ Standard Process variable name. Omit only when --use-default-process is selected.",
    )
    plan.add_argument(
        "--use-default-process",
        action="store_true",
        help="Explicitly select the CPQ Dev default process variable name, oraclecpqo, for verification.",
    )
    add_connection_arguments(plan)
    preflight = subparsers.add_parser(
        "preflight",
        help="Combine read-only CPQ checks with supplied fresh Fusion opt-in evidence; never writes either system.",
    )
    preflight.add_argument(
        "--process-variable-name",
        help="Exact CPQ Standard Process variable name. Omit only when --use-default-process is selected.",
    )
    preflight.add_argument(
        "--use-default-process",
        action="store_true",
        help="Explicitly select the CPQ Dev default process variable name, oraclecpqo, for verification.",
    )
    preflight.add_argument(
        "--feature-state-evidence",
        required=True,
        help="Path to the exact fresh Fusion featureStates JSON response for all required Fusion ABO prerequisites.",
    )
    add_connection_arguments(preflight)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    selection_required = _process_selection_required_result(args)
    if selection_required is not None:
        _print_result(selection_required)
        return 0
    client = _client_from_args(args)
    if args.command == "read":
        _print_result({"status": "success", "commerce_settings": client.read_commerce_settings().as_dict()})
        return 0
    if args.command == "read-abo-delta-action-library-function":
        _print_result(
            {
                "status": "success",
                "abo_delta_action_library_function": (
                    client.read_abo_delta_action_library_function().as_dict()
                ),
            }
        )
        return 0
    if args.command == "verify-process":
        verification = client.verify_standard_process(args.process_variable_name)
        _print_result({"status": "success", "process_validation": verification.as_dict()})
        return 0
    if args.command == "plan":
        _print_result(client.plan_fusion_abo_write(args.process_variable_name))
        return 0
    if args.command == "preflight":
        _print_result(
            build_fusion_abo_preflight(
                client,
                args.process_variable_name,
                _read_feature_state_evidence(args.feature_state_evidence),
            )
        )
        return 0
    raise AssertionError(f"Unhandled command: {args.command}")


def _safe_cli_failure_result(error: CpqClientError) -> dict[str, Any]:
    """Render a bounded CLI error without exposing arbitrary exception text."""

    status_code = getattr(error, "status_code", None)
    if isinstance(status_code, int):
        message = f"CPQ returned HTTP {status_code} while completing the requested read or validation."
    else:
        message = "CPQ read or validation could not complete safely."
    result: dict[str, Any] = {"status": "failed", "message": message}
    details_are_sanitized = isinstance(error, CpqHttpError) or isinstance(
        error.__cause__, CpqHttpError
    )
    if details_are_sanitized:
        provider_message = getattr(error, "provider_message", None)
        provider_code = getattr(error, "provider_code", None)
        if isinstance(provider_message, str) and provider_message:
            result["provider_message"] = provider_message
        if isinstance(provider_code, str) and provider_code:
            result["provider_error_code"] = provider_code
    return result


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CpqClientError as exc:
        print(json.dumps(_safe_cli_failure_result(exc)), file=sys.stderr)
        raise SystemExit(1)
