#!/usr/bin/env python3
"""Build the task-local, non-executable CPQ Settings plan for Fusion ABO.

This module deliberately does not import an HTTP client or credential helper.
It turns a fresh, successful read-only preflight into a deterministic contract
that a future approved CPQ Settings write executor may execute.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

from fusion_abo_prerequisites import FUSION_ABO_PREREQUISITE_FEATURE_CODES


SKILL_ID = "cx.configure-price-quote.quoting.enable-fusion-asset-based-ordering"
PLAN_VERSION = "1.5"
CPQ_COMMERCE_SETTINGS_PATH = "/rest/v19/commerceUISettings"
CPQ_FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_PATH = (
    "/rest/v19/settings/COMMERCE/defineFieldsForModifyActionFunction"
)
CPQ_COMMERCE_SETTINGS_TYPE = "COMMERCE"
CPQ_COMMERCE_SETTINGS_BUSINESS_OBJECT = "CpqCommerceSettings"
FUSION_ABO_PROCESS_KEY = "commerceProcessVarNameForEnabledFusionABO"
FUSION_ABO_ENABLED_KEY = "enableFusionABO"
FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_KEY = "defineFieldsForModifyActionFunction"
FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_VALUE = "_s_getAttributesForABODeltaActionCalculation"
CPQ_DEFAULT_FUSION_ABO_PROCESS_VARIABLE_NAME = "oraclecpqo"
PROCESS_SELECTION_SOURCE_EXPLICIT = "explicit"
PROCESS_SELECTION_SOURCE_CPQ_DEFAULT = "cpq_default"


class CpqSettingsWritePlanError(ValueError):
    """Raised when a preflight result cannot safely produce a CPQ write plan."""


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CpqSettingsWritePlanError(f"{field_name} must be an object.")
    return value


def _require_nonblank_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CpqSettingsWritePlanError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _require_no(value: Any, field_name: str) -> None:
    if not isinstance(value, str) or value.casefold() != "no":
        raise CpqSettingsWritePlanError(f"{field_name} must be No before a Fusion ABO write plan is created.")


def _validate_process_variable_name(value: Any) -> str:
    process_name = _require_nonblank_string(value, "process_validation.process_variable_name")
    if len(process_name) > 255 or any(character in process_name for character in "\x00\r\n/\\"):
        raise CpqSettingsWritePlanError("process_validation.process_variable_name is malformed.")
    return process_name


def _validate_process_selection(value: Any, process_name: str) -> dict[str, Any]:
    """Require that CPQ Dev defaulting is disclosed and still independently verified."""

    selection = _require_mapping(value, "cpq_preflight.process_selection")
    if selection.get("resolved_process_variable_name") != process_name:
        raise CpqSettingsWritePlanError(
            "process_selection.resolved_process_variable_name must match the verified CPQ process."
        )
    source = selection.get("selection_source")
    requested_name = selection.get("requested_process_variable_name")
    disclosure_required = selection.get("requires_default_disclosure")
    default_disclosure = selection.get("default_disclosure")
    if source == PROCESS_SELECTION_SOURCE_EXPLICIT:
        if requested_name != process_name or disclosure_required is not False or default_disclosure is not None:
            raise CpqSettingsWritePlanError(
                "An explicit process selection must preserve the supplied process and cannot carry a default disclosure."
            )
    elif source == PROCESS_SELECTION_SOURCE_CPQ_DEFAULT:
        if (
            requested_name is not None
            or process_name.casefold() != CPQ_DEFAULT_FUSION_ABO_PROCESS_VARIABLE_NAME
            or disclosure_required is not True
            or not isinstance(default_disclosure, str)
            or not default_disclosure.strip()
        ):
            raise CpqSettingsWritePlanError(
                "A CPQ default process selection must be oraclecpqo, explicitly disclosed, and verified."
            )
    else:
        raise CpqSettingsWritePlanError(
            "process_selection.selection_source must be explicit or cpq_default."
        )
    return {
        "requested_process_variable_name": requested_name,
        "resolved_process_variable_name": process_name,
        "selection_source": source,
        "requires_default_disclosure": disclosure_required,
        "default_disclosure": default_disclosure,
    }


def _validate_feature_states(value: Any) -> None:
    states = _require_mapping(value, "feature_states")
    expected = set(FUSION_ABO_PREREQUISITE_FEATURE_CODES)
    if set(states) != expected:
        raise CpqSettingsWritePlanError(
            "feature_states must contain exactly the required Fusion ABO prerequisite feature codes."
        )
    for feature_code in FUSION_ABO_PREREQUISITE_FEATURE_CODES:
        if states[feature_code] is not True:
            raise CpqSettingsWritePlanError(
                f"Fusion prerequisite {feature_code} must be verified true before a CPQ write plan is created."
            )


def _require_ready_preflight(preflight: Mapping[str, Any]) -> tuple[str, dict[str, Any], Mapping[str, Any]]:
    if preflight.get("status") != "ready_for_cpq_write_route":
        raise CpqSettingsWritePlanError(
            "fusion_abo_preflight_result must have status ready_for_cpq_write_route."
        )
    _validate_feature_states(preflight.get("feature_states"))
    cpq_preflight = _require_mapping(preflight.get("cpq_preflight"), "cpq_preflight")
    if cpq_preflight.get("status") != "ready_for_cpq_write_design":
        raise CpqSettingsWritePlanError(
            "cpq_preflight.status must be ready_for_cpq_write_design."
        )

    commerce_settings = _require_mapping(
        cpq_preflight.get("commerce_settings"), "cpq_preflight.commerce_settings"
    )
    _require_no(commerce_settings.get("enable_standard_abo"), "enable_standard_abo")
    _require_no(commerce_settings.get("enable_fusion_abo"), "enable_fusion_abo")

    process_validation = _require_mapping(
        cpq_preflight.get("process_validation"), "cpq_preflight.process_validation"
    )
    if process_validation.get("exists") is not True:
        raise CpqSettingsWritePlanError("The selected CPQ process must exist.")
    if process_validation.get("is_standard_process") is not True:
        raise CpqSettingsWritePlanError("The selected CPQ process must be a Standard Process.")
    process_type = process_validation.get("process_type")
    if type(process_type) is not int or process_type != 0:
        raise CpqSettingsWritePlanError("The selected CPQ process must have processType 0.")
    process_name = _validate_process_variable_name(process_validation.get("process_variable_name"))
    process_selection = _validate_process_selection(
        cpq_preflight.get("process_selection"), process_name
    )
    return process_name, process_selection, cpq_preflight


def _require_function_recovery_preflight(
    preflight: Mapping[str, Any],
) -> tuple[str, dict[str, Any], Mapping[str, Any], Mapping[str, Any]]:
    """Validate the one safe recovery state without replaying ABO enablement.

    A setting-only recovery is allowed only after the normal Fusion ABO state
    is already verified.  It deliberately cannot save another process or send
    another ``enableFusionABO`` PATCH.
    """

    if preflight.get("status") != "requires_abo_delta_action_library_function_recovery":
        raise CpqSettingsWritePlanError(
            "fusion_abo_preflight_result must require ABO Delta Action Library Function recovery."
        )
    _validate_feature_states(preflight.get("feature_states"))
    cpq_preflight = _require_mapping(preflight.get("cpq_preflight"), "cpq_preflight")
    if cpq_preflight.get("status") != "requires_abo_delta_action_library_function_recovery":
        raise CpqSettingsWritePlanError(
            "cpq_preflight.status must require ABO Delta Action Library Function recovery."
        )
    commerce_settings = _require_mapping(
        cpq_preflight.get("commerce_settings"), "cpq_preflight.commerce_settings"
    )
    _require_no(commerce_settings.get("enable_standard_abo"), "enable_standard_abo")
    fusion_abo = commerce_settings.get("enable_fusion_abo")
    if not isinstance(fusion_abo, str) or fusion_abo.casefold() != "yes":
        raise CpqSettingsWritePlanError(
            "enable_fusion_abo must already be Yes before a function-only recovery plan is created."
        )

    process_validation = _require_mapping(
        cpq_preflight.get("process_validation"), "cpq_preflight.process_validation"
    )
    if (
        process_validation.get("exists") is not True
        or process_validation.get("is_standard_process") is not True
        or process_validation.get("process_type") != 0
    ):
        raise CpqSettingsWritePlanError(
            "The recovery plan requires the existing selected CPQ Standard Process with processType 0."
        )
    process_name = _validate_process_variable_name(process_validation.get("process_variable_name"))
    process_selection = _validate_process_selection(
        cpq_preflight.get("process_selection"), process_name
    )
    if commerce_settings.get("fusion_abo_process_variable_name") != process_name:
        raise CpqSettingsWritePlanError(
            "The recovery plan requires Fusion ABO to remain enabled for the verified selected process."
        )
    library_function = _require_mapping(
        cpq_preflight.get("abo_delta_action_library_function"),
        "cpq_preflight.abo_delta_action_library_function",
    )
    if library_function.get("is_expected") is not False:
        raise CpqSettingsWritePlanError(
            "A function-only recovery plan is permitted only when the fixed ABO Delta Action Library Function is missing or different."
        )
    return process_name, process_selection, cpq_preflight, library_function


def _library_function_payload() -> dict[str, Any]:
    """Return the sole static library-function mutation permitted for Fusion ABO."""

    return {
        "items": [
            {
                "type": CPQ_COMMERCE_SETTINGS_TYPE,
                "key": FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_KEY,
                "value": FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_VALUE,
            }
        ]
    }


def _library_function_readback_operation(
    *, sequence: int, legacy_failure_guidance: bool = False,
) -> dict[str, Any]:
    """Return the immutable readback contract for the ABO function."""

    return {
        "id": "verify_abo_delta_action_library_function",
        "sequence": sequence,
        "operation_type": "readback",
        "method": "GET",
        "endpoint_path": CPQ_FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_PATH,
        "expected_setting": {
            "type": CPQ_COMMERCE_SETTINGS_TYPE,
            "key": FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_KEY,
            "value": FUSION_ABO_DELTA_ACTION_LIBRARY_FUNCTION_VALUE,
        },
        "postcondition": {
            "description": (
                "The exact ABO Delta Action Commerce Library Function is confirmed before ESS "
                "synchronization is permitted."
            ),
            "next_operation": None,
        },
        "retry_policy": (
            "Use the executor's bounded read-only retry policy only; never replay the preceding PATCH automatically."
        ),
        "on_failure": (
            "Treat the outcome as indeterminate. Reconcile the exact CPQ setting and require a new approved recovery plan."
            if legacy_failure_guidance else
            "Treat the outcome as indeterminate. Reconcile the exact CPQ setting; request a new CPQ approval only if another CPQ write is required."
        ),
    }


def _library_function_operations(
    *, starting_sequence: int, legacy_failure_guidance: bool = False,
) -> list[dict[str, Any]]:
    """Return the immutable configure/readback pair for the ABO function."""

    return [
        {
            "id": "configure_abo_delta_action_library_function",
            "sequence": starting_sequence,
            "operation_type": "mutation",
            "execution_route": "core.data-loader",
            "business_object": CPQ_COMMERCE_SETTINGS_BUSINESS_OBJECT,
            "rest_action": "PATCH",
            "setting": _library_function_payload()["items"][0],
            "postcondition": {
                "description": (
                    "The fixed Commerce Library Function used for Fusion ABO delta action-code "
                    "calculation is saved before downstream synchronization begins."
                ),
                "next_operation": "verify_abo_delta_action_library_function",
            },
            "retry_policy": "Do not retry automatically.",
            "on_failure": (
                "Stop. Do not submit ESS or Adaptive Search work. Reconcile the current CPQ setting "
                + ("through the exact approved read route and require a new approval."
                   if legacy_failure_guidance else
                   "through the exact approved read route; request a new CPQ approval only if another CPQ write is required.")
            ),
        },
        _library_function_readback_operation(
            sequence=starting_sequence + 1,
            legacy_failure_guidance=legacy_failure_guidance,
        ),
    ]


def build_fusion_abo_cpq_settings_write_plan(
    fusion_abo_preflight_result: Mapping[str, Any],
    *,
    legacy_failure_guidance: bool = False,
) -> dict[str, Any]:
    """Return a deterministic, non-executable ordered CPQ Settings plan.

    The caller must pass the full, fresh output of
    ``build_fusion_abo_preflight``. The return value is intentionally suitable
    for a future CPQ Settings write executor, but this function does not select
    or invoke that executor.
    """

    preflight = _require_mapping(fusion_abo_preflight_result, "fusion_abo_preflight_result")
    if not isinstance(legacy_failure_guidance, bool):
        raise CpqSettingsWritePlanError("legacy_failure_guidance must be a boolean.")
    preflight_status = preflight.get("status")
    is_function_only_recovery = (
        preflight_status == "requires_abo_delta_action_library_function_recovery"
    )
    if is_function_only_recovery:
        process_name, process_selection, cpq_preflight, current_library_function = (
            _require_function_recovery_preflight(preflight)
        )
    else:
        process_name, process_selection, cpq_preflight = _require_ready_preflight(preflight)
        current_library_function = None
    enablement_settings = [
        {
            "type": CPQ_COMMERCE_SETTINGS_TYPE,
            "key": FUSION_ABO_PROCESS_KEY,
            "value": process_name,
        },
        {
            "type": CPQ_COMMERCE_SETTINGS_TYPE,
            "key": FUSION_ABO_ENABLED_KEY,
            "value": "Yes",
        },
        _library_function_payload()["items"][0],
    ]

    if is_function_only_recovery:
        operations = _library_function_operations(
            starting_sequence=1, legacy_failure_guidance=legacy_failure_guidance
        )
        write_scope = "abo_delta_action_library_function_recovery_only"
        pre_execution_rechecks = [
            "Reread all required Fusion prerequisite feature states through the existing governed shared opt-in workflow.",
            "Reread CPQ Commerce settings and verify Standard ABO remains No, Fusion ABO remains Yes, and the exact selected Standard Process remains configured.",
            "Reverify the selected CPQ process exists and has processType 0.",
            "Reread the exact ABO Delta Action Library Function setting and confirm it is still missing or different before the one fixed Data Loader import.",
        ]
    else:
        operations = [
            {
                "id": "configure_fusion_abo_settings",
                "sequence": 1,
                "operation_type": "mutation",
                "execution_route": "core.data-loader",
                "business_object": CPQ_COMMERCE_SETTINGS_BUSINESS_OBJECT,
                "rest_action": "PATCH",
                "settings": enablement_settings,
                "postcondition": {
                    "description": (
                        "The selected Standard Process, Fusion ABO enablement, and fixed delta-action "
                        "Library Function are submitted together in one immutable CPQ Settings payload."
                    ),
                    "next_operation": "verify_fusion_abo_enabled",
                },
                "retry_policy": "Do not retry automatically.",
                "on_failure": (
                    "Stop. The single batch may have applied partially; do not retry or roll back "
                    + ("automatically. Reconcile all three exact settings and require a new approval."
                       if legacy_failure_guidance else
                       "automatically. Reconcile all three exact settings; request a new CPQ approval only if another CPQ write is required.")
                ),
            },
            {
                "id": "verify_fusion_abo_enabled",
                "sequence": 2,
                "operation_type": "readback",
                "method": "GET",
                "endpoint_path": CPQ_COMMERCE_SETTINGS_PATH,
                "expected_commerce_settings": {
                    "enableFusionABO": "Yes",
                    "commerceProcessVarNameForEnabledFusionABO": process_name,
                },
                "postcondition": {
                    "description": "Fusion ABO is Yes and CPQ still reports the same selected Standard Process.",
                    "next_operation": "verify_abo_delta_action_library_function",
                },
                "retry_policy": "Use the executor's bounded read-only retry policy only; never replay the preceding PATCH automatically.",
                "on_failure": (
                    "Treat the outcome as indeterminate. Reconcile CPQ state through approved reads and require a new approved recovery plan."
                    if legacy_failure_guidance else
                    "Treat the outcome as indeterminate. Reconcile CPQ state through approved reads; request a new CPQ approval only if another CPQ write is required."
                ),
            },
            _library_function_readback_operation(
                sequence=3, legacy_failure_guidance=legacy_failure_guidance
            ),
        ]
        write_scope = "fusion_abo_enablement_and_abo_delta_action_library_function"
        pre_execution_rechecks = [
            "Reread all required Fusion prerequisite feature states through the existing governed shared opt-in workflow.",
            "Reread CPQ Commerce settings and verify Standard ABO remains No and Fusion ABO remains No.",
            "Reverify the selected CPQ process exists and has processType 0.",
        ]

    return {
        "status": "planned_requires_approved_executor",
        "skill_id": SKILL_ID,
        "plan_version": PLAN_VERSION,
        "operation": "enable_fusion_asset_based_ordering",
        "execution_mode": "plan_only",
        "write_scope": write_scope,
        "preflight_status": preflight_status,
        "validated_process_variable_name": process_name,
        "process_selection": process_selection,
        "execution_boundary": {
            "live_execution_allowed": False,
            "required_executor": "Approved CPQ Commerce Settings write executor",
            "reason": "This planner does not authenticate or execute CPQ writes. The route must be previewed and explicitly approved before execution.",
        },
        "approval_gate": {
            "required": True,
            "timing": "immediately_before_execution",
            "approval_must_bind": [
                "target_environment_identity",
                "verified_standard_process_variable_name",
                "process_selection_and_default_disclosure",
                "current_cpq_and_fusion_preflight_state",
                "all_ordered_operations_and_payloads",
            ],
        },
        "pre_execution_rechecks": pre_execution_rechecks,
        "operations": operations,
        "failure_policy": {
            "mutation_attempts_per_approval": 1,
            "automatic_mutation_retry": False,
            "automatic_rollback": False,
            "partial_failure_action": (
                "Stop after a failed or indeterminate batch or readback, collect redacted diagnostics and verified readback state, then require a new approved recovery plan."
                if legacy_failure_guidance else
                "Stop after a failed or indeterminate batch or readback and reconcile through read-only evidence. Request a new CPQ approval only if another CPQ write is required."
            ),
        },
        "source_preflight_summary": {
            "cpq_preflight_status": cpq_preflight["status"],
            "feature_state_codes": list(FUSION_ABO_PREREQUISITE_FEATURE_CODES),
            **(
                {"abo_delta_action_library_function": dict(current_library_function)}
                if current_library_function is not None
                else {}
            ),
        },
    }


def _read_json_object(path_value: str) -> dict[str, Any]:
    path = Path(path_value)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CpqSettingsWritePlanError("Unable to read the Fusion ABO preflight-result file.") from exc
    except json.JSONDecodeError as exc:
        raise CpqSettingsWritePlanError("The Fusion ABO preflight-result file is not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise CpqSettingsWritePlanError("The Fusion ABO preflight-result file must contain a JSON object.")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a plan-only CPQ Settings write sequence for Fusion ABO. No network or CPQ write is performed."
    )
    parser.add_argument(
        "--preflight-result",
        required=True,
        help="Path to a fresh read-only Fusion ABO preflight JSON result.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = build_fusion_abo_cpq_settings_write_plan(_read_json_object(args.preflight_result))
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CpqSettingsWritePlanError as exc:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "failure_class": "input_validation",
                    "message": str(exc),
                }
            ),
            file=sys.stderr,
        )
        raise SystemExit(1)
