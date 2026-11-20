#!/usr/bin/env python3
"""Enforce Manage Control Budgets validation gates before ZIP creation.

The task skill supplies independently evaluated check outcomes. This module
checks their coverage and dependencies, retains every issue in the active unit,
and prevents child-rule validation until every requested budget passes. The
Supplemental, Revenue Funding and Override Rule groups then collect findings independently.
It does not perform Fusion lookups or replace the task-specific check contracts.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping


BUDGET_SECTIONS = ("header", "budget_segments", "segment_trees")
RULE_SECTIONS = (
    "rule_header",
    "budget_segment_filters",
    "additional_segment_filters",
    "transaction_attribute_filters",
)
REVENUE_RULE_SECTIONS = ("rule_header", "funding_targets", "revenue_source_segments")
OVERRIDE_RULE_SECTIONS = (
    "rule_header", "transaction_types", "journal_conditions", "user_assignments",
)
STATUSES = {"passed", "failed", "not_evaluated", "deferred_to_fusion"}
FUSION_DEFERRALS = {
    "header": {"calendar_period_target", "rate_type_target", "existing_object_state"},
    "budget_segments": {"hierarchy_relationship_target"},
    "segment_trees": {"tree_version_target", "hierarchy_relationship_target"},
    "rule_header": {"business_unit_target"},
    "budget_segment_filters": {"specific_segment_value_membership"},
    "additional_segment_filters": {"specific_segment_value_membership", "tree_version_target"},
    "transaction_attribute_filters": set(),
}
REVENUE_FUSION_DEFERRALS = {
    "rule_header": {"budget_scenario_membership"},
    "funding_targets": {"target_budget_account_membership"},
    "revenue_source_segments": {"specific_segment_value_membership"},
}
OVERRIDE_FUSION_DEFERRALS = {
    "rule_header": set(),
    "transaction_types": set(),
    "journal_conditions": {"journal_source_membership", "journal_category_membership"},
    "user_assignments": {"override_user_membership"},
}
FAILED_CHECK_DEPENDENTS = {
    ("control_budget", "budget_segments",
     "Detail/Master SourceSegmentColumnName is the `segmentColumnName` returned for the resolved ledger's exact SourceSegmentName"):
        "SourceSegmentColumnName is resolved and KeySegmentColumnName follows the display sequence",
    ("supplemental_rules", "additional_segment_filters",
     "Budget versus additional segment membership"):
        "Additional segment filter identity",
}
DEPENDENCY_PATH_FIELDS = {
    "sourcesegmentname", "sourcesegmentcolumnname", "keysegmentcolumnname",
    "segmentname", "segment", "filterconditioncode", "segmentcolumnname",
}


class ValidationContractError(ValueError):
    """A validation report cannot prove complete, ordered unit evaluation."""


def _nonblank(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationContractError(f"{label} must be nonblank text")
    return value


def _issue(
    *,
    unit: str,
    path: str,
    check: str,
    message: str,
    rule_name: str | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "unit": unit,
        "path": path,
        "check": check,
        "message": message,
    }
    if rule_name is not None:
        result["ruleName"] = rule_name
    for key in ("code", "suppliedValue", "evidence", "failureClass", "recommendedAction"):
        if extra is not None and key in extra:
            if key in {"code", "failureClass", "recommendedAction"}:
                _nonblank(extra[key], f"issue {key}")
            result[key] = extra[key]
    return result


def _input_scope(path: str) -> str:
    """Compare field paths for the same input, retaining named selectors."""
    normalized = re.sub(r"\[(\d+)\]", r".\1", path)
    parent, separator, field = normalized.rpartition(".")
    if separator and (
        field.casefold() in DEPENDENCY_PATH_FIELDS
        or field.casefold() in {"identity", "code"} and parent.rsplit(".", 1)[-1].isdigit()
    ):
        return parent
    return normalized


def _require_failed_check_dependents(checks: list[dict[str, Any]], unit: str) -> None:
    # These task-defined prerequisites cannot disappear from a blocked report.
    # Require observed outcomes from the caller; never manufacture skipped checks.
    for prerequisite in checks:
        if prerequisite["status"] != "failed":
            continue
        label = FAILED_CHECK_DEPENDENTS.get(
            (unit, prerequisite["section"], prerequisite["check"])
        )
        if label is None:
            continue
        for failure in prerequisite["issues"]:
            scope = _input_scope(failure.get("path", prerequisite["path"]))
            if not any(
                dependent["section"] == prerequisite["section"]
                and dependent["check"] == label
                and prerequisite["id"] in dependent.get("prerequisites", [])
                and _input_scope(dependent["path"]) == scope
                for dependent in checks
            ):
                raise ValidationContractError(
                    f"Check {prerequisite['id']} at {scope} requires an explicit "
                    f"'{label}' result with this prerequisite; report it as "
                    "not_evaluated when the prerequisite fails"
                )


def _validate_checks(
    checks: Any,
    *,
    unit: str,
    sections: tuple[str, ...],
    path_prefix: str,
    rule_name: str | None = None,
    deferrals: Mapping[str, set[str]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(checks, list):
        raise ValidationContractError(f"{path_prefix}.checks must be an array")

    ordered: list[tuple[int, dict[str, Any]]] = []
    seen_ids: set[str] = set()
    covered: set[str] = set()
    for index, value in enumerate(checks):
        if not isinstance(value, dict):
            raise ValidationContractError(f"{path_prefix}.checks[{index}] must be an object")
        identifier = _nonblank(value.get("id"), "check id")
        section = _nonblank(value.get("section"), "check section")
        if section not in sections:
            raise ValidationContractError(f"Unknown {unit} section: {section}")
        _nonblank(value.get("path"), "check path")
        _nonblank(value.get("check"), "Check label")
        if identifier in seen_ids:
            raise ValidationContractError(f"Duplicate check id: {identifier}")
        if value.get("status") not in STATUSES:
            raise ValidationContractError(f"Invalid status for {identifier}")
        prerequisites = value.get("prerequisites", [])
        if not isinstance(prerequisites, list) or not all(
            isinstance(item, str) and item for item in prerequisites
        ):
            raise ValidationContractError(f"Invalid prerequisites for {identifier}")
        if value.get("status") == "deferred_to_fusion":
            _nonblank(value.get("basis"), f"Fusion deferral basis for {identifier}")
            allowed_deferrals = deferrals if deferrals is not None else FUSION_DEFERRALS
            if value.get("deferralId") not in allowed_deferrals[section]:
                raise ValidationContractError(
                    f"Check {identifier} cannot defer {section} validation to Fusion"
                )
        seen_ids.add(identifier)
        covered.add(section)
        ordered.append((index, value))

    # The first unit must finish as a whole. A missing section is a blocker,
    # including when the section has no user-selected items.
    issues_by_section: dict[str, list[dict[str, Any]]] = {section: [] for section in sections}
    for section in sections:
        if section in covered:
            continue
        issues_by_section[section].append(_issue(
            unit=unit,
            path=f"{path_prefix}.{section}",
            check="Validation coverage",
            message=f"No validation result was supplied for {section}.",
            rule_name=rule_name,
            extra={"failureClass": "input validation"},
        ))

    ordered.sort(key=lambda pair: (sections.index(pair[1]["section"]), pair[0]))
    statuses: dict[str, str] = {}
    normalized: list[dict[str, Any]] = []
    for _, value in ordered:
        identifier = value["id"]
        prerequisites = value.get("prerequisites", [])
        unknown = [item for item in prerequisites if item not in seen_ids]
        if unknown:
            raise ValidationContractError(
                f"Check {identifier} references unknown prerequisite(s): {', '.join(unknown)}"
            )
        unavailable = [
            item for item in prerequisites if statuses.get(item) != "passed"
        ]
        status = value["status"]
        if unavailable and status != "not_evaluated":
            raise ValidationContractError(
                f"Check {identifier} must be not_evaluated until prerequisite(s) pass: "
                + ", ".join(unavailable)
            )
        if status == "not_evaluated" and not unavailable:
            _nonblank(value.get("reason"), f"Not-evaluated reason for {identifier}")
        if status != "failed" and value.get("issues"):
            raise ValidationContractError(
                f"Nonfailed check {identifier} cannot include error issues"
            )
        if status == "failed":
            failures = value.get("issues")
            if not isinstance(failures, list) or not failures:
                raise ValidationContractError(f"Failed check {identifier} needs issue(s)")
            for failure in failures:
                if not isinstance(failure, dict):
                    raise ValidationContractError(f"Issue for {identifier} must be an object")
                if (
                    value["check"] in {"Transaction attribute type set", "Transaction attribute values"}
                    or failure.get("failureClass") == "reference lookup"
                ) and not isinstance(failure.get("evidence"), dict):
                    raise ValidationContractError(
                        f"Failed lookup check {identifier} must retain sanitized evidence"
                    )
                issues_by_section[value["section"]].append(
                    _issue(
                        unit=unit,
                        path=_nonblank(failure.get("path", value["path"]), "issue path"),
                        check=value["check"],
                        message=_nonblank(failure.get("message"), "issue message"),
                        rule_name=rule_name,
                        extra=failure,
                    )
                )
        elif status == "not_evaluated":
            reason = value.get("reason") or (
                "Prerequisite check(s) did not pass: " + ", ".join(unavailable)
            )
            issues_by_section[value["section"]].append(
                _issue(
                    unit=unit,
                    path=value["path"],
                    check=value["check"],
                    message=reason,
                    rule_name=rule_name,
                    extra={"code": "not_evaluated", "failureClass": "dependency"},
                )
            )
        statuses[identifier] = status
        normalized.append(
            {
                "id": identifier,
                "section": value["section"],
                "path": value["path"],
                "check": value["check"],
                "status": status,
                "prerequisites": prerequisites,
                **({"basis": value["basis"]} if status == "deferred_to_fusion" else {}),
            }
        )

    _require_failed_check_dependents([value for _, value in ordered], unit)

    for section in sections:
        if not any(
            item["section"] == section and item["status"] != "deferred_to_fusion"
            for item in normalized
        ):
            issues_by_section[section].append(_issue(
                unit=unit,
                path=f"{path_prefix}.{section}",
                check="Validation coverage",
                message=f"Only Fusion-deferred checks were supplied for {section}.",
                rule_name=rule_name,
                extra={"failureClass": "dependency"},
            ))
    issues = [issue for section in sections for issue in issues_by_section[section]]
    return normalized, issues


def _primary_reason(issues: list[dict[str, Any]]) -> str | None:
    # Skipped dependent checks are visible in the report, but the first
    # failed validation (not its skipped consequence) owns the reason.
    primary = next(
        (item for item in issues if item.get("code") != "not_evaluated"),
        issues[0] if issues else None,
    )
    return "task_rule:" + primary["check"] if primary else None


def _budget_result(
    payload: Mapping[str, Any], *, path_prefix: str, budget_index: int | None = None,
) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    raw_budget_name = payload.get("controlBudget")
    budget_name = raw_budget_name if isinstance(raw_budget_name, str) else ""
    budget_checks, budget_issues = _validate_checks(
        payload.get("controlBudgetChecks"),
        unit="control_budget",
        sections=BUDGET_SECTIONS,
        path_prefix=path_prefix,
    )
    if not budget_name.strip():
        budget_issues.insert(0, _issue(
            unit="control_budget", path=f"{path_prefix}.header.name",
            check="Control budget identity", message="Control budget name is required.",
            extra={"failureClass": "input validation"},
        ))
    if budget_index is not None:
        budget_label = budget_name if budget_name.strip() else f"<budget {budget_index + 1}>"
        for issue in budget_issues:
            issue["controlBudgetName"] = budget_label
            issue["controlBudgetIndex"] = budget_index + 1
    else:
        budget_label = budget_name
    budget_status = "blocked" if budget_issues else "passed"
    unit = {"unit": "control_budget", "status": budget_status, "checks": budget_checks}
    if budget_index is not None:
        unit["controlBudgetName"] = budget_label
        unit["controlBudgetIndex"] = budget_index + 1
    return budget_label, unit, budget_issues


def _append_rule_units(
    report: dict[str, Any], rules: Any, *, path_prefix: str,
    budget_name: str | None = None, budget_index: int | None = None,
    unit_name: str = "supplemental_rules",
    sections: tuple[str, ...] = RULE_SECTIONS,
    deferrals: Mapping[str, set[str]] | None = None,
) -> bool:
    if not isinstance(rules, list):
        raise ValidationContractError(f"{path_prefix} must be an array")
    if not rules:
        return False

    rule_names: set[str] = set()
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise ValidationContractError(f"{path_prefix}[{index}] must be an object")
        supplied_name = rule.get("ruleName")
        rule_name = supplied_name if isinstance(supplied_name, str) and supplied_name.strip() else f"<rule {index + 1}>"
        identity_issues: list[dict[str, Any]] = []
        if not isinstance(supplied_name, str) or not supplied_name.strip():
            identity_issues.append(_issue(
                unit=unit_name, rule_name=rule_name,
                path=f"{path_prefix}.{index}.rule_header.ruleName",
                check="Rule identity and parent", message="RuleName is required.",
                extra={"failureClass": "input validation"},
            ))
        elif rule_name in rule_names:
            identity_issues.append(_issue(
                unit=unit_name, rule_name=rule_name,
                path=f"{path_prefix}.{index}.rule_header.ruleName",
                check="Rule identity and parent", message="RuleName duplicates another rule in this control budget.",
                extra={"failureClass": "input validation", "suppliedValue": rule_name},
            ))
        rule_names.add(rule_name)
        checks, issues = _validate_checks(
            rule.get("checks"),
            unit=unit_name,
            sections=sections,
            path_prefix=f"{path_prefix}.{index}",
            rule_name=rule_name,
            deferrals=deferrals,
        )
        issues = identity_issues + issues
        unit = {"unit": unit_name, "ruleName": rule_name,
                "status": "blocked" if issues else "passed", "checks": checks}
        if budget_name is not None:
            unit["controlBudgetName"] = budget_name
            if budget_index is not None:
                unit["controlBudgetIndex"] = budget_index + 1
            for issue in issues:
                issue["controlBudgetName"] = budget_name
                if budget_index is not None:
                    issue["controlBudgetIndex"] = budget_index + 1
        report["units"].append(unit)
        report["actualIssues"].extend(issues)
    return True


def _append_revenue_rule_units(
    report: dict[str, Any], rules: Any, *, path_prefix: str,
    budget_name: str, budget_index: int,
) -> bool:
    return _append_rule_units(
        report, rules, path_prefix=path_prefix,
        budget_name=budget_name, budget_index=budget_index,
        unit_name="revenue_funding_rules", sections=REVENUE_RULE_SECTIONS,
        deferrals=REVENUE_FUSION_DEFERRALS,
    )


def _append_override_rule_units(
    report: dict[str, Any], rules: Any, *, path_prefix: str,
    budget_name: str, budget_index: int,
) -> bool:
    return _append_rule_units(
        report, rules, path_prefix=path_prefix,
        budget_name=budget_name, budget_index=budget_index,
        unit_name="override_rules", sections=OVERRIDE_RULE_SECTIONS,
        deferrals=OVERRIDE_FUSION_DEFERRALS,
    )


def _finish_child_groups(
    report: dict[str, Any], *, include_revenue: bool = True,
    include_override: bool = False,
) -> dict[str, Any]:
    """Summarize requested groups without letting one skip another."""
    groups = [("supplemental_rules", "supplementalRules")]
    if include_revenue:
        groups.append(("revenue_funding_rules", "revenueFundingRules"))
    if include_override:
        groups.append(("override_rules", "overrideRules"))
    for unit_name, field in groups:
        units = [unit for unit in report["units"] if unit["unit"] == unit_name]
        report[field] = (
            "not_applicable" if not units else
            "blocked" if any(unit["status"] == "blocked" for unit in units) else "passed"
        )
    report["status"] = "blocked" if report["actualIssues"] else "passed"
    report["packageReady"] = report["status"] == "passed"
    report["actualReason"] = _primary_reason(report["actualIssues"])
    if report["actualIssues"]:
        primary = next(
            (issue for issue in report["actualIssues"] if issue.get("code") != "not_evaluated"),
            report["actualIssues"][0],
        )
        report["activeUnit"] = primary["unit"]
    elif report.get("overrideRules") == "passed":
        report["activeUnit"] = "override_rules"
    elif report.get("revenueFundingRules") == "passed":
        report["activeUnit"] = "revenue_funding_rules"
    elif report["supplementalRules"] == "passed":
        report["activeUnit"] = "supplemental_rules"
    return report


def _validate_single(payload: Mapping[str, Any]) -> dict[str, Any]:
    budget_name, budget_unit, budget_issues = _budget_result(
        payload, path_prefix="controlBudget",
    )
    budget_status = budget_unit["status"]
    report: dict[str, Any] = {
        "controlBudget": budget_name,
        "status": budget_status,
        "activeUnit": "control_budget",
        "units": [budget_unit],
        "actualIssues": budget_issues,
        "actualReason": _primary_reason(budget_issues),
        "packageReady": False,
    }
    if budget_issues:
        report["supplementalRules"] = "not_evaluated"
        if "revenueFundingRules" in payload:
            report["revenueFundingRules"] = "not_evaluated"
        if "overrideRules" in payload:
            report["overrideRules"] = "not_evaluated"
        return report

    any_rules = _append_rule_units(
        report, payload.get("supplementalRules", []), path_prefix="supplementalRules",
    )
    if "revenueFundingRules" in payload:
        _append_revenue_rule_units(
            report, payload["revenueFundingRules"], path_prefix="revenueFundingRules",
            budget_name=budget_name, budget_index=0,
        )
    if "overrideRules" in payload:
        _append_override_rule_units(
            report, payload["overrideRules"], path_prefix="overrideRules",
            budget_name=budget_name, budget_index=0,
        )
    if "revenueFundingRules" in payload or "overrideRules" in payload:
        return _finish_child_groups(
            report, include_revenue="revenueFundingRules" in payload,
            include_override="overrideRules" in payload,
        )
    if not any_rules:
        report.update(status="passed", packageReady=True, supplementalRules="not_applicable")
        return report
    report["activeUnit"] = "supplemental_rules"
    report["status"] = "blocked" if report["actualIssues"] else "passed"
    report["packageReady"] = report["status"] == "passed"
    if report["actualIssues"]:
        report["actualReason"] = _primary_reason(report["actualIssues"])
    return report


def _validate_multiple(payload: Mapping[str, Any]) -> dict[str, Any]:
    if any(key in payload for key in (
        "controlBudget", "controlBudgetChecks", "supplementalRules", "revenueFundingRules",
        "overrideRules",
    )):
        raise ValidationContractError("Use either controlBudgets or the single-budget fields")
    budgets = payload["controlBudgets"]
    if not isinstance(budgets, list) or not budgets:
        raise ValidationContractError("controlBudgets must be a nonempty array")

    report: dict[str, Any] = {
        "controlBudgets": [], "status": "passed", "activeUnit": "control_budget",
        "units": [], "actualIssues": [], "actualReason": None,
        "packageReady": False,
    }
    seen_names: set[str] = set()
    # Complete the first unit for every budget before inspecting any rule.
    for index, budget in enumerate(budgets):
        if not isinstance(budget, Mapping):
            raise ValidationContractError(f"controlBudgets[{index}] must be an object")
        budget_name, unit, issues = _budget_result(
            budget, path_prefix=f"controlBudgets.{index}", budget_index=index,
        )
        if budget_name in seen_names:
            issues.insert(0, _issue(
                unit="control_budget", path=f"controlBudgets.{index}.header.name",
                check="Control budget identity",
                message="Control budget name duplicates another budget in this request.",
                extra={"failureClass": "input validation", "suppliedValue": budget_name},
            ))
            issues[0]["controlBudgetName"] = budget_name
            issues[0]["controlBudgetIndex"] = index + 1
            unit["status"] = "blocked"
        seen_names.add(budget_name)
        report["controlBudgets"].append(budget_name)
        report["units"].append(unit)
        report["actualIssues"].extend(issues)
    if report["actualIssues"]:
        report.update(
            status="blocked", actualReason=_primary_reason(report["actualIssues"]),
            supplementalRules="not_evaluated",
        )
        if any("revenueFundingRules" in budget for budget in budgets):
            report["revenueFundingRules"] = "not_evaluated"
        if any("overrideRules" in budget for budget in budgets):
            report["overrideRules"] = "not_evaluated"
        return report

    any_rules = False
    for index, budget in enumerate(budgets):
        any_rules = _append_rule_units(
            report, budget.get("supplementalRules", []),
            path_prefix=f"controlBudgets.{index}.supplementalRules",
            budget_name=report["controlBudgets"][index],
            budget_index=index,
        ) or any_rules
    if any("revenueFundingRules" in budget for budget in budgets):
        # Keep Supplemental findings first, then Revenue and Override findings
        # in budget/rule order, even when another group is already blocked.
        for index, budget in enumerate(budgets):
            _append_revenue_rule_units(
                report, budget.get("revenueFundingRules", []),
                path_prefix=f"controlBudgets.{index}.revenueFundingRules",
                budget_name=report["controlBudgets"][index], budget_index=index,
            )
    if any("overrideRules" in budget for budget in budgets):
        for index, budget in enumerate(budgets):
            _append_override_rule_units(
                report, budget.get("overrideRules", []),
                path_prefix=f"controlBudgets.{index}.overrideRules",
                budget_name=report["controlBudgets"][index], budget_index=index,
            )
    if any("revenueFundingRules" in budget or "overrideRules" in budget for budget in budgets):
        return _finish_child_groups(
            report,
            include_revenue=any("revenueFundingRules" in budget for budget in budgets),
            include_override=any("overrideRules" in budget for budget in budgets),
        )
    if not any_rules:
        report.update(packageReady=True, supplementalRules="not_applicable")
        return report
    report["activeUnit"] = "supplemental_rules"
    report["status"] = "blocked" if report["actualIssues"] else "passed"
    report["packageReady"] = report["status"] == "passed"
    report["supplementalRules"] = report["status"]
    report["actualReason"] = _primary_reason(report["actualIssues"])
    return report


def validate_units(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Aggregate all active-unit findings and return one pre-ZIP gate report."""
    if not isinstance(payload, Mapping):
        raise ValidationContractError("Input must be a JSON object")
    if "controlBudgets" in payload:
        return _validate_multiple(payload)
    return _validate_single(payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True,
                        help="JSON with ordered task check outcomes")
    parser.add_argument("--output", type=Path, required=True,
                        help="New pre-ZIP report path (existing files are never replaced)")
    args = parser.parse_args(argv)
    stage = "input_validation"
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8-sig"))
        report = validate_units(payload)
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        # Raw exceptions may contain supplied values or customer file contents.
        # Keep the diagnostic structural and never print the input document.
        report = {
            "status": "error", "stage": stage, "failure_class": "input_validation",
            "message": "Validation input could not be read or does not satisfy the check contract.",
            "error_type": type(exc).__name__, "packageReady": False,
            "recommended_action": "Correct the input JSON and ordered check contract, then write a new report.",
        }
    try:
        stage = "output_directory"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        stage = "output_creation"
        with args.output.open("x", encoding="utf-8") as output:
            output.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    except OSError as exc:
        conflict = isinstance(exc, FileExistsError) and stage == "output_creation"
        print(json.dumps({
            "status": "error", "stage": "artifact_persistence",
            "failure_class": "approval_blocker" if conflict else "artifact_persistence",
            "message": "Output already exists; it was preserved." if conflict else "Could not persist the validation report.",
            "error_type": type(exc).__name__, "packageReady": False,
            "recommended_action": "Choose a new output path; use the project artifact-version workflow for approved replacement.",
        }))
        return 1
    if report["status"] == "error":
        print(json.dumps(report))
        return 1
    print(json.dumps({key: report[key] for key in (
        "status", "activeUnit", "actualReason", "packageReady"
    )}))
    return 0 if report["packageReady"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
